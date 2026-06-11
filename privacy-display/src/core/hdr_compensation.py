"""
HDR 亮度补偿（交底书 4.3 节）

由于每帧仅显示 1/n 的像素，屏幕平均亮度降至 1/n，HDR 模式下利用
显示器峰值亮度（1000-4000 nits）将子帧亮度提升 n 倍。亮度提升可能
导致高饱和度色彩超出色域，采用 ICtCp 空间软裁剪在保持色相前提下
压缩超界饱和度。

实现要素：
  - PQ (ST.2084) EOTF / 逆 EOTF 编解码
  - RGB ↔ ICtCp 色彩空间转换（经 LMS）
  - 超色域软裁剪（保持 I 亮度与色相角，仅压缩饱和度）
"""

import numpy as np


# ------------------------------------------------------------------
# PQ (SMPTE ST.2084) 编解码
# ------------------------------------------------------------------

_PQ_M1 = 2610 / 16384
_PQ_M2 = 2523 / 4096 * 128
_PQ_C1 = 3424 / 4096
_PQ_C2 = 2413 / 4096 * 32
_PQ_C3 = 2392 / 4096 * 32
_PQ_LMAX = 10000.0  # PQ 绝对亮度上限 nits


def pq_encode(luminance_nits: np.ndarray) -> np.ndarray:
    """绝对亮度（nits）→ PQ 编码值 [0,1]（逆 EOTF / OETF）。"""
    L = np.clip(luminance_nits, 0, _PQ_LMAX) / _PQ_LMAX
    Lm1 = np.power(L, _PQ_M1)
    num = _PQ_C1 + _PQ_C2 * Lm1
    den = 1.0 + _PQ_C3 * Lm1
    return np.power(num / den, _PQ_M2)


def pq_decode(pq_value: np.ndarray) -> np.ndarray:
    """PQ 编码值 [0,1] → 绝对亮度（nits）（EOTF）。"""
    V = np.clip(pq_value, 0, 1)
    Vm2 = np.power(V, 1.0 / _PQ_M2)
    num = np.maximum(Vm2 - _PQ_C1, 0.0)
    den = _PQ_C2 - _PQ_C3 * Vm2
    return np.power(num / den, 1.0 / _PQ_M1) * _PQ_LMAX


# ------------------------------------------------------------------
# RGB ↔ ICtCp（Rec.2020 基色，经 LMS）
# ------------------------------------------------------------------

# 线性 Rec.2020 RGB → LMS
_RGB2LMS = np.array([
    [1688, 2146, 262],
    [683, 2951, 462],
    [99, 309, 3688],
], dtype=np.float64) / 4096.0

_LMS2RGB = np.linalg.inv(_RGB2LMS)

# PQ-LMS → ICtCp
_LMS2ICTCP = np.array([
    [2048, 2048, 0],
    [6610, -13613, 7003],
    [17933, -17390, -543],
], dtype=np.float64) / 4096.0

_ICTCP2LMS = np.linalg.inv(_LMS2ICTCP)


def rgb_to_ictcp(rgb_linear: np.ndarray, peak_nits: float = 1000.0) -> np.ndarray:
    """
    线性 RGB [0,1] → ICtCp。

    Args:
        rgb_linear: (..., 3) 线性光，[0,1] 映射到 [0, peak_nits]
        peak_nits: 显示器峰值亮度
    """
    lms = rgb_linear @ _RGB2LMS.T
    lms_nits = lms * peak_nits
    lms_pq = pq_encode(lms_nits)
    return lms_pq @ _LMS2ICTCP.T


def ictcp_to_rgb(ictcp: np.ndarray, peak_nits: float = 1000.0) -> np.ndarray:
    """ICtCp → 线性 RGB [0,1]。"""
    lms_pq = ictcp @ _ICTCP2LMS.T
    lms_nits = pq_decode(lms_pq)
    lms = lms_nits / peak_nits
    return lms @ _LMS2RGB.T


# ------------------------------------------------------------------
# 超色域软裁剪（保持亮度 I 与色相角，压缩饱和度）
# ------------------------------------------------------------------

