"""Audit explicit sensitive-field recovery in the canonical OCR archive.

This module deliberately does not discover fields from prose.  The annotation
manifest is fixed independently of OCR outputs, checked against archived
ground truth, and scored with both field-level micro and sample-level macro
estimands.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

try:
    from experiments.analyze_paper_ocr_clusters import derive_capture_unit
except ModuleNotFoundError:  # Direct ``python experiments/...py`` execution.
    from analyze_paper_ocr_clusters import derive_capture_unit


DEFAULT_INPUT = Path("experiments/results/real_capture_ocr.json")
DEFAULT_MANIFEST = Path("experiments/config/real_capture_sensitive_fields.json")
DEFAULT_JSON_OUTPUT = Path("experiments/results/sensitive_field_recovery.json")
DEFAULT_MD_OUTPUT = Path("experiments/results/sensitive_field_recovery.md")
PRIMARY_PROFILES = ("original", "deployed", "high_suppression")
EXCLUDED_PRIMARY_POSITION = "d0.5_a15"
ALLOWED_TYPES = {"credential", "digit_string", "url_path", "code_key", "none"}


def normalize_field(text: str) -> str:
    """Normalize only presentation variation, retaining Unicode letters/digits."""
    normalized = unicodedata.normalize("NFKC", str(text)).casefold()
    return "".join(character for character in normalized if character.isalnum())


def load_sensitive_field_manifest(path: str | Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(payload.get("items"), dict):
        raise ValueError("sensitive-field manifest must use schema_version 1 and contain items")
    items = payload["items"]
    for content_id, item in items.items():
        fields = item.get("fields")
        if not isinstance(fields, list):
            raise ValueError(f"{content_id}: fields must be a list")
        seen: set[str] = set()
        truth_norm = normalize_field(item.get("truth", ""))
        for field in fields:
            if not isinstance(field, dict) or not str(field.get("text", "")).strip():
                raise ValueError(f"{content_id}: each field requires text")
            if field.get("type") not in ALLOWED_TYPES - {"none"}:
                raise ValueError(f"{content_id}: unsupported field type {field.get('type')!r}")
            normalized = normalize_field(field["text"])
            if normalized in seen:
                raise ValueError(f"{content_id}: duplicate normalized field {field['text']!r}")
            if truth_norm and normalized not in truth_norm:
                raise ValueError(f"{content_id}: field {field['text']!r} is not present in truth")
            seen.add(normalized)
    return items


def score_sensitive_fields(prediction: str, fields: list[dict[str, str]]) -> dict[str, Any]:
    prediction_norm = normalize_field(prediction)
    recovered_fields = [
        field["text"] for field in fields
        if normalize_field(field["text"]) in prediction_norm
    ]
    total = len(fields)
    recovered = len(recovered_fields)
    return {
        "recovered": recovered,
        "total": total,
        "micro_recall": recovered / total if total else 0.0,
        "recovered_fields": recovered_fields,
    }


def collapse_engine_field_recovery(
    rows: list[dict[str, Any]],
    content_id: str,
    manifest: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if content_id not in manifest:
        raise KeyError(f"unknown content item: {content_id}")
    fields = manifest[content_id]["fields"]
    recovered_fields = []
    for field in fields:
        normalized = normalize_field(field["text"])
        if any(normalized in normalize_field(row.get("recognized_text", "")) for row in rows):
            recovered_fields.append(field["text"])
    total = len(fields)
    recovered = len(recovered_fields)
    return {
        "recovered": recovered,
        "total": total,
        "micro_recall": recovered / total if total else 0.0,
        "sample_recall": recovered / total if total else None,
        "recovered_fields": recovered_fields,
        "engine_count": len({str(row.get("engine", "")) for row in rows}),
    }


def summarize_cells(cells: list[dict[str, Any]]) -> dict[str, Any]:
    field_cells = [cell for cell in cells if int(cell["total"]) > 0]
    opportunities = sum(int(cell["total"]) for cell in field_cells)
    recovered = sum(float(cell["recovered"]) for cell in field_cells)
    return {
        "all_cell_count": len(cells),
        "field_bearing_cell_count": len(field_cells),
        "field_opportunities": opportunities,
        "expected_fields_recovered": recovered,
        "micro_exact_recovery": recovered / opportunities if opportunities else None,
        "sample_macro_exact_recovery": (
            mean(float(cell["sample_recall"]) for cell in field_cells)
            if field_cells else None
        ),
    }


def _load_truths(glob_pattern: str) -> dict[str, str]:
    truths: dict[str, str] = {}
    for path in sorted(Path().glob(glob_pattern)):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload.get("captures", []):
            content_id = derive_capture_unit(row).content_item
            truth = str(row.get("truth", ""))
            if content_id in truths and truths[content_id] != truth:
                raise ValueError(f"conflicting archived truth for {content_id}")
            truths[content_id] = truth
    return truths


def _validate_manifest_truths(
    manifest: dict[str, dict[str, Any]], truths: dict[str, str]
) -> dict[str, str]:
    if set(manifest) != set(truths):
        missing = sorted(set(truths) - set(manifest))
        extra = sorted(set(manifest) - set(truths))
        raise ValueError(f"manifest/truth content mismatch: missing={missing}, extra={extra}")
    hashes = {}
    for content_id, truth in truths.items():
        truth_norm = normalize_field(truth)
        for field in manifest[content_id]["fields"]:
            if normalize_field(field["text"]) not in truth_norm:
                raise ValueError(f"{content_id}: field {field['text']!r} is not present in truth")
        hashes[content_id] = hashlib.sha256(truth.encode("utf-8")).hexdigest()
    return hashes


def _collapse_archive_rows(
    rows: list[dict[str, Any]], manifest: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("id") or row.get("image") or "")].append(row)
    collapsed = []
    for capture_id, capture_rows in grouped.items():
        unit = derive_capture_unit(capture_rows[0])
        score = collapse_engine_field_recovery(capture_rows, unit.content_item, manifest)
        collapsed.append({
            "capture_id": capture_id,
            "profile": unit.profile,
            "attack": unit.attack,
            "content_item": unit.content_item,
            "position": unit.position,
            "repeat_index": unit.repeat_index,
            **score,
        })
    return collapsed


def _aggregate_duplicate_cells(rows: list[dict[str, Any]]) -> dict[str, dict[tuple[str, str, str], dict[str, Any]]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["attack"] != "short":
            continue
        key = (row["profile"], row["content_item"], row["position"], row["repeat_index"])
        groups[key].append(row)
    profiles: dict[str, dict[tuple[str, str, str], dict[str, Any]]] = defaultdict(dict)
    for (profile, content, position, repeat), duplicates in groups.items():
        total = int(duplicates[0]["total"])
        recovered = mean(float(row["recovered"]) for row in duplicates)
        profiles[profile][(content, position, repeat)] = {
            "recovered": recovered,
            "total": total,
            "sample_recall": recovered / total if total else None,
            "raw_capture_count": len(duplicates),
        }
    return profiles


def build_report(input_path: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    input_path = Path(input_path)
    manifest_path = Path(manifest_path)
    archive = json.loads(input_path.read_text(encoding="utf-8"))
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = load_sensitive_field_manifest(manifest_path)
    truths = _load_truths(manifest_payload["truth_metadata_glob"])
    truth_hashes = _validate_manifest_truths(manifest, truths)
    collapsed = _collapse_archive_rows(archive["captures"], manifest)
    profiles = _aggregate_duplicate_cells(collapsed)

    eligible = {
        profile: {key: cell for key, cell in profiles[profile].items() if key[1] != EXCLUDED_PRIMARY_POSITION}
        for profile in PRIMARY_PROFILES
    }
    matched_keys = set.intersection(*(set(cells) for cells in eligible.values()))
    matched = {
        profile: summarize_cells([eligible[profile][key] for key in sorted(matched_keys)])
        for profile in PRIMARY_PROFILES
    }
    sensitivity = {
        profile: summarize_cells(list(profiles.get(profile, {}).values()))
        for profile in PRIMARY_PROFILES
    }
    return {
        "schema_version": 1,
        "source": {
            "ocr_archive": str(input_path),
            "ocr_archive_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
            "manifest": str(manifest_path),
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "truth_sha256_by_content": truth_hashes,
        },
        "metric": {
            "name": "explicit_sensitive_field_exact_recovery",
            "field_selection": manifest_payload["annotation_policy"],
            "normalization": manifest_payload["normalization"],
            "engine_aggregation": "union across successful OCR-engine outputs for the same capture",
            "duplicate_rule": "mean recovered-field count within content × position × repeat cells",
        },
        "field_inventory": {
            "content_item_count": len(manifest),
            "field_bearing_content_count": sum(bool(item["fields"]) for item in manifest.values()),
            "field_count": sum(len(item["fields"]) for item in manifest.values()),
            "items": manifest,
        },
        "matched_common_short": {
            "profiles": list(PRIMARY_PROFILES),
            "excluded_position": EXCLUDED_PRIMARY_POSITION,
            "matching_rule": "content_item + position + repeat_index present in all three profiles",
            "matched_key_count": len(matched_keys),
            "profile_summaries": matched,
        },
        "all_available_short_sensitivity": {
            "description": "Duplicate-averaged short-exposure cells available for each profile; not the primary cross-profile estimand.",
            "profile_summaries": sensitivity,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Explicit Sensitive-Field Recovery",
        "",
        f"Canonical OCR archive SHA-256: `{report['source']['ocr_archive_sha256']}`.",
        "",
        "Fields were annotated before scoring; ordinary prose is excluded. Recovery is exact after the documented case/spacing/punctuation normalization.",
        "",
        "## Matched Common-Setting Short-Exposure Estimand",
        "",
        "| Profile | All matched cells | Field-bearing cells | Field opportunities | Field micro exact recovery (%) | Sample macro exact recovery (%) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    summaries = report["matched_common_short"]["profile_summaries"]
    for profile in report["matched_common_short"]["profiles"]:
        item = summaries[profile]
        lines.append(
            f"| {profile.replace('_', ' ')} | {item['all_cell_count']} | "
            f"{item['field_bearing_cell_count']} | {item['field_opportunities']} | "
            f"{item['micro_exact_recovery'] * 100:.1f} | "
            f"{item['sample_macro_exact_recovery'] * 100:.1f} |"
        )
    lines.extend([
        "",
        f"The primary pool excludes `{report['matched_common_short']['excluded_position']}` and contains "
        f"{report['matched_common_short']['matched_key_count']} duplicate-averaged keys per profile.",
        "",
        "## All-Available Sensitivity",
        "",
        "| Profile | All cells | Field-bearing cells | Field micro exact recovery (%) | Sample macro exact recovery (%) |",
        "|---|---:|---:|---:|---:|",
    ])
    for profile, item in report["all_available_short_sensitivity"]["profile_summaries"].items():
        lines.append(
            f"| {profile.replace('_', ' ')} | {item['all_cell_count']} | "
            f"{item['field_bearing_cell_count']} | {item['micro_exact_recovery'] * 100:.1f} | "
            f"{item['sample_macro_exact_recovery'] * 100:.1f} |"
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUTPUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(args.input, args.manifest)
    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {json_out}")
    print(f"Wrote {md_out}")


if __name__ == "__main__":
    main()
