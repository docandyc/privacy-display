# IEEE Access「Applied Research」适配修改方案

> 基准版本：`paper/main.tex`（2026-07-12，commit 42ab923 之后的工作区，976 行，编译 18 页）。
> 行号会随编辑漂移，因此每个修改点同时给出**行号 + 锚文本**，执行时以锚文本为准。
> 前提：本方案只在用户研究数据**达标**（见 Gate 0）后执行。若数据不达标或边缘达标，维持
> Research Article 类型，只执行 P0（数据注入），其余各节不动。
>
> IEEE Access 对 Applied Research 的官方定义（Submission Checklist 第 2 页）：
> "This article describes challenges and practical solutions for topics within the journal's
> scope. Quantitative results for validation of the approach are expected."
> 注意：所有类型审稿严格度相同；类型会印在最终发表的论文上。

---

## 总路线（一句话）

叙事主线从「we **measure** OCR recovery from temporally masked screens」（测量研究）改为
「we **present** a prototype defense, **validate** it on the machine side *and* the human side
within a declared operating envelope, and **characterize the capture escalation** it forces on
the attacker」（挑战 → 方案 → 双侧验证 → 运行包线）。

**三条红线（任何改写不得越过，对应仓库 CLAUDE.md 的 claims discipline）：**

- **R1 边界数字全保留**：150 帧均值 71.1%/47.9%（common-setting 79.7%/53.9%）、长曝光 60.9% vs
  未保护 47.3%、预处理 oracle 40.2%/13.7%（相对削减跌至 58.1%）、inversion slot 拉伸后 93.0%、
  数字域全周期 94.3–95.2%、P99=95.0%、字段精确恢复 17.7%。一个都不能删、不能弱化。
- **R2 范围限定全保留**：one eMeet S600 UVC link、3.91 ms 为 control-derived 标签（非光度测量）、
  固定几何、三个开源 OCR 引擎、应用层 PoC。
- **R3 禁词表**：prevents photography / defeats / guarantees / immune / anti-photography /
  secure against cameras。成本论证只能写「所需捕获时长/能力的提升」，不能写「攻击者会被发现」
  （未测量）。150 帧以下的时长—恢复曲线未解析（main.tex:939），因此不能写「需要至少 2.5 秒」，
  只能写「评估过的持续攻击使用了 2.5 秒；更短时长未测绘」。

---

## Gate 0：执行前提（数据决策门）

实验开始**之前**由作者把 G2/G3 的数值边际写死（避免看完数据再定标准）。全部满足才执行本方案：

| Gate | 内容 | 建议默认值（作者可改，改完锁定） |
|------|------|------|
| G1 | 预注册排除后有效样本 | N ≥ 24（论文 main.tex:616 已写明） |
| G2 | 打字任务等效性 | masked 平均准确率 ≥ ____%（建议 85%）；Δ准确率 95% CI 下界 > ____ pp（建议 −10）；WPM 相对下降 ≤ ____%（建议 25%） |
| G3 | 主观评分 | readability-priority 完整配置在 readability / stability / comfort 三项中位数均 ≥ 3 |
| G4 | 伦理文书 | 书面批准/豁免/免审文书已取得并存档 |

**Gate 失败时的回退**：仍执行 P0 把真实数据写入论文（负面/中性可用性结果在测量框架下依然是有效
发现），类型选 Research Article，P1–P3 不执行。这是两种类型的不对称性：Research Article 对任何
实验结果都稳健，Applied Research 押注结果良好。

**跑实验前的实现侧 blocker（与本文档并行处理）**：webstudy 的知情同意与光敏筛查复选框存在
「默认预勾选」问题（多轮 review 已确认未修复）。论文 main.tex:604 写的是 "Participants must
**separately check** informed consent and photosensitivity screening"，实现必须与论文一致后才能
开始正式收数据，否则构成论文—实现漂移 + 伦理缺陷。

---

## P0 — 用户研究数据注入（两种类型共用，最先做）

