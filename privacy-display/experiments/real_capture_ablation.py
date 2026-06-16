"""One-command Windows real-camera ablation orchestrator.

This script turns the deployed playback demo into a real USB-webcam capture
experiment. It is designed to be safe to test without hardware: ``--dry-run``
prints the full capture plan and never opens a camera or a pygame window.
"""

from __future__ import annotations

import argparse
import json
import queue
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.anti_ocr_profile_ablation import (  # noqa: E402
    DEPLOYED_GLYPH_ALPHA,
    DEPLOYED_INVERSION_ALPHA,
    DEPLOYED_STRIPE_ALPHA,
)
from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from experiments.real_capture_calibrate import (  # noqa: E402
    DEFAULT_CALIBRATION_DIR,
    load_roi_calibration,
    rectify_frame,
    roi_path,
)
from experiments.real_capture_shoot import (  # noqa: E402
    DEFAULT_CAPTURE_DIR,
    DEFAULT_DEVICE,
    DEFAULT_DEVICE_NAME,
    DEFAULT_EPSILON,
    build_base,
    camera_settings,
    exposure_log2_to_seconds,
    grab_frames,
    make_entry,
    merge_metadata,
    open_camera,
    try_set_exposure,
    warmup,
)
from src.demo.playback_demo import fit_image_to_canvas  # noqa: E402
from src.evaluation.real_capture import REAL_CAPTURE_JSON, REAL_CAPTURE_MD, run_real_capture_ocr  # noqa: E402
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402


DEFAULT_DISPLAY_WIDTH = 2560
DEFAULT_DISPLAY_HEIGHT = 1600
DEFAULT_REFRESH_HZ = 240.0
DEFAULT_N = 4
DEFAULT_CYCLES = 16

ATTACKS = ("short", "long", "video")
STUDIES = ("1", "2", "3", "all")


@dataclass(frozen=True)
class ConditionSpec:
    label: str
    profile: str = "off"
    use_noise: bool = True
    inversion: bool = False
    stripe_alpha: float | None = None
    glyph_alpha: float | None = None
    inversion_alpha: float | None = None
    show_original: bool = False
    attacks: tuple[str, ...] = ATTACKS


@dataclass(frozen=True)
class AttackSpec:
    label: str
    width: int
    height: int
    fps: float
    burst: int
    interval: float
    exposure_key: str | None
    capture_mode: str


COMPONENT_CONDITIONS: tuple[ConditionSpec, ...] = (
    ConditionSpec("original", show_original=True),
    ConditionSpec("mask_only", profile="off", use_noise=False),
    ConditionSpec("mask_noise", profile="off"),
    ConditionSpec(
        "anti_ocr",
        profile="strong",
        stripe_alpha=DEPLOYED_STRIPE_ALPHA,
        glyph_alpha=DEPLOYED_GLYPH_ALPHA,
    ),
    ConditionSpec(
        "deployed",
        profile="strong",
        stripe_alpha=DEPLOYED_STRIPE_ALPHA,
        glyph_alpha=DEPLOYED_GLYPH_ALPHA,
        inversion=True,
        inversion_alpha=DEPLOYED_INVERSION_ALPHA,
    ),
    ConditionSpec("vlm", profile="vlm", inversion=True, inversion_alpha=DEPLOYED_INVERSION_ALPHA),
)


def _parameter_conditions() -> tuple[ConditionSpec, ...]:
    stripe_values = (0.0, 0.10, 0.18, 0.30)
    glyph_values = (0.0, 0.12, 0.22)
    inversion_values = (0.0, 0.2, 0.3, 0.5, 1.0)
    specs: list[ConditionSpec] = []
    for value in stripe_values:
        specs.append(ConditionSpec(
            f"stripe_{value:.2f}",
            profile="strong",
            stripe_alpha=value,
            glyph_alpha=DEPLOYED_GLYPH_ALPHA,
            inversion=True,
            inversion_alpha=DEPLOYED_INVERSION_ALPHA,
            attacks=("short", "video"),
        ))
    for value in glyph_values:
        specs.append(ConditionSpec(
            f"glyph_{value:.2f}",
            profile="strong",
            stripe_alpha=DEPLOYED_STRIPE_ALPHA,
            glyph_alpha=value,
            inversion=True,
            inversion_alpha=DEPLOYED_INVERSION_ALPHA,
            attacks=("short", "video"),
        ))
    for value in inversion_values:
        specs.append(ConditionSpec(
            f"inversion_{value:.1f}",
            profile="strong",
            stripe_alpha=DEPLOYED_STRIPE_ALPHA,
            glyph_alpha=DEPLOYED_GLYPH_ALPHA,
            inversion=value > 0,
            inversion_alpha=value if value > 0 else None,
            attacks=("long", "video"),
        ))
    return tuple(specs)


