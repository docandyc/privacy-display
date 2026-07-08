# 根据 Claude 第二轮审稿意见修订 IEEE Access 中英文稿

## Goal

在不新增或虚构实验数据的前提下，逐条落实 Claude 提出的 26 项结构、术语、可复现性、逻辑、相关工作、局限性和排版问题，并同步修订英文稿 `paper/main.tex` 与中文稿 `paper-Chinese/main.tex`，使两稿的数值、边界声明和表格信息一致。

## What I already know

- 审稿意见针对当前 IEEE Access 英文稿，且多项修改会影响摘要、贡献、方法、结果、讨论和结论之间的一致性。
- 当前工作树已有未提交的论文、用户研究脚本和图表改动；本任务只能增量修改目标稿件，不能回滚或覆盖这些既有工作。
- Rainbow 与 Lim 已在上一轮证据审计中独立核验，当前 BibTeX 已补 DOI 并修正 Lim 作者；本轮只需复核两稿同步状态。
- 没有新增商业 OCR API、补充真机对比图或用户研究结果，因此相关建议应通过明确局限、收窄因果措辞和保留投稿前 TODO 来处理，不能伪造证据。

## Requirements

- 重写摘要与贡献：拆开跨 profile 的区间，移出贡献中的负面 noise 结果，降低摘要密度，并把第三项贡献拆成可读的边界证据结构。
- 将方法节中的实拍结果移到结果/讨论，并统一 `video temporal averaging` 术语及表格标签。
- 为 profile 参数表补充 stripe width；统一核心表格字号；为主结果表的字符恢复率补充 95% CI。
- 在实验设置中解释 0.49/3.91/31.25/125 ms 的仪器来源和实验用途，但不把它们误写成典型手机曝光。
- 将长曝光反转的 residual-edge 机制改为明确的假设性措辞；限定 VLM 结论只在已测 on-axis、单 profile、三距离范围内成立。
- 补充 best-of-engine 未覆盖商业 OCR API 的选择偏差、短曝光与视频攻击的操作成本、capture-hardened 命名说明、敏感字段部署风险和软件代理基线的公平比较边界。
- 扩展相关工作比较表，至少覆盖本文已讨论且能够可靠归类的 HideScreen、LiShield、Kaleido/Rainbow/Lim 与本文，避免只挑 Kaleido 的选择性比较。
- 将 synthetic/proxy trade-off 图移动到软件模拟附近，拆分 §5.1 过长段落，并适度减少会影响断行的破折号。
- 使结论中的 future work 具体指向字号自适应粒度、字形诱饵或字段级策略。
- 全文审计 `\TODO{}`：保留确实需要作者填写的占位，但将宏改为非红色、投稿安全的占位形式，并在任务说明中列出未解决项。
- 同步中英文稿的所有实质性修改；参考文献元数据保持一致。
- 第三轮追加：首次展开 CSPRNG、UVC、FPI、PoC、ISP、FGSM；将 paper-facing `capture-hardened` 重命名为 `high-suppression` / “高抑制档”，归档标识保持不变。
- 第三轮追加：删除“机构没有伦理委员会所以未审批”的表述；在不虚构既有审批的前提下，把书面批准、豁免或免审认定设为招募前置条件。
- 第三轮追加：修正 Rainbow/Lim 的 IEEEtran DOI 字段，核验 Wang/YOLO26，删除不受 Davis 文献支持的固定 CFF 阈值。
- 第三轮追加：解释 deployed 重复采集未覆盖长曝光，为 `tab:real_mot`、`tab:ocr_corpus`、`tab:mot_sim` 补 `\footnotesize`，拆分用户任务设计长段落，并去除引言与相关工作的防窥膜重复。
- 第四轮追加：降低摘要和引言的过度对冲密度，先完整陈述单 UVC 相机、9 组几何下传统 OCR 短曝光恢复率显著下降的核心结论，再集中说明边界。
- 第四轮追加：在环境照度局限中说明可能偏差方向、相反的自动补偿路径、不可估计的净量级，以及对跨几何结论和核心链路内对比的不同影响。
- 第四轮追加：展开 CER、mAP、AR、HOTA、IDF1、MOTA、MOTP、SSIM、DRM、QD、CPM/WPM，消除 FPI 公式中的样本量符号冲突，并修复用户研究段不可断等宽标识符。
- 第四轮追加：核验 7 条预印本并替换 3 条正式版本，修正 `b_zhao2023` 和 `b_li2025` 的错误作者；复核 Wang/YOLO26、Kimi K2.6、数据公开地址和 deployed P95。
- 第五轮追加：重新以权威来源核验 `b_yolo26`、`b_wang2026`、`b_fernandez2024`、`b_song2018`、`b_shi2023`、`b_li2025`，存在正式版本时优先替换，并记录无法确认正式发表版本的预印本状态。
- 第五轮追加：修正摘要、引言、贡献和结论中 77.8\% 的模型归属与统计范围；明确该值是 Qwen3-VL 在 0.5 m、高抑制、短曝光条件下汇总 12 类内容得到的 exact match，而内容类型集中趋势来自另一张字符恢复率表。
- 第五轮追加：强化论文的可辩护适用价值，将单次、短曝光、传统 OCR 的防护收益定位为提高无人值守或静默批量采集成本，同时明确普通短视频与 VLM 可绕过该边界。
- 第五轮追加：解释部署配置保留互补噪声的设计取舍，但不得把非单调消融写成普遍收益；合并重复 caveat，减少摘要、引言和 finding 收尾处的过度对冲。
- 第五轮追加：调整评测章节顺序，使 VLM、检测/跟踪与仿真攻击链连续，用户研究协议移到攻击实验之后；对两个 60.9\% 和两个 5.6\% 的不同统计量显式消歧。
- 第五轮追加：审计参考文献 DOI 完整性和错配 cite-key；在不破坏既有引用的前提下统一元数据。核验 S600 传感器规格，无法由厂商或可靠资料支持的具体型号、尺寸和读出时长不得作为事实保留。
- 第六轮追加：修复英文 IEEE Access 稿件的最后缩写与措辞问题：首次展开 FPI，提前或就地展开 SSIM，避免 S600 在全名定义前裸用，调整 Ray-Ban Meta 例示与 Wang 2026 引文的附着关系，并检查 Wang 2026 的 Crossref 页码元数据。
- 第六轮追加：轻量减少欠曝光 d0.5/$15^{\circ}$ caveat 的中段重复，但不得删除摘要、主结果或结论中用于限定边界的必要敏感性说明。

