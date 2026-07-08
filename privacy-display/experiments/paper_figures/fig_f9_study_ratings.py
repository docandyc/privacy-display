"""F9 - User study subjective ratings: 6 conditions x 3 Likert dimensions.

Reads ``rating_summary`` (mean/SD per condition and dimension) from
``webstudy/analysis_output/analysis_report.json`` (written by
``webstudy/analyze_study.py``), so the bars match the paper's Table
`tab:study_ratings` cell-for-cell. Error bars show SD.

Before the study runs (file missing or empty summary), the figure is still
emitted with the full frame and a "data pending" note so the paper compiles.
"""
from __future__ import annotations

import json

import numpy as np

import figstyle as fs

STUDY_OUT = fs.ROOT / "webstudy" / "analysis_output"
REPORT_PATH = STUDY_OUT / "analysis_report.json"

# (condition key in analyze_study, tick label) - same order as the paper table
CONDITIONS = [
    ("control_anchor", "Anchor"),
    ("n2_mask_noise", "$n{=}2$\nM+N"),
    ("n3_mask_noise", "$n{=}3$\nM+N"),
    ("n4_mask_noise", "$n{=}4$\nM+N"),
    ("n4_mask_only", "$n{=}4$\nmask"),
    ("deployed_full", "Deployed"),
]
# (dimension key, legend label, series colour)
DIMENSIONS = [
    ("readability", "Readability", "blue"),
    ("flicker", "Stability", "green"),
    ("fatigue", "Comfort", "orange"),
]


def load_summary() -> dict:
    if not REPORT_PATH.exists():
        return {}
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    return report.get("rating_summary") or {}

def main() -> None:
    summary = load_summary()
    has_data = bool(summary) and all(
        summary.get(ckey, {}).get(dkey, {}).get("mean") is not None
        for ckey, _ in CONDITIONS for dkey, _, _ in DIMENSIONS
    )

    x = np.arange(len(CONDITIONS))
    w = 0.26
    fig, ax = fs.plt.subplots(figsize=(fs.COL_W, 2.1))

    for di, (dkey, dlabel, color) in enumerate(DIMENSIONS):
        off = (di - (len(DIMENSIONS) - 1) / 2) * w
        if has_data:
            means = [summary[ckey][dkey]["mean"] for ckey, _ in CONDITIONS]
            sds = [summary[ckey][dkey]["sd"] or 0.0 for ckey, _ in CONDITIONS]
        else:
            means = [0.0] * len(CONDITIONS)
            sds = [0.0] * len(CONDITIONS)
        ax.bar(x + off, means, w, yerr=sds, capsize=2, color=color,
               edgecolor="black", linewidth=0.4, label=dlabel,
               error_kw={"elinewidth": 0.6})

    ax.set_ylabel("Rating (1–5, higher better)")
    ax.set_ylim(0, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in CONDITIONS])
    ax.grid(axis="y")
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.02),
              handlelength=1.0, columnspacing=0.8, frameon=False)
    if not has_data:
        ax.text(0.5, 0.45, "data pending", transform=ax.transAxes,
                ha="center", va="center", color="0.6", fontsize=9, style="italic")

    fs.save(fig, "study_ratings_likert")


if __name__ == "__main__":
    main()
