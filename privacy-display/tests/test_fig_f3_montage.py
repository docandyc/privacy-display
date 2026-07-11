from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pytest
from PIL import Image


PAPER_FIGURES = Path(__file__).resolve().parents[1] / "experiments" / "paper_figures"
sys.path.insert(0, str(PAPER_FIGURES))

import fig_f3_montage as montage  # noqa: E402
import figstyle as fs  # noqa: E402
from src.demo.playback_demo import fit_image_to_canvas  # noqa: E402


PAPER_DIR = Path(__file__).resolve().parents[2] / "paper"


def test_montage_uses_native_single_column_vertical_sequence():
    fig = montage.build_figure()
    try:
        assert fig.get_figwidth() == pytest.approx(fs.COL_W)
        assert len(fig.axes) == 9
        assert [ax.get_title(loc="left") for ax in fig.axes] == [
            "Unprotected - Digital integrated reconstruction",
            "Unprotected - Short exposure (single frame)",
            "Unprotected - Long exposure",
            "Readability-priority - Digital integrated reconstruction",
            "Readability-priority - Short exposure (single frame)",
            "Readability-priority - Long exposure",
            "High-suppression - Digital integrated reconstruction",
            "High-suppression - Short exposure (single frame)",
            "High-suppression - Long exposure",
        ]
        assert all(len(ax.images) == 1 for ax in fig.axes)
    finally:
        fs.plt.close(fig)


def test_capture_manifest_uses_d1_a0_common_setting():
    expected_files = {
        ("original", "short"): (
            "emeet_smartcam_s600_original_short_0deg_1m_"
            "en_sentence_00_n4_120852_s00.jpg"
        ),
        ("original", "long"): (
            "emeet_smartcam_s600_original_long_0deg_1m_"
            "en_sentence_00_n4_120856_s00.jpg"
        ),
        ("deployed", "short"): (
            "emeet_smartcam_s600_deployed_short_0deg_1m_"
            "en_sentence_00_n4_121623_s00.jpg"
        ),
        ("deployed", "long"): (
            "emeet_smartcam_s600_deployed_long_0deg_1m_"
            "en_sentence_00_n4_121628_s00.jpg"
        ),
        ("vlm", "short"): (
            "emeet_smartcam_s600_vlm_short_0deg_1m_"
            "en_sentence_00_n4_121904_s00.jpg"
        ),
        ("vlm", "long"): (
            "emeet_smartcam_s600_vlm_long_0deg_1m_"
            "en_sentence_00_n4_121907_s00.jpg"
        ),
    }
    assert montage.CAP_DIR.name == "real_captures_d1_a0_final"
    assert montage.FILES == expected_files

    metadata = json.loads((montage.CAP_DIR / "metadata.json").read_text())
    by_image = {row["image"]: row for row in metadata["captures"]}
    for (_, attack), filename in expected_files.items():
        assert (montage.CAP_DIR / filename).is_file()
        row = by_image[filename]
        assert row["roi_pos"] == "d1_a0"
        assert row["distance_m"] == pytest.approx(1.0)
        assert row["angle_degrees"] == pytest.approx(0.0)
        if attack == "short":
            assert row["capture_mode"] == "short_exposure"
            assert row["exposure_s"] == pytest.approx(0.00390625)
        else:
            assert row["capture_mode"] == "long_exposure"
            assert row["exposure_s"] == pytest.approx(0.03125)


def test_camera_panels_are_unmodified_jpeg_crops():
    assert montage.GAIN == {"short": 1.0, "long": 1.0, "eye": 1.0}
    fig = montage.build_figure()
    try:
        camera_axes = (1, 2, 4, 5, 7, 8)
        capture_keys = [
            (profile, attack)
            for profile in ("original", "deployed", "vlm")
            for attack in ("short", "long")
        ]
        for axis_index, capture_key in zip(camera_axes, capture_keys):
            path = montage.CAP_DIR / montage.FILES[capture_key]
            raw = np.asarray(Image.open(path).convert("RGB"), dtype=float) / 255.0
            h = raw.shape[0]
            expected = raw[
                int(h * montage.CROP_TOP):int(h * montage.CROP_BOT)
            ]
            actual = np.asarray(fig.axes[axis_index].images[0].get_array())
            np.testing.assert_array_equal(actual, expected)
    finally:
        fs.plt.close(fig)


def test_digital_reconstructions_use_capture_playback_canvas_and_profiles():
    capture = Image.open(
        montage.CAP_DIR / montage.FILES[("original", "short")]
    )
    width, height = capture.size
    crop = slice(
        int(height * montage.CROP_TOP),
        int(height * montage.CROP_BOT),
    )

    raw_source = np.asarray(Image.open(montage.SRC_IMG).convert("RGB"))
    expected_source = fit_image_to_canvas(
        raw_source,
        width,
        height,
        background=(0, 0, 0),
    )[crop].astype(np.float32) / 255.0

    reconstructions = {
        key: montage.integrated_reconstruction(key)
        for key in ("original", "deployed", "vlm")
    }
    assert all(panel.shape == expected_source.shape for panel in reconstructions.values())
    np.testing.assert_array_equal(reconstructions["original"], expected_source)
    for left, right in combinations(reconstructions.values(), 2):
        assert float(np.mean(np.abs(left - right))) > 1 / 255


def test_montage_caption_discloses_capture_and_image_processing_contract():
    text = (PAPER_DIR / "main.tex").read_text(encoding="utf-8")
    figure = text.split(
        r"\includegraphics[width=\columnwidth]{figures/real_capture_montage.pdf}",
        1,
    )[1].split(r"\label{fig:montage}", 1)[0]
    lower = figure.lower()

    for token in (
        "unprotected",
        "readability-priority",
        "high-suppression",
        "digital integrated reconstruction",
        "short-exposure capture",
        "long-exposure capture",
        r"1.0\,m",
        r"$0^{\circ}$",
        r"3.91\,ms",
        r"31.25\,ms",
        "raw camera jpeg",
        "no geometric correction or brightness gain",
    ):
        assert token in lower
    assert "human eye" not in lower
    assert "representative" not in lower
    assert "exactly as" not in montage.__doc__.lower()


def test_manuscript_minor_integrity_fixes_are_present():
    text = (PAPER_DIR / "main.tex").read_text(encoding="utf-8")

    assert "may take 2--5\\,ms" not in text
    # The nominal GtG spec was removed in a later revision; if it ever returns,
    # the accompanying measurement disclosure must return with it.
    if "GtG" in text:
        assert "Actual gray-level transitions may differ from the nominal GtG" in text
    assert "In the full 9-geometry sensitivity pool, long-exposure recovery" in text
    # These labels may exist only when actually referenced.
    for label in ("sec:introduction", "sec:detection", "sec:simulation"):
        if rf"\label{{{label}}}" in text:
            assert rf"\ref{{{label}}}" in text
