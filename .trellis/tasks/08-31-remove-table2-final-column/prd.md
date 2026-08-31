# Remove final column from Table 2

## Goal

Fix the English manuscript's Table 2 layout by removing its rightmost 'Intended evaluation role' column, which is clipped beyond the page boundary in the compiled PDF. Preserve the remaining profile-definition data and keep the manuscript build valid.

## Requirements

* Update only the English Table 2 source in paper/main.tex.
* Remove the 'Intended evaluation role' header and the corresponding final cell from every row.
* Update the nearby explanatory sentence so it no longer claims that Table 2 contains intended evaluation roles.
* Leave all other table content and the separate Chinese manuscript unchanged.

## Acceptance Criteria

* [ ] English Table 2 has four columns and no 'Intended evaluation role' column or cells.
* [ ] The surrounding prose accurately describes the reduced table.
* [ ] latexmk -xelatex -g main.tex completes successfully in paper/.
* [ ] The rebuilt PDF shows Table 2 fully inside the page width with no clipped right edge.
* [ ] The final LaTeX log has no undefined citations, undefined references, or changed-label warning.

## Definition of Done

* Source and generated manuscript artifacts are updated as required by the checked-in build workflow.
* The rebuilt Table 2 is visually inspected after rendering.
* The task change is committed without including unrelated worktree changes.

## Technical Approach

Change the Table 2 tabular declaration from five columns to four, remove the last header/cell from each row, revise the one nearby sentence that mentions the removed role column, then run the repository-prescribed full XeLaTeX/BibTeX build and render the affected page for visual verification.

## Decision (ADR-lite)

**Context**: Table 2 in the English PDF extends to the right page edge and clips its final column.

**Decision**: Remove the final column as requested instead of shrinking the whole table or changing unrelated layout settings.

**Consequences**: Table 2 becomes narrower and readable; intended evaluation roles are no longer tabulated there and remain outside this table's scope.

## Out of Scope

* Changes to the Chinese manuscript or its independently numbered tables.
* Changes to Table 3, other manuscript tables, profile definitions in code, or experimental claims.
* Global font, margin, or page-layout changes.

## Technical Notes

* The affected table is paper/main.tex around lines 286--300 and is rendered as TABLE 2 in paper/main.pdf.
* A pre-edit render of page 7 confirmed that the table line and rightmost content reach beyond the page boundary.
* The relevant build guidance is .trellis/spec/guides/latex-paper-build-thinking-guide.md.
