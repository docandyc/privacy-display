# System Design 章节修改方案

> 更新日期：2026-07-18
> 依据：当前 `privacy-display/WIKI.md`、逐条源码核查结果及既有审核意见
> 适用对象：`paper/main.tex` §IV System Design、§V Experimental Evaluation（仅涉及 profile 定义、参数和选择依据的分工）及方法流程图
> 性质：修改建议清单，含可直接粘贴的 LaTeX 替换文本；不自动改动 main.tex

## 0. 范围说明：不纳入本方案的条目

| 审稿条目 | 不纳入原因 |
|---|---|
| 2.1 Strong 档参数差异 | 论文的 0.10/0.12 与真实采集 `deployed` 条件的显式 CLI 覆盖一致，但不同于通用 `strong` 默认值 0.18/0.22。该问题不再排除，改由 M10 明确区分“系统 profile 定义”与“实验实例参数”。 |
| 3.1 中 "Integration ≈50 ms" | 已在早前修图轮次由 `remove_fixed_integration_time.py` 删除，最终 `final/figure2_method_pipeline.vsdx`/PDF 已无此文字，无需处理 |
| 6 中 ByteTrack 提醒 | 论文已写 "in-project greedy association implementation inspired by ByteTrack"（main.tex:680），表题为 "ByteTrack-Style Greedy Association"，归档结果确认实际使用 `greedy_bytetrack_fallback`，表述合规 |

审稿意见遗漏、但属同一问题域并已并入本方案的两点：
- WebStudy 的噪声是确定性图像域启发式纹理（`mask.js` `computeNoiseBase`：有限差分笔画能量 + 坐标哈希 + PRNG 抖动，`epsilonPixels=8`），不是 FGSM/PGD 模型梯度噪声 → 并入 M6、M12。
- `SubframeComposer` 类默认增益为 `n × 1.1`（`subframe_composer.py:40`），评估链路是显式覆盖为 `gamma=1.0` → 并入 M2 可选句、M4。
- 威胁模型一节（main.tex:177）还有第二处 "cross-cycle correlation" 措辞 → 并入 M8。

## 1. 修改总览

| 编号 | 优先级 | 位置 | 动作 |
|---|---|---|---|
| M1 | P0 | 流程图 vsdx | 改 3 组图内文字 + 刷新率标注 |
| M2 | P0 | main.tex:291–293 | 重写 Implementation Scope：三条实现路径、软件栈、key 与元数据边界 |
| M3 | P0 | main.tex:199 段末 | 增补 CSPRNG 适用范围句（Python 链路 vs Web 实现） |
| M4 | P0 | main.tex:219–221 | 重写亮度小节：按路径区分 γ 模型 |
| M5 | P0 | main.tex:267 | 反色帧表述限定到评估路径，并弱化 "counter" 措辞（合并审稿 2.5 与 3.5） |
| M6 | P0 | main.tex:215 | 噪声生成如实描述（FGSM+sign-PGD 轮换、梯度来源层级）+ Madry 引用 |
| M7 | P1 | main.tex:199 | 卡方自由度一般化 |
| M8 | P1 | main.tex:199、177 | "cross-cycle correlation" 改为可验证表述（两处） |
| M9 | — | — | 已并入 M5 |
| M10 | P0 | §IV profile 小节、§V Experimental Setup | 明确 profile 定义归 System Design，具体实验参数、显式覆盖和选择依据归 Experimental Evaluation；收紧 high-suppression 定位 |
| M11 | 已落实 | §IV、§V、Discussion | inversion ablation 已在 §V；Kaleido 对比已在 Discussion；TCSF/CFF 已压缩，后续仅防止重构时回退 |
| M12 | P1 | main.tex §V.C（约 608 行） | 用户研究小节补一句 Web 路径披露（可选但推荐） |
| M13 | P2 | §IV 整体 | 审稿 §4 的完整结构重排（可选，见 §4） |

