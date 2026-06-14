"""
Experiment — PRNG seed-sensitivity check.

The masks and complementary noise are driven by a per-key CSPRNG. A reviewer may
ask whether the reported metrics depend on the particular key/seed. This check
re-derives the protection under K independent keys on a fixed sample subset and
reports, per metric, the overall mean±CI plus the mean/max per-sample standard
deviation *across seeds* — a near-zero across-seed std demonstrates the
conclusions are seed-invariant rather than a lucky draw.

Metrics: single-frame OCR (security), CIEDE2000 ΔE / SSIM (perceptual fidelity),
and single-frame mutual information (entropy_ratio).

Run:
    python experiments/seed_sensitivity.py --seeds 10 --max-samples 8
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator  # noqa: E402
from src.core.mask_generator import MaskGenerator  # noqa: E402
from src.core.noise_injector import NoiseInjector  # noqa: E402
from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.evaluation.benchmark import _mean_std  # noqa: E402
from src.evaluation.metrics import compute_delta_e, compute_entropy_ratio, compute_ssim  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402

RESULT_FILE = "seed_sensitivity.json"


def seed_key(index: int) -> bytes:
    return hashlib.sha256(f"seed-sensitivity-{index}".encode()).digest()


def build_with_key(img, n, epsilon, cycle, key):
    h, w = img.shape[:2]
    gen = MaskGenerator(w, h, n, key=key)
    composer = SubframeComposer(n=n, gamma=1.0)
    masks = gen.generate(cycle)
    pedestal = epsilon * 255
    sub_noises = None
    if epsilon > 0:
        injector = NoiseInjector(n=n, epsilon=epsilon)
        nb, _, _ = injector.generate_rotating_noise(img.astype(np.float32) / 255.0, cycle=cycle)
        sub_noises = [(x * 255 + pedestal).astype(np.float32) for x in injector.split_complementary(nb)]
    subframes = composer.compose(img, masks, sub_noises)
    integrated = composer.integrate_subframes(subframes, pedestal=pedestal if epsilon > 0 else 0.0)
    return subframes, integrated


def _stat_with_invariance(per_sample_seed_values: list[list[float]]) -> dict:
    """_mean_std over all (sample, seed) values plus the across-seed dispersion."""
    flat = [v for sample in per_sample_seed_values for v in sample]
    stats = _mean_std(flat)
    across = [float(np.std(sample)) for sample in per_sample_seed_values if len(sample) > 1]
    stats["mean_across_seed_std"] = float(np.mean(across)) if across else 0.0
    stats["max_across_seed_std"] = float(np.max(across)) if across else 0.0
    return stats


def run_seed_sensitivity(
    output_dir: str | Path = ROOT / "experiments" / "results",
    n: int = 4,
    epsilon: float = 8 / 255,
    n_seeds: int = 10,
    max_samples: int = 8,
    samples_per_category: int | None = None,
    ocr_timeout: float = 4.0,
    evaluator: OCREvaluator | None = None,
    corpus: tuple[list, list[str], list[str]] | None = None,
    metadata: dict | None = None,
    progress_interval: int = 2,
    save: bool = True,
) -> dict:
    if n_seeds < 1:
        raise ValueError("n_seeds must be positive")
    if progress_interval < 0:
        raise ValueError("progress_interval must be non-negative")

    if corpus is None:
        images, truths, names = load_corpus()
        corpus_metadata = load_corpus_metadata()
    else:
        images, truths, names = corpus
        corpus_metadata = metadata or {}

    selected_indices, sample_policy = select_publication_subset(
        names, corpus_metadata, max_samples=max_samples, samples_per_category=samples_per_category,
    )
    images = take_indices(images, selected_indices)
    truths = take_indices(truths, selected_indices)
    ev = evaluator or OCREvaluator(engines=["tesseract"], timeout=ocr_timeout)
    keys = [seed_key(i) for i in range(n_seeds)]

    metrics = ("single_frame_ocr", "delta_e", "ssim", "entropy_ratio")
    per_sample_seed: dict[str, list[list[float]]] = {m: [] for m in metrics}

    total = len(images)
    for idx, (img, gt) in enumerate(zip(images, truths)):
        seed_vals: dict[str, list[float]] = {m: [] for m in metrics}
        for key in keys:
            subframes, integrated = build_with_key(img, n, epsilon, idx, key)
            seed_vals["single_frame_ocr"].append(
                float(np.mean([ev.evaluate_single(s, gt, "tesseract").char_accuracy for s in subframes]))
            )
            seed_vals["delta_e"].append(compute_delta_e(img, integrated))
            seed_vals["ssim"].append(compute_ssim(img, integrated))
            seed_vals["entropy_ratio"].append(
                float(np.mean([compute_entropy_ratio(s, img) for s in subframes]))
            )
        for m in metrics:
            per_sample_seed[m].append(seed_vals[m])
        if progress_interval and ((idx + 1) % progress_interval == 0 or idx + 1 == total):
            print(f"  seed-sensitivity sample {idx + 1}/{total}")

    summary = {
        "single_frame_ocr": _stat_with_invariance(per_sample_seed["single_frame_ocr"]),
        "perceptual_invariance": {
            "delta_e": _stat_with_invariance(per_sample_seed["delta_e"]),
            "ssim": _stat_with_invariance(per_sample_seed["ssim"]),
            "entropy_ratio": _stat_with_invariance(per_sample_seed["entropy_ratio"]),
        },
    }

    report = {
        "config": {
            "n": n,
            "epsilon": epsilon,
            "n_seeds": n_seeds,
            "n_samples": len(images),
            "sample_policy": sample_policy,
            "note": "mean_across_seed_std ~ 0 indicates seed-invariant results.",
        },
        "summary": summary,
    }

    if save:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / RESULT_FILE
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        ocr = summary["single_frame_ocr"]
        de = summary["perceptual_invariance"]["delta_e"]
        print(f"\n=== Seed sensitivity, n={n}, seeds={n_seeds} ===")
        print(
            f"  single-frame OCR : {ocr['mean'] * 100:.2f}% "
            f"(across-seed std mean {ocr['mean_across_seed_std'] * 100:.3f}%, "
            f"max {ocr['max_across_seed_std'] * 100:.3f}%)"
        )
        print(
            f"  ΔE               : {de['mean']:.3f} "
            f"(across-seed std mean {de['mean_across_seed_std']:.4f})"
        )
        print(f"Saved: {out}")

    return report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PRNG seed-sensitivity check")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--max-samples", type=int, default=8)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--progress-interval", type=int, default=2)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    run_seed_sensitivity(
        output_dir=args.output_dir,
        n=args.n,
        epsilon=args.epsilon,
        n_seeds=args.seeds,
        max_samples=args.max_samples,
        samples_per_category=args.samples_per_category,
        ocr_timeout=args.ocr_timeout,
        progress_interval=args.progress_interval,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
