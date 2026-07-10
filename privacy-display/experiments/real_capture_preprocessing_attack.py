"""Fixed-grid preprocessing attack for the primary real-capture OCR study."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
from importlib import metadata as importlib_metadata
import json
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
import PIL
from PIL import Image

from experiments.analyze_paper_ocr_clusters import (
    collapse_best_of_engines,
    derive_capture_unit,
    paired_contrast,
)
from src.attack.ocr_evaluator import OCREvaluator, text_recovery_metrics


PREPROCESSOR_MANIFEST: tuple[dict[str, Any], ...] = (
    {"name": "raw", "params": {}},
    {"name": "gamma_0.5", "params": {"gamma": 0.5}},
    {
        "name": "clahe_luma",
        "params": {
            "percentile_low": 1.0,
            "percentile_high": 99.0,
            "clip_limit": 4.0,
            "tile_grid_size": [8, 8],
        },
    },
    {
        "name": "unsharp_mask",
        "params": {"sigma": 1.0, "source_weight": 1.7, "blur_weight": -0.7},
    },
    {
        "name": "adaptive_threshold",
        "params": {"method": "gaussian", "block_size": 31, "constant": 5},
    },
    {
        "name": "upscale_2x",
        "params": {"scale": 2, "interpolation": "bicubic"},
    },
)

_PREPROCESSOR_BY_NAME = {item["name"]: item for item in PREPROCESSOR_MANIFEST}


def preprocess_image(image: np.ndarray, method: str) -> np.ndarray:
    """Apply one predeclared deterministic RGB preprocessing transform."""
    if method not in _PREPROCESSOR_BY_NAME:
        raise ValueError(f"unknown preprocessor: {method}")
    frame = np.ascontiguousarray(image, dtype=np.uint8)
    if frame.ndim != 3 or frame.shape[2] != 3:
        raise ValueError("preprocessing expects an RGB image with shape HxWx3")

    if method == "raw":
        return frame.copy()
    if method == "gamma_0.5":
        gamma = float(_PREPROCESSOR_BY_NAME[method]["params"]["gamma"])
        normalized = frame.astype(np.float32) / 255.0
        return np.rint(np.power(normalized, gamma) * 255.0).clip(0, 255).astype(np.uint8)
    if method == "clahe_luma":
        params = _PREPROCESSOR_BY_NAME[method]["params"]
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        low, high = np.percentile(
            gray,
            [float(params["percentile_low"]), float(params["percentile_high"])],
        )
        if high - low < 1.0:
            high = low + 1.0
        stretched = np.clip(
            (gray.astype(np.float32) - low) / (high - low) * 255.0,
            0,
            255,
        ).astype(np.uint8)
        clahe = cv2.createCLAHE(
            clipLimit=float(params["clip_limit"]),
            tileGridSize=tuple(int(value) for value in params["tile_grid_size"]),
        )
        enhanced = clahe.apply(stretched)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
    if method == "unsharp_mask":
        params = _PREPROCESSOR_BY_NAME[method]["params"]
        blur = cv2.GaussianBlur(frame, (0, 0), float(params["sigma"]))
        sharpened = (
            frame.astype(np.float32) * float(params["source_weight"])
            + blur.astype(np.float32) * float(params["blur_weight"])
        )
        return np.rint(sharpened).clip(0, 255).astype(np.uint8)
    if method == "adaptive_threshold":
        params = _PREPROCESSOR_BY_NAME[method]["params"]
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        thresholded = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            int(params["block_size"]),
            float(params["constant"]),
        )
        return cv2.cvtColor(thresholded, cv2.COLOR_GRAY2RGB)
    if method == "upscale_2x":
        params = _PREPROCESSOR_BY_NAME[method]["params"]
        height, width = frame.shape[:2]
        scale = int(params["scale"])
        return cv2.resize(
            frame,
            (width * scale, height * scale),
            interpolation=cv2.INTER_CUBIC,
        )
    raise AssertionError(f"unhandled preprocessor: {method}")


def load_primary_capture_records(
    canonical_report: str | Path,
    *,
    project_root: str | Path,
) -> list[dict[str, Any]]:
    """Load every archived image contributing to the matched primary estimand."""
    project = Path(project_root).resolve()
    report_path = Path(canonical_report)
    with report_path.open(encoding="utf-8") as handle:
        report = json.load(handle)
    raw_rows = list(report.get("captures") or [])
    rows_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in raw_rows:
        capture_id = str(row.get("id") or "")
        if capture_id:
            rows_by_id.setdefault(capture_id, []).append(row)

    metadata_by_id: dict[str, dict[str, Any]] = {}
    image_root_by_id: dict[str, Path] = {}
    for position in report.get("positions") or []:
        if str(position.get("position")) == "d0.5_a15":
            continue
        source_report_path = _resolve_project_path(
            project,
            str(position.get("source_report") or ""),
        )
        with source_report_path.open(encoding="utf-8") as handle:
            source_report = json.load(handle)
        capture_root = _resolve_project_path(
            project,
            str(source_report.get("capture_dir") or ""),
        )
        metadata_path = capture_root / str(source_report.get("metadata_file") or "metadata.json")
        with metadata_path.open(encoding="utf-8") as handle:
            metadata = json.load(handle)
        for entry in metadata.get("captures") or []:
            capture_id = str(entry.get("id") or "")
            if capture_id:
                metadata_by_id[capture_id] = dict(entry)
                image_root_by_id[capture_id] = capture_root

    best_rows = collapse_best_of_engines(raw_rows)
    selected: list[dict[str, Any]] = []
    for best_row in best_rows:
        unit = derive_capture_unit(best_row)
        if (
            unit.attack != "short"
            or unit.position == "d0.5_a15"
            or unit.profile not in {"original", "deployed", "high_suppression"}
        ):
            continue
        capture_id = str(best_row.get("id") or "")
        if capture_id not in metadata_by_id:
            raise ValueError(f"missing metadata for selected capture: {capture_id}")
        entry = dict(metadata_by_id[capture_id])
        image_path = image_root_by_id[capture_id] / str(entry["image"])
        if not image_path.is_file():
            raise FileNotFoundError(f"missing selected capture image: {image_path}")
        entry.update({
            "id": capture_id,
            "profile": unit.profile,
            "position": unit.position,
            "content_item": unit.content_item,
            "repeat_index": unit.repeat_index,
            "image_path": image_path,
            "raw_rows": sorted(
                (dict(row) for row in rows_by_id[capture_id]),
                key=lambda row: str(row.get("engine", "")),
            ),
        })
        selected.append(entry)
    return sorted(selected, key=lambda entry: str(entry["id"]))


def summarize_primary_selection(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Count archived images and matched analysis units by primary profile."""
    capture_counts = Counter(str(record["profile"]) for record in records)
    units_by_profile: dict[str, set[tuple[str, str, str]]] = {}
    for record in records:
        profile = str(record["profile"])
        units_by_profile.setdefault(profile, set()).add((
            str(record["content_item"]),
            str(record["position"]),
            str(record["repeat_index"]),
        ))
    return {
        "positions": sorted({str(record["position"]) for record in records}),
        "capture_counts": {
            profile: capture_counts.get(profile, 0)
            for profile in ("original", "deployed", "high_suppression")
        },
        "matched_unit_counts": {
            profile: len(units_by_profile.get(profile, set()))
            for profile in ("original", "deployed", "high_suppression")
        },
    }


