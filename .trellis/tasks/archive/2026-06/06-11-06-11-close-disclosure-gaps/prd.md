# Close disclosure implementation gaps

## Goal

Complete the remaining PoC-scope implementation gaps from the technical disclosure review after G1/PaddleOCR was finished. The target is to cover G2-G13 with code, lightweight tests, reproducible experiment artifacts, and honest documentation that distinguishes implemented PoC behavior from hardware/driver future work.

## What I Already Know

* G1 is complete in commit `7fd5d07`.
* The remaining gaps are G2-G13 from `技术交底书实现情况Review.md` and the Claude plan in `未命名.md`.
* The repo is a single Python project under `privacy-display/`.
* Existing patterns favor small pure-Python modules, NumPy/Torch optional fallbacks, and lightweight unit tests that avoid model downloads.
* `.trellis/` is gitignored, so task/spec updates are local workflow state only.

## Requirements

* G2: add detection evaluation support and a reproducible detection attack experiment without requiring new network downloads.
* G3: add an off-axis camera attack model and experiment comparing frontal vs off-axis temporal averaging.
* G4: add spatial-temporal complementary noise splitting with per-pixel zero-sum and local-neighborhood cancellation tests.
* G5: add a lightweight U-Net-style learned reconstruction attack and experiment artifact.
* G6: add a real differentiable OCR-style target path with robust fallback and explicit gradient source tracking.
* G7: add visual fatigue policy utilities for adaptive refresh, blue-light filtering, and viewing-distance compensation.
* G8: add display bandwidth calculation and interface fit decisions.
* G9: add permutation hash tracking to timing tokens.
* G10: add HLG OETF/EOTF functions with round-trip tests.
* G11: add simulated ALS ambient-light adaptation preserving Weber contrast.
* G12: add deterministic pregenerated mask/permutation ring buffers.
* G13: add JSON configuration persistence for n/epsilon/alpha/key/refresh settings and wire the demo/window entry point to it.

## Acceptance Criteria

* [ ] Unit tests cover all new pure-function and fallback behavior.
* [ ] `pytest tests/ -q` passes.
* [ ] `python main.py demo` completes.
* [ ] `experiments/results/` includes detection, view/off-axis, and U-Net reconstruction result JSON files.
* [ ] `README.md`, `改进文档.md`, and `技术交底书实现情况Review.md` reflect G2-G13 status and measured results.
* [ ] Git commit records the completed implementation.

## Out of Scope

* Kernel/display-driver injection.
* Downloading or committing model weights.
* Claiming YOLOv8/Faster R-CNN production metrics when cached weights are unavailable.
* Human-subject studies or real 240/480Hz hardware validation.

## Technical Notes

* Use existing modules where possible:
  * `src/core/mask_generator.py`
  * `src/core/noise_injector.py`
  * `src/core/timing_controller.py`
  * `src/core/hdr_compensation.py`
  * `src/attack/camera_simulator.py`
  * `src/attack/reconstruction_attack.py`
  * `src/evaluation/benchmark.py`
* Keep heavy OCR/detector engines out of unit tests; use deterministic synthetic or fake evaluators.
* Record experiments truthfully, including weaker-than-disclosure results.
