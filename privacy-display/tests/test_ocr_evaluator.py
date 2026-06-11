import numpy as np

from src.attack.ocr_evaluator import OCREvaluator


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
