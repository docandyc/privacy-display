"""MOT17 frame-level person detection attack experiment."""

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
from src.evaluation.mot import compute_detection_metrics, list_mot_sequences, load_mot_sequence


def run_mot_video_detection(
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

    for model_name in selected_models:
        detector = (
            detector_factory(model_name, selected_device)
            if detector_factory
            else build_detector(model_name, device=selected_device, conf=conf, imgsz=imgsz)
        )
        statuses[model_name] = detector.status()
        pred_by_attack = {
            attack: {seq: {} for seq in selected_sequences}
            for attack in selected_attacks
        }
        for seq, (frames, _gt) in loaded.items():
            for frame in frames:
                image = load_rgb(frame.path)
                variants = build_attack_variants(
                    image,
                    attacks=selected_attacks,
                    n=n,
                    epsilon=epsilon,
                    target_model=model_name,
                    seed=seed,
                    identifier=f"{seq}:{frame.frame_id}",
                    device=selected_device,
                )
                for attack, variant in variants.items():
                    pred_by_attack[attack][seq][frame.frame_id] = [
                        box for box in detector.detect(variant) if box.label == "person"
                    ]
        results[model_name] = {
            attack: compute_detection_metrics(gt_by_sequence, pred_by_sequence)
            for attack, pred_by_sequence in pred_by_attack.items()
        }

    report = {
        "config": {
            "dataset": "MOT17",
            "mot_root": str(root),
            "split": split,
            "models": selected_models,
            "sequences": selected_sequences,
            "attacks": selected_attacks,
            "device": selected_device,
            "n": int(n),
            "epsilon": float(epsilon),
            "conf": float(conf),
            "imgsz": int(imgsz),
            "seed": int(seed),
            "max_frames": max_frames,
        },
        "detectors": statuses,
        "results": results,
    }
    out = Path(output_dir) / "mot_video_detection.json"
    write_json(out, report)
    print_metric_table("MOT17 Video Detection Attack", results, ["map", "map50", "recall", "precision", "n_frames"])
    print(f"Saved: {out}")
    return report


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
    args = parser.parse_args(argv)
    max_frames = args.max_frames
    if args.smoke and max_frames is None:
        max_frames = 30
    run_mot_video_detection(
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
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
