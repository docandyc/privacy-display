# Experimental Evaluation 章节修订版意见（基于代码与数据核查）

> 核查日期：2026-07-17
> 核查对象：`~/Downloads/EXPERIMENTAL_EVALUATION_REVIEW.md`（下称"原审"）中对 `paper/main.tex` §V Experimental Evaluation 的全部事实性论断与修改建议
> 核查方法：逐条对照本机工作区的 `main.tex`、`privacy-display/` 源码、`experiments/` 归档结果 JSON、TrackEval 输出、`用户调研实验结果/cleaned/analysis_formal/analysis_report.json`
> 本文档性质：替代原审作为本章修改的执行依据。原审中已被论文现状满足或判定为误判的条目集中列于第 4 节，避免无效改动。

## 1. 总体结论

原审的代码级事实基本准确，但它审的是 **git 仓库内容**（fresh clone 视角），而本机 `privacy-display/experiments` 是指向外置盘的符号链接，数据完整可查；同时原审的多数"表述收窄"建议针对的是论文已经改掉的旧状态。核查后：

- **确认需要执行的修改项：6 项（E1–E6）+ 1 项投稿前工程项（E7）**；
- **原审约三分之二的收窄建议论文现状已满足**，不需要动；
- 原审对 HOTA 的怀疑（"无法确认则删除"）为**误判**：全部 12 个 HOTA 值已确认来自真实 TrackEval 输出；
- 核查过程中发现一个原审没有发现的新问题：`tab:real_mot` 同一张表的 HOTA 与 IDF1 来自**两个不同的指标后端**（见 E2）。

## 2. 原审条目逐条判定总表

| 原审条目 | 判定 | 去向 |
|---|---|---|
| 2.1 五项打字指标 Holm 校正未由脚本执行 | **属实**（但补救比"删句"轻） | E1 |
| 2.2 当前检出版本不能复现多数实验 | **实质成立，表述不准**（目录存在，是外置盘符号链接，git 只跟踪链接本身） | E7 |
| 2.3 检测/跟踪后端无法确认，"必要时删 HOTA" | **HOTA 部分误判**（已确认 TrackEval）；后端未披露属实 | E2 |
| 2.4 "pre-registered" 缺少可核验依据 | **属实** | E3 |
| 3.1 浏览器研究非物理系统等价实现 | **事实前提对，建议已满足**；残余半句光度学限定 | E6（可选） |
| 3.2 掩码 key 未归档、避免"fully reproducible" | **事实前提对，论文已披露**；"fully reproducible" 全文不存在 | 部分并入 E7 |
| 3.3 VLM 应定位为攻击边界 | **要求的透明性几乎全部已在文中**；残余一句前瞻句 | E5 |
| 3.4 长曝光"反转"机制解释 | **方向性误判**（论文报为防护失效方向，且已标注 candidate explanation） | 不改（移 Discussion 为可选风格） |
| 4.1 主实验/探索性实验分层 | 合理编辑建议，无事实错误 | 重写时采纳 |
| 4.2 Setup 混入结果 | **属实，逐条核实** | E4 |
| 4.3 阈值不应写成安全保证 | **已满足**（全文均为 descriptive targets 且保留分位数） | 不改 |
| 4.4 统计单位与 CI 措辞 | **已满足**（表注原句即 "Not Population Confidence Intervals"） | 不改 |
| 4.5 检测/跟踪仅探索性压力测试 | **限制已前置**；"transfers beyond text" 为疑问式引入 | 可选微调 |
| 4.6 用户研究结论保守化 + 伦理 | **已满足**（无 negligible 类表述；伦理段完整） | 不改 |
| 5 章节结构建议 | 合理编辑建议 | 重写时采纳 |
| 6.1–6.3 表格规范 | 合理编辑建议 | 重写时采纳 |
| 6.4 后端版本与引用 | 属实（OCR 引擎版本已在文，评估后端版本缺失） | 并入 E2 |
| 6.5 不应写作完整 ByteTrack | **已满足**（表题即 "ByteTrack-Style Greedy Association"） | 不改 |
| 6.6 ΔE00/SSIM 数字代理 | **已满足**（main.tex:181 已限定 "digital reconstruction quality"） | 不改 |

