# Reduce Manuscript Hedging and Improve Title

## Goal

Revise the English IEEE Access manuscript so that its title is clearer and its prose is more direct, while preserving every qualification required by the actual evidence. Remove repeated defensive wording that weakens readability, but do not convert associations into causal claims, broaden a single-camera result, or conceal limitations.

## What I Already Know

* The likely publication target is the English manuscript at `paper/main.tex`.
* The current title is `Temporal Pixel Masking Under a Nominal 3.91-ms UVC Setting: A Profile-Level Conventional-OCR Measurement Study`.
* The study measures 10,575 captures from one S600 UVC camera, with the primary matched analysis using 288 units per profile across eight common-setting geometries.
* The archive does not establish a physical exposure interval, isolate the temporal mechanism, or support cross-device generalization.
* The manuscript repeats these same boundaries in the abstract, introduction, contributions, discussion, limitations, and conclusion.
* Existing uncommitted changes outside this task must be preserved.

## Assumptions (Temporary)

* The initial pass targeted `paper/main.tex`; the user subsequently requested full synchronization into the canonical Chinese manuscript at `paper-Chinese/main.tex`.
* The title should foreground temporal pixel masking, conventional OCR recovery, short-exposure screen capture, and the fixed UVC link without advertising an unverified 3.91-ms physical exposure.
* The preferred working title is `Temporal Pixel Masking and Conventional OCR Recovery in Short-Exposure Screen Capture: A Fixed-Link UVC Study`.

## User Preference and Editorial Resolution

* The user asked to retain only the single-camera and fixed-profile-order limitations and omit the unmeasured physical exposure and missing luminance-matched controls.
* Editorial resolution: do not foreground or repeatedly restate the latter two limitations, but retain each once in the dedicated discussion/limitations material because they directly govern whether the nominal control value is a measured exposure and whether the temporal mechanism is causally identified.
* Proceed with the English submission manuscript only.
* The user further requested that limitations be concentrated at the end of the discussion/future-work material so the main narrative establishes value before presenting boundaries.
* Editorial resolution: relocate generalizability, missing-control, secondary-task, usability, and future-attack limitations to a final `Limitations and Future Work` subsection. Keep experimental-condition definitions, statistical interpretation, and result-specific anomalies where readers need them to interpret the reported numbers correctly.

## Requirements

* Replace the current title with a shorter, searchable, evidence-aligned title and update the running header consistently.
* Audit hedging throughout the manuscript by separating redundant rhetorical caution from evidence-required uncertainty.
* Delete or consolidate repeated scope disclaimers when the same boundary is already stated in the appropriate abstract, methods, discussion, or limitations location.
* Replace vague hedges with exact conditions or measured values where possible.
* Keep the single-camera and fixed-profile-order limitations prominent.
* Compress the unmeasured physical exposure and missing luminance-matched controls to one concise disclosure each in the discussion/limitations, removing their repeated appearances elsewhere.
* Preserve ethical statements about uncollected human-subject data and factual boundaries on cross-device or optimized-attacker performance where they are necessary to interpret a specific result.
* Do not invent evidence, hide unfavorable findings, or strengthen association language into causal or security guarantees.
* Preserve citations, numerical results, labels, and cross-references.
* Reorder the discussion so the main findings, implications, and attack mapping precede a single final limitations/future-work subsection.
* Convert the current limitations enumeration into connected scholarly prose.

## Acceptance Criteria

* [x] The English title is concise, readable, and no longer foregrounds the nominal 3.91-ms control value or the phrase `profile-level`.
* [x] Redundant hedging is measurably reduced in `paper/main.tex`.
* [x] Every strengthened sentence remains directly supported by reported data or is framed as an observation.
* [x] Core limitations are concentrated in discussion/limitations rather than repeated across the manuscript.
* [x] The running header matches the new title.
* [x] The manuscript builds successfully with complete references and cross-references.
* [x] No unrelated source files are modified by this task.
* [x] General limitations are concentrated in the final discussion subsection rather than repeated in the introduction, methods, results, and conclusion.
* [x] The revised main narrative foregrounds contribution and measured results without overstating causality or generalizability.
* [x] The canonical Chinese manuscript follows the English manuscript one-to-one at the sentence/semantic-unit level, without Chinese-only additions, omissions, reordered claims, or extra list items.

## Definition of Done

* The manuscript passes a claim-evidence audit focused on title, abstract, introduction, discussion, and conclusion.
* The LaTeX PDF builds without new errors or unresolved references.
* A focused diff confirms that numerical results and citations were not altered accidentally.

## Out of Scope

* Fabricating results, suppressing adverse evidence, or removing limitations required for accurate interpretation.
* Adding new experiments, citations, figures, or statistical analyses.
* Rewriting the planned human-subject study or changing its ethical safeguards.
* Synchronizing historical Chinese snapshots outside `paper-Chinese/main.tex`.
* Committing or pushing unrelated existing changes.

## Technical Notes

* Relevant manuscript: `paper/main.tex`.
* Relevant build guidance: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`.
* Title guidance: `.agents/skills/scientific-writing/references/editor-first-impression.md`.
* Revision method: reverse-outline major claims, map each to evidence, then remove only redundant language-level hedging.
* Final title: `Temporal Pixel Masking and Conventional OCR Recovery in Short-Exposure Screen Capture: A Single-Camera UVC Study`.
* Verification: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` completed successfully; final log contains no undefined citation/reference or rerun warnings, and extracted PDF text contains no `[?]` or `??` placeholders.
* Spec-update judgment: no code or reusable build contract changed, so `.trellis/spec/` requires no update.
* Narrative restructuring: Discussion now opens with `Principal Findings and Research Value`, proceeds through attacker escalation and practical implications, and ends with prose-form `Limitations and Future Work`.
* Final verification after restructuring: complete `latexmk`/BibTeX build passed; the PDF is 18 pages with no undefined citations, references, rerun warnings, or citation placeholders.
* Chinese synchronization: title, abstract, introduction framing, contribution language, full real-capture and simulated detection/tracking sections, discussion order, final limitations/future-work prose, and conclusion were synchronized to `paper-Chinese/main.tex`.
* Strict bilingual synchronization: removed Chinese-only qualifications and expansions, restored the English manuscript's exact paragraph/list ordering, and revised sentence boundaries so each English statement has a direct Chinese counterpart.
* Bilingual parity checks: the English and Chinese bodies each contain 686 ordered nonblank semantic/structural units; every corresponding unit has the same numeric, mathematical, citation, and cross-reference tokens; ordered label, citation, and reference sequences are identical.
* Chinese verification: `paper-Chinese/build.sh` completed successfully and produced a 15-page PDF with no undefined citations, references, rerun warnings, or citation placeholders.