建议执行顺序：M10（先建立两章职责边界）→ M2/M4（小节重写）→ M3/M5/M6（句级替换）→ M7/M8/M12（措辞微调）→ M1（图，独立于正文）；M11 仅在最终检查时复核。

---

## 2. P0 修改项

### M1 流程图文字（对应审稿 3.1、2.2）

文件：`paper/figures/visio/figure2_method_pipeline/final/figure2_method_pipeline.vsdx`，改后重导出 PDF。

| 现图内文字 | 改为 |
|---|---|
| `1  Secure mask generation` | `1  CSPRNG-based mask assignment` |
| `2  GPU synthesis and temporal sequence` | `2  Subframe composition and sequencing` |
| `GPU subframe synthesis`（分行为 "GPU subframe" + "synthesis"） | `Offline subframe composition` |
| `240-360 Hz` | `nominal 240 Hz` |
| `Unreadable fragment`（保留 `OCR ×` 图形亦可） | `Partially observed subframe`；若空间允许，`OCR ×` 旁注 `empirical outcome` |

理由：ChaCha20 只保证掩码流的密码学属性，不能标注整个系统 "secure"；评估链路是离线 CPU 合成 + blit/vsync 回放（`playback_demo.py:6,786–789`），非逐 slot GPU 合成；实验只有 240 Hz 数据；短曝光不保证 OCR 必然失败，论文核心正是测量残余恢复率。

操作路径：参照 `remove_fixed_integration_time.py` 的 zip 内 XML 文本替换方式批量改 `final/*.vsdx`，再用同目录 `export_final_pdf.py` 重导出；或 Visio 手工修改。完成后：
1. 用文本提取复核（`python3 -c "import zipfile,re; ..."`，确认旧字符串归零）；
2. 若页面尺寸变化，同步更新 `main.tex:203` 的 `viewport 0 0 515.52 206.16`；
3. 图注（main.tex:204）无需改动，现文已是恰当的期望性表述。

### M2 Implementation Scope 重写（对应审稿 2.2、4.6）

位置：main.tex:291–293。现文：

```latex
\subsection{Implementation Scope}

The current PoC operates at the application layer, using Python and GPU rendering to generate display sequences, an architecture that provides direct control over subframe composition, playback order, and profile parameters during evaluation.
```

替换为：

```latex
\subsection{Implementation Scope and Reproducibility}

The PoC operates at the application layer in Python (NumPy, PyCryptodome, pygame/SDL, mss, ModernGL; PDF input via pypdfium2 or pdftoppm) and separates three rendering paths. The physical-capture protocol pre-generates all subframes offline with a CPU compositor and presents the sequence through pygame, requesting VSync and applying a software frame-rate cap when VSync is unavailable; no per-slot synthesis occurs during display. A separate live-demonstration window captures the screen with mss and renders through an optional ModernGL backend that reads each frame back to the CPU and falls back to a NumPy renderer when GPU initialization fails; one capture--mask--compose cycle takes on the order of 190\,ms, so this window cannot sustain the 120--240\,Hz slot budget and serves demonstration only. Its inversion variant shows a full inversion frame for a target fraction $\alpha$ of the slot interval, a duration-based approximation that VSync does not guarantee. The user study runs a third, independent JavaScript/Canvas2D implementation (\S\ref{sec:user_study}). Mask keys default to 32 bytes from the operating-system CSPRNG, and a fixed key can be supplied for regeneration; the playback metadata records permutations, the per-cycle noise schedule, and profile parameters, but not the key, so reproduction relies on the archived stimuli and explicit configurations rather than on command-level replay. No operating-system, display-driver, or backlight-level integration is implemented.
```

可选披露句（涉及审稿 2.1 与 composer 默认增益，作者已确认实验值，采用与否自行决定；若担心 artifact 审查可保留）：

```latex
The software defaults (compositor gain $1.1n$; overlay amplitudes 0.18/0.22) differ from the evaluated settings, which were passed explicitly at run time ($\gamma=1$, $\alpha_s=0.10$, $\alpha_g=0.12$); Table~\ref{tab:profile_composition} reports the evaluated values.
```

