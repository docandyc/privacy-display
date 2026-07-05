# 补充审稿报告（第二轮独立 Review）

**论文标题**: Temporal Pixel Masking for Reducing OCR Recovery from Short-Exposure Screen Photographs: A Single-UVC-Camera Feasibility Study

**审稿日期**: 2026-07-05

**审稿定位**: 在已有 `review_report.md`（第一轮多视角审稿，识别 C1-C4 / M1-M10 / m1-m6）基础上的**补充审稿**，聚焦第一轮未覆盖或未充分展开的问题。

**审稿约束**: 同第一轮——忽略 TODO 占位内容；假设用户调研实验可完美支撑论点。

---

## 一、总体评价

第一轮审稿已经非常全面地覆盖了论文的核心逻辑链问题（VLM 穿透、noise 有害、长曝光异常、CSPRNG 夸大）和主要方法学缺陷（FPI 不连续、亮度补偿缺失、实验不平衡）。以下补充的问题分为三类：(A) 物理机制层面的遗漏，(B) 理论/分析层面的空白，(C) 写作与内部一致性问题。其中 A 类问题中有多项可能影响核心实验结论的解释力，建议作者在修订中与第一轮 CRITICAL/MAJOR 问题一并回应。

---

## 二、补充问题清单

### A. 物理机制层面的遗漏

#### A1. 像素响应时间与 temporal ghosting（严重度：MAJOR）

论文假设子帧在时域上是离散切换的——即每个像素在一个 time slot 内完美显示对应子帧内容，下一个 time slot 立即切换到新值。但真实 LCD 面板的像素响应时间（GtG）通常为 1-5ms，VA 面板可达 8ms 以上。在 240Hz 刷新率下，每个子帧的显示时间约为 4.17ms（$n=4$ 基本周期），这意味着像素过渡时间可能占据子帧持续时间的 25-100%。

**影响**：(a) 像素过渡期间，显示内容混合了相邻两个子帧的信息，产生"ghost subframe"，攻击者单次曝光可能同时捕获两个子帧的部分信息，降低保护效果；(b) 响应时间的温度依赖性意味着冷启动和长时间使用后的保护效果可能不同；(c) 不同灰度级之间的响应时间不对称（通常暗→亮比亮→暗更慢）可能导致某些像素值组合的保护效果系统性偏弱。

**改进建议**：(1) 报告所用显示器的面板类型（IPS/TN/VA/OLED）和标称 GtG 响应时间；(2) 讨论 temporal ghosting 对单次曝光恢复率的理论影响上界；(3) 在 Limitations 中增加 display panel response time 作为影响泛化性的因素。

#### A2. Rolling shutter 与子帧时序的交互分析不足（严重度：MAJOR）

Threat Model 的"Not yet adequately covered"列表中提到了 rolling-shutter row alignment，但全文未给出任何分析。绝大多数 CMOS 相机传感器（包括 S600 webcam 和所有智能手机）使用 rolling shutter，逐行曝光，行间延迟通常为 10-30μs，整帧读出时间约 5-30ms。

**关键问题**：当 rolling shutter 的整帧读出时间（例如 15ms）接近或超过子帧持续时间（4.17ms）时，单张"短曝光"照片的不同行实际上捕获了不同的子帧。这意味着论文中的"短曝光"条件可能并不等同于"只捕获一个子帧"——图像的上半部分和下半部分可能包含不同的子帧内容。

**影响**：(a) 这实际上可能*有利于*攻击者——单张照片的总信息量可能超过论文估计；(b) 也可能在某些特殊对齐下*有利于*防护——如果恰好每行都只覆盖了一个子帧的稀疏部分。论文未区分这两种情况。

**改进建议**：(1) 估算 S600 的 rolling shutter 读出时间并与子帧持续时间对比；(2) 检查真实捕获图像中是否存在行间子帧切换的迹象（如图像中出现水平条纹边界）；(3) 在 Discussion 中讨论 rolling shutter 对 short-exposure 结论方向的偏倚。

#### A3. 环境光照对实验结果的未控制影响（严重度：MINOR-MAJOR 边界）

