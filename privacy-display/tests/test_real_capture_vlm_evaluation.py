from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from experiments import real_capture_vlm_evaluation as target
from experiments.real_capture_vlm_evaluation import _aggregate_group, summarize_results


def _result_row(**overrides):
    row = {
        "id": "capture-1",
        "model": "model-A",
        "condition": "vlm|short",
        "ablation": "vlm",
        "attack": "short",
        "profile": "vlm",
        "position": "d0.5_a0",
        "distance_m": 0.5,
        "angle_degrees": 0.0,
        "visible_text": "SECRET-1234",
        "char_accuracy": 1.0,
        "word_accuracy": 1.0,
        "exact_match": True,
        "sensitive_token_recall": 1.0,
        "sensitive_token_count": 1,
        "vlm_confidence": 0.9,
        "vlm_can_read_sensitive": True,
        "vlm_error": "",
    }
    row.update(overrides)
    return row


def _capture_entry(
    capture_id: str,
    *,
    ablation: str,
    attack: str,
    condition: str,
    profile: str,
    truth: str = "SECRET-1234",
) -> dict:
    return {
        "id": capture_id,
        "image": f"{capture_id}.jpg",
        "truth": truth,
        "condition": condition,
        "ablation": ablation,
        "attack": attack,
        "profile": profile,
        "distance_m": 0.5,
        "angle_degrees": 0.0,
        "capture_mode": "short_exposure",
    }


def _write_position(experiments_dir: Path, position: str, entries: list[dict]) -> None:
    capture_dir = experiments_dir / f"real_captures_{position}_final"
    capture_dir.mkdir(parents=True)
    for entry in entries:
        Image.new("RGB", (4, 4), color="white").save(capture_dir / entry["image"])
    (capture_dir / "metadata.json").write_text(
        json.dumps({"schema_version": 1, "captures": entries}),
        encoding="utf-8",
    )


def test_aggregate_group_excludes_api_errors_from_metric_denominators():
    rows = [
        _result_row(),
        _result_row(
            id="capture-2",
            visible_text="",
            char_accuracy=0.0,
            word_accuracy=0.0,
            exact_match=False,
            sensitive_token_recall=0.0,
            sensitive_token_count=0,
            vlm_confidence=0.0,
            vlm_can_read_sensitive=False,
            vlm_error="HTTP 429",
        ),
    ]

    summary = _aggregate_group(rows)

    assert summary["attempted_count"] == 2
    assert summary["successful_count"] == 1
    assert summary["error_count"] == 1
    assert summary["exact_match"]["count"] == 1
    assert summary["exact_match"]["mean"] == 1.0
    assert summary["char_accuracy"]["mean"] == 1.0
    assert summary["vlm_read_success_rate"]["mean"] == 1.0


def test_aggregate_group_marks_all_error_metrics_unavailable():
    summary = _aggregate_group([
        _result_row(
            visible_text="",
            char_accuracy=0.0,
            word_accuracy=0.0,
            exact_match=False,
            sensitive_token_recall=0.0,
            sensitive_token_count=0,
            vlm_confidence=0.0,
            vlm_can_read_sensitive=False,
            vlm_error="timeout",
        )
    ])

    assert summary["successful_count"] == 0
    assert summary["error_count"] == 1
    assert summary["exact_match"]["count"] == 0
    assert summary["exact_match"]["mean"] is None


def test_position_summary_excludes_original_baseline():
    rows = [
        _result_row(
            id="protected",
            exact_match=False,
            char_accuracy=0.0,
            word_accuracy=0.0,
            sensitive_token_recall=0.0,
            vlm_can_read_sensitive=False,
        ),
        _result_row(
            id="baseline",
            condition="original|short",
            ablation="original",
            profile="off",
        ),
    ]

    summary = summarize_results(rows)

    position = summary["models"]["model-A"]["by_position"]["d0.5_a0"]
    assert position["attempted_count"] == 1
    assert position["exact_match"]["mean"] == 0.0


