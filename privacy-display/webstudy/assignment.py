"""Shared counterbalance assignment helpers for the WebStudy."""

from __future__ import annotations


RATING_CONDITION_ORDER = (
    "control_anchor",
    "n2_mask_noise",
    "n3_mask_noise",
    "n4_mask_noise",
    "n4_mask_only",
    "deployed_full",
)
ASSIGNMENT_BUCKET_COUNT = 2 * len(RATING_CONDITION_ORDER)


def assignment_for_registration_index(registration_index: int) -> dict[str, int]:
    index = int(registration_index)
    if index < 0 or index != registration_index:
        raise ValueError("registration_index must be a non-negative integer")
    return {
        "registration_index": index,
        "typing_order_index": index % 2,
        "rating_order_index": (index // 2) % len(RATING_CONDITION_ORDER),
    }


def assignment_bucket_key(assignment: dict[str, int]) -> str:
    return f"{assignment['typing_order_index']}:{assignment['rating_order_index']}"


def assignment_bucket_keys() -> list[str]:
    return [
        assignment_bucket_key(assignment_for_registration_index(index))
        for index in range(ASSIGNMENT_BUCKET_COUNT)
    ]
