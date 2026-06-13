"""
Publication-facing result summary builder.

This module consolidates experiment JSON files into a compact, auditable
summary that can be used when updating thesis or IEEE Access tables. It does
not rerun experiments or call online services.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


OCR_FILE = "corpus_multi_engine.json"
STRONG_ATTACK_FILE = "corpus_strong_camera_attack.json"
DETECTION_FILE = "detection_attack_yolo.json"
VIEW_ATTACK_FILE = "view_attack.json"
VLM_FILE = "vlm_qwen3_siliconflow.json"
REAL_CAPTURE_FILE = "real_capture_ocr.json"
SUMMARY_JSON = "publication_summary.json"
SUMMARY_MD = "publication_summary.md"

STRONG_ATTACK_ORDER = [
    "global_shutter_slot0",
    "differential_luma",
    "differential_blue",
    "temporal_average_cycle",
    "phase_search_mean",
    "phase_search_max",
    "blue_channel_max",
]
OCR_ENGINE_ORDER = ["tesseract", "easyocr", "paddleocr"]


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_publication_summary(results_dir: str | Path = "experiments/results") -> dict:
    """Build a summary from available result artifacts."""
    root = Path(results_dir)
    ocr = load_json(root / OCR_FILE)
    strong = load_json(root / STRONG_ATTACK_FILE)
    detection = _load_optional(root / DETECTION_FILE)
    view_attack = _load_optional(root / VIEW_ATTACK_FILE)
    vlm = _load_optional(root / VLM_FILE)
    real_capture = _load_optional(root / REAL_CAPTURE_FILE)

    summary = {
        "source_files": {
            "ocr": OCR_FILE,
            "strong_camera": STRONG_ATTACK_FILE,
            "detection": DETECTION_FILE if detection is not None else None,
            "view_attack": VIEW_ATTACK_FILE if view_attack is not None else None,
            "vlm": VLM_FILE if vlm is not None else None,
            "real_capture": REAL_CAPTURE_FILE if real_capture is not None else None,
        },
        "ocr": summarize_ocr(ocr),
        "strong_camera": summarize_strong_camera(strong),
        "detection": summarize_detection(detection),
        "view_attack": summarize_view_attack(view_attack),
        "vlm": summarize_vlm(vlm),
        "real_capture": summarize_real_capture(real_capture),
    }
    return summary


def summarize_ocr(report: dict) -> dict:
    """Summarize corpus OCR results by engine."""
    engines = []
    ordered = [name for name in OCR_ENGINE_ORDER if name in report]
    ordered.extend(sorted(name for name in report if name not in ordered))
    for engine in ordered:
        entry = report[engine]
        engines.append({
            "engine": engine,
            "n_samples": int(entry.get("n_samples", 0)),
            "n_categories": int(entry.get("n_categories", 0)),
            "original_mean": _num(entry.get("original_mean")),
            "original_std": _num(entry.get("original_std")),
            "original_ci95": _ci(entry.get("original_ci95", {})),
            "subframe_mean": _num(entry.get("subframe_mean")),
            "subframe_std": _num(entry.get("subframe_std")),
            "subframe_ci95": _ci(entry.get("subframe_ci95", {})),
            "paired_reduction_mean": _num(entry.get("paired_reduction", {}).get("mean")),
            "paired_reduction_ci95": _ci(entry.get("paired_reduction", {}).get("ci95", {})),
            "subframe_word_accuracy": _num(
                entry.get("recovery_metrics", {})
                .get("word_accuracy", {})
                .get("subframe", {})
                .get("mean")
            ),
            "subframe_exact_match": _num(
                entry.get("recovery_metrics", {})
                .get("exact_match", {})
                .get("subframe", {})
                .get("mean")
            ),
            "subframe_sensitive_token_recall": _num(
                entry.get("recovery_metrics", {})
                .get("sensitive_token_recall", {})
                .get("subframe", {})
                .get("mean")
            ),
            "sensitive_token_samples": int(
                entry.get("recovery_metrics", {})
                .get("sensitive_token_recall", {})
                .get("n_samples_with_sensitive_tokens", 0)
            ),
        })
    return {"engines": engines}


def summarize_strong_camera(report: dict) -> dict:
    """Summarize strong camera attack report."""
    attacks = report.get("summary", {}).get("attacks", {})
    rows = []
    ordered = [name for name in STRONG_ATTACK_ORDER if name in attacks]
    ordered.extend(sorted(name for name in attacks if name not in ordered))
    for name in ordered:
        entry = attacks[name]
        rows.append({
            "attack": name,
            "char_accuracy": _stat_mean(entry.get("char_accuracy")),
            "char_accuracy_ci95": _ci(entry.get("char_accuracy", {}).get("ci95", {})),
            "exact_match": _stat_mean(entry.get("exact_match")),
            "sensitive_token_recall": _stat_mean(entry.get("sensitive_token_recall", {}).get("stats")),
            "leak_rate_char_ge_20pct": _stat_mean(entry.get("leak_rate_char_ge_20pct")),
        })

    best = report.get("summary", {}).get("best_attack_per_sample", {})
    return {
        "config": report.get("config", {}),
        "attacks": rows,
        "best_attack_per_sample": {
            "char_accuracy": _stat_mean(best.get("char_accuracy")),
            "char_accuracy_ci95": _ci(best.get("char_accuracy", {}).get("ci95", {})),
            "exact_match": _stat_mean(best.get("exact_match")),
            "sensitive_token_recall": _stat_mean(best.get("sensitive_token_recall", {}).get("stats")),
            "leak_rate_char_ge_20pct": _stat_mean(best.get("leak_rate_char_ge_20pct")),
            "attack_wins": best.get("attack_wins", {}),
        },
    }


def summarize_detection(report: dict | None) -> dict:
    if report is None:
        return {"available": False, "reason": "missing_result_file"}
    return {
        "available": True,
        "engine": report.get("engine", ""),
        "model": report.get("yolo", {}).get("model", ""),
        "reference_boxes": int(report.get("original_reference_boxes", 0)),
        "single_subframe": _detection_row(report.get("single_subframe", {})),
        "temporal_average": _detection_row(report.get("temporal_average", {})),
    }


def summarize_view_attack(report: dict | None) -> dict:
    if report is None:
        return {"available": False, "reason": "missing_result_file"}
    return {
        "available": True,
        "angle_degrees": _num(report.get("angle_degrees")),
        "frontal_ocr_char_acc": _num(report.get("frontal_temporal_average", {}).get("ocr_char_acc")),
        "off_axis_ocr_char_acc": _num(report.get("off_axis_temporal_average", {}).get("ocr_char_acc")),
        "off_axis_corrected_ocr_char_acc": _num(report.get("off_axis_corrected", {}).get("ocr_char_acc")),
        "off_axis_ssim_drop": _num(report.get("off_axis_ssim_drop")),
        "conclusion": report.get("conclusion", ""),
    }


def summarize_vlm(report: dict | None) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": VLM_FILE,
            "interpretation": "Online VLM benchmark is implemented but no live result has been generated.",
        }
    samples = report.get("samples", [])
    error_count = int(sum(1 for row in samples if row.get("vlm_error")))
    successful_calls = len(samples) - error_count
    if samples and successful_calls == 0:
        return {
            "available": False,
            "reason": "all_calls_failed",
            "expected_file": VLM_FILE,
            "config": report.get("config", {}),
            "call_status": {
                "total_calls": len(samples),
                "successful_calls": 0,
                "error_calls": error_count,
            },
            "interpretation": "VLM result file exists, but all live API calls failed; do not cite recovery metrics.",
        }
    best = report.get("summary", {}).get("best_attack_per_sample", {})
    return {
        "available": True,
        "config": report.get("config", {}),
        "call_status": {
            "total_calls": len(samples),
            "successful_calls": successful_calls,
            "error_calls": error_count,
        },
        "best_attack_per_sample": {
            "char_accuracy": _stat_mean(best.get("char_accuracy")),
            "exact_match": _stat_mean(best.get("exact_match")),
            "sensitive_token_recall": _stat_mean(best.get("sensitive_token_recall", {}).get("stats")),
            "vlm_read_success_rate": _stat_mean(best.get("vlm_read_success_rate")),
            "attack_wins": best.get("attack_wins", {}),
        },
    }


def summarize_real_capture(report: dict | None) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": REAL_CAPTURE_FILE,
            "interpretation": "Real camera capture analysis is implemented, but no real photo/video-frame result has been generated.",
        }
    conditions = []
    for condition, stats in sorted(report.get("summary", {}).get("by_condition", {}).items()):
        conditions.append({
            "condition": condition,
            "count": int(stats.get("char_accuracy", {}).get("count", 0)),
            "char_accuracy": _stat_mean(stats.get("char_accuracy")),
            "exact_match": _stat_mean(stats.get("exact_match")),
            "sensitive_token_recall": _stat_mean(stats.get("sensitive_token_recall")),
            "leak_rate_char_ge_20pct": _stat_mean(stats.get("leak_rate_char_ge_20pct")),
        })
    return {
        "available": True,
        "config": report.get("config", {}),
        "conditions": conditions,
    }


def render_markdown(summary: dict) -> str:
    """Render a compact Markdown report suitable for thesis/paper table checks."""
    lines = [
        "# Publication Result Summary",
        "",
        "This file is generated from machine-readable experiment JSON artifacts.",
        "",
        "## Source Files",
        "",
    ]
    for key, value in summary["source_files"].items():
        lines.append(f"- {key}: `{value or 'missing'}`")

    lines.extend([
        "",
        "## OCR Corpus",
        "",
        "| Engine | Samples | Original char acc | Subframe char acc | Paired reduction | Subframe word/exact/sensitive |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in summary["ocr"]["engines"]:
        lines.append(
            f"| {row['engine']} | {row['n_samples']} | "
            f"{_pct_ci(row['original_mean'], row['original_ci95'])} | "
            f"{_pct_ci(row['subframe_mean'], row['subframe_ci95'])} | "
            f"{_pct_ci(row['paired_reduction_mean'], row['paired_reduction_ci95'])} | "
            f"{_pct(row['subframe_word_accuracy'])} / "
            f"{_pct(row['subframe_exact_match'])} / "
            f"{_pct(row['subframe_sensitive_token_recall'])} |"
        )

    lines.extend([
        "",
        "## Strong Camera Attacks",
        "",
        "| Attack | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in summary["strong_camera"]["attacks"]:
        lines.append(
            f"| {row['attack']} | {_pct_ci(row['char_accuracy'], row['char_accuracy_ci95'])} | "
            f"{_pct(row['exact_match'])} | {_pct(row['sensitive_token_recall'])} | "
            f"{_pct(row['leak_rate_char_ge_20pct'])} |"
        )
    best = summary["strong_camera"]["best_attack_per_sample"]
    lines.append(
        f"| **best_attack_per_sample** | **{_pct_ci(best['char_accuracy'], best['char_accuracy_ci95'])}** | "
        f"**{_pct(best['exact_match'])}** | **{_pct(best['sensitive_token_recall'])}** | "
        f"**{_pct(best['leak_rate_char_ge_20pct'])}** |"
    )

    detection = summary["detection"]
    lines.extend(["", "## Detection Attack", ""])
    if detection["available"]:
        lines.extend([
            f"- Engine: `{detection['engine']}` / `{detection['model']}`",
            f"- Single subframe mAP50: {_pct(detection['single_subframe']['map50'])}; recall: {_pct(detection['single_subframe']['recall'])}",
            f"- Temporal average mAP50: {_pct(detection['temporal_average']['map50'])}; recall: {_pct(detection['temporal_average']['recall'])}",
        ])
    else:
        lines.append("- Missing detection result file.")

    view = summary["view_attack"]
    lines.extend(["", "## View Attack", ""])
    if view["available"]:
        lines.extend([
            f"- Angle: {view['angle_degrees']:.1f} degrees",
            f"- Frontal/off-axis/corrected OCR: {_pct(view['frontal_ocr_char_acc'])} / {_pct(view['off_axis_ocr_char_acc'])} / {_pct(view['off_axis_corrected_ocr_char_acc'])}",
            f"- Off-axis SSIM drop: {view['off_axis_ssim_drop']:.3f}",
        ])
    else:
        lines.append("- Missing view-attack result file.")

    vlm = summary["vlm"]
    lines.extend(["", "## VLM Readability", ""])
    if vlm["available"]:
        best_vlm = vlm["best_attack_per_sample"]
        lines.extend([
            f"- Model: `{vlm['config'].get('model', '')}`",
            f"- Best attack char recovery: {_pct(best_vlm['char_accuracy'])}",
            f"- Best attack read success rate: {_pct(best_vlm['vlm_read_success_rate'])}",
        ])
    else:
        lines.append(f"- Not available: {vlm['interpretation']}")

    real = summary["real_capture"]
    lines.extend(["", "## Real Camera Capture", ""])
    if real["available"]:
        lines.extend([
            f"- Captures: {real['config'].get('n_captures', 0)}",
            "",
            "| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for row in real["conditions"]:
            lines.append(
                f"| {row['condition']} | {row['count']} | {_pct(row['char_accuracy'])} | "
                f"{_pct(row['exact_match'])} | {_pct(row['sensitive_token_recall'])} | "
                f"{_pct(row['leak_rate_char_ge_20pct'])} |"
            )
    else:
        lines.append(f"- Not available: {real['interpretation']}")

    lines.append("")
    return "\n".join(lines)


def write_publication_summary(
    results_dir: str | Path = "experiments/results",
    summary: dict | None = None,
) -> dict:
    root = Path(results_dir)
    root.mkdir(parents=True, exist_ok=True)
    summary = summary or build_publication_summary(root)
    with open(root / SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(root / SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write(render_markdown(summary))
    return summary


def _load_optional(path: Path) -> Any | None:
    if not path.exists():
        return None
    return load_json(path)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ci(value: dict) -> dict:
    return {
        "low": _num(value.get("low")),
        "high": _num(value.get("high")),
        "confidence": _num(value.get("confidence"), 0.95),
        "method": value.get("method", ""),
    }


def _stat_mean(value: dict | None) -> float:
    if not isinstance(value, dict):
        return 0.0
    return _num(value.get("mean"))


def _detection_row(value: dict) -> dict:
    return {
        "precision": _num(value.get("precision")),
        "recall": _num(value.get("recall")),
        "f1": _num(value.get("f1")),
        "map50": _num(value.get("map50")),
        "prediction_boxes": int(value.get("prediction_boxes", 0)),
        "status": value.get("status", ""),
    }


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _pct_ci(value: float, ci: dict) -> str:
    if ci.get("method"):
        return f"{_pct(value)} ({_pct(ci['low'])}-{_pct(ci['high'])})"
    return _pct(value)
