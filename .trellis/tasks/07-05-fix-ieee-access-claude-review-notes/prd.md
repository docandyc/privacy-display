# Fix IEEE Access review wording and references

## Goal

修复用户提供的 4 个 IEEE Access 论文审稿/自审问题，降低读者误读、引用错位和数据括注不精确带来的审稿风险。范围限定为论文正文与 BibTeX 的最小必要改动。

## Requirements

* 在 §IV-F 反转帧段落中，将 “measured values of 31.25 and 125 ms” 明确为相机长曝光时间，避免误读为显示周期。
* 在 §II-B 显示隐私保护相关工作中补充 HideScreen：Chen, Lin, Wang, Shin, “Keep Others from Peeking at Your Mobile Device Screen!”, MobiCom 2019。
* 对 HideScreen 做一句边界区分：它防一定距离外的人眼肩窥/空间域，不针对相机短曝光或机器识别/时间域。
* 调整 Ponemon/3M 白皮书引用负载：保留其支撑 visual hacking 攻击普遍性；从“物理防窥膜只限制视角、挡不住正面相机”的两处论证中移除 Ponemon 引用，改为常识陈述或由 HideScreen 相关工作支撑。
* 修正 §V-B 发现 4 中常规 OCR temporal-average 括注范围，避免 “48.4--50.7% char” 被理解为覆盖未列出的 1.0 m 数据。

## Acceptance Criteria

* [x] paper/main.tex 中不再出现 “reports measured values of 31.25 and 125” 这类歧义表述。
* [x] paper/main.tex 的 related work 显示隐私保护段包含 HideScreen 及与本文的空间域/时间域区别。
* [x] paper/refs.bib 包含可追溯的 HideScreen MobiCom 2019 条目。
* [x] Ponemon 引用只用于 visual hacking 攻击普遍性，不再支撑防窥膜光学特性。
* [x] §V-B 的括注限定到表内列出的距离，或改写为不覆盖 1.0 m 的表述。
* [x] LaTeX/BibTeX 编译或静态引用检查无新增未定义引用。

## Definition of Done

* 修改范围最小，只触碰本次任务相关正文、参考文献和 Trellis 任务记录。
* 保持论文现有保守论证风格，不扩大保护能力声称。
* 完成后报告具体修改文件与验证结果。

## Technical Approach

直接编辑 paper/main.tex 和 paper/refs.bib。引用采用可追溯 DOI/ACM 信息；不新增未经核实的文献。优先运行论文目录下可用的 LaTeX 编译命令；若环境缺少工具，则做静态 grep 检查并明确说明。

## Out of Scope

* 不重画图、不改实验数据、不改表格数值本身。
* 不处理现有 unrelated 图稿 WIP。
* 不提交 git commit，除非用户另行确认。

## Technical Notes

* 用户提供来源：ACM DL DOI https://dl.acm.org/doi/10.1145/3300061.3300119；PDF https://rtcl.eecs.umich.edu/rtclweb/assets/publications/2019/chen-mobicom19.pdf。
* 初步定位：paper/main.tex 包含四处正文修改点；paper/refs.bib 包含现有 Ponemon 条目，需新增 HideScreen。
