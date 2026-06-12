import numpy as np
import pytest

from src.attack.camera_simulator import CameraParams, CameraSimulator
from src.core.noise_injector import NoiseInjector


def test_pgd_noise_respects_linf_budget():
    injector = NoiseInjector(n=4, epsilon=8 / 255)
    image = np.random.default_rng(0).random((24, 32, 3), dtype=np.float32)

    noise = injector.generate_pgd_noise(
        image,
        model_name="easyocr",
        iterations=3,
        random_start=False,
    )

    assert noise.shape == image.shape
    assert float(np.max(np.abs(noise))) <= 8 / 255 + 1e-6


def test_rotating_noise_cycles_across_target_models():
    injector = NoiseInjector(n=4, target_models=["tesseract", "easyocr", "yolov8"])
    image = np.random.default_rng(1).random((16, 16, 3), dtype=np.float32)

    selections = [injector.generate_rotating_noise(image, cycle=i)[1] for i in range(4)]

    assert selections == ["tesseract", "easyocr", "yolov8", "tesseract"]


def test_online_update_switches_to_stronger_strategy():
    injector = NoiseInjector(n=4, epsilon=8 / 255, max_epsilon=16 / 255)

    before = injector.get_online_state("tesseract")
    after = injector.update_online_strategy("tesseract", recognition_score=0.75)

    assert before["preferred_method"] == "fgsm"
    assert after["preferred_method"] == "pgd"
    assert after["epsilon_scale"] > before["epsilon_scale"]
    assert after["updates"] == 1


def test_monitor_online_recognition_runs_evaluator_and_updates_strategy():
    class Result:
        text = "SECRET"
        char_accuracy = 0.8

    class FakeEvaluator:
        def evaluate_single(self, image, ground_truth, engine):
            assert ground_truth == "SECRET"
            assert engine == "tesseract"
            return Result()

    injector = NoiseInjector(n=4, epsilon=8 / 255, max_epsilon=16 / 255)
    frame = np.zeros((8, 8, 3), dtype=np.uint8)

    state = injector.monitor_online_recognition(
        frame,
        ground_truth="SECRET",
        model_name="tesseract",
        ocr_evaluator=FakeEvaluator(),
        threshold=0.5,
    )

    assert state["triggered"] is True
    assert state["preferred_method"] == "pgd"
    assert state["updates"] == 1
    assert state["recognized_text"] == "SECRET"


def test_fgsm_uses_differentiable_shadow_model_when_torch_available():
    pytest.importorskip("torch")

    injector = NoiseInjector(n=4, epsilon=8 / 255)
    image = np.full((24, 32, 3), 0.7, dtype=np.float32)
    image[7:17, 11:21] = 0.15

    noise = injector.generate_fgsm_noise(image, "tesseract", use_template=False)

    assert injector.last_gradient_source == "shadow"
    assert noise.shape == image.shape
    assert float(np.max(np.abs(noise))) <= 8 / 255 + 1e-6
    assert np.any(noise != 0)


def test_template_generation_saves_metadata_and_is_reused(tmp_path):
    pytest.importorskip("torch")

    image = np.random.default_rng(3).random((16, 20, 3), dtype=np.float32)
    injector = NoiseInjector(n=4, epsilon=8 / 255, template_dir=str(tmp_path))

    noise, metadata = injector.build_template(
        image,
        model_name="tesseract",
        method="fgsm",
        save=True,
    )

    reloaded = NoiseInjector(n=4, epsilon=8 / 255, template_dir=str(tmp_path))
    reused = reloaded.generate_fgsm_noise(image, "tesseract")

    assert metadata["gradient_source"] == "shadow"
    assert reloaded.last_gradient_source == "template"
    assert np.allclose(reused, noise)
    assert reloaded.get_template_metadata("tesseract")["method"] == "fgsm"


def test_model_specific_surrogates_produce_distinct_noise():
    injector = NoiseInjector(n=4, epsilon=8 / 255)
    image = np.zeros((32, 32, 3), dtype=np.float32)
    image[:, 10:22] = 1.0

    tesseract_noise = injector.generate_fgsm_noise(image, "tesseract")
    yolo_noise = injector.generate_fgsm_noise(image, "yolov8")

    assert not np.array_equal(tesseract_noise, yolo_noise)


def test_ocr_noise_pushes_dark_strokes_toward_background():
    injector = NoiseInjector(n=4, epsilon=32 / 255)
    image = np.full((32, 48, 3), 0.78, dtype=np.float32)
    image[8:24, 18:30] = 0.12

    noise = injector.generate_fgsm_noise(image, "tesseract")

    stroke_noise = float(noise[10:22, 20:28].mean())
    background_noise = float(noise[:, :10].mean())
    assert stroke_noise > 0.0
    assert background_noise <= 0.0


