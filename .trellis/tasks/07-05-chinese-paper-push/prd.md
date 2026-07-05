# 提交中文论文版本并推送

## Goal

把 `paper-Chinese/` 里的中文论文版本及其相关导出文件整理为一次提交，并推送到 GitHub；同时避免把与本次目标无关的改动混进去。

## What I already know

* 用户明确希望提交 `paper-Chinese` 中的中文论文版本，以及相关导出文件，一起推送到 GitHub。
* 当前工作区里除了 `paper-Chinese/` 外，还存在若干其他未提交改动，需要单独判断是否纳入本次提交。
* `paper-Chinese/` 看起来是一个完整的论文导出包，包含 `main.tex`、`main.pdf`、`main.xdv`、`main.aux`、`main.log`、图表资源和参考文献等。

## Assumptions (temporary)

* 本次只提交中文论文相关文件，不纳入其他任务的 WIP 改动。
* 导出文件（PDF、aux、log、xdv、synctex 等）需要和源文件一起提交，以保证版本可复现。

## Open Questions

* 无硬性阻塞问题；若工作区还有无关脏文件，将在提交前单独列出供确认。

## Requirements (evolving)

* 提交 `paper-Chinese/` 下的中文论文版本及其相关导出文件。
* 不要把其他任务相关改动自动并入本次提交。
* 最终把选定文件推送到 GitHub。

## Acceptance Criteria (evolving)

* [ ] `paper-Chinese/` 的中文论文版本及相关导出文件已纳入一次或多次逻辑清晰的提交。
* [ ] 任何与本次目标无关的脏文件都已明确排除或单独确认。
* [ ] 本地提交已完成，并已推送到远端仓库。

## Definition of Done

* 提交范围清晰，没有把无关改动混入。
* 若需要，提交说明能准确描述中文论文版本与导出文件。
* 推送成功。

## Out of Scope

* 不修改论文内容本身。
* 不处理其他未相关的实验脚本、测试文件或临时文件，除非用户明确要求。

## Technical Notes

* 目标目录：`paper-Chinese/`
* 相关导出件：`main.pdf`、`main.aux`、`main.log`、`main.xdv`、`main.fls`、`main.fdb_latexmk`、`main.bbl`、`main.blg`、`main.synctex.gz` 等（以实际脏文件为准）
* 需在提交前检查 `git status --porcelain`，区分本次可提交文件与无关文件。
