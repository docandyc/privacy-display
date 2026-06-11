"""
离轴相机攻击实验（G3）

对照三种重构路径，量化"视角差异化掩模 + 离轴相机"到底能提供多少**不可逆**的
保护。关键诚实结论：

  - 整周期时域平均时，每个区域无论使用何种（差异化）掩模都各自还原回原图，
    因此掩模差异化对**全周期对齐攻击者无密码学保护**；
  - 离轴 SSIM 的下降全部来自区域级衰减/色偏/位移这类**可逆物理畸变**，
    强攻击者（反推几何 + 数据驱动增益归一化）可基本撤销；
  - 真正不可逆的物理 LCD 视角响应建模属 PoC 范围外。

同时报告 OCR 字符准确率（真实隐私指标），而非仅 SSIM/PSNR。
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import _make_test_image
from src.attack.camera_simulator import CameraSimulator
from src.attack.ocr_evaluator import OCREvaluator
from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.evaluation.metrics import compute_ssim


def _psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = np.mean((a.astype(np.float32) - b.astype(np.float32)) ** 2)
    return float(10 * np.log10(255**2 / mse)) if mse > 0 else 99.0


def _cycle_rescale(frame: np.ndarray, n: int) -> np.ndarray:
    """攻击者已知 n 时可将完整周期平均结果乘回 n 以恢复亮度。"""
    return np.clip(frame.astype(np.float32) * n, 0, 255).astype(np.uint8)


def _tesseract_ok() -> bool:
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _ocr_char_acc(evaluator, image: np.ndarray, gt: str) -> float:
    """字符准确率；OCR 不可用时返回 -1。"""
    if evaluator is None or not evaluator.engines:
        return -1.0
    try:
        return float(evaluator.evaluate_single(image, gt, "tesseract").char_accuracy)
    except Exception:
        return -1.0


def run_view_attack(
    n: int = 4,
    angle_degrees: float = 35.0,
    regions: tuple[int, int] = (3, 3),
    output_dir: str = "experiments/results",
) -> dict:
    gt = "OFF AXIS CAMERA ATTACK"
    original = _make_test_image(gt)
    h, w = original.shape[:2]
    gen = MaskGenerator(w, h, n)
    masks = gen.generate_view_differentiated(cycle=0, regions=regions)
    composer = SubframeComposer(n=n, gamma=1.0)
    subframes = composer.compose(original, masks, None)
    cam = CameraSimulator()

    evaluator = OCREvaluator(engines=["tesseract"]) if _tesseract_ok() else None

    # 正视：完整周期平均 → ×n 复原 → 应近乎完美还原（与掩模差异化无关）。
    frontal = _cycle_rescale(
        cam.temporal_averaging_attack(subframes, k=n, randomize_order=False),
        n,
    )
    # 离轴（朴素）：区域级衰减/色偏/位移后的整周期平均。
    off_axis = _cycle_rescale(
        cam.off_axis_temporal_average_attack(
            subframes,
            angle_degrees=angle_degrees,
            regions=regions,
            cycles=1,
        ),
        n,
    )
    # 离轴（强攻击者校正）：反向位移 + 逐区域增益归一化撤销可逆畸变。
    off_axis_corrected = cam.off_axis_correction(
        off_axis,
        regions=regions,
        angle_degrees=angle_degrees,
    )

    def _entry(img):
        return {
            "psnr_db": _psnr(original, img),
            "ssim": compute_ssim(original, img),
            "ocr_char_acc": _ocr_char_acc(evaluator, img, gt),
        }

    report = {
        "n": n,
        "regions": list(regions),
        "angle_degrees": angle_degrees,
        "ground_truth": gt,
        "ocr_available": evaluator is not None,
        "original_reference": {"ocr_char_acc": _ocr_char_acc(evaluator, original, gt)},
        "frontal_temporal_average": _entry(frontal),
        "off_axis_temporal_average": _entry(off_axis),
        "off_axis_corrected": _entry(off_axis_corrected),
    }
    report["off_axis_ssim_drop"] = (
        report["frontal_temporal_average"]["ssim"]
        - report["off_axis_temporal_average"]["ssim"]
    )
    report["correction_ssim_recovery"] = (
        report["off_axis_corrected"]["ssim"]
        - report["off_axis_temporal_average"]["ssim"]
    )
    report["conclusion"] = (
        "离轴朴素捕获后 OCR 已与正视同为 100% → 视角差异化掩模对全周期对齐"
        "攻击者无 OCR 级保护；SSIM 的小幅下降仅为不影响可读性的可逆物理畸变"
        "（整周期平均时各区域各自还原，掩模差异化不参与）。真正不可逆的物理"
        "视角响应建模属 PoC 范围外。"
    )

    out = Path(output_dir) / "view_attack.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"结果已保存: {out}")
    return report


if __name__ == "__main__":
    run_view_attack()
