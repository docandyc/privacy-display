"""S3 - Privacy vs usability across screen-privacy baselines.

Scatter from ``screen_privacy_baselines.json``: x = OCR char recovery (privacy
leak, lower-left is safer), y = CIEDE2000 dE of the human view (visual
distortion, lower is better). Our temporal-mask sits in the ideal low-leak /
low-distortion corner, unlike blur/pixelate (distortion) or dimming/off-axis
(no real privacy).
"""
from __future__ import annotations

import figstyle as fs

# key -> (label, is_ours)
BASELINES = [
    ("unprotected", "Unprotected", False),
    ("dim_50pct", "Dim 50%", False),
    ("gaussian_blur", "Gaussian blur", False),
    ("pixelate_12px", "Pixelate 12px", False),
    ("privacy_filter_offaxis_proxy", "Privacy filter (off-axis)", False),
    ("temporal_mask_single_subframe", "Temporal mask (ours)", True),
]


def main() -> None:
    data = fs.load("screen_privacy_baselines.json")
    node = data.get("summary", data)

    fig, ax = fs.plt.subplots(figsize=(fs.COL_W, 2.9))
    for key, label, ours in BASELINES:
        v = node[key]
        x = fs.pct(v["char_accuracy"])
        y = fs.mean_hw(v["delta_e"])[0]
        ax.scatter([x], [y], s=110 if ours else 50,
                   marker="*" if ours else "o",
                   color="red" if ours else "blue",
                   edgecolor="black", linewidth=0.5, zorder=4 if ours else 3)
        dy = 1.6 if not ours else -3.0
        ax.annotate(label, (x, y), fontsize=6,
                    xytext=(4, dy), textcoords="offset points")

    ax.set_xlabel("OCR char recovery (%)  -  privacy leak (lower safer)")
    ax.set_ylabel(r"$\Delta E$ visual distortion (lower better)")
    ax.set_xlim(-5, 100)
    ax.set_ylim(-3, 58)
    # title in LaTeX caption
    ax.grid(True)
    # ideal corner marker
    ax.annotate("ideal", (0, 0), fontsize=6, style="italic", color="grey",
                xytext=(6, 6), textcoords="offset points")
    fs.save(fig, "baselines_scatter")


if __name__ == "__main__":
    main()