def _condition_specs_for_study(study: str) -> tuple[ConditionSpec, ...]:
    if study == "1":
        return COMPONENT_CONDITIONS
    if study == "2":
        return _parameter_conditions()
    if study == "3":
        deployed = next(spec for spec in COMPONENT_CONDITIONS if spec.label == "deployed")
        return (ConditionSpec(**{**deployed.__dict__, "attacks": ("short", "video")}),)
    raise ValueError(f"unknown study: {study}")


def _attack_specs() -> dict[str, AttackSpec]:
    return {
        "short": AttackSpec("short", 3840, 2160, 30.0, 3, 0.0, "short", "short_exposure"),
        "long": AttackSpec("long", 3840, 2160, 30.0, 3, 0.0, "long", "long_exposure"),
        "video": AttackSpec("video", 1920, 1080, 60.0, 150, 1 / 60, None, "video_frame"),
    }


def _csv(value: str | None, default: Iterable[str]) -> tuple[str, ...]:
    if value is None or not str(value).strip():
        return tuple(default)
    return tuple(part.strip() for part in str(value).split(",") if part.strip())


def _format_float(value: float) -> str:
    return f"{value:.2f}"


def condition_to_playback_args(condition: str | ConditionSpec) -> list[str]:
    spec = _resolve_condition(condition)
    args: list[str] = []
    if spec.show_original:
        return ["--show-original"]
    if not spec.use_noise:
        args.append("--no-noise")
    args += ["--anti-ocr-profile", spec.profile]
    if spec.stripe_alpha is not None:
        args += ["--stripe-alpha", _format_float(spec.stripe_alpha)]
    if spec.glyph_alpha is not None:
        args += ["--glyph-alpha", _format_float(spec.glyph_alpha)]
    if spec.inversion:
        args.append("--inversion")
        if spec.inversion_alpha is not None:
            args += ["--inversion-alpha", _format_float(spec.inversion_alpha)]
    return args


def _resolve_condition(condition: str | ConditionSpec) -> ConditionSpec:
    if isinstance(condition, ConditionSpec):
        return condition
    for spec in COMPONENT_CONDITIONS + _parameter_conditions():
        if spec.label == condition:
            return spec
    raise ValueError(f"unknown condition: {condition}")


def parse_positions(text: str | None) -> list[dict]:
    if text is None or not str(text).strip() or str(text).strip() == "deploy":
        return [{"label": "d0.5_a0", "distance_m": 0.5, "angle_degrees": 0.0}]
    if str(text).strip() == "matrix":
        return geometry_matrix_positions()

    positions: list[dict] = []
    for raw in str(text).split(","):
        label = raw.strip()
        if not label:
            continue
        try:
            dist_text, angle_text = label.split("_a", 1)
            if not dist_text.startswith("d"):
                raise ValueError
            distance = float(dist_text[1:])
            angle = float(angle_text)
        except ValueError as exc:
            raise ValueError(f"invalid position label: {label}") from exc
        positions.append({
            "label": f"d{distance:g}_a{angle:g}",
            "distance_m": distance,
            "angle_degrees": angle,
        })
    if not positions:
        raise ValueError("at least one position is required")
    return positions


def geometry_matrix_positions() -> list[dict]:
    return [
        {"label": f"d{distance:g}_a{angle:g}", "distance_m": distance, "angle_degrees": float(angle)}
        for distance in (0.5, 1.0, 1.5)
        for angle in (0, 15, 30, 45)
    ]


def _positions_for_study(study: str, positions: str | None) -> list[dict]:
    if positions:
        return parse_positions(positions)
    if study == "3":
        return geometry_matrix_positions()
    return parse_positions("deploy")


