"""Pluggable object detector adapters for COCO/MOT experiments."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

import numpy as np

from src.attack.detection_evaluator import DetectionBox, DetectionEvaluator


COCO_CATEGORIES: tuple[tuple[int, str], ...] = (
    (1, "person"),
    (2, "bicycle"),
    (3, "car"),
    (4, "motorcycle"),
    (5, "airplane"),
    (6, "bus"),
    (7, "train"),
    (8, "truck"),
    (9, "boat"),
    (10, "traffic light"),
    (11, "fire hydrant"),
    (13, "stop sign"),
    (14, "parking meter"),
    (15, "bench"),
    (16, "bird"),
    (17, "cat"),
    (18, "dog"),
    (19, "horse"),
    (20, "sheep"),
    (21, "cow"),
    (22, "elephant"),
    (23, "bear"),
    (24, "zebra"),
    (25, "giraffe"),
    (27, "backpack"),
    (28, "umbrella"),
    (31, "handbag"),
    (32, "tie"),
    (33, "suitcase"),
    (34, "frisbee"),
    (35, "skis"),
    (36, "snowboard"),
    (37, "sports ball"),
    (38, "kite"),
    (39, "baseball bat"),
    (40, "baseball glove"),
    (41, "skateboard"),
    (42, "surfboard"),
    (43, "tennis racket"),
    (44, "bottle"),
    (46, "wine glass"),
    (47, "cup"),
    (48, "fork"),
    (49, "knife"),
    (50, "spoon"),
    (51, "bowl"),
    (52, "banana"),
    (53, "apple"),
    (54, "sandwich"),
    (55, "orange"),
    (56, "broccoli"),
    (57, "carrot"),
    (58, "hot dog"),
    (59, "pizza"),
    (60, "donut"),
    (61, "cake"),
    (62, "chair"),
    (63, "couch"),
    (64, "potted plant"),
    (65, "bed"),
    (67, "dining table"),
    (70, "toilet"),
    (72, "tv"),
    (73, "laptop"),
    (74, "mouse"),
    (75, "remote"),
    (76, "keyboard"),
    (77, "cell phone"),
    (78, "microwave"),
    (79, "oven"),
    (80, "toaster"),
    (81, "sink"),
    (82, "refrigerator"),
    (84, "book"),
    (85, "clock"),
    (86, "vase"),
    (87, "scissors"),
    (88, "teddy bear"),
    (89, "hair drier"),
    (90, "toothbrush"),
)

COCO_ID_TO_NAME = dict(COCO_CATEGORIES)
COCO_NAME_TO_ID = {name: category_id for category_id, name in COCO_CATEGORIES}
COCO_CONTIGUOUS_TO_ID = {
    contiguous_id: category_id
    for contiguous_id, (category_id, _name) in enumerate(COCO_CATEGORIES)
}


class ObjectDetector(ABC):
    """Normalized detector interface used by dataset experiments."""

    name: str

    @abstractmethod
    def detect(self, image: np.ndarray) -> list[DetectionBox]:
        """Return COCO-label detections for an RGB uint8 image."""

    @abstractmethod
    def status(self) -> dict:
        """Return lightweight model/runtime metadata."""


class UltralyticsDetector(ObjectDetector):
    def __init__(
        self,
        weights: str,
        device: str = "cpu",
        conf: float = 0.25,
        imgsz: int = 640,
        model=None,
        model_cls: str = "YOLO",
        name: str | None = None,
    ):
        self.weights = str(weights)
        self.device = device
        self.conf = float(conf)
        self.imgsz = int(imgsz)
        self._model = model
        self.model_cls = model_cls
        self.name = name or self.weights.replace(".pt", "")

    def detect(self, image: np.ndarray) -> list[DetectionBox]:
        model = self._get_model()
        try:
            results = model.predict(
                source=image,
                conf=self.conf,
                imgsz=self.imgsz,
                device=self.device,
                verbose=False,
                save=False,
            )
        except AttributeError:
            results = model(image)
        return _round_boxes(DetectionEvaluator._parse_yolo_results(results))

    def status(self) -> dict:
        return {
            "backend": "ultralytics",
            "weights": self.weights,
            "device": self.device,
            "conf": self.conf,
            "imgsz": self.imgsz,
            "model_cls": self.model_cls,
        }

    def _get_model(self):
        if self._model is not None:
            return self._model
        if self.model_cls == "RTDETR":
            from ultralytics import RTDETR

            self._model = RTDETR(self.weights)
        else:
            from ultralytics import YOLO

            self._model = YOLO(self.weights)
        return self._model


class TorchvisionDetector(ObjectDetector):
    def __init__(
        self,
        arch: str,
        device: str = "cpu",
        score_thresh: float = 0.25,
        model=None,
        name: str | None = None,
    ):
        self.arch = arch
        self.device = device
        self.score_thresh = float(score_thresh)
        self._model = model
        self.name = name or arch

    def detect(self, image: np.ndarray) -> list[DetectionBox]:
        model = self._get_model()
        tensor = self._to_tensor(image)
        outputs = model([tensor])[0]
        boxes = DetectionEvaluator._as_numpy(outputs.get("boxes", []))
        scores = DetectionEvaluator._as_numpy(outputs.get("scores", np.ones(len(boxes))))
        labels = DetectionEvaluator._as_numpy(outputs.get("labels", np.zeros(len(boxes)))).astype(int)

        detections: list[DetectionBox] = []
        for idx, coords in enumerate(boxes):
            score = float(scores[idx]) if idx < len(scores) else 1.0
            if score < self.score_thresh:
                continue
            category_id = int(labels[idx]) if idx < len(labels) else 0
            label = COCO_ID_TO_NAME.get(category_id, f"class_{category_id}")
            detections.append(
                DetectionBox(
                    tuple(float(x) for x in coords[:4]),
                    float(round(score, 6)),
                    label,
                )
            )
        return detections

    def status(self) -> dict:
        return {
            "backend": "torchvision",
            "arch": self.arch,
            "device": self.device,
            "score_thresh": self.score_thresh,
        }

    def _get_model(self):
        if self._model is not None:
            return self._model.to(self.device).eval()
        import torchvision.models.detection as detection

        if self.arch == "faster_rcnn":
            weights = detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
            self._model = detection.fasterrcnn_resnet50_fpn(weights=weights)
        elif self.arch == "retinanet":
            weights = detection.RetinaNet_ResNet50_FPN_Weights.DEFAULT
            self._model = detection.retinanet_resnet50_fpn(weights=weights)
        else:
            raise ValueError(f"Unsupported torchvision detector: {self.arch}")
        return self._model.to(self.device).eval()

    def _to_tensor(self, image: np.ndarray):
        import torch

        image_f = image.astype(np.float32) / 255.0
        tensor = torch.from_numpy(image_f.transpose(2, 0, 1)).float()
        return tensor.to(self.device)


def build_detector(
    spec: str,
    device: str = "cpu",
    conf: float = 0.25,
    imgsz: int = 640,
    model_factory: Callable[[str], object] | None = None,
) -> ObjectDetector:
    """Build a detector from the short experiment spec name."""
    normalized = spec.lower().replace("_", "-")
    if normalized in {"yolo26x", "yolo26-x"}:
        weights = "yolo26x.pt"
        model = model_factory(weights) if model_factory else None
        return UltralyticsDetector(
            weights,
            device=device,
            conf=conf,
            imgsz=imgsz,
            model=model,
            model_cls="YOLO",
            name="yolo26x",
        )
    if normalized in {"rtdetr-x", "rtdetrx"}:
        weights = "rtdetr-x.pt"
        model = model_factory(weights) if model_factory else None
        return UltralyticsDetector(
            weights,
            device=device,
            conf=conf,
            imgsz=imgsz,
            model=model,
            model_cls="RTDETR",
            name="rtdetr-x",
        )
    if normalized in {"faster-rcnn", "faster-rcnn-resnet50-fpn", "faster-rcnn", "faster_rcnn"}:
        model = model_factory("faster_rcnn") if model_factory else None
        return TorchvisionDetector("faster_rcnn", device=device, score_thresh=conf, model=model, name="faster_rcnn")
    if normalized == "retinanet":
        model = model_factory("retinanet") if model_factory else None
        return TorchvisionDetector("retinanet", device=device, score_thresh=conf, model=model, name="retinanet")
    raise ValueError(f"Unsupported detector spec: {spec}")


def category_id_for_label(label: str) -> int | None:
    return COCO_NAME_TO_ID.get(label)


def detector_noise_target(model_name: str) -> str:
    normalized = model_name.lower().replace("_", "-")
    if normalized.startswith("yolo26"):
        return "yolo26"
    if normalized.startswith("rtdetr"):
        return "rtdetr"
    if normalized.startswith("faster"):
        return "faster_rcnn"
    if normalized.startswith("retinanet"):
        return "retinanet"
    return "yolov8"


def _round_boxes(boxes: list[DetectionBox]) -> list[DetectionBox]:
    return [
        DetectionBox(
            tuple(float(round(value, 6)) for value in box.box),
            float(round(box.score, 6)),
            box.label,
        )
        for box in boxes
    ]
