"""
学习型去混淆攻击实验（G5）

用 tiny U-Net 训练“单子帧 -> 原图”的低分辨率重构攻击。该实验是 CPU 友好
PoC 下界，不声称代表最强学习攻击。
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import _make_test_image
from src.attack.reconstruction_attack import (
    reconstruct_inpaint_single,
    reconstruct_unet_single,
    train_tiny_unet_reconstructor,
)
from src.core.mask_generator import MaskGenerator
from src.core.subframe_composer import SubframeComposer
from src.evaluation.metrics import compute_ssim


def _psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = np.mean((a.astype(np.float32) - b.astype(np.float32)) ** 2)
    return float(10 * np.log10(255**2 / mse)) if mse > 0 else 99.0


def _subframe_pair(text: str, cycle: int, n: int = 4) -> tuple[np.ndarray, np.ndarray]:
    original = _make_test_image(text)
    h, w = original.shape[:2]
    gen = MaskGenerator(w, h, n, key=b"unet-reconstruction-key-00000000")
    composer = SubframeComposer(n=n, gamma=1.0)
    masks = gen.generate(cycle)
    subframes = composer.compose(original, masks, None)
    return subframes[0], original


def run_unet_reconstruction(
    epochs: int = 3,
    output_dir: str = "experiments/results",
) -> dict:
    texts = [
        "CONFIDENTIAL 2026",
        "PASSWORD admin123",
        "FINANCIAL DATA Q4",
        "TOKEN eyJhbGc",
        "PRIVATE 用户数据",
        "HOLDOUT SECRET 42",
    ]
    pairs = [_subframe_pair(text, i) for i, text in enumerate(texts)]
    train_pairs = pairs[:-1]
    holdout_masked, holdout_original = pairs[-1]

    model, meta = train_tiny_unet_reconstructor(
        train_pairs,
        epochs=epochs,
        size=(64, 32),
        seed=0,
    )
    recon = reconstruct_unet_single(holdout_masked, model, size=(64, 32))
    inpaint = reconstruct_inpaint_single(holdout_masked)

    report = {
        "method": "tiny_unet_single_subframe",
        "training": meta,
        "holdout": {
            "unet": {
                "psnr_db": _psnr(holdout_original, recon),
                "ssim": compute_ssim(holdout_original, recon),
            },
            "inpaint_baseline": {
                "psnr_db": _psnr(holdout_original, inpaint),
                "ssim": compute_ssim(holdout_original, inpaint),
            },
        },
    }

    out = Path(output_dir) / "unet_reconstruction.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"结果已保存: {out}")
    return report


if __name__ == "__main__":
    run_unet_reconstruction()
