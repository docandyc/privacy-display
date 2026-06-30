"""Finalize canonical real-capture publication artifacts.

This script is intentionally a packaging step. It consumes already generated
real-capture OCR and MOT result JSON files, then writes the canonical artifacts
under ``experiments/results`` for publication summary and manifest generation.
It does not rerun OCR, detectors, trackers, or camera capture.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.real_capture import (  # noqa: E402
    REAL_CAPTURE_JSON,
    REAL_CAPTURE_MD,
    render_real_capture_markdown,
    summarize_real_capture_rows,
)

REAL_CAPTURE_MOT_DETECTION_JSON = "real_capture_mot_detection.json"
REAL_CAPTURE_MOT_TRACKING_JSON = "real_capture_mot_tracking.json"
REAL_CAPTURE_MOT_MANIFEST_JSON = "real_capture_mot_capture_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Finalize real-capture OCR/MOT artifacts into experiments/results."
    )
    parser.add_argument(
        "--project-root",
        default=str(ROOT),
        help="Project root containing experiments/, src/, and tests/.",
    )
    parser.add_argument(
        "--ocr-results-glob",
        default="experiments/results_d*_final/real_capture_ocr.json",
        help="Glob of per-position OCR result JSON files, relative to project root.",
    )
    parser.add_argument(
        "--output-dir",
        default="experiments/results",
        help="Canonical output directory, relative to project root unless absolute.",
    )
    parser.add_argument(
        "--mot-source-dir",
        default="experiments/results_d1.5_a0_detection/results",
        help="Directory containing canonical MOT real-capture result JSON files.",
    )
    parser.add_argument(
        "--mot-capture-dir",
        default="experiments/results_d1.5_a0_detection/captures/mot_MOT17-09-FRCNN",
        help="Directory containing the already captured MOT real images and manifest.",
    )
    parser.add_argument(
        "--skip-mot",
        action="store_true",
        help="Only merge the OCR position matrix; do not copy MOT artifacts.",
    )
    return parser.parse_args()


def finalize_real_capture_artifacts(
    *,
    project_root: str | Path = ROOT,
    ocr_results_glob: str = "experiments/results_d*_final/real_capture_ocr.json",
    output_dir: str | Path = "experiments/results",
    mot_source_dir: str | Path = "experiments/results_d1.5_a0_detection/results",
    mot_capture_dir: str | Path = "experiments/results_d1.5_a0_detection/captures/mot_MOT17-09-FRCNN",
    include_mot: bool = True,
) -> dict:
    """Write canonical OCR and MOT real-capture artifacts.

    Returns a small summary suitable for CLI output and tests.
    """
    root = Path(project_root)
    out_dir = _resolve(root, output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ocr_paths = sorted(root.glob(ocr_results_glob))
    if not ocr_paths:
        raise FileNotFoundError(f"no OCR result files matched {ocr_results_glob!r}")
    ocr_report = merge_ocr_position_reports(root, ocr_paths)
    _write_json(out_dir / REAL_CAPTURE_JSON, ocr_report)
    (out_dir / REAL_CAPTURE_MD).write_text(
        render_real_capture_markdown(ocr_report),
        encoding="utf-8",
    )

    written = [
        _project_relative(out_dir / REAL_CAPTURE_JSON, root),
        _project_relative(out_dir / REAL_CAPTURE_MD, root),
    ]

    if include_mot:
        mot_written = finalize_mot_artifacts(
            root=root,
            source_dir=_resolve(root, mot_source_dir),
            capture_dir=_resolve(root, mot_capture_dir),
            output_dir=out_dir,
        )
        written.extend(mot_written)

    return {
        "ocr_positions": len(ocr_report["positions"]),
        "ocr_captures": ocr_report["config"]["n_captures"],
        "ocr_rows": ocr_report["config"]["n_rows"],
        "written": written,
    }


def merge_ocr_position_reports(root: Path, paths: list[Path]) -> dict:
    rows: list[dict] = []
    positions: list[dict] = []
    engines: list[str] = []
    source_results: list[str] = []
    seen_ids: set[str] = set()

    for path in paths:
        report = _load_json(path)
        captures = report.get("captures")
        if not isinstance(captures, list):
            raise ValueError(f"{path} does not contain a captures list")
        position = _position_from_report(path, report)
        source_result = _project_relative(path, root)
        source_results.append(source_result)

        position_rows: list[dict] = []
        for row in captures:
            if not isinstance(row, dict):
                raise ValueError(f"{path} contains a non-object capture row")
            merged = dict(row)
            capture_id = str(merged.get("id", ""))
            if not capture_id:
                raise ValueError(f"{path} contains a capture row without id")
            if capture_id in seen_ids:
                raise ValueError(f"duplicate capture id across OCR reports: {capture_id}")
            seen_ids.add(capture_id)
            merged["position"] = position["position"]
            merged["source_capture_dir"] = report.get("capture_dir", "")
            merged["source_result_file"] = source_result
            rows.append(merged)
            position_rows.append(merged)

        for engine in report.get("config", {}).get("engines", []):
            if engine not in engines:
                engines.append(engine)
        positions.append({
            **position,
            "n_captures": len({str(row["id"]) for row in position_rows}),
            "n_rows": len(position_rows),
            "capture_dir": report.get("capture_dir", ""),
            "source_result_file": source_result,
        })

    positions.sort(key=lambda p: (float(p.get("distance_m") or 0), float(p.get("angle_degrees") or 0)))
    return {
        "schema_version": 2,
        "capture_dir": "multiple",
        "metadata_file": "metadata.json",
        "config": {
            "engines": engines,
            "n_captures": len({str(row["id"]) for row in rows}),
            "n_rows": len(rows),
            "n_positions": len(positions),
            "source_results": source_results,
            "aggregation": "position_matrix",
        },
        "positions": positions,
        "summary": summarize_real_capture_rows(rows),
        "captures": rows,
    }


def finalize_mot_artifacts(
    *,
    root: Path,
    source_dir: Path,
    capture_dir: Path,
    output_dir: Path,
) -> list[str]:
    if not source_dir.exists():
        raise FileNotFoundError(f"MOT result source directory not found: {source_dir}")
    manifest_source = capture_dir / "capture_manifest.json"
    if not manifest_source.exists():
        raise FileNotFoundError(f"MOT capture manifest not found: {manifest_source}")

    manifest = _rewrite_mot_manifest_paths(
        _load_json(manifest_source),
        capture_dir=capture_dir,
        root=root,
    )
    manifest_out = output_dir / REAL_CAPTURE_MOT_MANIFEST_JSON
    _write_json(manifest_out, manifest)

    written = [_project_relative(manifest_out, root)]
    for filename in (REAL_CAPTURE_MOT_DETECTION_JSON, REAL_CAPTURE_MOT_TRACKING_JSON):
        result_source = source_dir / filename
        if not result_source.exists():
            raise FileNotFoundError(f"MOT result JSON not found: {result_source}")
        result = _load_json(result_source)
        capture = result.setdefault("capture", {})
        capture["manifest_path"] = _project_relative(manifest_out, root)
        capture["manifest"] = copy.deepcopy(manifest)
        out = output_dir / filename
        _write_json(out, result)
        written.append(_project_relative(out, root))
    return written


def _rewrite_mot_manifest_paths(manifest: dict, *, capture_dir: Path, root: Path) -> dict:
    out = copy.deepcopy(manifest)
    capture_rel = _project_relative(capture_dir, root)
    for row in out.get("captures", []):
        if not isinstance(row, dict):
            continue
        path = str(row.get("path", ""))
        parts = Path(path.replace("\\", "/")).parts
        try:
            mot_index = parts.index(capture_dir.name)
            suffix = parts[mot_index + 1 :]
        except ValueError:
            suffix = parts[-2:] if len(parts) >= 2 else parts
        row["path"] = str(Path(capture_rel, *suffix)).replace("\\", "/")
    return out


def _position_from_report(path: Path, report: dict) -> dict:
    captures = report.get("captures", [])
    row = captures[0] if captures else {}
    distance = _first_float(row.get("distance_m"), report.get("distance_m"))
    angle = _first_float(row.get("angle_degrees"), report.get("angle_degrees"))
    if distance is None or angle is None:
        position = path.parent.name.replace("results_", "").replace("_final", "")
        distance, angle = _parse_position_label(position)
    else:
        position = f"d{_format_number(distance)}_a{_format_number(angle)}"
    return {
        "position": position,
        "distance_m": distance,
        "angle_degrees": angle,
    }


def _parse_position_label(label: str) -> tuple[float | None, float | None]:
    try:
        d_part, a_part = label.split("_", 1)
        return float(d_part.removeprefix("d")), float(a_part.removeprefix("a"))
    except (ValueError, AttributeError):
        return None, None


def _first_float(*values: Any) -> float | None:
    for value in values:
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _format_number(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _resolve(root: Path, path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else root / p


def _project_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main() -> int:
    args = parse_args()
    summary = finalize_real_capture_artifacts(
        project_root=args.project_root,
        ocr_results_glob=args.ocr_results_glob,
        output_dir=args.output_dir,
        mot_source_dir=args.mot_source_dir,
        mot_capture_dir=args.mot_capture_dir,
        include_mot=not args.skip_mot,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
