# Experimental Evaluation Revision Plan

## Purpose and Evidence Boundary

This plan governs the revision of Section V, *Experimental Evaluation*, in `main.tex`. Its objective is to make the reported evidence suitable for an IEEE Access submission without changing the paper's established contribution: the work provides system-level empirical evidence and characterizes the boundary at which stronger capture and recognition attacks recover protected content. It must not recast temporal masking as a universal security guarantee or as a wholly unprecedented primitive.

The physical-capture chain requires an external camera, a high-refresh display, and subsequently collected image analysis. Therefore, this revision assumes that the archived captures and reported analysis results are genuine and reliable. The review basis is the consistency among the manuscript, the accessible source code, test contracts, and `privacy-display/WIKI.md`; inability to reproduce camera capture in the current environment is not itself a defect in the experimental evidence.

No new experiment, algorithm, model, parameter sweep, or numerical result is to be added. The revision may only reorganize, qualify, and clarify claims already supported by the current archived evidence.

## Target Section-Level Claim

After revision, Section V should support the following bounded conclusion:

> In the evaluated 240-Hz display--S600 UVC-camera link, the tested composite profiles substantially reduce conventional OCR recovery under the matched short-exposure protocol. Fixed preprocessing, long exposure, temporal averaging, full-cycle digital reconstruction, and VLM probing recover substantial information under stronger attacker capabilities. The browser study separately quantifies the usability cost of the readability-priority configuration.

The section should not imply protection against arbitrary cameras, panels, exposure control, continuous recording, commercial OCR, VLMs, or complete-cycle reconstruction.

## Revision Principles

1. **Use one primary estimand.** The matched eight-geometry, common-setting comparison is the primary OCR result. The nine-geometry pool is sensitivity evidence only.
2. **Preserve the distinction between observation and causal attribution.** The physical results are evidence from one system link; brightness, exposure, panel response, ISP behavior, and profile order are not fully isolated.
3. **Report the real statistical unit.** Capture-level counts describe the archive, while content-cluster resampling describes the uncertainty calculation.
4. **Treat successful attacks as primary evidence, not as exceptions.** Preprocessing, temporal averaging, reconstruction, and VLM results define the attack boundary central to the paper.
5. **Keep evidence tiers explicit.** Main physical OCR is the central evaluation; VLM probing and browser usability are complementary; detection/tracking and small-image simulations are stress-test or pipeline evidence.
6. **Do not manufacture precision.** Any missing provenance detail should be described conservatively, not inferred from unavailable physical measurements.

## Planned Revisions by Subsection

### 1. Experimental Setup

**Current role:** Defines hardware, UVC exposure labels, content, metrics, aggregation, preprocessing, and exact physical-capture profiles.

**Required revisions:**

- Add a short paragraph immediately after the capture-device description stating that the reported UVC exposure values are control-derived labels and that profile acquisition order was fixed. State that automatic exposure, gain, white balance, physical panel luminance, and panel--camera phase were not fully measured. This should frame the physical comparisons as system-link evidence rather than a fully isolated causal experiment.
- Retain the exact physical profile table. Keep the explicit distinction between the reusable `strong` default and the reported readability-priority override (`stripe alpha = 0.10`, `glyph alpha = 0.12`, inversion `alpha = 0.20`). This matches the playback contract.
- In the OCR aggregation paragraph, distinguish the three quantities clearly:
  - capture-level result rows;
  - duplicate-averaged, matched profile--content--position--repeat cells;
  - 12 content-item clusters used for the paired bootstrap.
- State that the cluster intervals hold the evaluated geometries fixed. Do not describe the 288 matched capture units as 288 independent population samples.
- Preserve the six-transform preprocessing grid as a fixed attacker model. Continue to state that it is stronger than raw OCR but not an exhaustive adaptive reconstruction attack.

**Do not change:** Hardware names, the nine geometry locations, the UVC labels, the 12-item content composition, the fixed preprocessing transformations, engine versions, or reported values.

### 2. Real-Capture OCR Experiment

**Current role:** Supplies the main physical evidence for conventional OCR reduction and the physical integration boundary.

