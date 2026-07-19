# Research: Figure 1 asset/build/export/mirror pipeline

- Query: Identify the canonical Figure 1 source, scene, VSDX, PDF, render/export commands, English/Chinese synchronization path, existing drift, and governing Trellis contracts.
- Scope: internal
- Date: 2026-07-19

## Findings

### Executive conclusion

The authoritative working tree is the English `paper/` tree. The active Figure 1 maintenance chain is:

`paper/figures/concept_threat.png`
→ staged source + manifest
→ round-1 inventory/topology builder and scene
→ round-2 detail-polish builder and scene
→ canonical English `final/figure1_concept_threat.vsdx`
→ Visio COM PDF export
→ canonical English `final/figure1_concept_threat.pdf`
→ manual byte-for-byte copy of the final VSDX/PDF into the live `paper-Chinese/figures/.../final/` mirror.

The English final VSDX/PDF were explicitly designated canonical by the prior export task (`.trellis/tasks/07-05-export-revised-figure1/research/export-context.md:3-7`, `.trellis/tasks/07-05-export-revised-figure1/prd.md:9-18`). Both manuscripts include their local copy of the same PDF at the same relative path and with the same viewport (`paper/main.tex:84-89`, `paper-Chinese/main.tex:101-106`). The Chinese paper translates only the caption; the labels inside the diagram remain English.

### Authoritative files and roles

| Role | Path | Status / reason |
|---|---|---|
| Original raster input | `paper/figures/concept_threat.png` | Hash-locked source image; byte-identical to the staged copy. |
| Canonical staged source | `paper/figures/visio/figure1_concept_threat/source/original.png` | Manifest-backed visual-review source. SHA-256 `83c58eb205b505169f5b18708758344d9ec14a6bfce9e531c34ddf889a668be3`. |
| Source manifest | `paper/figures/visio/figure1_concept_threat/source/source_manifest.json` | Declares the English staged source canonical and records the same input/staged hash (`source_manifest.json:3-7`). |
| Round-1 builder | `paper/figures/visio/figure1_concept_threat/build_round1_scene.py` | Generates the source inventory/topology scene `figure1_concept_threat.scene.json` (`build_round1_scene.py:7-8,99-133,582-583`). It is still a dependency, not merely disposable history. |
| Round-1 inventory scene | `paper/figures/visio/figure1_concept_threat/figure1_concept_threat.scene.json` | Supplies `metadata.source_visual_inventory`, `region_plan`, and `arrow_plan` to round 2. Current English hash `0e09aecd3558cb39bbc9db380d412a8eadc5f3871ed27d8427931a2052e52826`. |
| Latest maintained builder | `paper/figures/visio/figure1_concept_threat/build_round2_scene.py` | Reads only the round-1 metadata, then reauthors all visible nodes (`build_round2_scene.py:15-20,54,233,283-284`). This is the builder to update for current visible content. |
| Latest maintained scene | `paper/figures/visio/figure1_concept_threat/figure1_concept_threat.round2.scene.json` | Current detail-polish source: 80 nodes, 11 edges, 1536×1024 px authoring coordinates, 3.5-in target width (`scene.json:729-735`). SHA-256 `f7218b17caa972cfa54bdc72fa524153f79aed4b3a8abbb553ce0dd9bc154c8c`. |
| Canonical editable deliverable | `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.vsdx` | The prior export task explicitly made this the revised source. Current SHA-256 `2b4b2b18651664b849a93c003fbba0ac51ad0a880e290f00b322fa3075a7b8ff`. Its page is A4, with all drawing content occupying the lower-left 3.5×2.333-in rectangle. |
| Canonical paper asset | `paper/figures/visio/figure1_concept_threat/final/figure1_concept_threat.pdf` | One A4 vector page, 48,133 bytes, SHA-256 `ec20d8126fb81e81861c43d72150b4180a93205dd1a39d091c7aa19fa112432f`; the manuscript clips the lower-left 252×168-pt drawing viewport. |
| Live Chinese VSDX mirror | `paper-Chinese/figures/visio/figure1_concept_threat/final/figure1_concept_threat.vsdx` | Intended byte-for-byte mirror, but currently stale; details below. |
| Live Chinese PDF mirror | `paper-Chinese/figures/visio/figure1_concept_threat/final/figure1_concept_threat.pdf` | Currently byte-identical to the English canonical PDF. |
| Manuscript consumers | `paper/main.tex`, `paper-Chinese/main.tex` | Both consume `figures/visio/figure1_concept_threat/final/figure1_concept_threat.pdf` with `viewport=0 0 252 168,clip` (`paper/main.tex:86`, `paper-Chinese/main.tex:103`). |

