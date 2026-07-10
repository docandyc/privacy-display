"""F3 - Real-capture montage: digital integrated view and camera captures.

Nine vertically stacked panels, grouped by protection profile. Within each
group: Digital integrated reconstruction | Short exposure | Long exposure.

Camera panels are genuine EMEET S600 captures from the common-setting
d1_a0 position (1.0 m, 0 deg; 3.91 ms short exposure, 31.25 ms long
exposure) with no brightness gain applied. The digital integrated panels
are computed with the deployment playback pipeline: the unprotected row
shows the displayed source frame, while the readability-priority and
high-suppression rows show the brightness-aligned full-cycle integration
(n=4 subframes plus the alpha=0.2 inversion slot) of their actual profile
configurations. These panels reproduce the display-side playback configuration
at the real-capture canvas size; they are not the native-resolution corpus
realizations used to aggregate SSIM/DeltaE00, nor are they human-readability or
visual-comfort evidence.
"""
from __future__ import annotations

import sys
from functools import lru_cache

import numpy as np
from PIL import Image

import figstyle as fs

sys.path.insert(0, str(fs.ROOT))

from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.demo.playback_demo import build_playback_frames, fit_image_to_canvas  # noqa: E402

CAP_DIR = fs.ROOT / "experiments" / "real_captures_d1_a0_final"
SRC_IMG = fs.ROOT / "data" / "test_images" / "en_sentence_00.png"

FILES = {
    ("original", "short"): "emeet_smartcam_s600_original_short_0deg_1m_en_sentence_00_n4_120852_s00.jpg",
    ("original", "long"):  "emeet_smartcam_s600_original_long_0deg_1m_en_sentence_00_n4_120856_s00.jpg",
    ("deployed", "short"): "emeet_smartcam_s600_deployed_short_0deg_1m_en_sentence_00_n4_121623_s00.jpg",
    ("deployed", "long"):  "emeet_smartcam_s600_deployed_long_0deg_1m_en_sentence_00_n4_121628_s00.jpg",
    ("vlm", "short"):      "emeet_smartcam_s600_vlm_short_0deg_1m_en_sentence_00_n4_121904_s00.jpg",
    ("vlm", "long"):       "emeet_smartcam_s600_vlm_long_0deg_1m_en_sentence_00_n4_121907_s00.jpg",
}
GRADES = [
    ("Unprotected", "original"),
    ("Readability-priority", "deployed"),
    ("High-suppression", "vlm"),
]
COLS = [
    ("eye", "Digital integrated\nreconstruction"),
    ("short", "Short exposure\n(single frame)"),
    ("long", "Long exposure"),
]

# No brightness manipulation: the 3.91/31.25 ms common-setting captures are
# adequately exposed, so panels show the archived raw camera JPEGs (no
# geometric correction; a fixed vertical band crop only).
GAIN = {"short": 1.0, "long": 1.0, "eye": 1.0}
CROP_TOP, CROP_BOT = 0.40, 0.61
PLAYBACK_WIDTH, PLAYBACK_HEIGHT = 1920, 1080

# Deployment-faithful integration parameters (match paper Table "Profile
# Composition Summary" and the anti-OCR profile ablation pipeline).
N_SUBFRAMES = 4
EPSILON = 8 / 255
INVERSION_ALPHA = 0.2
MONTAGE_KEY = b"fig-f3-montage-integration-key00"
PROFILE_CONFIG = {
    # profile key -> (anti_ocr_profile, stripe_alpha, glyph_alpha)
    "deployed": ("strong", 0.10, 0.12),
    "vlm": ("capture_hardened", None, None),  # profile defaults: 0.42/0.55
}


def _load_capture(path, gain):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=float) / 255.0
    a = np.clip(a * gain, 0.0, 1.0)
    h = a.shape[0]
    return a[int(h * CROP_TOP):int(h * CROP_BOT)]


def _crop_panel(arr):
    h = arr.shape[0]
    return arr[int(h * CROP_TOP):int(h * CROP_BOT)]


@lru_cache(maxsize=None)
def integrated_reconstruction(gkey: str) -> np.ndarray:
    """Full-cycle brightness-aligned digital integration for one profile.

    The real-capture runner first fits each corpus item to the 1920x1080 black
    playback canvas, then generates profile frames. Reproduce that order here
    before applying the same vertical crop as the camera JPEG panels. The
    integration model matches the anti-OCR profile ablation: integrate the n
    subframes plus the inversion slot with boost=displayed_slots/gamma and a
    slot-weighted pedestal.
    """
    source = np.asarray(Image.open(SRC_IMG).convert("RGB"))
    src = fit_image_to_canvas(
        source,
        PLAYBACK_WIDTH,
        PLAYBACK_HEIGHT,
        background=(0, 0, 0),
    )
    if gkey == "original":
        integrated = src
    else:
        profile, stripe_alpha, glyph_alpha = PROFILE_CONFIG[gkey]
        frames, meta = build_playback_frames(
            src,
            n=N_SUBFRAMES,
            cycles=1,
            epsilon=EPSILON,
            insert_inversion=True,
            inversion_alpha=INVERSION_ALPHA,
            anti_ocr_profile=profile,
            stripe_alpha=stripe_alpha,
            glyph_alpha=glyph_alpha,
            key=MONTAGE_KEY,
        )
        sequence = [frame for frame, _ in frames]
        subframes = [frame for frame, kind in frames if kind == "subframe"]
        pedestal = float(meta["pedestal"])
        composer = SubframeComposer(n=N_SUBFRAMES, gamma=1.0)
        boost = len(sequence) / composer.gamma
        effective_pedestal = pedestal * (len(subframes) / len(sequence))
        integrated = composer.integrate_subframes(
            sequence,
            boost=boost,
            pedestal=effective_pedestal,
        )
    return _crop_panel(integrated).astype(np.float32) / 255.0


def build_figure():
    fig = fs.plt.figure(figsize=(fs.COL_W, 5.25), layout="constrained")
    grid = fig.add_gridspec(
        11,
        1,
        height_ratios=(1, 1, 1, 0.28, 1, 1, 1, 0.28, 1, 1, 1),
        hspace=0.16,
    )
    axes = []
    grid_row = 0
    for grade_index, (glabel, gkey) in enumerate(GRADES):
        if grade_index:
            grid_row += 1
        for mkey, mlabel in COLS:
            ax = fig.add_subplot(grid[grid_row, 0])
            axes.append(ax)
            if mkey == "eye":
                panel = integrated_reconstruction(gkey)
            else:
                panel = _load_capture(CAP_DIR / FILES[(gkey, mkey)], GAIN[mkey])
            ax.imshow(panel)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)
            for sp in ax.spines.values():
                sp.set_edgecolor("#BBBBBB")
                sp.set_linewidth(0.5)
            panel_label = mlabel.replace("\n", " ")
            ax.set_title(
                f"{glabel} - {panel_label}",
                loc="left",
                fontsize=8.5,
                fontweight="bold" if mkey == "eye" else "normal",
                pad=2,
            )
            grid_row += 1
    return fig


def main() -> None:
    fig = build_figure()
    fs.save(fig, "real_capture_montage")


if __name__ == "__main__":
    main()
