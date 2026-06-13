"""
Adaptive single-frame preprocessing attack ablation.

This experiment checks whether a camera-side attacker can recover protected
single subframes after common OCR preprocessing: binarization, contrast
enhancement, sharpening, denoising, and upscaling. These are cheap adaptive
attacks reviewers often expect before accepting a "single-frame OCR is 0%"
claim.

Run:
    python experiments/adaptive_attack_ablation.py --max-samples 24
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
from src.evaluation.benchmark import _mean_std, compose_protected_subframes  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402


PREPROCESSORS = (
    "raw_subframe",
    "otsu_binarize",
    "adaptive_threshold",
    "clahe_luma",
    "unsharp_mask",
    "denoise",
    "upscale_2x",
)


def preprocess(frame: np.ndarray, method: str) -> np.ndarray:
    if method == "raw_subframe":
        return frame

    import cv2

    if method == "otsu_binarize":
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        _, out = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return np.repeat(out[..., None], 3, axis=2)
    if method == "adaptive_threshold":
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        out = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 5
        )
        return np.repeat(out[..., None], 3, axis=2)
    if method == "clahe_luma":
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
        lab[..., 0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lab[..., 0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    if method == "unsharp_mask":
        blur = cv2.GaussianBlur(frame, (0, 0), 1.0)
        return np.clip(frame.astype(np.float32) * 1.7 - blur.astype(np.float32) * 0.7, 0, 255).astype(np.uint8)
    if method == "denoise":
        return cv2.fastNlMeansDenoisingColored(frame, None, 5, 5, 7, 21)
    if method == "upscale_2x":
        h, w = frame.shape[:2]
        return cv2.resize(frame, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    raise ValueError(f"unknown preprocessor: {method}")


def summarize(rows: list[dict]) -> dict:
    out = {}
    for method in PREPROCESSORS:
        group = [r for r in rows if r["preprocessor"] == method]
        sensitive = [r for r in group if int(r.get("sensitive_token_count", 0)) > 0]
        out[method] = {
            "char_accuracy": _mean_std([float(r["char_accuracy"]) for r in group]),
            "word_accuracy": _mean_std([float(r["word_accuracy"]) for r in group]),
            "exact_match": _mean_std([float(r["exact_match"]) for r in group]),
            "sensitive_token_recall": _mean_std([float(r["sensitive_token_recall"]) for r in sensitive]),
            "leak_rate_char_ge_20pct": _mean_std([float(r["char_accuracy"] >= 0.20) for r in group]),
            "error_count": int(sum(1 for r in group if r.get("ocr_error"))),
        }
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Adaptive OCR preprocessing ablation")
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
        subframe = compose_protected_subframes(
            img, n=args.n, epsilon=args.epsilon, cycles=1, cycle_start=selected_indices[idx]
        )[0]
        for method in PREPROCESSORS:
            frame = preprocess(subframe, method)
            ocr_error = ""
            try:
                text = ev.recognize(frame, "tesseract")
            except Exception as exc:
                text = ""
                ocr_error = str(exc)
            metrics = text_recovery_metrics(text, truth)
            rows.append({
                "name": name,
                "metadata": metadata.get(name, {}),
                "preprocessor": method,
                "char_accuracy": metrics["char_accuracy"],
                "word_accuracy": metrics["word_accuracy"],
                "exact_match": metrics["exact_match"],
                "sensitive_token_recall": metrics["sensitive_token_recall"],
                "sensitive_token_count": metrics["sensitive_token_count"],
                "recognized_text": text[:160],
                "ocr_error": ocr_error,
            })
        if (idx + 1) % 4 == 0 or idx + 1 == len(images):
            print(f"  adaptive sample {idx + 1}/{len(images)}")

    report = {
        "config": {
            "n": args.n,
            "epsilon": args.epsilon,
            "n_samples": len(images),
            "sample_policy": sample_policy,
            "preprocessors": list(PREPROCESSORS),
        },
        "summary": summarize(rows),
        "samples": rows,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "adaptive_attack_ablation.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
