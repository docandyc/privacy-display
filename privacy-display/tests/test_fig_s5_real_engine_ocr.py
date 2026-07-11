from __future__ import annotations

import sys
from pathlib import Path

import pytest


PAPER_FIGURES = Path(__file__).resolve().parents[1] / "experiments" / "paper_figures"
sys.path.insert(0, str(PAPER_FIGURES))

import fig_s5_real_engine_ocr as real_engine_ocr  # noqa: E402
import figstyle as fs  # noqa: E402


def test_real_engine_ocr_uses_primary_matched_profiles_in_order():
    assert real_engine_ocr.PROFILES == [
        ("original", "Original"),
        ("deployed", "Readability-priority"),
        ("high_suppression", "High-suppression"),
    ]


def test_real_engine_ocr_loads_matched_raw_and_fixed_grid_values():
    values = real_engine_ocr.load_preprocessing_recovery()

    assert values["tesseract"]["original"] == {
        "raw": pytest.approx(84.886125),
        "grid_oracle": pytest.approx(91.788629),
    }
    assert values["easyocr"]["deployed"] == {
        "raw": pytest.approx(14.175892),
        "grid_oracle": pytest.approx(33.897470),
    }
    assert values["surya"]["high_suppression"] == {
        "raw": pytest.approx(2.012754),
        "grid_oracle": pytest.approx(6.030114),
    }


def test_real_engine_ocr_is_regenerated_by_make_all():
    import make_all

    assert "fig_s5_real_engine_ocr" in make_all.MODULES
