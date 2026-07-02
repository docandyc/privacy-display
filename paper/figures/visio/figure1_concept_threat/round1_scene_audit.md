# Visiomaster Audit: Physical visual eavesdropping and asymmetric perception

- Style profile: `paper_white`
- Nodes: 79
- Edges: 11
- Containers: 4 (`visible frames`: 0, `dashed_region`: 0, `loss_region`: 0, `audit_region`: 4)

## Typography Review
- Resolved fonts: `Times New Roman` (55), `Arial` (24)
- No obvious font availability or source-font mismatch items found.

## Module Checklist
### `physical_scene`
- Frame: invisible logical audit region
- Children (32): `panel_a_title`, `authorized_line1`, `authorized_line2`, `sensitive_line1`, `sensitive_line2`, `phone_line1`, `phone_line2`, `chair_back`, `chair_seat`, `chair_post`, `chair_base`, `user_torso`, `user_head`, `user_hair`, `user_arm`, `desk_top`, `desk_cabinet`, `desk_leg`, `keyboard`, `bookshelf`, `shelf_1`, `shelf_2`, `sensitive_display`, `display_screen`, `display_private`, `display_data`, `display_stand`, `display_base`, `phone_hand`, `smartphone`, `phone_screen`, `phone_lens`
- Incoming edges (0): none
- Outgoing edges (0): none
- Internal edges (2): `capture_ray_upper`, `capture_ray_lower`
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `subframe_region`
- Frame: invisible logical audit region
- Children (16): `subframe_label`, `fast_time_label`, `subframe_1`, `subframe_grid_1`, `subframe_1_base`, `subframe_2`, `subframe_grid_2`, `subframe_2_base`, `subframe_3`, `subframe_grid_3`, `subframe_3_base`, `subframe_4`, `subframe_grid_4`, `subframe_4_base`, `selection_left`, `selection_right`
- Incoming edges (0): none
- Outgoing edges (5): `frame1_to_eye`, `frame2_to_eye`, `frame3_to_eye`, `frame4_to_eye`, `selected_to_camera`
- Internal edges (1): `time_axis`
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `human_region`
- Frame: invisible logical audit region
- Children (13): `panel_b_title`, `human_eye_label`, `human_eye`, `human_pupil`, `integration_label`, `integration_time`, `readable_display`, `readable_screen`, `readable_private`, `readable_data`, `readable_stand`, `readable_base`, `readable_label`
- Incoming edges (4): `frame1_to_eye`, `frame2_to_eye`, `frame3_to_eye`, `frame4_to_eye`
- Outgoing edges (0): none
- Internal edges (1): `eye_to_readable`
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

### `camera_region`
- Frame: invisible logical audit region
- Children (12): `camera_icon`, `camera_lens`, `camera_top`, `camera_label`, `sampling_label`, `sampling_label_2`, `fragment_display`, `fragment_grid`, `fragment_base`, `fragment_label`, `fragment_label_2`, `ocr_failure`
- Incoming edges (1): `selected_to_camera`
- Outgoing edges (0): none
- Internal edges (2): `camera_to_fragment`, `fragment_to_ocr`
- [ ] Compare this module against the source crop: frame bounds, child count, labels, colors, and arrow directions.
- [ ] Check every outgoing edge: does it originate from a component, a boundary, or a bus in the source?

## Topology Review Items
- [ ] `integration_label` text is likely to shrink/wrap (0.90x0.11 estimated vs 0.48x0.10); use `math_text`, caption runs, or source-sized text box.
- [ ] `subframe_label` text is likely to shrink/wrap (1.43x0.11 estimated vs 0.91x0.12); use `math_text`, caption runs, or source-sized text box.
- [ ] `subframe_grid_1` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `subframe_grid_2` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `subframe_grid_3` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `subframe_grid_4` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `sampling_label` text is likely to shrink/wrap (0.64x0.11 estimated vs 0.43x0.10); use `math_text`, caption runs, or source-sized text box.
- [ ] `fragment_grid` is a compact paper grid/vector without source_bbox_px; count/spacing mistakes are hard to catch without source-region binding.
- [ ] `frame1_to_eye` directly jumps between regions with no intermediate point; compare source crop for orthogonal lane, bus, or boundary crossing.
- [ ] `frame2_to_eye` directly jumps between regions with no intermediate point; compare source crop for orthogonal lane, bus, or boundary crossing.
- [ ] `frame3_to_eye` directly jumps between regions with no intermediate point; compare source crop for orthogonal lane, bus, or boundary crossing.
- [ ] `frame4_to_eye` directly jumps between regions with no intermediate point; compare source crop for orthogonal lane, bus, or boundary crossing.
- [ ] `selected_to_camera` directly jumps between regions with no intermediate point; compare source crop for orthogonal lane, bus, or boundary crossing.

## Edge Inventory
- `capture_ray_upper`: `line_segment` `straight` `physical_scene` -> `physical_scene`
- `capture_ray_lower`: `line_segment` `straight` `physical_scene` -> `physical_scene`
- `time_axis`: `lane_arrow` `horizontal` `subframe_region` -> `subframe_region`
- `frame1_to_eye`: `arrow_connector` `straight` `subframe_region` -> `human_region`
- `frame2_to_eye`: `arrow_connector` `straight` `subframe_region` -> `human_region`
- `frame3_to_eye`: `arrow_connector` `straight` `subframe_region` -> `human_region`
- `frame4_to_eye`: `arrow_connector` `straight` `subframe_region` -> `human_region`
- `eye_to_readable`: `lane_arrow` `horizontal` `human_region` -> `human_region`
- `selected_to_camera`: `lane_arrow` `vertical` `subframe_region` -> `camera_region`
- `camera_to_fragment`: `lane_arrow` `horizontal` `camera_region` -> `camera_region`
- `fragment_to_ocr`: `lane_arrow` `horizontal` `camera_region` -> `camera_region`
