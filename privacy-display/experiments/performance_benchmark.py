"""
性能实测（改进项 A4）

交底书 6.4 给出一张性能表（GPU 额外负载 3-5%、帧生成 +0.3ms 等），但这些
数字在原代码中从未被测量。本脚本**实测**各环节耗时，并与交底书声称值
并列对比，诚实标注差距与原因（PoC 为 Python/CPU 路径，非交底书假设的
驱动层 GPU 注入）。

运行: python experiments/performance_benchmark.py
"""

import sys
import time
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.core.noise_injector import NoiseInjector
from src.gpu.renderer import GPURenderer, SoftwareRenderer


def _timeit(fn, repeats: int = 50, warmup: int = 5) -> dict:
    """测量函数执行耗时，返回 ms 统计。"""
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000)
    arr = np.array(samples)
    return {
        "mean_ms": float(arr.mean()),
        "p50_ms": float(np.percentile(arr, 50)),
        "p95_ms": float(np.percentile(arr, 95)),
        "min_ms": float(arr.min()),
    }


def bench_mask_generation(w, h, n) -> dict:
    gen = MaskGenerator(w, h, n)
    c = [0]

    def run():
        c[0] += 1
        gen.generate(c[0])
    return _timeit(run)


def bench_noise_generation(w, h, n) -> dict:
    injector = NoiseInjector(n=n, epsilon=8/255)
    img = np.random.rand(h, w, 3).astype(np.float32)

    def run():
        nb = injector.generate_fgsm_noise(img)
        injector.split_complementary(nb)
    return _timeit(run, repeats=30)


def bench_composition(w, h, n, hdr=False) -> dict:
    gen = MaskGenerator(w, h, n)
    composer = SubframeComposer(n=n, gamma=1.0, hdr_mode=hdr)
    img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
    masks = gen.generate(0)

    def run():
        composer.compose(img, masks)
    # HDR 含 ICtCp 软裁剪，较慢，减少重复次数
    return _timeit(run, repeats=8 if hdr else 30, warmup=2 if hdr else 5)


def bench_gpu_render(w, h, n) -> dict | None:
    try:
        gen = MaskGenerator(w, h, n)
        renderer = GPURenderer(w, h, n, gamma=1.0)
        img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
        masks = gen.generate(0)

        def run():
            renderer.render_subframe(img, masks[0], None)
        result = _timeit(run, repeats=30)
        renderer.release()
        return result
    except Exception as e:
        print(f"  [GPU 渲染不可用: {type(e).__name__}: {e}]")
        return None


def bench_software_render(w, h, n) -> dict:
    sw = SoftwareRenderer(n, gamma=1.0)
    gen = MaskGenerator(w, h, n)
    img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
    masks = gen.generate(0)

    def run():
        sw.render_subframe(img, masks[0], None)
    return _timeit(run, repeats=30)


def main():
    print("=" * 68)
    print("性能实测  (改进项 A4) —— 实测值 vs 交底书声称值")
    print("=" * 68)

    resolutions = [
        ("1080p", 1920, 1080),
        ("1440p", 2560, 1440),
    ]
    n = 4

    for name, w, h in resolutions:
        print(f"\n■ 分辨率 {name} ({w}x{h}), n={n}")
        print("-" * 68)

        mask = bench_mask_generation(w, h, n)
        print(f"  掩模生成（拒绝采样）  : {mask['mean_ms']:.3f} ms (p95 {mask['p95_ms']:.3f})")
        print(f"    交底书声称: <0.1ms (GPU Compute Shader) | 实测为 CPU 路径")

        noise = bench_noise_generation(w, h, n)
        print(f"  对抗噪声生成          : {noise['mean_ms']:.3f} ms (p95 {noise['p95_ms']:.3f})")

        comp_sdr = bench_composition(w, h, n, hdr=False)
        print(f"  子帧合成 SDR (×{n})    : {comp_sdr['mean_ms']:.3f} ms")

        comp_hdr = bench_composition(w, h, n, hdr=True)
        print(f"  子帧合成 HDR (×{n})    : {comp_hdr['mean_ms']:.3f} ms (含 ICtCp 软裁剪)")

        sw = bench_software_render(w, h, n)
        print(f"  软件渲染单子帧        : {sw['mean_ms']:.3f} ms")

        gpu = bench_gpu_render(w, h, n)
        if gpu:
            print(f"  GPU 渲染单子帧        : {gpu['mean_ms']:.3f} ms")
            print(f"    交底书声称: 帧生成 +0.3ms (n=4) | 实测见上")

        # 端到端单帧（掩模+噪声+合成）等效帧生成时间
        e2e = mask['mean_ms'] + noise['mean_ms'] + comp_sdr['mean_ms']
        print(f"  ── 端到端单周期生成   : {e2e:.3f} ms")
        # 240Hz 下每子帧预算 4.17ms
        budget = 1000.0 / 240 * n
        print(f"     240Hz 周期预算 {budget:.2f}ms → {'✓ 满足' if e2e < budget else '✗ 超预算（需 GPU 驱动层加速）'}")

    print("\n" + "=" * 68)
    print("诚实结论:")
    print("  本 PoC 为 Python + NumPy/CPU 路径，耗时显著高于交底书声称的")
    print("  驱动层 GPU 实现。交底书的 <0.1ms 掩模生成、+0.3ms 帧生成假设")
    print("  Compute Shader 并行；要达到该指标需将核心算子下沉至 GPU 驱动/")
    print("  合成器层（交底书第四章），属本 PoC 范围外的未来工作。")
    print("  PoC 的价值在验证算法正确性与防御有效性，而非生产级性能。")
    print("=" * 68)


if __name__ == "__main__":
    main()
