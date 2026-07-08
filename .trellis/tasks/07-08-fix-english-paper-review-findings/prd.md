# 修复英文论文投稿前复核问题

## Goal

依据用户提供的 Claude 复核结果，修订当前英文 IEEE Access 稿件中已经核实的证据口径、统计措辞、机制解释、VLM 缺失数据表述和版面问题，使主张与现有实验实现及归档结果一致。

## What I already know

- `video:temporal_mean` 对 150 帧、名义 60 fps 的完整 burst 求均值，约对应 2.5 s，而不是四帧或 67 ms。
- `window_mean_best` 才使用四帧滑动窗口，且从完整 150 帧 burst 中事后择优，不能证明任意 67 ms 录像达到论文中的 71.1%/47.9%。
- Table II 将重复捕获称为 independent captures，与正文披露冲突。
- 当前稿已提供 deployed 的 12-content cluster bootstrap 和 leave-one-round-out，但其他核心 profile 未提供同等聚类区间。
- 面板时序、rolling-shutter readout 和相位未直接测量；本轮不新增实验，只保持假设性机制措辞。
- 物理匹配竞争基线尚缺失；本轮不能虚构数据，只能明确不作比较优越性主张。
- 当前像素级 MI 实现不建模空间邻域，不能据此把 MI 与 `1/n` 的差异归因于相邻像素相关性。
- VLM 请求失败具有内容依赖性；1.5 m 零失败结果已经被指定为主要跨模型证据。

## Requirements

- 将所有把 71.1%/47.9% 绑定到四帧或约 67 ms 的表述改为 150-frame、约 2.5 s temporal mean。
- 不引用未经独立复现的 pooled `window_mean_best` 数字。
- 删除 Table II caption 中的 `Independent`，并明确 capture-level bootstrap 的描述性范围。
- 保留现有 cluster bootstrap/leave-one-round-out，不伪造其他聚类结果。
- 将未测量时序机制维持为假设，并补充实际 playback timing 未经 photometric verification 的边界。
- 明确软件 proxy baseline 不能支持相对物理方案的优越性主张。
- 删除或改写超出像素级 MI 指标能力的空间相关性解释。
- 将“human integration is linear summation”改为理想线性显示—相机辐射积分边界。
- 统一说明受失败请求影响的 VLM 单元仅为成功调用条件下的描述性结果，主要跨条件证据依赖零失败单元。
- 修正“does not add perturbations”与 enhanced profile 的矛盾。
- 将已知不连续且不能筛选配置的 FPI/Pareto 主文分析移除，保留必要的实测/用户研究 flicker 边界。
- 删除参考文献前造成近空白页的 `\clearpage`。
- 不修改尚未完成的用户研究结果占位、作者信息、资助和致谢占位。

## Acceptance Criteria

- [x] `paper/main.tex` 中不存在 `67 ms`、`67\,ms`、`four-frame video temporal averaging` 或将 71.1%/47.9% 解释为四帧攻击的表述。
- [x] 71.1%/47.9% 均被准确标注为 150-frame、约 2.5 s temporal mean。
- [x] Table II 不再称重复捕获为 independent。
- [x] 主文不再用像素级 MI 推断空间邻域相关性，也不把人类视觉等同线性求和器。
- [x] 主文不再包含无区分力的 FPI/Pareto sweep 小节和图。
- [x] 完整 LaTeX/BibTeX 构建成功，无未解析 citation/reference。
- [x] 渲染 PDF 无缺图、裁切或新增明显空白页，原第 22 页近空白问题已消失。

## Out of Scope

- 新采集硬件时序、光电二极管、示波器或高速相机数据。
- 新增物理匹配 baseline 实验。
- 重新运行并引用未经核验的 pooled `window_mean_best` 结果。
- 填写用户研究、作者、资助、DOI、致谢等占位内容。
- 同步中文稿；本任务仅针对用户要求复核的当前英文稿。

## Technical Notes

- Manuscript: `paper/main.tex`
- Build guide: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`
- Video implementation: `privacy-display/experiments/real_capture_ablation.py`
- Canonical PDF: `paper/main.pdf`
