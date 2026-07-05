# Translate Revised Paper into Chinese

## Goal

以当前 `paper/main.tex` 为唯一权威英文源，将多轮修改后的论文完整、准确地同步翻译到 `paper-Chinese/main.tex`，保留现有中文稿的 XeLaTeX 配置、参考文献和资源组织，并生成可成功编译的中文 PDF。

## What I Already Know

* 用户指定目标语言为简体中文，采用精修模式、学术读者和学术文风。
* 最新英文源为 `paper/main.tex`；当前 HEAD 为 `52eddfb`。
* `paper-Chinese/main.tex` 已有一版中文稿，最后一次修改位于提交 `e8916ef`，之后英文源又发生 94 行新增、33 行删除。
* 中文稿已配置 XeLaTeX/CJK 字体，并已有可编译的参考文献与论文资源；应增量同步，不应重建整个目录。
* 最新英文稿新增两个表格标签 `tab:kaleido_compare`、`tab:profile_composition`，以及讨论章节中的“物理层混杂与仿真—实拍差距”“自适应视频攻击者”等内容。

## Assumptions

* 保留英文论文标题、作者占位符、机构信息和关键词的现有处理方式；正文、章节标题、表题、图题和表格文本翻译为中文。
* 技术缩写（OCR、VLM、CSPRNG、SSIM、FPI、UVC 等）保留英文缩写，首次出现按现有中文稿习惯给出中文说明。
* 数值、公式、引用键、标签、图路径、表结构、实验边界与 `TODO` 不得改写或推断。
* `paper-Chinese/refs.bib` 保留原文条目；仅在编译或引用完整性要求时同步缺失条目。

## Requirements

* 对齐最新英文稿的全部论述、实验结果、限制条件和安全边界，不遗漏新增或改写内容。
* 保持 LaTeX 命令、公式、交叉引用、引用键、表格行列、图路径和标签语义一致。
* 复用现有中文术语，并建立统一术语表，避免“掩码/掩模”“恢复率/识别率”等概念漂移。
* 保留中文稿 XeLaTeX 可编译性，不引入 pdflatex 不兼容的中文配置。
* 完成中文学术表达复核，避免欧化长句、过度意译和证据强度变化。

## Acceptance Criteria

* [x] `paper-Chinese/main.tex` 覆盖 `paper/main.tex` 当前全部正文、章节、图表和限制项。
* [x] 英中稿的 `label`、`ref`、`cite`、图路径和表格数量经脚本核对一致，允许仅有语言/排版层差异。
* [x] 所有新增英文修订均已翻译，且没有残留的英文正文句段（专名、缩写、标题与代码除外）。
* [x] `paper-Chinese/refs.bib` 包含全部被引用的 BibTeX 键。
* [x] 使用 XeLaTeX + BibTeX 完整编译成功，日志中无未定义引用或未定义引文。
* [x] 最终 `paper-Chinese/main.pdf` 已更新，并对关键页面做视觉检查。

## Definition of Done

* 精修流程的分析、初稿同步、批判性复核、修订与终稿检查均有可追溯记录。
* 中文论文源文件和 PDF 与最新英文稿内容一致。
* 不修改实验数据或扩大原文主张。

## Out of Scope

* 不重新设计英文论文内容、实验或图表。
* 不翻译图片内部的英文文字，除非它阻碍中文稿理解；此类图片仅记录本地化提醒。
* 不提交或推送 Git，除非用户另行要求。

## Technical Notes

* Source: `paper/main.tex`
* Target: `paper-Chinese/main.tex`
* Bibliography: `paper-Chinese/refs.bib`
* Baseline Chinese correspondence: English `paper/main.tex` at commit `e8916ef`
* Build engine: XeLaTeX + BibTeX
* Translation analysis: `research/01-analysis.md`
* Translation prompt: `research/02-prompt.md`
