# Fix Actionable English Paper Review Issues

## Goal

Revise the current IEEE Access English manuscript using only existing evidence and author-confirmed acquisition facts. Fix citation, terminology, reproducibility, claim-scope, and layout issues; reduce repetitive caveats; and produce a source/PDF pair that compiles cleanly and matches exactly.

## Requirements

- Treat the display brightness setting as fixed throughout physical acquisition.
- Treat the acquisition phase as controlled and unchanged throughout the collection.
- Remove statements that describe display brightness or acquisition phase as unknown, uncontrolled, or unmeasured.
- Do not claim that photometric luminance or panel transitions were measured.
- Do not claim worst-phase robustness or a causal temporal mechanism.
- Correct the Ponemon 91%/15-minute claim.
- Remove the unsupported claim that Eykholt et al. established weakening by JPEG compression.
- Remove the uncited 1-ms GtG numerical claim and the derived 24%-of-slot argument.
- Define OCR, UVC, VLM, GPU, and CLAHE at first use in the main body.
- Replace ambiguous “VLM failures” language with “protection failures” or equivalent.
- Use “character recovery” consistently.
- Make clear that the primary 288 matched units are derived from 12 content clusters.
- Add reproducibility details that can be recovered from the current code and archived configurations; do not invent unavailable Windows runtime versions or hardware measurements.
- Consolidate repeated scope limitations so they appear where scientifically necessary rather than throughout every section.
- Shorten overly dense captions and prose where this can be done without removing necessary audit information.
- Preserve author, affiliation, funding, acknowledgment, and user-study result placeholders.
- Preserve all unrelated user changes in the dirty worktree.

## Acceptance Criteria

- [ ] No manuscript statement calls acquisition phase unknown, uncontrolled, or unmeasured.
- [ ] The manuscript states that display brightness setting and acquisition phase were held fixed.
- [ ] The manuscript does not claim measured photometric luminance, measured panel response, or worst-phase robustness.
- [ ] The Ponemon statistic and Eykholt claim are corrected.
- [ ] The uncited 1-ms GtG claim and 24%-of-slot inference are removed.
- [ ] Required acronyms are expanded at first body use.
- [ ] Terminology uses “character recovery” and unambiguous “protection failure” wording.
- [ ] Primary-sample wording exposes the 12 content clusters alongside the 288 matched units.
- [ ] Main and supplementary PDFs compile from clean auxiliary state with no undefined citations or references.
- [ ] Extracted PDF text contains no unexpected citation placeholders.
- [ ] Rendered pages show no new clipping, overlap, or unreadable tables.
- [ ] The checked-in PDF is regenerated from the final source.

## Definition of Done

- Manuscript and bibliography edits are complete and evidence-consistent.
- Relevant analysis tests pass.
- LaTeX source, bibliography, and generated PDFs are synchronized.
- Remaining experimental blockers are reported separately as a future-work repair roadmap.

## Technical Approach

Use an evidence-preserving revision. Author-confirmed fixed brightness and phase replace the inaccurate unknown/uncontrolled wording. Remove the manuscript's phase-measurement boundary rather than restating it elsewhere. Retain only boundaries that still follow from the archive, including no photometric luminance measurement, no mechanism isolation, and no worst-phase claim. Repair factual and citation errors, clarify statistical units, recover method settings from code where possible, compress repeated disclaimers, then rebuild and visually inspect both PDFs.

## Decision (ADR-lite)

**Context:** The manuscript currently repeats uncertainty about brightness and phase, while the author confirms both settings were controlled and unchanged. Removing all related limitations could still imply measurements that did not occur.

**Decision:** State the controlled settings as acquisition facts. Delete claims that they were unknown, uncontrolled, or unmeasured. Do not present the fixed brightness setting as a photometric measurement, and do not add a worst-phase robustness claim.

**Consequences:** The manuscript becomes less self-undermining and more accurate, while preserving a defensible distinction between fixed acquisition conditions and unperformed measurement/generalization experiments.

## Out of Scope

- New physical captures, devices, displays, or participants.
- New luminance, photodiode, oscilloscope, high-speed-camera, or phase-sweep measurements.
- New physical privacy-filter or prior-system baselines.
- Fabricating missing runtime versions, camera metadata, or user-study values.
- Creating a public release, DOI, or submission tag in this task.

## Technical Notes

- Primary manuscript: `paper/main.tex`
- Supplement: `paper/supplementary.tex`
- Bibliography: `paper/refs.bib`
- Relevant project guideline: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`
- The worktree contains extensive pre-existing user changes; edit and stage only task-scoped files.
