# Fix All English Paper Review Findings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Produce an evidence-consistent IEEE Access manuscript that resolves every current P0/P1/P2 finding using existing archives and explicitly narrows claims where new physical captures are unavailable.

**Architecture:** Treat canonical OCR/VLM/capture archives as immutable inputs. Add tested analysis layers for explicit sensitive-field recovery, matched primary estimates, preprocessing attacks, acquisition-order sensitivity, and missing-response bounds; generate machine-readable and Markdown artifacts; then revise the manuscript from those artifacts. Hardware-only gaps are closed by removing causal/worst-case claims and documenting protocols rather than inventing results.

**Tech Stack:** Python 3, pytest, NumPy/Pandas-style JSON analysis, OpenCV/Pillow, existing OCR runtimes, LaTeX/XeLaTeX, BibTeX, Poppler.

---

### Task 1: Baseline, preserve concurrent work, and lock canonical inputs

**Files:**
- Read: `paper/main.tex`
- Read: `paper/supplementary.tex`
- Read: `privacy-display/experiments/results/real_capture_ocr.json`
- Read: `privacy-display/src/attack/ocr_evaluator.py`
- Read: `privacy-display/experiments/real_capture_preprocessing_attack.py`
- Modify: `.trellis/tasks/07-10-fix-all-english-paper-review-findings/prd.md`

**Step 1: Record the focused dirty state and hashes**

Run:

```bash
git status --short -- paper privacy-display/src/attack/ocr_evaluator.py \
  privacy-display/experiments privacy-display/tests
shasum -a 256 privacy-display/experiments/results/real_capture_ocr.json
```

Expected: existing unrelated figure and Windows-path changes remain visible; the canonical archive hash is recorded in the task research notes.

**Step 2: Run focused baseline tests**

Run:

```bash
cd privacy-display
../.venv/bin/python -m pytest \
  tests/test_ocr_evaluator.py \
  tests/test_paper_ocr_cluster_analysis.py \
  tests/test_real_capture_preprocessing_attack.py -q
```

Expected: current tests pass before new regression cases are added.

**Step 3: Verify current manuscript build state without editing prose**

Run:

```bash
cd paper
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

Expected: 20-page Letter PDF, no undefined citations/references.

**Step 4: Commit only the implementation plan**

```bash
git add docs/plans/2026-07-10-fix-all-english-paper-review-findings.md
git commit -m "docs(plan): sequence English paper review fixes"
```

### Task 2: Replace paper-facing heuristic tokens with explicit sensitive fields

**Files:**
- Create: `privacy-display/experiments/config/real_capture_sensitive_fields.json`
- Create: `privacy-display/experiments/analyze_sensitive_field_recovery.py`
- Create: `privacy-display/tests/test_sensitive_field_recovery.py`
- Modify: `privacy-display/src/attack/ocr_evaluator.py`
- Modify: `privacy-display/tests/test_ocr_evaluator.py`
- Create: `privacy-display/experiments/results/sensitive_field_recovery.json`
- Create: `privacy-display/experiments/results/sensitive_field_recovery.md`

**Step 1: Write failing extractor regressions**

Add tests proving ordinary prose is not a structured sensitive token:

```python
def test_sensitive_tokens_exclude_ordinary_mixed_case_and_long_words():
    tokens = _sensitive_tokens(
        "Part Writing Directions For With increasing application technology"
    )
    assert tokens == []
```

Run:

```bash
cd privacy-display
../.venv/bin/python -m pytest \
  tests/test_ocr_evaluator.py::test_sensitive_tokens_exclude_ordinary_mixed_case_and_long_words -q
