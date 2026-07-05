# Figure 2 Visio Redraw Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a publication-ready, editable Visio redraw of paper Figure 2 using the approved three-stage IEEE Access layout.

**Architecture:** A source-bound `scene.json` is the single semantic source of truth. Visiomaster validates and renders it through Visio COM to `.vsdx`, `.svg`, and `.png`; a Visio fixed-format export produces `.pdf`. Two source-versus-render review rounds verify topology, typography, spacing, and grayscale-safe branch encoding.

**Tech Stack:** Microsoft Visio COM, Python 3.10 with `pywin32`, Visiomaster scene schema and review scripts, PowerShell, SVG/PDF/PNG exports.

---

## File structure

- Create: `paper/figures/visio/figure2_method_pipeline/source/original.png` — canonical staged source.
- Create: `paper/figures/visio/figure2_method_pipeline/source/source_manifest.json` — source hash and provenance.
- Create: `paper/figures/visio/figure2_method_pipeline/figure2_method_pipeline.scene.json` — final semantic scene.
- Create: `paper/figures/visio/figure2_method_pipeline/round1/` — first Visio render and review evidence.
- Create: `paper/figures/visio/figure2_method_pipeline/review/round1/` — first review manifest, findings, gate, repair brief, and regeneration packet.
- Create: `paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.vsdx` — editable Visio source.
- Create: `paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.svg` — vector manuscript asset.
- Create: `paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.pdf` — vector IEEE submission asset.
- Create: `paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.png` — high-resolution preview.
- Create: `paper/figures/visio/figure2_method_pipeline/review/round2/` — final comparison and no-op proof.
- Do not modify: `paper/main.tex` or `paper/figures/method_pipeline.png`.

### Task 1: Stage the source and verify the Visio environment

**Files:**
- Create: `paper/figures/visio/figure2_method_pipeline/source/original.png`
- Create: `paper/figures/visio/figure2_method_pipeline/source/source_manifest.json`

- [ ] **Step 1: Stage the canonical source image**

Run from `E:\毕设\privacy-display`:

```powershell
$env:PYTHONPATH = (Resolve-Path '.\privacy-display\.venv\Lib\site-packages').Path
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\stage_source_image.py' `
  --input 'paper\figures\method_pipeline.png' `
  --workspace 'paper\figures\visio\figure2_method_pipeline' `
  --id 'figure2_method_pipeline'
```

Expected: `original.png` is 1983 × 793 pixels and the manifest contains its SHA-256 hash.

- [ ] **Step 2: Verify Visio COM and pywin32**

```powershell
$env:PYTHONPATH = (Resolve-Path '.\privacy-display\.venv\Lib\site-packages').Path
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\check_visio_env.py' `
  --output-dir 'paper\figures\visio\figure2_method_pipeline\env_check'
```

Expected: Python, `win32com`, and Microsoft Visio are reported available.

- [ ] **Step 3: Verify publication fonts**

```powershell
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\font_inventory.py' `
  --check 'Arial' --check 'Cambria Math' --check 'Times New Roman'
```

Expected: Arial and Cambria Math resolve locally; Times New Roman is available as a fallback.

### Task 2: Author the source-bound scene

**Files:**
- Create: `paper/figures/visio/figure2_method_pipeline/figure2_method_pipeline.scene.json`

- [ ] **Step 1: Define the scene contract**

Author a pixel-coordinate scene with this page contract:

```json
{
  "version": "0.1",
  "metadata": {
    "title": "Temporal pixel-masking privacy display pipeline",
    "created_by": "codex.visiomaster",
    "style_profile": "paper_white",
    "fidelity": "exact",
    "replica_review_mode": "strict_replica",
    "replica_stage": "layout_topology",
    "source_image": "E:/毕设/privacy-display/paper/figures/visio/figure2_method_pipeline/source/original.png",
    "source_aspect_ratio": 2.5006305,
    "region_strategy": "region_first",
    "font_scale": {"frame_title": 10, "body": 9.5, "small_label": 8.5, "operator": 10, "formula": 10}
  },
  "page": {
    "width": 1983,
    "height": 793,
    "units": "px",
    "origin": "top-left",
    "target_width_in": 7.16,
    "background": "#FFFFFF"
  },
  "nodes": [],
  "edges": [],
  "assets": []
}
```

Add `source_visual_inventory`, `region_plan`, and `arrow_plan` before adding nodes or edges.

- [ ] **Step 2: Inventory regions and visible text**

Define these source-bound regions:

```text
stage_1: Source and secure decomposition
stage_2: GPU synthesis and temporal sequence
stage_3: Observer asymmetry
stage_3_human: green upper outcome
stage_3_camera: orange-red lower outcome
arrow_dense: subframe row and observer fork
small_text: formulas, timing labels, and output labels
```

Record every visible approved label exactly as written in the design specification. Mark formulas as math and keep `PRIVATE DATA`, `240–360 Hz`, `≈ 50 ms`, `Σ Mₖ = 1`, `Iₖ = I ⊙ Mₖ + Nₖ`, and `Σ Nₖ = 0` on one line.

- [ ] **Step 3: Inventory all flow arrows**

Create one `arrow_plan` entry per visible connector:

```text
A001 input_frame -> security_module
A002 security_module -> mask_stack
A003 mask_stack -> gpu_synthesis
A004 optional_enhancement -> gpu_synthesis
A005 adversarial_noise -> gpu_synthesis
A006 gpu_synthesis -> subframe_1
A007 subframe_1 -> subframe_2
A008 subframe_2 -> subframe_3
A009 subframe_3 -> subframe_4
A010 subframe_4 -> observer_fork
A011 observer_fork -> human_panel
A012 human_panel -> readable_output
A013 observer_fork -> camera_panel
A014 camera_panel -> sampled_fragment
A015 sampled_fragment -> ocr_failure
```

Use straight horizontal routes for A001–A010 and A012/A014/A015. Use orthogonal fork routes for A011/A013. A013 must be dashed as well as orange-red.

- [ ] **Step 4: Build editable nodes**

Use these semantic components:

```text
page_background: canvas preservation
group_container: stage_1, stage_2, stage_3
process_box / rounded_process: input, security, GPU, output panels
grid_matrix or token_grid: complementary masks and sparse subframes
math_text: three equations
text_block: stage titles, labels, timing labels
junction_point: observer_fork
bracket or line_segment: short-exposure sampling window
```

Apply the approved palette: navy `#17365D`, cyan `#159FCF`, magenta `#A50064`, green `#177A36`, orange-red `#D94722`, and frame gray-blue `#B7C5D8`.

