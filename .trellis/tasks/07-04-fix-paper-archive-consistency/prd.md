# 修复论文与数据归档一致性

## Goal

以当前 2026-07-04 合并后的逐样本归档为唯一数据口径，修复论文中的 bootstrap 置信区间、图注、VLM 趋势表述和摘要长度，并为易被误读的探索性/非报告结果补充归档策展说明，使论文数字可由随文 JSON 复核。

## Requirements

* 以 `experiments/results/real_capture_ocr.json` 的当前聚合结果为准，更新正文 deployed short、capture-hardened long、capture-hardened video temporal mean 的字符恢复率置信区间。
* 更新反色强度消融表中 5 个 alpha 档位、2 种攻击条件的全部 10 个 bootstrap 区间，均值保持不变。
* 保持 2000 次百分位 bootstrap 和固定种子；在最终聚合 JSON 的配置元数据中显式记录种子、重采样次数、置信水平和方法，并验证重复汇总结果稳定。
* 将图 11 图注中的“16 个参数格点”改为“12 个参数格点”；16 仅表示每格点样本数，不混入格点计数。
* 修正 V-C 对 1.0 m VLM 长曝光/视频趋势的概括：一致性仅适用于 Qwen 与 Kimi；明确 GLM 长曝光 exact 在 1.0 m 为 3.3%，显著低于 1.5 m 的 58.3%。
* 将摘要压缩为单段、可译为不超过 250 个英文词的内容，保留问题、方法、核心单 UVC OCR 结果、残余攻击边界和泛化/可用性限制，删除密集数字罗列。
* 在 `experiments/results/README.md` 中区分论文报告产物、替代/未采用会话、归档试点和玩具冒烟测试：
  * 说明 `real_capture_vlm_d0.5_a0_rerun.json` 使用 012715 欠曝会话、短曝光转写为空，不是论文 0.5 m 报告会话；论文采用同批 OCR 参照的 141107、3.91 ms 会话，属于对攻击者有利的保守口径。
  * 说明 `_archive_real_capture_vlm_ENHANCED_*` 是带局部对比度增强的试点/不完整运行，不作为论文主结果。
  * 说明 `unet_reconstruction.json` 仅为 5 个训练样本、3 epoch 的玩具冒烟测试，不构成对学习型重构攻击的充分覆盖。
* 在探索性基线段补一句：调暗 50% 的字符恢复率与未保护条件相同，说明该设置没有降低当前 OCR 恢复率，避免把探索性比较写成有效防护。
* 为 `publication_summary.real_capture.conditions` 明确标注 `engine_rows_pooled` 口径，并机器可读地指向论文主表采用的 `summary.by_ablation_attack` / `best_of_engine_per_capture` 口径；README 同步解释两者的分母差异。
* 更新人工结果整理报告中两处旧版真机 OCR 数字，避免归档内继续出现 92.5%/14.1%/4.2%/65.4% 的旧口径。
* 编译论文并检查 PDF；已知每页 505 pt overfull hbox 来自 IEEE Access 页眉 logo 条，不作为本文正文排版缺陷处理，但需目视确认页眉。

## Acceptance Criteria

* [x] 论文中上述 13 组 CI 与最终 `real_capture_ocr.json` 按一位小数格式化后逐项一致。
* [x] 最终 JSON 显式记录 deterministic bootstrap 参数，连续两次生成的摘要与 CI 完全一致。
* [x] 图 11 正确写为 12 个格点。
* [x] V-C 不再声称 GLM 的 1.0 m 长曝光趋势与 1.5 m 一致。
* [x] 摘要保持单段，等价英文草译不超过 250 词，且不扩大论文主张。
* [x] results README 清楚标注三个非主报告文件类别及选择报告会话的原则。
* [x] 论文可用 XeLaTeX/latexmk 成功编译，无新增未定义引用或致命错误；PDF 页眉目视正常。
* [x] 与 bootstrap 元数据相关的自动化测试通过。
* [x] `publication_summary.real_capture` 明确区分引擎行合并口径和论文逐拍摄 best-of-engine 口径，README 与 Markdown 汇总均可见。
* [x] 人工结果整理报告不再包含旧版 92.5%/14.1%/4.2%/65.4% 真机 OCR 数字。

## Definition of Done

* 修改保留用户当前未提交的合并结果，不回退或覆盖无关工作。
* 运行针对性测试、数据一致性检查、重复生成检查和 LaTeX 编译。
* 更新归档说明，并记录无法由自动化验证的边界。

## Technical Approach

当前 `src/evaluation/benchmark.py` 已将 bootstrap 固定为 2000 次、种子 `20260612`。本次不另起一套随机实现；聚合脚本复用这组常量并将参数写入归档 JSON。论文数值直接从重新生成的最终 JSON 提取并格式化，另加脚本式断言检查论文字符串，避免手抄漂移。对争议结果采用“保留并分层标注”，不删除不利运行。

## Decision (ADR-lite)

**Context**: 当前均值已与归档一致，但论文仍保留旧一轮 bootstrap 端点；部分结果文件如果脱离采集会话和用途说明，会被误读为选择性报告。

**Decision**: 以当前逐样本聚合 JSON 为规范源，公开固定 bootstrap 参数；保留替代会话、增强试点和玩具测试，同时在 results 目录入口 README 中明确其证据等级和不采用原因。

**Consequences**: 审稿人可以复算并得到相同区间，也能看到不利/失败运行及其物理条件。README 的说明不能替代原始光度测量；“欠曝”判断仍依据空转写、会话曝光和同类现象，不能扩展为对未记录 ISP 行为的精确解释。

## Out of Scope

* 不重新采集相机数据，不重新调用商用 VLM API。
* 不删除或隐藏与主结论不一致的原始结果。
* 不修复 IEEE Access 类文件产生的已知 505 pt 页眉 overfull 日志。
* 不将玩具 U-Net 结果升级为正式学习型攻击评测。
* 不改动论文尚待完成的用户研究数据。

## Technical Notes

* 论文：`paper/main.tex`
* 最终 OCR 归档：`privacy-display/experiments/results/real_capture_ocr.json`
* 聚合器：`privacy-display/experiments/finalize_real_capture_artifacts.py`
* bootstrap 实现：`privacy-display/src/evaluation/benchmark.py`
* 当前归档均值与 CI 来自 9 个位置、逐样本 best-of-engine 汇总。
* IEEE 官方写作指南要求摘要为单段且最多 250 词，见 `research/ieee-abstract-requirements.md`。
