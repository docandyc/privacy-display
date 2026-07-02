# Revise IEEE Access Manuscript After Review

## Goal

Revise `paper/main.tex` so that every non-TODO claim, method description,
experimental statement, citation, and presentation detail is consistent with
the available evidence and suitable for IEEE Access review. Preserve all TODO
placeholders because the user explicitly deferred them.

## Requirements

- Preserve every existing `\TODO{...}` placeholder and do not invent missing
  author, funding, user-study, or acknowledgement data.
- Reframe the title, abstract, contributions, threat model, discussion, and
  conclusion around the demonstrated scope: short-exposure/snapshot mitigation,
  with long-exposure and temporal aggregation treated as explicit boundaries.
- Position temporal masking as prior art and state the manuscript's incremental
  contributions precisely: pixel-level CSPRNG masking, physical-camera
  evaluation, multi-task evaluation, and boundary analysis.
- Correct the temporal integration, luminance compensation, refresh-cycle, and
  capture-hardened parameter descriptions without claiming unimplemented
  hardware behaviour.
- Define every reported metric and explain the statistical unit and bootstrap
  procedure. Do not treat repeated captures, OCR engines, or video frames as
  independent participants.
- Describe the 10,575-capture corpus as an unbalanced collection of component,
  parameter, and geometry studies rather than a false balanced factorial design.
- Correct the real COCO/MOT setup using the authoritative JSON artifacts,
  including the 1.5 m/0-degree position, stop-motion MOT capture, and
  `greedy_bytetrack_fallback` tracker.
- Reconcile all headline numbers, profile names, sample counts, captions, and
  table statements with machine-readable result artifacts.
- Report the physical `mask_noise` ablation as a negative result rather than
  calling it an unconditional reinforcement.
- Keep the manuscript in Chinese-draft form for this revision, while making its
  terminology, logic, and academic register internally consistent.
- Add and verify directly relevant prior work and correct bibliographic metadata
  that can be established from canonical sources.
- Remove template publication metadata that could be mistaken for assigned IEEE
  metadata while leaving deferred author/funding TODOs intact.
- Compile and visually inspect the final PDF. Resolve undefined references,
  missing citations, overfull content, and material layout defects.

## Acceptance Criteria

- [ ] The set and count of `\TODO{...}` placeholders are unchanged.
- [ ] The manuscript remains a Chinese draft; no full-text translation is
      introduced in this revision.
- [ ] No title, abstract, contribution, or conclusion claims protection against
      arbitrary camera capture or complete-cycle video reconstruction.
- [ ] Threat-model levels are explicitly marked in scope, mitigated, or outside
      the demonstrated guarantee.
- [ ] FPI, MI, OCR recovery, exact match, sensitive-token recall, leak rate,
      SSIM, Delta E, detection, and tracking metrics used in the paper are defined.
- [ ] The method distinguishes ideal digital integration from measured physical
      display behaviour and does not claim hardware backlight compensation was
      implemented.
- [ ] Real-capture sample construction and per-condition sample counts are
      described accurately.
- [ ] COCO/MOT position, capture mode, tracker implementation, and limitations
      match the authoritative JSON artifacts.
- [ ] Known numerical/textual inconsistencies (1,175 typo, Surya 2.6%, Fig. 11
      range, profile counts, and configuration naming) are corrected.
- [ ] Prior temporal-masking work is cited and the novelty statement is
      incremental rather than absolute.
- [ ] A clean multi-pass LaTeX build succeeds with no undefined citations or
      references, and the rendered PDF has no visible placeholders other than
      the preserved TODOs.

## Technical Approach

Use the experiment JSON/Markdown artifacts as the source of truth, revise the
argument before translating, maintain a fixed terminology ledger, and perform a
final claim-to-evidence audit. Where evidence is absent, narrow or remove the
claim rather than adding inferred results.

## Decision (ADR-lite)

**Context:** The draft combines a defensible snapshot result with unsupported
broad camera-defeat and human-imperceptibility language.

**Decision:** Present the work as an evaluated mitigation for snapshot and
short-exposure capture, with hardened-mode partial mitigation and complete-cycle
aggregation as a documented security boundary.

**Consequences:** The paper makes a narrower claim, but the claim matches the
available evidence and is more likely to survive technical review.

## Out of Scope

- Completing or fabricating user-study results.
- Filling author names, affiliations, funding, correspondence, or acknowledgements.
- Running new camera, photometric, display-response, usability, or tracking experiments.
- Replacing the existing tracking implementation in source code.
- Claiming final submission readiness while deferred TODOs remain.

## Technical Notes

- Primary manuscript: `paper/main.tex`
- Primary rendered draft: `paper/main.pdf`
- Authoritative OCR evidence: `privacy-display/experiments/results/real_capture_ocr.json`
- Authoritative detector/tracker evidence:
  `privacy-display/experiments/results/real_capture_coco_detection.json`,
  `privacy-display/experiments/results/real_capture_mot_tracking.json`, and
  `privacy-display/experiments/results/mot_tracking_attack.json`
- Review and source findings: `research/review-evidence.md`
