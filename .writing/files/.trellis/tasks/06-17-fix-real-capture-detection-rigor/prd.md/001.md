# Fix Real Capture Detection Rigor Bugs

## Goal

Make the COCO/MOT17 real-device capture scripts publication-grade enough to avoid contaminated captures, incomparable sample sets, and uncitable summaries. This task fixes the defects found in code review of Claude's real-capture detection/tracking implementation.

## What I Already Know

* Current changes add `experiments/real_capture_detection.py`, `experiments/real_capture_mot.py`, playback `--frames-dir`, summary wiring, manifest wiring, a Windows batch file, and tests.
* Review found correctness risks in playback hot-swap synchronization, HUD contamination, missing-frame handling, capture provenance, publication summary availability, MOT stop-motion scope, and missing tests.
* Existing Trellis backend quality guidelines require real-camera capture orchestration to use deterministic playback readiness, preserve structured metadata, keep dry runs bounded, and make publication artifacts reproducible.

## Requirements

* Playback hot-swaps must provide a deterministic acknowledgement before camera capture starts.
* Real capture playback must not render HUD overlays into COCO/MOT frames.
* Evaluation must compare attacks on the same captured COCO images or MOT frames, or fail with a clear error.
* Result JSON must include enough capture provenance to audit backend, exposure, ROI, letterbox/cropping, frame counts, playback command, and capture manifest paths.
* Publication summary must mark real-capture detection/tracking sections unavailable when result files exist but contain no citable rows, missing baselines, zero samples, or mismatched attack sample counts.
* MOT real-capture output must explicitly identify the current method as stop-motion physical-frame validation, not continuous video capture.
* Tests must cover the new behavior, including new publication summary and manifest wiring.

## Acceptance Criteria

* [ ] `PersistentDisplay.show()` waits for an explicit epoch acknowledgement or fails before camera capture.
* [ ] Playback supports disabling HUD from CLI, and real-capture scripts pass that option.
* [ ] COCO evaluation fails or rejects publication output when real attacks do not share the same captured image IDs.
* [ ] MOT evaluation fails or rejects publication output when real attacks do not share the same captured frame IDs.
* [ ] Real-capture result JSON records capture provenance and sample coverage.
* [ ] Publication summary reports unavailable real-capture sections for uncitable/empty/mismatched reports.
* [ ] Reproducibility manifest includes the real-capture scripts/results and capture manifest artifacts where paths are known.
* [ ] Targeted pytest suites and syntax checks pass.

## Definition of Done

* Tests are added before production fixes for changed behavior.
* Existing COCO/MOT detection-suite tests still pass.
* No hardware is required for unit tests; hardware-only behavior is covered through fakes/stubs.
* No unrelated user changes are reverted.

## Technical Approach

Add minimal protocol plumbing to playback and capture orchestration: an acknowledgement file is safer than trying to reuse the existing local stdout queue. Add a `--no-hud` CLI flag to playback and pass it from real-capture scripts. Add sample coverage helpers that compute the shared attack intersection before detector evaluation and write missing IDs into reports. Enrich capture manifests/results with provenance gathered at capture time. Harden summary availability checks with explicit reason strings.

## Out of Scope

* Running real COCO/MOT17 hardware capture on this machine.
* Adding full continuous MOT video capture; current implementation will be labeled as stop-motion validation.
* Downloading datasets, model weights, BoxMOT, or TrackEval.

## Technical Notes

* Relevant files: `privacy-display/src/demo/playback_demo.py`, `privacy-display/experiments/real_capture_detection.py`, `privacy-display/experiments/real_capture_mot.py`, `privacy-display/src/evaluation/publication_summary.py`, `privacy-display/src/evaluation/reproducibility_manifest.py`, and matching tests.
* Relevant spec: `.trellis/spec/backend/quality-guidelines.md`, scenarios "Detection Suite Server Experiments", "Real Camera Capture Ablation Orchestration", "Publication Result Summary", and "Reproducibility Manifest".
