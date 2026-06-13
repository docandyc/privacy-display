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

        if switch_time is None:
            # 相机帧起点相对显示子帧周期的相位
            switch_time = np.random.uniform(0, delta_t)

        result = np.zeros_like(subframes[0], dtype=np.float32)

        for y in range(h):
            row_start = switch_time + y * self.params.readout_time
            row_end = row_start + self.params.exposure_time
            weights = self._exposure_weights(
                row_start,
                row_end,
                display_rate,
                len(subframes),
            )
            for sf_idx, weight in enumerate(weights):
                if weight > 0:
                    result[y] += subframes[sf_idx][y].astype(np.float32) * weight

        return result.clip(0, 255).astype(np.uint8)

    @staticmethod
    def _exposure_weights(
        start_time: float,
        end_time: float,
        display_rate: float,
        n_subframes: int,
    ) -> np.ndarray:
        """
        计算曝光窗口与各显示子帧的时间重叠比例。

        对应交底书 7.1：一行曝光窗口可能跨过多个子帧切换边界，
        捕获值应按重叠时间做线性积分，而不是只取某一个子帧。
        """
        if end_time <= start_time:
            idx = int(np.floor(start_time * display_rate)) % n_subframes
            weights = np.zeros(n_subframes, dtype=np.float32)
            weights[idx] = 1.0
            return weights

        interval = 1.0 / display_rate
        total = end_time - start_time
        weights = np.zeros(n_subframes, dtype=np.float64)
        cursor = start_time
        guard = 0

        while cursor < end_time and guard < 10000:
            absolute_idx = int(np.floor(cursor / interval))
            next_boundary = (absolute_idx + 1) * interval
            segment_end = min(end_time, next_boundary)
            overlap = max(0.0, segment_end - cursor)
            weights[absolute_idx % n_subframes] += overlap
            if segment_end <= cursor:
                break
            cursor = segment_end
            guard += 1

        if weights.sum() <= 0:
            idx = int(np.floor(start_time / interval)) % n_subframes
            weights[idx] = total
        return (weights / total).astype(np.float32)

    def count_contaminated_rows(
        self, h: int, display_rate: float, switch_time: float
    ) -> int:
        """
        计算卷帘快门下被"污染"（跨子帧边界）的行数。
        对应交底书 7.1 节的 N_row 计算。
        """
        interval = 1.0 / display_rate
        contaminated = 0
        for y in range(h):
            row_start = switch_time + y * self.params.readout_time
            row_end = row_start + self.params.exposure_time
            sf_start = int(np.floor(row_start / interval))
            sf_end = int(np.floor(np.nextafter(row_end, row_start) / interval))
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

    def phase_search_recovery_attack(
        self,
        frame_sequence: list[np.ndarray],
        window_size: int | None = None,
        method: str = "mean",
        restore_brightness: bool = True,
    ) -> tuple[np.ndarray, dict]:
        """
        强相机攻击者的相位搜索重构。

        屏幕-相机通信文献里的解码器通常不会假设已知帧边界，而是先在视频流
        中搜索同步相位。本攻击模拟同样能力：攻击者知道一个完整保护周期包含
        `window_size` 个输出槽，但不知道周期起点，于是枚举所有连续窗口，选择
        对比度/边缘能量最高的重构结果。

        Args:
            frame_sequence: 连续采集到的屏幕帧
            window_size: 一个候选完整周期的帧数；None 时使用全部帧
            method: "mean"、"max" 或 "median"
            restore_brightness: mean/median 会因时间平均变暗，是否按窗口长度放大

        Returns:
            (best_frame, metadata)
        """
        if not frame_sequence:
            raise ValueError("frame_sequence must not be empty")
        if window_size is None:
            window_size = len(frame_sequence)
        if window_size <= 0 or window_size > len(frame_sequence):
            raise ValueError("window_size must be in [1, len(frame_sequence)]")
        if method not in {"mean", "max", "median"}:
            raise ValueError("method must be one of {'mean', 'max', 'median'}")

        best_frame = None
        best_score = -1.0
        best_offset = 0
        best_metrics: dict = {}

        for offset in range(0, len(frame_sequence) - window_size + 1):
            window = frame_sequence[offset:offset + window_size]
            candidate = self._combine_frames(
                window,
                method=method,
                restore_brightness=restore_brightness,
            )
            score, metrics = self._reconstruction_score(candidate)
            if score > best_score:
                best_frame = candidate
                best_score = score
                best_offset = offset
                best_metrics = metrics

        assert best_frame is not None  # for type checkers
        metadata = {
            "attack": "phase_search_recovery",
            "method": method,
            "window_size": int(window_size),
            "best_offset": int(best_offset),
            "score": float(best_score),
            **best_metrics,
        }
        return best_frame, metadata

    def weighted_differential_accumulator_attack(
        self,
        frame_sequence: list[np.ndarray],
        channel: str = "luma",
        normalize: bool = True,
    ) -> tuple[np.ndarray, dict]:
        """
        屏幕-相机通信式差分累加攻击。

        DeepLight/Revelio/BRIGHTNESS 一类工作说明：相机可以从人眼不明显的
        时域亮度/颜色变化中恢复信号。该攻击不直接平均帧，而是累加相邻帧
        差分，突出稳定内容边界和周期性调制痕迹；`channel="blue"` 用于检查
        蓝通道是否形成可被相机利用的侧信道。
        """
        if len(frame_sequence) < 2:
            raise ValueError("frame_sequence must contain at least two frames")
        if channel not in {"luma", "red", "green", "blue"}:
            raise ValueError("channel must be one of {'luma', 'red', 'green', 'blue'}")

        planes = [self._select_channel(frame, channel) for frame in frame_sequence]
        accum = np.zeros_like(planes[0], dtype=np.float32)
        total_weight = 0.0
        for prev, cur in zip(planes, planes[1:]):
            diff = cur.astype(np.float32) - prev.astype(np.float32)
            weight = float(np.std(cur) + np.std(prev) + 1e-6)
            accum += np.abs(diff) * weight
            total_weight += weight

        if total_weight > 0:
            accum /= total_weight
        if normalize:
            accum = self._normalize_plane(accum)
        else:
            accum = np.clip(accum, 0, 255)

        frame = np.repeat(accum[..., None], 3, axis=2).astype(np.uint8)
        score, metrics = self._reconstruction_score(frame)
        metadata = {
            "attack": "weighted_differential_accumulator",
            "channel": channel,
            "frames": len(frame_sequence),
            "score": float(score),
            **metrics,
        }
        return frame, metadata

    def channel_selective_recovery_attack(
        self,
        frame_sequence: list[np.ndarray],
        channel: str = "blue",
        method: str = "max",
    ) -> tuple[np.ndarray, dict]:
        """
        单通道恢复攻击。

        屏幕-相机通信方案常利用人眼对不同颜色通道的敏感度差异。防御端若
        在某一通道上留下更稳定的残差信息，相机可只用该通道做重构。
        """
        if not frame_sequence:
            raise ValueError("frame_sequence must not be empty")
        if channel not in {"luma", "red", "green", "blue"}:
            raise ValueError("channel must be one of {'luma', 'red', 'green', 'blue'}")
        if method not in {"mean", "max", "median"}:
            raise ValueError("method must be one of {'mean', 'max', 'median'}")

        planes = [self._select_channel(frame, channel) for frame in frame_sequence]
        stack = np.stack([p.astype(np.float32) for p in planes], axis=0)
        if method == "mean":
            recovered = np.mean(stack, axis=0)
        elif method == "max":
            recovered = np.max(stack, axis=0)
        else:
            recovered = np.median(stack, axis=0)
        recovered = self._normalize_plane(recovered)
        frame = np.repeat(recovered[..., None], 3, axis=2).astype(np.uint8)
        score, metrics = self._reconstruction_score(frame)
        metadata = {
            "attack": "channel_selective_recovery",
            "channel": channel,
            "method": method,
            "frames": len(frame_sequence),
            "score": float(score),
            **metrics,
        }
        return frame, metadata

    def screen_camera_attack_suite(
        self,
        frame_sequence: list[np.ndarray],
        cycle_length: int,
    ) -> dict:
        """
        运行一组屏幕-相机通信启发的强攻击基线。

        返回的帧可继续交给 OCR/VLM/SSIM 评估；metadata 记录窗口、通道与
        重构分数，便于写论文中的攻击矩阵。
        """
        if cycle_length <= 0:
            raise ValueError("cycle_length must be positive")
        attacks: dict[str, dict] = {}

        phase_mean, phase_mean_meta = self.phase_search_recovery_attack(
            frame_sequence,
            window_size=min(cycle_length, len(frame_sequence)),
            method="mean",
            restore_brightness=True,
        )
        phase_max, phase_max_meta = self.phase_search_recovery_attack(
            frame_sequence,
            window_size=min(cycle_length, len(frame_sequence)),
            method="max",
            restore_brightness=False,
        )
        diff_luma, diff_luma_meta = self.weighted_differential_accumulator_attack(
            frame_sequence,
            channel="luma",
        )
        diff_blue, diff_blue_meta = self.weighted_differential_accumulator_attack(
            frame_sequence,
            channel="blue",
        )
        blue_max, blue_max_meta = self.channel_selective_recovery_attack(
            frame_sequence,
            channel="blue",
            method="max",
        )

        for name, frame, meta in [
            ("phase_search_mean", phase_mean, phase_mean_meta),
            ("phase_search_max", phase_max, phase_max_meta),
            ("differential_luma", diff_luma, diff_luma_meta),
            ("differential_blue", diff_blue, diff_blue_meta),
            ("blue_channel_max", blue_max, blue_max_meta),
        ]:
            attacks[name] = {"frame": frame, "metadata": meta}
        return attacks

    @staticmethod
    def _combine_frames(
        frames: list[np.ndarray],
        method: str,
        restore_brightness: bool,
    ) -> np.ndarray:
        stack = np.stack([f.astype(np.float32) for f in frames], axis=0)
        if method == "mean":
            combined = np.mean(stack, axis=0)
        elif method == "max":
            combined = np.max(stack, axis=0)
        elif method == "median":
            combined = np.median(stack, axis=0)
        else:
            raise ValueError("unsupported combine method")
        if restore_brightness and method in {"mean", "median"}:
            combined *= len(frames)
        return np.clip(combined, 0, 255).astype(np.uint8)

    @staticmethod
    def _select_channel(frame: np.ndarray, channel: str) -> np.ndarray:
        if frame.ndim != 3 or frame.shape[-1] < 3:
            raise ValueError("frame must be H×W×3")
        f = frame.astype(np.float32)
        if channel == "red":
            return f[..., 0]
        if channel == "green":
            return f[..., 1]
        if channel == "blue":
            return f[..., 2]
        if channel == "luma":
            return 0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2]
        raise ValueError("unsupported channel")

    @staticmethod
    def _normalize_plane(plane: np.ndarray) -> np.ndarray:
        p = plane.astype(np.float32)
        lo = float(np.percentile(p, 1))
        hi = float(np.percentile(p, 99))
        if hi <= lo + 1e-6:
            return np.zeros_like(p, dtype=np.uint8)
        norm = (p - lo) * (255.0 / (hi - lo))
        return np.clip(norm, 0, 255).astype(np.uint8)

    @staticmethod
    def _reconstruction_score(frame: np.ndarray) -> tuple[float, dict]:
        f = frame.astype(np.float32)
        gray = (
            0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2]
            if frame.ndim == 3
            else f
        )
        contrast = float(np.std(gray))
        gx = np.diff(gray, axis=1)
        gy = np.diff(gray, axis=0)
        edge_energy = float(np.mean(np.abs(gx)) + np.mean(np.abs(gy)))
        coverage = float(np.mean(gray > 1.0))
        saturation = float(np.mean(gray > 254.0))
        # 攻击者不只偏好高对比，也偏好覆盖完整且不过度椒盐化的候选窗口。
        # 错误相位常保留随机掩模的高频边缘，视觉上很"硬"但并非好重构，
        # 因此边缘能量和过曝饱和都作为负信号。
        score = 300.0 * coverage + contrast - edge_energy - 100.0 * saturation
        return score, {
            "contrast": contrast,
            "edge_energy": edge_energy,
            "coverage": coverage,
            "saturation": saturation,
        }

    def off_axis_temporal_average_attack(
        self,
        subframes: list[np.ndarray],
        angle_degrees: float = 35.0,
        regions: tuple[int, int] = (3, 3),
        cycles: int = 1,
    ) -> np.ndarray:
        """
        离轴相机时域平均攻击模型（交底书 7.2）。

        正视时完整周期平均会重构原图；离轴时 LCD 视角响应导致区域级亮度
        衰减、色偏和微小错位。这里用区域分块近似这些现象，配合
        view-differentiated 掩模可量化"正视 vs 离轴"攻击差异。
        """
        if not subframes:
            raise ValueError("subframes must not be empty")
        if cycles <= 0:
            raise ValueError("cycles must be positive")

        h, w = subframes[0].shape[:2]
        rows, cols = regions
        angle = abs(float(angle_degrees))
        attenuation = float(np.clip(np.cos(np.deg2rad(angle)) ** 1.4, 0.35, 1.0))
        color_shift = np.array(
            [1.0 - 0.12 * (1 - attenuation), 1.0, 1.0 + 0.18 * (1 - attenuation)],
            dtype=np.float32,
        )
        result = np.zeros_like(subframes[0], dtype=np.float32)
        rh = h // rows
        rw = w // cols

        for r in range(rows):
            for c in range(cols):
                y0, y1 = r * rh, h if r == rows - 1 else (r + 1) * rh
                x0, x1 = c * rw, w if c == cols - 1 else (c + 1) * rw
                phase = (r + 2 * c) % len(subframes)
                sampled = [
                    subframes[(i + phase) % len(subframes)][y0:y1, x0:x1].astype(np.float32)
                    for i in range(len(subframes) * cycles)
                ]
                region = np.mean(sampled, axis=0)
                region = region * attenuation * color_shift.reshape(1, 1, 3)
                # 离轴透视/采样错位：区域位置越偏，错位越明显。
                shift_x = int(round((c - (cols - 1) / 2) * angle / 25))
                shift_y = int(round((r - (rows - 1) / 2) * angle / 40))
                region = np.roll(region, shift=(shift_y, shift_x), axis=(0, 1))
                result[y0:y1, x0:x1] = region

        return np.clip(result, 0, 255).astype(np.uint8)

    def off_axis_correction(
        self,
        frame: np.ndarray,
        regions: tuple[int, int] = (3, 3),
        angle_degrees: float = 35.0,
        target_mean: np.ndarray | None = None,
    ) -> np.ndarray:
        """
        强攻击者对离轴畸变的最佳努力校正（诚实性对照，交底书 7.2）。

        `off_axis_temporal_average_attack` 施加的区域级衰减、色偏与整块位移
        都是**可逆**的：知道（或反推出）成像几何的攻击者可以反向平移，并用
        数据驱动的逐区域增益归一化撤销亮度/色彩差异，无需知道精确衰减系数。

        本函数即模拟该校正，用来量化"视角差异化掩模"在纯软件模型下能提供
        多少**不可被撤销**的保护——结论是：几乎为零。离轴 SSIM 下降主要来自
        可逆物理畸变，而非掩模差异化（整周期平均时各区域各自还原）。真正不可逆
        的物理视角响应建模属 PoC 范围外。

        Args:
            frame: 离轴攻击输出帧（已 ×n 复原亮度的重构图）
            regions: 与前向模型一致的区域划分
            angle_degrees: 攻击者估计的离轴角（用于反向平移几何）
            target_mean: 各区域归一化到的目标逐通道均值，None 取全帧均值

        Returns:
            校正后帧 uint8 (H, W, 3)
        """
        if frame.ndim != 3:
            raise ValueError("frame must be H×W×3")
        h, w = frame.shape[:2]
        rows, cols = regions
        f = frame.astype(np.float32)
        if target_mean is None:
            target_mean = f.reshape(-1, f.shape[-1]).mean(axis=0)
        angle = abs(float(angle_degrees))
        rh = h // rows
        rw = w // cols
        out = f.copy()

        for r in range(rows):
            for c in range(cols):
                y0, y1 = r * rh, h if r == rows - 1 else (r + 1) * rh
                x0, x1 = c * rw, w if c == cols - 1 else (c + 1) * rw
                # 反向平移：撤销前向模型施加的整块位移。
                shift_x = int(round((c - (cols - 1) / 2) * angle / 25))
                shift_y = int(round((r - (rows - 1) / 2) * angle / 40))
                region = np.roll(
                    f[y0:y1, x0:x1], shift=(-shift_y, -shift_x), axis=(0, 1)
                )
                # 数据驱动逐区域增益归一化：撤销区域级衰减/色偏，无需已知系数。
                rmean = region.reshape(-1, region.shape[-1]).mean(axis=0)
                gain = np.where(rmean > 1e-3, target_mean / rmean, 1.0)
                out[y0:y1, x0:x1] = region * gain.reshape(1, 1, -1)

        return np.clip(out, 0, 255).astype(np.uint8)

    # ------------------------------------------------------------------
    # 卷帘快门行对齐重构 / 时域超分（强攻击者，边界分析补强）
    # ------------------------------------------------------------------

    def rolling_shutter_row_alignment_attack(
        self,
        subframes: list[np.ndarray],
        display_rate: float,
        n_captures: int = 8,
        method: str = "max",
    ) -> tuple[np.ndarray, dict]:
        """
        多相位卷帘快门行对齐重构。

        单张卷帘帧只混合了部分子帧的行片段；强攻击者用不同触发相位多次拍摄，
        让每个像素在某些帧的曝光行内落在"已点亮子帧"上，再做逐像素聚合
        （max/median）即可跨完整周期重构内容。这是"卷帘快门不构成额外保护"
        的边界证据：行级混合可被多帧相位对齐撤销。

        Args:
            subframes: 一个或多个周期的子帧序列
            display_rate: 子帧显示刷新率（Hz）
            n_captures: 不同相位的卷帘帧数量
            method: 逐像素聚合方式 "max"/"median"/"mean"

        Returns:
            (reconstructed_frame, metadata)
        """
        if not subframes:
            raise ValueError("subframes must not be empty")
        if display_rate <= 0:
            raise ValueError("display_rate must be positive")
        if n_captures <= 0:
            raise ValueError("n_captures must be positive")
        if method not in {"mean", "max", "median"}:
            raise ValueError("method must be one of {'mean', 'max', 'median'}")
        delta_t = 1.0 / display_rate
        span = delta_t * len(subframes)
        captures = [
            self.capture_rolling_shutter(
                subframes, display_rate, switch_time=(i / n_captures) * span
            )
            for i in range(n_captures)
        ]
        recovered = self._combine_frames(
            captures, method=method, restore_brightness=(method != "max")
        )
        score, metrics = self._reconstruction_score(recovered)
        metadata = {
            "attack": "rolling_shutter_row_alignment",
            "n_captures": int(n_captures),
            "method": method,
            "score": float(score),
            **metrics,
        }
        return recovered, metadata

    def temporal_superresolution_attack(
        self,
        frame_sequence: list[np.ndarray],
        sharpen: bool = True,
    ) -> tuple[np.ndarray, dict]:
        """
        时域超分重构。

        攻击者把覆盖 ≥1 个完整周期的多张稀疏帧逐像素取最大值聚合，恢复每个
        像素被点亮时的真实值（每像素在周期内恰好点亮一次），可选反锐化增强
        笔画边缘。进一步坐实：任何覆盖完整周期的逐像素聚合（max/median/mean）
        都能反演互斥完备掩模——与时域平均/相位搜索同属线性时间分片的边界。
        """
        if not frame_sequence:
            raise ValueError("frame_sequence must not be empty")
        recovered = self._combine_frames(
            frame_sequence, method="max", restore_brightness=False
        )
        if sharpen:
            import cv2
            blur = cv2.GaussianBlur(recovered, (0, 0), 1.0)
            recovered = np.clip(
                recovered.astype(np.float32) * 1.5 - blur.astype(np.float32) * 0.5,
                0, 255,
            ).astype(np.uint8)
        score, metrics = self._reconstruction_score(recovered)
        metadata = {
            "attack": "temporal_superresolution",
            "frames": len(frame_sequence),
            "sharpen": bool(sharpen),
            "score": float(score),
            **metrics,
        }
        return recovered, metadata

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
        attack_metadata: dict[str, dict] = {}
        if len(subframes) >= 2:
            for name, entry in self.screen_camera_attack_suite(
                subframes,
                cycle_length=len(subframes),
            ).items():
                attacks[name] = entry["frame"]
                attack_metadata[name] = entry["metadata"]
        if inversion_frames:
            attacks["long_exposure_with_inv"] = self.long_exposure_attack(
                subframes, inversion_frames, 4
            )

        results = {}
        for attack_name, frame in attacks.items():
            entry: dict = dict(attack_metadata.get(attack_name, {}))

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
