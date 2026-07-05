# Fix Chinese paper broken citations

## Goal

Fix the Chinese paper PDF so citation markers render as numbered references instead of question marks.

## Requirements

* Diagnose the LaTeX/BibTeX citation chain before changing files.
* Keep the existing Chinese manuscript wording unchanged unless a citation key is genuinely broken.
* Restore all cited BibTeX keys needed by `paper-Chinese/main.tex`.
* Rebuild `paper-Chinese/main.pdf` with the correct XeLaTeX + BibTeX sequence.

## Acceptance Criteria

* [x] `paper-Chinese/main.log` has no `Citation ... undefined` warnings.
* [x] `paper-Chinese/main.log` has no `There were undefined references` warning.
* [x] `paper-Chinese/main.pdf` is regenerated successfully.
* [x] The screenshot symptom, bracketed citation placeholders such as `[?]`, is resolved in the rebuilt PDF.

## Definition of Done

* Minimal BibTeX/source change only.
* Full LaTeX rebuild completed.
* Verification command output checked before reporting completion.

## Technical Approach

The initial log showed `No file main.aux.`, which explains why a single XeLaTeX pass produced widespread `?` placeholders. A citation-key comparison then found one real missing key: `b_hidescreen2019`, present in the packaged English/alternate BibTeX copy but missing from `paper-Chinese/refs.bib`. The fix is to restore that BibTeX entry and run a full rebuild.

## Out of Scope

* Rewriting related-work prose.
* Reordering or reformatting the bibliography beyond the missing entry.
* Addressing unrelated font/overfull-box warnings unless they block compilation.

## Technical Notes

* Main source: `paper-Chinese/main.tex`
* Bibliography: `paper-Chinese/refs.bib`
* Existing reference source for missing entry: `paper-Chinese/paper/refs.bib`
* Build style: `\\usepackage{cite}`, `\\bibliographystyle{IEEEtran}`, `\\bibliography{refs}`
