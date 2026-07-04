# 修复 WebStudy 实验效度与数据质量问题

## Goal

在正式招募前修复评审指出的实验设计、刺激等价性、计分、显示安全、数据完整性和论文表述问题，使 WebStudy 收集的数据能够支持被试内因果比较，并可从正式数据库 `study_formal.db` 复现论文用户研究表格与统计检验。

## What I Already Know

- 当前研究机为 240Hz；`n=8` 只产生 30Hz 子帧周期并必然进入 `static_fallback`，不能作为时域层数消融。
- 当前 control 为白底 DOM 文本，masked 为深底 Canvas 文本，存在极性、字重和复制行为混淆。
- 当前打字顺序固定且每条件只有一次；后端又强制恰好两行，因此前后端、数据库、管理页和分析都要一起升级。
- 当前计分按字符位置逐一比较，插入或遗漏会造成后续字符全部错位。
- 当前 144Hz 全局准入与论文的 deployed `n=4` 不一致；研究模式必须以 200Hz 为硬门槛。
- 当前评分只有四个条件、无最短观看时长、无观看时长字段、无丢帧统计。
- `paper/main.tex` 已有用户未提交改动；仅修改用户研究相关段落并保留其他改动。

## Requirements

### 复审追加要求（2026-07-03）

- 被试信息页进入刷新率检查前必须向后端预检正式登记序号 `k`；已占用、非法或预检网络失败时留在当前页并给出明确错误，不允许被试完成整场后才发现撞号。最终提交仍保留唯一约束，防止预检与提交之间的竞争条件。
- 默认正式采集数据库改为全新的 `webstudy/study_formal.db`；现有旧结构 `study.db` 只读保留，不迁移、不删除，也不得继续作为无参数启动、分析或备份命令的默认目标。
- 遮罩预览在点击“开始预览”前不得显示 `load()` 绘制的静态首子帧；用户主动开始后再显示并播放画布。
- 论文只描述最终确定性联合分配，不提及已废弃的哈希实现或使用“碰运气”等口语措辞。

- 正式会话由实验员输入从 0 开始、不可重复的登记序号 `k`；打字顺序索引为 `k % 2`，评分拉丁方行索引为 `floor(k / 2) % 6`。两个平衡机制不得由同一个余数直接派生，也不得依赖随机 session UUID。每 12 位被试构成一个完整交叉循环，`N=24` 恰好两轮。
- `registration_index` 必须进入 session payload、SQLite、管理页与导出；正式会话重复使用登记序号必须被后端拒绝，debug/demo 会话不占用正式轮转序号。
- 空输入的 `accuracy` 必须为 0；任一计分试次 `attempted_chars < 5` 时，分析脚本排除整位被试并记录原因。论文必须明确速度、输入量和准确率联合解读。
- `?debug=1&selftest=1` 在 source-only 热身元数据没有 `counts` 时不得崩溃。
- 恢复论文“数据与代码可用性”声明，消除 VLM 正文的悬空引用。
- JavaScript 测试文件改为 Node 可自动发现的 `*.test.js` 命名，并验证 `node --test` 无需逐文件列举即可运行。
- 禁止在计分输入框粘贴文本。
- Williams 六阶设计测试必须验证 30 个有向相邻前驱对各出现一次，而不仅是六行唯一。
- 在未遮罩打字热身后增加 10 秒 deployed 遮罩预览，使正式 masked 试次不再承担首次接触新颖性。
- 正式模式侧边栏品牌文案使用“受控实验”，仅 demo 模式显示“演示模式”。

### 实验设计与刺激

- 研究模式最低实测刷新率为 200Hz；低于门槛不得开始计分实验，也不得静默降低 `n`。显式 `?demo=1` 模式可保留 144Hz 和自适应 `n`，但必须写入 session 并与正式数据隔离。
- 评分层数梯度使用 `n∈{2,3,4}`，删除 `n=8` 时域条件。
- control 与 masked 都使用 `renderSourceCanvas` 生成同一深底亮字、同字号、同字重的 Canvas；control 等价于 `n=1`、无掩模。
- 添加 12 秒、不计分的 control Canvas 热身试次。
- 每位被试完成四个 20 秒计分试次。顺序为 ABBA 或 BAAB，按稳定的被试分配索引平衡；每个条件两次，保存 `trial_index`、`condition_repetition` 和 `typing_order`。
- 评分增加未遮罩锚点和 deployed 完整配置，共六条件：control、`n=2/3/4 mask+noise`、`n=4 mask-only`、`n=4 mask+noise+anti-OCR+inversion`。
- 六个评分条件按稳定的 6×6 平衡拉丁方顺序呈现并保存分配索引。
- 每个评分条件至少观看 10 秒后才可提交；保存 `view_started_at`、`view_submitted_at`、`view_duration_ms`。
- “疲劳感”改为“即时视觉不适感”；“隐私感”明确为“感知隐私”，论文不得把它解释为客观防护证据。

