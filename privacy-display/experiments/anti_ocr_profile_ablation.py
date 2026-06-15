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

  Block 1  profile: off / strong@overlay (0.10·0.12) /
           strong@deployed (0.10·0.12 + α=0.2) / vlm — single-frame,
           temporal-average, screen-camera-suite best, and best-observed
           measured attack; readability drift + ΔE + SSIM.
  Block 2  stripe_alpha × glyph_alpha grid (profile=strong) — temporal-average
           recovery vs readability drift; locates the 0.10/0.12 operating point.
  Block 3  inversion α∈{0, 0.2, 0.3, 0.5, 1.0} (profile=strong@deployed) —
           long-exposure recovery (defence) vs readability drift (cost);
           justifies α=0.2.

Optional Block V (``--vlm`` + ``SILICONFLOW_API_KEY``): VLM recovery on
off vs strong@deployed temporal averages. Skipped without a key; failed calls
are counted and not converted into zero-recovery evidence.

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
RNG_SEED = 20260615

DEPLOYED_STRIPE_ALPHA = 0.10
DEPLOYED_GLYPH_ALPHA = 0.12
DEPLOYED_INVERSION_ALPHA = 0.2

# Block 1 profiles. ``stripe``/``glyph`` are overrides (None → profile default).
# ``strong@overlay`` is the anti-OCR layer alone; ``strong@deployed`` is the
# actual shipped playback stream (overlay + weak inversion frame).
PROFILE_CONDITIONS = [
    ("off", "off", None, None, None),
    ("strong@overlay", "strong", DEPLOYED_STRIPE_ALPHA, DEPLOYED_GLYPH_ALPHA, None),
    (
        "strong@deployed",
        "strong",
        DEPLOYED_STRIPE_ALPHA,
        DEPLOYED_GLYPH_ALPHA,
        DEPLOYED_INVERSION_ALPHA,
    ),
    ("vlm", "vlm", None, None, None),
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


def build_frame_sequence(
    img,
    *,
    n,
    cycles,
    epsilon,
    profile,
    stripe_alpha,
    glyph_alpha,
    inversion_alpha=None,
):
    """Return deployment-ordered frames plus separated subframes and metadata."""
    frames, meta = build_playback_frames(
        img,
        n=n,
        cycles=cycles,
        epsilon=epsilon,
        insert_inversion=inversion_alpha is not None,
        inversion_alpha=(
            DEPLOYED_INVERSION_ALPHA
            if inversion_alpha is None
            else inversion_alpha
        ),
        anti_ocr_profile=profile,
        stripe_alpha=stripe_alpha,
        glyph_alpha=glyph_alpha,
        key=ABLATION_KEY,
    )
    sequence = [f for f, _ in frames]
    subframes = [f for f, kind in frames if kind == "subframe"]
    return sequence, subframes, float(meta["pedestal"]), meta


def inversion_frame_for(composer, img, alpha):
    """α=0 → None; 0<α<1 → partial; α≥1 → full inverse (255−I)."""
    if alpha <= 0.0:
        return None
    if alpha >= 1.0:
        return composer.compose_inversion_frame(img)
    return composer.compose_partial_inversion_frame(img, alpha)


def frame_sequence_with_inversion(subframes, n, inv_frame):
    """Interleave one optional inversion frame after every n-subframe cycle."""
    sequence = []
    for start in range(0, len(subframes), n):
        cycle = subframes[start:start + n]
        if len(cycle) != n:
            raise ValueError("subframes length must be a multiple of n")
        sequence.extend(cycle)
        if inv_frame is not None:
            sequence.append(inv_frame)
    return sequence


def average_frame_sequence(frames):
    """Long-exposure / full-sequence integration without reusing only cycle 0."""
    if not frames:
        raise ValueError("frames must not be empty")
    stacked = np.mean([f.astype(np.float64) for f in frames], axis=0)
    return stacked.clip(0, 255).astype(np.uint8)


def brightness_aligned_boost(composer, frame_count):
    """Use the actually displayed slot count when integrating readability frames."""
    if composer.hdr_mode:
        return None
    return frame_count / composer.gamma


def contrast_stretch(frame, low=1.0, high=99.0):
    """Per-channel percentile stretch for low-contrast recovered attack frames."""
    arr = frame.astype(np.float32)
    lo = np.percentile(arr, low, axis=(0, 1), keepdims=True)
    hi = np.percentile(arr, high, axis=(0, 1), keepdims=True)
    span = hi - lo
    scale = np.where(span > 1e-6, 255.0 / span, 1.0)
    return np.clip((arr - lo) * scale, 0, 255).astype(np.uint8)


def inversion_frame_recovery_attack(inv_frame):
    """Natural attack on α·(255-I): invert the frame, then stretch contrast."""
    inverted = 255 - inv_frame.astype(np.uint8)
    return contrast_stretch(inverted)


def readability_drift(composer, cycle_subframes, inv_frame, pedestal, img, saliency):
    """Human-perceived integration drift on text pixels (lower = more readable).

    When a weak inversion slot is appended, the deployed cycle has n+1 displayed
    slots. For perceptual cost we brightness-align that cycle by using
    boost=per_cycle_slots/gamma instead of the composer default n/gamma; otherwise
    ΔE is dominated by a global dimming artefact rather than the overlay/inversion
    distortion itself.
    """
    frames = list(cycle_subframes)
    if inv_frame is not None:
        frames = frames + [inv_frame]
    boost = brightness_aligned_boost(composer, len(frames))
    effective_pedestal = pedestal * (len(cycle_subframes) / len(frames))
    integrated = composer.integrate_subframes(
        frames,
        boost=boost,
        pedestal=effective_pedestal,
    )
    diff = np.abs(integrated.astype(np.int16) - img.astype(np.int16))
    return float(diff[saliency].mean()), integrated


def ocr_recovery(ev, frame, gt):
    """(exact_match∈{0,1}, char_accuracy) for one attacked frame."""
    res = ev.evaluate_single(frame, gt, "tesseract")
    rec = text_recovery_metrics(res.text, gt)
    return float(rec["exact_match"]), float(res.char_accuracy)


def screen_camera_suite_best(ev, cam, frame_sequence, cycle_length, gt):
    """Max recovery over the screen-camera suite only."""
    suite = cam.screen_camera_attack_suite(frame_sequence, cycle_length=cycle_length)
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
    for label, profile, s_alpha, g_alpha, inv_alpha in PROFILE_CONDITIONS:
        sequence, subframes, pedestal, meta = build_frame_sequence(
            img, n=n, cycles=cycles, epsilon=eps,
            profile=profile, stripe_alpha=s_alpha, glyph_alpha=g_alpha,
            inversion_alpha=inv_alpha,
        )
        per_cycle_slots = int(meta["per_cycle_slots"])
        one_cycle_subframes = subframes[:n]
        one_cycle_sequence = sequence[:per_cycle_slots]
        one_cycle_inv = (
            one_cycle_sequence[-1]
            if meta["insert_inversion"]
            else None
        )

        sf_exact, sf_char = ocr_recovery(ev, one_cycle_subframes[0], gt)
        ta = cam.temporal_averaging_attack(
            one_cycle_sequence,
            k=per_cycle_slots,
            randomize_order=False,
        )
        ta_exact, ta_char = ocr_recovery(ev, ta, gt)
        suite_exact, suite_char = screen_camera_suite_best(
            ev, cam, sequence, per_cycle_slots, gt
        )
        if one_cycle_inv is None:
            inv_exact, inv_char = 0.0, 0.0
        else:
            inv_attack = inversion_frame_recovery_attack(one_cycle_inv)
            inv_exact, inv_char = ocr_recovery(ev, inv_attack, gt)
        best_exact = max(sf_exact, ta_exact, suite_exact, inv_exact)
        best_char = max(sf_char, ta_char, suite_char, inv_char)

        drift, integrated = readability_drift(
            composer, one_cycle_subframes, one_cycle_inv, pedestal, img, saliency
        )
        delta_e = compute_delta_e(img, integrated)
        ssim = compute_ssim(img, integrated)

        acc[f"block1/{label}"]["single_frame_exact"].append(sf_exact)
        acc[f"block1/{label}"]["single_frame_char"].append(sf_char)
        acc[f"block1/{label}"]["temporal_avg_exact"].append(ta_exact)
        acc[f"block1/{label}"]["temporal_avg_char"].append(ta_char)
        acc[f"block1/{label}"]["screen_camera_suite_exact"].append(suite_exact)
        acc[f"block1/{label}"]["screen_camera_suite_char"].append(suite_char)
        acc[f"block1/{label}"]["inversion_frame_attack_exact"].append(inv_exact)
        acc[f"block1/{label}"]["inversion_frame_attack_char"].append(inv_char)
        acc[f"block1/{label}"]["best_observed_exact"].append(best_exact)
        acc[f"block1/{label}"]["best_observed_char"].append(best_char)
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
        profile="strong",
        stripe_alpha=DEPLOYED_STRIPE_ALPHA,
        glyph_alpha=DEPLOYED_GLYPH_ALPHA,
    )
    one_cycle = subframes[:n]
    for alpha in INVERSION_ALPHAS:
        inv = inversion_frame_for(composer, img, alpha)
        playback_sequence = frame_sequence_with_inversion(subframes, n, inv)
        le = average_frame_sequence(playback_sequence)
        le_exact, le_char = ocr_recovery(ev, le, gt)
        if inv is None:
            inv_exact, inv_char = 0.0, 0.0
        else:
            inv_attack = inversion_frame_recovery_attack(inv)
            inv_exact, inv_char = ocr_recovery(ev, inv_attack, gt)
        drift, _ = readability_drift(composer, one_cycle, inv, pedestal, img, saliency)

        key = f"block3/alpha_{alpha:.1f}"
        acc[key]["long_exposure_exact"].append(le_exact)
        acc[key]["long_exposure_char"].append(le_char)
        acc[key]["inversion_frame_attack_exact"].append(inv_exact)
        acc[key]["inversion_frame_attack_char"].append(inv_char)
        acc[key]["readability_drift"].append(drift)


