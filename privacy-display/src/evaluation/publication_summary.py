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
COCO_DETECTION_FILE = "coco_detection_attack.json"
MOT_VIDEO_DETECTION_FILE = "mot_video_detection.json"
MOT_TRACKING_FILE = "mot_tracking_attack.json"
VIEW_ATTACK_FILE = "view_attack.json"
VLM_FILE = "vlm_qwen3_siliconflow.json"
REAL_CAPTURE_FILE = "real_capture_ocr.json"
REAL_CAPTURE_COCO_DETECTION_FILE = "real_capture_coco_detection.json"
REAL_CAPTURE_MOT_DETECTION_FILE = "real_capture_mot_detection.json"
REAL_CAPTURE_MOT_TRACKING_FILE = "real_capture_mot_tracking.json"
SUPPLEMENTAL_FILES = {
    "component_ablation": "component_ablation.json",
    "recognizer_generalization": "recognizer_generalization.json",
    "perceptual_ablation": "perceptual_ablation.json",
    "pareto_sweep": "pareto_sweep.json",
    "strong_attack_extra": "strong_attack_extra.json",
    "adaptive_attack_ablation": "adaptive_attack_ablation.json",
    "camera_pipeline_ablation": "camera_pipeline_ablation.json",
    "screen_privacy_baselines": "screen_privacy_baselines.json",
    "vlm_prompt_ablation": "vlm_prompt_ablation.json",
    "noise_epsilon_sweep": "noise_epsilon_sweep.json",
    "vlm_model_ablation": "vlm_model_ablation.json",
    "brightness_compensation_ablation": "brightness_compensation_ablation.json",
    "mask_granularity_ablation": "mask_granularity_ablation.json",
    "anti_ocr_profile_ablation": "anti_ocr_profile_ablation.json",
    "seed_sensitivity": "seed_sensitivity.json",
    "usability_pilot": "usability_pilot.json",
}
SUMMARY_JSON = "publication_summary.json"
SUMMARY_MD = "publication_summary.md"

STRATA_FIELDS = ["category", "language", "layout", "font_size"]

ANTI_OCR_PROFILE_PRIORITY = [
    "block1/off",
    "block1/strong@overlay",
    "block1/strong@deployed",
    "block1/capture_hardened",
    "block2/s0.00_g0.00",
    "block2/s0.10_g0.12",
    "block2/s0.18_g0.22",
    "block2/s0.30_g0.22",
    "block3/alpha_0.0",
    "block3/alpha_0.2",
    "block3/alpha_0.5",
    "block3/alpha_1.0",
]

