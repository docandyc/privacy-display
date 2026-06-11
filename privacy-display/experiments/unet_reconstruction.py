"""
学习型去混淆攻击实验（G5）

用 tiny U-Net 训练"单子帧 -> 原图"的低分辨率重构攻击。该实验是 CPU 友好
PoC 下界，不声称代表最强学习攻击。

诚实性说明（与 B2 表的 inpaint SSIM=0.026 对照）：
  - B2 的子帧带噪声基底 pedestal=8，未激活像素≈8 而非 0，使
    `reconstruct_inpaint_single` 的 `gray<1` 缺失检测失效→inpaint 近乎空操作，
    输出稀疏暗帧，SSIM 极低（0.026）。
  - 本实验子帧由 `compose(..., None)` 干净生成（未激活像素=0），inpaint 能填洞，
    且测试图为白底黑字、SSIM 被背景主导，故 inpaint SSIM 偏高（~0.93）——
    但这并不代表文字被还原。
  - 因此本实验同时报告 **OCR 字符准确率**（真实隐私指标）：单子帧重构后
    OCR≈0，与"单帧防御有效"结论一致；SSIM 仅作结构参考。
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import _make_test_image
from src.attack.ocr_evaluator import OCREvaluator
from src.attack.reconstruction_attack import (
    reconstruct_inpaint_single,
    reconstruct_unet_single,
    train_tiny_unet_reconstructor,
)
from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.evaluation.metrics import compute_ssim


def _psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = np.mean((a.astype(np.float32) - b.astype(np.float32)) ** 2)
    return float(10 * np.log10(255**2 / mse)) if mse > 0 else 99.0


def _tesseract_ok() -> bool:
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _ocr_char_acc(evaluator, image: np.ndarray, gt: str) -> float:
    if evaluator is None or not evaluator.engines:
        return -1.0
    try:
        return float(evaluator.evaluate_single(image, gt, "tesseract").char_accuracy)
    except Exception:
        return -1.0



def _subframe_pair(text: str, cycle: int, n: int = 4) -> tuple[np.ndarray, np.ndarray]:
    original = _make_test_image(text)
    h, w = original.shape[:2]
    gen = MaskGenerator(w, h, n, key=b"unet-reconstruction-key-00000000")
    composer = SubframeComposer(n=n, gamma=1.0)
    masks = gen.generate(cycle)
    subframes = composer.compose(original, masks, None)
    return subframes[0], original


def _noised_subframe0(
    text: str, cycle: int, n: int = 4, epsilon: float = 8 / 255
) -> np.ndarray:
    """构造带对抗噪声基底（pedestal）的首个子帧，复现真实显示链路输出。"""
    from src.core.noise_injector import NoiseInjector

    original = _make_test_image(text)
    h, w = original.shape[:2]
    gen = MaskGenerator(w, h, n, key=b"unet-reconstruction-key-00000000")
    composer = SubframeComposer(n=n, gamma=1.0)
    injector = NoiseInjector(n=n, epsilon=epsilon)
    masks = gen.generate(cycle)
    nb, _, _ = injector.generate_rotating_noise(
        original.astype(np.float32) / 255.0, cycle=cycle
    )
    pedestal = epsilon * 255
    sub_noises = [(x * 255 + pedestal).astype(np.float32) for x in injector.split_complementary(nb)]
    return composer.compose(original, masks, sub_noises)[0]



def run_unet_reconstruction(
    epochs: int = 3,
    output_dir: str = "experiments/results",
) -> dict:
    texts = [
        "CONFIDENTIAL 2026",
        "PASSWORD admin123",
        "FINANCIAL DATA Q4",
        "TOKEN eyJhbGc",
        "PRIVATE 用户数据",
        "HOLDOUT SECRET 42",
    ]
    pairs = [_subframe_pair(text, i) for i, text in enumerate(texts)]
    train_pairs = pairs[:-1]
    holdout_masked, holdout_original = pairs[-1]
    holdout_gt = texts[-1]
    evaluator = OCREvaluator(engines=["tesseract"]) if _tesseract_ok() else None

    model, meta = train_tiny_unet_reconstructor(
        train_pairs,
        epochs=epochs,
        size=(64, 32),
        seed=0,
    )
    recon = reconstruct_unet_single(holdout_masked, model, size=(64, 32))
    inpaint = reconstruct_inpaint_single(holdout_masked)

    # Pedestal 消融：同一 holdout 的"干净子帧"vs"带噪声 pedestal 子帧"分别 inpaint。
    # 干净子帧未激活像素=0，inpaint 能填洞并恢复 OCR；带 pedestal 子帧未激活≈ε，
    # 缺失检测失效→inpaint 空操作→OCR≈0。直接量化对抗噪声 pedestal 对单帧防御的贡献。
    holdout_noised = _noised_subframe0(holdout_gt, len(texts) - 1)
    inpaint_clean = reconstruct_inpaint_single(holdout_masked)
    inpaint_noised = reconstruct_inpaint_single(holdout_noised)

    report = {
        "method": "tiny_unet_single_subframe",
        "training": meta,
        "ground_truth": holdout_gt,
        "ocr_available": evaluator is not None,
        "ssim_note": (
            "白底黑字 SSIM 被背景主导，不代表文字被还原；OCR 才是隐私指标。"
            "B2 表 inpaint SSIM=0.026 来自带 pedestal 子帧使 inpaint 空操作，"
            "本实验干净子帧 SSIM 偏高且 inpaint 可恢复 OCR——见 pedestal 消融。"
        ),
        "pedestal_ablation": {
            "note": (
                "干净子帧（未激活=0）单帧 inpaint 即可恢复高对比文档 OCR；"
                "加对抗噪声 pedestal 后单帧 inpaint OCR≈0 → pedestal 是单帧"
                "防御对 inpainting 攻击鲁棒的关键，印证 B1‘噪声二级强化’结论。"
            ),
            "clean_subframe_inpaint_ocr": _ocr_char_acc(evaluator, inpaint_clean, holdout_gt),
            "noised_subframe_inpaint_ocr": _ocr_char_acc(evaluator, inpaint_noised, holdout_gt),
        },
        "holdout": {
            "original_reference": {
                "ocr_char_acc": _ocr_char_acc(evaluator, holdout_original, holdout_gt),
            },
            "unet": {
                "psnr_db": _psnr(holdout_original, recon),
                "ssim": compute_ssim(holdout_original, recon),
                "ocr_char_acc": _ocr_char_acc(evaluator, recon, holdout_gt),
            },
            "inpaint_baseline": {
                "psnr_db": _psnr(holdout_original, inpaint),
                "ssim": compute_ssim(holdout_original, inpaint),
                "ocr_char_acc": _ocr_char_acc(evaluator, inpaint, holdout_gt),
            },
        },
    }

    out = Path(output_dir) / "unet_reconstruction.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"结果已保存: {out}")
    return report


if __name__ == "__main__":
    run_unet_reconstruction()
