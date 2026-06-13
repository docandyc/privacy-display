# 基于视觉暂留与时间分片掩模的显示器隐私保护系统（PoC）

本项目是毕业设计技术交底书《一种基于视觉暂留与时间分片掩模的显示器隐私保护方法及系统》的**概念验证原型（Proof of Concept）**实现。在普通桌面（Python + GPU）环境下验证核心算法的有效性、量化关键指标，并诚实评估方案的边界与局限。

> **实现范围**：本 PoC 实现应用/算法层，不含交底书第四章的 OS 驱动级注入（DXGI/KMS-DRM/CoreDisplay）。后者需内核模块与代码签名，属未来工作。

---

## 1. 核心原理

将每帧完整图像 `I` 在时域随机拆分为 `n` 个互补子帧 `I₁…Iₙ`，满足：

- **完备性** `ΣI_k = I`：人眼在 ~50ms 积分窗口内叠加所有子帧，感知到完整原图。
- **互斥性**：每个像素在 `n` 个时隙中恰好被点亮一次（随机点阵掩模，ChaCha20 CSPRNG 驱动）。
- **噪声互补** `ΣN_k = 0`：对抗噪声分解为时域互补分量，人眼积分后完全抵消、单帧内最大化 OCR 混淆。注：随机点阵掩模是主防御（单独已将单帧 OCR 压至 0%），噪声为二级强化，用于弱掩模泄露、面板串扰、自适应攻击等场景（见改进文档 B1 消融）。

相机在任一快门时刻只能捕获碎片化的单子帧，信息熵远低于 OCR/检测模型的识别下限。

---

## 2. 项目结构

```
privacy-display/
├── main.py                      # 入口: demo / benchmark / window / test-noise
├── scripts/
│   └── reproduce_all.sh          # 投稿材料复现编排脚本
├── experiments/
│   ├── attack_analysis.py       # 攻击鲁棒性分析（核心实验）
│   ├── publication_summary.py   # 论文/投稿表格汇总（读取已有 JSON）
│   ├── reproducibility_manifest.py # 复现实验清单（环境/命令/文件哈希）
│   ├── real_capture_analysis.py # 真实手机/相机拍摄图片 OCR 分析
│   ├── vlm_readability_analysis.py # 在线 VLM 可读性攻击评测（需环境变量密钥）
│   ├── real_captures/           # 真实拍摄 metadata 模板与待导入图片
│   └── results/                 # 实验输出（对比图/GIF/JSON/图表）
├── src/
│   ├── core/
│   │   ├── mask_generator.py    # ChaCha20 CSPRNG 随机点阵掩模 + Fisher-Yates 置换
│   │   ├── subframe_composer.py # 子帧分解、亮度补偿、视觉积分、反色帧
│   │   ├── noise_injector.py    # FGSM 对抗噪声 + 时域互补分解
│   │   └── timing_controller.py # VBlank 软件模拟时序调度
│   ├── gpu/
│   │   ├── renderer.py          # moderngl GPU 渲染 + 软件渲染回退
│   │   └── shaders/             # GLSL 掩模/噪声/亮度补偿着色器
│   ├── attack/
│   │   ├── ocr_evaluator.py     # Tesseract/EasyOCR 准确率测量（CER/WER）
│   │   ├── vlm_evaluator.py     # OpenAI-compatible 在线 VLM 读屏评测
│   │   └── camera_simulator.py  # 全局/卷帘快门、时域平均、长曝光攻击
│   ├── demo/
│   │   ├── visual_integration.py # 人眼视角 vs 相机视角对比图/动画
│   │   └── privacy_window.py    # pygame 实时屏幕保护演示
│   └── evaluation/
│       ├── metrics.py           # FPI / CIEDE2000 ΔE / 归一化互信息 / 亮度均匀性
│       ├── benchmark.py         # 参数扫描评测套件 + matplotlib 图表
│       ├── publication_summary.py # 论文表格可复现汇总器
│       ├── real_capture.py      # 真实拍摄 OCR 结果汇总器
│       ├── reproducibility_manifest.py # 环境/结果/源码哈希 manifest
│       └── vlm_benchmark.py     # VLM 语料抽样评测与统计汇总
└── tests/                       # 179 个单元测试
```