STRONG_ATTACK_ORDER = [
    "global_shutter_slot0",
    "differential_luma",
    "differential_blue",
    "temporal_average_cycle",
    "phase_search_mean",
    "phase_search_max",
    "blue_channel_max",
]
OCR_ENGINE_ORDER = ["tesseract", "easyocr", "surya"]


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_publication_summary(results_dir: str | Path = "experiments/results") -> dict:
    """Build a summary from available result artifacts."""
    root = Path(results_dir)
    ocr = load_json(root / OCR_FILE)
    strong = load_json(root / STRONG_ATTACK_FILE)
    detection = _load_optional(root / DETECTION_FILE)
    coco_detection = _load_optional(root / COCO_DETECTION_FILE)
    mot_video_detection = _load_optional(root / MOT_VIDEO_DETECTION_FILE)
    mot_tracking = _load_optional(root / MOT_TRACKING_FILE)
    view_attack = _load_optional(root / VIEW_ATTACK_FILE)
    vlm = _load_optional(root / VLM_FILE)
    real_capture = _load_optional(root / REAL_CAPTURE_FILE)
    real_capture_coco = _load_optional(root / REAL_CAPTURE_COCO_DETECTION_FILE)
    real_capture_mot_det = _load_optional(root / REAL_CAPTURE_MOT_DETECTION_FILE)
    real_capture_mot_trk = _load_optional(root / REAL_CAPTURE_MOT_TRACKING_FILE)
    supplemental = {
        name: _load_optional(root / filename)
        for name, filename in SUPPLEMENTAL_FILES.items()
    }

    summary = {
        "source_files": {
            "ocr": OCR_FILE,
            "strong_camera": STRONG_ATTACK_FILE,
            "detection": DETECTION_FILE if detection is not None else None,
            "coco_detection": COCO_DETECTION_FILE if coco_detection is not None else None,
            "mot_video_detection": MOT_VIDEO_DETECTION_FILE if mot_video_detection is not None else None,
            "mot_tracking": MOT_TRACKING_FILE if mot_tracking is not None else None,
            "view_attack": VIEW_ATTACK_FILE if view_attack is not None else None,
            "vlm": VLM_FILE if vlm is not None else None,
            "real_capture": REAL_CAPTURE_FILE if real_capture is not None else None,
            "real_capture_coco_detection": (
                REAL_CAPTURE_COCO_DETECTION_FILE if real_capture_coco is not None else None
            ),
            "real_capture_mot_detection": (
                REAL_CAPTURE_MOT_DETECTION_FILE if real_capture_mot_det is not None else None
            ),
            "real_capture_mot_tracking": (
                REAL_CAPTURE_MOT_TRACKING_FILE if real_capture_mot_trk is not None else None
            ),
            **{
                name: filename if supplemental[name] is not None else None
                for name, filename in SUPPLEMENTAL_FILES.items()
            },
        },
        "ocr": summarize_ocr(ocr),
        "ocr_strata": summarize_ocr_strata(ocr),
        "pareto_security": summarize_pareto_security(supplemental.get("pareto_sweep")),
        "strong_camera": summarize_strong_camera(strong),
        "detection": summarize_detection(detection),
        "coco_detection": summarize_coco_detection(coco_detection),
        "mot_video_detection": summarize_mot_video_detection(mot_video_detection),
        "mot_tracking": summarize_mot_tracking(mot_tracking),
        "view_attack": summarize_view_attack(view_attack),
        "vlm": summarize_vlm(vlm),
        "vlm_model_cross": summarize_vlm_model_ablation(supplemental.get("vlm_model_ablation")),
        "real_capture": summarize_real_capture(real_capture),
        "real_capture_coco_detection": summarize_real_capture_coco_detection(real_capture_coco),
        "real_capture_mot_detection": summarize_real_capture_mot_detection(real_capture_mot_det),
        "real_capture_mot_tracking": summarize_real_capture_mot_tracking(real_capture_mot_trk),
        "supplemental_ablations": {
            name: summarize_supplemental_ablation(payload, SUPPLEMENTAL_FILES[name])
            for name, payload in supplemental.items()
        },
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


def summarize_ocr_strata(report: dict) -> dict:
    """Surface the per-stratum OCR defense already computed by the benchmark.

    ``run_corpus_multi_engine`` stores ``report[engine]['strata'][field][value]``
    with original/subframe/reduction ``_mean_std`` dicts. This presents them so a
    reviewer can see the defense holds across content type, language, layout, and
    font size. Returns ``available: False`` when no strata were recorded.
    """
    if not isinstance(report, dict) or not report:
        return {"available": False, "reason": "missing_ocr_result"}
    ordered = [name for name in OCR_ENGINE_ORDER if name in report]
    ordered.extend(sorted(name for name in report if name not in ordered))
    engine = ordered[0]
    strata = report.get(engine, {}).get("strata", {})
    if not strata:
        return {"available": False, "reason": "no_strata_in_result", "engine": engine}
    fields: dict[str, list[dict]] = {}
    for field in STRATA_FIELDS:
        groups = strata.get(field)
        if not groups:
            continue
        rows = []
        for value, stats in sorted(groups.items()):
            original = stats.get("original", {})
            subframe = stats.get("subframe", {})
            rows.append({
                "value": str(value),
                "count": int(original.get("count", 0)),
                "original_mean": _stat_mean(original),
                "original_ci95": _ci(original.get("ci95", {})),
                "subframe_mean": _stat_mean(subframe),
                "subframe_ci95": _ci(subframe.get("ci95", {})),
                "reduction_mean": _stat_mean(stats.get("reduction")),
            })
        fields[field] = rows
    return {"available": bool(fields), "engine": engine, "fields": fields}


def summarize_pareto_security(report: dict | None) -> dict:
    """Surface the n-vs-security/usability table from the Pareto sweep configs.

    The sweep already computes, per (n, refresh), the single-frame OCR, full-cycle
    OCR, single-frame mutual information (entropy_ratio ~ 1/n), and FPI. This groups
    them by n (image metrics are constant across refresh for a fixed epsilon) and
    lists FPI per refresh.
    """
    if not isinstance(report, dict):
        return {"available": False, "reason": "missing_pareto_result"}
    configs = report.get("configs", [])
    if not configs:
        return {"available": False, "reason": "no_configs"}
    by_n: dict[int, dict] = {}
    for cfg in configs:
        n = int(cfg.get("n", 0))
        bucket = by_n.setdefault(n, {
            "entropy_ratio": _num(cfg.get("entropy_ratio")),
            "single_frame_ocr": _num(cfg.get("single_frame_ocr")),
            "full_cycle_ocr": _num(cfg.get("full_cycle_ocr")),
            "refresh": [],
        })
        bucket["refresh"].append({
            "refresh_hz": _num(cfg.get("refresh_hz")),
            "fpi": _num(cfg.get("fpi")),
            "fpi_safe": bool(cfg.get("fpi_safe")),
        })
    rows = []
    for n in sorted(by_n):
        bucket = by_n[n]
        rows.append({
            "n": n,
            "entropy_ratio": bucket["entropy_ratio"],
            "single_frame_ocr": bucket["single_frame_ocr"],
            "full_cycle_ocr": bucket["full_cycle_ocr"],
            "refresh": sorted(bucket["refresh"], key=lambda r: r["refresh_hz"]),
        })
    rec = report.get("recommended", {})
    return {
        "available": True,
        "rows": rows,
        "recommended": {
            "n": rec.get("n"),
            "refresh_hz": rec.get("refresh_hz"),
            "fpi": _num(rec.get("fpi")),
            "entropy_ratio": _num(rec.get("entropy_ratio")),
        },
    }


def summarize_vlm_model_ablation(report: dict | None) -> dict:
    """Cross-model x attack verbatim-recovery matrix from the multi-VLM ablation.

    Reports exact line-match recovery (the privacy-relevant question: did the VLM
    reproduce the actual text). A single captured subframe yields 0 across every
    VLM family, while full-cycle/temporal attacks recover text on all of them, so
    the boundary is not model-specific. Character-level overlap is intentionally
    omitted from this table because it overstates recovery on near-blank frames.
    """
    if not isinstance(report, dict):
        return {"available": False, "reason": "missing_vlm_model_result"}
    per_model = report.get("models", {})
    models = report.get("config", {}).get("models") or list(per_model.keys())
    attacks = report.get("config", {}).get("attacks", [])
    if not models or not attacks or not per_model:
        return {"available": False, "reason": "no_models_or_attacks"}
    rows = []
    for attack in attacks:
        cells = []
        for model in models:
            stats = (
                per_model.get(model, {})
                .get("summary", {})
                .get("attacks", {})
                .get(attack, {})
            )
            cells.append({
                "model": model,
                "exact_match": _num(stats.get("exact_match", {}).get("mean")),
            })
        rows.append({"attack": attack, "cells": cells})
    return {
        "available": True,
        "metric": "exact_match",
        "models": list(models),
        "rows": rows,
    }


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


def summarize_coco_detection(report: dict | None) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": COCO_DETECTION_FILE,
        }
    return {
        "available": True,
        "config": report.get("config", {}),
        "rows": _model_attack_rows(
            report,
            ["map", "map50", "map75", "ap_small", "ap_medium", "ap_large", "ar", "n_images"],
        ),
    }


