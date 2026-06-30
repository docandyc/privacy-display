"""
Reproducibility manifest for publication artifacts.

The manifest records environment metadata, canonical reproduction commands, and
hashes of result/source files. It intentionally records only whether secret
environment variables are required, never their values.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any


MANIFEST_JSON = "reproducibility_manifest.json"

REAL_CAPTURE_POSITION_LABELS = [
    "d0.5_a0",
    "d0.5_a15",
    "d0.5_a30",
    "d1_a0",
    "d1_a15",
    "d1_a30",
    "d1.5_a0",
    "d1.5_a15",
    "d1.5_a30",
]

REAL_CAPTURE_POSITION_RESULT_FILES = [
    f"experiments/results_{label}_final/real_capture_ocr.json"
    for label in REAL_CAPTURE_POSITION_LABELS
] + [
    f"experiments/results_{label}_final/real_capture_ocr.md"
    for label in REAL_CAPTURE_POSITION_LABELS
] + [
    f"experiments/real_captures_{label}_final/metadata.json"
    for label in REAL_CAPTURE_POSITION_LABELS
]

RESULT_FILES = [
    "experiments/results/corpus_multi_engine.json",
    "experiments/results/corpus_strong_camera_attack.json",
    "experiments/results/detection_attack_yolo.json",
    "experiments/results/coco_detection_attack.json",
    "experiments/results/mot_video_detection.json",
    "experiments/results/mot_tracking_attack.json",
    "experiments/results/view_attack.json",
    "experiments/results/unet_reconstruction.json",
    "experiments/results/real_capture_ocr.json",
    "experiments/results/real_capture_ocr.md",
    *REAL_CAPTURE_POSITION_RESULT_FILES,
    "experiments/results/real_capture_coco_detection.json",
    "experiments/results/real_capture_mot_detection.json",
    "experiments/results/real_capture_mot_tracking.json",
    "experiments/results/real_capture_mot_capture_manifest.json",
    "experiments/real_captures/coco_detection/capture_manifest.json",
    "experiments/results/component_ablation.json",
    "experiments/results/recognizer_generalization.json",
    "experiments/results/perceptual_ablation.json",
    "experiments/results/pareto_sweep.json",
    "experiments/results/pareto_sweep.png",
    "experiments/results/strong_attack_extra.json",
    "experiments/results/adaptive_attack_ablation.json",
    "experiments/results/camera_pipeline_ablation.json",
    "experiments/results/screen_privacy_baselines.json",
    "experiments/results/vlm_prompt_ablation.json",
    "experiments/results/noise_epsilon_sweep.json",
    "experiments/results/vlm_model_ablation.json",
    "experiments/results/brightness_compensation_ablation.json",
    "experiments/results/mask_granularity_ablation.json",
    "experiments/results/seed_sensitivity.json",
    "experiments/results/usability_pilot.json",
    "experiments/results/usability_pilot.md",
    "experiments/results/publication_summary.json",
    "experiments/results/publication_summary.md",
    "experiments/results/vlm_qwen3_siliconflow.json",
]

SOURCE_FILES = [
    "README.md",
    "docs/detection_suite_server.md",
    ".env.example",
    "requirements.txt",
    "requirements-surya.txt",
    "requirements-detection.txt",
    "scripts/reproduce_all.sh",
    "scripts/download_coco_val2017.sh",
    "scripts/download_mot17.sh",
    "scripts/run_detection_suite.sh",
    "scripts/run_real_capture_ocr_all.ps1",
    "scripts/run_real_capture_ocr_all_engines.ps1",
    "scripts/setup_surya_ocr_env.ps1",
    "scripts/download_surya_models.ps1",
    "scripts/rerun_real_capture_surya_only.ps1",
    "scripts/run_real_capture_detection_windows.bat",
    "experiments/build_corpus.py",
    "experiments/attack_analysis.py",
    "experiments/detection_attack.py",
    "experiments/coco_detection_attack.py",
    "experiments/mot_video_detection.py",
    "experiments/mot_tracking_attack.py",
    "experiments/view_attack.py",
    "experiments/unet_reconstruction.py",
    "experiments/real_capture_analysis.py",
    "experiments/merge_real_capture_surya.py",
    "experiments/finalize_real_capture_artifacts.py",
    "experiments/real_capture_shoot.py",
    "experiments/real_capture_detection.py",
    "experiments/real_capture_mot.py",
    "experiments/component_ablation.py",
    "experiments/recognizer_generalization.py",
    "experiments/perceptual_ablation.py",
    "experiments/pareto_sweep.py",
    "experiments/strong_attack_extra.py",
    "experiments/adaptive_attack_ablation.py",
    "experiments/camera_pipeline_ablation.py",
    "experiments/screen_privacy_baselines.py",
    "experiments/vlm_prompt_ablation.py",
    "experiments/noise_epsilon_sweep.py",
    "experiments/vlm_model_ablation.py",
    "experiments/brightness_compensation_ablation.py",
    "experiments/mask_granularity_ablation.py",
    "experiments/seed_sensitivity.py",
    "experiments/usability_pilot.py",
    "experiments/real_captures/metadata_template.json",
    "experiments/vlm_readability_analysis.py",
    "experiments/publication_summary.py",
    "experiments/reproducibility_manifest.py",
    "src/evaluation/benchmark.py",
    "src/evaluation/publication_summary.py",
    "src/evaluation/vlm_benchmark.py",
    "src/evaluation/real_capture.py",
    "src/evaluation/sampling.py",
    "src/evaluation/reproducibility_manifest.py",
    "src/evaluation/coco_eval.py",
    "src/evaluation/detection_suite.py",
    "src/evaluation/mot.py",
    "src/attack/camera_simulator.py",
    "src/attack/detectors.py",
    "src/attack/ocr_evaluator.py",
    "src/attack/vlm_evaluator.py",
]

PACKAGE_NAMES = [
    "numpy",
    "scipy",
    "Pillow",
    "opencv-python",
    "pytest",
    "pytesseract",
    "easyocr",
    "surya-ocr",
    "ultralytics",
    "pycryptodome",
    "moderngl",
    "transformers",
    "torch",
    "python-doctr",
    "pycocotools",
    "motmetrics",
    "boxmot",
    "lap",
]

REPRODUCTION_COMMANDS = [
    {
        "name": "reproduce_quick",
        "command": "scripts/reproduce_all.sh",
        "purpose": "Run the default safe artifact refresh path.",
        "expected": "Tests pass, VLM dry-run succeeds, publication summary and manifest are regenerated.",
    },
    {
        "name": "reproduce_full_offline",
        "command": "scripts/reproduce_all.sh --full-offline",
        "purpose": "Run heavier offline experiments before refreshing publication artifacts.",
        "expected": "Offline result JSON files, publication summary, and manifest are regenerated.",
    },
    {
        "name": "reproduce_with_vlm_live",
        "command": "scripts/reproduce_all.sh --with-vlm-live",
        "purpose": "Run the bounded live online VLM benchmark before refreshing publication artifacts.",
        "expected": "experiments/results/vlm_qwen3_siliconflow.json, publication summary, and manifest are regenerated.",
        "requires_env": ["SILICONFLOW_API_KEY"],
        "secret_policy": "Do not pass the API key as an argument or write it into logs/artifacts.",
    },
    {
        "name": "reproduce_with_real_capture",
        "command": "scripts/reproduce_all.sh --real-capture",
        "purpose": "Finalize already collected real camera OCR/MOT artifacts before refreshing publication artifacts.",
        "expected": "experiments/results/real_capture_ocr.json, real_capture_ocr.md, real_capture_mot_detection.json, real_capture_mot_tracking.json, publication summary, and manifest are regenerated.",
        "requires_data": [
            "experiments/results_d*_final/real_capture_ocr.json",
            "experiments/results_d1.5_a0_detection/results",
            "referenced capture image files",
        ],
    },
    {
        "name": "unit_tests",
        "command": "./.venv/bin/pytest tests/ -q",
        "purpose": "Run unit and regression tests.",
        "expected": "All tests pass.",
    },
    {
        "name": "build_corpus",
        "command": "python experiments/build_corpus.py",
        "purpose": "Regenerate deterministic 120-sample text corpus.",
        "expected": "data/test_images/*.png, ground_truth.json, corpus_metadata.json",
    },
    {
        "name": "multi_engine_ocr",
        "command": ".venv-surya/bin/python -c \"from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','surya'], merge_existing=True)\"",
        "purpose": "Run or merge Tesseract/EasyOCR/Surya corpus OCR results.",
        "expected": "experiments/results/corpus_multi_engine.json",
    },
    {
        "name": "strong_camera_attacks",
        "command": "python experiments/attack_analysis.py",
        "purpose": "Run single-sample and corpus strong camera attack baselines.",
        "expected": "experiments/results/attack_analysis_strong_camera.json and corpus_strong_camera_attack.json",
    },
    {
        "name": "detection_attack",
        "command": "python experiments/detection_attack.py",
        "purpose": "Evaluate YOLOv8n object-detection leakage.",
        "expected": "experiments/results/detection_attack_yolo.json",
    },
    {
        "name": "detection_suite_setup",
        "command": "pip install -U ultralytics && pip install -r requirements-detection.txt",
        "purpose": "Install server-only detection, COCO, MOT, and tracking dependencies.",
        "expected": "Ultralytics YOLO/RT-DETR, pycocotools, motmetrics, and ByteTrack-compatible packages are available.",
    },
    {
        "name": "download_coco_val2017",
        "command": "bash scripts/download_coco_val2017.sh",
        "purpose": "Download COCO val2017 images and annotations to data/coco by default.",
        "expected": "data/coco/val2017 and data/coco/annotations/instances_val2017.json",
    },
    {
        "name": "download_mot17",
        "command": "bash scripts/download_mot17.sh",
        "purpose": "Download MOT17 to data/MOT17 by default.",
        "expected": "data/MOT17/train/MOT17-*/img1 and gt/gt.txt",
    },
    {
        "name": "trackeval_hota_setup",
        "command": "git clone https://github.com/JonathonLuiten/TrackEval.git && pip install -r TrackEval/requirements.txt && export TRACKEVAL_ROOT=$PWD/TrackEval",
        "purpose": "Optional: enable HOTA/DetA/AssA for MOT17 tracking via the reference TrackEval implementation.",
        "expected": "mot_tracking_attack.json rows gain non-null hota/deta/assa; otherwise hota stays null and MOTChallenge files are exported under experiments/results/trackeval_workspace.",
    },
    {
        "name": "run_detection_suite",
        "command": "bash scripts/run_detection_suite.sh",
        "purpose": "Run COCO val2017 detection, MOT17 frame detection, and MOT17 tracking across the planned detector suite.",
        "expected": "experiments/results/coco_detection_attack.json, mot_video_detection.json, and mot_tracking_attack.json",
        "requires_data": ["data/coco/val2017", "data/coco/annotations/instances_val2017.json", "data/MOT17/train"],
    },
    {
        "name": "real_capture_calibrate",
        "command": "scripts\\run_real_capture_detection_windows.bat calibrate-roi --pos d0.5_a0 && scripts\\run_real_capture_detection_windows.bat calibrate-exposure --image data\\coco\\val2017\\000000000139.jpg",
        "purpose": "Windows 240Hz only: calibrate ROI homography (rectify to display canvas) and short/long exposure before real detection/tracking capture.",
        "expected": "experiments/real_captures/calibration/roi_d0.5_a0.json and exposure.json",
    },
    {
        "name": "real_capture_coco_detection",
        "command": "python experiments/real_capture_detection.py --coco-root data/coco --max-images 150 --device cuda:0",
        "purpose": "Windows 240Hz only: photograph privacy-displayed COCO images with a USB webcam and score 4 detectors against COCO GT (real_clean/real_short/real_video).",
        "expected": "experiments/results/real_capture_coco_detection.json",
        "requires_data": ["data/coco/val2017", "experiments/real_captures/calibration/roi_d0.5_a0.json"],
    },
    {
        "name": "real_capture_mot",
        "command": "python experiments/real_capture_mot.py --mot-root data/MOT17 --sequence MOT17-09-FRCNN --max-frames 450 --device cuda:0",
        "purpose": "Windows 240Hz only: stop-motion real capture of a MOT17 clip; per-frame detection + ByteTrack tracking against MOT GT.",
        "expected": "experiments/results/real_capture_mot_detection.json and real_capture_mot_tracking.json",
        "requires_data": ["data/MOT17/train", "experiments/real_captures/calibration/roi_d0.5_a0.json"],
    },
    {
        "name": "view_attack",
        "command": "python experiments/view_attack.py",
        "purpose": "Evaluate off-axis/full-cycle attack behavior.",
        "expected": "experiments/results/view_attack.json",
    },
    {
        "name": "unet_reconstruction",
        "command": "python experiments/unet_reconstruction.py",
        "purpose": "Run learned/inpainting reconstruction attack checks.",
        "expected": "experiments/results/unet_reconstruction.json",
    },
    {
        "name": "component_ablation",
        "command": "python experiments/component_ablation.py --samples-per-category 20 --max-samples 120",
        "purpose": "Run systematic component contribution ablation.",
        "expected": "experiments/results/component_ablation.json",
    },
    {
        "name": "recognizer_generalization",
        "command": "python experiments/recognizer_generalization.py --engines tesseract --samples-per-category 20 --max-samples 120",
        "purpose": "Run recognizer/attack-frame matrix with offline-safe OCR engines.",
        "expected": "experiments/results/recognizer_generalization.json",
    },
    {
        "name": "perceptual_ablation",
        "command": "python experiments/perceptual_ablation.py --samples-per-category 20 --max-samples 120",
        "purpose": "Run channel/perceptual side-channel ablation.",
        "expected": "experiments/results/perceptual_ablation.json",
    },
    {
        "name": "pareto_sweep",
        "command": "python experiments/pareto_sweep.py --samples-per-category 20 --max-samples 120",
        "purpose": "Run security/usability Pareto sweep.",
        "expected": "experiments/results/pareto_sweep.json and pareto_sweep.png",
    },
    {
        "name": "strong_attack_extra",
        "command": "python experiments/strong_attack_extra.py --samples-per-category 20 --max-samples 120",
        "purpose": "Run rolling-shutter row-alignment and temporal-superresolution boundary checks.",
        "expected": "experiments/results/strong_attack_extra.json",
    },
    {
        "name": "adaptive_attack_ablation",
        "command": "python experiments/adaptive_attack_ablation.py --samples-per-category 20 --max-samples 120",
        "purpose": "Run adaptive single-frame OCR preprocessing attacks.",
        "expected": "experiments/results/adaptive_attack_ablation.json",
    },
    {
        "name": "camera_pipeline_ablation",
        "command": "python experiments/camera_pipeline_ablation.py --samples-per-category 20 --max-samples 120",
        "purpose": "Run simulated camera pipeline perturbation ablation.",
        "expected": "experiments/results/camera_pipeline_ablation.json",
    },
    {
        "name": "screen_privacy_baselines",
        "command": "python experiments/screen_privacy_baselines.py --samples-per-category 20 --max-samples 120",
        "purpose": "Compare temporal masking against software baseline controls.",
        "expected": "experiments/results/screen_privacy_baselines.json",
    },
    {
        "name": "noise_epsilon_sweep",
        "command": "python experiments/noise_epsilon_sweep.py --samples-per-category 5 --max-samples 60",
        "purpose": "Sweep the adversarial noise budget epsilon (perceptual cost vs weak-mask leakage margin).",
        "expected": "experiments/results/noise_epsilon_sweep.json",
    },
    {
        "name": "brightness_compensation_ablation",
        "command": "python experiments/brightness_compensation_ablation.py --samples-per-category 20 --max-samples 120",
        "purpose": "Ablate the brightness-compensation factor (backlight vs pixel-space compensation).",
        "expected": "experiments/results/brightness_compensation_ablation.json",
    },
    {
        "name": "mask_granularity_ablation",
        "command": "python experiments/mask_granularity_ablation.py --samples-per-category 20 --max-samples 120",
        "purpose": "Ablate mask spatial granularity (per-pixel vs b×b blocks): flicker vs leakage.",
        "expected": "experiments/results/mask_granularity_ablation.json",
    },
    {
        "name": "seed_sensitivity",
        "command": "python experiments/seed_sensitivity.py --seeds 10 --samples-per-category 5 --max-samples 60",
        "purpose": "Confirm metrics are PRNG-seed-invariant across independent keys.",
        "expected": "experiments/results/seed_sensitivity.json",
    },
    {
        "name": "vlm_model_ablation_dry_run",
        "command": "python experiments/vlm_model_ablation.py --dry-run --samples-per-category 3",
        "purpose": "Estimate multi-VLM model-ablation call count without requiring secrets.",
        "expected": "Print model list, selected samples, attacks, and call count.",
    },
    {
        "name": "vlm_model_ablation_live",
        "command": "python experiments/vlm_model_ablation.py --samples-per-category 3",
        "purpose": "Run multi-VLM model-robustness ablation across VLM families.",
        "expected": "experiments/results/vlm_model_ablation.json",
        "requires_env": ["SILICONFLOW_API_KEY"],
        "secret_policy": "Do not record or commit the API key value.",
    },
    {
        "name": "vlm_prompt_ablation_dry_run",
        "command": "python experiments/vlm_prompt_ablation.py --dry-run --samples-per-category 1",
        "purpose": "Estimate online VLM prompt-ablation call count without requiring secrets.",
        "expected": "Print selected sample, attack, prompt, and call counts.",
    },
    {
        "name": "vlm_prompt_ablation_live",
        "command": "python experiments/vlm_prompt_ablation.py --samples-per-category 1",
        "purpose": "Run live prompt-robustness ablation for online VLM readability.",
        "expected": "experiments/results/vlm_prompt_ablation.json",
        "requires_env": ["SILICONFLOW_API_KEY"],
        "secret_policy": "Do not record or commit the API key value.",
    },
    {
        "name": "usability_pilot",
        "command": "python experiments/usability_pilot.py --input experiments/usability_pilot.csv",
        "purpose": "Summarize a small internal usability pilot when CSV data exists.",
        "expected": "experiments/results/usability_pilot.json and usability_pilot.md",
        "requires_data": ["experiments/usability_pilot.csv with non-template rows"],
    },
    {
        "name": "real_capture_template",
        "command": "python experiments/real_capture_analysis.py --init-template",
        "purpose": "Create the manual metadata template for real phone/camera capture collection.",
        "expected": "experiments/real_captures/metadata_template.json",
    },
    {
        "name": "real_capture_ocr",
        "command": "powershell -ExecutionPolicy Bypass -File scripts/run_real_capture_ocr_all.ps1",
        "purpose": "Analyze the 3x3 real camera OCR position matrix with Tesseract.",
        "expected": "experiments/results_<position>_final/real_capture_ocr.json and .md for all 9 positions",
        "requires_data": ["experiments/real_captures_<position>_final/metadata.json", "referenced capture image files"],
    },
    {
        "name": "real_capture_surya",
        "command": "powershell -ExecutionPolicy Bypass -File scripts/rerun_real_capture_surya_only.ps1",
        "purpose": "Replace legacy third-engine rows with Surya while preserving Tesseract/EasyOCR.",
        "expected": "Nine per-position reports and the combined report use tesseract/easyocr/surya.",
        "requires_data": ["experiments/results_<position>_final/real_capture_ocr.json", "referenced capture image files"],
    },
    {
        "name": "real_capture_finalize",
        "command": "python experiments/finalize_real_capture_artifacts.py",
        "purpose": "Merge the 3x3 OCR position reports and canonicalize real MOT capture artifacts under experiments/results.",
        "expected": "experiments/results/real_capture_ocr.json, real_capture_ocr.md, real_capture_mot_detection.json, real_capture_mot_tracking.json, and real_capture_mot_capture_manifest.json",
        "requires_data": [
            "experiments/results_d*_final/real_capture_ocr.json",
            "experiments/results_d1.5_a0_detection/results",
            "experiments/results_d1.5_a0_detection/captures/mot_MOT17-09-FRCNN",
        ],
    },
    {
        "name": "vlm_dry_run",
        "command": "python experiments/vlm_readability_analysis.py --dry-run --samples-per-category 1",
        "purpose": "Estimate online VLM call count without requiring secrets.",
        "expected": "Print selected samples, attacks, and call count.",
    },
    {
        "name": "vlm_live",
        "command": "python experiments/vlm_readability_analysis.py --samples-per-category 1",
        "purpose": "Run online VLM readability benchmark.",
        "expected": "experiments/results/vlm_qwen3_siliconflow.json",
        "requires_env": ["SILICONFLOW_API_KEY"],
        "secret_policy": "Do not record or commit the API key value.",
    },
    {
        "name": "publication_summary",
        "command": "python experiments/publication_summary.py",
        "purpose": "Consolidate experiment JSON into paper/table summary artifacts.",
        "expected": "experiments/results/publication_summary.json and publication_summary.md",
    },
    {
        "name": "reproducibility_manifest",
        "command": "python experiments/reproducibility_manifest.py",
        "purpose": "Record environment metadata and file hashes.",
        "expected": "experiments/results/reproducibility_manifest.json",
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(project_root: Path, relative_path: str) -> dict:
    path = project_root / relative_path
    if not path.exists():
        return {
            "path": relative_path,
            "exists": False,
            "sha256": "",
            "bytes": 0,
        }
    return {
        "path": relative_path,
        "exists": True,
        "sha256": sha256_file(path),
        "bytes": int(path.stat().st_size),
    }


def package_versions(package_names: list[str] | None = None) -> dict:
    versions = {}
    for name in package_names or PACKAGE_NAMES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def git_metadata(project_root: Path) -> dict:
    return {
        "commit": _git(project_root, "rev-parse", "HEAD"),
        "branch": _git(project_root, "rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(_git(project_root, "status", "--porcelain")),
    }


def build_reproducibility_manifest(
    project_root: str | Path = ".",
    result_files: list[str] | None = None,
    source_files: list[str] | None = None,
    timestamp: str | None = None,
) -> dict:
    """Build a reproducibility manifest without reading or writing secrets."""
    root = Path(project_root)
    if result_files is None:
        result_files = RESULT_FILES
    if source_files is None:
        source_files = SOURCE_FILES
    return {
        "schema_version": 1,
        "generated_at_utc": timestamp or datetime.now(timezone.utc).isoformat(),
        "project_root": str(root.resolve()),
        "git": git_metadata(root),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "packages": package_versions(),
        },
        "commands": REPRODUCTION_COMMANDS,
        "result_files": [file_record(root, path) for path in result_files],
        "source_files": [file_record(root, path) for path in source_files],
        "secret_policy": {
            "record_secret_values": False,
            "secret_env_vars": ["SILICONFLOW_API_KEY"],
            "notes": "Manifest records required secret variable names only, never values.",
        },
    }


def write_reproducibility_manifest(
    project_root: str | Path = ".",
    output_path: str | Path = "experiments/results/reproducibility_manifest.json",
    manifest: dict | None = None,
) -> dict:
    root = Path(project_root)
    manifest = manifest or build_reproducibility_manifest(root)
    out = Path(output_path)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return manifest


def _git(project_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()
