# IEEE Access Submission Revision Design

## Objective

Turn the current English manuscript into a shorter, internally consistent IEEE Access submission whose positive claim is exactly the claim supported by the existing experiment: under one calibrated UVC display-camera link, evaluated temporal pixel-masking profiles reduce conventional-OCR recovery from isolated short-exposure captures, while sustained integration and modern VLMs remain practical bypasses.

## Recommended Revision Strategy

Use an evidence-preserving revision. Reanalyze existing data at the correct cluster/paired level, but do not manufacture a physical brightness-matched baseline that was never captured. Replace mechanistic wording with profile-level wording wherever the current experiment cannot distinguish temporal sparsity from duty-cycle luminance, static overlays, panel response, and exposure.

This strategy keeps the paper publishable as a controlled feasibility and boundary study. It deliberately gives up stronger claims about temporal-only causation, optimized profile composition, cross-device generality, and deployment readiness.

## Manuscript Architecture

The main paper will keep the following narrative:

1. A specific operational problem: fixed-exposure UVC frames processed by conventional OCR.
2. A temporal pixel-masking profile family and its physical implementation.
3. Primary evidence: paired one-camera OCR measurements across nine geometries.
4. Failure boundaries: long exposure, sustained video aggregation, sensitive tokens, and VLMs.
5. Usability evidence for the deployed profile after the user study is completed.
6. A consolidated discussion that separates supported observations, unresolved mechanism, and external-validity limits.

Detection/tracking simulations, approximate tracking metrics, and cross-task normalized summary graphics do not carry the central argument. They will be moved to supplementary material or removed if they cannot be reproduced cleanly.

## Statistical Design

The statistical estimand is the profile contrast within the tested content/geometry archive, not uncertainty over thousands of independent real-world images. The analysis should therefore:

- retain descriptive capture-level distributions;
- compute paired contrasts for matched content and geometry;
- resample at the content level, or at the highest available independent acquisition cluster when round/session identifiers permit it;
- report cluster-aware intervals for the central unprotected-versus-deployed and unprotected-versus-high-suppression short-exposure contrasts;
- avoid treating repeated captures as independent population samples.

If authoritative identifiers do not permit a valid paired or clustered analysis for a condition, the manuscript will state that limitation instead of fabricating an interval.

## Claim Design

### Keep

The tested profiles materially reduced conventional-OCR recovery from calibrated short-exposure captures within the measured S600 link.

### Revise

The experiment does not isolate temporal sparsity as the sole cause because average luminance was not physically matched, actual panel timing was not measured, and enhanced profiles include static/nonlinear components.

The deployed profile is a preselected readability-priority composite whose end-to-end performance was measured. The current ablation does not prove that each included component improves protection.

### Remove or Move to Supplement

Claims based on eight-image detection simulation, approximate nonstandard tracking metrics, or normalization of incomparable OCR/detection/tracking metrics.

## Language and Compression

Report the headline numeric result once in the Abstract, once in Results, and once in the Conclusion. Other sections should refer to the result qualitatively or by cross-reference. Consolidate repeated statements about one camera, fixed exposure, VLM failure, and integration boundaries.

Use `conventional OCR` consistently. Replace the current title with a shorter construction centered on calibrated UVC capture and profile-level feasibility. Remove non-native phrases such as `cleaner discriminative caliber` and internally conflicting phrases such as `three-engine ceiling likely underestimates`.

## Submission and Rendering

Migrate to the current official IEEE Access template when its archive can be obtained and verified. Do not invent volume, year, DOI, or publication-history values. The final main PDF must be no more than 20 pages, contain no stale 2023 footer, and pass a full visual inspection for clipping, unreadable figures, float displacement, and incomplete references.

The final data/code statement should point to the repository and state that an immutable release will accompany submission. It must not describe the current stale SHA as the final release.

## Verification

- Clean LaTeX/BibTeX build.
- Zero unresolved citations/references.
- Automated placeholder scan excluding approved author/user-study placeholders.
- Automated claim-number consistency scan for headline values.
- Page-count check.
- Page-by-page PDF rendering and visual inspection.
- Reverse claim audit from Conclusion to Results and Methods.

## Scope Boundary

This design does not include new physical capture. If a brightness-matched control, matched noise-off enhanced profiles, panel-timing measurements, or cross-camera replication are added, the manuscript should be re-reviewed because its defensible claim scope would materially change.

