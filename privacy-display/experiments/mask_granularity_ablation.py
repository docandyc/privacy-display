"""
Experiment — mask spatial-granularity ablation.

The deployed masks assign every pixel independently (block size b=1). This
ablation justifies that choice by coarsening the random assignment into b×b
blocks (b in {1, 2, 4, 8}) and measuring the usability/security trade-off:

  - usability: a spatially-pooled flicker proxy. The FPI model relies on a human
    receptive field averaging many independently-phased pixels (modulation falls
    ~1/sqrt(N)); coarser blocks defeat that pooling, so pooled flicker rises.
  - security: single-frame OCR and single-frame mutual information. Larger blocks
    leave larger contiguous readable regions in each subframe, so leakage rises.

Reconstruction is exact for any partition (ΣM_k = 1 still holds), so ΔE/SSIM
stay flat — the cost of coarser blocks is paid entirely in flicker and leakage,
which is why per-pixel assignment (b=1) is the deployed choice.

Run:
    python experiments/mask_granularity_ablation.py --max-samples 8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator  # noqa: E402
from src.core.mask_generator import MaskGenerator  # noqa: E402
from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.evaluation.benchmark import _mean_std  # noqa: E402
from src.evaluation.metrics import compute_delta_e, compute_entropy_ratio, compute_ssim  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402

RESULT_FILE = "mask_granularity_ablation.json"

ABLATION_KEY = b"mask-granularity-ablation-key-000"


def block_masks(shape: tuple[int, int], n: int, b: int, cycle: int, key: bytes) -> list[np.ndarray]:
    """Random slot assignment coarsened to b×b blocks (b=1 == per-pixel)."""
    if b <= 0:
        raise ValueError("block size must be positive")
    h, w = shape
    if b == 1:
        R = MaskGenerator(w, h, n, key=key)._generate_index_matrix(cycle)
    else:
        ch = (h + b - 1) // b
        cw = (w + b - 1) // b
        coarse = MaskGenerator(cw, ch, n, key=key)._generate_index_matrix(cycle)
        R = np.repeat(np.repeat(coarse, b, axis=0), b, axis=1)[:h, :w]
    return [(R == k) for k in range(n)]


def pooled_flicker(subframes: list[np.ndarray], pool: int = 25) -> float:
    """Temporal std of spatially-pooled luminance (receptive-field flicker proxy)."""
    pooled = [uniform_filter(np.mean(sf.astype(np.float64), axis=2), size=pool) for sf in subframes]
    stack = np.stack(pooled, axis=0)
    return float(np.mean(np.std(stack, axis=0)) / 255.0)


def build_block_subframes(img, n, b, cycle, key):
    masks = block_masks(img.shape[:2], n, b, cycle, key)
    composer = SubframeComposer(n=n, gamma=1.0)
    subframes = composer.compose(img, masks, None)
    integrated = composer.integrate_subframes(subframes, pedestal=0.0)
    return subframes, integrated


def _block_key(b: int) -> str:
    return f"block_{b}"


def run_granularity_ablation(
    output_dir: str | Path = ROOT / "experiments" / "results",
    n: int = 4,
    block_sizes: tuple[int, ...] = (1, 2, 4, 8),
    pool: int = 25,
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

    acc: dict[int, dict[str, list[float]]] = {
        b: {k: [] for k in ("single_frame_ocr", "entropy_ratio", "pooled_flicker", "delta_e", "ssim")}
        for b in block_sizes
    }

    total = len(images)
    for idx, (img, gt) in enumerate(zip(images, truths)):
        for b in block_sizes:
            subframes, integrated = build_block_subframes(img, n, b, idx, ABLATION_KEY)
            acc[b]["single_frame_ocr"].append(
                float(np.mean([ev.evaluate_single(s, gt, "tesseract").char_accuracy for s in subframes]))
            )
            acc[b]["entropy_ratio"].append(
                float(np.mean([compute_entropy_ratio(s, img) for s in subframes]))
            )
            acc[b]["pooled_flicker"].append(pooled_flicker(subframes, pool=pool))
            acc[b]["delta_e"].append(compute_delta_e(img, integrated))
            acc[b]["ssim"].append(compute_ssim(img, integrated))
        if progress_interval and ((idx + 1) % progress_interval == 0 or idx + 1 == total):
            print(f"  granularity sample {idx + 1}/{total}")

    summary = {}
    for b in block_sizes:
        entry = {"block_size": int(b)}
        entry.update({k: _mean_std(v) for k, v in acc[b].items()})
        summary[_block_key(b)] = entry

    report = {
        "config": {
            "n": n,
            "block_sizes": [int(b) for b in block_sizes],
            "pool": pool,
            "n_samples": len(images),
            "sample_policy": sample_policy,
            "note": "block_size=1 is the deployed per-pixel assignment.",
        },
        "summary": summary,
    }

    if save:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / RESULT_FILE
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n=== Mask granularity ablation, n={n} (pool={pool}) ===")
        print("| block | 1-frame OCR | 1-frame MI | pooled flicker |  ΔE  | SSIM |")
        print("|" + "---|" * 6)
        for b in block_sizes:
            s = summary[_block_key(b)]
            print(
                f"| {b}x{b} | {s['single_frame_ocr']['mean'] * 100:.0f}% | "
                f"{s['entropy_ratio']['mean']:.3f} | {s['pooled_flicker']['mean']:.4f} | "
                f"{s['delta_e']['mean']:.2f} | {s['ssim']['mean']:.3f} |"
            )
        print(f"Saved: {out}")

    return report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Mask spatial-granularity ablation")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--block-sizes", default="1,2,4,8")
    p.add_argument("--pool", type=int, default=25)
    p.add_argument("--max-samples", type=int, default=8)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--progress-interval", type=int, default=2)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    block_sizes = tuple(int(x.strip()) for x in args.block_sizes.split(",") if x.strip())
    run_granularity_ablation(
        output_dir=args.output_dir,
        n=args.n,
        block_sizes=block_sizes,
        pool=args.pool,
        max_samples=args.max_samples,
        samples_per_category=args.samples_per_category,
        ocr_timeout=args.ocr_timeout,
        progress_interval=args.progress_interval,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