### P0.1 数据管线（main.tex:618–622 注释已写明映射关系）

1. 正式收数据（`webstudy/server.py`，240 Hz 实验室机，формal 会话 ≥200 Hz 门槛）。
2. `privacy-display/.venv/bin/python privacy-display/webstudy/analyze_study.py`
   → `analysis_output/typing_table.tex`、`ratings_table.tex`、JSON audit（数据源 `study_formal.db`，
   该库含身份字段，**永不提交/发布**）。
3. 两个 `.tex` 输出的行与 `tab:study_typing`、`tab:study_ratings` 一一对应，直接替换表体。
4. `privacy-display/.venv/bin/python privacy-display/experiments/paper_figures/make_all.py`
   重生成 `fig:study_typing`、`fig:study_ratings`。
5. 正文统计量（检验统计、p、效应量）填入 Results 段（main.tex:664 的全部 XX）。

### P0.2 XX 占位符清单

| 位置 | 锚文本 | 内容 |
|------|--------|------|
| 623 | `\textbf{Participants}: XX volunteers` | 招募数/纳入数/排除数/人口学 |
| 626 | caption `($N=$ XX; Participant Means` | 打字表 N |
| 635–639 | 表体 `-- & -- & -- [--, --]` | 打字表 5 行 |
| 645 | caption `($N=$ XX; 1--5 Likert` | 评分表 N |
| 表体（evaluated 6 条件行） | `--` 单元格 | 评分均值±SD |
| 664 | `changed mean accuracy by XX percentage points` | 全部统计量 |

### P0.3 「planned study」状态句总清单（数据落地后逐处改状态）

| 行号 | 锚文本 | 改法 |
|------|--------|------|
| 44–49 | `\tfootnote{...planned minimal-risk human-subject study. No participant data have been collected...` | 改为已完成：写明文书类型（approval/exemption/waiver）与批准主体；删除 "No participant data have been collected" |
| 110 | `the deferred usability protocol` | → `the usability study` |
| 228 | `Only the planned user study can determine whether either configuration supports comfortable temporal integration.` | → 引用结果：`The user study (\S\ref{sec:user_study}) addresses this question; ratings for the 48\,Hz inversion configuration appear there.`（若 stability 项结果差，此处必须如实反映——同时意味着 Gate 3 失败） |
| 420 | `The planned user study evaluates readability-priority rather than this visibly stronger profile.` | `planned` → 删去；句子其余保留（high-suppression 不在研究范围这一事实不变） |
| 604 | `The planned study involves minimal-risk...no participant data have been collected. Before recruitment, the authors will obtain...` | 全段时态与状态改写：文书已取得（写明类型与日期）、筛查与同意机制**已执行**、其余保障措施描述由 will → 过去式 |
| 616 | `A minimum of $N=24$ participants is planned` | → `was pre-specified`；预注册排除标准全部保留原文 |
| 931 | Ethics Statement：`The planned user study would involve...no participant data have been collected. Recruitment will begin only after...` | 改为已完成状态 + 文书信息；同意/筛查/退出机制改过去式 |
| 941 | `The planned user study has not yet collected participant data. It evaluates readability-priority rather than high-suppression, and its immediate-comfort rating does not address long-term or clinical effects.` | 删除第一句；第二、三句**保留**（单会话、即时舒适度、不覆盖 high-suppression 仍是真实局限）；可补 `single-session` 局限 |
| 943 | `Completing the preregistered usability study would connect machine-recovery gains to human readability and comfort.` | 删除，替换为长期/多会话方向：`Longitudinal, multi-session use and the high-suppression profile's visual acceptability remain untested.` |
| 593 / 898 | `\long\def\deferreduserstudy{` / `\deferreduserstudy` | 宏名 `deferred` 已名不副实：改名 `\userstudysection`，或按 P2.4 直接搬移解包 |

---

## P1 — 框架层改写（题目 / 摘要 / 关键词 / 引言 / 贡献）

