# Figure 1 Supervisor Revision Design

## Scope

This revision changes only panel (b) of Figure 1. Panel (a), the two-panel page composition, the color system, and the human-above/camera-below branch structure remain unchanged.

## Considered approaches

1. **Targeted scene rebuild (selected):** update the existing scene generator, regenerate editable Visio shapes, and export fresh assets. This preserves editability and keeps panel (a) stable.
2. **Direct VSDX patching:** edit shapes inside the current VSDX through COM. This is fast for labels but fragile for the pixel decomposition and cannot reliably regenerate the scene source.
3. **Raster overlay:** replace the right panel with an image. This is rejected because it breaks editability and the Visiomaster contract.

## Approved visual design

The four displays in panel (b) show mutually exclusive portions of a single 5-by-5 capital `A`. Each active glyph pixel appears in exactly one subframe. The green human path combines all four and ends at a display containing the complete `A`. The orange-red bracket continues to select the second subframe; the camera output repeats that exact partial-pixel pattern.

The words `Fast time` are removed. Temporal order is encoded with clean rightward arrow cues placed between the four displays so no green fan-in or orange-red camera connector crosses the arrowheads.

The existing small `OCR ×` symbol becomes an `OCR` node covered by a large, thick red X. This deliberately follows the supervisor's requested visual convention.

## Glyph contract

The complete `A` uses these 5-by-5 active cells, with zero-based row/column indices:

* Row 0: columns 1, 2, 3
* Row 1: columns 0, 4
* Row 2: columns 0, 1, 2, 3, 4
* Row 3: columns 0, 4
* Row 4: columns 0, 4

The partition is:

* Subframe 1: `(0,1)`, `(1,4)`, `(2,2)`, `(4,0)`
* Subframe 2: `(0,2)`, `(1,0)`, `(2,3)`, `(3,4)`
* Subframe 3: `(0,3)`, `(2,0)`, `(2,4)`
* Subframe 4: `(2,1)`, `(3,0)`, `(4,4)`

The camera fragment must use the Subframe 2 set verbatim. The readable display uses the union of all four sets.

## Publication and export constraints

* Final figure remains 3.50 by 2.333 inches and is reviewed at 1050 by 700 pixels.
* Arial typography and the existing navy/green/orange-red palette remain unchanged.
* No visible label may fall below 6.5 pt.
* Deliverables remain editable VSDX plus SVG, PNG, and vector PDF.
* English and Chinese final asset mirrors must remain byte-identical.

## Verification

Validation checks the scene schema, grid partition invariants, selected-frame/camera identity, absence of `Fast time`, unobstructed sequence arrows, and presence of two red diagonal OCR-cross strokes. Visual review checks the full figure and targeted crops for the subframe row, human output, camera fragment, OCR mark, small text, and connector crossings.
