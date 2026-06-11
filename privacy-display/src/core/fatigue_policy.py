"""
视觉疲劳优化策略（交底书 7.4）

PoC 版提供可测试的纯函数策略：
  - 根据帧间运动量选择刷新率
  - 低色温蓝光抑制
  - 近距离观看时降低补偿亮度
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AdaptiveRefreshPolicy:
    """静态内容提高刷新率，动态内容降低刷新压力。"""

    min_refresh_hz: int = 120
    max_refresh_hz: int = 240
    motion_threshold: float = 0.04

    def motion_score(self, previous: np.ndarray, current: np.ndarray) -> float:
        if previous.shape != current.shape:
            raise ValueError("previous and current frames must have the same shape")
        diff = np.abs(
            current.astype(np.float32) - previous.astype(np.float32)
        ) / 255.0
        return float(np.mean(diff))

    def select_refresh_rate(self, previous: np.ndarray, current: np.ndarray) -> int:
        score = self.motion_score(previous, current)
        return self.max_refresh_hz if score <= self.motion_threshold else self.min_refresh_hz


def blue_light_filter(image: np.ndarray, color_temperature_k: int = 4000) -> np.ndarray:
    """
    简化色温滤镜：低色温降低蓝通道并轻微提升红通道。

    输入/输出均为 uint8 RGB。6500K 近似原图，4000K 约降蓝 30%。
    """
    temp = float(np.clip(color_temperature_k, 3000, 6500))
    warmth = (6500.0 - temp) / 3500.0
    gains = np.array([
        1.0 + 0.08 * warmth,
        1.0 - 0.03 * warmth,
        1.0 - 0.30 * warmth,
    ], dtype=np.float32)
    filtered = image.astype(np.float32) * gains.reshape(1, 1, 3)
    return np.clip(filtered, 0, 255).astype(np.uint8)


def viewing_distance_adjust(
    distance_cm: float,
    compensation_scale: float = 1.0,
    min_comfort_cm: float = 50.0,
    min_scale: float = 0.65,
) -> dict:
    """近距离观看时降低亮度/噪声补偿强度。"""
    if distance_cm <= 0:
        raise ValueError("distance_cm must be positive")
    ratio = min(1.0, distance_cm / min_comfort_cm)
    scale = max(min_scale, compensation_scale * ratio)
    return {
        "distance_cm": float(distance_cm),
        "scale": float(scale),
        "reduced": distance_cm < min_comfort_cm,
    }
