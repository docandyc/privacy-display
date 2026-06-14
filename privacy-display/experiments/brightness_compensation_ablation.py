"""
Experiment — brightness-compensation factor ablation.

The deployed design restores brightness with a pure backlight boost (gamma=1.0,
so integration boost = n) rather than pixel-space compensation. This ablation
justifies that choice and answers whether a brighter output raises attacker SNR:
it sweeps the pixel-space compensation factor gamma in {1.0 (backlight-only),
n/2, n (full pixel compensation)} and measures, per gamma:

  - perceptual cost: CIEDE2000 ΔE, SSIM, and the highlight clip fraction
    (pixel-space compensation clips bright content, breaking reconstruction);
  - attacker leakage: single-frame OCR (does a brighter subframe leak more?) and
    full-cycle temporal-average OCR (the boundary attack).

Expected story: gamma=1.0 reconstructs exactly (ΔE~0) and single-frame OCR stays
at the floor for every gamma, while larger gamma only adds perceptual clipping
cost without buying any attacker advantage — i.e. brightness compensation does
not compromise single-frame security.

Run:
    python experiments/brightness_compensation_ablation.py --max-samples 8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.camera_simulator import CameraSimulator  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator  # noqa: E402
from src.core.mask_generator import MaskGenerator  # noqa: E402
from src.core.noise_injector import NoiseInjector  # noqa: E402
from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.evaluation.benchmark import _mean_std  # noqa: E402
from src.evaluation.metrics import compute_delta_e, compute_ssim  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402

RESULT_FILE = "brightness_compensation_ablation.json"

ABLATION_KEY = b"brightness-comp-ablation-key-0000"


def build_subframes_gamma(img, n, epsilon, cycle, gamma):
    """Compose one cycle with an explicit pixel-space compensation factor gamma."""
    h, w = img.shape[:2]
    gen = MaskGenerator(w, h, n, key=ABLATION_KEY)
    composer = SubframeComposer(n=n, gamma=gamma)
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


def clip_fraction(subframes: list[np.ndarray]) -> float:
    """Fraction of subframe pixels saturated at 255 (pixel-compensation cost)."""
    return float(np.mean([np.mean(sf >= 255) for sf in subframes]))


def _gamma_key(gamma: float) -> str:
    return f"gamma_{gamma:.2f}"


def run_brightness_ablation(
    output_dir: str | Path = ROOT / "experiments" / "results",
    n: int = 4,
    epsilon: float = 8 / 255,
    gammas: tuple[float, ...] | None = None,
    max_samples: int = 8,
    samples_per_category: int | None = None,
    ocr_timeout: float = 4.0,
    evaluator: OCREvaluator | None = None,
    corpus: tuple[list, list[str], list[str]] | None = None,
    metadata: dict | None = None,
    progress_interval: int = 2,
    save: bool = True,
) -> dict:
    if progress_interval < 0:
        raise ValueError("progress_interval must be non-negative")
    gammas = gammas or (1.0, n / 2, float(n))

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
    cam = CameraSimulator()

    acc: dict[float, dict[str, list[float]]] = {
        g: {k: [] for k in ("delta_e", "ssim", "clip_fraction", "single_frame_ocr", "full_cycle_ocr")}
        for g in gammas
    }

    total = len(images)
    for idx, (img, gt) in enumerate(zip(images, truths)):
        for gamma in gammas:
            subframes, integrated = build_subframes_gamma(img, n, epsilon, idx, gamma)
            acc[gamma]["delta_e"].append(compute_delta_e(img, integrated))
            acc[gamma]["ssim"].append(compute_ssim(img, integrated))
            acc[gamma]["clip_fraction"].append(clip_fraction(subframes))
            acc[gamma]["single_frame_ocr"].append(
                float(np.mean([ev.evaluate_single(s, gt, "tesseract").char_accuracy for s in subframes]))
            )
            full = cam.temporal_averaging_attack(subframes, n, randomize_order=False)
            acc[gamma]["full_cycle_ocr"].append(ev.evaluate_single(full, gt, "tesseract").char_accuracy)
        if progress_interval and ((idx + 1) % progress_interval == 0 or idx + 1 == total):
            print(f"  brightness-comp sample {idx + 1}/{total}")

    summary = {}
    for gamma in gammas:
        entry = {"gamma": float(gamma), "integration_boost": float(n) / float(gamma)}
        entry.update({k: _mean_std(v) for k, v in acc[gamma].items()})
        summary[_gamma_key(gamma)] = entry

    report = {
        "config": {
            "n": n,
            "epsilon": epsilon,
            "gammas": [float(g) for g in gammas],
            "n_samples": len(images),
            "sample_policy": sample_policy,
            "note": "gamma=1.0 is the deployed backlight-only model (integration boost=n).",
        },
        "summary": summary,
    }

    if save:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / RESULT_FILE
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n=== Brightness compensation ablation, n={n} ===")
        print("|  gamma  | boost |  ΔE  | SSIM | clip% | 1-frame OCR | full-cycle OCR |")
        print("|" + "---|" * 7)
        for gamma in gammas:
            s = summary[_gamma_key(gamma)]
            print(
                f"| {gamma:.2f} | {s['integration_boost']:.2f} | {s['delta_e']['mean']:.2f} | "
                f"{s['ssim']['mean']:.3f} | {s['clip_fraction']['mean'] * 100:.1f}% | "
                f"{s['single_frame_ocr']['mean'] * 100:.0f}% | {s['full_cycle_ocr']['mean'] * 100:.0f}% |"
            )
        print(f"Saved: {out}")

    return report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Brightness-compensation factor ablation")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--gammas", default=None, help="Comma-separated gammas; default 1.0,n/2,n")
    p.add_argument("--max-samples", type=int, default=8)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--progress-interval", type=int, default=2)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    gammas = None
    if args.gammas:
        gammas = tuple(float(x.strip()) for x in args.gammas.split(",") if x.strip())
    run_brightness_ablation(
        output_dir=args.output_dir,
        n=args.n,
        epsilon=args.epsilon,
        gammas=gammas,
        max_samples=args.max_samples,
        samples_per_category=args.samples_per_category,
        ocr_timeout=args.ocr_timeout,
        progress_interval=args.progress_interval,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
