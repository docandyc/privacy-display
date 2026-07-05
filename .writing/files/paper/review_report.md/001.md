# 学术论文审稿报告

**论文标题**: Temporal Pixel Masking for Reducing OCR Recovery from Short-Exposure Screen Photographs: A Single-UVC-Camera Feasibility Study

**目标期刊**: IEEE Access

**审稿日期**: 2026-07-05

**审稿模式**: 多视角完整审稿（EIC + 方法学审稿人 + 领域审稿人 + 跨域审稿人 + 魔鬼代言人）

**审稿约束**: 忽略 TODO 占位内容；假设用户调研实验可完美支撑论点；聚焦其余问题与漏洞。

---

## 一、编辑决定信 (Editorial Decision Letter)

### 决定：Major Revision (大修)

论文在学术诚实性方面表现突出——作者反复且一致地声明了方法的适用边界，主动报告 VLM 穿透、视频时域平均泄漏、组件实效不足等负面结果。10,575 张真实捕获图像的实验规模和 9 种几何配置的覆盖为短曝光 OCR 缓解提供了扎实的 empirical evidence。VLM 边界的系统化刻画对社区有实际参考价值。

然而，本次审稿识别出若干 CRITICAL 和 MAJOR 级别问题，需要在修订中实质性回应：

1. **魔鬼代言人标记了 4 项 CRITICAL 问题**（见第三节），涉及核心论点逻辑链断裂、核心组件有害、保护后恢复率反升、CSPRNG 安全价值被夸大。根据审稿铁律，存在 CRITICAL 问题的论文不能给出 Accept 决定。
2. **5 位审稿人一致推荐 Major Revision**，共识认为当前版本的贡献力度处于 IEEE Access 发表门槛的边缘。
3. **FPI 指标缺陷被 5 位审稿人一致指出**——一个作者自认有数学缺陷的指标不应用于 Pareto 前沿的硬阈值配置选择。
4. **VLM 在最高价值内容上的彻底失效**（credentials/digit strings 恢复率 50-100%）与论文的安全贡献定位存在根本张力，需要在论文定位和标题/摘要中更直接地反映。
5. **缺少与 Kaleido 等时域方法的实验对比**，仅有的 baseline 对比为 9 样本仿真 proxy，不构成公平对比。

修订后若上述问题得到实质性回应（即使结果仍为 negative），论文有望达到 IEEE Access 的发表标准。建议作者在修订中保持当前的学术诚实度——这是论文最大的优点——但在 honesty 之外加强 constructive contribution。

---

## 二、共识问题清单（按优先级排序）

以下问题被多位审稿人独立提出，按严重程度和共识度排序。

### CRITICAL 级别

#### C1. 长曝光下保护后恢复率反高于未保护 baseline —— 异常未解释

- **共识度**: EIC W2 + 魔鬼代言人 C1
- **论文位置**: Table II（第 289-291 行 vs 第 308-311 行），Section V-B Key Finding 2（第 326 行）
- **问题描述**: 未保护屏幕长曝光 char recovery 为 47.3%，deployed profile 长曝光反而升至 60.9%（+13.6 pp）。论文仅以"fixed long-exposure parameters produce nonmonotonic effects across display conditions"一笔带过，未做任何诊断实验。这一反直觉现象意味着保护机制在某些攻击模式下不仅无效，反而有害。
- **可能原因**: (a) inversion frame 改变了平均亮度导致相机自动曝光行为变化；(b) stripe/glyph overlay 在长曝光下引入了额外可识别结构；(c) 240Hz 的 5-slot 周期(~20.8ms)与 31.25ms 曝光的相位关系导致 inversion frame 的负贡献被部分窗口对齐消解。
- **改进建议**: (1) 报告 31.25ms 和 125ms 两个长曝光时长的分项恢复率；(2) 检查 inversion frame 对相机自动曝光/白平衡的影响；(3) 做曝光时间 vs 恢复率的 fine-grained sweep 验证机制；(4) 若无法解释，在 Discussion 中提升为 explicit limitation。

#### C2. mask+noise 短曝光恢复率高于 mask-only —— 核心组件有害

