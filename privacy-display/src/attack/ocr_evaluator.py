"""
OCR 准确率评估器

测量原始帧与子帧的 OCR 识别准确率，量化隐私保护效果。
支持 Tesseract、EasyOCR、Surya 等 OCR 引擎。
"""

import os
from pathlib import Path
import shutil

import numpy as np
import re
from dataclasses import dataclass


def _configure_surya_runtime() -> None:
    """Use a project-local model cache and stable Windows download concurrency."""
    project_root = Path(__file__).resolve().parents[2]
    cache_dir = project_root / ".cache" / "surya"
    os.environ.setdefault("MODEL_CACHE_DIR", str(cache_dir))
    if os.name == "nt":
        os.environ.setdefault("PARALLEL_DOWNLOAD_WORKERS", "1")
    Path(os.environ["MODEL_CACHE_DIR"]).mkdir(parents=True, exist_ok=True)


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


def _normalize_for_match(text: str) -> str:
    """Normalize OCR text for exact-match style recovery checks."""
    return re.sub(r"\s+", "", text).casefold()


def _sensitive_tokens(text: str) -> list[str]:
    """
    Extract credential-like or structured tokens for sensitive-field recovery.

    Natural-language words are intentionally excluded; this metric focuses on
    fields an attacker would care about recovering exactly, such as numbers,
    email/URL/path fragments, keys, and account identifiers.
    """
    tokens = re.findall(r"[A-Za-z0-9_@:/.$¥?&=%+\-]+", text)
    out: list[str] = []
    for token in tokens:
        stripped = token.strip(".,;:()[]{}<>\"'")
        if len(stripped) < 2:
            continue
        has_digit = any(ch.isdigit() for ch in stripped)
        has_special = any(ch in stripped for ch in "@:/.$¥?&=%+_-")
        has_mixed_case = any(ch.islower() for ch in stripped) and any(ch.isupper() for ch in stripped)
        is_long_id = len(stripped) >= 8 and any(ch.isalpha() for ch in stripped)
        if has_digit or has_special or has_mixed_case or is_long_id:
            norm = _normalize_for_match(stripped)
            if norm and norm not in out:
                out.append(norm)
    return out


def _sensitive_token_recall(pred: str, ref: str) -> tuple[float, int]:
    tokens = _sensitive_tokens(ref)
    if not tokens:
        return 0.0, 0
    pred_norm = _normalize_for_match(pred)
    recovered = sum(1 for token in tokens if token in pred_norm)
    return recovered / len(tokens), len(tokens)


def text_recovery_metrics(pred: str, ref: str) -> dict:
    """Return OCR recovery metrics for an already recognized text string."""
    sensitive_recall, sensitive_count = _sensitive_token_recall(pred, ref)
    return {
        "char_accuracy": _char_accuracy(pred, ref),
        "word_accuracy": _word_accuracy(pred, ref),
        "exact_match": _normalize_for_match(pred) == _normalize_for_match(ref),
        "sensitive_token_recall": sensitive_recall,
        "sensitive_token_count": sensitive_count,
    }


