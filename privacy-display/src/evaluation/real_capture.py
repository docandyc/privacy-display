"""
Real camera capture OCR analysis.

This module evaluates photos or extracted video frames captured from phones,
smart glasses, or other cameras. It does not capture from hardware itself; it
turns manually collected images plus metadata into auditable publication
artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from PIL import Image

from src.attack.ocr_evaluator import OCREvaluator, text_recovery_metrics
from src.evaluation.benchmark import _mean_std


REAL_CAPTURE_JSON = "real_capture_ocr.json"
REAL_CAPTURE_MD = "real_capture_ocr.md"
METADATA_TEMPLATE_JSON = "metadata_template.json"

CAPTURE_TEMPLATE = {
    "schema_version": 1,
    "notes": "Copy this file to metadata.json after collecting real camera photos or extracted video frames.",
    "captures": [
        {
            "id": "iphone15pro_auto_0deg_1m_protected_sample01",
            "image": "iphone15pro_auto_0deg_1m_protected_sample01.jpg",
            "truth": "PLACE THE EXACT DISPLAYED TEXT HERE",
            "condition": "protected",
            "device": "iPhone 15 Pro",
            "camera_type": "phone",
            "capture_mode": "auto_photo",
            "distance_m": 1.0,
            "angle_degrees": 0.0,
            "exposure_s": None,
            "frame_rate_fps": None,
            "display_refresh_hz": 240,
            "n": 4,
            "epsilon": 0.031372549,
            "lighting_lux": None,
            "environment": "office",
            "notes": "Use protected/original/short_exposure/video_frame as condition labels.",
        }
    ],
}


def write_capture_template(
    capture_dir: str | Path = "experiments/real_captures",
    filename: str = METADATA_TEMPLATE_JSON,
) -> Path:
    """Write a metadata template for manual real-camera collection."""
    root = Path(capture_dir)
    root.mkdir(parents=True, exist_ok=True)
    out = root / filename
    with open(out, "w", encoding="utf-8") as f:
        json.dump(CAPTURE_TEMPLATE, f, ensure_ascii=False, indent=2)
    return out


def load_capture_metadata(
    capture_dir: str | Path = "experiments/real_captures",
    metadata_file: str = "metadata.json",
) -> list[dict]:
    """Load and validate real-capture metadata entries."""
    path = Path(capture_dir) / metadata_file
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    captures = payload.get("captures")
    if not isinstance(captures, list):
        raise ValueError("real capture metadata must contain a captures list")
    for idx, entry in enumerate(captures):
        if not isinstance(entry, dict):
            raise ValueError(f"capture entry {idx} must be an object")
        for field in ("id", "image", "truth"):
            if not str(entry.get(field, "")).strip():
                raise ValueError(f"capture entry {idx} is missing required field: {field}")
    return captures


def load_capture_image(capture_dir: Path, relative_path: str) -> np.ndarray:
    path = capture_dir / relative_path
    if not path.exists():
        raise FileNotFoundError(f"real capture image not found: {path}")
    return np.asarray(Image.open(path).convert("RGB"))


def run_real_capture_ocr(
    capture_dir: str | Path = "experiments/real_captures",
    metadata_file: str = "metadata.json",
    output_dir: str | Path = "experiments/results",
    engines: list[str] | None = None,
    evaluator: OCREvaluator | None = None,
    ocr_timeout: float | None = 10.0,
    show_progress: bool = False,
    save: bool = True,
) -> dict:
    """Run OCR on manually collected real-camera captures."""
    capture_root = Path(capture_dir)
    captures = load_capture_metadata(capture_root, metadata_file)
    evaluator = evaluator or OCREvaluator(engines=engines, timeout=ocr_timeout)
    engine_list = engines or evaluator.engines
    if not engine_list:
        raise ValueError("no OCR engines available for real-capture analysis")

    rows: list[dict] = []
    total_rows = len(captures) * len(engine_list)
    completed_rows = 0
    for entry in captures:
        image = load_capture_image(capture_root, str(entry["image"]))
        truth = str(entry["truth"])
        for engine in engine_list:
            ocr_error = ""
            try:
                result = evaluator.evaluate_single(image, truth, engine)
                recognized = result.text
                char_accuracy = result.char_accuracy
                word_accuracy = result.word_accuracy
            except Exception as exc:
                recognized = ""
                metrics = text_recovery_metrics(recognized, truth)
                char_accuracy = metrics["char_accuracy"]
                word_accuracy = metrics["word_accuracy"]
                ocr_error = str(exc)
            metrics = text_recovery_metrics(recognized, truth)
            rows.append({
                "id": str(entry["id"]),
                "image": str(entry["image"]),
                "engine": engine,
                "condition": str(entry.get("condition", "unknown")),
                "ablation": str(entry.get("ablation", "")),
                "attack": str(entry.get("attack", "")),
                "profile": str(entry.get("profile", "")),
                "stripe_alpha": _optional_float(entry.get("stripe_alpha")),
                "glyph_alpha": _optional_float(entry.get("glyph_alpha")),
                "inversion_alpha": _optional_float(entry.get("inversion_alpha")),
                "playback_cmd": str(entry.get("playback_cmd", "")),
                "roi_pos": str(entry.get("roi_pos", "")),
                "device": str(entry.get("device", "unknown")),
                "camera_type": str(entry.get("camera_type", "unknown")),
                "capture_mode": str(entry.get("capture_mode", "unknown")),
                "distance_m": _optional_float(entry.get("distance_m")),
                "angle_degrees": _optional_float(entry.get("angle_degrees")),
                "exposure_s": _optional_float(entry.get("exposure_s")),
                "frame_rate_fps": _optional_float(entry.get("frame_rate_fps")),
                "display_refresh_hz": _optional_float(entry.get("display_refresh_hz")),
                "n": _optional_int(entry.get("n")),
                "epsilon": _optional_float(entry.get("epsilon")),
                "lighting_lux": _optional_float(entry.get("lighting_lux")),
                "environment": str(entry.get("environment", "")),
                "notes": str(entry.get("notes", "")),
                "char_accuracy": char_accuracy,
                "word_accuracy": word_accuracy,
                "exact_match": metrics["exact_match"],
                "sensitive_token_recall": metrics["sensitive_token_recall"],
                "sensitive_token_count": metrics["sensitive_token_count"],
                "recognized_text": recognized[:240],
                "ocr_error": ocr_error,
            })
            completed_rows += 1
            if show_progress:
                _print_ocr_progress(
                    completed_rows,
                    total_rows,
                    capture_id=str(entry["id"]),
                    engine=engine,
                )

    report = {
        "schema_version": 1,
        "capture_dir": str(capture_root),
        "metadata_file": metadata_file,
        "config": {
            "engines": engine_list,
            "n_captures": len(captures),
            "n_rows": len(rows),
            "ocr_timeout": ocr_timeout,
        },
        "summary": summarize_real_capture_rows(rows),
        "captures": rows,
    }
    if save:
        out_root = Path(output_dir)
        out_root.mkdir(parents=True, exist_ok=True)
        with open(out_root / REAL_CAPTURE_JSON, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        with open(out_root / REAL_CAPTURE_MD, "w", encoding="utf-8") as f:
            f.write(render_real_capture_markdown(report))
    return report


def _print_ocr_progress(
    current: int,
    total: int,
    *,
    capture_id: str,
    engine: str,
) -> None:
    """Render a dependency-free console progress bar for long OCR runs."""
    ratio = 1.0 if total <= 0 else min(max(current / total, 0.0), 1.0)
    width = 30
    filled = int(round(width * ratio))
    bar = "#" * filled + "-" * (width - filled)
    label = f"{engine} {capture_id}"[:72]
    print(
        f"\rOCR [{bar}] {current}/{total} ({ratio * 100:5.1f}%) {label:<72}",
        end="",
        file=sys.stderr,
        flush=True,
    )
    if current >= total:
        print(file=sys.stderr, flush=True)


def summarize_real_capture_rows(rows: list[dict]) -> dict:
    """Summarize real-camera OCR rows by engine, condition, and device.

    The headline ``by_ablation_attack`` / ``protection_delta`` views collapse
    OCR engines to the attacker-favorable best-of per capture (a leak counts if
    *any* engine reads it), rather than averaging a weak engine with a strong
    one. ``by_engine`` keeps the raw per-engine numbers for transparency.
    """
    summary = {
        "by_engine": _group_summary(rows, "engine"),
        "by_condition": _group_summary(rows, "condition"),
        "by_device": _group_summary(rows, "device"),
    }
    if any(row.get("ablation") and row.get("attack") for row in rows):
        best = collapse_best_of_engines(rows)
        summary["by_ablation_attack"] = summarize_by(best, ["ablation", "attack"])
        delta = protection_delta(best)
        if delta:
            summary["protection_delta"] = delta
    return summary


def collapse_best_of_engines(rows: list[dict]) -> list[dict]:
    """Reduce per-(capture id) rows across OCR engines to the maximum recovery.

    Models an attacker who runs every available engine and keeps whatever reads
    best; averaging engines would understate recovery and overstate protection.
    """
    by_id: dict[str, list[dict]] = {}
    for row in rows:
        # Group engines of the SAME capture together. The metadata id is shared
        # across engines and unique per capture; fall back to a composite that
        # still separates distinct captures (e.g. different attacks) when absent.
        key = str(row.get("id") or "")
        if not key:
            key = "|".join(
                str(row.get(field, ""))
                for field in ("image", "condition", "ablation", "attack")
            )
        by_id.setdefault(key, []).append(row)
    collapsed: list[dict] = []
    for group in by_id.values():
        best = max(
            group,
            key=lambda r: (float(r.get("exact_match", 0.0)), float(r.get("char_accuracy", 0.0))),
        )
        merged = dict(best)
        merged["engine"] = "best_of"
        merged["char_accuracy"] = max(float(r["char_accuracy"]) for r in group)
        merged["word_accuracy"] = max(float(r.get("word_accuracy", 0.0)) for r in group)
        merged["exact_match"] = max(float(r["exact_match"]) for r in group)
        merged["sensitive_token_recall"] = max(
            float(r.get("sensitive_token_recall", 0.0)) for r in group
        )
        merged["sensitive_token_count"] = max(
            int(r.get("sensitive_token_count", 0)) for r in group
        )
        collapsed.append(merged)
    return collapsed


def protection_delta(rows: list[dict], baseline_ablation: str = "original") -> dict:
    """Per attack, recovery reduction of each ablation vs the unprotected baseline.

    Positive numbers mean the protection lowered attacker recovery relative to
    the ``original`` (unprotected) capture under the same attack — the headline
    paired effect that absolute per-condition means alone don't show.
    """
    by_attack: dict[str, list[dict]] = {}
    for row in rows:
        attack = str(row.get("attack", "")).strip()
        if not attack:
            continue
        by_attack.setdefault(attack, []).append(row)
    out: dict[str, dict] = {}
    for attack, group in by_attack.items():
        base = [r for r in group if str(r.get("ablation")) == baseline_ablation]
        if not base:
            continue
        base_char = float(np.mean([float(r["char_accuracy"]) for r in base]))
        base_exact = float(np.mean([float(r["exact_match"]) for r in base]))
        for ablation in sorted({str(r.get("ablation")) for r in group}):
            sub = [r for r in group if str(r.get("ablation")) == ablation]
            out[f"{ablation}|{attack}"] = {
                "ablation": ablation,
                "attack": attack,
                "char_accuracy_drop": base_char - float(np.mean([float(r["char_accuracy"]) for r in sub])),
                "exact_match_drop": base_exact - float(np.mean([float(r["exact_match"]) for r in sub])),
                "baseline_char_accuracy": base_char,
                "baseline_exact_match": base_exact,
            }
    return out


def summarize_by(rows: list[dict], fields: list[str]) -> dict:
    """Summarize rows by a compound key made from structured metadata fields."""
    if not fields:
        raise ValueError("fields must not be empty")
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        if not all(str(row.get(field, "")).strip() for field in fields):
            continue
        key = "|".join(str(row.get(field, "unknown")) for field in fields)
        grouped.setdefault(key, []).append(row)
    return {
        key: _metric_summary(group)
        for key, group in sorted(grouped.items())
    }


def render_real_capture_markdown(report: dict) -> str:
    lines = [
        "# Real Camera Capture OCR Summary",
        "",
        "This file is generated from manually collected camera photos or video frames.",
        "",
        f"- Captures: {report['config']['n_captures']}",
        f"- OCR rows: {report['config']['n_rows']}",
        "",
    ]
    positions = report.get("positions", [])
    if positions:
        lines.extend([
            "## Position Matrix",
            "",
            "| Position | Distance | Angle | Captures | OCR rows |",
            "|---|---:|---:|---:|---:|",
        ])
        for pos in positions:
            lines.append(
                f"| {pos.get('position', '')} | "
                f"{_fmt_float(pos.get('distance_m'))} m | "
                f"{_fmt_float(pos.get('angle_degrees'))} deg | "
                f"{int(pos.get('n_captures') or 0)} | "
                f"{int(pos.get('n_rows') or 0)} |"
            )
        lines.append("")
    lines.extend([
        "## By Condition",
        "",
        "| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for condition, stats in sorted(report["summary"]["by_condition"].items()):
        condition = _canonical_profile_label(condition)
        lines.append(
            f"| {condition} | {stats['char_accuracy']['count']} | "
            f"{_pct(stats['char_accuracy']['mean'])} | "
            f"{_pct(stats['exact_match']['mean'])} | "
            f"{_pct(stats['sensitive_token_recall']['mean'])} | "
            f"{_pct(stats['leak_rate_char_ge_20pct']['mean'])} |"
        )
    lines.append("")
    if "by_ablation_attack" in report["summary"]:
        lines.extend([
            "## By Ablation And Attack (best-of-engine, attacker-favorable)",
            "",
            "| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |",
            "|---|---|---:|---:|---:|---:|---:|",
        ])
        for key, stats in sorted(report["summary"]["by_ablation_attack"].items()):
            ablation, attack = key.split("|", 1)
            ablation = _canonical_profile_label(ablation)
            lines.append(
                f"| {ablation} | {attack} | {stats['char_accuracy']['count']} | "
                f"{_pct(stats['char_accuracy']['mean'])} | "
                f"{_pct(stats['exact_match']['mean'])} | "
                f"{_pct(stats['sensitive_token_recall']['mean'])} | "
                f"{_pct(stats['leak_rate_char_ge_20pct']['mean'])} |"
            )
        lines.append("")
    if "protection_delta" in report["summary"]:
        lines.extend([
            "## Protection Delta vs Unprotected Baseline (best-of-engine)",
            "",
            "Recovery reduction relative to the `original` capture under the same attack "
            "(higher = stronger protection).",
            "",
            "| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |",
            "|---|---|---:|---:|---:|---:|",
        ])
        for key, stats in sorted(report["summary"]["protection_delta"].items()):
            lines.append(
                f"| {_canonical_profile_label(stats['ablation'])} | {stats['attack']} | "
                f"{_pct(stats['char_accuracy_drop'])} | "
                f"{_pct(stats['exact_match_drop'])} | "
                f"{_pct(stats['baseline_char_accuracy'])} | "
                f"{_pct(stats['baseline_exact_match'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def _canonical_profile_label(value: str) -> str:
    """Normalize the legacy aggressive-profile label for publication display."""
    text = str(value)
    if text == "vlm" or text.startswith("vlm|"):
        return "capture_hardened" + text[len("vlm"):]
    return text


def _group_summary(rows: list[dict], field: str) -> dict:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(str(row.get(field, "unknown")), []).append(row)
    return {
        name: _metric_summary(group)
        for name, group in sorted(grouped.items())
    }


def _metric_summary(group: list[dict]) -> dict:
    return {
        "char_accuracy": _mean_std([float(row["char_accuracy"]) for row in group]),
        "word_accuracy": _mean_std([float(row["word_accuracy"]) for row in group]),
        "exact_match": _mean_std([float(row["exact_match"]) for row in group]),
        "sensitive_token_recall": _mean_std([
            float(row["sensitive_token_recall"])
            for row in group
            if int(row.get("sensitive_token_count", 0)) > 0
        ]),
        "leak_rate_char_ge_20pct": _mean_std([
            float(row["char_accuracy"] >= 0.20) for row in group
        ]),
    }


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _fmt_float(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    text = f"{number:.3f}".rstrip("0").rstrip(".")
    return text or "0"
