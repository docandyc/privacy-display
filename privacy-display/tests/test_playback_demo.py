"""playback_demo 预计算与 CLI 解析测试（不依赖 pygame/显示环境）。"""

import numpy as np

from src.core.subframe_composer import SubframeComposer
from src.demo.playback_demo import (
    build_playback_frames,
    make_demo_document,
    parse_args,
)


KEY = b"\x01" * 32


def _small_test_image(width: int = 160, height: int = 90) -> np.ndarray:
    """生成确定性小测试图，像素值限制在 [20, 230] 避免噪声+pedestal 饱和。"""
    rng = np.random.default_rng(0)
    return rng.integers(20, 230, (height, width, 3), dtype=np.uint8)


def test_make_demo_document_shape_and_contrast():
    doc = make_demo_document(1280, 720)

    assert doc.shape == (720, 1280, 3)
    assert doc.dtype == np.uint8
    assert doc.mean() > 200          # 浅色背景为主
    assert doc.min() < 80            # 含深色文字像素


def test_build_playback_frames_counts_without_inversion():
    img = _small_test_image()
    frames, meta = build_playback_frames(img, n=2, cycles=3, key=KEY)

    assert len(frames) == 3 * 2
    assert all(kind == "subframe" for _, kind in frames)
    assert meta["n"] == 2
    assert meta["cycles"] == 3
    assert meta["per_cycle_slots"] == 2
    assert len(meta["permutations"]) == 3
    for perm in meta["permutations"]:
        assert sorted(perm) == [0, 1]


def test_build_playback_frames_inserts_inversion_at_cycle_end():
    img = _small_test_image()
    frames, meta = build_playback_frames(
        img, n=2, cycles=3, insert_inversion=True, key=KEY
    )

    slots = meta["per_cycle_slots"]
    assert slots == 3
    assert len(frames) == 3 * slots
    for cycle in range(3):
        cycle_frames = frames[cycle * slots:(cycle + 1) * slots]
        kinds = [kind for _, kind in cycle_frames]
        assert kinds == ["subframe", "subframe", "inversion"]
        inversion = cycle_frames[-1][0]
        assert np.array_equal(inversion, 255 - img)


def test_each_cycle_integrates_back_to_original():
    img = _small_test_image()
    frames, meta = build_playback_frames(img, n=2, cycles=3, key=KEY)

    composer = SubframeComposer(n=2, gamma=1.0)
    slots = meta["per_cycle_slots"]
    for cycle in range(3):
        cycle_subframes = [
            f for f, kind in frames[cycle * slots:(cycle + 1) * slots]
            if kind == "subframe"
        ]
        integrated = composer.integrate_subframes(
            cycle_subframes,
            pedestal=meta["pedestal"],
        )
        max_err = np.max(
            np.abs(integrated.astype(np.int16) - img.astype(np.int16))
        )
        assert max_err < 2


def test_masks_rotate_across_cycles():
    img = _small_test_image()
    frames, meta = build_playback_frames(img, n=2, cycles=3, key=KEY)

    slots = meta["per_cycle_slots"]
    first_of_cycle0 = frames[0][0]
    first_of_cycle1 = frames[slots][0]
    assert not np.array_equal(first_of_cycle0, first_of_cycle1)


def test_no_noise_mode_has_zero_pedestal_and_pure_masking():
    img = _small_test_image()
    frames, meta = build_playback_frames(
        img, n=2, cycles=3, use_noise=False, key=KEY
    )

    assert meta["pedestal"] == 0
    for sf, kind in frames:
        assert kind == "subframe"
        assert np.all((sf == 0) | (sf == img))


def test_build_playback_frames_is_deterministic_with_same_key():
    img = _small_test_image()
    frames_a, meta_a = build_playback_frames(img, n=2, cycles=3, key=KEY)
    frames_b, meta_b = build_playback_frames(img, n=2, cycles=3, key=KEY)

    assert meta_a["permutations"] == meta_b["permutations"]
    assert len(frames_a) == len(frames_b)
    for (fa, ka), (fb, kb) in zip(frames_a, frames_b):
        assert ka == kb
        assert np.array_equal(fa, fb)


def test_parse_args_defaults():
    cfg = parse_args([])

    assert cfg.width == 1280
    assert cfg.height == 720
    assert cfg.n == 4
    assert cfg.cycles == 16
    assert cfg.use_noise
    assert not cfg.insert_inversion
    assert cfg.image_path is None
    assert cfg.benchmark_seconds == 0.0


def test_parse_args_overrides():
    cfg = parse_args([
        "--no-noise", "--n", "4", "--benchmark", "2",
        "--cycles", "8", "--inversion",
        "--width", "640", "--height", "360",
        "--image", "doc.png",
    ])

    assert not cfg.use_noise
    assert cfg.n == 4
    assert cfg.benchmark_seconds == 2.0
    assert cfg.cycles == 8
    assert cfg.insert_inversion
    assert cfg.width == 640
    assert cfg.height == 360
    assert cfg.image_path == "doc.png"
