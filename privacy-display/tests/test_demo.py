import numpy as np

from src.demo.visual_integration import analyze_single_frame_readability
from src.demo.privacy_window import (
    WindowConfig,
    create_display_surface,
    ensure_safe_refresh_rate,
    minimum_refresh_rate,
    output_slot_duration,
    resolve_runtime_display_config,
    runtime_renderer_gamma,
    run_online_noise_monitor,
    select_output_frame,
    sub_noises_to_pixel_space,
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


def test_window_config_validates_inversion_alpha():
    cfg = WindowConfig(n=2, refresh_rate=120, inversion_alpha=0.3)

    assert cfg.inversion_alpha == 0.3
    assert output_slot_duration(1 / 120, "inversion", cfg.inversion_alpha) == (1 / 120) * 0.3
    assert output_slot_duration(1 / 120, "subframe", cfg.inversion_alpha) == 1 / 120


def test_runtime_renderer_gamma_defaults_to_backlight_model():
    cfg = WindowConfig(n=4, refresh_rate=240, gamma_factor=1.2)

    assert cfg.brightness_model == "backlight"
    assert runtime_renderer_gamma(cfg.n, cfg.gamma_factor, cfg.brightness_model) == 1.0
    assert runtime_renderer_gamma(4, 1.2, "pixel") == 4.8


def test_window_config_rejects_invalid_brightness_model():
    try:
        WindowConfig(n=2, refresh_rate=120, brightness_model="invalid")
    except ValueError as exc:
        assert "brightness_model" in str(exc)
    else:
        raise AssertionError("invalid brightness_model should be rejected")


def test_window_config_rejects_invalid_inversion_alpha():
    try:
        WindowConfig(n=2, refresh_rate=120, inversion_alpha=1.1)
    except ValueError as exc:
        assert "inversion_alpha" in str(exc)
    else:
        raise AssertionError("invalid inversion_alpha should be rejected")


def test_create_display_surface_passes_fullscreen_flag_with_vsync():
    class FakeDisplay:
        def __init__(self):
            self.calls = []

        def set_mode(self, size, flags=0, vsync=0):
            self.calls.append((size, flags, vsync))
            return "surface"

    class FakePygame:
        FULLSCREEN = 0x80000000
        display = FakeDisplay()

    surface, vsync = create_display_surface(
        FakePygame,
        (2560, 1600),
        prefer_vsync=True,
        fullscreen=True,
    )

    assert surface == "surface"
    assert vsync is True
    assert FakePygame.display.calls == [((2560, 1600), FakePygame.FULLSCREEN, 1)]


def test_sub_noises_to_pixel_space_adds_pedestal():
    sub_noises_f = [
        np.full((2, 2, 3), -8 / 255, dtype=np.float32),
        np.full((2, 2, 3), 8 / 255, dtype=np.float32),
    ]

    sub_noises, pedestal = sub_noises_to_pixel_space(sub_noises_f, epsilon=8 / 255)

    assert pedestal == 8
    assert np.allclose(sub_noises[0], 0.0)
    assert np.allclose(sub_noises[1], 16.0)


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


def test_online_noise_monitor_samples_on_configured_interval():
    class FakeInjector:
        def __init__(self):
            self.calls = []

        def monitor_online_recognition(
            self,
            protected_frame,
            ground_truth,
            model_name,
            engine,
            ocr_evaluator,
        ):
            self.calls.append((protected_frame, ground_truth, model_name, engine))
            return {"triggered": True, "preferred_method": "pgd"}

    injector = FakeInjector()
    frame = np.zeros((4, 4, 3), dtype=np.uint8)

    skipped = run_online_noise_monitor(
        injector,
        frame,
        cycle=3,
        enabled=True,
        interval_cycles=2,
    )
    sampled = run_online_noise_monitor(
        injector,
        frame,
        cycle=4,
        enabled=True,
        interval_cycles=2,
        model_name="tesseract",
        engine="tesseract",
        ground_truth="SECRET",
        ocr_evaluator=object(),
    )

    assert skipped is None
    assert sampled["status"] == "sampled"
    assert sampled["preferred_method"] == "pgd"
    assert injector.calls[0][0] is frame
    assert injector.calls[0][1:] == ("SECRET", "tesseract", "tesseract")