---

## 3. 环境与运行

```bash
# 已用 uv 维护 .venv，激活后：
source .venv/bin/activate

# 核心依赖（已安装）：numpy scipy pycryptodome pillow opencv-python pytest moderngl
# OCR 攻击实验额外需要：pytesseract + 系统 tesseract（brew install tesseract）
# 目标检测实验使用：ultralytics YOLOv8n（首次运行会下载 yolov8n.pt，本地权重不提交）

python -m pytest tests/ -q          # 183 项单元测试
python main.py demo                 # 生成对比图/GIF + 打印指标
python main.py benchmark            # 参数扫描评测（需 tesseract）
python experiments/attack_analysis.py       # 攻击鲁棒性分析（核心实验）
python main.py window               # 实时屏幕保护演示（默认 n=2@120Hz，需 pygame+mss）
python main.py playback             # 人眼端回放演示（240Hz 屏，预生成子帧后纯 vsync 回放）
python main.py playback --n 4 --cycles 16 --inversion --benchmark 5   # 带参示例
python main.py playback --n 4 --anti-ocr-profile strong                # 手机 OCR 压制演示（人眼可读优先）
python main.py playback --demo cet6 --pdf-page 1 --width 900 --height 1280 --n 4  # 英语六级真题 PDF 演示
python main.py playback --demo cet6 --pdf-page 1 --width 900 --height 1280 --n 4 --anti-ocr-profile vlm  # VLM/OCR 压力测试

# 改进项实验（见 改进文档.md）
python experiments/performance_benchmark.py # A4 性能实测
python experiments/build_corpus.py          # C2 生成多样本语料
python -c "from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','paddleocr'], merge_existing=True)"  # 120 样本三引擎全量复测
python experiments/ablation_noise.py        # B1 对抗噪声消融
python experiments/detection_attack.py      # G2 YOLOv8n 目标检测攻击
python experiments/view_attack.py           # G3 离轴相机攻击
python experiments/unet_reconstruction.py   # G5 学习型重构攻击
python experiments/real_capture_analysis.py --init-template # 生成真实拍摄 metadata 模板
python experiments/real_capture_analysis.py --engines tesseract # 分析已采集的真实拍摄图片
python experiments/publication_summary.py   # 汇总主要 JSON 结果到 publication_summary.{json,md}
python experiments/reproducibility_manifest.py # 记录环境、复现命令和关键文件哈希
scripts/reproduce_all.sh                    # 默认安全路径：测试 + VLM dry-run + summary + manifest
scripts/reproduce_all.sh --full-offline     # 追加重型离线实验，耗时较长
scripts/reproduce_all.sh --with-vlm-live    # 追加真实在线 VLM，需先设置环境变量

# 在线 VLM 读屏攻击评测（SiliconFlow / Qwen3-VL，密钥只从环境变量或本地 .env.local 读取）
export SILICONFLOW_API_KEY="<your_api_key>"
# 或复制 .env.example 为 .env.local，并在 .env.local 中填写；.env.local 不提交
python experiments/vlm_readability_analysis.py --dry-run --samples-per-category 1
python experiments/vlm_readability_analysis.py --samples-per-category 1
```

> **改进路线见 [`改进文档.md`](改进文档.md)**：已实现 HDR 补偿(ICtCp/PQ/HLG 与 HDR 感知积分回归)、黑帧+AE 攻击、
> 多显示器同步、性能实测、真实对抗噪声+消融、去混淆/重构攻击、视角差异化掩模、
> 掩模取模偏置修复、多样本多引擎评测、YOLOv8n 目标检测评测、离轴攻击、
> 学习型重构攻击、在线 VLM 读屏评测入口、HLG/ALS、配置持久化、SSIM/运动模糊指标等。
> 新增模块：`src/core/hdr_compensation.py`、`src/core/multi_display.py`、
> `src/core/fatigue_policy.py`、`src/core/config.py`、`src/attack/reconstruction_attack.py`、
> `src/attack/detection_evaluator.py`、`src/attack/vlm_evaluator.py`、`src/evaluation/vlm_benchmark.py`、
> `src/evaluation/publication_summary.py`、`src/evaluation/reproducibility_manifest.py`。