- **共识度**: EIC W3 + 领域审稿人 W2 + 魔鬼代言人 C2
- **论文位置**: Table II（第 294 行 vs 第 299 行），Section IV-B（第 198 行）
- **问题描述**: mask+noise 短曝光 char recovery 为 25.6%，mask-only 为 19.2%（+6.4 pp）；exact match 从 0.3% 升至 2.8%。adversarial noise 在主要评估场景中不仅无效，反而有害。然而 noise 仍是 Contribution 1 的组成部分，且所有非 base profile（Strong, Deployed, Capture-hardened）默认启用 noise。
- **深层问题**: Section IV-B 承认互补噪声方程 Eq. (1) "仅在理想线性域中严格成立"，经过 gamma 校正、量化、裁剪和相机成像后"不保证物理抵消"。理论基础被论文自我否定，实验数据也不支持。
- **改进建议**: 有三条路径——(a) 将 noise 从 primary method description 中移除，仅在 ablation 中作为 negative result 报告；(b) 重新设计 noise 使其在物理域仍满足互补性（需在 display transfer function 的 inverse domain 中构造）；(c) 提供 noise 在 digital domain 有效而 real-capture 有害的定量机理分析。同时应做 mask-only + stripe/glyph（不含 noise）的 ablation，证明 noise 的净贡献为正。

#### C3. 逻辑链断裂：稀疏采样假设被 VLM 结果直接否定

- **共识度**: 魔鬼代言人 C3 + EIC W1 + 跨域审稿人 W2
- **论文位置**: Section I-B（Core Idea, 第 85 行），Section V-C（Table III, IV），第 472-473 行
- **问题描述**: 核心逻辑链为 (a) 人眼时域积分 > 相机曝光窗口 → (b) 相机只捕获部分像素 → (c) OCR 无法恢复。步骤 (b)→(c) 的隐含假设是"稀疏采样足以破坏机器识别"。但 VLM 在同一张照片上从同样的稀疏像素子集恢复了 91.5% char / 77.8% exact（对比 OCR 的 8.4% / 0%）。VLM 的 language prior 可从部分视觉输入补全文本，绕过了 binarization 瓶颈。
- **关键含义**: 方法的安全基础不是物理采样原理，而是 OCR pipeline 的特定弱点。一旦攻击者升级到 VLM（2025 年的现实），物理基础完全不成立。更严重的是，失效集中在最高价值内容（credentials 97.6%、digit strings 100%），而 CET6 dense documents 仅 0.4-18.5%——防护效果与内容安全价值呈反向关系。
- **改进建议**: (1) 在 Introduction 中更早、更直接地说明 VLM 失效，而非推迟到 Section V-C；(2) 至少对一个 countermeasure 方向（建议 font-size-adaptive mask granularity，因已有 Section V-C 的 mask granularity 观察支撑）进行 preliminary evaluation；(3) 在标题中加入"conventional OCR"限定词。

#### C4. CSPRNG 的安全价值被夸大

- **共识度**: 魔鬼代言人 C4 + 领域审稿人 W5
- **论文位置**: Section I-D Contribution 1（第 100 行），Section III-C（第 158 行），Section IV-A（第 180 行）
- **问题描述**: 论文使用 ChaCha20 CSPRNG 并将其作为方法核心组件描述。但 Section III-C 同时承认"Once an attacker obtains and registers a complete cycle, an unknown seed cannot prevent linear reconstruction"。攻击者执行视频时域平均时完全不需要知道 seed——只需累加足够帧数覆盖完整周期。CSPRNG 的实际安全增益仅为：(a) 防止固定空间模式被学习；(b) 防止跨周期重复——本质是 pattern randomization，不是 cryptographic security。"CSPRNG" 和 "cryptographically secure" 的术语使用暗示了比实际更强的安全保证。
- **改进建议**: 将 CSPRNG 的角色重新定位为"per-cycle mask randomization to prevent fixed-pattern learning and cross-cycle correlation"，明确区分两层安全属性：(1) per-cycle randomness（CSPRNG 提供）；(2) anti-integration security（CSPRNG 不提供，需非线性 profile）。

---

### MAJOR 级别

#### M1. FPI 指标存在已知数学缺陷，仍被用于 Pareto 前沿硬阈值配置选择

