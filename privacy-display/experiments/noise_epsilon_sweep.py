"""
Experiment — adversarial noise budget (epsilon) sweep.

The complementary adversarial noise is a *secondary* defence: under a strong
random-dot mask it is marginal, but once the mask leaks (weak-mask scenario) it
has independent value. The single most-expected missing ablation for a method
that ships adversarial noise is the security/perceptibility trade-off as a
function of the L-inf budget epsilon. This experiment sweeps epsilon at a fixed
n and reports, per epsilon:

  - perceptual cost: CIEDE2000 ΔE, SSIM, temporal modulation (flicker proxy),
    plus the operating-point FPI (depends only on refresh and n);
  - strong-mask single-frame OCR (floor check, expected ~0);
  - weak-mask leakage OCR: mask-only vs mask+noise, and the resulting
    `noise_margin` = mask_only - mask_noise (how much the budget buys once the
    mask leaks).

epsilon=0 anchors the mask-only baseline (noise contributes nothing). The
weak-mask branch reuses ``component_ablation.leakage_stress`` verbatim so the
two ablations stay consistent.

Run:
    python experiments/noise_epsilon_sweep.py --max-samples 8
    python experiments/noise_epsilon_sweep.py --max-samples 120  # full corpus
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
from experiments.component_ablation import leakage_stress  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator  # noqa: E402
from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.evaluation.benchmark import _mean_std, compose_protected_subframes  # noqa: E402
from src.evaluation.metrics import compute_delta_e, compute_fpi, compute_ssim  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402

RESULT_FILE = "noise_epsilon_sweep.json"

# Span the budget from the deployed 8/255 down to 0 (mask-only anchor) and up to
# 96/255 — the weak-mask budget used by component_ablation — so the perceptual
# cost and the weak-mask noise margin are both visible across their useful range.
DEFAULT_EPSILONS = (0.0, 2 / 255, 4 / 255, 8 / 255, 16 / 255, 32 / 255, 64 / 255, 96 / 255)


def temporal_modulation(subframes: list[np.ndarray]) -> float:
    """Per-pixel temporal std across subframes, normalized to [0, 1] (flicker proxy)."""
    stack = np.stack([sf.astype(np.float32) for sf in subframes], axis=0)
    return float(np.mean(np.std(stack, axis=0)) / 255.0)


def _eps_key(epsilon: float) -> str:
    return f"eps_{epsilon:.4f}"


def run_epsilon_sweep(
    output_dir: str | Path = ROOT / "experiments" / "results",
    n: int = 4,
    epsilons: tuple[float, ...] = DEFAULT_EPSILONS,
    refresh_hz: float = 240.0,
    leak: float = 0.75,
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
    if not epsilons:
        raise ValueError("at least one epsilon is required")

    if corpus is None:
        images, truths, names = load_corpus()
        corpus_metadata = load_corpus_metadata()
    else:
        images, truths, names = corpus
        corpus_metadata = metadata or {}

    selected_indices, sample_policy = select_publication_subset(
        names,
        corpus_metadata,
        max_samples=max_samples,
        samples_per_category=samples_per_category,
    )
    images = take_indices(images, selected_indices)
    truths = take_indices(truths, selected_indices)
    ev = evaluator or OCREvaluator(engines=["tesseract"], timeout=ocr_timeout)
    composer = SubframeComposer(n=n, gamma=1.0)
    fpi = compute_fpi(refresh_hz, n)

    acc: dict[float, dict[str, list[float]]] = {
        eps: {k: [] for k in (
            "delta_e", "ssim", "temporal_mod",
            "single_frame_ocr", "weak_mask_only_ocr", "weak_mask_noise_ocr",
            "noise_margin",
        )}
        for eps in epsilons
    }

    total = len(images)
    for idx, (img, gt) in enumerate(zip(images, truths)):
        for eps in epsilons:
            with_noise = eps > 0
            sf = compose_protected_subframes(
                img, n=n, epsilon=eps, cycles=1, cycle_start=idx, with_noise=with_noise,
            )
            integrated = composer.integrate_subframes(
                sf, pedestal=eps * 255 if with_noise else 0.0,
            )
            acc[eps]["delta_e"].append(compute_delta_e(img, integrated))
            acc[eps]["ssim"].append(compute_ssim(img, integrated))
            acc[eps]["temporal_mod"].append(temporal_modulation(sf))
            acc[eps]["single_frame_ocr"].append(
                float(np.mean([ev.evaluate_single(s, gt, "tesseract").char_accuracy for s in sf]))
            )
            mask_only, mask_noise = leakage_stress(img, gt, ev, n, leak, eps)
            acc[eps]["weak_mask_only_ocr"].append(mask_only)
            acc[eps]["weak_mask_noise_ocr"].append(mask_noise)
            acc[eps]["noise_margin"].append(mask_only - mask_noise)
        if progress_interval and ((idx + 1) % progress_interval == 0 or idx + 1 == total):
            print(f"  epsilon-sweep sample {idx + 1}/{total}")

    summary = {}
    for eps in epsilons:
        entry = {"epsilon": float(eps)}
        entry.update({k: _mean_std(v) for k, v in acc[eps].items()})
        summary[_eps_key(eps)] = entry

    report = {
        "config": {
            "n": n,
            "epsilons": [float(e) for e in epsilons],
            "refresh_hz": refresh_hz,
            "fpi": fpi,
            "leak": leak,
            "n_samples": len(images),
            "sample_policy": sample_policy,
            "axes": {
                "usability": "delta_e/ssim/temporal_mod (lower delta_e/temporal_mod = better)",
                "security": "weak_mask_noise_ocr (lower = safer); noise_margin = mask_only - mask_noise",
            },
        },
        "summary": summary,
    }

    if save:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / RESULT_FILE
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n=== Noise budget (epsilon) sweep, n={n}, FPI={fpi:.4f} ===")
        print("|   eps   |  ΔE  | SSIM | temporal | 1-frame OCR | weak mask-only | weak mask+noise | margin |")
        print("|" + "---|" * 8)
        for eps in epsilons:
            s = summary[_eps_key(eps)]
            print(
                f"| {eps:.4f} | {s['delta_e']['mean']:.2f} | {s['ssim']['mean']:.3f} | "
                f"{s['temporal_mod']['mean']:.3f} | {s['single_frame_ocr']['mean'] * 100:.0f}% | "
                f"{s['weak_mask_only_ocr']['mean'] * 100:.0f}% | {s['weak_mask_noise_ocr']['mean'] * 100:.0f}% | "
                f"{s['noise_margin']['mean'] * 100:.0f}% |"
            )
        print(f"Saved: {out}")

    return report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Adversarial noise budget (epsilon) sweep")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilons", default=",".join(f"{e:.6f}" for e in DEFAULT_EPSILONS))
    p.add_argument("--refresh-hz", type=float, default=240.0)
    p.add_argument("--leak", type=float, default=0.75)
    p.add_argument("--max-samples", type=int, default=8)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--progress-interval", type=int, default=2)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    epsilons = tuple(float(x.strip()) for x in args.epsilons.split(",") if x.strip())
    run_epsilon_sweep(
        output_dir=args.output_dir,
        n=args.n,
        epsilons=epsilons,
        refresh_hz=args.refresh_hz,
        leak=args.leak,
        max_samples=args.max_samples,
        samples_per_category=args.samples_per_category,
        ocr_timeout=args.ocr_timeout,
        progress_interval=args.progress_interval,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
