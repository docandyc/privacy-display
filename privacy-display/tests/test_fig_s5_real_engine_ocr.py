from __future__ import annotations

import sys
from pathlib import Path


PAPER_FIGURES = Path(__file__).resolve().parents[1] / "experiments" / "paper_figures"
sys.path.insert(0, str(PAPER_FIGURES))

import fig_s5_real_engine_ocr as real_engine_ocr  # noqa: E402
import figstyle as fs  # noqa: E402


def test_real_engine_ocr_covers_every_table_profile_in_order():
    assert real_engine_ocr.PROFILES == [
        ("original", "Original"),
        ("mask_only", "Mask only"),
        ("mask_noise", "Mask + noise"),
        ("strong", "Strong"),
        ("deployed", "Deployed"),
        ("capture_hardened", "Capture-\nhardened"),
    ]

    data = fs.load("real_capture_per_engine.json")
    expected_keys = {
        f"{profile}|short|{engine}"
        for profile, _ in real_engine_ocr.PROFILES
        for engine, _ in real_engine_ocr.ENGINES
    }
    assert expected_keys <= data.keys()
