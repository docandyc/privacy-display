"""
YOLO 目标检测攻击实验（G2）

运行 Ultralytics YOLOv8n：
  1. 在原始照片上检测目标，作为 pseudo-reference
  2. 生成隐私保护子帧
  3. 用 YOLO 检测单子帧/平均攻击帧，计算 P/R/F1/mAP50

默认使用 ultralytics 包自带 bus.jpg，避免额外下载测试图片。
模型权重 `yolov8n.pt` 若本地无缓存，Ultralytics 会按其默认机制下载。
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.attack.camera_simulator import CameraSimulator
from src.attack.detection_evaluator import DetectionEvaluator, yolo_status
from src.core.mask_generator import MaskGenerator
from src.core.noise_injector import NoiseInjector
from src.core.subframe_composer import SubframeComposer


def _load_ultralytics_asset(name: str = "bus.jpg") -> np.ndarray:
    from PIL import Image
    import ultralytics

    path = Path(ultralytics.__file__).parent / "assets" / name
    return np.array(Image.open(path).convert("RGB"))


def run_detection_attack(
    model_path: str = "yolov8n.pt",
    n: int = 4,
    epsilon: float = 8 / 255,
    output_dir: str = "experiments/results",
) -> dict:
    img = _load_ultralytics_asset("bus.jpg")
    h, w = img.shape[:2]
    gen = MaskGenerator(w, h, n)
    composer = SubframeComposer(n=n, gamma=1.0)
    injector = NoiseInjector(n=n, epsilon=epsilon, target_models=["tesseract", "yolov8"])

    masks = gen.generate(0)
    base = injector.generate_pgd_noise(img.astype(np.float32) / 255.0, "yolov8", seed=0)
    sub_noises = [(x * 255).astype(np.float32) for x in injector.split_complementary(base)]
    subframes = composer.compose(img, masks, sub_noises)
    cam = CameraSimulator()
    temporal_avg = cam.temporal_averaging_attack(subframes, k=n, randomize_order=False)

    evaluator = DetectionEvaluator(yolo_model_path=model_path)
    original_boxes = evaluator.detect_yolo_objects(img)
    single = evaluator.evaluate_yolo_attack(img, subframes[0])
    avg = evaluator.evaluate_yolo_attack(img, temporal_avg)

    report = {
        "engine": "ultralytics-yolo",
        "yolo": yolo_status(model_path),
        "image": "ultralytics/assets/bus.jpg",
        "n": n,
        "epsilon": epsilon,
        "original_reference_boxes": len(original_boxes),
        "single_subframe": single,
        "temporal_average": avg,
    }

    out = Path(output_dir) / "detection_attack_yolo.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"结果已保存: {out}")
    return report


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "yolov8n.pt"
    run_detection_attack(model_path=model)
