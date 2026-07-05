# Visiomaster Complexity Report: Temporal pixel-masking privacy display pipeline

## Summary
- Style profile: `paper_white`
- Page: 7.16 x 2.86 in, aspect 2.50
- Visible semantic nodes: 40
- Edges: 15
- Regions: 9
- Region-covered visible nodes: 40/40
- Cross-region edges: 7
- Region plan entries: 7
- Validation warnings: 18
- Validation errors: 0

## Source Region Plan
- `global_layout`: ok, source=[0, 0, 1983, 793], target=[0, 0, 1983, 793]
- `stage_1`: ok, source=[0, 80, 705, 700], target=[20, 20, 520, 753]
- `core`: ok, source=[680, 60, 1350, 735], target=[550, 20, 690, 753]
- `stage_3_human`: ok, source=[1320, 60, 1983, 330], target=[1350, 90, 590, 260]
- `stage_3_camera`: ok, source=[1320, 380, 1983, 760], target=[1350, 390, 590, 330]
- `arrow_dense`: ok, source=[930, 170, 1760, 620], target=[900, 150, 880, 470]
- `small_text`: ok, source=[350, 80, 1900, 720], target=[300, 90, 1600, 630]

## Recommended Build Mode
- Use `region_first` or `tiled_subscenes`: rebuild each logical module/crop, validate it, then assemble the full-page scene.
- Add invisible `audit_region` boxes for source areas that do not have visible dashed frames.
- Freeze shared style tokens before assembly: body font, small label font, operator font, frame title font, and arrow weight.

## Region Load
- `stage_1`: 10 visible nodes, density=1.96/sqin, center=(1.01, 1.43) `ok`, source_ar=0.87
- `stage_2`: 7 visible nodes, density=1.03/sqin, center=(3.23, 1.43) `ok`, source_ar=0.99
- `stage_3`: 1 visible nodes, density=0.14/sqin, center=(5.80, 1.43) `ok`, source_ar=0.93
- `stage_3_human`: 6 visible nodes, density=3.00/sqin, center=(5.94, 0.79) `ok`, source_ar=2.27
- `optional_enhancement`: 1 visible nodes, density=3.68/sqin, center=(2.55, 0.55) `ok`, source_ar=2.88
- `gpu_synthesis`: 2 visible nodes, density=2.56/sqin, center=(2.62, 1.26) `ok`, source_ar=1.50
- `stage_3_camera`: 11 visible nodes, density=4.33/sqin, center=(5.94, 2.00) `ok`, source_ar=1.79
- `sampling_window`: 0 visible nodes, density=0.00/sqin, center=(5.75, 1.99) `ok`, source_ar=0.48
- `adversarial_noise`: 2 visible nodes, density=5.04/sqin, center=(2.62, 2.19) `ok`, source_ar=1.45

## Font Scale
- `ellipse_node`: 13.0-13.0 pt across 1 nodes
- `math_text`: 8.2-8.5 pt across 3 nodes
- `process_box`: 8.2-8.5 pt across 2 nodes
- `rounded_process`: 7.2-7.5 pt across 2 nodes
- `stacked_process`: 14.0-14.0 pt across 1 nodes
- `text_block`: 7.2-8.5 pt across 18 nodes

## Text Fit Risks
- `input_label` 0.63x0.12 in estimated vs 0.50x0.11 in
- `security_module` 0.69x0.49 in estimated vs 0.51x0.59 in
- `mask_label` 0.68x0.35 in estimated vs 0.44x0.25 in
- `mask_formula` 0.55x0.13 in estimated vs 0.42x0.12 in
- `optional_label` 0.87x0.24 in estimated vs 0.68x0.11 in
- `gpu_title` 0.70x0.26 in estimated vs 0.80x0.16 in
- `gpu_formula` 1.07x0.14 in estimated vs 0.89x0.16 in
- `noise_title` 0.85x0.25 in estimated vs 0.53x0.16 in
- `noise_formula` 0.52x0.13 in estimated vs 0.46x0.07 in
- `high_refresh_label` 1.06x0.26 in estimated vs 1.06x0.17 in
- `time_label` 0.29x0.12 in estimated vs 0.26x0.09 in
- `human_title` 1.19x0.14 in estimated vs 1.89x0.11 in
- 10 additional text-fit risks suppressed.

## Dense Region Risks
- No region exceeds the default density threshold.

## Paper Detail Grammar Risks
- `grid_matrix`: 13
- `math_text`: 3

## Validation Snapshot
- WARN: Exact text node `mask_formula` would need roughly 72% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `gpu_formula` would need roughly 73% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Text in node `input_label` may not fit (0.63x0.12 in estimated vs 0.50x0.11 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `security_module` may not fit (0.69x0.49 in estimated vs 0.51x0.59 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `mask_label` may not fit (0.68x0.35 in estimated vs 0.44x0.25 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `optional_label` may not fit (0.87x0.24 in estimated vs 0.68x0.11 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `gpu_title` may not fit (0.70x0.26 in estimated vs 0.80x0.16 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `noise_title` may not fit (0.85x0.25 in estimated vs 0.53x0.16 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `high_refresh_label` may not fit (1.06x0.26 in estimated vs 1.06x0.17 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `time_label` may not fit (0.29x0.12 in estimated vs 0.26x0.09 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Additional text-fit warnings suppressed; fix the listed nodes and rerun validation.
- WARN: Edge `masks_to_gpu` leaves `mask_exit` across a module boundary without an explicit side anchor. Do not rely on center-to-center flow; use a boundary port, side anchor, bus, or explicit junction.
- WARN: Boundary arrow `subframes_to_fork` should start or end at a `boundary_port`; use it for frame-edge output, not ordinary component-to-component flow.
- WARN: Edge `subframes_to_fork` enters `observer_fork` across a module boundary without an explicit side anchor. Bind long cross-module edges to a side/port instead of default center landing.
- WARN: Edge `fork_to_human` leaves `observer_fork` across a module boundary without an explicit side anchor. Do not rely on center-to-center flow; use a boundary port, side anchor, bus, or explicit junction.
- WARN: Edge `fork_to_human` directly connects components across module boundary (stage_3 -> stage_3_human). For exact replicas, route through `boundary_port`/`boundary_arrow` unless the source visibly connects component-to-component.
- WARN: Edge `fork_to_camera` leaves `observer_fork` across a module boundary without an explicit side anchor. Do not rely on center-to-center flow; use a boundary port, side anchor, bus, or explicit junction.
- WARN: Edge `fork_to_camera` directly connects components across module boundary (stage_3 -> stage_3_camera). For exact replicas, route through `boundary_port`/`boundary_arrow` unless the source visibly connects component-to-component.

