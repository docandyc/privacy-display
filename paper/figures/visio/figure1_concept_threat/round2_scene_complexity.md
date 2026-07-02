# Visiomaster Complexity Report: Physical visual eavesdropping and asymmetric perception

## Summary
- Style profile: `paper_white`
- Page: 3.50 x 2.33 in, aspect 1.50
- Visible semantic nodes: 73
- Edges: 11
- Regions: 4
- Region-covered visible nodes: 72/73
- Cross-region edges: 5
- Region plan entries: 7
- Validation warnings: 30
- Validation errors: 0

## Source Region Plan
- `global_layout`: ok, source=[0, 0, 1536, 1024], target=[0, 0, 1536, 1024]
- `physical_input`: ok, source=[0, 0, 730, 1024], target=[20, 20, 710, 1000]
- `subframe_core`: ok, source=[760, 350, 1500, 650], target=[750, 370, 1510, 670]
- `human_output`: ok, source=[900, 60, 1510, 350], target=[830, 80, 1510, 370]
- `camera_output`: ok, source=[870, 610, 1536, 940], target=[850, 680, 1520, 950]
- `arrow_dense`: ok, source=[760, 120, 1536, 900], target=[760, 120, 1520, 930]
- `small_text`: ok, source=[20, 0, 1536, 960], target=[20, 0, 1520, 960]

## Recommended Build Mode
- Use `region_first` or `tiled_subscenes`: rebuild each logical module/crop, validate it, then assemble the full-page scene.
- Add invisible `audit_region` boxes for source areas that do not have visible dashed frames.
- Freeze shared style tokens before assembly: body font, small label font, operator font, frame title font, and arrow weight.

## Region Load
- `physical_scene`: 30 visible nodes, density=8.54/sqin, center=(0.83, 1.16) `dense`, source_ar=0.71
- `human_region`: 14 visible nodes, density=13.67/sqin, center=(2.67, 0.51) `ok`, source_ar=2.10
- `subframe_region`: 16 visible nodes, density=13.52/sqin, center=(2.57, 1.18) `ok`, source_ar=2.47
- `camera_region`: 12 visible nodes, density=12.78/sqin, center=(2.70, 1.86) `ok`, source_ar=2.02
- Uncovered visible nodes: `panel_divider`

## Font Scale
- `ellipse_node`: 6.8-7.0 pt across 7 nodes
- `polygon_node`: 13.0-13.0 pt across 14 nodes
- `process_box`: 16.0-16.0 pt across 9 nodes
- `rounded_process`: 16.0-16.0 pt across 11 nodes
- `text_block`: 6.5-7.8 pt across 26 nodes

## Text Fit Risks
- `panel_a_title` 1.57x0.11 in estimated vs 1.43x0.04 in
- `authorized_line1` 0.48x0.11 in estimated vs 0.46x0.04 in
- `authorized_line2` 0.20x0.11 in estimated vs 0.46x0.04 in
- `sensitive_line1` 0.40x0.11 in estimated vs 0.42x0.04 in
- `sensitive_line2` 0.30x0.11 in estimated vs 0.42x0.04 in
- `phone_line1` 0.49x0.11 in estimated vs 0.42x0.04 in
- `phone_line2` 0.30x0.11 in estimated vs 0.42x0.04 in
- `display_private` 0.33x0.11 in estimated vs 0.36x0.04 in
- `display_data` 0.20x0.11 in estimated vs 0.36x0.04 in
- `panel_b_title` 1.39x0.13 in estimated vs 1.59x0.04 in
- `human_eye_label` 0.44x0.11 in estimated vs 0.49x0.03 in
- `integration_line1` 0.37x0.11 in estimated vs 0.30x0.01 in
- 13 additional text-fit risks suppressed.

## Dense Region Risks
- `physical_scene` has 30 visible nodes; split this region or create a local subscene.

## Paper Detail Grammar Risks
- `grid_matrix`: 6

## Validation Snapshot
- WARN: Exact text node `integration_line2` would need roughly 73% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `sampling_label_1` would need roughly 67% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `fragment_label_1` would need roughly 77% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Complex scene has only 4 group/audit regions; add roughly 6 logical `audit_region`/`group_container` areas so large figures are reviewed as smaller subscenes instead of one global layout.
- WARN: Region `camera_region` aspect 2.48 differs from source region 2.02; fix region bbox before local visual polishing.
- WARN: Region `physical_scene` contains 30 visible nodes; split it into smaller `audit_region` subregions or create a local subscene first, then assemble it into the full page.
- WARN: Text in node `panel_a_title` may not fit (1.57x0.11 in estimated vs 1.43x0.04 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `authorized_line1` may not fit (0.48x0.11 in estimated vs 0.46x0.04 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `authorized_line2` may not fit (0.20x0.11 in estimated vs 0.46x0.04 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `sensitive_line1` may not fit (0.40x0.11 in estimated vs 0.42x0.04 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `sensitive_line2` may not fit (0.30x0.11 in estimated vs 0.42x0.04 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `phone_line1` may not fit (0.49x0.11 in estimated vs 0.42x0.04 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `phone_line2` may not fit (0.30x0.11 in estimated vs 0.42x0.04 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `display_private` may not fit (0.33x0.11 in estimated vs 0.36x0.04 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Additional text-fit warnings suppressed; fix the listed nodes and rerun validation.
- WARN: Nodes `bookshelf` and `bookshelf_lines` overlap by 0.109 sq in. For intended overlays set `allow_overlap: true`; otherwise fix region-local coordinates.
- WARN: Nodes `sensitive_display` and `display_screen` overlap by 0.171 sq in. For intended overlays set `allow_overlap: true`; otherwise fix region-local coordinates.
- WARN: Nodes `readable_display` and `readable_screen` overlap by 0.095 sq in. For intended overlays set `allow_overlap: true`; otherwise fix region-local coordinates.
- WARN: Nodes `subframe_1` and `subframe_grid_1` overlap by 0.037 sq in. For intended overlays set `allow_overlap: true`; otherwise fix region-local coordinates.
- WARN: Nodes `subframe_2` and `subframe_grid_2` overlap by 0.037 sq in. For intended overlays set `allow_overlap: true`; otherwise fix region-local coordinates.
- WARN: Nodes `subframe_3` and `subframe_grid_3` overlap by 0.037 sq in. For intended overlays set `allow_overlap: true`; otherwise fix region-local coordinates.
- WARN: Nodes `subframe_4` and `subframe_grid_4` overlap by 0.037 sq in. For intended overlays set `allow_overlap: true`; otherwise fix region-local coordinates.
- WARN: Nodes `fragment_display` and `fragment_grid` overlap by 0.030 sq in. For intended overlays set `allow_overlap: true`; otherwise fix region-local coordinates.
- WARN: Additional overlap warnings suppressed; fix the listed overlaps and rerun validation.
- Additional validation items suppressed; run `scene_validate.py` for the full list.

