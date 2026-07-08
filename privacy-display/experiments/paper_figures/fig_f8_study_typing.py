"""F8 - User study typing task: control vs deployed masked, within-subject.

Reads ``webstudy/analysis_output/typing_participant_means.csv`` (written by
``webstudy/analyze_study.py``). Each panel is a paired slope plot: one gray
line per participant (mean of two trials per condition), plus group means
with participant-level bootstrap 95% CIs, matching the caliber reported in
the paper's Table `tab:study_typing`.

Before the study runs (file missing or empty), the figure is still emitted
with the full frame and a "data pending" note so the paper compiles.
"""
from __future__ import annotations

import csv

import numpy as np

import figstyle as fs

STUDY_OUT = fs.ROOT / "webstudy" / "analysis_output"
CSV_PATH = STUDY_OUT / "typing_participant_means.csv"

# (csv metric key, panel label, unit scale)
PANELS = [
    ("accuracy", "Accuracy (%)", 100.0),
    ("wpm", "WPM", 1.0),
    ("first_key_latency_ms", "First-key\nlatency (ms)", 1.0),
]
CONDITIONS = [("control", "Control"), ("masked", "Masked")]
BOOTSTRAP_SAMPLES = 10_000


def load_rows() -> list[dict[str, float]]:
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def mean_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float, float]:
    """Group mean with participant-level bootstrap 95% CI (analyze_study caliber)."""
    mean = float(values.mean())
    if values.size < 2:
        return mean, mean, mean
    draws = rng.choice(values, size=(BOOTSTRAP_SAMPLES, values.size), replace=True).mean(axis=1)
    low, high = np.quantile(draws, [0.025, 0.975])
    return mean, float(low), float(high)


def main() -> None:
    rows = load_rows()
    rng = np.random.default_rng(20260703)

    fig, axes = fs.plt.subplots(1, len(PANELS), figsize=(fs.COL_W, 1.9))
    x = np.arange(len(CONDITIONS))

    for ax, (metric, label, scale) in zip(axes, PANELS):
        ax.set_ylabel(label)
        ax.set_xticks(x)
        ax.set_xticklabels([lbl for _, lbl in CONDITIONS])
        ax.set_xlim(-0.45, 1.45)
        ax.grid(axis="y")
        pairs = np.array([
            [float(row[f"{ckey}_{metric}"]) * scale for ckey, _ in CONDITIONS]
            for row in rows
            if row.get(f"control_{metric}") not in (None, "")
            and row.get(f"masked_{metric}") not in (None, "")
        ])
        if pairs.size == 0:
            ax.set_ylim(0, 1)
            ax.set_yticks([])
            ax.text(0.5, 0.5, "data\npending", transform=ax.transAxes,
                    ha="center", va="center", color="0.6", fontsize=8, style="italic")
            continue
        for pair in pairs:  # one gray line per participant
            ax.plot(x, pair, color="0.75", linewidth=0.6, zorder=1)
        for ci, (ckey, _) in enumerate(CONDITIONS):
            mean, low, high = mean_ci(pairs[:, ci], rng)
            color = fs.GRADE_COLORS["original" if ckey == "control" else "deployed"]
            ax.errorbar(ci, mean, yerr=[[mean - low], [high - mean]],
                        fmt="o", color=color, markersize=4.5, capsize=2.5,
                        elinewidth=1.0, zorder=3)

    fig.tight_layout(w_pad=0.8)
    fs.save(fig, "study_typing_paired")


if __name__ == "__main__":
    main()
