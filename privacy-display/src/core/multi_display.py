"""
多显示器同步（交底书 4.4 节）

当系统连接多个显示器时，确保跨屏内容的隐私一致性：
  - 主从时钟同步：选一台为 Master，其 VBlank 信号广播至所有 Slave，
    子帧切换在 ±0.1ms 容差内同步。
  - 异构刷新率处理：以各刷新率的最小公倍数（LCM）为虚拟时钟基准，
    各屏按 (虚拟时隙数 / 自身 n) 节拍取子帧，确保任意相机曝光窗口内
    所有屏幕均呈碎片态。
"""

import math
from dataclasses import dataclass, field


@dataclass
class DisplayNode:
    """单个显示器节点。"""
    name: str
    refresh_rate: float       # Hz
    n: int                    # 子帧数
    is_master: bool = False
    _subframe_idx: int = 0
    _cycle: int = 0


@dataclass
class SyncEvent:
    """一次虚拟时钟节拍上的同步事件。"""
    virtual_tick: int
    time_ms: float
    switches: dict = field(default_factory=dict)  # display_name -> subframe_idx


class MultiDisplaySync:
    def __init__(self, displays: list[DisplayNode]):
        """
        Args:
            displays: 显示器列表，须恰有一台 is_master=True
        """
        assert displays, "至少需要一台显示器"
        masters = [d for d in displays if d.is_master]
        if not masters:
            displays[0].is_master = True  # 默认第一台为主
        self.displays = displays
        self.master = next(d for d in displays if d.is_master)

        # 虚拟时钟 = 所有刷新率的最小公倍数
        rates = [int(round(d.refresh_rate)) for d in displays]
        self.virtual_clock_hz = self._lcm_list(rates)

        # 每台屏每隔多少虚拟时隙切换一个子帧
        self.ticks_per_subframe = {
            d.name: self.virtual_clock_hz // int(round(d.refresh_rate))
            for d in displays
        }

    @staticmethod
    def _lcm_list(nums: list[int]) -> int:
        result = 1
        for x in nums:
            result = result * x // math.gcd(result, x)
        return result

    def generate_schedule(self, duration_ms: float = 100.0) -> list[SyncEvent]:
        """
        生成一段时长内的子帧切换时间表。

        Returns:
            SyncEvent 列表，每个虚拟时隙上各屏应显示的子帧索引
        """
        tick_ms = 1000.0 / self.virtual_clock_hz
        n_ticks = int(duration_ms / tick_ms)

        events = []
        for t in range(n_ticks):
            switches = {}
            for d in self.displays:
                tps = self.ticks_per_subframe[d.name]
                if t % tps == 0:  # 该屏在此虚拟时隙切换子帧
                    sf_total = t // tps
                    switches[d.name] = sf_total % d.n
            if switches:
                events.append(SyncEvent(
                    virtual_tick=t, time_ms=t * tick_ms, switches=switches
                ))
        return events

    def simulate_vblank_broadcast(
        self, n_vblanks: int = 100, broadcast_jitter_ms: float = 0.05, seed: int = 0
    ) -> dict:
        """
        模拟主从 VBlank 广播同步（交底书 4.4 主从时钟同步，±0.1ms 容差）。

        ±0.1ms 的容差针对的是**同刷新率**显示器间 VBlank 信号的广播抖动，
        而非异构刷新率下子帧切换时刻的对齐（后者因频率不同本就无法对齐，
        靠虚拟时钟 + 无完整帧泄露保证，见 verify_no_full_frame_leak）。

        本函数对与主屏同刷新率的从屏，建模广播链路抖动并验证是否达标。

        Args:
            n_vblanks: 模拟的 VBlank 次数
            broadcast_jitter_ms: 广播链路抖动幅度（硬件实现决定）
            seed: 随机种子

        Returns:
            dict: 各同刷新率从屏的 max/mean 同步误差（ms）及是否 <0.1ms
        """
        import numpy as np
        rng = np.random.default_rng(seed)

        errors = {}
        for d in self.displays:
            if d.is_master:
                continue
            if abs(d.refresh_rate - self.master.refresh_rate) > 1e-6:
                # 异构刷新率：不适用 ±0.1ms 对齐，标注靠虚拟时钟保证
                errors[d.name] = {
                    "heterogeneous": True,
                    "note": "异构刷新率，靠虚拟时钟+无泄露保证，不适用±0.1ms",
                }
                continue
            # 同刷新率：广播抖动建模（均匀分布）
            jitter = np.abs(rng.uniform(-broadcast_jitter_ms, broadcast_jitter_ms, n_vblanks))
            errors[d.name] = {
                "heterogeneous": False,
                "max_error_ms": float(jitter.max()),
                "mean_error_ms": float(jitter.mean()),
                "within_tolerance": bool(jitter.max() < 0.1),
            }
        return errors

    def verify_no_full_frame_leak(
        self, schedule: list[SyncEvent], camera_exposure_ms: float
    ) -> bool:
        """
        验证任意相机曝光窗口内，没有任何单屏完整显示一个周期
        （即不会泄露完整帧）。

        Args:
            camera_exposure_ms: 相机曝光时长

        Returns:
            True 表示无完整帧泄露（安全）
        """
        for d in self.displays:
            # 该屏一个完整周期时长
            cycle_ms = 1000.0 / d.refresh_rate * d.n
            # 若相机曝光 ≥ 一个周期，可能积分出完整帧
            if camera_exposure_ms >= cycle_ms:
                return False
        return True

    def summary(self) -> dict:
        return {
            "virtual_clock_hz": self.virtual_clock_hz,
            "master": self.master.name,
            "displays": [
                {
                    "name": d.name,
                    "refresh_rate": d.refresh_rate,
                    "n": d.n,
                    "ticks_per_subframe": self.ticks_per_subframe[d.name],
                }
                for d in self.displays
            ],
        }
