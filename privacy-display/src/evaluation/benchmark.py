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
from src.attack.camera_simulator import CameraSimulator, CameraParams
from src.attack.ocr_evaluator import OCREvaluator, text_recovery_metrics


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


BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260612


def _bootstrap_mean_ci95(values: list[float]) -> dict:
    """Return a deterministic bootstrap 95% CI for the sample mean."""
    if not values:
        return {
            "low": 0.0,
            "high": 0.0,
            "half_width": 0.0,
            "confidence": 0.95,
            "method": "empty",
            "resamples": 0,
        }

    arr = np.asarray(values, dtype=np.float64)
    mean = float(np.mean(arr))
    if arr.size == 1:
        return {
            "low": mean,
            "high": mean,
            "half_width": 0.0,
            "confidence": 0.95,
            "method": "degenerate",
            "resamples": 0,
        }

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    idx = rng.integers(0, arr.size, size=(BOOTSTRAP_RESAMPLES, arr.size))
    boot_means = arr[idx].mean(axis=1)
    low, high = np.percentile(boot_means, [2.5, 97.5])
    return {
        "low": float(low),
        "high": float(high),
        "half_width": float((high - low) / 2),
        "confidence": 0.95,
        "method": "bootstrap_percentile",
        "resamples": BOOTSTRAP_RESAMPLES,
    }


def _mean_std(values: list[float]) -> dict:
    if not values:
        return {"mean": 0.0, "std": 0.0, "count": 0, "ci95": _bootstrap_mean_ci95(values)}
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "count": len(values),
        "ci95": _bootstrap_mean_ci95(values),
    }


def summarize_corpus_strata(sample_rows: list[dict], field: str) -> dict:
    """
    Summarize OCR accuracy by a metadata field.

    sample_rows entries must include:
      - `metadata`: dict
      - `original_char_acc`: float
      - `subframe_char_acc`: float
      - `accuracy_reduction`: float (optional; computed if absent)
    """
    grouped: dict[str, dict[str, list[float]]] = {}
    for row in sample_rows:
        meta = row.get("metadata", {})
        value = str(meta.get(field, "unknown"))
        original = float(row["original_char_acc"])
        subframe = float(row["subframe_char_acc"])
        reduction = float(row.get("accuracy_reduction", original - subframe))
        grouped.setdefault(value, {"original": [], "subframe": [], "reduction": []})
        grouped[value]["original"].append(original)
        grouped[value]["subframe"].append(subframe)
        grouped[value]["reduction"].append(reduction)

    out: dict[str, dict] = {}
    for value, vals in sorted(grouped.items()):
        out[value] = {
            "original": _mean_std(vals["original"]),
            "subframe": _mean_std(vals["subframe"]),
            "reduction": _mean_std(vals["reduction"]),
        }
    return out


def summarize_corpus_recovery_metrics(sample_rows: list[dict]) -> dict:
    """Summarize publication recovery metrics beyond character accuracy."""
    sensitive_rows = [
        row for row in sample_rows if int(row.get("sensitive_token_count", 0)) > 0
    ]
    return {
        "word_accuracy": {
            "original": _mean_std([float(row["original_word_acc"]) for row in sample_rows]),
            "subframe": _mean_std([float(row["subframe_word_acc"]) for row in sample_rows]),
        },
        "exact_match": {
            "original": _mean_std([float(row["original_exact_match"]) for row in sample_rows]),
            "subframe": _mean_std([float(row["subframe_exact_match"]) for row in sample_rows]),
        },
        "sensitive_token_recall": {
            "n_samples_with_sensitive_tokens": len(sensitive_rows),
            "original": _mean_std([
                float(row["original_sensitive_token_recall"]) for row in sensitive_rows
            ]),
            "subframe": _mean_std([
                float(row["subframe_sensitive_token_recall"]) for row in sensitive_rows
            ]),
        },
    }


def compose_protected_subframes(
    image: np.ndarray,
    n: int = 4,
    epsilon: float = 8 / 255,
    cycles: int = 1,
    cycle_start: int = 0,
    with_noise: bool = True,
) -> list[np.ndarray]:
    """Compose deterministic protected subframes for benchmarks and attacks."""
    if cycles <= 0:
        raise ValueError("cycles must be positive")
    h, w = image.shape[:2]
    gen = MaskGenerator(w, h, n)
    composer = SubframeComposer(n=n, gamma=1.0)
    injector = NoiseInjector(n=n, epsilon=epsilon)
    image_f = image.astype(np.float32) / 255.0
    pedestal = epsilon * 255 if with_noise else 0.0

    subframes: list[np.ndarray] = []
    for offset in range(cycles):
        cycle = cycle_start + offset
        masks = gen.generate(cycle)
        sub_noises = None
        if with_noise:
            noise_base, _, _ = injector.generate_rotating_noise(image_f, cycle=cycle)
            sub_noises = [
                (noise * 255 + pedestal).astype(np.float32)
                for noise in injector.split_complementary(noise_base)
            ]
        subframes.extend(composer.compose(image, masks, sub_noises))
    return subframes


