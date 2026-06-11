# 技术交底书实现情况 Review

> 对照《发明专利技术交底书：一种基于视觉暂留与时间分片掩模的显示器隐私保护方法及系统》
> 逐章核查 `privacy-display/` PoC 代码的实现情况。
>
> - Review 日期：2026-06-12
> - 代码基线：git `2e52e93` + 本轮 review 修复（HDR 积分回归、实时窗口亮度模型、文档口径更新）
> - 测试状态：`pytest tests/ -q` → **127 passed**
> - 运行环境：Python 3.10（uv 维护 `.venv`），tesseract 5.4.1、easyocr 1.7.2、paddleocr 3.6.0、ultralytics 8.4.65、torch 2.11、moderngl 5.12、pygame 2.6 均可用

---

## 一、总体结论

1. **算法层完成度很高。** 交底书第三章四大技术要素（随机点阵掩模、时域互补对抗噪声、高刷新率时序、相机针对性防御）均有对应实现与单元测试；改进文档 A1–C4 共 11 项改进全部落地并回填实测数据。
2. **原 13 处 PoC 可补缺口（G1–G13，见第四节）已全部补齐**，并以单测、实验 JSON 或文档证据回填。
3. **驱动层注入等系统级内容（交底书第四章 4.2）明确超出 PoC 范围**，`README.md` 与 `规划.md` 已声明为未来工作，不视为实现缺口（见第五节）。
4. **两处交底书声称值与实验事实存在张力**（多帧叠加防御、检测模型 mAP），应在论文/答辩中按 PoC 实测口径表述（见第六节）。
5. **第二轮复核对 G3/G5 的证据做了诚实加固**（原版只测 SSIM，易高估保护）：补测 OCR 后得出三条新结论——视角差异化掩模对全周期对齐攻击者无 OCR 级保护、对抗噪声 pedestal 是单帧 inpaint 防御的关键、目标检测防御弱于 OCR 防御（详见第八节）。
6. **本轮修复已补上 HDR 视觉积分回归与窗口亮度模型一致性**：HDR 子帧按峰值亮度归一化输出预览，积分时按 `peak_nits/content_peak_nits` 恢复内容亮度；实时窗口默认改为与 demo/benchmark 一致的 `backlight` 模型，`pixel` 模式仅用于演示 SDR 像素补偿。

---

## 二、已实现对照表（交底书 → 代码 → 证据）

