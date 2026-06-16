"""MOT17 tracking attack experiment using a shared ByteTrack-style tracker."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.attack.detectors import build_detector
from src.evaluation.detection_suite import (
    DEFAULT_ATTACKS,
    DEFAULT_MODELS,
    build_attack_variants,
    default_device,
    load_rgb,
    parse_csv_list,
    print_metric_table,
    write_json,
)
from src.evaluation.mot import (
    build_bytetrack_tracker,
    compute_tracking_metrics,
    list_mot_sequences,
    load_mot_sequence,
    prepare_trackeval_workspace,
    run_trackeval_hota,
)


def run_mot_tracking_attack(
    mot_root: str | Path = "data/MOT17",
    output_dir: str | Path = "experiments/results",
    models: list[str] | None = None,
    detector_factory=None,
    sequences: list[str] | None = None,
    split: str = "train",
    max_frames: int | None = None,
    attacks: list[str] | None = None,
    device: str | None = None,
    n: int = 4,
    epsilon: float = 8 / 255,
    conf: float = 0.25,
    imgsz: int = 640,
    seed: int = 0,
    prefer_external_tracker: bool = True,
    enable_hota: bool = True,
    trackeval_root: str | Path | None = None,
) -> dict:
    root = Path(mot_root)
    selected_models = models or list(DEFAULT_MODELS)
    selected_attacks = attacks or list(DEFAULT_ATTACKS)
    selected_device = device or default_device()
    selected_sequences = sequences or list_mot_sequences(root, split=split)
    loaded = {
        seq: load_mot_sequence(root, seq, split=split, max_frames=max_frames)
        for seq in selected_sequences
    }
    gt_by_sequence = {seq: gt for seq, (_frames, gt) in loaded.items()}
    results: dict[str, dict[str, dict]] = {}
    statuses: dict[str, dict] = {}
    # Keep predicted tracks per (model, attack) so we can export MOTChallenge
    # files and recover HOTA from TrackEval after metrics are computed.
    track_runs: dict[tuple[str, str], dict[str, dict]] = {}

    for model_name in selected_models:
        detector = (
            detector_factory(model_name, selected_device)
            if detector_factory
            else build_detector(model_name, device=selected_device, conf=conf, imgsz=imgsz)
        )
        statuses[model_name] = detector.status()
        results[model_name] = {}
        tracker_name = "unknown"
        for attack in selected_attacks:
            tracks_by_sequence = {seq: {} for seq in selected_sequences}
            for seq, (frames, _gt) in loaded.items():
                tracker = build_bytetrack_tracker(prefer_external=prefer_external_tracker)
                tracker_name = getattr(tracker, "name", tracker_name)
                for frame in frames:
                    image = load_rgb(frame.path)
                    variants = build_attack_variants(
                        image,
                        attacks=[attack],
                        n=n,
                        epsilon=epsilon,
                        target_model=model_name,
                        seed=seed,
                        identifier=f"{seq}:{frame.frame_id}",
                        device=selected_device,
                    )
                    detections = [
                        box for box in detector.detect(variants[attack]) if box.label == "person"
                    ]
                    tracks_by_sequence[seq][frame.frame_id] = tracker.update(
                        detections,
                        sequence=seq,
                        frame_id=frame.frame_id,
                        image=image,
                    )
            results[model_name][attack] = compute_tracking_metrics(
                gt_by_sequence,
                tracks_by_sequence,
            )
            track_runs[(model_name, attack)] = tracks_by_sequence

    hota_status = {"available": False, "reason": "disabled"}
    if enable_hota:
        hota_status = _augment_with_hota(
            output_dir=output_dir,
            gt_by_sequence=gt_by_sequence,
            track_runs=track_runs,
            results=results,
            split=split,
            trackeval_root=trackeval_root,
        )

    report = {
        "config": {
            "dataset": "MOT17",
            "mot_root": str(root),
            "split": split,
            "models": selected_models,
            "sequences": selected_sequences,
            "attacks": selected_attacks,
            "device": selected_device,
            "tracker": tracker_name,
            "n": int(n),
            "epsilon": float(epsilon),
            "conf": float(conf),
            "imgsz": int(imgsz),
            "seed": int(seed),
            "max_frames": max_frames,
            "hota": hota_status,
        },
        "detectors": statuses,
        "results": results,
    }
    out = Path(output_dir) / "mot_tracking_attack.json"
    write_json(out, report)
    print_metric_table("MOT17 Tracking Attack", results, ["mota", "motp", "idf1", "hota", "n_frames"])
    print(f"Saved: {out}")
    return report


def _augment_with_hota(
    *,
    output_dir: str | Path,
    gt_by_sequence: dict[str, dict],
    track_runs: dict[tuple[str, str], dict[str, dict]],
    results: dict[str, dict[str, dict]],
    split: str,
    trackeval_root: str | Path | None,
) -> dict:
    """Export MOTChallenge files and fold TrackEval HOTA back into ``results``.

    Always writes the exportable workspace (so HOTA can be produced manually even
    when TrackEval is not installed). When TrackEval runs, HOTA/DetA/AssA are
    merged into each ``results[model][attack]`` row.
    """
    workspace = Path(output_dir) / "trackeval_workspace"
    trackers = {f"{model}__{attack}": runs for (model, attack), runs in track_runs.items()}
    workspace_info = prepare_trackeval_workspace(
        workspace, gt_by_sequence, trackers, split=split
    )
    hota_result = run_trackeval_hota(workspace_info, trackeval_root=trackeval_root)
    if hota_result.get("available"):
        for (model, attack) in track_runs:
            tracker_metrics = hota_result["trackers"].get(f"{model}__{attack}", {})
            for key in ("hota", "deta", "assa", "loca"):
                if key in tracker_metrics:
                    results[model][attack][key] = tracker_metrics[key]
    else:
        print(
            "[mot-tracking] HOTA not computed "
            f"({hota_result.get('reason')}); MOTChallenge files exported to "
            f"{workspace_info['trackers_folder']}. Run TrackEval there to obtain HOTA."
        )
    return {
        "available": bool(hota_result.get("available")),
        "reason": hota_result.get("reason"),
        "workspace": workspace_info["workspace"],
        "gt_folder": workspace_info["gt_folder"],
        "trackers_folder": workspace_info["trackers_folder"],
        "seqmap_file": workspace_info["seqmap_file"],
        "benchmark": workspace_info["benchmark"],
        "split": workspace_info["split"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mot-root", default="data/MOT17")
    parser.add_argument("--output-dir", default="experiments/results")
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--sequences", default="")
    parser.add_argument("--attacks", default=",".join(DEFAULT_ATTACKS))
    parser.add_argument("--split", default="train")
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--smoke", action="store_true", help="Run a bounded sample for setup checks.")
    parser.add_argument("--device", default=None)
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--epsilon", type=float, default=8 / 255)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--no-external-tracker", action="store_true")
    parser.add_argument(
        "--trackeval-root",
        default=None,
        help="Path to a TrackEval checkout for HOTA (defaults to $TRACKEVAL_ROOT).",
    )
    parser.add_argument(
        "--no-hota",
        action="store_true",
        help="Skip MOTChallenge export and TrackEval HOTA computation.",
    )
    args = parser.parse_args(argv)
    max_frames = args.max_frames
    if args.smoke and max_frames is None:
        max_frames = 30
    run_mot_tracking_attack(
        mot_root=args.mot_root,
        output_dir=args.output_dir,
        models=parse_csv_list(args.models, DEFAULT_MODELS),
        sequences=parse_csv_list(args.sequences, []),
        split=args.split,
        max_frames=max_frames,
        attacks=parse_csv_list(args.attacks, DEFAULT_ATTACKS),
        device=args.device,
        n=args.n,
        epsilon=args.epsilon,
        conf=args.conf,
        imgsz=args.imgsz,
        seed=args.seed,
        prefer_external_tracker=not args.no_external_tracker,
        enable_hota=not args.no_hota,
        trackeval_root=args.trackeval_root,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
