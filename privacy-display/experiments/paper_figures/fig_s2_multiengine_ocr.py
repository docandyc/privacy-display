"""S2 - OCR-engine generalization: original vs single-subframe, per engine.

Paired bars per OCR engine (``corpus_multi_engine.json``): the unprotected frame
is read at ~94% char accuracy by every engine, the single protected subframe at
~0% -- the defence is engine-agnostic. 95% bootstrap CI error bars.
"""
from __future__ import annotations

import numpy as np

import figstyle as fs

ENGINES = [
    ("tesseract", "Tesseract"),
    ("easyocr", "EasyOCR"),
    ("surya", "Surya"),
]


def main() -> None:
    data = fs.load("corpus_multi_engine.json")

    x = np.arange(len(ENGINES))
    w = 0.36
    fig, ax = fs.plt.subplots(figsize=(fs.COL_W, 2.4))

    orig = [fs.pct(data[k]["original_mean"]) for k, _ in ENGINES]
    orig_e = [fs.pct_err(data[k]["original_mean"]) for k, _ in ENGINES]
    sub = [fs.pct(data[k]["subframe_mean"]) for k, _ in ENGINES]
    sub_e = [fs.pct_err(data[k]["subframe_mean"]) for k, _ in ENGINES]

    ax.bar(x - w / 2, orig, w, yerr=orig_e, capsize=2, color=fs.GRADE_COLORS["original"],
           edgecolor="black", linewidth=0.4, label="Original frame",
           error_kw={"elinewidth": 0.6})
    ax.bar(x + w / 2, sub, w, yerr=sub_e, capsize=2, color=fs.GRADE_COLORS["protected"],
           edgecolor="black", linewidth=0.4, label="Single protected subframe",
           error_kw={"elinewidth": 0.6})

    ax.set_ylabel("Char accuracy (%)")
    ax.set_ylim(0, 100)
    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in ENGINES])
    ax.grid(axis="y")
    ax.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.02),
              handlelength=1.0, frameon=False)
    # title in LaTeX caption
    fs.save(fig, "multiengine_ocr")


if __name__ == "__main__":
    main()
