# Land Windows One-Click Real Capture Ablation

## Goal

Implement the real-device ablation workflow described in `/Users/andyhuang/Desktop/240hz-windows-windows-usb-windows-serialized-whale_副本.md` so the `privacy-display` project can run Windows + EMEET S600 real camera capture experiments with a one-command orchestrator, calibration helpers, and reproducible OCR summaries.

## What I Already Know

* The existing ablation experiments are simulation-based; the new work must collect real USB webcam captures to validate rolling shutter, exposure, perspective, moire, and physical display/camera behavior.
* Target setup: Windows, 2560x1600@240Hz display, EMEET SmartCam S600, OpenCV camera index 1, UVC modes 3840x2160@30 and 1920x1080@60 MJPG.
* The deployed condition is `python main.py playback --n 4 --anti-ocr-profile strong --inversion --stripe-alpha 0.10 --glyph-alpha 0.12`.
* The project already has reusable pieces:
  * `experiments/real_capture_shoot.py` for capture metadata and image writes.
  * `src/demo/playback_demo.py` for deployment-faithful playback frame generation.
  * `experiments/build_corpus.py` and `src/evaluation/sampling.py` for publication corpus sampling.
  * `src/evaluation/real_capture.py` and `src/attack/ocr_evaluator.py` for OCR metrics.
  * `experiments/anti_ocr_profile_ablation.py` for deployed constants and simulated ablation design.

## Requirements

* Update `experiments/real_capture_shoot.py` to support platform-aware OpenCV backends:
  * Windows: prefer MSMF, fallback DSHOW.
  * macOS: AVFoundation.
  * Linux: V4L2.
  * Default to EMEET S600 index 1 and `usb_webcam` metadata.
  * Add backend-aware manual exposure support and log2-exposure seconds conversion.
  * Preserve existing metadata schema and capture helpers.
* Update playback so the orchestrator can run it unattended:
  * `--fullscreen` opens a full-screen pygame display surface.
  * `--show-original` displays the input image directly as an unprotected baseline.
  * Print `PLAYBACK_READY` after frame/surface preparation and before the main loop.
  * Allow explicit inversion-alpha values through 1.0 for ablation references.
* Add `experiments/real_capture_calibrate.py`:
  * ROI/homography selection with four clicked points saved to calibration JSON.
  * Exposure calibration scaffold that scans exposure values and writes short/long settings.
  * Keep the calibration script usable on Windows without new dependencies.
* Add `experiments/real_capture_ablation.py` as the main one-command orchestrator:
  * Supports `--study {1,2,3,all}`, `--dry-run`, `--list-conditions`, subset sizing, attacks, positions, and OCR engines.
  * Builds study plans for component ablation, parameter sweeps, and geometry robustness without full cross-product blowup.
  * Starts `main.py playback` with the right flags, waits for `PLAYBACK_READY`, captures stills/video bursts, optionally rectifies ROI, writes metadata, and can run OCR analysis.
  * Provides pure helper functions for condition-to-playback flags, planning, padding, ROI rectification, metadata enrichment, and offline video attack frame selection.
* Extend `src/evaluation/real_capture.py` to include structured metadata fields and summaries by `(ablation, attack)`, while preserving existing outputs.
* Add `tests/test_real_capture_ablation.py` and update existing tests for the new Windows capture and playback helpers.
* Add a Windows one-click batch entrypoint for the typical workflow.

## Acceptance Criteria

* [ ] `python experiments/real_capture_shoot.py --list` can enumerate devices on Windows through the platform backend.
* [ ] `python experiments/real_capture_shoot.py --probe --device 1` reports effective modes and manual exposure read-back.
* [ ] `python main.py playback --show-original --fullscreen --benchmark 1` parses and reaches the playback path.
* [ ] `python experiments/real_capture_ablation.py --study all --dry-run` prints a bounded plan and exits without opening camera/playback.
* [ ] `python experiments/real_capture_ablation.py --study 1 --subset-size 1 --attacks short --conditions original,deployed --dry-run` shows the intended smoke plan.
* [ ] Unit tests cover exposure mapping, condition flags, study planning, padding/rectification, metadata enrichment, and offline video attack helpers.
* [ ] A Windows `.bat` script gives the user a one-click dry-run/calibrate/run entrypoint with sensible defaults.

## Definition of Done

* Tests added or updated for changed pure behavior.
* Targeted pytest suite passes locally.
* Existing behavior stays backward-compatible where possible.
* No new heavyweight dependencies are introduced.
* The final response includes Windows commands for dry-run, calibration, smoke, and full run.

## Technical Approach

Implement a conservative MVP that is useful immediately on the Windows machine:

* Keep hardware-specific actions behind CLI flags and dry-run-friendly pure helpers.
* Reuse `real_capture_shoot.py` metadata/write helpers rather than inventing a new metadata format.
* Reuse `main.py playback` for display, with small CLI additions only.
* Make geometry study semi-automatic: prompt before each new position, then automate content/condition/attack loops.
* Use ROI JSON files as optional inputs; if absent, capture raw frames and record the missing calibration in notes.

## Decision (ADR-lite)

**Context**: The source plan asks for a realistic Windows real-camera experiment but full hardware verification cannot run on this macOS/Linux development environment.

**Decision**: Land the Windows-compatible scripts and pure tests now, with hardware paths exposed through explicit CLI commands and a dry-run mode that validates the complete experiment plan without camera access.

**Consequences**: The code can be tested here without hardware, while final device validation must be run on the user's Windows + EMEET S600 setup.

## Out of Scope

* Claiming or fabricating real capture results without running the Windows hardware experiment.
* Fully automating physical camera movement for the geometry matrix.
* Adding smartphone or smart-glasses capture beyond the existing metadata import path.
* Adding new OCR/camera dependencies beyond existing OpenCV, Pillow, numpy, pygame, and pytesseract paths.

## Technical Notes

* Relevant specs: `.trellis/spec/backend/index.md`, `.trellis/spec/frontend/index.md`, `.trellis/spec/guides/index.md`.
* Existing tests to keep green include `tests/test_real_capture_shoot.py`, `tests/test_anti_ocr_profile_ablation.py`, and playback-related tests.
* The implementation should preserve `condition` as a string label but add optional structured fields (`ablation`, `attack`, alpha/profile metadata) for richer summaries.
