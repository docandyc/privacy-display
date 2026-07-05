# PRD: Write Undergraduate Thesis in LaTeX

## Goal
在 `thesis/` 目录用 XeLaTeX 撰写本科毕业论文《基于视觉暂留与时间分片掩模的显示器隐私保护系统的设计与实现》。

## Requirements
- 结构：封面、声明、中英摘要、目录、第一~五章（绪论/相关技术/需求与总体设计/核心模块实现/实验与分析）、结论、参考文献、致谢
- 格式：A4，左 30mm 其余 28mm；页眉"浙江水利水电学院2026届毕业设计（论文）"五号楷体；章标题三号宋体加粗居中；节小三宋体加粗居左；正文小四宋体固定 22 磅行距、首行缩进 2 字符；图题在下表题在上、五号宋体、三线表；参考文献 GB7714、五号；前置部分罗马页码、正文阿拉伯页码
- 内容：以 privacy-display PoC 真实实验数据为准（FPI 0.030/ΔE 0.006/多引擎 OCR 0%/完整周期叠加 100% 等诚实结论）
- 产出：可用 xelatex 编译通过的 PDF

## Acceptance
- latexmk -xelatex 编译无错误，PDF 含完整章节
- 实验数字与 experiments/results/*.json 一致
