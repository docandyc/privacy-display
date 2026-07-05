from __future__ import annotations

import sys
from pathlib import Path

import pytest


PAPER_FIGURES = Path(__file__).resolve().parents[1] / "experiments" / "paper_figures"
sys.path.insert(0, str(PAPER_FIGURES))

import fig_f3_montage as montage  # noqa: E402
import figstyle as fs  # noqa: E402


def test_montage_uses_native_single_column_vertical_sequence():
    fig = montage.build_figure()
    try:
        assert fig.get_figwidth() == pytest.approx(fs.COL_W)
        assert len(fig.axes) == 9
        assert [ax.get_title(loc="left") for ax in fig.axes] == [
            "Unprotected - Human eye (integrated)",
            "Unprotected - Short exposure (single frame)",
            "Unprotected - Long exposure",
            "Deployed - Human eye (integrated)",
            "Deployed - Short exposure (single frame)",
            "Deployed - Long exposure",
            "Capture-hardened - Human eye (integrated)",
            "Capture-hardened - Short exposure (single frame)",
            "Capture-hardened - Long exposure",
        ]
        assert all(len(ax.images) == 1 for ax in fig.axes)
    finally:
        fs.plt.close(fig)
