"""
攻击鲁棒性分析（毕设核心实验）

本脚本系统验证各攻击场景下的防御效果，**包括暴露方案根本局限的
多帧时域平均攻击**——这是毕设答辩"局限性与未来工作"的核心数据。

运行: python experiments/attack_analysis.py
"""

import sys
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
            nb = injector.generate_fgsm_noise(img.astype(np.float32) / 255.0)
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

    print("=" * 60)
    print("攻击鲁棒性分析  (n=4, ε=8/255, 显示 240Hz)")
    print("=" * 60)
    print(f"\n[基线] 原始帧 OCR 准确率: {orig.char_accuracy:.1%}\n")

    # --- 攻击 1: 单帧捕获（全局快门）---
    sf = build_subframes(img, n, epsilon, n_cycles=8)
    print("[攻击1] 全局快门单帧捕获:")
    accs = [ev.evaluate_single(sf[i], gt, "tesseract").char_accuracy for i in range(4)]
    print(f"  4 个子帧 OCR 准确率: {[f'{a:.0%}' for a in accs]}")
    print(f"  → 防御{'有效 ✓' if max(accs) < 0.2 else '失败 ✗'}\n")

    # --- 攻击 2: 时域平均（多帧叠加）---
    print("[攻击2] 时域平均攻击（攻击者叠加 k 帧）:")
    for k in [1, 2, 3, 4, 8, 16]:
        stacked = cam.temporal_averaging_attack(sf, k, randomize_order=False)
        r = ev.evaluate_single(stacked, gt, "tesseract")
        flag = "✓防御" if r.char_accuracy < 0.2 else "✗失守"
        print(f"  叠加 {k:2d} 帧: OCR={r.char_accuracy:5.1%}  [{flag}]  {r.text[:32]!r}")
    print("  ⚠️ 关键发现: 叠加 ≥n 帧覆盖完整周期后, 互斥完备掩模被平均还原,")
    print("     对抗噪声因 ΣN_k=0 同时被抵消 → 这是方案的根本数学局限。\n")

    # --- 攻击 3: 卷帘快门 ---
    print("[攻击3] 卷帘快门混合采样:")
    rolling = cam.capture_rolling_shutter(sf, 240.0)
    r = ev.evaluate_single(rolling, gt, "tesseract")
    contaminated = cam.count_contaminated_rows(img.shape[0], 240.0, 0.002)
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
    print(f"  无反色帧:  OCR={r1.char_accuracy:.1%}")
    print(f"  插入反色帧: OCR={r2.char_accuracy:.1%}  (反色帧使积分趋向中性灰)")

    print("\n" + "=" * 60)
    print("结论: 单帧抽帧/流式识别防御有效; 多帧时域平均是本方案")
    print("      （及视觉暂留类方案普遍）的根本局限——人眼积分与相机")
    print("      积分是同一数学操作, 能被人眼还原即能被相机还原。")
    print("      可行缓解方向: 视角差异化掩模 / 非线性时域调制 /")
    print("      运动内容自适应（见 README 局限性分析）。")
    print("=" * 60)


if __name__ == "__main__":
    main()
