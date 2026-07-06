# Journal - 毕设 (Part 1)

> AI development session journal
> Started: 2026-06-10

---



## Session 1: PaddleOCR verification

**Date**: 2026-06-11
**Task**: PaddleOCR verification
**Branch**: `master`

### Summary

Added PaddleOCR detection and parsing, reran three-engine corpus evaluation, updated review/archive docs, and archived completed Trellis tasks.

### Main Changes

- Added `POST /api/next-assignment` and moved formal counterbalancing to server-side least-filled buckets.
- Required vision correction, added masked typing practice, repeated refresh measurement metadata, fullscreen/screen audit metadata, stability labeling, and debriefing.
- Added analysis audits for assignment balance and minimum-view straight-line rating exclusions.
- Updated WebStudy README, backend code-spec, and regression tests.

### Git Commits

| Hash | Message |
|------|---------|
| `7fd5d07` | (see git log) |

### Testing

- [OK] `.venv/bin/pytest tests/test_webstudy_*.py -q` (22 passed)
- [OK] `node --test tests/js/webstudy_design.test.js tests/js/webstudy_welcome.test.js tests/js/webstudy_mask_timing.test.js tests/js/webstudy_typing.test.js` (17 passed)
- [OK] `python3 -m py_compile webstudy/server.py webstudy/analyze_study.py webstudy/backup_db.py webstudy/assignment.py`

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 2: Close disclosure gaps

**Date**: 2026-06-11
**Task**: Close disclosure gaps
**Branch**: `master`

### Summary

Completed G3-G13 PoC gaps with off-axis and learned reconstruction experiments, spatial complementary noise, EasyOCR gradient fallback, fatigue/bandwidth/hash/HLG/ALS/pregeneration/config utilities, documentation updates, and full verification.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `167b83a` | (see git log) |
| `13b3917` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 3: Strengthen WebStudy experiment controls

**Date**: 2026-07-06
**Task**: Strengthen WebStudy experiment controls
**Branch**: `master`

### Summary

Added server-side least-filled WebStudy assignment, required vision correction, masked practice, refresh distribution metadata, rating satisficing exclusions, stability labeling, README/spec updates, and regression tests.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `c14811e` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 4: 调整 WebStudy 单选与评分色阶

**Date**: 2026-07-06
**Task**: 调整 WebStudy 单选与评分色阶
**Branch**: `master`

### Summary

将视力矫正改为必填单选，增加评分红到绿色阶，并同步量表文案、分析标签、文档和中英文论文。

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `276ea88` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete
