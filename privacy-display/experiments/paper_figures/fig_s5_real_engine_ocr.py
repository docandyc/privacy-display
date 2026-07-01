"""S5 - Real-capture per-engine OCR: char recovery by engine × profile (short exposure).

Grouped bars showing that all three OCR engines (Surya, EasyOCR, Tesseract) are
suppressed under real camera capture with protection enabled. Parallels
fig_s2_multiengine_ocr.py but for real-capture data instead of simulation.
"""
from __future__ import annotations

import numpy as np

import figstyle as fs

ENGINES = [
    ("surya", "Surya"),
    ("easyocr", "EasyOCR"),
    ("tesseract", "Tesseract"),
]

PROFILES = [
    ("original", "Original"),
    ("deployed", "Deployed"),
    ("capture_hardened", "Capture-\nhardened"),
]


def main() -> None:
    data = fs.load("real_capture_per_engine.json")

    x = np.arange(len(ENGINES))
    n_profiles = len(PROFILES)
    w = 0.24
    offsets = np.arange(n_profiles) * w - (n_profiles - 1) * w / 2

    colors = [
        fs.GRADE_COLORS.get(p, "gray") for p, _ in PROFILES
    ]

    fig, ax = fs.plt.subplots(figsize=(fs.COL_W, 2.6))

    for i, (prof_key, prof_label) in enumerate(PROFILES):
        vals = []
        errs = []
        for eng_key, _ in ENGINES:
            key = f"{prof_key}|short|{eng_key}"
            node = data[key]["char_accuracy"]
            vals.append(fs.pct(node))
            errs.append(fs.pct_err(node))
        ax.bar(
            x + offsets[i], vals, w,
            yerr=errs, capsize=2,
            color=colors[i], edgecolor="black", linewidth=0.4,
            label=prof_label.replace("\n", " "),
            error_kw={"elinewidth": 0.6},
        )

    ax.set_ylabel("Char recovery (%)")
    ax.set_ylim(0, 100)
    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in ENGINES])
    ax.grid(axis="y")
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.02),
              handlelength=1.0, columnspacing=0.8, frameon=False, fontsize=7)
    # title in LaTeX caption
    fs.save(fig, "real_engine_ocr")


if __name__ == "__main__":
    main()
