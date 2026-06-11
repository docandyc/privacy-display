"""
隐私保护窗口演示（pygame）

实时捕获屏幕内容，应用时间分片掩模后在独立窗口中循环显示子帧。
默认 n=2@120Hz，并在运行时强制满足交底书 f_r >= 60n 的刷新率约束。
"""

import json
import numpy as np
import platform
import re
import subprocess
import time
from dataclasses import dataclass


@dataclass
class WindowConfig:
    width: int = 1280
    height: int = 720
    n: int = 2
    refresh_rate: int = 120      # 目标刷新率（Hz），需满足 f_r >= 60n
    epsilon: float = 8 / 255
    gamma_factor: float = 1.1
    inversion_alpha: float = 0.3  # 反色帧持续时间系数，t_inv = alpha * Δt
    show_hud: bool = True         # 显示 HUD 信息
    capture_region: tuple | None = None  # (x, y, w, h) 截图区域，None=全屏
    prefer_vsync: bool = True      # 优先使用 SDL/系统 VBlank 阻塞
    insert_inversion: bool = False  # 启用后周期末输出反色帧用于长曝光防御
    emergency_black_frame: bool = True  # 渲染超时时实际输出黑帧
    enable_ocr_monitoring: bool = True  # 周期性 OCR 监测，驱动在线噪声更新
    monitor_interval_cycles: int = 120  # 监测间隔，避免每周期运行 OCR
    monitor_engine: str = "tesseract"
    monitor_ground_truth: str = ""

    def __post_init__(self) -> None:
        self.refresh_rate = ensure_safe_refresh_rate(self.n, self.refresh_rate)
        if self.gamma_factor <= 0:
            raise ValueError("gamma_factor must be positive")
        validate_inversion_alpha(self.inversion_alpha)


def minimum_refresh_rate(n: int) -> int:
    """交底书约束：完整周期 T_cycle=n/f_r ≤ 16.7ms，即 f_r ≥ 60n。"""
    return int(60 * n)


def ensure_safe_refresh_rate(n: int, refresh_rate: int) -> int:
    """返回满足 f_r >= 60n 的目标刷新率。"""
    return max(int(refresh_rate), minimum_refresh_rate(n))


def validate_inversion_alpha(alpha: float) -> None:
    """交底书约束：反色帧持续时间系数 alpha ∈ [0.2, 0.5]。"""
    if not (0.2 <= float(alpha) <= 0.5):
        raise ValueError("inversion_alpha must be in [0.2, 0.5]")


def noise_pedestal_value(epsilon: float) -> float:
    """把归一化噪声预算 ε 转成像素空间 pedestal。"""
    if epsilon < 0:
        raise ValueError("epsilon must be non-negative")
    return float(epsilon * 255)


def sub_noises_to_pixel_space(
    sub_noises_f: list[np.ndarray],
    epsilon: float,
) -> tuple[list[np.ndarray], float]:
    """
    将 [-ε,+ε] 归一化子噪声转换到像素空间，并加入 pedestal。

    pedestal 让未激活像素也高于 0，从而避免负噪声在显示裁剪时破坏
    ΣN_k=0；这与 main/benchmark/重构攻击实验中的真实链路保持一致。
    """
    pedestal = noise_pedestal_value(epsilon)
    sub_noises = [
        (nf * 255 + pedestal).astype(np.float32)
        for nf in sub_noises_f
    ]
    return sub_noises, pedestal


def output_slot_duration(
    frame_interval: float,
    output_kind: str,
    inversion_alpha: float,
) -> float:
    """返回当前输出 slot 的目标持续时间；反色帧按 alpha*Δt 模拟。"""
    validate_inversion_alpha(inversion_alpha)
    if output_kind == "inversion":
        return frame_interval * float(inversion_alpha)
    return frame_interval


@dataclass(frozen=True)
class DisplayCapabilities:
    """当前显示器能力探测结果。"""

    refresh_rate_hz: int | None = None
    width: int | None = None
    height: int | None = None
    source: str = "unknown"


