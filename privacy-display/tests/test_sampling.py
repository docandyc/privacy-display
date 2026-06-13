import pytest

from src.evaluation.sampling import select_publication_subset, select_stratified_samples, take_indices


def test_select_publication_subset_distributes_max_samples_across_categories():
    names = ["a0", "a1", "a2", "b0", "b1", "c0"]
    metadata = {
        "a0": {"category": "alpha"},
        "a1": {"category": "alpha"},
        "a2": {"category": "alpha"},
        "b0": {"category": "beta"},
        "b1": {"category": "beta"},
        "c0": {"category": "gamma"},
    }

    selected, policy = select_publication_subset(names, metadata, max_samples=4)

    assert selected == [0, 1, 3, 4]
    assert policy["strategy"] == "stratified_max_samples"
    assert take_indices(names, selected) == ["a0", "a1", "b0", "b1"]


def test_select_stratified_samples_rejects_invalid_counts():
    with pytest.raises(ValueError):
        select_stratified_samples(["a"], {}, samples_per_category=0)
    with pytest.raises(ValueError):
        select_publication_subset(["a"], {}, max_samples=0)