Non-authoritative material:

- `paper/figures/visio/figure1_concept_threat/round1/` and `review/round1|round2/` are historical render/review evidence. Trellis explicitly says historical rounds and review evidence remain immutable (`.trellis/spec/backend/quality-guidelines.md:1346`).
- `paper-Chinese/paper/figures/visio/figure1_concept_threat/` is a nested packaging/archive copy. It is not resolved by `paper-Chinese/main.tex`; its builders/scenes and VSDX happen to match the current English tree, but it has no final PDF.
- `.writing/files/...` copies are staging/cache material and are not manuscript consumers.

### Scene build pattern

The required regeneration order is round 1 before round 2:

```powershell
py -3 paper\figures\visio\figure1_concept_threat\build_round1_scene.py
py -3 paper\figures\visio\figure1_concept_threat\build_round2_scene.py
```

Round 2 deep-copies the round-1 metadata and declares `reuse_source_inventory_and_arrow_plan_only; reauthor_all_visible_nodes` (`build_round2_scene.py:15-20`). Therefore:

- a layout/text-only revision normally changes the round-2 builder and generated round-2 scene;
- a semantic/topology/source-inventory revision also changes round 1 so the inherited inventory and arrow plan do not contradict the visible scene;
- running round 2 alone preserves whatever absolute `metadata.source_image` is already stored in the round-1 scene.

The latest English builder already contains the July 5 correction `Short-exposure` (`build_round2_scene.py:213`) and omits the unsupported fixed `≈ 50 ms` node. The English scene carries the same corrected wording (`figure1_concept_threat.round2.scene.json:242,661,690,2714`).

### Validation and render commands

The local Visiomaster contract is `image → scene.json → strict validation/audit → Visio COM render → VSDX/SVG/PNG`. With the installed skill location:

```powershell
$VM = "$env:USERPROFILE\.codex\skills\visiomaster"
$ROOT = "paper\figures\visio\figure1_concept_threat"
$SCENE = "$ROOT\figure1_concept_threat.round2.scene.json"

py -3 "$VM\scripts\scene_validate.py" $SCENE --strict
py -3 "$VM\scripts\scene_complexity.py" $SCENE --strict --output "$ROOT\round2_scene_complexity.md"
py -3 "$VM\scripts\scene_audit.py" $SCENE --fail-on-rebuild --output "$ROOT\round2_scene_audit.md"
py -3 "$VM\scripts\scene_to_visio.py" $SCENE --output-dir "$ROOT\final" --basename figure1_concept_threat
```

`--basename figure1_concept_threat` is essential; otherwise the renderer derives the output name from `figure1_concept_threat.round2.scene.json` and writes `figure1_concept_threat.round2.*`. The renderer writes VSDX, SVG, and PNG, sets the page geometry from the normalized scene, and saves/exports through Visio (`C:/Users/黄哲远/.codex/skills/visiomaster/scripts/scene_to_visio.py:6054-6088,6133-6169`).

The checked-in text-margin pass is:

```powershell
py -3 paper\figures\visio\figure1_concept_threat\fix_visio_text_margins.py `
  paper\figures\visio\figure1_concept_threat\final\figure1_concept_threat.vsdx
