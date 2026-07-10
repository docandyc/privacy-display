# PRD: Fix montage figure integrity and minor paper review items

## Background
2026-07-10 投稿前审查发现 Fig. 3（real_capture_montage.pdf）三处与正文矛盾，另有四项小改。
用户在 review 报告后回复"修复"，范围明确，无需进一步需求讨论。
d0.5_a0 画布披露（A1）不在本任务内，等用户确认第二台机器硬件后另行处理。

## Requirements

### R1 Fig. 3 蒙太奇重做（fig_f3_montage.py + main.tex caption）
- 图像改用常设 3.91/31.25 ms 位置（首选 d1_a0；禁用 d0.5_a0，其画布为 2560×1600）。
- 第一行改为各 profile 真实的全周期数字积分渲染（原实现对三个 profile 均加载同一张源图）。
  若积分渲染管线不可复用，降级方案：第一行改标 "Source content (reference)"。
- 数字积分必须复现真机捕获顺序：先将源图 fit 到 1920×1080 黑底 playback 画布，在完整画布上生成 profile 帧并积分，最后使用与相机 JPEG 相同的 0.40:0.61 裁剪；不得在 720×71 原图上生成后放大。
- readability-priority 与 high-suppression 均按捕获元数据包含 alpha=0.2 inversion slot；修复 anti_ocr_profile_ablation 中 high-suppression 漏传 inversion 的口径错误，并同步受影响的数字指标。
- caption 披露捕获位置、曝光与列内统一增益；删除 "representative" 措辞。
- 跑 tests/test_fig_f3_montage.py（按新实现更新断言），重新生成 paper/figures/real_capture_montage.pdf。

### R2 main.tex:310 删除无来源的 "2–5 ms" 面板转换数字
改为不含具体数字的表述（如 can exceed the specified GtG figure for dark-to-light transitions）。

### R3 main.tex:769 结论长曝句补口径标注 "(full pool)"

### R4 refs.bib DOI 输出兼容性（审计后修订）
本地 IEEEtran.bst v1.14 不声明或渲染 `doi` 字段，refs.bib 顶部也明确规定 DOI 保存在 `note`。因此不得机械转换为 `doi = {}`，否则最终参考文献会丢失 DOI。保留现有 DOI note，并在完整构建后的 main.bbl 中验证 DOI 仍然可见。

### R5 删除三个未被引用的 label（sec:introduction、sec:detection、sec:simulation）

### 验收
- pytest 蒙太奇相关测试通过。
- latexmk 重编译 main.pdf 无新增错误/未定义引用；肉眼检查 Fig. 3 页。
