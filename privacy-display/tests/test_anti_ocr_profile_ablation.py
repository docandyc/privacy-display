"""anti_ocr_profile_ablation 帧源/可读性 helper 的确定性测试（不依赖 tesseract/OCR）。

OCR/VLM 全量评估为人工跑；此处只验证实验赖以成立的帧装配与趋势自洽。
"""

from collections import defaultdict

import numpy as np

import experiments.anti_ocr_profile_ablation as ab
from src.attack.camera_simulator import CameraSimulator
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


def test_build_frame_sequence_deployed_includes_weak_inversion():
    img, _, _ = _setup()
    sequence, subframes, _, meta = ab.build_frame_sequence(
        img,
        n=4,
        cycles=2,
        epsilon=8 / 255,
        profile="strong",
        stripe_alpha=ab.DEPLOYED_STRIPE_ALPHA,
        glyph_alpha=ab.DEPLOYED_GLYPH_ALPHA,
        inversion_alpha=ab.DEPLOYED_INVERSION_ALPHA,
    )

    assert len(subframes) == 2 * 4
    assert len(sequence) == 2 * 5
    assert meta["insert_inversion"] is True
    assert meta["per_cycle_slots"] == 5
    assert meta["inversion_alpha"] == ab.DEPLOYED_INVERSION_ALPHA


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


def test_readability_drift_brightness_aligns_deployed_inversion_slot():
    img, composer, saliency = _setup()
    subframes, pedestal = ab.build_subframes(
        img, n=4, cycles=4, epsilon=8 / 255, profile="strong",
        stripe_alpha=ab.DEPLOYED_STRIPE_ALPHA, glyph_alpha=ab.DEPLOYED_GLYPH_ALPHA,
    )
    one_cycle = subframes[:4]
    inv = ab.inversion_frame_for(composer, img, ab.DEPLOYED_INVERSION_ALPHA)

    _, aligned = ab.readability_drift(composer, one_cycle, inv, pedestal, img, saliency)
    dimmed = composer.integrate_subframes(one_cycle + [inv], pedestal=pedestal)

    aligned_error = abs(float(aligned.mean()) - float(img.mean()))
    dimmed_error = abs(float(dimmed.mean()) - float(img.mean()))
    assert aligned_error < dimmed_error


def test_frame_sequence_with_inversion_uses_every_cycle():
    img, composer, _ = _setup()
    subframes, _ = ab.build_subframes(
        img, n=4, cycles=3, epsilon=8 / 255, profile="strong",
        stripe_alpha=0.10, glyph_alpha=0.12,
    )
    inv = ab.inversion_frame_for(composer, img, 0.2)

    sequence = ab.frame_sequence_with_inversion(subframes, 4, inv)

    assert len(sequence) == 3 * 5
    assert np.array_equal(sequence[4], inv)
    assert np.array_equal(sequence[9], inv)
    assert np.array_equal(sequence[14], inv)


def test_inversion_frame_recovery_attack_inverts_and_stretches_partial_copy():
    img, composer, _ = _setup()
    inv = ab.inversion_frame_for(composer, img, 0.2)

    recovered = ab.inversion_frame_recovery_attack(inv)

    inv_contrast = float(inv.max()) - float(inv.min())
    recovered_contrast = float(recovered.max()) - float(recovered.min())
    corr = np.corrcoef(
        img[..., 0].astype(np.float32).ravel(),
        recovered[..., 0].astype(np.float32).ravel(),
    )[0, 1]
    assert recovered_contrast > inv_contrast
    assert corr > 0.95


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


def test_vlm_errors_are_counted_not_converted_to_zero_recovery():
    class FailingClient:
        def analyze_image(self, image, ground_truth=""):
            raise RuntimeError("synthetic API failure")

    img, _, _ = _setup()
    acc = defaultdict(lambda: defaultdict(list))

    ab.run_block_vlm(
        acc,
        client=FailingClient(),
        cam=CameraSimulator(),
        img=img,
        gt="VISIBLE TEXT",
        n=4,
        cycles=1,
        eps=8 / 255,
    )
    detail = ab.summarize(acc)
    summary = ab.headline_summary(detail)

    assert detail["vlm/off"]["error_count"] == 1
    assert detail["vlm/strong@deployed"]["error_count"] == 1
    assert detail["vlm/off"]["call_success"]["mean"] == 0.0
    assert "temporal_avg_char" not in detail["vlm/off"]
    assert "vlm/off" not in summary


def test_headline_summary_exposes_char_accuracy_rows():
    """publication_summary 靠 summary[*].char_accuracy 收录；headline 须产出该结构。"""
    detail = {
        "block1/off": {
            "single_frame_char": {"mean": 0.0, "count": 4, "ci95": {}},
            "single_frame_exact": {"mean": 0.0, "count": 4, "ci95": {}},
            "temporal_avg_char": {"mean": 0.2, "count": 4, "ci95": {}},
            "temporal_avg_exact": {"mean": 0.1, "count": 4, "ci95": {}},
            "best_observed_char": {"mean": 0.9, "count": 4, "ci95": {}},
            "best_observed_exact": {"mean": 0.5, "count": 4, "ci95": {}},
        },
        "block3/alpha_0.2": {
            "long_exposure_char": {"mean": 0.1, "count": 4, "ci95": {}},
            "long_exposure_exact": {"mean": 0.0, "count": 4, "ci95": {}},
            "inversion_frame_attack_char": {"mean": 0.7, "count": 4, "ci95": {}},
            "inversion_frame_attack_exact": {"mean": 0.2, "count": 4, "ci95": {}},
        },
        "block2/s0.10_g0.12": {
            "temporal_avg_char": {"mean": 0.2, "count": 4, "ci95": {}},
            "temporal_avg_exact": {"mean": 0.0, "count": 4, "ci95": {}},
        },
        "vlm/off": {
            "temporal_avg_char": {"mean": 0.0, "count": 0, "ci95": {}},
            "temporal_avg_exact": {"mean": 0.0, "count": 0, "ci95": {}},
            "error_count": 4,
        },
    }
    summary = ab.headline_summary(detail)
    assert set(summary) == {"block1/off", "block3/alpha_0.2", "block2/s0.10_g0.12"}
    assert all("char_accuracy" in row for row in summary.values())
    assert all("exact_match" in row for row in summary.values())
    assert summary["block1/off"]["headline_metric"] == "temporal_average"
    assert summary["block1/off"]["char_accuracy"]["mean"] == 0.2
    assert summary["block1/off"]["best_observed_char"]["mean"] == 0.9
    assert summary["block3/alpha_0.2"]["headline_metric"] == "long_exposure"
    assert summary["block3/alpha_0.2"]["inversion_frame_attack_char"]["mean"] == 0.7
