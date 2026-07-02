# Full-Scene Regeneration Packet: figure1_concept_threat

- rebuild_brief: `E:\毕设\privacy-display\paper\figures\visio\figure1_concept_threat\review\round1\figure1_concept_threat_scene_rebuild_brief.json`
- original image: `E:/毕设/privacy-display/paper/figures/visio/figure1_concept_threat/source/original.png`
- current replica: `E:/毕设/privacy-display/paper/figures/visio/figure1_concept_threat/round1/figure1_concept_threat.png`
- prior scene (failure evidence only): `E:\毕设\privacy-display\paper\figures\visio\figure1_concept_threat\round1\prior.scene.json`
- findings source: `E:\毕设\privacy-display\paper\figures\visio\figure1_concept_threat\review\round1\figure1_concept_threat_review_findings.json`

## Round-Specific Constraints

- Author a brand-new full scene from the source image and review findings.
- Do not patch or incrementally edit the prior scene geometry.
- Use the prior scene only as negative evidence about what looked wrong.
- Preserve source language and visible formulas exactly.
- Rebuild the whole page even when the visible defect looks local.

## Focus Regions

- physical_scene, small_text, human_output, arrow_dense, subframe_row, camera_output

## Findings Digest

- `F001` [blocking] Physical-scene labels break at single-column size
  - focus_regions: physical_scene, small_text
  - checklist_refs: V002, V007
  - visible_diff: The source keeps Authorized user, PRIVATE DATA, and Smartphone camera intact, while the replica splits several words into narrow fragments.
  - expected_visible_change: Widen label zones, reduce local type slightly, and enlarge the two display text areas.
- `F002` [blocking] Human-integration panel is overpacked
  - focus_regions: human_output, arrow_dense, small_text
  - checklist_refs: V004, V007
  - visible_diff: Green arrows, Human eye, Temporal integration, Readable, and PRIVATE DATA occupy the same narrow band.
  - expected_visible_change: Create a dedicated top object row, a separate lower caption row, and wider output display text boxes.
- `F003` [blocking] Subframe and camera captions collide
  - focus_regions: subframe_row, camera_output, small_text
  - checklist_refs: V005, V006, V007
  - visible_diff: The rapid-subframe caption and instantaneous-sampling labels crowd the frame row and lower camera chain.
  - expected_visible_change: Reserve a caption band under the frame row and move camera-path labels below their object row.

## Topology Checklist

- `A001` [pass] Upper dashed capture ray connects display and smartphone.
  - focus_region: physical_scene
  - replica_status: Upper dashed orange-red ray is present.
- `A002` [pass] Lower dashed capture ray connects display and smartphone.
  - focus_region: physical_scene
  - replica_status: Lower dashed orange-red ray is present.
- `A003` [pass] Fast-time arrow points right above the four subframes.
  - focus_region: subframe_row
  - replica_status: Right-pointing navy time arrow is present.
- `A004` [pass] First subframe feeds the human eye.
  - focus_region: human_output
  - replica_status: First green diagonal arrow reaches the eye.
- `A005` [pass] Second subframe feeds the human eye.
  - focus_region: human_output
  - replica_status: Second green diagonal arrow reaches the eye.
- `A006` [pass] Third subframe feeds the human eye.
  - focus_region: human_output
  - replica_status: Third green diagonal arrow reaches the eye.
- `A007` [pass] Fourth subframe feeds the human eye.
  - focus_region: human_output
  - replica_status: Fourth green diagonal arrow reaches the eye.
- `A008` [pass] The eye feeds the readable display.
  - focus_region: human_output
  - replica_status: Green horizontal arrow reaches the output display.
- `A009` [pass] The selected second subframe feeds the camera.
  - focus_region: camera_output
  - replica_status: Orange-red vertical arrow reaches the camera.
- `A010` [pass] Camera output feeds one sparse fragment.
  - focus_region: camera_output
  - replica_status: Orange-red horizontal arrow reaches the fragment.
- `A011` [pass] The sparse fragment reaches OCR failure.
  - focus_region: camera_output
  - replica_status: Orange-red horizontal arrow reaches OCR ×.

## Visual Checklist

- `V001` [pass] Two panel headings are clear and balanced.
  - focus_region: global_layout
  - replica_status: Both panel headings are present and readable.
- `V002` [fail] Authorized user, sensitive display, and smartphone labels remain readable.
  - focus_region: physical_scene
  - replica_status: Authorized, PRIVATE, Smartphone, and camera words break into narrow fragments.
- `V003` [pass] The user-screen-phone triangle reads as one physical eavesdropping scene.
  - focus_region: physical_scene
  - replica_status: The simplified editable office scene preserves the intended threat geometry.
- `V004` [fail] Eye, integration label, readable display, and output label occupy separate zones.
  - focus_region: human_output
  - replica_status: Human-eye and integration text overlap arrows and the readable display text is clipped.
- `V005` [fail] Four thumbnails, fast-time arrow, and subframe label remain distinct.
  - focus_region: subframe_row
  - replica_status: The subframe label collides with the lower outcome labels and green routes crowd the row.
- `V006` [fail] Camera, instantaneous-sampling label, fragment, and OCR failure are cleanly separated.
  - focus_region: camera_output
  - replica_status: Instantaneous sampling and fragment labels overlap the object row and each other.
- `V007` [fail] All labels remain readable at 3.50-inch width.
  - focus_region: small_text
  - replica_status: Several English words are broken or compressed beyond publication quality.
- `V008` [pass] Human and camera paths remain distinguishable without color alone.
  - focus_region: global_layout
  - replica_status: Icons, solid/dashed grammar, selection bracket, and outcome labels provide redundant distinction.

## Checklist Validation

- required: True
- failed_ids: V002, V004, V005, V006, V007

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