| 交底书章节 | 技术要素 | 实现位置 | 验证证据 |
|---|---|---|---|
| 3.2.1 | ChaCha20 CSPRNG 随机索引矩阵 | `src/core/mask_generator.py` | 单测；完备性/互斥性断言 |
| 3.2.1 步骤A | HKDF 派生周期子密钥 K_t | `mask_generator._derive_subkey`（HMAC-SHA256） | 周期统计独立单测 |
| 3.2.1 步骤B | 无偏索引生成 | 拒绝采样消除取模偏置（改进项 C1） | n∈{3,5,6,7} 卡方 p 值均匀 |
| 3.2.1 步骤D | 卡方均匀性验证 p>0.01 | `mask_generator._chi_square_check` | 单测 |
| 3.2.2 | Fisher-Yates 无偏置换 | `mask_generator.generate_permutation`（uint32 拒绝采样） | 单测 |
| 3.2.2 | 时序令牌（周期号/置换/VBlank 计数，原子更新） | `timing_controller.TimingToken` + 锁 | 单测 |
| 3.2.2 | FGSM/PGD 有界扰动 ‖N‖∞≤ε | `noise_injector.generate_fgsm_noise / generate_pgd_noise` | 单测验证 L∞ 约束 |
| 3.2.2 | 时域互补分解 ΣN_k=0 | `noise_injector.split_complementary` | 残差 0.0（精确） |
| 3.2.2 | 动态模型轮换（5 目标模型） | `noise_injector.select_target_model` | 单测 |
| 3.2.2 / 7.3 | 在线对抗更新闭环 | `update_online_strategy` + `monitor_online_recognition` | 单测 + window 演示接入 |
| 3.2.3 | 刷新率/子帧时序数学关系 | `timing_controller.get_subframe_timing` | FPI 模型与交底书数值逐项吻合 |
| 3.2.3 | VBlank 时序调度（软件模拟） | `timing_controller`（线程 + vsync 绑定接口） | 抖动统计 |
| 3.2.4 | 全局快门单帧捕获 | `attack/camera_simulator.capture_global_shutter*` | 攻击实验 OCR 0% |
| 3.2.4 / 7.1 | 卷帘快门曝光窗加权混合 + 污染行计算 | `capture_rolling_shutter` + `count_contaminated_rows` | 攻击实验 OCR 0% |
| 3.2.4 | 长曝光攻击 + 反色帧防御 | `long_exposure_attack` + `compose_inversion_frame` | 插反色帧后 OCR 0% |
| 3.2.4 | 黑帧插入 + 相机 AE 误判攻击模型（改进项 A2） | `compose_black_frame` + `auto_exposure_attack` | 单测：增益随黑帧占比上升 |
| 5.4 步骤17 | 渲染延迟应急黑帧 | `timing_controller.should_emit_black_frame` | 单测 |
| 4.1 | 四模块架构（掩模/噪声/渲染/时序） | `src/core/` + `src/gpu/` 应用层版 | — |
| 4.1.3 | 像素着色器掩模+噪声+补偿合成 | `gpu/renderer.py` + `shaders/mask_apply.*`（GPU 与软件渲染像素级一致） | 单测 + GL 失败自动回退 |
| 4.3 | HDR：PQ(ST.2084) 编解码、RGB↔ICtCp、超色域软裁剪、L_k·n 补偿与 HDR 感知积分 | `src/core/hdr_compensation.py` + `src/core/subframe_composer.py` | PQ 往返误差、保色相单测、HDR 积分还原回归 |
| 4.3（部分） | SDR 像素补偿 γ=n·β 与背光提升模型 B=n | `subframe_composer`（PoC 默认背光模型，γ 路径保留） | README §7 工程说明 |
| 4.4 | 多显示器主从同步 + 异构刷新率 LCM 虚拟时钟（改进项 A3） | `src/core/multi_display.py` | 同步误差 max 0.05ms<0.1ms |
| 5.1 步骤1 | 显示能力检测 + n 自动降级 + 实时窗口亮度模型配置 | `demo/privacy_window.py`（macOS/xrandr/Windows 刷新率查询；`brightness_model=backlight/pixel`） | 单测 |
| 6.3 | FPI（含随机点阵 1/√N 调制衰减模型） | `evaluation/metrics.py:compute_fpi` | 240Hz/n4→0.030 等与交底书吻合 |
| 6.3 | CIEDE2000 ΔE | `metrics.compute_delta_e` | 实测 0.006 < 1.0 |
| 6.3 | 亮度均匀性（九区域 ΔL/L） | `metrics.compute_brightness_uniformity` | <5% |
| 6.3 / 改进 C3 | SSIM + pursuit-camera 运动模糊宽度 | `metrics.compute_ssim / compute_motion_blur_width` | SSIM 0.99+，增幅<5% |
| 6.4 / 改进 A4 | 性能实测（掩模/噪声/合成/渲染/端到端） | `experiments/performance_benchmark.py` | 实测表 + 与交底书声称差距如实标注 |
| 7.2 | 视角差异化掩模（区域独立子密钥）+ 离轴攻击 + 强攻击者校正 | `mask_generator.generate_view_differentiated` + `camera_simulator.off_axis_temporal_average_attack / off_axis_correction` + `experiments/view_attack.py` | 正视/离轴/校正 OCR 全为 100%（见第三、八节诚实结论：掩模差异化对全周期对齐攻击者无 OCR 级保护） |
| 7.3 | 无训练重构 + tiny U-Net 学习攻击（改进项 B2/G5） | `src/attack/reconstruction_attack.py` + `experiments/unet_reconstruction.py` | max 堆叠攻破；单帧 inpaint：干净子帧 OCR 100% / 带噪声 pedestal 子帧 OCR 0%（pedestal 是单帧防御关键，见第八节） |
| 7.3 | HKDF 密钥派生多样性 | `mask_generator._derive_subkey` | 同 3.2.1 |
| 改进 B1 | 噪声消融四组对照 + 弱掩模泄露压力测试 | `experiments/ablation_noise.py` | 掩模主防御、噪声二级强化结论 |
| 改进 C2 | 12 样本语料 × 多 OCR 引擎统计 | `experiments/build_corpus.py` + `benchmark.run_corpus_multi_engine` | Tesseract 单子帧 0.4%±0.7%；EasyOCR/PaddleOCR 单子帧 0.0%±0.0% |
| — | PaddleOCR 引擎接入（3.x predict API + 输出解析） | `attack/ocr_evaluator.py` | `tests/test_ocr_evaluator.py` 通过；`OCREvaluator().engines` 包含 `paddleocr` |

