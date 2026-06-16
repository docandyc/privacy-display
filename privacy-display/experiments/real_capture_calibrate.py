"""Calibration helpers for Windows real-camera ablation captures.

The script provides two hardware-facing workflows:

* ``--select-roi``: click the four screen-content corners in a camera frame and
  save a homography under ``experiments/real_captures/calibration``.
* ``--calibrate-exposure``: scan manual exposure values and save the selected
  short/long values in a JSON file consumed by ``real_capture_ablation.py``.

The pure helpers are intentionally small so tests and the ablation orchestrator
can reuse the same JSON shape without opening a camera.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.real_capture_shoot import (  # noqa: E402
    DEFAULT_DEVICE,
    DEFAULT_DEVICE_NAME,
    camera_settings,
    exposure_log2_to_seconds,
    grab_frames,
    open_camera,
    try_set_exposure,
    warmup,
)

DEFAULT_CALIBRATION_DIR = "experiments/real_captures/calibration"


def roi_path(calibration_dir: str | Path, pos: str) -> Path:
    return Path(calibration_dir) / f"roi_{pos}.json"


def exposure_path(calibration_dir: str | Path) -> Path:
    return Path(calibration_dir) / "exposure.json"


def build_roi_calibration(
    points: list[tuple[float, float]],
    *,
    output_width: int,
    output_height: int,
    pos: str,
    image_shape: tuple[int, ...] | None = None,
) -> dict:
    if len(points) != 4:
        raise ValueError("exactly four ROI points are required")
    if output_width <= 0 or output_height <= 0:
        raise ValueError("output size must be positive")

    src = np.asarray(points, dtype=np.float32)
    dst = np.asarray(
        [
            [0, 0],
            [output_width - 1, 0],
            [output_width - 1, output_height - 1],
            [0, output_height - 1],
        ],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(src, dst)
    return {
        "schema_version": 1,
        "pos": pos,
        "points": [[float(x), float(y)] for x, y in points],
        "output_width": int(output_width),
        "output_height": int(output_height),
        "image_shape": list(image_shape) if image_shape is not None else None,
        "homography": matrix.tolist(),
    }


def save_roi_calibration(payload: dict, calibration_dir: str | Path) -> Path:
    path = roi_path(calibration_dir, str(payload["pos"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def load_roi_calibration(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    if "homography" not in payload:
        raise ValueError(f"ROI calibration lacks homography: {path}")
    return payload


def rectify_frame(frame: np.ndarray, calibration: dict) -> np.ndarray:
    matrix = np.asarray(calibration["homography"], dtype=np.float32)
    width = int(calibration["output_width"])
    height = int(calibration["output_height"])
    return cv2.warpPerspective(frame, matrix, (width, height))


def parse_exposure_values(text: str) -> list[float]:
    values: list[float] = []
    for part in str(text).split(","):
        part = part.strip()
        if not part:
            continue
        values.append(float(part))
    if not values:
        raise ValueError("at least one exposure value is required")
    return values


def build_exposure_calibration(
    *,
    short_value: float,
    long_value: float,
    backend: str | None,
    scan_results: list[dict] | None = None,
) -> dict:
    return {
        "schema_version": 1,
        "backend": backend,
        "short": {
            "value": float(short_value),
            "exposure_s": exposure_log2_to_seconds(short_value),
        },
        "long": {
            "value": float(long_value),
            "exposure_s": exposure_log2_to_seconds(long_value),
        },
        "scan_results": scan_results or [],
    }


def save_exposure_calibration(payload: dict, calibration_dir: str | Path) -> Path:
    path = exposure_path(calibration_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def _select_roi(args: argparse.Namespace) -> int:
    cap = open_camera(
        args.device,
        args.width,
        args.height,
        args.fourcc,
        args.fps,
        backend=args.backend,
    )
    try:
        warmup(cap, args.warmup)
        frames = grab_frames(cap, 1, 0)
    finally:
        cap.release()
    if not frames:
        print("no frame captured for ROI selection", file=sys.stderr)
        return 1

    frame = frames[0]
    points: list[tuple[float, float]] = []
    preview = frame.copy()
    window = "select four ROI corners clockwise"

    def on_mouse(event, x, y, flags, userdata):  # noqa: ARG001
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((float(x), float(y)))

    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window, on_mouse)
    while len(points) < 4:
        preview[:] = frame
        for idx, (x, y) in enumerate(points, 1):
            cv2.circle(preview, (int(x), int(y)), 7, (0, 255, 0), -1)
            cv2.putText(
                preview,
                str(idx),
                (int(x) + 8, int(y) + 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
        cv2.imshow(window, preview)
        if cv2.waitKey(20) & 0xFF in (27, ord("q")):
            cv2.destroyWindow(window)
            return 2
    cv2.destroyWindow(window)

    payload = build_roi_calibration(
        points,
        output_width=args.output_width,
        output_height=args.output_height,
        pos=args.pos,
        image_shape=frame.shape,
    )
    out = save_roi_calibration(payload, args.calibration_dir)
    print(f"ROI calibration written: {out}")
    return 0


def _calibrate_exposure(args: argparse.Namespace) -> int:
    cap = open_camera(
        args.device,
        args.width,
        args.height,
        args.fourcc,
        args.fps,
        backend=args.backend,
    )
    scan_results: list[dict] = []
    try:
        for value in parse_exposure_values(args.exposure_values):
            result = try_set_exposure(
                cap,
                manual=True,
                value=value,
                backend_name=args.backend,
            )
            warmup(cap, args.warmup)
            ok, frame = cap.read()
            scan_results.append({
                "value": value,
                "exposure_s": exposure_log2_to_seconds(value),
                "honored": result["honored"],
                "settings": camera_settings(cap),
                "frame_mean": float(frame.mean()) if ok and frame is not None else None,
            })
            print(
                f"value={value:g} exposure_s={exposure_log2_to_seconds(value)} "
                f"honored={result['honored']}"
            )
    finally:
        cap.release()

    payload = build_exposure_calibration(
        short_value=args.short_value,
        long_value=args.long_value,
        backend=args.backend,
        scan_results=scan_results,
    )
    out = save_exposure_calibration(payload, args.calibration_dir)
    print(f"Exposure calibration written: {out}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Calibrate ROI/exposure for real capture ablation")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--select-roi", action="store_true")
    mode.add_argument("--calibrate-exposure", action="store_true")
    p.add_argument("--device", type=int, default=DEFAULT_DEVICE)
    p.add_argument("--device-name", default=DEFAULT_DEVICE_NAME)
    p.add_argument("--backend", default=None)
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--fps", type=float, default=None)
    p.add_argument("--fourcc", default="MJPG")
    p.add_argument("--warmup", type=float, default=0.8)
    p.add_argument("--calibration-dir", default=DEFAULT_CALIBRATION_DIR)
    p.add_argument("--pos", default="d0.5_a0")
    p.add_argument("--output-width", type=int, default=2560)
    p.add_argument("--output-height", type=int, default=1600)
    p.add_argument("--exposure-values", default="-3,-4,-5,-6,-7,-8,-9,-10,-11")
    p.add_argument("--short-value", type=float, default=-8.0)
    p.add_argument("--long-value", type=float, default=-5.0)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.select_roi:
        return _select_roi(args)
    if args.calibrate_exposure:
        return _calibrate_exposure(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
