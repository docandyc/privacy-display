"""
预生成回放演示（人眼端效果）

实时窗口（`main.py window`）每周期需要截屏+掩模+噪声+合成（~190ms），
无法在 120/240Hz 下播放，因此只能作为"攻击者视角"演示器。本模块
对静态测试图**离线预生成全部子帧**，播放循环只做 blit + vsync，使
240Hz 显示器能真实呈现人眼视觉积分后的完整画面。

预计算部分（make_demo_document / build_playback_frames）是纯函数，
不依赖 pygame，可单元测试；播放部分（run_playback）延迟导入 pygame。
"""

import argparse
import json
import sys
import time
from collections import deque
from dataclasses import dataclass

import numpy as np

from src.core.mask_generator import MaskGenerator
from src.core.noise_injector import NoiseInjector
from src.core.subframe_composer import SubframeComposer
from src.demo.privacy_window import (
    create_display_surface,
    detect_display_capabilities,
    minimum_refresh_rate,
    sub_noises_to_pixel_space,
)


ANTI_OCR_PROFILES = ("off", "strong")


# ----------------------------------------------------------------------
# 预计算部分（纯函数，不依赖 pygame）
# ----------------------------------------------------------------------


def _load_demo_font(size: int):
    """按 main._make_test_image 的策略加载字体：PingFang → msyh → 默认。"""
    from PIL import ImageFont

    for path in (
        "/System/Library/Fonts/PingFang.ttc",
        "C:/Windows/Fonts/msyh.ttc",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_demo_document(width: int, height: int) -> np.ndarray:
    """
    生成一张演示文档图（uint8 RGB），模拟真实办公文档。

    浅色背景（245,245,245）上绘制多档字号的深色文字：大标题（~64px）、
    中字（~32px）、小字（~16px 多行正文，含英文+数字的敏感信息样例）。

    Returns:
        uint8 (height, width, 3) RGB 图像
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"图像尺寸须为正，实际为 ({width}, {height})")

    from PIL import Image, ImageDraw

    background = (245, 245, 245)
    ink = (25, 25, 25)
    img = Image.new("RGB", (width, height), color=background)
    draw = ImageDraw.Draw(img)

    title_font = _load_demo_font(64)
    mid_font = _load_demo_font(32)
    small_font = _load_demo_font(16)

    margin = max(16, width // 32)
    y = margin
    draw.text((margin, y), "内部资料 CONFIDENTIAL", fill=ink, font=title_font)
    y += 88
    draw.text(
        (margin, y),
        "Quarterly Finance Report 2026-Q2 季度财务报告",
        fill=ink,
        font=mid_font,
    )
    y += 52

    body_lines = [
        "Account No: 6222 0210 0112 3456 789   Holder: ZHANG SAN",
        "Password: Zx9#mQ!2026   OTP Code: 483920   Valid: 06/2026",
        "Card CVV: 351   Expiry: 09/28   Credit Limit: CNY 120,000",
        "Server: 10.24.6.18:5432   DB user: finance_ro   key: A7f3-99Qe",
        "Salary Grade P7: 38,500 / month   Bonus target: 4.2 months",
        "Meeting PIN: 7741 2026   Wi-Fi: Office-5G / pass: hz2026!@#",
    ]
    line_step = 24
    bottom = height - margin - line_step
    while y < bottom:
        for line in body_lines:
            if y >= bottom:
                break
            draw.text((margin, y), line, fill=ink, font=small_font)
            y += line_step

    return np.array(img, dtype=np.uint8)


def generate_cell_masks(
    width: int,
    height: int,
    n: int,
    cycle: int,
    cell_size: int,
    key: bytes | None = None,
) -> list[np.ndarray]:
    """
    生成大颗粒互补掩模：以 cell 为单位随机分配，再放大到像素网格。

    每个像素仍恰好属于一个子帧槽位，保持互斥/完备性；随机性继续复用
    MaskGenerator 的 ChaCha20 + 拒绝采样路径，避免另写有偏随机逻辑。
    """
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if cell_size <= 0:
        raise ValueError("cell_size must be positive")
    if cell_size == 1:
        return MaskGenerator(width, height, n, key=key).generate(cycle)

    cell_w = int(np.ceil(width / cell_size))
    cell_h = int(np.ceil(height / cell_size))
    coarse = MaskGenerator(cell_w, cell_h, n, key=key).generate(cycle)
    return [
        np.repeat(np.repeat(mask, cell_size, axis=0), cell_size, axis=1)[
            :height, :width
        ]
        for mask in coarse
    ]


def _dilate_bool(mask: np.ndarray, radius: int) -> np.ndarray:
    """小半径布尔膨胀，避免在纯函数测试里依赖 OpenCV。"""
    if radius <= 0:
        return mask.copy()

    h, w = mask.shape
    padded = np.pad(mask, radius, mode="constant", constant_values=False)
    out = np.zeros((h, w), dtype=bool)
    for dy in range(2 * radius + 1):
        for dx in range(2 * radius + 1):
            out |= padded[dy:dy + h, dx:dx + w]
    return out


def extract_text_saliency_mask(image: np.ndarray) -> np.ndarray:
    """
    提取疑似文字/边缘区域，用于把强扰动限制在 OCR 最关心的位置。

    文档场景通常是浅底深字；这里用亮度分位数估计背景，再叠加梯度边缘，
    不调用 OCR 或检测模型，保证预生成阶段可离线、可单测。
    """
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must be uint8 HxWx3 RGB")

    gray = image.astype(np.float32).mean(axis=2)
    background = float(np.percentile(gray, 85))
    dark_threshold = min(210.0, max(40.0, background - 35.0))
    dark = gray <= dark_threshold

    grad = np.zeros_like(gray)
    grad[:, 1:] = np.maximum(grad[:, 1:], np.abs(gray[:, 1:] - gray[:, :-1]))
    grad[1:, :] = np.maximum(grad[1:, :], np.abs(gray[1:, :] - gray[:-1, :]))
    edge = grad >= 22.0

    return _dilate_bool(dark | edge, radius=1)


def _stripe_mask(
    shape: tuple[int, int],
    cycle: int,
    slot: int,
    stripe_width: int,
) -> np.ndarray:
    if stripe_width <= 0:
        raise ValueError("stripe_width must be positive")

    h, w = shape
    yy, xx = np.indices((h, w))
    period = max(2, stripe_width * 2)
    phase = (cycle * stripe_width + slot * max(1, stripe_width // 2)) % period
    if (cycle + slot) % 2 == 0:
        coord = xx + phase
    else:
        coord = yy + phase
    return ((coord // stripe_width) % 2) == 0


def _blend_where(
    frame_f: np.ndarray,
    mask: np.ndarray,
    target: np.ndarray,
    alpha: float,
) -> None:
    if alpha <= 0 or not np.any(mask):
        return
    frame_f[mask] = frame_f[mask] * (1.0 - alpha) + target * alpha


def apply_anti_ocr_artifacts(
    frame: np.ndarray,
    original: np.ndarray,
    saliency_mask: np.ndarray,
    cycle: int,
    slot: int,
    stripe_width: int,
    stripe_alpha: float,
    glyph_alpha: float,
) -> np.ndarray:
    """
    对单个预生成子帧叠加 OCR 对抗伪影。

    - 条纹：奇偶 slot 切换横/竖方向，制造手机采样和滚动快门别名。
    - 字形扰动：对暗笔画打孔、在邻域生成假笔画，让平均后的字符边缘变脏。
    """
    if frame.dtype != np.uint8 or original.dtype != np.uint8:
        raise ValueError("frame and original must be uint8")
    if frame.shape != original.shape:
        raise ValueError("frame and original must have the same shape")
    if saliency_mask.shape != frame.shape[:2]:
        raise ValueError("saliency_mask shape must match frame")
    if not (0.0 <= stripe_alpha <= 1.0):
        raise ValueError("stripe_alpha must be in [0, 1]")
    if not (0.0 <= glyph_alpha <= 1.0):
        raise ValueError("glyph_alpha must be in [0, 1]")

    out = frame.astype(np.float32)
    h, w = saliency_mask.shape
    yy, xx = np.indices((h, w))
    stripe = _stripe_mask((h, w), cycle, slot, stripe_width)
    stroke = saliency_mask
    halo = _dilate_bool(stroke, radius=2)
    near_stroke = halo & ~stroke

    flat = original.reshape(-1, 3).astype(np.float32)
    background_rgb = np.percentile(flat, 92, axis=0).astype(np.float32)
    if np.any(stroke):
        ink_rgb = np.percentile(original[stroke].astype(np.float32), 12, axis=0)
    else:
        ink_rgb = np.zeros(3, dtype=np.float32)

    # Keep default artifacts readable: add faint aliases around glyph edges, and
    # only lightly erase actual strokes. Higher CLI alphas can still stress OCR.
    stripe_region = _dilate_bool(stroke, radius=1)
    _blend_where(out, (stripe_region & ~stroke) & stripe, ink_rgb, stripe_alpha)
    _blend_where(out, stroke & ~stripe, background_rgb, stripe_alpha * 0.30)

    erase = stroke & (((xx + 2 * yy + cycle + slot) % 5) == 0)
    fake = near_stroke & (((3 * xx + 5 * yy + 2 * cycle + slot) % 7) <= 1)
    _blend_where(out, erase, background_rgb, glyph_alpha)
    _blend_where(out, fake, ink_rgb, glyph_alpha)

    return np.clip(out, 0, 255).astype(np.uint8)


def _validate_anti_ocr_options(
    profile: str,
    mask_cell_size: int,
    stripe_width: int,
    stripe_alpha: float,
    glyph_alpha: float,
) -> None:
    if profile not in ANTI_OCR_PROFILES:
        raise ValueError(f"anti_ocr_profile must be one of {ANTI_OCR_PROFILES}")
    if mask_cell_size <= 0:
        raise ValueError("mask_cell_size must be positive")
    if stripe_width <= 0:
        raise ValueError("stripe_width must be positive")
    if not (0.0 <= stripe_alpha <= 1.0):
        raise ValueError("stripe_alpha must be in [0, 1]")
    if not (0.0 <= glyph_alpha <= 1.0):
        raise ValueError("glyph_alpha must be in [0, 1]")


def build_playback_frames(
    image: np.ndarray,
    n: int,
    cycles: int,
    epsilon: float = 8 / 255,
    insert_inversion: bool = False,
    use_noise: bool = True,
    key: bytes | None = None,
    anti_ocr_profile: str = "off",
    mask_cell_size: int = 1,
    stripe_width: int = 10,
    stripe_alpha: float = 0.18,
    glyph_alpha: float = 0.22,
) -> tuple[list[tuple[np.ndarray, str]], dict]:
    """
    对静态图像离线预生成全部回放子帧。

    复用现有组件：MaskGenerator（逐周期独立掩模+置换）、NoiseInjector
    （轮换对抗噪声+时域互补分解）、SubframeComposer（backlight 模型
    γ=1，与 demo/window 一致）、privacy_window.sub_noises_to_pixel_space
    （pedestal 处理）。

    Args:
        image: uint8 (H, W, 3) RGB 原图
        n: 子帧数量
        cycles: 预生成周期数
        epsilon: 噪声预算
        insert_inversion: 每周期末插入反色帧（长曝光防御）
        use_noise: False 时跳过噪声（pedestal=0）
        key: 32 字节掩模密钥，None 时随机生成（传入固定 key 可复现）
        anti_ocr_profile: "off" 保持原行为，"strong" 启用 OCR 对抗伪影
        mask_cell_size: strong 模式下的掩模颗粒边长（像素）
        stripe_width: strong 模式下条纹宽度（像素）
        stripe_alpha: strong 模式下条纹混合强度
        glyph_alpha: strong 模式下字形打孔/假笔画强度

    Returns:
        (frames, meta)：frames 为 [(uint8 帧, kind)]，kind ∈
        {"subframe", "inversion"}；meta 含 n/cycles/pedestal/
        per_cycle_slots/permutations 等。
    """
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image 须为 uint8 (H, W, 3) RGB 数组")
    if cycles <= 0:
        raise ValueError(f"cycles 须为正，实际为 {cycles}")
    _validate_anti_ocr_options(
        anti_ocr_profile,
        mask_cell_size,
        stripe_width,
        stripe_alpha,
        glyph_alpha,
    )

    h, w = image.shape[:2]
    gen = MaskGenerator(w, h, n, key=key)
    composer = SubframeComposer(n=n, gamma=1.0)
    injector = NoiseInjector(n=n, epsilon=epsilon) if use_noise else None

    img_f = image.astype(np.float32) / 255.0
    frames: list[tuple[np.ndarray, str]] = []
    permutations: list[list[int]] = []
    noise_schedule: list[dict] = []
    pedestal = 0.0
    saliency_mask = (
        extract_text_saliency_mask(image)
        if anti_ocr_profile == "strong"
        else None
    )

    for cycle in range(cycles):
        if anti_ocr_profile == "strong":
            masks = generate_cell_masks(
                w,
                h,
                n,
                cycle,
                mask_cell_size,
                key=gen.key,
            )
        else:
            masks = gen.generate(cycle)
        perm = gen.generate_permutation(cycle)
        permutations.append(list(perm))

        if use_noise:
            noise_base, target_model, attack_method = (
                injector.generate_rotating_noise(img_f, cycle=cycle)
            )
            sub_noises_f = injector.split_complementary(noise_base)
            sub_noises, pedestal = sub_noises_to_pixel_space(
                sub_noises_f,
                epsilon,
            )
            noise_schedule.append(
                {"cycle": cycle, "model": target_model, "method": attack_method}
            )
        else:
            sub_noises = None
            pedestal = 0.0

        if cycle == 0:
            ok, err = composer.verify_completeness(
                image,
                masks,
                sub_noises,
                pedestal=pedestal,
            )
            if not ok:
                raise RuntimeError(
                    f"子帧完备性验证失败（cycle=0，最大误差={err:.4f}）"
                )

        subframes = composer.compose(image, masks, sub_noises)
        for slot, idx in enumerate(perm):
            frame = subframes[idx]
            if anti_ocr_profile == "strong":
                frame = apply_anti_ocr_artifacts(
                    frame,
                    image,
                    saliency_mask,
                    cycle,
                    slot,
                    stripe_width,
                    stripe_alpha,
                    glyph_alpha,
                )
            frames.append((frame, "subframe"))
        if insert_inversion:
            frames.append((composer.compose_inversion_frame(image), "inversion"))

    meta = {
        "n": n,
        "cycles": cycles,
        "epsilon": epsilon,
        "pedestal": pedestal,
        "use_noise": use_noise,
        "insert_inversion": insert_inversion,
        "per_cycle_slots": n + (1 if insert_inversion else 0),
        "permutations": permutations,
        "noise_schedule": noise_schedule,
        "anti_ocr": {
            "profile": anti_ocr_profile,
            "mask_cell_size": mask_cell_size,
            "stripe_width": stripe_width,
            "stripe_alpha": stripe_alpha,
            "glyph_alpha": glyph_alpha,
            "saliency_pixels": (
                int(saliency_mask.sum()) if saliency_mask is not None else 0
            ),
        },
    }
    return frames, meta


# ----------------------------------------------------------------------
# 播放部分（pygame，延迟导入）
# ----------------------------------------------------------------------


@dataclass
class PlaybackConfig:
    width: int = 1280
    height: int = 720
    n: int = 4
    cycles: int = 16
    epsilon: float = 8 / 255
    use_noise: bool = True
    insert_inversion: bool = False
    image_path: str | None = None
    benchmark_seconds: float = 0.0  # >0 时运行该秒数后自动退出并打印统计
    show_hud: bool = True
    anti_ocr_profile: str = "off"
    mask_cell_size: int = 1
    stripe_width: int = 10
    stripe_alpha: float = 0.18
    glyph_alpha: float = 0.22


def _load_input_image(cfg: PlaybackConfig) -> np.ndarray:
    """加载输入图像；未指定路径时生成演示文档图。"""
    if cfg.image_path:
        from PIL import Image

        img = Image.open(cfg.image_path).convert("RGB")
        img = img.resize((cfg.width, cfg.height))
        return np.array(img, dtype=np.uint8)
    return make_demo_document(cfg.width, cfg.height)


def _render_hud_line(pygame_module, font, text: str):
    """把一行 HUD 文本预渲染成带半透明底色的 surface（blit 成本极低）。"""
    text_surf = font.render(text, True, (0, 255, 0))
    line = pygame_module.Surface(
        text_surf.get_size(),
        flags=pygame_module.SRCALPHA,
    )
    line.fill((0, 0, 0, 120))
    line.blit(text_surf, (0, 0))
    return line.convert_alpha()


def run_playback(cfg: PlaybackConfig) -> dict | None:
    """
    启动预生成回放窗口（阻塞，直到用户退出或 benchmark 到时）。

    播放循环内不做任何 numpy 帧处理：全部子帧在进入循环前转换为
    pygame surface，循环体只剩 blit + HUD + flip。

    Returns:
        benchmark 模式下返回统计 dict，否则返回 None
    """
    try:
        import pygame
    except ImportError:
        print("[错误] pygame 未安装，请运行: pip install pygame")
        return None

    pygame.init()
    capabilities = detect_display_capabilities(pygame)
    min_refresh = minimum_refresh_rate(cfg.n)
    detected = capabilities.refresh_rate_hz
    refresh_safe = detected is None or detected >= min_refresh
    target_refresh = int(detected) if detected else min_refresh

    screen, vsync_enabled = create_display_surface(
        pygame,
        (cfg.width, cfg.height),
        prefer_vsync=True,
    )
    pygame.display.set_caption("人眼端回放演示 | Privacy Display Playback")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    # 预计算提示（预生成可能耗时数秒，先给用户反馈）
    screen.fill((0, 0, 0))
    screen.blit(
        font.render("Precomputing frames...", True, (0, 255, 0)),
        (8, 8),
    )
    pygame.display.flip()

    image = _load_input_image(cfg)
    frames, meta = build_playback_frames(
        image,
        n=cfg.n,
        cycles=cfg.cycles,
        epsilon=cfg.epsilon,
        insert_inversion=cfg.insert_inversion,
        use_noise=cfg.use_noise,
        anti_ocr_profile=cfg.anti_ocr_profile,
        mask_cell_size=cfg.mask_cell_size,
        stripe_width=cfg.stripe_width,
        stripe_alpha=cfg.stripe_alpha,
        glyph_alpha=cfg.glyph_alpha,
    )

    # convert 必须在 set_mode 之后；转换完丢弃 numpy 帧引用以省内存
    surfaces = [
        (pygame.surfarray.make_surface(f.swapaxes(0, 1)).convert(), kind)
        for f, kind in frames
    ]
    original_surface = pygame.surfarray.make_surface(
        image.swapaxes(0, 1)
    ).convert()
    frames = None  # noqa: F841 —— 显式释放预生成帧

    # HUD 静态行：循环外一次性预渲染
    per_cycle_slots = meta["per_cycle_slots"]
    static_surfs = []
    if not refresh_safe:
        static_surfs.append(_render_hud_line(
            pygame,
            font,
            f"[ UNSAFE REFRESH ] display {detected}Hz < required "
            f"{min_refresh}Hz (n={cfg.n})",
        ))
    static_surfs.append(_render_hud_line(
        pygame,
        font,
        f"n={cfg.n}  cycles={cfg.cycles}  slots/cycle={per_cycle_slots}  "
        f"refresh={target_refresh}Hz  vsync={int(vsync_enabled)}  "
        f"noise={int(cfg.use_noise)}  inversion={int(cfg.insert_inversion)}",
    ))
    anti = meta["anti_ocr"]
    if anti["profile"] != "off":
        static_surfs.append(_render_hud_line(
            pygame,
            font,
            f"anti-ocr={anti['profile']}  cell={anti['mask_cell_size']}px  "
            f"stripe={anti['stripe_width']}px/{anti['stripe_alpha']:.2f}  "
            f"glyph={anti['glyph_alpha']:.2f}",
        ))
    static_surfs.append(_render_hud_line(
        pygame,
        font,
        "ESC/Q:quit  SPACE:pause  H:hud  O:original/protected",
    ))

    total_slots = len(surfaces)
    frame_interval = 1.0 / target_refresh
    idx = 0
    frame_count = 0
    show_hud = cfg.show_hud
    show_original = False
    paused = False
    running = True
    fps_value = 0.0
    last_body_ms = 0.0
    dynamic_surf = None
    fps_times: deque[float] = deque(maxlen=240)   # 滚动 fps 窗口
    body_times: deque[float] = deque(maxlen=100000)  # 循环体耗时（flip 前）
    start_time = time.perf_counter()
    next_deadline = start_time + frame_interval   # 软件帧率封顶的目标时刻

    while running:
        t_iter = time.perf_counter()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_h:
                    show_hud = not show_hud
                elif event.key == pygame.K_o:
                    show_original = not show_original

        if paused:
            clock.tick(30)
            continue

        # —— 循环体：仅 blit + HUD，无任何 numpy 帧处理 ——
        if show_original:
            screen.blit(original_surface, (0, 0))
        else:
            screen.blit(surfaces[idx][0], (0, 0))

        if show_hud:
            y = 8
            for line_surf in static_surfs:
                screen.blit(line_surf, (8, y))
                y += line_surf.get_height() + 2
            if dynamic_surf is None or frame_count % 30 == 0:
                if len(fps_times) >= 2:
                    fps_value = (len(fps_times) - 1) / max(
                        fps_times[-1] - fps_times[0],
                        1e-9,
                    )
                mode = "original" if show_original else "protected"
                dynamic_surf = _render_hud_line(
                    pygame,
                    font,
                    f"fps={fps_value:.1f}  slot={idx % per_cycle_slots + 1}/"
                    f"{per_cycle_slots}  cycle={idx // per_cycle_slots}  "
                    f"mode={mode}  body={last_body_ms:.2f}ms",
                )
            screen.blit(dynamic_surf, (8, y))

        body_elapsed = time.perf_counter() - t_iter
        body_times.append(body_elapsed)
        last_body_ms = body_elapsed * 1000.0

        pygame.display.flip()
        # SDL 的 vsync=1 在无 SCALED/OPENGL 标志时可能不真正阻塞
        # （macOS 上实测如此），因此始终把帧率封顶在 target_refresh。
        # 不用 pygame Clock：其内部是 SDL_GetTicks 的整毫秒时钟，
        # 16.67ms/4.17ms 的目标间隔会被截断成 ~16ms/~4ms（实测 60Hz
        # 封顶跑出 62fps），真 vsync 生效时还可能多 busy 等 ~1ms 而
        # 错过下一个 vblank。这里改用 perf_counter 精确忙等：
        # 落后于排程（真 vsync 已阻塞、慢帧或暂停恢复）时直接重新
        # 对齐、不补帧，保证既不超帧率也不饿死。
        now = time.perf_counter()
        if now < next_deadline:
            while time.perf_counter() < next_deadline:
                pass
            now = time.perf_counter()
            next_deadline += frame_interval
        else:
            next_deadline = now + frame_interval
        fps_times.append(now)
        frame_count += 1
        idx = (idx + 1) % total_slots

        if cfg.benchmark_seconds > 0 and now - start_time >= cfg.benchmark_seconds:
            running = False

    elapsed = time.perf_counter() - start_time
    pygame.quit()

    if cfg.benchmark_seconds > 0:
        body_ms = np.asarray(body_times, dtype=np.float64) * 1000.0
        stats = {
            "target_refresh": target_refresh,
            "measured_fps_avg": round(frame_count / max(elapsed, 1e-9), 2),
            "frame_count": frame_count,
            "loop_body_ms_p50": (
                round(float(np.percentile(body_ms, 50)), 4)
                if body_ms.size else 0.0
            ),
            "loop_body_ms_p95": (
                round(float(np.percentile(body_ms, 95)), 4)
                if body_ms.size else 0.0
            ),
            "vsync": bool(vsync_enabled),
        }
        print(json.dumps(stats))
        return stats
    return None


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> PlaybackConfig:
    """解析命令行参数为 PlaybackConfig（独立函数，便于单测）。"""
    parser = argparse.ArgumentParser(
        prog="playback",
        description="预生成回放演示：离线生成全部子帧后纯 vsync 回放",
    )
    parser.add_argument("--image", type=str, default=None,
                        help="输入图像路径（默认生成演示文档图）")
    parser.add_argument("--n", type=int, default=4, help="子帧数量")
    parser.add_argument("--cycles", type=int, default=16, help="预生成周期数")
    parser.add_argument("--no-noise", action="store_true",
                        help="关闭对抗噪声（pedestal=0）")
    parser.add_argument("--inversion", action="store_true",
                        help="每周期末插入反色帧（长曝光防御）")
    parser.add_argument("--benchmark", type=float, default=0.0,
                        metavar="SECONDS",
                        help="运行指定秒数后自动退出并打印 JSON 统计")
    parser.add_argument("--width", type=int, default=1280, help="窗口宽度")
    parser.add_argument("--height", type=int, default=720, help="窗口高度")
    parser.add_argument(
        "--anti-ocr-profile",
        choices=ANTI_OCR_PROFILES,
        default="off",
        help="反 OCR 预生成档位：off 保持原行为，strong 加强手机 OCR 抑制",
    )
    parser.add_argument("--mask-cell-size", type=int, default=1,
                        help="strong 模式下随机掩模颗粒边长（像素）")
    parser.add_argument("--stripe-width", type=int, default=10,
                        help="strong 模式下条纹宽度（像素）")
    parser.add_argument("--stripe-alpha", type=float, default=0.18,
                        help="strong 模式下条纹混合强度 [0,1]")
    parser.add_argument("--glyph-alpha", type=float, default=0.22,
                        help="strong 模式下字形打孔/假笔画强度 [0,1]")
    args = parser.parse_args(argv)

    return PlaybackConfig(
        width=args.width,
        height=args.height,
        n=args.n,
        cycles=args.cycles,
        use_noise=not args.no_noise,
        insert_inversion=args.inversion,
        image_path=args.image,
        benchmark_seconds=args.benchmark,
        anti_ocr_profile=args.anti_ocr_profile,
        mask_cell_size=args.mask_cell_size,
        stripe_width=args.stripe_width,
        stripe_alpha=args.stripe_alpha,
        glyph_alpha=args.glyph_alpha,
    )


def main(argv: list[str] | None = None) -> None:
    """CLI 入口：python main.py playback [--image ...] [--benchmark 3] ..."""
    cfg = parse_args(argv if argv is not None else sys.argv[1:])
    run_playback(cfg)


if __name__ == "__main__":
    main()
