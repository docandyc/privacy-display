"""
OCR 准确率评估器

测量原始帧与子帧的 OCR 识别准确率，量化隐私保护效果。
支持 Tesseract、EasyOCR、PaddleOCR 三种主流 OCR 引擎。
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class OCRResult:
    engine: str
    text: str
    char_accuracy: float   # CER 的补集：1 - CER
    word_accuracy: float   # WER 的补集：1 - WER


def _edit_distance(a: str, b: str) -> int:
    """标准 Levenshtein 编辑距离。"""
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[:]
        dp[0] = i
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[j] = prev[j-1]
            else:
                dp[j] = 1 + min(prev[j], dp[j-1], prev[j-1])
    return dp[n]


def _char_accuracy(pred: str, ref: str) -> float:
    if not ref:
        return 1.0 if not pred else 0.0
    cer = _edit_distance(pred, ref) / max(len(ref), 1)
    return max(0.0, 1.0 - cer)


def _word_accuracy(pred: str, ref: str) -> float:
    pred_words = pred.split()
    ref_words = ref.split()
    if not ref_words:
        return 1.0 if not pred_words else 0.0
    wer = _edit_distance(pred_words, ref_words) / max(len(ref_words), 1)
    return max(0.0, 1.0 - wer)


class OCREvaluator:
    def __init__(self, engines: list[str] | None = None):
        """
        Args:
            engines: 使用的 OCR 引擎列表，可选 'tesseract', 'easyocr', 'paddleocr'
                     None 时自动检测可用引擎
        """
        self.engines = engines or self._detect_available_engines()
        self._easyocr_reader = None
        self._paddleocr_reader = None

    def _detect_available_engines(self) -> list[str]:
        available = []
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            available.append("tesseract")
        except Exception:
            pass
        try:
            import easyocr  # noqa: F401
            available.append("easyocr")
        except ImportError:
            pass
        try:
            import paddleocr  # noqa: F401
            available.append("paddleocr")
        except Exception:
            pass
        return available

    def _run_tesseract(self, image: np.ndarray) -> str:
        import pytesseract
        from PIL import Image
        pil_img = Image.fromarray(image)
        return pytesseract.image_to_string(pil_img, lang="chi_sim+eng").strip()

    def _run_easyocr(self, image: np.ndarray) -> str:
        import easyocr
        if self._easyocr_reader is None:
            self._easyocr_reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
        results = self._easyocr_reader.readtext(image, detail=0)
        return " ".join(results)

    def _run_paddleocr(self, image: np.ndarray) -> str:
        from paddleocr import PaddleOCR

        if self._paddleocr_reader is None:
            self._paddleocr_reader = PaddleOCR(
                lang="ch",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )

        if hasattr(self._paddleocr_reader, "predict"):
            result = self._paddleocr_reader.predict(image)
        else:
            result = self._paddleocr_reader.ocr(image)
        return self._parse_paddleocr_text(result)

    @classmethod
    def _parse_paddleocr_text(cls, result) -> str:
        """解析 PaddleOCR 2.x/3.x 常见返回结构中的识别文本。"""
        texts: list[str] = []
        cls._collect_paddle_text(result, texts)
        return " ".join(t for t in texts if t)

    @classmethod
    def _collect_paddle_text(cls, value, texts: list[str]) -> None:
        if value is None:
            return
        if isinstance(value, str):
            texts.append(value)
            return
        if isinstance(value, dict):
            for key in ("rec_texts", "text", "texts"):
                if key in value:
                    cls._collect_paddle_text(value[key], texts)
                    return
            if "res" in value:
                cls._collect_paddle_text(value["res"], texts)
                return
            for child in value.values():
                cls._collect_paddle_text(child, texts)
            return
        if hasattr(value, "json"):
            cls._collect_paddle_text(value.json, texts)
            return
        if hasattr(value, "res"):
            cls._collect_paddle_text(value.res, texts)
            return
        if isinstance(value, tuple):
            if len(value) == 2 and isinstance(value[0], str):
                texts.append(value[0])
                return
            if len(value) == 2 and isinstance(value[1], (int, float)):
                cls._collect_paddle_text(value[0], texts)
                return
        if isinstance(value, list):
            # PaddleOCR 2.x: [box, ("text", score)]
            if (
                len(value) == 2
                and isinstance(value[1], tuple)
                and value[1]
                and isinstance(value[1][0], str)
            ):
                texts.append(value[1][0])
                return
            for child in value:
                cls._collect_paddle_text(child, texts)

    def recognize(self, image: np.ndarray, engine: str = "tesseract") -> str:
        """对单张图像运行 OCR，返回识别文本。"""
        image = np.ascontiguousarray(image)
        if engine == "tesseract":
            return self._run_tesseract(image)
        elif engine == "easyocr":
            return self._run_easyocr(image)
        elif engine == "paddleocr":
            return self._run_paddleocr(image)
        else:
            raise ValueError(f"不支持的引擎: {engine}")

    def evaluate_single(
        self,
        image: np.ndarray,
        ground_truth: str,
        engine: str = "tesseract",
    ) -> OCRResult:
        """评估单张图像的 OCR 准确率。"""
        pred = self.recognize(image, engine)
        ca = _char_accuracy(pred, ground_truth)
        wa = _word_accuracy(pred, ground_truth)
        return OCRResult(engine=engine, text=pred, char_accuracy=ca, word_accuracy=wa)

    def evaluate_protection(
        self,
        original: np.ndarray,
        subframes: list[np.ndarray],
        ground_truth: str,
        engine: str = "tesseract",
    ) -> dict:
        """
        对比原始图像与子帧的 OCR 准确率，输出保护效果报告。

        Returns:
            dict 包含：
              - original_char_acc: 原始帧字符准确率
              - subframe_char_accs: 各子帧字符准确率列表
              - mean_subframe_acc: 子帧平均准确率
              - accuracy_reduction: 准确率降幅（越大越好）
        """
        orig_result = self.evaluate_single(original, ground_truth, engine)
        sf_results = [self.evaluate_single(sf, ground_truth, engine) for sf in subframes]

        mean_sf_acc = float(np.mean([r.char_accuracy for r in sf_results]))
        reduction = orig_result.char_accuracy - mean_sf_acc

        return {
            "engine": engine,
            "original_char_acc": orig_result.char_accuracy,
            "original_text": orig_result.text,
            "subframe_char_accs": [r.char_accuracy for r in sf_results],
            "subframe_texts": [r.text for r in sf_results],
            "mean_subframe_acc": mean_sf_acc,
            "accuracy_reduction": reduction,
            "reduction_percent": reduction * 100,
            "protection_effective": mean_sf_acc < 0.20,  # 目标 <20%
        }

    def evaluate_temporal_averaging(
        self,
        subframes: list[np.ndarray],
        ground_truth: str,
        engine: str = "tesseract",
        max_stack: int = 16,
    ) -> list[dict]:
        """
        模拟攻击者叠加 k 帧后的 OCR 准确率（抗多帧叠加验证）。

        Returns:
            list of dict，每项包含 stack_count 和对应的准确率
        """
        results = []
        n = len(subframes)

        for k in [1, 2, 4, 8, 16]:
            if k > len(subframes):
                # 循环复用子帧
                frames_to_stack = [subframes[i % n] for i in range(k)]
            else:
                frames_to_stack = subframes[:k]

            # 时域平均
            stacked = np.mean(
                [sf.astype(np.float32) for sf in frames_to_stack], axis=0
            ).clip(0, 255).astype(np.uint8)

            result = self.evaluate_single(stacked, ground_truth, engine)
            results.append({
                "stack_count": k,
                "char_accuracy": result.char_accuracy,
                "text_preview": result.text[:50],
            })

        return results
