# Fix All English Paper Pre-Submission Review Findings

## Goal

Resolve the P0, P1, and P2 findings from the latest English-manuscript review without inventing evidence, overwriting unrelated user work, or filling the deferred user-study and author placeholders. The final manuscript must use internally coherent metrics, reproducible analysis, evidence-matched claims, and an IEEE Access-compliant build.

## What I Already Know

* The current manuscript is `paper/main.tex`; the current source and PDF were updated after the review and must be treated as authoritative.
* A prior active task already specifies matched `N=288` primary means and a real-capture preprocessing attack sweep. This task should incorporate and finish that work rather than create a competing estimand.
* `privacy-display/src/attack/ocr_evaluator.py` has an unrelated uncommitted Windows path change that must be preserved.
* The current sensitive-token extractor admits ordinary mixed-case and long English words, so the paper's high-value-field interpretation is invalid until the metric is replaced or relabeled and all derived results are regenerated.
* Several findings can be repaired with existing archives and code: matched estimates, token annotation, preprocessing sweeps, statistics, evidence tables, terminology, acronym expansion, and reproducibility documentation.
* Several findings require unavailable physical collection to close empirically: luminance-matched static controls, randomized profile recapture, photometric timing, and worst-phase capture. No result may be fabricated for these items.
* User-study results, author metadata, funding, acknowledgments, and final DOI remain intentionally deferred.

## Requirements

### A. Evidence and metric integrity

* Replace heuristic `sensitive_token_recall` as the paper's high-value-field metric with an auditable manifest of explicitly annotated sensitive fields for the 12 real-capture content items.
* Define and report the aggregation rule (token-level micro recovery and/or sample-level macro recovery) and regenerate every affected table, figure, abstract sentence, discussion statement, and conclusion.
* Use one coherent matched common-setting estimand for the primary three-profile result; all unbalanced/all-available values must be labeled as sensitivity summaries.
* Run the fixed real-capture preprocessing oracle already scoped by the prior task, preserving raw and per-transform outputs, versions, failures, and resumability.
* Replace capture-level population-style confidence claims with paired/cluster-aware summaries appropriate to repeated content and geometry; do not infer equivalence from overlapping marginal intervals.
* Add auditable tables/protocol details for digital strongest-attack, temporal-mean, inversion-slot, SSIM, and Delta-E values used in the discussion.

### B. Existing-data validity fixes

* Disclose the fixed profile acquisition order and evaluate available time/batch sensitivity; do not imply randomization.
* Correct the English/ASCII corpus statement and publish the 12-item selection/manifest details, including the CET6 content's Chinese characters.
* Distinguish nominal/logged UVC control settings from physically measured shutter time and document known/unknown exposure, AE, gain, AWB, focus, display brightness, JPEG, geometry, rectification, and crop state.
* Correct the normalized partial-inversion equation and specify the actual compositing domain/order.
* Add missing algorithm, OCR-version, model, language, preprocessing, failure-handling, and geometric-correction details needed for reproduction.
* Bound every VLM cell with non-random failures or remove unsupported cross-model comparisons.
* Validate supplementary tracking with the official metric path or remove/de-emphasize the approximate table; specify frame-selection rules and remove causal captions from exposure-confounded diagnostics.

### C. Findings that require new physical captures

* Do not claim that temporal sparsity, lower luminance, static overlays, panel response, and camera processing have been causally separated without luminance-matched/static controls.
* Do not present uncontrolled-phase short-exposure averages as worst-phase robustness; foreground the inversion-slot failure and define a future phase-sweep protocol.
* Do not claim profile-order randomization or photometric timing that did not occur.
* If no new captures are authorized in this task, repair these findings through explicit claim removal/reframing and a reproducible preregistered protocol, not placeholders that look like completed evidence.

### D. Manuscript logic and language

* Remove or qualify mechanism claims not isolated by the experiments, including binarization/segmentation, mask-granularity, ISP, moire, blur, and component-causal explanations.
* Replace absolute novelty/priority statements with evidence-bounded wording.
* Clarify contrast direction, analysis-pool labels, screenshot capture point, and the status of post-hoc thresholds/profile selection.
* Reduce repeated custom boundary terminology and redundant caveats while retaining the paper's narrow positive claim and negative evidence.
* Define acronyms independently in the abstract, body, keywords where required, and supplementary document.
* Keep the main article at or below 20 pages if feasible without harming reproducibility; otherwise document the IEEE Access pre-inquiry requirement.
* Replace the future-tense immutable release statement with a concrete tag/commit/DOI only if such a release is actually created.
* Add AI-text disclosure only if required by the author's actual use and IEEE policy; do not invent an acknowledgment.