- **共识度**: 5/5（全部审稿人一致）—— **本审稿的最高共识问题**
- **论文位置**: Section V-A（第 272 行，FPI 定义及不连续性声明），Section V-E（第 721 行，Pareto 前沿使用 FPI<0.1 硬阈值）
- **问题描述**: FPI 公式在 $f_p=60$ Hz 处不连续——低频分支在窄带内反而低于 60Hz 处的值，违反"频率越低闪烁越严重"的直觉。论文自认"not an IEEE 1789 standard metric or clinical threshold; it serves only for within-paper ranking"，但随后在 Section V-E 将 FPI<0.1 用作绝对安全阈值排除配置，构成自相矛盾。FPI<0.1 的阈值来源未给出任何依据。
- **改进建议**: (1) 使用 IEEE 1789-2015 标准的 flicker risk assessment 替代，或至少与 IEEE 1789 的 Low/Risk/Medium/High Risk 级别映射对照；(2) 修复不连续性（使用连续函数替代分段公式）；(3) 若仅用于 ranking，则移除 Section V-E 的硬阈值，改为在 Pareto 前沿上标注 FPI 值供参考。

#### M2. 亮度补偿未实现，所有 usability 代理指标基于未经光度验证的数字模型

- **共识度**: 4/5（EIC + 方法学 + 领域 + 跨域）
- **论文位置**: Section IV-C（第 200-202 行），Section V-A（第 272 行），Section V-E（第 721 行），Fig. 5, Fig. 7
- **问题描述**: Section IV-A 自身已指出"the average radiance over one cycle is $\mathbf{I}/n$, not $\mathbf{I}$"。PoC 未实现 per-slot 动态背光协调或光度验证，所有 $\Delta E_{00}$ 和 SSIM 来自 digital integration model。数字域 $\sum \mathbf{I}_k = \mathbf{I}$ 在数学上保证 SSIM 接近 1（报告 0.9995），但完全不反映真实面板上的亮度衰减——真实显示上 cycle-averaged luminance 降至 $1/n$，$\Delta E$ 会远大于数字模型报告的值。
- **改进建议**: (1) 在所有报告 $\Delta E$/SSIM 的位置加注"computed on digital models assuming $1/n$ luminance compensation that the PoC does not implement; real-panel values expected to be substantially worse"；(2) 在 Pareto 分析中标注真实面板的理论 $\Delta E$ 下界；(3) 增加 photometric validation 的 future work 段落。

#### M3. Capture-hardened profile 的感知代价完全未量化

- **共识度**: 4/5（EIC + 领域 + 跨域 + 魔鬼代言人）
- **论文位置**: Section IV-E（第 220 行），Section V-D（第 498 行），Section V-B Key Finding 3（第 328 行），Section VI-C（第 747 行）
- **问题描述**: capture-hardened profile 是唯一达到 5.0% char / 0% exact 的配置，也是唯一在长曝光下有显著改善（9.3%）的配置。但用户调研明确排除该 profile，论文承认"produces visible stripes and grain"且"perceptual cost unquantified"。即使假设用户调研完美支撑 deployed profile 的可用性，capture-hardened profile 的可用性仍是空白。
- **根本悖论**: deployed profile 在短曝光下 15.1% char（高于 5% 目标），长曝光下 60.9% char / 96.5% sensitive-token；capture-hardened profile 视频泄漏 47.9%——没有一组配置同时满足"可用"和"安全"。
- **改进建议**: (1) 至少为 capture-hardened profile 添加 pilot 可读性数据（3-5 名研究者的 informal readability rating）；(2) 报告 capture-hardened profile 的 digital SSIM 和 $\Delta E$ 并与 deployed 对比；(3) 扩展 Fig. 6 的 parameter grid，绘制 stripe/glyph amplitude vs video recovery rate 的 dose-response curve，判断是否存在使 recovery <10% 的参数组合及其对应的 visual cost。

#### M4. VLM 在最高价值内容上的彻底失效构成存在性威胁

