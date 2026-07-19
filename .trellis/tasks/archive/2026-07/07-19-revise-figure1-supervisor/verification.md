# Verification

Verified on 2026-07-19 (Asia/Taipei).

## Semantic and scene gates

* `validate_supervisor_revision.py`: pass. Four disjoint 5x5 subframes reconstruct the exact capital `A`; readable output equals the union; camera fragment equals selected subframe 2; three rightward sequence arrows and two thick OCR-X strokes are present.
* `scene_validate.py --strict`: pass with non-blocking legacy warnings confined to the source inventory/preserved left-panel scene and intentional nested display/grid overlays.
* `scene_audit.py --fail-on-rebuild`: pass, with no `[REBUILD]` findings.
* Python byte-compilation: pass for the builder, export/merge/polish helpers, and both validators.

## Final assets

* `validate_final_assets.py`: pass.
* The final-asset validator recovers every 5x5 cell from editable VSDX geometry/fills and checks the unobscured PNG cell interiors, so the scene, VSDX, and review render cannot silently diverge.
* Re-running the Open XML panel merge and second-pass polish reproduces the stored intermediate and final VSDX/PDF hashes exactly.
* Canonical panel (a) Shape XML is identical to the prior reviewed VSDX after ignoring remapped shape IDs.
* English and Chinese VSDX SHA-256: `b75e7e01442dada5d2dfd1dea05cc300f665cfd35c0c85b9bc9af0bc721a7674`.
* English and Chinese PDF SHA-256: `7854e39bf795fde7a00d74a8455f4b34a2f6e8b5420b93ebb4192dd32fedb3d5`.
* PDF geometry: one page, 252 x 168 pt (3.50 x 2.333 in).
* PNG review render: 1050 x 700 px (300 dpi equivalent).

## Visual review

* Round 1 exposed a generated-left-panel drift and the readable-display stand crossing `Temporal integration`; both were corrected.
* Round 2 reviewed the full 1050x700 figure and targeted subframe, human-output, and OCR crops.
* `review_checklist_gate.py`: pass, covering 15 topology items and 5 visual-layout items with zero failures.
* `round_noop_gate.py`: pass, with 35 renderer-effective scene changes and a nonzero rendered-PNG change from the preserved baseline.
* The final OCR X, complete `A`, exact subframe-2 fragment, and three local sequence arrows remain clear at publication width.

## Manuscript builds

* English: TeX Live `latexmk -pdf` full build to the review directory, exit 0. Missing shared study figures were resolved read-only through `TEXINPUTS` from the byte-identical Chinese figure directory.
* Chinese: TeX Live `latexmk`/XeLaTeX full build to the review directory, exit 0. A review-only copy used installed `STXihei` because this Windows host lacks the source-requested `STHeiti`; the checked-in manuscript source was not changed.
* Final English and Chinese logs contain no undefined citations, undefined references, or rerun-required warning.
* Extracted PDF text contains no `[?]`, `(?)`, or `??` placeholders.
* Figure 1 was visually inspected on page 2 of both compiled manuscripts; the existing `viewport=0 0 252 168,clip` includes the revised figure exactly.

## Diff hygiene

* `git diff --check -- . ':(exclude)**/*.pdf'`: pass. PDFs are configured with `diff=astextplain`; their standards-compliant xref rows contain trailing spaces and are therefore excluded from this text-only whitespace gate.
* Pre-existing untracked `paper/review_report.md` remains untouched.