def test_cross_model_summary_excludes_error_rows():
    rows = [
        _result_row(id="success"),
        _result_row(
            id="error",
            exact_match=False,
            char_accuracy=0.0,
            word_accuracy=0.0,
            sensitive_token_recall=0.0,
            vlm_can_read_sensitive=False,
            vlm_error="timeout",
        ),
    ]

    summary = summarize_results(rows)

    assert summary["cross_model"]["vlm|short"]["model-A"] == 1.0


def test_cross_model_summary_marks_all_error_cell_unavailable():
    row = _result_row(
        exact_match=False,
        char_accuracy=0.0,
        word_accuracy=0.0,
        sensitive_token_recall=0.0,
        vlm_can_read_sensitive=False,
        vlm_error="timeout",
    )

    summary = summarize_results([row])

    assert summary["cross_model"]["vlm|short"]["model-A"] is None


def test_upsert_rows_replaces_failed_observation_with_success():
    failed = _result_row(vlm_error="timeout", exact_match=False, char_accuracy=0.0)
    succeeded = _result_row(vlm_error="", exact_match=True, char_accuracy=1.0)

    merged = target.upsert_rows([failed], [succeeded])

    assert len(merged) == 1
    assert merged[0]["vlm_error"] == ""
    assert merged[0]["exact_match"] is True


def test_upsert_key_keeps_same_id_from_different_positions_distinct():
    rows = target.upsert_rows(
        [_result_row(position="d0.5_a0")],
        [_result_row(position="d1_a0")],
    )

    assert len(rows) == 2


def test_partial_path_follows_custom_output_path(tmp_path):
    output = tmp_path / "custom.json"

    assert target.partial_path_for_output(output) == tmp_path / "custom_partial.json"


def test_partial_round_trip_records_and_validates_resume_config(tmp_path):
    path = tmp_path / "result_partial.json"
    config = {"models": ["model-A"], "selection_sha256": "abc"}
    rows = [_result_row()]

    target.save_partial(rows, path, config)

    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["schema_version"] == 1
    assert stored["config"] == config
    assert target.load_partial(path, config) == rows
    assert not list(tmp_path.glob("*.tmp"))


def test_partial_atomic_write_retries_transient_replace_error(tmp_path, monkeypatch):
    path = tmp_path / "result_partial.json"
    config = {"models": ["model-A"], "selection_sha256": "abc"}
    real_replace = target.os.replace
    attempts = 0

    def flaky_replace(source, destination):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise PermissionError("transient file lock")
        return real_replace(source, destination)

    monkeypatch.setattr(target.os, "replace", flaky_replace)

    target.save_partial([_result_row()], path, config)

    assert attempts == 2
    assert target.load_partial(path, config)[0]["id"] == "capture-1"


def test_partial_resume_rejects_incompatible_config(tmp_path):
    path = tmp_path / "result_partial.json"
    target.save_partial(
        [_result_row()],
        path,
        {"models": ["model-A"], "selection_sha256": "abc"},
    )

    with pytest.raises(ValueError, match="incompatible"):
        target.load_partial(
            path,
            {"models": ["model-B"], "selection_sha256": "abc"},
        )


def test_capture_loader_normalizes_legacy_profile_across_requested_positions(tmp_path):
    for position in ("d0.5_a0", "d1_a0"):
        entries = [
            _capture_entry(
                f"{position}-short-{index}",
                ablation="vlm",
                attack="short",
                condition="vlm|short",
                profile="vlm",
            )
            for index in range(2)
        ] + [
            _capture_entry(
                f"{position}-long-{index}",
                ablation="vlm",
                attack="long",
                condition="vlm|long",
                profile="vlm",
            )
            for index in range(2)
        ] + [
            _capture_entry(
                f"{position}-baseline-{index}",
                ablation="original",
                attack="short",
                condition="original|short",
                profile="off",
            )
            for index in range(2)
        ]
        _write_position(tmp_path, position, entries)

    captures = target.load_real_captures(
        experiments_dir=tmp_path,
        positions=["d0.5_a0", "d1_a0"],
        baseline_position="d0.5_a0",
        max_samples=1,
    )

    assert {(row["position"], row["condition"]) for row in captures} == {
        ("d0.5_a0", "capture_hardened|short"),
        ("d0.5_a0", "capture_hardened|long"),
        ("d0.5_a0", "original|short"),
        ("d1_a0", "capture_hardened|short"),
        ("d1_a0", "capture_hardened|long"),
    }
    protected = [row for row in captures if row["ablation"] != "original"]
    assert {row["ablation"] for row in protected} == {"capture_hardened"}
    assert {row["profile"] for row in protected} == {"capture_hardened"}


