import numpy as np
import pytest

from src.attack.camera_simulator import CameraSimulator
from src.core.config import PrivacyDisplayConfig
from src.core.fatigue_policy import (
    AdaptiveRefreshPolicy,
    blue_light_filter,
    viewing_distance_adjust,
)
from src.core.hdr_compensation import AmbientAdaptation, hlg_decode, hlg_encode
from src.core.mask_generator import MaskGenerator
from src.core.noise_injector import NoiseInjector
from src.core.timing_controller import (
    check_bandwidth_fit,
    compute_bandwidth_gbps,
    compute_permutation_hash,
    TimingController,
)


def test_off_axis_temporal_average_changes_capture():
    cam = CameraSimulator()
    subframes = [
        np.full((24, 24, 3), [200, 80, 40], dtype=np.uint8),
        np.full((24, 24, 3), [40, 200, 80], dtype=np.uint8),
        np.full((24, 24, 3), [80, 40, 200], dtype=np.uint8),
    ]

    frontal = cam.temporal_averaging_attack(subframes, k=3, randomize_order=False)
    off_axis = cam.off_axis_temporal_average_attack(
        subframes,
        angle_degrees=40,
        regions=(3, 3),
        cycles=1,
    )

    assert off_axis.shape == frontal.shape
    assert off_axis.mean() < frontal.mean()
    assert not np.array_equal(off_axis, frontal)


def test_off_axis_correction_equalizes_region_brightness():
    cam = CameraSimulator()
    frame = np.zeros((30, 30, 3), dtype=np.uint8)
    vals = [40, 80, 120, 160, 200, 90, 70, 130, 180]
    rh = rw = 10
    idx = 0
    for r in range(3):
        for c in range(3):
            frame[r * rh:(r + 1) * rh, c * rw:(c + 1) * rw] = vals[idx]
            idx += 1

    # angle=0 → 无位移，纯逐区域增益归一化：各区域均值向全局均值收敛。
    corrected = cam.off_axis_correction(frame, regions=(3, 3), angle_degrees=0.0)

    assert corrected.shape == frame.shape and corrected.dtype == np.uint8

    def _spread(f):
        means = [
            f[r * rh:(r + 1) * rh, c * rw:(c + 1) * rw].mean()
            for r in range(3)
            for c in range(3)
        ]
        return float(np.std(means))

    assert _spread(corrected) < _spread(frame)


def test_spatial_complementary_noise_zero_sum_and_local_cancel():
    injector = NoiseInjector(n=4, epsilon=8 / 255)
    base = np.ones((8, 8, 3), dtype=np.float32) * 0.1

    sub_noises = injector.split_complementary_spatial(base, tile=1)

    ok, residual = injector.verify_complementarity(sub_noises)
    assert ok and residual < 1e-6
    # A 2x2 checkerboard neighborhood cancels inside each subframe.
    assert np.max(np.abs(sub_noises[0][:2, :2].sum(axis=(0, 1)))) < 1e-6


def test_easyocr_e2e_fallback_is_bounded_when_model_unavailable(monkeypatch):
    injector = NoiseInjector(n=4, epsilon=8 / 255)
    monkeypatch.setattr(injector, "_easyocr_e2e_gradient", lambda image: None)
    image = np.zeros((16, 16, 3), dtype=np.float32)
    image[:, 6:10] = 1.0

    noise = injector.generate_fgsm_noise(image, "easyocr", use_template=False)

    assert injector.last_gradient_source in {"shadow", "surrogate"}
    assert noise.shape == image.shape
    assert float(np.max(np.abs(noise))) <= 8 / 255 + 1e-6


def test_target_model_fallback_when_tesseract_not_configured():
    injector = NoiseInjector(n=4, epsilon=8 / 255, target_models=["yolov8"])
    image = np.zeros((12, 12, 3), dtype=np.float32)

    noise = injector.generate_fgsm_noise(image, "unknown", use_template=False)

    assert noise.shape == image.shape
    assert float(np.max(np.abs(noise))) <= 8 / 255 + 1e-6


