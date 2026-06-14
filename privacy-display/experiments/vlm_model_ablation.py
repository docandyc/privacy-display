"""
Online VLM model-robustness ablation.

The headline "honest boundary" finding — VLMs partially *infer* protected text
that traditional OCR cannot, so full-cycle/phase-search attacks recover content
while single subframes stay near zero — was measured on a single model
(Qwen3-VL-32B). A reviewer will ask whether that is model-specific. This
experiment reruns the same fixed attack set across several VLM families on the
same corpus subset and reports a per-model + cross-model comparison, so the
boundary conclusion can be shown to hold (or not) across models.

It is a thin multi-model wrapper over ``run_vlm_benchmark``: one bounded run per
model with ``save=False``, then a cross-model aggregation written to
``vlm_model_ablation.json``.

Model IDs below are SiliconFlow catalog names and MUST be verified against the
live catalog before a paid run (use ``--models`` to override). Unit tests inject
fake clients and never call the API.

Run:
    python experiments/vlm_model_ablation.py --dry-run
    python experiments/vlm_model_ablation.py --samples-per-category 3
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.vlm_evaluator import (  # noqa: E402
    API_KEY_ENV,
    DEFAULT_SILICONFLOW_BASE_URL,
    DEFAULT_VLM_MODEL,
    VLMClient,
)
from src.evaluation.benchmark import _mean_std  # noqa: E402
from src.evaluation.sampling import select_stratified_samples  # noqa: E402
from src.evaluation.vlm_benchmark import DEFAULT_VLM_ATTACKS, run_vlm_benchmark  # noqa: E402

RESULT_FILE = "vlm_model_ablation.json"

# Three VLM families. Verify these IDs against the live SiliconFlow catalog
# before any paid run; override with --models if an ID is unavailable.
DEFAULT_MODELS = (
    DEFAULT_VLM_MODEL,                  # Qwen/Qwen3-VL-32B-Instruct (incumbent)
    "Pro/moonshotai/Kimi-K2.6",         # Kimi-K2 family
    "zai-org/GLM-4.5V",                 # GLM-V family
)

DEFAULT_ABLATION_ATTACKS = (
    "original",
    "global_shutter_slot0",
    "temporal_average_cycle",
    "phase_search_max",
)


def parse_attacks(value: str) -> tuple[str, ...]:
    attacks = tuple(part.strip() for part in value.split(",") if part.strip())
    if not attacks:
        raise argparse.ArgumentTypeError("at least one attack is required")
    unknown = sorted(set(attacks) - set(DEFAULT_VLM_ATTACKS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown attacks: {', '.join(unknown)}")
    return attacks


def parse_models(value: str) -> tuple[str, ...]:
    models = tuple(part.strip() for part in value.split(",") if part.strip())
    if not models:
        raise argparse.ArgumentTypeError("at least one model is required")
    return models


def _char_mean(stat: dict | None) -> float:
    if not isinstance(stat, dict):
        return 0.0
    try:
        return float(stat.get("mean", 0.0))
    except (TypeError, ValueError):
        return 0.0


def run_model_ablation(
    clients: dict | None = None,
    models: tuple[str, ...] = DEFAULT_MODELS,
    output_dir: str | Path = ROOT / "experiments" / "results",
    n: int = 4,
    epsilon: float = 8 / 255,
    cycles: int = 2,
    samples_per_category: int = 3,
    max_samples: int | None = None,
    attacks: tuple[str, ...] = DEFAULT_ABLATION_ATTACKS,
    corpus: tuple[list, list[str], list[str]] | None = None,
    metadata: dict | None = None,
    base_url: str = DEFAULT_SILICONFLOW_BASE_URL,
    timeout: float = 60.0,
    progress_interval: int = 1,
    save: bool = True,
) -> dict:
    if corpus is None:
        images, truths, names = load_corpus()
        corpus_metadata = load_corpus_metadata()
    else:
        images, truths, names = corpus
        corpus_metadata = metadata or {}

    model_names = list(clients.keys()) if clients is not None else list(models)
    if not model_names:
        raise ValueError("at least one model is required")
    selected_attacks = tuple(attacks)

    per_model: dict[str, dict] = {}
    compact: dict[str, dict] = {}
    cross_model: dict[str, dict] = {attack: {} for attack in selected_attacks}

    for model in model_names:
        client = clients[model] if clients is not None else VLMClient(
            model=model, base_url=base_url, timeout=timeout,
        )
        report = run_vlm_benchmark(
            client=client,
            output_dir=str(output_dir),
            n=n,
            epsilon=epsilon,
            cycles=cycles,
            samples_per_category=samples_per_category,
            max_samples=max_samples,
            attacks=selected_attacks,
            save=False,
            corpus=(images, truths, names),
            metadata=corpus_metadata,
            progress_interval=progress_interval,
            partial_save=False,
        )
        s = report["summary"]
        best = s.get("best_attack_per_sample", {})
        attack_stats = s.get("attacks", {})
        per_model[model] = {"config": report["config"], "summary": s}
        compact[model] = {
            "char_accuracy": best.get("char_accuracy", _mean_std([])),
            "single_frame_char_accuracy": attack_stats.get("global_shutter_slot0", {}).get(
                "char_accuracy", _mean_std([])
            ),
            "read_success_rate": best.get("vlm_read_success_rate", _mean_std([])),
            "error_count": int(s.get("call_status", {}).get("error_calls", 0)),
        }
        for attack in selected_attacks:
            cross_model[attack][model] = _char_mean(
                attack_stats.get(attack, {}).get("char_accuracy")
            )

    n_selected = (
        next(iter(per_model.values()))["config"]["n_selected_samples"] if per_model else 0
    )
    report = {
        "config": {
            "models": model_names,
            "n": n,
            "epsilon": epsilon,
            "cycles": cycles,
            "attacks": list(selected_attacks),
            "samples_per_category": samples_per_category,
            "max_samples": max_samples,
            "n_selected_samples": n_selected,
            "planned_calls_total": n_selected * len(selected_attacks) * len(model_names),
            "base_url": base_url,
        },
        "models": per_model,
        "summary": compact,
        "cross_model": cross_model,
    }

    if save:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / RESULT_FILE
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n=== VLM model ablation (n_samples={n_selected}, n={n}) ===")
        header = "| attack | " + " | ".join(model_names) + " |"
        print(header)
        print("|" + "---|" * (len(model_names) + 1))
        for attack in selected_attacks:
            cells = " | ".join(f"{cross_model[attack][m] * 100:.0f}%" for m in model_names)
            print(f"| {attack} | {cells} |")
        print(f"Saved: {out}")

    return report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="VLM model robustness ablation")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--models", type=parse_models, default=DEFAULT_MODELS)
    p.add_argument("--samples-per-category", type=int, default=3)
    p.add_argument("--max-samples", type=int, default=None)
    p.add_argument("--attacks", type=parse_attacks, default=DEFAULT_ABLATION_ATTACKS)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--epsilon", type=float, default=8 / 255)
    p.add_argument("--cycles", type=int, default=2)
    p.add_argument("--base-url", default=DEFAULT_SILICONFLOW_BASE_URL)
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--progress-interval", type=int, default=1)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    import os

    args = parse_args()
    images, truths, names = load_corpus()
    metadata = load_corpus_metadata()
    selected = select_stratified_samples(
        names, metadata,
        samples_per_category=args.samples_per_category,
        max_samples=args.max_samples,
    )
    if args.dry_run:
        print(
            "VLM model ablation dry run: "
            f"models={len(args.models)} samples={len(selected)} attacks={len(args.attacks)} "
            f"calls={len(selected) * len(args.attacks) * len(args.models)}"
        )
        for model in args.models:
            print(f"  - {model}")
        return 0

    if not os.environ.get(API_KEY_ENV):
        print(
            f"Missing {API_KEY_ENV}. Export it before running live VLM model ablation.",
            file=sys.stderr,
        )
        return 2

    run_model_ablation(
        models=tuple(args.models),
        output_dir=args.output_dir,
        n=args.n,
        epsilon=args.epsilon,
        cycles=args.cycles,
        samples_per_category=args.samples_per_category,
        max_samples=args.max_samples,
        attacks=tuple(args.attacks),
        corpus=(images, truths, names),
        metadata=metadata,
        base_url=args.base_url,
        timeout=args.timeout,
        progress_interval=args.progress_interval,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
