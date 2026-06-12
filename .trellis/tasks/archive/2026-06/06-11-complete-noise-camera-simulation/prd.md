# Complete adversarial noise and camera simulation

## Goal

Close two implementation gaps from the technical disclosure review: adversarial noise should expose FGSM/PGD, multi-model template rotation, and online update hooks; rolling-shutter simulation should integrate row exposure windows across subframe boundaries instead of selecting one subframe per row.

## What I already know

* `NoiseInjector.generate_fgsm_noise()` currently falls back to Sobel/random noise unless a template is loaded.
* `generate_pytorch_fgsm()` uses a VGG proxy and is not target-model rotation.
* `CameraSimulator.capture_rolling_shutter()` currently assigns one subframe per row using row start time only.
* Existing callers expect `generate_fgsm_noise()` to remain available.

## Requirements

* Preserve existing public APIs where practical.
* Add PGD noise generation with bounded `L_inf` perturbation.
* Add target-model rotation across Tesseract, EasyOCR, PaddleOCR, YOLOv8, and Faster R-CNN identifiers.
* Add template selection and model-specific template storage support.
* Add an online update mechanism that reacts when recognition success rises.
* Replace rolling-shutter capture with exposure-window weighted temporal mixing.
* Add focused tests for the new adversarial-noise and rolling-shutter behavior.

## Acceptance Criteria

* [ ] Unit tests cover FGSM/PGD bounded output, rotation, online update, and rolling-shutter weighted blending.
* [ ] Existing tests continue to pass.
* [ ] `main.py demo` still runs.

## Out of Scope

* Downloading or training real OCR/detection model weights.
* Claiming that surrogate noise equals production-grade end-to-end attacks.
* Implementing actual camera hardware capture.

## Technical Notes

* Affected files: `src/core/noise_injector.py`, `src/attack/camera_simulator.py`, tests.
* Keep implementation deterministic/testable and offline-friendly.