def test_capture_loader_rejects_missing_image_instead_of_silent_skip(tmp_path):
    entry = _capture_entry(
        "missing-image",
        ablation="vlm",
        attack="short",
        condition="vlm|short",
        profile="vlm",
    )
    _write_position(tmp_path, "d0.5_a0", [entry])
    (tmp_path / "real_captures_d0.5_a0_final" / entry["image"]).unlink()

    with pytest.raises(FileNotFoundError, match="missing-image"):
        target.load_real_captures(
            experiments_dir=tmp_path,
            positions=["d0.5_a0"],
            baseline_position=None,
        )


def test_capture_loader_accepts_legacy_ablation_when_profile_is_missing(tmp_path):
    entry = _capture_entry(
        "legacy-without-profile",
        ablation="vlm",
        attack="short",
        condition="vlm|short",
        profile="",
    )
    _write_position(tmp_path, "d0.5_a0", [entry])

    captures = target.load_real_captures(
        experiments_dir=tmp_path,
        positions=["d0.5_a0"],
        baseline_position=None,
    )

    assert captures[0]["ablation"] == "capture_hardened"
    assert captures[0]["profile"] == "capture_hardened"


@pytest.mark.parametrize("bad_truth", ["", "   "])
def test_capture_loader_rejects_empty_ground_truth(tmp_path, bad_truth):
    entry = _capture_entry(
        "empty-truth",
        ablation="vlm",
        attack="short",
        condition="vlm|short",
        profile="vlm",
        truth=bad_truth,
    )
    _write_position(tmp_path, "d0.5_a0", [entry])

    with pytest.raises(ValueError, match="ground truth"):
        target.load_real_captures(
            experiments_dir=tmp_path,
            positions=["d0.5_a0"],
            baseline_position=None,
        )


def test_capture_loader_rejects_duplicate_ids_within_position(tmp_path):
    entry = _capture_entry(
        "duplicate",
        ablation="vlm",
        attack="short",
        condition="vlm|short",
        profile="vlm",
    )
    _write_position(tmp_path, "d0.5_a0", [entry, dict(entry)])

    with pytest.raises(ValueError, match="duplicate capture key"):
        target.load_real_captures(
            experiments_dir=tmp_path,
            positions=["d0.5_a0"],
            baseline_position=None,
        )


def test_evaluate_model_retries_transient_failure_and_passes_max_tokens(tmp_path):
    image_path = tmp_path / "capture.png"
    Image.new("RGB", (4, 4), color="white").save(image_path)

    class FlakyClient:
        model = "model-A"

        def __init__(self):
            self.calls = 0
            self.max_tokens = []

        def analyze_image(self, image, ground_truth="", max_tokens=256):
            self.calls += 1
            self.max_tokens.append(max_tokens)
            if self.calls == 1:
                raise RuntimeError("HTTP 429")
            return {
                "visible_text": ground_truth,
                "can_read_sensitive": True,
                "confidence": 0.9,
                "notes": "readable",
                "usage": {"total_tokens": 12},
                "metrics": {
                    "char_accuracy": 1.0,
                    "word_accuracy": 1.0,
                    "exact_match": True,
                    "sensitive_token_recall": 1.0,
                    "sensitive_token_count": 1,
                },
            }

    client = FlakyClient()
    capture = {
        "id": "capture-1",
        "image_path": str(image_path),
        "truth": "SECRET-1234",
        "condition": "vlm|short",
        "ablation": "vlm",
        "attack": "short",
        "profile": "vlm",
        "position": "d0.5_a0",
        "distance_m": 0.5,
        "angle_degrees": 0.0,
        "capture_mode": "short_exposure",
    }

    rows = target.evaluate_model(
        client,
        [capture],
        delay=0,
        retries=1,
        retry_backoff=0,
        max_tokens=2048,
    )

    assert client.calls == 2
    assert client.max_tokens == [2048, 2048]
    assert rows[0]["vlm_error"] == ""
    assert rows[0]["exact_match"] is True
    assert rows[0]["vlm_notes"] == "readable"
    assert rows[0]["usage"] == {"total_tokens": 12}


