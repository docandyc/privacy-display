# Revise Figure 1 per supervisor feedback

## Goal

Revise the editable Visio version of Figure 1 so the right-hand panel directly shows how four complementary temporal subframes form one readable glyph for the human observer while a short-exposure camera receives only the selected partial glyph. Preserve the left-hand threat-scene panel unchanged.

## Requirements

* Use `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.vsdx` as the canonical editable deliverable and retain the existing scene-to-Visio workflow.
* Keep panel (a), its labels, geometry, colors, and capture rays unchanged.
* Keep the existing two-panel composition and the human-above/camera-below structure in panel (b).
* Remove both visible `Fast time` text labels completely.
* Replace the four arbitrary sparse patterns with four mutually exclusive pixel subsets of one 5-by-5 capital `A`; their union must exactly form the complete `A`.
* Preserve four separate subframe displays. Use the existing orange-red bracket to select the second subframe.
* Replace the readable output's `PRIVATE DATA` text with the complete 5-by-5 capital `A` produced by the union of all four subframes.
* Make the camera fragment reproduce exactly the selected second subframe's active pixels.
* Replace the obstructed long time arrow with an unambiguous, unobstructed rightward sequence cue between the four subframes, without adding a replacement `Fast time` label.
* Retain the green human integration path and orange-red short-exposure camera path, adjusting anchors only as needed to avoid covering the new sequence cue.
* Replace the small `OCR ×` mark with a clearly legible `OCR` symbol overlaid by a large red X, as explicitly requested by the supervisor.
* Retain `Short-exposure sampling`, `Temporal integration`, `Rapid complementary subframes`, `Readable`, `Camera`, and `Unreadable fragment` unless local spacing requires a line-break-only adjustment.
* Keep the figure fully editable; do not rasterize either panel or paste the entire reference image.
* Synchronize the final VSDX and PDF to the matching English and Chinese paper paths.

## Acceptance Criteria

* [ ] Panel (a) is visually unchanged at publication size.
* [ ] `Fast time` is absent from the scene, VSDX, SVG/PNG previews, and final PDF.
* [ ] The four subframe grids are mutually exclusive and their union is exactly one recognizable capital `A`.
* [ ] The human output shows the same complete `A`.
* [ ] The camera output uses the exact pixel set from the bracketed second subframe.
* [ ] The temporal order cue points right and is not crossed, hidden, or visually broken by other connectors.
* [ ] The OCR result contains a prominent red X that remains obvious at 3.50-inch publication width.
* [ ] No labels overlap, wrap unexpectedly, or fall below the established 6.5 pt minimum.
* [ ] Scene validation, complexity review, and module audit pass without blocking defects.
* [ ] Editable VSDX plus SVG/PNG review outputs and a single-page PDF are generated successfully.
* [ ] English and Chinese final VSDX/PDF mirrors are byte-identical.
* [ ] Both manuscripts build successfully and Figure 1 is visually inspected in the compiled pages.

## Definition of Done

* The canonical scene generator, scene JSON, editable Visio file, and exported paper assets reflect the approved design.
* Two visual review passes cover the whole figure plus targeted subframe/OCR regions.
* Existing unrelated working-tree changes remain untouched.
* Relevant build and validation commands pass.

## Technical Approach

Update the existing `build_round2_scene.py` source-of-truth generator and regenerate the scene JSON. Use `grid_matrix` nodes for a 5-by-5 glyph decomposition, short axis-aligned sequence arrows for temporal order, and two thick red diagonal `line_segment` strokes over the OCR node. Render through the existing Visiomaster/Visio COM pipeline into a staging directory, review at 1050-by-700 pixels, then promote and mirror validated artifacts.

## Decision (ADR-lite)

**Context:** The current replica is editable and stylistically consistent, but its arbitrary sparse blocks do not visibly map to the readable output, the time arrow is obstructed, and the OCR failure mark is too small.

**Decision:** Perform a targeted semantic rebuild of panel (b) while preserving panel (a). Use a capital `A`, select subframe 2, remove `Fast time`, replace the long time arrow with local rightward sequence arrows, and use a large red X over `OCR`.

**Consequences:** The revised figure prioritizes immediate conceptual clarity and follows the supervisor's requested visual semantics. The prominent OCR X is intentionally retained as a schematic symbol because the user explicitly chose the supervisor's presentation choice.

## Out of Scope

* Replacing the left panel with an AI-generated image or changing its illustration style.
* Revising Figure 1 captions or surrounding manuscript prose unless a build failure requires a path-only correction.
* Changing Figure 2 or other paper figures.
* Altering experimental claims, metrics, or method implementation.

## Technical Notes

* Prior design: `docs/superpowers/specs/2026-07-02-figure-1-visio-design.md`.
* Canonical scene generator: `paper/figures/visio/figure1_concept_threat/build_round2_scene.py`.
* Canonical editable output: `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.vsdx`.
* Existing untracked Visio lock/temp file and `paper/review_report.md` predate this task and must not be removed or committed.

