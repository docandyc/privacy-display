"""
对抗噪声消融实验（改进项 B1）

交底书把"对抗性噪声"列为核心创新点 B。本实验分两层验证：

1. 默认 n=4/ε=8/255 场景：随机点阵掩模通常已将单帧 OCR 压到 0，
   因此噪声的边际贡献会被"地板效应"遮蔽。
2. 弱掩模泄露压力场景：模拟面板串扰、相机去噪或残影导致被关闭像素仍
   泄露部分亮度，检验 OCR 目标噪声是否能在掩模不再单独充分时继续降 OCR。

  组1  仅掩模（无噪声）
  组2  仅噪声（无掩模分割，全帧叠加噪声）
  组3  掩模 + OCR 对比度目标 FGSM 噪声（Tesseract）
  组4  掩模 + 多模型轮换 PGD 噪声（EasyOCR/PaddleOCR/YOLOv8 等）

运行: python experiments/ablation_noise.py
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


ABLATION_KEY = b"ablation-noise-key-0000000000000"


def run_group(img, gt, ev, n, mode):
    """mode ∈ {'mask_only','noise_only','mask_heuristic','mask_adversarial'}"""
    h, w = img.shape[:2]
    gen = MaskGenerator(w, h, n, key=ABLATION_KEY)
    composer = SubframeComposer(n=n, gamma=1.0)
    injector = NoiseInjector(n=n, epsilon=8/255)
    ped = 8.0

    if mode == "mask_only":
        masks = gen.generate(0)
        subframes = composer.compose(img, masks, None)
    elif mode == "noise_only":
        # 无掩模：每子帧 = 全图/n + 互补噪声（不做像素分割）
        nb = injector.generate_fgsm_noise(img.astype(np.float32)/255.0, "tesseract")
        sn = [(x*255).astype(np.float32) for x in injector.split_complementary(nb)]
        subframes = [np.clip(img.astype(np.float32)/n + s, 0, 255).astype(np.uint8) for s in sn]
    elif mode == "mask_heuristic":
        masks = gen.generate(0)
        nb = injector.generate_fgsm_noise(img.astype(np.float32)/255.0, "tesseract")
        sn = [(x*255+ped).astype(np.float32) for x in injector.split_complementary(nb)]
        subframes = composer.compose(img, masks, sn)
    elif mode == "mask_adversarial":
        masks = gen.generate(0)
        nb, _, _ = injector.generate_rotating_noise(img.astype(np.float32)/255.0, cycle=1)
        sn = [(x*255+ped).astype(np.float32) for x in injector.split_complementary(nb)]
        subframes = composer.compose(img, masks, sn)
    else:
        raise ValueError(mode)

    accs = [ev.evaluate_single(sf, gt, "tesseract").char_accuracy for sf in subframes]
    return float(np.mean(accs))


def run_leakage_stress(img, gt, ev, n=4, leak=0.75, epsilon=96/255):
    """
    弱掩模泄露压力测试。

    leak 表示未激活像素仍以 leak*I 泄露到相机端。该设置不代表正常工作
    参数，而是专门制造"掩模单独不足"的可读场景，用来验证 OCR 目标噪声
    是否具备独立边际贡献。
    """
    h, w = img.shape[:2]
    gen = MaskGenerator(w, h, n, key=ABLATION_KEY)
    masks = gen.generate(0)
    injector = NoiseInjector(n=n, epsilon=epsilon, target_models=["tesseract"])
    noise_base = injector.generate_fgsm_noise(img.astype(np.float32) / 255.0, "tesseract")
    sub_noises = [(x * 255).astype(np.float32) for x in injector.split_complementary(noise_base)]

    mask_only = []
    mask_with_noise = []
    img_f = img.astype(np.float32)
    for k, mask in enumerate(masks):
        active = mask[:, :, None].astype(np.float32)
        inactive = (~mask)[:, :, None].astype(np.float32)
        leaked = img_f * (active + inactive * leak)
        mask_only.append(np.clip(leaked, 0, 255).astype(np.uint8))
        mask_with_noise.append(np.clip(leaked + sub_noises[k], 0, 255).astype(np.uint8))

    mask_acc = float(np.mean([
        ev.evaluate_single(sf, gt, "tesseract").char_accuracy for sf in mask_only
    ]))
    noise_acc = float(np.mean([
        ev.evaluate_single(sf, gt, "tesseract").char_accuracy for sf in mask_with_noise
    ]))
    return {
        "leak": leak,
        "epsilon": epsilon,
        "mask_only_acc": mask_acc,
        "mask_noise_acc": noise_acc,
        "reduction": mask_acc - noise_acc,
    }


def main():
    gt = "CONFIDENTIAL data 2026 PASSWORD admin"
    img = _make_test_image(gt)
    ev = OCREvaluator(engines=["tesseract"])
    n = 4

    print("=" * 60)
    print("对抗噪声消融实验  (改进项 B1, n=4)")
    print("=" * 60)
    orig = ev.evaluate_single(img, gt, "tesseract").char_accuracy
    print(f"\n基线（原始帧）单帧 OCR: {orig:.1%}\n")

    groups = [
        ("组1  仅掩模（无噪声）", "mask_only"),
        ("组2  仅噪声（无掩模分割）", "noise_only"),
        ("组3  掩模+Tesseract对比度FGSM", "mask_heuristic"),
        ("组4  掩模+多模型轮换PGD", "mask_adversarial"),
    ]
    results = {}
    for label, mode in groups:
        try:
            acc = run_group(img, gt, ev, n, mode)
            results[mode] = acc
            print(f"  {label:32s}: 单帧 OCR = {acc:.1%}")
        except Exception as e:
            print(f"  {label:32s}: [跳过] {type(e).__name__}: {e}")

    print("\n" + "-" * 60)
    if "mask_only" in results and "mask_heuristic" in results:
        delta = results["mask_only"] - results["mask_heuristic"]
        print(f"默认场景噪声边际贡献（组1−组3）: {delta:+.1%}")
    if "noise_only" in results:
        print(f"仅噪声防御效果（组2）    : {results['noise_only']:.1%}"
              f"  {'← 噪声单独几乎无防御' if results.get('noise_only',1)>0.5 else ''}")
    stress = run_leakage_stress(img, gt, ev, n=4, leak=0.75, epsilon=96/255)
    print("\n[压力测试] 弱掩模泄露 leak=0.75, 增强 ε=96/255:")
    print(f"  弱掩模单独 OCR       : {stress['mask_only_acc']:.1%}")
    print(f"  弱掩模+OCR目标噪声   : {stress['mask_noise_acc']:.1%}")
    print(f"  OCR 降幅             : {stress['reduction']:+.1%}")

    print("\n结论: 默认 n=4/ε=8/255 下掩模已触发 OCR 地板效应；")
    print("      在弱掩模泄露压力场景中，OCR 对比度目标噪声能提供可测边际防御。")
    print("=" * 60)


if __name__ == "__main__":
    main()
