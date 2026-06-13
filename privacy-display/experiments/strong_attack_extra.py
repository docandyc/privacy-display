"""
Experiment F — additional strong-attacker baselines for the boundary analysis.

Extends the existing strong-camera suite (phase search / differential / blue
max) with two attacks that a reviewer would expect against a temporal-slicing
display:

  - rolling-shutter row alignment: multi-phase rolling captures aligned per
    pixel, showing rolling shutter is not extra protection.
  - temporal super-resolution: per-pixel max aggregation over >=1 cycle.

Both are expected to breach (high recovery), which reinforces the honest
boundary: any full-cycle pixel-wise aggregation inverts the mutually-exclusive
complete mask. Single-subframe capture (reported alongside) still defends.

Run:
    python experiments/strong_attack_extra.py --max-samples 40
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.camera_simulator import CameraSimulator, CameraParams  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator, text_recovery_metrics  # noqa: E402
from src.evaluation.benchmark import _mean_std, _psnr_db, compose_protected_subframes  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402

ATTACKS = ["single_subframe", "rolling_shutter_single", "rolling_shutter_row_alignment",
           "temporal_superresolution"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Experiment F: extra strong attacks")
    p.add_argument("--max-samples", type=int, default=40)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--cycles", type=int, default=2)
    p.add_argument("--display-rate", type=float, default=240.0)
    p.add_argument("--n-captures", type=int, default=8)
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--progress-interval", type=int, default=10)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.n < 2:
        raise ValueError("n must be at least 2")
    if args.cycles <= 0:
        raise ValueError("cycles must be positive")
    if args.progress_interval < 0:
        raise ValueError("progress_interval must be non-negative")
    images, truths, names = load_corpus()
    metadata = load_corpus_metadata()
    selected_indices, sample_policy = select_publication_subset(
        names,
        metadata,
        max_samples=args.max_samples,
        samples_per_category=args.samples_per_category,
    )
    images = take_indices(images, selected_indices)
    truths = take_indices(truths, selected_indices)
    names = take_indices(names, selected_indices)

    ev = OCREvaluator(engines=["tesseract"], timeout=args.ocr_timeout)
    # Short exposure (< subframe interval) so a single rolling frame stays
    # fragmented; the row-alignment attack must combine multiple phases to win.
    delta_t = 1.0 / args.display_rate
    cam = CameraSimulator(CameraParams(readout_time=15e-6, exposure_time=delta_t * 0.5))

    rows: list[dict] = []
    total = len(images)
    for idx, (img, gt, name) in enumerate(zip(images, truths, names)):
        if args.progress_interval and (idx == 0 or (idx + 1) % args.progress_interval == 0 or idx + 1 == total):
            print(f"  sample {idx + 1}/{total}: {name}")
        sf = compose_protected_subframes(img, n=args.n, epsilon=args.epsilon,
                                         cycles=args.cycles, cycle_start=idx * args.cycles)
        rolling_single = cam.capture_rolling_shutter(sf, args.display_rate, switch_time=0.0)
        rolling_align, rolling_align_meta = cam.rolling_shutter_row_alignment_attack(
            sf, args.display_rate, n_captures=args.n_captures)
        superres, superres_meta = cam.temporal_superresolution_attack(sf)
        frames = {
            "single_subframe": (sf[0], {"attack": "global_shutter_slot0"}),
            "rolling_shutter_single": (rolling_single, {"attack": "rolling_shutter_single"}),
            "rolling_shutter_row_alignment": (rolling_align, rolling_align_meta),
            "temporal_superresolution": (superres, superres_meta),
        }
        for attack, (frame, attack_meta) in frames.items():
            ocr_error = ""
            try:
                text = ev.recognize(frame, "tesseract")
            except Exception as exc:
                text = ""
                ocr_error = str(exc)
            m = text_recovery_metrics(text, gt)
            rows.append({
                "name": name, "attack": attack, "metadata": metadata.get(name, {}),
                "char_accuracy": m["char_accuracy"], "word_accuracy": m["word_accuracy"],
                "exact_match": m["exact_match"],
                "sensitive_token_recall": m["sensitive_token_recall"],
                "sensitive_token_count": m["sensitive_token_count"],
                "psnr_db": _psnr_db(img, frame),
                "reconstruction_score": float(attack_meta.get("score", 0.0)),
                "attack_metadata": attack_meta,
                "recognized_text": text[:160],
                "ocr_error": ocr_error,
            })

    summary = {}
    for attack in ATTACKS:
        grp = [r for r in rows if r["attack"] == attack]
        sens = [r for r in grp if int(r.get("sensitive_token_count", 0)) > 0]
        summary[attack] = {
            "char_accuracy": _mean_std([float(r["char_accuracy"]) for r in grp]),
            "word_accuracy": _mean_std([float(r["word_accuracy"]) for r in grp]),
            "exact_match": _mean_std([float(r["exact_match"]) for r in grp]),
            "sensitive_token_recall": _mean_std([float(r["sensitive_token_recall"]) for r in sens]),
            "leak_rate_char_ge_20pct": _mean_std([float(r["char_accuracy"] >= 0.20) for r in grp]),
            "psnr_db": _mean_std([float(r["psnr_db"]) for r in grp]),
            "error_count": int(sum(1 for r in grp if r.get("ocr_error"))),
        }

    report = {
        "config": {"n": args.n, "epsilon": args.epsilon, "cycles": args.cycles,
                   "display_rate_hz": args.display_rate, "n_captures": args.n_captures,
                   "exposure_time_s": delta_t * 0.5, "n_samples": len(images),
                   "sample_policy": sample_policy},
        "summary": summary, "samples": rows,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "strong_attack_extra.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== Extra strong attacks (n=%d, %.0fHz) ===" % (args.n, args.display_rate))
    print("| attack | char recovery | exact | sensitive | leak rate |")
    print("|" + "---|" * 5)
    for attack in ATTACKS:
        s = summary[attack]
        print(f"| {attack} | {s['char_accuracy']['mean'] * 100:.1f}% | "
              f"{s['exact_match']['mean'] * 100:.1f}% | "
              f"{s['sensitive_token_recall']['mean'] * 100:.1f}% | "
              f"{s['leak_rate_char_ge_20pct']['mean'] * 100:.1f}% |")
    print(f"\nSaved: {out}")
    print("Expected: single-subframe & single rolling frame defend (~0%); "
          "multi-phase row alignment and temporal super-resolution breach — "
          "reinforcing the full-cycle linear-slicing boundary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
