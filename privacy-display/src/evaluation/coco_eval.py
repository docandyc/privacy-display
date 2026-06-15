"""COCO dataset loading and detection metric helpers."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from typing import Iterable

import numpy as np

from src.attack.detection_evaluator import DetectionBox, average_precision_at_iou, box_iou
from src.attack.detectors import category_id_for_label


COCO_METRIC_KEYS = ("map", "map50", "map75", "ap_small", "ap_medium", "ap_large", "ar")


def load_coco_records(
    coco_root: str | Path,
    split: str = "val2017",
    max_images: int | None = None,
) -> tuple[list[dict], list[dict], Path]:
    root = Path(coco_root)
    ann_path = root / "annotations" / f"instances_{split}.json"
    if not ann_path.exists():
        raise FileNotFoundError(f"COCO annotations not found: {ann_path}")
    payload = json.loads(ann_path.read_text(encoding="utf-8"))
    images = list(payload.get("images", []))
    if max_images is not None:
        images = images[: int(max_images)]
        ids = {img["id"] for img in images}
        annotations = [ann for ann in payload.get("annotations", []) if ann.get("image_id") in ids]
    else:
        annotations = list(payload.get("annotations", []))
    return images, annotations, ann_path


def detections_to_coco_results(
    image_id: int,
    detections: Iterable[DetectionBox],
) -> list[dict]:
    rows = []
    for det in detections:
        category_id = category_id_for_label(det.label)
        if category_id is None:
            continue
        x1, y1, x2, y2 = det.box
        rows.append({
            "image_id": int(image_id),
            "category_id": int(category_id),
            "bbox": [
                float(x1),
                float(y1),
                float(max(0.0, x2 - x1)),
                float(max(0.0, y2 - y1)),
            ],
            "score": float(det.score),
        })
    return rows


def evaluate_coco_detections(
    annotation_file: str | Path,
    images: list[dict],
    annotations: list[dict],
    detections: list[dict],
) -> dict:
    """Evaluate detections with pycocotools when available, else a local fallback."""
    if detections:
        try:
            return _evaluate_with_pycocotools(annotation_file, images, detections)
        except Exception:
            pass
    return _simple_coco_eval(images, annotations, detections)


def _evaluate_with_pycocotools(
    annotation_file: str | Path,
    images: list[dict],
    detections: list[dict],
) -> dict:
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval

    with contextlib.redirect_stdout(io.StringIO()):
        coco_gt = COCO(str(annotation_file))
        coco_dt = coco_gt.loadRes(detections)
        evaluator = COCOeval(coco_gt, coco_dt, "bbox")
        evaluator.params.imgIds = [int(img["id"]) for img in images]
        evaluator.evaluate()
        evaluator.accumulate()
        evaluator.summarize()
    stats = evaluator.stats
    return {
        "map": _clean_stat(stats[0]),
        "map50": _clean_stat(stats[1]),
        "map75": _clean_stat(stats[2]),
        "ap_small": _clean_stat(stats[3]),
        "ap_medium": _clean_stat(stats[4]),
        "ap_large": _clean_stat(stats[5]),
        "ar": _clean_stat(stats[8]),
        "n_images": len(images),
        "evaluator": "pycocotools",
    }


def _simple_coco_eval(images: list[dict], annotations: list[dict], detections: list[dict]) -> dict:
    image_ids = {int(img["id"]) for img in images}
    refs = [_ann_to_box(ann) for ann in annotations if int(ann.get("image_id", -1)) in image_ids]
    preds = [_det_to_box(det) for det in detections if int(det.get("image_id", -1)) in image_ids]
    thresholds = np.arange(0.5, 1.0, 0.05)
    aps = [_ap_for_records(refs, preds, float(thr)) for thr in thresholds]
    return {
        "map": float(np.mean(aps)) if aps else 0.0,
        "map50": _ap_for_records(refs, preds, 0.5),
        "map75": _ap_for_records(refs, preds, 0.75),
        "ap_small": _ap_for_records(_filter_area(refs, "small"), preds, 0.5),
        "ap_medium": _ap_for_records(_filter_area(refs, "medium"), preds, 0.5),
        "ap_large": _ap_for_records(_filter_area(refs, "large"), preds, 0.5),
        "ar": _recall_for_records(refs, preds, 0.5),
        "n_images": len(images),
        "evaluator": "simple",
    }


def _ann_to_box(ann: dict) -> dict:
    x, y, w, h = ann.get("bbox", [0, 0, 0, 0])
    category_id = int(ann.get("category_id", 0))
    image_id = int(ann.get("image_id", 0))
    return {
        "image_id": image_id,
        "category_id": category_id,
        "box": DetectionBox((x, y, x + w, y + h), 1.0, f"{category_id}:{image_id}"),
        "area": float(ann.get("area", w * h)),
    }


def _det_to_box(det: dict) -> dict:
    x, y, w, h = det.get("bbox", [0, 0, 0, 0])
    category_id = int(det.get("category_id", 0))
    image_id = int(det.get("image_id", 0))
    return {
        "image_id": image_id,
        "category_id": category_id,
        "box": DetectionBox((x, y, x + w, y + h), float(det.get("score", 1.0)), f"{category_id}:{image_id}"),
        "area": float(w * h),
    }


def _ap_for_records(refs: list[dict], preds: list[dict], threshold: float) -> float:
    ref_boxes = [row["box"] for row in refs]
    pred_boxes = [row["box"] for row in preds]
    return average_precision_at_iou(ref_boxes, pred_boxes, threshold)


def _recall_for_records(refs: list[dict], preds: list[dict], threshold: float) -> float:
    if not refs:
        return 0.0
    matched: set[int] = set()
    for pred in sorted(preds, key=lambda row: row["box"].score, reverse=True):
        best_idx = -1
        best_iou = 0.0
        for idx, ref in enumerate(refs):
            if idx in matched:
                continue
            if pred["image_id"] != ref["image_id"] or pred["category_id"] != ref["category_id"]:
                continue
            iou = box_iou(pred["box"], ref["box"])
            if iou > best_iou:
                best_iou = iou
                best_idx = idx
        if best_idx >= 0 and best_iou >= threshold:
            matched.add(best_idx)
    return float(len(matched) / max(len(refs), 1))


def _filter_area(refs: list[dict], bucket: str) -> list[dict]:
    if bucket == "small":
        return [row for row in refs if row["area"] < 32 * 32]
    if bucket == "medium":
        return [row for row in refs if 32 * 32 <= row["area"] < 96 * 96]
    return [row for row in refs if row["area"] >= 96 * 96]


def _clean_stat(value) -> float:
    value = float(value)
    return value if value >= 0 else 0.0
