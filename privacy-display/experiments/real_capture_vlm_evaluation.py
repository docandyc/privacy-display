"""
Evaluate VLM models on real camera-capture photos of protected displays.

Sends each real-capture JPEG to VLM APIs (Qwen3-VL, Kimi-K2.6, GLM-4.5V),
collects exact-match / char-accuracy metrics, and writes results to
``results/real_capture_vlm.json``.

Usage:
    python experiments/real_capture_vlm_evaluation.py --dry-run
    python experiments/real_capture_vlm_evaluation.py --positions d0.5_a0 --max-samples 1
    python experiments/real_capture_vlm_evaluation.py                     # full run
    python experiments/real_capture_vlm_evaluation.py --resume            # continue after interrupt
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.attack.vlm_evaluator import (  # noqa: E402
    API_KEY_ENV,
    DEFAULT_SILICONFLOW_BASE_URL,
    VLMClient,
)
from src.evaluation.benchmark import _mean_std  # noqa: E402
from src.demo.playback_demo import canonical_anti_ocr_profile  # noqa: E402

EXPERIMENTS_DIR = ROOT / "experiments"
RESULTS_DIR = EXPERIMENTS_DIR / "results"

ALL_POSITIONS = (
    "d0.5_a0", "d0.5_a15", "d0.5_a30",
    "d1_a0", "d1_a15", "d1_a30",
    "d1.5_a0", "d1.5_a15", "d1.5_a30",
)

# Three VLM families for the real-capture evaluation. Instruct-style (non-thinking)
# models keep output tokens low; verify IDs against the live SiliconFlow catalog
# before any paid run and override with --models if an ID is unavailable.
DEFAULT_MODELS = (
    "Qwen/Qwen3-VL-32B-Instruct",       # Qwen-VL family (incumbent)
    "Pro/moonshotai/Kimi-K2.6",         # Kimi-K2 family
    "zai-org/GLM-4.5V",                 # GLM-V family
)

RESULT_FILE = "real_capture_vlm.json"
VLM_LEAK_THRESHOLD = 0.20


# ---------------------------------------------------------------------------
# .env.local loader (same as vlm_readability_analysis.py)
# ---------------------------------------------------------------------------

def load_local_env(path: Path | None = None) -> None:
    env_path = path or (ROOT / ".env.local")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value


# ---------------------------------------------------------------------------
# Real-capture photo loader
# ---------------------------------------------------------------------------

def _capture_dir_for_position(
    pos: str,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> Path:
    return experiments_dir / f"real_captures_{pos}_final"


def load_real_captures(
    experiments_dir: Path = EXPERIMENTS_DIR,
    positions: list[str] | None = None,
    profiles: tuple[str, ...] = ("capture_hardened",),
    baseline_position: str | None = "d0.5_a0",
    baseline_attack: str = "short",
    max_samples: int | None = None,
) -> list[dict]:
    """Load capture entries from metadata.json across position directories."""
    if positions is not None and not positions:
        raise ValueError("positions must not be empty")
    positions = list(positions) if positions is not None else list(ALL_POSITIONS)
    unknown_positions = sorted(set(positions) - set(ALL_POSITIONS))
    if unknown_positions:
        raise ValueError(f"unknown positions: {', '.join(unknown_positions)}")
    if baseline_position is not None and baseline_position not in ALL_POSITIONS:
        raise ValueError(f"unknown baseline position: {baseline_position}")
    if not profiles:
        raise ValueError("profiles must not be empty")
    profiles = tuple(canonical_anti_ocr_profile(value) for value in profiles)
    if max_samples is not None and max_samples <= 0:
        raise ValueError("max_samples must be positive when provided")

    captures: list[dict] = []
    seen_keys: set[tuple[str, str]] = set()

    for pos in positions:
        cap_dir = _capture_dir_for_position(pos, experiments_dir)
        meta_path = cap_dir / "metadata.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"capture metadata not found: {meta_path}")

        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        entries = meta.get("captures")
        if not isinstance(entries, list):
            raise ValueError(f"metadata captures must be a list: {meta_path}")

        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"capture entry must be an object: {meta_path}")
            raw_ablation = str(entry.get("ablation", ""))
            raw_profile = str(entry.get("profile", ""))
            ablation = (
                "capture_hardened" if raw_ablation == "vlm" else raw_ablation
            )
            profile = canonical_anti_ocr_profile(
                raw_profile or ("capture_hardened" if ablation == "capture_hardened" else "off")
            )
            is_target = ablation in profiles or profile in profiles
            is_baseline = (
                baseline_position
                and pos == baseline_position
                and ablation == "original"
                and profile == "off"
                and entry.get("attack") == baseline_attack
            )
            if not is_target and not is_baseline:
                continue

            capture_id = str(entry.get("id", "")).strip()
            image_name = str(entry.get("image", "")).strip()
            truth = str(entry.get("truth", ""))
            condition = str(entry.get("condition", "")).strip()
            if condition == "vlm" or condition.startswith("vlm|"):
                condition = "capture_hardened" + condition[len("vlm"):]
            if not capture_id:
                raise ValueError(f"capture id is required: {meta_path}")
            if not image_name:
                raise ValueError(f"capture image is required for {capture_id}: {meta_path}")
            if not truth.strip():
                raise ValueError(
                    f"capture ground truth is required for {capture_id}: {meta_path}"
                )
            if not condition:
                raise ValueError(f"capture condition is required for {capture_id}: {meta_path}")
            capture_key = (pos, capture_id)
            if capture_key in seen_keys:
                raise ValueError(f"duplicate capture key {pos}|{capture_id}: {meta_path}")
            seen_keys.add(capture_key)

            image_path = cap_dir / image_name
            if not image_path.exists():
                raise FileNotFoundError(
                    f"capture image not found for {capture_id}: {image_path}"
                )

            captures.append({
                "id": capture_id,
                "image_path": str(image_path),
                "truth": truth,
                "condition": condition,
                "ablation": ablation,
                "attack": entry.get("attack", ""),
                "profile": profile,
                "position": pos,
                "distance_m": entry.get("distance_m"),
                "angle_degrees": entry.get("angle_degrees"),
                "capture_mode": entry.get("capture_mode", ""),
            })

    if max_samples is not None:
        by_condition: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for c in captures:
            by_condition[(c["position"], c["condition"])].append(c)
        sampled: list[dict] = []
        for cond_captures in by_condition.values():
            sampled.extend(cond_captures[:max_samples])
        return sampled

    return captures


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def enhance_image(img: np.ndarray) -> np.ndarray:
    """Grayscale percentile stretch + CLAHE — simulates attacker preprocessing."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    lo, hi = np.percentile(gray, [1, 99])
    if hi - lo < 1:
        hi = lo + 1
    stretched = np.clip(
        (gray.astype(np.float32) - lo) / (hi - lo) * 255, 0, 255,
    ).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(stretched)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)


