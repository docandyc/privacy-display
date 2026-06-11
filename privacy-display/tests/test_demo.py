import numpy as np

from src.demo.visual_integration import analyze_single_frame_readability
from src.demo.privacy_window import (
    WindowConfig,
    ensure_safe_refresh_rate,
    minimum_refresh_rate,
    resolve_runtime_display_config,
    select_output_frame,
)


def test_active_ratio_ignores_noise_pedestal():
    original = np.full((8, 8, 3), 100, dtype=np.uint8)
    masks = []
    for idx in range(4):
        mask = np.zeros((8, 8), dtype=bool)
        mask[:, idx::4] = True
        masks.append(mask)

    subframes = [
        (original.astype(np.float32) * mask[:, :, None] + 8.0).astype(np.uint8)
        for mask in masks
    ]

    result = analyze_single_frame_readability(original, subframes)

    assert abs(result["mean_active_ratio"] - 0.25) < 0.01


def test_window_config_enforces_refresh_rate_constraint():
    cfg = WindowConfig(n=2, refresh_rate=60)

    assert minimum_refresh_rate(2) == 120
    assert cfg.refresh_rate == 120
    assert ensure_safe_refresh_rate(4, cfg.refresh_rate) == 240


def test_runtime_display_config_uses_detected_refresh_rate():
    cfg = resolve_runtime_display_config(n=4, requested_refresh_rate=120, detected_refresh_rate=240)

    assert cfg.n == 4
    assert cfg.refresh_rate == 240
    assert cfg.safe


def test_runtime_display_config_lowers_n_when_hardware_is_limited():
    cfg = resolve_runtime_display_config(n=4, requested_refresh_rate=240, detected_refresh_rate=144)

    assert cfg.n == 2
    assert cfg.refresh_rate == 144
    assert cfg.safe


def test_runtime_display_config_marks_unsafe_below_minimum_refresh():
    cfg = resolve_runtime_display_config(n=2, requested_refresh_rate=120, detected_refresh_rate=60)

    assert cfg.n == 2
    assert cfg.refresh_rate == 60
    assert not cfg.safe


def test_select_output_frame_outputs_black_and_inversion_frames():
    subframes = [
        np.full((2, 2, 3), 10, dtype=np.uint8),
        np.full((2, 2, 3), 20, dtype=np.uint8),
    ]
    inversion = np.full((2, 2, 3), 245, dtype=np.uint8)
    black = np.zeros((2, 2, 3), dtype=np.uint8)

    frame, kind = select_output_frame(subframes, inversion, black, 0, 2, True, False)
    assert kind == "subframe"
    assert np.array_equal(frame, subframes[0])

    frame, kind = select_output_frame(subframes, inversion, black, 2, 2, True, False)
    assert kind == "inversion"
    assert np.array_equal(frame, inversion)

    frame, kind = select_output_frame(subframes, inversion, black, 0, 2, True, True)
    assert kind == "black"
    assert np.array_equal(frame, black)