def test_batched_run_checkpoints_completed_position_before_interrupt(tmp_path):
    captures = []
    for position in ("d0.5_a0", "d1_a0"):
        image_path = tmp_path / f"{position}.png"
        Image.new("RGB", (4, 4), color="white").save(image_path)
        captures.append({
            "id": f"capture-{position}",
            "image_path": str(image_path),
            "truth": "SECRET-1234",
            "condition": "vlm|short",
            "ablation": "vlm",
            "attack": "short",
            "profile": "vlm",
            "position": position,
            "distance_m": 0.5,
            "angle_degrees": 0.0,
            "capture_mode": "short_exposure",
        })

    class InterruptingClient:
        model = "model-A"

        def __init__(self):
            self.calls = 0

        def analyze_image(self, image, ground_truth="", max_tokens=256):
            self.calls += 1
            if self.calls == 2:
                raise KeyboardInterrupt
            return {
                "visible_text": ground_truth,
                "can_read_sensitive": True,
                "confidence": 0.9,
                "notes": "",
                "usage": {},
                "metrics": {
                    "char_accuracy": 1.0,
                    "word_accuracy": 1.0,
                    "exact_match": True,
                    "sensitive_token_recall": 1.0,
                    "sensitive_token_count": 1,
                },
            }

    client = InterruptingClient()
    partial_path = tmp_path / "result_partial.json"
    config = {"models": ["model-A"], "selection_sha256": "fixture"}

    with pytest.raises(KeyboardInterrupt):
        target.run_evaluation_batches(
            models=("model-A",),
            captures=captures,
            client_factory=lambda _model: client,
            partial_path=partial_path,
            resume_config=config,
            delay=0,
            retries=0,
            retry_backoff=0,
            max_tokens=2048,
        )

    saved_rows = target.load_partial(partial_path, config)
    assert [(row["position"], row["id"]) for row in saved_rows] == [
        ("d0.5_a0", "capture-d0.5_a0")
    ]


def test_batched_run_persists_image_load_errors(tmp_path):
    capture = {
        "id": "broken-image",
        "image_path": str(tmp_path / "missing.png"),
        "truth": "SECRET-1234",
        "condition": "vlm|short",
        "ablation": "vlm",
        "attack": "short",
        "profile": "vlm",
        "position": "d0.5_a0",
        "distance_m": 0.5,
        "angle_degrees": 0.0,
        "capture_mode": "short_exposure",
    }

    class UnusedClient:
        model = "model-A"

        def analyze_image(self, image, ground_truth="", max_tokens=256):
            raise AssertionError("client must not be called when image loading fails")

    partial_path = tmp_path / "result_partial.json"
    config = {"models": ["model-A"], "selection_sha256": "fixture"}
    rows = target.run_evaluation_batches(
        models=("model-A",),
        captures=[capture],
        client_factory=lambda _model: UnusedClient(),
        partial_path=partial_path,
        resume_config=config,
        delay=0,
        retries=0,
    )

    assert len(rows) == 1
    assert rows[0]["vlm_error"].startswith("image_load:")
    assert target.load_partial(partial_path, config) == rows


