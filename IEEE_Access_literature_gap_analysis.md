# IEEE Access 投稿前文献调研与差距分析

日期：2026-06-12

对象：`privacy-display` 项目与毕业论文《基于视觉暂留与时间分片掩模的显示器隐私保护系统》。

## 1. 结论摘要

目前没有检索到与本项目完全同构的公开论文，即“纯软件、面向屏幕文本隐私、利用高刷新率时间分片随机掩模，使人眼积分可读而相机/OCR 难以识别”的完整系统。但相邻方向已经有较多基础：屏幕被摄像头拍摄的隐私管理、屏幕-相机通信、屏摄水印、亮度隐蔽信道、摄像头光学干扰、OCR 对抗样本、智能眼镜旁观者隐私研究。

因此，IEEE Access 投稿不宜宣称“首次利用视觉暂留防拍摄”，而应更精确地定位为：

> A software-only, camera-resistant display masking system for smart-glasses-era screen privacy, combining cryptographically randomized temporal subframe masking, OCR-oriented adversarial perturbation, and explicit attack-boundary analysis under snapshot, streaming, rolling-shutter, short-exposure, and reconstruction attacks.

最强卖点不是单一算法，而是“系统化威胁模型 + 可复现实验 + 对完整周期平均失守的诚实边界 + 针对 OCR/VLM 时代的屏幕隐私问题”。IEEE Access 的 `Applied Research` 或 `Research Article` 类型较适合；它要求定量验证，且官方强调代码/数据可复现性，这与当前项目已有代码、语料和实验脚本匹配。

## 2. 本项目当前方法

本项目将每帧图像拆成 `n` 个互斥、完备的随机点阵子帧，满足 `sum(I_k)=I`。掩模由 ChaCha20 CSPRNG 和周期子密钥驱动；时序侧使用 Fisher-Yates 置换、反色帧/黑帧插入；机器识别侧加入互补对抗噪声，满足 `sum(N_k)=0`。人眼在约 50 ms 时间窗口内积分得到完整画面，相机短曝光或抽帧只能看到稀疏碎片。

已有实验结果显示：`n=4, 240Hz` 下 FPI 约 0.030，CIEDE2000 色差约 0.37；Tesseract、EasyOCR、PaddleOCR 在 120 样本语料上的原始帧字符识别率分别为 94.0%±9.1%、94.1%±8.1%、94.9%±7.3%，单子帧识别率均约为 0.0%，配对降幅达到 93.9%–94.9%；单子帧词级准确率、exact-match、敏感 token 恢复率同样为 0.0%。但覆盖完整周期的时域平均、相位搜索和蓝通道 max 重构可高比例还原：120 样本强攻击逐样本择优后字符恢复率为 95.2%（95%CI 93.8%–96.5%）、exact-match 为 91.7%、敏感 token 恢复率为 98.6%，泄露率为 100%。这是线性时域方案的原理边界。

## 3. 已有相关研究

### 3.1 屏幕隐私与摄像头眼镜