def summarize_mot_video_detection(report: dict | None) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": MOT_VIDEO_DETECTION_FILE,
        }
    return {
        "available": True,
        "config": report.get("config", {}),
        "rows": _model_attack_rows(
            report,
            ["map", "map50", "recall", "precision", "n_frames"],
        ),
    }


def summarize_mot_tracking(report: dict | None) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": MOT_TRACKING_FILE,
        }
    return {
        "available": True,
        "config": report.get("config", {}),
        "rows": _model_attack_rows(
            report,
            ["mota", "motp", "idf1", "hota", "deta", "assa", "n_frames"],
        ),
    }


def summarize_real_capture_coco_detection(report: dict | None) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": REAL_CAPTURE_COCO_DETECTION_FILE,
        }
    rows, reason = _validate_real_capture_rows(
        report,
        ["map", "map50", "map75", "ap_small", "ap_medium", "ap_large", "ar", "n_images"],
        count_field="n_images",
    )
    if reason:
        return _real_capture_unavailable(
            REAL_CAPTURE_COCO_DETECTION_FILE, report, rows, reason
        )
    return {
        "available": True,
        "config": report.get("config", {}),
        "capture": report.get("capture", {}),
        "rows": rows,
    }


def summarize_real_capture_mot_detection(report: dict | None) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": REAL_CAPTURE_MOT_DETECTION_FILE,
        }
    rows, reason = _validate_real_capture_rows(
        report,
        ["map", "map50", "recall", "precision", "n_frames"],
        count_field="n_frames",
    )
    if reason:
        return _real_capture_unavailable(
            REAL_CAPTURE_MOT_DETECTION_FILE, report, rows, reason
        )
    return {
        "available": True,
        "config": report.get("config", {}),
        "capture": report.get("capture", {}),
        "rows": rows,
    }