def load_image(path: str, enhance: bool = False) -> np.ndarray:
    with Image.open(path) as img:
        arr = np.asarray(img.convert("RGB"))
    if enhance:
        arr = enhance_image(arr)
    return arr


def evaluate_model(
    client: VLMClient,
    captures: list[dict],
    delay: float = 0.5,
    done_ids: set[str] | None = None,
    retries: int = 2,
    retry_backoff: float = 1.0,
    max_tokens: int = 4096,
    enhance: bool = False,
    on_result: Callable[[dict], None] | None = None,
) -> list[dict]:
    """Run VLM evaluation on a list of captures, returning per-row results."""
    if delay < 0:
        raise ValueError("delay must be non-negative")
    if retries < 0:
        raise ValueError("retries must be non-negative")
    if retry_backoff < 0:
        raise ValueError("retry_backoff must be non-negative")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    rows: list[dict] = []
    done_ids = done_ids or set()
    to_process = [
        entry for entry in captures
        if f"{client.model}|{entry['position']}|{entry['id']}" not in done_ids
    ]
    model_short = client.model.split("/")[-1]
    em_count = 0
    err_count = 0

    pbar = tqdm(
        to_process,
        desc=f"{model_short}",
        unit="img",
        bar_format=(
            "{l_bar}{bar}| {n_fmt}/{total_fmt} "
            "[{elapsed}<{remaining}, {rate_fmt}] "
            "{postfix}"
        ),
    )
    for entry in pbar:
        try:
            image = load_image(entry["image_path"], enhance=enhance)
        except Exception as exc:
            row = _error_row(client.model, entry, f"image_load: {exc}")
            rows.append(row)
            if on_result is not None:
                on_result(row)
            err_count += 1
            pbar.set_postfix(exact=em_count, err=err_count)
            continue

        row: dict | None = None
        for attempt in range(retries + 1):
            try:
                result = client.analyze_image(
                    image,
                    ground_truth=entry["truth"],
                    max_tokens=max_tokens,
                )
                metrics = result.get("metrics", {})
                row = {
                    "id": entry["id"],
                    "model": client.model,
                    "condition": entry["condition"],
                    "ablation": entry["ablation"],
                    "attack": entry["attack"],
                    "profile": entry.get("profile", ""),
                    "position": entry["position"],
                    "distance_m": entry["distance_m"],
                    "angle_degrees": entry["angle_degrees"],
                    "capture_mode": entry.get("capture_mode", ""),
                    "visible_text": result.get("visible_text", ""),
                    "char_accuracy": metrics.get("char_accuracy", 0.0),
                    "word_accuracy": metrics.get("word_accuracy", 0.0),
                    "exact_match": metrics.get("exact_match", False),
                    "sensitive_token_recall": metrics.get("sensitive_token_recall", 0.0),
                    "sensitive_token_count": metrics.get("sensitive_token_count", 0),
                    "vlm_confidence": result.get("confidence", 0.0),
                    "vlm_can_read_sensitive": result.get("can_read_sensitive", False),
                    "vlm_notes": str(result.get("notes", "") or "")[:500],
                    "usage": result.get("usage", {}),
                    "attempt_count": attempt + 1,
                    "vlm_error": "",
                }
                break
            except Exception as exc:
                if attempt < retries:
                    if retry_backoff > 0:
                        time.sleep(retry_backoff * (2 ** attempt))
                    continue
                row = _error_row(
                    client.model,
                    entry,
                    str(exc),
                    attempt_count=attempt + 1,
                )

        assert row is not None
        rows.append(row)
        if on_result is not None:
            on_result(row)
        if row.get("exact_match"):
            em_count += 1
        if row.get("vlm_error"):
            err_count += 1
        pbar.set_postfix(exact=em_count, err=err_count)

        if delay > 0:
            time.sleep(delay)
    pbar.close()

    return rows


