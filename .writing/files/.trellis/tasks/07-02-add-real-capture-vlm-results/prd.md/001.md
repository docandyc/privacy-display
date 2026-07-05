# Add real-capture VLM results to IEEE Access manuscript

## Goal

Integrate the newly completed real-device VLM runs into `paper/main.tex` so the manuscript's VLM boundary argument is supported by the latest evidence rather than the earlier single-distance probe alone.

## What I Already Know

* The user completed the `d1.5_a0` real-capture VLM run: 120 captures, 360 API calls, 0 errors, exact-match summaries for Qwen3-VL-32B-Instruct, Kimi-K2.6, and GLM-4.5V.
* The `d1_a0` run produced 339 successful calls and 21 errors; `real_capture_vlm_d1_a0_partial.json` is intentionally retained, so this run must be labeled incomplete or supplementary.
* `paper/main.tex` already contains a VLM probe section based on the older `d0.5_a0` result file and frames VLM results as a boundary/negative finding rather than a broadened defense claim.
* The current manuscript already narrows the paper to a single-UVC-camera feasibility study and treats VLM/video averaging as residual attack frontiers.

## Requirements

* Update the VLM experiment description to cover the completed `d1.5_a0` run and the incomplete `d1_a0` run without overstating either.
* Revise the VLM table(s) so the new results are represented with actual successful-call counts and clear run-completion status.
* Preserve the manuscript's core claim scope: the method is supported for traditional OCR short-exposure mitigation, not for VLM attackers.
* Update abstract, contribution, discussion, limitations, and conclusion language if their current numbers or qualitative claims are made stale by the new VLM results.
* Treat `d1.5_a0` as the primary new completed VLM evidence and `d1_a0` as descriptive supplementary evidence unless the manuscript explicitly says it is incomplete.

## Acceptance Criteria

* [x] `paper/main.tex` reports the latest `d1.5_a0` completed VLM results.
* [x] `paper/main.tex` mentions the `d1_a0` run only with its incomplete status and actual successful-call counts.
* [x] VLM claims are evidence-bounded and do not imply cross-device, cross-model-version, or full multi-geometry validation.
* [x] The manuscript still compiles after the LaTeX edits.
* [x] Any stale references to "only 0.5 m" or "9-position VLM planned" are revised or qualified.

## Out of Scope

* Rerunning VLM API calls.
* Creating a full new VLM figure unless the existing table cannot carry the evidence clearly.
* Changing OCR, COCO, MOT, or user-study results except where VLM wording affects shared framing.
* Adding new citations.

## Technical Notes

* Main manuscript: `paper/main.tex`.
* Result files:
  * `privacy-display/experiments/results/real_capture_vlm.json` (`d0.5_a0`, older incomplete run).
  * `privacy-display/experiments/results/real_capture_vlm_d1_a0.json` (`d1_a0`, incomplete, 339/360 successful calls).
  * `privacy-display/experiments/results/real_capture_vlm_d1.5_a0.json` (`d1.5_a0`, complete, 360/360 successful calls).
* Result inventory: `research/vlm-result-inventory.md`.