def build_study_plan(
    *,
    study: str,
    names: list[str],
    truths: list[str],
    subset_size: int | None = None,
    attacks: Iterable[str] = ATTACKS,
    conditions: Iterable[str] | None = None,
    positions: str | None = None,
) -> list[dict]:
    if study == "all":
        merged: list[dict] = []
        default_sizes = {"1": 12, "2": 5, "3": 5}
        for part in ("1", "2", "3"):
            merged.extend(build_study_plan(
                study=part,
                names=names,
                truths=truths,
                subset_size=subset_size if subset_size is not None else default_sizes[part],
                attacks=attacks,
                conditions=conditions,
                positions=positions if part == "3" else None,
            ))
        return merged
    if study not in {"1", "2", "3"}:
        raise ValueError(f"unknown study: {study}")

    selected_attacks = set(attacks)
    unknown_attacks = selected_attacks - set(ATTACKS)
    if unknown_attacks:
        raise ValueError(f"unknown attacks: {', '.join(sorted(unknown_attacks))}")
    condition_filter = set(conditions or [])
    specs = _condition_specs_for_study(study)
    if condition_filter:
        specs = tuple(spec for spec in specs if spec.label in condition_filter)
    unknown_conditions = condition_filter - {spec.label for spec in _condition_specs_for_study(study)}
    if unknown_conditions:
        raise ValueError(f"unknown condition(s) for study {study}: {', '.join(sorted(unknown_conditions))}")

    if subset_size is None:
        subset_size = 12 if study == "1" else 5
    count = min(max(0, subset_size), len(names))
    positions_list = _positions_for_study(study, positions)
    plan: list[dict] = []
    for pos in positions_list:
        for name, truth in zip(names[:count], truths[:count]):
            for spec in specs:
                for attack in spec.attacks:
                    if attack not in selected_attacks:
                        continue
                    plan.append({
                        "study": study,
                        "image_name": name,
                        "truth": truth,
                        "ablation": spec.label,
                        "attack": attack,
                        "condition": f"{spec.label}|{attack}",
                        "profile": spec.profile,
                        "stripe_alpha": spec.stripe_alpha,
                        "glyph_alpha": spec.glyph_alpha,
                        "inversion_alpha": spec.inversion_alpha,
                        "use_noise": spec.use_noise,
                        "show_original": spec.show_original,
                        "position": dict(pos),
                    })
    return plan


def pad_to_display_aspect(
    image: np.ndarray,
    *,
    width: int = DEFAULT_DISPLAY_WIDTH,
    height: int = DEFAULT_DISPLAY_HEIGHT,
) -> np.ndarray:
    return fit_image_to_canvas(image, width, height, background=(0, 0, 0))


def offline_video_attack_frames(frames: list[np.ndarray], window: int = DEFAULT_N) -> dict[str, np.ndarray]:
    if not frames:
        raise ValueError("frames must not be empty")
    arrays = [np.asarray(frame, dtype=np.uint8) for frame in frames]
    stack = np.stack(arrays, axis=0).astype(np.float32)
    window = max(1, min(int(window), len(arrays)))
    single_best = max(arrays, key=_contrast_score)
    temporal_mean = np.rint(stack.mean(axis=0)).clip(0, 255).astype(np.uint8)
    window_means = [
        np.rint(stack[start:start + window].mean(axis=0)).clip(0, 255).astype(np.uint8)
        for start in range(0, len(arrays) - window + 1)
    ]
    window_mean_best = max(window_means, key=_contrast_score)
    max_proj = stack.max(axis=0).clip(0, 255).astype(np.uint8)
    return {
        "single_best": single_best.copy(),
        "temporal_mean": temporal_mean,
        "window_mean_best": window_mean_best,
        "max_proj": max_proj,
    }


def _contrast_score(frame: np.ndarray) -> float:
    gray = frame.astype(np.float32).mean(axis=2)
    return float(gray.std())


