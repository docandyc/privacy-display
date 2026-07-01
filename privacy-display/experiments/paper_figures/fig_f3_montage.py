"""F3 - Real-capture montage: readable to the eye, unreadable to the lens.

Three columns: Human-eye view (source image) | Short exposure | Long exposure.
Three rows: Unprotected | Deployed | Capture-hardened.

The human-eye column shows the original content (what the viewer sees on-screen
after temporal integration). Short and long columns show genuine EMEET S600
captures (0.5 m, 15 deg). A per-column gain keeps comparisons fair.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

import figstyle as fs

CAP_DIR = fs.ROOT / "experiments" / "real_captures_d0.5_a15_final"
SRC_IMG = fs.ROOT / "data" / "test_images" / "en_sentence_00.png"

FILES = {
    ("original", "short"): "emeet_smartcam_s600_original_short_15deg_0.5m_en_sentence_00_n4_163531_s00.jpg",
    ("original", "long"):  "emeet_smartcam_s600_original_long_15deg_0.5m_en_sentence_00_n4_163537_s00.jpg",
    ("deployed", "short"): "emeet_smartcam_s600_deployed_short_15deg_0.5m_en_sentence_00_n4_164257_s00.jpg",
    ("deployed", "long"):  "emeet_smartcam_s600_deployed_long_15deg_0.5m_en_sentence_00_n4_164302_s00.jpg",
    ("vlm", "short"):      "emeet_smartcam_s600_vlm_short_15deg_0.5m_en_sentence_00_n4_164533_s00.jpg",
    ("vlm", "long"):       "emeet_smartcam_s600_vlm_long_15deg_0.5m_en_sentence_00_n4_164538_s00.jpg",
}
GRADES = [("Unprotected", "original"), ("Deployed", "deployed"), ("Hardened", "vlm")]
COLS = [("eye", "Human eye\n(integrated)"), ("short", "Short exposure\n(single frame)"), ("long", "Long exposure")]

GAIN = {"short": 1.9, "long": 1.05, "eye": 1.0}
CROP_TOP, CROP_BOT = 0.40, 0.61


def _load_capture(path, gain):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=float) / 255.0
    a = np.clip(a * gain, 0.0, 1.0)
    h = a.shape[0]
    return a[int(h * CROP_TOP):int(h * CROP_BOT)]


def _load_source(path, target_shape):
    """Load the source content image, resize to match capture panel dimensions."""
    img = Image.open(path).convert("RGB")
    th, tw = target_shape[:2]
    img_r = img.resize((tw, th), Image.LANCZOS)
    return np.asarray(img_r, dtype=float) / 255.0


def main() -> None:
    ref = _load_capture(CAP_DIR / FILES[("original", "short")], GAIN["short"])
    ref_shape = ref.shape

    fig, axes = fs.plt.subplots(len(GRADES), len(COLS),
                                figsize=(fs.FULL_W * 0.88, fs.FULL_W * 0.32),
                                layout="constrained")
    for r, (glabel, gkey) in enumerate(GRADES):
        for c, (mkey, mlabel) in enumerate(COLS):
            ax = axes[r, c]
            if mkey == "eye":
                panel = _load_source(SRC_IMG, ref_shape)
            else:
                panel = _load_capture(CAP_DIR / FILES[(gkey, mkey)], GAIN[mkey])
            ax.imshow(panel)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)
            for sp in ax.spines.values():
                sp.set_edgecolor("#BBBBBB")
                sp.set_linewidth(0.5)
            if r == 0:
                ax.set_title(mlabel, fontsize=8)
            if c == 0:
                ax.set_ylabel(glabel, fontsize=7.5, labelpad=3)
    # suptitle in LaTeX caption
    fs.save(fig, "real_capture_montage")


if __name__ == "__main__":
    main()