---

## 4. 实验结果

### 4.1 视觉无感性与算法正确性（已验证 ✓）

| 指标 | 实测值（n=4, 240Hz, ε=8/255） | 交底书目标 | 状态 |
|------|------|------|------|
| FPI 闪烁感知指数 | **0.030** | <0.1 | ✓ 吻合 |
| Delta E (CIEDE2000) | **0.37** | <1.0 | ✓ 不可感知 |
| 噪声互补残差 ΣN_k | **0.0** | =0 | ✓ 精确 |
| 子帧完备性误差 ΣI_k−I | **0.0** | =0 | ✓ 精确 |
| 单帧信息保留率（互信息） | **0.15–0.35** | 0.12–0.18 | ✓ 接近 |
| GPU vs 软件渲染一致性 | 像素级一致 | — | ✓ |

FPI 模型与交底书逐项吻合：240Hz/n4→0.030、480Hz/n8→0.035、144Hz/n2→0.014、360Hz/n6→0.033。

### 4.2 语料级 OCR 防御效果

`experiments/build_corpus.py` 默认生成 120 张可复现合成语料（12 类 × 10 变体），并写入 `data/test_images/corpus_metadata.json`，支持按类别、语言、版式、字号做分层统计。`run_corpus_multi_engine(engines=['tesseract','easyocr','paddleocr'], merge_existing=True)` 的全量结果已保存到 `experiments/results/corpus_multi_engine.json`：

| OCR 引擎 | 样本数 | 原始帧准确率 | 单子帧准确率 | 配对降幅 |
|------|------:|------:|------:|------:|
| Tesseract | 120 | **94.0% ± 9.1%** (95%CI 92.3%–95.5%) | **0.0% ± 0.2%** (95%CI 0.0%–0.1%) | **93.9%** (95%CI 92.3%–95.5%) |
| EasyOCR | 120 | **94.1% ± 8.1%** (95%CI 92.7%–95.5%) | **0.0% ± 0.0%** (95%CI 0.0%–0.0%) | **94.1%** (95%CI 92.7%–95.5%) |
| PaddleOCR | 120 | **94.9% ± 7.3%** (95%CI 93.7%–96.2%) | **0.0% ± 0.0%** (95%CI 0.0%–0.0%) | **94.9%** (95%CI 93.7%–96.2%) |

补充恢复指标（单子帧）同样为 0：三引擎的词级准确率、exact-match 和敏感 token 恢复率均为 **0.0%**；敏感 token 统计覆盖 104/120 个样本。

投稿前仍建议继续加入 TrOCR、手机系统 OCR 与真实拍摄样本，验证防护结论不局限于桌面截图与开源 OCR。

### 4.2A 在线 VLM 可读性评估入口

项目已新增 `experiments/vlm_readability_analysis.py`，可把强相机攻击帧送入 SiliconFlow 的 OpenAI-compatible Chat Completions 接口，默认模型为 `Qwen/Qwen3-VL-32B-Instruct`。VLM 只接收图像和“转写可见文字”的 JSON 指令，ground truth 不会发送给模型，只在本地用于计算字符准确率、词级准确率、exact-match 与敏感 token 恢复率，避免模型照抄答案导致评估污染。

默认 dry-run 会按类别抽样 9 张语料、每张评估 8 类攻击帧，共 72 次调用；真实在线结果保存为 `experiments/results/vlm_qwen3_siliconflow.json`。如果所有 API 调用失败，CLI 会返回非零，`publication_summary` 会把该文件标记为不可引用。本次仓库中的 VLM 文件是沙箱 DNS 失败诊断，不应作为论文 VLM 防御率；在可联网环境中重新运行 `scripts/reproduce_all.sh --with-vlm-live` 后再引用数值。

### 4.2B 投稿表格汇总

`experiments/publication_summary.py` 会读取 `corpus_multi_engine.json`、`corpus_strong_camera_attack.json`、`detection_attack_yolo.json`、`view_attack.json` 和可选的 `vlm_qwen3_siliconflow.json`，输出 `experiments/results/publication_summary.json` 与 `experiments/results/publication_summary.md`。论文或 IEEE Access 草稿更新表格前，应先重新生成该汇总文件，避免从多个结果 JSON 手工抄数造成不一致。