### P1.1 标题（main.tex:37；`\markboth` 51–53 同步改）

现标题是测量式：`Temporal Pixel Masking and Conventional OCR Recovery in Short-Exposure Screen
Capture: A Single-Camera UVC Study`。候选（均保留 Short-Exposure 限定词，这是包线诚实性的一部分）：

1. **（推荐）** `Temporal Pixel Masking for On-Axis Screen-Capture Privacy: Prototype Design and Physical Validation Under Short-Exposure Capture`
2. `Design and Two-Sided Validation of Temporal Pixel Masking Against Short-Exposure Screen Capture`
3. `Temporal Pixel Masking Against Short-Exposure Screen Capture: OCR Suppression and Usability on a 240 Hz Prototype`

「Single-Camera UVC」限定从标题移入摘要末句与 §Threat Model（不许丢，只是换位置）。

### P1.2 摘要（main.tex:60–62，重排叙事，≤250 词）

逐句映射（现文 → 新框架）：

| 现摘要句 | 处理 |
|----------|------|
| `Screen content can be silently captured...` | 保留为挑战句，追加半句 on-axis 生态位（防窥膜/视角方案不影响正对镜头） |
| `This study measures conventional-OCR recovery...` | **替换**为方案句：`We present a temporal pixel-masking display pipeline..., implemented as a GPU-rendered prototype on a 240 Hz panel.` |
| `We collected 10,575 physical captures...` / `Per-capture best-of-engine mean...94.5/17.8/5.6` | 保留，前面加 `On the machine side,`；**新增达标句**：81.2% 相对削减 + 0.4% exact match，meets pre-declared targets（依据 main.tex:414） |
| （无对应句） | **新增人侧验证句**：`On the human side, a preregistered within-subject study ([STUDY-N] participants) found [STUDY-TYPING-SUMMARY] and [STUDY-RATING-SUMMARY].` |
| `A fixed five-transform...oracle raised...40.2/13.7` / `A 150-frame mean and on-axis VLM probes recovered substantially more text.` | 保留，合并为包线句，加解释性半句：`the defense removes the single-snapshot channel rather than preventing recovery outright` |
| `The study maps recovery under...` | **替换**为范围+部署句：`Results are scoped to one UVC camera link; deployment requirements and access-control pairing are reported.` |

完整英文骨架见附录 A2。

### P1.3 关键词（main.tex:64–66，现 8 个，上限 10）

追加：`usability study`、`human factors`（或 `privacy-enhancing technology`，三选二）。

### P1.4 引言

| 位置 | 锚文本 | 改法 |
|------|--------|------|
| 80–82 | `Current screen-privacy solutions each address a narrow threat subset.` | 段末追加 on-axis 生态位句（附录 A7），把「gap」从"没人测过"升级为"没人防住正对镜头的机器识别" |
| 88 | `This study compares conventional OCR recovery across three display profiles at one UVC control setting.` | → `We implement this principle as a GPU-rendered prototype and validate it on both sides of the display.` 后接现有数字句（保留），补达标半句（81.2% / 0.4%） |
| 90 | `Attack-oriented evaluation expands this result.` | → `Envelope evaluation bounds where protection holds.` 其余数字句保留 |
| 110 | 路线图句 | `reports OCR evidence, VLM probes...and the deferred usability protocol` → `reports machine-side validation, the usability study, and the operating-envelope evaluation` |

### P1.5 贡献（main.tex:99–108，3 条重排为 4 条）

现三条 = measurement / evidence / attack mapping。新四条（完整英文草稿见附录 A3）：

1. **System design and implementation**（工程贡献前置：ChaCha20 CSPRNG 互补子帧、profile 覆盖层、亮度补偿、240 Hz GPU 原型）
2. **Machine-side physical validation**（10,575 captures；288 matched units；94.5→17.8/5.6；81.2% 相对削减 + 0.4% exact match **meets pre-declared targets**；cluster contrasts 76.7/88.9 pp）
3. **Human-side validation**（[STUDY-*] 占位；与第 2 条合起来构成"可读性—隐私运行点"的双侧验证）
4. **Operating envelope and attacker-cost characterization**（oracle / 150 帧 / 长曝光 / VLM / 检测追踪——原贡献 3 的全部内容换叙事不换数字；显式写明 duration–recovery 曲线未解析）

