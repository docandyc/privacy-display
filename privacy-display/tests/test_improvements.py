"""
改进项单元测试（A1-A4, B1-B3, C1-C4）
"""

import numpy as np
import pytest

from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer


# ------------------------------------------------------------------
# A1 HDR 亮度补偿
# ------------------------------------------------------------------
class TestHDR:
    def test_pq_roundtrip(self):
        from src.core.hdr_compensation import pq_encode, pq_decode
        L = np.array([0.0, 1.0, 50.0, 100.0, 1000.0, 4000.0, 10000.0])
        rt = pq_decode(pq_encode(L))
        assert np.max(np.abs(rt - L)) < 1e-3

    def test_ictcp_roundtrip(self):
        from src.core.hdr_compensation import rgb_to_ictcp, ictcp_to_rgb
        rgb = np.random.rand(50, 3)
        rt = ictcp_to_rgb(rgb_to_ictcp(rgb))
        assert np.max(np.abs(rt - rgb)) < 1e-6

    def test_hdr_compensate_in_range(self):
        from src.core.hdr_compensation import hdr_compensate, sdr_to_linear
        img = np.random.randint(0, 256, (16, 16, 3), dtype=np.uint8)
        comp = hdr_compensate(sdr_to_linear(img), n=4)
        assert comp.min() >= 0 and comp.max() <= 1.0

    def test_hdr_mode_compose_runs(self):
        n = 4
        gen = MaskGenerator(32, 24, n)
        composer = SubframeComposer(n=n, hdr_mode=True, peak_nits=1000)
        img = np.random.randint(0, 256, (24, 32, 3), dtype=np.uint8)
        sfs = composer.compose(img, gen.generate(0))
        assert len(sfs) == n and all(s.dtype == np.uint8 for s in sfs)


# ------------------------------------------------------------------
# A2 黑帧 + 自动曝光攻击
# ------------------------------------------------------------------
class TestBlackFrameAE:
    def test_black_frame_all_zero(self):
        composer = SubframeComposer(n=4)
        bf = composer.compose_black_frame((10, 10, 3))
        assert np.all(bf == 0) and bf.shape == (10, 10, 3)

    def test_ae_overexposes_after_black(self):
        from src.attack.camera_simulator import CameraSimulator
        cam = CameraSimulator()
        # 正常帧 → 黑帧 → 正常帧：AE 应在黑帧后推高增益使后续帧变亮
        seq = [np.full((8, 8, 3), 100, np.uint8),
               np.zeros((8, 8, 3), np.uint8),
               np.full((8, 8, 3), 100, np.uint8)]
        out = cam.auto_exposure_attack(seq, ae_speed=0.8)
        assert out[2].mean() > out[0].mean(), "黑帧后 AE 增益上升应使后续帧更亮"

    def test_emergency_black_frame_decision(self):
        from src.core.timing_controller import TimingController
        tc = TimingController(refresh_rate=240, n=4)
        assert tc.should_emit_black_frame(render_ready=False, time_to_vblank_ms=2.0)
        assert tc.should_emit_black_frame(render_ready=True, time_to_vblank_ms=0.1)
        assert not tc.should_emit_black_frame(render_ready=True, time_to_vblank_ms=2.0)
        assert tc.black_frame_count == 2

    def test_external_vblank_advances_timing_token(self):
        from src.core.timing_controller import TimingController
        seen = []
        tc = TimingController(
            refresh_rate=240,
            n=3,
            on_subframe=lambda cycle, idx: seen.append((cycle, idx)),
        )
        tc.set_permutation(7, [2, 0, 1])

        assert tc.advance_on_vblank() == (7, 2)
        assert tc.advance_on_vblank() == (7, 0)
        assert tc.advance_on_vblank() == (7, 1)
        assert tc.get_token().cycle == 8
        assert seen == [(7, 2), (7, 0), (7, 1)]


# ------------------------------------------------------------------
# A3 多显示器同步
# ------------------------------------------------------------------
class TestMultiDisplay:
    def test_homogeneous_within_tolerance(self):
        from src.core.multi_display import MultiDisplaySync, DisplayNode
        sync = MultiDisplaySync([
            DisplayNode("A", 240, 4, is_master=True),
            DisplayNode("B", 240, 4),
        ])
        err = sync.simulate_vblank_broadcast(n_vblanks=200)
        assert err["B"]["within_tolerance"], "同刷新率应 <0.1ms"

    def test_heterogeneous_virtual_clock(self):
        from src.core.multi_display import MultiDisplaySync, DisplayNode
        sync = MultiDisplaySync([
            DisplayNode("A", 240, 4, is_master=True),
            DisplayNode("B", 144, 4),
        ])
        assert sync.virtual_clock_hz == 720  # LCM(240,144)
        err = sync.simulate_vblank_broadcast()
        assert err["B"]["heterogeneous"] is True

    def test_no_full_frame_leak(self):
        from src.core.multi_display import MultiDisplaySync, DisplayNode
        sync = MultiDisplaySync([DisplayNode("A", 240, 4, is_master=True)])
        sched = sync.generate_schedule(50)
        # 短曝光（<周期16.7ms）无泄露；长曝光（>周期）有泄露
        assert sync.verify_no_full_frame_leak(sched, 5.0)
        assert not sync.verify_no_full_frame_leak(sched, 20.0)


