from __future__ import annotations

import sys
from pathlib import Path


PAPER_FIGURES = Path(__file__).resolve().parents[1] / "experiments" / "paper_figures"
sys.path.insert(0, str(PAPER_FIGURES))

import fig_f4_attack_bar as attack_bar  # noqa: E402


def test_attack_bar_uses_paper_facing_profile_labels():
    assert attack_bar.GRADES == [
        ("original", "Unprotected"),
        ("deployed", "Readability-priority"),
        ("vlm", "High-suppression"),
    ]
