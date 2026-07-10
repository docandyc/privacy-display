# Real-Capture Preprocessing and Paper Revision Design

## Purpose

Close the remaining pre-submission evidence and reporting gaps in the English IEEE Access manuscript without collecting new camera data. The revision must align the primary table with its paired estimand, evaluate a fixed conventional-OCR preprocessing attacker, update related work, expose reproducibility details, and weaken causal claims that are not isolated by the experiment.

## Analysis Architecture

The preprocessing analysis will be a separate, resumable real-capture experiment. It will read the nine archived position metadata files and select short-exposure captures from the three paper-facing primary profiles. The primary report will exclude `d0.5_a15`, match capture units by content, position, and repeat index, and collapse duplicate readability-priority captures before paired analysis.

Raw predictions will be imported from the canonical OCR archive. Five transformed variants will be generated from a versioned manifest:

1. gamma correction;
2. CLAHE luminance enhancement;
3. unsharp masking;
4. adaptive thresholding;
5. bicubic 2x upscaling.

Each transformed image will be evaluated with Tesseract, EasyOCR, and Surya. Rows will be checkpointed using `(capture ID, preprocessor, engine)` as the identity so interrupted runs can resume without silently duplicating observations.

The aggregation layer will produce:

* raw best-of-engine per capture;
* best-of-preprocessing-and-engine per capture;
* equal-`N` matched means and paired content-cluster intervals;
* all-available descriptive means as separately labeled sensitivity evidence;
* per-transform and per-engine results, failures, runtime versions, and the exact manifest.

No parameter will be selected manually for an individual image. The attacker oracle may retain the highest recovery produced by the predeclared grid.

## Manuscript Data Flow

Generated JSON and Markdown reports are the numerical source of truth. The main manuscript will use only the matched `N=288` primary values when presenting paired contrasts. The all-available readability-priority mean remains descriptive evidence and will not share a row with a paired effect derived from another estimand.

The preprocessing result will be described as a fixed-grid robustness check, not an upper bound over arbitrary image enhancement. Negative results will be retained.

## Writing Revision

The Introduction will state three research questions:

* RQ1: How much do the evaluated profiles change conventional-OCR recovery at the common 3.91-ms setting?
* RQ2: Where do failures concentrate across content and attacker preprocessing?
* RQ3: How do integration and VLM attackers bound the observation?

Related Work will cite Bao et al. (2026) and the 2025 *Displays* modulated-projection-light study. The novelty sentence will be protocol-specific rather than absolute.

Methods will record OCR/runtime versions, engine configuration, RGB image loading, metric normalization, sensitive-token extraction, perspective-corrected crop provenance, known and unknown camera controls, and the post-hoc status of the common-setting subset if confirmed by the archive history.

Causal wording will use observational language for mask granularity, physical-layer mechanisms, and the high-suppression composite. The non-preregistered `<5%` value will be called a manuscript-defined interpretive threshold.

## Failure Handling

* Missing image, ground truth, or raw OCR row: fail the finalization gate and report the exact key.
* OCR exception: checkpoint the error row; incomplete/error-bearing runs cannot become the final oracle silently.
* Engine environment mismatch: record runtime metadata and run engines separately, then merge only after key validation.
* Duplicate transformed rows: reject unless byte-identical and explicitly deduplicated.
* Partial run: preserve checkpoints, but do not update paper numbers.

## Testing

Tests will be written before production code and observed failing. They will cover selection of the common-setting primary captures, deterministic preprocessing, checkpoint identity, raw-row reuse, attacker-favorable aggregation across both engines and preprocessors, duplicate collapse, matched estimand arithmetic, and finalization rejection on missing engine/preprocessor cells.

The final verification will run focused tests, regenerate reports, build both LaTeX documents, scan logs for unresolved citations/references, and inspect the rendered primary table and surrounding pages.
