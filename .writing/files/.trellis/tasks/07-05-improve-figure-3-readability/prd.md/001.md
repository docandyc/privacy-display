# Improve Figure 3 Readability in the Two-Column Paper

## Goal

Make Figure 3 legible at IEEE Access single-column width. The current 3 x 3 montage is generated at approximately 6.4 inches wide and then reduced to a 3.5-inch column, which makes its labels and image text too small.

## Requirements

* Reflow the same nine qualitative panels into three vertically stacked profile groups: Unprotected, Deployed, and Capture-hardened.
* Within each profile group, show Human-eye view, Short exposure, and Long exposure vertically in that order.
* Generate the figure natively at single-column width so labels are not reduced by LaTeX.
* Preserve the existing source image, real-capture files, crop, and per-mode gain settings; this task changes presentation only.
* Keep the English paper caption scientifically accurate and consistent with the new vertical ordering.
* Do not modify the Chinese paper or unrelated manuscript content.

## Acceptance Criteria

* [x] All nine panels are present and correctly grouped.
* [x] Profile and exposure labels are readable in the rendered IEEE Access PDF at normal page scale.
* [x] The figure fits within one column without clipping, overlap, or an excessive blank region.
* [x] The caption describes top-to-bottom ordering rather than left/center/right columns.
* [x] The paper compiles without new LaTeX errors or missing references.
* [x] A rendered page inspection confirms that Figure 3 is materially larger and clearer than the previous layout.

## Definition of Done

* Figure generator, generated PDF, and Figure 3 caption are updated.
* The generator runs successfully and the English paper recompiles.
* The standalone figure and containing manuscript page are rendered to PNG and visually checked.

## Technical Approach

Change `fig_f3_montage.py` from a 3-row x 3-column grid to a 9-row x 1-column grid. Use `figstyle.COL_W` as the native figure width, reserve explicit vertical space for group headings, and label each panel by exposure mode. Regenerate `paper/figures/real_capture_montage.pdf`, then update only the corresponding caption in `paper/main.tex`.

## Decision (ADR-lite)

**Context**: The capture crops are very wide horizontal strips. In the current grid, each strip receives only one third of the column width after the entire figure is scaled down.

**Decision**: Use a single-column vertical sequence grouped by protection profile.

**Consequences**: Each strip becomes roughly three times wider in the manuscript, substantially improving the visibility of embedded text. The figure becomes taller, but the strips' shallow aspect ratio keeps the total height practical for a single column.

## Out of Scope

* Changing experimental data, capture selection, image enhancement, crop bounds, or gain values.
* Revising other figures or the Chinese manuscript.
* Rewriting unrelated English-paper content already modified in the working tree.

## Technical Notes

* Current generator: `privacy-display/experiments/paper_figures/fig_f3_montage.py`.
* Current generated PDF size: 462.057 x 157.667 pt; it is included at `\\columnwidth`, causing approximately 55% downscaling.
* Before the change, Figure 3 appeared on page 8 of the 19-page English manuscript. The verified vertical layout appears on page 9 of the rebuilt 20-page manuscript.
* Existing uncommitted edits in `paper/main.tex` belong to the user and must be preserved.