```

It changes `LeftMargin`, `RightMargin`, `TopMargin`, and `BottomMargin` on every text-bearing shape, saves the VSDX, and re-exports SVG/PNG (`fix_visio_text_margins.py:9-37,40-64`). Reopen-before-authoritative-export remains the project-specific Visio cache precaution (`.trellis/tasks/07-02-redraw-figure-1-visio/research/visio-finalization-notes.md:3-5`).

### PDF export and one-off migrations

The normal checked-in PDF entry point is:

```powershell
py -3 paper\figures\visio\figure1_concept_threat\export_final_pdf.py
```

It opens the canonical final VSDX in a fresh hidden Visio instance and calls `ExportAsFixedFormat(1, PDF, 1, 0)` (`export_final_pdf.py:8-24`). It exports whatever page geometry exists in the VSDX.

Two scripts are historical July 5 migrations, not general post-processing steps for a redesigned layout:

- `patch_final_vsdx_labels.py` atomically rewrites `visio/pages/page1.xml`, replacing exactly one `Instantaneous` with `Short-exposure` and removing exactly one `≈ 50 ms`; it accepts only wholly old or already-patched states (`patch_final_vsdx_labels.py:19-63`). The current English VSDX is already patched.
- `overlay_final_pdf_labels.py` removes/repaints those two labels at hard-coded PDF coordinates. Its own header documents the A4/lower-left viewport assumption (`overlay_final_pdf_labels.py:1-5`), and the rectangles/text positions are fixed (`overlay_final_pdf_labels.py:50-71`). Do not run it after a supervisor-driven layout change unless those exact coordinates have been revalidated.

### English/Chinese synchronization and paper build

There is no Figure 1 sync script, symlink, or generated-asset rule. The prior task prescribes a physical copy of the canonical English VSDX and freshly exported PDF into the matching live Chinese `final/` directory (`.trellis/tasks/07-05-export-revised-figure1/prd.md:11,29-31`):

```powershell
Copy-Item -LiteralPath paper\figures\visio\figure1_concept_threat\final\figure1_concept_threat.vsdx `
  -Destination paper-Chinese\figures\visio\figure1_concept_threat\final\figure1_concept_threat.vsdx
Copy-Item -LiteralPath paper\figures\visio\figure1_concept_threat\final\figure1_concept_threat.pdf `
  -Destination paper-Chinese\figures\visio\figure1_concept_threat\final\figure1_concept_threat.pdf
