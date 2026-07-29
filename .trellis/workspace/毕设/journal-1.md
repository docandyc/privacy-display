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

- Restored the nine-position primary real-capture contract, including `d0.5_a15`, across manifest metadata and regression tests.
- Completed and synced the 19,926-cell fixed-grid OCR matrix and all derived Data Availability reports.
- Made the external archive self-contained by syncing every source/result file declared by the reproducibility manifest.
- Added the reusable nine-position archive contract to the backend quality specification and repaired the workspace `experiments` link.

### Git Commits

| Hash | Message |
|------|---------|
| `167b83a` | (see git log) |
| `13b3917` | (see git log) |

### Testing

- [OK] 31 targeted workspace tests passed.
- [OK] Staging and external nine-position archive validators passed.
- [OK] Matrix audit: 19,926 unique cells, 0 OCR errors, 2,214 cells per position.
- [OK] Manifest audit: 71 source and 80 result records, 0 existence/SHA-256 issues.

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


## Session 5: 删除 WebStudy 防偷窥评分项

**Date**: 2026-07-06
**Task**: 删除 WebStudy 防偷窥评分项
**Branch**: `master`

### Summary

删除防偷窥主观评分，改为三项量表；同步旧库兼容迁移、管理导出、分析脚本、README 和中英文论文。

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `0f13654` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 6: Complete nine-position archive consistency

**Date**: 2026-07-27
**Task**: Complete nine-position archive consistency
**Branch**: `master`

### Summary

Regenerated and validated the full nine-position fixed-grid OCR archive, synced 19,926 error-free cells and self-contained provenance files, updated regression contracts/specs, and repaired the workspace experiments link.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `0889461` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 7: Fix English Figure 4 error-bar reporting

**Date**: 2026-07-28
**Task**: Fix English Figure 4 error-bar reporting
**Branch**: `master`

### Summary

Defined Figure 4 capture-resampled 95% percentile-bootstrap intervals, regenerated asymmetric error bars and the English paper PDF, and verified a clean complete LaTeX build.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `27da278` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 8: 修复论文表格排版与 Strong 命名

**Date**: 2026-07-29
**Task**: 修复论文表格排版与 Strong 命名
**Branch**: `master`

### Summary

修复英文稿 Table 12 Delta caption glyph, Table 4 caption grammar, Table 16 percentage-point unit, and distinguish the Strong-overlay physical-capture instance from reusable strong defaults. Built paper/main.tex with latexmk -xelatex -g and verified the final PDF and log.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `24c5e89` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete
