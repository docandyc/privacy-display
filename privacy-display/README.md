# 基于视觉暂留与时间分片掩模的显示器隐私保护系统（PoC）

本项目是毕业设计技术交底书《一种基于视觉暂留与时间分片掩模的显示器隐私保护方法及系统》的**概念验证原型（Proof of Concept）**实现。在普通桌面（Python + GPU）环境下验证核心算法的有效性、量化关键指标，并诚实评估方案的边界与局限。

> **实现范围**：本 PoC 实现应用/算法层，不含交底书第四章的 OS 驱动级注入（DXGI/KMS-DRM/CoreDisplay）。后者需内核模块与代码签名，属未来工作。

---

## 1. 核心原理

将每帧完整图像 `I` 在时域随机拆分为 `n` 个互补子帧 `I₁…Iₙ`，满足：

- **完备性** `ΣI_k = I`：人眼在 ~50ms 积分窗口内叠加所有子帧，感知到完整原图。
- **互斥性**：每个像素在 `n` 个时隙中恰好被点亮一次（随机点阵掩模，ChaCha20 CSPRNG 驱动）。
- **噪声互补** `ΣN_k = 0`：对抗噪声分解为时域互补分量，人眼积分后完全抵消、单帧内最大化 OCR 混淆。

相机在任一快门时刻只能捕获碎片化的单子帧，信息熵远低于 OCR/检测模型的识别下限。

---

## 2. 项目结构

```
privacy-display/
├── main.py                      # 入口: demo / benchmark / window / test-noise
├── experiments/
│   ├── attack_analysis.py       # 攻击鲁棒性分析（核心实验）
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
│   │   └── camera_simulator.py  # 全局/卷帘快门、时域平均、长曝光攻击
│   ├── demo/
│   │   ├── visual_integration.py # 人眼视角 vs 相机视角对比图/动画
│   │   └── privacy_window.py    # pygame 实时屏幕保护演示
│   └── evaluation/
│       ├── metrics.py           # FPI / CIEDE2000 ΔE / 归一化互信息 / 亮度均匀性
│       └── benchmark.py         # 参数扫描评测套件 + matplotlib 图表
└── tests/                       # 57 个单元测试
```

---

## 3. 环境与运行

```bash
# 已用 uv 维护 .venv，激活后：
source .venv/bin/activate

# 核心依赖（已安装）：numpy scipy pycryptodome pillow opencv-python pytest moderngl
# OCR 攻击实验额外需要：pytesseract + 系统 tesseract（brew install tesseract）
# 目标检测实验使用：ultralytics YOLOv8n（首次运行会下载 yolov8n.pt，本地权重不提交）

python -m pytest tests/ -q          # 117 项单元测试
python main.py demo                 # 生成对比图/GIF + 打印指标
python main.py benchmark            # 参数扫描评测（需 tesseract）
python experiments/attack_analysis.py       # 攻击鲁棒性分析（核心实验）
python main.py window               # 实时屏幕保护演示（默认 n=2@120Hz，需 pygame+mss）

# 改进项实验（见 改进文档.md）
python experiments/performance_benchmark.py # A4 性能实测
python experiments/build_corpus.py          # C2 生成多样本语料
python experiments/ablation_noise.py        # B1 对抗噪声消融
python experiments/detection_attack.py      # G2 YOLOv8n 目标检测攻击
python experiments/view_attack.py           # G3 离轴相机攻击
python experiments/unet_reconstruction.py   # G5 学习型重构攻击
```

> **改进路线见 [`改进文档.md`](改进文档.md)**：已实现 HDR 补偿(ICtCp/PQ)、黑帧+AE 攻击、
> 多显示器同步、性能实测、真实对抗噪声+消融、去混淆/重构攻击、视角差异化掩模、
> 掩模取模偏置修复、多样本多引擎评测、YOLOv8n 目标检测评测、离轴攻击、
> 学习型重构攻击、HLG/ALS、配置持久化、SSIM/运动模糊指标等。
> 新增模块：`src/core/hdr_compensation.py`、`src/core/multi_display.py`、
> `src/core/fatigue_policy.py`、`src/core/config.py`、`src/attack/reconstruction_attack.py`、
> `src/attack/detection_evaluator.py`。

---

## 4. 实验结果

### 4.1 视觉无感性与算法正确性（已验证 ✓）