### 4.2C 可复现 manifest

`experiments/reproducibility_manifest.py` 会输出 `experiments/results/reproducibility_manifest.json`，记录 Python/平台/关键包版本、Git commit/branch/dirty 状态、主要复现实验命令，以及结果文件和关键源码文件的 SHA-256。在线 VLM 只记录所需环境变量名 `SILICONFLOW_API_KEY`，不记录 API key 值；该文件用于投稿补充材料或归档前的可审计复现清单。

`scripts/reproduce_all.sh` 是投稿材料的统一编排入口。默认只执行安全、无联网路径：全量单元测试、VLM dry-run 调用量检查、`publication_summary` 和 `reproducibility_manifest` 刷新；`--full-offline` 才会重跑较慢的 OCR/检测/重构实验，`--with-vlm-live` 才会调用在线模型。脚本会自动加载本地 `privacy-display/.env.local`，但该文件被 `.gitignore` 忽略；仓库只保留 [.env.example](/Users/andyhuang/Desktop/毕业设计相关文档/我的毕设/privacy-display/.env.example:1) 占位模板。

### 4.2D 真实手机/相机拍摄分析入口

`experiments/real_capture_analysis.py --init-template` 会生成 `experiments/real_captures/metadata_template.json`，用于记录手机/智能眼镜/相机的设备、拍摄模式、距离、角度、曝光、刷新率和 ground truth。把真实拍摄图片或视频抽帧放入 `experiments/real_captures/` 并将模板复制为 `metadata.json` 后，可运行 `python experiments/real_capture_analysis.py --engines tesseract` 输出 `experiments/results/real_capture_ocr.json` 与 `real_capture_ocr.md`。当前仓库只提供分析入口和模板，不虚构真实拍摄结果。

### 4.3 攻击防御效果

| 攻击方式 | OCR 准确率 | 防御 |
|------|------|------|
| 原始帧（基线） | 100% | — |
| 全局快门单帧捕获 | **0%** | ✓ 有效 |
| 卷帘快门混合采样 | **0%** | ✓ 有效 |
| 时域平均（叠加 1–3 帧，<一个周期） | **0%** | ✓ 有效 |
| **时域平均（叠加 ≥4 帧，覆盖完整周期）** | **100%** | ✗ **失守** |
| 相位搜索完整周期重构 | **100%** | ✗ 失守 |
| 加权差分累加（luma/blue） | **0%** | ✓ 当前样本有效 |
| 蓝通道 max 重构 | **100%** | ✗ 失守 |
| 长曝光积分（无反色帧） | 100% | ✗ 失守 |
| 长曝光积分（插入反色帧） | **0%** | ✓ 有效 |

为贴近 IEEE Access 投稿所需的强攻击者模型，`CameraSimulator` 还实现了屏幕-相机通信启发的攻击基线：相位搜索重构（攻击者不知道周期起点但知道周期长度）、逐帧加权差分累加（模拟从不可见闪烁中恢复信号）、蓝通道/单通道恢复（检查颜色侧信道）。`experiments/attack_analysis.py` 会输出这些攻击的 OCR 结果、相位 offset、通道和重构分数，并保存为 `experiments/results/attack_analysis_strong_camera.json`；语料级结果另存为 `experiments/results/corpus_strong_camera_attack.json`。

120 样本语料上的 Tesseract 强攻击统计如下（`n=4, ε=8/255, cycles=2, OCR timeout=4s`）：

| 攻击方式 | 字符恢复率 | exact-match | 敏感 token 恢复率 | 泄露率（字符≥20%） |
|------|------:|------:|------:|------:|
| 全局快门单帧 | 0.0% | 0.0% | 0.0% | 0.0% |
| 加权差分累加（luma/blue） | 0.0% | 0.0% | 0.0% | 0.0% |
| 完整周期时域平均 | 94.3% | 85.8% | 98.4% | 100.0% |
| 相位搜索均值重构 | 94.2% | 87.5% | 97.2% | 100.0% |
| 相位搜索最大值重构 | 94.3% | 85.8% | 96.4% | 100.0% |
| 蓝通道最大值重构 | 95.0% | 90.0% | 98.3% | 100.0% |
| 最强攻击逐样本择优 | **95.2%** | **91.7%** | **98.6%** | **100.0%** |