注：原审引用的 Holm 句行号 655 实为 main.tex:664，不影响判定。

## 3. 确认需要执行的修改项

### E1（P0）打字指标 Holm 校正：补分析代码，不删正文句

**事实**：`webstudy/analyze_study.py` 中 `holm_adjust()`（第 160 行）仅用于主观评分的 Friedman 后成对 Wilcoxon（第 203–208 行）；五项打字指标只逐项调用 `paired_inference()`（第 360–362 行）。权威报告 `用户调研实验结果/cleaned/analysis_formal/analysis_report.json` 的 typing 各指标均无 holm 字段。

**验算**：权威报告五个原始 p 值为 wpm 0.0049、cpm 0.0049、accuracy 0.0431、attempted_chars 0.0043、first_key_latency 0.2003。Holm 校正后依次为 0.0215、0.0215、0.0215、0.0862、0.2003：WPM、CPM、attempted 显著，accuracy（rank 4 of 5）不显著，latency 不显著。**main.tex:664 的正文结论算术完全正确**，问题仅是归档脚本未产出该数值。

**改法**：在 `analyze_study.py` 的 typing 推断段对五个 p 值调用现成的 `holm_adjust()`，将 `holm_p` 写入 `typing` 报告字段，重新生成 `analysis_report.json`（数值结论不会变）。正文无需改动。原审"删除该句"的选项不必采用。

### E2（P0）检测/跟踪指标后端：统一 IDF1 来源并披露后端与版本

**事实（核查确认，回答原审 P0 问题 2）**：

- mAP/mAP50/AR：真实拍摄与仿真的所有单元 `evaluator=pycocotools`（`real_capture_coco_detection.json`、`coco_detection_attack.json`），非回退实现；
- HOTA：来自真实 TrackEval 运行（`experiments/results/trackeval_workspace_real/trackers/PRIVACY-train/*/pedestrian_summary.txt`），论文 `tab:real_mot` 的 12 个 HOTA 值与之逐格精确吻合，**不需要删除 HOTA**；
- 但 `tab:real_mot` 的 IDF1 一列与 TrackEval 不符，而与 `real_capture_mot_tracking.json` 中 `metric_backend=approximate_scipy` 的项目内近似实现逐格吻合（差异示例：RT-DETR short 5.2 vs TrackEval 5.37；Faster R-CNN video 7.1 vs 7.56；RetinaNet clean 9.8 vs 10.34）。即**同一张表两列来自两个后端**；
- 仿真 MOT 表（main.tex:857–886）的 MOTA/MOTP/IDF1 全部来自同一近似实现（`mot_tracking_attack.json` 全单元 `metric_backend=approximate_scipy`），未使用 motmetrics；
- tracker 为 `greedy_bytetrack_fallback`（项目内贪心关联），论文措辞已如实，无需改。

**改法（推荐 a）**：

a. 将 `tab:real_mot` 的 IDF1 替换为 TrackEval 输出值（同一后端产出 HOTA+IDF1，全表口径一致），正文 main.tex:751 的 IDF1 区间随之更新；
b. 或保留现值，在表注声明两列来源不同。

无论 a/b，均需在 §V 检测/跟踪小节（main.tex:685 附近）与仿真小节补一句后端披露，含义为：mAP 系列由 pycocotools 计算；真实拍摄跟踪的 HOTA（及 IDF1，若采用方案 a）由 TrackEval 计算；仿真 MOT 的 CLEAR/IDF1 指标由项目内近似实现计算。同时补 pycocotools、TrackEval 的版本号与引用（HOTA 原始论文与 TrackEval 工具）。OCR 引擎版本已在文中（main.tex:303），无需重复。

### E3（P0）"pre-registered" 改为 "pre-specified"

**事实**：main.tex:619（"Pre-registered exclusion criteria"）与 main.tex:623（"met all pre-registered inclusion criteria"）两处。全文无 OSF/AsPredicted 或机构注册记录可引；`analysis_report.json` 内嵌的 analysis plan 不构成带时间戳的公开注册。