def _psnr_db(reference: np.ndarray, candidate: np.ndarray) -> float:
    mse = float(np.mean(
        (reference.astype(np.float64) - candidate.astype(np.float64)) ** 2
    ))
    return float(10 * np.log10((255.0 ** 2) / mse)) if mse > 0 else 99.0


def summarize_strong_attack_rows(
    sample_rows: list[dict],
    leak_threshold: float = 0.20,
) -> dict:
    """Summarize corpus-level strong camera attack rows by attack and worst case."""
    attacks = sorted({row["attack"] for row in sample_rows})
    attack_summary: dict[str, dict] = {}
    for attack in attacks:
        rows = [row for row in sample_rows if row["attack"] == attack]
        sensitive_rows = [
            row for row in rows if int(row.get("sensitive_token_count", 0)) > 0
        ]
        attack_summary[attack] = {
            "char_accuracy": _mean_std([float(row["char_accuracy"]) for row in rows]),
            "word_accuracy": _mean_std([float(row["word_accuracy"]) for row in rows]),
            "exact_match": _mean_std([float(row["exact_match"]) for row in rows]),
            "sensitive_token_recall": {
                "n_samples_with_sensitive_tokens": len(sensitive_rows),
                "stats": _mean_std([
                    float(row["sensitive_token_recall"]) for row in sensitive_rows
                ]),
            },
            "psnr_db": _mean_std([float(row["psnr_db"]) for row in rows]),
            "reconstruction_score": _mean_std([
                float(row.get("reconstruction_score", 0.0)) for row in rows
            ]),
            "leak_rate_char_ge_20pct": _mean_std([
                float(row["char_accuracy"] >= leak_threshold) for row in rows
            ]),
        }

    best_rows: list[dict] = []
    for sample in sorted({row["name"] for row in sample_rows}):
        rows = [row for row in sample_rows if row["name"] == sample]
        best = max(
            rows,
            key=lambda row: (
                float(row["char_accuracy"]),
                float(row["word_accuracy"]),
                float(row["sensitive_token_recall"]),
            ),
        )
        best_rows.append(best)

    sensitive_best = [
        row for row in best_rows if int(row.get("sensitive_token_count", 0)) > 0
    ]
    return {
        "attacks": attack_summary,
        "best_attack_per_sample": {
            "char_accuracy": _mean_std([
                float(row["char_accuracy"]) for row in best_rows
            ]),
            "word_accuracy": _mean_std([
                float(row["word_accuracy"]) for row in best_rows
            ]),
            "exact_match": _mean_std([
                float(row["exact_match"]) for row in best_rows
            ]),
            "sensitive_token_recall": {
                "n_samples_with_sensitive_tokens": len(sensitive_best),
                "stats": _mean_std([
                    float(row["sensitive_token_recall"]) for row in sensitive_best
                ]),
            },
            "leak_rate_char_ge_20pct": _mean_std([
                float(row["char_accuracy"] >= leak_threshold) for row in best_rows
            ]),
            "attack_wins": {
                attack: sum(1 for row in best_rows if row["attack"] == attack)
                for attack in attacks
            },
        },
    }


