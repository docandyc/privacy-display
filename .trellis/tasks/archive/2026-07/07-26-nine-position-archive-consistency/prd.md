# 统一九位置论文与归档数据

## Goal

把论文、生成脚本和 Data Availability 对应的归档文件统一为九个物理位置，并将 `d0.5_a15` 的真实 raw 与五种预处理 OCR 结果纳入主分析，消除仍按八位置统计或把九位置结果放在非主分析段落中的内部冲突。

## What I already know

* 用户确认 `0.5 m/15°` 实际也使用与其他位置相同的 UVC `-8/-5` 配置。
* 原归档 `paper_ocr_clustered_stats.json` 的 primary 段仍为 288 单元并排除 `d0.5_a15`，但同文件 contrasts 已是九位置版本。
* 原归档 `sensitive_field_recovery.json` 把论文采用的九位置数值放在标为非主估计量的 sensitivity 段。
* 原预处理矩阵缺少 `d0.5_a15` 的五种预处理结果，不能用 raw OCR 行冒充这些结果。
* 论文已经采用九位置汇总，归档必须从真实逐图结果重新生成并与论文交叉核对。

## Requirements

* 九个位置全部进入 primary common-setting estimand，`excluded_positions` 为空。
* 修正 `d0.5_a15` 元数据和对应 OCR 归档中的曝光配置，使其与用户确认的 `-8/-5` 一致。
* 预处理矩阵包含九位置、1,107 张主分析图像、6 种输入形式和 3 个 OCR 引擎，共 19,926 个唯一单元。
* `d0.5_a15` 的五种预处理必须在原始图片上实际执行；只允许 raw 单元复用 canonical raw archive。
* 从完整矩阵重新生成 Tesseract、EasyOCR、Surya 和三引擎汇总报告。
* 重新生成 clustered OCR、sensitive-field recovery、design audit 和 reproducibility manifest。
* 更新生成脚本、测试和 manifest 期望值，防止以后重新生成时退回八位置版本。
* 将最终生成物同步到 `/Volumes/MacExtension/Projects/privacy-display` 的 Data Availability 归档。

## Acceptance Criteria

* [x] preprocessing matrix 恰有 19,926 行且唯一键数也是 19,926。
* [x] 每个位置恰有 2,214 个单元，包含 `d0.5_a15`。
* [x] 每个 OCR 引擎恰有 6,642 个单元，每种输入形式恰有 3,321 个单元。
* [x] 所有预处理 OCR 单元均无 `ocr_error`。
* [x] clustered primary 为 324 个匹配单元、九位置、无排除位置。
* [x] sensitive-field primary 为 324 个匹配单元，且论文数值来自该 primary 段。
* [x] 预处理报告、论文表格和归档 JSON/Markdown 的四舍五入数值一致。
* [x] design audit 与 reproducibility manifest 均声明九位置和 19,926 个预处理单元。
* [x] 相关测试和归档一致性审计通过。

## Definition of Done

* 生成脚本与测试已更新。
* 真实缺失 OCR 单元已完成并可逐行审计。
* 所有九位置归档文件已重新生成并同步。
* 论文和归档之间不存在已知的八位置/九位置冲突。

## Technical Approach

保留原八位置矩阵和九位置 raw OCR 行，只对 `d0.5_a15` 缺失的五种预处理 × 三个引擎单元执行 OCR。运行采用可恢复 JSONL 检查点；EasyOCR 使用两个均衡 CPU 分片，Surya 使用批处理。完成后按唯一键合并，运行矩阵完整性审计，再由修正后的生成脚本产出全部汇总文件和 manifest。

## Decision (ADR-lite)

**Context**: 对话中保留了九位置汇总百分比，但没有保留每张图像、每种预处理和每个 OCR 引擎的完整逐行输出。

**Decision**: 汇总值可用于最终交叉核对，但不能反推或伪造逐行矩阵；缺失单元必须从归档图片实际重跑。

**Consequences**: 运行耗时较长，但归档具备可复核的行级证据，也避免“拿 raw OCR 冒充预处理结果”的方法学问题。

## Out of Scope

* 不重新采集相机图片。
* 不重跑已有八位置且哈希未变化的 OCR 单元。
* 不改动与九位置归档冲突无关的论文实验结论。
* 不用新的 OCR 参数或模型替换原实验配置。

## Technical Notes

* 论文目录：`paper/`
* 代码与测试：`privacy-display/src/`、`privacy-display/tests/`
* 外部归档：`/Volumes/MacExtension/Projects/privacy-display/experiments/`
* 本次可恢复运行暂存：`/tmp/codex-archive9-20260726/`

## Validation

* 外部归档矩阵：19,926 行、19,926 个唯一键、0 个 OCR 错误。
* 各位置 2,214 行；各引擎 6,642 行；各输入形式 3,321 行。
* `d0.5_a15` 的 1,845 个非 raw 单元全部来自 `generated_preprocessing_attack`。
* 三引擎 matched raw：94.1% / 16.2% / 5.0%；fixed-grid oracle：95.5% / 37.2% / 13.2%。
* `validate_nine_position_archive.py --with-preprocessing-reports` 在 staging 和外部归档上均通过。
* 工作区与 staging 的相关测试均为 31 passed。
* 外部 manifest 的 71 个源码记录和 80 个结果记录均通过存在性与 SHA-256 校验，0 个问题。