这组负结果是论文安全声明的边界：系统对被动抽帧、逐帧流式识别、卷帘快门和不足完整周期的短曝光有效，但不能宣称防御主动连续录制后的完整周期积分、相位搜索或单通道最大值重构。

---

## 5. 关键发现与局限性分析 ⚠️

> 这是本毕设最重要的科学结论，也是答辩"局限性与未来工作"的核心。

### 5.1 多帧时域平均是视觉暂留类方案的根本数学局限

本 PoC 诚实地暴露：**当攻击者叠加 ≥n 帧（覆盖一个完整显示周期）后，可完全还原原始图像（OCR 100%）。**

原因是数学上的本质矛盾：

- 人眼"视觉无感"依赖 **积分还原** `ΣI_k = I`；
- 相机时域平均攻击用的是 **同一个求和操作**；
- 互斥完备掩模在叠加完整周期后被精确平均还原，对抗噪声因 `ΣN_k = 0` **同时被抵消**。

**凡是能被人眼积分还原的，就能被相机积分还原。** 交底书 3.1 节"抗多帧叠加约束"与"视觉完整性约束"在纯线性时域方案下不可同时严格成立——这不是实现缺陷，而是原理性张力。

### 5.2 有效的防御边界

PoC 确认方案对以下**主流威胁仍然有效**：

- **抽帧分析（Snapshots）**：智能眼镜随机抽取单张高分辨率图 → 0% 识别。
- **流式识别（Streaming）**：低分辨率连续帧逐帧 OCR → 每帧 0%，且帧间掩模独立。
- **卷帘快门**：逐行混合多子帧 → 0%。
- **长曝光**：配合反色帧插入 → 0%。

即覆盖了交底书背景技术中描述的 Ray-Ban Meta 等设备的**两种实际采集策略**。新增强攻击者结果进一步表明：只要攻击者能连续录制并做完整周期平均、相位搜索或逐通道 max 重构，内容仍会泄露；120 样本上逐样本最强攻击字符恢复率为 95.2%，泄露率为 100%，而加权差分累加仍未恢复 OCR。这一结果应作为论文中的边界证据，而不是回避：本方案防御被动抽帧/流式逐帧识别，但不宣称防御主动完整周期视频重构。

### 5.3 可行缓解方向（未来工作）

1. **视角差异化掩模**（交底书 7.2）：利用 LCD 视角依赖特性，使非正对相机捕获低质量帧——破坏多相机/离轴对齐。
2. **非线性时域调制**：引入人眼非线性（视觉积分非纯线性求和）与相机线性积分的差异，跳出 `ΣI_k=I` 的线性陷阱。
3. **运动内容自适应**（交底书 7.4）：对静态文档配合反色帧/黑帧打破纯线性叠加；对动态内容用运动模糊掩盖。
4. **帧率/相位攻防**：随机化周期长度与相位，提高攻击者完整周期对齐的难度。

### 5.4 视觉无感性的验证边界

视觉无感性目前仅由**模拟指标**验证（FPI 模型、CIEDE2000 ΔE、SSIM、运动模糊宽度）。交底书第 6 章要求的人因/硬件闭环验证——10 人 30 分钟主观观看实验、真实 HDR 屏输出、pursuit camera 运动清晰度实拍——尚未进行，属未来工作。

---

## 6. 与交底书的对应关系