### P1.6 Related Work

| 位置 | 锚文本 | 改法 |
|------|--------|------|
| 121 | `Eye-Shield addresses human onlookers; our work instead measures machine recognition applied to short-exposure physical captures.` | 后半句 → `our system instead targets machine recognition of on-axis short-exposure captures, a channel that viewing-angle defenses leave open.` |
| 123 后（Display Privacy Protection 小节内） | — | 增加防窥膜实用性定位 1–2 句（附录 A7）。`[CITATION NEEDED: micro-louver 防窥膜的光学原理或厂商规格；先查 b_ponemon2016 是否含 privacy-filter 对照条件，有则直接引]` |
| 151 | `The contribution is a system-level UVC measurement spanning explicit-field recovery, temporal integration, and VLM recognition.` | → `The contribution is a physically validated system: explicit-field recovery, temporal integration, VLM recognition, and usability are evaluated on one UVC link and one 240 Hz panel.` |
| tab:kaleido_compare | — | 可选：加一列 practicality 维度（防护对象 on-axis/off-axis、额外硬件、是否有人因数据）。若加列导致表过宽，改为正文对比段 |

---

## P2 — 新增论证与内容（Applied Research 的增量部分）

### P2.1 Threat Model §Protection Goals（main.tex:182 段末追加）

追加 capture-escalation 目标句（附录 A4）。作用：把"150 帧攻击成功"从「方案失效」翻转为
「方案达成了迫使攻击升级的设计目标」——这是本方案最重要的一处叙事转换，且完全有数据支撑。

### P2.2 System Design §Implementation Scope（main.tex:292–294）扩写

现在只有 2 句。扩为 `\subsection{Implementation and Deployment Considerations}`，5 段骨架见
附录 A5：现状（保留原 2 句）→ 硬件前提（240 Hz 面板、GPU、引用 §Timing and Bandwidth 224 行的
带宽数字）→ 集成路线（应用层已评估；合成器/驱动层需 framebuffer 集成、面板协调、时序验证，
措辞直接复用 main.tex:941）→ profile 选择指南（readability-priority 已双侧验证用于交互场景；
high-suppression 保持 exploratory，人因未评估）→ defense-in-depth 定位（复用 main.tex:922 的
field-level policies + access controls 句）。预计 +0.4 页。

### P2.3 Discussion 改写

| 位置 | 锚文本 | 改法 |
|------|--------|------|
| 906 小节题 `Principal Findings and Research Value` | — | → `Principal Findings and Validation Outcome`；段内加一句人侧结果 `[STUDY-SENTENCE]`，并把 908 段末 `...then map how attacker capability changes these outcomes` → `...bound the operating envelope within which the validated profile holds` |
| 912–916 §Integration and Attacker Escalation | 数字全保留 | 段末追加成本解读段（附录 A6） |
| 918–922 §Profile Trade-offs and Practical Implications | 保留 | 扩为部署指南：何时启用（屏上出现敏感字段时按窗口/字段启用而非全屏常开）、明确「不防什么」清单（持续录像、长曝光、VLM 读大字号——各附 § 引用）、与 P2.2 小节互引 |
| 924–927 §VLM-Aware Implications | 原样保留 | — |

### P2.4 （可选，推荐）评估小节重排：验证在前、包线在后

现渲染顺序：Setup → Real-Capture OCR → VLM → Detection → Simulation → **User Study**（宏在 898 调用）。
Applied Research 更自然的顺序：Setup → Real-Capture OCR（机器验证）→ **User Study（人侧验证）**
→ VLM / Detection / Simulation（包线）。