def run_corpus_strong_camera_attacks(
    n: int = 4,
    epsilon: float = 8 / 255,
    cycles: int = 2,
    engine: str = "tesseract",
    output_dir: str = "experiments/results",
    max_samples: int | None = None,
    evaluator: OCREvaluator | None = None,
    corpus: tuple[list[np.ndarray], list[str], list[str]] | None = None,
    metadata: dict | None = None,
    with_noise: bool = True,
    ocr_timeout: float | None = 4.0,
    progress_interval: int = 10,
    save: bool = True,
) -> dict:
    """
    Run screen-camera-inspired strong attacks across the publication corpus.

    The result intentionally reports both protected single-frame baselines and
    full-cycle reconstruction attacks. This makes the threat-model boundary
    auditable instead of hiding attacks that can integrate a complete cycle.
    """
    if cycles <= 0:
        raise ValueError("cycles must be positive")
    if max_samples is not None and max_samples <= 0:
        raise ValueError("max_samples must be positive when provided")
    if progress_interval < 0:
        raise ValueError("progress_interval must be non-negative")

    if corpus is None:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from experiments.build_corpus import load_corpus, load_corpus_metadata

        images, truths, names = load_corpus()
        corpus_metadata = load_corpus_metadata()
    else:
        images, truths, names = corpus
        corpus_metadata = metadata or {}

    if max_samples is not None:
        images = images[:max_samples]
        truths = truths[:max_samples]
        names = names[:max_samples]

    evaluator = evaluator or OCREvaluator(timeout=ocr_timeout)
    if engine not in evaluator.engines:
        raise ValueError(f"OCR engine is not available: {engine}")

    cam = CameraSimulator(CameraParams(readout_time=15e-6, exposure_time=1 / 240))
    sample_rows: list[dict] = []
    total_samples = len(images)
    for sample_idx, (image, truth, name) in enumerate(zip(images, truths, names)):
        if progress_interval and (
            sample_idx == 0
            or (sample_idx + 1) % progress_interval == 0
            or sample_idx + 1 == total_samples
        ):
            print(f"  强攻击语料进度 {sample_idx + 1}/{total_samples}: {name}")
        subframes = compose_protected_subframes(
            image,
            n=n,
            epsilon=epsilon,
            cycles=cycles,
            cycle_start=sample_idx * cycles,
            with_noise=with_noise,
        )
        attack_frames: dict[str, tuple[np.ndarray, dict]] = {
            "global_shutter_slot0": (subframes[0], {"attack": "global_shutter"}),
            "temporal_average_cycle": (
                cam.temporal_averaging_attack(subframes, n, randomize_order=False),
                {"attack": "temporal_average", "frames": n},
            ),
        }
        for attack_name, entry in cam.screen_camera_attack_suite(
            subframes,
            cycle_length=n,
        ).items():
            attack_frames[attack_name] = (entry["frame"], entry["metadata"])

        for attack_name, (frame, attack_meta) in attack_frames.items():
            ocr_error = ""
            try:
                ocr = evaluator.evaluate_single(frame, truth, engine)
                text = ocr.text
                char_accuracy = ocr.char_accuracy
                word_accuracy = ocr.word_accuracy
            except Exception as exc:
                text = ""
                recovery_on_error = text_recovery_metrics(text, truth)
                char_accuracy = recovery_on_error["char_accuracy"]
                word_accuracy = recovery_on_error["word_accuracy"]
                ocr_error = str(exc)
            recovery = text_recovery_metrics(text, truth)
            sample_rows.append({
                "name": name,
                "attack": attack_name,
                "metadata": corpus_metadata.get(name, {}),
                "char_accuracy": char_accuracy,
                "word_accuracy": word_accuracy,
                "exact_match": recovery["exact_match"],
                "sensitive_token_recall": recovery["sensitive_token_recall"],
                "sensitive_token_count": recovery["sensitive_token_count"],
                "psnr_db": _psnr_db(image, frame),
                "reconstruction_score": float(attack_meta.get("score", 0.0)),
                "attack_metadata": attack_meta,
                "recognized_text": text[:160],
                "ocr_error": ocr_error,
            })

    report = {
        "config": {
            "n": n,
            "epsilon": epsilon,
            "cycles": cycles,
            "engine": engine,
            "n_samples": len(images),
            "with_noise": with_noise,
            "ocr_timeout": ocr_timeout,
            "leak_threshold_char_accuracy": 0.20,
        },
        "summary": summarize_strong_attack_rows(sample_rows),
        "samples": sample_rows,
    }

    if save:
        out = Path(output_dir) / "corpus_strong_camera_attack.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"强相机攻击语料评测已保存: {out}")

    return report


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

        for sample_idx, (img, gt) in enumerate(zip(self.test_images, self.ground_truths)):
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
                noise_base, _, _ = injector.generate_rotating_noise(img_f, cycle=sample_idx)
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
    merge_existing: bool = False,
    progress_interval: int = 0,
) -> dict:
    """
    语料级多 OCR 引擎评测（改进项 C2）。

    在整个测试语料上运行多个 OCR 引擎，报告原始帧与单子帧的字符准确率
    mean±std，提供统计显著性（样本量 = 语料图片数）。

    Returns:
        dict: 每引擎的 {original_mean/std/ci95, subframe_mean/std/ci95, paired_reduction, n_samples}
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from experiments.build_corpus import load_corpus, load_corpus_metadata

    if progress_interval < 0:
        raise ValueError("progress_interval must be non-negative")

    images, truths, names = load_corpus()
    metadata = load_corpus_metadata()
    evaluator = OCREvaluator()
    avail = evaluator.engines if engines is None else engines
    avail = [e for e in avail if e in evaluator.engines]
    out = Path(output_dir) / "corpus_multi_engine.json"

    report = {}
    if merge_existing and out.exists():
        with open(out, encoding="utf-8") as f:
            existing = json.load(f)
        if isinstance(existing, dict):
            report.update(existing)

    for engine in avail:
        orig_accs, sf_accs, reductions = [], [], []
        sample_rows = []
        total_samples = len(images)
        for sample_idx, (img, gt, name) in enumerate(zip(images, truths, names)):
            if progress_interval and (
                sample_idx == 0
                or (sample_idx + 1) % progress_interval == 0
                or sample_idx + 1 == total_samples
            ):
                print(
                    f"  [{engine}] OCR 进度 {sample_idx + 1}/{total_samples}: {name}",
                    flush=True,
                )
            subframes = compose_protected_subframes(
                img,
                n=n,
                epsilon=epsilon,
                cycles=1,
                cycle_start=sample_idx,
            )

            res = evaluator.evaluate_protection(img, subframes, gt, engine)
            orig_accs.append(res["original_char_acc"])
            sf_accs.append(res["mean_subframe_acc"])
            reductions.append(res["accuracy_reduction"])
            sample_rows.append({
                "name": name,
                "metadata": metadata.get(name, {}),
                "original_char_acc": res["original_char_acc"],
                "subframe_char_acc": res["mean_subframe_acc"],
                "original_word_acc": res["original_word_acc"],
                "subframe_word_acc": res["mean_subframe_word_acc"],
                "original_exact_match": res["original_exact_match"],
                "subframe_exact_match": res["mean_subframe_exact_match"],
                "original_sensitive_token_recall": res["original_sensitive_token_recall"],
                "subframe_sensitive_token_recall": res["mean_subframe_sensitive_token_recall"],
                "sensitive_token_count": res["sensitive_token_count"],
                "accuracy_reduction": res["accuracy_reduction"],
            })

        original_stats = _mean_std(orig_accs)
        subframe_stats = _mean_std(sf_accs)
        reduction_stats = _mean_std(reductions)
        report[engine] = {
            "n_samples": len(images),
            "n_categories": len({metadata.get(name, {}).get("category", "unknown") for name in names}),
            "original_mean": original_stats["mean"],
            "original_std": original_stats["std"],
            "original_ci95": original_stats["ci95"],
            "subframe_mean": subframe_stats["mean"],
            "subframe_std": subframe_stats["std"],
            "subframe_ci95": subframe_stats["ci95"],
            "paired_reduction": reduction_stats,
            "recovery_metrics": summarize_corpus_recovery_metrics(sample_rows),
            "strata": {
                "category": summarize_corpus_strata(sample_rows, "category"),
                "language": summarize_corpus_strata(sample_rows, "language"),
                "layout": summarize_corpus_strata(sample_rows, "layout"),
                "font_size": summarize_corpus_strata(sample_rows, "font_size"),
            },
            "samples": sample_rows,
        }

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n语料级多引擎评测（n={n}, 样本={len(images)}）:")
    for eng, r in report.items():
        if "original_ci95" not in r or "subframe_ci95" not in r or "paired_reduction" not in r:
            print(f"  [{eng}] 保留既有结果（旧格式，未包含 CI/配对降幅字段）")
            continue
        orig_ci = r["original_ci95"]
        sf_ci = r["subframe_ci95"]
        red = r["paired_reduction"]
        red_ci = red["ci95"]
        print(f"  [{eng}] 原始 {r['original_mean']:.1%}±{r['original_std']:.1%}  "
              f"(95%CI {orig_ci['low']:.1%}-{orig_ci['high']:.1%})  "
              f"→ 子帧 {r['subframe_mean']:.1%}±{r['subframe_std']:.1%}  "
              f"(95%CI {sf_ci['low']:.1%}-{sf_ci['high']:.1%});  "
              f"配对降幅 {red['mean']:.1%} "
              f"(95%CI {red_ci['low']:.1%}-{red_ci['high']:.1%})")
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
