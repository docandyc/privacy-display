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


def summarize_real_capture_rows(rows: list[dict]) -> dict:
    """Summarize real-camera OCR rows by engine, condition, and device."""
    return {
        "by_engine": _group_summary(rows, "engine"),
        "by_condition": _group_summary(rows, "condition"),
        "by_device": _group_summary(rows, "device"),
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
        "## By Condition",
        "",
        "| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for condition, stats in sorted(report["summary"]["by_condition"].items()):
        lines.append(
            f"| {condition} | {stats['char_accuracy']['count']} | "
            f"{_pct(stats['char_accuracy']['mean'])} | "
            f"{_pct(stats['exact_match']['mean'])} | "
            f"{_pct(stats['sensitive_token_recall']['mean'])} | "
            f"{_pct(stats['leak_rate_char_ge_20pct']['mean'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def _group_summary(rows: list[dict], field: str) -> dict:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(str(row.get(field, "unknown")), []).append(row)
    return {
        name: {
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
        for name, group in sorted(grouped.items())
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
