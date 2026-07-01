# GPT-Image prompt for Figure 2

Use case: scientific-educational

Asset type: publication-ready Figure 2 method schematic for an IEEE Access paper, wide landscape figure spanning two columns

Input images: Image 1 is a content-and-pattern reference only. Redraw its idea of a readable source, readable human integration, and sparse random camera subframes; do not copy its black background or tiny header text.

Primary request: Create a clean, rigorous scientific schematic explaining a temporal pixel-masking privacy display. The visual logic must read left to right, then split into two observer outcomes.

Composition/framing: very wide landscape canvas, approximately 2.5:1. White background, generous margins, three coherent stages connected by clear arrows.

Stage 1 — source and secure decomposition:

- A small clean display thumbnail containing the exact sample text "PRIVATE DATA" and label "Input frame I".
- Arrow into a compact security module labeled exactly "ChaCha20 CSPRNG" and "Fisher–Yates".
- Show four small complementary random binary mask tiles labeled collectively "Complementary masks M₁…Mₙ" with formula "Σ Mₖ = 1".

Stage 2 — GPU synthesis and temporal sequence:

- A central module labeled "GPU subframe synthesis" with formula "Iₖ = I ⊙ Mₖ + Nₖ".
- Feed into it a secondary small module labeled "Complementary adversarial noise" with formula "Σ Nₖ = 0".
- Include a dashed optional enhancement tag labeled exactly "Optional: anti-OCR / inversion".
- Output a horizontal row of four sparse, fragmented subframe thumbnails, each showing different random pieces of the source, with a time arrow beneath them.
- Label the row "High-refresh display" and "240–360 Hz".

Stage 3 — observer asymmetry, shown as a clean fork:

- Upper green branch: simple eye icon, label "Human visual system", a subtle temporal accumulation symbol across all subframes, label "Temporal integration ≈ 50 ms", ending in a fully readable display thumbnail containing "PRIVATE DATA" and label "Readable reconstruction".
- Lower orange-red branch: simple camera icon with one narrow shutter-window bracket selecting only one subframe, label "Camera / machine vision", label "Short-exposure sampling", ending in a sparse fragmented thumbnail with an OCR icon crossed out and label "Unreadable fragment".

Style/medium: flat vector-like scientific infographic, crisp geometry, restrained IEEE journal aesthetic, consistent sans-serif typography, thin dark-navy outlines, simple icons, strong visual hierarchy. Use navy for the main pipeline, cyan for masks, magenta only for adversarial noise, green for the human-readable branch, orange-red for the camera-unreadable branch.

Text constraints: Render every quoted label and formula verbatim, exactly once where specified. Use large legible text suitable for reduction in a two-column paper. Mathematical subscripts should appear correctly. No title inside the figure because the LaTeX caption will provide it.

Scientific constraints: Make it visually clear that masks are complementary and mutually exclusive; different subframes contain different pixel subsets; human integration accumulates the full sequence; the camera samples only one short exposure. Do not imply that adversarial noise is the primary defense: show it as a smaller secondary input. Optional enhancements must be dashed and visually subordinate.

Avoid: photorealism, 3D, gradients, drop shadows, glossy UI, dark background, dense paragraphs, decorative circuitry, fake numerical results, logos, watermark, caption, citations, extra labels, spelling errors, illegible tiny text.

Reference image: `privacy-display/experiments/results/demo_n4_grid.png` (content and pattern reference only).
