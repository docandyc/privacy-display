# Fix anti-OCR ablation rigor gaps

## Goal

Repair the rigor issues found in the anti-OCR profile ablation and webstudy synchronization review so the experiment outputs can be safely used in the thesis/paper pipeline.

## What I already know

* `experiments/anti_ocr_profile_ablation.py` was added to measure anti-OCR overlay profiles, stripe/glyph grid points, and weak inversion alpha.
* Review found several paper-risk gaps: Block 1 says deployed but omits inversion, VLM exceptions are recorded as zero recovery, "strongest camera" naming overclaims, Block 3 long exposure repeats only the first cycle, and publication summary truncates away key alpha rows.
* Worktree was clean before this task started.

## Requirements

* Block 1 must distinguish overlay-only measurements from full deployed measurements, or include a full deployed condition with `inversion_alpha=0.2`.
* VLM optional metrics must not turn API/model errors into successful zero-recovery samples; errors must be counted or surfaced as unavailable.
* The screen-camera suite metric must not be mislabeled as the global strongest attacker unless it actually includes all attacker families being compared.
* Block 3 long-exposure alpha sweep must integrate the multi-cycle playback sequence rather than repeating only the first cycle when `cycles > 1`.
* Publication summary must surface anti-OCR ablation rows that matter for the paper, including deployed profile and inversion alpha rows, not silently truncate them out.
* Tests must cover the above behavior without requiring live OCR/VLM services where practical.

## Acceptance Criteria

* [ ] Focused tests for `test_anti_ocr_profile_ablation.py`, `test_publication_summary.py`, and relevant playback/webstudy tests pass.
* [ ] The full test suite passes, or any failure is clearly unrelated and documented.
* [ ] `publication_summary` regenerated or generation behavior verified so anti-OCR rows appear in the summary artifact.
* [ ] Existing webstudy behavior remains: masked typing uses weak inversion, ratings do not.

## Out of Scope

* Running live VLM calls or full human-subject webstudy sessions.
* Re-running the final 16-sample OCR experiment unless needed for structural verification.

## Technical Notes

* Likely files: `privacy-display/experiments/anti_ocr_profile_ablation.py`, `privacy-display/src/evaluation/publication_summary.py`, `privacy-display/tests/test_anti_ocr_profile_ablation.py`, `privacy-display/tests/test_publication_summary.py`.
* Current smoke result is only 4 samples and should not be treated as the final paper dataset.