### 计分与时序质量

- 使用基于 Levenshtein/MSD 的目标前缀对齐计分，避免一次插入/漏打使后续全部判错；保存编辑距离、对齐前缀长度、MSD 错误率和计分方法版本。
- 保存从点击开始到首个有效输入的 `first_key_latency_ms`。
- `MaskedPlayer` 在 rAF 循环内记录实际帧间隔；间隔大于期望值 1.5 倍计为 dropped frame，并保存渲染帧数、丢帧数/率、均值/最大帧间隔、观测刷新率和有效周期率。
- control Canvas 也使用同一 rAF 监控口径，以便比较运行时数据质量。
- 修复刷新率重测后旧 trial/rating 计划未重建的问题。

### 伦理、人口学与环境协议

- 知情同意与光敏性筛查使用两个独立必选框；保存同意时间和筛查通过标记。
- 页面说明身份信息仅用于参与管理，分析/发布只用去标识化数据。
- 增加可选年龄和性别字段，并做后端范围/枚举校验。
- 刷新率页增加实验员环境确认：固定亮度、关闭自动亮度/省电、浏览器全屏、约 60cm 观看距离；保存确认标记。
- README 和论文写明统一环境协议；增加使用 SQLite Online Backup API 的每日备份脚本。

### 数据完整性、管理和分析

- 客户端生成 session UUID；`participants.session_uuid` 建唯一索引。重复提交同一 UUID 返回原记录，不重复插入事件行。
- 数据库初始化必须能无损迁移既有数据库，为新增列补默认值并建立索引。
- 正式统计、CSV/JSON 导出和管理页默认排除 `debug=1` 与 demo 会话；如需排障，只能通过显式 `include_debug=1` 查看。
- 后端严格验证四个 typing 行（两 control、两 masked）和六个唯一 rating 条件，并验证刷新率/研究模式、时长、计分及同意字段。
- 管理页和聚合逻辑按每位被试的两次条件均值计算 paired delta。
- 新增分析脚本，从 `study_formal.db` 生成去标识化 CSV、JSON 和 LaTeX 表；预先实施排除标准，完成配对 t/Wilcoxon、Friedman、Holm 事后检验、效应量与 bootstrap CI。
- 预注册目标样本量为至少 N=24（六阶平衡顺序的倍数）；分析脚本清楚报告纳入/排除人数和原因。

### 论文与文档

- 同步更新用户研究的设备门槛、ABBA/BAAB、热身、Canvas 等价刺激、MSD 计分、六个评分条件、观看时长、丢帧记录、伦理筛查、人口学、环境协议、样本量与分析计划。
- 在 limitation 中说明即时视觉不适为单题项、感知隐私不是客观防拍证据。
- README 给出研究/演示模式差异、正式开跑检查清单、备份和分析命令。

## Acceptance Criteria

- [x] 空库登记号预检返回可用；正式记录占用后返回不可用；非法序号返回 400；debug/demo 记录不占用正式序号。
- [x] 前端在正式模式通过预检后才能离开被试信息页；撞号或请求失败均保留表单与已填写信息。
- [x] 服务、分析和备份的无参数默认数据库均为 `study_formal.db`，旧 `study.db` 的 schema 与两条记录保持原样。
- [x] 遮罩预览开始前画布隐藏，点击开始后显示并播放。
- [x] 论文改为“保证联合顺序分配的确定性与均衡性”，不再出现“哈希随机碰运气”。

