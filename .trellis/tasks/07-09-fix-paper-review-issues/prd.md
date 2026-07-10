# Fix English Paper Pre-Submission Review Issues

## Goal

Revise the English IEEE Access manuscript and directly supporting repository materials so the claim scope, contribution framing, profile naming, statistical summaries, public reproducibility notes, and boundary evidence match the current experimental evidence before submission.

## Requirements

* Revise the abstract so effects are attributed to the evaluated profile-level pipeline, not to temporal masking alone.
* Reframe the primary evidence as a fixed 3.91-ms UVC exposure, profile-level measurement study rather than an exposure-independent protection or operating-window claim.
* Make the high-suppression target miss visible where the 5.0% pooled result is reported.
* Narrow protected-assets wording so passwords, credentials, and other sensitive fields are treated as evaluated stress cases rather than assets the deployed profile can protect alone.
* Reduce the deployment implication of the `Deployed` profile name by reframing it as a readability-priority/preselected profile while preserving archived-label traceability.
* Make VLM session-selection transparency visible near the VLM table, not only in surrounding prose.
* Improve result narration by separating primary short-exposure evidence from integration/VLM boundary evidence.
* State that adaptive contrast enhancement/preprocessing sweeps were not systematically evaluated; keep the CLAHE observation as a pilot boundary note only.
* Correct the mask/randomization method so ChaCha20 rejection sampling is described for pixel assignments and Fisher-Yates only for playback-order randomization.
* Recompute descriptive sensitive-token means over rows that actually contain sensitive tokens, and preserve sample counts in generated clustered-stat outputs.
* Align the public README and supplementary real-capture definitions with the narrowed manuscript scope.
* Fix verification-only test infrastructure issues that prevent the repository test suite from running to completion, without changing OCR experiment semantics.
* Preserve all existing experimental numbers unless the source text already contains the corresponding value.

## Acceptance Criteria

* [ ] `paper/main.tex` contains revised abstract, contribution, threat-model, profile, OCR-results, VLM, discussion, and conclusion wording.
* [ ] `paper/supplementary.tex` documents the protected/unprotected real-capture definitions and states that clean-vs-short detection/tracking differences are descriptive diagnostics, not isolated protection effects.
* [ ] `privacy-display/README.md` no longer frames the prototype as a general anti-photography defense and reports the same fixed-condition evidence and failure boundaries as the paper.
* [ ] `privacy-display/experiments/results/paper_ocr_clustered_stats.*` is regenerated from the analysis script after the sensitive-token denominator fix.
* [ ] Cross-platform OCR evaluator tests no longer monkeypatch global `os.name`, so the full pytest suite can report failures normally on macOS.
* [ ] No new experimental claims are introduced without existing supporting text or table evidence.
* [ ] Citations and references remain resolved after a complete LaTeX/BibTeX build.
* [ ] Final PDF text contains no new `??`/`[?]` reference placeholders.

## Definition of Done

* Complete LaTeX build for `paper/main.tex` exits successfully.
* Complete LaTeX build for `paper/supplementary.tex` exits successfully.
* `privacy-display/tests/test_paper_ocr_cluster_analysis.py` passes with the sensitive-token denominator regression test.
* Full `privacy-display/tests/` suite completes without pytest internal errors.
* Final log has no undefined citations or unresolved references.
* Diff is limited to the manuscript, supplementary material, README, cluster-stat analysis/test/output files, Trellis task record, and generated build artifacts touched by the verification workflow.
* Remaining placeholders are only the user-approved author/user-study placeholders.

## Technical Approach

Use the existing `paper/main.tex` as the authoritative manuscript and `privacy-display/experiments/results/real_capture_ocr.*` as the source for OCR summary values. Apply targeted wording edits, then regenerate only derived clustered-stat outputs whose denominator logic is corrected by a regression-tested script change.

## Out of Scope

* Running or inventing user-study results.
* Rerunning OCR, VLM, detection, tracking, or figure-generation experiments.
* Changing author information, funding, acknowledgments, or other user-approved placeholders.
* Verifying every citation against external publisher metadata in this pass.
* Claiming robustness to ordinary smartphones, smart glasses, adaptive preprocessing, commercial OCR, or cross-device camera conditions not directly evaluated here.

## Technical Notes

* Relevant manuscript: `paper/main.tex`.
* Build guidance: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`.
* Review basis: previous self-review findings in the current conversation and `paper/review.md`.
