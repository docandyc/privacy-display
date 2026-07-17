# Figure 2 M1 Flowchart Correction Design

## Objective

Correct the five M1 wording defects in the editable Figure 2 method-pipeline diagram without changing its topology, visual grammar, or paper integration geometry.

## Maintained Artifact Chain

The latest maintained authoring source is `paper/figures/visio/figure2_method_pipeline/build_round3_scene.py`, which produces `figure2_method_pipeline.round3.scene.json`. The canonical editable and paper deliverables are `final/figure2_method_pipeline.vsdx` and `final/figure2_method_pipeline.pdf`.

All four artifacts must agree after the change. Historical round-1/round-2 scenes and prior review bundles remain unchanged because they document earlier reconstruction rounds.

## Visible Text Contract

| Existing visible text | Replacement |
|---|---|
| `1  Secure mask generation` | `1  CSPRNG-based mask assignment` |
| `2  GPU synthesis and temporal sequence` | `2  Subframe composition and sequencing` |
| `GPU subframe` / `synthesis` | `Offline subframe` / `composition` |
| `240-360 Hz` | `nominal 240 Hz` |
| `Unreadable` / `fragment` | `Partially` / `observed subframe` |

`OCR ×` remains unchanged. The optional `empirical outcome` note is omitted because the camera-output panel is already dense and the revised subframe label provides the necessary epistemic qualification. The line split is chosen from measured Arial Bold text extents: `Partially observed` does not fit beside `Short-exposure` at the maintained scale, while `Partially` / `observed subframe` preserves the full wording without collision.

## Implementation Strategy

Use a source-synchronized minimal patch:

1. Update the five labels in `build_round3_scene.py` and regenerate the latest scene JSON using the existing builder.
2. Patch only the matching Visio text shapes in `final/figure2_method_pipeline.vsdx`, using the established ZIP/XML editing pattern and strict expected-count checks.
3. Re-export `final/figure2_method_pipeline.pdf` through the existing Visio COM exporter.
4. Do not regenerate the entire Visio scene, because a wording-only change does not justify unrelated geometry drift.

## Layout Rules

Preserve all node bounds, connectors, styles, page geometry, and the LaTeX viewport. Keep the two longer module/output labels on two lines. The longer stage-1 title uses a 7.2 pt font and a title-only width increase that remains inside the existing panel. The `observed subframe` line receives a wider 270 px text-only box below the sampled frame so Visio keeps it on one line. No panel, module, or connector geometry changes.

## Verification

* Search the generated round-3 scene and canonical VSDX package text: every obsolete label must be absent and every replacement present in its intended role. Obsolete strings may remain only in explicit migration-match tables in the maintenance scripts.
* Extract PDF text to confirm the re-export contains the replacement labels.
* Compare pre/post page size and Visio shape geometry to prove the viewport remains valid.
* Render the cropped figure region to PNG and inspect for wrapping, clipping, overlap, unreadable glyphs, and unintended layout changes.
* Confirm unrelated worktree content, especially `paper/review_report.md`, is untouched.
