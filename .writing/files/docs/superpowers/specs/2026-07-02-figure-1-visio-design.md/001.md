# Figure 1 Visio Redraw Design

## Goal

Rebuild `paper/figures/concept_threat.png` as an editable Microsoft Visio figure suitable for an IEEE Access single-column figure, while preserving the source's scientific meaning and two-panel visual hierarchy.

## Recommended direction

Use an editorial vector reconstruction rather than tracing every decorative office line. Three approaches were considered:

1. Exact decorative tracing: closest to the generated image, but too dense at 3.5-inch width.
2. Editorial vector reconstruction (selected): preserves every scientific object, label, branch, and sampling relation while simplifying furniture details.
3. Fully abstract block diagram: easiest to read, but loses the physical visual-eavesdropping scene.

The selected approach balances source fidelity, editability, and final-size legibility.

## Canvas and publication constraints

- Source coordinate system: 1536 x 1024 px, 3:2 aspect ratio.
- Final page: 3.50 x 2.333 inches, matching IEEE Access single-column width.
- Primary font: Arial; mathematical symbols: Cambria Math.
- Panel headings: 8.0-8.5 pt.
- Body labels: 6.5-7.5 pt; no label below 6.5 pt.
- Main strokes: 1.0-1.35 pt.
- No gradients, shadows, photographic tiles, decorative logos, or rasterized full-page background.
- Final outputs: editable VSDX, SVG, single-page vector PDF, 300 dpi PNG, and source scene JSON.

## Layout

### Panel (a): Physical visual eavesdropping

- Occupies the left 46% of the page.
- Contains an authorized user silhouette, chair, desk, monitor, keyboard, small office cues, and one unauthorized smartphone.
- The monitor contains `PRIVATE DATA`.
- Two orange-red dashed sight rays form a narrow capture cone from the display toward the smartphone.
- Required labels remain: `Authorized user`, `Sensitive display`, and `Smartphone camera`.
- Furniture is simplified to clean line-art primitives and carries no topology.

### Panel (b): Asymmetric perception

- Occupies the right 54% of the page.
- Four sparse complementary display thumbnails share one time row.
- A navy right-pointing time arrow is labeled `Fast time`.
- Four green arrows feed the eye, showing temporal integration across the sequence.
- A green arrow connects the eye to a readable output containing `PRIVATE DATA`.
- A narrow orange-red bracket selects exactly one subframe.
- The selected frame feeds a camera, then a sparse fragment, then `OCR ×`.
- Human and camera outcomes are distinguishable by color, solid/dashed grammar, icons, labels, and topology.

## Color system

- Navy: `#17365D` for neutral structure and time.
- Cyan/light blue: `#DFF3FA` and `#159FCF` for displays and sparse pixels.
- Green: `#177A36` for the human integration path.
- Orange-red: `#D94722` for unauthorized capture and camera sampling.
- White/off-white background with pale panel fills only where needed.

## Review and acceptance

- Source image is staged and hash-locked.
- Scene contains a source visual inventory, region plan, and one arrow-plan item per visible arrow or ray.
- Strict scene validation and audit pass before rendering.
- Round one locks composition and topology; round two fixes text and detail using a fresh full scene when required.
- Final review must pass all topology and visual checklist items.
- Final PDF is one page at 3.50 x 2.333 inches.
- Final PNG is 1050 x 700 pixels at 300 dpi.
- `paper/main.tex` and `paper/figures/concept_threat.png` remain unchanged.

