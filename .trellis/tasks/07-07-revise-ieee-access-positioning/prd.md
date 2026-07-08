# Revise IEEE Access manuscript positioning after review

## Goal

Revise the English IEEE Access manuscript so the contribution framing matches the evidence already present in the paper. The manuscript should foreground the useful niche: controlled/manual-exposure single-frame conventional OCR mitigation on one UVC camera, plus explicit boundary characterization for video, VLM, long-exposure, and usability split risks.

## Requirements

* Narrow title, abstract, introduction, contribution list, discussion, and conclusion language away from broad screen-photography protection.
* Make the security-usability split explicit at the contribution level: deployed profile is the readability-priority candidate, while high-suppression has stronger mitigation but unresolved acceptability.
* Reframe high-suppression as near-boundary mitigation, not a profile that meets the strict `<5%` target.
* Move the "silent single-frame bulk collection" niche earlier and make clear why video/VLM attacks are outside that niche but still important boundaries.
* Demote the Pareto/FPI analysis to an exploratory proxy diagnostic, not an independent contribution or recommendation mechanism.
* Reduce CSPRNG prominence in the abstract and framing; keep it as an implementation detail in Methods.
* Preserve the existing traceability defense for keeping noise in archived composite profiles, while making clear current deployed is not proven optimal.
* Do not invent user-study results, new experiments, citations, or numerical claims.

## Acceptance Criteria

* [ ] `paper/main.tex` builds without undefined references or missing citations.
* [ ] Abstract and conclusion state the same scoped contribution and boundary.
* [ ] Contributions no longer imply a general screen-photography defense.
* [ ] The security-usability profile split is visible before the Discussion.
* [ ] Pareto/FPI wording is clearly diagnostic/exploratory.
* [ ] CSPRNG is not presented as the headline contribution in the abstract.
* [ ] Existing placeholders for user study and author information are preserved.

## Definition of Done

* Manuscript source updated.
* LaTeX build run for `paper/main.tex`.
* Basic citation/label checks pass.
* Review summary reported to the user.

## Technical Approach

Apply a tightly scoped prose revision to `paper/main.tex`. Prefer wording changes over structural rewrites. Keep all reported numbers unchanged unless a local consistency error is discovered.

## Decision (ADR-lite)

**Context**: The latest review confirmed that the paper is sufficiently honest but risks letting negative boundary results swallow the positive contribution.

**Decision**: Reposition the manuscript around a narrow but defensible feasibility claim and boundary characterization, rather than broad anti-photography protection.

**Consequences**: The contribution will sound narrower but more reviewable. Remaining unresolved issues, especially cross-device validation and high-suppression usability, stay as limitations or future work.

## Out of Scope

* Running or filling the user study.
* Adding new experiments, figures, or tables.
* Releasing or committing a final immutable data/code snapshot.
* Changing author, funding, or acknowledgment placeholders.

## Technical Notes

* Main file: `paper/main.tex`.
* Current review findings came from the user's confirmation message and prior local review of the manuscript.
* Relevant paper-writing skill route: manuscript polishing and pre-submission positioning.
