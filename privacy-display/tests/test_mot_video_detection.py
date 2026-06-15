import numpy as np
from PIL import Image

from experiments.mot_video_detection import run_mot_video_detection
from src.attack.detection_evaluator import DetectionBox


class FakeDetector:
    name = "fake_detector"

    def detect(self, image):
        return [DetectionBox((10, 12, 40, 52), 0.9, "person")]

    def status(self):
        return {"available": True, "fake": True}


def _write_mot_fixture(root):
    seq = root / "train" / "MOT17-02"
    (seq / "img1").mkdir(parents=True)
    (seq / "gt").mkdir()
    for frame in (1, 2, 3):
        Image.fromarray(np.full((80, 100, 3), frame, dtype=np.uint8)).save(
            seq / "img1" / f"{frame:06d}.jpg"
        )
    (seq / "gt" / "gt.txt").write_text(
        "\n".join(
            [
                "1,1,10,12,30,40,1,1,1",
                "2,1,10,12,30,40,1,1,1",
                "3,1,10,12,30,40,1,1,1",
            ]
        ),
        encoding="utf-8",
    )


def test_mot_video_detection_writes_person_detection_schema(tmp_path):
    mot_root = tmp_path / "MOT17"
    _write_mot_fixture(mot_root)

    report = run_mot_video_detection(
        mot_root=mot_root,
        output_dir=tmp_path / "results",
        models=["fake"],
        detector_factory=lambda _model, _device: FakeDetector(),
        sequences=["MOT17-02"],
        max_frames=3,
        attacks=["clean", "temporal_average"],
        device="cpu",
        n=2,
        epsilon=0.0,
    )

    metrics = report["results"]["fake"]["clean"]
    assert metrics["n_frames"] == 3
    assert {"map", "map50", "recall", "precision"} <= set(metrics)
    assert (tmp_path / "results" / "mot_video_detection.json").exists()
