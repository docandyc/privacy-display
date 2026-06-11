import numpy as np

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


def test_model_specific_surrogates_produce_distinct_noise():
    injector = NoiseInjector(n=4, epsilon=8 / 255)
    image = np.zeros((32, 32, 3), dtype=np.float32)
    image[:, 10:22] = 1.0

    tesseract_noise = injector.generate_fgsm_noise(image, "tesseract")
    yolo_noise = injector.generate_fgsm_noise(image, "yolov8")

    assert not np.array_equal(tesseract_noise, yolo_noise)


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