机械步骤：
1. 剪切宏定义整块（593 行 `\long\def\deferreduserstudy{` 至 680 行的孤立 `}`）。
2. 去掉首尾的宏包装两行，把内容粘贴到 `\subsection{Real-Capture VLM Probes}`（509 行）之前。
3. 删除 898 行的 `\deferreduserstudy` 调用。
4. 检查交界处过渡句与 float 位置，重编译核对图表顺序编号。

不重排也成立（"先机器验证、再测绘包线、最后人因"也讲得通），重排为加分项。

---

## P3 — 语言层清单（动词/主语点位）

原则：**只改叙事框架句，不改结果句**。Results 各小节的数字陈述句全部原样。

| 行号 | 现文（锚） | 改为 |
|------|-----------|------|
| 61 | `This study measures conventional-OCR recovery` | `We present ... and validate`（P1.2） |
| 61 末 | `The study maps recovery under` | scope + deployment 句（P1.2） |
| 88 | `This study compares conventional OCR recovery` | `We implement ... and validate`（P1.4） |
| 103 | `\textbf{Controlled physical measurement}:` | 四条新贡献（P1.5） |
| 151 | `The contribution is a system-level UVC measurement` | P1.6 |
| 906 | `Principal Findings and Research Value` | P2.3 |
| 949 | `We evaluated temporal pixel masking on one UVC camera link.` | `We designed, implemented, and validated temporal pixel masking for on-axis screen-capture privacy on one UVC camera link, on both the machine and the human side.` 后接现有全部数字句（不动），插入一句 `[STUDY-SENTENCE]`，末段 baseline 句保留 |

全局注意：不要机械地把每个 "measure/map" 都换掉——Threat Model、Setup、Limitations 里的
measurement 语言是方法学描述，**应当保留**；只有摘要/引言/贡献/讨论/结论这些定位句改。

---

## P4 — 不许动清单（红线明细，自检时逐条核对）

| 行号 | 内容 | 为什么不能动 |
|------|------|-------------|
| 88/952 | `The high-suppression profile misses its descriptive $<5\%$ target` | 未达标事实；AR 叙事靠 readability-priority 达标撑，不靠掩盖这条 |
| 230 | 小节名 `Exploratory High-Suppression Profile` | exploratory 定位是防 overclaim 的锚 |
| 268 | `nominal values derived from UVC controls, not photometric measurements` | R2 |
| 414 | oracle 使相对削减跌至 58.1% 的整句 | 这是"轻度升级即跌破目标"的诚实披露 |
| 420 | high-suppression 150 帧 47.9%→53.9% 与 exploratory 表述 | R1 |
| 522 | VLM 0.5 m 会话选择透明度整段 | 数据完整性披露 |
| 586 | VLM 幻觉/exact-match 保守读法整句 | 记忆中的既定口径：VLM 单帧按 exact-match 报告 |
| 914–916 | 全周期重建 94.3–95.2%、150 帧数字 | R1 |
| 922 | `combine temporal masking with field-level policies and independent access controls` | AR 版部署指南的种子句 |
| 935–941 | Limitations 全部实质内容（仅删"未收数据"状态句） | R2 |
| 961–964 | AI 辅助披露（Codex 段） | 诚信披露 |
| 929–931 | Ethics Statement（仅改状态，不删保障描述） | 伦理 |

---

## P5 — 提交硬项（与类型无关，投稿前必须清零）

1. 5 处 `\TODO` 占位符（编译产生 `[PLACEHOLDER: ...]` 直接印在 PDF）：作者 40、单位 42、基金 44、
   通讯作者 55、致谢 962。
2. **全体作者 `IEEEbiography`**（checklist #6 硬性要求）：目前完全没有，加在 references 之后。
3. 投稿账号 ORCID 公开且填写完整（#4）。
4. 缩写正文首用重展开（#11）：`UVC`（main.tex:88，摘要已定义但正文首用未展开）、`ISP`
   （main.tex:937 → `image signal processor (ISP)`）。
