# LaTeX Paper Build Thinking Guide

> **Purpose**: Prevent committing or sharing a PDF produced by an incomplete LaTeX/BibTeX build.

## Trigger

Use this checklist whenever a paper source, bibliography, label, figure, or generated PDF changes.

## Required build path

- [ ] Use the manuscript's checked-in build entry point, such as `./build.sh` or `latexmk main.tex`.
- [ ] Do not treat one direct XeLaTeX run as a complete build after auxiliary files were removed.
- [ ] Keep the bibliography database and all `\\cite{...}` keys synchronized.

## Verification

- [ ] The build command exits with status 0.
- [ ] The final log contains no `Citation ... undefined`.
- [ ] The final log contains no `There were undefined references`.
- [ ] The final log contains no `Label(s) may have changed`.
- [ ] Extracted PDF text contains no citation placeholders such as `[?]`, `(?)`, or repeated `??`.

## Common failure mode

**Symptom**: Most citations and cross-references become question marks at once.

**Cause**: Auxiliary files were cleaned and only one XeLaTeX pass was run. The first pass records citation and label requests; BibTeX and subsequent XeLaTeX passes are still required.

**Corrective action**: Run the checked-in `latexmk` build entry point. If a cited key is still unresolved after a complete build, compare keys in `main.aux`, `main.bbl`, and the bibliography database before editing manuscript prose.
