"""Real-capture OCR preprocessing stress test on the matched primary pool.

Each panel pairs raw-input recovery with the per-capture oracle over the fixed,
predeclared preprocessing grid.  Exact values are reported in the manuscript
table; this figure emphasizes the direction and engine dependence of the gain.
"""
from __future__ import annotations

from matplotlib.lines import Line2D

import figstyle as fs

ENGINES = [
    ("tesseract", "Tesseract"),
    ("easyocr", "EasyOCR"),
    ("surya", "Surya"),
]

PROFILES = [
    ("original", "Original"),
    ("deployed", "Readability-priority"),
    ("high_suppression", "High-suppression"),
]

REPORT_FILES = {
    engine: f"real_capture_preprocessing_attack_{engine}.json"
    for engine, _ in ENGINES
}


def _matched_profile_means(report: dict, oracle: str) -> dict[str, float]:
    contrasts = report["oracles"][oracle]["contrasts"]
    deployed = contrasts["original_minus_deployed"]
    high = contrasts["original_minus_high_suppression"]

    if deployed["matched_unit_count"] != 288 or high["matched_unit_count"] != 288:
        raise ValueError("preprocessing figure requires 288 matched units per profile")
    if abs(deployed["matched_baseline_mean"] - high["matched_baseline_mean"]) > 1e-12:
        raise ValueError("inconsistent matched original means across contrasts")

    return {
        "original": 100.0 * deployed["matched_baseline_mean"],
        "deployed": 100.0 * deployed["matched_treatment_mean"],
        "high_suppression": 100.0 * high["matched_treatment_mean"],
    }


def load_preprocessing_recovery() -> dict[str, dict[str, dict[str, float]]]:
    """Load matched raw/grid-oracle recovery from the three engine reports."""
    values: dict[str, dict[str, dict[str, float]]] = {}
    for engine, _ in ENGINES:
        report = fs.load(REPORT_FILES[engine])
        raw = _matched_profile_means(report, "raw")
        grid = _matched_profile_means(report, "best_preprocessing_engine")
        values[engine] = {
            profile: {"raw": raw[profile], "grid_oracle": grid[profile]}
            for profile, _ in PROFILES
        }
    return values


def main() -> None:
    values = load_preprocessing_recovery()
    fig, axes = fs.plt.subplots(3, 1, figsize=(fs.COL_W, 3.15), sharex=True)
    y_positions = list(range(len(ENGINES)))

    for ax, (profile, profile_label) in zip(axes, PROFILES, strict=True):
        for y, (engine, _) in zip(y_positions, ENGINES, strict=True):
            raw = values[engine][profile]["raw"]
            oracle = values[engine][profile]["grid_oracle"]
            ax.plot([raw, oracle], [y, y], color="0.65", linewidth=1.2, zorder=1)
            ax.plot(
                raw, y, marker="o", linestyle="none", markersize=4.8,
                markerfacecolor="white", markeredgecolor="dimgray",
                markeredgewidth=0.9, zorder=2,
            )
            ax.plot(
                oracle, y, marker="D", linestyle="none", markersize=4.5,
                markerfacecolor="blue", markeredgecolor="blue", zorder=3,
            )

        ax.set_title(profile_label, loc="left", pad=2, fontsize=8.5)
        ax.set_yticks(y_positions)
        ax.set_yticklabels([label for _, label in ENGINES])
        ax.set_ylim(len(ENGINES) - 0.5, -0.5)
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.grid(axis="x")

    axes[-1].set_xlabel("Matched character recovery (%)")
    axes[-1].legend(
        handles=[
            Line2D([], [], marker="o", linestyle="none", markersize=4.8,
                   markerfacecolor="white", markeredgecolor="dimgray",
                   label="Raw input"),
            Line2D([], [], marker="D", linestyle="none", markersize=4.5,
                   markerfacecolor="blue", markeredgecolor="blue",
                   label="Fixed-grid oracle"),
        ],
        loc="center right", ncol=2, fontsize=7, handletextpad=0.35,
        columnspacing=0.8, borderpad=0.35,
    )
    fig.subplots_adjust(hspace=0.42)
    fs.save(fig, "real_engine_ocr")


if __name__ == "__main__":
    main()
