import json

import numpy as np

from experiments import build_corpus
from src.attack.ocr_evaluator import OCRResult
from src.evaluation.benchmark import (
    _mean_std,
    compose_protected_subframes,
    run_corpus_multi_engine,
    run_corpus_strong_camera_attacks,
    summarize_corpus_recovery_metrics,
    summarize_corpus_strata,
    summarize_strong_attack_rows,
)


def test_build_corpus_generates_metadata_and_preserves_loader(tmp_path, monkeypatch):
    monkeypatch.setattr(build_corpus, "OUT_DIR", tmp_path)

    ground_truth = build_corpus.build(samples_per_template=2)
    images, truths, names = build_corpus.load_corpus()
    metadata = build_corpus.load_corpus_metadata()

    assert len(ground_truth) == len(build_corpus.BASE_CORPUS) * 2
    assert len(images) == len(truths) == len(names) == len(ground_truth)
    assert set(metadata) == set(ground_truth)

    first = metadata[names[0]]
    assert {"truth", "category", "language", "layout", "font_size", "width", "height"}.issubset(first)
    assert first["truth"] == ground_truth[names[0]]
    assert (tmp_path / "ground_truth.json").exists()
    assert (tmp_path / "corpus_metadata.json").exists()

    stored = json.loads((tmp_path / "corpus_metadata.json").read_text(encoding="utf-8"))
    assert stored[names[0]]["category"] == first["category"]


def test_iter_corpus_specs_rejects_non_positive_count():
    try:
        build_corpus.iter_corpus_specs(samples_per_template=0)
    except ValueError as exc:
        assert "samples_per_template" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_run_corpus_multi_engine_can_merge_existing_without_running_engines(tmp_path, monkeypatch):
    monkeypatch.setattr(build_corpus, "OUT_DIR", tmp_path / "corpus")
    build_corpus.build(samples_per_template=1)

    out_dir = tmp_path / "results"
    out_dir.mkdir()
    existing = {
        "tesseract": {
            "n_samples": 120,
            "original_mean": 0.94,
            "subframe_mean": 0.0,
        }
    }
    report_path = out_dir / "corpus_multi_engine.json"
    report_path.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")

    report = run_corpus_multi_engine(engines=[], output_dir=str(out_dir), merge_existing=True)

    assert report == existing
    stored = json.loads(report_path.read_text(encoding="utf-8"))
    assert stored == existing


def test_mean_std_reports_deterministic_ci95():
    empty = _mean_std([])
    assert empty["count"] == 0
    assert empty["ci95"]["method"] == "empty"

    single = _mean_std([0.75])
    assert single["count"] == 1
    assert single["ci95"]["low"] == 0.75
    assert single["ci95"]["high"] == 0.75
    assert single["ci95"]["method"] == "degenerate"

    stats = _mean_std([1.0, 0.8, 0.6, 0.4])
    assert stats["count"] == 4
    assert abs(stats["mean"] - 0.7) < 1e-9
    assert stats["ci95"]["method"] == "bootstrap_percentile"
    assert stats["ci95"]["low"] <= stats["mean"] <= stats["ci95"]["high"]


def test_summarize_corpus_strata_reports_count_mean_std_ci_and_reduction():
    rows = [
        {
            "metadata": {"category": "code"},
            "original_char_acc": 1.0,
            "subframe_char_acc": 0.0,
            "accuracy_reduction": 1.0,
        },
        {
            "metadata": {"category": "code"},
            "original_char_acc": 0.8,
            "subframe_char_acc": 0.2,
            "accuracy_reduction": 0.6,
        },
        {
            "metadata": {"category": "table"},
            "original_char_acc": 0.6,
            "subframe_char_acc": 0.1,
            "accuracy_reduction": 0.5,
        },
    ]

    summary = summarize_corpus_strata(rows, "category")

    assert summary["code"]["original"]["count"] == 2
    assert abs(summary["code"]["original"]["mean"] - 0.9) < 1e-9
    assert abs(summary["code"]["subframe"]["mean"] - 0.1) < 1e-9
    assert abs(summary["code"]["reduction"]["mean"] - 0.8) < 1e-9
    assert summary["code"]["original"]["ci95"]["method"] == "bootstrap_percentile"
    assert summary["table"]["original"]["count"] == 1
    assert summary["table"]["reduction"]["ci95"]["method"] == "degenerate"


