import json

from src.evaluation.publication_summary import (
    SUMMARY_JSON,
    SUMMARY_MD,
    build_publication_summary,
    render_markdown,
    summarize_real_capture,
    summarize_real_capture_coco_detection,
    summarize_real_capture_mot_detection,
    summarize_supplemental_ablation,
    summarize_ocr_strata,
    summarize_pareto_security,
    summarize_vlm_model_ablation,
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
    _write_json(
        tmp_path / "component_ablation.json",
        {
            "config": {"n_samples": 2},
            "summary": {
                "single_mask_only": {"mean": 0.0, "std": 0.0},
                "long_exposure_no_inv": {"mean": 0.9, "std": 0.1},
            },
        },
    )
    _write_json(
        tmp_path / "coco_detection_attack.json",
        {
            "config": {"models": ["fake"], "attacks": ["clean"]},
            "results": {
                "fake": {
                    "clean": {
                        "map": 0.75,
                        "map50": 0.9,
                        "map75": 0.8,
                        "ap_small": 0.4,
                        "ap_medium": 0.7,
                        "ap_large": 0.85,
                        "ar": 0.8,
                        "n_images": 2,
                    }
                }
            },
        },
    )
    _write_json(
        tmp_path / "mot_video_detection.json",
        {
            "config": {"sequences": ["MOT17-02"]},
            "results": {
                "fake": {
                    "clean": {
                        "map": 0.6,
                        "map50": 0.8,
                        "recall": 0.7,
                        "precision": 0.9,
                        "n_frames": 3,
                    }
                }
            },
        },
    )
    _write_json(
        tmp_path / "mot_tracking_attack.json",
        {
            "config": {"sequences": ["MOT17-02"], "tracker": "greedy_bytetrack_fallback"},
            "results": {
                "fake": {
                    "clean": {
                        "mota": 0.5,
                        "motp": 0.75,
                        "idf1": 0.65,
                        "hota": None,
                        "n_frames": 3,
                    }
                }
            },
        },
    )

    summary = build_publication_summary(tmp_path)
    markdown = render_markdown(summary)

    assert summary["ocr"]["engines"][0]["engine"] == "tesseract"
    assert summary["strong_camera"]["best_attack_per_sample"]["char_accuracy"] == 0.96
    assert summary["detection"]["single_subframe"]["map50"] == 0.4
    assert summary["coco_detection"]["available"] is True
    assert summary["coco_detection"]["rows"][0]["map"] == 0.75
    assert summary["mot_video_detection"]["rows"][0]["recall"] == 0.7
    assert summary["mot_tracking"]["rows"][0]["idf1"] == 0.65
    assert summary["view_attack"]["available"] is False
    assert summary["vlm"]["available"] is False
    assert summary["real_capture"]["available"] is False
    assert summary["supplemental_ablations"]["component_ablation"]["available"] is True
    assert summary["supplemental_ablations"]["perceptual_ablation"]["available"] is False
    assert "VLM Readability" in markdown
    assert "Real Camera Capture" in markdown
    assert "Supplemental Ablations" in markdown
    assert "COCO Detection Suite" in markdown
    assert "MOT17 Video Detection" in markdown
    assert "MOT17 Tracking" in markdown
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
        "coco_detection": {"available": False},
        "mot_video_detection": {"available": False},
        "mot_tracking": {"available": False},
        "view_attack": {"available": False},
        "vlm": {"available": False, "interpretation": "missing"},
        "real_capture": {"available": False, "interpretation": "missing"},
        "supplemental_ablations": {},
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


def test_real_capture_detection_summary_rejects_uncitable_coverage():
    report = {
        "config": {"models": ["fake"], "attacks": ["real_clean", "real_short"]},
        "capture": {"coverage": {"complete": False, "reason": "missing real_short"}},
        "results": {
            "fake": {
                "real_clean": {"map": 0.8, "map50": 0.9, "n_images": 2},
                "real_short": {"map": 0.1, "map50": 0.2, "n_images": 1},
            }
        },
    }

    out = summarize_real_capture_coco_detection(report)

    assert out["available"] is False
    assert out["reason"] == "incomplete_capture_coverage"


def test_real_capture_detection_summary_requires_clean_baseline_and_samples():
    report = {
        "config": {"models": ["fake"], "attacks": ["real_short"]},
        "capture": {"coverage": {"complete": True, "n_shared": 0}},
        "results": {"fake": {"real_short": {"map": 0.0, "map50": 0.0, "n_images": 0}}},
    }

    out = summarize_real_capture_coco_detection(report)

    assert out["available"] is False
    assert out["reason"] == "missing_real_clean_baseline"


def test_real_capture_mot_summary_rejects_mismatched_sample_counts():
    report = {
        "config": {"models": ["fake"], "attacks": ["real_clean", "real_short"]},
        "results": {
            "fake": {
                "real_clean": {"map": 0.8, "map50": 0.9, "n_frames": 3},
                "real_short": {"map": 0.1, "map50": 0.2, "n_frames": 2},
            }
        },
    }

    out = summarize_real_capture_mot_detection(report)

    assert out["available"] is False
    assert out["reason"] == "mismatched_sample_counts"


def test_real_capture_summary_surfaces_position_matrix():
    report = {
        "config": {"n_captures": 2350, "n_rows": 2350, "n_positions": 2},
        "positions": [
            {
                "position": "d0.5_a0",
                "distance_m": 0.5,
                "angle_degrees": 0.0,
                "n_captures": 1175,
                "n_rows": 1175,
                "capture_dir": "experiments/real_captures_d0.5_a0_final",
                "source_result_file": "experiments/results_d0.5_a0_final/real_capture_ocr.json",
            },
            {
                "position": "d1_a15",
                "distance_m": 1.0,
                "angle_degrees": 15.0,
                "n_captures": 1175,
                "n_rows": 1175,
                "capture_dir": "experiments/real_captures_d1_a15_final",
                "source_result_file": "experiments/results_d1_a15_final/real_capture_ocr.json",
            },
        ],
        "summary": {
            "by_condition": {
                "deployed|short": {
                    "char_accuracy": {"mean": 0.04, "count": 102},
                    "exact_match": {"mean": 0.0},
                    "sensitive_token_recall": {"mean": 0.01},
                    "leak_rate_char_ge_20pct": {"mean": 0.02},
                }
            }
        },
    }

    out = summarize_real_capture(report)

    assert out["available"] is True
    assert len(out["positions"]) == 2
    assert out["positions"][0]["position"] == "d0.5_a0"
    assert out["positions"][1]["n_captures"] == 1175


def test_anti_ocr_supplemental_rows_prioritize_profile_and_alpha_sweep():
    report = {
        "summary": {
            "block1/off": {
                "headline_metric": "temporal_average",
                "char_accuracy": {"mean": 0.90, "ci95": {"low": 0.80, "high": 1.0, "method": "bootstrap"}},
                "exact_match": {"mean": 0.50, "ci95": {"low": 0.25, "high": 0.75, "method": "bootstrap"}},
                "best_observed_char": {"mean": 0.95},
                "single_frame_char": {"mean": 0.0},
            },
            "block1/strong@overlay": {"char_accuracy": {"mean": 0.88}},
            "block1/strong@deployed": {"char_accuracy": {"mean": 0.82}},
            "block1/vlm": {"char_accuracy": {"mean": 0.55}},
            "block2/s0.00_g0.00": {"char_accuracy": {"mean": 0.91}},
            "block2/s0.00_g0.12": {"char_accuracy": {"mean": 0.90}},
            "block2/s0.00_g0.22": {"char_accuracy": {"mean": 0.89}},
            "block2/s0.10_g0.00": {"char_accuracy": {"mean": 0.90}},
            "block2/s0.10_g0.12": {"char_accuracy": {"mean": 0.87}},
            "block2/s0.10_g0.22": {"char_accuracy": {"mean": 0.86}},
            "block2/s0.18_g0.00": {"char_accuracy": {"mean": 0.89}},
            "block2/s0.18_g0.12": {"char_accuracy": {"mean": 0.86}},
            "block2/s0.18_g0.22": {"char_accuracy": {"mean": 0.84}},
            "block2/s0.30_g0.00": {"char_accuracy": {"mean": 0.88}},
            "block2/s0.30_g0.12": {"char_accuracy": {"mean": 0.83}},
            "block2/s0.30_g0.22": {"char_accuracy": {"mean": 0.80}},
            "block3/alpha_0.0": {"char_accuracy": {"mean": 0.87}},
            "block3/alpha_0.2": {
                "headline_metric": "long_exposure",
                "char_accuracy": {"mean": 0.82},
                "inversion_frame_attack_char": {"mean": 0.72},
            },
            "block3/alpha_0.5": {"char_accuracy": {"mean": 0.70}},
            "block3/alpha_1.0": {"char_accuracy": {"mean": 0.58}},
        }
    }

    rows = summarize_supplemental_ablation(
        report,
        "anti_ocr_profile_ablation.json",
    )["rows"]
    names = [row["name"] for row in rows]

    assert len(rows) == 12
    assert names[:4] == [
        "block1/off",
        "block1/strong@overlay",
        "block1/strong@deployed",
        "block1/capture_hardened",
    ]
    assert rows[0]["headline_metric"] == "temporal_average"
    assert rows[0]["exact_match"] == 0.50
    assert rows[0]["best_observed_char"] == 0.95
    assert "block2/s0.10_g0.12" in names
    assert "block3/alpha_0.2" in names
    assert "block3/alpha_1.0" in names
    alpha_row = rows[names.index("block3/alpha_0.2")]
    assert alpha_row["headline_metric"] == "long_exposure"
    assert alpha_row["inversion_frame_attack_char"] == 0.72


def test_summarize_ocr_strata_surfaces_per_stratum_rows():
    report = {
        "tesseract": {
            "strata": {
                "category": {
                    "code": {
                        "original": {"mean": 0.9, "count": 10, "ci95": {"low": 0.85, "high": 0.95, "method": "bootstrap"}},
                        "subframe": {"mean": 0.0, "count": 10, "ci95": {"low": 0.0, "high": 0.0, "method": "bootstrap"}},
                        "reduction": {"mean": 0.9},
                    }
                }
            }
        }
    }
    out = summarize_ocr_strata(report)
    assert out["available"] is True
    assert out["engine"] == "tesseract"
    row = out["fields"]["category"][0]
    assert row["value"] == "code"
    assert row["original_mean"] == 0.9
    assert row["subframe_mean"] == 0.0
    assert row["original_ci95"]["method"] == "bootstrap"


def test_summarize_ocr_strata_handles_missing_strata():
    assert summarize_ocr_strata({"tesseract": {}})["available"] is False
    assert summarize_ocr_strata({})["available"] is False


def test_summarize_pareto_security_groups_by_n():
    report = {
        "configs": [
            {"n": 4, "refresh_hz": 240, "single_frame_ocr": 0.0, "full_cycle_ocr": 0.92, "entropy_ratio": 0.4, "fpi": 0.03, "fpi_safe": True},
            {"n": 4, "refresh_hz": 144, "single_frame_ocr": 0.0, "full_cycle_ocr": 0.92, "entropy_ratio": 0.4, "fpi": 0.30, "fpi_safe": False},
            {"n": 2, "refresh_hz": 240, "single_frame_ocr": 0.0, "full_cycle_ocr": 0.92, "entropy_ratio": 0.57, "fpi": 0.005, "fpi_safe": True},
        ],
        "recommended": {"n": 4, "refresh_hz": 240, "fpi": 0.03, "entropy_ratio": 0.4},
    }
    out = summarize_pareto_security(report)
    assert out["available"] is True
    assert [r["n"] for r in out["rows"]] == [2, 4]
    row4 = next(r for r in out["rows"] if r["n"] == 4)
    assert len(row4["refresh"]) == 2
    assert out["recommended"]["n"] == 4


def test_summarize_pareto_security_handles_missing():
    assert summarize_pareto_security(None)["available"] is False
    assert summarize_pareto_security({})["available"] is False


def test_summarize_vlm_model_ablation_builds_exact_match_matrix():
    report = {
        "config": {
            "models": ["org/A", "org/B"],
            "attacks": ["global_shutter_slot0", "temporal_average_cycle"],
        },
        "models": {
            "org/A": {"summary": {"attacks": {
                "global_shutter_slot0": {"exact_match": {"mean": 0.0}},
                "temporal_average_cycle": {"exact_match": {"mean": 0.93}},
            }}},
            "org/B": {"summary": {"attacks": {
                # char-acc on a blank frame would be nonzero here, but exact_match is 0
                "global_shutter_slot0": {"exact_match": {"mean": 0.0}},
                "temporal_average_cycle": {"exact_match": {"mean": 1.0}},
            }}},
        },
    }
    out = summarize_vlm_model_ablation(report)
    assert out["available"] is True
    assert out["metric"] == "exact_match"
    assert out["models"] == ["org/A", "org/B"]
    single = next(r for r in out["rows"] if r["attack"] == "global_shutter_slot0")
    assert [c["exact_match"] for c in single["cells"]] == [0.0, 0.0]
    full = next(r for r in out["rows"] if r["attack"] == "temporal_average_cycle")
    assert [c["exact_match"] for c in full["cells"]] == [0.93, 1.0]


def test_summarize_vlm_model_ablation_handles_missing():
    assert summarize_vlm_model_ablation(None)["available"] is False
    assert summarize_vlm_model_ablation({})["available"] is False
