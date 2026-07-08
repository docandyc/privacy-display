# IEEE Access Manuscript Revision Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Revise the English IEEE Access manuscript into a concise, evidence-bounded submission using only the existing physical-capture archive and verified references.

**Architecture:** Add a reproducible cluster-aware OCR contrast analysis over the canonical real-capture JSON, then use its outputs to revise the manuscript's claim hierarchy. Move weak detection/tracking diagnostics to a standalone supplementary source, update submission formatting, and verify the final PDF from a clean multi-pass LaTeX/BibTeX build.

**Tech Stack:** Python 3, NumPy, pytest, JSON, LaTeX/IEEE Access, BibTeX, latexmk/XeLaTeX, Poppler.

---

### Task 1: Activate the Trellis task and load implementation guidance

**Files:**
- Read: `.trellis/tasks/07-08-revise-ieee-access-after-review/prd.md`
- Read: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`
- Read: `.agents/skills/trellis-before-dev/SKILL.md`

**Step 1:** Start the task with `python3 ./.trellis/scripts/task.py start .trellis/tasks/07-08-revise-ieee-access-after-review`.

**Step 2:** Load project-specific pre-development guidance and confirm the working tree contains only the approved planning artifacts.

### Task 2: Add cluster-aware paired OCR analysis

**Files:**
- Create: `privacy-display/experiments/analyze_paper_ocr_clusters.py`
- Create: `privacy-display/tests/test_paper_ocr_cluster_analysis.py`
- Create: `privacy-display/experiments/results/paper_ocr_clustered_stats.json`
- Create: `privacy-display/experiments/results/paper_ocr_clustered_stats.md`
- Read: `privacy-display/experiments/results/real_capture_ocr.json`

**Step 1: Write failing tests**

Cover:

- per-capture best-of-engine reduction;
- deterministic content-cluster bootstrap with seed `20260612` and 2,000 resamples;
- matched contrast construction over profile, attack mode, content item, position, and available repeat index;
- transparent dropping/reporting of unmatched rows;
- JSON output containing estimate, CI, cluster count, matched-unit count, resampling unit, and seed.

**Step 2: Run tests and confirm failure**

Run: `cd privacy-display && pytest -q tests/test_paper_ocr_cluster_analysis.py`

Expected: import or missing-function failure.

**Step 3: Implement the analysis**

Parse canonical capture rows, select the maximum `char_accuracy` across engines for each capture, derive stable content/position/round keys from authoritative row metadata, and calculate:

- original short minus deployed short;
- original short minus high-suppression short;
- mask-only short minus deployed short where pairing is valid;
- original short minus mask-only short;
- sensitivity contrasts excluding `d0.5_a15`.

Use a paired cluster bootstrap over content items. Do not silently coerce repeated deployed captures into independent matches; report the matching rule and unmatched counts.

**Step 4: Run tests and generate outputs**

Run:

```bash
cd privacy-display
pytest -q tests/test_paper_ocr_cluster_analysis.py tests/test_real_capture_finalization.py
python experiments/analyze_paper_ocr_clusters.py
```

Expected: tests pass and the JSON/Markdown outputs are deterministic.

**Step 5: Cross-check manuscript headline values**

Confirm the script reproduces the existing group means before using any new contrast interval in the paper.

### Task 3: Revise title, abstract, introduction, and contribution claims

**Files:**
- Modify: `paper/main.tex:37-111`

**Step 1:** Shorten the title to natural English centered on calibrated UVC capture and conventional OCR.

**Step 2:** Rewrite the abstract so it:

- states the profile-level question rather than temporal-only causation;
- names the missing physical luminance match;
- reports the central group means once;
- reports Qwen as `28/36 captures from 12 items`;
- retains the integration/VLM boundary;
- avoids repeating sensitivity numbers that belong in Results.

**Step 3:** Consolidate the Introduction's repeated caveats and define one concrete operational use case without implying it represents ordinary smartphone photography.

**Step 4:** Rewrite Contributions as:

1. controlled profile-level physical measurement;
2. cluster-aware evidence and exposure sensitivity;
3. measured integration/VLM boundaries and an evidence hierarchy.

Do not present detection/tracking diagnostics as a contribution.

### Task 4: Tighten method and experimental interpretation

**Files:**
- Modify: `paper/main.tex:193-324`

**Step 1:** State immediately after the temporal decomposition model that the physical experiment lacks luminance matching and cannot isolate sparse sampling from duty-cycle dimming.

**Step 2:** Define `deployed` as a preselected readability-priority composite profile, not an empirically optimized profile.

**Step 3:** Shorten repeated explanations of noise nonmonotonicity, inversion failure, unmeasured timing, and panel response while retaining all evidence-bearing qualifications.

**Step 4:** Replace capture-level uncertainty as the main inferential emphasis with the new cluster-aware paired contrasts; retain capture-level intervals as descriptive distribution summaries.

### Task 5: Revise OCR and VLM Results

**Files:**
- Modify: `paper/main.tex:327-534`
- Modify if necessary: `privacy-display/experiments/paper_figures/fig_f4_attack_bar.py`
- Regenerate if necessary: `paper/figures/real_capture_bar.pdf`

**Step 1:** Add the cluster-aware paired contrast estimates and matching contract from Task 2.

**Step 2:** Make clear that the 15.1% deployed result is an end-to-end composite-profile observation and does not establish benefit from each component.

**Step 3:** Remove internally conflicting phrases such as `three-engine ceiling likely underestimates` and non-native uses of `caliber`.

**Step 4:** Revise the VLM reporting:

- express 77.8% as 28/36 captures from 12 items;
- keep the failure-free 1.5 m cells as the main cross-model comparison;
- treat GLM cells with content-dependent failures as bounded sensitivity results, not direct model rankings;
- remove repeated VLM numbers outside Abstract, Results, and Conclusion.

### Task 6: Move weak detection/tracking diagnostics to supplementary material

**Files:**
- Create: `paper/supplementary.tex`
- Modify: `paper/main.tex:628-847`

**Step 1:** Create a standalone supplementary source that preserves:

- real-capture detection/tracking setup and tables;
- eight-image simulated detection diagnostic;
- approximate tracking table and limitations;
- associated figures where still informative.

**Step 2:** Remove the detection/tracking subsections and cross-task normalized summary figure from the main paper.

**Step 3:** Replace them with one short paragraph directing readers to supplementary material and explicitly stating that these diagnostics do not extend the primary OCR claim.

**Step 4:** Build the supplement and verify that it has no missing references or figures.

### Task 7: Consolidate Discussion, Limitations, and Conclusion

**Files:**
- Modify: `paper/main.tex:852-929`

**Step 1:** Collapse repeated result recitations into a three-level evidence hierarchy:

1. supported within-link observation;
2. measured failure boundaries;
3. unresolved mechanism/external validity.

**Step 2:** State that the experiment cannot separate temporal sparsity, luminance duty cycle, static overlays, panel response, and exposure.

**Step 3:** Keep the profile split explicit: deployed has planned usability evidence but weaker protection; high-suppression has stronger observed suppression but no user-acceptability claim.

**Step 4:** Rewrite the Conclusion to report headline values once and avoid calling the niche `useful` without evidence. Use `measured operating window` instead.

**Step 5:** Replace the stale SHA wording in Data and Code Availability with repository-level availability plus a commitment to mint an immutable release aligned with the final submission. Do not invent a release identifier.

### Task 8: Update references and submission template metadata

**Files:**
- Modify if required: `paper/refs.bib`
- Modify or replace after verification: `paper/ieeeaccess.cls`
- Modify: `paper/main.tex`

**Step 1:** Remove the unused `b_ieee1789` entry unless it becomes cited.

**Step 2:** Add or cite authoritative manufacturer documentation for claims that remain about the AOC panel. If a claim cannot be verified, remove or qualify it as unmeasured.

**Step 3:** Obtain the current official IEEE Access LaTeX template. Compare its class and sample structure with the local source before replacing anything.

**Step 4:** Remove stale `VOLUME 11, 2023` output without inventing acceptance metadata. Keep approved author/user-study placeholders unchanged.

### Task 9: Build and visual verification

**Files:**
- Modify/create build entry point if needed: `paper/build.sh` or `paper/latexmkrc`
- Regenerate: `paper/main.pdf`
- Generate: `paper/supplementary.pdf`

**Step 1:** Build from clean auxiliaries using a full LaTeX/BibTeX/LaTeX/LaTeX sequence or equivalent `latexmk` entry point.

**Step 2:** Verify logs contain none of:

- undefined citations;
- undefined references;
- changed labels requiring another pass;
- unresolved non-approved placeholders.

**Step 3:** Check `pdfinfo paper/main.pdf` reports at most 20 pages.

**Step 4:** Render every page to images and inspect for clipping, overlap, unreadable text, float displacement, stale metadata, and incomplete references.

**Step 5:** Run automated consistency scans for all headline values and the VLM denominator.

### Task 10: Reverse claim audit and handoff

**Files:**
- Read: `.trellis/tasks/07-08-revise-ieee-access-after-review/prd.md`
- Read: `paper/main.tex`
- Read: `paper/main.pdf`
- Read: `privacy-display/experiments/results/paper_ocr_clustered_stats.json`

**Step 1:** Check every acceptance criterion in the PRD against source, analysis output, build log, and rendered PDF.

**Step 2:** Read from Conclusion backward to Methods and verify every main claim names supporting evidence and stays within the one-camera scope.

**Step 3:** Report any items intentionally deferred to the user-study completion or final immutable release.

**Step 4:** Present a commit plan under the Trellis finish workflow; do not commit or push without the required confirmation.

