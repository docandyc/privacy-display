import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from experiments import rerun_corpus_surya


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_corpus_surya_rerun_module_exists():
    assert importlib.util.find_spec("experiments.rerun_corpus_surya") is not None


def test_direct_script_bootstraps_project_root_for_src_import(tmp_path):
    script = PROJECT_ROOT / "experiments" / "rerun_corpus_surya.py"
    probe = (
        "import runpy, sys; "
        f"runpy.run_path({str(script)!r}, run_name='path_probe'); "
        f"assert {str(PROJECT_ROOT)!r} in sys.path, sys.path; "
        "print('project root OK')"
    )
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    completed = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "project root OK" in completed.stdout


def test_merge_results_keeps_legacy_engines_and_removes_paddleocr():
    merge_results = getattr(rerun_corpus_surya, "merge_results", None)
    assert callable(merge_results)

    tesseract = {"n_samples": 120, "original_mean": 0.94}
    easyocr = {"n_samples": 120, "original_mean": 0.941}
    existing = {
        "tesseract": tesseract,
        "easyocr": easyocr,
        "paddleocr": {"n_samples": 120, "original_mean": 0.949},
    }
    surya = {"surya": {"n_samples": 120, "original_mean": 0.88}}

    merged = merge_results(existing, surya)

    assert list(merged) == ["tesseract", "easyocr", "surya"]
    assert merged["tesseract"] is tesseract
    assert merged["easyocr"] is easyocr
    assert merged["surya"] == surya["surya"]


@pytest.mark.parametrize(
    "existing, message",
    [
        ({"easyocr": {}}, "tesseract"),
        ({"tesseract": {}}, "easyocr"),
        ([], "JSON object"),
    ],
)
def test_validate_existing_results_rejects_missing_or_malformed_data(existing, message):
    validate = getattr(rerun_corpus_surya, "validate_existing_results", None)
    assert callable(validate)

    with pytest.raises(ValueError, match=message):
        validate(existing)


def test_run_surya_only_keeps_existing_file_when_runner_fails(tmp_path):
    run_surya_only = getattr(rerun_corpus_surya, "run_surya_only", None)
    assert callable(run_surya_only)

    result_path = tmp_path / "corpus_multi_engine.json"
    original = {
        "tesseract": {"n_samples": 120},
        "easyocr": {"n_samples": 120},
        "paddleocr": {"n_samples": 120},
    }
    original_text = json.dumps(original, ensure_ascii=False, indent=2)
    result_path.write_text(original_text, encoding="utf-8")

    def failing_runner(**kwargs):
        raise RuntimeError("surya failed")

    with pytest.raises(RuntimeError, match="surya failed"):
        run_surya_only(result_path, runner=failing_runner)

    assert result_path.read_text(encoding="utf-8") == original_text


def test_run_surya_only_writes_strict_three_engine_result(tmp_path):
    result_path = tmp_path / "corpus_multi_engine.json"
    original = {
        "tesseract": {"n_samples": 120, "original_mean": 0.94},
        "easyocr": {"n_samples": 120, "original_mean": 0.941},
        "paddleocr": {"n_samples": 120, "original_mean": 0.949},
        "stale_engine": {"n_samples": 1},
    }
    result_path.write_text(json.dumps(original), encoding="utf-8")
    calls = []

    def successful_runner(**kwargs):
        calls.append(kwargs)
        return {"surya": {"n_samples": 120, "original_mean": 0.88}}

    merged = rerun_corpus_surya.run_surya_only(result_path, runner=successful_runner)
    stored = json.loads(result_path.read_text(encoding="utf-8"))

    assert stored == merged
    assert list(stored) == ["tesseract", "easyocr", "surya"]
    assert calls[0]["engines"] == ["surya"]
    assert calls[0]["progress_interval"] == 1
    assert calls[0]["merge_existing"] is False


def test_one_click_shell_entrypoint_uses_surya_environment():
    script = PROJECT_ROOT / "scripts" / "rerun_corpus_surya.sh"

    assert script.is_file()
    assert script.stat().st_mode & 0o111
    text = script.read_text(encoding="utf-8")
    assert ".venv-surya/bin/python" in text
    assert "experiments/rerun_corpus_surya.py" in text


def test_cli_runs_injected_surya_runner_and_prints_summary(tmp_path, capsys):
    main = getattr(rerun_corpus_surya, "main", None)
    assert callable(main)

    result_path = tmp_path / "corpus_multi_engine.json"
    result_path.write_text(
        json.dumps({
            "tesseract": {
                "n_samples": 120,
                "original_mean": 0.94,
                "subframe_mean": 0.0,
                "paired_reduction": {"mean": 0.94},
            },
            "easyocr": {
                "n_samples": 120,
                "original_mean": 0.941,
                "subframe_mean": 0.0,
                "paired_reduction": {"mean": 0.941},
            },
            "paddleocr": {"n_samples": 120},
        }),
        encoding="utf-8",
    )

    def successful_runner(**kwargs):
        return {
            "surya": {
                "n_samples": 120,
                "original_mean": 0.88,
                "subframe_mean": 0.01,
                "paired_reduction": {"mean": 0.87},
            }
        }

    exit_code = main(
        ["--result", str(result_path)],
        runner=successful_runner,
        runtime_checker=lambda: None,
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "只运行 Surya" in output
    assert "Surya" in output
    assert "88.0%" in output
