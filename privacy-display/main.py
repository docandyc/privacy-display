"""
主入口：生成演示图像并运行快速评测

使用方法：
  python main.py demo          # 生成对比图（不需要 OCR 依赖）
  python main.py benchmark     # 运行完整评测（需要 tesseract）
  python main.py window        # 启动实时显示演示（需要 pygame+mss）
  python main.py test-noise    # 验证对抗噪声互补性
"""

import sys
import numpy as np
from pathlib import Path

# 将项目根目录加入 sys.path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.core.noise_injector import NoiseInjector
from src.gpu.renderer import create_renderer
from src.demo.visual_integration import (
    make_comparison_grid, make_animation, analyze_single_frame_readability
)
from src.evaluation.metrics import evaluate_all, compute_fpi
from src.attack.camera_simulator import CameraSimulator, CameraParams


OUTPUT_DIR = ROOT / "experiments" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _make_test_image(text: str = "PRIVATE DATA 机密信息 ABC123") -> np.ndarray:
    """生成带文字的测试图像（使用 OpenCV 或 Pillow）。"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (640, 120), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
        except Exception:
            font = ImageFont.load_default()
        draw.text((20, 30), text, fill=(20, 20, 20), font=font)
        return np.array(img)
    except Exception:
        # 最简单的纯色渐变图
        img = np.zeros((120, 640, 3), dtype=np.uint8)
        for x in range(640):
            img[:, x] = [x * 255 // 640, 100, 200 - x * 200 // 640]
        return img


def cmd_demo(n: int = 4, refresh_rate: float = 240.0, epsilon: float = 8/255):
    """生成对比图和 GIF 动画，验证核心算法。

    采用背光提升模型（γ=1）：子帧像素值不放大，亮度恢复由
    硬件背光增益 B=n 完成（见 SubframeComposer.integrate_subframes）。
    SDR 像素空间补偿 γ=n·β 仅适用于暗内容（I < 255/γ），
    对亮背景文档会饱和裁剪。
    """
    print(f"\n=== Demo: n={n}, f_r={refresh_rate}Hz, ε={epsilon:.4f} ===")

    img = _make_test_image()
    h, w = img.shape[:2]

    gen = MaskGenerator(w, h, n)
    composer = SubframeComposer(n=n, gamma=1.0)
    injector = NoiseInjector(n=n, epsilon=epsilon)
    renderer = create_renderer(w, h, n, gamma=1.0)

    masks = gen.generate(cycle=0)
    perm = gen.generate_permutation(cycle=0)
    print(f"  置换序列: {perm}")

    # 生成对抗噪声
    img_f = img.astype(np.float32) / 255.0
    noise_base, target_model, attack_method = injector.generate_rotating_noise(
        img_f,
        cycle=0,
    )
    print(f"  噪声目标模型: {target_model} ({attack_method.upper()})")
    sub_noises_f = injector.split_complementary(noise_base)

    # 基底电平：屏幕无法显示负光，黑像素处负噪声会被裁剪而破坏
    # ΣN_k=0。加基底 ε 让负噪声有下探空间，积分时扣除。
    pedestal = epsilon * 255
    sub_noises = [(nf * 255 + pedestal).astype(np.float32) for nf in sub_noises_f]

    # 验证互补性
    ok, residual = injector.verify_complementarity(sub_noises_f)
    print(f"  噪声互补性验证: {'✓' if ok else '✗'} (残差={residual:.2e})")

    # 渲染子帧
    subframes = renderer.render_all_subframes(img, masks, sub_noises, perm)
    integrated = composer.integrate_subframes(subframes, pedestal=pedestal)

    # 完备性验证
    ok2, err = composer.verify_completeness(img, masks, sub_noises, pedestal=pedestal)
    print(f"  子帧完备性验证: {'✓' if ok2 else '✗'} (最大误差={err:.2f})")

    # 评估指标
    metrics = evaluate_all(img, subframes, integrated, refresh_rate, n)
    print(f"\n  评估结果:")
    print(f"    FPI = {metrics['fpi']:.4f}  ({'安全' if metrics['fpi_safe'] else '有闪烁'})")
    print(f"    Delta E = {metrics['delta_e']:.3f}  ({'不可感知' if metrics['delta_e_imperceptible'] else '可感知'})")
    print(f"    信息熵比 = {metrics['entropy_ratio_mean']:.3f}  (越低越安全)")
    print(f"    亮度均匀性 ΔL/L = {metrics['brightness_uniformity']:.4f}")
    print(f"    等效帧率 = {metrics['effective_fps']:.1f} fps")

    # 相机攻击模拟
    cam = CameraSimulator()
    single_frame = cam.capture_global_shutter_random(subframes)
    avg4 = cam.temporal_averaging_attack(subframes, 4)
    readability = analyze_single_frame_readability(img, subframes)
    print(f"\n  单帧 PSNR（相机视角，越低越好）: {readability['mean_psnr']:.1f} dB")
    print(f"  有效像素比例: {readability['mean_active_ratio']:.3f} ({1/n:.3f} 理论值)")

    # 保存对比图
    grid_path = str(OUTPUT_DIR / f"demo_n{n}_grid.png")
    make_comparison_grid(img, subframes, integrated, output_path=grid_path)

    gif_path = str(OUTPUT_DIR / f"demo_n{n}_animation.gif")
    make_animation(subframes, gif_path, fps=6)

    print(f"\n  输出已保存至: {OUTPUT_DIR}")


def cmd_benchmark():
    """运行完整评测套件。"""
    print("\n=== 完整评测 ===")
    from src.evaluation.benchmark import Benchmark, BenchmarkConfig, generate_plots

    img = _make_test_image("The quick brown fox 12345 密码 PASSWORD")
    gt = "The quick brown fox 12345 密码 PASSWORD"

    bm = Benchmark(
        test_images=[img],
        ground_truths=[gt],
        output_dir=str(OUTPUT_DIR),
    )

    configs = [
        BenchmarkConfig(n=2, refresh_rate=60.0,  epsilon=8/255, use_noise=True),
        BenchmarkConfig(n=2, refresh_rate=144.0, epsilon=8/255, use_noise=True),
        BenchmarkConfig(n=4, refresh_rate=144.0, epsilon=8/255, use_noise=True),
        BenchmarkConfig(n=4, refresh_rate=240.0, epsilon=8/255, use_noise=True),
        BenchmarkConfig(n=4, refresh_rate=144.0, epsilon=4/255, use_noise=True),
        BenchmarkConfig(n=4, refresh_rate=144.0, epsilon=0,     use_noise=False),
    ]

    results = bm.run_sweep(configs)
    print()
    bm.print_table(results)
    generate_plots(results, str(OUTPUT_DIR))


def cmd_window():
    """启动实时隐私保护演示窗口。"""
    from src.demo.privacy_window import PrivacyWindow, WindowConfig
    cfg = WindowConfig(width=1280, height=720, n=2, show_hud=True)
    win = PrivacyWindow(cfg)
    win.run()


def cmd_test_noise():
    """快速验证对抗噪声互补性。"""
    print("\n=== 对抗噪声互补性验证 ===")
    for n in [2, 3, 4, 6, 8]:
        injector = NoiseInjector(n=n, epsilon=8/255)
        base = np.random.uniform(-8/255, 8/255, (64, 64, 3)).astype(np.float32)
        sub_noises = injector.split_complementary(base)
        ok, residual = injector.verify_complementarity(sub_noises)
        print(f"  n={n}: {'✓' if ok else '✗'} (残差={residual:.2e})")


COMMANDS = {
    "demo": cmd_demo,
    "benchmark": cmd_benchmark,
    "window": cmd_window,
    "test-noise": cmd_test_noise,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"
    if cmd not in COMMANDS:
        print(f"未知命令: {cmd}")
        print(f"可用命令: {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[cmd]()
