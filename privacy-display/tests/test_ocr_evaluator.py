import numpy as np
import sys
import types
from pathlib import Path

from src.attack.ocr_evaluator import (
    OCREvaluator,
    _sensitive_token_recall,
    _sensitive_tokens,
)


def test_parse_surya_result_objects_and_dicts():
    result = [
        types.SimpleNamespace(
            text_lines=[
                types.SimpleNamespace(text="Hello"),
                types.SimpleNamespace(text="世界"),
            ]
        ),
        {"text_lines": [{"text": "second page"}]},
    ]

    assert OCREvaluator._parse_surya_text(result) == "Hello 世界 second page"


def test_recognize_surya_uses_cached_readers():
    calls = []

    class FakeRecognitionPredictor:
        def __call__(self, images, **kwargs):
            calls.append((images, kwargs))
            return [
                types.SimpleNamespace(
                    text_lines=[
                        types.SimpleNamespace(text="cached"),
                        types.SimpleNamespace(text="reader"),
                    ]
                )
            ]

    evaluator = OCREvaluator(engines=["surya"])
    detector = object()
    evaluator._surya_readers = (FakeRecognitionPredictor(), detector)
    image = np.zeros((8, 8, 3), dtype=np.uint8)

    assert evaluator.recognize(image[:, ::-1], "surya") == "cached reader"
    assert calls[0][1] == {
        "det_predictor": detector,
        "sort_lines": True,
        "math_mode": False,
    }


def test_surya_device_env_is_respected(monkeypatch):
    monkeypatch.setenv("SURYA_DEVICE", "cpu")

    assert OCREvaluator._resolve_surya_device() == "cpu"


def test_heavy_ocr_auto_detection_is_offline_safe(monkeypatch):
    monkeypatch.setattr(OCREvaluator, "_trocr_cache_available", classmethod(lambda cls: False))
    monkeypatch.delenv("PRIVACY_DISPLAY_ENABLE_DOCTR_AUTO", raising=False)

    evaluator = OCREvaluator(engines=[])
    engines = evaluator._detect_available_engines()

    assert "trocr" not in engines
    assert "doctr" not in engines


def test_tesseract_detection_uses_windows_program_files_path(monkeypatch):
    expected = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

    class FakePytesseract:
        class pytesseract:
            tesseract_cmd = "tesseract"

        @staticmethod
        def get_tesseract_version():
            if FakePytesseract.pytesseract.tesseract_cmd != str(expected):
                raise RuntimeError("not in PATH")
            return "5.5.0"

    monkeypatch.setitem(sys.modules, "pytesseract", FakePytesseract)
    monkeypatch.setenv("ProgramFiles", r"C:\Program Files")
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.delenv("TESSERACT_CMD", raising=False)
    monkeypatch.delenv("TESSERACT_EXE", raising=False)
    monkeypatch.setattr("src.attack.ocr_evaluator.shutil.which", lambda name: None, raising=False)
    monkeypatch.setattr("src.attack.ocr_evaluator.os.name", "nt")
    monkeypatch.setattr(
        "src.attack.ocr_evaluator.Path.exists",
        lambda self: str(self) == str(expected),
    )

    evaluator = OCREvaluator(engines=[])

    assert "tesseract" in evaluator._detect_available_engines()
    assert FakePytesseract.pytesseract.tesseract_cmd == str(expected)


def test_trocr_loader_uses_local_files_only(monkeypatch):
    calls = []

    class FakeProcessor:
        @classmethod
        def from_pretrained(cls, model_id, local_files_only=False):
            calls.append(("processor", model_id, local_files_only))
            return cls()

        def __call__(self, images, return_tensors):
            return types.SimpleNamespace(pixel_values="pixels")

        def batch_decode(self, generated_ids, skip_special_tokens=True):
            return ["decoded text"]

    class FakeModel:
        @classmethod
        def from_pretrained(cls, model_id, local_files_only=False):
            calls.append(("model", model_id, local_files_only))
            return cls()

        def eval(self):
            return None

        def generate(self, pixel_values, max_new_tokens):
            return ["ids"]

    class FakeNoGrad:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_transformers = types.SimpleNamespace(
        TrOCRProcessor=FakeProcessor,
        VisionEncoderDecoderModel=FakeModel,
    )
    fake_torch = types.SimpleNamespace(no_grad=lambda: FakeNoGrad())
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    evaluator = OCREvaluator(engines=["trocr"])
    image = np.zeros((8, 8, 3), dtype=np.uint8)

    assert evaluator.recognize(image, "trocr") == "decoded text"
    assert calls == [
        ("processor", OCREvaluator.TROCR_MODEL_ID, True),
        ("model", OCREvaluator.TROCR_MODEL_ID, True),
    ]


def test_sensitive_tokens_focus_on_structured_fields():
    text = "The quick token sk-test-4821 belongs to user@mail.com"

    tokens = _sensitive_tokens(text)

    assert "sk-test-4821" in tokens
    assert "user@mail.com" in tokens
    assert "quick" not in tokens


def test_sensitive_token_recall_and_protection_metrics():
    class FakeEvaluator(OCREvaluator):
        def __init__(self):
            super().__init__(engines=["fake"])
            self._texts = iter(["API KEY sk-test-4821", "", "sk-test-4821"])

        def recognize(self, image, engine="fake"):
            return next(self._texts)

    recall, count = _sensitive_token_recall("leaked sk-test-4821", "API KEY sk-test-4821")
    assert count == 1
    assert recall == 1.0

    image = np.zeros((2, 2, 3), dtype=np.uint8)
    evaluator = FakeEvaluator()
    report = evaluator.evaluate_protection(
        image,
        [image.copy(), image.copy()],
        "API KEY sk-test-4821",
        "fake",
    )

    assert report["original_exact_match"] is True
    assert report["original_word_acc"] == 1.0
    assert report["sensitive_token_count"] == 1
    assert report["original_sensitive_token_recall"] == 1.0
    assert report["mean_subframe_exact_match"] == 0.0
    assert report["mean_subframe_sensitive_token_recall"] == 0.5
