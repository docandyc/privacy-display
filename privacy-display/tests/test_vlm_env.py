import os

from experiments.vlm_readability_analysis import load_local_env


def test_load_local_env_reads_quoted_values_without_overriding_existing(tmp_path, monkeypatch):
    env_file = tmp_path / ".env.local"
    env_file.write_text(
        "\n".join([
            "# local secrets",
            'SILICONFLOW_API_KEY="sk-local-secret"',
            "EXISTING=value-from-file",
        ]),
        encoding="utf-8",
    )
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    monkeypatch.setenv("EXISTING", "value-from-shell")

    load_local_env(env_file)

    assert os.environ["SILICONFLOW_API_KEY"] == "sk-local-secret"
    assert os.environ["EXISTING"] == "value-from-shell"