def test_fatigue_policy_blue_filter_and_distance_adjust():
    policy = AdaptiveRefreshPolicy(min_refresh_hz=120, max_refresh_hz=240)
    frame = np.full((8, 8, 3), 100, dtype=np.uint8)
    moving = frame.copy()
    moving[:4] = 255

    assert policy.select_refresh_rate(frame, frame) == 240
    assert policy.select_refresh_rate(frame, moving) == 120

    filtered = blue_light_filter(np.full((2, 2, 3), 200, dtype=np.uint8), 4000)
    assert filtered[..., 2].mean() < 200
    assert filtered[..., 0].mean() >= 200

    near = viewing_distance_adjust(35)
    far = viewing_distance_adjust(70)
    assert near["reduced"] is True
    assert near["scale"] < far["scale"]


def test_bandwidth_and_permutation_hash_contracts():
    bw = compute_bandwidth_gbps(3840, 2160, 240, bpp=4)
    fit = check_bandwidth_fit(bw)

    assert bw > 70
    assert fit["fits"]["dp2.0_uhbr20"] is True
    assert fit["fits"]["dp1.4_hbr3"] is False

    perm = [2, 0, 1, 3]
    controller = TimingController(refresh_rate=240, n=4)
    controller.set_permutation(9, perm)
    token = controller.get_token()
    assert token.permutation_hash == compute_permutation_hash(perm)
    assert len(token.permutation_hash) == 64


def test_hlg_roundtrip_and_ambient_monotonicity():
    values = np.linspace(0, 1, 32)
    restored = hlg_decode(hlg_encode(values))
    assert np.max(np.abs(restored - values)) < 1e-6

    adapter = AmbientAdaptation()
    low = adapter.adapt(ambient_lux=50)
    high = adapter.adapt(ambient_lux=5000)
    assert high["backlight_scale"] > low["backlight_scale"]
    assert high["weber_contrast"] >= 2.5


def test_pregenerated_masks_match_on_demand():
    key = b"pregen-test-key-000000000000000"
    gen = MaskGenerator(16, 12, 4, key=key)
    gen.pregenerate(cycles=4, start_cycle=10)

    masks = gen.get_pregenerated_masks(12)
    expected = gen.generate(12)
    for a, b in zip(masks, expected):
        assert np.array_equal(a, b)
    assert gen.get_pregenerated_permutation(12) == gen.generate_permutation(12)


def test_config_save_load_and_validation(tmp_path):
    cfg = PrivacyDisplayConfig(
        n=4,
        epsilon=0.05,
        gamma_factor=1.2,
        brightness_model="pixel",
        inversion_alpha=0.3,
        insert_inversion=True,
        refresh_rate=240,
    )
    path = tmp_path / "privacy-display.json"
    cfg.save(path)

    loaded = PrivacyDisplayConfig.load(path)

    assert loaded.n == 4
    assert loaded.key == cfg.key
    assert loaded.to_window_kwargs()["gamma_factor"] == 1.2
    assert loaded.to_window_kwargs()["brightness_model"] == "pixel"
    assert loaded.to_window_kwargs()["inversion_alpha"] == 0.3
    assert loaded.to_window_kwargs()["insert_inversion"] is True
    with pytest.raises(ValueError):
        PrivacyDisplayConfig(n=1)
    with pytest.raises(ValueError):
        PrivacyDisplayConfig(inversion_alpha=1.1)


def test_config_alpha_alias_maps_to_inversion_alpha():
    cfg = PrivacyDisplayConfig.from_dict({
        "n": 4,
        "alpha": 0.3,
        "refresh_rate": 240,
    })

    assert cfg.inversion_alpha == 0.3


def test_config_legacy_alpha_above_inversion_range_maps_to_gamma_factor():
    cfg = PrivacyDisplayConfig.from_dict({
        "n": 4,
        "alpha": 1.2,
        "refresh_rate": 240,
    })

    assert cfg.gamma_factor == 1.2
    assert cfg.inversion_alpha == 0.3


def test_tiny_unet_reconstructor_smoke():
    pytest.importorskip("torch")
    from src.attack.reconstruction_attack import (
        reconstruct_unet_single,
        train_tiny_unet_reconstructor,
    )

    original = np.full((16, 16, 3), 180, dtype=np.uint8)
    masked = original.copy()
    masked[:, ::2] = 0

    model, meta = train_tiny_unet_reconstructor(
        [(masked, original)],
        epochs=1,
        size=(16, 16),
    )
    recon = reconstruct_unet_single(masked, model, size=(16, 16))

    assert meta["available"] is True
    assert recon.shape == original.shape
    assert recon.dtype == np.uint8
