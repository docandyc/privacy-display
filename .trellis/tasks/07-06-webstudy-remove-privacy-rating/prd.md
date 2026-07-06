# 删除 WebStudy 防偷窥评分项

## Goal

Remove the subjective anti-peeking item from the formal WebStudy before participant collection, leaving three participant-rated dimensions: readability, stability, and immediate visual comfort.

## Requirements

- Remove the `防偷窥效果` item from the participant rating form and submission payload.
- Require exactly the remaining three 1--5 ratings for each of the six conditions.
- Update the minimum-view straight-line exclusion to compare the three collected dimensions.
- Stop presenting or analyzing `privacy` in admin summaries, exports, generated statistics, and LaTeX tables.
- Preserve existing SQLite rows during migration. Keep the legacy `privacy` column nullable for storage compatibility, but write `NULL` for new submissions.
- Synchronize README, Trellis backend contract, and both active manuscripts with the three-item protocol.

## Acceptance Criteria

- [x] Participant UI shows only readability, stability, and immediate visual comfort.
- [x] Formal submissions without `privacy` succeed and store six rating rows with `privacy IS NULL`.
- [x] Existing databases with a non-null `privacy` column migrate without losing rating rows or historical values.
- [x] Straight-line exclusion evaluates the three current dimensions.
- [x] Admin, CSV/JSON exports, statistics, and analysis outputs do not expose or analyze `privacy`.
- [x] English and Chinese manuscripts describe three rating items and three-item straight-line detection.
- [x] WebStudy tests pass and both manuscripts build without unresolved references.

## Out Of Scope

- Removing the legacy SQLite column entirely.
- Changing rating conditions, Latin-square order, or typing trials.
