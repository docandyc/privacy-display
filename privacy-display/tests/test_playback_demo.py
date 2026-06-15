"""playback_demo 预计算与 CLI 解析测试（不依赖 pygame/显示环境）。"""

import numpy as np
import pytest

from src.core.subframe_composer import SubframeComposer
from src.demo.playback_demo import (
    CET6_PDF_PATH,
    apply_anti_ocr_artifacts,
    build_playback_frames,
    extract_text_saliency_mask,
    fit_image_to_canvas,
    generate_cell_masks,
    make_cet6_demo_document,
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


def test_fit_image_to_canvas_preserves_aspect_ratio():
    img = np.zeros((40, 20, 3), dtype=np.uint8)
    fitted = fit_image_to_canvas(img, width=100, height=100)

    assert fitted.shape == (100, 100, 3)
    non_bg = np.any(fitted != 245, axis=2)
    ys, xs = np.where(non_bg)
    assert xs.max() - xs.min() + 1 == 50
    assert ys.max() - ys.min() + 1 == 100


def test_make_cet6_demo_document_renders_pdf_when_available():
    if not CET6_PDF_PATH.exists():
        pytest.skip("CET6 demo PDF is not present in this checkout")

    doc = make_cet6_demo_document(320, 180, page_number=1)

    assert doc.shape == (180, 320, 3)
    assert doc.dtype == np.uint8
    assert doc.mean() > 220
    assert doc.min() < 80


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


def test_explicit_anti_ocr_off_matches_default_output():
    img = _small_test_image()

    default_frames, default_meta = build_playback_frames(
        img, n=2, cycles=2, key=KEY, use_noise=False
    )
    off_frames, off_meta = build_playback_frames(
        img,
        n=2,
        cycles=2,
        key=KEY,
        use_noise=False,
        anti_ocr_profile="off",
    )

    assert default_meta["anti_ocr"]["profile"] == "off"
    assert off_meta["anti_ocr"]["profile"] == "off"
    for (fa, ka), (fb, kb) in zip(default_frames, off_frames):
        assert ka == kb
        assert np.array_equal(fa, fb)


def test_generate_cell_masks_are_deterministic_and_complete():
    masks_a = generate_cell_masks(
        width=17, height=13, n=4, cycle=5, cell_size=3, key=KEY
    )
    masks_b = generate_cell_masks(
        width=17, height=13, n=4, cycle=5, cell_size=3, key=KEY
    )

    total = sum(mask.astype(np.int32) for mask in masks_a)
    assert np.all(total == 1)
    for a, b in zip(masks_a, masks_b):
        assert np.array_equal(a, b)

    assignment = np.argmax(np.stack(masks_a, axis=0), axis=0)
    assert np.all(assignment[:3, :3] == assignment[0, 0])


def test_strong_profile_changes_frames_and_records_metadata():
    img = make_demo_document(320, 180)
    off_frames, _ = build_playback_frames(
        img, n=2, cycles=1, key=KEY, use_noise=False
    )
    strong_frames, meta = build_playback_frames(
        img,
        n=2,
        cycles=1,
        key=KEY,
        use_noise=False,
        anti_ocr_profile="strong",
        mask_cell_size=3,
        stripe_width=5,
        stripe_alpha=0.5,
        glyph_alpha=0.6,
    )

    anti = meta["anti_ocr"]
    assert anti["profile"] == "strong"
    assert anti["mask_cell_size"] == 3
    assert anti["stripe_width"] == 5
    assert anti["stripe_alpha"] == 0.5
    assert anti["glyph_alpha"] == 0.6
    assert anti["saliency_pixels"] > 0
    assert any(
        not np.array_equal(a[0], b[0])
        for a, b in zip(off_frames, strong_frames)
    )


def test_vlm_profile_uses_stronger_defaults_and_records_metadata():
    img = make_demo_document(320, 180)
    off_frames, _ = build_playback_frames(
        img, n=2, cycles=1, key=KEY, use_noise=False
    )
    vlm_frames, meta = build_playback_frames(
        img,
        n=2,
        cycles=1,
        key=KEY,
        use_noise=False,
        anti_ocr_profile="vlm",
    )

    anti = meta["anti_ocr"]
    assert anti["profile"] == "vlm"
    assert anti["mask_cell_size"] == 2
    assert anti["stripe_width"] == 6
    assert anti["stripe_alpha"] == 0.42
    assert anti["glyph_alpha"] == 0.55
    assert anti["saliency_pixels"] > 0
    assert any(
        not np.array_equal(a[0], b[0])
        for a, b in zip(off_frames, vlm_frames)
    )


@pytest.mark.parametrize("profile", ["strong", "vlm"])
def test_anti_ocr_profiles_coexist_with_inversion(profile):
    img = make_demo_document(320, 180)
    frames, meta = build_playback_frames(
        img,
        n=4,
        cycles=2,
        key=KEY,
        use_noise=False,
        insert_inversion=True,
        anti_ocr_profile=profile,
    )

    # 反色帧（长曝光防御）与 anti-OCR 叠加层共存：每周期 n 个子帧 + 1 个反色帧。
    assert meta["insert_inversion"] is True
    assert meta["per_cycle_slots"] == 5
    kinds = [kind for _, kind in frames]
    assert kinds.count("subframe") == 2 * 4
    assert kinds.count("inversion") == 2
    # 反色帧位于每周期末尾，且自身不叠加 anti-OCR 伪迹（保持灰场中和能力）。
    assert kinds == ["subframe"] * 4 + ["inversion"] + ["subframe"] * 4 + ["inversion"]


def test_strong_profile_disrupts_integrated_glyph_regions():
    img = make_demo_document(320, 180)
    frames, meta = build_playback_frames(
        img,
        n=2,
        cycles=1,
        key=KEY,
        use_noise=False,
        anti_ocr_profile="strong",
        stripe_width=5,
        stripe_alpha=0.6,
        glyph_alpha=0.7,
    )

    subframes = [frame for frame, kind in frames if kind == "subframe"]
    integrated = SubframeComposer(n=2, gamma=1.0).integrate_subframes(
        subframes,
        pedestal=meta["pedestal"],
    )
    saliency = extract_text_saliency_mask(img)
    diff = np.abs(integrated.astype(np.int16) - img.astype(np.int16))

    assert float(diff[saliency].mean()) > 8.0


def test_vlm_profile_disrupts_integrated_glyph_regions_more_than_strong():
    img = make_demo_document(320, 180)
    strong_frames, strong_meta = build_playback_frames(
        img,
        n=2,
        cycles=1,
        key=KEY,
        use_noise=False,
        anti_ocr_profile="strong",
    )
    vlm_frames, vlm_meta = build_playback_frames(
        img,
        n=2,
        cycles=1,
        key=KEY,
        use_noise=False,
        anti_ocr_profile="vlm",
    )

    composer = SubframeComposer(n=2, gamma=1.0)
    strong_integrated = composer.integrate_subframes(
        [frame for frame, kind in strong_frames if kind == "subframe"],
        pedestal=strong_meta["pedestal"],
    )
    vlm_integrated = composer.integrate_subframes(
        [frame for frame, kind in vlm_frames if kind == "subframe"],
        pedestal=vlm_meta["pedestal"],
    )
    saliency = extract_text_saliency_mask(img)
    strong_diff = np.abs(
        strong_integrated.astype(np.int16) - img.astype(np.int16)
    )
    vlm_diff = np.abs(vlm_integrated.astype(np.int16) - img.astype(np.int16))

    assert float(vlm_diff[saliency].mean()) > float(strong_diff[saliency].mean()) * 2


def test_default_strong_profile_preserves_readable_text_contrast():
    img = make_demo_document(320, 180)
    frames, meta = build_playback_frames(
        img,
        n=2,
        cycles=1,
        key=KEY,
        use_noise=False,
        anti_ocr_profile="strong",
    )

    subframes = [frame for frame, kind in frames if kind == "subframe"]
    integrated = SubframeComposer(n=2, gamma=1.0).integrate_subframes(
        subframes,
        pedestal=meta["pedestal"],
    )
    saliency = extract_text_saliency_mask(img)
    background = ~saliency

    assert meta["anti_ocr"]["mask_cell_size"] == 1
    assert float(integrated[background].mean() - integrated[saliency].mean()) > 35.0


def test_apply_anti_ocr_artifacts_is_deterministic():
    img = make_demo_document(160, 90)
    frame = img.copy()
    saliency = extract_text_saliency_mask(img)

    a = apply_anti_ocr_artifacts(frame, img, saliency, 1, 2, 5, 0.4, 0.5)
    b = apply_anti_ocr_artifacts(frame, img, saliency, 1, 2, 5, 0.4, 0.5)

    assert np.array_equal(a, b)
    assert not np.array_equal(a, frame)


def test_parse_args_defaults():
    cfg = parse_args([])

    assert cfg.width == 1280
    assert cfg.height == 720
    assert cfg.n == 4
    assert cfg.cycles == 16
    assert cfg.use_noise
    assert not cfg.insert_inversion
    assert cfg.image_path is None
    assert cfg.demo_name == "document"
    assert cfg.pdf_page == 1
    assert cfg.benchmark_seconds == 0.0
    assert cfg.anti_ocr_profile == "off"
    assert cfg.mask_cell_size == 1
    assert cfg.stripe_width == 10
    assert cfg.stripe_alpha == 0.18
    assert cfg.glyph_alpha == 0.22


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


def test_parse_args_anti_ocr_options():
    cfg = parse_args([
        "--anti-ocr-profile", "strong",
        "--mask-cell-size", "4",
        "--stripe-width", "9",
        "--stripe-alpha", "0.7",
        "--glyph-alpha", "0.8",
    ])

    assert cfg.anti_ocr_profile == "strong"
    assert cfg.mask_cell_size == 4
    assert cfg.stripe_width == 9
    assert cfg.stripe_alpha == 0.7
    assert cfg.glyph_alpha == 0.8


def test_parse_args_vlm_profile_defaults():
    cfg = parse_args(["--anti-ocr-profile", "vlm"])

    assert cfg.anti_ocr_profile == "vlm"
    assert cfg.mask_cell_size == 2
    assert cfg.stripe_width == 6
    assert cfg.stripe_alpha == 0.42
    assert cfg.glyph_alpha == 0.55


def test_parse_args_cet6_demo_options():
    cfg = parse_args(["--demo", "cet6", "--pdf-page", "3"])

    assert cfg.demo_name == "cet6"
    assert cfg.pdf_page == 3
