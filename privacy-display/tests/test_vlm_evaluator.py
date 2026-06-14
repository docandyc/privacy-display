import json

import numpy as np
import pytest

from src.attack.vlm_evaluator import VLMClient, extract_json_object, image_to_data_url


def test_image_to_data_url_is_png_data_url():
    image = np.zeros((4, 5, 3), dtype=np.uint8)

    data_url = image_to_data_url(image)

    assert data_url.startswith("data:image/png;base64,")


def test_extract_json_object_handles_fenced_json():
    parsed = extract_json_object(
        "```json\n"
        "{\"visible_text\":\"CODE-1234\",\"can_read_sensitive\":true}\n"
        "```"
    )

    assert parsed["visible_text"] == "CODE-1234"
    assert parsed["can_read_sensitive"] is True


def test_vlm_client_sends_openai_compatible_image_payload_without_ground_truth():
    captured = {}

    def fake_transport(url, payload, headers, timeout):
        captured["url"] = url
        captured["payload"] = payload
        captured["headers"] = headers
        captured["timeout"] = timeout
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "visible_text": "CODE-1234",
                            "can_read_sensitive": True,
                            "confidence": 0.91,
                            "notes": "readable",
                        })
                    }
                }
            ],
            "usage": {"total_tokens": 12},
        }

    client = VLMClient(api_key="test-key", transport=fake_transport)
    result = client.analyze_image(
        np.full((8, 8, 3), 255, dtype=np.uint8),
        ground_truth="CODE-1234",
    )

    assert captured["url"] == "https://api.siliconflow.cn/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["payload"]["model"] == "Qwen/Qwen3-VL-32B-Instruct"
    assert captured["payload"]["response_format"] == {"type": "json_object"}

    user_content = captured["payload"]["messages"][1]["content"]
    assert user_content[0]["type"] == "text"
    assert user_content[1]["type"] == "image_url"
    assert user_content[1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert "CODE-1234" not in json.dumps(captured["payload"], ensure_ascii=False)

    assert result["visible_text"] == "CODE-1234"
    assert result["can_read_sensitive"] is True
    assert result["confidence"] == 0.91
    assert result["metrics"]["exact_match"] is True
    assert result["metrics"]["sensitive_token_recall"] == 1.0
    assert result["usage"]["total_tokens"] == 12


def test_vlm_client_falls_back_when_model_rejects_json_mode():
    """GLM-4.5V style models reject response_format; client must retry plainly."""
    calls = []

    def fake_transport(url, payload, headers, timeout):
        calls.append("json" if "response_format" in payload else "plain")
        if "response_format" in payload:
            raise RuntimeError(
                "VLM API request failed with status 400: "
                '{"code":20024,"message":"Json mode is not supported for this model."}'
            )
        return {
            "choices": [
                {"message": {"content": '<|begin_of_box|>{"visible_text": "HELLO"}<|end_of_box|>'}}
            ],
            "usage": {},
        }

    client = VLMClient(api_key="test-key", transport=fake_transport)
    first = client.analyze_image(np.full((8, 8, 3), 255, dtype=np.uint8), ground_truth="HELLO")
    second = client.analyze_image(np.full((8, 8, 3), 255, dtype=np.uint8), ground_truth="HELLO")

    # First call attempts JSON mode, gets rejected, retries plainly and succeeds.
    assert calls == ["json", "plain", "plain"]
    # The decision is cached: the second call skips the doomed JSON attempt.
    assert client._send_json_mode is False
    assert first["visible_text"] == "HELLO"
    assert second["visible_text"] == "HELLO"


def test_vlm_client_forced_json_mode_off_never_sends_response_format():
    captured = {}

    def fake_transport(url, payload, headers, timeout):
        captured["payload"] = payload
        return {"choices": [{"message": {"content": '{"visible_text": "X"}'}}], "usage": {}}

    client = VLMClient(api_key="test-key", transport=fake_transport, json_mode=False)
    client.analyze_image(np.zeros((4, 4, 3), dtype=np.uint8))

    assert "response_format" not in captured["payload"]


def test_vlm_client_requires_env_api_key_without_leaking_secret(monkeypatch):
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    client = VLMClient(transport=lambda *_args: {})

    with pytest.raises(ValueError) as exc:
        client.analyze_image(np.zeros((2, 2, 3), dtype=np.uint8))

    assert "SILICONFLOW_API_KEY" in str(exc.value)
    assert "sk-" not in str(exc.value)
