"""COCO val2017 multi-detector attack experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.attack.detectors import build_detector
from src.evaluation.coco_eval import (
    detections_to_coco_results,
    evaluate_coco_detections,
    load_coco_records,
)
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


def run_coco_detection_attack(
    coco_root: str | Path = "data/coco",
    output_dir: str | Path = "experiments/results",
    models: list[str] | None = None,
    detector_factory=None,
    split: str = "val2017",
    max_images: int | None = None,
    attacks: list[str] | None = None,
    device: str | None = None,
    n: int = 4,
    epsilon: float = 8 / 255,
    conf: float = 0.25,
    imgsz: int = 640,
    seed: int = 0,
) -> dict:
    root = Path(coco_root)
    selected_models = models or list(DEFAULT_MODELS)
    selected_attacks = attacks or list(DEFAULT_ATTACKS)
    selected_device = device or default_device()
    images, annotations, ann_path = load_coco_records(root, split=split, max_images=max_images)
    results: dict[str, dict[str, dict]] = {}
    statuses: dict[str, dict] = {}

    for model_name in selected_models:
        detector = (
            detector_factory(model_name, selected_device)
            if detector_factory
            else build_detector(model_name, device=selected_device, conf=conf, imgsz=imgsz)
        )
        statuses[model_name] = detector.status()
        by_attack: dict[str, list[dict]] = {attack: [] for attack in selected_attacks}
        for image_info in images:
            image = load_rgb(root / split / image_info["file_name"])
            variants = build_attack_variants(
                image,
                attacks=selected_attacks,
                n=n,
                epsilon=epsilon,
                target_model=model_name,
                seed=seed,
                identifier=image_info["file_name"],
            )
            for attack, variant in variants.items():
                detections = detector.detect(variant)
                by_attack[attack].extend(detections_to_coco_results(image_info["id"], detections))
        results[model_name] = {
            attack: evaluate_coco_detections(ann_path, images, annotations, rows)
            for attack, rows in by_attack.items()
        }

    report = {
        "config": {
            "dataset": "COCO",
            "coco_root": str(root),
            "split": split,
            "models": selected_models,
            "attacks": selected_attacks,
            "device": selected_device,
            "n": int(n),
            "epsilon": float(epsilon),
            "conf": float(conf),
            "imgsz": int(imgsz),
            "seed": int(seed),
            "max_images": max_images,
        },
        "detectors": statuses,
        "results": results,
        "baseline_clean_map": {
            model: metrics.get("clean", {}).get("map")
            for model, metrics in results.items()
        },
    }
    out = Path(output_dir) / "coco_detection_attack.json"
    write_json(out, report)
    print_metric_table("COCO Detection Attack", results, ["map", "map50", "map75", "ap_small", "ap_medium", "ap_large", "ar", "n_images"])
    print(f"Saved: {out}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coco-root", default="data/coco")
    parser.add_argument("--output-dir", default="experiments/results")
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--attacks", default=",".join(DEFAULT_ATTACKS))
    parser.add_argument("--split", default="val2017")
    parser.add_argument("--max-images", type=int, default=None)
    parser.add_argument("--smoke", action="store_true", help="Run a bounded sample for setup checks.")
    parser.add_argument("--device", default=None)
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--epsilon", type=float, default=8 / 255)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    max_images = args.max_images
    if args.smoke and max_images is None:
        max_images = 8
    run_coco_detection_attack(
        coco_root=args.coco_root,
        output_dir=args.output_dir,
        models=parse_csv_list(args.models, DEFAULT_MODELS),
        split=args.split,
        max_images=max_images,
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
