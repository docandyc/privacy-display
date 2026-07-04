# Narrow IEEE Access manuscript positioning to single UVC-camera feasibility study

## Goal

Revise the IEEE Access manuscript so its claims are explicitly positioned as a single-UVC-camera feasibility study, reducing overgeneralization from the current one-camera empirical evidence to broader smartphone, smart-glasses, multi-device, or cross-environment claims.

## What I already know

* The user requested: “把全文定位进一步收窄为 ‘single UVC-camera feasibility study’.”
* The manuscript source is `paper/main.tex`; rendered output is `paper/main.pdf`.
* The current real-capture evidence uses one eMeet SmartCam S600 UVC camera, one 240 Hz display setup, and 9 distance/angle geometry conditions.
* Existing manuscript text already contains several limitations, but the abstract, introduction, contribution framing, evaluation summary, discussion, and conclusion still risk sounding broader than the evidence supports.

## Requirements

* Reframe the manuscript’s real-device evidence as a feasibility study using a single UVC camera rather than a broadly validated screen-photography defense.
* Preserve the existing quantitative results, tables, and figure references.
* Keep the main technical contribution: temporal pixel masking reduces traditional OCR recovery under short-exposure captures in the evaluated setup.
* Make the single-camera scope visible in high-impact locations: abstract, introduction/contributions, experiment setup, evidence-scope discussion, limitations, and conclusion.
* Keep VLM, temporal averaging, and cross-device generalization as explicit residual risks.
* Do not perform language polishing beyond what is necessary to change the scientific positioning.
* Do not fill author, user-study, funding, data availability, or acknowledgement TODOs in this task.

## Acceptance Criteria

* [ ] The abstract explicitly says the physical evaluation is a single-UVC-camera feasibility study.
* [ ] Contributions no longer imply broad real-device or cross-device validation.
* [ ] Evaluation text states that the eMeet S600 results establish feasibility under one UVC camera and should not be generalized to phones, smart glasses, or other camera pipelines.
* [ ] Discussion/conclusion consistently repeat the narrowed evidence scope.
* [ ] Existing quantitative results are unchanged.
* [ ] The LaTeX source still compiles or, at minimum, has no obvious syntax errors in edited regions.

## Definition of Done

* `paper/main.tex` updated.
* Relevant occurrences of broad/generalized language inspected.
* A lightweight verification command run after edits.
* User receives a concise summary of changed positioning and any remaining caveats.

## Technical Approach

Search for broad-scope phrases around the abstract, contributions, experiment setup, discussion, and conclusion. Patch only claim-framing text. Avoid touching experimental values or TODO placeholders. Use source-level verification and, if feasible, a quick LaTeX compile/check.

## Decision (ADR-lite)

**Context**: The paper’s physical evidence currently comes from a single UVC camera but the motivation discusses smartphones, smart glasses, and general screen-photography threats.

**Decision**: Adopt a conservative “single UVC-camera feasibility study” framing throughout the manuscript while retaining broader threats as motivation and future validation targets.

**Consequences**: The manuscript becomes less vulnerable to overclaim criticism, but the contribution is narrower and must be sold as feasibility plus boundary analysis rather than cross-device deployment validation.

## Out of Scope

* New camera, phone, or smart-glasses experiments.
* Rerunning OCR/VLM/detection/tracking analyses.
* Filling user-study or submission metadata TODOs.
* Rewriting the full paper for English style.
* Changing figures, tables, or bibliography entries unless required by syntax.

## Technical Notes

* Main source: `paper/main.tex`.
* Prior review identified the “single eMeet S600 vs broader smartphone/smart-glasses motivation” mismatch as a high-priority issue.
* User explicitly requested this narrowing, so no additional preference question is blocking.
