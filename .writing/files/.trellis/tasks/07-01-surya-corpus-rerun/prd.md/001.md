# One-click Surya corpus rerun and merge

## Goal

Provide a visible, reliable one-command workflow for rerunning only the Surya
portion of the simulated Table 5 OCR corpus experiment. Preserve the existing
Tesseract and EasyOCR results, replace the legacy PaddleOCR entry with the new
Surya result, and avoid damaging the publication result if the long-running
Surya job is interrupted.

## Requirements

* Add a macOS/Linux shell entry point under `privacy-display/scripts/` that uses
  `.venv-surya/bin/python` by default and honors `SURYA_PYTHON` and
  `SURYA_DEVICE` overrides.
* Run only the `surya` engine over the existing 120-sample corpus with the paper
  parameters `n=4` and `epsilon=8/255`.
* Print startup/model-loading status and per-sample progress so a long run does
  not appear frozen.
* Require the existing result to contain valid `tesseract` and `easyocr`
  entries before starting the expensive run.
* Run Surya into a temporary result location, then atomically write a final
  `corpus_multi_engine.json` containing exactly `tesseract`, `easyocr`, and
  `surya` in that order.
* Remove `paddleocr` and any other stale engine entries from the final result.
* Preserve the original result file unchanged if Surya fails or the process is
  interrupted before completion.
* Print the final original-frame accuracy, single-subframe accuracy, and paired
  reduction for all three retained engines.

## Acceptance Criteria

* [ ] `scripts/rerun_corpus_surya.sh` starts the workflow with one command.
* [ ] Only Surya OCR inference is invoked by the new workflow.
* [ ] Progress is visible during the 120-sample run.
* [ ] A successful merge retains the existing Tesseract/EasyOCR payloads
      byte-for-byte at the object level, adds Surya, and removes PaddleOCR.
* [ ] Missing/malformed legacy results fail before Surya inference begins.
* [ ] Failed/interrupted runs do not overwrite the existing publication JSON.
* [ ] Focused automated tests cover merge filtering and validation behavior.

## Definition of Done

* Focused tests pass in the project environment.
* Shell syntax validation passes.
* The new command supports `--help` or prints self-explanatory startup output.
* No unrelated experiment or publication artifact is rerun.

## Technical Approach

Add a small Python experiment CLI for validation, temporary Surya execution,
strict merge filtering, atomic replacement, and result reporting. Add a thin
shell wrapper for environment discovery and one-command invocation. Extend
`run_corpus_multi_engine` with an opt-in progress interval while preserving its
existing default behavior.

## Decision (ADR-lite)

**Context:** Calling `run_corpus_multi_engine(..., merge_existing=True)` would
temporarily retain PaddleOCR and provides no progress, while rerunning all three
engines wastes substantial time.

**Decision:** Run Surya alone into a temporary directory and merge only after a
complete successful result. Explicitly whitelist the two legacy engines plus
Surya and replace the destination atomically.

**Consequences:** The workflow is slightly more code than a one-line command,
but it is interruption-safe, transparent, and cannot accidentally keep stale
PaddleOCR data.

## Out of Scope

* Rerunning Tesseract or EasyOCR.
* Automatically editing `paper/main.tex` with the resulting numbers.
* Regenerating all publication summaries or figures.
* Adding a Windows PowerShell wrapper in this task.

## Technical Notes

* Existing result: `privacy-display/experiments/results/corpus_multi_engine.json`.
* Core runner: `privacy-display/src/evaluation/benchmark.py`.
* Existing result currently contains `tesseract`, `easyocr`, and `paddleocr`.
* Surya model construction is lazy, so startup may pause while model files are
  loaded before the first sample completes.
* The repository already uses `progress_interval` and atomic `os.replace`
  patterns in other experiment scripts.
