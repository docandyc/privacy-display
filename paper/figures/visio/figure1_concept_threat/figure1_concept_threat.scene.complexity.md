# Visiomaster Complexity Report: Physical visual eavesdropping and asymmetric perception

## Summary
- Style profile: `paper_white`
- Page: 3.50 x 2.33 in, aspect 1.50
- Visible semantic nodes: 72
- Edges: 11
- Regions: 4
- Region-covered visible nodes: 71/72
- Cross-region edges: 5
- Region plan entries: 7
- Validation warnings: 71
- Validation errors: 0

## Source Region Plan
- `global_layout`: ok, source=[0, 0, 1536, 1024], target=[0, 0, 1536, 1024]
- `physical_input`: ok, source=[0, 0, 730, 1024], target=[20, 20, 710, 1000]
- `subframe_core`: ok, source=[760, 350, 1500, 610], target=[750, 350, 1510, 620]
- `human_output`: ok, source=[900, 60, 1510, 350], target=[830, 80, 1510, 350]
- `camera_output`: ok, source=[870, 610, 1536, 940], target=[850, 650, 1520, 940]
- `arrow_dense`: ok, source=[760, 120, 1536, 900], target=[760, 120, 1520, 930]
- `small_text`: ok, source=[20, 0, 1536, 960], target=[20, 0, 1520, 960]

## Recommended Build Mode
- Use `region_first` or `tiled_subscenes`: rebuild each logical module/crop, validate it, then assemble the full-page scene.
- Add invisible `audit_region` boxes for source areas that do not have visible dashed frames.
- Freeze shared style tokens before assembly: body font, small label font, operator font, frame title font, and arrow weight.

## Region Load
- `physical_scene`: 32 visible nodes, density=9.11/sqin, center=(0.83, 1.16) `dense`, source_ar=0.71
- `human_region`: 13 visible nodes, density=13.64/sqin, center=(2.67, 0.49) `ok`, source_ar=2.10
- `subframe_region`: 14 visible nodes, density=13.14/sqin, center=(2.57, 1.11) `ok`, source_ar=2.85
- `camera_region`: 12 visible nodes, density=11.89/sqin, center=(2.70, 1.81) `ok`, source_ar=2.02
- Uncovered visible nodes: `panel_divider`

## Font Scale
- `ellipse_node`: 7.0-15.0 pt across 7 nodes
- `polygon_node`: 13.0-13.0 pt across 5 nodes
- `process_box`: 16.0-16.0 pt across 20 nodes
- `rounded_process`: 16.0-16.0 pt across 12 nodes
- `text_block`: 6.8-8.2 pt across 23 nodes

## Text Fit Risks
- `panel_a_title` 1.84x0.13 in estimated vs 1.31x0.04 in
- `authorized_line1` 0.50x0.11 in estimated vs 0.33x0.01 in
- `authorized_line2` 0.21x0.11 in estimated vs 0.33x0.01 in
- `sensitive_line1` 0.42x0.11 in estimated vs 0.33x0.01 in
- `sensitive_line2` 0.32x0.11 in estimated vs 0.33x0.01 in
- `phone_line1` 0.53x0.11 in estimated vs 0.33x0.01 in
- `phone_line2` 0.32x0.11 in estimated vs 0.33x0.01 in
- `display_private` 0.37x0.12 in estimated vs 0.29x0.02 in
- `display_data` 0.23x0.12 in estimated vs 0.29x0.02 in
- `panel_b_title` 1.46x0.13 in estimated vs 1.18x0.04 in
- `human_eye_label` 0.46x0.12 in estimated vs 0.40x0.01 in
- `subframe_label` 1.43x0.11 in estimated vs 0.97x0.02 in
- 1 additional text-fit risks suppressed.

## Dense Region Risks
- `physical_scene` has 32 visible nodes; split this region or create a local subscene.

## Paper Detail Grammar Risks
- `grid_matrix`: 5

## Validation Snapshot
- WARN: metadata.source_visual_inventory.regions misses review coverage for `global`.
- WARN: Node `chair_post` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `desk_leg` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `shelf_1` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `shelf_2` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `display_base` is an ultra-thin `rounded_process` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `readable_base` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `subframe_1_base` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `subframe_2_base` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `subframe_3_base` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `subframe_4_base` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `camera_top` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Node `fragment_base` is an ultra-thin `process_box` with no text; use `bracket` or an edge/connector instead of a fake line box.
- WARN: Exact text node `panel_a_title` would need roughly 68% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `authorized_line1` would need roughly 77% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `phone_line1` would need roughly 74% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `panel_b_title` would need roughly 78% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `integration_label` would need roughly 40% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `readable_private` would need roughly 75% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `readable_data` would need roughly 77% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `readable_label` would need roughly 67% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `subframe_label` would need roughly 67% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `fast_time_label` would need roughly 64% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `sampling_label` would need roughly 61% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- Additional validation items suppressed; run `scene_validate.py` for the full list.

