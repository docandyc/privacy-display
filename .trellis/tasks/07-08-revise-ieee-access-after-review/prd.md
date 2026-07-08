# Revise IEEE Access Manuscript After Submission Review

## Goal

Revise the English IEEE Access manuscript so that its central contribution is supported by the existing physical-capture evidence, its statistical uncertainty matches the true experimental units, weak supplementary diagnostics no longer obscure the main claim, and the rendered submission conforms to current IEEE Access presentation constraints.

## What I Already Know

- The user approved the findings from the 2026-07-08 pre-submission review.
- Author, funding, acknowledgment, DOI, and unfinished user-study values remain intentionally out of scope for this revision.
- The user study is assumed to support the manuscript's deployed-profile usability claim once its data are inserted.
- The current central evidence is a one-camera, calibrated fixed-exposure, single-frame conventional-OCR measurement study.
- Current data do not include a physically brightness-matched dimming control, a matched noise-off deployed profile, photometric panel measurements, or cross-camera replication.
- Existing capture-level bootstrap intervals do not provide population inference across repeated content and geometry; only deployed short exposure currently has a 12-content cluster interval.
- The current PDF is 22 pages. IEEE Access recommends no more than 20 pages for ordinary research articles and asks authors of longer papers to contact the EIC before submission.
- The local `paper/ieeeaccess.cls` hard-codes 2023 publication metadata and is older than the current official 2026 template download.

## Open Question

- Should this revision remain strictly evidence-preserving, with no new physical capture, or should it wait for a new brightness-matched/matched-noise-off capture experiment?

## Feasible Approaches

### Approach A: Evidence-Preserving Submission Revision (Recommended)

- Recompute clustered and paired uncertainty from existing archived results.
- Reframe the central conclusion as a profile-level observed effect, not isolated proof of temporal sparsity as the sole mechanism.
- State explicitly that duty-cycle luminance, static overlays, panel response, and exposure cannot be separated without a matched physical control.
- Treat deployed as a preselected readability-priority composite, not an optimized or component-validated profile.
- Move weak detection/tracking diagnostics to supplementary material.
- Tighten repeated caveats and repeated result numbers, update the title and terminology, and reduce the main PDF to at most 20 pages.
- Update to the current IEEE Access template if the official archive can be obtained and verified; otherwise remove stale local publication metadata without inventing publication values.

Pros: uses current evidence honestly, materially improves submission readiness, and does not delay the paper for new capture.  
Cons: cannot make a mechanistic claim that temporal sparsity, rather than luminance/static effects, caused the full observed reduction.

### Approach B: Strong Experimental Revision

- Do everything in Approach A.
- Add a physically brightness-matched static dimming baseline and matched noise-off versions of the deployed/high-suppression profiles.
- Preferably verify panel timing or luminance with a photodiode/high-speed camera and add a second camera pipeline.

Pros: directly addresses the strongest causal and external-validity objections.  
Cons: requires new hardware capture, analysis, figure regeneration, and user-study alignment; substantially delays submission.

### Approach C: Editorial-Only Revision

- Change wording, title, page count, and formatting without statistical reanalysis or structural changes.

Pros: fastest.  
Cons: leaves the main statistical and causal-review risks unresolved and is not recommended.

## Requirements

- Preserve all reported experimental values unless recomputed from authoritative archived data.
- Do not fabricate missing user-study results, physical measurements, references, or release identifiers.
- Add clustered/paired uncertainty for the main OCR contrasts where the archived data permit it.
- Distinguish observed profile-level performance from component-level causal attribution.
- Remove or weaken claims that imply physical brightness matching, temporal-only causation, component optimization, cross-device generality, or resistance to modern VLMs.
- Define the VLM 77.8% result using its actual denominator of 36 captures from 12 content items.
- Restrict cross-model interpretation to failure-free cells or report missing-response bounds consistently.
- Move nonessential detection/tracking simulations and approximate metrics out of the main narrative.
- Remove cross-metric normalized comparison figures that imply commensurability among OCR, mAP, and IDF1.
- Replace repeated defensive wording with one clear evidence hierarchy and one consolidated limitations section.
- Keep the final main paper at or below 20 rendered pages unless the user explicitly chooses an EIC pre-submission inquiry.
- Build the LaTeX/BibTeX source from clean intermediates and visually inspect every rendered page.

## Acceptance Criteria

- [ ] Abstract, Introduction, Contributions, Discussion, and Conclusion all state the same evidence-bounded central claim.
- [ ] The paper explicitly says that the existing experiment cannot isolate temporal sparsity from duty-cycle luminance, static overlays, panel response, and exposure.
- [ ] Main OCR contrasts use cluster-aware or paired uncertainty where the archive permits it; the resampling unit and estimand are stated.
- [ ] `deployed` is described as a preselected composite profile, not an empirically optimized component combination.
- [ ] The VLM 77.8% result is reported as 28/36 captures from 12 items, and content-dependent API failures are not used for unsupported model comparisons.
- [ ] Weak detection/tracking diagnostics and the normalized cross-task summary are absent from the main paper and preserved, if retained, in supplementary material.
- [ ] No citation or cross-reference is unresolved; every main-text figure/table is cited and legible.
- [ ] The main PDF is at most 20 pages and has no stale `VOLUME 11, 2023` footer.
- [ ] The data/code statement does not claim that a stale development SHA is the final immutable submission release.
- [ ] A final reverse claim audit finds no main claim stronger than its named evidence.

## Definition of Done

- Revised `paper/main.tex`, `paper/refs.bib` if needed, and supplementary source are internally consistent.
- Statistical scripts/outputs used for new values are reproducible and retained in the repository.
- Full LaTeX/BibTeX build succeeds without unresolved citations or references.
- Rendered PDF passes page-by-page visual inspection.
- User-study and author placeholders remain untouched.

## Decision (ADR-lite)

**Context:** The strongest remaining objections require either new physical controls or a narrower evidence-preserving claim.  
**Recommended decision:** Use Approach A now. It improves the manuscript using authoritative existing evidence while making the unresolved physical-control experiment an explicit follow-up rather than implying it was performed.  
**Consequence:** The paper becomes a controlled profile-level feasibility and boundary study, not a causal validation of temporal sparsity alone and not a deployment-ready anti-camera defense.

## Out of Scope

- Filling author, funding, DOI, acknowledgment, biography, or user-study result placeholders.
- Inventing or estimating user-study outcomes.
- Claiming cross-camera, smartphone, smart-glasses, CJK, or real-world ambient-light generality.
- Creating a final immutable public release before all manuscript and user-study outputs are finalized.

## Technical Notes

- Main manuscript: `paper/main.tex`
- Current PDF: `paper/main.pdf`
- References: `paper/refs.bib`
- Primary experiment archive: `privacy-display/experiments/`
- Existing paper-figure scripts: `privacy-display/experiments/paper_figures/`
- Build guidance: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`
- Prior review evidence: `.trellis/tasks/07-08-fix-english-paper-review-findings/prd.md`