- **共识度**: 4/5（EIC + 领域 + 跨域 + 魔鬼代言人）
- **论文位置**: Table III（第 427-428 行），Table IV（第 455-461 行），Section V-C Key Finding 2（第 472-473 行），Section VI-D（第 750-752 行）
- **问题描述**: capture-hardened profile 在 0.5m 短曝光下对 Qwen3-VL exact-match 达 77.8%。失效集中在最高价值内容：credentials 97.6%、digit strings 100%、code snippets 94.9% character recovery。而 CET6 dense documents 仅 0.4-18.5%。Section VI-D 提出的三个 countermeasure 方向均"None have been experimentally validated"。
- **改进建议**: (1) 将 VLM failure 从"boundary probe"提升为论文核心 negative result，在 Abstract 中与 OCR mitigation result 并列；(2) 至少对 font-size-adaptive mask 进行初步验证；(3) 讨论 VLM attacker cost（API 调用成本 <$0.01）与 defense deployment cost 的 asymmetry。

#### M5. 缺少与 Kaleido 等时域方法的实验对比 + baseline 对比不充分

- **共识度**: 领域审稿人 W1 + W6 + 魔鬼代言人 Observation 4
- **论文位置**: Section II-B（第 130 行），Section V-E（第 626 行，9 样本仿真 proxy），Fig. 5
- **问题描述**: 论文详细论述了与 Kaleido 的机制差异，但全文无任何实验对比。Section V-E 的 baseline 对比仅在 simulation 中用 9 个样本对比 dimming/blur/pixelation/off-axis proxy，参数不匹配，样本量不足，缺少 real-capture baseline 和 temporal method baseline。Kaleido 的 anti-piracy 目标恰好是论文方法失效的视频场景——如果比较，论文方法在视频场景下可能远不如 Kaleido。
- **改进建议**: (1) 至少在 simulation 层面实现 Kaleido 的 chrominance-complementary frame decomposition 并对比 full-cycle integration recovery 和 short-exposure recovery；(2) 将 baseline 样本从 9 扩展至至少 60-120；(3) 在等效 readability cost（相同 $\Delta E$ 或 SSIM）下对比各方法的 OCR recovery rate。

#### M6. 动机-评估失配：motivation 提到 smartphones/smart glasses 但仅测试 UVC webcam

- **共识度**: 4/5（EIC + 领域 + 跨域 + 魔鬼代言人）
- **论文位置**: Section I（第 74 行），Section I-C（第 87 行），Section V-A（第 264 行）
- **问题描述**: Introduction 以 smartphones 和 smart glasses（Ray-Ban Meta）作为威胁动机，但所有实验仅用 eMeet S600 UVC webcam。更关键的是，智能手机 auto-exposure 典型 10-33ms，恰好跨越论文的基本 cycle（16.7-20.8ms），落入"long exposure"攻击区间——在该区间 deployed profile 的 sensitive-token recovery 为 96.5%。论文的方案对最现实的威胁很可能无效。
- **改进建议**: (1) 至少补充一组 smartphone auto-exposure 探索性实测数据（即使是 negative result）；(2) 若无法获取，在 Abstract 前两句即声明 camera scope limitation，并将 title 中"Feasibility Study"的限定贯穿全文。

#### M7. 实验设计不平衡，bootstrap CI 解释力受限

- **共识度**: 3/5（EIC + 方法学 + 魔鬼代言人）
- **论文位置**: Section V-B（第 278 行），Table I/II（deployed N=459/153 vs 其他 324/108），Section V-A（第 270 行）
- **问题描述**: deployed profile 对 5 项内容重复捕获导致 N 不对称。同一内容的重复捕获意味着 captures 之间不独立，bootstrap CI 的覆盖率可能被高估。0.49ms 和 3.91ms 两组校准参数中，0.5m/15° 位置使用 0.49ms 导致视频帧严重欠曝但仍纳入 pooled 分析。
- **改进建议**: (1) 使用 cluster bootstrap（以 content item 为 cluster）；(2) 报告排除 0.49ms 欠曝位置后的 pooled 结果作为 sensitivity analysis；(3) 对 deployed profile 的重复捕获做 leave-one-round-out 分析。

#### M8. Sensitive-token recovery 远高于 char recovery —— 最敏感内容最易被恢复

