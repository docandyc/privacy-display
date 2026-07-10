"""Bound VLM recovery when API failures may be non-random."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_INPUTS = (
    Path("experiments/results/real_capture_vlm.json"),
    Path("experiments/results/real_capture_vlm_d1_a0.json"),
    Path("experiments/results/real_capture_vlm_d1.5_a0.json"),
)


def bound_condition_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    planned = len(rows)
    successful = [row for row in rows if not str(row.get("vlm_error") or "").strip()]
    failures = planned - len(successful)
    if planned == 0:
        raise ValueError("cannot bound an empty VLM cell")
    exact_sum = sum(float(bool(row.get("exact_match"))) for row in successful)
    char_sum = sum(float(row.get("char_accuracy") or 0.0) for row in successful)
    return {
        "planned_calls": planned,
        "successful_calls": len(successful),
        "error_calls": failures,
        "conditional_exact_match": exact_sum / len(successful) if successful else None,
        "conditional_char_accuracy": char_sum / len(successful) if successful else None,
        "exact_match_bounds": [exact_sum / planned, (exact_sum + failures) / planned],
        "char_accuracy_bounds": [char_sum / planned, (char_sum + failures) / planned],
        "bound_rule": "failed calls assigned recovery 0 for the lower bound and 1 for the upper bound",
    }


def build_report(paths: list[str | Path]) -> dict[str, Any]:
    sessions = {}
    for path_value in paths:
        path = Path(path_value)
        payload = json.loads(path.read_text(encoding="utf-8"))
        session = {}
        for model, model_payload in payload["models"].items():
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in model_payload["rows"]:
                grouped[str(row.get("condition") or "unknown")].append(row)
            session[model] = {
                condition: bound_condition_rows(rows)
                for condition, rows in sorted(grouped.items())
            }
        sessions[str(path)] = session
    return {
        "schema_version": 1,
        "interpretation": (
            "Bounds include every planned call. Conditional successful-call means must not be used "
            "to rank models when failure patterns differ."
        ),
        "sessions": sessions,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# VLM Missing-Response Bounds",
        "",
        report["interpretation"],
        "",
        "| Session | Model | Condition | Success/planned | Exact bounds (%) | Character bounds (%) |",
        "|---|---|---|---:|---:|---:|",
    ]
    for session, models in report["sessions"].items():
        for model, conditions in models.items():
            for condition, item in conditions.items():
                exact = item["exact_match_bounds"]
                char = item["char_accuracy_bounds"]
                lines.append(
                    f"| {Path(session).name} | {model} | {condition} | "
                    f"{item['successful_calls']}/{item['planned_calls']} | "
                    f"[{exact[0] * 100:.1f}, {exact[1] * 100:.1f}] | "
                    f"[{char[0] * 100:.1f}, {char[1] * 100:.1f}] |"
                )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", nargs="+", default=[str(path) for path in DEFAULT_INPUTS])
    parser.add_argument("--json-out", default="experiments/results/vlm_missing_response_bounds.json")
    parser.add_argument("--md-out", default="experiments/results/vlm_missing_response_bounds.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(args.inputs)
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