@dataclass(frozen=True)
class RuntimeDisplayConfig:
    """结合交底书约束和硬件能力后的运行参数。"""

    n: int
    refresh_rate: int
    safe: bool
    note: str


def resolve_runtime_display_config(
    n: int,
    requested_refresh_rate: int,
    detected_refresh_rate: int | None,
) -> RuntimeDisplayConfig:
    """
    根据硬件刷新率解析可运行参数。

    若硬件刷新率不足以满足 f_r >= 60n，优先降低 n；若连 n=2 都不满足，
    标记为 unsafe，让窗口 HUD 明确暴露风险。
    """
    requested = ensure_safe_refresh_rate(n, requested_refresh_rate)
    if detected_refresh_rate is None:
        return RuntimeDisplayConfig(n, requested, True, "refresh=target")

    detected = int(round(detected_refresh_rate))
    if detected >= minimum_refresh_rate(n):
        return RuntimeDisplayConfig(
            n,
            detected,
            True,
            f"refresh=detected:{detected}",
        )

    max_safe_n = int(detected // 60)
    if max_safe_n >= 2:
        adjusted_n = min(n, max_safe_n)
        return RuntimeDisplayConfig(
            adjusted_n,
            detected,
            True,
            f"n lowered to {adjusted_n} for {detected}Hz display",
        )

    return RuntimeDisplayConfig(
        2,
        detected,
        False,
        f"display refresh {detected}Hz below minimum 120Hz",
    )


def detect_display_capabilities(pygame_module=None) -> DisplayCapabilities:
    """
    读取当前显示器分辨率和刷新率。

    pygame/SDL 通常能给出桌面尺寸但不给刷新率；刷新率再用平台命令探测。
    探测失败时返回 refresh_rate_hz=None，调用方会退回目标刷新率。
    """
    width = height = None
    if pygame_module is not None:
        try:
            sizes = pygame_module.display.get_desktop_sizes()
            if sizes:
                width, height = sizes[0]
        except Exception:
            pass
        if width is None or height is None:
            try:
                info = pygame_module.display.Info()
                width = int(info.current_w)
                height = int(info.current_h)
            except Exception:
                pass

    refresh, source = _detect_platform_refresh_rate()
    return DisplayCapabilities(refresh, width, height, source)


def _detect_platform_refresh_rate() -> tuple[int | None, str]:
    system = platform.system()
    try:
        if system == "Darwin":
            return _detect_macos_refresh_rate(), "system_profiler"
        if system == "Linux":
            return _detect_xrandr_refresh_rate(), "xrandr"
        if system == "Windows":
            return _detect_windows_refresh_rate(), "win32"
    except Exception:
        return None, "unavailable"
    return None, "unsupported"


def _detect_macos_refresh_rate() -> int | None:
    proc = subprocess.run(
        ["system_profiler", "SPDisplaysDataType", "-json"],
        capture_output=True,
        text=True,
        timeout=3,
        check=False,
    )
    if proc.returncode != 0:
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return _extract_refresh_rate_from_text(proc.stdout)
    rates = _collect_refresh_rates(payload)
    return max(rates) if rates else _extract_refresh_rate_from_text(proc.stdout)


def _detect_xrandr_refresh_rate() -> int | None:
    proc = subprocess.run(
        ["xrandr", "--current"],
        capture_output=True,
        text=True,
        timeout=2,
        check=False,
    )
    if proc.returncode != 0:
        return None
    current_rates = [
        float(match.group(1))
        for match in re.finditer(r"(\d+(?:\.\d+)?)\*", proc.stdout)
    ]
    return int(round(max(current_rates))) if current_rates else None


def _detect_windows_refresh_rate() -> int | None:
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return None

    class DEVMODE(ctypes.Structure):
        _fields_ = [
            ("dmDeviceName", wintypes.WCHAR * 32),
            ("dmSpecVersion", wintypes.WORD),
            ("dmDriverVersion", wintypes.WORD),
            ("dmSize", wintypes.WORD),
            ("dmDriverExtra", wintypes.WORD),
            ("dmFields", wintypes.DWORD),
            ("dmOrientation", wintypes.SHORT),
            ("dmPaperSize", wintypes.SHORT),
            ("dmPaperLength", wintypes.SHORT),
            ("dmPaperWidth", wintypes.SHORT),
            ("dmScale", wintypes.SHORT),
            ("dmCopies", wintypes.SHORT),
            ("dmDefaultSource", wintypes.SHORT),
            ("dmPrintQuality", wintypes.SHORT),
            ("dmColor", wintypes.SHORT),
            ("dmDuplex", wintypes.SHORT),
            ("dmYResolution", wintypes.SHORT),
            ("dmTTOption", wintypes.SHORT),
            ("dmCollate", wintypes.SHORT),
            ("dmFormName", wintypes.WCHAR * 32),
            ("dmLogPixels", wintypes.WORD),
            ("dmBitsPerPel", wintypes.DWORD),
            ("dmPelsWidth", wintypes.DWORD),
            ("dmPelsHeight", wintypes.DWORD),
            ("dmDisplayFlags", wintypes.DWORD),
            ("dmDisplayFrequency", wintypes.DWORD),
        ]

    mode = DEVMODE()
    mode.dmSize = ctypes.sizeof(DEVMODE)
    if ctypes.windll.user32.EnumDisplaySettingsW(None, -1, ctypes.byref(mode)):
        return int(mode.dmDisplayFrequency) or None
    return None


def _collect_refresh_rates(value) -> list[int]:
    rates: list[int] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if "refresh" in str(key).lower():
                rates.extend(_extract_refresh_rates_from_value(child))
            rates.extend(_collect_refresh_rates(child))
    elif isinstance(value, list):
        for child in value:
            rates.extend(_collect_refresh_rates(child))
    elif isinstance(value, str):
        rates.extend(_extract_refresh_rates_from_value(value))
    return rates


def _extract_refresh_rates_from_value(value) -> list[int]:
    if isinstance(value, (int, float)) and 24 <= float(value) <= 1000:
        return [int(round(value))]
    if isinstance(value, str):
        return [
            int(round(float(match.group(1))))
            for match in re.finditer(r"(\d+(?:\.\d+)?)\s*Hz", value, re.IGNORECASE)
        ]
    return []


def _extract_refresh_rate_from_text(text: str) -> int | None:
    rates = _extract_refresh_rates_from_value(text)
    return max(rates) if rates else None


def create_display_surface(pygame_module, size: tuple[int, int], prefer_vsync: bool):
    """创建显示表面；支持时优先开启 SDL vsync。"""
    if prefer_vsync:
        try:
            return pygame_module.display.set_mode(size, vsync=1), True
        except TypeError:
            pass
        except Exception:
            pass
    return pygame_module.display.set_mode(size), False


def select_output_frame(
    subframes: list[np.ndarray],
    inversion_frame: np.ndarray | None,
    black_frame: np.ndarray,
    slot_index: int,
    n: int,
    use_inversion: bool,
    emergency_black: bool,
) -> tuple[np.ndarray, str]:
    """根据当前时隙选择实际输出帧。"""
    if emergency_black or not subframes:
        return black_frame, "black"
    if use_inversion and slot_index == n and inversion_frame is not None:
        return inversion_frame, "inversion"
    return subframes[slot_index % n], "subframe"


def run_online_noise_monitor(
    injector,
    protected_frame: np.ndarray,
    cycle: int,
    enabled: bool,
    interval_cycles: int,
    model_name: str = "tesseract",
    engine: str | None = None,
    ground_truth: str = "",
    ocr_evaluator=None,
) -> dict | None:
    """按周期抽样保护帧运行 OCR 监测，并反馈给噪声在线策略。"""
    if not enabled or interval_cycles <= 0 or cycle % interval_cycles != 0:
        return None

    try:
        state = injector.monitor_online_recognition(
            protected_frame,
            ground_truth=ground_truth,
            model_name=model_name,
            engine=engine,
            ocr_evaluator=ocr_evaluator,
        )
        state["status"] = "sampled"
        return state
    except Exception as exc:
        return {
            "status": "unavailable",
            "engine": engine or model_name,
            "triggered": False,
            "error": exc.__class__.__name__,
        }


class PrivacyWindow:
    """
    实时隐私保护演示窗口。

    按键说明：
      ESC / Q  退出
      N        循环切换 n (2/4)
      S        截图保存当前子帧
      H        切换 HUD 显示
      SPACE    暂停/继续
    """

    def __init__(self, config: WindowConfig | None = None):
        self.cfg = config or WindowConfig()
        self._running = False
        self._paused = False
        self._current_subframe_idx = 0
        self._cycle = 0
        self._subframes: list[np.ndarray] = []
        self._permutation: list[int] = []
        self._stats = {"fps": 0.0, "jitter_ms": 0.0}
        self._noise_state = {"model": "?", "method": "?", "gradient": "none"}
        self._monitor_state = {"status": "idle", "triggered": False}

    def run(self) -> None:
        """启动演示窗口（阻塞，直到用户退出）。"""
        try:
            import pygame
        except ImportError:
            print("[错误] pygame 未安装，请运行: pip install pygame")
            return

        try:
            import mss
        except ImportError:
            print("[错误] mss 未安装，请运行: pip install mss")
            return

        from src.core.mask_generator import MaskGenerator
        from src.core.subframe_composer import SubframeComposer
        from src.core.noise_injector import NoiseInjector
        from src.core.timing_controller import TimingController
        from src.gpu.renderer import create_renderer

        pygame.init()
        capabilities = detect_display_capabilities(pygame)
        runtime = resolve_runtime_display_config(
            self.cfg.n,
            self.cfg.refresh_rate,
            capabilities.refresh_rate_hz,
        )
        self.cfg.n = runtime.n
        self.cfg.refresh_rate = runtime.refresh_rate

        screen, vsync_enabled = create_display_surface(
            pygame,
            (self.cfg.width, self.cfg.height),
            self.cfg.prefer_vsync,
        )
        pygame.display.set_caption("隐私保护显示演示 | Privacy Display PoC")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("monospace", 14)

        n = self.cfg.n
        w, h = self.cfg.width, self.cfg.height

        gen = MaskGenerator(w, h, n)
        composer = SubframeComposer(
            n=n,
            gamma=n * self.cfg.gamma_factor,
            insert_inversion=self.cfg.insert_inversion,
            inversion_alpha=self.cfg.inversion_alpha,
        )
        injector = NoiseInjector(n=n, epsilon=self.cfg.epsilon)
        renderer = create_renderer(w, h, n, gamma=n * self.cfg.gamma_factor)
        timing = TimingController(refresh_rate=self.cfg.refresh_rate, n=n)

        self._running = True
        frame_interval = 1.0 / self.cfg.refresh_rate
        screenshot_counter = 0
        self._inversion_frame: np.ndarray | None = None
        self._last_output_kind = "subframe"

        with mss.mss() as sct:
            while self._running:
                t_start = time.perf_counter()

                # 事件处理
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_q):
                            self._running = False
                        elif event.key == pygame.K_SPACE:
                            self._paused = not self._paused
                        elif event.key == pygame.K_h:
                            self.cfg.show_hud = not self.cfg.show_hud
                        elif event.key == pygame.K_n:
                            n = 4 if n == 2 else 2
                            runtime = resolve_runtime_display_config(
                                n,
                                self.cfg.refresh_rate,
                                capabilities.refresh_rate_hz,
                            )
                            n = runtime.n
                            self.cfg.n = n
                            self.cfg.refresh_rate = runtime.refresh_rate
                            frame_interval = 1.0 / self.cfg.refresh_rate
                            gen = MaskGenerator(w, h, n)
                            composer = SubframeComposer(
                                n=n,
                                gamma=n * self.cfg.gamma_factor,
                                insert_inversion=self.cfg.insert_inversion,
                                inversion_alpha=self.cfg.inversion_alpha,
                            )
                            injector = NoiseInjector(n=n, epsilon=self.cfg.epsilon)
                            renderer = create_renderer(
                                w,
                                h,
                                n,
                                gamma=n * self.cfg.gamma_factor,
                            )
                            timing = TimingController(
                                refresh_rate=self.cfg.refresh_rate,
                                n=n,
                            )
                            self._cycle = 0
                            self._current_subframe_idx = 0
                        elif event.key == pygame.K_s:
                            if self._subframes:
                                shot_idx = min(
                                    self._current_subframe_idx,
                                    len(self._subframes) - 1,
                                )
                                _save_screenshot(
                                    self._subframes[shot_idx],
                                    f"screenshot_{screenshot_counter:04d}.png"
                                )
                                screenshot_counter += 1

                if self._paused:
                    clock.tick(30)
                    continue

                # 捕获屏幕
                region = self.cfg.capture_region or {
                    "left": 0, "top": 0, "width": w, "height": h
                }
                if isinstance(region, tuple):
                    region = {"left": region[0], "top": region[1],
                              "width": region[2], "height": region[3]}
                shot = sct.grab(region)
                img = np.array(shot)[:, :, :3]  # BGRA -> BGR
                img = img[:, :, ::-1]  # BGR -> RGB

                if img.shape[:2] != (h, w):
                    import cv2
                    img = cv2.resize(img, (w, h))

                # 生成掩模与噪声
                if self._current_subframe_idx == 0:
                    masks = gen.generate(self._cycle)
                    perm = gen.generate_permutation(self._cycle)
                    timing.set_permutation(self._cycle, perm)

                    img_f = img.astype(np.float32) / 255.0
                    (
                        noise_base,
                        target_model,
                        attack_method,
                    ) = injector.generate_rotating_noise(img_f, cycle=self._cycle)
                    self._noise_state = {
                        "model": target_model,
                        "method": attack_method,
                        "gradient": injector.last_gradient_source,
                    }
                    sub_noises_f = injector.split_complementary(noise_base)
                    sub_noises, pedestal = sub_noises_to_pixel_space(
                        sub_noises_f,
                        self.cfg.epsilon,
                    )

                    self._subframes = renderer.render_all_subframes(
                        img, masks, sub_noises, perm
                    )
                    self._permutation = perm
                    self._inversion_frame = composer.compose_inversion_frame(img)
                    monitor_state = run_online_noise_monitor(
                        injector,
                        self._subframes[0],
                        cycle=self._cycle,
                        enabled=self.cfg.enable_ocr_monitoring,
                        interval_cycles=self.cfg.monitor_interval_cycles,
                        model_name=self.cfg.monitor_engine,
                        engine=self.cfg.monitor_engine,
                        ground_truth=self.cfg.monitor_ground_truth,
                    )
                    if monitor_state is not None:
                        self._monitor_state = monitor_state
                    self._noise_state["pedestal_px"] = pedestal

                elapsed_before_output = time.perf_counter() - t_start
                time_to_vblank_ms = max(
                    0.0,
                    (frame_interval - elapsed_before_output) * 1000,
                )
                render_ready = bool(self._subframes)
                emergency_black = (
                    self.cfg.emergency_black_frame
                    and timing.should_emit_black_frame(render_ready, time_to_vblank_ms)
                )

                black = composer.compose_black_frame(img.shape)
                sf, output_kind = select_output_frame(
                    self._subframes,
                    self._inversion_frame,
                    black,
                    self._current_subframe_idx,
                    n,
                    self.cfg.insert_inversion,
                    emergency_black,
                )
                self._last_output_kind = output_kind
                target_interval = output_slot_duration(
                    frame_interval,
                    output_kind,
                    self.cfg.inversion_alpha,
                )
                surf = pygame.surfarray.make_surface(sf.swapaxes(0, 1))
                screen.blit(surf, (0, 0))

                # HUD 叠加
                if self.cfg.show_hud:
                    _draw_hud(screen, font, {
                        "n": n,
                        "subframe": (
                            f"{min(self._current_subframe_idx + 1, n)}/{n}"
                        ),
                        "cycle": self._cycle,
                        "fps": self._stats["fps"],
                        "refresh": self.cfg.refresh_rate,
                        "paused": self._paused,
                        "vsync": vsync_enabled,
                        "display": capabilities.refresh_rate_hz,
                        "mode": output_kind,
                        "black": timing.black_frame_count,
                        "safe": runtime.safe,
                        "note": runtime.note,
                        "noise": self._noise_state,
                        "monitor": self._monitor_state,
                        "inversion_alpha": self.cfg.inversion_alpha,
                    })

                pygame.display.flip()
                timing.advance_on_vblank()

                # 更新子帧索引
                cycle_slots = n + (1 if self.cfg.insert_inversion else 0)
                self._current_subframe_idx = (
                    self._current_subframe_idx + 1
                ) % cycle_slots
                if self._current_subframe_idx == 0:
                    self._cycle += 1

                if not vsync_enabled:
                    elapsed = time.perf_counter() - t_start
                    sleep_t = max(0, target_interval - elapsed)
                    if sleep_t > 0:
                        time.sleep(sleep_t)
                    clock.tick(max(1, int(round(1.0 / target_interval))))

                self._stats["fps"] = 1.0 / max(time.perf_counter() - t_start, 1e-6)

        pygame.quit()
        renderer.release() if hasattr(renderer, "release") else None


