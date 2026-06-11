"""
离轴相机攻击实验（G3）

比较正视完整周期时域平均与离轴区域响应模型下的重构效果。结果用于补齐
交底书 7.2 “视角差异化掩模/离轴攻击”验证缺口。
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import _make_test_image
from src.attack.camera_simulator import CameraSimulator
from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.evaluation.metrics import compute_ssim


def _psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = np.mean((a.astype(np.float32) - b.astype(np.float32)) ** 2)
    return float(10 * np.log10(255**2 / mse)) if mse > 0 else 99.0


def _cycle_rescale(frame: np.ndarray, n: int) -> np.ndarray:
    """攻击者已知 n 时可将完整周期平均结果乘回 n 以恢复亮度。"""
    return np.clip(frame.astype(np.float32) * n, 0, 255).astype(np.uint8)


def run_view_attack(
    n: int = 4,
    angle_degrees: float = 35.0,
    regions: tuple[int, int] = (3, 3),
    output_dir: str = "experiments/results",
) -> dict:
    original = _make_test_image("OFF AXIS CAMERA ATTACK 视角差异化")
    h, w = original.shape[:2]
    gen = MaskGenerator(w, h, n)
    masks = gen.generate_view_differentiated(cycle=0, regions=regions)
    composer = SubframeComposer(n=n, gamma=1.0)
    subframes = composer.compose(original, masks, None)
    cam = CameraSimulator()

    frontal = _cycle_rescale(
        cam.temporal_averaging_attack(subframes, k=n, randomize_order=False),
        n,
    )
    off_axis = _cycle_rescale(
        cam.off_axis_temporal_average_attack(
            subframes,
            angle_degrees=angle_degrees,
            regions=regions,
            cycles=1,
        ),
        n,
    )

    report = {
        "n": n,
        "regions": list(regions),
        "angle_degrees": angle_degrees,
        "frontal_temporal_average": {
            "psnr_db": _psnr(original, frontal),
            "ssim": compute_ssim(original, frontal),
        },
        "off_axis_temporal_average": {
            "psnr_db": _psnr(original, off_axis),
            "ssim": compute_ssim(original, off_axis),
        },
    }
    report["off_axis_ssim_drop"] = (
        report["frontal_temporal_average"]["ssim"]
        - report["off_axis_temporal_average"]["ssim"]
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