**改法**：两处改为 "pre-specified"。若作者确有带时间戳的注册记录，则保留原词并在文中给出匿名标识（作者决定）。

### E4（P1）将结果数据移出 Experimental Setup

**核实的混入位置**（原审举例全部属实）：

- main.tex:295：readability-priority 与 high-suppression 的 P50/P75/P90/P95/P99 数值（10.1/22.0/45.6/63.6/95.0 与 3.4/9.2/15.2/19.1/22.6）；
- main.tex:297：全几何差值 78.0pp [75.5, 80.3]、89.1pp [85.0, 92.4]、mask-only 3.0pp [-0.5, 6.5]；
- main.tex:299：匹配均值 94.5/17.8/5.6、差值 76.7/88.9、408 图敏感性均值 16.7%、视频均值 71.1→79.7、47.9→53.9；
- main.tex:301：leave-one-round-out 16.6%/15.8%。

**改法**：数值移入 §V.B 真实拍摄 OCR 结果（分位数与尾部风险并入相应结果段，leave-one-round-out 并入稳健性检查段）。Setup 保留定义性内容：硬件、拍摄协议、内容构成、指标定义、统计单位与匹配策略、resample 参数与 seed、软件版本、预处理网格、复现状态。

### E5（P1）前瞻句移入 Discussion

main.tex:593 句尾 "content-adaptive, VLM-aware temporal profiles warrant investigation" 属未来设计方向，移入 Discussion 的 VLM-Aware Implications 小节（main.tex:923 起），合并前先查重：该小节已有相近含义表述，若重复则直接删除 §V 中这半句。

### E6（P1，可选）用户研究补光度边界半句

现状已有关键区分句（web player 为独立 JavaScript/Canvas2D 路径、非 ChaCha20 与梯度噪声管线；§IV main.tex:199 亦声明 web 实现无 CSPRNG 性质）。残余缺口：rAF/时序日志证明的是帧调度，不构成面板 scan-out 或子帧光度波形的测量验证。可在该句后追加一句，含义为：

> Frame-scheduling logs verify presentation timing at the JavaScript level; no photometric measurement of per-subframe panel output was performed.

### E7（P2）投稿冻结前的 artifact release

**事实**：`privacy-display/experiments` 在 git 中是 mode 120000 的符号链接（指向 `/Volumes/Mac扩展盘/项目数据/privacy-display/experiments`），实验脚本与结果 JSON 均不在 git 内容中；fresh clone 无法复现，原审 2.2 的实质结论成立。

**改法**：冻结一个包含以下内容的 release/tag 或补充材料包：实验脚本、去标识输入与结果 JSON、依赖版本、模型标识、文件哈希（`reproducibility_manifest.py` 已有基础），并分类列出随机性来源：掩码 key（不归档，论文 main.tex:275 已披露，复现依赖归档 stimuli）、内容 cluster resample seed 20260612（已在文）、浏览器确定性 seed、检测/跟踪派生 key、bootstrap seed。

## 4. 判定为误判或论文现状已满足的条目（不要重复修改）

以下各条附核查证据，重写章节时**保持现状即可**：

