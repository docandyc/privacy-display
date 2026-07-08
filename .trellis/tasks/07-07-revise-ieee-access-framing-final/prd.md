# Revise IEEE Access manuscript framing before submission

## Goal

Revise the English IEEE Access manuscript so its contribution is framed as a controlled UVC single-frame conventional-OCR feasibility study with measured failure boundaries, rather than as a general screen-photography defense. Preserve all reported experiment values and leave pending user-study, author, funding, and acknowledgment placeholders untouched.

## What I Already Know

* The target manuscript is `paper/main.tex`.
* The current paper already narrows claims to one UVC camera, calibrated short exposure, conventional OCR, and boundary characterization.
* The remaining review risk is mostly framing: the positive contribution can look too thin unless failure-boundary characterization is made central.
* VLM model endpoint wording needs caution, especially for the SiliconFlow `Pro/moonshotai/Kimi-K2.6` endpoint.
* `Data and Code Availability` currently points to an older fixed commit while the local manuscript and scripts have uncommitted changes.

## Requirements

* Rewrite the abstract to lead with the measurement/boundary-characterization contribution.
* Rework the contribution list into three clearer contributions:
  * controlled real-capture evidence for the single-frame conventional-OCR window;
  * quantified failure boundaries under integration and VLM attackers;
  * profile-level evidence hierarchy for deployment decisions.
* Update the Introduction's transition and organization sentence so readers understand the paper as a boundary-bounded measurement study.
* Make the VLM endpoint paragraph report provider identifiers without making unsupported claims about upstream public model capabilities.
* Revise the Conclusion to end on the evidence-bounded value of the study rather than only on failure.
* Update `Data and Code Availability` wording so the current SHA is described as a development snapshot and not implied to be the final aligned release.

## Acceptance Criteria

* [x] `paper/main.tex` compiles successfully.
* [x] The final log has no undefined citations or references.
* [x] The PDF text contains no new placeholder markers beyond existing author, funding, acknowledgment, and user-study placeholders.
* [x] All numeric claims changed in framing remain consistent with existing tables and text.
* [x] The manuscript no longer states that Kimi K2.6 is a native multimodal upstream model unless a citable source is added.

## Definition of Done

* Manuscript source is patched in-place.
* A complete LaTeX build is run using the manuscript's existing build path.
* A quick PDF-text check verifies the intended framing appears in the rendered document.

## Technical Approach

Edit only targeted prose in `paper/main.tex`. Do not change experiment data, figures, generated tables, user-study result placeholders, author metadata, or bibliography entries unless required by the prose changes. Use conservative language and preserve the manuscript's narrow claim scope.

## Decision (ADR-lite)

**Context**: The paper's strongest defensible value is not broad protection, but controlled evidence for a narrow OCR mitigation window and precise failure-boundary measurement.

**Decision**: Reframe the manuscript around an evidence-bounded measurement contribution, with failure modes treated as primary boundary findings rather than late-stage caveats.

**Consequences**: The claims become narrower but more defensible. The manuscript may sound less like a deployable defense, but it should be harder for reviewers to reject on overclaiming grounds.

## Out of Scope

* Filling user-study results or author/funding/acknowledgment placeholders.
* Running new experiments or changing reported numbers.
* Moving figures/tables to supplementary material in this pass.
* Creating a final public release commit.

## Technical Notes

* Relevant spec: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`.
* Relevant skill fragments loaded: `paper-writing`, `nature-polishing` core fragments, and abstract/intro/results/discussion/conclusion fragments.
* Shared `nature-polishing` fragments referenced by the manifest were missing in this local skill installation, so the available local fragments were used.
