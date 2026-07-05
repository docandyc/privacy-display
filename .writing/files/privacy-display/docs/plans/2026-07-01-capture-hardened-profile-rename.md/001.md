# Capture-hardened Profile Rename Implementation Plan

> **For Codex:** Implement this plan in the active Trellis inline session using test-driven development.

**Goal:** Rename the model-specific `vlm` anti-OCR profile to the mechanism-oriented `capture_hardened` profile and use “抗拍强化档” consistently in project and paper text without invalidating historical experiment artifacts.

**Architecture:** `capture_hardened` becomes the canonical runtime and metadata value. The old `vlm` value remains an input-only compatibility alias and historical result label; loaders normalize it at the boundary, while raw experiment JSON remains immutable for provenance. Project documentation and the paper present the new name and explicitly identify `vlm` only as the legacy label where needed.

**Tech Stack:** Python 3, pytest, argparse, Markdown, LaTeX.

---

### Task 1: Define and test the compatibility contract

**Files:**
- Modify: `tests/test_playback_demo.py`
- Modify: `src/demo/playback_demo.py`

1. Add failing tests that require `capture_hardened` to use the aggressive defaults and require legacy `vlm` input to emit canonical metadata.
2. Run the focused tests and confirm they fail because the canonical profile does not exist.
3. Add a single canonicalization helper and canonical profile constants.
4. Run the focused tests and confirm they pass.

### Task 2: Migrate capture orchestration and historical-data loading

**Files:**
- Modify: `tests/test_real_capture_ablation.py`
- Modify: `tests/test_real_capture_vlm_evaluation.py`
- Modify: `experiments/real_capture_ablation.py`
- Modify: `experiments/anti_ocr_profile_ablation.py`
- Modify: `experiments/real_capture_vlm_evaluation.py`

1. Add failing tests for the new capture condition and normalization of historical `vlm` metadata.
2. Run the focused tests and confirm the expected failures.
3. Emit `capture_hardened` for new captures and normalize old profile/condition values when loading historical data.
4. Run the focused tests and confirm they pass.

### Task 3: Update publication-facing terminology

**Files:**
- Modify: `README.md`
- Modify: `docs/paper_framework_zh.md`
- Modify: `../paper/main.tex`
- Modify: `.trellis/spec/backend/quality-guidelines.md`

1. Replace profile-name references with `capture_hardened` / “抗拍强化档” while leaving genuine VLM evaluator/model references unchanged.
2. Mark `vlm` as a legacy compatibility label only where migration context is necessary.
3. Keep all reported metrics unchanged and preserve the documented long-exposure/video boundary.

### Task 4: Verify the migration

1. Search active source and publication files for stale profile-name references.
2. Run profile, capture-orchestration, and real-capture VLM tests.
3. Run the project quality checks required by Trellis.
4. Compile the LaTeX paper if the local toolchain is available.
5. Review the diff to ensure raw result JSON and unrelated user changes were not modified.