def build_metadata_entry(
    item: dict,
    *,
    image_name: str,
    entry_id: str,
    device_name: str,
    camera_type: str,
    capture_mode: str,
    exposure_s,
    fps,
    refresh_hz: float,
    n: int,
    epsilon: float,
    playback_cmd: list[str],
    lighting_lux=None,
    environment: str = "office",
    notes: str = "",
) -> dict:
    pos = item["position"]
    entry = make_entry(
        image=image_name,
        truth=str(item["truth"]),
        condition=str(item["condition"]),
        device_name=device_name,
        camera_type=camera_type,
        capture_mode=capture_mode,
        distance=float(pos["distance_m"]),
        angle=float(pos["angle_degrees"]),
        exposure_s=exposure_s,
        fps=fps,
        refresh=refresh_hz,
        n=n,
        epsilon=epsilon,
        lux=lighting_lux,
        environment=environment,
        notes=notes,
        entry_id=entry_id,
    )
    entry.update({
        "ablation": item.get("ablation"),
        "attack": item.get("attack"),
        "profile": item.get("profile"),
        "stripe_alpha": item.get("stripe_alpha"),
        "glyph_alpha": item.get("glyph_alpha"),
        "inversion_alpha": item.get("inversion_alpha"),
        "playback_cmd": " ".join(playback_cmd),
        "roi_pos": pos.get("label"),
        "display_refresh_hz": refresh_hz,
    })
    return entry


def load_exposure_calibration(calibration_dir: str | Path) -> dict:
    path = Path(calibration_dir) / "exposure.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def exposure_for_attack(calibration: dict, attack: str) -> tuple[float | None, float | None]:
    payload = calibration.get(attack) or {}
    value = payload.get("value")
    exposure_s = payload.get("exposure_s")
    if exposure_s is None and value is not None:
        exposure_s = exposure_log2_to_seconds(value)
    return value, exposure_s


def _load_subset(subset_size: int | None) -> tuple[list[np.ndarray], list[str], list[str]]:
    images, truths, names = load_corpus()
    if subset_size is not None and subset_size >= len(names):
        return images, truths, names
    metadata = load_corpus_metadata()
    indices, _ = select_publication_subset(names, metadata, max_samples=subset_size)
    return take_indices(images, indices), take_indices(truths, indices), take_indices(names, indices)


def _playback_command(args: argparse.Namespace, image_path: Path, item: dict) -> list[str]:
    cmd = [
        args.python_executable,
        "main.py",
        "playback",
        "--image",
        str(image_path),
        "--width",
        str(args.display_width),
        "--height",
        str(args.display_height),
        "--n",
        str(args.n),
        "--cycles",
        str(args.cycles),
    ]
    if args.fullscreen:
        cmd.append("--fullscreen")
    cmd += condition_to_playback_args(str(item["ablation"]))
    return cmd


