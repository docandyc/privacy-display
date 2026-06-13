"""
Simulated camera pipeline ablation for protected subframes.

Real hardware is still required for Experiment A, but this bounded offline
experiment checks whether common camera processing stages alter the single-frame
security conclusion: JPEG/video compression, sensor noise, motion blur, digital
zoom, auto contrast, and rolling shutter capture.

Run:
    python experiments/camera_pipeline_ablation.py --max-samples 24
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
from src.attack.camera_simulator import CameraParams, CameraSimulator  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator, text_recovery_metrics  # noqa: E402
from src.evaluation.benchmark import _mean_std, compose_protected_subframes  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402


PIPELINES = (
    "clean_subframe",
    "jpeg_q50",
    "sensor_noise_iso_high",
    "motion_blur",
    "digital_zoom_2x",
    "auto_contrast",
    "rolling_shutter_single",
    "temporal_average_boundary",
)


def apply_pipeline(frame: np.ndarray, method: str, *, subframes: list[np.ndarray], cam: CameraSimulator, display_rate: float, n: int) -> np.ndarray:
    import cv2

    if method == "clean_subframe":
        return frame
    if method == "jpeg_q50":
        ok, buf = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        if not ok:
            raise RuntimeError("JPEG encoding failed")
        return cv2.cvtColor(cv2.imdecode(buf, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    if method == "sensor_noise_iso_high":
        rng = np.random.default_rng(20260613)
        noise = rng.normal(0, 9.0, size=frame.shape)
        return np.clip(frame.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    if method == "motion_blur":
        kernel = np.zeros((1, 9), dtype=np.float32)
        kernel[0, :] = 1.0 / 9.0
        return cv2.filter2D(frame, -1, kernel)
    if method == "digital_zoom_2x":
        h, w = frame.shape[:2]
        crop = frame[h // 4: h * 3 // 4, w // 4: w * 3 // 4]
        return cv2.resize(crop, (w, h), interpolation=cv2.INTER_CUBIC)
    if method == "auto_contrast":
        lo = np.percentile(frame, 1)
        hi = np.percentile(frame, 99)
        if hi <= lo + 1e-6:
            return frame
        return np.clip((frame.astype(np.float32) - lo) * (255.0 / (hi - lo)), 0, 255).astype(np.uint8)
    if method == "rolling_shutter_single":
        return cam.capture_rolling_shutter(subframes, display_rate, switch_time=0.0)
    if method == "temporal_average_boundary":
        return cam.temporal_averaging_attack(subframes, n, randomize_order=False)
    raise ValueError(f"unknown camera pipeline: {method}")


def summarize(rows: list[dict]) -> dict:
    out = {}
    for method in PIPELINES:
        group = [r for r in rows if r["pipeline"] == method]
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
    p = argparse.ArgumentParser(description="Camera pipeline ablation")
    p.add_argument("--max-samples", type=int, default=24)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--cycles", type=int, default=2)
    p.add_argument("--display-rate", type=float, default=240.0)
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

    cam = CameraSimulator(CameraParams(readout_time=15e-6, exposure_time=(1.0 / args.display_rate) * 0.5))
    ev = OCREvaluator(engines=["tesseract"], timeout=args.ocr_timeout)
    rows: list[dict] = []
    for idx, (img, truth, name) in enumerate(zip(images, truths, names)):
        subframes = compose_protected_subframes(
            img, n=args.n, epsilon=args.epsilon, cycles=args.cycles, cycle_start=selected_indices[idx] * args.cycles
        )
        single = subframes[0]
        for method in PIPELINES:
            frame = apply_pipeline(single, method, subframes=subframes, cam=cam, display_rate=args.display_rate, n=args.n)
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
                "pipeline": method,
                "char_accuracy": metrics["char_accuracy"],
                "word_accuracy": metrics["word_accuracy"],
                "exact_match": metrics["exact_match"],
                "sensitive_token_recall": metrics["sensitive_token_recall"],
                "sensitive_token_count": metrics["sensitive_token_count"],
                "recognized_text": text[:160],
                "ocr_error": ocr_error,
            })
        if (idx + 1) % 4 == 0 or idx + 1 == len(images):
            print(f"  camera-pipeline sample {idx + 1}/{len(images)}")

    report = {
        "config": {
            "n": args.n,
            "epsilon": args.epsilon,
            "cycles": args.cycles,
            "display_rate_hz": args.display_rate,
            "n_samples": len(images),
            "sample_policy": sample_policy,
            "pipelines": list(PIPELINES),
        },
        "summary": summarize(rows),
        "samples": rows,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "camera_pipeline_ablation.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
