"""
Experiment — deployed anti-OCR overlay + partial-inversion ablation.

Every other experiment in ``experiments/`` measures the *core* mask+noise scheme
(exact reconstruction, ΣM_k=1). None of them evaluate the layer that the demo /
webstudy actually deploys on top of it:

  - the anti-OCR overlay (per-subframe stripe aliasing + glyph hole-punch / fake
    strokes), tuned by the user to ``stripe_alpha=0.10`` / ``glyph_alpha=0.12``;
  - the partial inversion frame ``α·(255−I)`` (long-exposure defence), tuned to
    ``α=0.2``.

This overlay deliberately breaks exact reconstruction, so the ΔE≈0 / SSIM≈1
numbers from the core experiments do not describe it, and the security side
under-counts the extra suppression. This experiment fills that gap.

Faithfulness: subframes are produced by the *deployment code itself*
(``build_playback_frames``), so we measure exactly what ships. Inversion frames
are composed directly (``compose_partial_inversion_frame`` / ``compose_inversion_frame``)
so the α sweep can include α=0 (off) and α=1 (full) without tripping the
playback's [0.2,0.5] validation.

Three blocks (security headline = exact-match recovery, per memory; char-accuracy
kept as a secondary signal):

  Block 1  profile: off / strong@deployed (0.10·0.12) / vlm — single-frame,
           temporal-average, strongest screen-camera attack; readability drift +
           ΔE + SSIM (overlay perceptual cost).
  Block 2  stripe_alpha × glyph_alpha grid (profile=strong) — temporal-average
           recovery vs readability drift; locates the 0.10/0.12 operating point.
  Block 3  inversion α∈{0, 0.2, 0.3, 0.5, 1.0} (profile=strong@deployed) —
           long-exposure recovery (defence) vs readability drift (cost);
           justifies α=0.2.

Optional Block V (``--vlm`` + ``SILICONFLOW_API_KEY``): VLM exact-match on
off vs strong@deployed (the hardest attacker). Skipped without a key.

Run:
    python experiments/anti_ocr_profile_ablation.py --max-samples 16
    python experiments/anti_ocr_profile_ablation.py --max-samples 4   # smoke
    python experiments/anti_ocr_profile_ablation.py --max-samples 8 --vlm
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.camera_simulator import CameraSimulator  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator, text_recovery_metrics  # noqa: E402
from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.demo.playback_demo import build_playback_frames, extract_text_saliency_mask  # noqa: E402
from src.evaluation.benchmark import _mean_std  # noqa: E402
from src.evaluation.metrics import compute_delta_e, compute_ssim  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402


ABLATION_KEY = b"anti-ocr-profile-ablation-key-00"

# Block 1 profiles. ``stripe``/``glyph`` are overrides (None → profile default);
# strong@deployed pins the user's measured operating point.
PROFILE_CONDITIONS = [
    ("off", None, None),
    ("strong@deployed", 0.10, 0.12),
    ("vlm", None, None),
]

# Block 2 grid (profile=strong). Includes the deployed (0.10, 0.12) cell and the
# zero anchors that strip each artefact independently.
GRID_STRIPE = (0.0, 0.10, 0.18, 0.30)
GRID_GLYPH = (0.0, 0.12, 0.22)

# Block 3 inversion amplitudes. 0.0=off, 1.0=full (reference); 0.2 is deployed.
INVERSION_ALPHAS = (0.0, 0.2, 0.3, 0.5, 1.0)


# ----------------------------------------------------------------------
# Frame source + metric helpers
# ----------------------------------------------------------------------


def build_subframes(img, *, n, cycles, epsilon, profile, stripe_alpha, glyph_alpha):
    """Deployment-faithful subframes (anti-OCR overlay baked in when profile≠off).

    Inversion is handled separately so the α sweep can leave [0.2,0.5].
    Returns (all_subframes [n*cycles], pedestal).
    """
    frames, meta = build_playback_frames(
        img,
        n=n,
        cycles=cycles,
        epsilon=epsilon,
        insert_inversion=False,
        anti_ocr_profile=profile,
        stripe_alpha=stripe_alpha,
        glyph_alpha=glyph_alpha,
        key=ABLATION_KEY,
    )
    subframes = [f for f, kind in frames if kind == "subframe"]
    return subframes, float(meta["pedestal"])


def inversion_frame_for(composer, img, alpha):
    """α=0 → None; 0<α<1 → partial; α≥1 → full inverse (255−I)."""
    if alpha <= 0.0:
        return None
    if alpha >= 1.0:
        return composer.compose_inversion_frame(img)
    return composer.compose_partial_inversion_frame(img, alpha)


def readability_drift(composer, cycle_subframes, inv_frame, pedestal, img, saliency):
    """Human-perceived integration drift on text pixels (lower = more readable)."""
    frames = list(cycle_subframes)
    if inv_frame is not None:
        frames = frames + [inv_frame]
    integrated = composer.integrate_subframes(frames, pedestal=pedestal)
    diff = np.abs(integrated.astype(np.int16) - img.astype(np.int16))
    return float(diff[saliency].mean()), integrated


def ocr_recovery(ev, frame, gt):
    """(exact_match∈{0,1}, char_accuracy) for one attacked frame."""
    res = ev.evaluate_single(frame, gt, "tesseract")
    rec = text_recovery_metrics(res.text, gt)
    return float(rec["exact_match"]), float(res.char_accuracy)


def strongest_screen_camera(ev, cam, subframes, n, gt):
    """Max recovery over the screen-camera attack suite (the strongest attacker)."""
    suite = cam.screen_camera_attack_suite(subframes, cycle_length=n)
    best_exact, best_char = 0.0, 0.0
    for entry in suite.values():
        em, ca = ocr_recovery(ev, entry["frame"], gt)
        best_exact = max(best_exact, em)
        best_char = max(best_char, ca)
    return best_exact, best_char


# ----------------------------------------------------------------------
# Blocks
# ----------------------------------------------------------------------


def run_block1_profile(acc, *, ev, cam, composer, img, gt, saliency, n, cycles, eps):
    for label, s_alpha, g_alpha in PROFILE_CONDITIONS:
        profile = "off" if label == "off" else ("vlm" if label == "vlm" else "strong")
        subframes, pedestal = build_subframes(
            img, n=n, cycles=cycles, epsilon=eps,
            profile=profile, stripe_alpha=s_alpha, glyph_alpha=g_alpha,
        )
        one_cycle = subframes[:n]

        sf_exact, sf_char = ocr_recovery(ev, one_cycle[0], gt)
        ta = cam.temporal_averaging_attack(subframes, k=n, randomize_order=False)
        ta_exact, ta_char = ocr_recovery(ev, ta, gt)
        cam_exact, cam_char = strongest_screen_camera(ev, cam, subframes, n, gt)

        drift, integrated = readability_drift(
            composer, one_cycle, None, pedestal, img, saliency
        )
        delta_e = compute_delta_e(img, integrated)
        ssim = compute_ssim(img, integrated)

        acc[f"block1/{label}"]["single_frame_exact"].append(sf_exact)
        acc[f"block1/{label}"]["single_frame_char"].append(sf_char)
        acc[f"block1/{label}"]["temporal_avg_exact"].append(ta_exact)
        acc[f"block1/{label}"]["temporal_avg_char"].append(ta_char)
        acc[f"block1/{label}"]["strong_camera_exact"].append(cam_exact)
        acc[f"block1/{label}"]["strong_camera_char"].append(cam_char)
        acc[f"block1/{label}"]["readability_drift"].append(drift)
        acc[f"block1/{label}"]["delta_e"].append(delta_e)
        acc[f"block1/{label}"]["ssim"].append(ssim)


def run_block2_grid(acc, *, ev, cam, composer, img, gt, saliency, n, cycles, eps):
    for s_alpha in GRID_STRIPE:
        for g_alpha in GRID_GLYPH:
            subframes, pedestal = build_subframes(
                img, n=n, cycles=cycles, epsilon=eps,
                profile="strong", stripe_alpha=s_alpha, glyph_alpha=g_alpha,
            )
            one_cycle = subframes[:n]
            ta = cam.temporal_averaging_attack(subframes, k=n, randomize_order=False)
            ta_exact, ta_char = ocr_recovery(ev, ta, gt)
            drift, _ = readability_drift(composer, one_cycle, None, pedestal, img, saliency)

            cell = f"block2/s{s_alpha:.2f}_g{g_alpha:.2f}"
            acc[cell]["temporal_avg_exact"].append(ta_exact)
            acc[cell]["temporal_avg_char"].append(ta_char)
            acc[cell]["readability_drift"].append(drift)


def run_block3_inversion(acc, *, ev, cam, composer, img, gt, saliency, n, cycles, eps):
    # Strong@deployed subframes are identical across α (inversion is a separate frame).
    subframes, pedestal = build_subframes(
        img, n=n, cycles=cycles, epsilon=eps,
        profile="strong", stripe_alpha=0.10, glyph_alpha=0.12,
    )
    one_cycle = subframes[:n]
    for alpha in INVERSION_ALPHAS:
        inv = inversion_frame_for(composer, img, alpha)
        inv_frames = [inv] if inv is not None else None
        le = cam.long_exposure_attack(one_cycle, inv_frames, n_cycles=4)
        le_exact, le_char = ocr_recovery(ev, le, gt)
        drift, _ = readability_drift(composer, one_cycle, inv, pedestal, img, saliency)

        key = f"block3/alpha_{alpha:.1f}"
        acc[key]["long_exposure_exact"].append(le_exact)
        acc[key]["long_exposure_char"].append(le_char)
        acc[key]["readability_drift"].append(drift)


def run_block_vlm(acc, *, client, cam, img, gt, n, cycles, eps):
    """Optional: VLM exact-match on the strongest attacker frame, off vs strong."""
    for label, s_alpha, g_alpha in (("off", None, None), ("strong@deployed", 0.10, 0.12)):
        profile = "off" if label == "off" else "strong"
        subframes, _ = build_subframes(
            img, n=n, cycles=cycles, epsilon=eps,
            profile=profile, stripe_alpha=s_alpha, glyph_alpha=g_alpha,
        )
        ta = cam.temporal_averaging_attack(subframes, k=n, randomize_order=False)
        try:
            result = client.analyze_image(ta, ground_truth=gt)
            visible = str(result.get("visible_text", "") or "")
            rec = result.get("metrics") or text_recovery_metrics(visible, gt)
        except Exception:
            rec = text_recovery_metrics("", gt)
        acc[f"vlm/{label}"]["temporal_avg_exact"].append(float(rec["exact_match"]))
        acc[f"vlm/{label}"]["temporal_avg_char"].append(float(rec["char_accuracy"]))


# ----------------------------------------------------------------------
# Aggregation + driver
# ----------------------------------------------------------------------


def summarize(acc):
    """Per-condition {metric: mean_std}. Block prefix kept in the key."""
    return {cond: {m: _mean_std(v) for m, v in metrics.items()}
            for cond, metrics in acc.items()}


def headline_summary(detail):
    """Flat ``summary`` for publication_summary auto-pickup.

    Security headline char-accuracy per condition (lower = safer): strongest
    attacker for profiles, temporal-average for the grid, long-exposure for α.
    """
    summary = {}
    for cond, metrics in detail.items():
        if "strong_camera_char" in metrics:
            summary[cond] = {"char_accuracy": metrics["strong_camera_char"]}
        elif "long_exposure_char" in metrics:
            summary[cond] = {"char_accuracy": metrics["long_exposure_char"]}
        elif "temporal_avg_char" in metrics:
            summary[cond] = {"char_accuracy": metrics["temporal_avg_char"]}
    return summary


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Anti-OCR overlay + inversion ablation")
    p.add_argument("--max-samples", type=int, default=16)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--cycles", type=int, default=4,
                   help="Mask/noise/stripe realisations for multi-cycle attacks.")
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--vlm", action="store_true",
                   help="Run the optional VLM block (needs SILICONFLOW_API_KEY).")
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    images, truths, names = load_corpus()
    metadata = load_corpus_metadata()
    selected, sample_policy = select_publication_subset(
        names, metadata,
        max_samples=args.max_samples,
        samples_per_category=args.samples_per_category,
    )
    images = take_indices(images, selected)
    truths = take_indices(truths, selected)
    names = take_indices(names, selected)

    n, cycles, eps = args.n, args.cycles, args.epsilon
    ev = OCREvaluator(engines=["tesseract"], timeout=args.ocr_timeout)
    cam = CameraSimulator()
    composer = SubframeComposer(n=n, gamma=1.0)

    vlm_client = None
    if args.vlm:
        if not os.environ.get("SILICONFLOW_API_KEY"):
            print("[vlm] SILICONFLOW_API_KEY missing; skipping VLM block.", flush=True)
        else:
            from src.attack.vlm_evaluator import (  # noqa: E402
                DEFAULT_SILICONFLOW_BASE_URL, DEFAULT_VLM_MODEL, VLMClient,
            )
            vlm_client = VLMClient(
                model=DEFAULT_VLM_MODEL, base_url=DEFAULT_SILICONFLOW_BASE_URL, timeout=60.0,
            )

    acc = defaultdict(lambda: defaultdict(list))
    for idx, (img, gt) in enumerate(zip(images, truths)):
        saliency = extract_text_saliency_mask(img)
        common = dict(ev=ev, cam=cam, composer=composer, img=img, gt=gt,
                      saliency=saliency, n=n, cycles=cycles, eps=eps)
        run_block1_profile(acc, **common)
        run_block2_grid(acc, **common)
        run_block3_inversion(acc, **common)
        if vlm_client is not None:
            run_block_vlm(acc, client=vlm_client, cam=cam, img=img, gt=gt,
                          n=n, cycles=cycles, eps=eps)
        print(f"  sample {idx + 1}/{len(images)}: {names[idx]}", flush=True)

    detail = summarize(acc)
    report = {
        "config": {
            "n": n, "epsilon": eps, "cycles": cycles,
            "n_samples": len(images), "sample_policy": sample_policy,
            "profiles": [c[0] for c in PROFILE_CONDITIONS],
            "grid_stripe": list(GRID_STRIPE), "grid_glyph": list(GRID_GLYPH),
            "inversion_alphas": list(INVERSION_ALPHAS),
            "deployed": {"profile": "strong", "stripe_alpha": 0.10,
                         "glyph_alpha": 0.12, "inversion_alpha": 0.2},
            "vlm": vlm_client is not None,
        },
        "summary": headline_summary(detail),
        "detail": detail,
    }

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "anti_ocr_profile_ablation.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    def m(cond, metric):
        return detail.get(cond, {}).get(metric, {}).get("mean", float("nan"))

    print(f"\nSaved {out}")
    print("--- Block 1: profile (strongest-camera exact | temporal char | readability) ---")
    for label, _, _ in PROFILE_CONDITIONS:
        c = f"block1/{label}"
        print(f"  {label:16s} cam_exact={m(c, 'strong_camera_exact'):.3f}  "
              f"temporal_char={m(c, 'temporal_avg_char'):.3f}  "
              f"drift={m(c, 'readability_drift'):.2f}  "
              f"ΔE={m(c, 'delta_e'):.2f}  SSIM={m(c, 'ssim'):.3f}")
    print("--- Block 3: inversion α (long-exposure char=defence | readability drift=cost) ---")
    for alpha in INVERSION_ALPHAS:
        c = f"block3/alpha_{alpha:.1f}"
        print(f"  α={alpha:.1f}  long_exp_char={m(c, 'long_exposure_char'):.3f}  "
              f"(exact={m(c, 'long_exposure_exact'):.3f})  "
              f"drift={m(c, 'readability_drift'):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
