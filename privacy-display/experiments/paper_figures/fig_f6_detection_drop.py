"""F6 - Real-capture object detection: mAP50 collapse under protection.

Grouped bars, one group per detector, three bars per group for the
real_clean / real_short / real_video capture conditions. Detection metrics are
computed over the full image set (no bootstrap CI), so no error bars.
"""
from __future__ import annotations

import numpy as np

import figstyle as fs

MODELS = [
    ("yolo26x", "YOLO26x"),
    ("rtdetr-x", "RT-DETR-x"),
    ("faster_rcnn", "Faster R-CNN"),
    ("retinanet", "RetinaNet"),
]
CONDS = [
    ("real_clean", "Clean capture", "dimgray"),
    ("real_short", "Short exposure", "blue"),
    ("real_video", "Video temporal-avg", "red"),
]


def main() -> None:
    res = fs.load("real_capture_coco_detection.json")["results"]

    x = np.arange(len(MODELS))
    w = 0.26
    fig, ax = fs.plt.subplots(figsize=(fs.COL_W, 2.5))

    for ci, (ckey, clabel, color) in enumerate(CONDS):
        vals = [res[mkey][ckey]["map50"] * 100 for mkey, _ in MODELS]
        off = (ci - (len(CONDS) - 1) / 2) * w
        ax.bar(x + off, vals, w, color=color, edgecolor="black",
               linewidth=0.4, label=clabel)

    ax.set_ylabel("mAP@50 (%)")
    ax.set_ylim(0, 60)
    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in MODELS], rotation=12, ha="right")
    ax.grid(axis="y")
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.02),
              handlelength=1.0, columnspacing=0.8, frameon=False)
    # title in LaTeX caption
    fs.save(fig, "real_detection_drop")


if __name__ == "__main__":
    main()
