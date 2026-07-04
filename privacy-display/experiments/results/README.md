# Results archive guide

本目录同时保存论文报告产物、复现实验输出、诊断性复跑和早期试点。文件存在于目录中不等于其数值被正文采用；论文主结果应以正文明确引用的文件和下述证据分层为准。保留未采用或不利运行是为了公开拍摄条件与选择依据，而不是将这些运行合并为可互换的重复测量。

## 论文主结果

`real_capture_ocr.json` 是 9 个距离/角度位置合并后的逐样本真机 OCR 规范归档。正文的真机 OCR 均值和置信区间以该文件为唯一口径。其 `config.bootstrap` 记录固定随机种子、重采样次数、置信水平、方法和重采样单位；区间由拍摄样本级 best-of-engine 值进行确定性的百分位 bootstrap 得到。

`publication_summary.json` 的 `real_capture.conditions` 使用 `aggregation: "engine_rows_pooled"`：它直接汇总 `real_capture_ocr.json` 的 `summary.by_condition`，每次拍摄的三个 OCR 引擎各占一行。因此 deployed short 在该块中为 1377 条引擎记录的合并均值，而不是论文主表的 459 次独立拍摄。论文主表采用逐拍摄 `best_of_engine_per_capture` 口径，规范来源是 `real_capture_ocr.json` 的 `summary.by_ablation_attack`；不要用 `publication_summary.real_capture.conditions` 复核论文主表数值。

`real_capture_vlm.json` 是正文 0.5 m VLM 表采用的 141107 拍摄会话结果。该会话的抗拍强化档短曝光为 3.91 ms，并与论文表中的同批 OCR best-of-engine 参照列对齐。采用它不是因为恢复率较低，而是为了保持 VLM 与 OCR 输入同批，并以曝光更充分、对攻击者更有利的条件报告防护边界。

## 替代会话与未采用复跑

`real_capture_vlm_d0.5_a0_rerun.json` 是 2026-07-03 生成的替代复跑，抗拍强化档输入来自文件名时间戳为 012715 的拍摄会话，不是正文采用的 141107 会话。该复跑中三模型对抗拍强化档短曝光的字符恢复率均为 0，逐条转写为空；图像表现与欠曝一致。它与论文中 0.5 m/15°、0.49 ms 视频帧欠曝造成低恢复的现象方向一致，但本归档没有独立光度计数据，因而只将“欠曝”作为由曝光设置、图像和空转写共同支持的会话诊断，不把它当作精确的 ISP 因果结论。该文件不进入正文聚合，也不应与 141107 会话平均。

对应的 `real_capture_vlm_d0.5_a0_rerun_partial.json` 是同一替代复跑的中间检查点，仅用于审计调用进度，不是可引用的完成结果。完成文件本身仍有 1 次 API 错误，`call_status.run_complete` 为 false，因此更不能替代正文主运行。

## 预处理试点与不完整运行

`_archive_real_capture_vlm_ENHANCED_partial.json` 和 `_archive_real_capture_vlm_ENHANCED_incomplete.json` 是启用局部对比度增强的早期 VLM 试点/不完整运行。增强会部分重建被掩文字，相当于增加一种攻击预处理，且这些文件并非完整、无错误的主实验。它们仅用于说明为何正文输入统一采用未经增强的原始相机 JPEG，不用于正文主表或跨模型结论。

文件名含 `_partial`、`_incomplete` 或前缀 `_archive_` 的其他 VLM 文件同样属于检查点或历史试点；除非论文或复现清单另有明确引用，不应作为最终报告结果。

## 学习型重构冒烟测试

`unet_reconstruction.json` 是 tiny U-Net 管线的玩具冒烟测试：仅 5 个训练样本、3 个 epoch，并在一个 holdout 文本上检查输出。该文件证明训练、重构和指标记录链路可以运行，但样本量与训练强度不足以评估学习型攻击上限，也不能支持“已充分覆盖学习型重构器”的主张。论文将学习型重构列为尚未充分覆盖的威胁模型，两者并不矛盾。

## 使用原则

复算论文数字时，可先使用 `publication_summary.json` 追踪源文件，但必须按其 `aggregation` 标签选择统计口径；真机 OCR 论文主表应直接读取 `real_capture_ocr.json` 的 `summary.by_ablation_attack`。不要将诊断复跑、预处理试点、partial checkpoint 或玩具测试与正文主结果合并。若未来替换主运行，应同时更新源文件映射、正文数字、复现清单和本说明，并重新生成全部确定性汇总。
