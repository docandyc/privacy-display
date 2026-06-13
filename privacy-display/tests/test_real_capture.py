import json

import numpy as np
from PIL import Image
import pytest

from src.attack.ocr_evaluator import OCRResult
from src.evaluation.real_capture import (
    REAL_CAPTURE_JSON,
    REAL_CAPTURE_MD,
    load_capture_metadata,
    run_real_capture_ocr,
    write_capture_template,
)


class FakeEvaluator:
    engines = ["fakeocr"]

    def evaluate_single(self, image, ground_truth, engine):
        assert engine == "fakeocr"
        assert image.shape == (8, 10, 3)
        return OCRResult(engine=engine, text=ground_truth, char_accuracy=1.0, word_accuracy=1.0)


def _write_metadata(root, captures):
    (root / "metadata.json").write_text(
        json.dumps({"schema_version": 1, "captures": captures}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_write_capture_template_and_validate_metadata(tmp_path):
    out = write_capture_template(tmp_path)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["captures"][0]["condition"] == "protected"

    with pytest.raises(FileNotFoundError):
        load_capture_metadata(tmp_path, "missing.json")

    (tmp_path / "bad.json").write_text('{"captures": {}}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_capture_metadata(tmp_path, "bad.json")


def test_run_real_capture_ocr_writes_json_and_markdown(tmp_path):
    Image.fromarray(np.full((8, 10, 3), 220, dtype=np.uint8)).save(tmp_path / "capture.png")
    _write_metadata(
        tmp_path,
        [
            {
                "id": "sample",
                "image": "capture.png",
                "truth": "CODE-1234",
                "condition": "protected",
                "device": "phone-a",
                "camera_type": "phone",
                "capture_mode": "short_exposure",
                "distance_m": 1.0,
                "angle_degrees": 15,
                "display_refresh_hz": 240,
                "n": 4,
            }
        ],
    )

    report = run_real_capture_ocr(
        capture_dir=tmp_path,
        output_dir=tmp_path / "results",
        engines=["fakeocr"],
        evaluator=FakeEvaluator(),
    )

    assert report["config"]["n_captures"] == 1
    assert report["summary"]["by_condition"]["protected"]["char_accuracy"]["mean"] == 1.0
    assert report["summary"]["by_device"]["phone-a"]["leak_rate_char_ge_20pct"]["mean"] == 1.0
    assert (tmp_path / "results" / REAL_CAPTURE_JSON).exists()
    assert (tmp_path / "results" / REAL_CAPTURE_MD).exists()


def test_run_real_capture_ocr_rejects_missing_image(tmp_path):
    _write_metadata(
        tmp_path,
        [{"id": "missing", "image": "missing.png", "truth": "SECRET"}],
    )

    with pytest.raises(FileNotFoundError):
        run_real_capture_ocr(
            capture_dir=tmp_path,
            output_dir=tmp_path / "results",
            engines=["fakeocr"],
            evaluator=FakeEvaluator(),
        )