## Acceptance Criteria

- [x] 两稿摘要、贡献与结论不再用未标注 profile 的 `47.9--71.1%` / `53.9--79.7%` 区间。
- [x] 方法节不再陈述 `mask+noise 25.6%` 与 `mask-only 19.2%` 的结果比较。
- [x] 两稿术语、参数表 stripe width、主结果 CI 和表格字号一致。
- [x] 曝光值有可审计来源说明，且没有外推为手机默认曝光。
- [x] VLM、商业 OCR、长曝光机制、基线公平性和敏感字段风险均有明确边界声明。
- [x] 相关工作表覆盖多个代表性方案，Rainbow/Lim 引用信息经现有证据审计复核。
- [x] 两稿 LaTeX 构建成功，无新增未定义引用/文献或非模板 overfull。
- [x] 关键表格与移动后的图经 PDF 目检无裁切、越栏或语义错位。
- [x] `git diff --check` 通过，且没有修改无关源码或实验结果。
- [x] CSPRNG、UVC、FPI、PoC、ISP、FGSM 在两稿首次出现处均已展开，标题不再裸用 UVC。
- [x] `capture-hardened` 已从正文、表格、图注和图内标签改为 `high-suppression` / “高抑制档”；仅归档映射保留 `capture_hardened` 与 `vlm`。
- [x] 伦理表述不再以“机构没有委员会”替代审批；两稿明确无被试数据，并将书面批准/豁免/免审认定设为招募前置条件。
- [x] Rainbow/Lim DOI 采用 IEEEtran 可输出的 `note` 字段；Wang 与 YOLO26 已复核；CFF 不再使用不受引文支持的固定 50--70 Hz 断言。
- [x] deployed 样本数不对称、三张表字号、CFF 句段、任务设计长段落和防窥膜重复均已处理。
- [x] 摘要和引言先陈述核心正面结果，再集中披露目标未达、视频/VLM 与可读性边界。
- [x] 环境照度局限给出可能偏差方向、反向补偿机制和无法定量的原因。
- [x] 本轮点名缩写均在首次或指标定义处展开，FPI 空间池化像素数改为 $N_p$，长等宽标识符可断行。
- [x] Ghiasi、Zhong、Gu 等正式版本已替换；Li 作者已修正；Wang、YOLO26、Kimi K2.6 与 P95 均有源证据。
- [x] 数据声明已指向公开、版本固定的 Git 提交，不再含存档 URL 占位符。
- [x] 六条点名引用均有本轮权威来源核验记录；不存在的引用已删除或替换，已正式发表的预印本已升级。
- [x] 77.8\% 在摘要、引言、贡献、结果解释和结论中的模型、条件、样本池与指标归属完全一致。
- [x] 引言与结论清楚区分“降低静默单帧批量 OCR 的可扩展性”和“无法抵御约 67 ms 视频/VLM”的贡献边界。
- [x] 部署档噪声保留理由与消融结果相容，不声称其在真机短曝光下单调有效。
- [x] 用户研究协议位置不再打断攻击评测链；60.9\% 与 5.6\% 的数值巧合已就地消歧。
- [x] DOI、作者、年份和 cite-key 审计完成；S600 规格只保留可追溯事实。
- [x] 两稿完整构建、日志检查、PDF 文本检查和关键页面目检通过。
- [x] 英文稿首次出现的 FPI、SSIM 和 S600 均有清楚展开或定义。
- [x] Ray-Ban Meta 作为智能眼镜例子出现，Wang 2026 引文附着到 camera/smart glasses 类别而非单一产品断言。
- [x] Wang 2026 页码经 Crossref/ACM 元数据复核；若权威元数据仍为 1--28，则不做无依据 article-number 改写。
- [x] 欠曝光 caveat 至少减少一处中段重复，且核心边界信息仍可追踪。

