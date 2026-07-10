import pytest

from experiments.analyze_vlm_missing_response_bounds import bound_condition_rows


def test_missing_response_bounds_include_worst_and_best_case_failures():
    rows = [
        {"vlm_error": "", "exact_match": True, "char_accuracy": 0.8},
        {"vlm_error": "", "exact_match": False, "char_accuracy": 0.2},
        {"vlm_error": "timeout", "exact_match": False, "char_accuracy": 0.0},
    ]

    bounded = bound_condition_rows(rows)

    assert bounded["planned_calls"] == 3
    assert bounded["successful_calls"] == 2
    assert bounded["error_calls"] == 1
    assert bounded["exact_match_bounds"] == pytest.approx([1 / 3, 2 / 3])
    assert bounded["char_accuracy_bounds"] == pytest.approx([1 / 3, 2 / 3])


def test_complete_cell_has_point_bounds():
    rows = [{"vlm_error": "", "exact_match": True, "char_accuracy": 0.75}]

    bounded = bound_condition_rows(rows)

    assert bounded["exact_match_bounds"] == [1.0, 1.0]
    assert bounded["char_accuracy_bounds"] == [0.75, 0.75]
