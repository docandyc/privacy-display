from src.evaluation.real_capture import summarize_real_capture_rows, summarize_by


def _row(ablation, attack, exact, sensitive):
    return {
        "engine": "tesseract",
        "condition": f"{ablation}|{attack}",
        "device": "EMEET SmartCam S600",
        "ablation": ablation,
        "attack": attack,
        "char_accuracy": 0.25,
        "word_accuracy": 0.0,
        "exact_match": exact,
        "sensitive_token_recall": sensitive,
        "sensitive_token_count": 1,
    }


def test_summarize_by_groups_structured_fields():
    rows = [_row("deployed", "short", 0.0, 0.0), _row("original", "long", 1.0, 1.0)]

    summary = summarize_by(rows, ["ablation", "attack"])

    assert set(summary) == {"deployed|short", "original|long"}
    assert summary["deployed|short"]["exact_match"]["mean"] == 0.0
    assert summary["original|long"]["sensitive_token_recall"]["mean"] == 1.0


def test_real_capture_summary_includes_ablation_attack_when_present():
    rows = [_row("deployed", "short", 0.0, 0.0), _row("deployed", "video", 0.0, 0.5)]

    summary = summarize_real_capture_rows(rows)

    assert "by_ablation_attack" in summary
    assert set(summary["by_ablation_attack"]) == {"deployed|short", "deployed|video"}
