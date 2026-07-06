# Fix Chinese paper broken citations

## Goal

Fix the Chinese paper PDF so citation markers render as numbered references instead of question marks.

## Requirements

* Diagnose the LaTeX/BibTeX citation chain before changing files.
* Keep the existing Chinese manuscript wording unchanged unless a citation key is genuinely broken.
* Restore all cited BibTeX keys needed by `paper-Chinese/main.tex`.
* Rebuild `paper-Chinese/main.pdf` with the correct XeLaTeX + BibTeX sequence.
* Provide a checked-in build entry point that prevents recurrence after auxiliary files are cleaned.

## Acceptance Criteria

* [x] `paper-Chinese/main.log` has no `Citation ... undefined` warnings.
* [x] `paper-Chinese/main.log` has no `There were undefined references` warning.
* [x] `paper-Chinese/main.pdf` is regenerated successfully.
* [x] The screenshot symptom, bracketed citation placeholders such as `[?]`, is resolved in the rebuilt PDF.
* [x] A clean build through `paper-Chinese/build.sh` resolves all citations and cross-references.
* [x] The build fails if unresolved citation or cross-reference warnings remain.

## Definition of Done

* Minimal BibTeX/source change only.
* Full LaTeX rebuild completed.
* Verification command output checked before reporting completion.

## Technical Approach

The initial log showed `No file main.aux.`, which explains why a single XeLaTeX pass produced widespread `?` placeholders. A citation-key comparison then found one real missing key: `b_hidescreen2019`, present in the packaged English/alternate BibTeX copy but missing from `paper-Chinese/refs.bib`. After the issue recurred, the new log again showed a clean auxiliary state followed by only one direct XeLaTeX pass, while all 52 citation keys were present in both `refs.bib` and `main.bbl`. The durable fix is a `latexmkrc` plus `build.sh` that runs BibTeX and repeated XeLaTeX passes and rejects unresolved-reference logs.

## Out of Scope

* Rewriting related-work prose.
* Reordering or reformatting the bibliography beyond the missing entry.
* Addressing unrelated font/overfull-box warnings unless they block compilation.

## Technical Notes

* Main source: `paper-Chinese/main.tex`
* Bibliography: `paper-Chinese/refs.bib`
* Existing reference source for missing entry: `paper-Chinese/paper/refs.bib`
* Build style: `\\usepackage{cite}`, `\\bibliographystyle{IEEEtran}`, `\\bibliography{refs}`