---

## 三、攻防实验结论（影响交底书表述口径的事实）

| 攻击方式 | 结果 | 与交底书的关系 |
|---|---|---|
| 抽帧分析（全局快门单帧） | OCR **0%** | 吻合 3.3"高安全性" |
| 流式识别（逐帧低分辨率） | 每帧 **0%** | 吻合 |
| 卷帘快门混合 | **0%** | 吻合 7.1 |
| 长曝光（插反色帧） | **0%** | 吻合 3.2.4 |
| 时域平均 <1 周期 | **0%** | 吻合 |
| **时域平均 ≥1 完整周期** | **100% 还原** | **与 3.1"抗多帧叠加约束"冲突** |
| **逐像素 max 堆叠（覆盖完整周期）** | **SSIM 0.991 / OCR 100%** | 同上，且对抗噪声被 max 选择性忽略 |

> 数学根因：人眼"视觉无感"依赖 ΣI_k=I 的线性积分，相机叠加用的是同一求和——凡能被人眼积分还原的就能被相机积分还原。互斥完备掩模在覆盖完整周期的任意逐像素聚合（mean/median/max）下均可反演。这是原理性张力而非实现缺陷，论文应以"防御被动抽帧/流式威胁模型 + 主动完整周期采集是已知局限与缓解方向（视角差异化/非线性调制/周期随机化）"的口径表述。

---

## 四、可补缺口清单（G1–G13 已补齐）

| # | 缺口 | 交底书出处 | 现状 | 优先级 |
|---|------|-----------|------|--------|
| G1 | PaddleOCR 端到端语料评测 | 3.2.2 / 改进 C2 | 已补齐：PaddleOCR 3.6.0 可探测并参与 12 样本语料评测；`corpus_multi_engine.json` 已含 tesseract/easyocr/paddleocr 三行 | Done |
| G2 | YOLOv8 通用目标检测评测 | 3.3 / 6.2 声称"YOLOv8 文本检测 mAP 0.92→0.08" | 已补齐为 PoC 通用目标检测实验：`ultralytics==8.4.65` + YOLOv8n，`detection_attack_yolo.json` 记录单子帧 mAP50=0.40、完整周期平均 mAP50=1.00；不等同于文本检测 mAP | Done |
| G3 | 离轴相机攻击实验 | 7.2 / 改进 B3 验证方法 | 已补齐并加测 OCR + 强攻击者校正：`view_attack.json` 显示正视/离轴/校正 OCR 全为 100%、离轴 SSIM 仅降 0.064 → 诚实结论是掩模差异化对全周期对齐攻击者无 OCR 级保护（详见第八节） | Done |
| G4 | 空间-时间联合扰动 | 7.2 | 已补齐：`split_complementary_spatial` 约束逐像素 ΣN_k=0 与邻域棋盘抵消 | Done |
| G5 | 学习型去混淆攻击 | 7.3 / 改进 B2 可选项 | 已补齐并加测 OCR + pedestal 消融：tiny U-Net 单帧 OCR 0%（下界）；单帧 inpaint 干净子帧 OCR 100% / 带噪声 pedestal 子帧 OCR 0% → pedestal 是单帧防御对 inpainting 鲁棒的关键（详见第八节） | Done |
| G6 | 真实可微 OCR 端到端梯度攻击 | 3.2.2 噪声生成模型 | 已补齐：EasyOCR recognizer 可微路径，失败自动回退 shadow/surrogate 并记录来源 | Done |
| G7 | 视觉疲劳优化三件套 | 7.4 | 已补齐：自适应刷新率、蓝光抑制、观看距离补偿纯函数策略 | Done |
| G8 | 显示接口带宽约束计算 | 3.2.3 | 已补齐：带宽公式及 DP1.4/DP2.0/HDMI2.1 容量判断 | Done |
| G9 | 时序令牌缺置换序列哈希 | 3.2.2 | 已补齐：`TimingToken.permutation_hash` 随置换原子更新 | Done |
| G10 | HLG 编码 | 4.3 | 已补齐：HLG OETF/逆 OETF，往返误差单测 | Done |
| G11 | ALS 环境光反馈闭环 | 4.3 | 已补齐：`AmbientAdaptation` 模拟 lux→背光/γ 反馈以保持 Weber 对比度 | Done |
| G12 | 1024 周期掩模/置换预生成缓冲 | 4.1.1 / 5.1 步骤3 | 已补齐：`MaskGenerator.pregenerate` 环形缓冲，预生成==按需生成单测 | Done |
| G13 | 配置持久化 | 5.1 步骤2 | 已补齐：`PrivacyDisplayConfig` JSON 读写并接入 `main.py window <config.json>` | Done |

