# Fix Final English Paper Review Findings

## Goal

Revise the English IEEE Access manuscript and its supporting OCR analysis so the primary fixed-setting result uses one coherent matched estimand, a fixed and auditable camera-side preprocessing attack is evaluated on the archived real captures, current adjacent work is cited, reproduction details are explicit, and causal language does not exceed the evidence.

## What I Already Know

* The current primary table combines the all-available readability-priority mean (`N=408`, 16.7%) with a paired contrast computed from 288 matched units; the paired treatment mean is 17.8%.
* The combined real-capture archive contains per-engine OCR rows for 10,575 captures and links back to nine position-specific reports and image directories.
* The primary common-setting subset excludes `d0.5_a15` and contains 288 matched short-exposure units for each of original, readability-priority (`deployed`), and high-suppression (`vlm`) profiles.
* Existing code already implements raw, Otsu, adaptive threshold, CLAHE, unsharp, denoise, and 2x-upscale preprocessing for a synthetic single-subframe ablation, but not for the real-capture primary estimand.
* Tesseract 5.4.1, pytesseract 0.3.13, EasyOCR 1.7.2, and Surya OCR 0.14.7 runtimes are available locally across the project virtual environments.
* The manuscript has 54 resolved bibliography keys and currently builds without undefined citations or references.
* The user explicitly requires the related-work update, reproducibility clarification, and weaker causal wording listed below.

## Assumptions

* Existing archived captures and ground truth are authoritative; no new camera collection is required.
* Raw OCR rows can be reused rather than rerun.
* The fixed preprocessing grid is an attacker oracle over predeclared transforms, not per-sample manual tuning.
* The main preprocessing result should align with the common-setting matched primary estimand; broader all-available summaries may be retained as sensitivity evidence.

## Requirements

* Replace the mixed-estimand primary table with matched `N=288` means: 94.5% original, 17.8% readability-priority, and 5.6% high-suppression, with paired contrasts of 76.7 pp and 88.9 pp.
* Preserve 16.7% (`N=408`) only as an explicitly labeled all-available descriptive mean.
* Synchronize the matched primary values across the abstract, introduction, contributions, results, discussion, and conclusion.
* Evaluate a fixed real-capture preprocessing grid including raw, gamma correction, CLAHE, unsharp masking, adaptive thresholding, and upscaling.
* Report raw best-of-engine and best-of-preprocessing-and-engine results without per-sample manual parameter choice.
* Persist per-capture, per-engine, per-preprocessor outputs, configuration, runtime versions, failures, and aggregate summaries.
* Add Bao et al. (2026) and the 2025 *Displays* modulated-projection-light work; replace the absolute novelty claim with a protocol-specific statement.
* State three explicit research questions covering fixed-setting OCR reduction, failure concentration, and integration/VLM boundaries.
* Add reproducibility details for OCR versions/configuration, image representation, normalization, text metrics, geometric correction, camera controls, and the status of the 3.91-ms common-setting selection.
* Remove the unsupported generic 2--5 ms IPS transition claim unless a defensible source is found.
* Weaken causal wording for mask granularity, physical-layer explanations, and high-suppression composite effects.
* Replace repeated “strict target” wording with “manuscript-defined interpretive threshold” or equivalent.

## Acceptance Criteria

* [ ] Primary matched means and paired contrasts are arithmetically coherent and derived from the same 288 matched units per profile.
* [ ] All manuscript occurrences of the primary common-setting readability-priority result use 17.8%, while 16.7% is labeled all-available descriptive evidence.
* [ ] A regression test fails before and passes after implementing real-capture preprocessing selection and attacker-favorable aggregation.
* [ ] The preprocessing report records the complete fixed grid, engine/runtime metadata, sample selection, raw reuse, failures, and best-of-preprocessing-and-engine summaries.
* [ ] The preprocessing run covers the three primary profiles across the eight common-setting geometries and all three OCR engines, unless a documented runtime constraint forces a narrower scope approved by the user.
* [ ] Manuscript claims use the generated preprocessing results without inventing or suppressing negative findings.
* [ ] Both new related works have verified metadata and are cited in the comparison narrative.
* [ ] Three research questions are explicit and map to the experiment/result structure.
* [ ] Reproduction details distinguish recorded settings from unknown/unmeasured controls.
* [ ] Searches find no remaining unsupported target/causal phrasings identified in the review.
* [ ] Main and supplementary LaTeX builds complete without undefined citations or references.
* [ ] Relevant Python tests pass and generated JSON/Markdown artifacts are internally consistent.

## Definition of Done

* Tests are written and observed failing before production-code changes.
* The fixed preprocessing experiment is implemented, resumable, executed, and summarized.
* Manuscript, supplement, bibliography, and generated analysis artifacts agree.
* Rendered PDFs are inspected for table/figure legibility and no new layout defects.
* No unrelated user changes are reverted or committed.

## Out of Scope

* Collecting new camera captures.
* Filling user-study results or author/funding/acknowledgment placeholders.
* Claiming cross-device, smartphone, commercial-OCR, or arbitrary-preprocessing robustness.
* Replacing the existing OCR metric definitions with a new metric family.
* Reworking unrelated detection/tracking experiments.

## Technical Notes

* Manuscript: `paper/main.tex`
* Supplement: `paper/supplementary.tex`
* Bibliography: `paper/refs.bib`
* Cluster analysis: `privacy-display/experiments/analyze_paper_ocr_clusters.py`
* Existing preprocessing implementation: `privacy-display/experiments/adaptive_attack_ablation.py`
* Real-capture evaluation: `privacy-display/src/evaluation/real_capture.py`
* Canonical OCR archive: `privacy-display/experiments/results/real_capture_ocr.json`
* Primary profiles use archive labels `original`, `deployed`, and `vlm`; the paper-facing labels are unprotected, readability-priority, and high-suppression.

## Decision (ADR-lite)

**Context**: A reduced engine set or diagnostic sample would be faster, but it would create a different attacker model from the paper's three-engine primary result and leave the same reviewer objection partly unresolved.

**Decision**: Run the complete primary scope: three matched profiles, eight common-setting geometries, six predeclared preprocessing conditions including raw, and all three OCR engines. Reuse raw OCR outputs and make the five transformed-condition runs resumable by engine.

**Consequences**: The experiment requires substantially more OCR inference time, but the resulting best-of-preprocessing-and-engine estimate is directly comparable with the matched raw primary result. Partial engine completion must not be reported as the final three-engine oracle.
