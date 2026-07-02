# Figure 1 Visio Redraw Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an editable, IEEE Access-ready Visio reconstruction of paper Figure 1.

**Architecture:** Stage the source image, author a source-pixel semantic scene with explicit regions and arrows, render through Microsoft Visio, and use strict visual review gates before vector/raster publication export. Keep all new artifacts isolated under `paper/figures/visio/figure1_concept_threat/`.

**Tech Stack:** Python 3.10, Visiomaster scene tools, pywin32, Microsoft Visio COM, Poppler, Pillow/pypdf.

---

### Task 1: Stage and inventory the source

**Files:**
- Create: `paper/figures/visio/figure1_concept_threat/source/original.png`
- Create: `paper/figures/visio/figure1_concept_threat/source/source_manifest.json`

- [ ] Stage `paper/figures/concept_threat.png` with `stage_source_image.py`.
- [ ] Record the 1536 x 1024 aspect ratio, two-panel regions, required labels, motifs, and typography.
- [ ] Record each visible capture ray and flow arrow as an independent arrow-plan item.

### Task 2: Author the first complete scene

**Files:**
- Create: `paper/figures/visio/figure1_concept_threat/figure1_concept_threat.scene.json`
- Create: `paper/figures/visio/figure1_concept_threat/build_round1_scene.py`

- [ ] Build both panels entirely from editable Visio primitives.
- [ ] Use source-pixel coordinates and a 3.50-inch target width.
- [ ] Use explicit regions for the physical scene, subframe row, human outcome, and camera outcome.
- [ ] Run strict validation, complexity analysis, font inventory, and rebuild audit.

### Task 3: Render and review round one

**Files:**
- Create: `paper/figures/visio/figure1_concept_threat/round1/*`
- Create: `paper/figures/visio/figure1_concept_threat/review/round1/*`

- [ ] Render VSDX/SVG/PNG through Visio.
- [ ] Inspect the full source and replica plus targeted panel/text crops.
- [ ] Write topology and visual-layout checklists.
- [ ] Run the checklist gate and generate a rebuild brief/regeneration packet if any item fails.

### Task 4: Reauthor and render the publication scene

**Files:**
- Create: `paper/figures/visio/figure1_concept_threat/figure1_concept_threat.round2.scene.json`
- Create: `paper/figures/visio/figure1_concept_threat/final/*`

- [ ] Reauthor the full scene from the source inventory and round-one findings.
- [ ] Render through Visio and apply correct ShapeSheet text margins.
- [ ] Visually inspect all labels, capture rays, four human integration arrows, the sampling bracket, and both outcomes.
- [ ] Run the no-op gate and final structured review.

### Task 5: Export and verify publication artifacts

**Files:**
- Create: `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.vsdx`
- Create: `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.svg`
- Create: `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.pdf`
- Create: `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.png`
- Create: `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.scene.json`

- [ ] Export a one-page vector PDF through Visio.
- [ ] Rasterize the PDF at 300 dpi to 1050 x 700 pixels.
- [ ] Verify PDF page size, PNG DPI, SVG XML, VSDX ZIP structure, scene node/edge counts, and source-file preservation.