- [x] 登记序号 `k=0..23` 生成两轮完整的 12 人交叉分配；每个 typing 顺序 × rating 行组合各出现两次。
- [x] 正式登记序号不可重复，且从 UI 到 DB、导出和管理页可追溯。
- [x] 空输入 accuracy 为 0；任一计分试次少于 5 个字符会在分析审计中排除。
- [x] selftest source-only 路径、禁粘贴和 10 秒遮罩预览通过真实浏览器检查。
- [x] `node --test` 自动发现并运行全部 WebStudy JS 测试，前驱平衡断言覆盖 30 个有向相邻对。
- [x] 论文恢复数据与代码可用性声明，并准确描述轮转、最小输入量与速度-准确率联合解释。

- [x] 240Hz 下所有基础评分条件均为 temporal；仓库不再把 `n=8` 作为用户研究时域条件。
- [x] 正式模式 199.9Hz 不可开始，200Hz 可开始；demo 模式被明确标记且不进入默认统计。
- [x] control 与 masked 的源文本 Canvas 尺寸、字体、颜色和背景完全一致。
- [x] 每次正式提交恰好有四个计分 typing 行、每条件两行，以及六个唯一 rating 行。
- [x] ABBA/BAAB、六阶拉丁方、热身和 10 秒评分门槛有自动化测试。
- [x] 插入/删除计分不会导致后续正确文本整体错判；计分有 JS 自动化测试。
- [x] mask metadata 包含 dropped-frame 指标和观测有效周期率。
- [x] 同一 session UUID 连续提交两次只产生一位 participant 和一组事件。
- [x] 旧 schema 数据库可以原地迁移，新旧记录均可导出。
- [x] stats、CSV 和 JSON 默认不含 debug/demo 数据。
- [x] 分析脚本可在空库和合成测试库上运行，并生成论文表格与统计报告。
- [x] WebStudy 后端测试、JS 测试、相关现有测试及 LaTeX 编译通过。

## Definition of Done

- 代码、数据库迁移、测试、README、分析脚本和论文表述全部同步。
- 自动化检查通过；对无法在无 240Hz 物理显示器环境中验证的行为明确标注人工预检步骤。
- 不覆盖或提交用户原有的无关工作区改动。

## Technical Approach

- 前端保持原生 JS/Canvas2D；给 `MaskedPlayer` 增加 source-only 载入和统一 timing stats。
- 计分使用动态规划做 typed-to-target-prefix 半全局对齐，并从回溯结果计算 matches/MSD。
- 使用实验员连续登记的零起始序号 `k` 生成两个正交分配索引：`k % 2` 选择 ABBA/BAAB，`floor(k / 2) % 6` 选择六阶 Williams 行；后端按同一公式复核，正式 `k` 建部分唯一索引。
- SQLite 使用显式列迁移 helper；既有参与者补 `legacy-<id>` UUID，再建唯一索引。
- 分析脚本使用项目已有 NumPy/SciPy，不引入 pandas；输出保持可审计、可直接粘贴论文。

## Decision (ADR-lite)

**Context**: `n=8`、固定顺序和非等价 control 会直接破坏因果解释；低刷自适应会让同一标签对应不同刺激。

**Decision**: 正式研究锁定 240Hz 实验协议和 `n=4` deployed 配置；用 `n=3` 替换 `n=8`；采用热身 + 四试次 ABBA/BAAB；六评分条件用平衡拉丁方；演示兼容行为与正式数据完全隔离。

**Consequences**: 单位被试时长增加约 72 秒，但每个打字条件有重复测量，主观评分与 deployed 配置闭环，且所有正式被试看到同语义刺激。旧数据库需要自动迁移，后端契约与现有两行/四行测试必须更新。

## Out of Scope

- 不声称浏览器 rAF 与真实面板扫描时序完全等价；物理设备仍需人工预检。
- 不新增抗拍强化档主观条件；本任务只补 deployed 完整配置。
- 不替用户填入尚未采集的最终 N、人口学结果或显著性结论。

## Technical Notes

- 主要文件：`privacy-display/webstudy/static/{app,mask,typing}.js`、`privacy-display/webstudy/server.py`、`privacy-display/webstudy/README.md`、`privacy-display/tests/`、`paper/main.tex`、`paper/refs.bib`。
- `.trellis/spec/backend/quality-guidelines.md` 已同步登记序号、联合轮转、最小输入量、浏览器预览和新增验证契约。
- 复审要求已覆盖早先“不得恢复数据与代码可用性小节”的临时约束；本轮应恢复该声明并保留待导师确认的 TODO。
