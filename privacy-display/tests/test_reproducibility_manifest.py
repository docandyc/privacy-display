import hashlib
import json

from src.evaluation.reproducibility_manifest import (
    build_reproducibility_manifest,
    file_record,
    sha256_file,
    write_reproducibility_manifest,
)


def test_manifest_records_hashes_commands_and_no_secret_values(tmp_path, monkeypatch):
    result_path = tmp_path / "experiments" / "results" / "result.json"
    source_path = tmp_path / "src" / "evaluation" / "module.py"
    result_path.parent.mkdir(parents=True)
    source_path.parent.mkdir(parents=True)
    result_path.write_text('{"metric": 1}', encoding="utf-8")
    source_path.write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setenv("SILICONFLOW_API_KEY", "sk-test-secret-value")

    manifest = build_reproducibility_manifest(
        tmp_path,
        result_files=["experiments/results/result.json", "experiments/results/missing.json"],
        source_files=["src/evaluation/module.py"],
        timestamp="2026-06-13T00:00:00+00:00",
    )
    payload = json.dumps(manifest, ensure_ascii=False)

    assert manifest["schema_version"] == 1
    assert manifest["result_files"][0]["exists"] is True
    assert manifest["result_files"][0]["sha256"] == hashlib.sha256(b'{"metric": 1}').hexdigest()
    assert manifest["result_files"][1] == {
        "path": "experiments/results/missing.json",
        "exists": False,
        "sha256": "",
        "bytes": 0,
    }
    assert manifest["source_files"][0]["exists"] is True
    assert any(command["name"] == "vlm_live" for command in manifest["commands"])
    assert any(command["name"] == "reproduce_quick" for command in manifest["commands"])
    assert any(command["name"] == "component_ablation" for command in manifest["commands"])
    assert any(command["name"] == "adaptive_attack_ablation" for command in manifest["commands"])
    vlm_live = next(command for command in manifest["commands"] if command["name"] == "vlm_live")
    reproduce_live = next(command for command in manifest["commands"] if command["name"] == "reproduce_with_vlm_live")
    assert vlm_live["requires_env"] == ["SILICONFLOW_API_KEY"]
    assert reproduce_live["requires_env"] == ["SILICONFLOW_API_KEY"]
    assert manifest["secret_policy"]["record_secret_values"] is False
    assert "SILICONFLOW_API_KEY" in payload
    assert "sk-test-secret-value" not in payload


def test_file_record_and_sha256_file(tmp_path):
    path = tmp_path / "artifact.txt"
    path.write_text("artifact\n", encoding="utf-8")

    assert sha256_file(path) == hashlib.sha256(b"artifact\n").hexdigest()
    assert file_record(tmp_path, "artifact.txt") == {
        "path": "artifact.txt",
        "exists": True,
        "sha256": hashlib.sha256(b"artifact\n").hexdigest(),
        "bytes": len(b"artifact\n"),
    }


def test_write_reproducibility_manifest_writes_nested_output(tmp_path):
    manifest = build_reproducibility_manifest(
        tmp_path,
        result_files=[],
        source_files=[],
        timestamp="2026-06-13T00:00:00+00:00",
    )

    write_reproducibility_manifest(tmp_path, "out/repro.json", manifest=manifest)

    written = json.loads((tmp_path / "out" / "repro.json").read_text(encoding="utf-8"))
    assert written["generated_at_utc"] == "2026-06-13T00:00:00+00:00"
    assert written["result_files"] == []
    assert written["source_files"] == []
