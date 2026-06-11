"""
去混淆/重构攻击（改进项 B2，交底书 7.3）

交底书把"AI 自适应去混淆攻击"列为重点防御对象，但原实验从未实现这类攻击。
本模块实现由弱到强的三档重构攻击，诚实量化方案在重构攻击下的脆弱性：

  1. 多帧中值堆叠 + 去噪（无需训练）
  2. 单帧 inpainting 重构（OpenCV，无需训练）
  3. 多帧时域平均后锐化（近似"学习去混淆"的下界）

结论性发现（与 PoC 主结论一致）：一旦攻击者能采集覆盖完整周期的多帧，
中值/平均堆叠即可高质量重构——重构网络只会更强。单帧 inpainting 则因
信息缺失过多而基本无效。
"""

import numpy as np


def reconstruct_median_stack(subframes: list[np.ndarray], k: int | None = None) -> np.ndarray:
    """
    多帧中值堆叠重构。

    对覆盖完整周期的子帧逐像素取中值——掩模使每像素在多数子帧为 0、
    仅 1/n 帧为真实值，中值能滤除 0 与噪声、逼近真实像素（当 k≥n 且
    每像素至少被点亮一次时）。比均值更抗对抗噪声。

    Args:
        subframes: 子帧序列
        k: 使用前 k 帧，None 用全部
    """
    frames = subframes[:k] if k else subframes
    stack = np.stack([f.astype(np.float32) for f in frames], axis=0)
    # 仅对非零像素取中值（0 是掩模屏蔽，不代表真实暗像素）
    stack_nan = np.where(stack > 0, stack, np.nan)
    with np.errstate(all="ignore"):
        med = np.nanmedian(stack_nan, axis=0)
    med = np.where(np.isnan(med), 0.0, med)
    return med.clip(0, 255).astype(np.uint8)


def reconstruct_max_stack(subframes: list[np.ndarray]) -> np.ndarray:
    """
    多帧逐像素取最大值重构。

    掩模屏蔽处为 0，真实值为正，取 max 直接恢复每像素被点亮时的值。
    对无噪声掩模方案是**精确**重构——这是该方案对完整周期采集最脆弱处。
    """
    stack = np.stack([f.astype(np.float32) for f in subframes], axis=0)
    return stack.max(axis=0).clip(0, 255).astype(np.uint8)


def reconstruct_inpaint_single(subframe: np.ndarray) -> np.ndarray:
    """
    单帧 inpainting 重构（攻击者只拿到一帧时）。

    把掩模屏蔽的 0 像素当作缺失区域，用 OpenCV Telea inpaint 补全。
    由于单帧丢失 (n-1)/n 的像素，缺失率过高，重构通常失败——
    这正是单帧防御有效的体现。
    """
    try:
        import cv2
    except ImportError:
        return subframe.copy()

    gray = np.mean(subframe, axis=-1)
    missing = (gray < 1).astype(np.uint8) * 255  # 缺失掩码
    return cv2.inpaint(subframe, missing, inpaintRadius=3, flags=cv2.INPAINT_TELEA)


def reconstruct_average_sharpen(subframes: list[np.ndarray]) -> np.ndarray:
    """
    时域平均 + 反锐化（近似"学习型去混淆"的简单下界）。

    平均恢复整体结构，再用 unsharp mask 复原被亮度补偿/噪声柔化的边缘。
    """
    avg = np.mean([f.astype(np.float32) for f in subframes], axis=0)
    avg_u8 = avg.clip(0, 255).astype(np.uint8)
    try:
        import cv2
        blur = cv2.GaussianBlur(avg_u8, (0, 0), 1.5)
        sharp = cv2.addWeighted(avg_u8, 1.6, blur, -0.6, 0)
        return sharp
    except ImportError:
        return avg_u8


def evaluate_reconstruction(
    original: np.ndarray,
    subframes: list[np.ndarray],
    ground_truth: str = "",
    ocr_evaluator=None,
    engine: str = "tesseract",
) -> dict:
    """
    运行全部重构攻击并量化效果（PSNR + 可选 OCR 恢复率）。

    Returns:
        dict: 各攻击方法的 PSNR/SSIM/OCR 准确率
    """
    from src.evaluation.metrics import compute_ssim

    attacks = {
        "median_stack": reconstruct_median_stack(subframes),
        "max_stack": reconstruct_max_stack(subframes),
        "inpaint_single": reconstruct_inpaint_single(subframes[0]),
        "average_sharpen": reconstruct_average_sharpen(subframes),
    }

    results = {}
    for name, recon in attacks.items():
        mse = np.mean((original.astype(float) - recon.astype(float)) ** 2)
        psnr = float(10 * np.log10(255**2 / mse)) if mse > 0 else 99.0
        entry = {
            "psnr_db": psnr,
            "ssim": compute_ssim(original, recon),
        }
        if ocr_evaluator and ground_truth:
            try:
                r = ocr_evaluator.evaluate_single(recon, ground_truth, engine)
                entry["char_accuracy"] = r.char_accuracy
            except Exception:
                entry["char_accuracy"] = -1.0
        results[name] = entry

    return results