事实依据：三路径与耗时来自 `playback_demo.py:4–7` 模块说明（实时窗口约 190 ms/周期、无法 120/240Hz）；FBO 读回与软件回退来自 `src/gpu/renderer.py:133,225–230`；meta 字段清单来自 `playback_demo.py:656–677`（无 key）；固定 key API 见 `build_playback_frames` 的 `key` 参数；反色时长近似见 `privacy_window.py:102–110` 与 `playback_demo.py:570–571` 注释。

### M3 CSPRNG 适用范围（对应审稿 2.3）

位置：main.tex:199，在 "…cannot prevent linear reconstruction of a registered full cycle." 之后、"Fig.~\ref{fig:pipeline}…" 之前插入：

```latex
This ChaCha20-based generator drives the Python physical-capture pipeline. The user-study web implementation reproduces the same mask structure, rejection sampling, and playback shuffling with a deterministic seeded 32-bit generator so that stimuli are exactly repeatable in the browser; it has no CSPRNG properties (\S\ref{sec:user_study}).
```

事实依据：`webstudy/static/mask.js:6–25`（FNV-1a 种子 + Mulberry32 型 32-bit 生成器）、`mask.js:27–45`（拒绝采样 `uniformInt` 与 Fisher–Yates `shuffle` 均有 JS 镜像实现）。

### M4 亮度小节重写（对应审稿 2.4）

位置：main.tex:219–221。现文：

```latex
\subsection{Luminance Compensation}

Because each pixel is illuminated only once per $n$-slot cycle, a factor-$n$ light-output increase during the active slot would be needed to restore the original cycle-averaged luminance in the linear-light model; the current proof of concept (PoC) uses fixed panel output. CIEDE2000 $\Delta E_{00}$~\cite{b_ciede2000} and SSIM~\cite{b_wang2004} quantify digitally integrated and normalized reconstructions across configurations.
```

替换为：

```latex
\subsection{Luminance Model Across Rendering Paths}

Because each pixel is illuminated only once per $n$-slot cycle, restoring the original cycle-averaged luminance in a linear-light model would require a factor-$n$ light-output increase during the active slot. No evaluated path implements per-slot backlight control. The physical-capture playback fixes the compositor gain at $\gamma=1$ under fixed panel settings, leaving the linear-model cycle average at $\mathbf{I}/n$. The user-study web implementation instead applies a pixel-space gain of $1.1n$ with clipping to $[0,255]$, which partially compensates the $1/n$ duty cycle but clips bright content; its stimuli are therefore not photometrically identical to the physical-capture condition. Digitally integrated reconstructions are normalized before comparison, and CIEDE2000 $\Delta E_{00}$~\cite{b_ciede2000} and SSIM~\cite{b_wang2004} quantify these digital reconstructions only. None of these settings establishes radiometric equivalence on a real panel.
```

注意首次缩写：现文的 "(PoC)" 首次展开在此小节。重写后该展开丢失，需把 §IV 中第一次出现的 `PoC` 写为 `proof of concept (PoC)`（M2 重写文本中的首个 "The PoC" 若位于 M4 之后则无需动；若 M4 在前，则在 M4 内展开。以最终编译顺序为准，全文只保留一次展开）。

事实依据：`playback_demo.py:577`（`SubframeComposer(n=n, gamma=1.0)` 显式）；`mask.js:376,439`（`gamma = n × 1.1`，写入 Uint8ClampedArray 自动截断）；线性模型均值 `I/n` 与现文 main.tex:197 一致。

### M5 反色帧路径限定 + 动机措辞（对应审稿 2.5、3.5）

位置：main.tex:267。现文（前两句）：

```latex
To counter this threat in the normalized domain $\mathbf{I}\in[0,1]$, the implementation inserts a \textbf{partial inversion frame} $\alpha(\mathbf{1}-\mathbf{I})$ after each $n$-subframe cycle. The equivalent 8-bit expression is $\alpha(255-\mathbf{I}_{8})$.
```

