# 论文表格单位通篇审查与修订记录

审查与修订对象：`paper/main.tex`（2026-09-02 现行稿）及其编译稿 `paper/main.pdf`。

全文共 19 张表。第一轮审查逐项核对了 LaTeX 源码及 PDF 中表 1--19 的实际可见表头。根据作者随后确认的统一口径，所有百分比指标和差值均使用 `%`，不采用其他差值单位；物理量和无量纲指标仍按其自身含义标注。

## 本轮统一规则

- 百分比指标及相关差值：列头统一标 `(%)`，数据区只保留数字。
- 物理单位：放在列头，例如 `Distance (m)`、`Latency (ms)`、`Width (px)`。
- 区间水平与数值单位分开表示，例如 `Recovery (\%) [95\% CI]`。
- SSIM、`\Delta E_{00}` 和归一化 `\alpha` 系数不添加 `%`。
- 计数保留 `N`、opportunities、valid/planned 等分母或分析单位。

## 逐表结果

| 表 | 标签与表头位置 | 最终处理 |
|---|---:|---|
| 表 1 | `tab:kaleido_compare`，132 | 定性比较，无定量单位，保留。 |
| 表 2 | `tab:profile_definitions`，233 | 组件启用情况，无定量单位，保留。 |
| 表 3 | `tab:profile_composition`，289 | `Cell (px)`、`Stripe width (px)` 已正确；`\alpha` 系数保持无量纲，保留。 |
| 表 4 | `tab:real_ocr_common`，325 | 已改为 `Mean char recovery (\%)` 和 `Unprotected $-$ profile (\%)`；数据区移除重复 `%`。 |
| 表 5 | `tab:explicit_fields`，342 | 已改为 `Field micro (\%; 486 opp.)` 和 `Sample macro (\%)`；数据区移除重复 `%`。 |
| 表 6 | `tab:real_ocr_full_pool`，359 | 已为 character recovery、exact match、leak rate 三列补 `(%)`；数据区移除重复 `%`。 |
| 表 7 | `tab:real_ocr_engine`，435 | 原表头已有 `Char (\%)`、`Exact (\%)`，保留。 |
| 表 8 | `tab:preprocessing_grid`，478 | 已增加跨列表头 `Character recovery (\%)`。 |
| 表 9 | `tab:inversion_ablation`，510 | 原表头已有 `Long-exp. char (\%)`、`Video avg. char (\%)`，保留。 |
| 表 10 | `tab:real_vlm`，543 | 已增加跨列表头 `Exact / character recovery (\%)`；`Distance` 改为 `Distance (m)`，数据区距离只保留数值。 |
| 表 11 | `tab:vlm_content`，577 | 原四个恢复率列均已有 `(%)`，保留。 |
| 表 12 | `tab:study_typing`，641 | Accuracy、WPM、CPM、字符数及延迟沿用 Metric 行各自单位；差值不另设其他单位。 |
| 表 13 | `tab:study_ratings`，660 | 1--5 Likert 范围和 Mean ± SD 已在表注说明，保留。 |
| 表 14 | `tab:real_coco`，705 | 已改为 `mAP (\%)`、`mAP50 (\%)`、`AR (\%)`；数据区移除重复 `%`。 |
| 表 15 | `tab:real_mot`，738 | 已改为 `HOTA (\%)`、`IDF1 (\%)`；数据区移除重复 `%`。 |
| 表 16 | `tab:ocr_corpus`，787 | 已改为 `Original (\%)`、`Single subframe (\%)`、`Reduction (\%)`；数据区只保留数字。 |
| 表 17 | `tab:digital_boundary`，817 | 已改为 `Char. (\%)`、`Exact (\%)`；SSIM 和 `\Delta E_{00}` 保持原样。 |
| 表 18 | `tab:coco_sim`，843 | 已改为 `mAP (\%)`、`mAP50 (\%)`、`AR (\%)`；数据区移除重复 `%`。 |
| 表 19 | `tab:mot_sim`，876 | 已改为 `MOTA (\%)`、`MOTP (\%)`、`IDF1 (\%)`；数据区移除重复 `%`。 |

## 正文同步

摘要、主要结果、预处理敏感性分析、讨论和结论中原先采用其他差值表述的 5 处文字，已统一改为带 `\%` 的数值写法。数值、区间、比较方向与实验结论均未改变。

## 综合结果

19 张表已完成统一。所有百分比相关列现在都能直接从表头识别单位；物理单位与无量纲指标没有被误加百分号。论文已重新编译，并对表 4--19 所在页面完成版面抽查；新增表头均可见，单栏表格未出现裁切或由本轮修改引入的溢出。
