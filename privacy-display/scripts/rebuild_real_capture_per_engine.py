"""Rebuild experiments/results/real_capture_per_engine.json from raw captures.

Reads the engine-level records in real_capture_ocr.json and aggregates
per (profile | attack | engine), plus an attacker-favorable ``best_of`` view
used by the paper's profile--attack table. Duplicate capture rounds are first averaged
within ``profile + attack + content_item + position + repeat_index`` so the
publication estimand gives every planned capture unit equal weight. The
artifact keeps the raw capture count alongside the balanced unit count.

This also fixes an earlier aggregation bug where the
``capture_hardened`` label had merged two different ablation labels
(``vlm`` = capture-hardened profile AND ``anti_ocr`` = strong overlay,
stripe 0.10 / glyph 0.12, no inversion), inflating N to 648 and distorting
the per-engine means. ``capture_hardened`` now maps to ablation ``vlm`` only,
matching the paper's per-engine table (tab:real_ocr_engine).

Usage: python scripts/rebuild_real_capture_per_engine.py
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.analyze_paper_ocr_clusters import (
    collapse_best_of_engines,
    derive_capture_unit,
)

RESULTS = PROJECT_ROOT / "experiments" / "results"
SOURCE = RESULTS / "real_capture_ocr.json"
TARGET = RESULTS / "real_capture_per_engine.json"

# output profile label -> raw ablation label in real_capture_ocr.json
PROFILE_MAP = {
    "original": "original",
    "mask_only": "mask_only",
    "mask_noise": "mask_noise",
    "strong": "anti_ocr",
    "deployed": "deployed",
    "capture_hardened": "vlm",  # historical label for the capture-hardened profile
}

# output attack label -> raw attack label
ATTACK_MAP = {
    "short": "short",
    "long": "long",
    "video_temporal_mean": "video:temporal_mean",
}

ENGINES = ("tesseract", "easyocr", "surya")
ENGINE_AGGREGATIONS = (*ENGINES, "best_of")
METRICS = ("char_accuracy", "exact_match", "sensitive_token_recall")
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260612


def average_duplicate_capture_units(
    records: list[dict[str, Any]],
    metric: str,
) -> list[float]:
    """Average one metric within the established balanced capture-unit key."""
    grouped: dict[tuple[str, str, str, str, str], list[float]] = {}
    for record in sorted(
        records,
        key=lambda row: str(row.get("id") or row.get("image") or ""),
    ):
        unit = derive_capture_unit(record)
        key = (
            unit.profile,
            unit.attack,
            unit.content_item,
            unit.position,
            unit.repeat_index,
        )
        grouped.setdefault(key, []).append(float(record.get(metric) or 0.0))
    return [
        float(np.mean(np.asarray(values, dtype=np.float64)))
        for values in grouped.values()
    ]


def metric_summary(
    values: list[float],
    *,
    raw_count: int,
    seed: int = BOOTSTRAP_SEED,
    resamples: int = BOOTSTRAP_RESAMPLES,
) -> dict[str, Any]:
    """Return deterministic unit-resampling statistics plus raw provenance."""
    array = np.asarray(values, dtype=np.float64)
    if array.size == 0:
        return {
            "mean": 0.0,
            "ci95": {
                "low": 0.0,
                "high": 0.0,
                "half_width": 0.0,
                "confidence": 0.95,
                "method": "empty",
                "resamples": 0,
                "seed": seed,
                "resampling_unit": "duplicate_averaged_capture_unit",
            },
            "count": 0,
            "raw_count": raw_count,
            "duplicate_extra_rows": raw_count,
        }

    estimate = float(array.mean())
    if array.size == 1 or resamples <= 0:
        low = high = estimate
        method = "degenerate"
        actual_resamples = 0
    else:
        rng = np.random.default_rng(seed)
        indexes = rng.integers(
            0,
            array.size,
            size=(resamples, array.size),
        )
        bootstrap_means = array[indexes].mean(axis=1)
        low, high = (
            float(value)
            for value in np.percentile(bootstrap_means, [2.5, 97.5])
        )
        method = "bootstrap_percentile"
        actual_resamples = resamples

    return {
        "mean": estimate,
        "ci95": {
            "low": low,
            "high": high,
            "half_width": float((high - low) / 2.0),
            "confidence": 0.95,
            "method": method,
            "resamples": actual_resamples,
            "seed": seed,
            "resampling_unit": "duplicate_averaged_capture_unit",
        },
        "count": int(array.size),
        "raw_count": raw_count,
        "duplicate_extra_rows": raw_count - int(array.size),
    }


def build_per_engine_summary(captures: list[dict[str, Any]]) -> dict[str, dict]:
    """Build balanced engine/best-of summaries while retaining raw counts."""
    out: dict[str, dict] = {}
    for profile, ablation in PROFILE_MAP.items():
        for attack, raw_attack in ATTACK_MAP.items():
            attack_records = [
                capture
                for capture in captures
                if capture["ablation"] == ablation
                and capture["attack"] == raw_attack
            ]
            for engine in ENGINE_AGGREGATIONS:
                if engine == "best_of":
                    recs = collapse_best_of_engines(attack_records)
                else:
                    recs = [
                        capture
                        for capture in attack_records
                        if capture["engine"] == engine
                    ]
                if not recs:
                    continue
                entry: dict[str, dict] = {}
                for metric in METRICS:
                    values = average_duplicate_capture_units(recs, metric)
                    entry[metric] = metric_summary(
                        values,
                        raw_count=len(recs),
                    )
                char_values = average_duplicate_capture_units(
                    recs,
                    "char_accuracy",
                )
                entry["leak_rate_char_ge_20pct"] = metric_summary(
                    [float(value >= 0.20) for value in char_values],
                    raw_count=len(recs),
                )
                out[f"{profile}|{attack}|{engine}"] = entry
    return out


def rebuild(
    source: str | Path = SOURCE,
    target: str | Path = TARGET,
) -> dict[str, dict]:
    """Load raw engine rows, write the balanced artifact, and return it."""
    source_path = Path(source)
    target_path = Path(target)
    data = json.loads(source_path.read_text(encoding="utf-8"))
    captures = data.get("captures")
    if not isinstance(captures, list):
        raise ValueError("source report must contain a captures list")
    out = build_per_engine_summary(captures)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out


def main() -> None:
    out = rebuild()
    print(f"wrote {TARGET} with {len(out)} keys")


if __name__ == "__main__":
    main()