**Required revisions:**

- Introduce Table `tab:real_ocr_common` explicitly as the sole primary headline estimate: 8 common-setting geometries, 12 content items, 3 repeats, and 288 matched units per profile.
- Describe the 94.1% / 15.1% / 5.0% nine-geometry values only as an unbalanced all-available sensitivity pool. Do not use them as the main cross-profile comparison in the section narrative.
- In Table `tab:real_ocr_common` or its caption, add a compact note that uncertainty is derived from 12 content clusters, with geometry held fixed. The table may retain `$N=288$`, but the resampling unit must be visible near the result.
- Keep the best-of-engine aggregation because it models an attacker selecting the most successful tested OCR engine. Continue to report per-engine results so that the attacker-favorable summary remains auditable.
- Retain the preprocessing oracle result and state its interpretation precisely: the reported raw short-exposure reduction is not a bound against the fixed preprocessing attacker.
- Tighten the long-exposure discussion. Keep the observed position-dependent reversal, but call it an interaction observed in the evaluated imaging chain. Do not attribute it definitively to the mask or overlays; retain saturation/contrast compression only as a candidate explanation.
- Retain the high-suppression result as an exploratory recovery-boundary profile. Avoid presenting the descriptive `<10%` target as a general security threshold.
- State the nominal duration associated with the 150-frame mean at the recorded nominal frame rate, and specify whether each aggregate is formed per content item and position. If the existing archived documentation contains exact segment/window information, quote it; otherwise use only the currently documented aggregate definition.

**Claims to retain:**

- Short-exposure conventional OCR reduction in the matched physical protocol.
- Upper-tail leakage and sensitive-field recovery as part of the attack-boundary characterization.
- Recovery under long exposure and 150-frame temporal averaging.

### 3. Inversion-Strength Ablation

**Current role:** Establishes that the readability-priority inversion setting is a modeled operating choice rather than an empirically optimized universal setting.

**Required revisions:**

- Keep the five-item subset and its separate sample sizes prominent in the prose and caption.
- Retain the explicit statement that the `alpha = 0.20` ablation estimate is not a second estimate of the 12-item readability-priority condition.
- Use neutral phrasing for overlapping descriptive resampling intervals; do not claim equivalence or an optimized weak-inversion setting.
- Keep the degradation under near-full inversion as a trade-off observation, not as a recommendation for deployment.

### 4. Real-Capture VLM Probes

**Current role:** Demonstrates that conventional OCR results do not delimit recovery by stronger recognition systems and thus materially characterizes the attack boundary.

**Required revisions:**

- Keep the three endpoint names, raw-JPEG input path, temperature-zero setting, local scoring, and the statement that ground truth was excluded from prompts.
- Preserve the distinction between conditional parseable-response cells and lower/upper missingness bounds. Do not rank models using cells with non-random failures.
- Make the 0.5-m session-selection qualification visible in the subsection opening and in any summary sentence: the reported high short-exposure recovery comes from the archived adequate-exposure, attacker-favorable session selected after comparing the two available sessions.
- Align the Abstract and Conclusion with this qualification when they cite the 77.8% exact-match result. The statement must not read as a stable distance-generalizable estimate.
- Clarify the video aggregation protocol in reproducible prose: source duration or nominal frame count, number of aggregate inputs, whether windows overlap, and the unit represented by each table row. Only use details already present in archived metadata or scripts.
- Retain the content-type analysis as evidence that large-font short snippets are more recoverable than dense pages. Do not infer an untested general relationship between VLM ability and all font sizes or languages.

### 5. User Experience Study

**Current role:** Quantifies the usability cost of the readability-priority browser implementation, separately from the Python physical-capture path.

**Required revisions:**

