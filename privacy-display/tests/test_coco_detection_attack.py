import json
from pathlib import Path

import numpy as np
from PIL import Image

from experiments.coco_detection_attack import run_coco_detection_attack
from src.attack.detection_evaluator import DetectionBox


class FakeDetector:
    name = "fake_detector"

    def detect(self, image):
        h, w = image.shape[:2]
        return [DetectionBox((10, 10, min(w - 1, 40), min(h - 1, 50)), 0.9, "person")]

    def status(self):
        return {"available": True, "fake": True}


def _write_coco_fixture(root: Path) -> None:
    (root / "val2017").mkdir(parents=True)
    (root / "annotations").mkdir(parents=True)
    for image_id in (1, 2):
        Image.fromarray(np.full((64, 80, 3), image_id, dtype=np.uint8)).save(
            root / "val2017" / f"{image_id:012d}.jpg"
        )
    payload = {
        "images": [
            {"id": 1, "file_name": "000000000001.jpg", "width": 80, "height": 64},
            {"id": 2, "file_name": "000000000002.jpg", "width": 80, "height": 64},
        ],
        "annotations": [
            {"id": 1, "image_id": 1, "category_id": 1, "bbox": [10, 10, 30, 40], "area": 1200, "iscrowd": 0},
            {"id": 2, "image_id": 2, "category_id": 1, "bbox": [10, 10, 30, 40], "area": 1200, "iscrowd": 0},
        ],
        "categories": [{"id": 1, "name": "person"}],
    }
    (root / "annotations" / "instances_val2017.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )


def test_coco_detection_attack_writes_model_attack_metric_schema(tmp_path):
    coco_root = tmp_path / "coco"
    _write_coco_fixture(coco_root)

    report = run_coco_detection_attack(
        coco_root=coco_root,
        output_dir=tmp_path / "results",
        models=["fake"],
        detector_factory=lambda _model, _device: FakeDetector(),
        max_images=2,
        attacks=["clean", "single_subframe", "temporal_average"],
        device="cpu",
        n=2,
        epsilon=0.0,
    )

    clean = report["results"]["fake"]["clean"]
    assert clean["n_images"] == 2
    assert {"map", "map50", "map75", "ap_small", "ap_medium", "ap_large", "ar"} <= set(clean)
    assert (tmp_path / "results" / "coco_detection_attack.json").exists()
