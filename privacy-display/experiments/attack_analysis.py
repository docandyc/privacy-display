"""
攻击鲁棒性分析（毕设核心实验）

本脚本系统验证各攻击场景下的防御效果，**包括暴露方案根本局限的
多帧时域平均攻击**——这是毕设答辩"局限性与未来工作"的核心数据。

运行: python experiments/attack_analysis.py
"""

import sys
import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from main import _make_test_image
from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.core.noise_injector import NoiseInjector
from src.attack.ocr_evaluator import OCREvaluator
from src.attack.camera_simulator import CameraSimulator, CameraParams
from src.evaluation.benchmark import run_corpus_strong_camera_attacks


def build_subframes(img, n, epsilon, n_cycles, with_noise=True):
    """构造跨 n_cycles 个周期的子帧序列（每周期掩模独立重生成）。"""
    h, w = img.shape[:2]
    gen = MaskGenerator(w, h, n)
    composer = SubframeComposer(n=n, gamma=1.0)
    injector = NoiseInjector(n=n, epsilon=epsilon)

    all_sf = []
    pedestal = epsilon * 255 if with_noise else 0.0
    for cycle in range(n_cycles):
        masks = gen.generate(cycle)
        if with_noise:
            nb, _, _ = injector.generate_rotating_noise(
                img.astype(np.float32) / 255.0,
                cycle=cycle,
            )
            sn_f = injector.split_complementary(nb)
            sn = [(x * 255 + pedestal).astype(np.float32) for x in sn_f]
        else:
            sn = None
        all_sf.extend(composer.compose(img, masks, sn))
    return all_sf


