"""
时序控制器（软件模拟）

在 PoC 中模拟 VBlank 驱动的子帧时序调度。
实际部署时需替换为 OS 级 VBlank 中断驱动版本。
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class TimingToken:
    """子帧切换时序令牌（对应交底书 3.2.2 中的时序令牌）。"""
    cycle: int = 0
    subframe_index: int = 0
    permutation: list[int] = field(default_factory=list)
    next_vblank_count: int = 0


class TimingController:
    def __init__(
        self,
        refresh_rate: int,
        n: int,
        on_subframe: Callable[[int, int], None] | None = None,
    ):
        """
        Args:
            refresh_rate: 目标刷新率（Hz），如 144
            n: 子帧数量
            on_subframe: 回调函数 (cycle, subframe_idx) -> None
        """
        self.refresh_rate = refresh_rate
        self.n = n
        self.frame_interval = 1.0 / refresh_rate
        self.on_subframe = on_subframe

        self._token = TimingToken()
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

        # 性能统计
        self._jitter_history: list[float] = []

        # 应急黑帧统计
        self._black_frame_count = 0

    def should_emit_black_frame(
        self, render_ready: bool, time_to_vblank_ms: float, margin_ms: float = 0.5
    ) -> bool:
        """
        判断是否应插入应急黑帧（交底书 5.4 步骤17）。

        当 GPU 未在 VBlank 前完成渲染（render_ready=False）或剩余时间不足
        margin_ms 时，插入黑帧防止未完成渲染的中间态被相机捕获。

        Args:
            render_ready: 下一子帧是否渲染完成
            time_to_vblank_ms: 距下次 VBlank 的剩余时间（ms）
            margin_ms: 安全余量

        Returns:
            True 表示本次 VBlank 应输出黑帧而非子帧
        """
        emit = (not render_ready) or (time_to_vblank_ms < margin_ms)
        if emit:
            self._black_frame_count += 1
        return emit

    @property
    def black_frame_count(self) -> int:
        return self._black_frame_count

    def set_permutation(self, cycle: int, permutation: list[int]) -> None:
        """原子更新时序令牌中的置换序列。"""
        with self._lock:
            self._token.cycle = cycle
            self._token.permutation = permutation
            self._token.subframe_index = 0

    def get_token(self) -> TimingToken:
        with self._lock:
            return TimingToken(
                cycle=self._token.cycle,
                subframe_index=self._token.subframe_index,
                permutation=list(self._token.permutation),
                next_vblank_count=self._token.next_vblank_count,
            )

    def start(self) -> None:
        """启动后台时序线程。"""
        self._running = True
        self._thread = threading.Thread(target=self._timing_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _timing_loop(self) -> None:
        """软件模拟 VBlank 中断的时序循环。"""
        next_tick = time.perf_counter()
        while self._running:
            now = time.perf_counter()
            jitter = abs(now - next_tick)
            self._jitter_history.append(jitter)

            with self._lock:
                perm = self._token.permutation
                k = self._token.subframe_index
                cycle = self._token.cycle

            if perm and self.on_subframe:
                actual_k = perm[k % len(perm)] if perm else k
                self.on_subframe(cycle, actual_k)

            with self._lock:
                self._token.subframe_index = (k + 1) % self.n
                if self._token.subframe_index == 0:
                    self._token.cycle += 1
                self._token.next_vblank_count += 1

            next_tick += self.frame_interval
            sleep_time = next_tick - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)

    def get_jitter_stats(self) -> dict:
        """返回时序抖动统计（单位 ms）。"""
        if not self._jitter_history:
            return {}
        arr = [j * 1000 for j in self._jitter_history[-1000:]]
        return {
            "mean_ms": float(sum(arr) / len(arr)),
            "max_ms": float(max(arr)),
            "count": len(arr),
        }

    def get_subframe_timing(self) -> dict:
        """返回当前刷新率配置的时序参数。"""
        delta_t = self.frame_interval * 1000  # ms
        cycle_ms = delta_t * self.n
        return {
            "refresh_rate_hz": self.refresh_rate,
            "n": self.n,
            "delta_t_ms": delta_t,
            "cycle_ms": cycle_ms,
            "effective_fps": self.refresh_rate / self.n,
        }
