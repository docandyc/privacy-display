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
from src.attack.vlm_evaluator import API_KEY_ENV, DEFAULT_SILICONFLOW_BASE_URL, DEFAULT_VLM_MODEL, VLMClient  # noqa: E402
from src.evaluation.benchmark import _mean_std, _psnr_db  # noqa: E402
from src.evaluation.sampling import select_publication_subset  # noqa: E402
from src.evaluation.vlm_benchmark import DEFAULT_VLM_ATTACKS, build_vlm_attack_frames  # noqa: E402


RESULT_FILE = "vlm_prompt_ablation.json"


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


def parse_attacks(value: str) -> tuple[str, ...]:
    attacks = tuple(part.strip() for part in value.split(",") if part.strip())
    if not attacks:
        raise argparse.ArgumentTypeError("at least one attack is required")
    unknown = sorted(set(attacks) - set(DEFAULT_VLM_ATTACKS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown attacks: {', '.join(unknown)}")
    return attacks


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="VLM prompt robustness ablation")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--samples-per-category", type=int, default=1)
    p.add_argument("--max-samples", type=int, default=None)
    p.add_argument(
        "--attacks",
        type=parse_attacks,
        default=parse_attacks("original,global_shutter_slot0,temporal_average_cycle,phase_search_max"),
    )
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--cycles", type=int, default=2)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    p.add_argument("--model", default=DEFAULT_VLM_MODEL)
    p.add_argument("--base-url", default=DEFAULT_SILICONFLOW_BASE_URL)
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument(
        "--progress-interval",
        type=int,
        default=1,
        help="Print one progress line every N live calls; use 0 to disable.",
    )
    p.add_argument(
        "--no-partial-save",
        action="store_true",
        help="Disable rewriting the partial JSON result after each completed call.",
    )
    return p.parse_args()


def run_prompt_ablation(
    client: VLMClient | None = None,
    output_dir: str | Path = ROOT / "experiments" / "results",
    n: int = 4,
    epsilon: float = 8 / 255,
    cycles: int = 2,
    samples_per_category: int = 1,
    max_samples: int | None = None,
    attacks: tuple[str, ...] = parse_attacks(
        "original,global_shutter_slot0,temporal_average_cycle,phase_search_max"
    ),
    corpus: tuple[list, list[str], list[str]] | None = None,
    metadata: dict | None = None,
    model: str = DEFAULT_VLM_MODEL,
    base_url: str = DEFAULT_SILICONFLOW_BASE_URL,
    timeout: float = 60.0,
    progress_interval: int = 1,
    partial_save: bool = True,
) -> dict:
    if progress_interval < 0:
        raise ValueError("progress_interval must be non-negative")
    if samples_per_category <= 0:
        raise ValueError("samples_per_category must be positive")
    if max_samples is not None and max_samples <= 0:
        raise ValueError("max_samples must be positive when provided")

    if corpus is None:
        images, truths, names = load_corpus()
        corpus_metadata = load_corpus_metadata()
    else:
        images, truths, names = corpus
        corpus_metadata = metadata or {}

    selected_indices, sample_policy = select_publication_subset(
        names,
        corpus_metadata,
        max_samples=max_samples,
        samples_per_category=samples_per_category,
    )
    selected_attacks = tuple(attacks)
    client = client or VLMClient(model=model, base_url=base_url, timeout=timeout)
    total_calls = len(selected_indices) * len(selected_attacks) * len(PROMPT_PRESETS)
    out_dir = Path(output_dir)
    out = out_dir / RESULT_FILE

    def build_report(rows: list[dict], interrupted: bool = False) -> dict:
        return {
            "config": {
                "model": getattr(client, "model", model),
                "base_url": getattr(client, "base_url", base_url),
                "n": n,
                "epsilon": epsilon,
                "cycles": cycles,
                "attacks": list(selected_attacks),
                "prompt_presets": list(PROMPT_PRESETS),
                "sample_policy": sample_policy,
                "n_selected_samples": len(selected_indices),
                "planned_calls": total_calls,
                "completed_calls": len(rows),
                "interrupted": interrupted,
            },
            "summary": summarize(rows),
            "samples": rows,
        }

    def write_report(rows: list[dict], interrupted: bool = False) -> dict:
        report = build_report(rows, interrupted=interrupted)
        out_dir.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report

    rows: list[dict] = []
    try:
        for order, sample_idx in enumerate(selected_indices):
            image = images[sample_idx]
            truth = truths[sample_idx]
            name = names[sample_idx]
            attack_frames = build_vlm_attack_frames(
                image,
                n=n,
                epsilon=epsilon,
                cycles=cycles,
                cycle_start=sample_idx * cycles,
                attacks=selected_attacks,
            )
            for attack_name, (frame, attack_meta) in attack_frames.items():
                for prompt_name, prompt in PROMPT_PRESETS.items():
                    call_number = len(rows) + 1
                    if progress_interval and (
                        call_number == 1
                        or call_number % progress_interval == 0
                        or call_number == total_calls
                    ):
                        print(
                            f"VLM prompt call {call_number}/{total_calls}: "
                            f"sample={name} attack={attack_name} prompt={prompt_name}",
                            flush=True,
                        )
                    try:
                        result = client.analyze_image(
                            frame,
                            ground_truth=truth,
                            prompt=prompt,
                        )
                        visible_text = str(result.get("visible_text", "") or "")
                        metrics = result.get("metrics") or text_recovery_metrics(
                            visible_text,
                            truth,
                        )
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
                        "metadata": corpus_metadata.get(name, {}),
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
                    if partial_save:
                        write_report(rows)
    except KeyboardInterrupt:
        write_report(rows, interrupted=True)
        print(f"VLM prompt partial result saved after interrupt: {out}")
        raise

    return write_report(rows)


def main() -> int:
    args = parse_args()
    images, truths, names = load_corpus()
    metadata = load_corpus_metadata()
    selected_indices, _sample_policy = select_publication_subset(
        names,
        metadata,
        max_samples=args.max_samples,
        samples_per_category=args.samples_per_category,
    )
    if args.dry_run:
        print(
            "VLM prompt dry run: "
            f"samples={len(selected_indices)} attacks={len(args.attacks)} "
            f"prompts={len(PROMPT_PRESETS)} "
            f"calls={len(selected_indices) * len(args.attacks) * len(PROMPT_PRESETS)}"
        )
        return 0

    if not os.environ.get(API_KEY_ENV):
        print(
            f"Missing {API_KEY_ENV}. Export it before running live VLM prompt ablation.",
            file=sys.stderr,
        )
        return 2

    client = VLMClient(model=args.model, base_url=args.base_url, timeout=args.timeout)
    report = run_prompt_ablation(
        client=client,
        output_dir=args.output_dir,
        n=args.n,
        epsilon=args.epsilon,
        cycles=args.cycles,
        samples_per_category=args.samples_per_category,
        max_samples=args.max_samples,
        attacks=args.attacks,
        corpus=(images, truths, names),
        metadata=metadata,
        model=args.model,
        base_url=args.base_url,
        timeout=args.timeout,
        progress_interval=args.progress_interval,
        partial_save=not args.no_partial_save,
    )
    out = Path(args.output_dir) / RESULT_FILE
    print(f"Saved: {out}")
    if report["samples"] and all(row.get("vlm_error") for row in report["samples"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
