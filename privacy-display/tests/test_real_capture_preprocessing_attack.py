from pathlib import Path
import json

import numpy as np
import pytest
from PIL import Image

from experiments.real_capture_preprocessing_attack import (
    PREPROCESSOR_MANIFEST,
    append_checkpoint_row,
    build_attack_report,
    checkpoint_row_key,
    collapse_attacker_oracle,
    evaluate_job,
    import_raw_checkpoint_rows,
    load_checkpoint_rows,
    load_primary_capture_records,
    pending_jobs,
    preprocess_image,
    render_attack_markdown,
    retain_rows_for_retry,
    summarize_primary_selection,
    validate_complete_matrix,
    validate_no_ocr_errors,
)


def test_real_capture_preprocessing_experiment_module_exists():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "real_capture_preprocessing_attack.py"
    )

    assert module_path.is_file()


def test_preprocessor_manifest_is_fixed_and_complete():
    assert [item["name"] for item in PREPROCESSOR_MANIFEST] == [
        "raw",
        "gamma_0.5",
        "clahe_luma",
        "unsharp_mask",
        "adaptive_threshold",
        "upscale_2x",
    ]
    assert PREPROCESSOR_MANIFEST[1]["params"] == {"gamma": 0.5}
    assert PREPROCESSOR_MANIFEST[2]["params"] == {
        "percentile_low": 1.0,
        "percentile_high": 99.0,
        "clip_limit": 4.0,
        "tile_grid_size": [8, 8],
    }


@pytest.mark.parametrize(
    ("method", "expected_shape"),
    [
        ("raw", (64, 64, 3)),
        ("gamma_0.5", (64, 64, 3)),
        ("clahe_luma", (64, 64, 3)),
        ("unsharp_mask", (64, 64, 3)),
        ("adaptive_threshold", (64, 64, 3)),
        ("upscale_2x", (128, 128, 3)),
    ],
)
def test_preprocess_image_is_deterministic_rgb_uint8(method, expected_shape):
    image = np.arange(64 * 64 * 3, dtype=np.uint8).reshape(64, 64, 3)

    first = preprocess_image(image, method)
    second = preprocess_image(image, method)

    assert first.shape == expected_shape
    assert first.dtype == np.uint8
    np.testing.assert_array_equal(first, second)


def test_preprocess_image_rejects_unknown_method():
    with pytest.raises(ValueError, match="unknown preprocessor"):
        preprocess_image(np.zeros((64, 64, 3), dtype=np.uint8), "manual_tuning")


def test_primary_selection_matches_the_paper_estimand():
    project_root = Path(__file__).resolve().parents[1]
    records = load_primary_capture_records(
        project_root / "experiments" / "results" / "real_capture_ocr.json",
        project_root=project_root,
    )
    summary = summarize_primary_selection(records)

    assert summary["positions"] == [
        "d0.5_a0",
        "d0.5_a30",
        "d1.5_a0",
        "d1.5_a15",
        "d1.5_a30",
        "d1_a0",
        "d1_a15",
        "d1_a30",
    ]
    assert summary["capture_counts"] == {
        "original": 288,
        "deployed": 408,
        "high_suppression": 288,
    }
    assert summary["matched_unit_counts"] == {
        "original": 288,
        "deployed": 288,
        "high_suppression": 288,
    }
    assert all(record["image_path"].is_file() for record in records)
    assert all(record["truth"].strip() for record in records)


def _record_with_raw_rows(capture_id="capture-1"):
    return {
        "id": capture_id,
        "profile": "deployed",
        "position": "d1_a0",
        "content_item": "account_00",
        "repeat_index": "s00",
        "truth": "ACCOUNT-1234",
        "image_path": Path("/tmp/example.jpg"),
        "raw_rows": [
            {
                "id": capture_id,
                "engine": "tesseract",
                "char_accuracy": 0.2,
                "word_accuracy": 0.1,
                "exact_match": False,
                "sensitive_token_recall": 0.5,
                "sensitive_token_count": 1,
                "recognized_text": "1234",
                "ocr_error": "",
            },
            {
                "id": capture_id,
                "engine": "easyocr",
                "char_accuracy": 0.4,
                "word_accuracy": 0.2,
                "exact_match": False,
                "sensitive_token_recall": 1.0,
                "sensitive_token_count": 1,
                "recognized_text": "ACCOUNT-1234",
                "ocr_error": "",
            },
        ],
    }


