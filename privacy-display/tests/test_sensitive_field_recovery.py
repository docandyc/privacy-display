import json
from pathlib import Path

import pytest

from experiments.analyze_sensitive_field_recovery import (
    collapse_engine_field_recovery,
    load_sensitive_field_manifest,
    normalize_field,
    score_sensitive_fields,
    summarize_cells,
)


ROOT = Path(__file__).resolve().parents[1]


def test_normalize_field_ignores_case_spacing_and_punctuation_only():
    assert normalize_field("Card 4532-1234") == "card45321234"
    assert normalize_field("用户 user@mail.com") == "用户usermailcom"


def test_score_sensitive_fields_reports_micro_counts():
    fields = [
        {"text": "4532-1234-5678-9010", "type": "digit_string"},
        {"text": "CVV 123", "type": "credential"},
    ]

    score = score_sensitive_fields("card 4532 1234 5678 9010", fields)

    assert score == {
        "recovered": 1,
        "total": 2,
        "micro_recall": 0.5,
        "recovered_fields": ["4532-1234-5678-9010"],
    }


def test_manifest_rejects_duplicate_fields(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({
            "schema_version": 1,
            "items": {
                "account_00": {
                    "truth": "Card 4532-1234",
                    "fields": [
                        {"text": "4532-1234", "type": "digit_string"},
                        {"text": "4532 1234", "type": "digit_string"},
                    ],
                }
            },
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate normalized field"):
        load_sensitive_field_manifest(path)


def test_manifest_rejects_field_not_copied_from_truth(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({
            "schema_version": 1,
            "items": {
                "account_00": {
                    "truth": "Card 4532-1234",
                    "fields": [{"text": "9999", "type": "digit_string"}],
                }
            },
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="not present in truth"):
        load_sensitive_field_manifest(path)


def test_engine_collapse_uses_union_of_recovered_fields():
    manifest = {
        "account_00": {
            "truth": "Card 4532-1234 CVV 123",
            "fields": [
                {"text": "4532-1234", "type": "digit_string"},
                {"text": "CVV 123", "type": "credential"},
            ],
        }
    }
    rows = [
        {"id": "capture", "recognized_text": "4532 1234"},
        {"id": "capture", "recognized_text": "cvv123"},
    ]

    collapsed = collapse_engine_field_recovery(rows, "account_00", manifest)

    assert collapsed["recovered"] == 2
    assert collapsed["total"] == 2
    assert collapsed["micro_recall"] == 1.0


def test_summary_separates_field_micro_from_sample_macro():
    cells = [
        {"recovered": 1.0, "total": 1, "sample_recall": 1.0},
        {"recovered": 1.0, "total": 3, "sample_recall": 1 / 3},
        {"recovered": 0.0, "total": 0, "sample_recall": None},
    ]

    summary = summarize_cells(cells)

    assert summary["all_cell_count"] == 3
    assert summary["field_bearing_cell_count"] == 2
    assert summary["field_opportunities"] == 4
    assert summary["micro_exact_recovery"] == pytest.approx(0.5)
    assert summary["sample_macro_exact_recovery"] == pytest.approx(2 / 3)


def test_generated_primary_field_values_are_synchronized_with_manuscript():
    report = json.loads(
        (ROOT / "experiments" / "results" / "sensitive_field_recovery.json").read_text(
            encoding="utf-8"
        )
    )
    manuscript = (ROOT.parent / "paper" / "main.tex").read_text(encoding="utf-8")
    summaries = report["matched_common_short"]["profile_summaries"]

    for profile in ("original", "deployed", "high_suppression"):
        micro = summaries[profile]["micro_exact_recovery"] * 100
        macro = summaries[profile]["sample_macro_exact_recovery"] * 100
        assert f"{micro:.1f}\\% & {macro:.1f}\\%" in manuscript
