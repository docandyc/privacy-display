"""
子帧合成器

将原始图像帧按掩模分解为 n 个子帧，并施加亮度补偿，
使人眼视觉积分后感知到的亮度与原始图像一致。
"""

import numpy as np
from typing import Sequence


class SubframeComposer:
    def __init__(
        self,
        n: int,
        gamma: float | None = None,
        brightness_factor: float = 1.1,
        insert_inversion: bool = False,
        inversion_alpha: float = 0.3,
        hdr_mode: bool = False,
        peak_nits: float = 1000.0,
        content_peak_nits: float = 100.0,
    ):
        """
        Args:
            n: 子帧数量
            gamma: 亮度补偿系数，None 时自动设为 n * brightness_factor
            brightness_factor: 舒适度修正因子，典型值 1.0-1.2
            insert_inversion: 是否在周期末尾插入反色帧（长曝光防御）
            inversion_alpha: 反色帧时长比例 α ∈ [0.2, 0.5]
            hdr_mode: 启用 HDR 非线性补偿（线性光提升 n 倍 + ICtCp 软裁剪）
            peak_nits: HDR 显示器峰值亮度
            content_peak_nits: SDR 内容白场对应亮度，用于 HDR 积分还原
        """
        self.n = n
        if peak_nits <= 0:
            raise ValueError("peak_nits must be positive")
        if content_peak_nits <= 0:
            raise ValueError("content_peak_nits must be positive")
        self.gamma = gamma if gamma is not None else n * brightness_factor
        self.insert_inversion = insert_inversion
        self.inversion_alpha = inversion_alpha
        self.hdr_mode = hdr_mode
        self.peak_nits = peak_nits
        self.content_peak_nits = content_peak_nits

    def compose(
        self,
        image: np.ndarray,
        masks: Sequence[np.ndarray],
        sub_noises: Sequence[np.ndarray] | None = None,
    ) -> list[np.ndarray]:
        """
        按掩模将 image 分解为 n 个带亮度补偿的子帧。

        Args:
            image: uint8 RGB 图像，shape (H, W, 3)
            masks: n 个 bool 掩模，shape (H, W)
            sub_noises: n 个 float32 子噪声，shape (H, W, 3)，可选

        Returns:
            子帧列表，每帧 uint8 (H, W, 3)
        """
        if image.dtype != np.uint8:
            raise ValueError(f"图像 dtype 须为 uint8，实际为 {image.dtype}")
        if len(masks) != self.n:
            raise ValueError(f"掩模数量须为 {self.n}，实际为 {len(masks)}")
        if sub_noises is not None and len(sub_noises) != self.n:
            raise ValueError(f"子噪声数量须为 {self.n}，实际为 {len(sub_noises)}")

        img_f = image.astype(np.float32)
        subframes = []

        for k, mask in enumerate(masks):
            mask3 = mask[:, :, np.newaxis]  # (H, W, 1) -> broadcast

            # 基础子帧：仅保留分配到该槽位的像素
            sf = img_f * mask3

            # 注入子噪声（若有）
            if sub_noises is not None:
                sf = sf + sub_noises[k]

            if self.hdr_mode:
                # HDR 非线性补偿：sRGB→线性光→提升 n 倍+软裁剪→sRGB
                from src.core.hdr_compensation import (
                    sdr_to_linear, linear_to_sdr, hdr_compensate,
                )
                sf_clip = np.clip(sf, 0, 255)
                linear = sdr_to_linear(sf_clip)
                comp = hdr_compensate(
                    linear,
                    self.n,
                    self.peak_nits,
                    self.content_peak_nits,
                )
                sf = linear_to_sdr(comp)
            else:
                # SDR 亮度补偿：I_k_comp = clip(I_k * gamma, 0, 255)
                sf = np.clip(sf * self.gamma, 0, 255).astype(np.uint8)

            subframes.append(sf)

        return subframes

    def compose_inversion_frame(self, image: np.ndarray) -> np.ndarray:
        """生成反色帧：I_inv(x,y) = 255 - I(x,y)，用于长曝光防御。"""
        return (255 - image.astype(np.int16)).clip(0, 255).astype(np.uint8)

    def compose_partial_inversion_frame(
        self, image: np.ndarray, alpha: float
    ) -> np.ndarray:
        """振幅按 α 缩放的反色帧 α·(255−I)：固定 vsync 回放下复现实时端
        α·Δt 短时全反色的能量等效，避免整帧反色压垮人眼可读性。"""
        arr = float(alpha) * (255.0 - image.astype(np.float32))
        return np.clip(np.rint(arr), 0, 255).astype(np.uint8)

    def compose_black_frame(self, shape: tuple) -> np.ndarray:
        """
        生成全黑帧（交底书 3.2.4 / 5.4 步骤17）。

        用途：(1) 周期末插入使相机自动曝光误判环境亮度→后续帧过曝；
              (2) 帧生成延迟时作应急保护，防止未完成渲染的中间态被捕获。

        Args:
            shape: 帧形状，如 (H, W, 3)
        """
        return np.zeros(shape, dtype=np.uint8)

    def verify_completeness(
        self,
        image: np.ndarray,
        masks: Sequence[np.ndarray],
        sub_noises: Sequence[np.ndarray] | None = None,
        pedestal: float = 0.0,
    ) -> tuple[bool, float]:
        """
        验证完备性：gamma=1 时 ΣI_k ≈ I（像素误差应为 0）。
        含噪声时验证 ΣN_k = 0（若噪声含基底电平，先扣除 n×pedestal）。

        Returns:
            (completeness_ok, max_pixel_error)
        """
        img_f = image.astype(np.float32)
        reconstructed = np.zeros_like(img_f)

        for k, mask in enumerate(masks):
            mask3 = mask[:, :, np.newaxis]
            sf = img_f * mask3
            if sub_noises is not None:
                sf = sf + sub_noises[k]
            reconstructed += sf

        reconstructed -= len(masks) * pedestal
        max_err = float(np.max(np.abs(reconstructed - img_f)))
        return max_err < 1.0, max_err

    def integrate_subframes(
        self,
        subframes: Sequence[np.ndarray],
        boost: float | None = None,
        pedestal: float = 0.0,
    ) -> np.ndarray:
        """
        模拟人眼视觉积分：等权叠加 n 个子帧并施加显示亮度增益。

        物理模型：每个像素仅在 1/n 占空比内点亮，人眼积分得到
        平均亮度 mean(I_k)。硬件通过背光提升（增益 B）或像素空间
        补偿（γ）恢复原始亮度，约束 B·γ = n。因此积分结果为
        integrated = mean(I_k) · (n / γ)。

        γ=1（纯背光提升模型）时 integrated = ΣI_k = I 精确成立；
        γ=n（SDR 像素补偿）时仅对 I < 255/γ 的暗内容无裁剪失真。
        HDR 模式下，子帧数组是“显示峰值归一化”的 SDR 预览：先还原
        到线性峰值归一化亮度，平均后再乘以 peak/content headroom，
        才能模拟真实 HDR 亮度积分。

        Args:
            boost: 显示亮度增益，None 时自动取 n/γ
            pedestal: 子帧基底电平。屏幕无法显示负光，负向噪声在黑像素
                处会被裁剪而破坏 ΣN_k=0；给每个子帧加基底 ε 可避免裁剪，
                积分时在此扣除（代价为黑位抬升约 ε/255 的对比度损失）

        Returns:
            uint8 (H, W, 3) 积分后图像
        """
        if self.hdr_mode:
            from src.core.hdr_compensation import sdr_to_linear, linear_to_sdr

            if boost is None:
                boost = self.peak_nits / self.content_peak_nits
            acc = np.zeros_like(subframes[0], dtype=np.float64)
            for sf in subframes:
                acc += sdr_to_linear(np.clip(sf.astype(np.float32) - pedestal, 0, 255))
            mean = acc / len(subframes)
            return linear_to_sdr(mean * boost)

        if boost is None:
            boost = self.n / self.gamma
        acc = np.zeros_like(subframes[0], dtype=np.float32)
        for sf in subframes:
            acc += sf.astype(np.float32)
        mean = acc / len(subframes) - pedestal
        return np.clip(mean * boost, 0, 255).astype(np.uint8)
