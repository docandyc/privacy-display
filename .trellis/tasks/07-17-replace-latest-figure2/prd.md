# Replace Figure 2 with the latest revision

## Goal

Rebuild the English manuscript so that Figure 2 in the compiled article uses the latest figure asset committed in `b00fcd9` while preserving all existing uncommitted manuscript edits.

## Requirements

- Treat `paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.pdf` from commit `b00fcd9` as the authoritative latest Figure 2.
- Keep the current Figure 2 caption, label, placement, and LaTeX sizing/cropping unless rendering proves that the revised asset requires an adjustment.
- Preserve the user's existing uncommitted edits in `paper/main.tex` and the generated manuscript artifacts.
- Rebuild `paper/main.pdf` from the current working-tree version of `paper/main.tex`.

## Acceptance Criteria

- [x] `paper/main.tex` resolves Figure 2 to the latest committed figure asset.
- [x] `paper/main.pdf` is rebuilt successfully with no LaTeX errors.
- [x] The rendered Figure 2 visibly contains the revised M1 wording from commit `b00fcd9`.
- [x] Figure 2 is sharp, unclipped, correctly positioned, and its caption remains legible.
- [x] No existing user-authored manuscript changes are overwritten.

## Definition of Done

- The compiled English manuscript contains the latest Figure 2.
- The affected manuscript page and the final PDF are visually checked.
- Build diagnostics contain no fatal errors or missing references introduced by this replacement.

## Technical Approach

The LaTeX source already includes the authoritative `final/figure2_method_pipeline.pdf` path. Recompile the English manuscript in place so the PDF embeds the updated asset, then render and inspect the affected page. Modify `main.tex` only if the latest figure no longer fits the existing viewport.

## Decision (ADR-lite)

**Context**: The latest git commit updates the English Figure 2 PDF in place, and the manuscript already references that path.

**Decision**: Rebuild rather than copy or rename the figure, avoiding unnecessary source changes and preserving a single authoritative figure path.

**Consequences**: The current uncommitted manuscript edits are included in the rebuilt PDF; they remain untouched in the source and are not claimed as part of this task.

## Out of Scope

- Regenerating or redesigning Figure 2.
- Syncing the separate Chinese manuscript, whose Figure 2 asset was not changed by commit `b00fcd9`.
- Editing unrelated manuscript prose or committing the user's existing work.

## Technical Notes

- Latest figure commit: `b00fcd9` (`paper: fix Figure 2 M1 flowchart wording`).
- Figure include location: `paper/main.tex`, label `fig:pipeline`.
- Existing dirty files before this task: `paper/main.aux`, `paper/main.log`, `paper/main.pdf`, and `paper/main.tex`.

## Spec Review

No spec update is needed. The existing LaTeX paper-build guide already requires a complete `latexmk` build plus citation/reference checks, and the editable Visio paper-figure scenario already requires viewport preservation and visual inspection of both the standalone figure and compiled manuscript page. This task followed those contracts without revealing a new reusable rule or failure mode.