论文在 Section V-A 中承认"Ambient illuminance was not recorded"，但仅将其归入 Limitations 的一条。实际上，环境光照可能通过两条路径显著影响实验结果：(a) 环境光影响相机的自动曝光/自动白平衡/自动增益控制（AGC），改变相机对屏幕内容的采样特性；(b) 环境光在屏幕表面的反射叠加在显示内容上，改变了实际被相机捕获的信噪比。

在 9 个几何配置（3 距离 × 3 角度）的采集过程中，如果实验跨多天进行或在自然光条件下进行，环境光照的变化可能引入系统性偏差——某些几何配置可能恰好在更亮/更暗的环境条件下采集，导致恢复率差异被错误归因于几何因素。

**改进建议**：(1) 在 Limitations 中将环境光未控制的影响从一句提及扩展为显式讨论；(2) 检查不同几何配置间的恢复率方差是否与环境光照变化相关（如果实验时间记录可用）。

#### A4. 显示面板类型未报告，结论的可复现性受限（严重度：MINOR）

论文报告了显示器分辨率为 1920×1080 @ 240Hz，但未报告显示器型号、面板类型（IPS/TN/VA/OLED）、背光类型（全局/局部调光）或像素排列方式。这些参数直接影响 temporal masking 的有效性：

- OLED 像素自发光，响应时间极短（~0.1ms），temporal ghosting 最小
- IPS LCD 响应时间 3-5ms，temporal ghosting 显著
- VA LCD 响应时间更长，temporal ghosting 更严重
- 局部调光（local dimming）背光可能在子帧切换时引入额外的亮度波动

**改进建议**：在 Experimental Setup 中报告显示器型号和面板类型。

---

### B. 理论/分析层面的空白

#### B1. 缺少信息论形式化分析（严重度：MAJOR）

论文使用 normalized mutual information $I(X;Y)/H(X)$ 作为 Pareto sweep中的安全代理指标，但全文缺少对方案安全性的信息论形式化分析。具体而言：

- 在 $n$ 个子帧、每个子帧包含 $1/n$ 像素的条件下，单帧短曝光照片的**理论最大信息泄漏**是多少？
- 该泄漏如何随 mask cell size（1 pixel vs 2 pixels）、stripe/glyph overlay 幅度、以及噪声强度 $\varepsilon$ 变化？
- 是否存在一个闭式表达或渐近界来描述 $n \to \infty$ 时的安全极限？

论文目前仅以 empirical observation 报告"恢复率从 94.1% 降至 15.1%"，但缺少理论框架来解释*为什么*是这个数值，以及它在什么条件下是紧的。

**改进建议**：(1) 在 System Design 或 Evaluation 中增加一节简要的信息论分析，推导单子帧的理论最大信息保留率（对 $n=4$ 的无噪声理想情况，理论值为 $1/n = 25\%$，与实际 19.2% mask-only 的对比可提供 insight）；(2) 讨论实际恢复率与理论界的差距来源（相机 ISP 非线性、moiré 效应等）。

#### B2. 子帧数量 $n=4$ 的选择缺乏原则性论证（严重度：MINOR-MAJOR 边界）

论文选择 $n=4$ 作为默认配置，理由是"60Hz 作为最低 cycle rate 需要 $f_r \geq 60n$，在 $n=4$ 时对应 240Hz"。但这只是硬件约束下的工程选择，不是安全-可用性权衡的最优选择。Pareto sweep 涵盖了 $n \in \{2, 4, 6, 8\}$，但所有真实捕获实验均使用 $n=4$，其他 $n$ 值仅在数字仿真中评估。

**问题**：(a) $n=2$ 在 120Hz 即可运行，降低了硬件门槛，但安全性如何？论文未报告 $n=2$ 的真实捕获数据；(b) 从 $n=2$ 到 $n=4$ 的安全性增益是否显著大于从 $n=4$ 到 $n=6$？如果边际收益递减，$n=4$ 可能是合理的，但这需要数据支持。

**改进建议**：(1) 至少报告 $n=2$ 和 $n=6$ 各一组真实捕获 short-exposure 数据作为 ablation；(2) 或提供信息论分析说明 $n=4$ 是 diminishing returns 的拐点。

#### B3. 卡方均匀性检查的统计参数未报告（严重度：MINOR）

