import json

import pytest

from experiments.analyze_paper_ocr_clusters import (
    DEFAULT_RESAMPLES,
    DEFAULT_SEED,
    _descriptive_group_means,
    bootstrap_cluster_mean_ci,
    build_cluster_report,
    collapse_best_of_engines,
    derive_capture_unit,
    paired_contrast,
    render_markdown,
)


def _row(
    *,
    capture_id,
    ablation,
    attack="short",
    engine="tesseract",
    char=0.0,
    exact=False,
    position="d0.5_a0",
):
    return {
        "id": capture_id,
        "image": f"{capture_id}.jpg",
        "engine": engine,
        "condition": f"{ablation}|{attack}",
        "ablation": ablation,
        "attack": attack,
        "position": position,
        "distance_m": 0.5,
        "angle_degrees": 0.0,
        "char_accuracy": char,
        "word_accuracy": char / 2,
        "exact_match": exact,
        "sensitive_token_recall": char / 3,
        "sensitive_token_count": 1,
    }


def _capture_id(ablation, content, repeat="s00", *, stamp="123456", attack="short"):
    return (
        f"emeet_smartcam_s600_{ablation}_{attack}_0deg_0.5m_"
        f"{content}_n4_{stamp}_{repeat}"
    )


def test_collapse_best_of_engines_keeps_attacker_favorable_metrics():
    capture_id = _capture_id("deployed", "account_00")
    rows = [
        _row(capture_id=capture_id, ablation="deployed", engine="tesseract", char=0.1),
        _row(
            capture_id=capture_id,
            ablation="deployed",
            engine="easyocr",
            char=0.8,
            exact=True,
        ),
        _row(capture_id=capture_id, ablation="deployed", engine="surya", char=0.3),
    ]

    collapsed = collapse_best_of_engines(rows)

    assert len(collapsed) == 1
    assert collapsed[0]["engine"] == "best_of"
    assert collapsed[0]["char_accuracy"] == pytest.approx(0.8)
    assert collapsed[0]["word_accuracy"] == pytest.approx(0.4)
    assert collapsed[0]["exact_match"] == 1.0
    assert collapsed[0]["sensitive_token_recall"] == pytest.approx(0.8 / 3)


def test_derive_capture_unit_extracts_content_position_and_repeat():
    unit = derive_capture_unit(_row(
        capture_id=_capture_id("mask_only", "cet6_p1", "s02", stamp="135824"),
        ablation="mask_only",
    ))

    assert unit.profile == "mask_only"
    assert unit.attack == "short"
    assert unit.content_item == "cet6_p1"
    assert unit.position == "d0.5_a0"
    assert unit.repeat_index == "s02"


def test_paired_contrast_matches_content_position_repeat_and_reports_drops():
    rows = collapse_best_of_engines([
        _row(capture_id=_capture_id("original", "account_00", "s00"), ablation="original", char=0.9),
        _row(capture_id=_capture_id("deployed", "account_00", "s00"), ablation="deployed", char=0.2),
        _row(
            capture_id=_capture_id("deployed", "account_00", "s00", stamp="123999"),
            ablation="deployed",
            char=0.4,
        ),
        _row(capture_id=_capture_id("original", "account_01", "s00"), ablation="original", char=0.8),
        _row(capture_id=_capture_id("deployed", "account_01", "s01"), ablation="deployed", char=0.1),
    ])

    result = paired_contrast(
        rows,
        baseline_profile="original",
        treatment_profile="deployed",
        attack="short",
    )

    assert result["matched_unit_count"] == 1
    assert result["cluster_count"] == 1
    assert result["estimate"] == pytest.approx(0.9 - 0.3)
    assert result["matching_rule"] == "profile + attack + content_item + position + repeat_index"
    assert result["unmatched"]["baseline_only"] == 1
    assert result["unmatched"]["treatment_only"] == 1
    assert result["duplicates_collapsed"]["treatment_cells"] == 1
    assert result["duplicates_collapsed"]["treatment_extra_rows"] == 1


def test_bootstrap_cluster_mean_ci_is_deterministic():
    pairs = [
        {"cluster": "a", "delta": 0.1},
        {"cluster": "a", "delta": 0.3},
        {"cluster": "b", "delta": 0.8},
        {"cluster": "c", "delta": 0.4},
    ]

    first = bootstrap_cluster_mean_ci(pairs)
    second = bootstrap_cluster_mean_ci(pairs)

    assert first == second
    assert first["seed"] == DEFAULT_SEED
    assert first["resamples"] == DEFAULT_RESAMPLES
    assert first["resampling_unit"] == "content_item"
    assert first["method"] == "cluster_percentile_bootstrap"
    assert first["low"] <= first["estimate"] <= first["high"]


def test_build_cluster_report_contains_required_json_contract(tmp_path):
    rows = []
    for content, base, deployed, hardened in (
        ("account_00", 0.9, 0.2, 0.05),
        ("account_01", 0.8, 0.1, 0.02),
    ):
        rows.extend([
            _row(capture_id=_capture_id("original", content, "s00"), ablation="original", char=base),
            _row(capture_id=_capture_id("deployed", content, "s00"), ablation="deployed", char=deployed),
            _row(capture_id=_capture_id("vlm", content, "s00"), ablation="vlm", char=hardened),
        ])
    source = tmp_path / "real_capture_ocr.json"
    source.write_text(json.dumps({"captures": rows}), encoding="utf-8")

    report = build_cluster_report(source)

    contrast = report["contrasts"]["original_short_minus_deployed_short"]
    assert contrast["metric"] == "char_accuracy"
    assert contrast["estimate"] == pytest.approx(0.7)
    assert contrast["ci95"]["seed"] == DEFAULT_SEED
    assert contrast["cluster_count"] == 2
    assert contrast["matched_unit_count"] == 2
    assert contrast["resampling_unit"] == "content_item"
    assert "original_short_minus_high_suppression_short" in report["contrasts"]

    primary = report["primary_common_setting"]
    assert primary["excluded_positions"] == []
    assert primary["matched_unit_count_per_profile"] == 2
    assert primary["profiles"]["original"]["char_accuracy_mean"] == pytest.approx(0.85)
    assert primary["profiles"]["deployed"]["char_accuracy_mean"] == pytest.approx(0.15)
    assert primary["profiles"]["high_suppression"]["char_accuracy_mean"] == pytest.approx(0.035)
    assert report["all_available_capture_sensitivity"]["deployed"]["capture_count"] == 2

    markdown = render_markdown(report)
    assert "Matched baseline (%)" in markdown
    assert "Matched treatment (%)" in markdown
    assert "| 85.0 | 15.0 |" in markdown


def test_descriptive_sensitive_token_mean_excludes_rows_without_tokens():
    token_row = _row(
        capture_id=_capture_id("deployed", "account_00"),
        ablation="deployed",
        char=0.3,
    )
    token_row["sensitive_token_recall"] = 1.0
    no_token_row = _row(
        capture_id=_capture_id("deployed", "paragraph_00"),
        ablation="deployed",
        char=0.3,
    )
    no_token_row["sensitive_token_count"] = 0
    no_token_row["sensitive_token_recall"] = 0.0

    summary = _descriptive_group_means([token_row, no_token_row])

    assert summary["deployed|short"]["sensitive_token_recall_mean"] == pytest.approx(1.0)
    assert summary["deployed|short"]["sensitive_token_sample_count"] == 1