def _error_row(
    model: str,
    entry: dict,
    error: str,
    attempt_count: int = 1,
) -> dict:
    return {
        "id": entry["id"],
        "model": model,
        "condition": entry["condition"],
        "ablation": entry["ablation"],
        "attack": entry["attack"],
        "profile": entry.get("profile", ""),
        "position": entry["position"],
        "distance_m": entry.get("distance_m"),
        "angle_degrees": entry.get("angle_degrees"),
        "capture_mode": entry.get("capture_mode", ""),
        "visible_text": "",
        "char_accuracy": 0.0,
        "word_accuracy": 0.0,
        "exact_match": False,
        "sensitive_token_recall": 0.0,
        "sensitive_token_count": 0,
        "vlm_confidence": 0.0,
        "vlm_can_read_sensitive": False,
        "vlm_notes": "",
        "usage": {},
        "attempt_count": attempt_count,
        "vlm_error": _sanitize_row_error(error),
    }


def _sanitize_row_error(error: str) -> str:
    sanitized = str(error).replace("\n", " ").strip()
    api_key = os.environ.get(API_KEY_ENV, "")
    if api_key:
        sanitized = sanitized.replace(api_key, "[REDACTED]")
    return sanitized[:500]


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------
def _metric_stats(values: list[float]) -> dict:
    if values:
        return _mean_std(values)
    return {
        "mean": None,
        "std": None,
        "count": 0,
        "ci95": {
            "low": None,
            "high": None,
            "half_width": None,
            "confidence": 0.95,
            "method": "unavailable",
            "resamples": 0,
        },
    }