- [ ] **Step 5: Bind and route edges**

Every edge must carry its `arrow_plan_id`. Use `lane_arrow` for straight lanes, `rounded_orthogonal_connector` for the fork, and explicit points so no route crosses text or a non-endpoint node.

### Task 3: Validate the first scene before Visio rendering

**Files:**
- Modify: `paper/figures/visio/figure2_method_pipeline/figure2_method_pipeline.scene.json`

- [ ] **Step 1: Run strict schema validation**

```powershell
$env:PYTHONPATH = (Resolve-Path '.\privacy-display\.venv\Lib\site-packages').Path
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\scene_validate.py' `
  'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json' --strict
```

Expected: exit code 0 with no missing arrow bindings, no diagonal drift, and no source-contract errors.

- [ ] **Step 2: Run complexity and module audits**

```powershell
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\scene_complexity.py' `
  'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json'

& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\scene_audit.py' `
  'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json' --fail-on-rebuild
```

Expected: no `[REBUILD]` items, no uncovered semantic nodes, no route-through-text findings, and no typography mismatch.

### Task 4: Render and review round 1

**Files:**
- Create: `paper/figures/visio/figure2_method_pipeline/round1/*`
- Create: `paper/figures/visio/figure2_method_pipeline/review/round1/*`

- [ ] **Step 1: Render the first Visio export**

```powershell
$env:PYTHONPATH = (Resolve-Path '.\privacy-display\.venv\Lib\site-packages').Path
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\scene_to_visio.py' `
  'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json' `
  --output-dir 'paper\figures\visio\figure2_method_pipeline\round1' `
  --style-profile paper_white
```

Expected: `.vsdx`, `.svg`, and `.png` exist and are non-empty.

- [ ] **Step 2: Package review evidence**

```powershell
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\make_review_assets.py' `
  --original 'paper\figures\visio\figure2_method_pipeline\source\original.png' `
  --replica 'paper\figures\visio\figure2_method_pipeline\round1\figure2_method_pipeline.png' `
  --scene 'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json' `
  --output-dir 'paper\figures\visio\figure2_method_pipeline\review\round1' `
  --id 'figure2_method_pipeline' --round 1 `
  --write-review-bundle --crops arrow_dense small_text
```

Expected: `review_manifest.json` and reviewer templates reference the canonical source and round-1 replica.

Copy the round-1 scene before any repair:

```powershell
Copy-Item `
  'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json' `
  'paper\figures\visio\figure2_method_pipeline\round1\prior.scene.json'
```

- [ ] **Step 3: Record visual findings**

Create `review_findings.json` with:

```json
{
  "topology_checklist": [],
  "visual_checklist": [],
  "findings": []
}
```

Populate one topology item for each A001–A015 arrow and visual items for stage bounds, 9–10 pt text, formulas, subframe sparsity, sampling window, grayscale distinction, and final-size legibility. Every failed finding must cite `checklist_refs`.

- [ ] **Step 4: Gate and convert findings into a rebuild brief**

```powershell
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\review_checklist_gate.py' `
  'paper\figures\visio\figure2_method_pipeline\review\round1\review_findings.json' `
  --manifest 'paper\figures\visio\figure2_method_pipeline\review\round1\review_manifest.json' `
  --require-failed-refs `
  --output-report 'paper\figures\visio\figure2_method_pipeline\review\round1\review_checklist_gate.json'

& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\review_findings_to_repair_plan.py' `
  'paper\figures\visio\figure2_method_pipeline\review\round1\review_findings.json' `
  --scene 'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json' `
  --manifest 'paper\figures\visio\figure2_method_pipeline\review\round1\review_manifest.json' `
  --require-checklists `
  --output 'paper\figures\visio\figure2_method_pipeline\review\round1\scene_rebuild_brief.json'
```

Expected: both commands exit 0 and the brief names each failed region or edge.

Prepare the mandatory regeneration packet:

```powershell
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\prepare_regeneration_packet.py' `
  'paper\figures\visio\figure2_method_pipeline\review\round1\scene_rebuild_brief.json' `
  --output-dir 'paper\figures\visio\figure2_method_pipeline\review\round1\regeneration_packet'
```

Expected: the packet contains the source path, replica path, rebuild brief, and a round-specific regeneration prompt.

### Task 5: Reauthor and render the final round

**Files:**
- Modify: `paper/figures/visio/figure2_method_pipeline/figure2_method_pipeline.scene.json`
- Create: `paper/figures/visio/figure2_method_pipeline/final/*`
- Create: `paper/figures/visio/figure2_method_pipeline/review/round2/*`

- [ ] **Step 1: Reauthor failed subsystems**

Apply fixes in this order: component choice, topology and anchors, formula typography, container proportions, then style polish. If a region is structurally wrong, rebuild that subsystem from the source inventory instead of nudging the prior coordinates.

- [ ] **Step 2: Re-run strict validation and render final outputs**

Run the Task 3 validation/audit commands again, then:

```powershell
$env:PYTHONPATH = (Resolve-Path '.\privacy-display\.venv\Lib\site-packages').Path
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\scene_to_visio.py' `
  'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json' `
  --output-dir 'paper\figures\visio\figure2_method_pipeline\final' `
  --style-profile paper_white
```

Expected: final `.vsdx`, `.svg`, and `.png` exist and differ visibly from round 1 when round-1 findings required repairs.

- [ ] **Step 3: Prove the round is non-no-op**

```powershell
& 'C:\Users\黄哲远\AppData\Local\Programs\Python\Python310\python.exe' `
  'C:\Users\黄哲远\.codex\skills\visiomaster\scripts\round_noop_gate.py' `
  --before-scene 'paper\figures\visio\figure2_method_pipeline\round1\prior.scene.json' `
  --after-scene 'paper\figures\visio\figure2_method_pipeline\figure2_method_pipeline.scene.json' `
  --before-png 'paper\figures\visio\figure2_method_pipeline\round1\figure2_method_pipeline.png' `
  --after-png 'paper\figures\visio\figure2_method_pipeline\final\figure2_method_pipeline.png' `
  --rebuild-brief 'paper\figures\visio\figure2_method_pipeline\review\round1\scene_rebuild_brief.json' `
  --output-report 'paper\figures\visio\figure2_method_pipeline\review\round2\round_noop_gate.json'
```

Expected: the report confirms renderer-effective scene changes and a non-zero pixel diff.

- [ ] **Step 4: Repeat the review checklist for round 2**

Package round-2 assets and record all A001–A015 topology items plus the visual checklist. Expected: all required items pass; uncertain items are allowed only when they do not affect topology or publication readability.

### Task 6: Export PDF and run delivery checks

**Files:**
- Create: `paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.pdf`

- [ ] **Step 1: Export PDF through Visio fixed-format output**

Open the final `.vsdx` through Visio COM and call `ExportAsFixedFormat` with PDF format (`1`), print intent (`1`), and all foreground pages (`0`):

```powershell
$vsdx = (Resolve-Path 'paper\figures\visio\figure2_method_pipeline\final\figure2_method_pipeline.vsdx').Path
$pdf = Join-Path (Split-Path $vsdx) 'figure2_method_pipeline.pdf'
$visio = New-Object -ComObject Visio.Application
$visio.Visible = $false
try {
  $doc = $visio.Documents.Open($vsdx)
  $doc.ExportAsFixedFormat(1, $pdf, 1, 0)
  $doc.Close()
} finally {
  $visio.Quit()
}
```

Expected: `figure2_method_pipeline.pdf` exists, is non-empty, and contains one page.

- [ ] **Step 2: Verify deliverable dimensions and integrity**

Check:

```text
VSDX opens in Visio and primary objects are editable.
SVG has a 7.16 in-equivalent viewBox and no clipped labels.
PDF contains one vector page with embedded or outlined fonts.
PNG preserves the 1983:793 aspect ratio and is at least 300 dpi at 7.16 in width.
All labels remain readable at 100% manuscript size.
Human and camera outcomes remain distinct in grayscale.
paper/main.tex is unchanged.
```

- [ ] **Step 3: Prepare the final commit plan without committing**

List only files created by this task. Present one proposed artifact commit and keep unrelated dirty files excluded. Wait for explicit user confirmation before staging or committing.

---

## Plan self-review

- Spec coverage: canvas, editable Visio construction, exact labels, formulas, palette, grayscale redundancy, all deliverables, and two review rounds are covered.
- Placeholder scan: no `TBD`, `TODO`, or unspecified test steps remain.
- Type consistency: scene node/edge families and Visiomaster script names match the selected skill references.
- Scope: the manuscript source and existing Figure 2 asset remain untouched.
