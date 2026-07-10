from pathlib import Path

from experiments.audit_real_capture_design import build_design_audit


def test_design_audit_distinguishes_recorded_derived_and_unknown_fields():
    root = Path(__file__).resolve().parents[1]

    audit = build_design_audit(root)

    assert audit["acquisition_order"]["randomized"] is False
    assert audit["acquisition_order"]["component_profile_order"] == [
        "original",
        "mask_only",
        "mask_noise",
        "anti_ocr",
        "deployed",
        "capture_hardened",
    ]
    assert audit["geometry"]["primary_position_count"] == 8
    assert audit["geometry"]["excluded_position"] == "d0.5_a15"
    assert audit["camera_controls"]["short_exposure_seconds"]["status"] == "derived"
    assert audit["camera_controls"]["short_exposure_seconds"]["value"] == 0.00390625
    assert audit["camera_controls"]["auto_exposure_state"]["status"] == "unknown"
    assert "display_luminance" in audit["camera_controls"]["unknown_fields"]


def test_design_audit_detects_non_ascii_corpus_and_duplicate_capture_round():
    root = Path(__file__).resolve().parents[1]

    audit = build_design_audit(root)

    assert audit["corpus"]["content_item_count"] == 12
    assert "cet6_p1" in audit["corpus"]["items_with_non_ascii_truth"]
    assert audit["corpus"]["all_english_ascii"] is False
    assert audit["duplicates"]["deployed_short_capture_count_primary"] == 408
    assert audit["duplicates"]["deployed_short_matched_cell_count_primary"] == 288