def _capture_id(ablation, content, repeat="s00", *, stamp="123456"):
    return (
        f"emeet_smartcam_s600_{ablation}_short_0deg_1m_"
        f"{content}_n4_{stamp}_{repeat}"
    )


def test_import_raw_checkpoint_rows_preserves_canonical_metrics():
    rows = import_raw_checkpoint_rows([_record_with_raw_rows()])

    assert len(rows) == 2
    assert {row["preprocessor"] for row in rows} == {"raw"}
    assert {row["source"] for row in rows} == {"canonical_raw_archive"}
    assert {row["engine"] for row in rows} == {"tesseract", "easyocr"}
    assert max(row["char_accuracy"] for row in rows) == pytest.approx(0.4)
    assert all(row["profile"] == "deployed" for row in rows)


def test_checkpoint_loader_rejects_duplicate_cells(tmp_path):
    row = import_raw_checkpoint_rows([_record_with_raw_rows()])[0]
    path = tmp_path / "rows.jsonl"
    path.write_text(
        json.dumps(row) + "\n" + json.dumps(row) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate checkpoint cell"):
        load_checkpoint_rows(path)


def test_retry_filter_removes_only_failed_rows_in_requested_matrix():
    rows = [
        {"id": "a", "preprocessor": "upscale_2x", "engine": "tesseract", "ocr_error": "timeout"},
        {"id": "b", "preprocessor": "raw", "engine": "tesseract", "ocr_error": ""},
        {"id": "c", "preprocessor": "upscale_2x", "engine": "surya", "ocr_error": "timeout"},
    ]

    retained = retain_rows_for_retry(
        rows,
        engines=["tesseract"],
        preprocessors=["raw", "upscale_2x"],
    )

    assert [row["id"] for row in retained] == ["b", "c"]


def test_pending_jobs_skip_completed_cells():
    record = _record_with_raw_rows()
    completed = {
        checkpoint_row_key({
            "id": record["id"],
            "preprocessor": "gamma_0.5",
            "engine": "tesseract",
        })
    }

    jobs = pending_jobs(
        [record],
        engines=["tesseract", "easyocr"],
        preprocessors=["gamma_0.5", "clahe_luma"],
        completed_keys=completed,
    )

    assert [
        (job["record"]["id"], job["preprocessor"], job["engine"])
        for job in jobs
    ] == [
        ("capture-1", "gamma_0.5", "easyocr"),
        ("capture-1", "clahe_luma", "tesseract"),
        ("capture-1", "clahe_luma", "easyocr"),
    ]


def _checkpoint_row(
    *,
    capture_id,
    profile,
    preprocessor,
    engine,
    char,
    exact=False,
    content_item="account_00",
):
    return {
        "id": capture_id,
        "profile": profile,
        "ablation": profile,
        "attack": "short",
        "position": "d1_a0",
        "content_item": content_item,
        "repeat_index": "s00",
        "preprocessor": preprocessor,
        "engine": engine,
        "char_accuracy": char,
        "word_accuracy": char / 2,
        "exact_match": exact,
        "sensitive_token_recall": char / 3,
        "sensitive_token_count": 1,
        "recognized_text": "",
        "ocr_error": "",
    }


def test_attacker_oracle_takes_metricwise_max_across_preprocessors_and_engines():
    rows = [
        _checkpoint_row(
            capture_id="c1",
            profile="deployed",
            preprocessor="raw",
            engine="tesseract",
            char=0.3,
            exact=True,
        ),
        _checkpoint_row(
            capture_id="c1",
            profile="deployed",
            preprocessor="clahe_luma",
            engine="easyocr",
            char=0.8,
        ),
    ]

    collapsed = collapse_attacker_oracle(rows)

    assert len(collapsed) == 1
    assert collapsed[0]["char_accuracy"] == pytest.approx(0.8)
    assert collapsed[0]["exact_match"] == 1.0
    assert collapsed[0]["metric_sources"]["char_accuracy"] == {
        "preprocessor": "clahe_luma",
        "engine": "easyocr",
    }
    assert collapsed[0]["metric_sources"]["exact_match"] == {
        "preprocessor": "raw",
        "engine": "tesseract",
    }


def test_complete_matrix_validator_rejects_missing_engine_preprocessor_cell():
    records = [_record_with_raw_rows()]
    rows = [
        _checkpoint_row(
            capture_id="capture-1",
            profile="deployed",
            preprocessor="raw",
            engine="tesseract",
            char=0.3,
        )
    ]

    with pytest.raises(ValueError, match="incomplete preprocessing matrix"):
        validate_complete_matrix(
            records,
            rows,
            engines=["tesseract", "easyocr"],
            preprocessors=["raw", "gamma_0.5"],
        )


def test_attack_report_uses_duplicate_averaged_matched_estimand(tmp_path):
    original_id = _capture_id("original", "account_00", stamp="100000")
    deployed_id_1 = _capture_id("deployed", "account_00", stamp="100001")
    deployed_id_2 = _capture_id("deployed", "account_00", stamp="100002")
    hardened_id = _capture_id("vlm", "account_00", stamp="100003")
    records = [
        {**_record_with_raw_rows(original_id), "profile": "original"},
        {**_record_with_raw_rows(deployed_id_1), "profile": "deployed"},
        {**_record_with_raw_rows(deployed_id_2), "profile": "deployed"},
        {**_record_with_raw_rows(hardened_id), "profile": "high_suppression"},
    ]
    rows = []
    for capture_id, profile, raw_char, gamma_char in (
        (original_id, "original", 0.9, 0.95),
        (deployed_id_1, "deployed", 0.2, 0.5),
        (deployed_id_2, "deployed", 0.4, 0.6),
        (hardened_id, "high_suppression", 0.1, 0.2),
    ):
        rows.extend([
            _checkpoint_row(
                capture_id=capture_id,
                profile=profile,
                preprocessor="raw",
                engine="tesseract",
                char=raw_char,
            ),
            _checkpoint_row(
                capture_id=capture_id,
                profile=profile,
                preprocessor="gamma_0.5",
                engine="tesseract",
                char=gamma_char,
            ),
        ])

    source_archive = tmp_path / "source.json"
    source_archive.write_text('{"captures": []}\n', encoding="utf-8")
    report = build_attack_report(
        records,
        rows,
        engines=["tesseract"],
        preprocessors=["raw", "gamma_0.5"],
        bootstrap_resamples=0,
        source_archive=source_archive,
    )

    raw = report["oracles"]["raw"]["contrasts"]["original_minus_deployed"]
    adaptive = report["oracles"]["best_preprocessing_engine"]["contrasts"][
        "original_minus_deployed"
    ]
    assert raw["matched_baseline_mean"] == pytest.approx(0.9)
    assert raw["matched_treatment_mean"] == pytest.approx(0.3)
    assert raw["estimate"] == pytest.approx(0.6)
    assert adaptive["matched_baseline_mean"] == pytest.approx(0.95)
    assert adaptive["matched_treatment_mean"] == pytest.approx(0.55)
    assert adaptive["estimate"] == pytest.approx(0.4)
    assert report["source"]["ocr_archive"] == str(source_archive)
    assert len(report["source"]["ocr_archive_sha256"]) == 64
    assert report["audit"]["ocr_error_count"] == 0
    assert report["runtime_versions"]["python"]
    assert report["config"]["preprocessor_manifest"][1] == PREPROCESSOR_MANIFEST[1]
    markdown = render_attack_markdown(report)
    assert "Raw best-of-engine" in markdown
    assert "Best-of-preprocessing-and-engine" in markdown
    assert "30.0%" in markdown
    assert "55.0%" in markdown


class _FakeEvaluator:
    def __init__(self, text="ACCOUNT-1234", error=None):
        self.text = text
        self.error = error

    def recognize(self, image, engine):
        assert image.dtype == np.uint8
        assert engine == "tesseract"
        if self.error:
            raise self.error
        return self.text


def test_evaluate_job_records_transform_metrics_and_provenance(tmp_path):
    image_path = tmp_path / "capture.jpg"
    Image.fromarray(np.full((64, 64, 3), 64, dtype=np.uint8)).save(image_path)
    record = {
        **_record_with_raw_rows(),
        "image_path": image_path,
    }

    row = evaluate_job(
        {
            "record": record,
            "preprocessor": "gamma_0.5",
            "engine": "tesseract",
        },
        evaluator=_FakeEvaluator(),
    )

    assert row["char_accuracy"] == 1.0
    assert row["exact_match"] is True
    assert row["preprocessor"] == "gamma_0.5"
    assert row["source"] == "generated_preprocessing_attack"
    assert row["ocr_error"] == ""
    assert row["duration_seconds"] >= 0.0


def test_evaluate_job_persists_ocr_error_as_zero_recovery(tmp_path):
    image_path = tmp_path / "capture.jpg"
    Image.fromarray(np.full((64, 64, 3), 64, dtype=np.uint8)).save(image_path)
    record = {**_record_with_raw_rows(), "image_path": image_path}

    row = evaluate_job(
        {
            "record": record,
            "preprocessor": "clahe_luma",
            "engine": "tesseract",
        },
        evaluator=_FakeEvaluator(error=RuntimeError("timeout")),
    )

    assert row["char_accuracy"] == 0.0
    assert row["exact_match"] is False
    assert row["ocr_error"] == "timeout"


def test_append_checkpoint_row_is_immediately_reloadable(tmp_path):
    path = tmp_path / "tesseract.jsonl"
    row = _checkpoint_row(
        capture_id="capture-1",
        profile="deployed",
        preprocessor="gamma_0.5",
        engine="tesseract",
        char=0.4,
    )
    completed = set()

    append_checkpoint_row(path, row, completed_keys=completed)

    assert checkpoint_row_key(row) in completed
    assert load_checkpoint_rows(path)[checkpoint_row_key(row)]["char_accuracy"] == 0.4
    with pytest.raises(ValueError, match="already exists"):
        append_checkpoint_row(path, row, completed_keys=completed)


def test_error_validator_requires_explicit_clean_completion():
    row = _checkpoint_row(
        capture_id="capture-1",
        profile="deployed",
        preprocessor="gamma_0.5",
        engine="tesseract",
        char=0.0,
    )
    row["ocr_error"] = "timeout"

    with pytest.raises(ValueError, match="OCR errors"):
        validate_no_ocr_errors([row])


def test_completed_three_engine_matrix_is_reflected_in_manuscript():
    root = Path(__file__).resolve().parents[1]
    report = json.loads(
        (root / "experiments" / "results" /
         "real_capture_preprocessing_attack_three_engine.json").read_text(
            encoding="utf-8"
        )
    )
    manuscript = (root.parent / "paper" / "main.tex").read_text(encoding="utf-8")

    assert report["audit"]["matrix_row_count"] == 17_712
    assert report["audit"]["ocr_error_count"] == 0
    assert report["config"]["engines"] == ["tesseract", "easyocr", "surya"]
    assert "17,712" in manuscript
    assert "40.2\\%" in manuscript
    assert "13.7\\%" in manuscript
    assert "EasyOCR and Surya preprocessing remain unevaluated" not in manuscript
