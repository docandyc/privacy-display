"""Cluster-aware OCR contrasts for the IEEE Access manuscript.

This script consumes the canonical merged ``real_capture_ocr.json`` artifact.
It does not rerun OCR. The goal is to report profile contrasts using the
content item as the resampling cluster, while keeping the older capture-level
descriptive summaries auditable.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np


DEFAULT_SEED = 20260612
DEFAULT_RESAMPLES = 2000
DEFAULT_INPUT = Path("experiments/results/real_capture_ocr.json")
DEFAULT_JSON_OUTPUT = Path("experiments/results/paper_ocr_clustered_stats.json")
DEFAULT_MD_OUTPUT = Path("experiments/results/paper_ocr_clustered_stats.md")
MATCHING_RULE = "profile + attack + content_item + position + repeat_index"


@dataclass(frozen=True)
class CaptureUnit:
    profile: str
    attack: str
    content_item: str
    position: str
    repeat_index: str


def collapse_best_of_engines(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reduce per-engine rows to one attacker-favorable row per capture."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        capture_id = str(row.get("id") or row.get("image") or "")
        if not capture_id:
            capture_id = "|".join(
                str(row.get(field, ""))
                for field in ("condition", "ablation", "attack", "position")
            )
        grouped[capture_id].append(row)

    collapsed: list[dict[str, Any]] = []
    for capture_rows in grouped.values():
        best = max(
            capture_rows,
            key=lambda row: (
                _as_float(row.get("exact_match")),
                _as_float(row.get("char_accuracy")),
                _as_float(row.get("word_accuracy")),
            ),
        )
        merged = dict(best)
        merged["engine"] = "best_of"
        for metric in (
            "char_accuracy",
            "word_accuracy",
            "exact_match",
            "sensitive_token_recall",
        ):
            merged[metric] = max(_as_float(row.get(metric)) for row in capture_rows)
        merged["sensitive_token_count"] = max(
            int(row.get("sensitive_token_count") or 0) for row in capture_rows
        )
        collapsed.append(merged)
    return sorted(collapsed, key=lambda row: str(row.get("id", "")))


def derive_capture_unit(row: dict[str, Any]) -> CaptureUnit:
    """Extract the analysis unit from row metadata and the archived id."""
    content_item, repeat_index = _parse_content_and_repeat(str(row.get("id") or row.get("image") or ""))
    return CaptureUnit(
        profile=_normalize_profile(str(row.get("ablation", ""))),
        attack=str(row.get("attack", "")),
        content_item=content_item,
        position=_position_label(row),
        repeat_index=repeat_index,
    )


def paired_contrast(
    rows: list[dict[str, Any]],
    *,
    baseline_profile: str,
    treatment_profile: str,
    attack: str,
    metric: str = "char_accuracy",
    exclude_positions: list[str] | None = None,
    seed: int = DEFAULT_SEED,
    resamples: int = DEFAULT_RESAMPLES,
) -> dict[str, Any]:
    """Construct a matched profile contrast and cluster bootstrap interval."""
    exclude = set(exclude_positions or [])
    baseline = _aggregate_cells(
        rows,
        profile=_normalize_profile(baseline_profile),
        attack=attack,
        metric=metric,
        exclude_positions=exclude,
    )
    treatment = _aggregate_cells(
        rows,
        profile=_normalize_profile(treatment_profile),
        attack=attack,
        metric=metric,
        exclude_positions=exclude,
    )

    baseline_keys = set(baseline["cells"])
    treatment_keys = set(treatment["cells"])
    matched_keys = sorted(baseline_keys & treatment_keys)
    pairs = []
    for key in matched_keys:
        base_cell = baseline["cells"][key]
        treatment_cell = treatment["cells"][key]
        pairs.append({
            "cluster": base_cell["cluster"],
            "delta": base_cell["value"] - treatment_cell["value"],
            "baseline_value": base_cell["value"],
            "treatment_value": treatment_cell["value"],
            "key": list(key),
        })

    ci = bootstrap_cluster_mean_ci(pairs, seed=seed, resamples=resamples)
    estimate = ci["estimate"]
    result = {
        "baseline_profile": _normalize_profile(baseline_profile),
        "treatment_profile": _normalize_profile(treatment_profile),
        "attack": attack,
        "metric": metric,
        "estimate": estimate,
        "estimate_percent": estimate * 100.0,
        "ci95": ci,
        "ci95_percent": {
            "low": ci["low"] * 100.0,
            "high": ci["high"] * 100.0,
            "half_width": ci["half_width"] * 100.0,
        },
        "cluster_count": ci["cluster_count"],
        "matched_unit_count": len(pairs),
        "resampling_unit": "content_item",
        "seed": seed,
        "resamples": resamples,
        "matching_rule": MATCHING_RULE,
        "excluded_positions": sorted(exclude),
        "matched_baseline_mean": _mean([pair["baseline_value"] for pair in pairs]),
        "matched_treatment_mean": _mean([pair["treatment_value"] for pair in pairs]),
        "unmatched": {
            "baseline_only": len(baseline_keys - treatment_keys),
            "treatment_only": len(treatment_keys - baseline_keys),
            "baseline_total_cells": len(baseline_keys),
            "treatment_total_cells": len(treatment_keys),
        },
        "duplicates_collapsed": {
            "baseline_cells": baseline["duplicate_cells"],
            "baseline_extra_rows": baseline["duplicate_extra_rows"],
            "treatment_cells": treatment["duplicate_cells"],
            "treatment_extra_rows": treatment["duplicate_extra_rows"],
        },
    }
    return result


def bootstrap_cluster_mean_ci(
    pairs: list[dict[str, Any]],
    *,
    seed: int = DEFAULT_SEED,
    resamples: int = DEFAULT_RESAMPLES,
) -> dict[str, Any]:
    """Bootstrap a paired-contrast mean by resampling content clusters."""
    if not pairs:
        return {
            "estimate": 0.0,
            "low": 0.0,
            "high": 0.0,
            "half_width": 0.0,
            "confidence": 0.95,
            "method": "empty",
            "resampling_unit": "content_item",
            "seed": seed,
            "resamples": 0,
            "cluster_count": 0,
        }

    by_cluster: dict[str, list[float]] = defaultdict(list)
    for pair in pairs:
        by_cluster[str(pair["cluster"])].append(float(pair["delta"]))
    clusters = sorted(by_cluster)
    estimate = _mean([float(pair["delta"]) for pair in pairs])

    if len(clusters) == 1 or resamples <= 0:
        return {
            "estimate": estimate,
            "low": estimate,
            "high": estimate,
            "half_width": 0.0,
            "confidence": 0.95,
            "method": "degenerate",
            "resampling_unit": "content_item",
            "seed": seed,
            "resamples": 0,
            "cluster_count": len(clusters),
        }

    rng = np.random.default_rng(seed)
    bootstrap_means = []
    for _ in range(resamples):
        sampled_clusters = rng.choice(clusters, size=len(clusters), replace=True)
        sampled_values = []
        for cluster in sampled_clusters:
            sampled_values.extend(by_cluster[str(cluster)])
        bootstrap_means.append(float(np.mean(sampled_values)))
    low, high = np.percentile(np.asarray(bootstrap_means), [2.5, 97.5])
    return {
        "estimate": estimate,
        "low": float(low),
        "high": float(high),
        "half_width": float((high - low) / 2.0),
        "confidence": 0.95,
        "method": "cluster_percentile_bootstrap",
        "resampling_unit": "content_item",
        "seed": seed,
        "resamples": resamples,
        "cluster_count": len(clusters),
    }


def build_cluster_report(
    source: str | Path = DEFAULT_INPUT,
    *,
    seed: int = DEFAULT_SEED,
    resamples: int = DEFAULT_RESAMPLES,
) -> dict[str, Any]:
    source_path = Path(source)
    with source_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    raw_rows = payload.get("captures")
    if not isinstance(raw_rows, list):
        raise ValueError("input report must contain a captures list")

    best_rows = collapse_best_of_engines(raw_rows)
    contrast_specs = [
        ("original_short_minus_deployed_short", "original", "deployed", "short", []),
        (
            "original_short_minus_high_suppression_short",
            "original",
            "high_suppression",
            "short",
            [],
        ),
        ("mask_only_short_minus_deployed_short", "mask_only", "deployed", "short", []),
        ("original_short_minus_mask_only_short", "original", "mask_only", "short", []),
        (
            "sensitivity_excluding_d0.5_a15_original_short_minus_deployed_short",
            "original",
            "deployed",
            "short",
            ["d0.5_a15"],
        ),
        (
            "sensitivity_excluding_d0.5_a15_original_short_minus_high_suppression_short",
            "original",
            "high_suppression",
            "short",
            ["d0.5_a15"],
        ),
        (
            "sensitivity_excluding_d0.5_a15_mask_only_short_minus_deployed_short",
            "mask_only",
            "deployed",
            "short",
            ["d0.5_a15"],
        ),
        (
            "sensitivity_excluding_d0.5_a15_original_short_minus_mask_only_short",
            "original",
            "mask_only",
            "short",
            ["d0.5_a15"],
        ),
    ]
    contrasts = {
        name: paired_contrast(
            best_rows,
            baseline_profile=baseline,
            treatment_profile=treatment,
            attack=attack,
            exclude_positions=exclude,
            seed=seed,
            resamples=resamples,
        )
        for name, baseline, treatment, attack, exclude in contrast_specs
    }

    return {
        "schema_version": 1,
        "source": str(source_path),
        "analysis": "paper_ocr_clustered_stats",
        "metric": "char_accuracy",
        "config": {
            "seed": seed,
            "resamples": resamples,
            "confidence": 0.95,
            "resampling_unit": "content_item",
            "matching_rule": MATCHING_RULE,
            "engine_reduction": "best_of_engine_per_capture",
            "duplicate_cell_rule": (
                "Multiple captures with the same profile, attack, content item, "
                "position, and repeat index are averaged before pairing."
            ),
        },
        "input_counts": {
            "engine_rows": len(raw_rows),
            "best_of_capture_rows": len(best_rows),
        },
        "descriptive_group_means": _descriptive_group_means(best_rows),
        "contrasts": contrasts,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Paper OCR Clustered Statistics",
        "",
        f"- Source: `{report['source']}`",
        f"- Engine reduction: {report['config']['engine_reduction']}",
        f"- Matching rule: {report['config']['matching_rule']}",
        f"- Resampling unit: {report['config']['resampling_unit']}",
        f"- Bootstrap: seed {report['config']['seed']}, {report['config']['resamples']} resamples",
        "",
        "## Paired Character-Recovery Contrasts",
        "",
        "| Contrast | Matched units | Clusters | Estimate (pp) | 95% CI (pp) | Unmatched baseline/treatment | Duplicate extra rows |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, contrast in report["contrasts"].items():
        ci = contrast["ci95_percent"]
        dup = contrast["duplicates_collapsed"]
        un = contrast["unmatched"]
        lines.append(
            "| "
            + " | ".join([
                name.replace("_", " "),
                str(contrast["matched_unit_count"]),
                str(contrast["cluster_count"]),
                f"{contrast['estimate_percent']:.1f}",
                f"[{ci['low']:.1f}, {ci['high']:.1f}]",
                f"{un['baseline_only']}/{un['treatment_only']}",
                f"{dup['baseline_extra_rows']}/{dup['treatment_extra_rows']}",
            ])
            + " |"
        )

    lines.extend([
        "",
        "## Descriptive Best-of-Engine Means",
        "",
        "| Profile | Attack | N | Char (%) | Exact (%) | Sensitive token (%) |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for key, summary in sorted(report["descriptive_group_means"].items()):
        profile, attack = key.split("|", 1)
        lines.append(
            f"| {profile} | {attack} | {summary['count']} | "
            f"{summary['char_accuracy_mean'] * 100:.1f} | "
            f"{summary['exact_match_mean'] * 100:.1f} | "
            f"{summary['sensitive_token_recall_mean'] * 100:.1f} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    report: dict[str, Any],
    *,
    json_output: str | Path = DEFAULT_JSON_OUTPUT,
    md_output: str | Path = DEFAULT_MD_OUTPUT,
) -> None:
    json_path = Path(json_output)
    md_path = Path(md_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Merged real-capture OCR JSON.")
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT), help="Output JSON path.")
    parser.add_argument("--md-output", default=str(DEFAULT_MD_OUTPUT), help="Output Markdown path.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--resamples", type=int, default=DEFAULT_RESAMPLES)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_cluster_report(args.input, seed=args.seed, resamples=args.resamples)
    write_outputs(report, json_output=args.json_output, md_output=args.md_output)
    print(f"Wrote {args.json_output}")
    print(f"Wrote {args.md_output}")


def _aggregate_cells(
    rows: list[dict[str, Any]],
    *,
    profile: str,
    attack: str,
    metric: str,
    exclude_positions: set[str],
) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        unit = derive_capture_unit(row)
        if unit.profile != profile or unit.attack != attack or unit.position in exclude_positions:
            continue
        key = (unit.content_item, unit.position, unit.repeat_index)
        grouped.setdefault(key, {"values": [], "cluster": unit.content_item})
        grouped[key]["values"].append(_as_float(row.get(metric)))

    cells = {}
    duplicate_cells = 0
    duplicate_extra_rows = 0
    for key, cell in grouped.items():
        values = cell["values"]
        if len(values) > 1:
            duplicate_cells += 1
            duplicate_extra_rows += len(values) - 1
        cells[key] = {
            "value": _mean(values),
            "cluster": cell["cluster"],
            "raw_count": len(values),
        }
    return {
        "cells": cells,
        "duplicate_cells": duplicate_cells,
        "duplicate_extra_rows": duplicate_extra_rows,
    }


def _descriptive_group_means(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        unit = derive_capture_unit(row)
        grouped[f"{unit.profile}|{unit.attack}"].append(row)
    out = {}
    for key, group in grouped.items():
        out[key] = {
            "count": len(group),
            "char_accuracy_mean": _mean([_as_float(row.get("char_accuracy")) for row in group]),
            "exact_match_mean": _mean([_as_float(row.get("exact_match")) for row in group]),
            "sensitive_token_recall_mean": _mean([
                _as_float(row.get("sensitive_token_recall")) for row in group
            ]),
        }
    return out


def _parse_content_and_repeat(capture_id: str) -> tuple[str, str]:
    label = capture_id
    for suffix in (".jpg", ".jpeg", ".png", ".webp"):
        if label.lower().endswith(suffix):
            label = label[: -len(suffix)]
            break
    parts = label.split("_")
    repeat = parts[-1] if parts and parts[-1].startswith("s") else "r0"
    n_index = None
    for idx in range(len(parts) - 1, -1, -1):
        if len(parts[idx]) > 1 and parts[idx].startswith("n") and parts[idx][1:].isdigit():
            n_index = idx
            break
    angle_index = None
    for idx, part in enumerate(parts[:-1]):
        if part.endswith("deg") and parts[idx + 1].endswith("m"):
            angle_index = idx
            break
    if angle_index is None or n_index is None or angle_index + 2 >= n_index:
        return label, repeat
    return "_".join(parts[angle_index + 2:n_index]), repeat


def _position_label(row: dict[str, Any]) -> str:
    position = str(row.get("position") or row.get("roi_pos") or "").strip()
    if position:
        return position
    distance = row.get("distance_m")
    angle = row.get("angle_degrees")
    if distance is None or angle is None:
        return "unknown"
    return f"d{_format_number(float(distance))}_a{_format_number(float(angle))}"


def _format_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:g}"


def _normalize_profile(profile: str) -> str:
    mapping = {
        "vlm": "high_suppression",
        "capture_hardened": "high_suppression",
        "anti_ocr": "strong",
    }
    return mapping.get(profile, profile)


def _as_float(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if value is None:
        return 0.0
    return float(value)


def _mean(values: list[float]) -> float:
    return float(mean(values)) if values else 0.0


if __name__ == "__main__":
    main()
