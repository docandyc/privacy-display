"""
Screen privacy baseline comparison.

Compares the temporal masking system against simple software baselines that a
reviewer may ask for: dimming, blur, pixelation, and an off-axis/privacy-filter
proxy. This is not a replacement for a physical privacy-film real-capture
baseline; it provides a bounded offline control table.

Run:
    python experiments/screen_privacy_baselines.py --max-samples 24
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
from src.attack.ocr_evaluator import OCREvaluator, text_recovery_metrics  # noqa: E402
from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.evaluation.benchmark import _mean_std, compose_protected_subframes  # noqa: E402
from src.evaluation.metrics import compute_delta_e, compute_ssim  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402


BASELINES = (
    "unprotected",
    "dim_50pct",
    "gaussian_blur",
    "pixelate_12px",
    "privacy_filter_offaxis_proxy",
    "temporal_mask_single_subframe",
)


def baseline_frame(image: np.ndarray, baseline: str, *, subframes: list[np.ndarray], n: int, epsilon: float) -> tuple[np.ndarray, np.ndarray, dict]:
    import cv2

    if baseline == "unprotected":
        return image, image, {"type": "plain_display"}
    if baseline == "dim_50pct":
        frame = np.clip(image.astype(np.float32) * 0.5, 0, 255).astype(np.uint8)
        return frame, frame, {"type": "brightness_reduction", "gain": 0.5}
    if baseline == "gaussian_blur":
        frame = cv2.GaussianBlur(image, (0, 0), 2.2)
        return frame, frame, {"type": "spatial_degradation", "sigma": 2.2}
    if baseline == "pixelate_12px":
        h, w = image.shape[:2]
        small = cv2.resize(image, (max(1, w // 12), max(1, h // 12)), interpolation=cv2.INTER_AREA)
        frame = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        return frame, frame, {"type": "spatial_degradation", "cell_px": 12}
    if baseline == "privacy_filter_offaxis_proxy":
        # Approximate a traditional privacy filter observed off-axis: luminance
        # compression plus mild blur. Physical film must be measured separately.
        dark = np.clip(image.astype(np.float32) * 0.32, 0, 255).astype(np.uint8)
        frame = cv2.GaussianBlur(dark, (0, 0), 1.0)
        return frame, frame, {"type": "simulated_offaxis_privacy_filter", "gain": 0.32}
    if baseline == "temporal_mask_single_subframe":
        composer = SubframeComposer(n=n, gamma=1.0)
        integrated = composer.integrate_subframes(subframes, pedestal=epsilon * 255)
        return subframes[0], integrated, {"type": "temporal_mask", "attack_frame": "single_subframe"}
    raise ValueError(f"unknown baseline: {baseline}")


def summarize(rows: list[dict]) -> dict:
    out = {}
    for baseline in BASELINES:
        group = [r for r in rows if r["baseline"] == baseline]
        sensitive = [r for r in group if int(r.get("sensitive_token_count", 0)) > 0]
        out[baseline] = {
            "char_accuracy": _mean_std([float(r["char_accuracy"]) for r in group]),
            "word_accuracy": _mean_std([float(r["word_accuracy"]) for r in group]),
            "exact_match": _mean_std([float(r["exact_match"]) for r in group]),
            "sensitive_token_recall": _mean_std([float(r["sensitive_token_recall"]) for r in sensitive]),
            "delta_e": _mean_std([float(r["delta_e"]) for r in group]),
            "ssim": _mean_std([float(r["ssim"]) for r in group]),
            "leak_rate_char_ge_20pct": _mean_std([float(r["char_accuracy"] >= 0.20) for r in group]),
            "error_count": int(sum(1 for r in group if r.get("ocr_error"))),
        }
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Screen privacy baseline comparison")
    p.add_argument("--max-samples", type=int, default=24)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    images, truths, names = load_corpus()
    metadata = load_corpus_metadata()
    selected_indices, sample_policy = select_publication_subset(
        names, metadata, max_samples=args.max_samples, samples_per_category=args.samples_per_category
    )
    images = take_indices(images, selected_indices)
    truths = take_indices(truths, selected_indices)
    names = take_indices(names, selected_indices)

    ev = OCREvaluator(engines=["tesseract"], timeout=args.ocr_timeout)
    rows: list[dict] = []
    for idx, (img, truth, name) in enumerate(zip(images, truths, names)):
        subframes = compose_protected_subframes(
            img, n=args.n, epsilon=args.epsilon, cycles=1, cycle_start=selected_indices[idx]
        )
        for baseline in BASELINES:
            attack_frame, user_frame, meta = baseline_frame(
                img, baseline, subframes=subframes, n=args.n, epsilon=args.epsilon
            )
            ocr_error = ""
            try:
                text = ev.recognize(attack_frame, "tesseract")
            except Exception as exc:
                text = ""
                ocr_error = str(exc)
            metrics = text_recovery_metrics(text, truth)
            rows.append({
                "name": name,
                "metadata": metadata.get(name, {}),
                "baseline": baseline,
                "baseline_metadata": meta,
                "char_accuracy": metrics["char_accuracy"],
                "word_accuracy": metrics["word_accuracy"],
                "exact_match": metrics["exact_match"],
                "sensitive_token_recall": metrics["sensitive_token_recall"],
                "sensitive_token_count": metrics["sensitive_token_count"],
                "delta_e": compute_delta_e(img, user_frame),
                "ssim": compute_ssim(img, user_frame),
                "recognized_text": text[:160],
                "ocr_error": ocr_error,
            })
        if (idx + 1) % 4 == 0 or idx + 1 == len(images):
            print(f"  baseline sample {idx + 1}/{len(images)}")

    report = {
        "config": {
            "n": args.n,
            "epsilon": args.epsilon,
            "n_samples": len(images),
            "sample_policy": sample_policy,
            "baselines": list(BASELINES),
            "scope_note": "Software/off-axis proxy baselines; physical privacy film requires real_capture condition data.",
        },
        "summary": summarize(rows),
        "samples": rows,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "screen_privacy_baselines.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
