# 修复 IEEE Access 论文审稿硬伤与排版问题

## Goal

修复 `paper/main.tex` 中会影响审稿可信度的实验材料数量矛盾、用户研究状态不一致、若干不准确措辞和可见排版问题，并重新编译与目检最终 PDF。

## Requirements

- 补足短曝光威胁的现实动机，但不得把当前手动曝光的 S600 实验误写成手机默认自动曝光实测；应明确“机会型默认抓拍”与“持续对准、主动切换长曝光/录像”的攻击成本差异，同时承认短曝光不是强攻击者边界。
- 修正 Fig. 1(b) 与正文的语义冲突：删除无来源的固定 ``50 ms`` 数字，将 ``Instantaneous sampling`` 改为 ``Short-exposure sampling``，并同步可编辑源文件与论文实际引用的 PDF。
- 将 OCR 主实验的伪全因子描述从 7 profiles 改为实际 6 个主档位，并继续区分主档位与 stripe/glyph/inversion 参数扫描。
- 明确反转帧消融使用 5 个内容项子集、基础叠层配置与主表 deployed 行的样本设计不同，避免把两个 $\alpha=0.2$ 结果当成同一实验重复值。
- 在 per-engine Table 3 中补回 Strong (anti-OCR) 档，并同步正文、图注和必要的图表源数据表述。
- 在 VLM Table 4 中补报 1.5 m 的 ``video:window_mean_best`` 聚合视图；数值必须从同批归档结果重新提取，不能估算。
- 在 §V-F 首次给出基础配置 $n=4$ @ 240 Hz 的 FPI=0.030，再允许结论引用该值。
- 将 deployed 长曝光 96.5% 敏感 token 泄漏转化为明确的部署约束：高风险凭证/账号字段不能依赖 deployed 档，应采用 hardened 或密排小字号策略，同时说明后者仍非完整防护。
- 精简重复的 single-UVC 与“用户研究未做”免责声明：摘要、威胁模型/实验设置和 Limitations 保留完整边界，其余改为局部短语或删除重复句，不能因此扩大论文主张。
- 用标签交叉引用替换标题页脚注的硬编码 ``Section V-D``。
- 将 ``Strong/deployed profile`` 拆成两个独立档位定义。
- 在 Introduction 末尾加入 IEEE 常见的全文结构导览段。
- 扩写 Fig. 1 与 Fig. 5（real-capture bar）的 caption，使其与其余自包含式 caption 风格一致。
- 用户研究结果仍不在本轮补写；保留一份集中同步清单，供正式结果产生后一次性翻转全文状态。

- 明确区分物理真机与软件仿真的 OCR 材料：真机每个几何位置使用 12 个内容项（11 个合成项，每个模板取 1 个变体，加 1 个 CET6 文档）；软件仿真使用全部 120 个合成样本（12 模板 × 10 变体）。
- 全文系统检查 `user study` 相关表述。仓库目前不存在 `study_formal.db`、分析产物或可填入论文的结果，因此不得伪造“已完成”或结果数字；将误写成过去时的 Limitations 恢复为计划/未完成口径，保留 deployed 与 capture-hardened 两类结论的边界差异。
- 将贡献 5 的裸 TODO 改成当前证据所支持的、明确而非占位式的贡献表述；摘要明确说明用户研究尚未完成，而非暗示已有未呈现结果。
- capture-hardened profile 未纳入现有用户研究设计，其视觉代价仍须保留未来验证对冲；数字模型中的 360 Hz 候选也继续保留未验证边界。
- 将 “below 8.3% exact” 修正为 “at or below 8.3% exact”。
- 将 VLM 的 “at the 0° on-axis distance” 修正为 “at the 0° on-axis position across three distances”，并统一相关作用域表述。
- 删除系统设计正文中面向内部归档的历史 `vlm` 标签说明；如需保留，移至 Data and Code Availability，以读者可理解的方式说明。
- 在 Fig. 7 的正文引用处再次明确它来自 synthetic-corpus digital pipeline，避免被误读为真机证据。图本身暂不跨小节搬移，以减少浮动体重排风险。
- 修复 Table 4 超出单栏宽度的问题，优先用简洁且语义无损的内容类型名称与适度缩小列距。
- 用可断行的 LaTeX 路径排版修复长 JSON 文件名导致的 overfull box。
- 不处理 `ieeeaccess.cls` 产生的每页 505 pt 页眉/页脚 overfull 模板噪音和 T1/formata 字体警告。
- 重新编译 PDF；检查非模板 overfull 警告已消失；渲染并目检 Fig. 1、Fig. 2 和 Table 4 所在页，确认无裁切、越界或不可读问题。

## Acceptance Criteria

