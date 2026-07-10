# Real-Capture Preprocessing Paper Revision Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `test-driven-development`, `trellis-before-dev`, and `verification-before-completion` while implementing this plan task-by-task.

**Goal:** Produce a matched-estimand IEEE Access revision backed by a complete, fixed-grid real-capture preprocessing attack across Tesseract, EasyOCR, and Surya.

**Architecture:** Add a resumable experiment that imports canonical capture metadata and raw OCR rows, generates five deterministic transforms, checkpoints transformed OCR rows by capture/preprocessor/engine, and finalizes only when the complete matrix is present. Extend the existing cluster-analysis contract to expose matched profile means, then use generated artifacts as the sole numerical source for manuscript edits.

**Tech Stack:** Python 3.10/3.11, OpenCV, Pillow, Tesseract, EasyOCR, Surya OCR, pytest, JSON/JSONL, LaTeX/IEEE Access.

---

### Task 1: Define the fixed preprocessing contract

**Files:**
- Create: `privacy-display/tests/test_real_capture_preprocessing_attack.py`
- Create: `privacy-display/experiments/real_capture_preprocessing_attack.py`

**Steps:**
1. Write failing tests for the six manifest entries, deterministic transforms, and invalid method rejection.
2. Run `privacy-display/.venv/bin/python -m pytest tests/test_real_capture_preprocessing_attack.py -q` and verify imports/functions are missing.
3. Implement the immutable transform manifest and preprocessing function by reusing the existing adaptive-attack semantics.
4. Run the focused tests and verify they pass.

### Task 2: Select and key the primary real-capture matrix

**Files:**
- Modify: `privacy-display/tests/test_real_capture_preprocessing_attack.py`
- Modify: `privacy-display/experiments/real_capture_preprocessing_attack.py`

**Steps:**
1. Add failing tests for excluding `d0.5_a15`, selecting `original/deployed/vlm` short captures, collapsing duplicate readability-priority capture units, and producing 288 units per profile.
2. Verify the tests fail for missing selection behavior.
3. Implement metadata loading, capture-unit parsing compatible with `analyze_paper_ocr_clusters.py`, and deterministic primary selection.
4. Verify focused tests pass against fixtures, then run a read-only selection check against the real archive.

### Task 3: Add raw reuse and resumable transformed OCR

**Files:**
- Modify: `privacy-display/tests/test_real_capture_preprocessing_attack.py`
- Modify: `privacy-display/experiments/real_capture_preprocessing_attack.py`

**Steps:**
1. Add failing tests for importing raw rows, checkpoint identity `(capture ID, preprocessor, engine)`, idempotent resume, error persistence, and duplicate rejection.
2. Verify expected failures.
3. Implement JSONL checkpoint loading/appending and per-engine CLI execution.
4. Record Python, OpenCV, engine package/model configuration, command arguments, and transform parameters.
5. Verify focused tests pass.

### Task 4: Finalize the attacker oracle and matched summaries

**Files:**
- Modify: `privacy-display/tests/test_real_capture_preprocessing_attack.py`
- Modify: `privacy-display/experiments/real_capture_preprocessing_attack.py`
- Modify: `privacy-display/tests/test_paper_ocr_cluster_analysis.py`
- Modify: `privacy-display/experiments/analyze_paper_ocr_clusters.py`

**Steps:**
1. Add failing tests showing best-of-preprocessing-and-engine chooses metric-wise maxima across both dimensions and refuses incomplete matrices.
2. Add a failing test requiring paired contrasts to expose `matched_baseline_mean` and `matched_treatment_mean` in rendered Markdown.
3. Verify failures.
4. Implement final JSON/Markdown aggregation and the matched-mean rendering.
5. Verify both focused test modules pass.

### Task 5: Execute and validate all three engine runs

**Files:**
- Generate: `privacy-display/experiments/results/real_capture_preprocessing_attack/*.jsonl`
- Generate: `privacy-display/experiments/results/real_capture_preprocessing_attack.json`
- Generate: `privacy-display/experiments/results/real_capture_preprocessing_attack.md`

**Steps:**
1. Run a two-capture smoke test for Tesseract and EasyOCR.
2. Run a two-capture smoke test for Surya in `.venv-surya`.
3. Execute the complete Tesseract and EasyOCR matrices with resume enabled.
4. Execute the complete Surya matrix with resume enabled.
5. Finalize only after the completeness validator reports every required cell.
6. Cross-check raw imported values against `real_capture_ocr.json` and paired keys against `paper_ocr_clustered_stats.json`.

### Task 6: Update matched estimands in the manuscript

**Files:**
- Modify: `paper/main.tex`

**Steps:**
1. Replace the primary Table 4 rows with matched `N=288` means.
2. Preserve 16.7%/`N=408` as explicitly all-available descriptive evidence.
3. Update abstract, Introduction, Contributions, Results, Discussion, and Conclusion to use the matched 17.8% primary value.
4. Add the fixed-grid preprocessing result using only finalized generated values.
5. Search for stale 16.7% primary wording and mixed-estimand descriptions.

### Task 7: Update research framing, reproduction details, and references

**Files:**
- Modify: `paper/main.tex`
- Modify: `paper/supplementary.tex`
- Modify: `paper/refs.bib`

**Steps:**
1. Add verified BibTeX metadata for Bao et al. (2026) and the 2025 *Displays* study.
2. Add the protocol-specific novelty sentence and three research questions.
3. Add an OCR/preprocessing reproducibility table or compact main-text summary, with full configuration in the supplement.
4. State recorded versus unknown camera controls and explain the post-hoc common-setting subset from archive chronology.
5. Remove the unsupported 2--5 ms panel-transition number.
6. Apply the requested observational causal wording and manuscript-defined threshold terminology.
7. Search for stale absolute novelty, amplitude-causal, mechanistic, and “strict target” wording.

### Task 8: Verify code, artifacts, and rendered papers

**Files:**
- Regenerate: `paper/main.pdf`
- Regenerate: `paper/supplementary.pdf`

**Steps:**
1. Run focused preprocessing and cluster-analysis tests.
2. Run the relevant real-capture/OCR test subset.
3. Validate JSON and Markdown aggregate arithmetic with an independent script.
4. Build main and supplementary documents using the project LaTeX workflow.
5. Scan logs for undefined citations/references, unresolved placeholders outside the approved user/author scope, and meaningful overfull boxes.
6. Render and inspect pages containing the abstract, primary table, preprocessing results, related work, and references.
7. Perform a requirement-by-requirement completion audit against the Trellis PRD.