def wait_for_playback_ready(proc: subprocess.Popen, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    buffered: list[str] = []
    lines: queue.Queue[str] = queue.Queue()

    def read_stdout() -> None:
        if proc.stdout is None:
            return
        for line in proc.stdout:
            lines.put(line)

    threading.Thread(target=read_stdout, daemon=True).start()
    while time.monotonic() < deadline:
        remaining = max(0.0, deadline - time.monotonic())
        try:
            line = lines.get(timeout=min(0.05, remaining))
        except queue.Empty:
            if proc.poll() is not None:
                raise RuntimeError(f"playback exited before ready: {' | '.join(buffered[-5:])}")
            continue
        buffered.append(line.rstrip())
        if "PLAYBACK_READY" in line:
            return
        if proc.poll() is not None and lines.empty():
            raise RuntimeError(f"playback exited before ready: {' | '.join(buffered[-5:])}")
    raise TimeoutError(f"playback did not print PLAYBACK_READY within {timeout}s")


def _maybe_rectify_frames(frames: list[np.ndarray], calibration_dir: str | Path, pos_label: str) -> list[np.ndarray]:
    path = roi_path(calibration_dir, pos_label)
    if not path.exists():
        return frames
    calib = load_roi_calibration(path)
    return [rectify_frame(frame, calib) for frame in frames]


def _save_frames(
    frames: list[np.ndarray],
    *,
    args: argparse.Namespace,
    item: dict,
    attack_spec: AttackSpec,
    settings: dict,
    exposure_s,
    playback_cmd: list[str],
    suffix: str = "",
) -> list[dict]:
    capture_dir = Path(args.capture_dir)
    capture_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%H%M%S")
    content = str(item["image_name"])
    base = build_base(
        args.device_name,
        str(item["condition"]) + suffix,
        float(item["position"]["angle_degrees"]),
        float(item["position"]["distance_m"]),
        content,
        args.n,
    )
    entries: list[dict] = []
    for idx, frame in enumerate(frames):
        image_name = f"{base}_{timestamp}_s{idx:02d}.jpg"
        cv2.imwrite(str(capture_dir / image_name), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        entry_id = f"{base}_{timestamp}_s{idx:02d}"
        entry_item = dict(item)
        if suffix:
            entry_item["condition"] = f"{item['condition']}|{suffix.strip('_')}"
            entry_item["attack"] = f"{item['attack']}:{suffix.strip('_')}"
        entries.append(build_metadata_entry(
            entry_item,
            image_name=image_name,
            entry_id=entry_id,
            device_name=args.device_name,
            camera_type=args.camera_type,
            capture_mode=attack_spec.capture_mode,
            exposure_s=exposure_s,
            fps=settings.get("fps"),
            refresh_hz=args.refresh_hz,
            n=args.n,
            epsilon=args.epsilon,
            playback_cmd=playback_cmd,
            lighting_lux=args.lighting_lux,
            environment=args.environment,
            notes=args.notes,
        ))
    merge_metadata(capture_dir, args.metadata, entries)
    return entries


def _execute_plan(args: argparse.Namespace, images: list[np.ndarray], plan: list[dict]) -> int:
    unique_names: list[str] = []
    for item in plan:
        name = str(item["image_name"])
        if name not in unique_names:
            unique_names.append(name)
    image_by_name = {
        name: image
        for name, image in zip(unique_names, images)
    }

    exposure_calib = load_exposure_calibration(args.calibration_dir)
    attacks = _attack_specs()
    last_pos = None
    total_entries = 0
    with tempfile.TemporaryDirectory(prefix="real-capture-ablation-") as tmp:
        tmp_root = Path(tmp)
        for idx, item in enumerate(plan, 1):
            pos_label = item["position"]["label"]
            if args.prompt_positions and pos_label != last_pos:
                input(f"[position {pos_label}] Move camera to distance/angle, then press ENTER...")
                last_pos = pos_label
            image = image_by_name[str(item["image_name"])]
            padded = pad_to_display_aspect(image, width=args.display_width, height=args.display_height)
            image_path = tmp_root / f"{item['image_name']}_{idx}.png"
            from PIL import Image

            Image.fromarray(padded).save(image_path)
            playback_cmd = _playback_command(args, image_path, item)
            print(f"[{idx}/{len(plan)}] {item['condition']} {item['image_name']} {pos_label}")
            proc = subprocess.Popen(
                playback_cmd,
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                wait_for_playback_ready(proc, args.playback_timeout)
                attack_spec = attacks[str(item["attack"])]
                exposure_value, exposure_s = exposure_for_attack(exposure_calib, attack_spec.exposure_key or "")
                cap = open_camera(
                    args.device,
                    attack_spec.width,
                    attack_spec.height,
                    args.fourcc,
                    attack_spec.fps,
                    backend=args.backend,
                )
                try:
                    if exposure_value is not None:
                        try_set_exposure(
                            cap,
                            manual=True,
                            value=exposure_value,
                            backend_name=args.backend,
                        )
                    warmup(cap, args.warmup)
                    frames = grab_frames(cap, attack_spec.burst, attack_spec.interval)
                    frames = _maybe_rectify_frames(frames, args.calibration_dir, pos_label)
                    settings = camera_settings(cap)
                finally:
                    cap.release()
                if item["attack"] == "video":
                    variants = offline_video_attack_frames(frames, window=args.n)
                    for name, frame in variants.items():
                        total_entries += len(_save_frames(
                            [frame],
                            args=args,
                            item=item,
                            attack_spec=attack_spec,
                            settings=settings,
                            exposure_s=exposure_s,
                            playback_cmd=playback_cmd,
                            suffix=f"_{name}",
                        ))
                else:
                    total_entries += len(_save_frames(
                        frames,
                        args=args,
                        item=item,
                        attack_spec=attack_spec,
                        settings=settings,
                        exposure_s=exposure_s,
                        playback_cmd=playback_cmd,
                    ))
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
    print(f"Saved metadata entries: {total_entries}")
    if args.analyze:
        engines = [part for part in _csv(args.engines, ("tesseract",))]
        run_real_capture_ocr(args.capture_dir, args.metadata, engines=engines)
        print(f"Analysis written: experiments/results/{REAL_CAPTURE_JSON}, {REAL_CAPTURE_MD}")
    return 0


def print_plan(plan: list[dict]) -> None:
    print(f"Planned captures: {len(plan)}")
    by_study: dict[str, int] = {}
    by_condition: dict[str, int] = {}
    for item in plan:
        by_study[item["study"]] = by_study.get(item["study"], 0) + 1
        by_condition[item["condition"]] = by_condition.get(item["condition"], 0) + 1
    print("By study:")
    for key, value in sorted(by_study.items()):
        print(f"  {key}: {value}")
    print("By condition:")
    for key, value in sorted(by_condition.items()):
        print(f"  {key}: {value}")
    print("First 20 items:")
    for item in plan[:20]:
        pos = item["position"]["label"]
        print(f"  - study={item['study']} image={item['image_name']} condition={item['condition']} pos={pos}")
    if len(plan) > 20:
        print(f"  ... {len(plan) - 20} more")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Windows real-camera ablation captures")
    p.add_argument("--study", choices=STUDIES, default="all")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--list-conditions", action="store_true")
    p.add_argument("--subset-size", type=int, default=None)
    p.add_argument("--attacks", default=",".join(ATTACKS))
    p.add_argument("--conditions", default="")
    p.add_argument("--positions", default="")
    p.add_argument("--device", type=int, default=DEFAULT_DEVICE)
    p.add_argument("--device-name", default=DEFAULT_DEVICE_NAME)
    p.add_argument("--camera-type", default="usb_webcam")
    p.add_argument("--backend", default=None)
    p.add_argument("--fourcc", default="MJPG")
    p.add_argument("--warmup", type=float, default=0.8)
    p.add_argument("--capture-dir", default=DEFAULT_CAPTURE_DIR)
    p.add_argument("--metadata", default="metadata.json")
    p.add_argument("--calibration-dir", default=DEFAULT_CALIBRATION_DIR)
    p.add_argument("--display-width", type=int, default=DEFAULT_DISPLAY_WIDTH)
    p.add_argument("--display-height", type=int, default=DEFAULT_DISPLAY_HEIGHT)
    p.add_argument("--refresh-hz", type=float, default=DEFAULT_REFRESH_HZ)
    p.add_argument("--n", type=int, default=DEFAULT_N)
    p.add_argument("--cycles", type=int, default=DEFAULT_CYCLES)
    p.add_argument("--epsilon", type=float, default=DEFAULT_EPSILON)
    p.add_argument("--fullscreen", action="store_true", default=True)
    p.add_argument("--no-fullscreen", action="store_false", dest="fullscreen")
    p.add_argument("--prompt-positions", action="store_true", default=True)
    p.add_argument("--no-prompt-positions", action="store_false", dest="prompt_positions")
    p.add_argument("--lighting-lux", type=float, default=None)
    p.add_argument("--environment", default="office")
    p.add_argument("--notes", default="")
    p.add_argument("--engines", default="tesseract")
    p.add_argument("--analyze", action="store_true")
    p.add_argument("--playback-timeout", type=float, default=20.0)
    p.add_argument("--python-executable", default=sys.executable)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list_conditions:
        for study in ("1", "2", "3"):
            print(f"Study {study}:")
            for spec in _condition_specs_for_study(study):
                print(f"  - {spec.label}: attacks={','.join(spec.attacks)} args={' '.join(condition_to_playback_args(spec))}")
        return 0

    load_subset_size = args.subset_size
    if load_subset_size is None:
        load_subset_size = 12 if args.study in {"1", "all"} else 5
    images, truths, names = _load_subset(load_subset_size)
    conditions = _csv(args.conditions, ())
    plan = build_study_plan(
        study=args.study,
        names=names,
        truths=truths,
        subset_size=args.subset_size,
        attacks=_csv(args.attacks, ATTACKS),
        conditions=conditions or None,
        positions=args.positions or None,
    )
    if args.dry_run:
        print_plan(plan)
        return 0
    return _execute_plan(args, images, plan)


if __name__ == "__main__":
    raise SystemExit(main())
