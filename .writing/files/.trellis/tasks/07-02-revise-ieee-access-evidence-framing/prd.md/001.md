# Revise IEEE Access Manuscript Claim Scope and Evidence Framing

## Goal

Revise the IEEE Access manuscript so its central claim matches the current evidence: strong mitigation for traditional OCR under short-exposure screen captures, with VLM, temporal averaging, detection/tracking, and unbalanced datasets framed as bounded evidence or exploratory stress tests rather than universal protection.

## Requirements

* Fix review issue 1 by narrowing the title, abstract, contribution list, discussion, and conclusion so the paper does not imply broad protection against all camera or machine-vision captures.
* Fix review issue 2 by clarifying that the 10,575 real-capture images are a broad experimental corpus, while the core OCR short-exposure subset is the primary evidence for the main claim.
* Fix review issue 4 by positioning object detection and tracking as exploratory cross-task evidence, not equal-weight proof of general visual protection.
* Fix review issue 5 by making the VLM probe more reproducible and more cautiously interpreted using facts already in the manuscript: model names, provider, geometry, sample counts, API failures, prompt constraint, non-cohort OCR reference, and content-type split.
* Do not fill author information, TODO placeholders, or translate Chinese to English in this task.
* Do not invent new experiments, statistics, model versions, dates, citations, or repository links.

## Acceptance Criteria

* [x] `paper/main.tex` uses a narrower title and abstract claim centered on short-exposure OCR mitigation.
* [x] Mentions of `10,575` distinguish corpus scale from the core balanced/primary evidence subset.
* [x] Detection/tracking wording is explicitly exploratory/descriptive and does not imply cross-device or cross-task generalization.
* [x] VLM wording clearly states it is a single-geometry adversarial probe and explains the OCR reference and API-failure handling.
* [x] The manuscript still compiles after the edits.

## Definition of Done

* Manuscript changes are limited to claim/evidence framing.
* LaTeX build is run from `paper/`.
* Any remaining warnings that predate the task are reported rather than silently treated as fixed.

## Technical Approach

Use the existing manuscript evidence and rewrite only framing paragraphs: title, abstract, contribution bullets, setup/OCR introduction, VLM probe preamble/results interpretation, detection/tracking preamble/results interpretation, discussion, limitations, and conclusion.

## Decision (ADR-lite)

**Context**: The review identified four claim-scope risks that could make IEEE Access reviewers read the paper as overclaiming.

**Decision**: Keep the paper's current experimental results and boundaries, but make the main evidence hierarchy explicit: OCR short-exposure is the primary supported claim; VLM and temporal averaging are residual attack frontiers; detection/tracking is exploratory cross-task evidence.

**Consequences**: The revised paper is more conservative, but more defensible. It sacrifices broad phrasing for reviewer trust and clearer claim-evidence alignment.

## Out of Scope

* Author metadata, acknowledgements, funding, data/code availability TODOs.
* Chinese-to-English translation.
* New experiments or result recalculation.
* Reference verification beyond existing citations.

## Technical Notes

* Primary file: `paper/main.tex`
* Existing review basis: user requested fixes for issues 1, 2, 4, and 5 from the prior manuscript review.
* Writing rule used: every major claim must trace to evidence, and weak evidence should be framed as descriptive or exploratory rather than definitive.
