import numpy as np
import sys
import types

from src.attack.ocr_evaluator import (
    OCREvaluator,
    _sensitive_token_recall,
    _sensitive_tokens,
)


def test_parse_paddleocr_v2_result():
    result = [
        [
            [[[0, 0], [10, 0], [10, 10], [0, 10]], ("Hello", 0.99)],
            [[[12, 0], [20, 0], [20, 10], [12, 10]], ("世界", 0.98)],
        ]
    ]

    assert OCREvaluator._parse_paddleocr_text(result) == "Hello 世界"


def test_parse_paddleocr_v3_result_dict():
    result = [{"res": {"rec_texts": ["Hello", "PaddleOCR"]}}]

    assert OCREvaluator._parse_paddleocr_text(result) == "Hello PaddleOCR"


def test_recognize_paddleocr_uses_cached_reader():
    class FakeReader:
        def predict(self, image):
            assert image.flags["C_CONTIGUOUS"]
            return [{"res": {"rec_texts": ["cached", "reader"]}}]

    evaluator = OCREvaluator(engines=["paddleocr"])
    evaluator._paddleocr_reader = FakeReader()

    image = np.zeros((8, 8, 3), dtype=np.uint8)

    assert evaluator.recognize(image, "paddleocr") == "cached reader"


def test_heavy_ocr_auto_detection_is_offline_safe(monkeypatch):
    monkeypatch.setattr(OCREvaluator, "_trocr_cache_available", classmethod(lambda cls: False))
    monkeypatch.delenv("PRIVACY_DISPLAY_ENABLE_DOCTR_AUTO", raising=False)

    evaluator = OCREvaluator(engines=[])
    engines = evaluator._detect_available_engines()

    assert "trocr" not in engines
    assert "doctr" not in engines


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
