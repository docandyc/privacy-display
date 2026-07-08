# 根据 Claude 审稿意见修订中英文论文

## Goal

在不改动原始实验数据、不夸大证据强度的前提下，同步修订 `paper/main.tex` 与 `paper-Chinese/main.tex`，解决 Claude 审稿中指出的披露不对称、不可复现数字、术语漂移、贡献过度包装和局限性遗漏，并保证中英文口径一致、LaTeX 可编译。

## What I already know

- Claude 已核验主要数值与表 3--9，一般算术正确；关键缺陷集中在论证、披露与可追溯性。
- d0.5/15° 的 0.49 ms 采集明显欠曝，且对所有受保护条件产生单向有利于防守方的偏差。
- 原稿只对 deployed short 报告了排除该点的敏感性结果，未同步披露偏差更大的 deployed/hardened 视频积分与 hardened short。
- 归档结果与 `ablation_noise.py` 均不能追溯 89.7% 数值；95.2% 是逐样本最强攻击汇总，不是纯 `temporal_average_cycle` 数值。
- 当前英文稿已有未提交的用户实验占位、表格与图引用修改；这些属于用户现有工作，必须完整保留。
- Rainbow 与 Lim 两条参考文献均可核验；现有 Rainbow 文字把环境照明防盗版误写成屏幕时域重编码延伸，Lim 作者字段不准确。

## Assumptions

- 用户要求“根据 Claude 审稿意见修复”即授权落实全部可由现有证据支持的修改，而非仅修两个最高优先级问题。
- 本任务不新增实验、不伪造用户研究结果；对于证据不足的主张，采用删除、降级或明确局限，而不是补造解释。
- 保留全 9 几何条件的主表作为完整语料汇总，同时在摘要、正文、讨论与结论并列报告排除欠曝点的敏感性结果。

## Requirements

- 删除中英文稿中的 89.7% 噪声收益及其衍生论证；明确没有隔离证据证明噪声改善积分攻击或 VLM 结果。
- 报告排除 d0.5/15° 后的敏感性结果：deployed short 16.7% [14.7, 18.8]，hardened short 5.6% [4.8, 6.4]，deployed video 79.7% [75.4, 83.8]，hardened video 53.9% [48.0, 59.9]。
- 在摘要和结论突出敏感 token 风险：deployed short 24.0%，long 96.5%。
- 将长曝光反转机制统一表述为避免饱和/裁剪、落入传感器未饱和近线性响应区，避免混用 linear range 与 dynamic range。
- 删除无数据支撑的“3.91 ms 比典型自动曝光更有利于攻击者”判断，说明未记录环境照度，无法外推机会性手机自动曝光。
- 将约 67 ms 的四帧视频攻击明确为低门槛现实攻击，不包装为有意义的安全分界。
- 将跨任务检测/跟踪、VLM 与可用性代理降级为诊断/边界证据；不作为独立贡献过度包装。
- 补充检测器降幅差异的谨慎解释，明确是模型尺度/架构相关假设而非因果证明。
- 将 VLM 对策改为未验证研究假设，并指出互补诱饵仍受全周期求和约束。
- 将卡方检验表述为实现健全性检查，不作为密码学或安全证据。
- 对 0.5 m VLM 两次会话并列报告范围，避免只靠事后“充分曝光”标准。
- 补充 ASCII-only/CJK 未测与 ambient illuminance 未记录的局限。
- 修正并补充 Rainbow、Lim 参考文献元数据与相关工作描述。
- 中英文稿的数字、限定语、贡献结构和局限性逐项对齐。

## Acceptance Criteria

- [x] `rg` 不再在两稿中找到 89.7% 或把 95.2% 称为纯 temporal-average 结果的表述。
- [x] 摘要、结果、讨论、结论均披露欠曝光点的方向性影响，且数值与原始 JSON 重算一致。
- [x] hardened `<5%` 目标明确判定为未达到，而非“接近达标”式暗示。
- [x] 两稿长曝光机制统一为 saturation/clipping avoidance 与 unsaturated near-linear response region。
- [x] 两稿不再断言实验曝光比典型手机自动曝光更强。
- [x] 两稿贡献列表不把探索性跨任务与全非支配 Pareto 代理包装为独立主要贡献。
- [x] `refs.bib` 两版一致，Rainbow/Lim 元数据可追溯。
- [x] 英文与中文 LaTeX 均成功编译，无新增 undefined reference/citation。
- [x] 用户原有英文用户实验改动保持不丢失。

## Verification Record

- 2026-07-06：英文 `latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex`，exit 0，23 页。
- 2026-07-06：中文同命令，exit 0，17 页。
- 两份 `main.log` 均无 undefined citation/reference 或 `Label(s) may have changed`。
- 两份 PDF 文本均无 `[?]`、`(?)` 或 `??` 引用占位。
- `git diff --check` 通过；两份 `refs.bib` 字节一致。
- 未更新 `.trellis/spec/`：本次新信息是论文数据与表述的任务特定证据，已记录于 `research/review-evidence-audit.md`；现有 LaTeX build guide 已覆盖可复用的构建与引用核验流程。

## Out of Scope

- 新增或重跑相机、VLM、用户实验。
- 填写作者、单位、伦理、存档 URL 等现有 TODO。
- 修改与审稿意见无关的 WebStudy 分析脚本和论文图生成脚本。
- 提交或推送 Git 变更，除非用户后续明确确认。

## Technical Notes

- 审稿意见：`/Users/andyhuang/.codex/attachments/adbe08bc-244f-4f07-906c-1bf3c9edf99d/pasted-text-1.txt`
- 英文稿：`paper/main.tex`
- 中文稿：`paper-Chinese/main.tex`
- 结果重算与文献核验：`research/review-evidence-audit.md`
- 当前工作树中 `paper/main.tex` 的已有差异位于用户体验研究部分，实施时避开覆盖。

## Definition of Done

- 逐条审稿映射已落实或给出基于证据的“不修改”说明。
- 两稿完成内容一致性、语言质量和 LaTeX 编译核验。
- 只改动本任务所需文件，不纳入用户既有无关改动。
