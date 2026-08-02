# 提交论文图表修复并包含 Likert 图

## Goal

提交当前论文修订结果，并把修复后的 `paper/figures/study_ratings_likert.pdf` 一并纳入版本，使术语、Likert 误差棒和相对降幅口径的修复在源稿与图稿中可复现。

## What I already know

* `paper/main.tex` 已包含三处修订：character recovery 口径、Fig. 7 截断误差棒图注、以及 rounded-mean reduction 的明确说明。
* `paper/main.pdf` 已重新生成，且包含修订后的图和正文。
* `paper/figures/study_ratings_likert.pdf` 被 `paper/.gitignore` 忽略，需要显式加入提交。
* LaTeX 临时文件（aux、log、fls、fdb_latexmk、xdv）不属于本次提交范围。

## Requirements

* 保留当前 `paper/main.tex` 的论文修订。
* 将修复后的 `paper/figures/study_ratings_likert.pdf` 强制加入版本。
* 提交前核验 PDF 文本和图表资产存在，且无未定义引用或致命编译错误。
* 创建一个清晰、可回溯的 Git commit。

## Acceptance Criteria

* [ ] `paper/main.tex` 与修复后的 `paper/figures/study_ratings_likert.pdf` 已暂存。
* [ ] `paper/main.pdf` 与源稿一致并保留在提交中。
* [ ] 提交中不包含 LaTeX 临时文件。
* [ ] 最终 commit 成功创建，工作区只剩明确说明的非本任务改动（如有）。

## Out of Scope

* 不重算实验数据。
* 不改变图表统计方法或论文结论。
* 不修改与本次修复无关的源码或图表。

## Technical Notes

* 相关正文：`paper/main.tex`。
* 相关图稿：`paper/figures/study_ratings_likert.pdf`。
* 由于图稿被忽略，使用 `git add -f` 显式纳入。