- **共识度**: 3/5（EIC + 跨域 + 魔鬼代言人）
- **论文位置**: Table II（deployed long: 60.9% char vs 96.5% token；capture-hardened long: 9.3% char vs 34.9% token）
- **问题描述**: sensitive tokens（digits, account numbers, URLs）的结构特征（大字体、短长度、有限字符集）使其在 degraded image 中更容易被恢复。防护效果与内容安全价值呈反向关系。deployed profile 长曝光 96.5% sensitive-token recovery 意味着 credentials 几乎完全可恢复。
- **改进建议**: (1) 在 Threat Model 中将 long-exposure 攻击者提升为 realistic threat；(2) 增加 sensitive-token divergence 的机理分析；(3) 在 Abstract 中加入 long-exposure sensitive-token 的失败数据。

#### M9. Best-of-engine 口径代表性有限

- **共识度**: 2/5（方法学 + 魔鬼代言人）
- **论文位置**: Section V-A（第 270 行），Table II, Table IV
- **问题描述**: 仅 3 个引擎族，无保护时三者差异巨大（Surya 37.1% vs Tesseract 84.3%）。best-of-engine 的 94.1% 远超任何单引擎。3 引擎的"best"可能远低于真实攻击者能力（VLM 已证明可大幅突破）。论文未同时报告 per-engine average 作为对照。
- **改进建议**: (1) 明确声明 best-of-engine 的局限性；(2) 报告 per-engine average 作为对照口径；(3) 讨论 bias 方向。

#### M10. 参考文献问题

- **共识度**: 领域审稿人 W7
- **论文位置**: refs.bib
- **已核验问题**:
  - `b_ponemon2016`: note 中"Accessed: Jul.~2, 2026"为未来日期，需修正
  - `b_ciede2000`: key 为"2000"但 year=2005，建议统一为 b_ciede2005
  - `b_fernandez2024`: arXiv preprint，该工作已发表于 USENIX Security 2025，应更新
  - `b_wang2026`: CHI 2026 论文，需确认公开可用性
  - 多个 arXiv preprint（b_ghiasi2024, b_li2025, b_zhao2023, b_zhong2023, b_song2018）应检查是否有正式发表版本
  - **缺失 IEEE 1789-2015 标准引用**（论文讨论 flicker safety 但未引用该权威标准）
  - **VLM 相关文献引用密度不足**：核心论断"VLMs can complete glyph contours via visual encoding and language priors"无引用支撑

---

### MINOR 级别

#### m1. 检测/跟踪实验证据强度低，应降级或移至附录

- **共识度**: 4/5（EIC + 方法学 + 跨域 + 魔鬼代言人）
- **论文位置**: Section V-D（Table IV, V），Section V-E（Table VI 仅 8 张图，Table VII 使用非标准评估后端）
- **问题描述**: 仿真检测仅 8 张 COCO 图像；real_clean baseline 本身极低（mAP50 39.2-50.2%, HOTA 14.2-15.8%），floor effect 可能是主要驱动；TrackEval 运行失败，MOTA 出现负值；8 张图的 mAP 以与 150 张图相同的精度呈现，可能误导读者。
- **改进建议**: 将 8 张图诊断结果从正式 Table 降级为 inline text 或 appendix；对 150 张真实检测图报告 bootstrap CI；移除或明确标注 MOTA 列不可比。

#### m2. GLM-4.5V 高失败率可能引入 selection bias

- **共识度**: 方法学 W6
- **论文位置**: Section V-C（第 411 行），Table III（GLM 列 N=26, 31, 33 等）
- **问题描述**: 0.5m 处 468 次调用中 32 次失败（6.8%），1.0m 处 360 次中 16 次失败（4.4%）。若失败非随机（集中在更难识别的 capture），则有效样本的恢复率被偏估。
- **改进建议**: 分析失败 call 的特征分布；对 GLM 结果做 worst-case（失败=0%）和 upper-bound（失败=100%）分析。

#### m3. 视频聚合视图对方法选择高度敏感

