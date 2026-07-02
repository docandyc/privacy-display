# 真机 VLM 规划与初版代码审计

## 已核实的覆盖事实

- 九份 metadata 均各含 120 条 `ablation/profile == vlm`，总计 1,080。
- `d0.5_a0` 含 36 条 `ablation == original && attack == short`。
- 默认三模型应计划 3,348 次调用。
- 单位置 VLM 有六种 condition；加入 original-short 后是七种。因此 `--max-samples 1` 的单位置三模型 smoke test 应为 21 次调用。

## 初版实现的高影响问题

1. `save_partial()` 只在一个模型全部跑完后调用。模型内部中断会丢失该模型全部进度，不满足“每位置保存”。
2. `_aggregate_group()` 把 `vlm_error` 行的全零指标计入均值；远程服务失败会被错误解释为防护成功。
3. `done_ids_from_rows()` 会让错误行在 resume 时重试，但旧错误行仍留在 `existing_rows`，成功结果追加后会产生同一观测的双重统计。
4. 完成循环后无论是否仍有错误都删除 partial，导致失败调用无法可靠续跑。
5. partial 固定为全局 `results/real_capture_vlm_partial.json`，与自定义 `--output` 无关联，也没有配置兼容性校验，容易串跑。
6. `by_position` 把 original 基线与 VLM 样本一起聚合，但 original 只在一个位置存在，会扭曲位置比较。
7. 规划要求的 `vlm_read_success_rate` 未聚合。
8. 缺失图片被静默跳过，空 truth、重复 id、未知位置和无效 CLI 值未严格校验，最终样本量可能悄然缩水。
9. 长批量 API 调用没有重试/退避；一次瞬时 429/5xx 就永久记为失败。
10. 缺少该脚本的专用测试，因此断点、错误统计和样本覆盖都没有回归保护。
11. 初版调用 `VLMClient.analyze_image()` 时继承 `max_tokens=256`。真实 truth 最长 3,093 字符，长文本即使在 original 基线上也可能被响应上限截断，导致 exact-match 校验结构性失败。

## 统计判断

API 错误不是“模型没有识别出文字”，而是该观测没有产生有效模型输出。将它记为 exact-match=0 会系统性降低攻击成功率，正好朝有利于论文结论的方向偏置，因此属于必须修复的科研有效性问题。合理做法是排除失败观测、披露错误数/成功率，并在未完成时保留续跑状态。

## 验证结果

- 默认 dry-run：1,116 captures / 3,348 calls，条件计数与九份 metadata 一致。
- 单位置 `--max-samples 1`：7 captures / 21 calls，纠正规划中“18 calls”的笔误。
- VLM 定向回归：34 passed。
- 全量回归：326 passed，1 deselected。被排除的既有 `test_tesseract_detection_uses_windows_program_files_path` 在 macOS 上把共享 `os.name` 改成 `nt`，使 pytest 自身构造 `WindowsPath` 时崩溃，与本任务改动无关。
