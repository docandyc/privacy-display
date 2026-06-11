"""
评估指标单元测试
"""

import numpy as np
import pytest
from src.evaluation.metrics import (
    compute_fpi, fpi_is_safe,
    compute_entropy, compute_entropy_ratio,
    compute_brightness_uniformity,
)


class TestFPI:
    def test_safe_at_240hz_n4(self):
        fpi = compute_fpi(240, 4)
        assert fpi_is_safe(fpi), f"240Hz n=4 应安全，但 FPI={fpi:.4f}"

    def test_safe_at_144hz_n2(self):
        fpi = compute_fpi(144, 2)
        assert fpi_is_safe(fpi), f"144Hz n=2 应安全，但 FPI={fpi:.4f}"

    def test_unsafe_at_60hz_n4(self):
        fpi = compute_fpi(60, 4)
        assert not fpi_is_safe(fpi), f"60Hz n=4 应不安全（有闪烁），但 FPI={fpi:.4f}"

    def test_higher_refresh_lower_fpi(self):
        fpi_144 = compute_fpi(144, 2)
        fpi_240 = compute_fpi(240, 2)
        assert fpi_240 < fpi_144, "更高刷新率应产生更低 FPI"


class TestEntropy:
    def test_uniform_image_max_entropy(self):
        """均匀分布图像熵接近 8 bits。"""
        img = np.arange(256, dtype=np.uint8).repeat(4).reshape(32, 32)
        img3 = np.stack([img] * 3, axis=-1)
        h = compute_entropy(img3)
        assert h > 7.0, f"均匀图像熵应接近 8，实际 {h:.2f}"

    def test_constant_image_zero_entropy(self):
        """常数图像熵为 0。"""
        img = np.full((32, 32, 3), 128, dtype=np.uint8)
        h = compute_entropy(img)
        assert h < 0.01, f"常数图像熵应为 0，实际 {h:.4f}"

    def test_subframe_lower_entropy(self):
        """子帧（仅含 1/n 像素）熵低于原始图像。"""
        from src.core.mask_generator import MaskGenerator
        from src.core.subframe_composer import SubframeComposer

        n, W, H = 4, 128, 96
        img = np.random.randint(50, 200, (H, W, 3), dtype=np.uint8)
        gen = MaskGenerator(W, H, n)
        composer = SubframeComposer(n=n, gamma=1.0)
        masks = gen.generate()
        subframes = composer.compose(img, masks)

        ratio = compute_entropy_ratio(subframes[0], img)
        assert ratio < 0.7, f"子帧熵比应明显低于 1，实际 {ratio:.3f}"


class TestUniformity:
    def test_uniform_brightness(self):
        """均匀纯色图像的亮度均匀性应接近 0。"""
        img = np.full((120, 160, 3), 100, dtype=np.uint8)
        u = compute_brightness_uniformity(img)
        assert u < 0.01, f"纯色图亮度均匀性应接近 0，实际 {u:.4f}"

    def test_nonuniform_brightness(self):
        """半亮半暗图像均匀性应较差。"""
        img = np.zeros((120, 160, 3), dtype=np.uint8)
        img[:, :80] = 200
        img[:, 80:] = 20
        u = compute_brightness_uniformity(img)
        assert u > 0.3, f"非均匀图亮度不均性应较大，实际 {u:.4f}"