def _draw_hud(screen, font, info: dict) -> None:
    """绘制半透明 HUD 信息栏。"""
    try:
        import pygame
    except ImportError:
        return

    lines = [
        f"n={info['n']}  subframe={info['subframe']}  cycle={info['cycle']}",
        (
            f"refresh={info['refresh']}Hz  fps={info['fps']:.1f}  "
            f"vsync={int(info.get('vsync', False))}"
        ),
        (
            f"mode={info.get('mode', 'subframe')}  "
            f"black={info.get('black', 0)}  "
            f"display={info.get('display') or '?'}Hz"
        ),
        "ESC:quit  N:toggle-n  S:screenshot  SPACE:pause  H:hud",
    ]
    noise = info.get("noise") or {}
    monitor = info.get("monitor") or {}
    lines.insert(
        3,
        "noise="
        f"{noise.get('model', '?')}/{noise.get('method', '?')}"
        f" grad={noise.get('gradient', 'none')} "
        f"ped={noise.get('pedestal_px', 0):.1f}px "
        f"ocr={monitor.get('status', 'idle')}",
    )
    if not info.get("safe", True):
        lines.insert(0, f"[ UNSAFE REFRESH ] {info.get('note', '')}")
    if info.get("paused"):
        lines.insert(0, "[ PAUSED ]")

    y = 8
    for line in lines:
        text_surf = font.render(line, True, (0, 255, 0))
        bg = pygame.Surface(text_surf.get_size())
        bg.set_alpha(120)
        bg.fill((0, 0, 0))
        screen.blit(bg, (8, y))
        screen.blit(text_surf, (8, y))
        y += text_surf.get_height() + 2


def _save_screenshot(frame: np.ndarray, path: str) -> None:
    try:
        from PIL import Image
        Image.fromarray(frame).save(path)
        print(f"截图已保存: {path}")
    except Exception as e:
        print(f"截图保存失败: {e}")
