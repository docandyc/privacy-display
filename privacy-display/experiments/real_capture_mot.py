"""MOT17 real-device camera-capture detection + tracking attack (Windows 240Hz).

Stop-motion analogue of ``experiments/mot_video_detection.py`` and
``experiments/mot_tracking_attack.py``: a short MOT17 clip (~450 consecutive
frames of one sequence) is played one frame at a time on the privacy display and
photographed with a real USB webcam. Per displayed frame we capture three
conditions (real_clean / real_short / real_video) exactly like the COCO
real-capture experiment, rectify + crop each back to the original frame
resolution, then offline run the 4 detectors + ByteTrack to produce:

  real_capture_mot_detection.json  – per-frame person mAP/recall (mirrors
                                      mot_video_detection.json schema).
  real_capture_mot_tracking.json   – MOTA/MOTP/IDF1 (+ optional HOTA via
                                      TrackEval; mirrors mot_tracking_attack.json).

Capture reuses the persistent playback + camera helpers from
``real_capture_detection`` so a single pygame process serves the whole clip.
``--eval-only`` re-scores already-captured frames with no camera/display.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.real_capture_detection import (  # noqa: E402
    COCO_CAPTURE_SPECS,
    DEFAULT_DISPLAY_HEIGHT,
    DEFAULT_DISPLAY_WIDTH,
    DEFAULT_REFRESH_HZ,
    NOISE_TARGET,
    PersistentDisplay,
    _capture_one_attack,
    _coverage_payload,
    _letterbox,
    _load_capture_manifest,
    _warn_if_uncalibrated_exposure,
    assert_roi_matches_canvas,
    exposure_calibration_status,
)
from experiments.real_capture_calibrate import (  # noqa: E402
    DEFAULT_CALIBRATION_DIR,
    load_roi_calibration,
    roi_path,
)
from experiments.real_capture_shoot import (  # noqa: E402
    DEFAULT_CAPTURE_DIR,
    DEFAULT_DEVICE,
    DEFAULT_DEVICE_NAME,
)
from src.attack.detectors import build_detector  # noqa: E402
from src.evaluation.detection_suite import (  # noqa: E402
    DEFAULT_MODELS,
    build_display_subframes,
    load_rgb,
    parse_csv_list,
    print_metric_table,
    write_json,
)
from src.evaluation.mot import (  # noqa: E402
    build_bytetrack_tracker,
    compute_detection_metrics,
    compute_tracking_metrics,
    list_mot_sequences,
    load_mot_sequence,
    prepare_trackeval_workspace,
    run_trackeval_hota,
)

DET_RESULT_FILENAME = "real_capture_mot_detection.json"
TRK_RESULT_FILENAME = "real_capture_mot_tracking.json"
REAL_ATTACKS = ("real_clean", "real_short", "real_video")


def _capture_subdir(capture_dir: str | Path, sequence: str) -> Path:
    return Path(capture_dir) / f"mot_{sequence}"


def _mot_capture_coverage(
    capture_root: Path,
    attacks: list[str],
    frames: list,
    *,
    strict: bool = True,
) -> dict:
    expected = [int(frame.frame_id) for frame in frames]
    by_attack = {
        attack: [
            int(frame.frame_id)
            for frame in frames
            if (capture_root / attack / f"{frame.frame_id:06d}.png").exists()
        ]
        for attack in attacks
    }
    coverage = _coverage_payload(expected_ids=expected, by_attack=by_attack, id_label="frame_id")
    if strict and not coverage["complete"]:
        raise ValueError(
            "Incomplete MOT capture coverage: "
            f"missing_by_attack={coverage['missing_by_attack']}"
        )
    if not coverage["shared_ids"]:
        raise ValueError("No shared MOT captures available across requested attacks")
    return coverage


# --------------------------------------------------------------------------- #
# Capture (Windows): stop-motion over the clip with one persistent playback.
# --------------------------------------------------------------------------- #
def capture_mot(args: argparse.Namespace, frames: list, root: Path) -> dict:
    from PIL import Image

    roi = load_roi_calibration(roi_path(args.calibration_dir, args.pos))
    assert_roi_matches_canvas(roi, args.display_width, args.display_height)
    from experiments.real_capture_ablation import load_exposure_calibration

    exposure_calib = load_exposure_calibration(args.calibration_dir)
    exposure_status = exposure_calibration_status(exposure_calib, COCO_CAPTURE_SPECS)
    _warn_if_uncalibrated_exposure(exposure_status)
    capture_root = _capture_subdir(args.capture_dir, args.sequence)
    for spec in COCO_CAPTURE_SPECS:
        (capture_root / spec.label).mkdir(parents=True, exist_ok=True)

    canvas = (args.display_width, args.display_height)
    manifest = {
        "captures": [],
        "config": {
            "capture_mode": "stop_motion_physical_frame_validation",
            "note": (
                "Each MOT frame is displayed as a static stimulus and captured under "
                "real_clean/real_short/real_video; this validates physical-frame "
                "effects, not continuous video playback synchronization."
            ),
            "canvas": canvas,
            "display_width": int(args.display_width),
            "display_height": int(args.display_height),
            "refresh_hz": float(getattr(args, "refresh_hz", DEFAULT_REFRESH_HZ)),
            "n": int(args.n),
            "epsilon": float(args.epsilon),
            "seed": int(args.seed),
            "pos": args.pos,
            "sequence": args.sequence,
            "calibration_dir": str(args.calibration_dir),
            "roi_output_width": int(roi.get("output_width", -1)),
            "roi_output_height": int(roi.get("output_height", -1)),
            "exposure_calibration": exposure_status,
        },
    }

    with tempfile.TemporaryDirectory(prefix="rc-mot-") as tmp:
        display = PersistentDisplay(args, Path(tmp))
        first = load_rgb(frames[0].path)
        display.start([_letterbox(first, *canvas)])
        try:
            for frame in frames:
                image = load_rgb(frame.path)
                src_h, src_w = image.shape[:2]
                subframes = build_display_subframes(
                    image, n=args.n, epsilon=args.epsilon, target_model=NOISE_TARGET,
                    seed=args.seed, identifier=f"{args.sequence}:{frame.frame_id}", device=args.device,
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
                    out = capture_root / spec.label / f"{frame.frame_id:06d}.png"
                    Image.fromarray(cropped).save(out)
                    manifest["captures"].append(
                        {
                            "frame_id": frame.frame_id,
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


# --------------------------------------------------------------------------- #
# Evaluation (hardware-free): load captured frames -> detectors + ByteTrack.
# --------------------------------------------------------------------------- #
def evaluate_capture(
    mot_root: str | Path,
    sequence: str,
    output_dir: str | Path = "experiments/results",
    capture_dir: str | Path = DEFAULT_CAPTURE_DIR,
    models: list[str] | None = None,
    split: str = "train",
    max_frames: int | None = None,
    attacks: list[str] | None = None,
    device: str | None = None,
    conf: float = 0.25,
    imgsz: int = 640,
    n: int = 4,
    epsilon: float = 8 / 255,
    seed: int = 0,
    prefer_external_tracker: bool = True,
    enable_hota: bool = True,
    trackeval_root: str | Path | None = None,
    detector_factory=None,
    config_extra: dict | None = None,
    strict_coverage: bool = True,
) -> tuple[dict, dict]:
    """Score captured MOT frames: per-frame detection + ByteTrack tracking."""
    root = Path(mot_root)
    selected_models = list(models or DEFAULT_MODELS)
    selected_attacks = list(attacks or REAL_ATTACKS)
    frames, gt = load_mot_sequence(root, sequence, split=split, max_frames=max_frames)
    capture_root = _capture_subdir(capture_dir, sequence)
    coverage = _mot_capture_coverage(
        capture_root, selected_attacks, frames, strict=strict_coverage
    )
    shared_ids = set(coverage["shared_ids"])
    eval_frames = [frame for frame in frames if int(frame.frame_id) in shared_ids]
    capture_manifest = _load_capture_manifest(capture_root)

    det_results: dict[str, dict[str, dict]] = {}
    trk_results: dict[str, dict[str, dict]] = {}
    statuses: dict[str, dict] = {}
    track_runs: dict[tuple[str, str], dict[str, dict]] = {}
    tracker_name = "unknown"

    for model_name in selected_models:
        detector = (
            detector_factory(model_name, device)
            if detector_factory
            else build_detector(model_name, device=device or "cpu", conf=conf, imgsz=imgsz)
        )
        statuses[model_name] = detector.status()
        det_results[model_name] = {}
        trk_results[model_name] = {}
        for attack in selected_attacks:
            pred_by_frame: dict[int, list] = {}
            tracks_by_frame: dict[int, list] = {}
            captured_gt: dict[int, list] = {}
            tracker = build_bytetrack_tracker(prefer_external=prefer_external_tracker)
            tracker_name = getattr(tracker, "name", tracker_name)
            for frame in eval_frames:
                path = capture_root / attack / f"{frame.frame_id:06d}.png"
                image = load_rgb(path)
                dets = detector.detect(image)
                pred_by_frame[frame.frame_id] = dets
                persons = [box for box in dets if box.label == "person"]
                tracks_by_frame[frame.frame_id] = tracker.update(
                    persons, sequence=sequence, frame_id=frame.frame_id, image=image
                )
                captured_gt[frame.frame_id] = gt.get(frame.frame_id, [])
            gt_by_sequence = {sequence: captured_gt}
            det_results[model_name][attack] = compute_detection_metrics(
                gt_by_sequence, {sequence: pred_by_frame}
            )
            trk_results[model_name][attack] = compute_tracking_metrics(
                gt_by_sequence, {sequence: tracks_by_frame}
            )
            track_runs[(model_name, attack)] = {sequence: tracks_by_frame}

    # GT for HOTA export uses the captured frames of real_clean (the densest set).
    gt_for_hota = {sequence: {f.frame_id: gt.get(f.frame_id, []) for f in eval_frames}}
    hota_status = {"available": False, "reason": "disabled"}
    if enable_hota:
        hota_status = _augment_with_hota(
            output_dir=output_dir, gt_by_sequence=gt_for_hota, track_runs=track_runs,
            results=trk_results, split=split, trackeval_root=trackeval_root,
        )

    base_config = {
        "dataset": "MOT17",
        "capture": "real_device_webcam",
        "mot_root": str(root),
        "split": split,
        "sequence": sequence,
        "models": selected_models,
        "attacks": selected_attacks,
        "device": device,
        "n": int(n),
        "epsilon": float(epsilon),
        "conf": float(conf),
        "imgsz": int(imgsz),
        "seed": int(seed),
        "max_frames": max_frames,
        "noise_target": NOISE_TARGET,
        "capture_mode": "stop_motion_physical_frame_validation",
        "capture_mode_note": (
            "MOT real capture is stop-motion: each dataset frame is displayed as a "
            "static stimulus before camera capture, so this is not a continuous "
            "video playback synchronization experiment."
        ),
        **(config_extra or {}),
    }
    capture_section = {
        "mode": "stop_motion_physical_frame_validation",
        "coverage": coverage,
        "manifest_path": str(capture_root / "capture_manifest.json"),
        "manifest": capture_manifest,
    }
    det_report = {
        "config": base_config,
        "detectors": statuses,
        "capture": capture_section,
        "results": det_results,
    }
    trk_report = {
        "config": {**base_config, "tracker": tracker_name, "hota": hota_status},
        "detectors": statuses,
        "capture": capture_section,
        "results": trk_results,
    }
    det_out = Path(output_dir) / DET_RESULT_FILENAME
    trk_out = Path(output_dir) / TRK_RESULT_FILENAME
    write_json(det_out, det_report)
    write_json(trk_out, trk_report)
    print_metric_table(
        "MOT17 Real-Capture Detection", det_results,
        ["map", "map50", "recall", "precision", "n_frames"],
    )
    print_metric_table(
        "MOT17 Real-Capture Tracking", trk_results, ["mota", "motp", "idf1", "hota", "n_frames"]
    )
    print(f"Saved: {det_out}")
    print(f"Saved: {trk_out}")
    return det_report, trk_report


def _augment_with_hota(
    *, output_dir, gt_by_sequence, track_runs, results, split, trackeval_root
) -> dict:
    """Export MOTChallenge files and fold TrackEval HOTA back into tracking results."""
    workspace = Path(output_dir) / "trackeval_workspace_real"
    trackers = {f"{model}__{attack}": runs for (model, attack), runs in track_runs.items()}
    workspace_info = prepare_trackeval_workspace(workspace, gt_by_sequence, trackers, split=split)
    hota_result = run_trackeval_hota(workspace_info, trackeval_root=trackeval_root)
    if hota_result.get("available"):
        for (model, attack) in track_runs:
            tracker_metrics = hota_result["trackers"].get(f"{model}__{attack}", {})
            for key in ("hota", "deta", "assa", "loca"):
                if key in tracker_metrics:
                    results[model][attack][key] = tracker_metrics[key]
    else:
        print(
            "[mot-real] HOTA not computed "
            f"({hota_result.get('reason')}); MOTChallenge files exported to "
            f"{workspace_info['trackers_folder']}. Run TrackEval there to obtain HOTA."
        )
    return {
        "available": bool(hota_result.get("available")),
        "reason": hota_result.get("reason"),
        "workspace": workspace_info["workspace"],
        "trackers_folder": workspace_info["trackers_folder"],
        "benchmark": workspace_info["benchmark"],
        "split": workspace_info["split"],
    }


def _dry_run(args: argparse.Namespace, frames: list) -> int:
    print("[dry-run] MOT real-capture detection+tracking plan")
    print(f"  sequence={args.sequence}  frames={len(frames)}  attacks={[s.label for s in COCO_CAPTURE_SPECS]}")
    print(f"  display={args.display_width}x{args.display_height}@{args.refresh_hz}Hz  n={args.n}")
    print(f"  captures planned={len(frames) * len(COCO_CAPTURE_SPECS)} (1 persistent playback)")
    print(f"  capture_dir={_capture_subdir(args.capture_dir, args.sequence)}")
    print(f"  results={Path(args.output_dir) / DET_RESULT_FILENAME}, {Path(args.output_dir) / TRK_RESULT_FILENAME}")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mot-root", default="data/MOT17")
    p.add_argument("--output-dir", default="experiments/results")
    p.add_argument("--capture-dir", default=DEFAULT_CAPTURE_DIR)
    p.add_argument("--models", default=",".join(DEFAULT_MODELS))
    p.add_argument("--attacks", default=",".join(REAL_ATTACKS))
    p.add_argument("--sequence", default=None, help="MOT17 sequence (default: first in split)")
    p.add_argument("--split", default="train")
    p.add_argument("--max-frames", type=int, default=450)
    p.add_argument("--device", default=None, help="cuda:N for detectors/PGD (offline)")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-external-tracker", action="store_true")
    p.add_argument("--trackeval-root", default=None)
    p.add_argument("--no-hota", action="store_true")
    # capture-side (Windows)
    p.add_argument("--camera-index", type=int, default=DEFAULT_DEVICE)
    p.add_argument("--device-name", default=DEFAULT_DEVICE_NAME)
    p.add_argument("--backend", default=None)
    p.add_argument("--fourcc", default="MJPG")
    p.add_argument("--display-width", type=int, default=DEFAULT_DISPLAY_WIDTH)
    p.add_argument("--display-height", type=int, default=DEFAULT_DISPLAY_HEIGHT)
    p.add_argument("--refresh-hz", type=float, default=DEFAULT_REFRESH_HZ)
    p.add_argument("--warmup", type=float, default=0.8)
    p.add_argument("--settle", type=float, default=0.5)
    p.add_argument("--calibration-dir", default=DEFAULT_CALIBRATION_DIR)
    p.add_argument("--pos", default="d0.5_a0")
    p.add_argument("--video-window", type=int, default=0)
    p.add_argument("--playback-timeout", type=float, default=30.0)
    p.add_argument("--advance-timeout", type=float, default=5.0)
    p.add_argument("--allow-partial-captures", action="store_true")
    p.add_argument("--capture-only", action="store_true")
    p.add_argument("--eval-only", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p


def run(args: argparse.Namespace) -> int:
    root = Path(args.mot_root)
    try:
        if not args.sequence:
            args.sequence = list_mot_sequences(root, split=args.split)[0]
        frames, _gt = load_mot_sequence(root, args.sequence, split=args.split, max_frames=args.max_frames)
    except FileNotFoundError as exc:
        if args.dry_run:
            print(f"[dry-run] dataset unavailable: {exc}")
            frames = []
            if not args.sequence:
                args.sequence = "<unknown>"
        else:
            raise
    if args.dry_run:
        return _dry_run(args, frames)
    if not args.eval_only:
        capture_mot(args, frames, root)
    if not args.capture_only:
        evaluate_capture(
            mot_root=root, sequence=args.sequence, output_dir=args.output_dir,
            capture_dir=args.capture_dir, models=parse_csv_list(args.models, DEFAULT_MODELS),
            split=args.split, max_frames=args.max_frames,
            attacks=parse_csv_list(args.attacks, REAL_ATTACKS), device=args.device,
            conf=args.conf, imgsz=args.imgsz, n=args.n, epsilon=args.epsilon, seed=args.seed,
            prefer_external_tracker=not args.no_external_tracker, enable_hota=not args.no_hota,
            trackeval_root=args.trackeval_root,
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
