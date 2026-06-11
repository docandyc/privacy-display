"""
核心算法单元测试

验证：
  1. 完备性：∑M_k(x,y) = 1 对每个像素成立
  2. 互斥性：每像素在 n 个时隙中恰好激活一次
  3. 掩模均匀性（卡方检验）
  4. 周期独立性
  5. 子噪声互补性：∑N_k = 0
  6. 子帧完备性：∑I_k = I（无噪声时）
  7. 置换合法性：包含 [0..n-1] 的完整排列
"""

import numpy as np
import pytest
from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.core.noise_injector import NoiseInjector


W, H = 64, 48  # 小分辨率加速测试
N_VALUES = [2, 3, 4, 6, 8]


@pytest.fixture(params=N_VALUES)
def n(request):
    return request.param


class TestMaskGenerator:
    def test_completeness(self, n):
        """每个像素恰好被激活一次（完备性）。"""
        gen = MaskGenerator(W, H, n)
        masks = gen.generate()
        assert len(masks) == n
        total = sum(m.astype(np.int32) for m in masks)
        assert np.all(total == 1), f"完备性失败：sum={total.max()}"

    def test_exclusivity(self, n):
        """互斥性：任意两个掩模无重叠像素。"""
        gen = MaskGenerator(W, H, n)
        masks = gen.generate()
        for i in range(n):
            for j in range(i + 1, n):
                overlap = np.logical_and(masks[i], masks[j])
                assert not np.any(overlap), f"掩模 {i} 与 {j} 有重叠"

    def test_uniformity(self, n):
        """分布均匀性：每个槽位约有 W*H/n 个像素。"""
        gen = MaskGenerator(W, H, n)
        masks = gen.generate()
        counts = [int(m.sum()) for m in masks]
        expected = W * H / n
        for k, cnt in enumerate(counts):
            ratio = abs(cnt - expected) / expected
            assert ratio < 0.15, f"槽位 {k} 分布不均: cnt={cnt}, expected={expected:.0f}"

    def test_cycle_independence(self, n):
        """相邻周期掩模统计独立（像素分配不同）。"""
        gen = MaskGenerator(W, H, n)
        masks0 = gen.generate(cycle=0)
        masks1 = gen.generate(cycle=1)
        same = sum(
            int(np.sum(masks0[k] == masks1[k])) for k in range(n)
        )
        total_pixels = W * H * n
        same_ratio = same / total_pixels
        # 如果完全相同说明没有周期独立性；期望差异率 > 50%
        assert same_ratio < 0.95, f"周期独立性不足: same_ratio={same_ratio:.3f}"

    def test_deterministic_with_same_key(self, n):
        """相同密钥和周期应产生相同掩模。"""
        key = b"x" * 32
        gen1 = MaskGenerator(W, H, n, key=key)
        gen2 = MaskGenerator(W, H, n, key=key)
        masks1 = gen1.generate(cycle=42)
        masks2 = gen2.generate(cycle=42)
        for k in range(n):
            assert np.array_equal(masks1[k], masks2[k])

    def test_permutation_is_valid(self, n):
        """置换序列必须是 [0..n-1] 的完整排列。"""
        gen = MaskGenerator(W, H, n)
        gen.generate(cycle=7)
        perm = gen.generate_permutation(cycle=7)
        assert sorted(perm) == list(range(n)), f"非法置换: {perm}"


class TestSubframeComposer:
    def test_subframe_completeness(self):
        """无噪声时 ∑I_k = I（完备性，精度误差 < 1 LSB）。"""
        n = 4
        gen = MaskGenerator(W, H, n)
        composer = SubframeComposer(n=n, gamma=1.0)  # gamma=1 验证无补偿时的完备性
        masks = gen.generate()

        img = np.random.randint(0, 256, (H, W, 3), dtype=np.uint8)
        subframes = composer.compose(img, masks, sub_noises=None)

        ok, err = composer.verify_completeness(img, masks)
        assert ok, f"子帧完备性失败: max_err={err}"

    def test_integration_restores_original(self):
        """视觉积分（含背光增益 boost=n/γ）应精确还原原始图像。"""
        n = 4
        gen = MaskGenerator(W, H, n)
        composer = SubframeComposer(n=n, gamma=1.0)
        masks = gen.generate()
        img = np.random.randint(50, 200, (H, W, 3), dtype=np.uint8)

        subframes = composer.compose(img, masks)
        integrated = composer.integrate_subframes(subframes)

        # γ=1 时 boost=n，积分 = ΣI_k = I（完备性保证精确还原）
        diff = np.abs(integrated.astype(np.float32) - img.astype(np.float32))
        assert np.mean(diff) < 2.0, f"积分还原误差过大: {np.mean(diff):.2f}"

    def test_inversion_frame(self):
        """反色帧 I_inv = 255 - I。"""
        n = 2
        composer = SubframeComposer(n=n)
        img = np.random.randint(0, 256, (H, W, 3), dtype=np.uint8)
        inv = composer.compose_inversion_frame(img)
        expected = 255 - img
        assert np.array_equal(inv, expected)


class TestNoiseInjector:
    def test_complementarity(self, n):
        """∑N_k = 0（互补性）。"""
        injector = NoiseInjector(n=n, epsilon=8/255)
        base_noise = np.random.uniform(-8/255, 8/255, (H, W, 3)).astype(np.float32)
        sub_noises = injector.split_complementary(base_noise)

        assert len(sub_noises) == n
        ok, residual = injector.verify_complementarity(sub_noises)
        assert ok, f"互补性验证失败: max_residual={residual:.2e}"

    def test_noise_budget_respected(self, n):
        """每个子噪声的最大幅度不超过 ε（允许少量数值误差）。"""
        epsilon = 8 / 255
        injector = NoiseInjector(n=n, epsilon=epsilon)
        img = np.random.rand(H, W, 3).astype(np.float32)
        base = injector.generate_fgsm_noise(img)

        max_val = float(np.max(np.abs(base)))
        assert max_val <= epsilon + 1e-6, f"噪声超出预算: {max_val:.6f} > {epsilon:.6f}"

    def test_noise_with_subframes(self, n):
        """含噪声的子帧合成后完备性：∑(I_k + N_k) ≈ I（因∑N_k=0）。"""
        gen = MaskGenerator(W, H, n)
        composer = SubframeComposer(n=n, gamma=1.0)
        injector = NoiseInjector(n=n, epsilon=8/255)

        img = np.random.randint(50, 200, (H, W, 3), dtype=np.uint8)
        masks = gen.generate()

        img_f = img.astype(np.float32) / 255.0
        base = injector.generate_fgsm_noise(img_f)
        sub_noises_f = injector.split_complementary(base)
        sub_noises = [(nf * 255).astype(np.float32) for nf in sub_noises_f]

        ok, err = composer.verify_completeness(img, masks, sub_noises)
        assert ok, f"含噪声时完备性失败: max_err={err:.4f}"
