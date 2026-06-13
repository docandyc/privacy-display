"""
Experiment D — perceptual color-space / channel ablation.

Answers the reviewer question "why a full RGB random-dot mask instead of a
perceptually motivated modulation (e.g. keep the low-salience blue channel to
reduce flicker)?". For each variant we report three groups:

  - usability:    CIEDE2000 ΔE and SSIM of the integrated frame vs original,
                  plus a temporal-modulation proxy (lower = less flicker).
  - defense:      single-subframe char recovery (lower = stronger).
  - side-channel: blue-channel recovery via differential accumulation and
                  mean stacking (DeepLight/Revelio-style probes).

The expectation: keeping a channel constant across subframes lowers flicker but
opens a recoverable colour side-channel and/or regresses defense — which is why
the deployed design masks all channels (rgb_full).

Run:
    python experiments/perceptual_ablation.py --max-samples 12
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
from src.core.mask_generator import MaskGenerator  # noqa: E402
from src.attack.camera_simulator import CameraSimulator  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator  # noqa: E402
from src.evaluation.benchmark import _mean_std  # noqa: E402
from src.evaluation.metrics import compute_delta_e, compute_ssim  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402

PERC_KEY = b"perceptual-ablation-key-00000000"
VARIANTS = ["rgb_full", "blue_residual_0.5", "blue_kept", "green_kept"]


def build_variant(img: np.ndarray, masks, variant: str) -> list[np.ndarray]:
    """Construct n subframes for a color-space variant (all start from random-dot)."""
    imgf = img.astype(np.float32)
    out = []
    for mask in masks:
        m = mask[:, :, None].astype(np.float32)
        sf = imgf * m  # base random-dot: inactive pixels = 0 in all channels
        if variant == "rgb_full":
            pass
        elif variant == "blue_residual_0.5":
            sf[..., 2] = np.where(mask, imgf[..., 2], 0.5 * imgf[..., 2])
        elif variant == "blue_kept":
            sf[..., 2] = imgf[..., 2]   # blue never masked
        elif variant == "green_kept":
            sf[..., 1] = imgf[..., 1]   # green (luma-heavy) never masked — control
        else:
            raise ValueError(variant)
        out.append(np.clip(sf, 0, 255).astype(np.uint8))
    return out


def integrate(subframes: list[np.ndarray], n: int) -> np.ndarray:
    """Eye integration model: mean over subframes restored by the n× display boost."""
    acc = np.zeros_like(subframes[0], dtype=np.float32)
    for sf in subframes:
        acc += sf.astype(np.float32)
    return np.clip(acc / len(subframes) * n, 0, 255).astype(np.uint8)


def temporal_modulation(subframes: list[np.ndarray]) -> float:
    """Per-pixel luminance std across subframes, normalized — a flicker proxy."""
    lum = np.stack([
        0.2126 * s[..., 0] + 0.7152 * s[..., 1] + 0.0722 * s[..., 2]
        for s in subframes
    ], axis=0).astype(np.float32)
    std = lum.std(axis=0)
    mean = lum.mean(axis=0) + 1e-3
    return float(np.mean(std / mean))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Experiment D: perceptual channel ablation")
    p.add_argument("--max-samples", type=int, default=12)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
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
    ev = OCREvaluator(engines=["tesseract"], timeout=args.ocr_timeout)
    cam = CameraSimulator()
    n = args.n

    acc: dict[str, dict[str, list[float]]] = {
        v: {k: [] for k in ["delta_e", "ssim", "temporal_modulation",
                            "single_frame_ocr", "blue_diff_ocr", "single_frame_blue_ocr"]}
        for v in VARIANTS
    }

    for idx, (img, gt) in enumerate(zip(images, truths)):
        h, w = img.shape[:2]
        masks = MaskGenerator(w, h, n, key=PERC_KEY).generate(idx)
        for variant in VARIANTS:
            sf = build_variant(img, masks, variant)
            integrated = integrate(sf, n)
            acc[variant]["delta_e"].append(compute_delta_e(img, integrated))
            acc[variant]["ssim"].append(compute_ssim(img, integrated))
            acc[variant]["temporal_modulation"].append(temporal_modulation(sf))
            acc[variant]["single_frame_ocr"].append(
                ev.evaluate_single(sf[0], gt, "tesseract").char_accuracy)
            # Side-channel probes. Differential accumulation is a genuine
            # inter-frame side-channel; the single-frame blue plane shows whether
            # one captured frame's blue channel alone already reveals the text
            # (the real risk of keeping a channel constant). Note: full-cycle blue
            # *mean* recovery is omitted here — it equals temporal averaging and
            # belongs to the boundary analysis, not a colour side-channel.
            diff_frame, _ = cam.weighted_differential_accumulator_attack(sf, channel="blue")
            acc[variant]["blue_diff_ocr"].append(
                ev.evaluate_single(diff_frame, gt, "tesseract").char_accuracy)
            blue_plane = np.repeat(sf[0][..., 2:3], 3, axis=2)
            acc[variant]["single_frame_blue_ocr"].append(
                ev.evaluate_single(blue_plane, gt, "tesseract").char_accuracy)
        if (idx + 1) % 4 == 0 or idx + 1 == len(images):
            print(f"  perceptual sample {idx + 1}/{len(images)}")

    summary = {v: {k: _mean_std(vals) for k, vals in groups.items()} for v, groups in acc.items()}
    report = {
        "config": {
            "n": n,
            "n_samples": len(images),
            "variants": VARIANTS,
            "sample_policy": sample_policy,
        },
        "summary": summary,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "perceptual_ablation.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== Perceptual channel ablation (n=%d) ===" % n)
    print("| variant | ΔE2000 | SSIM | flicker | 1-frame OCR | blue-diff OCR | 1-frame blue OCR |")
    print("|" + "---|" * 7)
    for v in VARIANTS:
        s = summary[v]
        print(f"| {v} | {s['delta_e']['mean']:.2f} | {s['ssim']['mean']:.3f} | "
              f"{s['temporal_modulation']['mean']:.3f} | "
              f"{s['single_frame_ocr']['mean'] * 100:.1f}% | "
              f"{s['blue_diff_ocr']['mean'] * 100:.1f}% | "
              f"{s['single_frame_blue_ocr']['mean'] * 100:.1f}% |")
    print(f"\nSaved: {out}")
    print("Read: rgb_full should hold defense + blue side-channel near 0; keeping a "
          "channel lowers flicker but raises blue recovery / regresses defense.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
