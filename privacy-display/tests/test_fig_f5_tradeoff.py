from __future__ import annotations

import sys
from pathlib import Path


PAPER_FIGURES = Path(__file__).resolve().parents[1] / "experiments" / "paper_figures"
sys.path.insert(0, str(PAPER_FIGURES))

import fig_f5_tradeoff as tradeoff  # noqa: E402


def test_tradeoff_resolves_canonical_and_legacy_high_suppression_keys():
    resolver = getattr(tradeoff, "resolve_profile_keys", None)
    assert resolver is not None

    common = {
        "block1/off": {},
        "block1/strong@overlay": {},
        "block1/strong@deployed": {},
    }
    assert resolver({**common, "block1/capture_hardened": {}})[-1] == (
        "block1/capture_hardened"
    )
    assert resolver({**common, "block1/vlm": {}})[-1] == "block1/vlm"


def test_tradeoff_uses_paper_facing_profile_names():
    labels = [label for _, label in tradeoff.PROFILES]
    normalized = [label.replace("-\n", "-").replace("\n", " ") for label in labels]

    assert any("Readability-priority" in label for label in normalized)
    assert all("Deployed" not in label for label in labels)