## Verification Record

- 2026-07-07：英文 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 成功，23 页。
- 2026-07-07：中文 `latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex` 成功，18 页。
- 两份日志均无未定义引用、未稳定标签或新增非模板 overfull；PDF 文本无 `[?]`、`(?)`、`??` 占位。
- PDF 目检页：英文 4/6/9/17，中文 3/5/7/12；扩展相关工作表、profile 参数表、带 CI 主表和移动后的权衡图均无裁切或越栏。
- Rainbow 与 Lim 的 DOI/作者信息沿用上一轮独立证据审计；中英文 `refs.bib` 字节一致。
- `\TODO{}` 仍有英文 6 处、中文 10 处，均改为非红色显式占位并在每次构建发出 `manuscript` 警告；作者信息、单位、基金、邮箱、用户研究结果、存档地址与致谢必须在投稿前补齐。
- 未更新 `.trellis/spec/`：本轮新增信息是论文特定的审稿映射、曝光元数据和表格数值，已由本任务 PRD 与上一轮证据审计承载；现有 LaTeX 构建指南已覆盖完整构建、引用和 PDF 核验要求。
- 2026-07-07 第三轮追加：英文与中文再次以 `latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex` 完整构建成功，页数仍为 23/18；日志无未定义引用或未稳定标签。
- 受改名影响的 `real_capture_montage.pdf`、`real_capture_bar.pdf`、`readability_robustness_tradeoff.pdf`、`real_engine_ocr.pdf` 已重生成并同步到中文稿；PDF 文本只显示 `High-suppression`，不再显示旧 paper-facing 名称。
- PDF 目检页：英文 5/10/13/15，中文 3/7/10/12；配置章节、图内标签、伦理/任务段落和小字号表格均未发现裁切、越栏或语义错位。
- 引用核验记录见 `research/review-round3-citation-audit.md`；中英文 `refs.bib` 字节一致，生成的参考文献正确输出 Rainbow、Lim、Wang、YOLO26 与 Davis 的 DOI/元数据。
- 源文件范围 `git diff --check` 通过。全树检查仍会命中 LaTeX 生成日志中的行尾空格；这些是编译产物而非稿件源文件问题。
- 2026-07-07 第四轮：摘要和引言已改为先完整陈述核心短曝光 OCR 结果，再集中说明边界；环境照度局限已补偏差方向与不可估计的净量级。
- 本轮点名缩写已展开，FPI 空间池化符号改为 $N_p$；用户研究段与 VLM 模型标识使用显式断行点，原 38.07 pt 与新增 45.46 pt 溢出均消失。
- Ghiasi、Zhong 和 Gu 等正式版本已替换，Li 作者已修正；完整核验见 `research/review-round4-audit.md`。两份 `refs.bib` 字节一致。
- 数据声明已指向远端 HEAD 提交 `13977c25d21f2b520112bab6274dcac1f67adacf`；该提交包含 `real_capture_ocr.json`、`real_capture_vlm.json` 和 `reproducibility_manifest.json`。
- deployed 短曝光拍摄级 P95 从源 JSON 重算为 60.9365%，长曝光拍摄级均值为 60.8603%；两者四舍五入同为 60.9% 是不同统计量的真实巧合。
- 英文与中文再次以 `latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex` 完整构建成功（23/18 页）。两份日志均无未定义引用、未稳定标签或非模板/标题 overfull；PDF 目检摘要、VLM、用户研究、数据声明与参考文献页未见越栏或页眉侵入。
- 2026-07-07 第五轮：`b_yolo26` 经 arXiv API 与 Ultralytics 官方文档双重确认；`b_wang2026` 经 Crossref/ACM 确认，原文明确提及 Ray-Ban Meta。Deep-TEMPEST 已由 arXiv 升级为 LADC 2024 正式版；Song、Shi、Jiang 三条仍为可确认的 CoRR 预印本。完整记录见 `research/review-round5-citation-hardware-audit.md`。
- `b_li2025` 与 `b_zhao2023` 分别改为 `b_jiang2025` 与 `b_gu2024`；补齐 Backes、Raguram、Eiband、Kaleido、LiShield、Nguyen 和 DeepLight DOI，并修正 DeepLight 页码。两份 `refs.bib` 字节一致，生成参考文献已目检。
- 摘要、引言、贡献和结论将 77.8\% 统一为 Qwen3-VL 在 0.5 m、高抑制、短曝光、完整 12 项内容池上的 pooled exact match；大字号短片段结论仅由独立的按内容类型字符恢复率分析支撑。
- S600 的 “Sony 1/2.55-inch” 与未实测 10--16 ms 读出时间已删除；正文改引厂商可确认的 8 MP/4K、1080p/60 fps 规格，并将滚动快门行混合降为未隔离的可能机制。
- 攻击实验呈现顺序现为 VLM → 真机检测/跟踪 → 软件模拟 → 用户体验协议。PDF 文本确认英文 C/D/E/F 与中文 C/D/E/F 顺序正确。
- 两稿再次完整构建成功（英文 23 页，中文 18 页）；最终 `main.log`/`main.blg` 无未定义引用或 BibTeX 缺失条目，PDF 文本无 `[?]`/`??`，`git diff --check` 通过。目检英文第 1、15、18、22 页和中文第 13、17 页，未见裁切或越栏。
- 本轮逐项完成证据见 `research/review-round5-completion-audit.md`。通用经验已补入 `.trellis/spec/guides/latex-paper-build-thinking-guide.md`：引用需经主来源核验，预印本应检查正式版本，硬件型号/时序不得把未测推断写成事实，改 cite-key 后须检查最终 `.aux/.blg`。
- 2026-07-07 第六轮：英文 `paper/main.tex` 将 Ray-Ban Meta 改为智能眼镜类别后的例示、将首次 `S600 experiments` 改为 `eMeet SmartCam S600 experiments`、在保护目标处展开 `Flicker Perception Index (FPI)`，并在相关工作表首次展开 `structural similarity (SSIM)`；中文稿同步对应措辞。
- Wang 2026 通过 Crossref DOI `10.1145/3772318.3791848` 复核，权威元数据页码为 `1-28`，故现有 BibTeX `pages = {1--28}` 保持不变。记录见 `research/review-round6-minor-polish-audit.md`。
- 第六轮验证：`git diff --check -- paper/main.tex paper-Chinese/main.tex .trellis/tasks/07-07-revise-ieee-access-claude-round2/prd.md .trellis/tasks/07-07-revise-ieee-access-claude-round2/research/review-round6-minor-polish-audit.md` 通过；中英文 `latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex` 均成功（英文 23 页，中文 18 页）；最终日志无未定义引用/文献或未稳定标签；PDF 文本无 `[?]`、`??`、`(?)` 占位；目检英文第 4 页和中文第 3 页相关工作表无裁切或越栏。

