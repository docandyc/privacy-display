from __future__ import annotations

import sys
from pathlib import Path


PAPER_FIGURES = Path(__file__).resolve().parents[1] / "experiments" / "paper_figures"
sys.path.insert(0, str(PAPER_FIGURES))

import fig_f9_study_ratings as study_ratings  # noqa: E402


def test_study_ratings_uses_paper_facing_readability_priority_label():
    assert study_ratings.CONDITIONS[-1] == (
        "deployed_full",
        "Readability-\npriority",
    )
