import json

from src.evaluation.real_capture_merge import (
    aggregate_position_reports,
    replace_engine_rows,
)


def _row(capture_id: str, engine: str, *, error: str = "") -> dict:
    return {
        "id": capture_id,
        "image": f"{capture_id}.png",
        "condition": "original",
        "ablation": "original",
        "attack": "short",
        "profile": "",
        "engine": engine,
        "char_accuracy": 1.0,
        "word_accuracy": 1.0,
        "exact_match": True,
        "sensitive_token_recall": 1.0,
        "sensitive_token_count": 1,
        "ocr_error": error,
    }


def test_replace_engine_rows_removes_paddle_and_preserves_other_engines():
    existing = {
        "config": {
            "engines": ["tesseract", "easyocr", "paddleocr"],
            "n_captures": 2,
            "n_rows": 6,
            "paddleocr_rerun": True,
        },
        "captures": [
            _row("a", "tesseract"),
            _row("a", "easyocr"),
            _row("a", "paddleocr"),
            _row("b", "tesseract"),
            _row("b", "easyocr"),
            _row("b", "paddleocr"),
        ],
    }
    replacement = {
        "captures": [_row("a", "surya"), _row("b", "surya")],
    }

    updated, stats = replace_engine_rows(
        existing,
        replacement,
        engine="surya",
        remove_engines=("paddleocr", "surya"),
    )

    assert updated["config"]["engines"] == ["tesseract", "easyocr", "surya"]
    assert updated["config"]["n_rows"] == 6
    assert "paddleocr_rerun" not in updated["config"]
    assert [row["engine"] for row in updated["captures"]] == [
        "tesseract",
        "easyocr",
        "surya",
        "tesseract",
        "easyocr",
        "surya",
    ]
    assert stats["removed_legacy_rows"] == 2


def test_aggregate_position_reports_waits_for_all_surya_rows(tmp_path):
    ready = tmp_path / "results_d0.5_a0_final" / "real_capture_ocr.json"
    pending = tmp_path / "results_d0.5_a15_final" / "real_capture_ocr.json"
    ready.parent.mkdir()
    pending.parent.mkdir()
    ready.write_text(
        json.dumps({
            "config": {"n_captures": 1},
            "captures": [
                _row("a", "tesseract"),
                _row("a", "easyocr"),
                _row("a", "surya"),
            ],
        }),
        encoding="utf-8",
    )
    pending.write_text(
        json.dumps({
            "config": {"n_captures": 1},
            "captures": [
                _row("b", "tesseract"),
                _row("b", "easyocr"),
                _row("b", "paddleocr"),
            ],
        }),
        encoding="utf-8",
    )

    report, pending_names = aggregate_position_reports([ready, pending])

    assert report is None
    assert pending_names == ["results_d0.5_a15_final"]