替换为：

```latex
To perturb, rather than eliminate, full-cycle accumulation, the evaluated offline-playback and web pipelines append a \textbf{partial inversion frame} $\alpha(\mathbf{1}-\mathbf{I})$ (normalized domain $\mathbf{I}\in[0,1]$; 8-bit form $\alpha(255-\mathbf{I}_{8})$) after each $n$-subframe cycle, implemented as amplitude scaling over one additional display slot because vsync playback holds slot duration fixed.
```

实时窗口的时长缩放变体已在 M2 的 Implementation Scope 文本中说明，此处不再用 "the implementation" 统称全部路径。

事实依据：离线振幅缩放及原因见 `playback_demo.py:570–571` 注释与 `subframe_composer.py` `compose_partial_inversion_frame`；实时全反色 + 时长系数见 `subframe_composer.py:106–108`、`privacy_window.py:28,102–110`；α=0.2 对长曝光恢复降低有限（68.6%→67.0%，Table `tab:inversion_ablation`），故 "counter" 措辞需弱化。

### M6 对抗噪声如实描述（对应审稿 3.4 + 遗漏项）

位置：main.tex:215。现文（中间句）：

```latex
Motivated by prior work showing that small text-image perturbations can significantly mislead OCR systems~\cite{b_song2018}, noise directions are generated by fast gradient sign method (FGSM)-style~\cite{b_goodfellow2015} proxy gradients with an amplitude bound of $\varepsilon=8/255$ and then decomposed complementarily in the temporal domain.
```

替换为：

```latex
Motivated by prior work showing that small text-image perturbations can significantly mislead OCR systems~\cite{b_song2018}, noise is generated per cycle by single-step fast gradient sign method (FGSM)~\cite{b_goodfellow2015} or iterative sign-PGD~\cite{b_madry2018} updates under an $\varepsilon=8/255$ bound, rotating across eight OCR and detector targets; depending on availability, gradients come from the EasyOCR recognition network, a differentiable shadow objective, or a deterministic image-space surrogate. The resulting noise is then decomposed complementarily in the temporal domain. The user-study web implementation substitutes a deterministic image-space texture of comparable amplitude for these model-gradient perturbations (\S\ref{sec:user_study}).
```

事实依据：`noise_injector.py:31–38`（8 个目标：tesseract 用 FGSM，easyocr/surya 及 5 个检测器用 PGD）；梯度来源层级 `_target_gradient`（easyocr 端到端梯度 → 可微 shadow → 图像域代理/模板）；评估链路调用 `generate_rotating_noise` 逐周期轮换并写入 `noise_schedule`（`playback_demo.py:606–617`）；ε 默认 `8/255`（`noise_injector.py:46`）；web 噪声为启发式纹理、`epsilonPixels=8`（`mask.js:110–140`）。`b_madry2018` 已在 refs.bib:237，无需新增条目。

注意：不要在正文声称"归档元数据记录了每周期 gradient_source"，除非先核实实体采集会话确实保存了 `noise_schedule`（采集档案 `metadata.json` 目前只含 id/图片/真值）。

---

## 3. P1 修改项

### M7 卡方自由度一般化（对应审稿 3.2）

位置：main.tex:199。

```latex
% 现：($\alpha=0.01$, $\mathrm{df}=n{-}1=3$)
% 改：
($\alpha=0.01$, $\mathrm{df}=n{-}1$; 3 at the evaluated $n=4$)
```

其余（"used only as an implementation sanity check with at most 5 resampling attempts, is not evidence of cryptographic strength"）保留，与代码一致（`mask_generator.py:86,105`：p=0.01、max_retries=5）。

### M8 cross-cycle correlation 措辞（对应审稿 3.3，含遗漏的第二处）

处 1，main.tex:199：