def summarize_real_capture_mot_tracking(report: dict | None) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": REAL_CAPTURE_MOT_TRACKING_FILE,
        }
    rows, reason = _validate_real_capture_rows(
        report,
        ["mota", "motp", "idf1", "hota", "deta", "assa", "n_frames"],
        count_field="n_frames",
    )
    if reason:
        return _real_capture_unavailable(
            REAL_CAPTURE_MOT_TRACKING_FILE, report, rows, reason
        )
    return {
        "available": True,
        "config": report.get("config", {}),
        "capture": report.get("capture", {}),
        "rows": rows,
    }


def _real_capture_unavailable(
    expected_file: str,
    report: dict,
    rows: list[dict],
    reason: str,
) -> dict:
    return {
        "available": False,
        "reason": reason,
        "expected_file": expected_file,
        "config": report.get("config", {}),
        "capture": report.get("capture", {}),
        "rows": rows,
    }


def _validate_real_capture_rows(
    report: dict,
    fields: list[str],
    *,
    count_field: str,
) -> tuple[list[dict], str | None]:
    rows = _model_attack_rows(report, fields)
    if not rows:
        return rows, "no_citable_rows"

    coverage = report.get("capture", {}).get("coverage", {})
    if coverage:
        if coverage.get("complete") is False:
            return rows, "incomplete_capture_coverage"

    by_model: dict[str, list[dict]] = {}
    for row in rows:
        by_model.setdefault(str(row.get("model")), []).append(row)
    for model_rows in by_model.values():
        attacks = {str(row.get("attack")) for row in model_rows}
        if "real_clean" not in attacks:
            return rows, "missing_real_clean_baseline"
        counts = [int(row.get(count_field) or 0) for row in model_rows]
        if any(count <= 0 for count in counts):
            return rows, "no_citable_samples"
        if len(set(counts)) > 1:
            return rows, "mismatched_sample_counts"
    if coverage and int(coverage.get("n_shared") or 0) <= 0:
        return rows, "no_shared_samples"
    return rows, None


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
        "positions": _real_capture_positions(report),
        "conditions": conditions,
    }


def summarize_supplemental_ablation(report: dict | None, expected_file: str) -> dict:
    if report is None:
        return {
            "available": False,
            "reason": "missing_result_file",
            "expected_file": expected_file,
        }
    rows = (
        _anti_ocr_profile_rows(report)
        if expected_file == "anti_ocr_profile_ablation.json"
        else _supplemental_rows(report)
    )
    return {
        "available": True,
        "config": report.get("config", {}),
        "rows": rows,
    }


def _model_attack_rows(report: dict, fields: list[str]) -> list[dict]:
    rows = []
    config = report.get("config", {})
    model_order = config.get("models") or list(report.get("results", {}).keys())
    for model in model_order:
        attacks = report.get("results", {}).get(model, {})
        attack_order = config.get("attacks") or list(attacks.keys())
        for attack in attack_order:
            metrics = attacks.get(attack)
            if not isinstance(metrics, dict):
                continue
            row = {"model": model, "attack": attack}
            for field in fields:
                value = metrics.get(field)
                row[field] = _num(value) if isinstance(value, (int, float)) else value
            rows.append(row)
    return rows


