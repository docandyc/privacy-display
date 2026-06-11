"""
完整评测套件

批量测试不同参数组合（n、ε、刷新率）下的全部指标，
输出论文所需的对比表格与图表。
"""

import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass, asdict

from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.core.noise_injector import NoiseInjector
from src.evaluation.metrics import evaluate_all, compute_entropy_ratio
from src.attack.ocr_evaluator import OCREvaluator


@dataclass
class BenchmarkConfig:
    n: int
    refresh_rate: float
    epsilon: float
    gamma_factor: float = 1.1
    use_noise: bool = True
    use_inversion: bool = False


@dataclass
class BenchmarkResult:
    config: BenchmarkConfig
    fpi: float
    fpi_safe: bool
    delta_e: float
    entropy_ratio_mean: float
    ocr_original_acc: float
    ocr_subframe_acc: float
    accuracy_reduction_pct: float
    protection_effective: bool


class Benchmark:
    def __init__(
        self,
        test_images: list[np.ndarray],
        ground_truths: list[str],
        output_dir: str = "experiments/results",
        ocr_engine: str = "tesseract",
    ):
        self.test_images = test_images
        self.ground_truths = ground_truths
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ocr_engine = ocr_engine
        self.evaluator = OCREvaluator()

    def run_config(self, cfg: BenchmarkConfig) -> BenchmarkResult:
        """对单个参数配置运行完整评测。"""
        ocr_results = []
        metric_results = []

        for img, gt in zip(self.test_images, self.ground_truths):
            h, w = img.shape[:2]
            gen = MaskGenerator(w, h, cfg.n)
            # 背光提升模型：γ=1，亮度恢复由 integrate_subframes 的
            # boost=n/γ 完成，避免 SDR 像素空间补偿的饱和裁剪
            composer = SubframeComposer(
                n=cfg.n,
                gamma=1.0,
                insert_inversion=cfg.use_inversion,
            )
            injector = NoiseInjector(n=cfg.n, epsilon=cfg.epsilon)

            masks = gen.generate()

            if cfg.use_noise:
                img_f = img.astype(np.float32) / 255.0
                noise_base = injector.generate_fgsm_noise(img_f)
                sub_noises_f = injector.split_complementary(noise_base)
                # 转换为 uint8 空间并加基底电平（防止黑像素裁剪负噪声）
                pedestal = cfg.epsilon * 255
                sub_noises = [
                    (n * 255 + pedestal).astype(np.float32) for n in sub_noises_f
                ]
            else:
                pedestal = 0.0
                sub_noises = None

            subframes = composer.compose(img, masks, sub_noises)
            integrated = composer.integrate_subframes(subframes, pedestal=pedestal)

            # 视觉质量指标
            m = evaluate_all(img, subframes, integrated, cfg.refresh_rate, cfg.n)
            metric_results.append(m)

            # OCR 保护效果
            if self.ocr_engine in self.evaluator.engines:
                ocr = self.evaluator.evaluate_protection(
                    img, subframes, gt, self.ocr_engine
                )
                ocr_results.append(ocr)

        # 汇总
        fpi = float(np.mean([m["fpi"] for m in metric_results]))
        delta_e = float(np.mean([m["delta_e"] for m in metric_results]))
        entropy = float(np.mean([m["entropy_ratio_mean"] for m in metric_results]))

        if ocr_results:
            orig_acc = float(np.mean([r["original_char_acc"] for r in ocr_results]))
            sf_acc = float(np.mean([r["mean_subframe_acc"] for r in ocr_results]))
            reduction = orig_acc - sf_acc
            protection = sf_acc < 0.20
        else:
            orig_acc = sf_acc = reduction = 0.0
            protection = False

        return BenchmarkResult(
            config=cfg,
            fpi=fpi,
            fpi_safe=fpi < 0.1,
            delta_e=delta_e,
            entropy_ratio_mean=entropy,
            ocr_original_acc=orig_acc,
            ocr_subframe_acc=sf_acc,
            accuracy_reduction_pct=reduction * 100,
            protection_effective=protection,
        )

    def run_sweep(self, configs: list[BenchmarkConfig] | None = None) -> list[BenchmarkResult]:
        """批量测试一组参数配置，输出所有结果。"""
        if configs is None:
            configs = self._default_configs()

        results = []
        for cfg in configs:
            print(f"  测试 n={cfg.n}, f_r={cfg.refresh_rate}Hz, ε={cfg.epsilon:.4f}...")
            try:
                r = self.run_config(cfg)
                results.append(r)
                print(
                    f"    FPI={r.fpi:.4f}({'✓' if r.fpi_safe else '✗'}) "
                    f"ΔE={r.delta_e:.2f} "
                    f"熵比={r.entropy_ratio_mean:.3f} "
                    f"OCR降幅={r.accuracy_reduction_pct:.1f}%"
                )
            except Exception as e:
                print(f"    [错误] {e}")

        self._save_results(results)
        return results

    def _default_configs(self) -> list[BenchmarkConfig]:
        """论文对比实验的默认参数矩阵。"""
        configs = []
        for n in [2, 4]:
            for refresh_rate in [60.0, 144.0]:
                for epsilon in [4/255, 8/255]:
                    configs.append(BenchmarkConfig(
                        n=n,
                        refresh_rate=refresh_rate,
                        epsilon=epsilon,
                        use_noise=True,
                    ))
        # 无噪声对照组
        configs.append(BenchmarkConfig(n=4, refresh_rate=144.0, epsilon=0, use_noise=False))
        return configs

    def _save_results(self, results: list[BenchmarkResult]) -> None:
        """保存结果到 JSON 文件。"""
        data = []
        for r in results:
            d = asdict(r)
            data.append(d)
        out_path = self.output_dir / "benchmark_results.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存至: {out_path}")

    def print_table(self, results: list[BenchmarkResult]) -> None:
        """打印 Markdown 格式对比表格（用于论文）。"""
        header = "| n | f_r(Hz) | ε | FPI | ΔE | 熵比 | OCR准确率(原始) | OCR准确率(子帧) | 降幅 | 保护 |"
        sep = "|" + "|".join(["---"] * 10) + "|"
        print(header)
        print(sep)
        for r in results:
            c = r.config
            print(
                f"| {c.n} | {c.refresh_rate:.0f} | {c.epsilon:.4f} "
                f"| {r.fpi:.4f} | {r.delta_e:.2f} | {r.entropy_ratio_mean:.3f} "
                f"| {r.ocr_original_acc:.1%} | {r.ocr_subframe_acc:.1%} "
                f"| {r.accuracy_reduction_pct:.1f}% "
                f"| {'✓' if r.protection_effective else '✗'} |"
            )


