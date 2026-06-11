"""
视觉质量评估指标

实现论文所需的全部量化评估指标：
  - FPI（闪烁感知指数，IEEE 1789-2015）
  - Delta E（CIEDE2000 色差）
  - 信息熵比（单帧 vs. 原始帧）
  - 亮度均匀性
"""

import numpy as np
from scipy import stats


# ------------------------------------------------------------------
# FPI：闪烁感知指数（IEEE 1789-2015 简化模型）
# ------------------------------------------------------------------

def compute_fpi(
    refresh_rate: float,
    n: int,
    modulation_depth: float | None = None,
    spatial_pool_pixels: int = 625,
) -> float:
    """
    计算闪烁感知指数（FPI）。

    基于 IEEE 1789-2015，FPI < 0.1 表示人眼不可感知闪烁。

    模型要点：随机点阵掩模下每像素以 f_r/n 频率点亮，但相邻像素相位
    由 CSPRNG 随机分配。人眼感受野在空间上汇聚 N 个像素（典型观看距离
    下约数百像素），随机相位使汇聚后亮度调制深度按 1/√N 衰减——
    这是随机点阵优于全屏高频闪烁方案的核心数学依据。

    当每像素闪烁频率低于临界融合频率（CFF≈60Hz）时，闪烁以"颗粒噪声"
    形式被相干感知，空间汇聚不再有效。

    Args:
        refresh_rate: 显示刷新率（Hz）
        n: 子帧数量
        modulation_depth: 单像素调制深度 ∈ [0, 1]，None 时估算为 1-1/n
        spatial_pool_pixels: 人眼感受野汇聚像素数（默认 625，即 25x25）

    Returns:
        FPI 值（<0.1 为安全）
    """
    pixel_flash_freq = refresh_rate / n  # 每像素点亮频率
    if modulation_depth is None:
        # 每像素在周期内仅点亮 1/n 时间，单像素调制深度约 (1 - 1/n)
        modulation_depth = 1.0 - 1.0 / n

    critical_freq = 60.0  # Hz，人眼临界融合频率

    if pixel_flash_freq >= critical_freq:
        # 高于 CFF：空间相位随机化生效，调制深度按 1/√N 汇聚衰减，
        # 再按频率超出 CFF 的比例平方衰减（Ferry-Porter 定律近似）
        perceived_depth = modulation_depth / np.sqrt(spatial_pool_pixels)
        fpi = perceived_depth * (critical_freq / pixel_flash_freq) ** 2
    else:
        # 低于 CFF：闪烁可被相干感知，空间汇聚失效，线性近似
        fpi = modulation_depth * (1 - pixel_flash_freq / critical_freq)

    return float(fpi)


def fpi_is_safe(fpi: float, threshold: float = 0.1) -> bool:
    return fpi < threshold


# ------------------------------------------------------------------
# Delta E：CIEDE2000 色差
# ------------------------------------------------------------------

