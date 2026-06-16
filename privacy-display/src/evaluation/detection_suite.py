"""Shared helpers for detection attack dataset experiments."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image

from src.attack.camera_simulator import CameraSimulator
from src.attack.detectors import detector_noise_target
from src.core.mask_generator import MaskGenerator
from src.core.noise_injector import NoiseInjector
from src.core.subframe_composer import SubframeComposer


DEFAULT_ATTACKS = ("clean", "single_subframe", "temporal_average")
DEFAULT_MODELS = ("yolo26x", "rtdetr-x", "faster_rcnn", "retinanet")


def load_rgb(path: str | Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))


def mask_key(seed: int, identifier: str) -> bytes:
    """Deterministic 32-byte ChaCha20 key for reproducible masks per stimulus."""
    return hashlib.sha256(f"detection-suite-{seed}-{identifier}".encode()).digest()


def build_attack_variants(
    image: np.ndarray,
    attacks: Iterable[str] = DEFAULT_ATTACKS,
    n: int = 4,
    epsilon: float = 8 / 255,
    target_model: str = "yolov8",
    seed: int = 0,
    identifier: str = "",
    device: str | None = None,
) -> dict[str, np.ndarray]:
    """Build clean/single-subframe/temporal-average variants for one RGB image.

    Masks use a deterministic key derived from ``seed`` and ``identifier`` so a
    rerun reproduces the exact attacked pixels (the repo tracks this via the
    reproducibility manifest); ``identifier`` should uniquely name the stimulus
    (e.g. COCO file name or ``sequence:frame``).

    ``device`` (e.g. ``cuda:0``) lets the PGD adversarial noise run on the GPU,
    which is the dominant cost for large frames; it falls back to CPU when CUDA
    is unavailable.
    """
    requested = tuple(attacks)
    variants: dict[str, np.ndarray] = {}
    if "clean" in requested:
        variants["clean"] = image
    needs_subframes = any(name in requested for name in ("single_subframe", "temporal_average"))
    if not needs_subframes:
        return variants

    h, w = image.shape[:2]
    noise_target = detector_noise_target(target_model)
    generator = MaskGenerator(w, h, n, key=mask_key(seed, identifier))
    composer = SubframeComposer(n=n)
    injector = NoiseInjector(n=n, epsilon=epsilon, target_models=[noise_target], device=device)
    masks = generator.generate(0)
    base = injector.generate_pgd_noise(
        image.astype(np.float32) / 255.0,
        model_name=noise_target,
        seed=seed,
    )
    sub_noises = [(noise * 255).astype(np.float32) for noise in injector.split_complementary(base)]
    subframes = composer.compose(image, masks, sub_noises)
    if "single_subframe" in requested:
        variants["single_subframe"] = subframes[0]
    if "temporal_average" in requested:
        variants["temporal_average"] = CameraSimulator().temporal_averaging_attack(
            subframes,
            k=n,
            randomize_order=False,
        )
    return variants


def parse_csv_list(value: str | None, default: Iterable[str]) -> list[str]:
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def default_device() -> str:
    try:
        import torch

        return "cuda:0" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def write_json(path: str | Path, payload: dict) -> None:
    import json

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def print_metric_table(title: str, results: dict[str, dict[str, dict]], fields: list[str]) -> None:
    print(f"\n## {title}\n")
    print("| Model | Attack | " + " | ".join(fields) + " |")
    print("|---|---|" + "|".join(["---:"] * len(fields)) + "|")
    for model, attacks in results.items():
        for attack, metrics in attacks.items():
            cells = []
            for field in fields:
                value = metrics.get(field)
                if isinstance(value, float):
                    cells.append(f"{value:.4f}")
                else:
                    cells.append(str(value))
            print(f"| {model} | {attack} | " + " | ".join(cells) + " |")
