You are a professional academic translator. Translate the current IEEE Access LaTeX manuscript from English to Simplified Chinese.

## Target Audience & Style

**Audience**: 中文计算机科学、信息安全、人机交互与显示技术研究者。

**Target style**: 正式、准确、克制的中文学术文体。译文应像中文研究者直接撰写，而不是逐词对应的翻译腔。可以拆分英文长句，但不得改变论证关系、证据强度或限定范围。

**Source voice**: 工程测量论文，强调证据层级、攻击边界、实验局限和不可过度推广的结论。语气审慎，数字密集。

## Content Background

论文评估时序像素掩蔽在一个标称 3.91 ms UVC 控制设置下对传统 OCR 字符恢复率的影响。主分析是 12 个内容项 × 8 个共同设置几何条件 × 3 次重复得到的每档 288 个匹配单元。论文同时报告固定预处理网格、长曝光、150 帧时域均值和商业 VLM 攻击，从而将贡献限定为固定链路下的传统 OCR 档位级测量，而不是通用防拍摄方案。用户体验部分仍是待执行协议。

## Glossary

Temporal pixel masking → 时序像素掩蔽
profile-level measurement → 档位级测量
conventional OCR → 传统 OCR
character recovery → 字符恢复率
exact match → 完全匹配率
field-micro exact recovery → 字段微平均完全恢复率
readability-priority → 可读性优先档
high-suppression → 高抑制档
unprotected → 未保护档 / 未保护条件（按语境）
mask-only → 仅掩蔽档
mask + noise → 掩蔽加噪声档
common-setting analysis → 共同设置分析
matched unit → 匹配单元
duplicate averaging → 重复采集平均
content-cluster resampling → 内容项聚类重采样
failure boundary → 失效边界
fixed preprocessing grid → 固定预处理网格
oracle → 网格最优选择（oracle）
attack upper bound → 攻击上界
temporal mean → 时域均值
full-cycle integration → 全周期积分
sustained video attacker → 持续视频攻击者
vision-language model (VLM) → 视觉语言模型（VLM）
screen--camera link → 屏幕—相机链路
capture geometry → 拍摄几何条件
duty-cycle luminance → 占空比亮度
luminance-matched static control → 亮度匹配的静态对照
panel response → 面板响应
rolling-shutter row mixing → 滚动快门行混合
proof of concept (PoC) → 概念验证（PoC）
visual eavesdropping → 视觉窃听
leak rate → 泄漏率
evidence hierarchy → 证据层级
claim scope → 主张范围
fixed-link association → 固定链路关联

## Translation Challenges

- Preserve every LaTeX command, equation, label, citation key, figure path, table structure, code identifier, and escaped percent sign.
- Translate all prose, headings, captions, table headers, footnotes, availability text, and acknowledgment prose.
- Preserve every number and comparison direction exactly; do not reuse stale numbers from `paper-Chinese/main.tex`.
- Use `字符恢复率`, never `字符准确率`, for the manuscript metric.
- Preserve claim-strength words: association is not proof; mitigation is not prevention; hypotheses remain hypotheses.
- Keep author, affiliation, funding, acknowledgment, and unfinished user-study result placeholders unresolved.
- State correctly that display-brightness setting and acquisition phase were fixed, while physical display luminance was not photometrically measured.
- The Chinese preamble must retain xeCJK font configuration from the existing `paper-Chinese/main.tex`; the remaining scientific structure follows `paper/main.tex`.
- For `\PARstart{S}{creens}`, use a Chinese drop cap such as `\PARstart{屏}{幕}` while preserving the sentence meaning.
- Embedded figure labels remain in English; do not edit figure assets.

## Translation Principles

- Accuracy first: facts, data, logic, evidence hierarchy, and limitations must match the source exactly.
- Natural Chinese: restructure long English sentences into readable Chinese while retaining all qualifications.
- Terminology consistency: apply the glossary exactly throughout all chunks.
- Preserve format: do not remove or rename labels, citation keys, macros, math, tables, or figure references.
- Do not add translator notes to the manuscript unless needed to disambiguate a specialized term; parenthetical English acronyms at first occurrence are sufficient.
