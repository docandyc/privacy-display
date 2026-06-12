# Harden G3/G5 experiments with OCR metrics

## Goal

Fix three honesty/quality issues found while reviewing the second-round disclosure-gap
work (G2/G3/G5), so the experiments measure the metric that actually matters (OCR) and
the documentation does not overstate protection.

## Issues

1. **G3 离轴攻击只测 PSNR/SSIM，未测 OCR**；且离轴 SSIM 下降（0.089）来自可逆的
   全局衰减/色偏/位移，而非视角差异化掩模本身。整周期平均时每个区域无论掩模如何
   都各自还原 → 掩模差异化对全周期对齐攻击者**无密码学保护**。需补 OCR + 攻击者
   校正对照，并如实改写结论。
2. **G5 U-Net 实验的 inpaint baseline SSIM=0.93 与 B2 表的 0.026 自相矛盾**：根因是
   B2 子帧带 pedestal=8（`gray<1` 缺失检测失效→inpaint 空操作），新实验子帧干净
   （masked=0）且 SSIM 被白底主导。两者都未测 OCR。需补 OCR（真实隐私指标）并在文档
   中解释差异。
3. **G2 检测实测 mAP50=0.40 揭示"检测防御弱于 OCR 防御"**（0.40 vs 0.0%），应作为
   独立发现强调，而非埋在表中。

## Requirements

* `experiments/view_attack.py`：报告 OCR（原图上限 / 正视恢复 / 离轴朴素 / 离轴校正后），
  保留 SSIM/PSNR；新增"强攻击者校正"（逐区域增益归一化 + 反向位移）。
* `src/attack/camera_simulator.py`：新增 `off_axis_correction()`，可被实验与测试复用。
* `experiments/unet_reconstruction.py`：为 U-Net 重构、inpaint baseline、holdout 原图
  补 OCR 字符准确率；report 增 SSIM 背景主导的说明。
* 文档（`改进文档.md`、`技术交底书实现情况Review.md`）：如实回填 OCR 数据与三条诚实结论。
* 重跑两实验更新 JSON；`pytest tests/` 全绿；新增 off_axis_correction 烟雾/合理性测试。

## Acceptance Criteria

* [ ] view_attack / unet_reconstruction JSON 含 OCR 字段
* [ ] 文档中 G3 结论改为"离轴下降可逆、掩模差异化无保护"；G5 用 OCR 复核；G2 标注检测弱于 OCR
* [ ] 全量 pytest 通过

## Out of Scope

* 物理 LCD 视角响应的真实建模（仍属 PoC 范围外，文档声明）
* 更强 U-Net / 更大训练（仍定位为学习攻击下界）

## Technical Notes

* 受影响文件：`experiments/view_attack.py`、`experiments/unet_reconstruction.py`、
  `src/attack/camera_simulator.py`、`tests/test_disclosure_gaps.py`、`改进文档.md`、
  `技术交底书实现情况Review.md`。
* OCR 走 `OCREvaluator`（tesseract，已装），不可用时降级记 -1。
