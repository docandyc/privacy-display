# Claude 审稿意见证据审计

## 原始数据重算

从 9 个 `privacy-display/experiments/results_d*_a*_final/real_capture_ocr.json` 合并 31,725 个引擎级记录，按 capture id 对三引擎取攻击者有利的最大恢复率，得到 10,575 个 best-of-engine capture。排除 `roi_pos=d0.5_a15` 后：

| 条件 | 全 9 点 char | 排除欠曝点 char | 排除后 capture-level bootstrap 95% CI | 排除后 exact |
|---|---:|---:|---:|---:|
| deployed short | 15.1% | 16.7% | [14.7, 18.8]% | 0.5% |
| capture-hardened short (`vlm` legacy tag) | 5.0% | 5.6% | [4.8, 6.4]% | 0.0% |
| deployed video temporal mean | 71.1% | 79.7% | [75.4, 83.8]% | 47.8% |
| capture-hardened video temporal mean | 47.9% | 53.9% | [48.0, 59.9]% | 6.3% |

Bootstrap 使用 2,000 次 capture-level percentile resamples 和固定种子 20260612，与论文现有分析口径一致。该敏感性分析证实欠曝光点对所有 protected pooled 指标均单向有利于防守方，不能只在 deployed short 披露。

## 95.2% 与 89.7% 可追溯性

- 95.2% 对应数字仿真中“逐样本最强攻击”的汇总值，不等同于纯 `temporal_average_cycle`；后者约为 94.3%，`blue_channel_max` 约为 95.0%。
- 89.7% 未出现在已发布结果 JSON；产生该值的噪声消融脚本不持久化结果。
- 因此不能保留“噪声使时域平均从 95.2% 降至 89.7%”的主张，也不能据此证明噪声具有积分收益。
- hardened VLM 与 unprotected 的比较同时改变 mask、noise、stripe/glyph 等多个因素，不能隔离证明 noise 贡献。

## 参考文献核验

- Rainbow：Lin Yang, Wei Wang, Zeyu Wang, Qian Zhang, IEEE INFOCOM 2018, pp. 1061--1069, DOI `10.1109/INFOCOM.2018.8485881`。其对象是物理世界目标（如艺术品）的环境照明调制，而不是屏幕视频的时域重编码；相关工作描述应修正。
- Lim：Johnny Lim, “Defeat Spyware With Anti-Screen Capture Technology Using Visual Persistence,” SOUPS 2007, pp. 147--148, DOI `10.1145/1280680.1280701`。现有 `Y. S. Lim` 作者字段不准确。

## 修改策略

1. 主表保留全语料汇总，避免事后删点；同时并列报告预先明确的曝光敏感性分析。
2. 对无法复现的数值直接删除，不用推测性解释替代证据。
3. 将检测、跟踪、VLM、数字代理明确为压力测试、失败边界或诊断，不作为与主 OCR 实验同等级的独立贡献。
4. 对 VLM 两次 0.5 m 会话同时报告：欠曝会话为 0%，充分曝光会话最高 77.8% exact；范围本身体现曝光敏感性，避免隐藏选择过程。
5. 对 ambient illuminance 缺失、ASCII-only 语料、单相机/单显示器和用户研究未完成进行明确限定。
