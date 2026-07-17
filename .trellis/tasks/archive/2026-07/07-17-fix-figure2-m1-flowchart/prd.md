# Fix Figure 2 M1 flowchart wording

## Goal

Apply the M1 corrections from `paper/system_design_revision_plan.md` to the editable Figure 2 method-pipeline diagram so that the figure accurately describes the evaluated implementation and display conditions, then regenerate and visually verify the canonical PDF.

## What I already know

* Canonical editable deliverable: `paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.vsdx`.
* Canonical paper asset: `paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.pdf`, referenced by `paper/main.tex` with viewport `0 0 515.52 206.16`.
* The latest authored source is `build_round3_scene.py`, which generates `figure2_method_pipeline.round3.scene.json`; both still contain the outdated M1 labels.
* M1 requests these visible replacements:
  * `1  Secure mask generation` -> `1  CSPRNG-based mask assignment`.
  * `2  GPU synthesis and temporal sequence` -> `2  Subframe composition and sequencing`.
  * `GPU subframe synthesis` -> `Offline subframe composition`.
  * `240-360 Hz` -> `nominal 240 Hz`.
  * `Unreadable fragment` -> `Partially observed subframe`; retain `OCR ×`, with optional `empirical outcome` only if it fits cleanly.
* The requested change is semantic wording correction, not a topology redesign.
* `paper/review_report.md` is an unrelated untracked user file and must remain untouched.

## Confirmed Scope

* Synchronize the latest round-3 generator and scene source with the canonical VSDX/PDF so future regeneration does not restore obsolete wording.
* Keep historical round-1/round-2 scenes and archived review evidence unchanged.
* Preserve the current page geometry and LaTeX viewport unless export inspection proves that the page bounds changed.
* Retain `OCR ×` and omit the optional `empirical outcome` annotation because the camera-output panel is already spatially constrained.
* Use the measured-fit line split `Partially` / `observed subframe`; the initially proposed `Partially observed` / `subframe` split collides with the adjacent `Short-exposure` label at the maintained font scale.

## Requirements (evolving)

* Preserve the current diagram structure, connectors, colors, typography hierarchy, and page dimensions.
* Apply all five M1 wording corrections to the canonical editable Visio file.
* Regenerate the canonical PDF through the existing Visio COM export path.
* Keep the correction reproducible from the latest maintained source.

## Acceptance Criteria (evolving)

* [x] All obsolete M1 strings are absent from the generated round-3 scene and canonical VSDX/PDF. They may appear only in explicit migration-match tables used to upgrade an older artifact safely.
* [x] All required replacement strings are present exactly once in their intended visible roles.
* [x] `OCR ×` remains visible; the optional `empirical outcome` annotation is omitted to avoid crowding the camera-output panel.
* [x] The exported PDF retains the original A4 page size, so the `paper/main.tex` viewport remains unchanged.
* [x] Rendered standalone and manuscript-page inspections show no clipped, overlapping, wrapped, or unreadable replacement text.
* [x] Diagram topology and non-M1 content remain unchanged.

## Definition of Done

* Latest maintained source and canonical deliverables are consistent.
* VSDX package text extraction confirms old strings are gone and replacements are present.
* PDF text extraction and rendered-page inspection confirm the exported result.
* Relevant validation/audit checks pass in proportion to this wording-only change.

## Feasible Approaches

### A. Source-synchronized minimal patch (recommended)

Update `build_round3_scene.py` and the latest round-3 scene, patch the matching Visio shape text in the canonical VSDX, then re-export PDF. This preserves reproducibility while avoiding a full diagram rebuild.

### B. Final-artifact-only patch

Patch only the canonical VSDX and re-export PDF. This is fastest, but a future round-3 regeneration would restore obsolete labels.

### C. Full scene regeneration

Update the generator and rerender the entire scene through visiomaster. This gives a fully regenerated chain but risks unrelated geometry/layout drift for a wording-only correction.

## Decision (ADR-lite)

**Context**: The final VSDX/PDF needs five semantic corrections, while the latest round-3 generator and scene still contain the obsolete wording. Patching only the final artifact would make the next regeneration regress; regenerating the whole figure would risk unrelated layout drift.

**Decision**: Use Approach A, the source-synchronized minimal patch. Update `build_round3_scene.py`, regenerate or synchronize `figure2_method_pipeline.round3.scene.json`, patch only the corresponding visible shape text in the canonical VSDX, and re-export the canonical PDF through Visio COM. Use two-line labels `Offline subframe` / `composition` and `Partially` / `observed subframe`; keep `OCR ×`; do not add `empirical outcome`. Fit the longer stage-1 title by widening only its title text box within the existing panel and reducing that title to 7.2 pt.

**Consequences**: The maintained source and final deliverables stay consistent with minimal visual risk. Historical review artifacts remain records of prior rounds rather than being rewritten.

## Approval

The user approved Approach A on 2026-07-17 and directed that subsequent routine choices follow the recommended option through completion.

## Out of Scope (explicit)

* Reworking the figure topology, visual style, arrows, or panel organization.
* Rewriting historical round-1/round-2 artifacts or past review records.
* Applying M2-M13 manuscript changes.
* Editing the Figure 1 assets.

## Technical Notes

* Revision plan: `paper/system_design_revision_plan.md`, section M1.
* Existing VSDX ZIP/XML patch pattern: `paper/figures/visio/figure2_method_pipeline/remove_fixed_integration_time.py`.
* Existing Visio PDF export: `paper/figures/visio/figure2_method_pipeline/export_final_pdf.py`.
* Visiomaster rule: prefer editable reconstruction, preserve information design, validate source/final consistency, and visually review the exported PDF rather than trusting text extraction alone.

## Validation Evidence

* `py_compile` passes for the round-3 builder, M1 VSDX patcher, and Visio PDF exporter.
* Replacement-state regression checks accept wholly old/new packages and reject a mixed package before any canonical write.
* Re-running `build_round3_scene.py` reproduces the maintained round-3 scene; re-running `apply_m1_wording.py` reports the VSDX is already patched.
* Strict scene validation passes with 74 nodes, 15 edges, and no errors. Complexity coverage is 55/55 visible nodes; the audit has no `[REBUILD]` findings. Remaining warnings describe pre-existing compact-paper geometry and are resolved for the changed labels by direct render inspection.
* Baseline comparison proves every non-target scene node and the complete edge list are byte-for-byte equivalent; only the seven intended text nodes and their approved text-fit properties differ.
* A page-XML comparison across all 784 Visio shapes confirms unchanged shape identities and unchanged non-target text/geometry; geometry changes are limited to the two approved text boxes (IDs 14 and 765).
* VSDX package extraction reports zero retired labels and exactly one occurrence of every replacement. Visio COM inspection confirms `OCR ×`, the two measured text fits, and an unchanged A4 page (`8.268 x 11.693 in`).
* Canonical artifact hashes after export: scene `0C563512975DB9059DD418503188AD34514C87975DB0C3C371F76290CE2763DD`, VSDX `92A3FB83AD4ADE05833D0800FA267A83BF2DF4F57504860D26DBCBF6001F00AD`, PDF `E02D5ADA809659F9CF2F3682AF53EC79D6AC874778423577654C5613857A450B`.
* `latexmk -xelatex` completes in an isolated output directory with exit 0, no undefined citations/references, and no `??` placeholders. The repository is missing two unrelated user-study PDFs, so temporary stand-ins were supplied only for those page-13 assets; Figure 2 remains on page 6 and was visually inspected in the compiled IEEE Access layout.
