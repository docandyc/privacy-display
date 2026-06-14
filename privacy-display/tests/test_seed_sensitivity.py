import json

import numpy as np

from experiments.seed_sensitivity import RESULT_FILE, run_seed_sensitivity


class _FakeOCR:
    engines = ["tesseract"]

    class _Result:
        char_accuracy = 0.0

    def evaluate_single(self, image, ground_truth="", engine="tesseract"):
        return self._Result()


def test_run_seed_sensitivity_reports_invariance(tmp_path):
    img = np.full((24, 24, 3), 160, dtype=np.uint8)
    corpus = ([img], ["SECRET-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code"}}

    report = run_seed_sensitivity(
        output_dir=tmp_path,
        n=4,
        epsilon=0.0,
        n_seeds=3,
        max_samples=1,
        evaluator=_FakeOCR(),
        corpus=corpus,
        metadata=metadata,
        progress_interval=0,
    )

    stored = json.loads((tmp_path / RESULT_FILE).read_text(encoding="utf-8"))
    assert stored["config"]["n_seeds"] == 3
    assert set(stored["summary"]) == {"single_frame_ocr", "perceptual_invariance"}

    ocr = stored["summary"]["single_frame_ocr"]
    assert "ci95" in ocr
    # Faked OCR is constant -> exactly seed-invariant.
    assert ocr["mean_across_seed_std"] == 0.0

    delta_e = stored["summary"]["perceptual_invariance"]["delta_e"]
    # epsilon=0 -> exact reconstruction under every key -> seed-invariant ΔE.
    assert delta_e["mean"] < 1.0
    assert delta_e["mean_across_seed_std"] == 0.0

    assert report["summary"]["perceptual_invariance"]["entropy_ratio"]["count"] == 3