- [x] Introduction/Threat Model 能回答“攻击者为何可能使用短曝光”，且没有把未做过的 smartphone auto-exposure 实验写成事实。
- [x] Fig. 1(b) 不再出现 ``Instantaneous sampling`` 或无来源的 ``50 ms``，可编辑源和最终 PDF 一致。
- [x] 主档位数量、Strong/deployed 定义、反转帧消融样本/配置说明均与归档元数据一致。
- [x] Table 3 含 Strong 档三引擎真实统计；Table 4 含 1.5 m window-mean-best 三模型及 OCR BoE 的同批真实统计。
- [x] FPI=0.030 在结论之前的指标/权衡正文中定义并给出。
- [x] Discussion 明确 96.5% 敏感 token 泄漏对应的高风险字段部署限制。
- [x] 标题页使用 ``\ref``，Introduction 有结构导览，Fig. 1/Fig. 5 caption 自包含。
- [x] 全文重复对冲有所精简，但摘要、核心证据边界和 Limitations 不被弱化。
- [x] LaTeX 编译成功，新增表格行不越界，Fig. 1 和相关表图经渲染目检可读。
- [x] 全文检索确认用户研究“未完成”口径一致，并在任务记录中保存未来同步位置清单。

- [x] `paper/main.tex` 不再把 120 个合成样本描述为真机 OCR 的每位置材料。
- [x] 324、459、36 等样本数均能由 12 个真机内容项的采集设计自洽解释。
- [x] 全文 `user study` 检索结果与“尚无正式结果”的仓库事实一致，且没有裸的贡献 TODO 或误写为已开展。
- [x] capture-hardened profile 和未实测 360 Hz 候选的感知代价对冲仍在。
- [x] 指定的三处小措辞问题已修复，历史内部标签不再出现在方法正文。
- [x] Fig. 7 的真机小节引用明确标注为数字代理证据。
- [x] 编译日志不再出现 Table 4 的约 20.3 pt 与 JSON 文件名的约 12.7 pt 非模板 overfull。
- [x] 最新 PDF 可成功生成，Fig. 1/2 与 Table 4 经渲染目检无明显缺陷。

## Definition of Done

- 只修改与本次论文修订直接相关的源文件和 Trellis 任务记录，不覆盖用户现有的 `paper/main.log` / `paper/main.pdf` 改动之外的工作。
- 完成 LaTeX 编译、日志检查和关键页面视觉核验。
- 明确记录因正式用户研究数据缺失而不能补写结果的边界。

## Technical Approach

直接对 `paper/main.tex` 做最小、可审计的文字与 LaTeX 布局修改；使用全文检索校对交叉引用与用户研究措辞；以论文现有构建方式编译；用 Poppler 将关键页渲染为 PNG 后目检。

## Decision (ADR-lite)

**Context**: 审稿意见假设用户研究数据即将或已经落地，但当前仓库没有正式数据库和结果产物。

**Decision**: 不虚构数据。先将全文统一到可验证的“研究尚待执行”状态，同时完成所有不依赖用户数据的硬伤与排版修复。Fig. 7 保留当前位置，但在正文明确其数字代理来源。

**Consequences**: 本轮可消除现有自相矛盾和排版缺陷；等正式用户数据产生后，仍需单独执行一次结果落稿与时态转换。

## Out of Scope

- 生成或伪造不存在的用户研究结果、参与者人数和人口统计信息。
- 修改 capture-hardened profile 的用户研究范围。
- 重导出 Fig. 1/2 原始图形；本轮只对最终 PDF 做裁切风险目检。
- 修复 IEEE Access 模板自身的页眉页脚和字体警告。

## Technical Notes

- 目标源文件：`paper/main.tex`。
- 当前用户生成/既有脏文件：`paper/main.log`、`paper/main.pdf`；修改源文件前不覆盖或回滚它们，最终编译会按任务需要更新。
- 用户研究实现与分析脚本位于 `privacy-display/webstudy/`，但仅存在旧的 `study.db`，不存在正式 `study_formal.db`。
- 最终验证：`latexmk -xelatex main.tex` 成功生成 20 页 PDF；目标 20.3 pt 和 12.7 pt overfull 均消失；渲染页 2、5、10、11 后确认 Fig. 1/2、长路径和 VLM 内容表无裁切或越栏。
- Code-spec 判断：本次没有修改 API、数据库、前后端或基础设施契约，也没有形成适用于 backend/frontend 的新编码规范，因此不更新 `.trellis/spec/`。
- 2026-07-05 最终验证：相关 pytest 21 项通过；`latexmk -xelatex` 成功生成 20 页 PDF；无未定义引用/文献；除 IEEE Access 模板既有的 505.12 pt 页眉噪音与标题页 9.27 pt 噪音外，无非模板 overfull；最终页 2、5、9、10、11 已渲染目检。

## Future User-Study Result Sync Checklist

正式用户研究完成后，必须在一次修订中全文检索并同步以下位置，避免完成/未完成时态并存：摘要；贡献 5；Threat Model/Protection Goals；System Design 中感知代价表述；Experimental Setup 的 hardware/metrics；real-capture Finding 3；§V-C User Experience Study 全节及 4 个 TODO 表格；Discussion/Ethics；Limitations 第 1、2 条；Conclusion；Data and Code Availability。机械检索词至少包括 `not yet`、`not-yet`、`planned`、`protocol`、`unvalidated`、`user study` 和 `user-study`。
