"""S4 - One protected subframe defeats every attacker family.

Grouped bars over four attacker families (OCR, VLM, object detection, tracking).
Because each family uses a different native metric (char accuracy, mAP, MOTA),
bars are normalised to *capability retained relative to the clean baseline*
(clean = 100%). A single protected subframe drives every family to ~0%.

Sources (means across engines / models):
  OCR       corpus_multi_engine.json      original_mean vs subframe_mean
  VLM       vlm_model_ablation.json       char_accuracy vs single_frame_char_accuracy
  Detection coco_detection_attack.json    clean.map vs single_subframe.map
  Tracking  mot_tracking_attack.json      clean.mota vs single_subframe.mota
"""
from __future__ import annotations

import numpy as np

import figstyle as fs


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return float(np.mean(vals)) if vals else 0.0


def _families():
    # OCR
    oc = fs.load("corpus_multi_engine.json")
    engines = [k for k in oc if isinstance(oc[k], dict) and "original_mean" in oc[k]]
    ocr_clean = _mean([fs.mean_hw(oc[e]["original_mean"])[0] for e in engines])
    ocr_prot = _mean([fs.mean_hw(oc[e]["subframe_mean"])[0] for e in engines])

    # Detection
    cd = fs.load("coco_detection_attack.json")
    cdr = cd.get("results", cd)
    dmodels = [k for k in cdr if isinstance(cdr[k], dict) and "clean" in cdr[k]]
    det_clean = _mean([cdr[m]["clean"]["map"] for m in dmodels])
    det_prot = _mean([cdr[m]["single_subframe"]["map"] for m in dmodels])

    # Tracking
    mt = fs.load("mot_tracking_attack.json")
    mtr = mt.get("results", mt)
    tmodels = [k for k in mtr if isinstance(mtr[k], dict) and "clean" in mtr[k]]
    trk_clean = _mean([mtr[m]["clean"]["idf1"] for m in tmodels])
    trk_prot = _mean([mtr[m]["single_subframe"]["idf1"] for m in tmodels])

    return [
        ("OCR\n(char acc)", ocr_clean, ocr_prot),
        ("Detection\n(mAP)", det_clean, det_prot),
        ("Tracking\n(IDF1)", trk_clean, trk_prot),
    ]


def main() -> None:
    fams = _families()
    labels = [f[0] for f in fams]
    retained = [max(0.0, f[2]) / f[1] * 100 if f[1] else 0.0 for f in fams]

    x = np.arange(len(fams))
    w = 0.38
    fig, ax = fs.plt.subplots(figsize=(fs.COL_W, 2.5))
    ax.bar(x - w / 2, [100] * len(fams), w, color=fs.GRADE_COLORS["clean"],
           edgecolor="black", linewidth=0.4, label="Clean baseline")
    bars = ax.bar(x + w / 2, retained, w, color=fs.GRADE_COLORS["protected"],
                  edgecolor="black", linewidth=0.4, label="One protected subframe")
    for b, r in zip(bars, retained):
        ax.annotate(f"{r:.1f}%", (b.get_x() + b.get_width() / 2, r + 1),
                    ha="center", fontsize=6)

    ax.set_ylabel("Capability retained vs clean (%)")
    ax.set_ylim(0, 110)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.grid(axis="y")
    ax.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.02),
              handlelength=1.0, frameon=False)
    # title in LaTeX caption
    fs.save(fig, "all_attackers")


if __name__ == "__main__":
    main()