def run_block_vlm(acc, *, client, cam, img, gt, n, cycles, eps):
    """Optional: VLM recovery on temporal averages, with explicit error counts."""
    for label, s_alpha, g_alpha in (
        ("off", None, None),
        ("strong@deployed", DEPLOYED_STRIPE_ALPHA, DEPLOYED_GLYPH_ALPHA),
    ):
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
            acc[f"vlm/{label}"]["call_success"].append(0.0)
            acc[f"vlm/{label}"]["error_count"].append(1.0)
            continue
        acc[f"vlm/{label}"]["temporal_avg_exact"].append(float(rec["exact_match"]))
        acc[f"vlm/{label}"]["temporal_avg_char"].append(float(rec["char_accuracy"]))
        acc[f"vlm/{label}"]["call_success"].append(1.0)
        acc[f"vlm/{label}"]["error_count"].append(0.0)


# ----------------------------------------------------------------------
# Aggregation + driver
# ----------------------------------------------------------------------


def summarize(acc):
    """Per-condition {metric: mean_std}. Block prefix kept in the key."""
    summary = {}
    for cond, metrics in acc.items():
        summary[cond] = {}
        for metric, values in metrics.items():
            if metric == "error_count":
                summary[cond][metric] = int(sum(values))
            else:
                summary[cond][metric] = _mean_std(values)
    return summary