def test_batched_run_rejects_resume_rows_outside_selected_run(tmp_path):
    image_path = tmp_path / "capture.png"
    Image.new("RGB", (4, 4), color="white").save(image_path)
    capture = {
        "id": "capture-1",
        "image_path": str(image_path),
        "truth": "SECRET-1234",
        "condition": "vlm|short",
        "ablation": "vlm",
        "attack": "short",
        "profile": "vlm",
        "position": "d0.5_a0",
        "distance_m": 0.5,
        "angle_degrees": 0.0,
        "capture_mode": "short_exposure",
    }
    foreign_row = _result_row(model="model-B")

    with pytest.raises(ValueError, match="outside the selected run"):
        target.run_evaluation_batches(
            models=("model-A",),
            captures=[capture],
            client_factory=lambda _model: None,
            partial_path=tmp_path / "partial.json",
            resume_config={"models": ["model-A"]},
            existing_rows=[foreign_row],
            delay=0,
        )


def test_cli_single_position_dry_run_reports_all_seven_conditions(capsys):
    exit_code = target.main([
        "--dry-run",
        "--positions", "d0.5_a0",
        "--max-samples", "1",
        "--models", "model-A,model-B,model-C",
    ])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Loaded 7 captures" in output
    assert "Total API calls: 21" in output
    assert "original|short: 1" in output
    assert "capture_hardened|video|window_mean_best: 1" in output


def test_live_run_keeps_partial_on_errors_then_resume_replaces_them(
    tmp_path,
    monkeypatch,
):
    entries = [
        _capture_entry(
            "protected",
            ablation="vlm",
            attack="short",
            condition="vlm|short",
            profile="vlm",
        ),
        _capture_entry(
            "baseline",
            ablation="original",
            attack="short",
            condition="original|short",
            profile="off",
        ),
    ]
    _write_position(tmp_path, "d0.5_a0", entries)
    output_path = tmp_path / "real_capture_vlm.json"
    partial_path = target.partial_path_for_output(output_path)
    monkeypatch.setenv("SILICONFLOW_API_KEY", "test-key")

    class FailingClient:
        model = "model-A"

        def analyze_image(self, image, ground_truth="", max_tokens=256):
            raise RuntimeError("temporary service failure")

    first_exit = target.main(
        [
            "--models", "model-A",
            "--positions", "d0.5_a0",
            "--delay", "0",
            "--retries", "0",
            "--output", str(output_path),
        ],
        client_factory=lambda _model: FailingClient(),
        experiments_dir=tmp_path,
    )

    first = json.loads(output_path.read_text(encoding="utf-8"))
    assert first_exit == 3
    assert first["call_status"]["error_calls"] == 2
    assert first["call_status"]["run_complete"] is False
    assert first["cross_model"]["capture_hardened|short"]["model-A"] is None
    assert partial_path.exists()

    class SuccessfulClient:
        model = "model-A"

        def analyze_image(self, image, ground_truth="", max_tokens=256):
            return {
                "visible_text": ground_truth,
                "can_read_sensitive": True,
                "confidence": 0.9,
                "notes": "",
                "usage": {},
                "metrics": {
                    "char_accuracy": 1.0,
                    "word_accuracy": 1.0,
                    "exact_match": True,
                    "sensitive_token_recall": 1.0,
                    "sensitive_token_count": 1,
                },
            }

    second_exit = target.main(
        [
            "--resume",
            "--models", "model-A",
            "--positions", "d0.5_a0",
            "--delay", "0",
            "--retries", "0",
            "--output", str(output_path),
        ],
        client_factory=lambda _model: SuccessfulClient(),
        experiments_dir=tmp_path,
    )

    second = json.loads(output_path.read_text(encoding="utf-8"))
    assert second_exit == 0
    assert second["call_status"]["successful_calls"] == 2
    assert second["call_status"]["error_calls"] == 0
    assert len(second["models"]["model-A"]["rows"]) == 2
    assert not partial_path.exists()
