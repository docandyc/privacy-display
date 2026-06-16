import numpy as np

from experiments.real_capture_calibrate import (
    build_exposure_calibration,
    build_roi_calibration,
    load_roi_calibration,
    parse_exposure_values,
    rectify_frame,
    save_roi_calibration,
    select_exposure_from_scan,
)


def _scan(pairs):
    return [{"value": v, "ssim": s} for v, s in pairs]


def test_select_exposure_picks_floor_and_plateau():
    # Shorter (more negative) exposure -> masked (low SSIM); longer -> integrated.
    scan = _scan([
        (-11, 0.05), (-10, 0.06), (-9, 0.08), (-8, 0.12),
        (-7, 0.45), (-6, 0.90), (-5, 0.95), (-4, 0.96),
    ])
    short_value, long_value, method = select_exposure_from_scan(scan)
    assert method == "ssim_floor_plateau"
    # short = largest still-masked exposure; long = smallest fully-integrated one.
    assert short_value == -8
    assert long_value == -6


def test_select_exposure_flags_low_contrast_scene():
    # All-low SSIM (camera never integrates / wrong scene) must not be reported
    # as a real floor->plateau; falls back to the scan extremes.
    scan = _scan([(-11, 0.05), (-10, 0.06), (-9, 0.07)])
    short_value, long_value, method = select_exposure_from_scan(scan)
    assert method == "ssim_low_contrast_fallback"
    assert short_value == -11 and long_value == -9


def test_select_exposure_needs_two_points():
    assert select_exposure_from_scan(_scan([(-8, 0.1)]))[2] == "insufficient_ssim"


def test_build_exposure_calibration_records_selection_method():
    payload = build_exposure_calibration(
        short_value=-8, long_value=-5, backend="dshow", selection_method="ssim_floor_plateau"
    )
    assert payload["selection_method"] == "ssim_floor_plateau"
    assert payload["short"]["exposure_s"] == 2 ** -8


def test_parse_exposure_values():
    assert parse_exposure_values("-3, -8 , -11") == [-3.0, -8.0, -11.0]


def test_roi_calibration_roundtrip_rectifies_to_axis_aligned(tmp_path):
    # A skewed quad maps to a full output rectangle; the rectified frame size
    # must match the requested output size.
    points = [(10, 12), (110, 8), (118, 92), (6, 96)]
    payload = build_roi_calibration(
        points, output_width=64, output_height=48, pos="d0.5_a0", image_shape=(120, 160, 3)
    )
    out = save_roi_calibration(payload, tmp_path)
    loaded = load_roi_calibration(out)
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    rect = rectify_frame(frame, loaded)
    assert rect.shape == (48, 64, 3)