def run_corpus_multi_engine(
    n: int = 4,
    epsilon: float = 8 / 255,
    engines: list[str] | None = None,
    output_dir: str = "experiments/results",
) -> dict:
    """
    语料级多 OCR 引擎评测（改进项 C2）。

    在整个测试语料上运行多个 OCR 引擎，报告原始帧与单子帧的字符准确率
    mean±std，提供统计显著性（样本量 = 语料图片数）。

    Returns:
        dict: 每引擎的 {original_mean/std, subframe_mean/std, n_samples}
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from experiments.build_corpus import load_corpus

    images, truths, names = load_corpus()
    evaluator = OCREvaluator()
    avail = engines or evaluator.engines
    avail = [e for e in avail if e in evaluator.engines]

    report = {}
    for engine in avail:
        orig_accs, sf_accs = [], []
        for img, gt in zip(images, truths):
            h, w = img.shape[:2]
            gen = MaskGenerator(w, h, n)
            composer = SubframeComposer(n=n, gamma=1.0)
            injector = NoiseInjector(n=n, epsilon=epsilon)
            masks = gen.generate()
            nb = injector.generate_fgsm_noise(img.astype(np.float32) / 255.0)
            ped = epsilon * 255
            sub_noises = [(x * 255 + ped).astype(np.float32)
                          for x in injector.split_complementary(nb)]
            subframes = composer.compose(img, masks, sub_noises)

            res = evaluator.evaluate_protection(img, subframes, gt, engine)
            orig_accs.append(res["original_char_acc"])
            sf_accs.append(res["mean_subframe_acc"])

        report[engine] = {
            "n_samples": len(images),
            "original_mean": float(np.mean(orig_accs)),
            "original_std": float(np.std(orig_accs)),
            "subframe_mean": float(np.mean(sf_accs)),
            "subframe_std": float(np.std(sf_accs)),
        }

    out = Path(output_dir) / "corpus_multi_engine.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n语料级多引擎评测（n={n}, 样本={len(images)}）:")
    for eng, r in report.items():
        print(f"  [{eng}] 原始 {r['original_mean']:.1%}±{r['original_std']:.1%}  "
              f"→ 子帧 {r['subframe_mean']:.1%}±{r['subframe_std']:.1%}")
    print(f"结果已保存: {out}")
    return report


def generate_plots(results: list[BenchmarkResult], output_dir: str = "experiments/results") -> None:
    """生成论文所需图表（需要 matplotlib）。"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.rcParams["font.family"] = ["Arial Unicode MS", "SimHei", "sans-serif"]
    except ImportError:
        print("matplotlib 未安装，跳过图表生成")
        return

    out_path = Path(output_dir)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("隐私保护效果评估", fontsize=14)

    labels = [f"n={r.config.n}\nε={r.config.epsilon:.4f}" for r in results]
    x = np.arange(len(results))

    # FPI 对比
    ax = axes[0, 0]
    ax.bar(x, [r.fpi for r in results], color=["green" if r.fpi_safe else "red" for r in results])
    ax.axhline(0.1, color="red", linestyle="--", label="安全阈值 0.1")
    ax.set_title("闪烁感知指数（FPI）")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.legend()

    # Delta E 对比
    ax = axes[0, 1]
    ax.bar(x, [r.delta_e for r in results], color="steelblue")
    ax.axhline(1.0, color="red", linestyle="--", label="不可感知阈值 ΔE=1.0")
    ax.set_title("色差（Delta E CIEDE2000）")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.legend()

    # 信息熵比
    ax = axes[1, 0]
    ax.bar(x, [r.entropy_ratio_mean for r in results], color="orange")
    ax.set_title("单帧信息熵比（越低越安全）")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)

    # OCR 准确率对比
    ax = axes[1, 1]
    w = 0.35
    ax.bar(x - w/2, [r.ocr_original_acc for r in results], w, label="原始帧", color="red", alpha=0.7)
    ax.bar(x + w/2, [r.ocr_subframe_acc for r in results], w, label="单子帧", color="green", alpha=0.7)
    ax.set_title("OCR 字符准确率对比")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.legend()

    plt.tight_layout()
    fig_path = out_path / "benchmark_plots.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"图表已保存至: {fig_path}")