```latex
% 现：While randomization reduces fixed patterns and cross-cycle correlation, it cannot prevent linear reconstruction of a registered full cycle.
% 改：
Per-cycle randomization avoids a fixed, periodically repeated pixel-to-slot pattern across cycles, but it cannot prevent linear reconstruction of a registered full cycle.
```

处 2，main.tex:177（威胁模型，审稿未提及）：

```latex
% 现：...provides per-cycle mask randomization to prevent fixed-pattern learning and cross-cycle correlation; it does not provide...
% 改：
...provides per-cycle mask randomization so that no fixed pixel-to-slot pattern repeats across cycles; it does not provide...
```

理由：仓库中唯一的互信息度量是单子帧对原图的 NMI（`metrics.py:197–200`），不存在跨周期相关性测量，不应声称已实证降低某个未报告指标。

### M10 profile 定义与实验配置的章节分工（P0）

**原则：定义归 §IV，参数与选择归 §V。** Profile 是系统中可组合组件的命名和角色约定，因此读者必须在 System Design 中先理解 `Mask only`、`Mask + noise`、`Strong`、`Readability-priority` 与 `High-suppression` 的组成及设计意图；但某一组 alpha、`n`、刷新率、曝光设置和显式 CLI 覆盖是具体实验实例，不应被包装为通用系统默认值。

#### M10a：§IV System Design 保留 profile 定义，但删除实验性细节

1. 将小节标题改为：

```latex
\subsection{Evaluated Profile Definitions}
\label{sec:hardened}
```

2. 保留简短的组件关系说明：

```latex
The implementation exposes composable profiles that combine the base temporal mask with optional complementary noise, stripe/glyph artifacts, and a partial inversion frame. ``Mask only'' and ``Mask + noise'' isolate the base components; ``Strong'' denotes the readability-oriented artifact profile; ``Readability-priority'' denotes the composite configuration assessed for usability; and ``High-suppression'' denotes an exploratory stress configuration for characterizing recovery boundaries.
```

3. 以一张**定义表**替换当前带有具体数值的 Table~\ref{tab:profile_composition}。表中只列 `Mask`、`Noise`、`Stripe/glyph artifacts`、`Partial inversion` 和 `Role`；不列 cell size、alpha、刷新率、曝光或 capture 标签。表注应明确：

```latex
\caption{Component-level definitions of the evaluated operating profiles. Exact parameterizations and the profile instances used in each experiment are reported in \S\ref{sec:setup}.}
```

4. 保留但收紧 high-suppression 的设计意图：

```latex
The high-suppression profile is designed to trade visible artifacts for reduced recovery under stronger acquisition conditions; \S\ref{sec:real_capture} reports the measured outcome.
```

5. 将当前 §IV 中 UVC 曝光标签、`\alpha` 消融结果、以及任何“which setting performed better”的结果性句子移出。§IV 只说明反色帧的数学形式、它在不同渲染路径中的实现差异及其不能保证阻止完整周期重构的边界。

#### M10b：§V Experimental Evaluation 负责精确参数、覆盖和选择范围

在 `\subsection{Experimental Setup}` 中，在硬件与采集协议之后新增一个紧凑小节或加粗段落：

```latex
\textbf{Evaluated configurations}: Table~\ref{tab:evaluated_configurations} reports the exact profile instances used for physical capture and for the browser study. These settings are experimental configurations rather than universal implementation defaults. In particular, the readability-priority capture condition invokes the \texttt{strong} profile with explicit stripe and glyph overrides of 0.10 and 0.12, respectively, plus a partial inversion frame with $\alpha=0.20$; the reusable \texttt{strong} CLI default uses different overlay amplitudes. The high-suppression condition uses the canonical \texttt{capture\_hardened} profile.
```

新增 `tab:evaluated_configurations`，将原表中的数值迁入，并至少区分以下两类实例：

| 实例 | 应报告的字段 | 归属 |
|---|---|---|
| 物理真实采集 | profile/legacy archive label、`n`、noise、cell size、stripe/glyph alpha、inversion alpha、nominal display refresh、capture exposure label | §V Experimental Setup |
| WebStudy 完整部署条件 | JavaScript/Canvas2D、deterministic PRNG、`n`、cycles、pixel-space gain、surrogate texture noise、stripe/glyph alpha、inversion alpha、refresh eligibility rule | §V User Experience Study setup |