def _real_capture_positions(report: dict) -> list[dict]:
    positions = report.get("positions")
    if isinstance(positions, list):
        rows = []
        for pos in positions:
            if not isinstance(pos, dict):
                continue
            rows.append({
                "position": str(pos.get("position", "")),
                "distance_m": _num(pos.get("distance_m")),
                "angle_degrees": _num(pos.get("angle_degrees")),
                "n_captures": int(pos.get("n_captures") or 0),
                "n_rows": int(pos.get("n_rows") or 0),
                "capture_dir": str(pos.get("capture_dir", "")),
                "source_result_file": str(pos.get("source_result_file", "")),
            })
        if rows:
            return rows

    captures = report.get("captures", [])
    if not isinstance(captures, list):
        return []
    grouped: dict[tuple[float, float], dict] = {}
    for row in captures:
        if not isinstance(row, dict):
            continue
        distance = _num(row.get("distance_m"), None)
        angle = _num(row.get("angle_degrees"), None)
        if distance is None or angle is None:
            continue
        key = (distance, angle)
        bucket = grouped.setdefault(key, {
            "position": f"d{_format_number(distance)}_a{_format_number(angle)}",
            "distance_m": distance,
            "angle_degrees": angle,
            "ids": set(),
            "n_rows": 0,
        })
        bucket["ids"].add(str(row.get("id", "")))
        bucket["n_rows"] += 1
    out = []
    for _, bucket in sorted(grouped.items()):
        out.append({
            "position": bucket["position"],
            "distance_m": bucket["distance_m"],
            "angle_degrees": bucket["angle_degrees"],
            "n_captures": len(bucket["ids"]),
            "n_rows": int(bucket["n_rows"]),
            "capture_dir": "",
            "source_result_file": "",
        })
    return out


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

    _render_ocr_strata(lines, summary.get("ocr_strata", {}))

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

    _render_coco_detection(lines, summary.get("coco_detection", {}))
    _render_mot_video_detection(lines, summary.get("mot_video_detection", {}))
    _render_mot_tracking(lines, summary.get("mot_tracking", {}))
    _render_real_capture_detection(lines, summary)

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

    _render_vlm_model_cross(lines, summary.get("vlm_model_cross", {}))

    real = summary["real_capture"]
    lines.extend(["", "## Real Camera Capture", ""])
    if real["available"]:
        lines.extend([
            f"- Captures: {real['config'].get('n_captures', 0)}",
            f"- Positions: {real['config'].get('n_positions', len(real.get('positions', [])))}",
            "",
        ])
        positions = real.get("positions", [])
        if positions:
            lines.extend([
                "### Position Matrix",
                "",
                "| Position | Distance | Angle | Captures | OCR rows |",
                "|---|---:|---:|---:|---:|",
            ])
            for pos in positions:
                lines.append(
                    f"| {pos.get('position', '')} | "
                    f"{_format_number(pos.get('distance_m', 0.0))} m | "
                    f"{_format_number(pos.get('angle_degrees', 0.0))} deg | "
                    f"{int(pos.get('n_captures') or 0)} | "
                    f"{int(pos.get('n_rows') or 0)} |"
                )
            lines.append("")
        lines.extend([
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

    _render_pareto_security(lines, summary.get("pareto_security", {}))

    supplemental = summary.get("supplemental_ablations", {})
    lines.extend(["", "## Supplemental Ablations", ""])
    if supplemental:
        lines.extend([
            "| Experiment | Status | Highlight |",
            "|---|---|---|",
        ])
        for name, entry in supplemental.items():
            if not entry.get("available"):
                lines.append(f"| {name} | missing | `{entry.get('expected_file', '')}` |")
                continue
            rows = entry.get("rows", [])
            if rows:
                first = rows[0]
                highlight = _format_supplemental_row(first)
            else:
                highlight = "available"
            lines.append(f"| {name} | available | {highlight} |")
    else:
        lines.append("- No supplemental ablation section in summary input.")

    _render_supplemental_details(lines, supplemental)

    lines.append("")
    return "\n".join(lines)


def _render_ocr_strata(lines: list[str], strata: dict) -> None:
    lines.extend(["", "## Stratified OCR Defense", ""])
    if not strata.get("available"):
        lines.append("- Stratified breakdown not available (no per-stratum data in OCR result).")
        return
    lines.append(f"Primary engine: `{strata.get('engine', '')}`")
    for field, rows in strata.get("fields", {}).items():
        lines.extend([
            "",
            f"### By {field}",
            "",
            "| Value | Rows | Original char acc | Subframe char acc | Reduction |",
            "|---|---:|---:|---:|---:|",
        ])
        for row in rows:
            lines.append(
                f"| {row['value']} | {row['count']} | "
                f"{_pct_ci(row['original_mean'], row['original_ci95'])} | "
                f"{_pct_ci(row['subframe_mean'], row['subframe_ci95'])} | "
                f"{_pct(row['reduction_mean'])} |"
            )


def _render_coco_detection(lines: list[str], section: dict) -> None:
    lines.extend(["", "## COCO Detection Suite", ""])
    if not section.get("available"):
        lines.append("- COCO detection suite not available (run coco_detection_attack.py).")
        return
    lines.extend([
        "| Model | Attack | mAP | mAP50 | mAP75 | AP_S | AP_M | AP_L | AR | Images |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in section.get("rows", []):
        lines.append(
            f"| {row['model']} | {row['attack']} | {_pct(row.get('map'))} | "
            f"{_pct(row.get('map50'))} | {_pct(row.get('map75'))} | "
            f"{_pct(row.get('ap_small'))} | {_pct(row.get('ap_medium'))} | "
            f"{_pct(row.get('ap_large'))} | {_pct(row.get('ar'))} | "
            f"{int(row.get('n_images') or 0)} |"
        )


def _render_mot_video_detection(lines: list[str], section: dict) -> None:
    lines.extend(["", "## MOT17 Video Detection", ""])
    if not section.get("available"):
        lines.append("- MOT17 video detection not available (run mot_video_detection.py).")
        return
    lines.extend([
        "| Model | Attack | mAP | mAP50 | Recall | Precision | Frames |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in section.get("rows", []):
        lines.append(
            f"| {row['model']} | {row['attack']} | {_pct(row.get('map'))} | "
            f"{_pct(row.get('map50'))} | {_pct(row.get('recall'))} | "
            f"{_pct(row.get('precision'))} | {int(row.get('n_frames') or 0)} |"
        )


def _render_mot_tracking(lines: list[str], section: dict) -> None:
    lines.extend(["", "## MOT17 Tracking", ""])
    if not section.get("available"):
        lines.append("- MOT17 tracking not available (run mot_tracking_attack.py).")
        return
    tracker = section.get("config", {}).get("tracker")
    if tracker:
        lines.append(f"Tracker: `{tracker}`")
        lines.append("")
    lines.extend([
        "| Model | Attack | MOTA | MOTP | IDF1 | HOTA | Frames |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in section.get("rows", []):
        hota = row.get("hota")
        hota_text = "n/a" if hota is None else _pct(hota)
        lines.append(
            f"| {row['model']} | {row['attack']} | {_pct(row.get('mota'))} | "
            f"{_pct(row.get('motp'))} | {_pct(row.get('idf1'))} | "
            f"{hota_text} | {int(row.get('n_frames') or 0)} |"
        )


def _render_real_capture_detection(lines: list[str], summary: dict) -> None:
    """Real USB-webcam capture of COCO/MOT content (validates the sim trend on hardware)."""
    coco = summary.get("real_capture_coco_detection", {})
    mot_det = summary.get("real_capture_mot_detection", {})
    mot_trk = summary.get("real_capture_mot_tracking", {})
    if not any(s.get("available") for s in (coco, mot_det, mot_trk)):
        return
    lines.extend([
        "", "## Real-Device Capture (COCO/MOT)", "",
        "Privacy content shown on a 240Hz screen and photographed with a USB webcam; "
        "`real_clean` is the captured unprotected baseline, so the gap to `real_short` "
        "(single-frame) / `real_video` (temporal mean) isolates the privacy effect.",
        "MOT17 rows are stop-motion physical-frame validation: each dataset frame is "
        "displayed as a static stimulus before capture, so they should not be described "
        "as continuous video playback results.",
    ])
    if coco.get("available"):
        lines.extend(["", "### COCO Real Capture", "",
                      "| Model | Attack | mAP | mAP50 | mAP75 | AP_S | AP_M | AP_L | AR | Images |",
                      "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
        for row in coco.get("rows", []):
            lines.append(
                f"| {row['model']} | {row['attack']} | {_pct(row.get('map'))} | "
                f"{_pct(row.get('map50'))} | {_pct(row.get('map75'))} | "
                f"{_pct(row.get('ap_small'))} | {_pct(row.get('ap_medium'))} | "
                f"{_pct(row.get('ap_large'))} | {_pct(row.get('ar'))} | "
                f"{int(row.get('n_images') or 0)} |"
            )
    if mot_det.get("available"):
        lines.extend(["", "### MOT17 Real Capture — Detection", "",
                      "| Model | Attack | mAP | mAP50 | Recall | Precision | Frames |",
                      "|---|---|---:|---:|---:|---:|---:|"])
        for row in mot_det.get("rows", []):
            lines.append(
                f"| {row['model']} | {row['attack']} | {_pct(row.get('map'))} | "
                f"{_pct(row.get('map50'))} | {_pct(row.get('recall'))} | "
                f"{_pct(row.get('precision'))} | {int(row.get('n_frames') or 0)} |"
            )
    if mot_trk.get("available"):
        lines.extend(["", "### MOT17 Real Capture — Tracking", "",
                      "| Model | Attack | MOTA | MOTP | IDF1 | HOTA | Frames |",
                      "|---|---|---:|---:|---:|---:|---:|"])
        for row in mot_trk.get("rows", []):
            hota = row.get("hota")
            hota_text = "n/a" if hota is None else _pct(hota)
            lines.append(
                f"| {row['model']} | {row['attack']} | {_pct(row.get('mota'))} | "
                f"{_pct(row.get('motp'))} | {_pct(row.get('idf1'))} | "
                f"{hota_text} | {int(row.get('n_frames') or 0)} |"
            )


def _render_vlm_model_cross(lines: list[str], cross: dict) -> None:
    lines.extend(["", "## Multi-VLM Cross-Attack Recovery", ""])
    if not cross.get("available"):
        lines.append("- Multi-VLM ablation not available (run vlm_model_ablation.py).")
        return
    models = cross.get("models", [])
    short = [m.split("/")[-1] for m in models]
    lines.extend([
        "Verbatim recovery (exact line-match rate) per VLM family and attack frame.",
        "",
        "| Attack frame | " + " | ".join(short) + " |",
        "|---|" + "|".join(["---:"] * len(short)) + "|",
    ])
    for row in cross.get("rows", []):
        cells = " | ".join(_pct(c["exact_match"]) for c in row["cells"])
        lines.append(f"| {row['attack']} | {cells} |")


def _render_pareto_security(lines: list[str], psec: dict) -> None:
    lines.extend(["", "## n vs Security / Usability", ""])
    if not psec.get("available"):
        lines.append("- n-vs-security table not available (run pareto_sweep).")
        return
    lines.extend([
        "| n | Single-frame OCR | Full-cycle OCR | Single-frame MI | FPI @ refresh |",
        "|---:|---:|---:|---:|---|",
    ])
    for row in psec.get("rows", []):
        fpis = ", ".join(
            f"{r['refresh_hz']:.0f}Hz:{r['fpi']:.4f}{'✓' if r['fpi_safe'] else '✗'}"
            for r in row["refresh"]
        )
        lines.append(
            f"| {row['n']} | {_pct(row['single_frame_ocr'])} | {_pct(row['full_cycle_ocr'])} | "
            f"{row['entropy_ratio']:.3f} | {fpis} |"
        )
    rec = psec.get("recommended", {})
    if rec.get("n") is not None:
        lines.append(
            f"\nRecommended: n={rec['n']} @ {rec['refresh_hz']}Hz "
            f"(FPI {rec['fpi']:.4f}, single-frame MI {rec['entropy_ratio']:.3f})"
        )


def _render_supplemental_details(lines: list[str], supplemental: dict) -> None:
    detail = {
        name: entry for name, entry in supplemental.items()
        if entry.get("available")
        and any("char_accuracy" in row for row in entry.get("rows", []))
    }
    if not detail:
        return
    lines.extend(["", "### Supplemental Ablation Detail", ""])
    for name, entry in detail.items():
        rows = [row for row in entry.get("rows", []) if "char_accuracy" in row]
        lines.extend([
            "",
            f"#### {name}",
            "",
            "| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in rows:
            exact = (
                _pct_ci(row["exact_match"], row.get("exact_match_ci95", {}))
                if "exact_match" in row
                else ""
            )
            worst = _pct(row["best_observed_char"]) if "best_observed_char" in row else ""
            inv = (
                _pct(row["inversion_frame_attack_char"])
                if "inversion_frame_attack_char" in row
                else ""
            )
            lines.append(
                f"| {row['name']} | "
                f"{row.get('headline_metric', '')} | "
                f"{_pct_ci(row['char_accuracy'], row.get('char_accuracy_ci95', {}))} | "
                f"{exact} | "
                f"{worst} | "
                f"{inv} | "
                f"{_pct(row.get('leak_rate_char_ge_20pct', 0.0))} | "
                f"{row.get('error_count', 0)} |"
            )


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


def _supplemental_rows(report: dict, limit: int | None = 12) -> list[dict]:
    summary = report.get("summary", {})
    if isinstance(summary, dict):
        rows = []
        for key, value in summary.items():
            if not isinstance(value, dict):
                continue
            if "char_accuracy" in value:
                row = {
                    "name": key,
                    "char_accuracy": _stat_mean(value.get("char_accuracy")),
                    "char_accuracy_ci95": _ci(value.get("char_accuracy", {}).get("ci95", {})),
                    "leak_rate_char_ge_20pct": _stat_mean(value.get("leak_rate_char_ge_20pct")),
                    "error_count": int(value.get("error_count", 0)),
                }
                if "headline_metric" in value:
                    row["headline_metric"] = str(value.get("headline_metric", ""))
                if "exact_match" in value:
                    row["exact_match"] = _stat_mean(value.get("exact_match"))
                    row["exact_match_ci95"] = _ci(value.get("exact_match", {}).get("ci95", {}))
                if "best_observed_char" in value:
                    row["best_observed_char"] = _stat_mean(value.get("best_observed_char"))
                    row["best_observed_exact"] = _stat_mean(value.get("best_observed_exact"))
                if "single_frame_char" in value:
                    row["single_frame_char"] = _stat_mean(value.get("single_frame_char"))
                    row["single_frame_exact"] = _stat_mean(value.get("single_frame_exact"))
                if "inversion_frame_attack_char" in value:
                    row["inversion_frame_attack_char"] = _stat_mean(value.get("inversion_frame_attack_char"))
                    row["inversion_frame_attack_exact"] = _stat_mean(value.get("inversion_frame_attack_exact"))
                rows.append(row)
            elif "single_frame_ocr" in value:
                rows.append({
                    "name": key,
                    "char_accuracy": _stat_mean(value.get("single_frame_ocr")),
                    "char_accuracy_ci95": _ci(value.get("single_frame_ocr", {}).get("ci95", {})),
                    "leak_rate_char_ge_20pct": _stat_mean(value.get("leak_rate_char_ge_20pct")),
                    "error_count": int(value.get("error_count", 0)),
                })
            elif "mean" in value:
                rows.append({
                    "name": key,
                    "char_accuracy": _stat_mean(value),
                    "char_accuracy_ci95": _ci(value.get("ci95", {})),
                    "leak_rate_char_ge_20pct": 0.0,
                    "error_count": 0,
                })
            elif "reading_time_s" in value:
                rows.append({
                    "name": key,
                    "readability_1_5": _stat_mean(value.get("readability_1_5")),
                    "flicker_1_5": _stat_mean(value.get("flicker_1_5")),
                    "fatigue_1_5": _stat_mean(value.get("fatigue_1_5")),
                })
            else:
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, dict) and "char_accuracy" in nested_value:
                        row = {
                            "name": f"{key}/{nested_key}",
                            "char_accuracy": _stat_mean(nested_value.get("char_accuracy")),
                            "char_accuracy_ci95": _ci(nested_value.get("char_accuracy", {}).get("ci95", {})),
                            "leak_rate_char_ge_20pct": _stat_mean(nested_value.get("leak_rate_char_ge_20pct")),
                            "error_count": int(nested_value.get("error_count", 0)),
                        }
                        if "headline_metric" in nested_value:
                            row["headline_metric"] = str(nested_value.get("headline_metric", ""))
                        if "exact_match" in nested_value:
                            row["exact_match"] = _stat_mean(nested_value.get("exact_match"))
                            row["exact_match_ci95"] = _ci(nested_value.get("exact_match", {}).get("ci95", {}))
                        rows.append(row)
        if rows:
            return rows if limit is None else rows[:limit]
    if "recommended" in report:
        rec = report["recommended"]
        return [{
            "name": "recommended",
            "n": rec.get("n"),
            "refresh_hz": rec.get("refresh_hz"),
            "fpi": _num(rec.get("fpi")),
            "entropy_ratio": _num(rec.get("entropy_ratio")),
        }]
    return []


def _anti_ocr_profile_rows(report: dict) -> list[dict]:
    """Pick the paper-relevant rows from the multi-block anti-OCR ablation."""
    summary = report.get("summary", {})
    if not isinstance(summary, dict):
        return []
    rows_by_name = _supplemental_rows({"summary": summary}, limit=None)
    rows_by_name = [
        {
            **row,
            "name": (
                "block1/capture_hardened"
                if row.get("name") == "block1/vlm"
                else row.get("name")
            ),
        }
        for row in rows_by_name
    ]
    lookup = {row.get("name"): row for row in rows_by_name}
    selected = [
        lookup[name] for name in ANTI_OCR_PROFILE_PRIORITY
        if name in lookup
    ]
    if len(selected) >= len(ANTI_OCR_PROFILE_PRIORITY):
        return selected
    for row in rows_by_name:
        if row.get("name") not in {r.get("name") for r in selected}:
            selected.append(row)
        if len(selected) >= len(ANTI_OCR_PROFILE_PRIORITY):
            break
    return selected


def _format_supplemental_row(row: dict) -> str:
    if "char_accuracy" in row:
        metric = row.get("headline_metric") or "char recovery"
        parts = [
            (
                f"{row['name']}: {metric} "
                f"{_pct_ci(row['char_accuracy'], row.get('char_accuracy_ci95', {}))}"
            )
        ]
        if "exact_match" in row:
            parts.append(f"exact {_pct_ci(row['exact_match'], row.get('exact_match_ci95', {}))}")
        if "best_observed_char" in row:
            parts.append(f"worst-case char {_pct(row['best_observed_char'])}")
        if "inversion_frame_attack_char" in row:
            parts.append(f"inv-frame char {_pct(row['inversion_frame_attack_char'])}")
        parts.append(f"leak {_pct(row['leak_rate_char_ge_20pct'])}")
        parts.append(f"errors {row['error_count']}")
        return ", ".join(parts)
    if "readability_1_5" in row:
        return (
            f"{row['name']}: readability {row['readability_1_5']:.2f}, "
            f"flicker {row['flicker_1_5']:.2f}"
        )
    if "fpi" in row:
        return (
            f"recommended n={row.get('n')} @ {row.get('refresh_hz')}Hz, "
            f"FPI {row['fpi']:.4f}, MI {row['entropy_ratio']:.3f}"
        )
    return str(row.get("name", "available"))


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _format_number(value: float) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{number:.3f}".rstrip("0").rstrip(".")


def _pct_ci(value: float, ci: dict) -> str:
    if ci.get("method"):
        return f"{_pct(value)} ({_pct(ci['low'])}-{_pct(ci['high'])})"
    return _pct(value)
