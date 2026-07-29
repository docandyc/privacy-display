# Correct Table 16 Tesseract Reduction

## Goal

Correct the Tesseract reduction value in English manuscript Table 16 so it reflects the absolute percentage-point difference between the original frame and a single subframe.

## What I Already Know

* `paper/main.tex` Table 16 (`tab:ocr_corpus`) currently reports Tesseract as 94.0% original, 0.0% single subframe, and 93.9% reduction.
* The other rows use the absolute percentage-point convention: EasyOCR is 94.1 - 0.0 = 94.1%, and Surya is 97.0 - 2.6 = 94.4%.
* The corresponding Chinese manuscript table already reports Tesseract's reduction as 94.0%.

## Requirements

* Change only the Tesseract Reduction cell in English Table 16 from 93.9% to 94.0%.
* Preserve the existing absolute percentage-point convention and all other table values.

## Acceptance Criteria

* [ ] `paper/main.tex` Table 16 contains `Tesseract & 94.0\% & 0.0\% & 94.0\%`.
* [ ] EasyOCR and Surya rows remain unchanged.
* [ ] The manuscript has no whitespace errors introduced by the edit.

## Definition of Done

* The source correction is verified by a targeted search and diff check.
* Existing unrelated working-tree changes are preserved.

## Technical Approach

Apply a one-cell source correction in `paper/main.tex`; compilation is unnecessary because the edit neither changes LaTeX structure nor layout.

## Decision (ADR-lite)

**Context:** Table 16 labels the column as Reduction and its adjacent rows establish absolute percentage-point subtraction as the reporting convention.

**Decision:** Report Tesseract's 94.0 percentage-point reduction, matching 94.0% minus 0.0% and the Chinese manuscript.

**Consequences:** The English table becomes arithmetically consistent without changing experimental data or claims.

## Out of Scope

* Recomputing OCR measurements.
* Revising other manuscript content, generated PDFs, or unrelated working-tree changes.

## Technical Notes

* Source: `paper/main.tex`, Table 16 / `tab:ocr_corpus`.
* Related manuscript-design guidance: `docs/superpowers/specs/2026-07-11-fix-claim-audit-presentation-design.md` calls for clear semantics in the synthetic OCR reduction table.
