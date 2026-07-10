# Fix English paper pre-submission review issues

## Goal

Revise the English IEEE Access manuscript so the pre-submission review findings are fixed in source, generated figures, references, and rendered PDFs. The revision should preserve the intentionally incomplete user-study data placeholders and author/funding placeholders while tightening every other reviewed issue.

## Requirements

* Make the 8-geometry common 3.91-ms subset the visually primary result, and demote the full 9-geometry pool to disclosed sensitivity evidence.
* Reframe the manuscript contribution as a bounded empirical measurement with explicit failure-boundary mapping, not as a deployable anti-camera defense.
* Fix Figure 3 source labels so digital integrated reconstruction views are not presented as direct "human eye" evidence.
* Treat high-suppression as an exploratory security-oriented stress profile, not a deployment candidate or user-validated option.
* Clean citation details for SSIM and VLM references without inventing unsupported bibliography claims.
* Keep user-study and author placeholders intact, because the user explicitly asked to ignore those pending items for this pass.

## Acceptance Criteria

* [x] `paper/main.tex` contains a primary common-setting OCR table before the full-pool sensitivity table.
* [x] `paper/main.tex` contribution, discussion, deployment-path, and conclusion wording do not imply a completed deployment recommendation.
* [x] `privacy-display/experiments/paper_figures/fig_f3_montage.py` emits "Digital integrated reconstruction" labels, and the matching test expects those labels.
* [x] `paper/figures/real_capture_montage.pdf` is regenerated from the updated source.
* [x] `paper/refs.bib` has no unused `b_wang2004`; SSIM is cited where first used.
* [x] VLM bibliography metadata matches the cited source scope, with Kimi treated via provider/model metadata rather than a claimed independent technical report.
* [x] A complete LaTeX build exits successfully and the final log has no undefined citations or references.
* [x] Rendered PDF inspection shows the reviewed pages are readable and the Figure 3 label issue is gone.

## Definition of Done

* Source edits are limited to the manuscript, figure-generation source/test, regenerated figure/PDF artifacts, and Trellis task metadata needed for this work.
* No unrelated dirty files are reverted or committed.
* Build and verification commands are run and their outcomes are summarized.

## Out of Scope

* Filling author, affiliation, funding, or acknowledgment placeholders.
* Filling user-study result placeholders or changing the planned user-study design.
* Running new OCR, VLM, user, camera, or statistical experiments.
* Making claims beyond the already archived evidence.

## Technical Notes

* Main manuscript: `paper/main.tex`.
* Bibliography: `paper/refs.bib`.
* Figure 3 source: `privacy-display/experiments/paper_figures/fig_f3_montage.py`.
* Figure 3 test: `privacy-display/tests/test_fig_f3_montage.py`.
* LaTeX verification guide: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`.
* Review findings came from the previous paper-self-review pass in this Codex thread.
