# 调整 WebStudy 防偷拍评分文案

## Goal

Change the fourth subjective rating label from bystander shoulder-surfing wording to camera-capture wording so the UI matches the anti-camera purpose of the deployed mask.

## Requirements

- In the rating form, change `防偷看效果` to `防偷拍效果`.
- Change the scale hint to `1 = 旁人拍照很清晰，5 = 旁人拍照几乎拍不清楚`.
- Keep the stored field name `privacy` unchanged for database compatibility.
- Align admin tables, LaTeX table headers, README wording, and regression tests with the new label.

## Acceptance Criteria

- [x] The WebStudy rating form shows `防偷拍效果`.
- [x] Tests assert the new camera-capture scale text.
- [x] Existing WebStudy Python and Node tests still pass.

## Definition of Done

- Focused text-only change committed.
- No unrelated untracked files touched.