1. **HOTA 来源怀疑（原审 2.3）**：误判。12/12 HOTA 值与 TrackEval `pedestrian_summary.txt` 精确吻合，删除 HOTA 的条件不成立。
2. **"fully reproducible" 过度声明（原审 2.2/3.2）**：该短语在 main.tex 中不存在。唯一 "reproducible" 修饰固定参数预处理网格（main.tex:303），本身成立。§IV Implementation Scope and Reproducibility（main.tex:275）已主动披露 playback metadata 不保存掩码 key、复现依赖归档 stimuli，正是原审 3.2 要求的披露。
3. **阈值写成安全保证（原审 4.3）**：已满足。main.tex:181 "tiered design goals ... These descriptive thresholds"；摘要、main.tex:325/395/949 均用 "descriptive target"；P50–P99、exact match、敏感字段、尾部分位数均已保留，均值未掩盖尾部泄露。
4. **CI 措辞（原审 4.4）**：已满足。九位置池表注（main.tex:347）原句即 "Brackets Are 95% Capture-Resampling Summaries, Not Population Confidence Intervals"；main.tex:297 正文同样限定。
5. **用户研究结论与伦理（原审 4.6）**：已满足。全文无 "negligible"、"normal user experience" 类表述；摘要结论为 "indicating measurable usability costs"。伦理段（main.tex:607）与 Discussion Ethics Statement（main.tex:930）已说明：机构无对应伦理委员会、当面确认自愿同意与光敏筛查、正式流程未采集姓名/学号/专业/年龄/性别、仅发布去标识数据。数据库遗留身份字段与论文声明不冲突（论文只声明"未采集"，与正式前端行为一致）。
6. **浏览器研究定位（原审 3.1）**：核心区分句已在（独立 JS/Canvas2D 路径、非 ChaCha20 管线；无 CSPRNG 性质），仅剩 E6 的半句光度学限定。
7. **检测/跟踪定位（原审 4.5）**：限制已前置。main.tex:685 小节首句即 "exploratory ... stress test ... evidence strength is not equivalent to the OCR main experiment"；main.tex:751 再次声明 "cross-task stress test rather than an isolated protection effect"；8 张 COCO 已标注 "implementation pipeline diagnostic"（main.tex:821）。"To probe whether ... transfers beyond text" 为疑问式引入而非结论，可在重写时顺手软化，非必改项。
8. **ByteTrack 措辞（原审 6.5）**：已满足。表题 "ByteTrack-Style Greedy Association"，正文 "in-project greedy association implementation inspired by ByteTrack"。
9. **长曝光机制解释（原审 3.4）**：方向性误判。论文将长曝光反转如实报告为防护失效方向（掩模降低亮度使攻击者恢复率升高），并非"系统额外保护优势的证据"；机制表述已标注 "a candidate explanation"（main.tex:399），摘要为 hedged 的 "consistent with"。是否将解释移入 Discussion 属风格选择。
10. **VLM 透明性（原审 3.3）**：已满足。1,188/1,133 与失败分布、非随机缺失声明、单元上下界、"Conditional cells are not used to rank models"（main.tex:520 原句）、0.5 m 会话事后选择披露（main.tex:526）、provider 标识/解码参数/prompt 归档（main.tex:524）均在文中。残余仅 E5。
11. **ΔE00/SSIM（原审 6.6）**：已满足。main.tex:181 限定为 "digital reconstruction quality"。

## 5. 原审四个 P0 问题的核查答案

1. **Holm 依据**：脚本确实未执行，但论文数值算术正确；按 E1 补代码闭环，无需删句。
2. **HOTA/COCO/MOT 后端**：mAP=pycocotools；HOTA=TrackEval；`tab:real_mot` 的 IDF1 与仿真 MOT 全部指标=项目内 approximate_scipy 近似实现；tracker=项目内贪心（措辞已如实）。按 E2 统一并披露。
3. **实验脚本与归档**：存在且完整，但在外置盘符号链接下、不在 git 内容中；按 E7 冻结 release。
4. **pre-registered**：无带时间戳的注册记录；按 E3 改词（除非作者确有注册）。

## 6. 保留采纳的结构性建议

原审 4.1（证据分层标注）、第 5 节（primary OCR → enhanced attack → boundary attack → usability → exploratory transfer 的小节顺序）、6.1–6.3（主文/补充材料分配、单表单结论、指标方向标注与小数精度统一）无事实错误，作为本章重写时的编辑框架采纳。执行 E4 的搬移应与该重排一次完成，避免两轮大改。

## 7. 修订后的优先级

- **P0（重写正文前）**：E1 补 Holm 代码并重新生成报告；E2 确定 IDF1 方案（推荐替换为 TrackEval 值）并起草后端披露句；E3 改词（或作者提供注册记录）。
- **P1（本轮章节重写）**：E4 Setup 移结果；E5 前瞻句移 Discussion；E6 可选半句；同步执行第 6 节的结构重排。
- **P2（投稿冻结前）**：E7 artifact release 与随机性来源清单。
