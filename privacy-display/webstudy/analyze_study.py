"""Predeclared analysis for the privacy-display WebStudy SQLite database."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

try:  # pragma: no cover - supports both package imports and script execution.
    from .assignment import RATING_CONDITION_ORDER, assignment_bucket_key, assignment_for_registration_index
except ImportError:  # pragma: no cover
    from assignment import RATING_CONDITION_ORDER, assignment_bucket_key, assignment_for_registration_index  # type: ignore


TARGET_N = 24
MIN_REFRESH_HZ = 200.0
MIN_CONTROL_ACCURACY = 0.50
MIN_ATTEMPTED_CHARS_PER_TRIAL = 5
MIN_RATING_QUALITY_VIEW_MS = 11_000
CONDITIONS = RATING_CONDITION_ORDER
RATING_DIMENSIONS = ("readability", "flicker", "fatigue")
TYPING_METRICS = ("wpm", "cpm", "accuracy", "attempted_chars", "first_key_latency_ms")
DEFAULT_DB_PATH = Path(__file__).with_name("study_formal.db")


def parse_meta(raw: str | None) -> dict[str, Any]:
    try:
        value = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def mean(values: list[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return float(np.mean(clean)) if clean else None


def is_straightline_rating_row(row: sqlite3.Row) -> bool:
    values = [int(row[dimension]) for dimension in RATING_DIMENSIONS]
    return len(set(values)) == 1


def has_minimum_view_straightline_ratings(ratings: list[sqlite3.Row]) -> bool:
    if len(ratings) != len(CONDITIONS):
        return False
    return all(
        int(row["view_duration_ms"] or 0) <= MIN_RATING_QUALITY_VIEW_MS
        and is_straightline_rating_row(row)
        for row in ratings
    )


def participant_exclusions(participant: sqlite3.Row, typing: list[sqlite3.Row], ratings: list[sqlite3.Row]) -> list[str]:
    reasons: list[str] = []
    if participant["debug"]:
        reasons.append("debug_session")
    if participant["demo"]:
        reasons.append("demo_session")
    if not participant["refresh_ok"] or float(participant["refresh_hz"] or 0) < MIN_REFRESH_HZ:
        reasons.append("refresh_below_200hz")
    counts = Counter(row["condition"] for row in typing)
    if len(typing) != 4 or counts != Counter({"control": 2, "masked": 2}):
        reasons.append("incomplete_typing")
    rating_labels = {row["condition_label"] for row in ratings}
    if len(ratings) != 6 or rating_labels != set(CONDITIONS):
        reasons.append("incomplete_ratings")
    elif has_minimum_view_straightline_ratings(ratings):
        reasons.append("rating_straightline_minimum_view")
    control_accuracy = mean([row["accuracy"] for row in typing if row["condition"] == "control"])
    if control_accuracy is not None and control_accuracy < MIN_CONTROL_ACCURACY:
        reasons.append("control_accuracy_below_50pct")
    if any(int(row["attempted_chars"] or 0) < MIN_ATTEMPTED_CHARS_PER_TRIAL for row in typing):
        reasons.append("typing_trial_below_5_attempted_chars")
    for row in typing:
        if row["condition"] != "masked":
            continue
        meta = parse_meta(row["mask_meta_json"])
        if meta.get("mode") != "temporal":
            reasons.append("masked_trial_not_temporal")
            break
        observed = meta.get("observed_effective_cycle_hz")
        if observed is not None and float(observed) < 50.0:
            reasons.append("observed_cycle_below_50hz")
            break
    return sorted(set(reasons))


def bootstrap_mean_ci(values: np.ndarray, samples: int, rng: np.random.Generator) -> list[float | None]:
    if values.size == 0:
        return [None, None]
    draws = rng.choice(values, size=(samples, values.size), replace=True).mean(axis=1)
    low, high = np.quantile(draws, [0.025, 0.975])
    return [float(low), float(high)]


def rank_biserial(differences: np.ndarray) -> float | None:
    nonzero = differences[differences != 0]
    if nonzero.size == 0:
        return 0.0
    ranks = stats.rankdata(np.abs(nonzero))
    positive = float(ranks[nonzero > 0].sum())
    negative = float(ranks[nonzero < 0].sum())
    total = positive + negative
    return (positive - negative) / total if total else None


def paired_inference(control: list[float], masked: list[float], bootstrap_samples: int, rng: np.random.Generator) -> dict[str, Any]:
    a = np.asarray(control, dtype=float)
    b = np.asarray(masked, dtype=float)
    differences = b - a
    normality_p = None
    if 3 <= differences.size <= 5000 and not np.allclose(differences, differences[0]):
        normality_p = float(stats.shapiro(differences).pvalue)
    use_t = differences.size >= 2 and (normality_p is None or normality_p >= 0.05)
    if differences.size < 2:
        test_name, statistic, p_value, effect_name, effect = "insufficient_n", None, None, None, None
    elif use_t:
        sd = float(np.std(differences, ddof=1))
        effect_name = "cohen_dz"
        if sd == 0:
            statistic = 0.0 if np.allclose(differences, 0) else None
            p_value = 1.0 if np.allclose(differences, 0) else 0.0
            effect = 0.0 if np.allclose(differences, 0) else None
        else:
            test = stats.ttest_rel(b, a)
            statistic, p_value = float(test.statistic), float(test.pvalue)
            effect = float(np.mean(differences) / sd)
        test_name = "paired_t"
    else:
        if np.allclose(differences, 0):
            statistic, p_value = 0.0, 1.0
        else:
            result = stats.wilcoxon(b, a, alternative="two-sided")
            statistic, p_value = float(result.statistic), float(result.pvalue)
        test_name, effect_name, effect = "wilcoxon_signed_rank", "rank_biserial", rank_biserial(differences)
    return {
        "n": int(differences.size),
        "control_mean": float(np.mean(a)) if a.size else None,
        "masked_mean": float(np.mean(b)) if b.size else None,
        "paired_difference_masked_minus_control": float(np.mean(differences)) if differences.size else None,
        "difference_95ci": bootstrap_mean_ci(differences, bootstrap_samples, rng),
        "normality_shapiro_p": normality_p,
        "test": test_name,
        "statistic": statistic,
        "p_value": p_value,
        "effect_name": effect_name,
        "effect": effect,
    }


def holm_adjust(p_values: list[float]) -> list[float]:
    order = np.argsort(p_values)
    adjusted = [1.0] * len(p_values)
    running = 0.0
    total = len(p_values)
    for rank, index in enumerate(order):
        candidate = min(1.0, (total - rank) * p_values[index])
        running = max(running, candidate)
        adjusted[index] = running
    return adjusted


def rating_inference(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for dimension in RATING_DIMENSIONS:
        arrays = [np.asarray([row[condition][dimension] for row in rows], dtype=float) for condition in CONDITIONS]
        if len(rows) < 2:
            statistic, p_value = None, None
        elif np.allclose(np.stack(arrays), arrays[0]):
            statistic, p_value = 0.0, 1.0
        else:
            omnibus = stats.friedmanchisquare(*arrays)
            statistic, p_value = float(omnibus.statistic), float(omnibus.pvalue)
        pairs = []
        raw_p = []
        for left in range(len(CONDITIONS)):
            for right in range(left + 1, len(CONDITIONS)):
                differences = arrays[right] - arrays[left]
                if len(rows) < 2:
                    pair_stat, pair_p = None, 1.0
                elif np.allclose(differences, 0):
                    pair_stat, pair_p = 0.0, 1.0
                else:
                    test = stats.wilcoxon(arrays[right], arrays[left], alternative="two-sided")
                    pair_stat, pair_p = float(test.statistic), float(test.pvalue)
                pairs.append({
                    "left": CONDITIONS[left],
                    "right": CONDITIONS[right],
                    "statistic": pair_stat,
                    "p_value": pair_p,
                    "rank_biserial": rank_biserial(differences),
                })
                raw_p.append(pair_p)
        for pair, adjusted in zip(pairs, holm_adjust(raw_p), strict=True):
            pair["holm_p"] = adjusted
        result[dimension] = {
            "friedman_statistic": statistic,
            "friedman_p": p_value,
            "pairwise_wilcoxon_holm": pairs,
        }
    return result


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float | None, digits: int = 2) -> str:
    return "--" if value is None or not math.isfinite(value) else f"{value:.{digits}f}"


def write_latex_tables(output_dir: Path, typing_report: dict[str, Any], rating_summary: dict[str, Any]) -> None:
    typing_lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"指标 & Control & Masked & 配对差（95\% CI） & 检验 \\",
        r"\midrule",
    ]
    labels = {
        "wpm": "WPM",
        "cpm": "CPM",
        "accuracy": "Accuracy",
        "attempted_chars": "尝试字符数",
        "first_key_latency_ms": "首击延迟(ms)",
    }
    for metric in TYPING_METRICS:
        row = typing_report[metric]
        ci = row["difference_95ci"]
        typing_lines.append(
            f"{labels[metric]} & {fmt(row['control_mean'])} & {fmt(row['masked_mean'])} & "
            f"{fmt(row['paired_difference_masked_minus_control'])} [{fmt(ci[0])}, {fmt(ci[1])}] & "
            f"{row['test']} ($p={fmt(row['p_value'], 3)}$) \\\\"
        )
    typing_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (output_dir / "typing_table.tex").write_text("\n".join(typing_lines), encoding="utf-8")

    rating_lines = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"条件 & 可读性 & 稳定感 & 即时视觉舒适感 \\",
        r"\midrule",
    ]
    for condition in CONDITIONS:
        values = rating_summary[condition]
        rating_lines.append(
            condition.replace("_", r"\_") + " & " + " & ".join(
                f"{fmt(values[dimension]['mean'])} $\\pm$ {fmt(values[dimension]['sd'])}"
                for dimension in RATING_DIMENSIONS
            ) + r" \\"
        )
    rating_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (output_dir / "ratings_table.tex").write_text("\n".join(rating_lines), encoding="utf-8")


def assignment_balance(participants: list[sqlite3.Row]) -> dict[str, Any]:
    formal = [
        participant for participant in participants
        if not participant["debug"] and not participant["demo"] and int(participant["registration_index"]) >= 0
    ]
    typing_counts = Counter()
    rating_counts = Counter()
    joint_counts = Counter()
    for participant in formal:
        assignment = assignment_for_registration_index(int(participant["registration_index"]))
        typing_counts[str(assignment["typing_order_index"])] += 1
        rating_counts[str(assignment["rating_order_index"])] += 1
        joint_counts[assignment_bucket_key(assignment)] += 1
    return {
        "formal_n": len(formal),
        "typing_order": dict(sorted(typing_counts.items())),
        "rating_order": dict(sorted(rating_counts.items(), key=lambda item: int(item[0]))),
        "joint_buckets": dict(sorted(joint_counts.items())),
    }


def analyze_study(db_path: str | Path, output_dir: str | Path, *, bootstrap_samples: int = 10_000) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260703)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        participants = conn.execute("SELECT * FROM participants ORDER BY id").fetchall()
        typing_by_id = {
            int(row["id"]): conn.execute("SELECT * FROM typing WHERE participant_id = ? ORDER BY trial_index", (row["id"],)).fetchall()
            for row in participants
        }
        ratings_by_id = {
            int(row["id"]): conn.execute("SELECT * FROM ratings WHERE participant_id = ? ORDER BY order_index", (row["id"],)).fetchall()
            for row in participants
        }

    exclusions = []
    included = []
    for participant in participants:
        pid = int(participant["id"])
        reasons = participant_exclusions(participant, typing_by_id[pid], ratings_by_id[pid])
        if reasons:
            exclusions.append({"participant_id": pid, "reasons": reasons})
        else:
            included.append(participant)

    typing_means = []
    rating_matrix = []
    for code_index, participant in enumerate(included, start=1):
        pid = int(participant["id"])
        row: dict[str, Any] = {
            "participant_code": f"P{code_index:03d}",
            "participant_id": pid,
            "registration_index": participant["registration_index"],
        }
        for condition in ("control", "masked"):
            condition_rows = [item for item in typing_by_id[pid] if item["condition"] == condition]
            for metric in TYPING_METRICS:
                row[f"{condition}_{metric}"] = mean([item[metric] for item in condition_rows])
        typing_means.append(row)
        by_condition = {item["condition_label"]: item for item in ratings_by_id[pid]}
        rating_matrix.append({
            condition: {dimension: int(by_condition[condition][dimension]) for dimension in RATING_DIMENSIONS}
            for condition in CONDITIONS
        })

    typing_report = {}
    for metric in TYPING_METRICS:
        valid = [row for row in typing_means if row[f"control_{metric}"] is not None and row[f"masked_{metric}"] is not None]
        typing_report[metric] = paired_inference(
            [row[f"control_{metric}"] for row in valid],
            [row[f"masked_{metric}"] for row in valid],
            bootstrap_samples,
            rng,
        )

    rating_summary = {
        condition: {
            dimension: {
                "mean": float(np.mean([row[condition][dimension] for row in rating_matrix])) if rating_matrix else None,
                "sd": float(np.std([row[condition][dimension] for row in rating_matrix], ddof=1)) if len(rating_matrix) > 1 else None,
            }
            for dimension in RATING_DIMENSIONS
        }
        for condition in CONDITIONS
    }
    report = {
        "analysis_plan": {
            "target_n": TARGET_N,
            "unit_of_analysis": "participant means across two repetitions per typing condition",
            "typing": "paired t if Shapiro p>=.05, otherwise Wilcoxon; effect size and participant bootstrap CI",
            "ratings": "Friedman plus pairwise Wilcoxon with Holm correction",
            "exclusions": [
                "debug/demo", "incomplete rows", "refresh <200Hz", "control accuracy <50%",
                "any typing trial with attempted_chars <5", "non-temporal masked trial",
                "observed effective base cycle <50Hz", "minimum-view straight-line ratings",
            ],
        },
        "sample": {
            "target_n": TARGET_N,
            "submitted": len(participants),
            "included": len(included),
            "excluded": len(exclusions),
            "exclusion_audit": exclusions,
        },
        "typing": typing_report,
        "rating_summary": rating_summary,
        "rating_inference": rating_inference(rating_matrix) if rating_matrix else {},
        "assignment_balance": assignment_balance(participants),
        "exclusions": dict(Counter(reason for item in exclusions for reason in item["reasons"])),
    }
    fields = ["participant_code", "participant_id", "registration_index"] + [
        f"{condition}_{metric}" for condition in ("control", "masked") for metric in TYPING_METRICS
    ]
    write_csv(output / "typing_participant_means.csv", typing_means, fields)
    write_latex_tables(output, typing_report, rating_summary)
    (output / "analysis_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze privacy-display WebStudy data")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output", default=str(Path(__file__).with_name("analysis_output")))
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    args = parser.parse_args()
    report = analyze_study(args.db, args.output, bootstrap_samples=max(100, args.bootstrap_samples))
    print(json.dumps(report["sample"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
