# Visiomaster Complexity Report: Temporal pixel-masking privacy display pipeline

## Summary
- Style profile: `paper_white`
- Page: 7.16 x 2.86 in, aspect 2.50
- Visible semantic nodes: 40
- Edges: 15
- Regions: 9
- Region-covered visible nodes: 40/40
- Cross-region edges: 7
- Region plan entries: 9
- Validation warnings: 24
- Validation errors: 0

## Source Region Plan
- `global_layout`: ok, source=[0, 0, 1983, 793], target=[0, 0, 1983, 793]
- `stage_1`: ok, source=[0, 80, 705, 700], target=[24, 22, 540, 748]
- `stage_2`: ok, source=[680, 60, 1350, 735], target=[582, 22, 700, 748]
- `core`: ok, source=[680, 60, 1350, 735], target=[600, 105, 640, 545]
- `stage_3`: ok, source=[1320, 50, 1983, 760], target=[1300, 22, 659, 748]
- `stage_3_human`: ok, source=[1320, 60, 1983, 330], target=[1415, 92, 510, 250]
- `stage_3_camera`: ok, source=[1320, 380, 1983, 760], target=[1415, 390, 510, 315]
- `arrow_dense`: ok, source=[930, 170, 1760, 620], target=[880, 150, 900, 460]
- `small_text`: ok, source=[350, 80, 1900, 720], target=[300, 80, 1600, 640]

## Recommended Build Mode
- Use `region_first` or `tiled_subscenes`: rebuild each logical module/crop, validate it, then assemble the full-page scene.
- Add invisible `audit_region` boxes for source areas that do not have visible dashed frames.
- Freeze shared style tokens before assembly: body font, small label font, operator font, frame title font, and arrow weight.

## Region Load
- `stage_1`: 10 visible nodes, density=1.90/sqin, center=(1.06, 1.43) `ok`, source_ar=0.87
- `stage_2`: 7 visible nodes, density=1.03/sqin, center=(3.37, 1.43) `ok`, source_ar=0.99
- `stage_3`: 1 visible nodes, density=0.16/sqin, center=(5.88, 1.43) `ok`, source_ar=0.93
- `stage_3_human`: 6 visible nodes, density=3.61/sqin, center=(6.03, 0.78) `ok`, source_ar=2.46
- `optional_enhancement`: 1 visible nodes, density=5.35/sqin, center=(2.64, 0.56) `ok`, source_ar=2.93
- `gpu_synthesis`: 2 visible nodes, density=3.71/sqin, center=(2.65, 1.26) `ok`, source_ar=1.28
- `stage_3_camera`: 11 visible nodes, density=5.25/sqin, center=(6.03, 1.98) `ok`, source_ar=1.75
- `sampling_window`: 0 visible nodes, density=0.00/sqin, center=(5.89, 1.90) `ok`
- `adversarial_noise`: 2 visible nodes, density=6.46/sqin, center=(2.69, 2.07) `ok`, source_ar=1.52

## Font Scale
- `ellipse_node`: 17.0-17.0 pt across 1 nodes
- `math_text`: 8.2-9.2 pt across 5 nodes
- `process_box`: 8.8-9.0 pt across 2 nodes
- `rounded_process`: 7.2-8.0 pt across 2 nodes
- `stacked_process`: 18.0-18.0 pt across 1 nodes
- `text_block`: 7.5-10.0 pt across 16 nodes

## Text Fit Risks
- `input_frame` 0.44x0.29 in estimated vs 0.37x0.26 in
- `input_label` 0.69x0.13 in estimated vs 0.51x0.07 in
- `mask_label` 1.09x0.26 in estimated vs 0.50x0.11 in
- `mask_formula` 0.62x0.15 in estimated vs 0.44x0.07 in
- `optional_label` 0.91x0.25 in estimated vs 0.55x0.08 in
- `gpu_title` 0.72x0.27 in estimated vs 0.61x0.15 in
- `gpu_formula` 1.10x0.14 in estimated vs 0.66x0.12 in
- `noise_title` 0.91x0.26 in estimated vs 0.48x0.10 in
- `noise_formula` 0.57x0.15 in estimated vs 0.37x0.05 in
- `high_refresh_label` 1.12x0.27 in estimated vs 1.16x0.11 in
- `time_label` 0.33x0.14 in estimated vs 0.12x0.01 in
- `human_title` 1.23x0.14 in estimated vs 1.52x0.08 in
- 11 additional text-fit risks suppressed.

## Dense Region Risks
- No region exceeds the default density threshold.

## Paper Detail Grammar Risks
- `grid_matrix`: 13
- `math_text`: 5

## Validation Snapshot
- WARN: Exact text node `input_label` would need roughly 74% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `mask_formula` would need roughly 67% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `gpu_formula` would need roughly 53% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `noise_formula` would need roughly 61% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `time_label` would need roughly 48% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Exact text node `human_eye` would need roughly 63% font scaling to stay on one line. Widen the source-bound bbox, split into runs, or rebuild the local text layout instead of relying on heavy shrink.
- WARN: Text in node `input_frame` may not fit (0.44x0.29 in estimated vs 0.37x0.26 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `mask_label` may not fit (1.09x0.26 in estimated vs 0.50x0.11 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `optional_label` may not fit (0.91x0.25 in estimated vs 0.55x0.08 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `gpu_title` may not fit (0.72x0.27 in estimated vs 0.61x0.15 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `noise_title` may not fit (0.91x0.26 in estimated vs 0.48x0.10 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `high_refresh_label` may not fit (1.12x0.27 in estimated vs 1.16x0.11 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `human_title` may not fit (1.23x0.14 in estimated vs 1.52x0.08 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Text in node `human_eye` may not fit (0.22x0.28 in estimated vs 0.16x0.12 in available). Wrap text, enlarge the node, or assign a smaller role font before rendering.
- WARN: Additional text-fit warnings suppressed; fix the listed nodes and rerun validation.
- WARN: Edge `masks_to_gpu` leaves `mask_exit` across a module boundary without an explicit side anchor. Do not rely on center-to-center flow; use a boundary port, side anchor, bus, or explicit junction.
- WARN: Edge `time_axis` crosses text/formula node `high_refresh_label`. Exact replicas should route around labels or move the label anchor; visual review treats line-through-text as a blocking/important defect.
- WARN: Boundary arrow `subframes_to_fork` should start or end at a `boundary_port`; use it for frame-edge output, not ordinary component-to-component flow.
- WARN: Edge `subframes_to_fork` enters `observer_fork` across a module boundary without an explicit side anchor. Bind long cross-module edges to a side/port instead of default center landing.
- WARN: Edge `fork_to_human` leaves `observer_fork` across a module boundary without an explicit side anchor. Do not rely on center-to-center flow; use a boundary port, side anchor, bus, or explicit junction.
- WARN: Edge `fork_to_human` directly connects components across module boundary (stage_3 -> stage_3_human). For exact replicas, route through `boundary_port`/`boundary_arrow` unless the source visibly connects component-to-component.
- WARN: Edge `fork_to_camera` looks like a dashed/loss/backprop feedback route but uses `rounded_orthogonal_connector`. Use `dashed_feedback_path` so the path is audited as one continuous feedback route.
- WARN: Edge `fork_to_camera` leaves `observer_fork` across a module boundary without an explicit side anchor. Do not rely on center-to-center flow; use a boundary port, side anchor, bus, or explicit junction.
- WARN: Edge `fork_to_camera` directly connects components across module boundary (stage_3 -> stage_3_camera). For exact replicas, route through `boundary_port`/`boundary_arrow` unless the source visibly connects component-to-component.

