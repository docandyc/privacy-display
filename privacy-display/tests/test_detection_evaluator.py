import numpy as np

from src.attack.detection_evaluator import (
    DetectionBox,
    DetectionEvaluator,
    average_precision_at_iou,
    box_iou,
    yolo_status,
)


class FakeBoxes:
    def __init__(self):
        self.xyxy = np.array([[10, 10, 40, 40], [50, 20, 90, 70]], dtype=np.float32)
        self.conf = np.array([0.9, 0.8], dtype=np.float32)
        self.cls = np.array([0, 2], dtype=np.float32)


class FakeResult:
    boxes = FakeBoxes()
    names = {0: "person", 2: "car"}


class FakeYOLO:
    def __init__(self, outputs):
        self.outputs = outputs

    def predict(self, **kwargs):
        assert kwargs["verbose"] is False
        return self.outputs


def test_box_iou():
    a = DetectionBox((0, 0, 10, 10), label="object")
    b = DetectionBox((5, 5, 15, 15), label="object")
    assert 0.14 < box_iou(a, b) < 0.15


def test_parse_yolo_results_from_fake_model():
    ev = DetectionEvaluator(yolo_model=FakeYOLO([FakeResult()]))
    boxes = ev.detect_yolo_objects(np.zeros((100, 100, 3), dtype=np.uint8))

    assert len(boxes) == 2
    assert boxes[0].label == "person"
    assert boxes[1].label == "car"
    assert boxes[0].score > boxes[1].score


def test_yolo_attack_metrics_use_model_predictions():
    original = np.zeros((100, 100, 3), dtype=np.uint8)
    attacked = np.zeros_like(original)
    ev = DetectionEvaluator(yolo_model=FakeYOLO([FakeResult()]))

    metrics = ev.evaluate_yolo_attack(original, attacked)

    assert metrics["reference_boxes"] == 2
    assert metrics["prediction_boxes"] == 2
    assert metrics["f1"] == 1.0
    assert metrics["map50"] == 1.0
    assert metrics["status"] == "ok"


def test_average_precision_partial_match():
    refs = [
        DetectionBox((0, 0, 10, 10), label="person"),
        DetectionBox((20, 20, 40, 40), label="car"),
    ]
    preds = [
        DetectionBox((0, 0, 10, 10), 0.9, "person"),
        DetectionBox((60, 60, 80, 80), 0.8, "car"),
    ]

    assert average_precision_at_iou(refs, preds) == 0.5


def test_ultralytics_status_available():
    status = yolo_status("yolov8n.pt")
    assert status["available"] is True
    assert status["model"] == "yolov8n.pt"