def _aggregate_group(rows: list[dict]) -> dict:
    """Compute summary stats for a group of result rows."""
    successful = [r for r in rows if not r.get("vlm_error")]
    sensitive = [r for r in successful if int(r.get("sensitive_token_count", 0)) > 0]
    return {
        "exact_match": _metric_stats([float(r["exact_match"]) for r in successful]),
        "char_accuracy": _metric_stats([r["char_accuracy"] for r in successful]),
        "sensitive_token_recall": _metric_stats([
            r["sensitive_token_recall"] for r in sensitive
        ]),
        "vlm_read_success_rate": _metric_stats([
            float(
                bool(r.get("vlm_can_read_sensitive", False))
                or float(r["char_accuracy"]) >= VLM_LEAK_THRESHOLD
            )
            for r in successful
        ]),
        "attempted_count": len(rows),
        "successful_count": len(successful),
        "error_count": sum(1 for r in rows if r.get("vlm_error")),
        "count": len(successful),
    }


def summarize_results(all_rows: list[dict]) -> dict:
    """Build per-model and cross-model summaries."""
    by_model: dict[str, list[dict]] = defaultdict(list)
    for row in all_rows:
        by_model[row["model"]].append(row)

    models_summary: dict[str, Any] = {}
    for model, rows in by_model.items():
        by_condition: dict[str, list[dict]] = defaultdict(list)
        by_position: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            by_condition[r["condition"]].append(r)
            if r.get("ablation") != "original":
                by_position[r["position"]].append(r)

        models_summary[model] = {
            "by_condition": {c: _aggregate_group(rs) for c, rs in sorted(by_condition.items())},
            "by_position": {p: _aggregate_group(rs) for p, rs in sorted(by_position.items())},
            "overall": _aggregate_group(rows),
        }

    conditions = sorted({r["condition"] for r in all_rows})
    cross_model: dict[str, dict[str, float | None]] = {}
    for cond in conditions:
        cross_model[cond] = {}
        for model in by_model:
            cond_rows = [
                r for r in by_model[model]
                if r["condition"] == cond and not r.get("vlm_error")
            ]
            cross_model[cond][model] = (
                float(np.mean([float(r["exact_match"]) for r in cond_rows]))
                if cond_rows
                else None
            )

    return {"models": models_summary, "cross_model": cross_model}


# ---------------------------------------------------------------------------
# Partial save / resume
# ---------------------------------------------------------------------------
def _row_key(row: dict) -> tuple[str, str, str]:
    return str(row["model"]), str(row["position"]), str(row["id"])


def upsert_rows(existing: list[dict], updates: list[dict]) -> list[dict]:
    """Replace prior observations with the newest row for the same capture."""
    merged: dict[tuple[str, str, str], dict] = {}
    for row in [*existing, *updates]:
        merged[_row_key(row)] = row
    return list(merged.values())


def partial_path_for_output(output_path: Path) -> Path:
    suffix = output_path.suffix or ".json"
    return output_path.with_name(f"{output_path.stem}_partial{suffix}")


def _write_json_atomic(
    payload: dict,
    path: Path,
    *,
    attempts: int = 3,
    retry_delay: float = 0.05,
) -> None:
    if attempts <= 0:
        raise ValueError("attempts must be positive")
    path.parent.mkdir(parents=True, exist_ok=True)
    last_error: OSError | None = None
    for attempt in range(1, attempts + 1):
        temp_path = path.with_name(
            f".{path.name}.{os.getpid()}.{time.monotonic_ns()}.tmp"
        )
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=1)
            os.replace(temp_path, path)
            return
        except OSError as exc:
            last_error = exc
            if attempt < attempts and retry_delay > 0:
                time.sleep(retry_delay)
        finally:
            temp_path.unlink(missing_ok=True)
    raise OSError(
        getattr(last_error, "errno", None),
        f"failed to write JSON after {attempts} attempts: {path}",
    ) from last_error


def save_partial(rows: list[dict], path: Path, config: dict) -> None:
    payload = {"schema_version": 1, "config": config, "rows": rows}
    _write_json_atomic(payload, path)


def load_partial(path: Path, expected_config: dict) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError(f"partial result is incompatible with this script: {path}")
    if payload.get("config") != expected_config:
        raise ValueError(f"partial result has incompatible run config: {path}")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError(f"partial result rows must be a list: {path}")
    return rows


