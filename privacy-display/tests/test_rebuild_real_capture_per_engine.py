from __future__ import annotations

import pytest

from scripts.rebuild_real_capture_per_engine import (
    BOOTSTRAP_SEED,
    average_duplicate_capture_units,
    build_per_engine_summary,
)


def _capture_id(
    content: str,
    repeat: str,
    *,
    stamp: str,
) -> str:
    return (
        "emeet_smartcam_s600_deployed_short_0deg_0.5m_"
        f"{content}_n4_{stamp}_{repeat}"
    )


def _row(
    content: str,
    repeat: str,
    *,
    stamp: str,
    char_accuracy: float,
    exact_match: float,
    sensitive_token_recall: float,
) -> dict:
    capture_id = _capture_id(content, repeat, stamp=stamp)
    return {
        "id": capture_id,
        "image": f"{capture_id}.jpg",
        "ablation": "deployed",
        "attack": "short",
        "position": "d0.5_a0",
        "engine": "tesseract",
        "char_accuracy": char_accuracy,
        "exact_match": exact_match,
        "sensitive_token_recall": sensitive_token_recall,
    }


def test_per_engine_summary_averages_duplicate_capture_units_before_statistics():
    captures = [
        _row(
            "account_00",
            "s00",
            stamp="100000",
            char_accuracy=0.2,
            exact_match=0.0,
            sensitive_token_recall=0.2,
        ),
        _row(
            "account_00",
            "s00",
            stamp="200000",
            char_accuracy=0.6,
            exact_match=1.0,
            sensitive_token_recall=0.6,
        ),
        _row(
            "account_01",
            "s00",
            stamp="100000",
            char_accuracy=0.8,
            exact_match=0.0,
            sensitive_token_recall=0.8,
        ),
    ]

    values = average_duplicate_capture_units(captures, "char_accuracy")
    report = build_per_engine_summary(captures)
    entry = report["deployed|short|tesseract"]

    assert values == pytest.approx([0.4, 0.8])
    assert entry["char_accuracy"]["mean"] == pytest.approx(0.6)
    assert entry["exact_match"]["mean"] == pytest.approx(0.25)
    assert entry["sensitive_token_recall"]["mean"] == pytest.approx(0.6)
    assert entry["leak_rate_char_ge_20pct"]["mean"] == pytest.approx(1.0)
    for metric in (
        "char_accuracy",
        "exact_match",
        "sensitive_token_recall",
        "leak_rate_char_ge_20pct",
    ):
        assert entry[metric]["count"] == 2
        assert entry[metric]["raw_count"] == 3
        assert entry[metric]["duplicate_extra_rows"] == 1
        assert entry[metric]["ci95"]["seed"] == BOOTSTRAP_SEED
        assert (
            entry[metric]["ci95"]["resampling_unit"]
            == "duplicate_averaged_capture_unit"
        )


def test_per_engine_duplicate_bootstrap_is_deterministic():
    captures = [
        _row(
            f"account_{index:02d}",
            "s00",
            stamp="100000",
            char_accuracy=value,
            exact_match=0.0,
            sensitive_token_recall=value,
        )
        for index, value in enumerate((0.1, 0.3, 0.7, 0.9))
    ]

    first = build_per_engine_summary(captures)
    second = build_per_engine_summary(list(reversed(captures)))

    assert first == second


def test_best_of_engine_is_reduced_per_capture_before_duplicate_averaging():
    captures = [
        _row(
            "account_00",
            "s00",
            stamp="100000",
            char_accuracy=0.2,
            exact_match=0.0,
            sensitive_token_recall=0.1,
        ),
        _row(
            "account_00",
            "s00",
            stamp="200000",
            char_accuracy=0.4,
            exact_match=0.0,
            sensitive_token_recall=0.2,
        ),
        _row(
            "account_01",
            "s00",
            stamp="100000",
            char_accuracy=0.1,
            exact_match=0.0,
            sensitive_token_recall=0.1,
        ),
    ]
    easyocr_values = ((0.6, 0.0), (0.8, 1.0), (0.3, 0.0))
    for source, (char_accuracy, exact_match) in zip(
        list(captures),
        easyocr_values,
        strict=True,
    ):
        easyocr = dict(source)
        easyocr["engine"] = "easyocr"
        easyocr["char_accuracy"] = char_accuracy
        easyocr["exact_match"] = exact_match
        captures.append(easyocr)

    report = build_per_engine_summary(captures)
    best = report["deployed|short|best_of"]

    assert best["char_accuracy"]["mean"] == pytest.approx(0.5)
    assert best["exact_match"]["mean"] == pytest.approx(0.25)
    assert best["char_accuracy"]["count"] == 2
    assert best["char_accuracy"]["raw_count"] == 3
    assert best["char_accuracy"]["duplicate_extra_rows"] == 1
