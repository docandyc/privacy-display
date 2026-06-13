"""
Run online VLM readability checks on protected-display attack frames.

The API key is read from SILICONFLOW_API_KEY. Do not put secrets in this file,
command arguments, or result JSON.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.vlm_evaluator import (  # noqa: E402
    API_KEY_ENV,
    DEFAULT_SILICONFLOW_BASE_URL,
    DEFAULT_VLM_MODEL,
    VLMClient,
)
from src.evaluation.vlm_benchmark import (  # noqa: E402
    DEFAULT_VLM_ATTACKS,
    run_vlm_benchmark,
    select_stratified_samples,
)


def _parse_attacks(value: str) -> list[str]:
    attacks = [part.strip() for part in value.split(",") if part.strip()]
    if not attacks:
        raise argparse.ArgumentTypeError("at least one attack is required")
    unknown = sorted(set(attacks) - set(DEFAULT_VLM_ATTACKS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown attacks: {', '.join(unknown)}")
    return attacks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Online VLM readability benchmark")
    parser.add_argument("--output-dir", default="experiments/results")
    parser.add_argument("--samples-per-category", type=int, default=1)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--epsilon", type=float, default=8 / 255)
    parser.add_argument("--cycles", type=int, default=2)
    parser.add_argument("--model", default=DEFAULT_VLM_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_SILICONFLOW_BASE_URL)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--attacks",
        type=_parse_attacks,
        default=",".join(DEFAULT_VLM_ATTACKS),
        help="Comma-separated attack names.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selected sample and call counts without requiring an API key.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    images, truths, names = load_corpus()
    metadata = load_corpus_metadata()
    selected = select_stratified_samples(
        names,
        metadata,
        samples_per_category=args.samples_per_category,
        max_samples=args.max_samples,
    )
    call_count = len(selected) * len(args.attacks)

    if args.dry_run:
        categories = sorted({
            str(metadata.get(names[idx], {}).get("category", "unknown"))
            for idx in selected
        })
        print(f"VLM dry run: selected_samples={len(selected)} attacks={len(args.attacks)} calls={call_count}")
        print("categories=" + ",".join(categories))
        print("attacks=" + ",".join(args.attacks))
        return 0

    if not os.environ.get(API_KEY_ENV):
        print(
            f"Missing {API_KEY_ENV}. Export it in your shell before running the live VLM benchmark.",
            file=sys.stderr,
        )
        return 2

    client = VLMClient(
        base_url=args.base_url,
        model=args.model,
        timeout=args.timeout,
    )
    report = run_vlm_benchmark(
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
    )
    summary = report["summary"]["best_attack_per_sample"]
    status = report["summary"].get("call_status", {})
    if status.get("all_calls_failed"):
        print(
            "VLM benchmark failed: all live API calls failed; "
            "result file was written for diagnostics but must not be cited.",
            file=sys.stderr,
        )
        return 3
    print(
        "VLM benchmark complete: "
        f"samples={report['config']['n_selected_samples']} calls={call_count} "
        f"best_char_accuracy={summary['char_accuracy']['mean']:.3f} "
        f"read_success_rate={summary['vlm_read_success_rate']['mean']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
