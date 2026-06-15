import numpy as np

from src.attack.detection_evaluator import DetectionBox
from src.attack.detectors import (
    COCO_ID_TO_NAME,
    COCO_NAME_TO_ID,
    TorchvisionDetector,
    UltralyticsDetector,
    build_detector,
)


class FakeBoxes:
    xyxy = np.array([[10, 10, 40, 40], [50, 20, 90, 70]], dtype=np.float32)
    conf = np.array([0.9, 0.8], dtype=np.float32)
    cls = np.array([0, 2], dtype=np.float32)


class FakeUltralyticsResult:
    boxes = FakeBoxes()
    names = {0: "person", 2: "car"}


class FakeUltralyticsModel:
    def predict(self, **kwargs):
        assert kwargs["source"].shape == (80, 100, 3)
        assert kwargs["device"] == "cpu"
        assert kwargs["verbose"] is False
        return [FakeUltralyticsResult()]


class FakeTorchvisionModel:
    def to(self, device):
        self.device = device
        return self

    def eval(self):
        self.eval_called = True
        return self

    def __call__(self, images):
        assert len(images) == 1
        return [
            {
                "boxes": np.array([[10, 10, 40, 40], [60, 60, 80, 80]], dtype=np.float32),
                "scores": np.array([0.95, 0.1], dtype=np.float32),
                "labels": np.array([1, 3], dtype=np.int64),
            }
        ]


def test_coco_category_mapping_uses_real_category_ids():
    assert COCO_ID_TO_NAME[1] == "person"
    assert COCO_ID_TO_NAME[3] == "car"
    assert COCO_NAME_TO_ID["person"] == 1
    assert COCO_NAME_TO_ID["car"] == 3


def test_ultralytics_detector_normalizes_yolo_like_results():
    detector = UltralyticsDetector(
        weights="yolo26x.pt",
        device="cpu",
        model=FakeUltralyticsModel(),
    )

    boxes = detector.detect(np.zeros((80, 100, 3), dtype=np.uint8))

    assert boxes == [
        DetectionBox((10.0, 10.0, 40.0, 40.0), 0.9, "person"),
        DetectionBox((50.0, 20.0, 90.0, 70.0), 0.8, "car"),
    ]
    assert detector.status()["weights"] == "yolo26x.pt"


def test_torchvision_detector_filters_scores_and_maps_labels():
    detector = TorchvisionDetector(
        arch="faster_rcnn",
        device="cpu",
        score_thresh=0.5,
        model=FakeTorchvisionModel(),
    )

    boxes = detector.detect(np.zeros((80, 100, 3), dtype=np.uint8))

    assert boxes == [DetectionBox((10.0, 10.0, 40.0, 40.0), 0.95, "person")]
    assert detector.status()["arch"] == "faster_rcnn"


def test_build_detector_accepts_all_planned_specs_with_injected_factory():
    fake = FakeUltralyticsModel()
    detector = build_detector("yolo26x", device="cpu", model_factory=lambda _weights: fake)
    assert detector.name == "yolo26x"

    detector = build_detector("rtdetr-x", device="cpu", model_factory=lambda _weights: fake)
    assert detector.name == "rtdetr-x"

    tv = build_detector("retinanet", device="cpu", model_factory=lambda _arch: FakeTorchvisionModel())
    assert tv.name == "retinanet"
