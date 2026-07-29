# LaTeX Paper Build Thinking Guide

> **Purpose**: Prevent committing or sharing a PDF produced by an incomplete LaTeX/BibTeX build.

## Trigger

Use this checklist whenever a paper source, bibliography, label, figure, or generated PDF changes.

## Required build path

- [ ] Use the manuscript's checked-in build entry point, such as `./build.sh` or `latexmk main.tex`.
- [ ] Do not treat one direct XeLaTeX run as a complete build after auxiliary files were removed.
- [ ] Keep the bibliography database and all `\\cite{...}` keys synchronized.

## Generated figure path integrity

- [ ] If a plotting script derives its repository root from
      `Path(__file__).resolve()`, inspect every parent symlink before running
      it. Resolving a symlink can redirect the output to another checkout even
      when the command was launched from the manuscript workspace.
- [ ] After regeneration, verify the absolute path, modification time, and
      content of the figure actually referenced by the manuscript. A generator
      log that reports a different `paper/figures/` directory does not prove
      that the current manuscript received the new artifact.

## Verification

- [ ] The build command exits with status 0.
- [ ] The final log contains no `Citation ... undefined`.
- [ ] The final log contains no `There were undefined references`.
- [ ] The final log contains no `Label(s) may have changed`.
- [ ] Extracted PDF text contains no citation placeholders such as `[?]`, `(?)`, or repeated `??`.
- [ ] For the English `paper/` manuscript, use `latexmk -xelatex -g main.tex` because that directory has no standalone `build.sh`; inspect the resulting `main.pdf` and `main.log` after the full XeLaTeX/BibTeX/xdvipdfmx cycle.
- [ ] In the checked-in `ieeeaccess.cls`, table captions use a different math-font version from table bodies. Uppercase Greek symbols such as `\Delta` can therefore render as an incorrect accent in a caption even when the same symbol is correct in a table header; use the `textgreek` text glyph (for example `{\textDelta}`) in the affected caption and verify the final PDF visually or with `pdftotext`.

## Editable Visio figure integrity

Use these checks when a manuscript figure has an editable `.vsdx` source plus mirrored English/Chinese PDFs:

- [ ] Treat the checked-in final VSDX as authoritative for any panel explicitly requested to remain unchanged; a scene generator may have drifted from the reviewed editable file.
- [ ] Before regeneration, preserve a baseline VSDX/PDF and compare unaffected panels at publication size. For an exact preservation claim, compare normalized Shape XML as well as pixels.
- [ ] Keep the scene, final VSDX, final PDF, and review PNG semantically aligned with a deterministic validator for task-specific invariants.
- [ ] Verify mirrored English/Chinese VSDX and PDF files by SHA-256, not by filename or file size.
- [ ] Check the figure PDF `MediaBox` against any `viewport=...,clip` in both manuscripts, then inspect the actual compiled page rather than only the standalone figure.
- [ ] Do not “fix” PDF xref-row trailing spaces to satisfy a text whitespace checker. This repository assigns PDFs `diff=astextplain`; run the whitespace gate on text sources while validating PDFs structurally.
- [ ] If a build host lacks a manuscript font, use a review-only source copy or an environment-local alias for verification. Do not commit a typography change as part of an unrelated figure task.

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

## Windows output-path and PDF-lock fallback

- [ ] If `xdvipdfmx` reports `Unable to open "main.pdf"` after XeLaTeX succeeds, test whether a PDF viewer has locked the existing file before changing manuscript source.
- [ ] When the canonical PDF is locked, complete the review build in a relative ASCII-only directory under the manuscript, for example `latexmk -xelatex -outdir=_build_review main.tex`.
- [ ] Prefer a relative review directory over `%TEMP%` on Windows hosts with a non-ASCII user profile. TeX Live can otherwise corrupt the expanded output path under a legacy console code page and fail while setting `TEXMF_OUTPUT_DIRECTORY`.
- [ ] Inspect the review PDF and final log normally, then replace the canonical PDF only after its lock is released. Do not delete or forcibly rename a locked user-opened PDF.
