"""anti_ocr_profile_ablation 帧源/可读性 helper 的确定性测试（不依赖 tesseract/OCR）。

OCR/VLM 全量评估为人工跑；此处只验证实验赖以成立的帧装配与趋势自洽。
"""

import numpy as np

import experiments.anti_ocr_profile_ablation as ab
from src.core.subframe_composer import SubframeComposer
from src.demo.playback_demo import extract_text_saliency_mask, make_demo_document


def _setup(n=4, cycles=4):
    img = make_demo_document(320, 180)
    composer = SubframeComposer(n=n, gamma=1.0)
    saliency = extract_text_saliency_mask(img)
    return img, composer, saliency


def test_build_subframes_frame_counts():
    img, _, _ = _setup()
    sub_off, ped_off = ab.build_subframes(
        img, n=4, cycles=4, epsilon=8 / 255, profile="off",
        stripe_alpha=None, glyph_alpha=None,
    )
    sub_strong, _ = ab.build_subframes(
        img, n=4, cycles=4, epsilon=8 / 255, profile="strong",
        stripe_alpha=0.10, glyph_alpha=0.12,
    )
    assert len(sub_off) == 4 * 4
    assert len(sub_strong) == 4 * 4
    assert all(f.shape == img.shape and f.dtype == np.uint8 for f in sub_strong)


def test_strong_overlay_disrupts_reconstruction_more_than_off():
    """anti-OCR 叠加故意打破精确重建：文本区积分漂移应远大于 off 基线。"""
    img, composer, saliency = _setup()
    sub_off, ped_off = ab.build_subframes(
        img, n=4, cycles=4, epsilon=8 / 255, profile="off",
        stripe_alpha=None, glyph_alpha=None,
    )
    sub_strong, ped_strong = ab.build_subframes(
        img, n=4, cycles=4, epsilon=8 / 255, profile="strong",
        stripe_alpha=0.10, glyph_alpha=0.12,
    )
    drift_off, _ = ab.readability_drift(composer, sub_off[:4], None, ped_off, img, saliency)
    drift_strong, _ = ab.readability_drift(
        composer, sub_strong[:4], None, ped_strong, img, saliency
    )
    assert drift_strong > drift_off


def test_partial_inversion_more_readable_than_full():
    """弱反色 α=0.2 比全反色 α=1.0 更可读（积分文本区漂移更小），α=0 居中偏低。"""
    img, composer, saliency = _setup()
    sub, ped = ab.build_subframes(
        img, n=4, cycles=4, epsilon=8 / 255, profile="strong",
        stripe_alpha=0.10, glyph_alpha=0.12,
    )
    one_cycle = sub[:4]

    inv_none = ab.inversion_frame_for(composer, img, 0.0)
    inv_weak = ab.inversion_frame_for(composer, img, 0.2)
    inv_full = ab.inversion_frame_for(composer, img, 1.0)
    assert inv_none is None and inv_weak is not None and inv_full is not None
    # 弱反色振幅应远小于全反色（朝黑压暗）。
    assert float(inv_weak.mean()) < float(inv_full.mean())

    drift_weak, _ = ab.readability_drift(composer, one_cycle, inv_weak, ped, img, saliency)
    drift_full, _ = ab.readability_drift(composer, one_cycle, inv_full, ped, img, saliency)
    assert drift_weak < drift_full


def test_headline_summary_exposes_char_accuracy_rows():
    """publication_summary 靠 summary[*].char_accuracy 收录；headline 须产出该结构。"""
    detail = {
        "block1/off": {"strong_camera_char": {"mean": 0.9, "ci95": {}}},
        "block3/alpha_0.2": {"long_exposure_char": {"mean": 0.1, "ci95": {}}},
        "block2/s0.10_g0.12": {"temporal_avg_char": {"mean": 0.2, "ci95": {}}},
    }
    summary = ab.headline_summary(detail)
    assert set(summary) == set(detail)
    assert all("char_accuracy" in row for row in summary.values())
