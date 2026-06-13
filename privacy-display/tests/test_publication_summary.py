import json

from src.evaluation.publication_summary import (
    SUMMARY_JSON,
    SUMMARY_MD,
    build_publication_summary,
    render_markdown,
    write_publication_summary,
)


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_publication_summary_builds_tables_and_marks_missing_vlm(tmp_path):
    _write_json(
        tmp_path / "corpus_multi_engine.json",
        {
            "tesseract": {
                "n_samples": 2,
                "n_categories": 1,
                "original_mean": 0.9,
                "original_std": 0.1,
                "original_ci95": {"low": 0.8, "high": 1.0, "confidence": 0.95, "method": "bootstrap"},
                "subframe_mean": 0.0,
                "subframe_std": 0.0,
                "subframe_ci95": {"low": 0.0, "high": 0.0, "confidence": 0.95, "method": "bootstrap"},
                "paired_reduction": {
                    "mean": 0.9,
                    "ci95": {"low": 0.8, "high": 1.0, "confidence": 0.95, "method": "bootstrap"},
                },
                "recovery_metrics": {
                    "word_accuracy": {"subframe": {"mean": 0.0}},
                    "exact_match": {"subframe": {"mean": 0.0}},
                    "sensitive_token_recall": {
                        "n_samples_with_sensitive_tokens": 1,
                        "subframe": {"mean": 0.0},
                    },
                },
            }
        },
    )
    _write_json(
        tmp_path / "corpus_strong_camera_attack.json",
        {
            "config": {"n": 4, "n_samples": 2},
            "summary": {
                "attacks": {
                    "global_shutter_slot0": {
                        "char_accuracy": {"mean": 0.0, "ci95": {"low": 0.0, "high": 0.0, "method": "bootstrap"}},
                        "exact_match": {"mean": 0.0},
                        "sensitive_token_recall": {"stats": {"mean": 0.0}},
                        "leak_rate_char_ge_20pct": {"mean": 0.0},
                    },
                    "phase_search_mean": {
                        "char_accuracy": {"mean": 0.95, "ci95": {"low": 0.9, "high": 0.99, "method": "bootstrap"}},
                        "exact_match": {"mean": 0.8},
                        "sensitive_token_recall": {"stats": {"mean": 1.0}},
                        "leak_rate_char_ge_20pct": {"mean": 1.0},
                    },
                },
                "best_attack_per_sample": {
                    "char_accuracy": {"mean": 0.96, "ci95": {"low": 0.91, "high": 1.0, "method": "bootstrap"}},
                    "exact_match": {"mean": 0.85},
                    "sensitive_token_recall": {"stats": {"mean": 1.0}},
                    "leak_rate_char_ge_20pct": {"mean": 1.0},
                    "attack_wins": {"phase_search_mean": 2},
                },
            },
        },
    )
    _write_json(
        tmp_path / "detection_attack_yolo.json",
        {
            "engine": "ultralytics-yolo",
            "yolo": {"model": "yolov8n.pt"},
            "original_reference_boxes": 5,
            "single_subframe": {"precision": 0.67, "recall": 0.4, "f1": 0.5, "map50": 0.4, "prediction_boxes": 3, "status": "ok"},
            "temporal_average": {"precision": 1.0, "recall": 1.0, "f1": 1.0, "map50": 1.0, "prediction_boxes": 5, "status": "ok"},
        },
    )

    summary = build_publication_summary(tmp_path)
    markdown = render_markdown(summary)

    assert summary["ocr"]["engines"][0]["engine"] == "tesseract"
    assert summary["strong_camera"]["best_attack_per_sample"]["char_accuracy"] == 0.96
    assert summary["detection"]["single_subframe"]["map50"] == 0.4
    assert summary["view_attack"]["available"] is False
    assert summary["vlm"]["available"] is False
    assert summary["real_capture"]["available"] is False
    assert "VLM Readability" in markdown
    assert "Real Camera Capture" in markdown
    assert "Not available" in markdown
    assert "90.0%" in markdown


def test_write_publication_summary_emits_json_and_markdown(tmp_path):
    summary = {
        "source_files": {"ocr": "a.json", "strong_camera": "b.json", "detection": None, "view_attack": None, "vlm": None, "real_capture": None},
        "ocr": {"engines": []},
        "strong_camera": {"attacks": [], "best_attack_per_sample": {
            "char_accuracy": 0.0,
            "char_accuracy_ci95": {"low": 0.0, "high": 0.0, "method": "degenerate"},
            "exact_match": 0.0,
            "sensitive_token_recall": 0.0,
            "leak_rate_char_ge_20pct": 0.0,
        }},
        "detection": {"available": False},
        "view_attack": {"available": False},
        "vlm": {"available": False, "interpretation": "missing"},
        "real_capture": {"available": False, "interpretation": "missing"},
    }

    write_publication_summary(tmp_path, summary=summary)

    assert (tmp_path / SUMMARY_JSON).exists()
    assert (tmp_path / SUMMARY_MD).exists()
    assert json.loads((tmp_path / SUMMARY_JSON).read_text(encoding="utf-8"))["ocr"]["engines"] == []


def test_publication_summary_marks_all_error_vlm_result_uncitable(tmp_path):
    _write_json(tmp_path / "corpus_multi_engine.json", {})
    _write_json(
        tmp_path / "corpus_strong_camera_attack.json",
        {
            "summary": {
                "attacks": {},
                "best_attack_per_sample": {},
            }
        },
    )
    _write_json(
        tmp_path / "vlm_qwen3_siliconflow.json",
        {
            "config": {"model": "Qwen/Qwen3-VL-32B-Instruct"},
            "samples": [
                {
                    "attack": "original",
                    "vlm_error": "VLM API request failed",
                    "char_accuracy": 0.0,
                }
            ],
            "summary": {"best_attack_per_sample": {}},
        },
    )

    summary = build_publication_summary(tmp_path)
    markdown = render_markdown(summary)

    assert summary["source_files"]["vlm"] == "vlm_qwen3_siliconflow.json"
    assert summary["vlm"]["available"] is False
    assert summary["vlm"]["reason"] == "all_calls_failed"
    assert "all live API calls failed" in markdown
