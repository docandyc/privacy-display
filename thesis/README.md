# 本科毕业论文（LaTeX 源）

《基于视觉暂留与时间分片掩模的显示器隐私保护系统的设计与实现》

## 编译

需要 TeX Live（含 XeLaTeX + ctex），macOS 已用系统字体（宋体 Songti SC / 黑体 Heiti SC / 楷体 Kaiti SC / Times New Roman）。

```bash
cd thesis
latexmk -xelatex main.tex      # 自动跑两遍生成目录
# 或手动：xelatex main.tex && xelatex main.tex
```

输出 `main.pdf`（约 35 页）。

## 结构

```
thesis/
├── main.tex              # 主文件：版式、字体、页眉、目录、编号规则
├── cover.tex             # 封面 + 声明授权页
├── chapters/
│   ├── abstract.tex      # 中/英文摘要与关键词
│   ├── ch1.tex           # 绪论
│   ├── ch2.tex           # 相关技术与原理
│   ├── ch3.tex           # 威胁模型与系统总体设计
│   ├── ch4.tex           # 核心模块设计与实现
│   ├── ch5.tex           # 实验与结果分析
│   ├── conclusion.tex    # 结论
│   ├── references.tex    # 参考文献（GB7714，顺序编码制）
│   └── acknowledgements.tex
└── figures/              # 取自 privacy-display/experiments/results
```

## 格式说明（对照学校撰写规范）

- A4，左 30mm、其余 28mm；页眉"浙江水利水电学院2026届毕业设计（论文）"五号楷体。
- 章标题三号宋体加粗居中、节小三加粗居左、条四号加粗居左；正文小四宋体、固定 22 磅行距、首行缩进 2 字符。
- 图题在下、表题在上，五号宋体居中；表格为三线表；图表按章编号（图1-1、表1-1）。
- 前置部分（摘要/目录）用罗马页码，正文起用阿拉伯页码，页脚居中。

## 待办（提交前请核对）

1. **封面信息**：补学号、姓名、指导教师。
2. **参考文献**：当前为真实可查的国际文献与标准（17 条，外文为主，满足"≥15 篇、外文≥2 篇"）。学校要求参考文献须与**开题报告/任务书一致**，请据此增删并核对页码、补充本课题相关中文文献。
3. **实验数字口径**：全文已统一引用固定 benchmark/语料结果（FPI 0.030、ΔE≈0.37、Tesseract/EasyOCR/PaddleOCR 均为 120 样本全量复测，单子帧 OCR 约 0.0%、bootstrap 95%CI 上界低于 0.1%、配对降幅 93.9%--94.9%、单子帧词级准确率/exact-match/敏感 token 恢复率均为 0.0%、完整周期叠加 100%、120 样本强攻击逐样本择优字符恢复率 95.2%、敏感 token 恢复率 98.6%），与 `privacy-display/experiments/results/*.json` 一致；若重跑实验请同步更新。