```

Expected: FAIL because the current heuristic admits mixed-case and long words.

**Step 2: Write failing manifest and aggregation tests**

Test that:

```python
manifest = load_sensitive_field_manifest(path)
assert manifest["account_00"]["fields"] == ["6222 0000 1234 5678"]
metrics = score_sensitive_fields("6222000012345678", manifest["account_00"]["fields"])
assert metrics == {"recovered": 1, "total": 1, "micro_recall": 1.0}
```

Also test normalization, duplicate fields, unknown content IDs, zero-field items, per-capture engine oracle, matched common-setting selection, micro totals, and sample-macro summaries.

Run:

```bash
cd privacy-display
../.venv/bin/python -m pytest tests/test_sensitive_field_recovery.py -q
```

Expected: FAIL because the analysis module and manifest do not exist.

**Step 3: Implement the minimal explicit-field analysis**

Requirements:

- Manifest keys must match the 12 archived `content_item` identifiers.
- Every field must be copied exactly from the corresponding ground truth and annotated with a type (`credential`, `digit_string`, `url_path`, `code_key`, or `none`).
- Scoring normalizes case and whitespace/punctuation only as documented; it must not discover fields heuristically.
- Report token-level micro exact recovery and sample-level macro exact recovery separately.
- Collapse engines attacker-favorably per capture, then produce matched common-setting and full-pool sensitivity summaries.
- Preserve the unrelated `ntpath`/Windows changes already present in `ocr_evaluator.py`.

**Step 4: Run tests and regenerate outputs**

```bash
cd privacy-display
../.venv/bin/python -m pytest \
  tests/test_ocr_evaluator.py tests/test_sensitive_field_recovery.py -q
../.venv/bin/python experiments/analyze_sensitive_field_recovery.py \
  --input experiments/results/real_capture_ocr.json \
  --manifest experiments/config/real_capture_sensitive_fields.json \
  --json-out experiments/results/sensitive_field_recovery.json \
  --md-out experiments/results/sensitive_field_recovery.md
```

Expected: tests PASS; JSON and Markdown identify the canonical archive hash, field counts, matched/full pools, and all computed values.

**Step 5: Commit**

```bash
git add privacy-display/src/attack/ocr_evaluator.py \
  privacy-display/tests/test_ocr_evaluator.py \
  privacy-display/experiments/config/real_capture_sensitive_fields.json \
  privacy-display/experiments/analyze_sensitive_field_recovery.py \
  privacy-display/tests/test_sensitive_field_recovery.py \
  privacy-display/experiments/results/sensitive_field_recovery.*