5. LaTeX 源 + PDF 同传且内容一致；≤40 MB（现 2.8 MB ✓）。
6. 页数：现 18 页，P2 新增约 +0.5~1 页，仍 <20 页建议线；超了就把部署小节细节移 supplementary。
7. 参考文献撤稿扫描（#8）。
8. ScholarOne 类型勾选 **Applied Research**（Gate 通过时）；记住类型会印在发表版上。
9. 3–10 关键词（P1.3 后为 9–10 个 ✓）。

---

## 验证清单（全部改完后跑）

```bash
cd paper
# 1. 状态句与占位符清零
grep -n 'planned user study\|deferred\|have been collected\|XX\b\|PLACEHOLDER\|TODO' main.tex
# 期望：无 stale 命中（tfootnote/ethics 改后不应再含 planned/no data 表述）

# 2. 禁词表扫描（每个命中人工判断）
grep -niE 'prevent(s|ing)? (photo|captur|recover)|defeat|guarantee|immune|anti-photography|thwart|foolproof' main.tex

# 3. 编译与页数
latexmk -xelatex main.tex   # 零 error；\TODO 的 PackageWarning 应为 0 次
mdls -name kMDItemNumberOfPages main.pdf   # ≤ 20

# 4. 图表再生成后数字一致性抽查
grep -n '94.5\|17.8\|5.6\|81.2\|0.4\\%\|76.7\|88.9' main.tex
# 摘要/贡献/Setup/Results/Conclusion 五处出现的同一指标必须一致
```

人工项：
- [ ] `[STUDY-*]` 占位符全部替换，且摘要/贡献/正文/结论四处的人因数字一致
- [ ] P4 红线清单逐条确认仍在原文中
- [ ] 新增英文段落过一遍 overclaim 检查与去 AI 味（/paper-self-review + academic-humanizer）
- [ ] 若 Gate 边缘：回到 Research Article 路线，仅保留 P0 修改

**建议执行顺序与工作量**：P0（0.5–1 天，数据出来后）→ Gate 0 判定 → P1（1 天）→ P2（1–1.5 天）
→ P3（0.5 天）→ P4/P5 + 验证（0.5 天）。合计约 3–4 个工作日。

---

## 附录：英文草稿（可直接作为改写起点；落稿前过 humanizer 与 overclaim 检查）

### A2 摘要骨架（约 190 词，[STUDY-*] 待填）

> Screen content leaks to nearby cameras: a single photograph suffices for optical character
> recognition (OCR) or vision-language model (VLM) extraction, and viewing-angle defenses leave
> an on-axis lens unaffected. We present a temporal pixel-masking display pipeline that
> partitions each frame into rapidly alternating complementary subframes with profile-dependent
> overlays, implemented as a GPU-rendered prototype on a 240 Hz panel. On the machine side,
> across 10,575 physical captures from one USB Video Class (UVC) camera and 288 matched
> short-exposure units per profile, best-of-engine character recovery falls from 94.5%
> (unprotected) to 17.8% under the readability-priority profile, an 81.2% relative reduction
> with 0.4% exact match, meeting the pre-declared targets; an exploratory high-suppression
> profile reaches 5.6%. On the human side, a preregistered within-subject study with [STUDY-N]
> participants found [STUDY-TYPING-SUMMARY] and [STUDY-RATING-SUMMARY]. The operating envelope
> is explicit: a 150-frame temporal mean, fixed-grid preprocessing, and VLM recognition of
> large-font content recover substantially more text, so the defense removes the single-snapshot
> channel and forces sustained or model-assisted capture rather than preventing recovery.
> Results are scoped to one UVC camera link; deployment requirements and access-control pairing
> are reported.

### A3 贡献四条

