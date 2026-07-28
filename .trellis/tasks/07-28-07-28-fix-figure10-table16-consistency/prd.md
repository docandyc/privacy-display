# Fix Figure 10 strongest-pipeline aggregation and Table 16 rounding

## Goal

Make Figure 10 use the conservative strongest-tested-pipeline aggregation
already selected by the user, and correct the Tesseract reduction displayed in
Table 16 so both artifacts are derived consistently from the unrounded results.

## Requirements

* Compute retained capability model by model as
  `single_subframe / clean * 100`, then select the largest ratio within each
  evaluated task family.
* Figure 10 must report the strongest tested pipelines: Surya for OCR,
  RT-DETR-x for detection, and RT-DETR-x for tracking.
* Update the Figure 10 prose and caption to state that the plotted protected
  values are the largest model-wise protected-to-clean ratios within each task.
* Change the Tesseract reduction in Table 16 from `94.0%` to `93.9%`, matching
  the unrounded difference between the original and single-subframe results.
* Regenerate `paper/figures/all_attackers.pdf` from the plotting script.

## Acceptance Criteria

* [x] Figure 10 displays OCR `2.7%`, detection `11.1%`, and tracking `14.1%`.
* [x] The plotting script derives all three values from the checked-in result
      JSON files without hard-coded metric values.
* [x] The manuscript explains the strongest-tested-pipeline aggregation and
      warns that task-specific metrics are not directly commensurate.
* [x] Table 16 displays the Tesseract reduction as `93.9%`.
* [x] The English manuscript completes a full LaTeX build with no undefined
      citations or references.

## Definition of Done

* The figure-generation script passes a syntax check and reproduces the
  expected values.
* The regenerated PDF is present at the manuscript path.
* The manuscript PDF builds successfully and contains no unresolved
  cross-reference or citation placeholders.

## Technical Approach

Replace across-model means with a helper that selects the model having the
largest finite protected-to-clean ratio. Preserve each selected clean and
protected pair so the plotted ratio remains auditable. Update the nearby
manuscript sentence and caption, then rebuild the figure and manuscript.

## Decision (ADR-lite)

**Context:** Averaging across models understated the residual capability of
the strongest tested attack and conflicted with the manuscript's conservative
best-of-engine framing.

**Decision:** Use the largest model-wise protected-to-clean ratio within each
task family.

**Consequences:** Figure 10 becomes a conservative summary of the evaluated
attackers, but it remains bounded by the tested models and its task-specific
metrics remain unsuitable for direct cross-task comparison.

## Out of Scope

* Changing any experimental result JSON.
* Adding new attack models or rerunning OCR, detection, or tracking experiments.
* Synchronizing historical Chinese translation drafts.
* Revising other figures or tables.

## Technical Notes

* Plot script: `privacy-display/experiments/paper_figures/fig_s4_all_attackers.py`
* Manuscript: `paper/main.tex`
* Generated figure: `paper/figures/all_attackers.pdf`
* Source results: `corpus_multi_engine.json`, `coco_detection_attack.json`,
  and `mot_tracking_attack.json`
* Required verification follows
  `.trellis/spec/guides/latex-paper-build-thinking-guide.md`.
