import json

import numpy as np
import pytest

from src.evaluation.vlm_benchmark import (
    DEFAULT_VLM_RESULT_FILE,
    build_vlm_attack_frames,
    run_vlm_benchmark,
    select_stratified_samples,
    summarize_vlm_rows,
)


def test_select_stratified_samples_is_deterministic_by_category():
    names = ["b_0", "a_0", "b_1", "a_1", "c_0"]
    metadata = {
        "a_0": {"category": "alpha"},
        "a_1": {"category": "alpha"},
        "b_0": {"category": "beta"},
        "b_1": {"category": "beta"},
        "c_0": {"category": "gamma"},
    }

    selected = select_stratified_samples(names, metadata, samples_per_category=1)

    assert selected == [1, 0, 4]


def test_build_vlm_attack_frames_filters_and_rejects_unknown_attacks():
    image = np.full((10, 12, 3), 180, dtype=np.uint8)

    frames = build_vlm_attack_frames(
        image,
        n=2,
        epsilon=0.0,
        cycles=1,
        attacks=("original", "global_shutter_slot0"),
        with_noise=False,
    )

    assert list(frames) == ["original", "global_shutter_slot0"]
    assert frames["original"][0].shape == image.shape
    with pytest.raises(ValueError):
        build_vlm_attack_frames(image, attacks=("not_an_attack",))


def test_summarize_vlm_rows_reports_success_rate_and_best_attack():
    rows = [
        {
            "name": "sample",
            "attack": "original",
            "char_accuracy": 1.0,
            "word_accuracy": 1.0,
            "exact_match": True,
            "sensitive_token_recall": 1.0,
            "sensitive_token_count": 1,
            "vlm_can_read_sensitive": True,
            "vlm_confidence": 0.9,
            "psnr_db": 99.0,
            "vlm_error": "",
        },
        {
            "name": "sample",
            "attack": "global_shutter_slot0",
            "char_accuracy": 0.0,
            "word_accuracy": 0.0,
            "exact_match": False,
            "sensitive_token_recall": 0.0,
            "sensitive_token_count": 1,
            "vlm_can_read_sensitive": False,
            "vlm_confidence": 0.1,
            "psnr_db": 5.0,
            "vlm_error": "timeout",
        },
    ]

    summary = summarize_vlm_rows(rows)

    assert summary["attacks"]["original"]["vlm_read_success_rate"]["mean"] == 1.0
    assert summary["attacks"]["global_shutter_slot0"]["error_count"] == 1
    assert summary["call_status"]["total_calls"] == 2
    assert summary["call_status"]["successful_calls"] == 1
    assert summary["call_status"]["all_calls_failed"] is False
    assert summary["best_attack_per_sample"]["attack_wins"]["original"] == 1


def test_run_vlm_benchmark_writes_report_with_fake_client(tmp_path, monkeypatch):
    monkeypatch.setenv("SILICONFLOW_API_KEY", "secret-value")

    class FakeClient:
        model = "fake-vlm"
        base_url = "https://example.invalid/v1"

        def analyze_image(self, image, ground_truth=""):
            visible = ground_truth if float(image.mean()) > 1.0 else ""
            return {
                "visible_text": visible,
                "can_read_sensitive": bool(visible),
                "confidence": 0.8 if visible else 0.0,
                "notes": "",
            }

    image = np.full((8, 8, 3), 160, dtype=np.uint8)
    corpus = ([image], ["CODE-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code", "language": "en"}}

    report = run_vlm_benchmark(
        client=FakeClient(),
        output_dir=str(tmp_path),
        n=2,
        epsilon=0.0,
        cycles=1,
        samples_per_category=1,
        attacks=("original", "global_shutter_slot0"),
        corpus=corpus,
        metadata=metadata,
        with_noise=False,
    )

    out = tmp_path / DEFAULT_VLM_RESULT_FILE
    stored_text = out.read_text(encoding="utf-8")
    stored = json.loads(stored_text)

    assert report["config"]["model"] == "fake-vlm"
    assert stored["config"]["n_selected_samples"] == 1
    assert len(stored["samples"]) == 2
    assert "secret-value" not in stored_text
    assert "Authorization" not in stored_text
    assert stored["summary"]["attacks"]["original"]["char_accuracy"]["mean"] == 1.0