| 交底书技术要素 | 实现位置 | 验证 |
|------|------|------|
| 3.2.1 随机点阵掩模 + CSPRNG + 卡方检验 | `core/mask_generator.py` | ✓ 单元测试 |
| 3.2.2 对抗噪声 + 时域互补 + Fisher-Yates 置换 | `core/noise_injector.py` | ✓ ΣN_k=0 |
| 3.2.3 高刷新率链路（时序/带宽数学关系） | `core/timing_controller.py` | ✓ hash/带宽/模拟 |
| 3.2.4 相机针对性防御（全局/卷帘/长曝光/离轴） | `attack/camera_simulator.py` | ✓ 攻击实验 |
| 4.2 驱动层注入 | — | 未来工作（需内核） |
| 4.3 HDR 亮度补偿 + HLG + ALS | `core/hdr_compensation.py` + `core/subframe_composer.py` | ✓ PQ/HLG/环境光/HDR 积分单测 |
| 5.1 配置持久化 + 预生成缓冲 | `core/config.py` + `core/mask_generator.py` | ✓ JSON/环形缓冲单测 |
| 6.3 视觉无感评估体系（FPI/ΔE/均匀性） | `evaluation/metrics.py` | ✓ 指标吻合 |
| 7.4 视觉疲劳策略 | `core/fatigue_policy.py` | ✓ 刷新率/蓝光/距离单测 |

---

## 7. 工程说明

- **亮度补偿默认采用背光提升模型（γ=1）**：子帧像素不放大，亮度恢复由硬件背光增益 `B=n` 完成（`integrate_subframes` 的 `boost=n/γ`）。`main.py demo`、benchmark 和实时窗口默认都使用该模型；实时窗口可通过配置 `brightness_model="pixel"` 演示交底书的 SDR 像素空间补偿 `γ=n·β`，但该模式只适合暗内容，对亮背景文档会饱和裁剪。
- **HDR 补偿是数值 PoC，不是真实 HDR 输出链路**：`hdr_compensation.py` 实现 PQ/HLG、ICtCp 软裁剪与峰值亮度 headroom；`SubframeComposer` 在 HDR 模式下按 `peak_nits/content_peak_nits` 做 HDR 感知积分回归。普通 SDR 窗口仍不能输出真实 PQ/HLG 帧，真实 HDR framebuffer/系统色彩管理接入属于未来工作。
- **噪声基底电平（pedestal）**：屏幕无法显示负光，黑像素处的负噪声会被裁剪而破坏 `ΣN_k=0`。给每个子帧加基底 `ε` 留出下探空间、积分时扣除，代价是黑位抬升 `ε/255` 的微小对比度损失。
- **FPI 模型核心**：随机点阵的空间相位随机化使人眼感受野汇聚后调制深度按 `1/√N` 衰减——这是随机掩模优于全屏高频闪烁方案的数学依据。
- **回放演示模式（`main.py playback`）**：实时窗口每周期要做截屏+掩模+噪声+合成（~190ms），在任何硬件上都到不了 120/240Hz，因此只能作为**攻击者视角**演示器。playback 模式对静态测试图离线预生成全部子帧，播放循环只做 blit+vsync，是**人眼端**演示器——在 `f_r ≥ 60n` 的高刷屏（n=4 需 240Hz）上可真实呈现人眼视觉积分后的完整画面（按 O 键可切换未保护原图对比）。内置演示可用 `--demo document`（默认合成文档）或 `--demo cet6 --pdf-page 1`（项目根目录的英语六级真题 PDF，建议竖版窗口 `--width 900 --height 1280`）。现场注意三点：① Windows 上先在"显示设置 → 高级显示"确认面板确实跑在 240Hz；② 用手机拍摄"防拍"效果需用专业模式短曝光（≤1/500s）——自动模式的长曝光会积分完整周期还原画面，这正是本文已记录的长曝光局限；③ 若手机翻译 OCR 仍能识别，可启用 `--anti-ocr-profile strong`，该模式默认保留小字可读性，只加入轻量条纹和字形扰动。不要在 strong/vlm 人眼演示中叠加等时长 `--inversion`：它会把周期变成 5 槽并洗掉小字；代码会自动抑制这个组合。若要压制能做版面重建的 VLM，可改用 `--anti-ocr-profile vlm`；该档位默认使用更大的 cell、更密的条纹和文字邻域伪笔画网格，优先让手机拍摄后的 VLM/OCR 读不稳。若 VLM 仍能读，再逐步提高 `--mask-cell-size`、`--stripe-alpha`、`--glyph-alpha`，代价是画面颗粒/条纹会更明显，且不再作为严格完备性数学演示。