def done_ids_from_rows(rows: list[dict]) -> set[str]:
    return {
        f"{r['model']}|{r['position']}|{r['id']}"
        for r in rows
        if not r.get("vlm_error")
    }


def run_evaluation_batches(
    *,
    models: tuple[str, ...],
    captures: list[dict],
    client_factory: Callable[[str], VLMClient],
    partial_path: Path,
    resume_config: dict,
    existing_rows: list[dict] | None = None,
    delay: float = 0.5,
    retries: int = 2,
    retry_backoff: float = 1.0,
    max_tokens: int = 4096,
    enhance: bool = False,
) -> list[dict]:
    """Evaluate model/position batches and checkpoint after every position."""
    allowed_keys = {
        (model_id, str(c["position"]), str(c["id"]))
        for model_id in models
        for c in captures
    }
    for row in existing_rows or []:
        try:
            key = _row_key(row)
        except (KeyError, TypeError) as exc:
            raise ValueError("resume row is missing model, position, or id") from exc
        if key not in allowed_keys:
            raise ValueError(f"resume row is outside the selected run: {'|'.join(key)}")

    row_map = {
        _row_key(row): row
        for row in upsert_rows([], existing_rows or [])
    }
    done = done_ids_from_rows(list(row_map.values()))
    positions = list(dict.fromkeys(str(c["position"]) for c in captures))

    for model_id in models:
        client = client_factory(model_id)
        for position in positions:
            batch = [c for c in captures if c["position"] == position]

            def record(row: dict) -> None:
                row_map[_row_key(row)] = row

            try:
                model_rows = evaluate_model(
                    client=client,
                    captures=batch,
                    delay=delay,
                    done_ids=done,
                    retries=retries,
                    retry_backoff=retry_backoff,
                    max_tokens=max_tokens,
                    enhance=enhance,
                    on_result=record,
                )
            except KeyboardInterrupt:
                save_partial(list(row_map.values()), partial_path, resume_config)
                raise

            for row in model_rows:
                record(row)
            done.update(done_ids_from_rows(model_rows))
            save_partial(list(row_map.values()), partial_path, resume_config)

    return list(row_map.values())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def _nonnegative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _parse_models(value: str) -> tuple[str, ...]:
    models = tuple(part.strip() for part in value.split(",") if part.strip())
    if not models:
        raise argparse.ArgumentTypeError("at least one model is required")
    return tuple(dict.fromkeys(models))