> 1. **Practical system design and implementation.** Pixel-level complementary subframes driven
>    by a ChaCha20 CSPRNG, profile-dependent stripe/glyph overlays, luminance compensation, and
>    a GPU rendering prototype sustaining $n{=}4$ slots on a 240 Hz panel.
> 2. **Machine-side physical validation.** A 10,575-capture archive from one eMeet SmartCam S600
>    across 3 distances and 3 angles. On 288 matched common-setting units per profile, mean
>    best-of-engine recovery falls from 94.5% to 17.8% (readability-priority; an 81.2% relative
>    reduction with 0.4% exact match, meeting the pre-declared targets) and to 5.6% for the
>    exploratory high-suppression profile, with content-cluster paired contrasts of 76.7 and
>    88.9 percentage points.
> 3. **Human-side validation.** A preregistered within-subject typing and rating study on the
>    same 240 Hz platform ([STUDY-N] valid participants): [STUDY-KEY-RESULTS]. Together with the
>    machine-side results, this validates a readability–privacy operating point rather than
>    machine suppression alone.
> 4. **Operating envelope and attacker-cost characterization.** A fixed-grid preprocessing
>    oracle (40.2%/13.7%), a 150-frame temporal mean (71.1%/47.9%; 79.7%/53.9% at the common
>    settings), long exposure, VLM probes, and detection/tracking stress tests bound where the
>    protection holds and quantify the capture escalation an attacker needs; the
>    duration–recovery curve below 150 frames remains unmapped.

### A4 Protection Goals 追加句（main.tex:182 段末）

> Within this scope, the applied design goal is capture escalation: content that a single
> short-exposure snapshot would reveal should instead require sustained multi-frame recording
> or model-level recognition to recover. The evaluated sustained attack used a 150-frame mean,
> nominally 2.5 s at 60 fps; shorter sufficient durations were not mapped
> (\S\ref{sec:discussion}).

### A5 Implementation and Deployment Considerations 骨架

> 段1（保留原文 294）：current PoC, application layer, Python + GPU rendering...
> 段2 硬件前提：`Deployment requires a panel refresh rate of at least 240 Hz to keep the n=4
> basic cycle at 60 Hz (48 Hz with the inversion slot), GPU headroom for per-slot composition
> (a TITAN Xp-class card sufficed in our prototype), and fixed panel output with the luminance
> compensation limits described in \S...` （带宽数字引 §Timing and Bandwidth）
> 段3 集成路线：`The evaluated evidence covers only the application layer. Driver- or
> compositor-level deployment would require framebuffer integration, panel coordination, and
> verified slot timing.`（复用 941 措辞）
> 段4 profile 指南：`The readability-priority profile is the validated operating point for
> interactive viewing of sensitive fields; the high-suppression profile remains exploratory and
> its visual acceptability is untested. Masking is best enabled per window or per field rather
> than full-screen.`
> 段5 纵深防御：复用 922 句 + `it removes the single-snapshot channel; it is not a substitute
> for access control.`

### A6 成本解读段（Discussion §Integration and Attacker Escalation 段末）

> Read as deployment guidance, these boundaries state what the defense buys. Under the tested
> conditions, recovery comparable to an unprotected snapshot required full-cycle registration,
> a sustained 150-frame recording, or VLM recognition of large-font content. The defense does
> not prevent recovery; it removes the single-snapshot channel and forces a longer or
> better-equipped capture, and the minimum sufficient recording duration remains unmapped.

### A7 On-axis 生态位句（Related Work / Intro 用）

> Viewing-angle defenses—micro-louver privacy films and software re-rendering such as
> Eye-Shield~\cite{b_tang2023}—degrade off-axis observation but leave an on-axis camera
> unaffected `[CITATION NEEDED: film optics/vendor spec; 或核查 b_ponemon2016 的
> privacy-filter 条件]`. Temporal masking targets this residual channel: a camera directly in
> front of the screen taking short-exposure captures.

### A8 结论开头句（main.tex:949 替换）

> We designed, implemented, and validated temporal pixel masking for on-axis screen-capture
> privacy on one UVC camera link, on both the machine and the human side.
> （后接原有全部数字句不动；在第一段末插入 `[STUDY-SENTENCE]`；第二、三段原样保留。）
