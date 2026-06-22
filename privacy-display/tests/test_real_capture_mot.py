from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import experiments.real_capture_mot as rcm
from experiments.real_capture_mot import evaluate_capture
from src.attack.detection_evaluator import DetectionBox


class FakeDetector:
    name = "fake"

    def detect(self, image):
        # person box matching the GT row (10,10,30,40) -> xyxy (10,10,40,50)
        return [DetectionBox((10, 10, 40, 50), 0.9, "person")]

    def status(self):
        return {"available": True, "fake": True}


def _write_mot_fixture(root: Path, sequence: str, frames: int = 3) -> None:
    seq = root / "train" / sequence
    (seq / "img1").mkdir(parents=True)
    (seq / "gt").mkdir(parents=True)
    for fid in range(1, frames + 1):
        Image.fromarray(np.full((64, 80, 3), fid, dtype=np.uint8)).save(
            seq / "img1" / f"{fid:06d}.jpg"
        )
    # frame,id,x,y,w,h,conf,class(1=person),visibility
    lines = [f"{fid},1,10,10,30,40,1,1,1" for fid in range(1, frames + 1)]
    (seq / "gt" / "gt.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_captures(capture_dir: Path, sequence: str, attacks, frames: int, size=(64, 80)) -> None:
    for attack in attacks:
        d = capture_dir / f"mot_{sequence}" / attack
        d.mkdir(parents=True, exist_ok=True)
        for fid in range(1, frames + 1):
            Image.fromarray(np.full((*size, 3), 120, dtype=np.uint8)).save(d / f"{fid:06d}.png")


def test_evaluate_capture_writes_detection_and_tracking(tmp_path):
    mot_root = tmp_path / "MOT17"
    sequence = "MOT17-09-FRCNN"
    _write_mot_fixture(mot_root, sequence, frames=3)
    capture_dir = tmp_path / "caps"
    attacks = ["real_clean", "real_short", "real_video"]
    _seed_captures(capture_dir, sequence, attacks, frames=3)

    det_report, trk_report = evaluate_capture(
        mot_root=mot_root,
        sequence=sequence,
        output_dir=tmp_path / "results",
        capture_dir=capture_dir,
        models=["fake"],
        attacks=attacks,
        max_frames=3,
        detector_factory=lambda _m, _d: FakeDetector(),
        prefer_external_tracker=False,  # force greedy fallback (no boxmot)
        enable_hota=False,  # skip TrackEval subprocess
    )

    det = det_report["results"]["fake"]["real_clean"]
    assert det["n_frames"] == 3
    assert {"map", "map50", "recall", "precision"} <= set(det)
    assert det["recall"] > 0.9  # detector matches GT person every frame

    trk = trk_report["results"]["fake"]["real_clean"]
    assert {"mota", "motp", "idf1", "n_frames"} <= set(trk)
    assert set(trk_report["results"]["fake"]) == set(attacks)
    assert det_report["config"]["sequence"] == sequence
    assert det_report["config"]["capture_mode"] == "stop_motion_physical_frame_validation"
    assert det_report["capture"]["coverage"]["complete"] is True
    assert det_report["capture"]["coverage"]["n_shared"] == 3
    assert (tmp_path / "results" / "real_capture_mot_detection.json").exists()
    assert (tmp_path / "results" / "real_capture_mot_tracking.json").exists()


def test_evaluate_capture_rejects_missing_mot_attack_frames(tmp_path):
    mot_root = tmp_path / "MOT17"
    sequence = "MOT17-09-FRCNN"
    _write_mot_fixture(mot_root, sequence, frames=3)
    capture_dir = tmp_path / "caps"
    _seed_captures(capture_dir, sequence, ["real_short"], frames=2)

    with pytest.raises(ValueError, match="Incomplete MOT capture coverage"):
        evaluate_capture(
            mot_root=mot_root,
            sequence=sequence,
            output_dir=tmp_path / "results",
            capture_dir=capture_dir,
            models=["fake"],
            attacks=["real_short"],
            max_frames=3,
            detector_factory=lambda _m, _d: FakeDetector(),
            prefer_external_tracker=False,
            enable_hota=False,
        )


def test_real_capture_mot_dry_run_without_dataset(tmp_path, capsys):
    args = rcm.build_arg_parser().parse_args(
        [
            "--dry-run",
            "--mot-root",
            str(tmp_path / "missing"),
            "--sequence",
            "MOT17-09-FRCNN",
            "--max-frames",
            "2",
        ]
    )

    assert rcm.run(args) == 0
    assert "dataset unavailable" in capsys.readouterr().out
