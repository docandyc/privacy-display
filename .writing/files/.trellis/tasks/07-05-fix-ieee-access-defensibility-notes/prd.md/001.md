# Fix IEEE Access defensibility review notes

## Goal

Revise the IEEE Access manuscript so the profile definitions, integration-attack interpretation, short-exposure component explanation, VLM table reporting asymmetry, and Fig. 2 caption are explicit enough to withstand reviewer scrutiny.

## Requirements

* Clarify in §IV-E that the Strong, Deployed, and capture-hardened profiles are built on the base temporal mask with complementary noise enabled; Table 2's `Mask + noise` row is the base mask+noise condition without stripe/glyph anti-OCR overlay.
* Clarify that weak-amplitude Strong overlay does not provide a measurable real-capture integration-attack gain over mask-only; integration-attack mitigation appears only at capture-hardened amplitudes, with residual leakage still disclosed.
* Extend the Component role discussion so the short-exposure increase for Strong versus mask-only is handled together with the mask+noise increase.
* Explain why Table 4 reports only `video:temporal_mean` at 0.5 m while reporting all four aggregate views at 1.5 m, and state that omitted 0.5 m aggregate views are archived.
* Expand Fig. 2 caption to match the paper's self-contained caption style.
* Leave Table 5 baseline and IEEE template `\\history` / `\\doi` placeholders unchanged unless a direct consistency problem appears.

## Acceptance Criteria

* [ ] `paper/main.tex` contains an unambiguous profile composition statement.
* [ ] §V-A findings distinguish weak overlay from capture-hardened integration-attack behavior.
* [ ] Component role text covers both `mask+noise` and Strong short-exposure nonmonotonicity.
* [ ] VLM section or Table 4 caption discloses the 0.5 m aggregate-view reporting asymmetry.
* [ ] Fig. 2 caption is expanded and remains concise.
* [ ] LaTeX source passes a lightweight syntax/build check where feasible.

## Definition of Done

* Edits are limited to the manuscript and task metadata needed for this Trellis session.
* No unrelated dirty files are staged or modified.
* Verification output is recorded in the final handoff.

## Technical Approach

Make targeted textual edits in `paper/main.tex`, preserving existing conservative claim scope and not adding unsupported citations or new empirical claims.

## Out of Scope

* Recomputing experimental metrics or regenerating figures.
* Changing Table 5 baseline wording or IEEE template placeholders noted by the reviewer as acceptable.
* Editing Chinese manuscript mirror unless explicitly requested.

## Technical Notes

* Implementation check: `privacy-display/experiments/anti_ocr_profile_ablation.py` and `privacy-display/src/demo/playback_demo.py` show `build_playback_frames(..., use_noise=True)` by default; Strong/deployed profile experiments therefore use complementary noise plus stripe/glyph anti-OCR overlay unless explicitly disabled.
* Current target file: `paper/main.tex`.
