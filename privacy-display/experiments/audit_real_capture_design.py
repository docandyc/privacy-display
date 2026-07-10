"""Generate an evidence-status audit for the physical real-capture design."""

from __future__ import annotations

import argparse
import json
import math
import sys
import re
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.analyze_paper_ocr_clusters import derive_capture_unit
from experiments.real_capture_preprocessing_attack import (
    load_primary_capture_records,
    summarize_primary_selection,
)


COMPONENT_PROFILE_ORDER = [
    "original",
    "mask_only",
    "mask_noise",
    "anti_ocr",
    "deployed",
    "capture_hardened",
]


def _load_truths(root: Path) -> dict[str, str]:
    truths: dict[str, str] = {}
    for path in sorted((root / "experiments").glob("real_captures*_final/metadata.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload.get("captures", []):
            content_id = derive_capture_unit(row).content_item
            truth = str(row.get("truth", ""))
            if content_id in truths and truths[content_id] != truth:
                raise ValueError(f"conflicting ground truth for {content_id}")
            truths[content_id] = truth
    return truths


def build_design_audit(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    archive_path = root / "experiments/results/real_capture_ocr.json"
    archive = json.loads(archive_path.read_text(encoding="utf-8"))
    records = load_primary_capture_records(archive_path, project_root=root)
    selection = summarize_primary_selection(records)
    truths = _load_truths(root)

    source_text = (root / "experiments/real_capture_ablation.py").read_text(encoding="utf-8")
    source_offsets = []
    for label in COMPONENT_PROFILE_ORDER:
        match = re.search(rf'ConditionSpec\(\s*"{re.escape(label)}"', source_text)
        if match is None:
            raise ValueError(f"component profile missing from collection source: {label}")
        source_offsets.append(match.start())
    if source_offsets != sorted(source_offsets):
        raise ValueError("component profile source order changed")

    common_short_values = sorted({
        float(row["exposure_s"])
        for row in records
        if str(row["position"]) != "d0.5_a15" and row.get("exposure_s") is not None
    })
    excluded_short_values = sorted({
        float(row["exposure_s"])
        for row in archive.get("captures", [])
        if derive_capture_unit(row).attack == "short"
        and derive_capture_unit(row).position == "d0.5_a15"
        and row.get("exposure_s") is not None
    })
    if common_short_values != [0.00390625] or excluded_short_values != [0.00048828125]:
        raise ValueError(
            f"unexpected archived exposure values: common={common_short_values}, excluded={excluded_short_values}"
        )

    non_ascii = sorted(
        content_id for content_id, truth in truths.items()
        if any(ord(character) > 127 for character in truth)
    )
    cjk = sorted(
        content_id for content_id, truth in truths.items()
        if any("\u4e00" <= character <= "\u9fff" for character in truth)
    )
    field_counts = Counter()
    for row in records:
        field_counts[(str(row["profile"]), str(row["position"]))] += 1

    return {
        "schema_version": 1,
        "source_archive": str(archive_path),
        "acquisition_order": {
            "status": "recorded_in_collection_source",
            "component_profile_order": COMPONENT_PROFILE_ORDER,
            "randomized": False,
            "interpretation": (
                "The collection plan groups profiles in a fixed insertion order. "
                "The archive therefore cannot separate profile effects from elapsed-time or batch effects."
            ),
        },
        "geometry": {
            "recorded_position_count": len(archive.get("positions", [])),
            "primary_position_count": len(selection["positions"]),
            "primary_positions": selection["positions"],
            "excluded_position": "d0.5_a15",
            "exclusion_reason": "different logged UVC exposure control value and visibly underexposed protected frames",
        },
        "camera_controls": {
            "short_exposure_seconds": {
                "status": "derived",
                "value": common_short_values[0],
                "derivation": "2**(-8), from the logged DirectShow/UVC exposure-control convention",
                "physical_shutter_time_measured": False,
            },
            "excluded_short_exposure_seconds": {
                "status": "derived",
                "value": excluded_short_values[0],
                "derivation": "2**(-11), from the logged DirectShow/UVC exposure-control convention",
                "physical_shutter_time_measured": False,
            },
            "auto_exposure_state": {
                "status": "unknown",
                "reason": "per-capture metadata does not preserve a semantically decoded AE state",
            },
            "display_refresh_hz": {"status": "recorded", "value": 240.0},
            "playback_fps": {
                "status": "recorded_for_some_captures",
                "value_range": sorted({
                    round(float(row["playback_fps_measured"]), 2)
                    for row in records if row.get("playback_fps_measured") is not None
                }),
            },
            "unknown_fields": [
                "ambient_illuminance",
                "display_luminance",
                "display_brightness_setting",
                "sensor_gain",
                "auto_white_balance_state",
                "focus_state",
                "photometric_exposure_time",
                "capture_phase_within_display_cycle",
            ],
        },
        "image_pipeline": {
            "perspective_rectification": {"status": "recorded_in_source_and_calibration_files"},
            "content_crop": {"status": "recorded_in_source"},
            "jpeg_quality": {"status": "recorded_in_source", "value": 95},
            "adaptive_enhancement_in_primary_ocr": False,
        },
        "corpus": {
            "content_item_count": len(truths),
            "content_items": sorted(truths),
            "items_with_non_ascii_truth": non_ascii,
            "items_with_cjk_truth": cjk,
            "all_english_ascii": not non_ascii,
            "selection_status": "fixed synthetic/document subset archived in per-position metadata",
        },
        "duplicates": {
            "deployed_short_capture_count_primary": selection["capture_counts"]["deployed"],
            "deployed_short_matched_cell_count_primary": selection["matched_unit_counts"]["deployed"],
            "rule": "average repeated profile/content/position/repeat captures before matched contrasts",
        },
        "estimand": {
            "primary": "duplicate-averaged matched content × position × repeat cells across 8 common-setting geometries",
            "all_available": "unbalanced captured-image sensitivity summary",
        },
    }


def render_markdown(audit: dict[str, Any]) -> str:
    camera = audit["camera_controls"]
    return "\n".join([
        "# Real-Capture Design Audit",
        "",
        "## Acquisition and estimand",
        "",
        f"- Component profiles were collected in the fixed source-plan order: {', '.join(audit['acquisition_order']['component_profile_order'])}. They were not randomized.",
        f"- The primary pool contains {audit['geometry']['primary_position_count']} geometries and excludes `{audit['geometry']['excluded_position']}` because it used a different logged UVC setting.",
        f"- Readability-priority contributes {audit['duplicates']['deployed_short_capture_count_primary']} captured images but {audit['duplicates']['deployed_short_matched_cell_count_primary']} duplicate-averaged matched cells.",
        "",
        "## Evidence status",
        "",
        f"- The reported {camera['short_exposure_seconds']['value'] * 1000:.5g} ms value is derived from the nominal UVC control convention; it is not a photometrically measured shutter time.",
        f"- Auto-exposure state is `{camera['auto_exposure_state']['status']}`. Unknown fields: {', '.join(camera['unknown_fields'])}.",
        "",
        "## Corpus",
        "",
        f"- The archive contains {audit['corpus']['content_item_count']} content items. It is not all-English/ASCII; non-ASCII items are: {', '.join(audit['corpus']['items_with_non_ascii_truth'])}.",
        "",
    ])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json-out", default="experiments/results/real_capture_design_audit.json")
    parser.add_argument("--md-out", default="experiments/results/real_capture_design_audit.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()
    report = build_design_audit(root)
    json_out = root / args.json_out
    md_out = root / args.md_out
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {json_out}")
    print(f"Wrote {md_out}")


if __name__ == "__main__":
    main()