def main():
    gt = "The quick brown fox 12345 PASSWORD"
    img = _make_test_image(gt)
    ev = OCREvaluator(engines=["tesseract"])
    cam = CameraSimulator(CameraParams(readout_time=15e-6, exposure_time=1/240))

    n, epsilon = 4, 8 / 255
    orig = ev.evaluate_single(img, gt, "tesseract")
    summary = {
        "config": {
            "n": n,
            "epsilon": epsilon,
            "display_rate_hz": 240,
            "ocr_engine": "tesseract",
            "ground_truth": gt,
        },
        "baseline": {
            "char_accuracy": orig.char_accuracy,
            "text": orig.text,
        },
        "global_shutter_single": [],
        "temporal_average": {},
        "screen_camera_strong_attacker": {},
        "rolling_shutter": {},
        "long_exposure": {},
    }

    print("=" * 60)
    print("攻击鲁棒性分析  (n=4, ε=8/255, 显示 240Hz)")
    print("=" * 60)
    print(f"\n[基线] 原始帧 OCR 准确率: {orig.char_accuracy:.1%}\n")

    # --- 攻击 1: 单帧捕获（全局快门）---
    sf = build_subframes(img, n, epsilon, n_cycles=8)
    print("[攻击1] 全局快门单帧捕获:")
    accs = []
    for i in range(4):
        result = ev.evaluate_single(sf[i], gt, "tesseract")
        accs.append(result.char_accuracy)
        summary["global_shutter_single"].append({
            "slot": i,
            "char_accuracy": result.char_accuracy,
            "text": result.text,
        })
    print(f"  4 个子帧 OCR 准确率: {[f'{a:.0%}' for a in accs]}")
    print(f"  → 防御{'有效 ✓' if max(accs) < 0.2 else '失败 ✗'}\n")

    # --- 攻击 2: 时域平均（多帧叠加）---
    print("[攻击2] 时域平均攻击（攻击者叠加 k 帧）:")
    for k in [1, 2, 3, 4, 8, 16]:
        stacked = cam.temporal_averaging_attack(sf, k, randomize_order=False)
        r = ev.evaluate_single(stacked, gt, "tesseract")
        flag = "✓防御" if r.char_accuracy < 0.2 else "✗失守"
        summary["temporal_average"][str(k)] = {
            "char_accuracy": r.char_accuracy,
            "text": r.text,
            "status": "defended" if r.char_accuracy < 0.2 else "leaked",
        }
        print(f"  叠加 {k:2d} 帧: OCR={r.char_accuracy:5.1%}  [{flag}]  {r.text[:32]!r}")
    print("  ⚠️ 关键发现: 叠加 ≥n 帧覆盖完整周期后, 互斥完备掩模被平均还原,")
    print("     对抗噪声因 ΣN_k=0 同时被抵消 → 这是方案的根本数学局限。\n")

    # --- 攻击 2B: 屏幕-相机通信启发的强攻击者 ---
    print("[攻击2B] 强相机攻击者（相位搜索/差分累加/单通道恢复）:")
    scc_attacks = cam.screen_camera_attack_suite(sf[: n * 2], cycle_length=n)
    for name, entry in scc_attacks.items():
        frame = entry["frame"]
        meta = entry["metadata"]
        r = ev.evaluate_single(frame, gt, "tesseract")
        flag = "✓防御" if r.char_accuracy < 0.2 else "✗泄露"
        summary["screen_camera_strong_attacker"][name] = {
            **meta,
            "char_accuracy": r.char_accuracy,
            "text": r.text,
            "status": "defended" if r.char_accuracy < 0.2 else "leaked",
        }
        detail = ""
        if "best_offset" in meta:
            detail = f", offset={meta['best_offset']}"
        if "channel" in meta:
            detail += f", channel={meta['channel']}"
        print(
            f"  {name:20s}: OCR={r.char_accuracy:5.1%} [{flag}]"
            f", score={meta['score']:.2f}{detail}"
        )
    print("  该组攻击模拟 DeepLight/Revelio/BRIGHTNESS 式攻击者：知道存在时域调制，")
    print("  会搜索周期相位、累加差分，并检查蓝通道等潜在相机侧信道。\n")

    # --- 攻击 3: 卷帘快门 ---
    print("[攻击3] 卷帘快门混合采样:")
    rolling = cam.capture_rolling_shutter(sf, 240.0)
    r = ev.evaluate_single(rolling, gt, "tesseract")
    contaminated = cam.count_contaminated_rows(img.shape[0], 240.0, 0.002)
    summary["rolling_shutter"] = {
        "char_accuracy": r.char_accuracy,
        "text": r.text,
        "contaminated_rows": contaminated,
        "total_rows": int(img.shape[0]),
    }
    print(f"  混合帧 OCR={r.char_accuracy:.1%}, 污染行数={contaminated}/{img.shape[0]}")
    print(f"  → 防御{'有效 ✓' if r.char_accuracy < 0.2 else '失败 ✗'}\n")

    # --- 攻击 4: 长曝光（反色帧防御对比）---
    print("[攻击4] 长曝光积分（反色帧防御对比）:")
    composer = SubframeComposer(n=n, gamma=1.0)
    inv_frames = [composer.compose_inversion_frame(s) for s in sf[:n]]
    le_no_inv = cam.long_exposure_attack(sf[:n], None, 4)
    le_with_inv = cam.long_exposure_attack(sf[:n], inv_frames, 4)
    r1 = ev.evaluate_single(le_no_inv, gt, "tesseract")
    r2 = ev.evaluate_single(le_with_inv, gt, "tesseract")
    summary["long_exposure"] = {
        "without_inversion": {
            "char_accuracy": r1.char_accuracy,
            "text": r1.text,
        },
        "with_inversion": {
            "char_accuracy": r2.char_accuracy,
            "text": r2.text,
        },
    }
    print(f"  无反色帧:  OCR={r1.char_accuracy:.1%}")
    print(f"  插入反色帧: OCR={r2.char_accuracy:.1%}  (反色帧使积分趋向中性灰)")

    # --- 攻击 5: 语料级强攻击统计 ---
    print("\n[攻击5] 120 样本文本语料上的强相机攻击统计:")
    corpus_report = run_corpus_strong_camera_attacks(
        n=n,
        epsilon=epsilon,
        cycles=2,
        engine="tesseract",
        ocr_timeout=4.0,
        progress_interval=10,
        output_dir=str(ROOT / "experiments" / "results"),
    )
    best = corpus_report["summary"]["best_attack_per_sample"]
    summary["corpus_strong_attacker"] = {
        "result_path": "experiments/results/corpus_strong_camera_attack.json",
        "config": corpus_report["config"],
        "summary": corpus_report["summary"],
    }
    print(
        "  最强攻击逐样本择优: "
        f"字符恢复均值={best['char_accuracy']['mean']:.1%}, "
        f"泄露率(字符准确率≥20%)={best['leak_rate_char_ge_20pct']['mean']:.1%}"
    )
    print("  该结果用于诚实界定威胁模型：单帧有效，完整周期积分可恢复。")

    out = ROOT / "experiments" / "results" / "attack_analysis_strong_camera.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[结果] JSON 已保存: {out}")

    print("\n" + "=" * 60)
    print("结论: 单帧抽帧/流式识别防御有效; 多帧时域平均是本方案")
    print("      （及视觉暂留类方案普遍）的根本局限——人眼积分与相机")
    print("      积分是同一数学操作, 能被人眼还原即能被相机还原。")
    print("      可行缓解方向: 视角差异化掩模 / 非线性时域调制 /")
    print("      运动内容自适应（见 README 局限性分析）。")
    print("=" * 60)


if __name__ == "__main__":
    main()