def test_summarize_corpus_recovery_metrics_reports_secondary_privacy_metrics():
    rows = [
        {
            "original_word_acc": 1.0,
            "subframe_word_acc": 0.0,
            "original_exact_match": True,
            "subframe_exact_match": 0.0,
            "original_sensitive_token_recall": 1.0,
            "subframe_sensitive_token_recall": 0.0,
            "sensitive_token_count": 2,
        },
        {
            "original_word_acc": 0.5,
            "subframe_word_acc": 0.25,
            "original_exact_match": False,
            "subframe_exact_match": 0.0,
            "original_sensitive_token_recall": 0.0,
            "subframe_sensitive_token_recall": 0.0,
            "sensitive_token_count": 0,
        },
    ]

    metrics = summarize_corpus_recovery_metrics(rows)

    assert metrics["word_accuracy"]["original"]["count"] == 2
    assert abs(metrics["word_accuracy"]["original"]["mean"] - 0.75) < 1e-9
    assert abs(metrics["exact_match"]["original"]["mean"] - 0.5) < 1e-9
    assert metrics["sensitive_token_recall"]["n_samples_with_sensitive_tokens"] == 1
    assert metrics["sensitive_token_recall"]["original"]["mean"] == 1.0
    assert metrics["sensitive_token_recall"]["subframe"]["mean"] == 0.0


def test_compose_protected_subframes_supports_multiple_cycles():
    image = np.full((8, 10, 3), 180, dtype=np.uint8)

    subframes = compose_protected_subframes(
        image,
        n=2,
        epsilon=0.0,
        cycles=3,
        with_noise=False,
    )

    assert len(subframes) == 6
    assert all(frame.shape == image.shape for frame in subframes)
    assert all(frame.dtype == np.uint8 for frame in subframes)


def test_summarize_strong_attack_rows_reports_best_attacker():
    rows = [
        {
            "name": "a",
            "attack": "single",
            "char_accuracy": 0.0,
            "word_accuracy": 0.0,
            "exact_match": False,
            "sensitive_token_recall": 0.0,
            "sensitive_token_count": 1,
            "psnr_db": 5.0,
            "reconstruction_score": 1.0,
        },
        {
            "name": "a",
            "attack": "phase",
            "char_accuracy": 0.9,
            "word_accuracy": 1.0,
            "exact_match": True,
            "sensitive_token_recall": 1.0,
            "sensitive_token_count": 1,
            "psnr_db": 30.0,
            "reconstruction_score": 10.0,
        },
        {
            "name": "b",
            "attack": "single",
            "char_accuracy": 0.1,
            "word_accuracy": 0.0,
            "exact_match": False,
            "sensitive_token_recall": 0.0,
            "sensitive_token_count": 0,
            "psnr_db": 6.0,
            "reconstruction_score": 2.0,
        },
        {
            "name": "b",
            "attack": "phase",
            "char_accuracy": 0.2,
            "word_accuracy": 0.0,
            "exact_match": False,
            "sensitive_token_recall": 0.0,
            "sensitive_token_count": 0,
            "psnr_db": 20.0,
            "reconstruction_score": 7.0,
        },
    ]

    summary = summarize_strong_attack_rows(rows, leak_threshold=0.20)

    assert summary["attacks"]["phase"]["char_accuracy"]["count"] == 2
    assert abs(summary["attacks"]["phase"]["char_accuracy"]["mean"] - 0.55) < 1e-9
    assert summary["attacks"]["phase"]["leak_rate_char_ge_20pct"]["mean"] == 1.0
    best = summary["best_attack_per_sample"]
    assert best["attack_wins"]["phase"] == 2
    assert best["sensitive_token_recall"]["n_samples_with_sensitive_tokens"] == 1
    assert best["exact_match"]["mean"] == 0.5


def test_run_corpus_strong_camera_attacks_writes_report_with_fake_ocr(tmp_path):
    class FakeEvaluator:
        engines = ["fake"]

        def evaluate_single(self, image, ground_truth, engine):
            assert engine == "fake"
            text = ground_truth if float(image.mean()) > 1.0 else ""
            return OCRResult(
                engine=engine,
                text=text,
                char_accuracy=1.0 if text else 0.0,
                word_accuracy=1.0 if text else 0.0,
            )

    image = np.full((8, 8, 3), 160, dtype=np.uint8)
    corpus = ([image], ["CODE-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code", "language": "en"}}

    report = run_corpus_strong_camera_attacks(
        n=2,
        epsilon=0.0,
        cycles=1,
        engine="fake",
        output_dir=str(tmp_path),
        evaluator=FakeEvaluator(),
        corpus=corpus,
        metadata=metadata,
        with_noise=False,
    )

    out = tmp_path / "corpus_strong_camera_attack.json"
    stored = json.loads(out.read_text(encoding="utf-8"))
    assert stored["config"]["n_samples"] == 1
    assert report["config"]["engine"] == "fake"
    assert "global_shutter_slot0" in report["summary"]["attacks"]
    assert "phase_search_mean" in report["summary"]["attacks"]
