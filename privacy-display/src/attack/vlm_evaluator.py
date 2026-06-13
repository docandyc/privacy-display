"""
Online VLM readability evaluator.

This module treats a vision-language model as a camera-side attacker: the
model only sees the captured image and is asked to transcribe visible text.
Ground truth stays local and is used only for recovery metrics.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Callable

import numpy as np

from src.attack.ocr_evaluator import text_recovery_metrics


DEFAULT_SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_VLM_MODEL = "Qwen/Qwen3-VL-32B-Instruct"
API_KEY_ENV = "SILICONFLOW_API_KEY"

Transport = Callable[[str, dict, dict, float], dict]


def _as_uint8_rgb(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image)
    if arr.ndim == 2:
        arr = np.repeat(arr[..., None], 3, axis=2)
    if arr.ndim != 3 or arr.shape[-1] not in {3, 4}:
        raise ValueError("image must be HxW, HxWx3, or HxWx4")
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    if arr.shape[-1] == 4:
        arr = arr[..., :3]
    return np.ascontiguousarray(arr)


def image_to_data_url(image: np.ndarray) -> str:
    """Encode a numpy image as a PNG data URL for OpenAI-compatible VLM APIs."""
    from PIL import Image

    arr = _as_uint8_rgb(image)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def extract_json_object(text: str) -> dict:
    """Extract a JSON object from direct, fenced, or lightly wrapped responses."""
    if not isinstance(text, str):
        raise ValueError("VLM response content must be a string")
    stripped = text.strip()
    if not stripped:
        raise ValueError("VLM response content is empty")

    try:
        value = json.loads(stripped)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL | re.IGNORECASE)
    if fence:
        value = json.loads(fence.group(1))
        if isinstance(value, dict):
            return value

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        value = json.loads(stripped[start:end + 1])
        if isinstance(value, dict):
            return value

    raise ValueError("VLM response does not contain a JSON object")


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().casefold() in {"true", "yes", "1", "readable", "visible"}
    return False


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class VLMClient:
    """Minimal OpenAI-compatible VLM client for SiliconFlow chat completions."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_SILICONFLOW_BASE_URL,
        model: str = DEFAULT_VLM_MODEL,
        timeout: float = 60.0,
        transport: Transport | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = float(timeout)
        self.transport = transport or self._urllib_transport

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}/chat/completions"

    def _api_key(self) -> str:
        key = self.api_key or os.environ.get(API_KEY_ENV)
        if not key:
            raise ValueError(f"{API_KEY_ENV} is required for online VLM evaluation")
        return key

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key()}",
            "Content-Type": "application/json",
        }

    def analyze_image(
        self,
        image: np.ndarray,
        ground_truth: str = "",
        prompt: str | None = None,
        max_tokens: int = 256,
    ) -> dict:
        """
        Ask the VLM to transcribe visible text and score recovery locally.

        `ground_truth` is deliberately excluded from the prompt to avoid
        answer leakage. It is used only after the response is parsed.
        """
        user_prompt = prompt or (
            "Transcribe only the text that is visibly readable in this image. "
            "Do not guess hidden or missing characters. Return JSON only with "
            "fields: visible_text, can_read_sensitive, confidence, notes."
        )
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a privacy attack evaluator. Report only what is "
                        "visible in the provided image and return a single JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_to_data_url(image)},
                        },
                    ],
                },
            ],
            "temperature": 0,
            "max_tokens": int(max_tokens),
            "response_format": {"type": "json_object"},
        }
        response = self.transport(self.endpoint, payload, self._headers(), self.timeout)
        content = self._message_content(response)
        parsed = extract_json_object(content)
        visible_text = str(parsed.get("visible_text", "") or "").strip()
        metrics = text_recovery_metrics(visible_text, ground_truth)
        return {
            "model": self.model,
            "base_url": self.base_url,
            "raw_text": content,
            "visible_text": visible_text,
            "can_read_sensitive": _coerce_bool(parsed.get("can_read_sensitive", False)),
            "confidence": _coerce_float(parsed.get("confidence", 0.0)),
            "notes": str(parsed.get("notes", "") or ""),
            "metrics": metrics,
            "usage": response.get("usage", {}),
        }

    @staticmethod
    def _message_content(response: dict) -> str:
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("VLM response is missing choices[0].message.content") from exc
        if isinstance(content, list):
            texts = [
                part.get("text", "") for part in content
                if isinstance(part, dict) and part.get("type") in {None, "text"}
            ]
            return "\n".join(texts)
        return str(content)

    def _urllib_transport(
        self,
        url: str,
        payload: dict,
        headers: dict,
        timeout: float,
    ) -> dict:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        key = self.api_key or os.environ.get(API_KEY_ENV) or ""
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            err_body = exc.read(4096).decode("utf-8", errors="replace")
            raise RuntimeError(
                f"VLM API request failed with status {exc.code}: "
                f"{self._sanitize_error_text(err_body, key)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"VLM API request failed: {self._sanitize_error_text(str(exc), key)}"
            ) from exc

        try:
            return json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError("VLM API returned non-JSON response") from exc

    @staticmethod
    def _sanitize_error_text(text: str, api_key: str = "") -> str:
        out = text.replace("\n", " ").strip()
        if api_key:
            out = out.replace(api_key, "[REDACTED]")
        return out[:500]