## Acceptance Criteria

* [ ] Sensitive-field annotations are explicit, versioned, tested, and regenerate all paper-facing sensitive-field results.
* [ ] The primary table, abstract, introduction, results, and conclusion use one arithmetically coherent matched estimand.
* [ ] The fixed preprocessing grid completes for the approved scope and attacker-oracle aggregation is regression-tested.
* [ ] No manuscript sentence attributes a causal mechanism that the design did not isolate.
* [ ] Unavailable physical controls are handled by claim removal/reframing and a concrete future protocol, unless new captures are supplied.
* [ ] Camera/display/OCR/geometry configuration is reproducible to the extent supported by the archive, with unknowns labeled unknown.
* [ ] Supplementary detection/tracking claims match their actual exposure and evaluation design.
* [ ] Citation keys, labels, generated numbers, JSON/Markdown outputs, figures, and LaTeX tables are synchronized.
* [ ] Relevant unit/integration tests pass; the full feasible test suite completes without internal errors.
* [ ] Main and supplementary XeLaTeX builds have no undefined citations/references, embedded fonts pass, and rendered pages have no new defects.
* [ ] User-study and author placeholders remain untouched except for surrounding consistency wording.

## Definition of Done

* Tests are added before production-code changes for metric and aggregation fixes.
* Derived analyses and paper artifacts are regenerated from canonical inputs.
* The final diff preserves pre-existing user changes and contains no fabricated experiment results.
* A final self-review maps every P0/P1/P2 item to fixed, reframed, or explicitly hardware-blocked evidence.

## Out of Scope

* Inventing or estimating user-study results.
* Filling author, funding, acknowledgment, biography, or DOI placeholders.
* Claiming new physical evidence without actual archived captures.
* Reverting unrelated active-task changes.

## Decision (ADR-lite)

**Context**: Four review findings require new physical captures that are not available in the current workspace: luminance-matched/static controls, randomized profile order, photometric timing, and worst-phase capture. Treating these gaps as completed experiments would fabricate evidence, while leaving the existing claims unchanged would preserve the submission blockers.

**Decision**: Use the existing-data comprehensive repair. Correct and regenerate every metric and analysis supported by the archive; run the fixed preprocessing attack; revise the manuscript and supplement; and close hardware-dependent findings by removing or narrowing unsupported claims plus documenting concrete future protocols. Do not wait for or invent new captures in this task.

**Consequences**: The revised paper will make a narrower profile-level measurement claim rather than a causal or worst-case defense claim. New physical experiments can strengthen the paper later, but their absence will no longer be hidden behind unsupported wording.

## Technical Notes

* Manuscript: `paper/main.tex`
* Supplement: `paper/supplementary.tex`
* Bibliography: `paper/refs.bib`
* OCR metrics: `privacy-display/src/attack/ocr_evaluator.py`
* Real-capture aggregation: `privacy-display/src/evaluation/real_capture.py`
* Cluster analysis: `privacy-display/experiments/analyze_paper_ocr_clusters.py`
* Preprocessing attack: `privacy-display/experiments/real_capture_preprocessing_attack.py`
* Capture planning/order: `privacy-display/experiments/real_capture_ablation.py`
* Prior overlapping task: `.trellis/tasks/07-09-fix-final-english-paper-review-findings/prd.md`

## Baseline Record (2026-07-10)

* Canonical OCR archive: `privacy-display/experiments/results/real_capture_ocr.json`
* SHA-256: `c3a23b6b5597195bc1c1b27a24198008d14f86a17fb396c793d02008b472007c`
* Focused baseline tests: 34 passed (`test_ocr_evaluator.py`, `test_paper_ocr_cluster_analysis.py`, and `test_real_capture_preprocessing_attack.py`).
* The pre-existing Windows-path changes in `ocr_evaluator.py` and all other unrelated dirty files are preserved as user-owned concurrent work.