class OCREvaluator:
    SUPPORTED_ENGINES = ("tesseract", "easyocr", "surya", "trocr", "doctr")
    TROCR_MODEL_ID = "microsoft/trocr-base-printed"
    TESSERACT_ENV_VARS = ("TESSERACT_CMD", "TESSERACT_EXE")

    def __init__(self, engines: list[str] | None = None, timeout: float | None = 10.0):
        """
        Args:
            engines: 使用的 OCR 引擎列表，可选 'tesseract', 'easyocr', 'surya'
                     None 时自动检测可用引擎
            timeout: 单次 OCR 调用超时时间（秒）；None 表示不设置超时
        """
        self.engines = self._detect_available_engines() if engines is None else engines
        self.timeout = timeout
        self._easyocr_reader = None
        self._surya_readers = None
        self._trocr = None        # (processor, model) tuple, lazily loaded
        self._doctr_predictor = None

    @classmethod
    def supported_engines(cls) -> tuple[str, ...]:
        return cls.SUPPORTED_ENGINES

    @staticmethod
    def _env_truthy(name: str) -> bool:
        return os.environ.get(name, "").strip().casefold() in {"1", "true", "yes", "on"}

    @classmethod
    def _candidate_tesseract_commands(cls) -> list[str]:
        candidates: list[str] = []
        for env_name in cls.TESSERACT_ENV_VARS:
            value = os.environ.get(env_name, "").strip()
            if value:
                candidates.append(value)
        path_cmd = shutil.which("tesseract")
        if path_cmd:
            candidates.append(path_cmd)
        if os.name == "nt":
            for base in (
                os.environ.get("ProgramFiles"),
                os.environ.get("ProgramFiles(x86)"),
                r"C:\Program Files",
                r"C:\Program Files (x86)",
            ):
                if base:
                    candidates.append(str(Path(base) / "Tesseract-OCR" / "tesseract.exe"))

        seen: set[str] = set()
        unique: list[str] = []
        for candidate in candidates:
            key = candidate.casefold()
            if key not in seen:
                seen.add(key)
                unique.append(candidate)
        return unique or ["tesseract"]

    @classmethod
    def _configure_tesseract(cls, pytesseract_module) -> bool:
        for cmd in cls._candidate_tesseract_commands():
            if cmd == "tesseract" or Path(cmd).exists():
                pytesseract_module.pytesseract.tesseract_cmd = cmd
                return True
        return False

    @classmethod
    def _trocr_cache_available(cls) -> bool:
        try:
            from transformers.utils import cached_file

            cached_file(cls.TROCR_MODEL_ID, "config.json", local_files_only=True)
            cached_file(cls.TROCR_MODEL_ID, "preprocessor_config.json", local_files_only=True)
            cached_file(cls.TROCR_MODEL_ID, "generation_config.json", local_files_only=True)
            return True
        except Exception:
            return False

    def _detect_available_engines(self) -> list[str]:
        available = []
        try:
            import pytesseract
            if not self._configure_tesseract(pytesseract):
                raise RuntimeError("tesseract executable not found")
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
            import surya  # noqa: F401
            available.append("surya")
        except Exception:
            pass
        # Heavy modern OCR engines often download pretrained weights. Auto-list
        # only local/offline-safe engines; explicit experiments can still request
        # trocr/doctr and record per-row setup errors instead of citing them.
        if self._trocr_cache_available():
            available.append("trocr")
        if self._env_truthy("PRIVACY_DISPLAY_ENABLE_DOCTR_AUTO"):
            try:
                import doctr  # noqa: F401
                available.append("doctr")
            except Exception:
                pass
        return available

    def _run_tesseract(self, image: np.ndarray) -> str:
        import pytesseract
        from PIL import Image
        if not self._configure_tesseract(pytesseract):
            raise RuntimeError("tesseract executable not found")
        pil_img = Image.fromarray(image)
        kwargs = {"lang": "chi_sim+eng"}
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout
        return pytesseract.image_to_string(pil_img, **kwargs).strip()

    def _run_easyocr(self, image: np.ndarray) -> str:
        import easyocr
        if self._easyocr_reader is None:
            self._easyocr_reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
        results = self._easyocr_reader.readtext(image, detail=0)
        return " ".join(results)

    @staticmethod
    def _resolve_surya_device() -> str:
        configured = os.environ.get("SURYA_DEVICE", "auto").strip().casefold()
        if configured and configured != "auto":
            return configured

        import torch

        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _run_surya(self, image: np.ndarray) -> str:
        from PIL import Image

        if self._surya_readers is None:
            _configure_surya_runtime()
            from surya.detection import DetectionPredictor
            from surya.recognition import RecognitionPredictor

            device = self._resolve_surya_device()
            self._surya_readers = (
                RecognitionPredictor(device=device),
                DetectionPredictor(device=device),
            )

        recognition_predictor, detection_predictor = self._surya_readers
        pil_image = Image.fromarray(image).convert("RGB")
        result = recognition_predictor(
            [pil_image],
            det_predictor=detection_predictor,
            sort_lines=True,
            math_mode=False,
        )
        return self._parse_surya_text(result)

    @staticmethod
    def _parse_surya_text(result) -> str:
        """Extract text lines from Surya 0.14.x OCRResult objects or dictionaries."""
        pages = result if isinstance(result, (list, tuple)) else [result]
        texts: list[str] = []
        for page in pages:
            if isinstance(page, dict):
                lines = page.get("text_lines", [])
            else:
                lines = getattr(page, "text_lines", [])
            for line in lines or []:
                if isinstance(line, dict):
                    text = line.get("text", "")
                else:
                    text = getattr(line, "text", "")
                text = str(text).strip()
                if text:
                    texts.append(text)
        return " ".join(texts)

    def _run_trocr(self, image: np.ndarray) -> str:
        """Transformer OCR (microsoft/trocr-base-printed). Printed-text English."""
        from PIL import Image
        if self._trocr is None:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            model_id = self.TROCR_MODEL_ID
            processor = TrOCRProcessor.from_pretrained(model_id, local_files_only=True)
            model = VisionEncoderDecoderModel.from_pretrained(model_id, local_files_only=True)
            model.eval()
            self._trocr = (processor, model)
        processor, model = self._trocr
        pil_img = Image.fromarray(image).convert("RGB")
        pixel_values = processor(images=pil_img, return_tensors="pt").pixel_values
        import torch
        with torch.no_grad():
            generated_ids = model.generate(pixel_values, max_new_tokens=64)
        return processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

    def _run_doctr(self, image: np.ndarray) -> str:
        """python-doctr detection+recognition pipeline."""
        if self._doctr_predictor is None:
            from doctr.models import ocr_predictor
            self._doctr_predictor = ocr_predictor(pretrained=True)
        result = self._doctr_predictor([np.ascontiguousarray(image)])
        words: list[str] = []
        for page in result.export().get("pages", []):
            for block in page.get("blocks", []):
                for line in block.get("lines", []):
                    for word in line.get("words", []):
                        if word.get("value"):
                            words.append(word["value"])
        return " ".join(words)

    def recognize(self, image: np.ndarray, engine: str = "tesseract") -> str:
        """对单张图像运行 OCR，返回识别文本。"""
        image = np.ascontiguousarray(image)
        if engine == "tesseract":
            return self._run_tesseract(image)
        elif engine == "easyocr":
            return self._run_easyocr(image)
        elif engine == "surya":
            return self._run_surya(image)
        elif engine == "trocr":
            return self._run_trocr(image)
        elif engine == "doctr":
            return self._run_doctr(image)
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
        mean_sf_word_acc = float(np.mean([r.word_accuracy for r in sf_results]))
        reduction = orig_result.char_accuracy - mean_sf_acc
        orig_recovery = text_recovery_metrics(orig_result.text, ground_truth)
        subframe_recovery = [
            text_recovery_metrics(r.text, ground_truth) for r in sf_results
        ]

        return {
            "engine": engine,
            "original_char_acc": orig_result.char_accuracy,
            "original_word_acc": orig_result.word_accuracy,
            "original_exact_match": orig_recovery["exact_match"],
            "original_sensitive_token_recall": orig_recovery["sensitive_token_recall"],
            "original_text": orig_result.text,
            "subframe_char_accs": [r.char_accuracy for r in sf_results],
            "subframe_word_accs": [r.word_accuracy for r in sf_results],
            "subframe_exact_matches": [
                recovery["exact_match"] for recovery in subframe_recovery
            ],
            "subframe_sensitive_token_recalls": [
                recovery["sensitive_token_recall"] for recovery in subframe_recovery
            ],
            "subframe_texts": [r.text for r in sf_results],
            "mean_subframe_acc": mean_sf_acc,
            "mean_subframe_word_acc": mean_sf_word_acc,
            "mean_subframe_exact_match": float(
                np.mean([recovery["exact_match"] for recovery in subframe_recovery])
            ),
            "mean_subframe_sensitive_token_recall": float(np.mean([
                recovery["sensitive_token_recall"] for recovery in subframe_recovery
            ])),
            "sensitive_token_count": orig_recovery["sensitive_token_count"],
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
