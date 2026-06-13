"""
Minimal usability pilot template and summarizer.

This is intentionally a small self-report pilot path, not a formal human
subjects study. It lets the paper include a clearly scoped appendix table when
N=3-5 internal pilot observations are available.

Run:
    python experiments/usability_pilot.py --init-template
    python experiments/usability_pilot.py --input experiments/usability_pilot.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.benchmark import _mean_std  # noqa: E402


FIELDS = [
    "participant_id",
    "condition",
    "n",
    "refresh_hz",
    "profile",
    "reading_time_s",
    "readability_1_5",
    "flicker_1_5",
    "fatigue_1_5",
    "notes",
]


def write_template(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow({
            "participant_id": "p01",
            "condition": "temporal_mask_n4_240hz",
            "n": "4",
            "refresh_hz": "240",
            "profile": "strong",
            "reading_time_s": "0",
            "readability_1_5": "0",
            "flicker_1_5": "0",
            "fatigue_1_5": "0",
            "notes": "Replace this example row before analysis.",
        })
    return path


def load_rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("usability pilot CSV has no rows")
    missing = [field for field in FIELDS if field not in rows[0]]
    if missing:
        raise ValueError(f"usability pilot CSV missing fields: {', '.join(missing)}")
    cleaned = []
    for idx, row in enumerate(rows):
        if str(row.get("participant_id", "")).strip().lower() == "p01" and "Replace this example" in str(row.get("notes", "")):
            continue
        cleaned.append({
            "participant_id": str(row["participant_id"]).strip(),
            "condition": str(row["condition"]).strip(),
            "n": _int(row["n"]),
            "refresh_hz": _float(row["refresh_hz"]),
            "profile": str(row["profile"]).strip(),
            "reading_time_s": _float(row["reading_time_s"]),
            "readability_1_5": _rating(row["readability_1_5"], idx, "readability_1_5"),
            "flicker_1_5": _rating(row["flicker_1_5"], idx, "flicker_1_5"),
            "fatigue_1_5": _rating(row["fatigue_1_5"], idx, "fatigue_1_5"),
            "notes": str(row.get("notes", ""))[:240],
        })
    if not cleaned:
        raise ValueError("usability pilot CSV contains only the template/example row")
    return cleaned


def summarize(rows: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["condition"], []).append(row)
    return {
        condition: {
            "n_rows": len(group),
            "n_participants": len({row["participant_id"] for row in group}),
            "reading_time_s": _mean_std([row["reading_time_s"] for row in group]),
            "readability_1_5": _mean_std([row["readability_1_5"] for row in group]),
            "flicker_1_5": _mean_std([row["flicker_1_5"] for row in group]),
            "fatigue_1_5": _mean_std([row["fatigue_1_5"] for row in group]),
        }
        for condition, group in sorted(grouped.items())
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Usability Pilot Summary",
        "",
        "Small internal pilot only; do not report as a formal user study.",
        "",
        "| Condition | N participants | Readability | Flicker | Fatigue | Reading time |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for condition, stats in report["summary"].items():
        lines.append(
            f"| {condition} | {stats['n_participants']} | "
            f"{stats['readability_1_5']['mean']:.2f} | "
            f"{stats['flicker_1_5']['mean']:.2f} | "
            f"{stats['fatigue_1_5']['mean']:.2f} | "
            f"{stats['reading_time_s']['mean']:.1f}s |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Usability pilot template/summarizer")
    p.add_argument("--input", default=str(ROOT / "experiments" / "usability_pilot.csv"))
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    p.add_argument("--init-template", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.input)
    if args.init_template:
        out = write_template(in_path)
        print(f"Wrote usability pilot template: {out}")
        return 0

    rows = load_rows(in_path)
    report = {
        "config": {
            "input": str(in_path),
            "scope": "minimal_internal_pilot_not_formal_user_study",
            "fields": FIELDS,
        },
        "summary": summarize(rows),
        "rows": rows,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_out = out_dir / "usability_pilot.json"
    md_out = out_dir / "usability_pilot.md"
    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_out.write_text(render_markdown(report), encoding="utf-8")
    print(f"Saved: {json_out}")
    print(f"Saved: {md_out}")
    return 0


def _float(value: str) -> float:
    return float(str(value).strip())


def _int(value: str) -> int:
    return int(float(str(value).strip()))


def _rating(value: str, idx: int, field: str) -> float:
    rating = _float(value)
    if rating < 1 or rating > 5:
        raise ValueError(f"row {idx} {field} must be in [1, 5]")
    return rating


if __name__ == "__main__":
    raise SystemExit(main())
