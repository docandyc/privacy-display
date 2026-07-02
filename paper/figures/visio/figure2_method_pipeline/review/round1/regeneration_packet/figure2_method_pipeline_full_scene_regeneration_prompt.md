# Full-Scene Regeneration Packet: figure2_method_pipeline

- rebuild_brief: `E:\毕设\privacy-display\paper\figures\visio\figure2_method_pipeline\review\round1\figure2_method_pipeline_scene_rebuild_brief.json`
- original image: `E:/毕设/privacy-display/paper/figures/visio/figure2_method_pipeline/source/original.png`
- current replica: `E:/毕设/privacy-display/paper/figures/visio/figure2_method_pipeline/round1/figure2_method_pipeline.scene.png`
- prior scene (failure evidence only): `E:\毕设\privacy-display\paper\figures\visio\figure2_method_pipeline\round1\prior.scene.json`
- findings source: `E:\毕设\privacy-display\paper\figures\visio\figure2_method_pipeline\review\round1\figure2_method_pipeline_review_findings.json`

## Round-Specific Constraints

- Author a brand-new full scene from the source image and review findings.
- Do not patch or incrementally edit the prior scene geometry.
- Use the prior scene only as negative evidence about what looked wrong.
- Preserve source language and visible formulas exactly.
- Rebuild the whole page even when the visible defect looks local.

## Focus Regions

- stage_1, small_text, core, stage_3_human, stage_3_camera

## Findings Digest

- `F001` [blocking] Stage 1 typography collapses around the input and masks
  - focus_regions: stage_1, small_text
  - checklist_refs: V002, V009
  - visible_diff: The source keeps input/security/mask labels readable, while the replica breaks several words into narrow vertical fragments and compresses the mask equation.
  - expected_visible_change: Allocate larger text boxes, use explicit two-line labels, and keep the mask formula on a clean baseline.
- `F002` [blocking] GPU and adversarial-noise modules have broken text layout
  - focus_regions: core, small_text
  - checklist_refs: V003, V009
  - visible_diff: The GPU formula is fragmented by large inter-character gaps and the noise module collapses its title/formula into a narrow vertical stack.
  - expected_visible_change: Use wider module interiors, larger formula boxes, and separate title/formula baselines without overlap.
- `F003` [blocking] Human outcome labels overlap and clip
  - focus_regions: stage_3_human
  - checklist_refs: V005, V009
  - visible_diff: The human branch topology is correct, but integration text overlaps the icons and the readable output label becomes clipped columns.
  - expected_visible_change: Move labels into dedicated rows and widen the readable-output display and caption.
- `F004` [blocking] Camera outcome panel is overpacked
  - focus_regions: stage_3_camera, small_text
  - checklist_refs: V006, V009
  - visible_diff: The camera title, CAMERA icon text, sampling label, OCR mark, and unreadable-fragment caption overlap or split vertically.
  - expected_visible_change: Simplify the camera title, widen key objects, and place sampling/action/outcome labels on non-overlapping rows.

## Topology Checklist

- `A001` [pass] Input display flows horizontally to the security module.
  - focus_region: stage_1
  - replica_status: Horizontal arrow is present with correct direction and endpoints.
- `A002` [pass] Security module flows horizontally to the complementary masks.
  - focus_region: stage_1
  - replica_status: Horizontal arrow is present and reaches the mask cluster.
- `A003` [pass] Complementary masks feed GPU subframe synthesis.
  - focus_region: stage_1_to_stage_2
  - replica_status: Cross-stage horizontal handoff is present and points into the GPU module.
- `A004` [pass] Optional anti-OCR/inversion connects downward to GPU synthesis without an arrowhead.
  - focus_region: stage_2
  - replica_status: Dashed vertical annotation route is present above the GPU module.
- `A005` [pass] Complementary adversarial noise feeds GPU synthesis from below.
  - focus_region: stage_2
  - replica_status: Magenta upward route and arrowhead are present.
- `A006` [pass] GPU synthesis emits the sparse displayed subframe sequence.
  - focus_region: stage_2
  - replica_status: Horizontal output arrow reaches the first subframe.
- `A007` [pass] A horizontal time arrow runs beneath the subframes.
  - focus_region: stage_2
  - replica_status: Time arrow is present below the subframe row and points right.
- `A008` [pass] The subframe sequence reaches a single observer fork.
  - focus_region: arrow_dense
  - replica_status: The main navy lane reaches one fork before branching.
- `A009` [pass] The fork routes upward to the human visual system.
  - focus_region: stage_3_human
  - replica_status: Green orthogonal upper branch reaches the eye node.
- `A010` [pass] Human visual system feeds temporal integration.
  - focus_region: stage_3_human
  - replica_status: Green horizontal arrow connects eye to the integration stack.
- `A011` [pass] Temporal integration produces a readable reconstruction.
  - focus_region: stage_3_human
  - replica_status: Green horizontal arrow reaches the readable output display.
- `A012` [pass] The fork routes downward to camera/machine vision.
  - focus_region: stage_3_camera
  - replica_status: Orange-red dashed lower branch reaches the camera node.
- `A013` [pass] Camera/machine vision receives the short-exposure subframe row.
  - focus_region: stage_3_camera
  - replica_status: Orange-red horizontal arrow reaches the camera-frame row.
