import json

import numpy as np

from experiments.mask_granularity_ablation import RESULT_FILE, run_granularity_ablation


class _FakeOCR:
    engines = ["tesseract"]

    class _Result:
        char_accuracy = 0.0

    def evaluate_single(self, image, ground_truth="", engine="tesseract"):
        return self._Result()


def test_run_granularity_ablation_block_flicker_tradeoff(tmp_path):
    img = np.full((48, 48, 3), 160, dtype=np.uint8)
    corpus = ([img], ["SECRET-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code"}}

    report = run_granularity_ablation(
        output_dir=tmp_path,
        n=4,
        block_sizes=(1, 8),
        pool=25,
        max_samples=1,
        evaluator=_FakeOCR(),
        corpus=corpus,
        metadata=metadata,
        progress_interval=0,
    )

    stored = json.loads((tmp_path / RESULT_FILE).read_text(encoding="utf-8"))
    assert set(stored["summary"]) == {"block_1", "block_8"}

    fine = stored["summary"]["block_1"]
    coarse = stored["summary"]["block_8"]

    # Coarser blocks defeat receptive-field spatial pooling -> more pooled flicker.
    assert coarse["pooled_flicker"]["mean"] > fine["pooled_flicker"]["mean"]
    # Any partition reconstructs exactly, so ΔE stays imperceptible for both.
    assert fine["delta_e"]["mean"] < 1.0
    assert coarse["delta_e"]["mean"] < 1.0
    assert "ci95" in fine["entropy_ratio"]

    assert report["config"]["block_sizes"] == [1, 8]
