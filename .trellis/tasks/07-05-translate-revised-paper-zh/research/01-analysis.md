# 翻译分析

## 文档与语域

本文是一篇 IEEE Access 风格的显示隐私与计算机视觉安全论文。中文译文应保持严谨、克制、证据边界清楚，不把 feasibility study 译成可普遍推广的有效性结论，也不弱化 VLM、长曝光和视频积分攻击所揭示的负面边界。

## 权威源与同步策略

* 权威英文源：`paper/main.tex`（HEAD `52eddfb`）。
* 现有中文基线：`paper-Chinese/main.tex`，其内容大体对应英文提交 `e8916ef`。
* 同步范围：英文源从 `e8916ef` 到 HEAD 的全部变动，以及英中结构核对发现的任何既有遗漏。
* 结构策略：保留中文稿前导区和 XeLaTeX 配置；正文以英文当前结构为准。

## 统一术语

| English | 中文 |
|---|---|
| temporal pixel masking | 时域像素掩模 |
| complementary subframe | 互补子帧 |
| short exposure | 短曝光 |
| long exposure | 长曝光 |
| video temporal averaging | 视频时域平均 |
| capture-hardened profile | 抗拍强化档 |
| deployed profile | 部署档 |
| mask-only | 仅掩模 |
| best-of-engine | 引擎最优结果（表格紧凑处可保留 best-of-engine） |
| character recovery | 字符恢复率 |
| exact match | 完全匹配率 |
| integration attack | 积分攻击 |
| rolling-shutter row mixing | 滚动快门行混合 |
| LCD pixel response ghosting | LCD 像素响应拖影 |
| simulation-to-real gap | 仿真—实拍差距 |
| security frontier/boundary | 安全前沿／安全边界（依语境） |
| normalized mutual information | 归一化互信息 |
| feasibility study | 可行性研究 |
| visual eavesdropping | 视觉窃听 |

## 高风险翻译点

* 数值区间、样本量和百分比必须逐字对齐，尤其是 5.0\% 的置信区间、67 ms 视频边界、长曝光反常增益以及 VLM 77.8\% 完全匹配率。
* “approaching but not conclusively meeting”必须译为“接近但不能确定达到”，不可简化为“达到”。
* “more favorable to the attacker”描述实验条件偏向攻击者，应译明逻辑方向。
* 物理层混杂分别有“有利于攻击者”和“有利于防御者”两个方向，不可合并。
* “proxy”统一译为“代理指标”，并明确其不是经验证的感知阈值或用户体验证据。
* LaTeX 中的百分号、下划线、波浪空格、公式与引用键原样保留。
