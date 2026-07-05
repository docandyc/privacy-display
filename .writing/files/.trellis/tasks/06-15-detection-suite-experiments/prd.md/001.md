# Land Detection Suite Experiments

## Goal

Build and document a reproducible detection/video/tracking experiment suite for the privacy-display project. The suite should replace the weak single-image YOLO pseudo-reference result with real COCO val2017 and MOT17 evaluations, while preserving the existing attack-frame pipeline and lightweight local test path.

## Requirements

* Add a pluggable detector interface for YOLO26x, RT-DETR-x, Faster R-CNN, and RetinaNet.
* Evaluate COCO val2017 with real annotations and report mAP, mAP50, mAP75, AP small/medium/large, AR, and image count for clean, single-subframe, and temporal-average variants.
* Evaluate MOT17 frame-level person detection for the same model/attack matrix and report mAP, mAP50, recall, precision, and frame count.
* Evaluate MOT17 tracking with a shared ByteTrack-style tracker path and report MOTA, MOTP, IDF1, optional HOTA, and frame count.
* Provide smoke/sample modes so local CPU tests can run without downloading full datasets or heavy weights.
* Provide one-command server scripts for dependency setup, dataset download, and full experiment execution.
* Document the expected server dataset layout and commands clearly.
* Preserve existing experiment scripts, result files, and publication summary behavior.

## Acceptance Criteria

* [ ] `src/attack/detectors.py` exposes `ObjectDetector`, concrete detector adapters, COCO category mappings, and `build_detector`.
* [ ] `src/evaluation/coco_eval.py` can run pycocotools COCOeval when available and falls back to deterministic simple metrics for tests when pycocotools is absent.
* [ ] `src/evaluation/mot.py` can read MOT17 frame/GT data, filter person GT, compute detection metrics, and compute tracking metrics.
* [ ] New experiment CLIs produce JSON files under `experiments/results/` and print compact markdown tables.
* [ ] `requirements-detection.txt`, dataset download scripts, and a one-key `scripts/run_detection_suite.sh` are present.
* [ ] Publication summary and reproducibility manifest include the new result files and reproduction commands.
* [ ] Unit tests cover detector adapters/mappings, COCO experiment schema, MOT detection schema, MOT tracking schema, publication summary additions, and manifest command registration.
* [ ] Existing detection/publication tests still pass.

## Definition of Done

* Tests added or updated for new behavior.
* Targeted pytest commands pass locally.
* Server run instructions explain setup, data placement, smoke run, and full run.
* No full COCO/MOT experiment is run on the local Mac; full evaluation remains a server operation.

## Technical Approach

Reuse the existing privacy subframe attack path: for each image/frame, generate `clean`, `single_subframe`, and `temporal_average` variants through `MaskGenerator`, `NoiseInjector`, `SubframeComposer`, and `CameraSimulator`. Detection adapters normalize all model outputs to `DetectionBox` plus COCO class labels. COCO/MOT helpers own dataset parsing and metric aggregation so experiment scripts stay thin.

Dataset defaults:

* COCO root: `data/coco` inside `privacy-display`, containing `val2017/` and `annotations/instances_val2017.json`.
* MOT17 root: `data/MOT17` inside `privacy-display`, containing `train/MOT17-*/img1` and `train/MOT17-*/gt/gt.txt`.
* Server scripts accept `COCO_ROOT`, `MOT17_ROOT`, and `RESULTS_DIR` overrides.

## Decision (ADR-lite)

**Context**: The thesis needs credible object-detection, video-detection, and tracking evidence without breaking the existing lightweight local workflow.

**Decision**: Implement real dataset evaluation as optional, dependency-gated scripts with fake/small-data test paths and a separate `requirements-detection.txt`.

**Consequences**: The repository remains usable on CPU/local machines, while the heavy server path can install COCO/MOT/ByteTrack dependencies and run full experiments on RTX 4090 GPUs.

## Out of Scope

* Training or fine-tuning detectors.
* Running the full COCO/MOT experiments locally.
* Requiring TrackEval/HOTA for the default local test path; HOTA is optional if a server has TrackEval installed.
* Removing or changing the legacy `detection_attack.py` / `detection_attack_yolo.json` experiment.

## Technical Notes

* Source plan: `/Users/andyhuang/.claude/plans/24g-4090-yolo-yolo26x-fast-r-cnn-rt-det-buzzing-snowflake.md`.
* Existing attack pipeline: `privacy-display/experiments/detection_attack.py`.
* Existing detection box API: `privacy-display/src/attack/detection_evaluator.py`.
* Existing summary/manifest integration points: `privacy-display/src/evaluation/publication_summary.py`, `privacy-display/src/evaluation/reproducibility_manifest.py`.
* Relevant spec: `.trellis/spec/backend/quality-guidelines.md`.
