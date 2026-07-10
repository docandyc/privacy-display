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

## Citation and hardware integrity

- [ ] Verify every new DOI and arXiv identifier against a primary metadata source (publisher/Crossref, arXiv API, conference proceedings, or official project documentation).
- [ ] Before normalizing BibTeX DOI fields, inspect the active `.bst`. This repository's `IEEEtran.bst` v1.14 does not read `doi`, so cited DOIs stay in `note = {doi: ...}` and must be verified in the final `.bbl`.
- [ ] If an arXiv preprint has a matching formal proceedings or journal version, cite the formal version and record the DOI.
- [ ] Keep local citation keys aligned with the actual first author and publication year; after renaming a key, search both manuscript sources and generated `.aux` files for the retired key.
- [ ] Treat product model, sensor, and timing claims as evidence-bearing facts. Cite manufacturer documentation for published specifications and label unmeasured quantities or mechanisms as hypotheses rather than facts.
- [ ] Inspect the final `.blg` and generated bibliography after a complete build. An early BibTeX pass may report stale keys from the previous `.aux`; only the final build state proves resolution.

## Common failure mode

**Symptom**: Most citations and cross-references become question marks at once.

**Cause**: Auxiliary files were cleaned and only one XeLaTeX pass was run. The first pass records citation and label requests; BibTeX and subsequent XeLaTeX passes are still required.

**Corrective action**: Run the checked-in `latexmk` build entry point. If a cited key is still unresolved after a complete build, compare keys in `main.aux`, `main.bbl`, and the bibliography database before editing manuscript prose.
