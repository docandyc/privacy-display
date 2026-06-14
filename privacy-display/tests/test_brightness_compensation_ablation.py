import json

import numpy as np

from experiments.brightness_compensation_ablation import RESULT_FILE, run_brightness_ablation


class _FakeOCR:
    engines = ["tesseract"]

    class _Result:
        char_accuracy = 0.0

    def evaluate_single(self, image, ground_truth="", engine="tesseract"):
        return self._Result()


def test_run_brightness_ablation_quantifies_compensation_cost(tmp_path):
    # Mid-gray content saturates under full pixel compensation (gamma=n) but
    # reconstructs exactly under the backlight-only model (gamma=1).
    img = np.full((24, 24, 3), 160, dtype=np.uint8)
    corpus = ([img], ["SECRET-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code"}}

    report = run_brightness_ablation(
        output_dir=tmp_path,
        n=4,
        epsilon=0.0,
        gammas=(1.0, 4.0),
        max_samples=1,
        evaluator=_FakeOCR(),
        corpus=corpus,
        metadata=metadata,
        progress_interval=0,
    )

    stored = json.loads((tmp_path / RESULT_FILE).read_text(encoding="utf-8"))
    assert set(stored["summary"]) == {"gamma_1.00", "gamma_4.00"}

    backlight = stored["summary"]["gamma_1.00"]
    full_pixel = stored["summary"]["gamma_4.00"]

    # Backlight-only model: integration boost = n, exact reconstruction, no clipping.
    assert backlight["integration_boost"] == 4.0
    assert backlight["delta_e"]["mean"] < 1.0
    assert backlight["clip_fraction"]["mean"] == 0.0
    # Full pixel compensation: integration boost = 1, clips highlights -> larger ΔE.
    assert full_pixel["integration_boost"] == 1.0
    assert full_pixel["clip_fraction"]["mean"] > 0.0
    assert full_pixel["delta_e"]["mean"] > backlight["delta_e"]["mean"]
    assert "ci95" in backlight["single_frame_ocr"]

    assert report["config"]["gammas"] == [1.0, 4.0]