def _parse_positions(value: str) -> list[str]:
    positions = [part.strip() for part in value.split(",") if part.strip()]
    if not positions:
        raise argparse.ArgumentTypeError("at least one position is required")
    positions = list(dict.fromkeys(positions))
    unknown = sorted(set(positions) - set(ALL_POSITIONS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown positions: {', '.join(unknown)}")
    return positions


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VLM evaluation on real camera captures")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without API calls")
    parser.add_argument("--resume", action="store_true", help="Resume from partial results")
    parser.add_argument("--models", type=_parse_models, default=DEFAULT_MODELS,
                        help="Comma-separated model IDs (default: 3 models)")
    parser.add_argument("--positions", type=_parse_positions, default=None,
                        help="Comma-separated positions (default: all 9)")
    parser.add_argument("--delay", type=_nonnegative_float, default=0.5,
                        help="Seconds between API calls (default: 0.5)")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output file path")
    parser.add_argument("--baseline-position", type=str, default="d0.5_a0",
                        help="Position for original baseline (set 'none' to disable)")
    parser.add_argument("--baseline-attack", type=str, default="short",
                        help="Attack type for original baseline (default: 'short')")
    parser.add_argument("--enhance", action="store_true", default=False,
                        help="Apply contrast enhancement before VLM "
                             "(default: off, matches the raw-RGB OCR pipeline)")
    parser.add_argument("--no-enhance", dest="enhance", action="store_false",
                        help="Disable contrast enhancement (default)")
    parser.add_argument("--max-samples", type=_positive_int, default=None,
                        help="Max samples per position and condition (for debugging)")
    parser.add_argument("--base-url", default=DEFAULT_SILICONFLOW_BASE_URL)
    parser.add_argument("--timeout", type=_positive_float, default=120.0)
    parser.add_argument("--max-tokens", type=_positive_int, default=4096,
                        help="Maximum response tokens per transcription (default: 4096)")
    parser.add_argument("--retries", type=_nonnegative_int, default=2,
                        help="Retries after a failed VLM call (default: 2)")
    parser.add_argument("--retry-backoff", type=_nonnegative_float, default=1.0,
                        help="Initial exponential retry delay in seconds (default: 1.0)")
    return parser.parse_args(argv)


def build_resume_config(
    *,
    models: tuple[str, ...],
    captures: list[dict],
    base_url: str,
    max_tokens: int,
    enhance: bool = False,
) -> dict:
    selection = [
        {
            "position": c["position"],
            "id": c["id"],
            "condition": c["condition"],
            "image_path": c["image_path"],
            "truth_sha256": hashlib.sha256(
                c["truth"].encode("utf-8")
            ).hexdigest(),
        }
        for c in captures
    ]
    digest = hashlib.sha256(
        json.dumps(selection, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        "models": list(models),
        "base_url": base_url.rstrip("/"),
        "max_tokens": max_tokens,
        "enhance": enhance,
        "selection_sha256": digest,
        "capture_count": len(captures),
    }


def _call_status(rows: list[dict], planned_calls: int) -> dict:
    completed = len(rows)
    errors = sum(1 for row in rows if row.get("vlm_error"))
    successful = completed - errors
    pending = max(0, planned_calls - completed)
    return {
        "planned_calls": planned_calls,
        "completed_calls": completed,
        "successful_calls": successful,
        "error_calls": errors,
        "pending_calls": pending,
        "all_calls_failed": completed > 0 and successful == 0,
        "run_complete": completed == planned_calls and errors == 0,
    }


def build_output_report(
    *,
    models: tuple[str, ...],
    positions: list[str],
    captures: list[dict],
    rows: list[dict],
    baseline_position: str | None,
    max_samples: int | None,
    delay: float,
    base_url: str,
    timeout: float,
    max_tokens: int,
    retries: int,
    retry_backoff: float,
    selection_sha256: str,
    enhance: bool = False,
) -> dict:
    rows = upsert_rows([], rows)
    summary = summarize_results(rows)
    total_calls = len(captures) * len(models)
    call_status = _call_status(rows, total_calls)
    output = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": {
            "models": list(models),
            "positions": positions,
            "profiles_evaluated": ["capture_hardened"],
            "original_baseline_position": baseline_position,
            "contrast_enhancement": enhance,
            "max_samples_per_position_condition": max_samples,
            "total_captures": len(captures),
            "total_api_calls": total_calls,
            "delay_between_calls_s": delay,
            "base_url": base_url.rstrip("/"),
            "timeout_s": timeout,
            "max_tokens": max_tokens,
            "retries": retries,
            "retry_backoff_s": retry_backoff,
            "selection_sha256": selection_sha256,
            "leak_threshold_char_accuracy": VLM_LEAK_THRESHOLD,
        },
        "call_status": call_status,
        "models": {},
        "cross_model": summary["cross_model"],
    }
    for model_id in models:
        model_rows = [r for r in rows if r["model"] == model_id]
        model_summary = summary["models"].get(model_id, {})
        output["models"][model_id] = {
            "rows": model_rows,
            "call_status": _call_status(model_rows, len(captures)),
            "by_condition": model_summary.get("by_condition", {}),
            "by_position": model_summary.get("by_position", {}),
            "overall": model_summary.get("overall", {}),
        }
    return output


