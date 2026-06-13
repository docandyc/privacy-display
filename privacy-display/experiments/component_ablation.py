"""
Experiment C — systematic per-component ablation.

Unifies the previously scattered findings (B1 noise ablation, B2/G5 inpaint +
pedestal, long-exposure inversion, black-frame AE) into a single table that
shows *which component is indispensable against which attack*:

  - random-dot mask:     the primary defence; drives single-frame OCR to the floor.
  - complementary noise: marginal under a strong mask, but decisive once the
                         mask leaks (weak-mask scenario).
  - noise pedestal:      indispensable against single-frame inpainting — without
                         it, inpaint refills the missing 1-1/n pixels.
  - inversion frame:     defeats long-exposure integration (drives it to grey).
  - black frame + AE:    pushes the camera auto-exposure to over-saturate real
                         subframes.

Run:
    python experiments/component_ablation.py --max-samples 16
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
from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.core.noise_injector import NoiseInjector  # noqa: E402
from src.attack.camera_simulator import CameraSimulator  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator  # noqa: E402
from src.evaluation.benchmark import _mean_std  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402

ABLATION_KEY = b"component-ablation-key-000000000"


def build_subframes(img, n, epsilon, cycle, *, with_noise, pedestal_on):
    """One cycle of subframes with explicit control over noise and pedestal."""
    h, w = img.shape[:2]
    gen = MaskGenerator(w, h, n, key=ABLATION_KEY)
    composer = SubframeComposer(n=n, gamma=1.0)
    masks = gen.generate(cycle)
    sub_noises = None
    if with_noise:
        injector = NoiseInjector(n=n, epsilon=epsilon)
        nb, _, _ = injector.generate_rotating_noise(img.astype(np.float32) / 255.0, cycle=cycle)
        ped = epsilon * 255 if pedestal_on else 0.0
        sub_noises = [(x * 255 + ped).astype(np.float32) for x in injector.split_complementary(nb)]
    return composer.compose(img, masks, sub_noises), composer


def inpaint_single(subframe: np.ndarray, missing_threshold: float = 1.0) -> np.ndarray:
    """Single-frame inpaint attack: refill pixels detected as 'missing' (dark)."""
    import cv2
    gray = subframe.mean(axis=2)
    mask = (gray < missing_threshold).astype(np.uint8) * 255
    if int(mask.sum()) == 0:
        return subframe.copy()
    return cv2.inpaint(np.ascontiguousarray(subframe), mask, 3, cv2.INPAINT_TELEA)


def leakage_stress(img, gt, ev, n, leak, epsilon):
    """Weak-mask scenario: inactive pixels still leak leak*I to the camera."""
    h, w = img.shape[:2]
    masks = MaskGenerator(w, h, n, key=ABLATION_KEY).generate(0)
    injector = NoiseInjector(n=n, epsilon=epsilon, target_models=["tesseract"])
    nb = injector.generate_fgsm_noise(img.astype(np.float32) / 255.0, "tesseract")
    sub_noises = [(x * 255).astype(np.float32) for x in injector.split_complementary(nb)]
    img_f = img.astype(np.float32)
    mask_only, mask_noise = [], []
    for k, mask in enumerate(masks):
        active = mask[:, :, None].astype(np.float32)
        inactive = (~mask)[:, :, None].astype(np.float32)
        leaked = img_f * (active + inactive * leak)
        mask_only.append(np.clip(leaked, 0, 255).astype(np.uint8))
        mask_noise.append(np.clip(leaked + sub_noises[k], 0, 255).astype(np.uint8))
    acc = lambda frames: float(np.mean([ev.evaluate_single(f, gt, "tesseract").char_accuracy for f in frames]))
    return acc(mask_only), acc(mask_noise)


def ocr_mean(ev, frames, gt):
    return float(np.mean([ev.evaluate_single(f, gt, "tesseract").char_accuracy for f in frames]))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Experiment C: component ablation")
    p.add_argument("--max-samples", type=int, default=16)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--leak", type=float, default=0.75)
    p.add_argument("--leak-epsilon", type=float, default=96 / 255)
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
    n, eps = args.n, args.epsilon

    # Accumulators per measured quantity.
    acc: dict[str, list[float]] = {k: [] for k in [
        "baseline", "single_mask_only", "single_mask_noise",
        "inpaint_mask_only", "inpaint_noise_pedestal", "inpaint_noise_no_pedestal",
        "long_exposure_no_inv", "long_exposure_with_inv",
        "ae_real_subframe_no_black", "ae_real_subframe_with_black",
        "weak_mask_only", "weak_mask_noise",
    ]}

    for idx, (img, gt) in enumerate(zip(images, truths)):
        acc["baseline"].append(ev.evaluate_single(img, gt, "tesseract").char_accuracy)

        sf_mask, composer = build_subframes(img, n, eps, idx, with_noise=False, pedestal_on=False)
        sf_ped, _ = build_subframes(img, n, eps, idx, with_noise=True, pedestal_on=True)
        sf_noped, _ = build_subframes(img, n, eps, idx, with_noise=True, pedestal_on=False)

        acc["single_mask_only"].append(ocr_mean(ev, sf_mask, gt))
        acc["single_mask_noise"].append(ocr_mean(ev, sf_ped, gt))

        acc["inpaint_mask_only"].append(ev.evaluate_single(inpaint_single(sf_mask[0]), gt, "tesseract").char_accuracy)
        acc["inpaint_noise_pedestal"].append(ev.evaluate_single(inpaint_single(sf_ped[0]), gt, "tesseract").char_accuracy)
        acc["inpaint_noise_no_pedestal"].append(ev.evaluate_single(inpaint_single(sf_noped[0]), gt, "tesseract").char_accuracy)

        inv_frames = [composer.compose_inversion_frame(s) for s in sf_ped]
        le_no = cam.long_exposure_attack(sf_ped, None, 4)
        le_inv = cam.long_exposure_attack(sf_ped, inv_frames, 4)
        acc["long_exposure_no_inv"].append(ev.evaluate_single(le_no, gt, "tesseract").char_accuracy)
        acc["long_exposure_with_inv"].append(ev.evaluate_single(le_inv, gt, "tesseract").char_accuracy)

        # Black-frame + AE: a black frame drives AE gain up, over-saturating real subframes.
        black = composer.compose_black_frame(sf_ped[0].shape)
        seq_no_black = list(sf_ped)
        seq_black = [black] + list(sf_ped)
        ae_no = cam.auto_exposure_attack(seq_no_black)
        ae_black = cam.auto_exposure_attack(seq_black)
        acc["ae_real_subframe_no_black"].append(ocr_mean(ev, ae_no, gt))
        acc["ae_real_subframe_with_black"].append(ocr_mean(ev, ae_black[1:], gt))  # skip the black frame itself

        wm, wmn = leakage_stress(img, gt, ev, n, args.leak, args.leak_epsilon)
        acc["weak_mask_only"].append(wm)
        acc["weak_mask_noise"].append(wmn)

        if (idx + 1) % 4 == 0 or idx + 1 == len(images):
            print(f"  ablation sample {idx + 1}/{len(images)}")

    summary = {k: _mean_std(v) for k, v in acc.items()}
    report = {
        "config": {"n": n, "epsilon": eps, "n_samples": len(images),
                   "leak": args.leak, "leak_epsilon": args.leak_epsilon,
                   "sample_policy": sample_policy},
        "summary": summary,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "component_ablation.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    def pct(k):
        return f"{summary[k]['mean'] * 100:5.1f}% ± {summary[k]['std'] * 100:.1f}"

    print("\n=== Component ablation (single-frame char recovery, n=%d) ===" % n)
    print(f"  baseline (original)              : {pct('baseline')}")
    print(f"  mask only                        : {pct('single_mask_only')}")
    print(f"  mask + complementary noise       : {pct('single_mask_noise')}")
    print("--- single-frame inpaint attack ---")
    print(f"  inpaint @ mask-only (no pedestal): {pct('inpaint_mask_only')}   <- inpaint refills missing pixels")
    print(f"  inpaint @ noise, pedestal ON     : {pct('inpaint_noise_pedestal')}   <- pedestal defeats inpaint")
    print(f"  inpaint @ noise, pedestal OFF    : {pct('inpaint_noise_no_pedestal')}")
    print("--- long exposure ---")
    print(f"  long exposure, no inversion      : {pct('long_exposure_no_inv')}")
    print(f"  long exposure, with inversion    : {pct('long_exposure_with_inv')}   <- inversion -> grey")
    print("--- black frame + auto-exposure ---")
    print(f"  AE on real subframes, no black   : {pct('ae_real_subframe_no_black')}")
    print(f"  AE on real subframes, with black : {pct('ae_real_subframe_with_black')}")
    print("--- weak-mask leakage stress (leak=%.2f, eps=%.3f) ---" % (args.leak, args.leak_epsilon))
    print(f"  weak mask only                   : {pct('weak_mask_only')}")
    print(f"  weak mask + OCR-target noise     : {pct('weak_mask_noise')}   <- noise margin appears here")
    print(f"\nSaved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
