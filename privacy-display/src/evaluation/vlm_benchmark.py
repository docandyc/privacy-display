"""
VLM readability benchmark for protected display attack frames.

The benchmark is intentionally separate from OCR benchmarks because online VLM
calls are slower, cost-bearing, and require a secret supplied through the shell
environment. Unit tests should inject fake clients instead of calling the API.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import numpy as np

from src.attack.camera_simulator import CameraParams, CameraSimulator
from src.attack.ocr_evaluator import text_recovery_metrics
from src.attack.vlm_evaluator import (
    DEFAULT_SILICONFLOW_BASE_URL,
    DEFAULT_VLM_MODEL,
    VLMClient,
)
from src.evaluation.benchmark import _mean_std, _psnr_db, compose_protected_subframes


DEFAULT_VLM_ATTACKS = (
    "original",
    "global_shutter_slot0",
    "temporal_average_cycle",
    "phase_search_mean",
    "phase_search_max",
    "differential_luma",
    "differential_blue",
    "blue_channel_max",
)
DEFAULT_VLM_RESULT_FILE = "vlm_qwen3_siliconflow.json"


def select_stratified_samples(
    names: list[str],
    metadata: dict | None,
    samples_per_category: int = 1,
    max_samples: int | None = None,
) -> list[int]:
    """Return deterministic sample indices, grouped by metadata category."""
    if samples_per_category <= 0:
        raise ValueError("samples_per_category must be positive")
    if max_samples is not None and max_samples <= 0:
        raise ValueError("max_samples must be positive when provided")

    metadata = metadata or {}
    buckets: dict[str, list[int]] = {}
    for idx, name in enumerate(names):
        category = str(metadata.get(name, {}).get("category", "unknown"))
        buckets.setdefault(category, []).append(idx)

    selected: list[int] = []
    for category in sorted(buckets):
        selected.extend(buckets[category][:samples_per_category])

    if max_samples is not None:
        selected = selected[:max_samples]
    return selected


def build_vlm_attack_frames(
    image: np.ndarray,
    n: int = 4,
    epsilon: float = 8 / 255,
    cycles: int = 2,
    cycle_start: int = 0,
    attacks: list[str] | tuple[str, ...] | None = None,
    with_noise: bool = True,
) -> dict[str, tuple[np.ndarray, dict]]:
    """Build original and protected attack frames for VLM readability checks."""
    if n < 2:
        raise ValueError("n must be at least 2")
    if cycles <= 0:
        raise ValueError("cycles must be positive")

    selected = tuple(attacks or DEFAULT_VLM_ATTACKS)
    unknown = sorted(set(selected) - set(DEFAULT_VLM_ATTACKS))
    if unknown:
        raise ValueError(f"unknown VLM attacks: {', '.join(unknown)}")

    subframes = compose_protected_subframes(
        image,
        n=n,
        epsilon=epsilon,
        cycles=cycles,
        cycle_start=cycle_start,
        with_noise=with_noise,
    )
    cam = CameraSimulator(CameraParams(readout_time=15e-6, exposure_time=1 / 240))
    all_frames: dict[str, tuple[np.ndarray, dict]] = {
        "original": (image.copy(), {"attack": "original"}),
        "global_shutter_slot0": (subframes[0], {"attack": "global_shutter"}),
        "temporal_average_cycle": (
            cam.temporal_averaging_attack(subframes, n, randomize_order=False),
            {"attack": "temporal_average", "frames": n},
        ),
    }
    for name, entry in cam.screen_camera_attack_suite(subframes, cycle_length=n).items():
        all_frames[name] = (entry["frame"], entry["metadata"])

    return {name: all_frames[name] for name in selected}


def summarize_vlm_rows(sample_rows: list[dict], leak_threshold: float = 0.20) -> dict:
    """Summarize VLM readability rows by attack and per-sample worst case."""
    total_calls = len(sample_rows)
    error_calls = int(sum(1 for row in sample_rows if row.get("vlm_error")))
    successful_calls = total_calls - error_calls
    attacks = sorted({row["attack"] for row in sample_rows})
    attack_summary: dict[str, dict] = {}
    for attack in attacks:
        rows = [row for row in sample_rows if row["attack"] == attack]
        sensitive_rows = [
            row for row in rows if int(row.get("sensitive_token_count", 0)) > 0
        ]
        attack_summary[attack] = {
            "char_accuracy": _mean_std([float(row["char_accuracy"]) for row in rows]),
            "word_accuracy": _mean_std([float(row["word_accuracy"]) for row in rows]),
            "exact_match": _mean_std([float(row["exact_match"]) for row in rows]),
            "sensitive_token_recall": {
                "n_samples_with_sensitive_tokens": len(sensitive_rows),
                "stats": _mean_std([
                    float(row["sensitive_token_recall"]) for row in sensitive_rows
                ]),
            },
            "vlm_confidence": _mean_std([
                float(row.get("vlm_confidence", 0.0)) for row in rows
            ]),
            "vlm_read_success_rate": _mean_std([
                float(
                    bool(row.get("vlm_can_read_sensitive", False))
                    or float(row["char_accuracy"]) >= leak_threshold
                )
                for row in rows
            ]),
            "psnr_db": _mean_std([float(row["psnr_db"]) for row in rows]),
            "error_count": int(sum(1 for row in rows if row.get("vlm_error"))),
        }

    best_rows: list[dict] = []
    for sample in sorted({row["name"] for row in sample_rows}):
        rows = [row for row in sample_rows if row["name"] == sample]
        best = max(
            rows,
            key=lambda row: (
                bool(row.get("vlm_can_read_sensitive", False)),
                float(row["char_accuracy"]),
                float(row["word_accuracy"]),
                float(row["sensitive_token_recall"]),
            ),
        )
        best_rows.append(best)

    sensitive_best = [
        row for row in best_rows if int(row.get("sensitive_token_count", 0)) > 0
    ]
    return {
        "call_status": {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "error_calls": error_calls,
            "all_calls_failed": total_calls > 0 and successful_calls == 0,
        },
        "attacks": attack_summary,
        "best_attack_per_sample": {
            "char_accuracy": _mean_std([
                float(row["char_accuracy"]) for row in best_rows
            ]),
            "word_accuracy": _mean_std([
                float(row["word_accuracy"]) for row in best_rows
            ]),
            "exact_match": _mean_std([
                float(row["exact_match"]) for row in best_rows
            ]),
            "sensitive_token_recall": {
                "n_samples_with_sensitive_tokens": len(sensitive_best),
                "stats": _mean_std([
                    float(row["sensitive_token_recall"]) for row in sensitive_best
                ]),
            },
            "vlm_read_success_rate": _mean_std([
                float(
                    bool(row.get("vlm_can_read_sensitive", False))
                    or float(row["char_accuracy"]) >= leak_threshold
                )
                for row in best_rows
            ]),
            "attack_wins": {
                attack: sum(1 for row in best_rows if row["attack"] == attack)
                for attack in attacks
            },
        },
    }


def run_vlm_benchmark(
    client: Any | None = None,
    output_dir: str = "experiments/results",
    n: int = 4,
    epsilon: float = 8 / 255,
    cycles: int = 2,
    samples_per_category: int = 1,
    max_samples: int | None = None,
    attacks: list[str] | tuple[str, ...] | None = None,
    save: bool = True,
    corpus: tuple[list[np.ndarray], list[str], list[str]] | None = None,
    metadata: dict | None = None,
    with_noise: bool = True,
) -> dict:
    """Run a bounded online VLM readability benchmark."""
    if n < 2:
        raise ValueError("n must be at least 2")
    if cycles <= 0:
        raise ValueError("cycles must be positive")
    if samples_per_category <= 0:
        raise ValueError("samples_per_category must be positive")
    if max_samples is not None and max_samples <= 0:
        raise ValueError("max_samples must be positive when provided")

    if corpus is None:
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from experiments.build_corpus import load_corpus, load_corpus_metadata

        images, truths, names = load_corpus()
        corpus_metadata = load_corpus_metadata()
    else:
        images, truths, names = corpus
        corpus_metadata = metadata or {}

    selected_indices = select_stratified_samples(
        names,
        corpus_metadata,
        samples_per_category=samples_per_category,
        max_samples=max_samples,
    )
    selected_attacks = tuple(attacks or DEFAULT_VLM_ATTACKS)
    client = client or VLMClient()

    sample_rows: list[dict] = []
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
            with_noise=with_noise,
        )
        for attack_name, (frame, attack_meta) in attack_frames.items():
            try:
                result = client.analyze_image(frame, ground_truth=truth)
                visible_text = str(result.get("visible_text", "") or "")
                metrics = result.get("metrics") or text_recovery_metrics(visible_text, truth)
                vlm_error = ""
                confidence = float(result.get("confidence", 0.0) or 0.0)
                can_read = bool(result.get("can_read_sensitive", False))
                notes = str(result.get("notes", "") or "")
            except Exception as exc:
                visible_text = ""
                metrics = text_recovery_metrics(visible_text, truth)
                vlm_error = _sanitize_row_error(str(exc))
                confidence = 0.0
                can_read = False
                notes = ""

            sample_rows.append({
                "name": name,
                "sample_order": order,
                "attack": attack_name,
                "metadata": corpus_metadata.get(name, {}),
                "char_accuracy": float(metrics["char_accuracy"]),
                "word_accuracy": float(metrics["word_accuracy"]),
                "exact_match": bool(metrics["exact_match"]),
                "sensitive_token_recall": float(metrics["sensitive_token_recall"]),
                "sensitive_token_count": int(metrics["sensitive_token_count"]),
                "psnr_db": _psnr_db(image, frame),
                "reconstruction_score": float(attack_meta.get("score", 0.0)),
                "attack_metadata": attack_meta,
                "visible_text": visible_text[:240],
                "vlm_can_read_sensitive": can_read,
                "vlm_confidence": confidence,
                "vlm_notes": notes[:240],
                "vlm_error": vlm_error,
            })

    report = {
        "config": {
            "model": getattr(client, "model", DEFAULT_VLM_MODEL),
            "base_url": getattr(client, "base_url", DEFAULT_SILICONFLOW_BASE_URL),
            "n": n,
            "epsilon": epsilon,
            "cycles": cycles,
            "with_noise": with_noise,
            "samples_per_category": samples_per_category,
            "max_samples": max_samples,
            "n_selected_samples": len(selected_indices),
            "attacks": list(selected_attacks),
            "leak_threshold_char_accuracy": 0.20,
        },
        "summary": summarize_vlm_rows(sample_rows),
        "samples": sample_rows,
    }

    if save:
        out = Path(output_dir) / DEFAULT_VLM_RESULT_FILE
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"VLM 可读性评测已保存: {out}")

    return report


def _sanitize_row_error(text: str) -> str:
    out = text
    key = os.environ.get("SILICONFLOW_API_KEY", "")
    if key:
        out = out.replace(key, "[REDACTED]")
    return out.replace("\n", " ").strip()[:500]
