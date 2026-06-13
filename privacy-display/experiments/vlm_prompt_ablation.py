"""
Online VLM prompt-robustness ablation.

This key-gated experiment runs the same attack frames with multiple prompts:
strict transcription, relaxed readability, and sensitive-field extraction. The
goal is to verify that VLM conclusions are not an artifact of one prompt.

Run:
    python experiments/vlm_prompt_ablation.py --dry-run
    python experiments/vlm_prompt_ablation.py --samples-per-category 1
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.ocr_evaluator import text_recovery_metrics  # noqa: E402
from src.attack.vlm_evaluator import DEFAULT_SILICONFLOW_BASE_URL, DEFAULT_VLM_MODEL, VLMClient  # noqa: E402
from src.evaluation.benchmark import _mean_std, _psnr_db  # noqa: E402
from src.evaluation.sampling import select_publication_subset  # noqa: E402
from src.evaluation.vlm_benchmark import build_vlm_attack_frames  # noqa: E402


PROMPT_PRESETS = {
    "strict_transcription": (
        "Transcribe only text that is clearly visible. Do not infer hidden, "
        "missing, or partially occluded characters. Return JSON only with "
        "visible_text, can_read_sensitive, confidence, notes."
    ),
    "relaxed_readability": (
        "Read any text you can reasonably make out in the image. If uncertain, "
        "include only characters you can justify visually. Return JSON only with "
        "visible_text, can_read_sensitive, confidence, notes."
    ),
    "sensitive_field_extraction": (
        "Report visible credentials, URLs, account numbers, codes, or long digit "
        "strings. Do not guess missing characters. Return JSON only with "
        "visible_text, can_read_sensitive, confidence, notes."
    ),
}


def summarize(rows: list[dict]) -> dict:
    out = {}
    for prompt_name in PROMPT_PRESETS:
        group = [r for r in rows if r["prompt_preset"] == prompt_name]
        sensitive = [r for r in group if int(r.get("sensitive_token_count", 0)) > 0]
        out[prompt_name] = {
            "char_accuracy": _mean_std([float(r["char_accuracy"]) for r in group]),
            "word_accuracy": _mean_std([float(r["word_accuracy"]) for r in group]),
            "exact_match": _mean_std([float(r["exact_match"]) for r in group]),
            "sensitive_token_recall": _mean_std([float(r["sensitive_token_recall"]) for r in sensitive]),
            "vlm_read_success_rate": _mean_std([float(r["vlm_can_read_sensitive"]) for r in group]),
            "error_count": int(sum(1 for r in group if r.get("vlm_error"))),
        }
    return out


def sanitize_error(text: str) -> str:
    key = os.environ.get("SILICONFLOW_API_KEY", "")
    if key:
        text = text.replace(key, "[REDACTED]")
    return text.replace("\n", " ").strip()[:500]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="VLM prompt robustness ablation")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--samples-per-category", type=int, default=1)
    p.add_argument("--max-samples", type=int, default=None)
    p.add_argument("--attacks", default="original,global_shutter_slot0,temporal_average_cycle,phase_search_max")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--cycles", type=int, default=2)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    p.add_argument("--model", default=DEFAULT_VLM_MODEL)
    p.add_argument("--base-url", default=DEFAULT_SILICONFLOW_BASE_URL)
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
    attacks = tuple(part.strip() for part in args.attacks.split(",") if part.strip())
    if args.dry_run:
        print(
            "VLM prompt dry run: "
            f"samples={len(selected_indices)} attacks={len(attacks)} "
            f"prompts={len(PROMPT_PRESETS)} calls={len(selected_indices) * len(attacks) * len(PROMPT_PRESETS)}"
        )
        return 0

    client = VLMClient(model=args.model, base_url=args.base_url)
    rows: list[dict] = []
    for order, sample_idx in enumerate(selected_indices):
        image = images[sample_idx]
        truth = truths[sample_idx]
        name = names[sample_idx]
        attack_frames = build_vlm_attack_frames(
            image,
            n=args.n,
            epsilon=args.epsilon,
            cycles=args.cycles,
            cycle_start=sample_idx * args.cycles,
            attacks=attacks,
        )
        for attack_name, (frame, attack_meta) in attack_frames.items():
            for prompt_name, prompt in PROMPT_PRESETS.items():
                try:
                    result = client.analyze_image(frame, ground_truth=truth, prompt=prompt)
                    visible_text = str(result.get("visible_text", "") or "")
                    metrics = result.get("metrics") or text_recovery_metrics(visible_text, truth)
                    vlm_error = ""
                    confidence = float(result.get("confidence", 0.0) or 0.0)
                    can_read = bool(result.get("can_read_sensitive", False))
                    notes = str(result.get("notes", "") or "")
                except Exception as exc:
                    visible_text = ""
                    metrics = text_recovery_metrics("", truth)
                    vlm_error = sanitize_error(str(exc))
                    confidence = 0.0
                    can_read = False
                    notes = ""
                rows.append({
                    "name": name,
                    "sample_order": order,
                    "attack": attack_name,
                    "prompt_preset": prompt_name,
                    "metadata": metadata.get(name, {}),
                    "char_accuracy": float(metrics["char_accuracy"]),
                    "word_accuracy": float(metrics["word_accuracy"]),
                    "exact_match": bool(metrics["exact_match"]),
                    "sensitive_token_recall": float(metrics["sensitive_token_recall"]),
                    "sensitive_token_count": int(metrics["sensitive_token_count"]),
                    "psnr_db": _psnr_db(image, frame),
                    "reconstruction_score": float(attack_meta.get("score", 0.0)),
                    "visible_text": visible_text[:240],
                    "vlm_can_read_sensitive": can_read,
                    "vlm_confidence": confidence,
                    "vlm_notes": notes[:240],
                    "vlm_error": vlm_error,
                })

    report = {
        "config": {
            "model": args.model,
            "base_url": args.base_url,
            "n": args.n,
            "epsilon": args.epsilon,
            "cycles": args.cycles,
            "attacks": list(attacks),
            "prompt_presets": list(PROMPT_PRESETS),
            "sample_policy": sample_policy,
            "n_selected_samples": len(selected_indices),
        },
        "summary": summarize(rows),
        "samples": rows,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "vlm_prompt_ablation.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    if rows and all(row.get("vlm_error") for row in rows):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
