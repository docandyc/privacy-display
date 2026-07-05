# 审查并修复真机 VLM 补充实验

## Goal

以 `/Users/andyhuang/.claude/plans/ocr-crispy-clover.md` 为实验规划基线，审查 `privacy-display/experiments/real_capture_vlm_evaluation.py` 的样本覆盖、断点续跑、统计口径、失败处理和可复现性；修复会影响运行可靠性或论文结论有效性的缺陷，并用离线测试验证，不发起真实 VLM API 调用。

## What I already know

- 真实元数据包含 9 个位置，每个位置 120 张 `vlm` 档照片，共 1,080 张。
- `d0.5_a0` 的 `original|short` 基线实际为 36 张，因此三模型完整计划是 `(1080 + 36) * 3 = 3348` 次调用。原规划中“基线约 108 张”是文字笔误，但总调用数 3,348 正确。
- 每个位置的 VLM 条件共有 6 类：`short`、`long`、`video|single_best`、`video|temporal_mean`、`video|window_mean_best`、`video|max_proj`；加一类 original 基线后，单位置 smoke test 的条件数是 7，不是规划 Verification 第 2 条所写的 6。
- 目标脚本当前为未跟踪文件；仓库另有用户既有未提交改动，本任务不得覆盖或捎带修改。

## Requirements

- 保持规划中的三模型、九位置、VLM 全攻击条件及单位置 original-short 基线覆盖。
- dry-run 必须在无 API key、无图像解码依赖参与网络调用的前提下，准确报告条件、捕获数和计划调用数。
- 输入必须做严格校验：未知位置、空模型列表、非法数值、元数据缺字段、重复 `(position, id)`、缺图或空 truth 不得静默污染实验。
- 断点文件必须与 `--output` 同目录/同 stem，包含足以验证恢复兼容性的运行配置，并采用原子写入。
- 至少按每个模型的每个位置保存断点；进程中断后，已完成位置不得丢失。
- resume 必须去重；同一 `(model, position, id)` 的新成功结果替换旧失败结果，不能同时进入聚合。
- API/图像失败必须单独计数，不得作为 0 分样本参与 exact-match、char-accuracy 或 token-recall 的均值与置信区间。
- 输出必须包含 VLM read-success rate、成功/失败/计划调用数和完成状态；存在未解决错误时保留 partial，便于 `--resume` 重试。
- 位置统计只比较受保护的 VLM 样本，避免仅 `d0.5_a0` 存在的 original 基线污染位置间比较；同时保留按条件统计与 cross-model exact-match 矩阵。
- 长批量调用提供有限重试与退避，最终仍失败时记录错误并继续。
- 为加载、采样、统计、失败排除、断点恢复、CLI dry-run 和输出结构补充离线测试。

## Acceptance Criteria

- [x] 默认 dry-run 报告 1,116 张捕获和 3,348 次计划调用。
- [x] `--positions d0.5_a0 --max-samples 1` 报告 7 张捕获、三模型 21 次调用，并列出 7 个条件。
- [x] 中断/恢复测试证明已保存行不重复，失败后成功重试只保留成功行。
- [x] 聚合测试证明错误行不进入指标分母，但进入 `error_count`；全失败组不伪装成 0% exact-match。
- [x] partial 路径不与其他输出运行冲突，配置不兼容时拒绝恢复。
- [x] 相关 pytest、静态编译和项目既有质量检查通过（326 passed；1 个既有跨平台测试因修改共享 `os.name` 导致 pytest 内部崩溃，已单独排除并记录）。
- [x] 不修改或提交本任务之外的用户工作。

## Definition of Done

- 实现与测试完成，离线验证通过。
- 代码符合 `.trellis/spec/backend/` 规范。
- 审查结论中区分：规划本身的数字笔误、原实现缺陷、已修复内容、未实际执行的在线实验。

## Technical Approach

将脚本拆成可测试的参数解析、捕获加载、单批评测、结果 upsert、原子 partial 存取和成功样本聚合函数。主循环按模型与位置分批，完成每一批即保存；最终输出仍沿用规划中的 `models / by_condition / by_position / cross_model` 主结构，同时增加 call-status 与 run-complete 信息。

## Decision (ADR-lite)

**Context**：3,348 次远程调用耗时数小时，API 失败和断点语义会直接改变论文统计。

**Decision**：把“失败”视为缺失观测而非识别失败，统计时排除并显式披露；采用可验证配置的原子断点和键控 upsert；位置统计只使用受保护样本。

**Consequences**：结果不会因服务故障虚假变好；若存在错误，报告会明确标记不完整并保留恢复入口。论文引用前必须达到完整或主动披露缺失率。

## Out of Scope

- 不在本任务中实际发起 3,348 次付费 API 调用。
- 不改写论文正文、`publication_summary.py` 或现有实验结果 JSON。
- 不处理仓库中与本任务无关的 `thesis/` 删除及其他未跟踪文件。

## Technical Notes

- 规划：`/Users/andyhuang/.claude/plans/ocr-crispy-clover.md`
- 目标：`privacy-display/experiments/real_capture_vlm_evaluation.py`
- 复用：`privacy-display/src/attack/vlm_evaluator.py`、`privacy-display/src/evaluation/benchmark.py`
- 真实元数据：`privacy-display/experiments/real_captures_*_final/metadata.json`
