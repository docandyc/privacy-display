"""Regression tests for the gaps fixed after the initial detection-suite drop:

1. Tracking IDF1 must be true identity-F1 (penalizing ID switches), not the
   detection F1 that the first implementation reported.
2. Attack variants must be reproducible from a (seed, identifier) pair so the
   reproducibility manifest is meaningful.
"""

import numpy as np

from src.evaluation.detection_suite import build_attack_variants
from src.evaluation.mot import MOTObject, compute_tracking_metrics


def _single_track(sequence: str, track_id: int) -> dict[str, dict[int, list[MOTObject]]]:
    box = (0.0, 0.0, 10.0, 10.0)
    frames = {
        fid: [MOTObject(sequence, fid, track_id if fid <= 2 else track_id + 1, box, 0.9)]
        for fid in (1, 2, 3, 4)
    }
    return {sequence: frames}


def test_tracking_idf1_penalizes_identity_switch_not_just_detection():
    seq = "S"
    box = (0.0, 0.0, 10.0, 10.0)
    gt = {seq: {fid: [MOTObject(seq, fid, 10, box, 1.0)] for fid in (1, 2, 3, 4)}}
    # Perfect detection every frame, but the tracker splits the one identity
    # across two track ids (id 1 for frames 1-2, id 2 for frames 3-4).
    tracks = {
        seq: {
            1: [MOTObject(seq, 1, 1, box, 0.9)],
            2: [MOTObject(seq, 2, 1, box, 0.9)],
            3: [MOTObject(seq, 3, 2, box, 0.9)],
            4: [MOTObject(seq, 4, 2, box, 0.9)],
        }
    }

    metrics = compute_tracking_metrics(gt, tracks)

    # Detection F1 here would be 1.0; identity F1 must drop because the GT
    # identity is recovered under two different track ids.
    assert metrics["idf1"] == 0.5
    assert metrics["mota"] == 0.75  # one ID switch out of four GT boxes
    assert metrics["id_switches"] == 1
    assert metrics["motp"] == 1.0  # boxes overlap perfectly
    assert metrics["hota"] is None
    assert "metric_backend" in metrics


def test_perfect_tracker_scores_one():
    seq = "S"
    box = (0.0, 0.0, 10.0, 10.0)
    gt = {seq: {fid: [MOTObject(seq, fid, 10, box, 1.0)] for fid in (1, 2, 3)}}
    tracks = {seq: {fid: [MOTObject(seq, fid, 7, box, 0.9)] for fid in (1, 2, 3)}}

    metrics = compute_tracking_metrics(gt, tracks)

    assert metrics["idf1"] == 1.0
    assert metrics["mota"] == 1.0
    assert metrics["id_switches"] == 0


def test_attack_variants_are_reproducible_per_seed_and_identifier():
    rng = np.random.default_rng(0)
    image = rng.integers(0, 256, size=(24, 32, 3), dtype=np.uint8)
    kwargs = dict(attacks=["single_subframe", "temporal_average"], n=2, epsilon=8 / 255)

    a = build_attack_variants(image, seed=0, identifier="img-1", **kwargs)
    b = build_attack_variants(image, seed=0, identifier="img-1", **kwargs)
    c = build_attack_variants(image, seed=1, identifier="img-1", **kwargs)

    for key in ("single_subframe", "temporal_average"):
        assert np.array_equal(a[key], b[key]), f"{key} not reproducible for same seed"
        assert not np.array_equal(a[key], c[key]), f"{key} did not change with seed"
