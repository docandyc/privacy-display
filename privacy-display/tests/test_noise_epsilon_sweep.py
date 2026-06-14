import json

import numpy as np

from experiments.noise_epsilon_sweep import RESULT_FILE, run_epsilon_sweep


class _FakeOCR:
    """OCR evaluator stub: keeps the sweep hermetic (no Tesseract dependency)."""

    engines = ["tesseract"]

    class _Result:
        char_accuracy = 0.0

    def evaluate_single(self, image, ground_truth="", engine="tesseract"):
        return self._Result()


def test_run_epsilon_sweep_writes_report(tmp_path):
    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, size=(32, 32, 3), dtype=np.uint8)
    corpus = ([img], ["SECRET-1234"], ["sample_0"])
    metadata = {"sample_0": {"category": "code", "language": "en"}}
    epsilons = (0.0, 8 / 255)

    report = run_epsilon_sweep(
        output_dir=tmp_path,
        n=4,
        epsilons=epsilons,
        max_samples=1,
        evaluator=_FakeOCR(),
        corpus=corpus,
        metadata=metadata,
        progress_interval=0,
    )

    stored = json.loads((tmp_path / RESULT_FILE).read_text(encoding="utf-8"))

    assert stored["config"]["epsilons"] == [0.0, 8 / 255]
    assert stored["config"]["n_samples"] == 1
    assert set(stored["summary"]) == {"eps_0.0000", "eps_0.0314"}

    eps0 = stored["summary"]["eps_0.0000"]
    # gamma=1, boost=n, epsilon=0 -> integrated reconstructs the original exactly.
    assert eps0["delta_e"]["mean"] < 1.0
    assert "ci95" in eps0["single_frame_ocr"]
    assert eps0["single_frame_ocr"]["mean"] == 0.0
    # Every measured quantity is summarized with a bootstrap CI.
    for key in ("ssim", "temporal_mod", "weak_mask_only_ocr", "weak_mask_noise_ocr", "noise_margin"):
        assert "ci95" in eps0[key]

    assert report["config"]["fpi"] > 0
