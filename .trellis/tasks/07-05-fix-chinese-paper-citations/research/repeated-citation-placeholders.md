# Bug Analysis: Chinese paper citations repeatedly become question marks

## 1. Root Cause Category

- **Category**: E — Implicit Assumption
- **Specific Cause**: The repository relied on the user or editor to know that a clean LaTeX build requires XeLaTeX, BibTeX, and repeated XeLaTeX passes. A direct single XeLaTeX invocation after deleting auxiliary files still produced a PDF, but every citation and cross-reference remained unresolved.

## 2. Why the previous fix did not persist

1. The previous repair correctly restored the missing `b_hidescreen2019` BibTeX entry and rebuilt the PDF.
2. It fixed the generated artifact but did not constrain future build entry points.
3. A later clean-and-single-XeLaTeX action recreated the same visible symptom even though all 52 citation keys were valid.

## 3. Prevention mechanisms

| Priority | Mechanism | Specific Action | Status |
|---|---|---|---|
| P0 | Architecture | Check in `paper-Chinese/latexmkrc` and `build.sh` as the canonical build path | Done |
| P0 | Runtime validation | Make the build fail when unresolved citation/reference warnings remain | Done |
| P1 | Documentation | Add build instructions and a TeX magic comment selecting `latexmk` | Done |
| P1 | Process | Add a LaTeX paper-build checklist to Trellis guides | Done |

## 4. Systematic expansion

- **Similar issues**: The English manuscript can exhibit the same behavior if auxiliary files are cleaned and only one engine pass is run.
- **Design improvement**: Treat the build command, not the generated PDF, as the source of reproducibility.
- **Process improvement**: Verify both the log and extracted PDF text before committing generated manuscripts.

## 5. Knowledge capture

- [x] Added a project-level LaTeX build thinking guide.
- [x] Added a canonical Chinese-manuscript build command.
- [x] Recorded the recurrence and why the earlier artifact-only repair was insufficient.