Section IV-A 提到"the implementation applies a chi-square uniformity check on generated slot counts, re-sampling the seed upon failure"，但未报告：(a) 卡方检验的显著性水平 $\alpha$；(b) 重新采样的频率（即多少比例的种子未通过检验）；(c) 当 $n=4$、总像素数为 $1920 \times 1080 = 2,073,600$ 时，期望的 slot count 为 518,400，卡方检验的自由度为 3。

如果拒绝率极低（例如 < 0.1%），则该检查几乎没有实际作用；如果拒绝率较高（例如 > 5%），则 ChaCha20 的种子空间可能在该应用条件下存在系统性偏差。

**改进建议**：报告卡方检验的 $\alpha$ 值和实际拒绝率。

#### B4. 跨周期像素分配的时域相关性未量化（严重度：MINOR）

论文声称 CSPRNG "reduces fixed patterns and cross-cycle correlation"，但未实际测量跨周期的像素分配相关性。对于 Fisher-Yates shuffle 生成的互补 mask，连续两个周期中同一像素被分配到同一 slot 的概率应为 $1/n = 0.25$（$n=4$ 时）。

**问题**：如果攻击者无法获取完整周期但可以获取连续两帧（概率较高，因为大多数相机连拍模式或视频帧间隔 < 周期长度），那么跨周期相关性决定了第二帧相对于第一帧的边际信息增益。如果相关性接近 $1/n$，则多帧攻击的信息增益较大；如果显著偏离 $1/n$（由于 ChaCha20 种子变化），则信息增益较小。

**改进建议**：测量并报告连续周期间的像素 slot 分配联合分布，验证其是否接近独立均匀分布。

#### B5. 人眼时域积分模型的物理基础需要加强（严重度：MINOR）

论文的核心前提是人类视觉系统的时域积分能力优于短曝光相机。但"persistence of vision"是一个被心理学界认为过于简化的概念——实际的时域视觉处理涉及 Bloch 定律（亮度-持续时间互惠，仅在 ~100ms 以下成立）、临界闪烁融合频率（CFF，受亮度、视网膜位置、刺激大小影响）、以及更复杂的时域对比敏感度函数（TCSF）。

论文引用了 Davis et al. (2015) 的"humans perceive flicker artifacts at 500Hz"和 Cai et al. (2024) 的 TCSF 模型，但核心假设——人眼能有效积分 $n=4$ 的互补子帧并感知完整图像——缺少直接引用支撑。特别是在 48Hz 全周期频率（含 inversion frame 配置）下，许多观察者可能感知到明显闪烁，这不仅影响用户体验，更影响"人眼能积分完整内容"这一前提本身——如果用户感知到的是闪烁而非完整图像，则安全-可用性权衡的前提就不成立。

**改进建议**：(1) 引用 TCSF 模型（如 Cai et al. 2024 或 de Lange 模型）预测在 48-60Hz 周期频率下人眼的时域积分质量；(2) 讨论 CFF 对"人眼积分优于相机"前提的约束条件。

#### B6. 缺少 adaptive attacker 的分析（严重度：MINOR）

论文假设攻击者不知道当前周期的 mask seed 和 phase starting point，但讨论了攻击者知道算法和参数（$n$、period）的情况。在两者之间存在一个重要的中间地带——adaptive attacker：

- 攻击者录制视频后，可以通过分析帧间差异推断 cycle frequency（无需知道 seed）
- 知道 cycle frequency 后，攻击者可以选择性地提取恰好覆盖完整周期的帧子集进行线性叠加
- 攻击者不需要知道 phase starting point——只需搜索所有可能的 phase offset 并选择叠加后信息量最大的

论文在 Section III-C 中承认"Once an attacker obtains and registers a complete cycle, an unknown seed cannot prevent linear reconstruction"，但未分析一个 adaptive attacker 从一段普通视频中自动完成这一过程的技术可行性和所需的最短视频长度。

**改进建议**：简要分析 adaptive attacker 从视频中自动推断 cycle frequency 和执行 phase search 的可行性，并给出所需的最短视频时长估计。

---

### C. 写作与内部一致性问题

#### C1. "vlm" profile tag 命名造成概念混淆（严重度：MINOR）