def main(
    argv: list[str] | None = None,
    *,
    client_factory: Callable[[str], VLMClient] | None = None,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> int:
    args = parse_args(argv)

    load_local_env()

    models = tuple(args.models)
    positions = args.positions
    baseline_pos = (
        None if args.baseline_position.strip().casefold() == "none"
        else args.baseline_position.strip()
    )
    if baseline_pos is not None and baseline_pos not in ALL_POSITIONS:
        print(f"[ERROR] unknown baseline position: {baseline_pos}", file=sys.stderr)
        return 2
    output_path = args.output or (RESULTS_DIR / RESULT_FILE)
    partial_path = partial_path_for_output(output_path)

    print(f"Models: {', '.join(models)}")
    print(f"Positions: {positions or 'all 9'}")
    print(f"Baseline position: {baseline_pos or 'disabled'}")
    print(f"Contrast enhancement: {'on' if args.enhance else 'off'}")

    captures = load_real_captures(
        experiments_dir=experiments_dir,
        positions=positions,
        baseline_position=baseline_pos,
        baseline_attack=args.baseline_attack,
        max_samples=args.max_samples,
    )

    conditions = defaultdict(int)
    for c in captures:
        conditions[c["condition"]] += 1
    print(f"\nLoaded {len(captures)} captures:")
    for cond, count in sorted(conditions.items()):
        print(f"  {cond}: {count}")

    total_calls = len(captures) * len(models)
    est_hours = total_calls * (2.0 + args.delay) / 3600
    print(f"\nTotal API calls: {total_calls} ({len(captures)} captures × {len(models)} models)")
    print(f"Estimated time: {est_hours:.1f} hours (at ~2s/call + {args.delay}s delay)")

    if args.dry_run:
        print("\n[DRY RUN] No API calls made.")
        return 0

    if not os.environ.get(API_KEY_ENV):
        print(
            f"\n[ERROR] {API_KEY_ENV} not set. Export it or add to .env.local",
            file=sys.stderr,
        )
        return 2

    selected_positions = positions or list(ALL_POSITIONS)
    resume_config = build_resume_config(
        models=models,
        captures=captures,
        base_url=args.base_url,
        max_tokens=args.max_tokens,
        enhance=args.enhance,
    )
    try:
        existing_rows = (
            load_partial(partial_path, resume_config) if args.resume else []
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"\n[ERROR] Cannot resume: {exc}", file=sys.stderr)
        return 2
    if existing_rows:
        print(f"\nResuming: {len(existing_rows)} rows loaded from partial file")

    factory = client_factory or (
        lambda model_id: VLMClient(
            model=model_id,
            base_url=args.base_url,
            timeout=args.timeout,
        )
    )
    try:
        all_rows = run_evaluation_batches(
            models=models,
            captures=captures,
            client_factory=factory,
            partial_path=partial_path,
            resume_config=resume_config,
            existing_rows=existing_rows,
            delay=args.delay,
            retries=args.retries,
            retry_backoff=args.retry_backoff,
            max_tokens=args.max_tokens,
            enhance=args.enhance,
        )
    except KeyboardInterrupt:
        print(f"\nInterrupted. Resume state saved to {partial_path}", file=sys.stderr)
        return 130

    print(f"\n{'='*60}")
    print("Aggregating results...")
    output = build_output_report(
        models=models,
        positions=selected_positions,
        captures=captures,
        rows=all_rows,
        baseline_position=baseline_pos,
        max_samples=args.max_samples,
        delay=args.delay,
        base_url=args.base_url,
        timeout=args.timeout,
        max_tokens=args.max_tokens,
        retries=args.retries,
        retry_backoff=args.retry_backoff,
        selection_sha256=resume_config["selection_sha256"],
        enhance=args.enhance,
    )
    _write_json_atomic(output, output_path)
    print(f"Results saved to {output_path}")

    status = output["call_status"]
    if status["run_complete"] and partial_path.exists():
        partial_path.unlink()
        print(f"Partial file removed: {partial_path.name}")
    elif not status["run_complete"]:
        print(
            "Run is incomplete: "
            f"successful={status['successful_calls']} "
            f"errors={status['error_calls']} pending={status['pending_calls']}. "
            f"Resume with --resume; partial kept at {partial_path}.",
            file=sys.stderr,
        )

    print("\n--- Cross-model exact-match summary ---")
    for cond, model_vals in sorted(output["cross_model"].items()):
        vals = "  ".join(
            f"{m.split('/')[-1]}: {'n/a' if v is None else f'{v:.1%}'}"
            for m, v in model_vals.items()
        )
        print(f"  {cond:40s} {vals}")
    return 0 if status["run_complete"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
