"""
检测模型攻击评测（交底书 3.3/6.2）

默认目标检测使用 Ultralytics YOLO：
  - 原始帧 YOLO 检测结果作为 pseudo-reference
  - 子帧/攻击帧 YOLO 检测结果与 reference 计算 P/R/F1/mAP50

轻量/单测路径避免下载外部权重：
  - 文本检测优先使用 EasyOCR CRAFT，失败时用 OpenCV 连通域 fallback
  - 单测可注入 fake yolo_model
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class DetectionBox:
    box: tuple[float, float, float, float]  # x1, y1, x2, y2
    score: float = 1.0
    label: str = "text"


def box_iou(a: DetectionBox, b: DetectionBox) -> float:
    ax1, ay1, ax2, ay2 = a.box
    bx1, by1, bx2, by2 = b.box
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter
    return float(inter / denom) if denom > 0 else 0.0


def precision_recall_f1(
    references: list[DetectionBox],
    predictions: list[DetectionBox],
    iou_threshold: float = 0.5,
) -> dict:
    matched: set[int] = set()
    tp = 0
    for pred in sorted(predictions, key=lambda b: b.score, reverse=True):
        best_idx = -1
        best_iou = 0.0
        for idx, ref in enumerate(references):
            if idx in matched or pred.label != ref.label:
                continue
            iou = box_iou(pred, ref)
            if iou > best_iou:
                best_iou = iou
                best_idx = idx
        if best_idx >= 0 and best_iou >= iou_threshold:
            matched.add(best_idx)
            tp += 1

    fp = max(0, len(predictions) - tp)
    fn = max(0, len(references) - tp)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def average_precision_at_iou(
    references: list[DetectionBox],
    predictions: list[DetectionBox],
    iou_threshold: float = 0.5,
) -> float:
    """Compute single-class AP at one IoU threshold over labeled boxes."""
    if not references:
        return 0.0
    # Pre-group refs by label so each pred only scans its own image's refs
    # instead of all refs — reduces from O(N_preds × N_refs_total) to
    # O(N_preds × N_refs_per_image), critical for multi-image datasets.
    refs_by_label: dict[str, list[tuple[int, "DetectionBox"]]] = {}
    for idx, ref in enumerate(references):
        refs_by_label.setdefault(ref.label, []).append((idx, ref))
    matched: set[int] = set()
    tps = []
    fps = []
    for pred in sorted(predictions, key=lambda b: b.score, reverse=True):
        best_idx = -1
        best_iou = 0.0
        for idx, ref in refs_by_label.get(pred.label, []):
            if idx in matched:
                continue
            iou = box_iou(pred, ref)
            if iou > best_iou:
                best_iou = iou
                best_idx = idx
        if best_idx >= 0 and best_iou >= iou_threshold:
            matched.add(best_idx)
            tps.append(1.0)
            fps.append(0.0)
        else:
            tps.append(0.0)
            fps.append(1.0)
    if not tps:
        return 0.0
    tp_cum = np.cumsum(tps)
    fp_cum = np.cumsum(fps)
    recalls = tp_cum / max(len(references), 1)
    precisions = tp_cum / np.maximum(tp_cum + fp_cum, 1e-12)
    # VOC-style envelope integration.
    mrec = np.concatenate([[0.0], recalls, [1.0]])
    mpre = np.concatenate([[0.0], precisions, [0.0]])
    for i in range(len(mpre) - 1, 0, -1):
        mpre[i - 1] = max(mpre[i - 1], mpre[i])
    changed = np.where(mrec[1:] != mrec[:-1])[0]
    return float(np.sum((mrec[changed + 1] - mrec[changed]) * mpre[changed + 1]))


class DetectionEvaluator:
    def __init__(
        self,
        use_easyocr: bool = False,
        yolo_model_path: str | Path = "yolov8n.pt",
        yolo_model=None,
        yolo_conf: float = 0.25,
        yolo_imgsz: int = 640,
    ):
        self.use_easyocr = use_easyocr
        self._easyocr_reader = None
        self.yolo_model_path = str(yolo_model_path)
        self._yolo_model = yolo_model
        self.yolo_conf = float(yolo_conf)
        self.yolo_imgsz = int(yolo_imgsz)

    def detect_text_boxes(self, image: np.ndarray) -> list[DetectionBox]:
        if self.use_easyocr:
            boxes = self._detect_easyocr_text(image)
            if boxes:
                return boxes
        return self._detect_text_fallback(image)

    def _detect_easyocr_text(self, image: np.ndarray) -> list[DetectionBox]:
        try:
            import easyocr
            if self._easyocr_reader is None:
                self._easyocr_reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
            results = self._easyocr_reader.readtext(image, detail=1)
        except Exception:
            return []
        boxes = []
        for pts, _text, score in results:
            arr = np.array(pts, dtype=np.float32)
            x1, y1 = arr.min(axis=0)
            x2, y2 = arr.max(axis=0)
            boxes.append(DetectionBox((x1, y1, x2, y2), float(score), "text"))
        return boxes

    @staticmethod
    def _detect_text_fallback(image: np.ndarray) -> list[DetectionBox]:
        try:
            import cv2
        except ImportError:
            return []
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # Text in this project is usually dark on a light document background.
        _, mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        h, w = gray.shape
        for contour in contours:
            x, y, bw, bh = cv2.boundingRect(contour)
            area = bw * bh
            if area < max(12, h * w * 0.0002):
                continue
            boxes.append(DetectionBox((x, y, x + bw, y + bh), 1.0, "text"))
        return boxes

    @staticmethod
    def detect_synthetic_objects(image: np.ndarray) -> list[DetectionBox]:
        """检测实验脚本生成的彩色矩形/圆形目标，无需外部模型。"""
        try:
            import cv2
        except ImportError:
            return []
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]
        mask = ((saturation > 60) & (value > 50)).astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h >= 100:
                boxes.append(DetectionBox((x, y, x + w, y + h), 1.0, "object"))
        return boxes

    def detect_yolo_objects(self, image: np.ndarray) -> list[DetectionBox]:
        """Run Ultralytics YOLO object detection and return normalized boxes."""
        model = self._get_yolo_model()
        try:
            results = model.predict(
                source=image,
                conf=self.yolo_conf,
                imgsz=self.yolo_imgsz,
                verbose=False,
                save=False,
            )
        except AttributeError:
            results = model(image)
        return self._parse_yolo_results(results)

    def _get_yolo_model(self):
        if self._yolo_model is None:
            from ultralytics import YOLO
            self._yolo_model = YOLO(self.yolo_model_path)
        return self._yolo_model

    @staticmethod
    def _as_numpy(value) -> np.ndarray:
        if hasattr(value, "detach"):
            value = value.detach()
        if hasattr(value, "cpu"):
            value = value.cpu()
        if hasattr(value, "numpy"):
            return value.numpy()
        return np.asarray(value)

    @classmethod
    def _parse_yolo_results(cls, results) -> list[DetectionBox]:
        boxes_out: list[DetectionBox] = []
        if results is None:
            return boxes_out
        for result in list(results):
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            xyxy = cls._as_numpy(getattr(boxes, "xyxy", []))
            conf = cls._as_numpy(getattr(boxes, "conf", np.ones(len(xyxy))))
            cls_ids = cls._as_numpy(getattr(boxes, "cls", np.zeros(len(xyxy)))).astype(int)
            names = getattr(result, "names", {}) or {}
            for i, coords in enumerate(xyxy):
                label = names.get(int(cls_ids[i]), f"class_{int(cls_ids[i])}") if isinstance(names, dict) else str(int(cls_ids[i]))
                boxes_out.append(
                    DetectionBox(
                        tuple(float(x) for x in coords[:4]),
                        float(conf[i]) if i < len(conf) else 1.0,
                        label,
                    )
                )
        return boxes_out

    def evaluate_text_attack(self, original: np.ndarray, attacked: np.ndarray) -> dict:
        refs = self.detect_text_boxes(original)
        preds = self.detect_text_boxes(attacked)
        metrics = precision_recall_f1(refs, preds)
        metrics.update({
            "reference_boxes": len(refs),
            "prediction_boxes": len(preds),
        })
        return metrics

    def evaluate_yolo_attack(self, original: np.ndarray, attacked: np.ndarray) -> dict:
        refs = self.detect_yolo_objects(original)
        preds = self.detect_yolo_objects(attacked)
        metrics = precision_recall_f1(refs, preds)
        metrics.update({
            "map50": average_precision_at_iou(refs, preds, 0.5),
            "reference_boxes": len(refs),
            "prediction_boxes": len(preds),
            "model": self.yolo_model_path,
            "status": "ok" if refs else "no_reference_detections",
        })
        return metrics


def cached_fasterrcnn_status() -> dict:
    """
    Report whether torchvision Faster R-CNN can run without network downloads.
    The function intentionally avoids requesting weights from the internet.
    """
    try:
        import torchvision.models.detection as detection
        _ = detection.fasterrcnn_resnet50_fpn
        return {"available": True, "weights_loaded": False, "note": "torchvision import ok; pretrained weights not requested"}
    except Exception as exc:
        return {"available": False, "weights_loaded": False, "note": exc.__class__.__name__}


def yolo_status(model_path: str = "yolov8n.pt") -> dict:
    """Check whether the Ultralytics package imports; does not force inference."""
    try:
        import ultralytics
        from ultralytics import YOLO
        _ = YOLO
        return {
            "available": True,
            "version": getattr(ultralytics, "__version__", "unknown"),
            "model": model_path,
        }
    except Exception as exc:
        return {
            "available": False,
            "version": None,
            "model": model_path,
            "error": exc.__class__.__name__,
        }