表注应说明 `Strong` 的通用 Python 默认值为 stripe/glyph `0.18/0.22`，而真实采集和 WebStudy 的 readability-oriented instance 明确覆盖为 `0.10/0.12`。这样可同时保持源码和论文实验事实一致。

#### M10c：术语与结论边界

- 一律使用 `Readability-priority` 指称论文中用于真实采集主比较和用户研究的评估实例；
- 使用 `Strong (anti-OCR)` 仅指无反色帧的组件 profile；
- 使用 `High-suppression` 指称论文中的探索性 stress profile，必要时在首次出现处标明归档名 `capture_hardened`；
- 不把实验实例的参数称为 “default” 或 “optimal”；不把 high-suppression 写成新的核心算法或通用安全保证；
- 具体配置的 OCR、VLM、长曝光和用户研究结果只在 §V 报告，§IV 不提前给出数值或比较性结论。

**源码依据：** 通用 `strong` 默认值为 stripe/glyph `0.18/0.22`（`src/demo/playback_demo.py`）；真实采集 `deployed` 条件使用 `--stripe-alpha 0.10 --glyph-alpha 0.12 --inversion-alpha 0.20`（`tests/test_real_capture_ablation.py`）；WebStudy 对同一 readable instance 使用 `0.10/0.12`、`n=4`、六个变换周期和 `\alpha=0.2`（`webstudy/static/app.js`、`webstudy/static/mask.js`）。

### M11 结构移动（对应审稿第 5 节）

**当前状态（2026-07-18）：已落实，后续不应重复移动。** 当前稿已将 inversion-strength ablation 置于 §V、将 Kaleido 对比置于 Discussion、并采用压缩后的 TCSF/CFF 段落。下列内容保留为来源与回归核验记录；重写 §IV/§V 时须维持这一分工。

(a) **inversion ablation 段+表移入 §V**。将 main.tex:269 整段与 Table（main.tex:271–287，含 `\label{tab:inversion_ablation}`）原样移动到 §V，在 `\subsection{Real-Capture VLM Probes}`（main.tex:508）之前新建：

```latex
\subsection{Inversion-Strength Ablation}
\label{sec:inversion_ablation}
% <此处粘贴原 269 段、原 271–287 表，内容不改>
```

原 §IV Partial Inversion Frame 小节中，用一句前向引用替代被移走的段落：

```latex
A real-capture ablation across $\alpha\in\{0, 0.2, 0.3, 0.5, 1.0\}$ (\S\ref{sec:inversion_ablation}) informs this choice; the readability-priority setting of $\alpha=0.2$ is a modeled design decision, not a validated optimum.
```

`tab:inversion_ablation` 全文仅在原 269 行被引用一次，移动后交叉引用自洽；main.tex:289（n+1 slots 与 48 Hz 讨论）留在 §IV。

(b) **Kaleido 对比句移入 Discussion**。从 main.tex:261 移出第 2–3 句，第 1 句（completeness 偏离与可见条纹）与第 4 句（完备性是积分攻击入口）留在 §IV。在 Discussion §Profile Trade-offs（main.tex:912 段后）插入：

```latex
This trade-off runs opposite to Kaleido-class temporal re-encoding: Kaleido relies on perceptually complete mixing within a cycle to preserve viewing experience, so full-cycle integration reconstructs an approximation of the original, whereas the composite profiles here give up completeness because, for static content, completeness is the entry point for integration attacks.
```

执行时补上 Related Work 中已有的 Kaleido 引用键（`grep -n -i kaleido paper/main.tex paper/refs.bib` 确认键名后加 `~\cite{...}`；Kaleido 引文此前已核实为必引，不可删）。

(c) **TCSF/CFF 压缩**。main.tex:227 整段替换为：