def checkpoint_row_key(row: dict[str, Any]) -> tuple[str, str, str]:
    """Return the unique identity of one OCR preprocessing cell."""
    return (
        str(row.get("id") or ""),
        str(row.get("preprocessor") or ""),
        str(row.get("engine") or ""),
    )


def import_raw_checkpoint_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reuse canonical raw OCR rows without rerunning an unchanged image."""
    imported: list[dict[str, Any]] = []
    for record in records:
        for raw in record.get("raw_rows") or []:
            row = dict(raw)
            row.update({
                "id": str(record["id"]),
                "profile": str(record["profile"]),
                "position": str(record["position"]),
                "content_item": str(record["content_item"]),
                "repeat_index": str(record["repeat_index"]),
                "preprocessor": "raw",
                "source": "canonical_raw_archive",
            })
            imported.append(row)
    return sorted(imported, key=checkpoint_row_key)


def load_checkpoint_rows(path: str | Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    """Load a JSONL checkpoint and reject ambiguous duplicate cells."""
    checkpoint = Path(path)
    if not checkpoint.exists():
        return {}
    rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    with checkpoint.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            key = checkpoint_row_key(row)
            if not all(key):
                raise ValueError(f"invalid checkpoint cell at line {line_number}: {key}")
            if key in rows:
                raise ValueError(f"duplicate checkpoint cell at line {line_number}: {key}")
            rows[key] = row
    return rows


def pending_jobs(
    records: list[dict[str, Any]],
    *,
    engines: list[str],
    preprocessors: list[str],
    completed_keys: set[tuple[str, str, str]],
) -> list[dict[str, Any]]:
    """Build deterministic missing OCR jobs for resumable execution."""
    jobs: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: str(item["id"])):
        for preprocessor in preprocessors:
            if preprocessor not in _PREPROCESSOR_BY_NAME:
                raise ValueError(f"unknown preprocessor: {preprocessor}")
            for engine in engines:
                key = (str(record["id"]), preprocessor, engine)
                if key not in completed_keys:
                    jobs.append({
                        "record": record,
                        "preprocessor": preprocessor,
                        "engine": engine,
                    })
    return jobs


def evaluate_job(
    job: dict[str, Any],
    *,
    evaluator: Any,
) -> dict[str, Any]:
    """Run one transformed OCR cell and preserve failures as auditable rows."""
    record = job["record"]
    preprocessor = str(job["preprocessor"])
    engine = str(job["engine"])
    with Image.open(Path(record["image_path"])) as image:
        rgb = np.asarray(image.convert("RGB"))
    transformed = preprocess_image(rgb, preprocessor)
    started = time.perf_counter()
    error = ""
    try:
        recognized = str(evaluator.recognize(transformed, engine))
    except Exception as exc:
        recognized = ""
        error = str(exc)
    duration = time.perf_counter() - started
    metrics = text_recovery_metrics(recognized, str(record["truth"]))
    return {
        "id": str(record["id"]),
        "profile": str(record["profile"]),
        "ablation": str(record["profile"]),
        "attack": "short",
        "position": str(record["position"]),
        "content_item": str(record["content_item"]),
        "repeat_index": str(record["repeat_index"]),
        "image": str(record.get("image") or Path(record["image_path"]).name),
        "preprocessor": preprocessor,
        "engine": engine,
        "char_accuracy": metrics["char_accuracy"],
        "word_accuracy": metrics["word_accuracy"],
        "exact_match": metrics["exact_match"],
        "sensitive_token_recall": metrics["sensitive_token_recall"],
        "sensitive_token_count": metrics["sensitive_token_count"],
        "recognized_text": recognized[:240],
        "ocr_error": error,
        "duration_seconds": duration,
        "source": "generated_preprocessing_attack",
    }


def append_checkpoint_row(
    path: str | Path,
    row: dict[str, Any],
    *,
    completed_keys: set[tuple[str, str, str]],
) -> None:
    """Durably append one new result cell and update the in-memory key set."""
    key = checkpoint_row_key(row)
    if key in completed_keys:
        raise ValueError(f"checkpoint cell already exists: {key}")
    checkpoint = Path(path)
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    with checkpoint.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    completed_keys.add(key)


def collapse_attacker_oracle(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse engines/transforms to independent attacker-favorable metrics."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        capture_id = str(row.get("id") or "")
        if not capture_id:
            raise ValueError("attacker-oracle row is missing capture id")
        grouped.setdefault(capture_id, []).append(row)

    metrics = (
        "char_accuracy",
        "word_accuracy",
        "exact_match",
        "sensitive_token_recall",
    )
    collapsed: list[dict[str, Any]] = []
    for capture_id, capture_rows in sorted(grouped.items()):
        ordered = sorted(
            capture_rows,
            key=lambda row: (
                str(row.get("preprocessor", "")),
                str(row.get("engine", "")),
            ),
        )
        merged = dict(ordered[0])
        merged.update({
            "id": capture_id,
            "engine": "best_of",
            "preprocessor": "best_of",
            "metric_sources": {},
        })
        for metric in metrics:
            source = max(ordered, key=lambda row: float(row.get(metric) or 0.0))
            merged[metric] = max(float(row.get(metric) or 0.0) for row in ordered)
            merged["metric_sources"][metric] = {
                "preprocessor": str(source.get("preprocessor") or ""),
                "engine": str(source.get("engine") or ""),
            }
        merged["sensitive_token_count"] = max(
            int(row.get("sensitive_token_count") or 0) for row in ordered
        )
        collapsed.append(merged)
    return collapsed


def validate_complete_matrix(
    records: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    *,
    engines: list[str],
    preprocessors: list[str],
) -> None:
    """Require exactly one result for every selected capture/grid/engine cell."""
    required = {
        (str(record["id"]), preprocessor, engine)
        for record in records
        for preprocessor in preprocessors
        for engine in engines
    }
    seen: set[tuple[str, str, str]] = set()
    duplicates: set[tuple[str, str, str]] = set()
    for row in rows:
        key = checkpoint_row_key(row)
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    missing = sorted(required - seen)
    unexpected = sorted(seen - required)
    if missing or unexpected or duplicates:
        raise ValueError(
            "incomplete preprocessing matrix: "
            f"missing={len(missing)} unexpected={len(unexpected)} "
            f"duplicates={len(duplicates)}; "
            f"first_missing={missing[:1]} first_unexpected={unexpected[:1]} "
            f"first_duplicate={sorted(duplicates)[:1]}"
        )


def build_attack_report(
    records: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    *,
    engines: list[str],
    preprocessors: list[str],
    bootstrap_resamples: int = 2000,
    source_archive: str | Path | None = None,
) -> dict[str, Any]:
    """Build raw and fixed-grid attacker oracles on one complete matrix."""
    validate_complete_matrix(
        records,
        rows,
        engines=engines,
        preprocessors=preprocessors,
    )
    raw_rows = [row for row in rows if row.get("preprocessor") == "raw"]
    raw_oracle = collapse_attacker_oracle(raw_rows)
    adaptive_oracle = collapse_attacker_oracle(rows)
    source_path = Path(source_archive) if source_archive is not None else None
    return {
        "schema_version": 1,
        "source": {
            "ocr_archive": str(source_path) if source_path is not None else None,
            "ocr_archive_sha256": (
                hashlib.sha256(source_path.read_bytes()).hexdigest()
                if source_path is not None else None
            ),
        },
        "runtime_versions": _runtime_versions(),
        "audit": {
            "matrix_row_count": len(rows),
            "ocr_error_count": sum(bool(str(row.get("ocr_error") or "").strip()) for row in rows),
            "generated_duration_seconds": sum(float(row.get("duration_seconds") or 0.0) for row in rows),
        },
        "config": {
            "engines": list(engines),
            "preprocessors": list(preprocessors),
            "preprocessor_manifest": [
                _PREPROCESSOR_BY_NAME[name] for name in preprocessors
            ],
            "selection": summarize_primary_selection(records),
            "bootstrap_resamples": bootstrap_resamples,
            "attacker_aggregation": "metricwise_best_of_preprocessor_and_engine_per_capture",
        },
        "oracles": {
            "raw": _oracle_summary(raw_oracle, bootstrap_resamples),
            "best_preprocessing_engine": _oracle_summary(
                adaptive_oracle,
                bootstrap_resamples,
            ),
        },
    }


def validate_no_ocr_errors(rows: list[dict[str, Any]]) -> None:
    """Prevent silent finalization when any transformed OCR cell failed."""
    failures = [row for row in rows if str(row.get("ocr_error") or "").strip()]
    if failures:
        preview = [
            {
                "key": checkpoint_row_key(row),
                "error": str(row.get("ocr_error")),
            }
            for row in failures[:3]
        ]
        raise ValueError(f"OCR errors remain in preprocessing matrix: {len(failures)} {preview}")


def retain_rows_for_retry(
    rows: list[dict[str, Any]],
    *,
    engines: list[str],
    preprocessors: list[str],
) -> list[dict[str, Any]]:
    """Drop failed cells only inside the requested matrix, preserving all other work."""
    return [
        row for row in rows
        if not (
            str(row.get("engine")) in engines
            and str(row.get("preprocessor")) in preprocessors
            and bool(str(row.get("ocr_error") or "").strip())
        )
    ]


def render_attack_markdown(report: dict[str, Any]) -> str:
    """Render the matched and descriptive attack summaries for audit/reuse."""
    lines = [
        "# Real-Capture Fixed-Grid Preprocessing Attack",
        "",
        "The primary rows use matched content/position/repeat units. Duplicate "
        "readability-priority captures are averaged inside their matched unit.",
        "",
        "| Oracle | Profile | Matched units | Matched mean | Difference vs original | 95% interval |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for oracle_key, oracle_label in (
        ("raw", "Raw best-of-engine"),
        ("best_preprocessing_engine", "Best-of-preprocessing-and-engine"),
    ):
        oracle = report["oracles"][oracle_key]
        deployed = oracle["contrasts"]["original_minus_deployed"]
        hardened = oracle["contrasts"]["original_minus_high_suppression"]
        lines.extend([
            _matched_markdown_row(
                oracle_label,
                "Original (unprotected)",
                deployed,
                baseline=True,
            ),
            _matched_markdown_row(
                oracle_label,
                "Readability-priority",
                deployed,
                baseline=False,
            ),
            _matched_markdown_row(
                oracle_label,
                "High-suppression",
                hardened,
                baseline=False,
            ),
        ])
    lines.extend([
        "",
        "## All-Available Descriptive Means",
        "",
        "| Oracle | Profile | Captures | Character recovery | Exact match |",
        "|---|---|---:|---:|---:|",
    ])
    for oracle_key, oracle_label in (
        ("raw", "Raw best-of-engine"),
        ("best_preprocessing_engine", "Best-of-preprocessing-and-engine"),
    ):
        descriptive = report["oracles"][oracle_key]["descriptive_all_available"]
        for profile in ("original", "deployed", "high_suppression", "vlm"):
            if profile not in descriptive:
                continue
            stats = descriptive[profile]
            lines.append(
                f"| {oracle_label} | {profile} | {stats['capture_count']} | "
                f"{stats['char_accuracy_mean'] * 100:.1f}% | "
                f"{stats['exact_match_mean'] * 100:.1f}% |"
            )
    return "\n".join(lines) + "\n"


def _matched_markdown_row(
    oracle_label: str,
    profile_label: str,
    contrast: dict[str, Any],
    *,
    baseline: bool,
) -> str:
    mean_value = (
        contrast["matched_baseline_mean"]
        if baseline
        else contrast["matched_treatment_mean"]
    )
    difference = "--" if baseline else f"{contrast['estimate_percent']:.1f} pp"
    interval = (
        "--"
        if baseline
        else (
            f"[{contrast['ci95_percent']['low']:.1f}, "
            f"{contrast['ci95_percent']['high']:.1f}]"
        )
    )
    return (
        f"| {oracle_label} | {profile_label} | {contrast['matched_unit_count']} | "
        f"{mean_value * 100:.1f}% | {difference} | {interval} |"
    )


def _oracle_summary(
    rows: list[dict[str, Any]],
    bootstrap_resamples: int,
) -> dict[str, Any]:
    contrasts = {}
    for treatment, label in (
        ("deployed", "original_minus_deployed"),
        ("high_suppression", "original_minus_high_suppression"),
    ):
        contrasts[label] = paired_contrast(
            rows,
            baseline_profile="original",
            treatment_profile=treatment,
            attack="short",
            exclude_positions=[],
            resamples=bootstrap_resamples,
        )
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("profile") or row.get("ablation") or ""), []).append(row)
    descriptive = {}
    for profile, group in sorted(grouped.items()):
        descriptive[profile] = {
            "capture_count": len(group),
            "char_accuracy_mean": float(np.mean([
                float(row.get("char_accuracy") or 0.0) for row in group
            ])),
            "exact_match_mean": float(np.mean([
                float(row.get("exact_match") or 0.0) for row in group
            ])),
        }
    return {
        "descriptive_all_available": descriptive,
        "contrasts": contrasts,
        "captures": rows,
    }


def _resolve_project_path(project_root: Path, stored_path: str) -> Path:
    normalized = stored_path.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() and path.exists():
        return path
    candidate = project_root / path
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"archived project path does not exist: {stored_path}")


def _runtime_versions() -> dict[str, str | None]:
    packages = {}
    for package in ("pytesseract", "easyocr", "surya-ocr"):
        try:
            packages[package] = importlib_metadata.version(package)
        except importlib_metadata.PackageNotFoundError:
            packages[package] = None
    try:
        import pytesseract

        tesseract_executable = str(pytesseract.get_tesseract_version())
    except Exception:
        tesseract_executable = None
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "opencv": cv2.__version__,
        "pillow": PIL.__version__,
        "tesseract_executable": tesseract_executable,
        **packages,
    }


def _write_initial_checkpoint(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="experiments/results/real_capture_ocr.json")
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--checkpoint",
        default="experiments/results/real_capture_preprocessing_rows/matrix.jsonl",
    )
    parser.add_argument(
        "--json-out",
        default="experiments/results/real_capture_preprocessing_attack.json",
    )
    parser.add_argument(
        "--md-out",
        default="experiments/results/real_capture_preprocessing_attack.md",
    )
    parser.add_argument(
        "--engines",
        default="tesseract,easyocr,surya",
        help="Comma-separated fixed OCR engine list.",
    )
    parser.add_argument(
        "--preprocessors",
        default=",".join(item["name"] for item in PREPROCESSOR_MANIFEST),
        help="Comma-separated fixed transform list.",
    )
    parser.add_argument("--ocr-timeout", type=float, default=30.0)
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Parallel workers; values above 1 are supported only for Tesseract-only runs.",
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=0,
        help="Process at most this many missing cells; 0 means all.",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Import raw archive rows, print matrix status, and do not run OCR.",
    )
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="Remove failed cells in the requested matrix from the checkpoint and rerun them.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    source_archive = Path(args.input)
    if not source_archive.is_absolute():
        source_archive = project_root / source_archive
    checkpoint = Path(args.checkpoint)
    if not checkpoint.is_absolute():
        checkpoint = project_root / checkpoint
    json_out = Path(args.json_out)
    if not json_out.is_absolute():
        json_out = project_root / json_out
    md_out = Path(args.md_out)
    if not md_out.is_absolute():
        md_out = project_root / md_out
    engines = [item.strip() for item in args.engines.split(",") if item.strip()]
    preprocessors = [item.strip() for item in args.preprocessors.split(",") if item.strip()]
    unknown = sorted(set(preprocessors) - set(_PREPROCESSOR_BY_NAME))
    if unknown:
        raise ValueError(f"unknown preprocessors: {unknown}")

    records = load_primary_capture_records(source_archive, project_root=project_root)
    if not checkpoint.exists():
        imported = import_raw_checkpoint_rows(records) if "raw" in preprocessors else []
        _write_initial_checkpoint(checkpoint, imported)
        print(f"Initialized checkpoint with {len(imported)} canonical raw rows: {checkpoint}")

    if args.retry_errors and checkpoint.exists():
        existing_rows = list(load_checkpoint_rows(checkpoint).values())
        retained_rows = retain_rows_for_retry(
            existing_rows,
            engines=engines,
            preprocessors=preprocessors,
        )
        removed = len(existing_rows) - len(retained_rows)
        _write_initial_checkpoint(checkpoint, retained_rows)
        print(f"Removed {removed} failed requested cells for retry.")

    completed = load_checkpoint_rows(checkpoint)
    jobs = pending_jobs(
        records,
        engines=engines,
        preprocessors=preprocessors,
        completed_keys=set(completed),
    )
    total_required = len(records) * len(engines) * len(preprocessors)
    print(
        f"Selection={summarize_primary_selection(records)} required={total_required} "
        f"completed={len(completed)} pending={len(jobs)}"
    )
    print(f"Runtime versions={_runtime_versions()}")
    if args.prepare_only:
        return

    if args.workers < 1:
        raise ValueError("workers must be at least 1")
    if args.workers > 1 and engines != ["tesseract"]:
        raise ValueError("parallel workers are restricted to a Tesseract-only run")
    evaluator = OCREvaluator(engines=engines, timeout=args.ocr_timeout)
    run_jobs = jobs[: args.max_jobs] if args.max_jobs > 0 else jobs
    completed_keys = set(completed)
    if args.workers == 1:
        evaluated_rows = (evaluate_job(job, evaluator=evaluator) for job in run_jobs)
    else:
        executor = ThreadPoolExecutor(max_workers=args.workers)
        evaluated_rows = executor.map(
            lambda job: evaluate_job(job, evaluator=evaluator),
            run_jobs,
        )
    try:
        for index, row in enumerate(evaluated_rows, start=1):
            append_checkpoint_row(checkpoint, row, completed_keys=completed_keys)
            if index == 1 or index % 25 == 0 or index == len(run_jobs):
                print(
                    f"Processed {index}/{len(run_jobs)} this run; "
                    f"cell={checkpoint_row_key(row)} error={bool(row['ocr_error'])} "
                    f"duration={row['duration_seconds']:.2f}s",
                    flush=True,
                )
    finally:
        if args.workers > 1:
            executor.shutdown(wait=True)

    selected_ids = {str(record["id"]) for record in records}
    final_rows = [
        row for row in load_checkpoint_rows(checkpoint).values()
        if str(row.get("id")) in selected_ids
        and str(row.get("engine")) in engines
        and str(row.get("preprocessor")) in preprocessors
    ]
    remaining = pending_jobs(
        records,
        engines=engines,
        preprocessors=preprocessors,
        completed_keys={checkpoint_row_key(row) for row in final_rows},
    )
    if remaining:
        print(f"Checkpoint saved; {len(remaining)} cells remain.")
        return

    validate_no_ocr_errors(final_rows)
    report = build_attack_report(
        records,
        final_rows,
        engines=engines,
        preprocessors=preprocessors,
        bootstrap_resamples=args.bootstrap_resamples,
        source_archive=source_archive,
    )
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(render_attack_markdown(report), encoding="utf-8")
    print(f"Wrote {json_out}")
    print(f"Wrote {md_out}")


if __name__ == "__main__":
    main()
