# Export revised Figure 1 to Chinese and English papers

## Goal

Export the user-edited Visio Figure 1 and place the resulting PDF in both the English and Chinese paper trees so both manuscripts use the revised figure.

## Requirements

* Treat `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.vsdx` as the revised source.
* Export a fresh PDF from Microsoft Visio.
* Synchronize the revised VSDX and exported PDF to the matching `final/` directory under `paper-Chinese`.
* Preserve the existing LaTeX figure path, size, crop, captions, labels, and surrounding manuscript text.
* Rebuild both manuscripts with their existing engines.

## Acceptance Criteria

* [ ] English and Chinese `final/figure1_concept_threat.pdf` files are freshly exported and byte-identical.
* [ ] English and Chinese VSDX source files are byte-identical.
* [ ] `paper/main.pdf` compiles successfully.
* [ ] `paper-Chinese/main.pdf` compiles successfully.
* [ ] Figure 1 is visible and correctly placed in both compiled PDFs.

## Definition of Done

* Exported artifacts are present in both paper trees.
* Both LaTeX builds complete without fatal errors.
* Rendered Figure 1 pages are visually inspected.

## Technical Approach

Use the existing `export_final_pdf.py` Visio COM export path, copy the canonical artifacts to the Chinese paper mirror, compile the English paper with its existing latexmk engine and the Chinese paper with XeLaTeX, then render/inspect the Figure 1 pages.

## Decision (ADR-lite)

The English `paper/.../final` VSDX is canonical because it is the exact path supplied by the user and has the latest modification time. Both papers already reference a PDF at the corresponding relative path, so no TeX source edit is necessary.

## Out of Scope

* Redesigning Figure 1.
* Changing captions, crop boxes, labels, or manuscript prose.
* Updating any other figure.

## Technical Notes

* English reference: `paper/main.tex:89`.
* Chinese reference: `paper-Chinese/main.tex:100`.
* The existing English PDF predates the revised VSDX and must be regenerated.