def headline_summary(detail):
    """Flat ``summary`` for publication_summary auto-pickup.

    Paper-facing recovery per condition (lower = safer): Block 1 reports the
    temporal-average attack as the headline and carries single-frame plus
    best-observed strong-camera values as explicit caveats; the grid uses
    temporal-average; the α sweep uses long exposure and carries the natural
    inversion-frame attack separately. Rows with zero successful VLM calls are
    omitted from citation summary.
    """
    summary = {}
    for cond, metrics in detail.items():
        if "best_observed_char" in metrics and "temporal_avg_char" in metrics:
            row = {
                "headline_metric": "temporal_average",
                "char_accuracy": metrics["temporal_avg_char"],
                "exact_match": metrics["temporal_avg_exact"],
                "single_frame_char": metrics["single_frame_char"],
                "single_frame_exact": metrics["single_frame_exact"],
                "best_observed_char": metrics["best_observed_char"],
                "best_observed_exact": metrics["best_observed_exact"],
            }
            if "inversion_frame_attack_char" in metrics:
                row["inversion_frame_attack_char"] = metrics["inversion_frame_attack_char"]
                row["inversion_frame_attack_exact"] = metrics["inversion_frame_attack_exact"]
            summary[cond] = row
        elif "best_observed_char" in metrics:
            summary[cond] = {
                "headline_metric": "best_observed",
                "char_accuracy": metrics["best_observed_char"],
                "exact_match": metrics["best_observed_exact"],
            }
        elif "long_exposure_char" in metrics:
            row = {
                "headline_metric": "long_exposure",
                "char_accuracy": metrics["long_exposure_char"],
                "exact_match": metrics["long_exposure_exact"],
            }
            if "inversion_frame_attack_char" in metrics:
                row["inversion_frame_attack_char"] = metrics["inversion_frame_attack_char"]
                row["inversion_frame_attack_exact"] = metrics["inversion_frame_attack_exact"]
            summary[cond] = row
        elif (
            "temporal_avg_char" in metrics
            and metrics["temporal_avg_char"].get("count", 0) > 0
        ):
            row = {
                "headline_metric": "temporal_average",
                "char_accuracy": metrics["temporal_avg_char"],
                "exact_match": metrics["temporal_avg_exact"],
            }
            if "error_count" in metrics:
                row["error_count"] = metrics["error_count"]
                row["call_success"] = metrics.get("call_success", {})
            summary[cond] = row
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
    np.random.seed(RNG_SEED)
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
            "rng_seed": RNG_SEED,
            "n_samples": len(images), "sample_policy": sample_policy,
            "profiles": [c[0] for c in PROFILE_CONDITIONS],
            "grid_stripe": list(GRID_STRIPE), "grid_glyph": list(GRID_GLYPH),
            "inversion_alphas": list(INVERSION_ALPHAS),
            "readability_integration": "brightness_aligned_per_cycle_slots_over_gamma",
            "block2_attack": "temporal_average_only",
            "deployed": {
                "profile": "strong",
                "stripe_alpha": DEPLOYED_STRIPE_ALPHA,
                "glyph_alpha": DEPLOYED_GLYPH_ALPHA,
                "inversion_alpha": DEPLOYED_INVERSION_ALPHA,
            },
            "vlm": vlm_client is not None,
        },
        "interpretation": {
            "headline_metric": (
                "Block 1 summary rows use temporal-average char recovery; "
                "single-frame and best-observed strong-camera results remain in "
                "detail/summary caveat fields."
            ),
            "exact_match_ci": (
                "At small N, off/overlay/deployed exact-match differences should "
                "be read with their CI; overlapping CI are not significance claims."
            ),
            "readability_delta_e": (
                "Readability drift, DeltaE, and SSIM use a brightness-aligned "
                "n_slots/gamma integration model when an inversion slot is present."
            ),
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
    print("--- Block 1: profile (best observed exact | temporal char | inv-frame char | readability) ---")
    for label, _, _, _, _ in PROFILE_CONDITIONS:
        c = f"block1/{label}"
        print(f"  {label:16s} best_exact={m(c, 'best_observed_exact'):.3f}  "
              f"temporal_char={m(c, 'temporal_avg_char'):.3f}  "
              f"inv_frame_char={m(c, 'inversion_frame_attack_char'):.3f}  "
              f"drift={m(c, 'readability_drift'):.2f}  "
              f"ΔE={m(c, 'delta_e'):.2f}  SSIM={m(c, 'ssim'):.3f}")
    print("--- Block 3: inversion α (long-exposure char=defence | inv-frame char=single-slot leak | drift=cost) ---")
    for alpha in INVERSION_ALPHAS:
        c = f"block3/alpha_{alpha:.1f}"
        print(f"  α={alpha:.1f}  long_exp_char={m(c, 'long_exposure_char'):.3f}  "
              f"inv_frame_char={m(c, 'inversion_frame_attack_char'):.3f}  "
              f"(exact={m(c, 'long_exposure_exact'):.3f})  "
              f"drift={m(c, 'readability_drift'):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