[ScreenAvoider](https://arxiv.org/abs/1412.0008) 明确提出“保护电脑屏幕免受泛在摄像头拍摄”的问题，面向 Google Glass、Narrative Clip 等第一人称摄像设备。其思路不是改变屏幕显示，而是检测照片中是否出现屏幕和敏感内容，并用 ScreenTag 标记/管理披露。与本项目相比，它属于拍摄后的内容控制，不阻止相机得到可识别画面。

[Cardea](https://arxiv.org/abs/1610.00889) 是更宽泛的上下文感知视觉隐私框架，通过隐私配置、视觉指示和手势交互让摄像设备按用户偏好处理隐私。它说明“上下文”和“用户控制”在视觉隐私中重要，但不是屏幕端主动防护。

[Mind the Gap](https://arxiv.org/abs/2603.04930) 是 2026 年 CHI 论文，研究摄像头眼镜中佩戴者与旁观者的隐私冲突。其价值在于为本文引言提供最新动机：在敏感环境中，旁观者期望更强保护，而佩戴者通常不会主动承担完整保护责任。这支持“屏幕端自动防护”的必要性。

### 3.2 屏幕-相机通信与不可感知显示调制

[DeepLight](https://arxiv.org/abs/2105.05092) 和 [Revelio](https://arxiv.org/abs/2501.02349) 都研究“人眼不明显、摄像头可解码”的屏幕-相机通信。目标与本项目相反，但技术非常相关：它们证明屏幕时空调制可以在现实显示器和手机摄像头之间形成稳定通道，也暴露出相机可以恢复人眼不敏感信号的能力。DeepLight 使用 DNN 解码器和蓝色通道轻量调制；Revelio 使用 OKLAB 色彩空间、空间自适应闪烁、加权差分累加器和两阶段神经网络解码。

对本项目的启发是双向的：这些方法可作为“强相机攻击者”的参考模型，也可借鉴其感知色彩空间、同步检测和相机失真建模来改进评测。

### 3.3 屏幕亮度隐蔽信道与反向安全风险

[BRIGHTNESS](https://arxiv.org/abs/2002.01078) 证明屏幕亮度的细微变化可以作为人眼不可见、相机可恢复的光学隐蔽信道，用于从隔离计算机泄露数据。它与本项目方向相反，但提醒我们：任何“人眼不可感知”的调制都可能被摄像头统计恢复。因此论文需要把完整周期平均、加权累积、自动曝光与重构攻击作为核心威胁，而不是附录式讨论。

### 3.4 摄像头光学干扰与卷帘快门利用

[Imperceptible CMOS camera dazzle](https://arxiv.org/abs/2311.16118) 使用人眼不可感知的光源扰动攻击 CMOS 卷帘快门相机，使深度模型误判。它需要外部光源硬件，不是纯软件显示端方案；但其物理建模思路值得借鉴，尤其是卷帘快门时序、光度条件、人眼不可见条件和 DNN 识别失败之间的关联。

本项目当前已有卷帘快门模拟，但如果要投 IEEE Access，建议增加真实手机/摄像头的滚动快门实拍，或者至少把模拟参数与真实设备测得的 readout time、曝光时间、自动曝光策略对应起来。

### 3.5 屏摄水印与事后溯源

[A Screen-Shooting Resilient Document Image Watermarking Scheme using Deep Neural Network](https://arxiv.org/abs/2203.05198) 关注文档显示后被摄像头拍摄仍能提取水印。它解决的是“拍摄后溯源/认证”，不是“拍摄时不可识别”。其训练中的屏摄失真层值得借鉴：可用类似失真层构建本项目的攻击模拟器，覆盖距离、角度、亮度、相机畸变、摩尔纹和压缩。

### 3.6 OCR 对抗样本

[Fooling OCR Systems with Adversarial Text Images](https://arxiv.org/abs/1802.05385) 说明轻微文本图像修改即可让 OCR 输出语义相反的词。[A Black-Box Attack on Optical Character Recognition Systems](https://arxiv.org/abs/2208.14302) 研究二值图像 OCR 的黑盒组合攻击。[Vulnerability Analysis of Transformer-based OCR](https://arxiv.org/abs/2311.17128) 表明 TrOCR 等 Transformer OCR 也容易受攻击。

这些文献支撑本项目的“对抗噪声”设计，但也指出一个审稿风险：如果本项目只用传统 OCR 引擎评估，而没有覆盖 Transformer OCR、VLM OCR 或手机端视觉助手，结论会显得偏窄。

## 4. 与已有工作的对比

| 方向/代表工作 | 目标 | 主要做法 | 是否需要硬件 | 与本项目关系 |
|---|---|---|---|---|
| ScreenAvoider | 管理含屏幕照片的披露 | 检测屏幕与敏感内容，事后控制 | 不改屏幕 | 问题动机相同，但不是显示端主动防护 |
| Cardea | 上下文视觉隐私 | 偏好配置、视觉标识、手势 | 依赖摄像端配合 | 可用于讨论用户/场景策略 |
| PrivacEye | 头戴眼动设备隐私 | 检测敏感场景并自动关闭第一人称摄像头 | 需要摄像端/机械快门 | 证明“自动保护触发”比纯用户自觉更可靠 |
| Eye-Shield | 手机屏幕防肩窥 | 让近距离正视可读、远距离/斜视模糊像素化 | 不额外硬件 | 与本项目同属屏幕侧主动保护，评测范式值得借鉴 |
| DeepLight / Revelio | 屏幕到相机通信 | 人眼不可感知调制，摄像头解码 | 不一定额外硬件 | 目标相反，但可作为强攻击者和感知调制参考 |
| BRIGHTNESS | 屏幕亮度泄露 | 不可见亮度调制，相机恢复 | 不额外硬件 | 证明相机可恢复人眼不敏感时域信号 |
| CMOS camera dazzle | 干扰相机/DNN | 外部光源 + 卷帘快门 | 需要光源 | 可借鉴真实快门和光度建模 |
| 屏摄水印 | 拍摄后仍能提取水印 | DNN 编解码 + 屏摄失真层 | 不额外硬件 | 可借鉴屏摄信道建模，但目标相反 |
| OCR 对抗样本 | 让 OCR 误识别 | 数字扰动/黑盒攻击 | 不额外硬件 | 支撑对抗噪声，但应扩展到新 OCR/VLM |
| 本项目 | 屏幕文本对相机不可识别，人眼可读 | CSPRNG 时间分片随机掩模 + 互补噪声 + 时序策略 | 目标为纯软件 | 直接面向智能眼镜屏幕防拍；系统完整度和威胁模型是主要贡献 |

## 4A. 同方向解决方案谱系：创新点、局限与可借鉴点

这一轮更宽的检索表明，“同方向”工作并不少，只是多数不采用本项目这种“时间分片随机掩模 + 人眼积分 + 相机单帧失效”的构型。已有方案大致分为七类。

### 4A.1 摄像端/平台端管控：先识别，再阻断或限制披露

代表工作包括 ScreenAvoider、Cardea、PrivacEye 和 2026 年 CHI 的 Mind the Gap。ScreenAvoider 的创新点是把“电脑屏幕被第一人称摄像头拍到”作为明确威胁，检测照片中是否含屏幕，再用 ScreenTag 辅助识别敏感内容。Cardea 的创新点是上下文感知和交互式隐私偏好：用户用个人隐私配置、视觉标识和手势告诉摄像系统如何处理隐私。PrivacEye 进一步把隐私判断做成头戴设备的自动控制：用第一人称画面和眼动特征判断敏感场景，敏感时关闭摄像头机械快门。Mind the Gap 从用户研究角度说明，佩戴者和旁观者对摄像眼镜隐私的期待不一致，敏感场景中旁观者倾向更强自动保护。

这类方案的共同局限是需要摄像端配合，无法防御恶意眼镜、被篡改的记录指示灯或普通手机偷拍。本项目的价值正是在不信任摄像端的情况下，把防护下沉到显示端。

可借鉴点：

- 加入上下文触发策略：只对密码、代码、财务表格、IM 窗口等 ROI 开强保护，对普通背景弱保护，降低可用性损失。
- 在论文威胁模型中明确区分“合作摄像端”和“非合作摄像端”，把本项目定位为非合作场景补位。
- 借鉴 Mind the Gap 的场景分级：公共空间、半公共会议室、涉密办公/银行柜台分别使用不同强度的保护参数。

### 4A.2 屏幕侧空间退化：让授权观察者可读，让旁观者难读

Eye-Shield 是最接近“显示端主动保护”的已发表系统之一。它的创新点不是时间调制，而是空间感知退化：生成的屏幕图像在近距离正视时可读，但在更远距离或更大角度下变得模糊/像素化；Android 和 iOS 原型分别达到 24 FPS 和 43 FPS，并通过用户研究评估可用性。传统防窥膜、HP Sure View、Lenovo PrivacyGuard、Dell SafeScreen、手机厂商的窄视角像素方案也属于这一类，核心都是利用角度选择性降低旁观者看到的清晰度。

这类方案的局限是主要防“肩窥”和侧向观察，不天然防正面相机、长焦相机或站在用户后方的摄像头；如果摄像头位置接近授权用户视角，空间退化会失效。

可借鉴点：

- 增加距离/角度实验维度。当前项目已经做离轴模拟，但 IEEE Access 投稿应参考 Eye-Shield 的方式，把正视、15°、30°、45°和 0.5m/1m/2m 作为标准实验矩阵。
- 引入 ROI 自适应保护。Eye-Shield 强调“不严重阻碍交互”，本项目可以只对文本笔画、密码框、代码 token 加强时间分片和噪声。
- 补用户实验。Eye-Shield 的强项是 MTurk 和线下用户研究；本项目若只用 FPI/Delta E 会显得弱，建议补阅读速度、疲劳、主观可读性评分。

### 4A.3 视觉密码/人眼端解密：让单个观察通道只看到随机份额

Naor-Shamir 视觉密码的思想与本项目非常接近：秘密图像被分成多个随机份额，单个份额不泄露内容，叠加多个份额后人眼可直接读出。UNC 的 AR 视觉密码实验把一个随机份额显示在普通屏幕，另一个份额由 AR 眼镜叠加，秘密只在用户眼睛中出现，旁观者或设备单独看到的都是随机图案。

这类方案的创新点是安全模型清晰：单份额理论上不含秘密信息；局限是需要额外透明片或 AR 眼镜，对齐困难，解码速度慢，不适合普通办公屏幕连续显示。

本项目可以把自己解释为“时间域动态视觉份额”：每个子帧类似一个份额，人眼在时间上叠加得到明文，相机短曝光只得到单份额。这个类比有助于写清楚创新来源和安全边界，但也要指出差异：传统视觉密码要求攻击者拿不到足够份额；本项目若攻击者录到完整周期，就能拿到全部时间份额，因此必须把完整周期平均列为边界。

可借鉴点：

- 用视觉密码术语重写一部分理论：share、qualified set、forbidden set、pixel expansion/contrast、single-share leakage。
- 给出“单子帧信息泄露”指标，而不只报告 OCR 结果，例如单份额互信息、笔画连通性、敏感字段恢复率。
- 作为未来工作，可设计“合法用户持有第二份额”的增强模式，例如浏览器插件或 AR 眼镜显示补偿份额，公共屏幕只显示随机份额。这样能突破“完整周期平均”边界，但部署条件变重。

### 4A.4 屏幕-相机通信与亮度隐蔽信道：目标相反，但攻击模型最有价值

DeepLight、Revelio 和 BRIGHTNESS 都证明了一个对本项目很关键的事实：人眼不明显的屏幕调制，相机未必看不见。DeepLight 的创新点是用 DNN 解码器整体解码屏幕中空间编码的比特，不依赖精确定位每个编码像素，并通过蓝色通道轻量调制降低可见闪烁。Revelio 的创新点是利用 OKLAB 色彩空间、空间自适应闪烁、加权差分累加器和两阶段神经网络，在真实屏幕-相机链路中做视觉不可感知数据嵌入。BRIGHTNESS 则从安全角度证明，屏幕亮度微小变化可被摄像头从视频流中恢复，用于隔离机数据泄露。

这些工作不是防御方案，但它们给出了本项目必须面对的强攻击者：攻击者不只是“抽一帧做 OCR”，还可能做帧同步、差分累加、色彩空间分离、蓝通道增强、神经解码。

可借鉴点：

- 把 DeepLight/Revelio 的解码思想转化为攻击实验：weighted differential accumulator、frame boundary detection、screen extraction、temporal super-resolution、blue-channel-only recovery。
- 在防御端借鉴 OKLAB/ICtCp/蓝通道感知调制，降低人眼可见性，同时不要让某一通道成为相机恢复的稳定侧信道。
- 增加“已知算法攻击者”评测：攻击者知道 n、刷新率和可能的子帧结构，但不知道密钥，尝试从连续视频中估计周期与相位。

### 4A.5 主动光学干扰：利用相机物理缺陷，而不是隐藏内容

Imperceptible CMOS camera dazzle 的创新点是利用 CMOS 卷帘快门，用人眼不可感知的光源扰动让相机图像出现足够干扰，从而欺骗深度模型。早期 IR/LED 干扰、交通摄像头过曝类方案也是同一思路：不改变被保护对象，而是攻击相机成像过程。

这类方案的局限是需要外部光源或硬件，功耗、合法性、空间覆盖和对不同相机的适配都比较复杂。它们也可能干扰正常摄像或造成安全问题。

可借鉴点：

- 借鉴其卷帘快门和光度条件建模。你的项目已经有卷帘快门模拟，但还可以补真实设备 readout time、曝光时间、自动曝光曲线。
- 反色帧/黑帧可以按“相机 ISP/AE 干扰”来解释，而不是只按数学积分解释。
- 增加过曝/欠曝/自动曝光收敛时间实验，证明黑帧策略不是只在理想模拟里有效。

### 4A.6 屏摄水印与溯源：不阻止泄露，但训练方法很有用

屏摄水印工作的目标是图像被拍走后仍能提取水印，用于认证或追责。2022 年的 DNN 屏摄文档水印方案把 encoder、screen-shooting distortion layer、decoder 端到端训练，并显式模拟相机畸变、拍摄畸变和光照畸变。

它与本项目目标相反：水印希望“相机仍能读到隐藏信息”，本项目希望“相机读不到明文”。但屏摄失真层非常值得借鉴。

可借鉴点：

- 构建 differentiable screen-shooting layer：透视变换、散焦、摩尔纹、曝光、白平衡、噪声、JPEG/视频压缩。
- 用这个失真层训练对抗噪声或评估重构攻击，而不是只用理想 numpy 相机模拟。
- 增加“防护 + 溯源”组合：在保护失败时，屏幕仍可嵌入低可见水印用于追责。

### 4A.7 OCR 对抗样本：证明机器识别脆弱，但不能单独支撑显示防护

Fooling OCR Systems with Adversarial Text Images、OCR 黑盒攻击、Transformer OCR 脆弱性分析都说明 OCR 系统可以被细微扰动误导。它们支持本项目“对抗噪声”模块，但不能替代时间分片掩模，因为纯数字扰动常常对模型、分辨率、重拍、压缩和二值化敏感。

可借鉴点：

- 不只评估 Tesseract/EasyOCR/PaddleOCR，应加入 TrOCR、DocTR、PaddleOCR PP-OCRv4/5、手机系统 OCR、Google Lens/Apple Live Text 或可用 VLM OCR。
- 把噪声模块写成“二级强化”而不是主防御：主防御是时域随机掩模，噪声用于弱掩模泄露、面板串扰、重构/inpainting 攻击。
- 建立 ensemble attack/defense：多 OCR 代理模型轮换生成扰动，评估迁移性。

### 4A.8 更准确的创新定位

综合上述工作，本项目的创新点不应写成“从未有人做过屏幕隐私保护”，而应写成以下组合创新：

1. 面向智能眼镜和屏幕 OCR 泄露，把防护放在显示端，不依赖摄像端合作。
2. 将视觉密码的“单份额随机、叠加可读”思想移到高刷新率时间域，用 CSPRNG 动态生成随机点阵子帧。
3. 将屏幕-相机通信领域的时域/色彩/相机信道问题反向用于防御评测。
4. 将 OCR 对抗扰动作为二级强化，并明确主防御和噪声贡献的消融边界。
5. 明确给出线性时间分片方案的完整周期平均边界，而不是回避失守攻击。

这个定位更像一篇系统安全/可用安全论文，而不是单一图像处理算法论文。IEEE Access 可以接受这种跨安全、显示、人机交互和计算机视觉的系统型工作，但实验矩阵必须比本科毕设更扎实。

## 5. 投稿风险

1. 当前论文中引用的 `Kaleido: You can watch it but cannot record it` 和 `LiShield: Automating visual privacy protection using a smart LED`，我用公开检索没有找到可核验记录。IEEE 投稿前必须补 DOI/ACM/IEEE 页面；若无法确认，建议删除或替换成可追溯文献。

2. 只做 12 张自建样本不足以支撑强安全结论。IEEE Access 可以接受应用系统型工作，但需要更完整的实验矩阵和统计置信区间。

3. “视觉无感”目前主要靠指标模拟。投稿前最好补真人实验：阅读速度、主观闪烁评分、疲劳评分、30 分钟连续观看、不同亮度环境。

4. 完整周期平均失守不能弱化。更好的写法是把它上升为一个“线性时间分片防护的不可能性/边界分析”，并把本文贡献限定在真实智能眼镜的抽帧、流式逐帧、短曝光和卷帘快门威胁模型。

5. 性能上 Python PoC 不能支撑“实时系统”声称。论文应明确：当前实现验证算法有效性；生产级实时性需要 GPU compute shader / compositor / driver 层实现。若要强投系统论文，至少补一个 shader-only 离线/实时子路径的性能数据。

## 6. 可借鉴的改进方向

### 6.1 从屏幕-相机通信借鉴感知调制与强攻击模型

借鉴 Revelio 的 OKLAB/感知色彩空间和空间自适应闪烁，把当前 RGB/线性亮度补偿升级为感知一致性优化。借鉴 DeepLight/Revelio 的相机解码器，构造“攻击者知道存在调制，尝试从视频中累积恢复文本”的学习型攻击，而不是只评估单帧 OCR。

已按这一方向补强项目：`CameraSimulator` 新增相位搜索重构、加权差分累加和单通道恢复攻击，`experiments/attack_analysis.py` 会输出强相机攻击者结果并保存 `experiments/results/attack_analysis_strong_camera.json`，语料级结果保存为 `experiments/results/corpus_strong_camera_attack.json`。当前全量结果显示，完整周期平均、相位搜索与蓝通道 max 在 120 样本上均可恢复 94%–95% 字符，逐样本最强攻击字符恢复率 95.2%，而 luma/blue 差分累加仍为 0%。剩余可继续补 rolling-shutter row alignment、时域 super-resolution、TrOCR/VLM 和真实手机/智能眼镜拍摄实验。

### 6.2 强化真实设备评测

至少选 3 类相机：普通手机、带高帧率/专业模式手机、智能眼镜或头戴设备。每类记录曝光时间、帧率、分辨率、是否自动曝光、距离、角度和环境光。实验组合建议：

| 维度 | 推荐范围 |
|---|---|
| 显示刷新率 | 144Hz, 240Hz, 360Hz |
| 子帧数 | n=2, 4, 6 |
| 相机曝光 | 自动、1/120s、1/250s、1/500s、1/1000s |
| 距离 | 0.5m, 1m, 2m |
| 角度 | 0°, 15°, 30°, 45° |
| 内容 | 英文、中文、代码、表格、账号、URL、UI 截图 |
| 识别器 | Tesseract, EasyOCR, PaddleOCR, TrOCR, Google Lens/手机 OCR, VLM OCR |

### 6.3 扩展数据集和统计口径

已把语料扩展到 120 张：12 类模板各 10 个确定性变体，覆盖英文、中文、混合凭据、数字、代码、表格、段落、财务字段和 URL/token，并输出 `corpus_metadata.json` 支持按类别、语言、版式、字号分层统计。三引擎全量复测显示：Tesseract 原始帧 94.0%±9.1%、单子帧 0.0%±0.2%；EasyOCR 原始帧 94.1%±8.1%、单子帧 0.0%±0.0%；PaddleOCR 原始帧 94.9%±7.3%、单子帧 0.0%±0.0%。新增词级准确率、exact-match 与敏感 token 恢复率后，三引擎单子帧仍均为 0.0%。下一步应继续扩到 300 张以上，并加入真实办公界面、PDF 文档、代码编辑器、终端、网页表格、聊天窗口截图。

隐私指标不只用 OCR accuracy。当前已补充 WER/词级准确率、exact-match 与敏感字段恢复率；下一步还应报告 VLM 问答成功率、目标检测 mAP、重构后 SSIM/LPIPS。安全结论以“文本恢复率”作为主指标，视觉指标作为可用性约束。

### 6.4 把负面结果写成贡献

完整周期平均可还原不是失败，而是论文最有学术价值的边界结论。建议形式化为：

若显示方案满足线性完备性 `sum(I_k)=I` 且攻击者获得覆盖完整周期的所有子帧并能线性配准，则攻击者可用与人眼积分等价的运算恢复原图。因此纯线性时间分片无法同时满足“人眼完美积分”和“任意完整周期视频不可还原”。本文的安全性限定在不覆盖完整周期、无法同步、短曝光/抽帧/流式逐帧识别等更现实威胁下。

这个边界分析能显著提高论文可信度，也能避免审稿人用一个平均攻击直接否定全文。

### 6.5 增加非线性与随机化缓解

可探索三类方向，但不要过度承诺：

- 非线性时域调制：利用人眼 temporal contrast sensitivity、亮度适应、局部对比阈值，而不是严格线性 `sum(I_k)=I`。
- 周期和相位随机化：让攻击者难以知道完整周期边界，配合 dummy frames、可变 n、可变曝光陷阱。
- 内容自适应保护：对小字、密码、代码等高风险区域使用更强掩模和噪声，对低风险背景降低扰动，提升可读性。

### 6.6 按 IEEE Access 组织可复现材料

IEEE Access 官方页面说明它是多学科、在线、金色开放获取期刊，并强调 4-6 周快速同行评审；APC 当前为 2160 美元且官方建议正文 20 页以内。Submission Guidelines 要求 IEEE Access 模板、PDF 与源文件一致、认真核对引用、至少 3 个关键词，并建议附补充材料。它还有 reproducibility initiative，建议代码和数据仓库可运行、可复现实验。

投稿前建议准备：

- GitHub/Zenodo 归档代码和实验数据，给 DOI；
- `README` 写清硬件、依赖、运行时间、如何复现实验表；
- `scripts/reproduce_all.sh` 或等价脚本，一键生成主要表格和图；
- 原始截图/拍摄视频作为 supplementary material；
- AI 使用披露按 IEEE 要求写入 acknowledgements。

## 7. 建议论文结构

1. Introduction：智能眼镜与屏幕隐私威胁；现有防窥膜/水印/摄像端控制不足；本文贡献。
2. Related Work：屏幕隐私、屏幕-相机通信、光学干扰、屏摄水印、OCR 对抗样本。
3. Threat Model and Design Goals：明确防御和不防御的攻击。
4. Temporal Random Masking：掩模、CSPRNG、完备性、互斥性、时序置换。
5. OCR-Oriented Perturbation and Exposure Traps：互补噪声、反色/黑帧、AE/rolling shutter。
6. Boundary Analysis：完整周期平均不可能性/负面结果。
7. Implementation：Python PoC + GPU shader path/未来驱动层。
8. Evaluation：视觉可用性、OCR/VLM 防御、真实相机、消融、性能、重构攻击。
9. Discussion：部署限制、伦理与可用性、安全边界。
10. Conclusion。

## 8. 下一步优先级

1. 先核验或替换当前论文中不可追溯的 Kaleido/LiShield 引用。
2. 增加真实相机/手机拍摄实验，至少覆盖自动曝光、短曝光、视频流和不同角度。
3. 加入 TrOCR、手机 OCR、VLM OCR 与真实拍摄样本，避免仅覆盖桌面截图和开源 OCR。
4. 继续补强强攻击者：rolling-shutter row alignment、时域 super-resolution、VLM 读屏。
5. 把完整周期平均和相位搜索/蓝通道 max 失守写成理论边界和负面结果贡献。
6. 用 OKLAB/蓝通道/空间自适应调制做一版感知优化，与当前 RGB 随机点阵做消融对比。
7. 准备可复现仓库和补充材料，按 IEEE Access 模板重写为英文 14-18 页。

## 9. 关键来源

- IEEE Access official site: https://ieeeaccess.ieee.org/
- IEEE Access APC: https://ieeeaccess.ieee.org/about/article-processing-charges/
- IEEE Access submission guidelines: https://ieeeaccess.ieee.org/authors/submission-guidelines/
- IEEE Access reproducibility: https://ieeeaccess.ieee.org/authors/reproducibility/
- ScreenAvoider: https://arxiv.org/abs/1412.0008
- Cardea: https://arxiv.org/abs/1610.00889
- PrivacEye: https://arxiv.org/abs/1801.04457
- Eye-Shield: https://arxiv.org/abs/2308.03868
- SoK Privacy Personalised: https://arxiv.org/abs/2411.18380
- Two-week study of screen filters and camera sliders: https://arxiv.org/abs/2602.08465
- Mind the Gap: https://arxiv.org/abs/2603.04930
- DeepLight: https://arxiv.org/abs/2105.05092
- Revelio: https://arxiv.org/abs/2501.02349
- BRIGHTNESS: https://arxiv.org/abs/2002.01078
- Imperceptible CMOS camera dazzle: https://arxiv.org/abs/2311.16118
- Screen-shooting resilient document watermarking: https://arxiv.org/abs/2203.05198
- Visual cryptography background: https://en.wikipedia.org/wiki/Visual_cryptography
- AR visual cryptography report: https://www.wired.com/2015/08/augmented-reality-glasses-visually-encrypt-secrets
- Fooling OCR Systems with Adversarial Text Images: https://arxiv.org/abs/1802.05385
- A Black-Box Attack on OCR Systems: https://arxiv.org/abs/2208.14302
- Vulnerability Analysis of Transformer-based OCR: https://arxiv.org/abs/2311.17128
