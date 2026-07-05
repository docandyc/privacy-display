# Visiomaster Audit: Temporal pixel-masking privacy display pipeline

- Style profile: `paper_white`
- Nodes: 75
- Edges: 15
- Containers: 9 (`visible frames`: 9, `dashed_region`: 2, `loss_region`: 0, `audit_region`: 0)

## Typography Review
- Resolved fonts: `Times New Roman` (38), `Arial` (31), `Cambria Math` (6)
- No obvious font availability or source-font mismatch items found.

## Module Checklist
### `stage_1`
- Frame: `rectangle` `solid`
- Children (17): `stage_1_title`, `input_frame`, `input_private`, `input_data`, `input_label`, `security_module`, `security_chacha`, `security_csprng`, `security_shuffle`, `mask_entry`, `mask_1`, `mask_2`, `mask_3`, `mask_4`, `mask_exit`, `mask_label`, `mask_formula`
- Incoming edges (0): none
- Outgoing edges (1): `masks_to_gpu`
- Internal edges (2): `input_to_security`, `security_to_masks`
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `stage_2`
- Frame: `rectangle` `solid`
- Children (8): `stage_2_title`, `subframe_1`, `subframe_2`, `subframe_3`, `subframe_4`, `high_refresh_label`, `refresh_rate_label`, `time_label`
- Incoming edges (1): `gpu_to_subframes`
- Outgoing edges (1): `subframes_to_fork`
- Internal edges (1): `time_axis`
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `stage_3`
- Frame: `rectangle` `solid`
- Children (2): `stage_3_title`, `observer_fork`
- Incoming edges (1): `subframes_to_fork`
- Outgoing edges (2): `fork_to_human`, `fork_to_camera`
- Internal edges (0): none
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `optional_enhancement`
- Frame: `rectangle` `dash`
- Children (3): `optional_label`, `optional_label_2`, `optional_out`
- Incoming edges (0): none
- Outgoing edges (1): `optional_to_gpu`
- Internal edges (0): none
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `gpu_synthesis`
- Frame: `rectangle` `solid`
- Children (7): `gpu_title`, `gpu_title_2`, `gpu_formula`, `gpu_in`, `gpu_out`, `gpu_top`, `gpu_bottom`
- Incoming edges (3): `masks_to_gpu`, `optional_to_gpu`, `noise_to_gpu`
- Outgoing edges (1): `gpu_to_subframes`
- Internal edges (0): none
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `adversarial_noise`
- Frame: `rectangle` `solid`
- Children (3): `noise_title`, `noise_formula`, `noise_out`
- Incoming edges (0): none
- Outgoing edges (1): `noise_to_gpu`
- Internal edges (0): none
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `stage_3_human`
- Frame: `rectangle` `solid`
- Children (9): `human_title`, `human_eye`, `temporal_integration`, `readable_output`, `readable_private`, `readable_data`, `integration_label`, `integration_time`, `readable_label`
- Incoming edges (1): `fork_to_human`
- Outgoing edges (0): none
- Internal edges (2): `human_to_integration`, `integration_to_output`
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `stage_3_camera`
- Frame: `rectangle` `solid`
- Children (16): `camera_title`, `camera_subtitle`, `camera_icon`, `camera_lens`, `camera_top`, `camera_frame_1`, `camera_frame_2`, `camera_frame_3`, `camera_frame_4`, `sampled_fragment`, `ocr_failure`, `camera_label`, `camera_sampling_label`, `camera_sampling_label_2`, `unreadable_label`, `unreadable_label_2`
- Incoming edges (1): `fork_to_camera`
- Outgoing edges (0): none
- Internal edges (3): `camera_to_sequence`, `sequence_to_fragment`, `fragment_to_ocr`
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `sampling_window`
- Frame: `rectangle` `dash`
- Children (0): none
- Incoming edges (0): none
- Outgoing edges (0): none
- Internal edges (0): none
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

## Topology Review Items
- [ ] `stage_2_title` is a long text block without role/semantic_role; classify it as title/caption/header/formula/annotation before visual polishing.
- [ ] `mask_1` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `mask_2` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `mask_3` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `mask_4` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `subframe_1` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `subframe_2` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `subframe_3` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `subframe_4` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `camera_frame_1` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `camera_frame_2` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `camera_frame_3` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `camera_frame_4` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `sampled_fragment` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `masks_to_gpu` leaves `mask_exit` across a module boundary without an explicit side anchor. Paper-figure cross-module flow should not default to center-to-center routing.
- [ ] `noise_to_gpu` directly jumps between regions with no intermediate point; compare source crop for orthogonal lane, bus, or boundary crossing.
- [ ] `gpu_to_subframes` directly jumps between regions with no intermediate point; compare source crop for orthogonal lane, bus, or boundary crossing.
- [ ] `subframes_to_fork` enters `observer_fork` across a module boundary without an explicit side anchor. Use boundary ports, side anchors, or junction/bus grammar to lock the landing point.
- [ ] `fork_to_human` leaves `observer_fork` across a module boundary without an explicit side anchor. Paper-figure cross-module flow should not default to center-to-center routing.
- [ ] `fork_to_camera` leaves `observer_fork` across a module boundary without an explicit side anchor. Paper-figure cross-module flow should not default to center-to-center routing.

## Edge Inventory
- `input_to_security`: `lane_arrow` `horizontal` `stage_1` -> `stage_1`
- `security_to_masks`: `lane_arrow` `horizontal` `stage_1` -> `stage_1`
- `masks_to_gpu`: `boundary_arrow` `horizontal` `stage_1` -> `gpu_synthesis`
- `optional_to_gpu`: `dashed_feedback_path` `vertical` `optional_enhancement` -> `gpu_synthesis`
- `noise_to_gpu`: `lane_arrow` `vertical` `adversarial_noise` -> `gpu_synthesis`
- `gpu_to_subframes`: `lane_arrow` `horizontal` `gpu_synthesis` -> `stage_2`
- `time_axis`: `lane_arrow` `horizontal` `stage_2` -> `stage_2`
- `subframes_to_fork`: `boundary_arrow` `horizontal` `stage_2` -> `stage_3`
- `fork_to_human`: `rounded_orthogonal_connector` `rounded_orthogonal` `stage_3` -> `stage_3_human`
- `human_to_integration`: `lane_arrow` `horizontal` `stage_3_human` -> `stage_3_human`
- `integration_to_output`: `lane_arrow` `horizontal` `stage_3_human` -> `stage_3_human`
- `fork_to_camera`: `dashed_feedback_path` `orthogonal` `stage_3` -> `stage_3_camera`
- `camera_to_sequence`: `lane_arrow` `horizontal` `stage_3_camera` -> `stage_3_camera`
- `sequence_to_fragment`: `lane_arrow` `horizontal` `stage_3_camera` -> `stage_3_camera`
- `fragment_to_ocr`: `lane_arrow` `horizontal` `stage_3_camera` -> `stage_3_camera`
