"""
隐私保护窗口演示（pygame）

实时捕获屏幕内容，应用时间分片掩模后在独立窗口中循环显示子帧，
模拟 144Hz 显示器上 n=2 的实际运行效果。
"""

import numpy as np
import time
import threading
from dataclasses import dataclass


@dataclass
class WindowConfig:
    width: int = 1280
    height: int = 720
    n: int = 2
    refresh_rate: int = 60       # 目标刷新率（Hz）
    epsilon: float = 8 / 255
    gamma_factor: float = 1.1
    show_hud: bool = True         # 显示 HUD 信息
    capture_region: tuple | None = None  # (x, y, w, h) 截图区域，None=全屏


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
        from src.gpu.renderer import create_renderer

        pygame.init()
        screen = pygame.display.set_mode((self.cfg.width, self.cfg.height))
        pygame.display.set_caption("隐私保护显示演示 | Privacy Display PoC")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("monospace", 14)

        n = self.cfg.n
        w, h = self.cfg.width, self.cfg.height

        gen = MaskGenerator(w, h, n)
        composer = SubframeComposer(n=n, gamma=n * self.cfg.gamma_factor)
        injector = NoiseInjector(n=n, epsilon=self.cfg.epsilon)
        renderer = create_renderer(w, h, n, gamma=n * self.cfg.gamma_factor)

        self._running = True
        frame_interval = 1.0 / self.cfg.refresh_rate
        screenshot_counter = 0

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
                            gen = MaskGenerator(w, h, n)
                            composer = SubframeComposer(n=n, gamma=n * self.cfg.gamma_factor)
                            injector = NoiseInjector(n=n, epsilon=self.cfg.epsilon)
                            renderer = create_renderer(w, h, n, gamma=n * self.cfg.gamma_factor)
                            self._cycle = 0
                        elif event.key == pygame.K_s:
                            if self._subframes:
                                _save_screenshot(
                                    self._subframes[self._current_subframe_idx],
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

                    img_f = img.astype(np.float32) / 255.0
                    noise_base = injector.generate_fgsm_noise(img_f)
                    sub_noises_f = injector.split_complementary(noise_base)
                    sub_noises = [(nf * 255).astype(np.float32) for nf in sub_noises_f]

                    self._subframes = renderer.render_all_subframes(
                        img, masks, sub_noises, perm
                    )
                    self._permutation = perm

                # 显示当前子帧
                sf_idx = self._current_subframe_idx % n
                sf = self._subframes[sf_idx] if self._subframes else img
                surf = pygame.surfarray.make_surface(sf.swapaxes(0, 1))
                screen.blit(surf, (0, 0))

                # HUD 叠加
                if self.cfg.show_hud:
                    _draw_hud(screen, font, {
                        "n": n,
                        "subframe": f"{sf_idx+1}/{n}",
                        "cycle": self._cycle,
                        "fps": self._stats["fps"],
                        "refresh": self.cfg.refresh_rate,
                        "paused": self._paused,
                    })

                pygame.display.flip()

                # 更新子帧索引
                self._current_subframe_idx = (self._current_subframe_idx + 1) % n
                if self._current_subframe_idx == 0:
                    self._cycle += 1

                # 精确帧率控制
                elapsed = time.perf_counter() - t_start
                sleep_t = max(0, frame_interval - elapsed)
                if sleep_t > 0:
                    time.sleep(sleep_t)

                self._stats["fps"] = 1.0 / max(time.perf_counter() - t_start, 1e-6)
                clock.tick(self.cfg.refresh_rate)

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
        f"refresh={info['refresh']}Hz  fps={info['fps']:.1f}",
        "ESC:quit  N:toggle-n  S:screenshot  SPACE:pause  H:hud",
    ]
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
