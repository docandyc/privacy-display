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
    open_camera_with_backend,
    try_set_exposure,
    warmup,
)
from src.demo.playback_demo import fit_image_to_canvas  # noqa: E402
from src.evaluation.metrics import compute_ssim  # noqa: E402

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
    image_shape = calibration.get("image_shape")
    if image_shape:
        calib_h, calib_w = int(image_shape[0]), int(image_shape[1])
        frame_h, frame_w = frame.shape[:2]
        if calib_w > 0 and calib_h > 0 and (calib_w, calib_h) != (frame_w, frame_h):
            scale_to_calibration = np.asarray(
                [
                    [calib_w / frame_w, 0.0, 0.0],
                    [0.0, calib_h / frame_h, 0.0],
                    [0.0, 0.0, 1.0],
                ],
                dtype=np.float32,
            )
            matrix = matrix @ scale_to_calibration
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


def select_exposure_from_scan(
    scan: list[dict],
    *,
    masked_threshold: float = 0.25,
    plateau_threshold: float = 0.9,
    min_dynamic_range: float = 0.15,
    min_plateau_ssim: float = 0.4,
) -> tuple[float | None, float | None, str]:
    """Pick (short, long) exposure log2 values from an SSIM-vs-original scan.

    The scan must come from a *mask_only* scene (no anti-OCR / inversion / noise
    defences) so SSIM-to-original purely tracks how much of the cycle the camera
    integrated. Then:

    * ``short`` = the largest (least-negative) exposure whose normalised SSIM is
      still at the floor → still captures only ~one sub-frame (masked).
    * ``long``  = the smallest (most-negative) exposure that already reaches the
      SSIM plateau → shortest shutter that integrates a full cycle.

    Guards against a curve with no real contrast (camera never integrates, wrong
    scene, or an exposure range that is too short): if the SSIM span is tiny or
    the peak SSIM never indicates reconstruction, returns the scan extremes with
    a ``low_contrast`` tag instead of inventing a spurious plateau.
    """
    pts = sorted(
        (float(s["value"]), float(s["ssim"]))
        for s in scan
        if s.get("ssim") is not None
    )
    if len(pts) < 2:
        return None, None, "insufficient_ssim"
    values = [v for v, _ in pts]
    ssims = [x for _, x in pts]
    lo, hi = min(ssims), max(ssims)
    if (hi - lo) < min_dynamic_range or hi < min_plateau_ssim:
        return min(values), max(values), "ssim_low_contrast_fallback"
    rng = hi - lo
    norm = [(x - lo) / rng for x in ssims]
    masked = [v for v, nn in zip(values, norm) if nn <= masked_threshold]
    integrated = [v for v, nn in zip(values, norm) if nn >= plateau_threshold]
    short_value = max(masked) if masked else min(values)
    long_value = min(integrated) if integrated else max(values)
    method = "ssim_floor_plateau"
    if not masked or not integrated:
        method = "ssim_partial_fallback"
    return short_value, long_value, method


def build_exposure_calibration(
    *,
    short_value: float,
    long_value: float,
    backend: str | None,
    scan_results: list[dict] | None = None,
    selection_method: str = "manual",
) -> dict:
    return {
        "schema_version": 1,
        "backend": backend,
        "selection_method": selection_method,
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


def _load_ssim_reference(image_path: str, width: int, height: int) -> np.ndarray:
    """Load the displayed content and letterbox it to the rectified ROI size."""
    from PIL import Image

    content = np.asarray(Image.open(image_path).convert("RGB"), dtype=np.uint8)
    return fit_image_to_canvas(content, width, height, background=(0, 0, 0))


def save_exposure_calibration(payload: dict, calibration_dir: str | Path) -> Path:
    path = exposure_path(calibration_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def _select_roi(args: argparse.Namespace) -> int:
    cap, _ = open_camera_with_backend(
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
    # SSIM-vs-original needs the captured frame rectified to the screen rect.
    reference = None
    roi_calib = None
    if args.image:
        roi_file = roi_path(args.calibration_dir, args.pos)
        if not roi_file.exists():
            print(f"[calibrate] --image given but no ROI for pos={args.pos} "
                  f"({roi_file}); run --select-roi first. Falling back to manual values.",
                  file=sys.stderr)
        else:
            roi_calib = load_roi_calibration(roi_file)
            reference = _load_ssim_reference(
                args.image, int(roi_calib["output_width"]), int(roi_calib["output_height"]))

    cap, backend_used = open_camera_with_backend(
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
                backend_name=backend_used,
            )
            warmup(cap, args.warmup)
            ok, frame = cap.read()
            ssim = None
            if ok and frame is not None and reference is not None and roi_calib is not None:
                rect = rectify_frame(frame, roi_calib)
                ssim = compute_ssim(rect, reference)
            scan_results.append({
                "value": value,
                "exposure_s": exposure_log2_to_seconds(value),
                "honored": result["honored"],
                "settings": camera_settings(cap),
                "frame_mean": float(frame.mean()) if ok and frame is not None else None,
                "ssim": ssim,
            })
            print(
                f"value={value:g} exposure_s={exposure_log2_to_seconds(value)} "
                f"honored={result['honored']} ssim={ssim}"
            )
    finally:
        cap.release()

    # Auto-pick from the SSIM curve only when the scene is defence-free
    # (mask_only); otherwise SSIM never plateaus and manual values are safer.
    short_value, long_value = args.short_value, args.long_value
    method = "manual"
    if reference is not None and args.scene == "mask_only":
        sel_short, sel_long, method = select_exposure_from_scan(scan_results)
        if sel_short is not None and sel_long is not None:
            short_value, long_value = sel_short, sel_long
            print(f"[calibrate] auto-selected short={short_value:g} long={long_value:g} "
                  f"({method})")
        else:
            method = "manual_fallback"
            print("[calibrate] SSIM scan insufficient; using manual --short/--long values.",
                  file=sys.stderr)
    elif reference is not None:
        print(f"[calibrate] scene={args.scene} is not 'mask_only'; SSIM recorded but "
              "short/long left at manual values.", file=sys.stderr)

    payload = build_exposure_calibration(
        short_value=short_value,
        long_value=long_value,
        backend=backend_used,
        scan_results=scan_results,
        selection_method=method,
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
    p.add_argument("--backend", default="dshow",
                   choices=("dshow", "msmf", "avfoundation", "v4l2", "any"))
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
    p.add_argument("--image", default=None,
                   help="Displayed content image; enables SSIM-vs-original "
                        "exposure auto-selection (needs --select-roi done first)")
    p.add_argument("--scene", default="mask_only",
                   choices=("mask_only", "deployed", "original"),
                   help="What playback shows during the scan; auto-select only "
                        "runs for mask_only (defence-free)")
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