def _srgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """向量化 sRGB(uint8) → CIE Lab 转换（D65 白点）。"""
    c = rgb.astype(np.float64) / 255.0
    # sRGB 反伽马
    linear = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    # 线性 RGB → XYZ（D65）
    m = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    xyz = linear @ m.T

    # XYZ → Lab
    white = np.array([0.95047, 1.0, 1.08883])
    t = xyz / white
    delta = 6 / 29
    f = np.where(t > delta ** 3, np.cbrt(t), t / (3 * delta ** 2) + 4 / 29)

    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def _ciede2000(lab1: np.ndarray, lab2: np.ndarray) -> np.ndarray:
    """向量化 CIEDE2000 色差公式（kL=kC=kH=1）。"""
    L1, a1, b1 = lab1[..., 0], lab1[..., 1], lab1[..., 2]
    L2, a2, b2 = lab2[..., 0], lab2[..., 1], lab2[..., 2]

    C1 = np.hypot(a1, b1)
    C2 = np.hypot(a2, b2)
    C_bar = (C1 + C2) / 2

    G = 0.5 * (1 - np.sqrt(C_bar ** 7 / (C_bar ** 7 + 25.0 ** 7 + 1e-30)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)

    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360

    dLp = L2 - L1
    dCp = C2p - C1p

    dhp = h2p - h1p
    dhp = np.where(dhp > 180, dhp - 360, dhp)
    dhp = np.where(dhp < -180, dhp + 360, dhp)
    dhp = np.where((C1p * C2p) == 0, 0.0, dhp)
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dhp) / 2)

    Lp_bar = (L1 + L2) / 2
    Cp_bar = (C1p + C2p) / 2

    hsum = h1p + h2p
    hdiff = np.abs(h1p - h2p)
    hp_bar = np.where(
        (C1p * C2p) == 0, hsum,
        np.where(hdiff <= 180, hsum / 2,
                 np.where(hsum < 360, (hsum + 360) / 2, (hsum - 360) / 2)),
    )

    T = (1 - 0.17 * np.cos(np.radians(hp_bar - 30))
         + 0.24 * np.cos(np.radians(2 * hp_bar))
         + 0.32 * np.cos(np.radians(3 * hp_bar + 6))
         - 0.20 * np.cos(np.radians(4 * hp_bar - 63)))

    SL = 1 + 0.015 * (Lp_bar - 50) ** 2 / np.sqrt(20 + (Lp_bar - 50) ** 2)
    SC = 1 + 0.045 * Cp_bar
    SH = 1 + 0.015 * Cp_bar * T

    d_theta = 30 * np.exp(-(((hp_bar - 275) / 25) ** 2))
    RC = 2 * np.sqrt(Cp_bar ** 7 / (Cp_bar ** 7 + 25.0 ** 7 + 1e-30))
    RT = -RC * np.sin(np.radians(2 * d_theta))

    return np.sqrt(
        (dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2
        + RT * (dCp / SC) * (dHp / SH)
    )


def compute_delta_e(img_original: np.ndarray, img_integrated: np.ndarray) -> float:
    """
    计算原始图像与视觉积分图像之间的平均 CIEDE2000 色差。

    Args:
        img_original: uint8 (H, W, 3) RGB 原始帧
        img_integrated: uint8 (H, W, 3) RGB 积分帧（子帧叠加后）

    Returns:
        平均 Delta E 值（< 1.0 为人眼不可感知）
    """
    lab1 = _srgb_to_lab(img_original.reshape(-1, 3))
    lab2 = _srgb_to_lab(img_integrated.reshape(-1, 3))
    return float(np.mean(_ciede2000(lab1, lab2)))


# ------------------------------------------------------------------
# 信息熵比
# ------------------------------------------------------------------

def compute_entropy(image: np.ndarray) -> float:
    """
    计算灰度图像的香农熵（bits/pixel）。

    Args:
        image: uint8 (H, W, 3) 或 (H, W)
    """
    if image.ndim == 3:
        gray = np.mean(image, axis=-1).astype(np.uint8)
    else:
        gray = image

    counts = np.bincount(gray.ravel(), minlength=256)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return float(stats.entropy(probs, base=2))


def compute_entropy_ratio(
    subframe: np.ndarray, original: np.ndarray, bins: int = 64
) -> float:
    """
    计算单子帧对原始图像的信息保留率（基于归一化互信息）。

    直方图熵无法度量"可用信息"——噪声反而推高子帧的直方图熵。
    正确度量是互信息：I(X;Y) = H(X) + H(Y) - H(X,Y)，
    归一化为 I(X;Y)/H(X) ∈ [0,1]，表示子帧泄露了原图多少信息。

    Returns:
        信息保留率 ∈ [0, 1]，越低越安全（交底书目标 0.12-0.18）
    """
    def _to_gray_binned(img: np.ndarray) -> np.ndarray:
        if img.ndim == 3:
            g = np.mean(img, axis=-1)
        else:
            g = img.astype(float)
        return (g * bins / 256).astype(np.int32).clip(0, bins - 1)

    x = _to_gray_binned(original).ravel()
    y = _to_gray_binned(subframe).ravel()

    joint, _, _ = np.histogram2d(x, y, bins=bins, range=[[0, bins], [0, bins]])
    joint = joint / joint.sum()

    px = joint.sum(axis=1)
    py = joint.sum(axis=0)

    h_x = -np.sum(px[px > 0] * np.log2(px[px > 0]))
    h_y = -np.sum(py[py > 0] * np.log2(py[py > 0]))
    h_xy = -np.sum(joint[joint > 0] * np.log2(joint[joint > 0]))

    if h_x < 1e-9:
        return 0.0
    mi = h_x + h_y - h_xy
    return float(np.clip(mi / h_x, 0.0, 1.0))


# ------------------------------------------------------------------
# SSIM 结构相似度（支撑"视觉无损"声称）
# ------------------------------------------------------------------

def compute_ssim(img1: np.ndarray, img2: np.ndarray, win_size: int = 7) -> float:
    """
    计算两图的平均 SSIM（结构相似度）。

    用于量化积分帧 vs 原始帧的感知一致性（交底书"视觉无损"）。
    SSIM > 0.98 通常视为视觉无损。纯 NumPy 实现，避免额外依赖。

    Args:
        img1, img2: uint8 (H,W,3) 或 (H,W)

    Returns:
        平均 SSIM ∈ [-1, 1]，越接近 1 越相似
    """
    def _gray(x):
        return np.mean(x, axis=-1).astype(np.float64) if x.ndim == 3 else x.astype(np.float64)

    a = _gray(img1)
    b = _gray(img2)
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    # 用均匀窗口的滑动均值/方差（uniform filter 近似高斯）
    from scipy.ndimage import uniform_filter
    mu1 = uniform_filter(a, win_size)
    mu2 = uniform_filter(b, win_size)
    mu1_sq, mu2_sq, mu1_mu2 = mu1**2, mu2**2, mu1*mu2

    sigma1_sq = uniform_filter(a*a, win_size) - mu1_sq
    sigma2_sq = uniform_filter(b*b, win_size) - mu2_sq
    sigma12 = uniform_filter(a*b, win_size) - mu1_mu2

    ssim_map = ((2*mu1_mu2 + C1) * (2*sigma12 + C2)) / (
        (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    return float(ssim_map.mean())


# ------------------------------------------------------------------
# 运动清晰度（pursuit-camera 运动模糊，交底书 6.3）
# ------------------------------------------------------------------

def compute_motion_blur_width(
    subframes: list[np.ndarray], velocity_px: float = 8.0
) -> dict:
    """
    模拟 pursuit-camera（眼动追踪）下运动边缘的模糊宽度。

    人眼追踪运动物体时，n 个子帧在视网膜上沿运动方向错位累积，可能加宽
    运动边缘。本函数对子帧序列按速度平移后积分，测量阶跃边缘的 10%-90%
    上升宽度，对比单帧基线，给出模糊增幅。

    Args:
        subframes: n 个子帧
        velocity_px: 每子帧位移（像素）

    Returns:
        dict: baseline_width / integrated_width / increase_pct
    """
    n = len(subframes)

    def _edge_width(img_gray: np.ndarray) -> float:
        # 取中间行的水平梯度，估计阶跃边缘 10-90% 宽度
        row = img_gray[img_gray.shape[0] // 2].astype(np.float64)
        if row.max() - row.min() < 1e-6:
            return 0.0
        norm = (row - row.min()) / (row.max() - row.min())
        above = np.where(norm > 0.1)[0]
        below = np.where(norm < 0.9)[0]
        if len(above) == 0 or len(below) == 0:
            return 0.0
        return float(abs(above[0] - below[-1])) or 1.0

    gray = [np.mean(sf, axis=-1) for sf in subframes]
    baseline = np.mean([_edge_width(g) for g in gray])

    # pursuit 积分：第 k 子帧沿运动方向平移 k*velocity
    h, w = gray[0].shape
    acc = np.zeros((h, w), dtype=np.float64)
    for k, g in enumerate(gray):
        shift = int(round((k - n / 2) * velocity_px))
        acc += np.roll(g, shift, axis=1)
    acc /= n

    integrated_width = _edge_width(acc)
    increase = (integrated_width - baseline) / baseline * 100 if baseline > 0 else 0.0
    return {
        "baseline_width_px": float(baseline),
        "integrated_width_px": float(integrated_width),
        "increase_pct": float(increase),
    }


# ------------------------------------------------------------------
# 亮度均匀性
# ------------------------------------------------------------------

def compute_brightness_uniformity(image: np.ndarray, regions: int = 9) -> float:
    """
    测量屏幕九区域亮度差异 ΔL/L。

    Args:
        image: uint8 (H, W, 3)
        regions: 分区数量（3x3=9）

    Returns:
        ΔL/L，< 0.05 为均匀（5% 阈值）
    """
    h, w = image.shape[:2]
    rows = int(np.sqrt(regions))
    cols = int(np.ceil(regions / rows))

    rh = h // rows
    rw = w // cols

    luminances = []
    for r in range(rows):
        for c in range(cols):
            patch = image[r*rh:(r+1)*rh, c*rw:(c+1)*rw]
            # ITU-R BT.601 亮度公式
            lum = 0.299 * patch[:,:,0] + 0.587 * patch[:,:,1] + 0.114 * patch[:,:,2]
            luminances.append(float(np.mean(lum)))

    L_mean = np.mean(luminances)
    if L_mean < 1e-6:
        return 0.0
    delta_L = max(luminances) - min(luminances)
    return float(delta_L / L_mean)


# ------------------------------------------------------------------
# 综合评估报告
# ------------------------------------------------------------------

def evaluate_all(
    original: np.ndarray,
    subframes: list[np.ndarray],
    integrated: np.ndarray,
    refresh_rate: float,
    n: int,
) -> dict:
    """
    生成完整评估报告。

    Returns:
        dict 包含所有指标及通过/失败状态
    """
    fpi = compute_fpi(refresh_rate, n)
    delta_e = compute_delta_e(original, integrated)
    ssim = compute_ssim(original, integrated)
    entropy_ratios = [compute_entropy_ratio(sf, original) for sf in subframes]

    # 管线引入的亮度不均匀性：测量积分帧/原始帧比值图的区域差异，
    # 与图像内容无关（直接测积分帧会把原图自身明暗当作不均匀）
    ratio_map = (integrated.astype(np.float64) + 1.0) / (original.astype(np.float64) + 1.0)
    ratio_img = np.clip(ratio_map * 128, 0, 255).astype(np.uint8)
    uniformity = compute_brightness_uniformity(ratio_img)

    return {
        "fpi": fpi,
        "fpi_safe": fpi_is_safe(fpi),
        "delta_e": delta_e,
        "delta_e_imperceptible": delta_e < 1.0,
        "ssim": ssim,
        "ssim_lossless": ssim > 0.98,
        "entropy_ratio_mean": float(np.mean(entropy_ratios)),
        "entropy_ratio_min": float(np.min(entropy_ratios)),
        "entropy_ratio_max": float(np.max(entropy_ratios)),
        "brightness_uniformity": uniformity,
        "uniformity_ok": uniformity < 0.05,
        "refresh_rate_hz": refresh_rate,
        "n_subframes": n,
        "effective_fps": refresh_rate / n,
    }