- **共识度**: 方法学 W8
- **论文位置**: Table III（1.5m capture-hardened: single_best 8.3% exact vs temporal_mean 66.7% exact）
- **问题描述**: 不同聚合方式结果差异达 8 倍（exact）。0.5m 仅报告 temporal_mean，其他三种聚合被 archived 但未进入 Table III，限制跨距离可比性。
- **改进建议**: 在 0.5m 也报告全部 4 种聚合方式；报告 best-of-aggregation 口径；对聚合方式间差异做 bootstrap CI。

#### m4. 摘要-结论一致性：VLM 结果在摘要中过于模糊

- **共识度**: EIC W8
- **论文位置**: Abstract（第 58 行）vs Conclusion（第 782 行）
- **问题描述**: 摘要称"three commercial VLMs recover substantial portions"但未给数字；结论给出具体数字（77.8%, 33.3-47.2%）。摘要提到 10,575 captures 但未区分核心 short-exposure subset 规模。
- **改进建议**: 在摘要中加入至少一个 VLM 失效具体数字；明确 10,575 中支撑核心结论的 subset 规模。

#### m5. 会话选择透明度

- **共识度**: 方法学 W12 + 魔鬼代言人 M1
- **论文位置**: Section V-C（第 413 行）
- **问题描述**: 0.5m VLM 实验排除了全黑替代会话。论文给出合理理由（input alignment + conservative reporting），但选择空间是否完整（是否存在第三个或更多候选会话）未说明。
- **改进建议**: 明确声明候选会话总数；将排除会话的 0% 结果作为 appendix 报告。

#### m6. 用户调研协议占据 Evaluation section 过大篇幅

- **共识度**: EIC W10
- **论文位置**: Section V-D（第 483-508 行，约 120 行）
- **问题描述**: 纯协议章节在 Experimental Evaluation 中占据过大篇幅，而紧随其后的 Section V-E 描述简短，叙事节奏不平衡。
- **改进建议**: 将协议细节移至 Supplementary Material，正文仅保留 1-2 段概述。

---

## 三、魔鬼代言人 CRITICAL 问题标记

根据审稿铁律，魔鬼代言人标记的 CRITICAL 问题不能被编辑决定忽略。本次审稿中魔鬼代言人标记了 4 项 CRITICAL 问题（C1-C4），均已在第二节共识问题清单中详细列出。这些问题的核心挑战是：

> 论文实质上证明的是：时域掩码仅在最弱的、对手不会主动选择的攻击条件下有效——这是一个 security boundary characterization，而非 security contribution。一个对手只需花费几秒钟录视频或一次 API 调用即可突破防护的安全方案，其 threat model 的现实相关性存疑。

作者需要在修订中正面回应这一挑战——不是通过缩小声明范围来回避，而是通过至少一个 validated countermeasure 或 cost-benefit analysis 来论证方法在退守后的定位仍具实际意义。

---

## 四、修订路线图 (Revision Roadmap)

按优先级排序，建议作者按以下顺序处理：

### 第一优先级（必须解决，影响发表决定）

| # | 问题 | 建议行动 | 工作量 |
|---|------|----------|--------|
| R1 | C1 长曝光恢复率反升 | 诊断实验：分项曝光时长 + 相位分析 + inversion frame 影响检查 | 中 |
| R2 | C2 noise 组件有害 | ablation：mask-only + stripe/glyph（不含 noise）vs 含 noise；决定是否从 method 移除 noise | 中 |
| R3 | C3 VLM 逻辑链断裂 | 至少对 font-size-adaptive mask 做初步验证；在 Introduction 更早说明 VLM 失效 | 中-高 |
| R4 | M1 FPI 指标缺陷 | 采用 IEEE 1789 标准或修复不连续性；移除 FPI<0.1 硬阈值 | 低-中 |
| R5 | M4 VLM 失效定位 | 在 Abstract/标题中反映 VLM 限制；至少一个 countermeasure 的 preliminary evaluation | 中-高 |

### 第二优先级（显著影响论文质量）

