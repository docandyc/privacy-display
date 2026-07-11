# Fix Claim Audit and Presentation Issues in the English Manuscript

## Goal

Revise the current English IEEE Access manuscript so that its claims match the existing evidence, the failure-boundary contribution is prominent, figures and tables cannot be misread, repeated caveats are reduced, and the supplementary material and page budget are more coherent. This task uses only existing results and does not invent or rerun physical or user-study evidence.

## What Is Already Known

- The supported positive claim is a profile-level association for conventional OCR under one fixed UVC archive.
- The manuscript must not attribute the observed reduction to temporal sparsity because luminance-matched, overlay-only, timing, and randomized-order controls are absent.
- General usability and a high-suppression privacy-defense claim are unsupported and must remain bounded.
- Preprocessing, VLM, temporal-integration, and inversion-slot failures are the strongest publishable contribution.
- The current main PDF is 19 pages; edits should reduce or preserve page count.
- Author placeholders and pending user-study values remain untouched except where nearby prose must retain accurate scope.

## Requirements

- Rewrite the research question, contribution statements, abstract/conclusion language, and figure captions so they consistently describe a single-link profile-level measurement and failure-boundary study.
- Remove or weaken causal language about temporal sparsity and general protection.
- Retain the narrow matched OCR observation and foreground the preprocessing, VLM, integration, and inversion-slot boundary evidence.
- Replace Figure 2 labels that assert readable/unreadable outcomes with evidence-bounded labels and regenerate its PDF/PNG exports from the editable source or existing figure-generation workflow.
- Make Table 9 units consistent across OCR and VLM columns.
- Explain Figure 4 error bars in its caption.
- Identify Table 4 intervals as 95% content-cluster resampling intervals.
- Rename percentage-point differences currently labeled as generic reductions.
- Remove repeated presentation of the 94.5/17.8/5.6 result and repeated caveats, targeting a 15–20% reduction where it improves flow without deleting necessary evidence.
- Retitle or narrow the supplementary material so it does not imply that omitted tracking scores are reported as evidence.
- Rebuild and visually inspect the main and supplementary PDFs; verify cross-references, citations, placeholder scope, and page count.

## Acceptance Criteria

- [ ] No sentence attributes the primary physical result causally to temporal sparsity.
- [ ] No sentence presents high-suppression as an effective general privacy defense.
- [ ] Readability claims remain limited to the planned/completed short-term user-study outcomes.
- [ ] Failure-boundary results are explicit in the abstract, contributions, discussion, and conclusion without repetitive numerical restatement.
- [ ] Figure 2 no longer says "Readable output" or "Unreadable fragment".
- [ ] Table 9 uses a single interpretable unit convention.
- [ ] Figure 4 and Table 4 define their intervals/error bars.
- [ ] Percentage-point changes are labeled as such.
- [ ] Supplement title and scope match the evidence actually reported.
- [ ] `paper/main.pdf` and `paper/supplementary.pdf` compile without undefined citations or references.
- [ ] Main manuscript remains at or below 19 pages if feasible and does not exceed 20 pages.

## Definition of Done

- Manuscript source, affected figure source/exports, and supplementary source are revised.
- LaTeX builds complete successfully.
- Rendered PDFs pass visual inspection for clipping, table overflow, float order, and legibility.
- A final diff audit confirms that pending author/user-study placeholders were not accidentally filled or removed.

## Approaches

### A. Surgical repair

Fix only the explicitly listed claims, labels, captions, and repeated passages. Lowest risk, but the manuscript may continue to oscillate between a defense paper and a negative-result paper.

### B. Failure-boundary-centered revision (recommended)

Apply all listed repairs and consistently make the paper a profile-level measurement and failure-boundary study. Preserve the existing title unless a local wording change is necessary, but rewrite the abstract, research question, contributions, key findings, discussion, and conclusion as one coherent argument. This best matches the evidence while staying within the user's requested scope.

### C. Full Negative Result conversion

Retitle and comprehensively restructure the manuscript as an IEEE Access `Negative Result` article. This is the strongest conceptual repositioning but is broader than "fix these issues first" and risks unnecessary churn before the remaining experiment is complete.

## Recommended Decision

Use Approach B. It repairs every listed problem without pretending that missing experiments have been completed, while avoiding the larger submission-strategy commitment of a full article-type conversion.

## Decision (ADR-lite)

**Context**: The current manuscript already contains the evidence needed for a narrow profile-level observation and a strong failure-boundary contribution, but its language and visual presentation still alternate between a defense claim and a measurement claim.

**Decision**: The user approved Approach B on 2026-07-11. Revise the manuscript around a single profile-level measurement and failure-boundary argument, without changing article type or introducing new evidence.

**Consequences**: Causal and deployment language will be removed or bounded; negative attack evidence will become more prominent; some repeated numerical statements and diagnostics will be condensed or moved. The resulting paper remains a research manuscript that could later be converted to a formal Negative Result submission if desired.

## Out of Scope

- New physical capture experiments, OCR/VLM reruns, or statistical recomputation.
- Filling author, affiliation, biography, funding, ethics-decision, or user-study result placeholders.
- Adding new literature or changing the public artifact repository in this pass.
- A complete conversion to the IEEE Access `Negative Result` manuscript type unless separately approved.

## Technical Notes

- Primary manuscript: `paper/main.tex`
- Rendered manuscript: `paper/main.pdf`
- Supplement: `paper/supplementary.tex`, `paper/supplementary.pdf`
- Figure 2 source/export family: `paper/figures/visio/figure2_method_pipeline/`
- Existing review evidence and current build logs were inspected before this task was created.

## Open Questions

- None.