git commit -m "fix(metrics): replace heuristic sensitive-token paper metric"
```

### Task 3: Finish matched estimates and fixed preprocessing attack

**Files:**
- Modify: `privacy-display/experiments/analyze_paper_ocr_clusters.py`
- Modify: `privacy-display/tests/test_paper_ocr_cluster_analysis.py`
- Modify: `privacy-display/experiments/real_capture_preprocessing_attack.py`
- Modify: `privacy-display/tests/test_real_capture_preprocessing_attack.py`
- Create/Update: `privacy-display/experiments/results/paper_ocr_clustered_stats.json`
- Create/Update: `privacy-display/experiments/results/paper_ocr_clustered_stats.md`
- Create: `privacy-display/experiments/results/real_capture_preprocessing_attack.json`
- Create: `privacy-display/experiments/results/real_capture_preprocessing_attack.md`
- Create: `privacy-display/experiments/results/real_capture_preprocessing_rows/*.jsonl`

**Step 1: Add failing matched-estimand tests**

Assert the generated primary summary contains:

```python
assert common["original"]["matched_n"] == 288
assert common["deployed"]["matched_n"] == 288
assert common["high_suppression"]["matched_n"] == 288
assert common["deployed"]["matched_char_mean"] == pytest.approx(0.178, abs=0.001)
assert common["unbalanced_deployed_char_mean"] == pytest.approx(0.167, abs=0.001)
```

Run the single test and verify FAIL before modifying the generator.

**Step 2: Implement one primary matched summary**

Generate matched means, exact-match rates, upper-tail quantiles, and explicit-field metrics from the same duplicate-averaged 288 units. Keep all-available 408-capture values in a separately named sensitivity block.

**Step 3: Run preprocessing module tests**

```bash
cd privacy-display
../.venv/bin/python -m pytest tests/test_real_capture_preprocessing_attack.py -q
```

Expected: PASS before the expensive run; add tests if current report omits runtime versions, failures, archive hash, or matched metric sources.

**Step 4: Execute resumable fixed-grid OCR**

Run the script's `--help`, then execute the full approved matrix: three profiles, eight common-setting geometries, six fixed preprocessors including raw, and Tesseract/EasyOCR/Surya. Use per-engine JSONL checkpoints and resume rather than restarting completed cells.

Expected: 984 selected captures; 288 matched units/profile after duplicate folding; no unacknowledged OCR errors; complete matrix validation passes.

**Step 5: Build attacker-oracle report**

Report raw best-of-engine and best-of-preprocessing-and-engine values with the same matched units and cluster-resampling scheme. Do not report a partial engine matrix as final.

**Step 6: Run tests and commit**

```bash
cd privacy-display
../.venv/bin/python -m pytest \
  tests/test_paper_ocr_cluster_analysis.py \
  tests/test_real_capture_preprocessing_attack.py -q
```

Commit only the analysis, tests, and generated artifacts for this task.

### Task 4: Add acquisition, camera, corpus, and statistical audits

**Files:**
- Create: `privacy-display/experiments/audit_real_capture_design.py`
- Create: `privacy-display/tests/test_real_capture_design_audit.py`
- Create: `privacy-display/experiments/results/real_capture_design_audit.json`
- Create: `privacy-display/experiments/results/real_capture_design_audit.md`
- Modify: `privacy-display/experiments/analyze_paper_ocr_clusters.py`
- Modify: `privacy-display/tests/test_paper_ocr_cluster_analysis.py`

**Step 1: Write failing audit tests**

Tests must detect:

- fixed profile order from metadata/filenames;
- the eight common-setting and one noncomparable geometry;
- nominal exposure controls and unknown AE/gain/AWB/focus states;
- CET6 ground truth containing non-ASCII/CJK characters;
- the deterministic publication-subset rule;
- repeated readability-priority content and its duplicate-folding rule.

**Step 2: Implement the audit**

The audit must distinguish `recorded`, `derived`, and `unknown` fields. Never convert UVC log2 values into a claim of physically measured shutter time.

**Step 3: Replace invalid interval language in generated reports**

Use `content-cluster resampling interval` for matched contrasts. Use `capture-resampling summary` for descriptive tables if dependence remains. Remove any inference based only on marginal interval overlap.

**Step 4: Run and commit**

```bash
cd privacy-display
../.venv/bin/python -m pytest \
  tests/test_real_capture_design_audit.py \
  tests/test_paper_ocr_cluster_analysis.py -q
../.venv/bin/python experiments/audit_real_capture_design.py
```

Expected: audit files enumerate every limitation with source paths and no unknown field is presented as measured.

### Task 5: Make digital and VLM boundary evidence auditable

**Files:**
- Create: `privacy-display/experiments/build_paper_boundary_evidence.py`
- Create: `privacy-display/tests/test_paper_boundary_evidence.py`
- Create: `privacy-display/experiments/results/paper_boundary_evidence.json`
- Create: `privacy-display/experiments/results/paper_boundary_evidence.md`
- Modify: `paper/supplementary.tex`

**Step 1: Write failing evidence-extraction tests**

Given archived digital/VLM result files, assert each paper-facing number has:

```python
{
    "value": 0.952,
    "metric": "character_recovery",
    "sample_count": 120,
    "corpus": "...",
    "attack_set": ["..."],
    "source_file": "...",
}
```

Include 95.2%, 94.3%, 93.0%, 81.2%, 56.6%, SSIM, Delta-E, and VLM effective-call bounds.

**Step 2: Implement extraction and VLM bounds**

For every failure-affected VLM cell, calculate failure-as-zero and failure-as-one bounds. If source data cannot support a number, mark it unavailable and remove it from the manuscript rather than reproducing it from prose.

**Step 3: Repair supplementary detection/tracking evidence**

- Specify the deterministic three-frame selection rule.
- Rename exposure-confounded figure/caption language to condition differences, not protection effects.
- Remove the approximate TrackEval-failed simulation table unless official outputs and definitions can be verified from the existing workspace.

**Step 4: Generate a compact supplementary evidence table and commit**

Keep detailed protocols in supplementary material so the main article can remain within the page recommendation.

### Task 6: Revise the English manuscript from generated evidence

**Files:**
- Modify: `paper/main.tex`
- Modify: `paper/supplementary.tex`
- Modify if needed: `paper/refs.bib`
- Modify: `privacy-display/README.md`

**Step 1: Update numbers only from generated artifacts**

Synchronize abstract, introduction, contributions, primary table, findings, discussion, limitations, and conclusion with matched estimates, explicit sensitive-field results, and preprocessing-oracle results.

**Step 2: Repair methods and equations**

- Change normalized inversion to `alpha (1 - I)` or explicitly define an 8-bit variable.
- Document compositing order, proxy-model status, masks, overlays, seeds/cycles, rectification, crop, OCR versions/models/languages/settings, and failures.
- Call 3.91 ms a nominal/logged UVC setting unless physically measured evidence exists.
- Disclose fixed profile order and unknown controls.
- Correct the corpus language description and selection rule.

**Step 3: Remove unsupported causal/worst-case claims**

Use observation/hypothesis wording for mechanisms. State explicitly that no luminance-matched/static control, photometric timing, randomized-order recapture, or worst-phase physical sweep was performed. Foreground the inversion-slot failure and do not call uncontrolled-phase means robust.

**Step 4: Fix logic, terminology, and IEEE style**

- Define OCR/UVC/VLM/GPU/CLAHE independently at first body use and all supplement acronyms.
- Replace absolute novelty/priority claims with `to our knowledge` plus scope.
- Rename contrast header to `Unprotected minus profile`.
- Qualify screenshot capture point.
- Replace post-hoc `design goal` language with `manuscript-defined interpretive benchmark` unless timestamped evidence proves otherwise.
- Reduce repeated `boundary/frontier/closure/evidence hierarchy` language.
- Remove redundant engine-scope paragraphs.
- Add a truthful AI-assisted language-editing disclosure consistent with IEEE Access policy, while leaving author/funding details untouched.

**Step 5: Update reproducibility and release wording**

Do not claim an immutable public release until one exists. State the repository, canonical archive identifiers, and exact analysis artifact names; prepare a stable local submission tag only after the final verified commit, without pushing unless separately authorized.

**Step 6: Keep main manuscript within the page recommendation**

Move protocol detail to supplementary material and tighten repeated caveats. If the verified main PDF still exceeds 20 pages, record the IEEE Access pre-inquiry requirement rather than silently shrinking figures or fonts.

**Step 7: Run textual consistency searches**

Search for stale values and wording:

```bash
rg -n '16\.7|24\.0|96\.5|strict.*target|measured.*3\.91|All 12.*ASCII|\bboundary\b|\bfrontier\b|CLAHE-type' paper/main.tex paper/supplementary.tex
```

Expected: every remaining match is intentionally labeled and supported.

### Task 7: Verification, visual QA, and final review mapping

**Files:**
- Modify: `.trellis/tasks/07-10-fix-all-english-paper-review-findings/prd.md`
- Create: `.trellis/tasks/07-10-fix-all-english-paper-review-findings/research/final-review-mapping.md`

**Step 1: Run targeted and full feasible tests**

```bash
cd privacy-display
../.venv/bin/python -m pytest \
  tests/test_ocr_evaluator.py \
  tests/test_sensitive_field_recovery.py \
  tests/test_paper_ocr_cluster_analysis.py \
  tests/test_real_capture_preprocessing_attack.py \
  tests/test_real_capture_design_audit.py \
  tests/test_paper_boundary_evidence.py -q
../.venv/bin/python -m pytest tests/ -q
```

Expected: targeted tests pass; full suite completes without pytest internal error. Any environment-dependent skip/failure is documented, not hidden.

**Step 2: Build both PDFs with XeLaTeX**

```bash
cd paper
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error supplementary.tex
```

Expected: no undefined citations/references; Letter pages; all fonts embedded.

**Step 3: Run structural checks**

Verify 1:1 citation/BibTeX keys, label/reference integrity, absence of `[?]`/`??`, PDF page count, and embedded fonts.

**Step 4: Render and inspect every page**

Render both PDFs to `tmp/pdfs/final-review/`; inspect tables, captions, equations, page breaks, placeholders, and figure legibility.

**Step 5: Map every prior finding**

Create `final-review-mapping.md` with one row per P0/P1/P2 finding and status `fixed`, `reframed using existing evidence`, or `removed because unsupported`. No finding may be marked fixed solely because it was moved into Limitations.

**Step 6: Final task check and commit**

Run `git diff --check`, inspect only scoped changes, then commit in coherent groups without staging unrelated user files.