---

## 五、明确超出 PoC 范围（不视为缺口，论文中声明为未来工作）

以下条目需要内核驱动、代码签名或专用硬件，`README.md`（实现范围说明）与 `规划.md`（可行性评估表）已提前声明排除：

- **4.2 驱动层/合成器层注入**：Windows Desktop Duplication / 图形过滤驱动、Linux KMS-DRM atomic commit 钩子、macOS CoreDisplay + DriverKit System Extension
- **SPIR-V 跨平台着色器 + 平台抽象层（PAL）**：PoC 使用 moderngl/GLSL
- **GPU Compute Shader 掩模生成（<0.1ms）与 R8_UINT 纹理、双缓冲/环形缓冲 GPU 显存管理**：PoC 为 CPU 生成（实测 15–27ms，已在性能报告中如实对比）
- **硬件 VBlank 中断、SCHED_FIFO / MMCSS 实时线程、±0.5ms 硬同步**：PoC 为软件模拟时序
- **真实 HDR framebuffer / PQ-HLG 输出 / 系统色彩管理接入**：PoC 已有 HDR 数学补偿与积分回归，但普通 SDR 窗口无法输出真实 HDR 帧
- **6.1/6.2 实施例的真实 240Hz/480Hz 硬件验证**：PoC 在 60–120Hz 普通屏上以 n=2 演示 + 数值模型外推
- **6.1 受试者主观实验（10 人暗室 30 分钟）**：未开展；FPI/ΔE/SSIM 客观指标替代

---

## 六、交底书声称值 vs PoC 实测（论文表述建议）

| 交底书声称 | PoC 实测 | 建议口径 |
|---|---|---|
| Tesseract 字符准确率 98%→12% | 100%→**0%**（单子帧，12 样本多引擎复核） | 实测更优，直接引用实测 |
| 单帧信息熵为原图 12–18% | 归一化互信息 0.15–0.35 | 量纲不同，按互信息口径表述 |
| YOLOv8 文本检测 mAP 0.92→0.08 | YOLOv8n 目标检测：单子帧 mAP50=**0.40**；完整周期平均 mAP50=**1.00** | 改用本实验实测值；不再引用无支撑的 0.08 |
| GPU 负载 3–5%、帧生成 +0.3ms | Python/CPU 路径慢 1–2 个数量级（性能报告已如实标注） | 声明该指标针对驱动层实现假设，PoC 验证算法正确性而非生产性能 |
| 抗多帧叠加约束（3.1） | 覆盖完整周期的逐像素聚合可完全还原 | 按第三节口径限定威胁模型 + 列缓解方向 |
| FPI 0.02–0.03 / ΔE<1.0 | FPI 0.030 / ΔE 0.006 | 吻合，直接引用 |
| HDR 视觉无感 | 本轮新增 HDR 感知积分回归；白场 headroom 允许时 Delta E≈0.20 | 可表述为“数学补偿链路成立”；真实 HDR 输出仍列未来工作 |

