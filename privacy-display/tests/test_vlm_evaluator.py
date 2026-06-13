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


def test_vlm_client_requires_env_api_key_without_leaking_secret(monkeypatch):
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    client = VLMClient(transport=lambda *_args: {})

    with pytest.raises(ValueError) as exc:
        client.analyze_image(np.zeros((2, 2, 3), dtype=np.uint8))

    assert "SILICONFLOW_API_KEY" in str(exc.value)
    assert "sk-" not in str(exc.value)
