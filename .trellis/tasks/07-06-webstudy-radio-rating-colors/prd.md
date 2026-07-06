# 调整 WebStudy 单选与评分色阶

## Goal

Make the participant identity and ablation-rating controls more direct while keeping the stored experiment schema backward compatible.

## Requirements

- Replace the required vision-correction `<select>` with three visible radio choices.
- Preserve stored values `none`, `glasses`, and `contacts`, and preserve restored session selection.
- Render rating choices 1--5 with a stable red, orange, yellow, light-green, green progression.
- Use a stronger selected state and a visible keyboard focus state; color must not be the only indication because each option retains its numeric label.
- Rename `即时视觉不适感` to `即时视觉舒适感`, with anchors `1 = 很不舒适，5 = 很舒适`.
- Keep `稳定感`, but change its upper anchor to `5 = 完全察觉不到闪烁`.
- Rename `防偷拍效果` to `防偷窥效果`, with anchors `1 = 旁人很容易看清，5 = 旁人完全看不清`.
- Keep internal rating fields `flicker`, `fatigue`, and `privacy` unchanged.
- Synchronize participant-facing text, admin/analysis labels, README/spec wording, and both active manuscripts with the new constructs.

## Acceptance Criteria

- [x] Vision correction is a required radio group, not a select.
- [x] Existing participant values and form submission behavior remain compatible.
- [x] All five rating buttons have an accessible red-to-green progression and distinct selected/focus states.
- [x] New labels and anchors appear in the participant UI and regression tests.
- [x] Admin, generated LaTeX labels, documentation, and English/Chinese protocol text use the same rating interpretation.
- [x] WebStudy tests pass and both manuscripts build without unresolved references.

## Out of Scope

- Database migration or rating-column renaming.
- Changing the numerical direction of any stored rating.