Data and Code Availability 部分提到"The legacy `vlm` profile tag in historical records denotes the capture-hardened configuration"。这意味着代码中 capture-hardened profile 的内部名称是 "vlm"，但恰恰是这个 profile 在 VLM 攻击下表现最差（credentials 97.6%、digit strings 100% 恢复）。如果代码和数据的标签在最终发布时保留，极易造成误解。

**改进建议**：在最终代码/数据发布时将 "vlm" tag 重命名为 "capture_hardened" 或类似的一致名称，或在 data archive 的 README 中显著说明这一映射。

#### C2. 内容类型覆盖限于英文/ASCII，但论文暗示更广泛的适用性（严重度：MINOR）

所有 12 个 content items 均为英文文本（CET6 文档、英文代码、ASCII 凭证、英文段落等）。但 OCR 引擎 EasyOCR 支持 80+ 种语言，Surya 定位为"multilingual document OCR toolkit"。不同语言的字符复杂度差异巨大——中文/日文/韩文的笔画密度远高于拉丁字母，在相同的 mask granularity 下，CJK 字符的笔画拓扑更容易被子帧采样破坏（因为笔画宽度与 mask cell size 更接近），但也可能因为字符间的视觉相似度更高而使 OCR 更容易混淆。

**改进建议**：(1) 在 Limitations 中明确测试内容限于英文/ASCII；(2) 讨论不同字符复杂度对保护效果的预期影响方向（不必做实验，但应给出定性分析）。

#### C3. 仿真与真实捕获之间的 gap 缺少系统性讨论（严重度：MINOR-MAJOR 边界）

论文同时包含软件仿真（Section V-E）和真实捕获（Section V-B）两套实验，但从未系统比较两者之间的差距。例如：

- 仿真单子帧 OCR 恢复率：0-2.6%（Table VII），而真实捕获 mask-only 短曝光恢复率：19.2%——差了约一个数量级
- 仿真 full-cycle integration 恢复率：95.2%，而真实捕获 video temporal averaging：71.1%（deployed）/ 47.9%（capture-hardened）

这两个差距说明相机 ISP pipeline、moiré 效应、光学模糊等因素对攻击者和防护者的影响方向不同——短曝光下真实相机比理想仿真更有利于攻击者（19.2% vs 0-2.6%），而视频聚合下真实相机比理想仿真更不利于攻击者（71.1% vs 95.2%）。这一系统性差异对理解方法的实际部署价值至关重要，但论文未专门讨论。

**改进建议**：增加一节或一段 simulation-to-real gap analysis，量化并解释仿真与真实捕获的系统性偏差方向。

#### C4. 多处 caveat 的重复降低了论文可读性（严重度：MINOR，属写作建议）

论文的学术诚实性值得赞赏，但同一 caveat 在全文中反复出现（例如"results apply to this UVC link and should not be extrapolated"至少出现 4-5 次；"not a clinical or user-study threshold"出现 3 次以上），导致行文冗长且重要信息被淹没。

**改进建议**：(1) 在 Limitations section 集中声明所有 caveats；(2) 正文中首次提及时引用 Limitations section 即可，不必每次重复完整表述；(3) 考虑将部分细粒度 caveat 移至 footnotes。

#### C5. Table II 中 "leak rate" 指标的定义与实际意义不匹配（严重度：MINOR）

Section V-A 定义 leak rate 为"proportion of samples with character recovery ≥ 20%"，但 20% 的阈值选择未给出依据。更重要的是，leak rate 作为二值化指标丢失了恢复率的连续分布信息——在 deployed short-exposure 中 20.5% 的样本 leak rate 意味着约 94 张图像恢复率 ≥ 20%，但这些图像的实际恢复率分布（是集中在 20-30% 还是有一些达到 80%+？）对安全评估更有意义。

**改进建议**：(1) 解释 20% 阈值的选择依据；(2) 补充恢复率的分布统计（如 P50/P90/P99）或直方图。

---

## 三、对第一轮审稿的补充意见

### 关于 C1（长曝光恢复率反升）的补充

