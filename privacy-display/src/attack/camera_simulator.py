"""
相机攻击模拟器

模拟不同类型的相机采样策略，验证各种攻击场景下的防御效果：
  - 全局快门单帧捕获
  - 卷帘快门混合采样
  - 时域平均攻击（多帧叠加）
  - 长曝光积分攻击
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class CameraParams:
    shutter_type: str = "global"    # "global" 或 "rolling"
    frame_rate: float = 30.0        # 相机帧率（fps）
    exposure_time: float = 1 / 60   # 曝光时间（秒）
    readout_time: float = 15e-6     # 卷帘快门逐行扫描时间（秒/行）


class CameraSimulator:
    def __init__(self, params: CameraParams | None = None):
        self.params = params or CameraParams()

    # ------------------------------------------------------------------
    # 全局快门模拟
    # ------------------------------------------------------------------

    def capture_global_shutter(
        self,
        subframes: list[np.ndarray],
        display_rate: float,
        capture_offset: float = 0.0,
    ) -> np.ndarray:
        """
        全局快门：在曝光时刻捕获单个子帧。

        Args:
            subframes: 按时序排列的子帧列表
            display_rate: 显示刷新率（Hz）
            capture_offset: 相机触发时刻相对周期开始的偏移（秒）

        Returns:
            捕获到的单帧（对应某一子帧）
        """
        delta_t = 1.0 / display_rate
        idx = int(capture_offset / delta_t) % len(subframes)
        return subframes[idx].copy()

    def capture_global_shutter_random(
        self, subframes: list[np.ndarray]
    ) -> np.ndarray:
        """在随机时刻触发全局快门（模拟智能眼镜随机抽帧）。"""
        idx = np.random.randint(len(subframes))
        return subframes[idx].copy()

    # ------------------------------------------------------------------
    # 卷帘快门模拟
    # ------------------------------------------------------------------

    def capture_rolling_shutter(
        self,
        subframes: list[np.ndarray],
        display_rate: float,
        switch_time: float | None = None,
    ) -> np.ndarray:
        """
        卷帘快门：逐行曝光，在曝光期间子帧可能切换，
        导致单帧内出现水平分割的混合片段。

        Args:
            subframes: 子帧序列
            display_rate: 显示刷新率（Hz）
            switch_time: 子帧切换时刻（相对帧开始，秒）

        Returns:
            混合了多子帧片段的"卷帘帧"
        """
        h, w = subframes[0].shape[:2]
        delta_t = 1.0 / display_rate
        readout = self.params.readout_time * h  # 全帧卷帘总时间

        if switch_time is None:
            # 随机选一个切换时刻
            switch_time = np.random.uniform(0, delta_t)

        result = np.zeros_like(subframes[0], dtype=np.float32)
        n = len(subframes)

        for y in range(h):
            row_t = y * readout / h  # 第 y 行的曝光开始时刻
            # 判断该行曝光期间经历哪个子帧
            sf_idx = int(row_t / delta_t) % n
            result[y] = subframes[sf_idx][y].astype(np.float32)

        return result.clip(0, 255).astype(np.uint8)

    def count_contaminated_rows(
        self, h: int, display_rate: float, switch_time: float
    ) -> int:
        """
        计算卷帘快门下被"污染"（跨子帧边界）的行数。
        对应交底书 7.1 节的 N_row 计算。
        """
        delta_t = 1.0 / display_rate
        readout = self.params.readout_time * h

        contaminated = 0
        for y in range(h):
            row_start = y * readout / h
            row_end = row_start + self.params.exposure_time
            # 跨越子帧边界的行被污染
            sf_start = int(row_start / delta_t)
            sf_end = int(row_end / delta_t)
            if sf_start != sf_end:
                contaminated += 1
        return contaminated

    # ------------------------------------------------------------------
    # 时域平均攻击（多帧叠加）
    # ------------------------------------------------------------------

    def temporal_averaging_attack(
        self,
        subframes: list[np.ndarray],
        k: int,
        randomize_order: bool = True,
    ) -> np.ndarray:
        """
        攻击者采集 k 帧后做时域平均，尝试重构原始图像。

        Args:
            subframes: 可用子帧序列
            k: 叠加帧数
            randomize_order: 是否随机选取帧（True 更真实）

        Returns:
            平均后图像
        """
        n = len(subframes)
        if randomize_order:
            indices = [np.random.randint(n) for _ in range(k)]
        else:
            indices = [i % n for i in range(k)]

        frames = [subframes[i] for i in indices]
        stacked = np.mean(
            [f.astype(np.float64) for f in frames], axis=0
        )
        return stacked.clip(0, 255).astype(np.uint8)

    # ------------------------------------------------------------------
    # 长曝光攻击
    # ------------------------------------------------------------------

    def long_exposure_attack(
        self,
        subframes: list[np.ndarray],
        inversion_frames: list[np.ndarray] | None = None,
        n_cycles: int = 4,
    ) -> np.ndarray:
        """
        长曝光积分攻击：模拟相机使用长曝光时间采集多个完整周期。

        若插入了反色帧，积分结果趋向中性灰（防御有效）。

        Args:
            subframes: 一个周期的子帧
            inversion_frames: 反色帧列表（None 表示未插入）
            n_cycles: 采集周期数

        Returns:
            长曝光积分图像
        """
        all_frames = []
        for _ in range(n_cycles):
            all_frames.extend(subframes)
            if inversion_frames:
                all_frames.extend(inversion_frames)

        integrated = np.mean(
            [f.astype(np.float64) for f in all_frames], axis=0
        )
        return integrated.clip(0, 255).astype(np.uint8)

    # ------------------------------------------------------------------
    # 自动曝光（AE）攻击模型
    # ------------------------------------------------------------------

    def auto_exposure_attack(
        self,
        frame_sequence: list[np.ndarray],
        target_luminance: float = 110.0,
        ae_speed: float = 0.3,
        gain_limits: tuple = (0.25, 8.0),
    ) -> list[np.ndarray]:
        """
        模拟相机自动曝光（AE）增益自适应。

        交底书 3.2.4：插入黑帧使相机 AE 误判环境亮度（observed 偏低）→
        提高增益 → 后续真实子帧被过曝饱和，OCR 失效。本函数复现该机制：
        AE 依据近期帧平均亮度反馈调整增益，黑帧拉低 observed_lum 推高增益。

        Args:
            frame_sequence: 相机依次看到的帧（可含黑帧/反色帧）
            target_luminance: AE 目标平均亮度（0-255）
            ae_speed: AE 收敛速度 ∈ (0,1]，越大越快
            gain_limits: 增益钳位 (min, max)

        Returns:
            经 AE 增益作用后的帧序列（过曝/欠曝体现在像素饱和）
        """
        gain = 1.0
        out = []
        gmin, gmax = gain_limits

        for frame in frame_sequence:
            # 当前帧在当前增益下的实际观测亮度
            observed = float(np.mean(frame.astype(np.float32) * gain))
            applied = np.clip(frame.astype(np.float32) * gain, 0, 255).astype(np.uint8)
            out.append(applied)

            # AE 反馈：observed 偏离 target 则调整增益（一阶收敛）
            if observed > 1e-3:
                desired_gain = gain * target_luminance / observed
            else:
                desired_gain = gmax  # 全黑帧 → AE 拉到最大增益
            gain = (1 - ae_speed) * gain + ae_speed * desired_gain
            gain = float(np.clip(gain, gmin, gmax))

        return out

    # ------------------------------------------------------------------
    # 综合攻击效果报告
    # ------------------------------------------------------------------

    def full_attack_report(
        self,
        original: np.ndarray,
        subframes: list[np.ndarray],
        inversion_frames: list[np.ndarray] | None,
        display_rate: float,
        ocr_evaluator=None,
        ground_truth: str = "",
    ) -> dict:
        """
        运行所有攻击场景，返回综合报告。
        """
        h, w = original.shape[:2]

        attacks = {
            "global_shutter_single": self.capture_global_shutter_random(subframes),
            "rolling_shutter": self.capture_rolling_shutter(subframes, display_rate),
            "temporal_avg_4": self.temporal_averaging_attack(subframes, 4),
            "temporal_avg_8": self.temporal_averaging_attack(subframes, 8),
            "temporal_avg_16": self.temporal_averaging_attack(subframes, 16),
            "long_exposure_no_inv": self.long_exposure_attack(subframes, None, 4),
        }
        if inversion_frames:
            attacks["long_exposure_with_inv"] = self.long_exposure_attack(
                subframes, inversion_frames, 4
            )

        results = {}
        for attack_name, frame in attacks.items():
            entry: dict = {}

            # PSNR（与原始图像的相似度，越低说明防御越好）
            mse = np.mean((original.astype(float) - frame.astype(float)) ** 2)
            entry["psnr_db"] = float(10 * np.log10(255**2 / mse)) if mse > 0 else 99.0

            # OCR 准确率（若提供了评估器）
            if ocr_evaluator and ground_truth:
                try:
                    ocr_result = ocr_evaluator.evaluate_single(
                        frame, ground_truth, "tesseract"
                    )
                    entry["char_accuracy"] = ocr_result.char_accuracy
                except Exception:
                    entry["char_accuracy"] = -1.0

            results[attack_name] = entry

        return {
            "display_rate_hz": display_rate,
            "n_subframes": len(subframes),
            "attacks": results,
        }
