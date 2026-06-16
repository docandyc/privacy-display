from src.evaluation.real_capture import (
    collapse_best_of_engines,
    protection_delta,
    summarize_real_capture_rows,
    summarize_by,
)


def _row(ablation, attack, exact, sensitive, *, engine="tesseract", char=0.25, rid=None):
    return {
        "id": rid or f"{ablation}_{attack}",
        "image": f"{ablation}_{attack}.jpg",
        "engine": engine,
        "condition": f"{ablation}|{attack}",
        "device": "EMEET SmartCam S600",
        "ablation": ablation,
        "attack": attack,
        "char_accuracy": char,
        "word_accuracy": 0.0,
        "exact_match": exact,
        "sensitive_token_recall": sensitive,
        "sensitive_token_count": 1,
    }


def test_collapse_best_of_engines_takes_attacker_favorable_max():
    rows = [
        _row("deployed", "short", 0.0, 0.0, engine="tesseract", char=0.05, rid="cap1"),
        _row("deployed", "short", 1.0, 0.8, engine="easyocr", char=0.90, rid="cap1"),
    ]
    collapsed = collapse_best_of_engines(rows)
    assert len(collapsed) == 1
    assert collapsed[0]["exact_match"] == 1.0
    assert collapsed[0]["char_accuracy"] == 0.90
    assert collapsed[0]["sensitive_token_recall"] == 0.8


def test_protection_delta_measures_drop_vs_original():
    rows = [
        _row("original", "short", 1.0, 1.0, char=0.9, rid="o1"),
        _row("deployed", "short", 0.0, 0.0, char=0.1, rid="d1"),
    ]
    delta = protection_delta(rows)
    assert delta["deployed|short"]["char_accuracy_drop"] == 0.8
    assert delta["deployed|short"]["exact_match_drop"] == 1.0
    assert delta["original|short"]["char_accuracy_drop"] == 0.0


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
