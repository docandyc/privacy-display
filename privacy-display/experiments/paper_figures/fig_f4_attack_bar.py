"""F4 - Real-capture OCR protection: grade x attack mode (best-of-engine).

Reads the same ``by_ablation_attack`` (best-of-engine, attacker-favourable)
aggregation the paper's Table `tab:real_ocr_main` reports, so the figure matches
the table cell-for-cell (e.g. original|short = 92.5%, deployed|short = 14.1%,
capture-hardened|short = 4.2%).
"""
from __future__ import annotations

import numpy as np

import figstyle as fs

# grade key in JSON -> display label
GRADES = [
    ("original", "Unprotected"),
    ("deployed", "Deployed"),
    ("vlm", "Capture-hardened"),
]
# attack-mode key in JSON -> display label
MODES = [
    ("short", "Short\nexposure"),
    ("long", "Long\nexposure"),
    ("video:temporal_mean", "Video\ntemporal-avg"),
]


def main() -> None:
    ba = fs.load("real_capture_ocr.json")["summary"]["by_ablation_attack"]

    x = np.arange(len(MODES))
    w = 0.26
    fig, (ax_c, ax_e) = fs.plt.subplots(
        2, 1, figsize=(fs.COL_W, 3.7), sharex=True
    )

    for gi, (gkey, glabel) in enumerate(GRADES):
        char = [fs.pct(ba[f"{gkey}|{mkey}"]["char_accuracy"]) for mkey, _ in MODES]
        cerr = [fs.pct_err(ba[f"{gkey}|{mkey}"]["char_accuracy"]) for mkey, _ in MODES]
        exact = [fs.pct(ba[f"{gkey}|{mkey}"]["exact_match"]) for mkey, _ in MODES]
        eerr = [fs.pct_err(ba[f"{gkey}|{mkey}"]["exact_match"]) for mkey, _ in MODES]
        off = (gi - (len(GRADES) - 1) / 2) * w
        color = fs.GRADE_COLORS[gkey]
        ax_c.bar(x + off, char, w, yerr=cerr, capsize=2, color=color,
                 edgecolor="black", linewidth=0.4, label=glabel,
                 error_kw={"elinewidth": 0.6})
        ax_e.bar(x + off, exact, w, yerr=eerr, capsize=2, color=color,
                 edgecolor="black", linewidth=0.4, error_kw={"elinewidth": 0.6})

    ax_c.set_ylabel("Char recovery (%)")
    ax_c.set_ylim(0, 100)
    ax_c.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.02),
                handlelength=1.0, columnspacing=0.8, frameon=False)
    ax_e.set_ylabel("Exact match (%)")
    ax_e.set_ylim(0, 80)
    ax_e.set_xticks(x)
    ax_e.set_xticklabels([lbl for _, lbl in MODES])
    for ax in (ax_c, ax_e):
        ax.grid(axis="y")
    # title in LaTeX caption
    fig.align_ylabels([ax_c, ax_e])
    fs.save(fig, "real_capture_bar")


if __name__ == "__main__":
    main()