```

After copying, compare SHA-256 hashes; the old acceptance criteria require byte-identical English/Chinese VSDX and PDF (`.trellis/tasks/07-05-export-revised-figure1/prd.md:17-18`). Only the live `paper-Chinese/figures/...` tree is required by the Chinese manuscript; the nested `paper-Chinese/paper/...` copy is not a consumer.

Paper verification commands currently evidenced in this repository are:

```powershell
Push-Location paper
latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex
Pop-Location
```

and, from a Bash-capable shell:

```bash
./paper-Chinese/build.sh
```

The Chinese script invokes `latexmk -g main.tex` under a checked-in `latexmkrc` that forces XeLaTeX and rejects unresolved references. The general paper-build guide requires a complete `latexmk` build, zero undefined citations/references/rerun warnings, placeholder checks, and visual inspection whenever a figure changes (`.trellis/spec/guides/latex-paper-build-thinking-guide.md:7-21,32-38`).

### Current parity and drift audit

Hashes below were measured from the working tree on 2026-07-19:

| Artifact | English canonical | Live Chinese mirror | Parity |
|---|---|---|---|
| `source/original.png` | `83c58eb205b505169f5b18708758344d9ec14a6bfce9e531c34ddf889a668be3` | same | Yes |
| `build_round1_scene.py` | `c65d7f5d867437cfc1c8f47005e81638354057d08bc049c1cd66e2195f1025fa` | `69bb8d3557b481002b756dff626a41014f18068e0fa20d1d6cafdaaff018295e` | No |
| `figure1_concept_threat.scene.json` | `0e09aecd3558cb39bbc9db380d412a8eadc5f3871ed27d8427931a2052e52826` | `c1e3f213dba5181144a17cc6543264e0384f416b3c2ec00d7a7924b2ea561d12` | No |
| `build_round2_scene.py` | `11a79b6d5c1a986631f1b5700ea3995adac497d3e34872a3234b8466ae48ebe7` | `f807651f5175c0006864f8288b9a747cd1285002e1f957f5211f608998e5e41c` | No |
| `figure1_concept_threat.round2.scene.json` | `f7218b17caa972cfa54bdc72fa524153f79aed4b3a8abbb553ce0dd9bc154c8c` | `47ac1e02875d996717492e418bb4f0a2f5a84ad26c2793ffc39361d204fc0288` | No |
| `final/figure1_concept_threat.vsdx` | `2b4b2b18651664b849a93c003fbba0ac51ad0a880e290f00b322fa3075a7b8ff` (31,073 B) | `8c7f2bfce075fb25ba59d60fdbcfe4ba1e1e78ba2154f65758380f953bf6dee5` (42,852 B) | **No** |
| `final/figure1_concept_threat.pdf` | `ec20d8126fb81e81861c43d72150b4180a93205dd1a39d091c7aa19fa112432f` (48,133 B) | same | **Yes** |

Concrete drift:

1. **The live Chinese VSDX is semantically stale.** English page XML contains one `Short-exposure`, zero `Instantaneous`, and zero `≈ 50 ms`; the live Chinese VSDX contains zero `Short-exposure`, one `Instantaneous`, and one `≈ 50 ms`. This violates the earlier byte-identical-mirror acceptance criterion even though the PDFs match.
2. **The live Chinese builders/scenes are also stale.** Their only substantive visible-source difference is the retired `Instantaneous` label plus the unsupported integration-time node. The English trees were updated; the live Chinese trees were not. Because these are not manuscript consumers, the immediate publication break is confined to editability/reproducibility, not compiled output.
3. **The current PDFs are correctly mirrored.** English and Chinese final PDFs are byte-identical, and both current LaTeX build records resolve the local `figures/visio/.../final/figure1_concept_threat.pdf` file.
4. **Scene page geometry and final-artifact page geometry diverge.** The maintained scene requests a 3.5×2.333-in page, and the round-1 VSDX has that page size. The canonical final VSDX/PDF is A4 (`8.2677165×11.6929134 in`, PDF media box `595.2×841.8 pt`) with the drawing occupying exactly the lower-left 3.5×2.333-in area. The `252×168 pt` TeX viewport makes this work. The old design requested a direct 3.5×2.333-in final PDF/PNG (`docs/superpowers/specs/2026-07-02-figure-1-visio-design.md:20,26,65-66`), but the later A4+viewport workflow is the current live contract. A full scene rerender will likely revert the VSDX to the small page, so page-size change must be deliberate and visually verified under `.trellis/spec/backend/quality-guidelines.md:1350,1358,1373`.
5. **Final renderer outputs are incomplete.** The original plan calls for final VSDX/SVG/PDF/PNG/scene (`docs/superpowers/plans/2026-07-02-figure-1-visio.md:59-67`), but the current English `final/` directory contains only VSDX and PDF. Round-2 review metadata still points to missing `final/figure1_concept_threat.png` and `final/figure1_concept_threat.scene.json` (`review_manifest.json:5-10`, `round_noop_gate.json:3-5`). These are historical-evidence/package gaps; the manuscripts themselves need only the PDF.
6. **The English scene has a non-portable absolute source path.** `figure1_concept_threat.round2.scene.json:10` points to `/Users/andyhuang/...`, while the manifest points to the valid Windows English source. Running round 1 then round 2 on this host will repair the path; running round 2 alone will not.
7. **The checked-in round-2 audit reports predate the July 5 label correction.** `round2_scene_audit.md` reports 81 nodes, while the current corrected English scene has 80; the complexity/audit evidence should be regenerated for a new review round rather than rewriting historical review JSON.
8. **Strict validation currently passes with warnings.** `scene_validate.py --strict` exits 0 with 80 nodes and 11 edges, but warns about heavy text fitting, only four audit regions, intentional-looking overlaps not marked `allow_overlap`, and five direct cross-region edges. These are not blocking validation errors, but a supervisor-driven redraw should not assume the old scene is warning-free.

### Relevant Trellis and project contracts

- `.trellis/spec/backend/quality-guidelines.md:1334-1373` is the governing editable-Visio scenario. It requires the latest builder/scene and canonical VSDX/PDF to move together, historical review artifacts to remain immutable, atomic package rewrites, PowerShell COM fallback when `pywin32` is absent, viewport/page preservation, strict validation, text/package assertions, and standalone/manuscript visual inspection.
- `.trellis/spec/guides/latex-paper-build-thinking-guide.md:7-21,32-38` governs both manuscript rebuilds after the figure changes.
- `docs/superpowers/specs/2026-07-02-figure-1-visio-design.md:20-66` defines the original 3:2, 3.5-in, editable-vector visual contract.
- `docs/superpowers/plans/2026-07-02-figure-1-visio.md:13-67` records the source→scene→review→final artifact production plan.
- `.trellis/tasks/07-05-fix-ieee-access-review-findings/research/reviewer-evidence-audit.md:37-40` records why `Instantaneous sampling` and `≈ 50 ms` were retired.
- `.trellis/tasks/07-05-export-revised-figure1/prd.md:9-31` records the English canonical source and manual Chinese mirror procedure.

### External/local-tool references

- Local Visiomaster skill, inspected 2026-07-19: `C:/Users/黄哲远/.codex/skills/visiomaster/SKILL.md`; render/export reference: `C:/Users/黄哲远/.codex/skills/visiomaster/references/visio-export-flow.md`.
- Visiomaster expects Windows, Microsoft Visio desktop, Python, and normally `pywin32`; the installed renderer exposes `--output-dir`, `--basename`, `--visible`, and rebuild-gate controls (`scene_to_visio.py:6054-6081`).
- Current default launcher is Python 3.10 via `py -3`; bare `python` is not on `PATH`.
- Current `py -3` environment does **not** contain `pywin32`. Figure 1's renderer, margin fixer, and PDF exporter import `win32com` directly and will fail in that interpreter. The repository's newer Figure 2 exporter demonstrates the spec-compliant fallback using native PowerShell Visio COM and explicit COM release (`paper/figures/visio/figure2_method_pipeline/export_final_pdf.py:13-64`).

## Caveats / Not Found

- No automatic English→Chinese Figure 1 mirror script was found. Synchronization is a documented manual copy plus hash check.
- No single current artifact can safely be treated as the only source of truth: Trellis requires the latest builders/scenes and the canonical VSDX/PDF to stay synchronized. The final VSDX is the live editable visual/layout baseline; the builders/scenes are the reproducible semantic source.
- The canonical English VSDX was open/locked by another process during this audit. Read-sharing allowed inspection, but normal hash/open calls failed. Verify that Visio has released it before any atomic replacement or export.
- A full `scene_to_visio.py` rerender and a targeted VSDX edit are not equivalent here because of the A4-versus-3.5-in page-size divergence. Preserve the current A4+viewport contract unless the task explicitly chooses and verifies a small-page regeneration.
- The hard-coded PDF overlay is unsafe as a generic finalization step after geometry changes.
- Trellis `task.py current --source` reported no session-active task; this report uses the exact task directory supplied in the dispatch prompt.