def test_rolling_shutter_uses_exposure_weighted_blending():
    cam = CameraSimulator(CameraParams(exposure_time=0.15, readout_time=0.0))
    subframes = [
        np.zeros((1, 1, 3), dtype=np.uint8),
        np.full((1, 1, 3), 90, dtype=np.uint8),
    ]

    captured = cam.capture_rolling_shutter(subframes, display_rate=10.0, switch_time=0.05)

    # Exposure [0.05, 0.20] overlaps frame0 for 0.05s and frame1 for 0.10s.
    assert int(captured[0, 0, 0]) == 60


def test_rolling_shutter_rows_follow_readout_time():
    cam = CameraSimulator(CameraParams(exposure_time=0.05, readout_time=0.1))
    subframes = [
        np.zeros((2, 1, 3), dtype=np.uint8),
        np.full((2, 1, 3), 100, dtype=np.uint8),
    ]

    captured = cam.capture_rolling_shutter(subframes, display_rate=10.0, switch_time=0.0)

    assert int(captured[0, 0, 0]) == 0
    assert int(captured[1, 0, 0]) == 100


def test_phase_search_recovery_finds_complete_cycle_window():
    cam = CameraSimulator()
    original = np.zeros((8, 8, 3), dtype=np.uint8)
    original[:, :4] = [180, 90, 40]
    original[:, 4:] = [20, 150, 220]
    masks = [
        np.tile(np.array([[1, 0], [0, 0]], dtype=bool), (4, 4)),
        np.tile(np.array([[0, 1], [0, 0]], dtype=bool), (4, 4)),
        np.tile(np.array([[0, 0], [1, 0]], dtype=bool), (4, 4)),
        np.tile(np.array([[0, 0], [0, 1]], dtype=bool), (4, 4)),
    ]
    subframes = [(original * mask[..., None]).astype(np.uint8) for mask in masks]
    # Prefix noise frame makes the correct cycle start at offset 1.
    sequence = [np.zeros_like(original)] + subframes + [np.zeros_like(original)]

    recovered, meta = cam.phase_search_recovery_attack(
        sequence,
        window_size=4,
        method="mean",
        restore_brightness=True,
    )

    assert meta["best_offset"] == 1
    assert meta["window_size"] == 4
    assert np.mean(np.abs(recovered.astype(np.int16) - original.astype(np.int16))) < 1.0


def test_weighted_differential_accumulator_reports_channel_metadata():
    cam = CameraSimulator()
    dark = np.zeros((8, 8, 3), dtype=np.uint8)
    blue = dark.copy()
    blue[:, 2:6, 2] = 220
    frames = [dark, blue, dark, blue]

    recovered, meta = cam.weighted_differential_accumulator_attack(
        frames,
        channel="blue",
    )

    assert recovered.shape == dark.shape
    assert recovered.dtype == np.uint8
    assert meta["channel"] == "blue"
    assert meta["frames"] == 4
    assert recovered[:, 2:6].mean() > recovered[:, :2].mean()


def test_screen_camera_attack_suite_returns_publication_baselines():
    cam = CameraSimulator()
    original = np.full((6, 6, 3), 120, dtype=np.uint8)
    subframes = [
        original * np.array([[[1]], [[0]], [[0]], [[1]], [[0]], [[0]]], dtype=np.uint8),
        original * np.array([[[0]], [[1]], [[0]], [[0]], [[1]], [[0]]], dtype=np.uint8),
        original * np.array([[[0]], [[0]], [[1]], [[0]], [[0]], [[1]]], dtype=np.uint8),
    ]

    suite = cam.screen_camera_attack_suite(subframes, cycle_length=3)

    assert {
        "phase_search_mean",
        "phase_search_max",
        "differential_luma",
        "differential_blue",
        "blue_channel_max",
    }.issubset(suite)
    for entry in suite.values():
        assert entry["frame"].shape == original.shape
        assert "metadata" in entry and "score" in entry["metadata"]


def test_screen_camera_attack_rejects_invalid_inputs():
    cam = CameraSimulator()
    frame = np.zeros((2, 2, 3), dtype=np.uint8)

    with pytest.raises(ValueError):
        cam.phase_search_recovery_attack([], window_size=1)
    with pytest.raises(ValueError):
        cam.phase_search_recovery_attack([frame], window_size=2)
    with pytest.raises(ValueError):
        cam.weighted_differential_accumulator_attack([frame])
    with pytest.raises(ValueError):
        cam.channel_selective_recovery_attack([frame], channel="alpha")
