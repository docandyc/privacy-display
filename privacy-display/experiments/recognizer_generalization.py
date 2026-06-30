"""
Experiment B — recognizer generalization across the attack-frame matrix.

Runs every available OCR family (Tesseract / EasyOCR / Surya / TrOCR /
docTR) over the same set of attack frames so a reviewer cannot argue the 0%
single-subframe result is specific to classic engines. The full-cycle
reconstruction frames are included on purpose: they should leak across *all*
recognizers, which keeps the threat-model boundary consistent.

Online VLM readability is evaluated by the separate, key-gated
``experiments/vlm_readability_analysis.py``; its results are folded into the
publication tables by ``experiments/publication_summary.py``.

Run:
    python experiments/recognizer_generalization.py --max-samples 40
    python experiments/recognizer_generalization.py --engines tesseract,trocr,doctr
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.camera_simulator import CameraSimulator, CameraParams  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator, text_recovery_metrics  # noqa: E402
from src.evaluation.benchmark import _mean_std, compose_protected_subframes  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402

# Attack frames evaluated for every recognizer. "original" is the unprotected
# baseline; "single_subframe" is the core defended case; the rest are
# full-cycle reconstruction attacks that define the leakage boundary.
ATTACK_ORDER = [
    "original",
    "single_subframe",
    "temporal_average_cycle",
    "phase_search_max",
    "blue_channel_max",
]


def build_attack_frames(image, n: int, epsilon: float, cycles: int, sample_idx: int) -> dict:
    cam = CameraSimulator(CameraParams(readout_time=15e-6, exposure_time=1 / 240))
    subframes = compose_protected_subframes(
        image, n=n, epsilon=epsilon, cycles=cycles, cycle_start=sample_idx * cycles
    )
    frames = {
        "original": image,
        "single_subframe": subframes[0],
        "temporal_average_cycle": cam.temporal_averaging_attack(
            subframes, n, randomize_order=False
        ),
    }
    suite = cam.screen_camera_attack_suite(subframes, cycle_length=n)
    frames["phase_search_max"] = suite["phase_search_max"]["frame"]
    frames["blue_channel_max"] = suite["blue_channel_max"]["frame"]
    return frames


def summarize(rows: list[dict]) -> dict:
    """Group rows by (engine, attack) and report mean±std + leak rate."""
    engines = sorted({r["engine"] for r in rows})
    attacks = [a for a in ATTACK_ORDER if any(r["attack"] == a for r in rows)]
    out: dict[str, dict] = {}
    for engine in engines:
        out[engine] = {}
        for attack in attacks:
            group = [r for r in rows if r["engine"] == engine and r["attack"] == attack]
            sensitive = [r for r in group if int(r.get("sensitive_token_count", 0)) > 0]
            out[engine][attack] = {
                "char_accuracy": _mean_std([float(r["char_accuracy"]) for r in group]),
                "exact_match": _mean_std([float(r["exact_match"]) for r in group]),
                "sensitive_token_recall": _mean_std(
                    [float(r["sensitive_token_recall"]) for r in sensitive]
                ),
                "leak_rate_char_ge_20pct": _mean_std(
                    [float(r["char_accuracy"] >= 0.20) for r in group]
                ),
                "error_count": int(sum(1 for r in group if r.get("ocr_error"))),
            }
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Experiment B: recognizer generalization")
    p.add_argument("--engines", default="", help="Comma engines; default = all detected")
    p.add_argument("--max-samples", type=int, default=None)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--cycles", type=int, default=2)
    p.add_argument("--ocr-timeout", type=float, default=8.0)
    p.add_argument("--progress-interval", type=int, default=10)
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
    names = take_indices(names, selected_indices)

    requested = [e.strip() for e in args.engines.split(",") if e.strip()]
    if requested:
        unknown = [e for e in requested if e not in OCREvaluator.supported_engines()]
        if unknown:
            print(f"[error] unsupported OCR engine(s): {unknown}", file=sys.stderr)
            return 2
        engines = requested
        evaluator = OCREvaluator(engines=engines, timeout=args.ocr_timeout)
    else:
        evaluator = OCREvaluator(timeout=args.ocr_timeout)
        engines = list(evaluator.engines)
    if not engines:
        print("[error] no requested OCR engine is available.", file=sys.stderr)
        return 2
    print(f"Recognizers: {engines} | samples={len(images)} | n={args.n}")

    rows: list[dict] = []
    total = len(images)
    for idx, (image, truth, name) in enumerate(zip(images, truths, names)):
        if args.progress_interval and (idx == 0 or (idx + 1) % args.progress_interval == 0 or idx + 1 == total):
            print(f"  sample {idx + 1}/{total}: {name}")
        frames = build_attack_frames(image, args.n, args.epsilon, args.cycles, idx)
        for engine in engines:
            for attack, frame in frames.items():
                ocr_error = ""
                try:
                    text = evaluator.recognize(frame, engine)
                except Exception as exc:
                    text = ""
                    ocr_error = str(exc)
                m = text_recovery_metrics(text, truth)
                rows.append({
                    "name": name, "engine": engine, "attack": attack,
                    "metadata": metadata.get(name, {}),
                    "char_accuracy": m["char_accuracy"], "word_accuracy": m["word_accuracy"],
                    "exact_match": m["exact_match"],
                    "sensitive_token_recall": m["sensitive_token_recall"],
                    "sensitive_token_count": m["sensitive_token_count"],
                    "recognized_text": text[:160], "ocr_error": ocr_error,
                })

    report = {
        "config": {
            "engines": engines, "n": args.n, "epsilon": args.epsilon,
            "cycles": args.cycles, "n_samples": len(images),
            "sample_policy": sample_policy,
            "attack_order": [a for a in ATTACK_ORDER if any(r["attack"] == a for r in rows)],
        },
        "summary": summarize(rows),
        "samples": rows,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "recognizer_generalization.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Console table: rows = attack, cols = engine (char recovery %).
    attacks = report["config"]["attack_order"]
    print("\nChar-recovery by recognizer × attack frame:")
    print("| attack | " + " | ".join(engines) + " |")
    print("|" + "---|" * (len(engines) + 1))
    for attack in attacks:
        cells = [f"{report['summary'][e][attack]['char_accuracy']['mean'] * 100:.1f}%" for e in engines]
        print(f"| {attack} | " + " | ".join(cells) + " |")
    print(f"\nSaved: {out}")
    print("Expected: single_subframe ~0% across all recognizers; full-cycle "
          "reconstruction leaks across all — the boundary is recognizer-agnostic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
