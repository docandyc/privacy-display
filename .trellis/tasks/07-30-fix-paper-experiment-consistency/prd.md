# 修复论文实验部分一致性问题

## Goal

修复英文论文实验部分中已经确认的五类不一致，使正文、表格、图件和统计输出在最终 PDF 中相互一致，同时不改动实验数据或重新运行实验。

## Requirements

* 明确三次重复仅适用于短曝光和长曝光静态图像。
* 明确视频按每个内容项与几何条件一段 150 帧视频计数，因此主实验视频分析单位为 \(12\times9=108\)。
* 修正表 6 的 \(N\) 口径说明，使静态图像和视频的分析单位均清楚。
* 在用户实验结果中补充 CPM 与尝试字符数的准确 \(t(55)\) 统计量。
* 在主观评分事后比较中补充三项 Wilcoxon \(W\) 和 rank-biserial \(r_{rb}\)。
* 将表 12 首键延迟差值改为 `+90.97` ms，与表内显示均值相减一致。
* 表 16 的 `Reduction (pp)` 列只保留数值，不在单元格中重复百分号。
* 将图 9 的 `Char accuracy` 和图 10 的 `char acc` 统一为 `character recovery`。

## Acceptance Criteria

* [x] 方法部分不再暗示视频也有三次计划重复。
* [x] 表 6 清楚区分静态图像的 content--geometry--repeat 单位和视频的 content--geometry 单位。
* [x] CPM 报告 \(t(55)=-2.93\)，尝试字符数报告 \(t(55)=-2.98\)。
* [x] 可读性、稳定性和舒适度比较分别报告 \(W=58\)、\(16.5\)、\(21.5\)，并报告对应 \(r_{rb}\)。
* [x] 表 12 显示 `+90.97` ms。
* [x] 表 16 的 Reduction 列显示 `94.0`、`94.1`、`94.4`，且无 `%`。
* [x] 图 9 和图 10 不再出现 `Char accuracy`、`char acc`。
* [x] 英文论文完成一次完整 XeLaTeX/latexmk 构建，无未定义引用或文献。
* [x] 最终 PDF 的相关页面经文本提取和视觉检查确认。

## Definition of Done

* 论文源文件和受影响图件已更新。
* 最终 `paper/main.pdf` 已完整重建。
* 构建日志、PDF 文本和页面排版均通过检查。

## Technical Approach

以正式分析报告中的未舍入统计输出为唯一统计依据。正文和表格修改集中在 `paper/main.tex`。图件保留现有数值与版式，仅替换两个指标标签；由于 Windows 工作区中的 `privacy-display/experiments` 是未解析的符号链接，图件标签通过可复核的矢量 PDF 文本补丁完成。

## Decision (ADR-lite)

**Context:** 用户已经逐项确认修复方案，且明确要求不修改实验数据。

**Decision:** 只修正论文表达、统计量披露、单位和指标术语，不改变任何实验结果或分析规则。

**Consequences:** 最终 PDF 内部口径一致；历史中文草稿、实验代码和原始数据保持不变。

## Out of Scope

* 重新运行 OCR、VLM、检测、跟踪或用户实验。
* 修改正式数据库、CSV、JSON 统计结果或分析代码。
* 同步历史中文翻译稿。
* 调整与五项问题无关的论文内容。

## Technical Notes

* Manuscript: `paper/main.tex`
* Figures: `paper/figures/multiengine_ocr.pdf`, `paper/figures/all_attackers.pdf`
* Authoritative statistics: `用户调研实验结果/cleaned/analysis_formal/analysis_report.json`
* Build checks: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`
* Verified build: `paper/main-fixed.pdf` (21 pages; full `latexmk -xelatex -g` build).
* `paper/main.pdf` was open in another process during handoff and could not be overwritten safely; the byte-identical verified build was copied to `paper/main-fixed.pdf`.