# ------------------------------------------------------------------
# B3 视角差异化掩模
# ------------------------------------------------------------------
class TestViewMask:
    def test_completeness_preserved(self):
        n = 4
        gen = MaskGenerator(96, 96, n)
        masks = gen.generate_view_differentiated(cycle=0, regions=(3, 3))
        total = sum(m.astype(int) for m in masks)
        assert np.all(total == 1), "视角差异化掩模仍须满足全屏完备性"

    def test_regions_differ(self):
        n = 4
        gen = MaskGenerator(96, 96, n)
        masks = gen.generate_view_differentiated(cycle=0, regions=(3, 3))
        # 左上区域与右下区域的掩模模式应不同（区域独立种子）
        top_left = masks[0][:32, :32]
        bot_right = masks[0][64:, 64:]
        # 不应完全相同（极小概率巧合）
        assert not np.array_equal(top_left, bot_right)


# ------------------------------------------------------------------
# B2 重构攻击
# ------------------------------------------------------------------
class TestReconstruction:
    def test_max_stack_recovers_no_noise(self):
        """无噪声掩模方案：max 堆叠应精确重构（暴露完整周期采集的脆弱性）。"""
        from src.attack.reconstruction_attack import reconstruct_max_stack
        n = 4
        gen = MaskGenerator(48, 48, n)
        composer = SubframeComposer(n=n, gamma=1.0)
        img = np.random.randint(10, 250, (48, 48, 3), dtype=np.uint8)
        masks = gen.generate(0)
        subframes = composer.compose(img, masks, None)  # 无噪声
        recon = reconstruct_max_stack(subframes)
        # 每像素恰被一个子帧点亮，max 恢复原值
        assert np.mean(np.abs(recon.astype(int) - img.astype(int))) < 1.0

    def test_inpaint_single_weak(self):
        """单帧 inpainting：缺失 3/4 像素，重构质量应远低于完整堆叠。"""
        from src.attack.reconstruction_attack import (
            reconstruct_inpaint_single, reconstruct_max_stack)
        from src.evaluation.metrics import compute_ssim
        n = 4
        gen = MaskGenerator(48, 48, n)
        composer = SubframeComposer(n=n, gamma=1.0)
        img = np.random.randint(10, 250, (48, 48, 3), dtype=np.uint8)
        masks = gen.generate(0)
        subframes = composer.compose(img, masks, None)
        ssim_single = compute_ssim(img, reconstruct_inpaint_single(subframes[0]))
        ssim_full = compute_ssim(img, reconstruct_max_stack(subframes))
        assert ssim_single < ssim_full


# ------------------------------------------------------------------
# C1 掩模取模偏置修复（拒绝采样）
# ------------------------------------------------------------------
class TestModuloBias:
    @pytest.mark.parametrize("n", [3, 5, 6, 7])
    def test_no_bias_non_power_of_two(self, n):
        """非 2 的幂的 n：拒绝采样后各槽位计数应高度均匀（无系统偏置）。"""
        gen = MaskGenerator(200, 200, n)
        R = gen._generate_index_matrix(cycle=12345)
        counts = np.bincount(R.ravel(), minlength=n)
        expected = R.size / n
        max_dev = np.max(np.abs(counts - expected)) / expected
        assert max_dev < 0.05, f"n={n} 偏差 {max_dev:.3f} 过大"

    def test_values_in_range(self):
        for n in [2, 3, 4, 5, 8, 16]:
            gen = MaskGenerator(64, 64, n)
            R = gen._generate_index_matrix(cycle=1)
            assert R.min() >= 0 and R.max() < n


# ------------------------------------------------------------------
# C3 SSIM + 运动模糊
# ------------------------------------------------------------------
class TestSSIM:
    def test_identical_ssim_one(self):
        from src.evaluation.metrics import compute_ssim
        img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        assert abs(compute_ssim(img, img) - 1.0) < 1e-6

    def test_integrated_high_ssim(self):
        """积分帧 vs 原图 SSIM 应接近 1（视觉无损）。"""
        from src.evaluation.metrics import compute_ssim
        n = 4
        gen = MaskGenerator(64, 64, n)
        composer = SubframeComposer(n=n, gamma=1.0)
        img = np.random.randint(30, 220, (64, 64, 3), dtype=np.uint8)
        masks = gen.generate(0)
        subframes = composer.compose(img, masks, None)
        integrated = composer.integrate_subframes(subframes)
        assert compute_ssim(img, integrated) > 0.98

    def test_motion_blur_width(self):
        from src.evaluation.metrics import compute_motion_blur_width
        n = 4
        # 构造一个有清晰垂直边缘的子帧序列
        base = np.zeros((32, 64, 3), dtype=np.uint8)
        base[:, 32:] = 200
        subframes = [base.copy() for _ in range(n)]
        result = compute_motion_blur_width(subframes, velocity_px=0.0)
        # 零速度时无额外模糊
        assert result["increase_pct"] < 50.0