第一轮 review 正确识别了这一问题并给出了可能原因。补充一个额外视角：Table I 的 inversion ablation 显示 $\alpha=0.3$ 的长曝光恢复率（72.0%）反而**高于** $\alpha=0.0$（68.6%），虽然 CI 重叠。这意味着弱 inversion 不仅无法防御 integration attack，在某些条件下甚至可能**帮助** OCR——可能因为 inversion frame 引入了额外的边缘结构（255-I 的边缘与 I 的边缘位置相同但极性相反），在固定曝光参数下反而提供了额外的可识别信号。这与 C1 中"stripe/glyph overlay 提供 residual edge structure"的假设一致，建议一并诊断。

### 关于 M5（缺少 Kaleido 对比）的补充

第一轮建议实现 Kaleido baseline。补充一个更轻量的替代方案：至少在论文中增加一个理论对比表，列出 Kaleido 和本文方法在以下维度的差异：(a) 目标威胁模型（continuous recording vs short exposure）；(b) 对 full-cycle integration 的预期表现（Kaleido 设计上可被完整恢复，本文 capture-hardened 设计为抵抗恢复）；(c) 对 short-exposure 单帧的预期表现（Kaleido 的 chrominance-complementary 帧在单帧下可能仍然可读，因为色彩信息被保留）。即使没有实验数据，一个清晰的理论对比也能帮助读者理解两种方法的适用范围差异。

### 关于 C3（VLM 逻辑链断裂）的补充

第一轮建议对 font-size-adaptive mask 做初步验证。补充一个更根本的反思：论文的核心安全前提本质上是"破坏 binarization pipeline"——传统 OCR 依赖清晰的二值化图像，而 VLM 通过 end-to-end visual encoding + language prior 绕过了这一步骤。这意味着方法的安全基础不在于物理采样原理本身，而在于攻击者 pipeline 的特定弱点。论文应在 Introduction 或 Threat Model 中更直接地承认这一点，并将方法的定位从"利用人眼-相机积分差异"修正为"利用传统 OCR pipeline 对 degraded binary image 的脆弱性"。

---

## 四、修订优先级补充建议

在第一轮修订路线图基础上，建议将以下补充问题纳入：

| 优先级 | 补充问题 | 建议行动 | 工作量 |
|:------:|----------|----------|:------:|
| 第一优先级 | A1 像素响应时间 | 报告面板类型和 GtG 响应时间；在 Limitations 讨论 temporal ghosting | 低 |
| 第一优先级 | A2 Rolling shutter | 估算 S600 rolling shutter 读出时间；讨论对 short-exposure 结论的偏倚方向 | 低 |
| 第二优先级 | B1 信息论分析 | 推导单子帧理论最大信息泄漏；与实际恢复率对比 | 中 |
| 第二优先级 | C3 Simulation-to-real gap | 增加一段系统性对比仿真与真实捕获的差异方向 | 低-中 |
| 第三优先级 | A4 显示器型号 | 在 Experimental Setup 中补充 | 低 |
| 第三优先级 | B2 $n$ 选择论证 | 理论分析或补充 $n=2$/$n=6$ 的 real-capture ablation | 低-中 |
| 第三优先级 | C4 重复 caveat | 集中至 Limitations，正文精简 | 低 |

---

## 五、总结

本补充审稿在第一轮已识别的 4 项 CRITICAL、10 项 MAJOR、6 项 MINOR 问题基础上，新增了 2 项 MAJOR（A1 像素响应时间、A2 rolling shutter）、1 项 MAJOR（B1 信息论分析缺失）、1 项 MINOR-MAJOR 边界（B2 子帧数量选择、C3 simulation-to-real gap），以及多项 MINOR 级别问题。

**最核心的新增关切**是 A1 和 A2：像素响应时间和 rolling shutter 是 temporal pixel masking 方案的两个基础物理约束，论文完全未讨论。如果 S600 的 rolling shutter 读出时间 > 4.17ms（子帧持续时间），那么论文中所有"短曝光 = 单子帧"的假设都需要修正——这可能使短曝光恢复率从 15.1%/5.0% 进一步上升，也可能使方法的实际保护效果低于论文报告的值。

与第一轮审稿的结论一致：论文的学术诚实性是突出优点，修订应在保持诚实的基础上填补物理机制和理论分析的空白。
