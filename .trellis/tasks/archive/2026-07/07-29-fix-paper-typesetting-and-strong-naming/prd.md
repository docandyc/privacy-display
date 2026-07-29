# 修复论文表格排版与 Strong 命名一致性

## Goal

修复当前英文 IEEE Access 稿件中的三个可见排版/文字问题，并明确区分可复用的 `strong` profile 与真机采集使用的低幅度 overlay 实例，避免 caption、表格单位和实验配置名称继续引起误读。

## What I already know

* 目标源文件是 `paper/main.tex`。
* Table 12 caption 中的 `\$\Delta\$` 在当前 PDF 中显示为错误的重音符号，而表头中的 Delta 正常。
* Table 4 caption 的句子把“holding geometries fixed”和“not independent population samples”错误地连成了从句。
* Table 16 的 Reduction 数值是绝对百分点差，应在列名中明确 `(pp)`。
* `paper/main.tex` 的可复用 `strong` profile 在论文叙述中与真机采集的显式 0.10/0.12 覆盖混用；代码中的 CLI/web 默认值为 0.18/0.22，采集实例为 0.10/0.12。
* 仓库当前已有用户未提交的相关论文和实验文件修改；本任务只应追加目标修复，不覆盖其他改动。

## Requirements

* 让 Table 12 caption 在编译 PDF 中可靠显示 `Δ = Masked − Control`。
* 将 Table 4 caption 拆成语法完整、语义清楚的句子。
* 将 Table 16 列名改为带有 `(pp)` 的明确单位表述。
* 将真机采集用的 0.10/0.12 overlay 实例命名为 `Strong-overlay`（必要时保留内部含义清楚的 `strong@overlay`），并同步更新 Table 3、真机结果表和正文中指向该采集实例的表述；可复用 CLI `strong` profile 继续保留原名并说明其默认幅度。
* 不改变任何实验数值、统计定义、表格结构或其他非目标内容。

## Acceptance Criteria

* [ ] `paper/main.tex` 中不存在 Table 4 的断裂句式。
* [ ] Table 12 caption 的源文本使用不会被 caption medium math font 错误映射的 Delta 写法，编译后的 PDF 视觉检查显示真正的 `Δ`。
* [ ] Table 16 表头明确写出 `Reduction (pp)` 或等价的绝对百分点单位。
* [ ] `Strong` 与 `Strong-overlay` 的使用边界清晰：可复用 profile 与物理采集实例不再指向同一个含混名称。
* [ ] 使用 `paper/build.sh` 完整构建成功，且最终日志没有未解析引用、交叉引用或标签变化警告。
* [ ] 从最终 PDF 提取的文字包含修复后的 caption/表头关键短语，且不再包含错误的 Table 4 句式。

## Definition of Done

* 源稿修改完成并通过完整 LaTeX/BibTeX 构建。
* 对 Table 4、Table 12、Table 16 进行 PDF 视觉或文本核验。
* 记录本次验证结果，并保留用户已有的非目标工作区改动。

## Out of Scope

* 不重算 OCR、用户研究或其他实验结果。
* 不修改 Python/JavaScript profile 默认值或归档数据标签。
* 不处理与本次四项问题无关的图、引用、统计和其他稿件内容。

## Technical Notes

* 适用构建规范：`.trellis/spec/guides/latex-paper-build-thinking-guide.md`。
* 论文目录没有独立的 `build.sh`；本次使用 `paper/` 目录中的 `latexmk -xelatex -g main.tex` 执行 XeLaTeX/BibTeX/xdvipdfmx 完整轮次。
* 已确认 `paper/ieeeaccess.cls` 的 table caption 使用 `\mediummath`，而表格主体使用 `\regularmath`；Table 12 的 Delta 修复应显式采用正常的 math version 或等价可靠写法。