def gamut_soft_clip(rgb_linear: np.ndarray, peak_nits: float = 1000.0,
                    knee: float = 0.8) -> np.ndarray:
    """
    在 ICtCp 空间软裁剪超色域颜色：保持 I（亮度）与色相角不变，
    仅对超出可显示范围的像素压缩 chroma 半径。

    Args:
        rgb_linear: (..., 3) 线性 RGB，可能超界 [0,1]
        knee: 软拐点，chroma 超过 knee*max_chroma 后开始压缩

    Returns:
        裁剪后线性 RGB，[0,1] 内
    """
    ictcp = rgb_to_ictcp(np.clip(rgb_linear, 0, None), peak_nits)
    I = ictcp[..., 0]
    Ct = ictcp[..., 1]
    Cp = ictcp[..., 2]

    chroma = np.sqrt(Ct ** 2 + Cp ** 2)
    hue = np.arctan2(Cp, Ct)

    # 二分搜索每像素最大可显示 chroma（沿色相方向缩放直到回到色域内）
    max_chroma = _max_displayable_chroma(I, hue, peak_nits)

    # 软拐点压缩：knee 以下不变，以上用 tanh 渐进压缩到 max_chroma
    safe = knee * max_chroma
    excess = np.maximum(chroma - safe, 0.0)
    room = np.maximum(max_chroma - safe, 1e-6)
    compressed = safe + room * np.tanh(excess / room)
    new_chroma = np.where(chroma > safe, compressed, chroma)

    Ct_new = new_chroma * np.cos(hue)
    Cp_new = new_chroma * np.sin(hue)
    ictcp_new = np.stack([I, Ct_new, Cp_new], axis=-1)

    rgb = ictcp_to_rgb(ictcp_new, peak_nits)
    return np.clip(rgb, 0, 1)


def _max_displayable_chroma(I: np.ndarray, hue: np.ndarray,
                            peak_nits: float, iters: int = 8) -> np.ndarray:
    """二分搜索：给定亮度 I 与色相 hue，可显示（RGB∈[0,1]）的最大 chroma。"""
    lo = np.zeros_like(I)
    hi = np.full_like(I, 0.5)  # ICtCp chroma 经验上界

    for _ in range(iters):
        mid = (lo + hi) / 2
        Ct = mid * np.cos(hue)
        Cp = mid * np.sin(hue)
        ictcp = np.stack([I, Ct, Cp], axis=-1)
        rgb = ictcp_to_rgb(ictcp, peak_nits)
        in_gamut = np.all((rgb >= -1e-4) & (rgb <= 1 + 1e-4), axis=-1)
        lo = np.where(in_gamut, mid, lo)
        hi = np.where(in_gamut, hi, mid)
    return lo


# ------------------------------------------------------------------
# HDR 子帧亮度补偿（核心接口）
# ------------------------------------------------------------------

def hdr_compensate(
    subframe_linear: np.ndarray,
    n: int,
    peak_nits: float = 1000.0,
    content_peak_nits: float = 100.0,
) -> np.ndarray:
    """
    HDR 子帧亮度补偿：在线性光空间将子帧亮度提升 n 倍，钳到峰值，
    仅对**超色域**像素做 ICtCp 软裁剪（保色相），其余像素直接归一化。

    性能优化：超色域像素通常是少数，仅对它们跑昂贵的 ICtCp 二分搜索，
    避免对全图每像素都做（原实现 12 迭代×全图，1080p 会卡数十秒）。

    Args:
        subframe_linear: (H,W,3) 子帧，线性光 [0,1]（1.0=content_peak_nits）
        n: 拆分因子（亮度需提升 n 倍）

    Returns:
        (H,W,3) 补偿后线性 RGB [0,1]
    """
    headroom = peak_nits / content_peak_nits
    boosted = subframe_linear * n

    # 超色域像素：任一通道提升后超过 headroom（per-channel 钳会破坏色相，
    # 这些像素改用 ICtCp 软裁剪）
    over = np.any(boosted > headroom, axis=-1)

    normalized = np.minimum(boosted, headroom) / headroom  # [0,1]

    if np.any(over):
        # 仅对超色域像素做保色相软裁剪
        clipped = gamut_soft_clip(normalized[over], peak_nits)
        normalized = normalized.copy()
        normalized[over] = clipped

    return normalized


def sdr_to_linear(srgb: np.ndarray) -> np.ndarray:
    """sRGB(uint8 或 [0,1]) → 线性光 [0,1]。"""
    c = srgb.astype(np.float64)
    if c.max() > 1.0:
        c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_sdr(linear: np.ndarray) -> np.ndarray:
    """线性光 [0,1] → sRGB uint8。"""
    c = np.clip(linear, 0, 1)
    srgb = np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1/2.4) - 0.055)
    return (srgb * 255).clip(0, 255).astype(np.uint8)
