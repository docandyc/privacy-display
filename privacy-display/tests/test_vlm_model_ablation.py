import json

import numpy as np

from experiments.vlm_model_ablation import RESULT_FILE, run_model_ablation


class _FakeClient:
    """Returns the ground truth verbatim, so char accuracy is 1.0 (no API call)."""

    base_url = "https://example.invalid/v1"

    def __init__(self, model):
        self.model = model

    def analyze_image(self, image, ground_truth="", prompt=None):
        return {
            "visible_text": ground_truth,
            "can_read_sensitive": True,
            "confidence": 0.9,
            "notes": "",
        }


def test_run_model_ablation_writes_cross_model_report(tmp_path):
    image = np.full((8, 8, 3), 160, dtype=np.uint8)
    corpus = ([image], ["CODE-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code", "language": "en"}}
    clients = {"model-A": _FakeClient("model-A"), "model-B": _FakeClient("model-B")}
    attacks = ("original", "global_shutter_slot0")

    report = run_model_ablation(
        clients=clients,
        output_dir=tmp_path,
        n=2,
        epsilon=0.0,
        cycles=1,
        samples_per_category=1,
        attacks=attacks,
        corpus=corpus,
        metadata=metadata,
        progress_interval=0,
    )

    stored = json.loads((tmp_path / RESULT_FILE).read_text(encoding="utf-8"))

    assert stored["config"]["models"] == ["model-A", "model-B"]
    assert stored["config"]["n_selected_samples"] == 1
    assert stored["config"]["planned_calls_total"] == 1 * 2 * 2
    assert set(stored["models"]) == {"model-A", "model-B"}
    assert set(stored["summary"]) == {"model-A", "model-B"}
    # Faked client transcribes the ground truth -> char accuracy 1.0 for both models.
    assert stored["summary"]["model-A"]["char_accuracy"]["mean"] == 1.0
    assert set(stored["cross_model"]) == set(attacks)
    for attack in attacks:
        assert stored["cross_model"][attack]["model-A"] == 1.0
        assert stored["cross_model"][attack]["model-B"] == 1.0

    assert report["config"]["planned_calls_total"] == 4