| 指标 | 实测值（n=4, 240Hz, ε=8/255） | 交底书目标 | 状态 |
|------|------|------|------|
| FPI 闪烁感知指数 | **0.030** | <0.1 | ✓ 吻合 |
| Delta E (CIEDE2000) | **0.006** | <1.0 | ✓ 不可感知 |
| 噪声互补残差 ΣN_k | **0.0** | =0 | ✓ 精确 |
| 子帧完备性误差 ΣI_k−I | **0.0** | =0 | ✓ 精确 |
| 单帧信息保留率（互信息） | **0.15–0.35** | 0.12–0.18 | ✓ 接近 |
| GPU vs 软件渲染一致性 | 像素级一致 | — | ✓ |

FPI 模型与交底书逐项吻合：240Hz/n4→0.030、480Hz/n8→0.035、144Hz/n2→0.014、360Hz/n6→0.033。

### 4.2 攻击防御效果

| 攻击方式 | OCR 准确率 | 防御 |
|------|------|------|
| 原始帧（基线） | 100% | — |
| 全局快门单帧捕获 | **0%** | ✓ 有效 |
| 卷帘快门混合采样 | **0%** | ✓ 有效 |
| 时域平均（叠加 1–3 帧，<一个周期） | **0%** | ✓ 有效 |
| **时域平均（叠加 ≥4 帧，覆盖完整周期）** | **100%** | ✗ **失守** |
| 长曝光积分（无反色帧） | 100% | ✗ 失守 |
| 长曝光积分（插入反色帧） | **0%** | ✓ 有效 |

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

即覆盖了交底书背景技术中描述的 Ray-Ban Meta 等设备的**两种实际采集策略**。只有"主动连续录制完整周期 + 精确帧对齐 + 时域平均"这一更强的离线攻击能突破，而这超出了被动抽帧/流式识别的威胁模型。

### 5.3 可行缓解方向（未来工作）

1. **视角差异化掩模**（交底书 7.2）：利用 LCD 视角依赖特性，使非正对相机捕获低质量帧——破坏多相机/离轴对齐。
2. **非线性时域调制**：引入人眼非线性（视觉积分非纯线性求和）与相机线性积分的差异，跳出 `ΣI_k=I` 的线性陷阱。
3. **运动内容自适应**（交底书 7.4）：对静态文档配合反色帧/黑帧打破纯线性叠加；对动态内容用运动模糊掩盖。
4. **帧率/相位攻防**：随机化周期长度与相位，提高攻击者完整周期对齐的难度。

---

## 6. 与交底书的对应关系

| 交底书技术要素 | 实现位置 | 验证 |
|------|------|------|
| 3.2.1 随机点阵掩模 + CSPRNG + 卡方检验 | `core/mask_generator.py` | ✓ 单元测试 |
| 3.2.2 对抗噪声 + 时域互补 + Fisher-Yates 置换 | `core/noise_injector.py` | ✓ ΣN_k=0 |
| 3.2.3 高刷新率链路（时序/带宽数学关系） | `core/timing_controller.py` | ✓ hash/带宽/模拟 |
| 3.2.4 相机针对性防御（全局/卷帘/长曝光/离轴） | `attack/camera_simulator.py` | ✓ 攻击实验 |
| 4.2 驱动层注入 | — | 未来工作（需内核） |
| 4.3 HDR 亮度补偿 + HLG + ALS | `core/hdr_compensation.py` | ✓ PQ/HLG/环境光单测 |
| 5.1 配置持久化 + 预生成缓冲 | `core/config.py` + `core/mask_generator.py` | ✓ JSON/环形缓冲单测 |
| 6.3 视觉无感评估体系（FPI/ΔE/均匀性） | `evaluation/metrics.py` | ✓ 指标吻合 |
| 7.4 视觉疲劳策略 | `core/fatigue_policy.py` | ✓ 刷新率/蓝光/距离单测 |

---

## 7. 工程说明

- **亮度补偿采用背光提升模型（γ=1）**：子帧像素不放大，亮度恢复由硬件背光增益 `B=n` 完成（`integrate_subframes` 的 `boost=n/γ`）。交底书的 SDR 像素空间补偿 `γ=n·β` 仅适用暗内容，对亮背景文档会饱和裁剪，故 PoC 默认用背光模型。
- **噪声基底电平（pedestal）**：屏幕无法显示负光，黑像素处的负噪声会被裁剪而破坏 `ΣN_k=0`。给每个子帧加基底 `ε` 留出下探空间、积分时扣除，代价是黑位抬升 `ε/255` 的微小对比度损失。
- **FPI 模型核心**：随机点阵的空间相位随机化使人眼感受野汇聚后调制深度按 `1/√N` 衰减——这是随机掩模优于全屏高频闪烁方案的数学依据。
