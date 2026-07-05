# 补充 Table 3 图表的 mask 系列

## Goal

让 Table 3 下方的真机短曝光分引擎 OCR 柱状图完整覆盖表中的五个 profile，避免图表只展示其中三组而与表格范围不一致。

## What I already know

- `paper/main.tex` 的 Table `tab:real_ocr_engine` 已包含 Original、Mask only、Mask + noise、Deployed、Capture-hardened 五组数据。
- `privacy-display/experiments/results/real_capture_per_engine.json` 已包含 `mask_only` 与 `mask_noise` 的三引擎均值和 95% bootstrap 区间。
- `fig_s5_real_engine_ocr.py` 当前 `PROFILES` 只配置 Original、Deployed、Capture-hardened，缺失来自生成脚本而不是数据。
- 用户给出的页面截图明确要求把 mask only 和 mask noise 放入该图。

## Requirements

- 按 Table 3 顺序绘制五组 profile：Original、Mask only、Mask + noise、Deployed、Capture-hardened。
- 继续从 `real_capture_per_engine.json` 读取数值和误差线，不硬编码表格数值。
- 保持单栏图宽、0–100% 纵轴、三 OCR 引擎横轴以及现有论文绘图风格。
- 调整柱宽与图例布局，使五组数据在单栏排版中清晰可辨。
- 同步更新正文和图注中“只可视化三种 profile”的过时表述。
- 重新生成 `paper/figures/real_engine_ocr.pdf` 并编译论文核验页面。

## Acceptance Criteria

- [x] 图中及图例可见五个 profile，且顺序与 Table 3 一致。
- [x] Mask only 的三引擎柱高约为 4.2%、15.6%、3.2%。
- [x] Mask + noise 的三引擎柱高约为 11.0%、18.1%、4.8%。
- [x] 所有五组均保留 95% bootstrap 误差线。
- [x] 图例不遮挡绘图区，标签无裁切，论文可成功编译。

## Out of Scope

- 不修改 Table 3 的实验数值、统计口径或原始结果 JSON。
- 不重绘其他论文图。
- 不覆盖 `paper/main.tex` 中与本任务无关的现有未提交修改。

## Technical Notes

- 生成脚本：`privacy-display/experiments/paper_figures/fig_s5_real_engine_ocr.py`
- 数据：`privacy-display/experiments/results/real_capture_per_engine.json`
- 输出：`paper/figures/real_engine_ocr.pdf`
- 引用文本：`paper/main.tex` 的 `fig:real_engine_ocr` 前导段与 caption。
