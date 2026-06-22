"""COCO real-device camera-capture detection attack (Windows 240Hz).

Mirrors ``experiments/coco_detection_attack.py`` but the attack frames come from
a real USB webcam photographing the privacy display, not the software
``CameraSimulator``. For each COCO subset image we letterbox it onto the display
canvas, show its privacy subframes on the high-refresh screen, and capture three
conditions:

  real_clean   – unprotected original shown; isolates the screen-photo + ROI
                 rectification degradation baseline (so the mAP drop attributed
                 to the privacy algorithm is not confounded with "it's a photo").
  real_short   – short-exposure single still ~ one subframe (single_subframe).
  real_video   – 60fps burst -> offline temporal mean (temporal_average).

Captured frames are ROI-rectified to the display canvas, the content region is
cropped back to the original image resolution, then the 4 detectors run offline
and COCOeval scores them against the unchanged COCO ground truth.

The privacy subframes use a single model-agnostic detector noise (generic PGD
Sobel proxy), so one capture pass per image yields all 4 detectors offline.

Capture and evaluation are split: ``--capture-only`` shoots on Windows,
``--eval-only`` re-scores already-captured frames anywhere (no camera needed).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.real_capture_ablation import (  # noqa: E402
    offline_video_attack_frames,
    wait_for_playback_ready,
)
from experiments.real_capture_calibrate import (  # noqa: E402
    DEFAULT_CALIBRATION_DIR,
    load_roi_calibration,
    rectify_frame,
    roi_path,
)
from experiments.real_capture_shoot import (  # noqa: E402
    DEFAULT_CAPTURE_DIR,
    DEFAULT_DEVICE,
    DEFAULT_DEVICE_NAME,
    camera_settings,
    exposure_log2_to_seconds,
    grab_frames,
    open_camera_with_backend,
    try_set_exposure,
    warmup,
)
from src.attack.detectors import build_detector
from src.evaluation.coco_eval import (  # noqa: E402
    COCO_METRIC_KEYS,
    detections_to_coco_results,
    evaluate_coco_detections,
    load_coco_records,
)
from src.evaluation.detection_suite import (  # noqa: E402
    DEFAULT_MODELS,
    build_display_subframes,
    load_rgb,
    parse_csv_list,
    print_metric_table,
    write_json,
)

RESULT_FILENAME = "real_capture_coco_detection.json"
CAPTURE_SUBDIR = "coco_detection"
REAL_ATTACKS = ("real_clean", "real_short", "real_video")
DEFAULT_DISPLAY_WIDTH = 2560
DEFAULT_DISPLAY_HEIGHT = 1600
DEFAULT_REFRESH_HZ = 240.0
# Model-agnostic generic detector noise: one display+capture per image scores all 4.
NOISE_TARGET = "yolov8"


@dataclass(frozen=True)
class CaptureSpec:
    """One real attack: which display variant + camera settings + how to reduce."""

    label: str          # real_clean / real_short / real_video
    variant: str        # "original" or "protected" (which frames the screen shows)
    width: int          # camera capture width
    height: int         # camera capture height
    fps: float          # camera fps
    burst: int          # frames to grab
    interval: float     # spacing between burst frames (s)
    exposure_key: str   # exposure.json key: "short"/"long"
    reduce: str         # "best" (max-contrast frame) or "temporal_mean"


# real_short uses a high-res still so the rolling-shutter band is thin; real_video
# uses 60fps short-exposure bursts whose offline mean is the temporal_average
# attack; real_clean shows the static original at long exposure (any phase works).
COCO_CAPTURE_SPECS: tuple[CaptureSpec, ...] = (
    CaptureSpec("real_clean", "original", 1920, 1080, 30.0, 3, 0.0, "long", "best"),
    CaptureSpec("real_short", "protected", 3840, 2160, 30.0, 3, 0.0, "short", "best"),
    CaptureSpec("real_video", "protected", 1920, 1080, 60.0, 150, 0.0, "short", "temporal_mean"),
)


# --------------------------------------------------------------------------- #
# Geometry: letterbox + rectified-crop back to original resolution
# --------------------------------------------------------------------------- #
def letterbox_rect(
    src_w: int, src_h: int, width: int, height: int
) -> tuple[int, int, int, int, float]:
    """Placement of an image letterboxed (aspect-preserving, centered) on a canvas.

    Returns ``(x, y, target_w, target_h, scale)`` matching
    :func:`src.demo.playback_demo.fit_image_to_canvas` so the rectified capture's
    content region can be cropped exactly.
    """
    scale = min(width / src_w, height / src_h)
    target_w = max(1, int(round(src_w * scale)))
    target_h = max(1, int(round(src_h * scale)))
    x = (width - target_w) // 2
    y = (height - target_h) // 2
    return x, y, target_w, target_h, scale


def crop_content_to_original(
    rectified_rgb: np.ndarray, src_w: int, src_h: int, width: int, height: int
) -> np.ndarray:
    """Crop the letterbox content region from a canvas-sized capture and resize
    back to the original image resolution (so detections land in GT coords)."""
    from PIL import Image

    x, y, tw, th, _ = letterbox_rect(src_w, src_h, width, height)
    content = rectified_rgb[y : y + th, x : x + tw]
    if content.shape[0] < 1 or content.shape[1] < 1:
        return np.zeros((src_h, src_w, 3), dtype=np.uint8)
    return np.array(
        Image.fromarray(content).resize((src_w, src_h), Image.LANCZOS), dtype=np.uint8
    )


def _bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    return frame[..., ::-1].copy() if frame.ndim == 3 and frame.shape[2] == 3 else frame


def _contrast(frame: np.ndarray) -> float:
    return float(frame.astype(np.float32).mean(axis=2).std()) if frame.ndim == 3 else 0.0


def _shape_of(frame: np.ndarray) -> list[int]:
    return [int(v) for v in getattr(frame, "shape", ())]


def _safe_camera_settings(cap) -> dict:
    try:
        return camera_settings(cap)
    except Exception as exc:  # pragma: no cover - defensive for unusual OpenCV backends
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def _reduce_frames(frames_rgb: list[np.ndarray], reduce: str, window: int) -> np.ndarray:
    if not frames_rgb:
        raise ValueError("no frames to reduce")
    if reduce == "temporal_mean":
        return offline_video_attack_frames(frames_rgb, window=window)["temporal_mean"]
    return max(frames_rgb, key=_contrast)


def assert_roi_matches_canvas(roi: dict, display_width: int, display_height: int) -> None:
    """Fail fast if the ROI rectifies to a canvas different from the display.

    ``crop_content_to_original`` indexes the rectified frame with display-sized
    letterbox coordinates, so if the ROI's ``output_width/height`` differs from
    the display the crop silently misaligns and *every* GT box becomes wrong
    (plausible-looking but meaningless mAP). Recalibrate ROI with
    ``--output-width/--output-height`` equal to the display resolution.
    """
    ow = int(roi.get("output_width", -1))
    oh = int(roi.get("output_height", -1))
    if (ow, oh) != (int(display_width), int(display_height)):
        raise ValueError(
            f"ROI calibration output size {ow}x{oh} != display canvas "
            f"{int(display_width)}x{int(display_height)}; the rectified-crop GT "
            f"alignment would be invalid. Recalibrate with --output-width "
            f"{int(display_width)} --output-height {int(display_height)}."
        )


def exposure_calibration_status(exposure_calib: dict, specs) -> dict:
    """Report which manual exposures the capture needs but the calibration lacks.

    Without a manual short exposure the camera falls back to AUTO (long)
    exposure, so ``real_short`` would integrate several sub-frames and capture
    the *recovered* image — silently invalidating the single-frame attack.
    """
    from experiments.real_capture_ablation import exposure_for_attack

    needed = sorted({spec.exposure_key for spec in specs if spec.exposure_key})
    missing = [key for key in needed if exposure_for_attack(exposure_calib, key)[0] is None]
    return {"calibrated": not missing, "needed_keys": needed, "missing_keys": missing}


def _warn_if_uncalibrated_exposure(status: dict) -> None:
    if status["missing_keys"]:
        print(
            "[warn] no manual exposure calibration for "
            f"{status['missing_keys']}; short/long captures will use the camera's "
            "AUTO exposure and real_short may integrate multiple sub-frames "
            "(invalid single-frame attack). Run real_capture_calibrate.py "
            "--calibrate-exposure first.",
            file=sys.stderr,
        )


# --------------------------------------------------------------------------- #
# Persistent playback: one process, hot-switched per (image, variant) via the
# control file. Reused by the MOT stop-motion capture as well.
# --------------------------------------------------------------------------- #
class PersistentDisplay:
    """Launch one fullscreen playback and hot-swap its frames via control file.

    Avoids relaunching pygame per image/frame (hundreds of launches). Each
    :meth:`show` writes the canvas frames to a fresh dir and bumps the control
    file's mtime; the playback polls it and reloads, then we ``settle`` before
    capturing. Cleans up superseded frame dirs to bound temp usage.
    """

    def __init__(self, args: argparse.Namespace, tmp_root: Path):
        self.args = args
        self.tmp = Path(tmp_root)
        self.ctrl = self.tmp / "control.json"
        self.ack = self.tmp / "playback_ack.json"
        self.epoch = 0
        self.proc: subprocess.Popen | None = None
        self._prev_dir: Path | None = None

    def _write_frames(self, frames_rgb: list[np.ndarray]) -> Path:
        from PIL import Image

        self.epoch += 1
        out = self.tmp / f"frames_{self.epoch:06d}"
        out.mkdir(parents=True, exist_ok=True)
        for i, frame in enumerate(frames_rgb):
            Image.fromarray(frame).save(out / f"{i:03d}.png")
        return out

    def _command(self, frames_dir: Path) -> list[str]:
        return [
            sys.executable, "main.py", "playback",
            "--frames-dir", str(frames_dir),
            "--control-file", str(self.ctrl),
            "--width", str(self.args.display_width),
            "--height", str(self.args.display_height),
            "--n", str(self.args.n),
            "--fullscreen",
            "--no-hud",
        ]

    def _control_payload(self, frames_dir: Path) -> dict:
        return {
            "frames_dir": str(frames_dir),
            "epoch": self.epoch,
            "ack_file": str(self.ack),
        }

    def _write_control(self, frames_dir: Path) -> None:
        self.ctrl.write_text(json.dumps(self._control_payload(frames_dir)), encoding="utf-8")

    def _wait_for_ack(self, epoch: int) -> None:
        timeout = float(getattr(self.args, "advance_timeout", 5.0))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.proc is not None and self.proc.poll() is not None:
                raise RuntimeError(f"playback exited before acknowledging epoch {epoch}")
            try:
                payload = json.loads(self.ack.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                time.sleep(0.01)
                continue
            if int(payload.get("epoch", -1)) == int(epoch):
                return
            time.sleep(0.01)
        raise TimeoutError(f"playback did not acknowledge epoch {epoch} within {timeout:.2f}s")

    def start(self, frames_rgb: list[np.ndarray]) -> None:
        d = self._write_frames(frames_rgb)
        self._write_control(d)
        self.proc = subprocess.Popen(
            self._command(d), cwd=str(ROOT),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        wait_for_playback_ready(self.proc, self.args.playback_timeout)
        time.sleep(self.args.settle)
        self._prev_dir = d

    def show(self, frames_rgb: list[np.ndarray]) -> None:
        d = self._write_frames(frames_rgb)
        self._write_control(d)
        self._wait_for_ack(self.epoch)
        time.sleep(self.args.settle)
        if self._prev_dir and self._prev_dir.exists():
            shutil.rmtree(self._prev_dir, ignore_errors=True)
        self._prev_dir = d

    def stop(self) -> None:
        if self.proc is None:
            return
        self.proc.terminate()
        try:
            self.proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def _capture_one_attack(
    args: argparse.Namespace,
    spec: CaptureSpec,
    roi: dict,
    exposure_calib: dict,
    src_w: int,
    src_h: int,
) -> tuple[np.ndarray, dict]:
    """Open camera with the spec, grab, rectify, reduce, crop to original size."""
    from experiments.real_capture_ablation import exposure_for_attack

    exposure_value, _ = exposure_for_attack(exposure_calib, spec.exposure_key)
    cap, backend_used = open_camera_with_backend(
        args.camera_index, spec.width, spec.height, args.fourcc, spec.fps, backend=args.backend
    )
    exposure_result = None
    try:
        settings_before = _safe_camera_settings(cap)
        if exposure_value is not None:
            exposure_result = try_set_exposure(
                cap, manual=True, value=exposure_value, backend_name=backend_used
            )
        settings_after_exposure = _safe_camera_settings(cap)
        warmup(cap, args.warmup)
        raw = grab_frames(cap, spec.burst, spec.interval)
        settings_after_capture = _safe_camera_settings(cap)
    finally:
        cap.release()
    if not raw:
        raise RuntimeError(f"camera returned no frames for {spec.label}")
    rect_rgb = [_bgr_to_rgb(rectify_frame(frame, roi)) for frame in raw]
    window = args.video_window or args.n
    reduced = _reduce_frames(rect_rgb, spec.reduce, window)
    cropped = crop_content_to_original(
        reduced, src_w, src_h, args.display_width, args.display_height
    )
    x, y, tw, th, scale = letterbox_rect(src_w, src_h, args.display_width, args.display_height)
    metadata = {
        "spec": asdict(spec),
        "backend": backend_used,
        "camera": {
            "device_index": int(args.camera_index),
            "requested_backend": args.backend,
            "requested_fourcc": args.fourcc,
            "settings_before": settings_before,
            "settings_after_exposure": settings_after_exposure,
            "settings_after_capture": settings_after_capture,
        },
        "exposure": {
            "key": spec.exposure_key,
            "requested_value": exposure_value,
            "requested_exposure_s": exposure_log2_to_seconds(exposure_value),
            "set_result": exposure_result,
        },
        "frames": {
            "requested_burst": int(spec.burst),
            "captured": len(raw),
            "raw_shapes": [_shape_of(frame) for frame in raw[:3]],
            "rectified_shapes": [_shape_of(frame) for frame in rect_rgb[:3]],
            "reduced_shape": _shape_of(reduced),
            "cropped_shape": _shape_of(cropped),
            "video_window": int(window),
            "reduce": spec.reduce,
        },
        "crop": {
            "src_w": int(src_w),
            "src_h": int(src_h),
            "display_width": int(args.display_width),
            "display_height": int(args.display_height),
            "x": int(x),
            "y": int(y),
            "target_w": int(tw),
            "target_h": int(th),
            "scale": float(scale),
        },
    }
    return cropped, metadata


def capture_coco(args: argparse.Namespace, images: list[dict], root: Path, split: str) -> dict:
    """Physically capture real_clean/real_short/real_video per subset image.

    Writes cropped, original-resolution RGB PNGs to
    ``<capture-dir>/coco_detection/<attack>/<image_id>.png`` plus a manifest.
    """
    from PIL import Image

    roi = load_roi_calibration(roi_path(args.calibration_dir, args.pos))
    assert_roi_matches_canvas(roi, args.display_width, args.display_height)
    from experiments.real_capture_ablation import load_exposure_calibration

    exposure_calib = load_exposure_calibration(args.calibration_dir)
    exposure_status = exposure_calibration_status(exposure_calib, COCO_CAPTURE_SPECS)
    _warn_if_uncalibrated_exposure(exposure_status)
    capture_root = Path(args.capture_dir) / CAPTURE_SUBDIR
    for spec in COCO_CAPTURE_SPECS:
        (capture_root / spec.label).mkdir(parents=True, exist_ok=True)

    canvas = (args.display_width, args.display_height)
    manifest = {
        "captures": [],
        "config": {
            "capture_mode": "real_device_still_physical_validation",
            "canvas": canvas,
            "display_width": int(args.display_width),
            "display_height": int(args.display_height),
            "refresh_hz": float(getattr(args, "refresh_hz", DEFAULT_REFRESH_HZ)),
            "n": int(args.n),
            "epsilon": float(args.epsilon),
            "seed": int(args.seed),
            "pos": args.pos,
            "calibration_dir": str(args.calibration_dir),
            "roi_output_width": int(roi.get("output_width", -1)),
            "roi_output_height": int(roi.get("output_height", -1)),
            "exposure_calibration": exposure_status,
            "capture_specs": [asdict(spec) for spec in COCO_CAPTURE_SPECS],
        },
    }

    with tempfile.TemporaryDirectory(prefix="rc-coco-") as tmp:
        display = PersistentDisplay(args, Path(tmp))
        first = load_rgb(root / split / images[0]["file_name"])
        display.start([_letterbox(first, *canvas)])
        try:
            for info in images:
                image = load_rgb(root / split / info["file_name"])
                src_h, src_w = image.shape[:2]
                subframes = build_display_subframes(
                    image, n=args.n, epsilon=args.epsilon, target_model=NOISE_TARGET,
                    seed=args.seed, identifier=info["file_name"], device=args.device,
                )
                canvas_subframes = [_letterbox(s, *canvas) for s in subframes]
                canvas_original = [_letterbox(image, *canvas)]
                shown_variant = None  # re-show only when the displayed content changes
                for spec in COCO_CAPTURE_SPECS:
                    if spec.variant != shown_variant:
                        display.show(canvas_subframes if spec.variant == "protected" else canvas_original)
                        shown_variant = spec.variant
                    cropped, capture_meta = _capture_one_attack(
                        args, spec, roi, exposure_calib, src_w, src_h
                    )
                    out = capture_root / spec.label / f"{info['id']}.png"
                    Image.fromarray(cropped).save(out)
                    manifest["captures"].append(
                        {
                            "image_id": info["id"],
                            "file_name": info["file_name"],
                            "attack": spec.label,
                            "variant": spec.variant,
                            "path": str(out),
                            "src_w": src_w,
                            "src_h": src_h,
                            "playback_epoch": display.epoch,
                            **capture_meta,
                        }
                    )
        finally:
            display.stop()
    write_json(capture_root / "capture_manifest.json", manifest)
    print(f"Captured {len(manifest['captures'])} frames -> {capture_root}")
    return manifest


def _letterbox(image: np.ndarray, width: int, height: int) -> np.ndarray:
    from src.demo.playback_demo import fit_image_to_canvas

    return fit_image_to_canvas(image, width, height, background=(0, 0, 0))


def _load_capture_manifest(capture_root: Path) -> dict | None:
    path = capture_root / "capture_manifest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _coverage_payload(
    *,
    expected_ids: list[int],
    by_attack: dict[str, list[int]],
    id_label: str,
) -> dict:
    expected_set = set(expected_ids)
    missing_by_attack = {
        attack: sorted(expected_set - set(ids))
        for attack, ids in by_attack.items()
    }
    shared = sorted(set.intersection(*(set(ids) for ids in by_attack.values()))) if by_attack else []
    complete = all(not missing for missing in missing_by_attack.values())
    same_ids = len({tuple(ids) for ids in by_attack.values()}) <= 1
    return {
        "id_label": id_label,
        "expected": expected_ids,
        "by_attack": by_attack,
        "missing_by_attack": missing_by_attack,
        "shared_ids": shared,
        "n_expected": len(expected_ids),
        "n_shared": len(shared),
        "complete": bool(complete and same_ids),
        "same_ids": bool(same_ids),
    }


def _coco_capture_coverage(
    capture_root: Path,
    attacks: list[str],
    images: list[dict],
    *,
    strict: bool = True,
) -> dict:
    expected = [int(info["id"]) for info in images]
    by_attack = {
        attack: [
            int(info["id"])
            for info in images
            if (capture_root / attack / f"{info['id']}.png").exists()
        ]
        for attack in attacks
    }
    coverage = _coverage_payload(expected_ids=expected, by_attack=by_attack, id_label="image_id")
    if strict and not coverage["complete"]:
        raise ValueError(
            "Incomplete COCO capture coverage: "
            f"missing_by_attack={coverage['missing_by_attack']}"
        )
    if not coverage["shared_ids"]:
        raise ValueError("No shared COCO captures available across requested attacks")
    return coverage


# --------------------------------------------------------------------------- #
# Evaluation (hardware-free): load captured frames, run detectors, COCOeval.
# --------------------------------------------------------------------------- #
def evaluate_capture(
    coco_root: str | Path,
    output_dir: str | Path = "experiments/results",
    capture_dir: str | Path = DEFAULT_CAPTURE_DIR,
    models: list[str] | None = None,
    split: str = "val2017",
    max_images: int | None = None,
    attacks: list[str] | None = None,
    device: str | None = None,
    conf: float = 0.25,
    imgsz: int = 640,
    n: int = 4,
    epsilon: float = 8 / 255,
    seed: int = 0,
    detector_factory=None,
    config_extra: dict | None = None,
    strict_coverage: bool = True,
) -> dict:
    """Score already-captured real frames against COCO GT. No camera needed."""
    root = Path(coco_root)
    selected_models = list(models or DEFAULT_MODELS)
    selected_attacks = list(attacks or REAL_ATTACKS)
    images, annotations, ann_path = load_coco_records(root, split=split, max_images=max_images)
    capture_root = Path(capture_dir) / CAPTURE_SUBDIR
    coverage = _coco_capture_coverage(
        capture_root, selected_attacks, images, strict=strict_coverage
    )
    shared_ids = set(coverage["shared_ids"])
    eval_images = [info for info in images if int(info["id"]) in shared_ids]
    capture_manifest = _load_capture_manifest(capture_root)

    results: dict[str, dict[str, dict]] = {}
    statuses: dict[str, dict] = {}
    for model_name in selected_models:
        detector = (
            detector_factory(model_name, device)
            if detector_factory
            else build_detector(model_name, device=device or "cpu", conf=conf, imgsz=imgsz)
        )
        statuses[model_name] = detector.status()
        results[model_name] = {}
        for attack in selected_attacks:
            rows: list[dict] = []
            for info in eval_images:
                path = capture_root / attack / f"{info['id']}.png"
                image = load_rgb(path)
                rows.extend(detections_to_coco_results(info["id"], detector.detect(image)))
            results[model_name][attack] = evaluate_coco_detections(
                ann_path, eval_images, annotations, rows
            )

    report = {
        "config": {
            "dataset": "COCO",
            "capture": "real_device_webcam",
            "coco_root": str(root),
            "split": split,
            "models": selected_models,
            "attacks": selected_attacks,
            "device": device,
            "n": int(n),
            "epsilon": float(epsilon),
            "conf": float(conf),
            "imgsz": int(imgsz),
            "seed": int(seed),
            "max_images": max_images,
            "noise_target": NOISE_TARGET,
            **(config_extra or {}),
        },
        "detectors": statuses,
        "capture": {
            "mode": "real_device_still_physical_validation",
            "coverage": coverage,
            "manifest_path": str(capture_root / "capture_manifest.json"),
            "manifest": capture_manifest,
        },
        "results": results,
        "baseline_clean_map": {
            model: metrics.get("real_clean", {}).get("map")
            for model, metrics in results.items()
        },
    }
    out = Path(output_dir) / RESULT_FILENAME
    write_json(out, report)
    print_metric_table(
        "COCO Real-Capture Detection Attack", results, [*COCO_METRIC_KEYS, "n_images"]
    )
    print(f"Saved: {out}")
    return report


def _dry_run(args: argparse.Namespace, images: list[dict]) -> int:
    print("[dry-run] COCO real-capture detection plan")
    print(f"  images={len(images)}  attacks={[s.label for s in COCO_CAPTURE_SPECS]}")
    print(f"  display={args.display_width}x{args.display_height}@{args.refresh_hz}Hz  n={args.n}")
    print(f"  camera_index={args.camera_index} backend={args.backend} pos={args.pos}")
    print(f"  captures planned={len(images) * len(COCO_CAPTURE_SPECS)} (1 persistent playback)")
    print(f"  capture_dir={Path(args.capture_dir) / CAPTURE_SUBDIR}")
    print(f"  result={Path(args.output_dir) / RESULT_FILENAME}")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--coco-root", default="data/coco")
    p.add_argument("--output-dir", default="experiments/results")
    p.add_argument("--capture-dir", default=DEFAULT_CAPTURE_DIR)
    p.add_argument("--models", default=",".join(DEFAULT_MODELS))
    p.add_argument("--attacks", default=",".join(REAL_ATTACKS))
    p.add_argument("--split", default="val2017")
    p.add_argument("--max-images", type=int, default=150)
    p.add_argument("--device", default=None, help="cuda:N for detectors/PGD (offline)")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--seed", type=int, default=0)
    # capture-side (Windows)
    p.add_argument("--camera-index", type=int, default=DEFAULT_DEVICE)
    p.add_argument("--device-name", default=DEFAULT_DEVICE_NAME)
    p.add_argument("--backend", default=None, help="dshow/msmf/avfoundation/v4l2/any")
    p.add_argument("--fourcc", default="MJPG")
    p.add_argument("--display-width", type=int, default=DEFAULT_DISPLAY_WIDTH)
    p.add_argument("--display-height", type=int, default=DEFAULT_DISPLAY_HEIGHT)
    p.add_argument("--refresh-hz", type=float, default=DEFAULT_REFRESH_HZ)
    p.add_argument("--warmup", type=float, default=0.8, help="camera AE settle seconds")
    p.add_argument("--settle", type=float, default=0.5, help="seconds after switching display frames")
    p.add_argument("--calibration-dir", default=DEFAULT_CALIBRATION_DIR)
    p.add_argument("--pos", default="d0.5_a0", help="ROI calibration position label")
    p.add_argument("--video-window", type=int, default=0, help="temporal-mean window (0=use --n)")
    p.add_argument("--playback-timeout", type=float, default=30.0)
    p.add_argument("--advance-timeout", type=float, default=5.0,
                   help="seconds to wait for playback hot-swap acknowledgement")
    p.add_argument("--allow-partial-captures", action="store_true",
                   help="evaluate only the shared captured subset instead of failing on missing captures")
    p.add_argument("--capture-only", action="store_true")
    p.add_argument("--eval-only", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p


def run(args: argparse.Namespace) -> int:
    root = Path(args.coco_root)
    try:
        images, _, _ = load_coco_records(root, split=args.split, max_images=args.max_images)
    except FileNotFoundError as exc:
        if args.dry_run:
            print(f"[dry-run] dataset unavailable: {exc}")
            images = []
        else:
            raise
    if args.dry_run:
        return _dry_run(args, images)
    if not args.eval_only:
        capture_coco(args, images, root, args.split)
    if not args.capture_only:
        evaluate_capture(
            coco_root=root, output_dir=args.output_dir, capture_dir=args.capture_dir,
            models=parse_csv_list(args.models, DEFAULT_MODELS), split=args.split,
            max_images=args.max_images, attacks=parse_csv_list(args.attacks, REAL_ATTACKS),
            device=args.device, conf=args.conf, imgsz=args.imgsz, n=args.n,
            epsilon=args.epsilon, seed=args.seed,
            strict_coverage=not args.allow_partial_captures,
            config_extra={"display_width": args.display_width,
                          "display_height": args.display_height,
                          "refresh_hz": args.refresh_hz, "pos": args.pos,
                          "device_name": args.device_name},
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(build_arg_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