- `A014` [pass] The sampled sequence produces one sparse fragment.
  - focus_region: stage_3_camera
  - replica_status: Orange-red horizontal arrow connects the camera row to the fragment.
- `A015` [pass] The sparse fragment reaches an OCR-failure mark.
  - focus_region: stage_3_camera
  - replica_status: Orange-red horizontal arrow reaches the OCR-failure mark.

## Visual Checklist

- `V001` [pass] Three stage titles are legible and aligned on one top baseline.
  - focus_region: global_layout
  - replica_status: All three stage titles are legible and aligned.
- `V002` [fail] Input, security, mask label, and mask formula remain readable without broken words or overlap.
  - focus_region: stage_1
  - replica_status: PRIVATE DATA, security labels, mask label, and mask formula wrap into cramped fragments and collide visually.
- `V003` [fail] Optional tag, GPU title/formula, and noise title/formula are cleanly separated and readable.
  - focus_region: core
  - replica_status: GPU formula has irregular gaps; optional tag is cramped; noise text and formula collapse into vertical fragments.
- `V004` [fail] Four subframes, refresh label, time axis, and time label are visually separated.
  - focus_region: stage_2
  - replica_status: Subframes and arrows are clear, but the refresh label sits too close to the row and the time label is split.
- `V005` [fail] Human title, integration text, readable display, and output label do not overlap.
  - focus_region: stage_3_human
  - replica_status: Integration wording overlaps the icon/stack area and readable-output text is clipped and stacked into narrow columns.
- `V006` [fail] Camera title, icon, selected exposure window, sampling labels, fragment, and OCR failure remain distinct.
  - focus_region: stage_3_camera
  - replica_status: Camera title wraps heavily; CAMERA and OCR are split into vertical letters; sampling and outcome labels overlap the frame row.
- `V007` [pass] Main flow and both branches are axis-aligned and do not cross visible text.
  - focus_region: arrow_dense
  - replica_status: Main flow and branch routes are visually clear and avoid text.
- `V008` [pass] Human and camera outcomes remain distinguishable without relying only on color.
  - focus_region: global_layout
  - replica_status: Solid versus dashed routes, panel labels, and outcome wording provide redundant distinction.
- `V009` [fail] All labels and formulas are readable at the final 7.16-inch width.
  - focus_region: small_text
  - replica_status: Multiple labels are too compressed or broken for final-size publication use.

## Checklist Validation

- required: True
- failed_ids: V002, V003, V004, V005, V006, V009

## Arrow Plan Repair Targets

- none recorded

## Supporting References

- scene schema: `C:\Users\黄哲远\.codex\skills\visiomaster\references\scene-schema.md`
- review contract: `C:\Users\黄哲远\.codex\skills\visiomaster\references\review-contract.md`
- renderer effective fields: `C:\Users\黄哲远\.codex\skills\visiomaster\references\renderer-effective-fields.json`

## Fixed Regeneration Prompt

# Full-Scene Regeneration Prompt

Use this prompt after a visiomaster review round fails.

## Inputs

You will receive:

1. the original source image
2. the current replica image
3. a structured `review_findings.json`
4. the visiomaster scene schema and supported component vocabulary
5. optionally, the prior scene JSON as failure evidence only

## Goal

Produce a brand-new full `scene.json` that more faithfully reconstructs the source image.

This is not a patch task.

## Hard Rules

- Rebuild the entire scene from scratch.
- Do not patch or incrementally edit the prior scene geometry.
- Do not copy old coordinates, routes, or bbox values as the starting point.
- Use the prior scene only to understand what looked wrong.
- Preserve visible source language and formulas exactly.
- If the source visually differs from the prior component choice, choose a better component family instead of nudging the old one.

## Required Working Order

1. Re-read the original source image.
2. Re-read the current replica image.
3. Read all review findings.
4. Build a fresh source visual inventory for the full figure.
5. Build a fresh `metadata.region_plan`.
6. Author a fresh full `scene.json`.

Do not skip directly from review findings to coordinate edits.

## Authoring Priorities

Before fine style tuning, lock:

1. page ratio and outer frame
2. major region layout
3. component families
4. topology and connection grammar
5. text roles and math handling

Only then tune:

- spacing
- density
- shadows
- gradients
- line weight
- small offsets

## Output Contract

Return a complete new `scene.json`.

The new scene must:

- include exact-replica metadata
- include a fresh `source_visual_inventory`
- include a fresh `region_plan`
- be authorable without relying on pair/crop packs
- differ materially from the prior scene in the defect areas described by review findings

## Failure Avoidance

Avoid these mistakes:

- reusing the old wrong topology with tiny coordinate changes
- preserving old generic component choices after review already said they were wrong
- translating source labels
- normalizing formulas that were visible in the source
- keeping the old scene's spacing just because it was already written

## Completion Check

Before returning the new scene, ask:

1. Did I genuinely rebuild the full scene?
2. Did I use the review findings as constraints, not as a patch checklist?
3. Would the new rendered PNG visibly change in the reported problem areas?

If any answer is no, rebuild the scene again before returning it.

## Output Requirement

Return a brand-new `scene.json` for the next round. Do not return patch instructions, repair notes, or metadata-only edits.
