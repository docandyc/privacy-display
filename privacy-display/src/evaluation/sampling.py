"""Deterministic corpus sampling helpers for publication experiments."""

from __future__ import annotations

from collections.abc import Sequence
from math import ceil
from typing import TypeVar


T = TypeVar("T")


def select_stratified_samples(
    names: list[str],
    metadata: dict | None,
    samples_per_category: int = 1,
    max_samples: int | None = None,
    field: str = "category",
) -> list[int]:
    """Return deterministic sample indices, grouped by a metadata field."""
    if samples_per_category <= 0:
        raise ValueError("samples_per_category must be positive")
    if max_samples is not None and max_samples <= 0:
        raise ValueError("max_samples must be positive when provided")

    metadata = metadata or {}
    buckets: dict[str, list[int]] = {}
    for idx, name in enumerate(names):
        group = str(metadata.get(name, {}).get(field, "unknown"))
        buckets.setdefault(group, []).append(idx)

    selected: list[int] = []
    for group in sorted(buckets):
        selected.extend(buckets[group][:samples_per_category])

    if max_samples is not None:
        selected = selected[:max_samples]
    return selected


def select_publication_subset(
    names: list[str],
    metadata: dict | None,
    max_samples: int | None = None,
    samples_per_category: int | None = None,
    field: str = "category",
) -> tuple[list[int], dict]:
    """
    Select a publication-facing subset without prefix bias.

    If `samples_per_category` is provided, it is used directly. Otherwise
    `max_samples` is distributed across metadata buckets. With neither option,
    the full corpus order is preserved.
    """
    if max_samples is not None and max_samples <= 0:
        raise ValueError("max_samples must be positive when provided")
    if samples_per_category is not None and samples_per_category <= 0:
        raise ValueError("samples_per_category must be positive when provided")

    metadata = metadata or {}
    if samples_per_category is None and max_samples is None:
        indices = list(range(len(names)))
        return indices, {
            "strategy": "full_corpus",
            "field": field,
            "max_samples": None,
            "samples_per_category": None,
            "n_selected": len(indices),
        }

    if samples_per_category is None:
        groups = {
            str(metadata.get(name, {}).get(field, "unknown")) for name in names
        } or {"unknown"}
        samples_per_category = max(1, ceil(max_samples / len(groups)))  # type: ignore[arg-type]
        strategy = "stratified_max_samples"
    else:
        strategy = "stratified_samples_per_category"

    indices = select_stratified_samples(
        names,
        metadata,
        samples_per_category=samples_per_category,
        max_samples=max_samples,
        field=field,
    )
    return indices, {
        "strategy": strategy,
        "field": field,
        "max_samples": max_samples,
        "samples_per_category": samples_per_category,
        "n_selected": len(indices),
    }


def take_indices(values: Sequence[T], indices: list[int]) -> list[T]:
    """Return values at selected indices while preserving selected order."""
    return [values[idx] for idx in indices]
