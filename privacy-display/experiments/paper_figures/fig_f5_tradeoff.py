"""F5 - Digital reconstruction vs integration-attack robustness trade-off.

Uses the anti-OCR profile ablation (``anti_ocr_profile_ablation.json`` block1),
which measures, for the SAME synthetic corpus, both:
  * temporal-average (integration attack) char recovery  -> security  (lower better)
  * complete-cycle digital-reconstruction SSIM             -> image fidelity
as the profile strengthens off -> overlay -> deployed -> capture-hardened.

SSIM is an image-level proxy and is not labelled as human readability.
"""
from __future__ import annotations

import numpy as np

import figstyle as fs

# block1 profile key -> display label (x order = weak..strong protection)
PROFILES = [
    ("block1/off", "None"),
    ("block1/strong@overlay", "Overlay"),
    ("block1/strong@deployed", "Deployed\n(alpha=0.2)"),
    ("block1/vlm", "Capture-\nhardened"),
]


def main() -> None:
    det = fs.load("anti_ocr_profile_ablation.json")["detail"]

    x = np.arange(len(PROFILES))
    sec = [fs.pct(det[k]["temporal_avg_char"]) for k, _ in PROFILES]
    sec_e = [fs.pct_err(det[k]["temporal_avg_char"]) for k, _ in PROFILES]
    ssim = [fs.mean_hw(det[k]["ssim"])[0] for k, _ in PROFILES]
    ssim_e = [fs.mean_hw(det[k]["ssim"])[1] or 0.0 for k, _ in PROFILES]

    fig, ax_l = fs.plt.subplots(figsize=(fs.COL_W, 2.6))
    ax_r = ax_l.twinx()

    c_sec, c_read = "red", "blue"
    ax_l.errorbar(x, sec, yerr=sec_e, marker="o", color=c_sec, capsize=2,
                  label="Integration-attack recovery")
    ax_r.errorbar(x, ssim, yerr=ssim_e, marker="s", color=c_read, ls="--", capsize=2,
                  label="Digital-integration SSIM")

    ax_l.set_ylabel("Temporal-avg char recovery (%)", color=c_sec)
    ax_l.tick_params(axis="y", labelcolor=c_sec)
    ax_l.set_ylim(0, 100)
    ax_r.set_ylabel("Digital-integration SSIM", color=c_read)
    ax_r.tick_params(axis="y", labelcolor=c_read)
    ax_r.set_ylim(0.6, 1.02)
    ax_r.grid(False)
    ax_l.tick_params(right=False)   # twin axis owns the right ticks

    ax_l.set_xticks(x)
    ax_l.set_xticklabels([lbl for _, lbl in PROFILES])
    ax_l.grid(axis="y")
    # title in LaTeX caption

    # single combined legend
    h1, l1 = ax_l.get_legend_handles_labels()
    h2, l2 = ax_r.get_legend_handles_labels()
    ax_l.legend(h1 + h2, l1 + l2, ncol=2, loc="lower center",
                bbox_to_anchor=(0.5, 1.02), handlelength=1.4, frameon=False,
                fontsize=7)
    fs.save(fig, "readability_robustness_tradeoff")


if __name__ == "__main__":
    main()
