import numpy as np

from src.demo.visual_integration import analyze_single_frame_readability


def test_active_ratio_ignores_noise_pedestal():
    original = np.full((8, 8, 3), 100, dtype=np.uint8)
    masks = []
    for idx in range(4):
        mask = np.zeros((8, 8), dtype=bool)
        mask[:, idx::4] = True
        masks.append(mask)

    subframes = [
        (original.astype(np.float32) * mask[:, :, None] + 8.0).astype(np.uint8)
        for mask in masks
    ]

    result = analyze_single_frame_readability(original, subframes)

    assert abs(result["mean_active_ratio"] - 0.25) < 0.01
