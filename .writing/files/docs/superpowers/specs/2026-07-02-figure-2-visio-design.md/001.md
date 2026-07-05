# Figure 2 Visio Redraw Design

## Goal

Redraw `paper/figures/method_pipeline.png` as a fully editable Microsoft Visio figure suitable for an IEEE Access two-column manuscript. Preserve the scientific argument while improving hierarchy, typography, grayscale readability, and reduction performance.

## Approved direction

Use the approved **three-stage journal layout (Option B)**:

1. **Source and secure decomposition**
2. **GPU synthesis and temporal sequence**
3. **Observer asymmetry**

The figure reads left to right, then forks into a human-observer outcome and a camera-observer outcome.

## Canvas and publication constraints

- Final width: **7.16 in** (IEEE two-column width).
- Target height: **2.86 in**, preserving the source figure's 2.5006:1 aspect ratio and excluding the LaTeX caption.
- White background; no gradients, glossy effects, decorative circuitry, logos, citations, or embedded caption.
- Vector-first delivery: editable `.vsdx` plus `.svg` and `.pdf`.
- Raster preview: `.png` exported at publication-quality resolution.
- Figure type should remain legible at final manuscript size.

IEEE references:

- Graphics size and resolution: <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/>
- File formats and fonts: <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/>
- Accessible use of color: <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/>

## Information architecture

### Stage 1 — Source and secure decomposition

- Input display containing `PRIVATE DATA`.
- Label: `Input frame I`.
- Security module with `ChaCha20 CSPRNG` and `Fisher–Yates`.
- Three or four editable complementary mask tiles.
- Collective label: `Complementary masks M₁…Mₙ`.
- Formula: `Σ Mₖ = 1`.

### Stage 2 — GPU synthesis and temporal sequence

- Central module: `GPU subframe synthesis`.
- Formula: `Iₖ = I ⊙ Mₖ + Nₖ`.
- Smaller secondary input: `Complementary adversarial noise`, with `Σ Nₖ = 0`.
- Dashed subordinate tag: `Optional: anti-OCR / inversion`.
- Four sparse fragmented subframes in a horizontal row.
- Labels: `High-refresh display · 240–360 Hz` and `time t`.

The noise module must not look like the primary mechanism. Complementary masks remain the dominant defense path.

### Stage 3 — Observer asymmetry

- A single fork node after the display sequence.
- Upper human branch:
  - Green solid route.
  - Label: `HUMAN VISUAL SYSTEM`.
  - Text: `Integrates all subframes (≈ 50 ms)`.
  - Readable `PRIVATE DATA` output.
  - Label: `Readable reconstruction`.
- Lower camera branch:
  - Orange-red dashed route.
  - Label: `CAMERA / MACHINE VISION`.
  - Four sparse frames with one explicit short-exposure sampling window.
  - Text: `Samples one short exposure`.
  - OCR failure mark and `Unreadable fragment`.

Color is not the only discriminator: the two branches also differ by line style, iconography, labels, and sampling-window geometry.

## Visual system

- Main pipeline: dark navy `#17365D`.
- Complementary masks: cyan `#159FCF`.
- Optional adversarial noise: magenta `#A50064`.
- Human branch: green `#177A36`, solid.
- Camera branch: orange-red `#D94722`, dashed.
- Region frames: light blue-gray `#B7C5D8` with near-white fills.
- Text: Arial, approximately 9–10 pt at final size.
- Mathematics: Cambria Math, approximately 9–10 pt at final size.
- Main outlines/connectors: 1.25–1.5 pt.
- Secondary details: at least 0.75 pt.
- Rounded corners are restrained and consistent; no drop shadows.

## Visio construction

- Use editable Visio primitives and semantic components for all primary content.
- Use source-pixel coordinates in `scene.json`, scaled to a 7.16 in target width.
- Use `group_container` for the three visible stage regions.
- Use `grid_matrix` or `token_grid` for mask/subframe patterns.
- Use `math_text` for equations and subscripts.
- Use explicit junctions and orthogonal routes for the observer fork.
- Use a dashed connector and sampling bracket/window for the camera branch.
- Do not paste the complete source image into Visio.

## Deliverables

- `paper/figures/visio/figure2_method_pipeline.scene.json`
- `paper/figures/visio/figure2_method_pipeline.vsdx`
- `paper/figures/visio/figure2_method_pipeline.svg`
- `paper/figures/visio/figure2_method_pipeline.pdf`
- `paper/figures/visio/figure2_method_pipeline.png`
- Strict review artifacts under `paper/figures/visio/review/`.

This task does not change the manuscript source to use the new figure.

## Verification

1. Validate the scene and arrow inventory.
2. Run typography and complexity preflights.
3. Render through Visio and verify `.vsdx`, `.svg`, and `.png` outputs.
4. Compare the source and replica at whole-figure and targeted-crop levels.
5. Verify all labels and formulas at final 7.16 in size.
6. Verify grayscale interpretation without relying on red/green alone.
7. Perform a second render/review round after fixing the first-round findings.
8. Export PDF from the vector output and confirm the page bounding box.

## Out of scope

- Changing the scientific claims or introducing new performance results.
- Rewriting the manuscript caption.
- Updating `paper/main.tex` to point to the new asset.
- Replacing the complete diagram with AI-generated raster artwork.
