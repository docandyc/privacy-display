"""S1 - Anti-OCR profile: stripe x glyph amplitude grid (twin heatmaps).

Left  heatmap: temporal-average char recovery (%) -> security (lower = safer).
Right heatmap: digital-reconstruction drift        -> image cost (lower better).
Both come from ``anti_ocr_profile_ablation.json`` block2 (attack =
temporal_average_only), a 4x3 stripe x glyph sweep. Shows protection only bites
at high stripe+glyph amplitude, at a growing digital-reconstruction cost.
"""
from __future__ import annotations

import numpy as np

import figstyle as fs


def _grid(det, stripes, glyphs, field, scale):
    g = np.full((len(stripes), len(glyphs)), np.nan)
    for i, s in enumerate(stripes):
        for j, gl in enumerate(glyphs):
            key = f"block2/s{s:.2f}_g{gl:.2f}"
            if key in det and field in det[key]:
                g[i, j] = fs.mean_hw(det[key][field])[0] * scale
    return g


def main() -> None:
    data = fs.load("anti_ocr_profile_ablation.json")
    det = data["detail"]
    stripes = data["config"]["grid_stripe"]   # [0.0, 0.10, 0.18, 0.30]
    glyphs = data["config"]["grid_glyph"]      # [0.0, 0.12, 0.22]

    sec = _grid(det, stripes, glyphs, "temporal_avg_char", 100.0)
    read = _grid(det, stripes, glyphs, "readability_drift", 1.0)

    fig, axes = fs.plt.subplots(1, 2, figsize=(fs.FULL_W * 0.72, 2.6))
    panels = [
        (axes[0], sec, "Char recovery (%)", "viridis_r", "Security (temporal-avg attack)"),
        (axes[1], read, "Reconstruction drift", "magma", "Reconstruction cost"),
    ]
    for ax, grid, cbar_label, cmap, title in panels:
        im = ax.imshow(grid, cmap=cmap, aspect="auto")
        ax.set_xticks(range(len(glyphs)))
        ax.set_xticklabels([f"{g:.2f}" for g in glyphs])
        ax.set_yticks(range(len(stripes)))
        ax.set_yticklabels([f"{s:.2f}" for s in stripes])
        ax.set_xlabel("Glyph amplitude")
        ax.set_ylabel("Stripe amplitude")
        ax.set_title(title)
        ax.grid(False)
        ax.tick_params(top=False, right=False)
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                if not np.isnan(grid[i, j]):
                    v = grid[i, j]
                    # pick readable text colour against the cell
                    ax.text(j, i, f"{v:.0f}" if v >= 10 else f"{v:.1f}",
                            ha="center", va="center", fontsize=6,
                            color="white" if cmap == "magma" and v > read[~np.isnan(read)].mean()
                            else "black")
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.ax.tick_params(labelsize=6)
        cb.set_label(cbar_label, fontsize=6.5)
    fig.tight_layout()
    fs.save(fig, "antiocr_heatmap")


if __name__ == "__main__":
    main()