| # | 问题 | 建议行动 | 工作量 |
|---|------|----------|--------|
| R6 | M2 亮度补偿缺失 | 在所有 $\Delta E$/SSIM 位置加注数字模型局限 | 低 |
| R7 | M3 capture-hardened 可用性 | pilot 可读性数据 + dose-response curve | 中 |
| R8 | M5 缺少 temporal method 对比 | 实现 Kaleido 风格 baseline 并对比 | 中-高 |
| R9 | M6 动机-评估失配 | 至少一组 smartphone exploratory data 或更显式的 scope 限定 | 中 |
| R10 | C4 CSPRNG 定位 | 重新定位为 pattern randomization，明确区分两层安全属性 | 低 |

### 第三优先级（必要但非决定性）

| # | 问题 | 建议行动 | 工作量 |
|---|------|----------|--------|
| R11 | M7 非平衡设计 | cluster bootstrap + sensitivity analysis | 中 |
| R12 | M8 sensitive-token divergence | 机理分析 + 在 Abstract 加入失败数据 | 低-中 |
| R13 | M9 best-of-engine 口径 | 报告 per-engine average 对照 | 低 |
| R14 | M10 参考文献问题 | 修复未来日期、更新 preprint、增加 IEEE 1789 和 VLM 文献 | 低 |
| R15 | m1 检测/跟踪降级 | 8 张图结果移至 appendix；修复 TrackEval 或标注不可比 | 低-中 |

---

## 五、评分汇总

| 维度 | EIC | 方法学 | 领域 | 跨域 | 平均 |
|------|:---:|:------:|:----:|:----:|:----:|
| 原创性 | 5 | — | — | — | 5 |
| 显著性 | 4 | — | — | — | 4 |
| 严谨性 | 6 | — | — | — | 6 |
| 清晰度 | 7 | — | — | — | 7 |

> 注：方法学、领域、跨域审稿人未给出数值评分，以上为 EIC 评分。整体评估：原创性偏低（时域掩码非新颖，增量贡献中 noise/inversion 实效不足），显著性偏低（声明范围过度收敛，VLM 失效覆盖最高价值内容），严谨性中等（实验规模可观但设计不平衡、指标有缺陷），清晰度较高（结构清晰、边界声明一致，但叙事节奏不均）。

---

## 六、审稿人共识与分歧

### 全体共识（5/5）

- **FPI 指标有已知缺陷且不应用于硬阈值配置选择**。这是本审稿的最高共识问题。
- **论文的学术诚实性值得肯定**，但诚实声明 limitation 不使 limitation 本身变成贡献。
- **Major Revision** 是当前版本的适当决定。

### 多数共识（3-4/5）

- 亮度补偿缺失导致 usability 代理指标不可靠
- capture-hardened profile 的可用性是未量化的关键空白
- VLM 失效对最高价值内容构成存在性威胁
- 动机-评估失配（smartphones vs UVC webcam）削弱实际价值
- 检测/跟踪实验证据强度低，应降级

### 审稿人分歧

- **CSPRNG 安全价值**：魔鬼代言人标记为 CRITICAL（C4），领域审稿人标记为 Major（W5），其他审稿人未特别关注。编辑综合后将 CSPRNG 定位问题列为 CRITICAL（因 DA 标记），但建议作者的处理力度可介于 CRITICAL 和 Major 之间——主要是术语和定位修正，而非实验工作。

---

## 七、总结

这篇论文的核心定性结论——temporal pixel masking 在短曝光条件下显著降低 conventional OCR 恢复率——在 10,575 张真实捕获的支持下是可靠的。论文的学术诚实度在同类工作中罕见，VLM 边界的系统化表征对社区有参考价值。

但论文面临一个根本性张力：方法在最现实的攻击场景（录视频 + VLM API）下失效，且失效集中在最高价值内容上。魔鬼代言人尖锐地指出：论文实质上证明的是"时域掩码仅在最弱的攻击条件下有效"。作者需要在修订中正面回应这一挑战——要么通过至少一个 validated countermeasure 证明方法可以扩展到更强攻击者，要么通过 cost-benefit analysis 论证"增加 opportunistic bulk collection 成本"的退守定位仍有实际意义，要么更彻底地将论文重新定位为"conventional OCR short-exposure mitigation 的系统性失效边界分析"。

建议作者优先处理第一优先级的 5 项修订（R1-R5），这些直接影响发表决定。在保持学术诚实度的同时，加强 constructive contribution 是本次修订的核心方向。