## Definition of Done

- 每条审稿意见均有“已修改 / 已有覆盖 / 因缺乏证据而降级措辞或列为投稿前事项”的可追踪结论。
- 中英文稿均重新编译并完成静态与视觉核验。
- 保留用户现有未提交工作，不提交或推送 Git，除非用户另行确认。

## Technical Approach

以当前未提交稿为基线做局部 LaTeX 编辑。先建立审稿意见到行号/段落的映射，再批量修改结构与措辞；对新增表列和 CI 只使用当前正文已有、可追溯的值。构建后检查日志、PDF 页面和中英文关键短语一致性。

## Decision (ADR-lite)

**Context**: 部分意见建议新增商业 OCR、局部对比图或用户研究数据，但仓库当前没有这些新证据。

**Decision**: 本轮落实所有可由现有材料支持的修改；需要新实验的项改为限制声明或谨慎假设，不制造数据。英文稿是投稿主稿，中文稿同步其证据边界。

**Consequences**: 论文结构和可辩护性会提高，但商业 OCR 覆盖、补充视觉佐证、跨设备泛化和真实可用性仍是明确的未来工作。

## Out of Scope

- 新增或重跑相机、商业 OCR API、VLM、用户研究实验。
- 生成不存在的局部对比图或统计结果。
- 代替作者填写姓名、单位、基金、通讯邮箱、致谢和最终存档标识符。
- 修改 WebStudy、实验数据或无关代码；仅允许更新受配置改名直接影响的论文图标签脚本并重生成对应图件。

## Technical Notes

- 审稿意见：`/Users/andyhuang/.codex/attachments/1f39dffa-b88c-4e0b-ba22-683d122b2566/pasted-text-1.txt`
- 英文稿：`paper/main.tex`
- 中文稿：`paper-Chinese/main.tex`
- 上一轮证据审计：`.trellis/tasks/07-06-fix-bilingual-paper-claude-review/research/review-evidence-audit.md`
- 相关 LaTeX 指南：`.trellis/spec/guides/latex-paper-build-thinking-guide.md`
