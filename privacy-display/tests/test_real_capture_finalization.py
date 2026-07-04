import json

import pytest

from experiments.finalize_real_capture_artifacts import merge_ocr_position_reports
from src.evaluation.benchmark import BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED


def test_merged_publication_artifact_records_bootstrap_contract(tmp_path):
    result_path = tmp_path / "experiments" / "results_d0.5_a0_final" / "real_capture_ocr.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(
        json.dumps({
            "capture_dir": "experiments/real_captures_d0.5_a0_final",
            "config": {
                "engines": ["test-ocr-a", "test-ocr-b"],
                "ocr_timeout": 30.0,
            },
            "captures": [{
                "id": "capture-1",
                "condition": "original|short",
                "device": "test-camera",
                "ablation": "original",
                "attack": "short",
                "engine": "test-ocr-a",
                "distance_m": 0.5,
                "angle_degrees": 0.0,
                "char_accuracy": 1.0,
                "word_accuracy": 1.0,
                "exact_match": True,
                "sensitive_token_recall": 1.0,
                "sensitive_token_count": 1,
            }, {
                "id": "capture-1",
                "condition": "original|short",
                "device": "test-camera",
                "ablation": "original",
                "attack": "short",
                "engine": "test-ocr-b",
                "distance_m": 0.5,
                "angle_degrees": 0.0,
                "char_accuracy": 0.5,
                "word_accuracy": 0.5,
                "exact_match": False,
                "sensitive_token_recall": 0.5,
                "sensitive_token_count": 1,
            }],
        }),
        encoding="utf-8",
    )

    report = merge_ocr_position_reports(tmp_path, [result_path])

    assert report["config"]["bootstrap"] == {
        "seed": BOOTSTRAP_SEED,
        "resamples": BOOTSTRAP_RESAMPLES,
        "confidence": 0.95,
        "method": "bootstrap_percentile",
        "resampling_unit": "capture",
    }
    assert report["config"]["ocr_timeout"] == 30.0
    assert report["config"]["source_reports"] == [
        "experiments/results_d0.5_a0_final/real_capture_ocr.json"
    ]
    assert "source_results" not in report["config"]
    assert "source_capture_dir" not in report["captures"][0]
    assert "source_result_file" not in report["captures"][0]


def test_merged_publication_artifact_uses_numeric_position_order(tmp_path):
    paths = []
    for label, capture_id, distance in (
        ("d1.5_a0", "capture-far", 1.5),
        ("d1_a0", "capture-mid", 1.0),
    ):
        path = tmp_path / "experiments" / f"results_{label}_final" / "real_capture_ocr.json"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps({
                "capture_dir": f"experiments/real_captures_{label}_final",
                "config": {"engines": ["test-ocr"], "ocr_timeout": 30.0},
                "captures": [{
                    "id": capture_id,
                    "condition": "original|short",
                    "device": "test-camera",
                    "ablation": "original",
                    "attack": "short",
                    "engine": "test-ocr",
                    "distance_m": distance,
                    "angle_degrees": 0.0,
                    "char_accuracy": distance / 2,
                    "word_accuracy": distance / 2,
                    "exact_match": False,
                    "sensitive_token_recall": distance / 2,
                    "sensitive_token_count": 1,
                }],
            }),
            encoding="utf-8",
        )
        paths.append(path)

    report = merge_ocr_position_reports(tmp_path, paths)

    assert [row["position"] for row in report["positions"]] == ["d1_a0", "d1.5_a0"]
    assert [row["id"] for row in report["captures"]] == ["capture-mid", "capture-far"]


def test_merged_publication_artifact_rejects_duplicate_capture_engine_row(tmp_path):
    path = tmp_path / "experiments" / "results_d1_a0_final" / "real_capture_ocr.json"
    path.parent.mkdir(parents=True)
    row = {
        "id": "duplicate-capture",
        "condition": "original|short",
        "device": "test-camera",
        "ablation": "original",
        "attack": "short",
        "engine": "test-ocr",
        "distance_m": 1.0,
        "angle_degrees": 0.0,
        "char_accuracy": 1.0,
        "word_accuracy": 1.0,
        "exact_match": True,
        "sensitive_token_recall": 1.0,
        "sensitive_token_count": 1,
    }
    path.write_text(
        json.dumps({
            "config": {"engines": ["test-ocr"]},
            "captures": [row, row],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate capture/engine row"):
        merge_ocr_position_reports(tmp_path, [path])
