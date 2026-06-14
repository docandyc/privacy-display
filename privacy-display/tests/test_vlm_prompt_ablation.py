import json

import numpy as np
import pytest

from experiments.vlm_prompt_ablation import RESULT_FILE, run_prompt_ablation


def test_run_prompt_ablation_writes_report_with_fake_client(tmp_path):
    class FakeClient:
        model = "fake-vlm"
        base_url = "https://example.invalid/v1"

        def analyze_image(self, image, ground_truth="", prompt=None):
            return {
                "visible_text": ground_truth,
                "can_read_sensitive": True,
                "confidence": 0.9,
                "notes": prompt[:8] if prompt else "",
            }

    image = np.full((8, 8, 3), 160, dtype=np.uint8)
    corpus = ([image], ["CODE-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code", "language": "en"}}

    report = run_prompt_ablation(
        client=FakeClient(),
        output_dir=tmp_path,
        n=2,
        epsilon=0.0,
        cycles=1,
        attacks=("original",),
        corpus=corpus,
        metadata=metadata,
        progress_interval=0,
    )

    stored = json.loads((tmp_path / RESULT_FILE).read_text(encoding="utf-8"))

    assert report["config"]["planned_calls"] == 3
    assert stored["config"]["completed_calls"] == 3
    assert stored["config"]["interrupted"] is False
    assert len(stored["samples"]) == 3
    assert stored["summary"]["strict_transcription"]["char_accuracy"]["mean"] == 1.0


def test_run_prompt_ablation_saves_partial_report_on_keyboard_interrupt(tmp_path):
    class InterruptingClient:
        model = "fake-vlm"
        base_url = "https://example.invalid/v1"

        def __init__(self):
            self.calls = 0

        def analyze_image(self, image, ground_truth="", prompt=None):
            self.calls += 1
            if self.calls == 2:
                raise KeyboardInterrupt
            return {
                "visible_text": ground_truth,
                "can_read_sensitive": True,
                "confidence": 0.9,
                "notes": "",
            }

    image = np.full((8, 8, 3), 160, dtype=np.uint8)
    corpus = ([image], ["CODE-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code", "language": "en"}}

    with pytest.raises(KeyboardInterrupt):
        run_prompt_ablation(
            client=InterruptingClient(),
            output_dir=tmp_path,
            n=2,
            epsilon=0.0,
            cycles=1,
            attacks=("original",),
            corpus=corpus,
            metadata=metadata,
            progress_interval=0,
        )

    stored = json.loads((tmp_path / RESULT_FILE).read_text(encoding="utf-8"))

    assert stored["config"]["planned_calls"] == 3
    assert stored["config"]["completed_calls"] == 1
    assert stored["config"]["interrupted"] is True
    assert len(stored["samples"]) == 1