---

## 七、工作流状态备注（review 时点）

- G1–G13 均已完成，剩余仅为 PoC 范围外硬件/驱动未来工作
- `.trellis` 中 `complete-noise-camera-simulation`、`fix-main-demo-renderer` 两任务代码已实现并已提交（127c437 / dfc38fd / 5147b7b），仅任务状态未归档
- G1–G13 的补齐计划见 `~/.claude/plans/users-andyhuang-desktop-md-review-replicated-nova.md`（已批准执行）

---

## 八、第二轮复核：G2/G3/G5 的诚实加固（OCR 为准）

第一轮 G3/G5 实验仅以 PSNR/SSIM 度量，易高估保护。第二轮补测真实隐私指标
（OCR 字符准确率）并加入"强攻击者"对照，得到三条更诚实、更有答辩价值的结论。

### 8.1 G3：视角差异化掩模对全周期对齐攻击者无 OCR 级保护

`experiments/view_attack.py`（n=4，35°，3×3 区域，`view_attack.json`）：

| 重构路径 | SSIM | OCR |
|---|---|---|
| 正视完整周期平均 | 1.000 | 100% |
| 离轴朴素捕获 | 0.936 | **100%** |
| 离轴 + 强攻击者校正（反向位移 + 逐区域增益归一化） | 0.926 | 100% |

- 整周期平均时**每个区域无论用何种差异化掩模都各自还原**（各自满足 ΣM_k=1），
  掩模差异化不参与防御；离轴朴素捕获 OCR 已经是 100%。
- 离轴 SSIM 仅降 0.064，且完全来自区域级衰减/色偏/位移这类**可逆物理畸变**。
- 论文口径：交底书 7.2 把视角差异化列为抗多帧叠加的缓解方向，但在纯软件可逆模型下
  不成立；真正的保护需依赖**不可逆**的物理 LCD 视角响应（属 PoC 范围外）。

### 8.2 G5：对抗噪声 pedestal 是单帧 inpaint 防御的关键

`experiments/unet_reconstruction.py`（`unet_reconstruction.json`）：

| 单帧重构方法 | OCR |
|---|---|
| tiny U-Net（学习攻击下界） | 0% |
| inpaint @ 干净子帧（未激活=0） | **100%** |
| inpaint @ 带噪声 pedestal 子帧（未激活≈ε） | **0%** |

- 这解释并修正了 B2 表"单帧 inpaint SSIM=0.026/OCR 0%"与新实验"SSIM 0.93"的表观
  矛盾：B2 子帧带 pedestal 使 `gray<1` 缺失检测失效→inpaint 空操作；干净子帧才会被填洞。
- **SSIM 不是隐私指标**：干净子帧单帧 inpaint 可把高对比文档 OCR 还原到 100%，加上
  对抗噪声 pedestal 后同一攻击 OCR 跌回 0%。
- 论文口径：把对抗噪声从"边际贡献存疑"提升为"单帧防御对 inpainting 攻击鲁棒的关键
  支撑"，与 B1"掩模主防御 + 噪声二级强化"一致，并给出了噪声不可或缺的具体攻击场景。

### 8.3 G2：通用目标检测防御弱于 OCR 防御

单子帧 YOLOv8n 目标检测 mAP50=**0.40**（召回 0.40）明显高于单子帧 OCR 的 **0.0%**。
目标检测依赖粗粒度形状/颜色团块，对 1/n 稀疏点阵采样比细笔画文本更鲁棒。论文应区分
"文本/细结构信息"（保护强）与"物体级场景信息"（保护弱）两类威胁，不笼统宣称等效防御。