- Retain the within-subject design, formal 200-Hz gate, fixed `n=4`, ABBA/BAAB typing order, six-condition Latin-square rating order, exclusion criteria, participant-level aggregation, bootstrap intervals, and Holm correction. These match the accessible browser and analysis code.
- Keep the rendering-path distinction explicit: the study uses the independent Canvas2D implementation with a deterministic browser PRNG, pixel-space gain, surrogate texture noise, six rotating cycles, and `alpha = 0.20` inversion. It is a usability evaluation of that browser implementation, not a photometric replication of the Python playback path.
- Replace any wording that implies identical control and masked text instances or that the temporal pipeline is literally the sole trial-level difference. The implementation generates independent pseudo-word text instances with the same generation mechanism and target length. State this accurately and retain the order counterbalancing explanation.
- Keep the interpretation of subjective measures narrow: stability is an inverse-flicker item, and comfort is immediate self-reported visual comfort rather than a clinical fatigue endpoint.
- In the results paragraph, retain the Holm-qualified interpretation: speed-related outcomes remain significant after correction, whereas the nominal accuracy difference does not.

### 6. Real-Capture Object Detection and Tracking

**Current role:** Provides an exploratory cross-task stress test, not the primary proof of the display-privacy claim.

**Required revisions:**

- Preserve the opening limitation that the evidence strength is below that of the main OCR experiment.
- State in the table captions and accompanying text that `real_clean`, `real_short`, and `real_video` differ in more than protection: exposure, resolution/cropping, and temporal aggregation differ. Do not describe their gaps as an isolated protection effect.
- Retain the still-display-then-capture description for MOT17; do not imply that it is a continuous real-world motion-video result.
- Verify the metric provenance from the archived result manifest before final wording. Report the backend actually used for HOTA and IDF1. The accessible code supports `motmetrics`, a SciPy fallback, and optional TrackEval; the manuscript must not make a broader TrackEval claim than the archived run supports.
- Replace any phrase equating detector/tracker degradation with OCR reduction. Use “directional degradation in exploratory detector/tracker stress tests.”

### 7. Software Simulation Experiments

**Current role:** Explains mechanism-level behavior and makes complete-cycle reconstruction an explicit, reproducible failure boundary.

**Required revisions:**

- Retain the 120-sample single-subframe OCR experiment as a renderer-level diagnostic, not as a physical-camera result.
- Retain the full-cycle mean and strongest per-sample reconstruction results as direct evidence that linear complementary decomposition is not secure after registered full-cycle accumulation.
- Keep the 16-sample profile reconstruction ablation clearly separate from the 120-sample base corpus.
- Retain the COCO 8-image evaluation only as a pipeline diagnostic, as currently labeled. Do not use it to claim broad detection generalization.
- Retain the 5,316-frame MOT simulation as an implementation-level stress test and preserve the in-project greedy-association qualification.

## Cross-Section Consistency Changes

The following wording changes must be propagated outside Section V after the section itself is revised:

1. **Abstract:** Use the matched common-setting OCR estimate as the main quantitative result. If the 0.5-m VLM exact-match value remains, include the attacker-favorable adequate-exposure-session qualification.
2. **Discussion and Conclusion:** Describe detection/tracking as exploratory cross-task stress evidence, not as additional OCR evidence.
3. **Discussion and Limitations:** Keep the one-camera, one-panel, fixed-order, control-derived exposure, and incomplete physical photometry limitations; ensure they do not contradict the upfront Experimental Setup disclosure.
4. **Data Availability:** Retain the existing access statement unless repository policy changes. The revision must not claim that the camera experiment can be regenerated in the current no-camera environment.

## Verification Checklist Before Editing `main.tex`

- [ ] Every numerical headline identifies whether it is the matched primary analysis or the unbalanced sensitivity pool.
- [ ] Every interval identifies its resampling unit and does not imply independent capture-level inference when clustering is used.
- [ ] Profile labels and exact physical parameters match the playback contract.
- [ ] VLM table labels, effective call counts, missingness qualifiers, and session-selection language agree with the archived evaluation record.
- [ ] User-study configuration and values agree with `webstudy/static/app.js` and `webstudy/analysis_output/analysis_report.json`.
- [ ] Detection/tracking metric backend wording agrees with the run manifest and `src/evaluation/mot.py`.
- [ ] Simulations are consistently labeled as renderer, reconstruction-boundary, or pipeline evidence rather than physical generalization evidence.
- [ ] No revision adds new numerical claims, attack models, algorithms, or experiments.