```latex
Whether an observer integrates complementary subframes into a perceptually complete image depends on the temporal contrast sensitivity function (TCSF) rather than on a single critical flicker fusion (CFF) cutoff; with high-frequency spatial edges, flicker can remain visible above 500\,Hz~\cite{b_davis2015}. The 48\,Hz full-cycle rate of the inversion configuration may therefore produce visible flicker for some observers, the 60\,Hz basic configuration cannot be assumed flicker-free, and the user study in \S\ref{sec:user_study} evaluates readability and immediate comfort under these configurations.
```

保留全部实质声明（TCSF 依赖、CFF 非普适、500 Hz 具体数字、48/60 Hz 推论、用户研究指引），仅去除铺陈。

### M12 用户研究小节的 Web 路径披露（推荐）

位置：§V.C，"Here ``cycles'' means that the web implementation rotates through six distinct mask, noise, and stripe instances before repeating." 之后加一句：

```latex
The web player is the independent JavaScript/Canvas2D path described in \S\ref{sec:method}: deterministic seeded masking, pixel-space gain, and surrogate texture noise, rather than the ChaCha20- and gradient-based Python pipeline.
```

与 M3/M4/M6 的 §IV 陈述互为呼应，避免读者把用户研究刺激当作 Python 密码学/对抗实现的输出。

---

## 4. P2（可选）：§IV 完整结构重排

审稿 §4 建议的目标结构及现有内容映射。仅在愿意承担较大改动时执行；上面 M1–M12 已解决全部正确性问题，临近投稿可不做此项。

| 目标小节 | 来自现有内容 |
|---|---|
| A. System Overview and Implementation Paths | 新总览段（输入/输出/核心流程/三路径）+ Fig.~\ref{fig:pipeline} |
| B. CSPRNG-Based Temporal Mask Construction | 现 §IV.A + M3；itemize 的 completeness/exclusivity 改紧凑正文 |
| C. Optional Perturbation Components | 现 §IV.B（噪声）+ stripe/glyph 说明 + M5 反色帧机制句，按"动机、机制、边界"组织，不报结果 |
| D. Playback, Timing, and Luminance Model | 现 §IV.D + M4 + main.tex:289 |
| E. Evaluated Profile Definitions | §IV 只保留组件构成、命名和设计角色；精确参数表按 M10 移至 §V |
| F. Implementation Scope and Reproducibility | M2 |

---

## 5. 执行与验证清单

1. 按 §1 的顺序应用 M10 → M2/M4 → M3/M5/M6 → M7/M8/M12；每步 `git diff` 自查。
2. M1 改图：文本替换 vsdx → `export_final_pdf.py` 重导出 → 文本提取复核旧字符串归零 → 核对 `main.tex:203` viewport。
3. 交叉引用检查：`grep -n "inversion_ablation\|sec:hardened\|sec:user_study\|sec:real_capture" paper/main.tex`，确认无悬空引用。
4. 复核 `tab:inversion_ablation` 位于 §V、Kaleido 对比位于 Discussion，且两者引用键未因重构失效。
5. `latexmk -xelatex main.tex` 全量重编译：无新增 error；overfull hbox 数量不高于当前基线（class logo 的 505pt 警告除外）；PLACEHOLDER 数量不变。
6. 摘要未触及（本方案不改 Abstract），无需复核字数。
7. 对所有被改动的英文段落跑一遍成稿语言门（academic-humanizer rewrite），保持术语一致：readability-priority / high-suppression / Strong (anti-OCR) profile / partial inversion frame / temporal pixel masking。
8. 若采用 M2 可选披露句或想在正文声称记录了 gradient_source，先核实实体采集归档是否保存 `noise_schedule`；未保存则不写。
9. 复核 M10 的章节边界：§IV 不再包含 profile 的具体 alpha、曝光、刷新率或“最佳”选择；§V 的 `tab:evaluated_configurations` 则完整报告这些实验实例及 `strong` 默认值与显式覆盖的差异。
