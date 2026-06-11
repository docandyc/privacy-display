"""
视觉积分模拟演示

生成对比图：原始帧 vs 单子帧（相机视角）vs 积分帧（人眼视角）。
输出 PNG 对比图和 GIF 动画，用于论文展示。
"""

import numpy as np
from pathlib import Path


def simulate_camera_capture(subframes: list[np.ndarray], frame_idx: int = 0) -> np.ndarray:
    """返回相机单次曝光捕获的子帧（模拟全局快门）。"""
    return subframes[frame_idx % len(subframes)]


def simulate_eye_integration(subframes: list[np.ndarray]) -> np.ndarray:
    """模拟人眼视觉积分：等权叠加所有子帧，等效于原始图像。"""
    acc = np.zeros_like(subframes[0], dtype=np.float64)
    for sf in subframes:
        acc += sf.astype(np.float64)
    return np.clip(acc / len(subframes), 0, 255).astype(np.uint8)


def simulate_temporal_averaging(subframes: list[np.ndarray], k: int) -> np.ndarray:
    """模拟攻击者叠加 k 帧（时域平均攻击）。"""
    n = len(subframes)
    frames = [subframes[i % n] for i in range(k)]
    acc = np.zeros_like(frames[0], dtype=np.float64)
    for f in frames:
        acc += f.astype(np.float64)
    return np.clip(acc / k, 0, 255).astype(np.uint8)


def make_comparison_grid(
    original: np.ndarray,
    subframes: list[np.ndarray],
    integrated: np.ndarray,
    output_path: str | None = None,
) -> np.ndarray:
    """
    生成对比网格图：
      Row 1: 原始图像 | 积分（人眼）| 对比差图
      Row 2: 子帧 0  | 子帧 1     | 子帧 2 | 子帧 3

    Returns:
        uint8 (H_total, W_total, 3) 对比图
    """
    try:
        import cv2
    except ImportError:
        cv2 = None

    h, w = original.shape[:2]
    pad = 4
    label_h = 24

    def _labeled(img: np.ndarray, text: str) -> np.ndarray:
        canvas = np.zeros((h + label_h + pad, w, 3), dtype=np.uint8)
        canvas[label_h:label_h + h] = img
        if cv2 is not None:
            cv2.putText(canvas, text, (4, label_h - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        return canvas

    # 差异图（放大 4x 便于观察）
    diff = np.abs(original.astype(np.int16) - integrated.astype(np.int16))
    diff_vis = np.clip(diff * 4, 0, 255).astype(np.uint8)

    row1_imgs = [
        _labeled(original, "Original (ground truth)"),
        _labeled(integrated, "Eye integration (n frames)"),
        _labeled(diff_vis, "Difference x4"),
    ]
    row1 = np.concatenate(row1_imgs, axis=1)

    n_show = min(len(subframes), 4)
    row2_imgs = [
        _labeled(subframes[i], f"Subframe {i} (camera view)")
        for i in range(n_show)
    ]
    # 补齐到 3 列宽
    total_w = row1.shape[1]
    sf_w = total_w // n_show
    row2_imgs_resized = []
    for img in row2_imgs:
        if cv2 is not None:
            img = cv2.resize(img, (sf_w, h + label_h + pad))
        row2_imgs_resized.append(img)
    row2 = np.concatenate(row2_imgs_resized, axis=1)[:, :total_w]

    # 补齐高度
    if row2.shape[1] < total_w:
        pad_col = np.zeros((row2.shape[0], total_w - row2.shape[1], 3), dtype=np.uint8)
        row2 = np.concatenate([row2, pad_col], axis=1)

    grid = np.concatenate([row1, row2], axis=0)

    if output_path:
        try:
            from PIL import Image
            Image.fromarray(grid).save(output_path)
            print(f"对比图已保存: {output_path}")
        except Exception as e:
            print(f"保存失败: {e}")

    return grid


def make_animation(
    subframes: list[np.ndarray],
    output_path: str,
    fps: int = 10,
    include_integrated: bool = True,
) -> None:
    """
    生成 GIF 动画展示子帧序列（模拟高频切换效果）。
    末尾插入积分帧展示"人眼感知结果"。
    """
    try:
        from PIL import Image
    except ImportError:
        print("Pillow 未安装，跳过 GIF 生成")
        return

    frames_pil = [Image.fromarray(sf) for sf in subframes]
    if include_integrated:
        integrated = simulate_eye_integration(subframes)
        frames_pil.append(Image.fromarray(integrated))

    duration_ms = int(1000 / fps)
    frames_pil[0].save(
        output_path,
        save_all=True,
        append_images=frames_pil[1:],
        duration=duration_ms,
        loop=0,
    )
    print(f"动画已保存: {output_path}")


def analyze_single_frame_readability(
    original: np.ndarray,
    subframes: list[np.ndarray],
) -> dict:
    """
    定量分析单子帧的可读性（信噪比、边缘保留率）。
    辅助论文中的"相机视角无法识别"论据。
    """
    results = []
    orig_f = original.astype(np.float64)

    for i, sf in enumerate(subframes):
        sf_f = sf.astype(np.float64)

        # PSNR（越低越好：单帧失真越大）
        mse = np.mean((orig_f - sf_f) ** 2)
        psnr = 10 * np.log10(255 ** 2 / mse) if mse > 0 else float("inf")

        # 有效像素比例（非零像素 / 总像素）
        active_ratio = float(np.mean(sf > 0))

        results.append({
            "subframe": i,
            "psnr_db": float(psnr),
            "active_pixel_ratio": active_ratio,
        })

    return {
        "subframes": results,
        "mean_psnr": float(np.mean([r["psnr_db"] for r in results])),
        "mean_active_ratio": float(np.mean([r["active_pixel_ratio"] for r in results])),
    }
