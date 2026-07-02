# 绘制论文图一与图二原理图

## Goal

根据论文 `paper/main.tex` 的 Figure 1、Figure 2 占位说明与 `privacy-display` 实际实现，生成一组风格统一的论文原理图：图一用于单栏展示威胁场景与核心概念，图二用于双栏通栏展示完整系统管线。

## What I already know

- ChaCha20 CSPRNG 与无偏拒绝采样生成像素槽位矩阵及互补掩模 `M_k`；Fisher–Yates 单独负责子帧的时序输出置换。
- 子帧满足 `I_k = I ⊙ M_k + N_k`、`ΣM_k = 1`、`ΣN_k = 0`。
- GPU 完成掩模、噪声与亮度补偿合成，时序控制器按 VBlank 在 240–360 Hz 下输出。
- 人眼在约 50 ms 时间窗口内积分并感知完整图像；相机短曝光只采到单个或局部子帧，OCR/检测难以恢复内容。
- 随机掩模是主防御，互补对抗噪声为二级强化；anti-OCR 与反色帧属于可选增强。

## Assumptions

- 使用英文标签，以便论文英文终稿直接采用。
- 使用白底、扁平、近似矢量的科学插图风格，保证缩放到双栏通栏后仍清晰。
- 生成图本身不含论文 caption；caption 由 LaTeX 排版。
- 图一使用单栏友好的双面板构图，并与图二保持同一视觉语言。

## Requirements

- 横向宽幅构图，适配 `figure*`。
- 主链路包含：Input Frame → Secure Mask Generation → Complementary Subframes → GPU Composition / Optional Enhancements → High-Refresh Display。
- 观察端形成两条明确分支：Human Visual System 与 Camera / Machine Vision。
- 显示核心公式与时间尺度，但避免过度文字化。
- 视觉上区分“可读恢复”与“不可读采样”。
- 不使用照片、3D、渐变、装饰背景、水印或虚构指标。

## Acceptance Criteria

- [x] 技术流程与代码实现一致，明确区分像素槽位生成与 Fisher--Yates 时序置换。
- [x] 关键英文标签可读、无明显拼写错误。
- [x] 人眼积分和相机单帧采样的差异一眼可辨。
- [x] Figure 2 提供内嵌可编辑 Draw.io XML 的矢量 PDF；Figure 1 提供高分辨率 PNG。
- [x] 最终文件保存到 `paper/figures/`，不覆盖现有文件。

## Out of Scope

- 不修改业务代码。
- 不替换 `paper/main.tex` 中现有占位图，避免覆盖用户未提交的论文编辑。
- 不把完整攻击评测或所有可选档位塞入图中。

## Figure 1 Requirements

- 左面板只展示手机对屏幕实施物理拍摄的视觉窃听场景，不出现智能眼镜。
- 右面板只解释感知非对称：人眼对高速互补子帧做时间积分，相机短曝光只采到单个碎片。
- 使用英文标签，单栏缩放后仍可读。
- 不重复图二中的 CSPRNG、GPU、噪声与时序实现细节。
- 保存为 `paper/figures/concept_threat_gpt_image.png`，不覆盖现有文件。

## Technical Notes

- 论文占位：`paper/main.tex:189-198`。
- 核心实现：`src/core/mask_generator.py`、`noise_injector.py`、`subframe_composer.py`、`timing_controller.py`、`gpu/renderer.py`。
- 参考视觉样例：`privacy-display/experiments/results/demo_n4_grid.png`。
- Figure 2 新文件名：`paper/figures/method_pipeline_ieee.drawio.pdf`（内嵌可编辑 Draw.io XML）及 `method_pipeline_ieee.drawio.png`（3000 px 宽预览）。
- Figure 1 文件名：`paper/figures/concept_threat_gpt_image.png`；本轮另调用 GPT Image 生成候选版本供视觉复核。
- IEEE 与代码映射研究：`research/ieee-figure-and-code-mapping.md`。
