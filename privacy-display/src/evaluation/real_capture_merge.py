"""Merge replacement OCR-engine rows into real-camera capture reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from src.evaluation.real_capture import (
    REAL_CAPTURE_JSON,
    REAL_CAPTURE_MD,
    render_real_capture_markdown,
    summarize_real_capture_rows,
)


DEFAULT_ENGINE_ORDER = ("tesseract", "easyocr", "surya")


def capture_row_key(row: dict) -> tuple[str, ...]:
    fields = ("id", "image", "condition", "ablation", "attack", "profile")
    return tuple(str(row.get(field, "")) for field in fields)


def replace_engine_rows(
    existing: dict,
    replacement: dict,
    *,
    engine: str,
    remove_engines: Iterable[str],
    replacement_source: str = "",
) -> tuple[dict, dict]:
    """Replace legacy/current rows for one engine while preserving other engines."""
    old_rows = _capture_rows(existing, "existing")
    replacement_rows = [
        row
        for row in _capture_rows(replacement, "replacement")
        if row.get("engine") == engine
    ]
    remove_set = set(remove_engines)
    remove_set.add(engine)

    key_order = _unique_keys(old_rows)
    expected_keys = set(key_order)
    expected_captures = int(
        existing.get("config", {}).get("n_captures") or len(expected_keys)
    )
    if expected_captures != len(expected_keys):
        raise ValueError(
            "existing report capture count mismatch: "
            f"config={expected_captures}, unique={len(expected_keys)}"
        )

    replacement_by_key: dict[tuple[str, ...], dict] = {}
    for row in replacement_rows:
        key = capture_row_key(row)
        if key in replacement_by_key:
            raise ValueError(f"duplicate {engine} replacement row for capture {key[0]!r}")
        replacement_by_key[key] = row

    replacement_keys = set(replacement_by_key)
    if replacement_keys != expected_keys:
        missing = sorted(key[0] for key in expected_keys - replacement_keys)
        extra = sorted(key[0] for key in replacement_keys - expected_keys)
        raise ValueError(
            f"{engine} replacement capture mismatch: "
            f"missing={missing[:5]} extra={extra[:5]}"
        )

    error_rows = [row for row in replacement_rows if row.get("ocr_error")]
    if error_rows:
        raise ValueError(
            f"refusing to merge {len(error_rows)} {engine} error rows; "
            f"first error: {error_rows[0].get('ocr_error')}"
        )

    kept_by_key: dict[tuple[str, ...], list[dict]] = {
        key: [] for key in key_order
    }
    removed_rows = 0
    for row in old_rows:
        key = capture_row_key(row)
        if row.get("engine") in remove_set:
            removed_rows += 1
            continue
        kept_by_key.setdefault(key, []).append(row)

    merged_rows: list[dict] = []
    for key in key_order:
        merged_rows.extend(kept_by_key.get(key, []))
        merged_rows.append(replacement_by_key[key])

    engines = _ordered_engines(merged_rows)
    config = {
        key: value
        for key, value in dict(existing.get("config", {})).items()
        if not str(key).startswith("paddleocr_") and key != "paddleocr_rerun"
    }
    config.update({
        "engines": engines,
        "n_captures": expected_captures,
        "n_rows": len(merged_rows),
        f"{engine}_rerun_source": replacement_source,
        f"{engine}_rerun_replaced_legacy_rows": removed_rows,
        f"{engine}_rerun_rows": len(replacement_rows),
    })

    updated = dict(existing)
    updated["config"] = config
    updated["summary"] = summarize_real_capture_rows(merged_rows)
    updated["captures"] = merged_rows
    stats = {
        "engine": engine,
        "captures": expected_captures,
        "replacement_rows": len(replacement_rows),
        "removed_legacy_rows": removed_rows,
        "total_rows": len(merged_rows),
    }
    return updated, stats


def aggregate_position_reports(
    report_paths: Iterable[str | Path],
    *,
    required_engines: Iterable[str] = DEFAULT_ENGINE_ORDER,
    forbidden_engines: Iterable[str] = ("paddleocr",),
    ocr_timeout: float | None = None,
) -> tuple[dict | None, list[str]]:
    """Aggregate complete per-position reports, or return pending report names."""
    required = tuple(required_engines)
    forbidden = set(forbidden_engines)
    rows: list[dict] = []
    positions: list[dict] = []
    source_reports: list[str] = []
    pending: list[str] = []

    for raw_path in report_paths:
        path = Path(raw_path)
        report = _load_report(path)
        report_rows = _capture_rows(report, str(path))
        n_captures = int(report.get("config", {}).get("n_captures") or 0)
        counts = {
            engine: sum(1 for row in report_rows if row.get("engine") == engine)
            for engine in required
        }
        present = {str(row.get("engine")) for row in report_rows if row.get("engine")}
        has_forbidden = bool(present.intersection(forbidden))
        has_errors = any(
            row.get("ocr_error")
            for row in report_rows
            if row.get("engine") in required
        )
        if (
            n_captures <= 0
            or any(counts[engine] != n_captures for engine in required)
            or has_forbidden
            or has_errors
        ):
            pending.append(path.parent.name)
            continue

        position = _position_from_path(path)
        enriched_rows = []
        for row in report_rows:
            enriched = dict(row)
            enriched.setdefault("position", position)
            enriched_rows.append(enriched)
        rows.extend(enriched_rows)
        source_reports.append(str(path))
        positions.append({
            "position": position,
            "distance_m": _first_value(enriched_rows, "distance_m"),
            "angle_degrees": _first_value(enriched_rows, "angle_degrees"),
            "n_captures": n_captures,
            "n_rows": len(enriched_rows),
            "source_report": str(path),
        })

    if pending:
        return None, pending

    merged = {
        "schema_version": 2,
        "capture_dir": "multiple",
        "metadata_file": "metadata.json",
        "config": {
            "engines": list(required),
            "n_positions": len(positions),
            "n_captures": sum(pos["n_captures"] for pos in positions),
            "n_rows": len(rows),
            "ocr_timeout": ocr_timeout,
            "source_reports": source_reports,
            "surya_rerun": True,
        },
        "positions": positions,
        "summary": summarize_real_capture_rows(rows),
        "captures": rows,
    }
    return merged, []


def write_real_capture_report(path: str | Path, report: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (path.parent / REAL_CAPTURE_MD).write_text(
        render_real_capture_markdown(report),
        encoding="utf-8",
    )


def _capture_rows(report: dict, label: str) -> list[dict]:
    rows = report.get("captures")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{label} report must contain an object-valued captures list")
    return rows


def _load_report(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _unique_keys(rows: list[dict]) -> list[tuple[str, ...]]:
    seen: set[tuple[str, ...]] = set()
    keys: list[tuple[str, ...]] = []
    for row in rows:
        key = capture_row_key(row)
        if key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def _ordered_engines(rows: list[dict]) -> list[str]:
    present = {str(row.get("engine")) for row in rows if row.get("engine")}
    ordered = [engine for engine in DEFAULT_ENGINE_ORDER if engine in present]
    ordered.extend(sorted(present.difference(ordered)))
    return ordered


def _position_from_path(path: Path) -> str:
    return path.parent.name.removeprefix("results_").removesuffix("_final")


def _first_value(rows: list[dict], field: str):
    return next((row.get(field) for row in rows if row.get(field) is not None), None)
