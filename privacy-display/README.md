# 基于视觉暂留与时间分片掩模的显示器隐私保护系统（PoC）

本项目是时间分片显示掩模的**概念验证原型（Proof of Concept）**和实验归档。当前英文论文把结果限定为：在一台 eMeet S600 UVC 摄像头、共同 3.91 ms 手动曝光、固定几何校正和三种开源传统 OCR 的条件下，评估完整配置的恢复率。该结果不是通用防拍照、防手机、防智能眼镜或防 VLM 声明。

> **实现范围**：本 PoC 实现应用/算法层，不含交底书第四章的 OS 驱动级注入（DXGI/KMS-DRM/CoreDisplay）。后者需内核模块与代码签名，属未来工作。

---

## 1. 核心原理

基础线性方案将图像 `I` 随机拆分为 `n` 个互补子帧 `I₁…Iₙ`：

- **数字域完备性** `ΣI_k = I`：子帧可在理想线性数字模型中重新求和。它不等价于真实面板亮度保持，也不预设固定的人眼积分时间。
- **互斥性**：每个像素在 `n` 个时隙中恰好被点亮一次（随机点阵掩模，ChaCha20 CSPRNG 驱动）。
- **理想域噪声互补** `ΣN_k = 0`：该等式只在裁剪、gamma、量化和相机成像之前成立；物理显示链路不保证抵消。

曝光窗口可能覆盖一个或多个时隙，也可能跨越面板响应过渡。完整周期、长曝光、视频平均、VLM 和自适应增强均可能恢复大量内容，因此安全性必须按具体曝光、设备、配置和攻击流程报告。

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
│   │   ├── mask_generator.py    # ChaCha20 CSPRNG 点阵分配 + 播放置换生成
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
python main.py playback --n 4 --anti-ocr-profile strong                # Strong 配置回放演示（非部署推荐）
python main.py playback --demo cet6 --pdf-page 1 --width 900 --height 1280 --n 4  # 英语六级真题 PDF 演示
python main.py playback --demo cet6 --pdf-page 1 --width 900 --height 1280 --n 4 --anti-ocr-profile capture_hardened  # 抗拍强化档压力测试

# 改进项实验（见 改进文档.md）
python experiments/performance_benchmark.py # A4 性能实测
python experiments/build_corpus.py          # C2 生成多样本语料
./scripts/rerun_corpus_surya.sh              # Table 5：仅重跑 Surya，保留 Tesseract/EasyOCR 并移除 PaddleOCR
.\.venv-surya\Scripts\python.exe -c "from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','surya'], merge_existing=True)"  # 120 样本三引擎全量复测
python experiments/ablation_noise.py        # B1 对抗噪声消融
python experiments/detection_attack.py      # G2 YOLOv8n 目标检测攻击
python experiments/view_attack.py           # G3 离轴相机攻击
python experiments/unet_reconstruction.py   # G5 学习型重构攻击
python experiments/real_capture_analysis.py --init-template # 生成真实拍摄 metadata 模板
python experiments/real_capture_analysis.py --engines tesseract # 分析已采集的真实拍摄图片
.\scripts\download_surya_models.ps1 # 首次下载 Surya 模型，支持失败后断点续传
.\scripts\rerun_real_capture_surya_only.ps1 -Jobs d0.5_a0 # 保留 Tesseract/EasyOCR，仅用 Surya 替换第三引擎
# Windows CUDA：EasyOCR + Surya 完整真实拍摄预处理网格见 docs/windows_easyocr_surya_preprocessing.md
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

### 3.1 服务器多检测器 / 视频 / 跟踪套件（COCO + MOT17）

GPU 服务器（如 2× RTX 4090）上对 YOLO26x、RT-DETR-x、Faster R-CNN、RetinaNet 四个检测器统一跑
clean / 单子帧 / 时间平均三种攻击帧，产出真实 COCO mAP（含 AP_S/M/L）、MOT17 逐帧检测与
ByteTrack 跟踪指标（MOTA/MOTP/IDF1，HOTA 经 TrackEval 可选）。完整步骤见
[`docs/detection_suite_server.md`](docs/detection_suite_server.md)。

```bash
pip install -U ultralytics && pip install -r requirements-detection.txt  # 服务器额外依赖
bash scripts/download_coco_val2017.sh                                     # 下载 COCO val2017
bash scripts/download_mot17.sh                                            # 下载 MOT17
SMOKE=1 MOT_SEQUENCES=MOT17-02 bash scripts/run_detection_suite.sh        # 小样冒烟
COCO_DEVICE=cuda:0 MOT_DEVICE=cuda:1 bash scripts/run_detection_suite.sh  # 双卡全量
# 产物：experiments/results/{coco_detection_attack,mot_video_detection,mot_tracking_attack}.json
# 并自动刷新 publication_summary.{json,md} 与 reproducibility_manifest.json
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

## 4. 与英文论文一致的实验结论

### 4.1 固定 3.91 ms UVC 条件

真实采集归档包含 10,575 张 S600 图像，混合主条件、组件消融和参数扫描，不能把总数理解成一个平衡比较的样本量。八个使用共同 3.91 ms 手动曝光的几何条件中，逐样本对 Surya、EasyOCR 和 Tesseract 取攻击者有利的最佳结果：

| 配置 | 样本数 | 平均字符恢复率 |
|---|---:|---:|
| 未保护 | 288 | 94.5% |
| 可读性优先 | 408 | 16.7% |
| 高抑制 | 288 | 5.6% |

这些数字只适用于几何校正后的相机裁剪图和固定预处理流程。主实验没有系统评估 CLAHE、gamma、阈值化、锐化、超分辨率或商业 OCR，因此不能据此宣称对所有传统 OCR 流程有效。可读性优先配置的 pooled P99 字符恢复率为 94.5%，敏感 token 恢复率为 24.0%；均值不能代表最坏情况。高抑制配置在共同曝光条件下也没有达到严格的 `<5%` 目标。

### 4.2 已测失效边界

- 150 帧时间均值仍可恢复大量文本；排除异常曝光位置后，可读性优先和高抑制配置的字符恢复率分别为 79.7% 和 53.9%。
- 长曝光不构成通用防护；部分位置甚至出现保护配置比未保护图像更易识别的反转。
- 三个商业 VLM 在大字体短文本上恢复率很高，传统 OCR 结论不能外推到 VLM。
- 数字域完整周期平均恢复率为 94.3%，逐样本最强数字攻击恢复率为 95.2%。

因此，本仓库展示的是一个固定物理条件下的测量结果及其失效边界，不是已经完成的安全产品。

### 4.3 可复现材料

- `experiments/results/real_capture_ocr.json`：真实采集 OCR 记录与汇总。
- `experiments/results/paper_ocr_clustered_stats.json`：内容聚类配对对比。
- `experiments/real_capture_vlm_evaluation.py`：VLM 评估与调用记录入口。
- `experiments/reproducibility_manifest.py`：环境、命令和文件哈希清单。
- `scripts/reproduce_all.sh`：测试、汇总与清单编排入口。

投稿对应的不可变 release 尚未生成。在正式提交前，需要冻结论文、脚本、去标识结果、依赖和哈希；任何包含姓名、学号或 API 密钥的文件都不得进入公开 release。

---

## 5. 关键局限与后续实验

当前最重要的未完成证据是：

1. 曝光—恢复率曲线，而不是仅比较 3.91 ms 与长曝光点；
2. CLAHE、gamma、阈值化、分通道、锐化和商业 OCR 的系统攻击扫描；
3. 亮度匹配静态对照、面板时序测量和跨摄像头复现；
4. 高抑制配置的可读性与视觉舒适度验证；
5. CJK 文字和更广内容分布。

只有完成相应实验后，才能扩大当前固定条件下的结论。

---

## 6. 与交底书的对应关系

| 交底书技术要素 | 实现位置 | 验证 |
|------|------|------|
| 3.2.1 随机点阵掩模 + CSPRNG 拒绝采样 + 卡方检验 | `core/mask_generator.py` | ✓ 单元测试 |
| 3.2.2 对抗噪声 + 时域互补分解 | `core/noise_injector.py` | ✓ ΣN_k=0 |
| 3.2.2b 子帧播放顺序 Fisher-Yates 置换 | `core/mask_generator.py` / 回放链路 | 方法说明 |
| 3.2.3 高刷新率链路（时序/带宽数学关系） | `core/timing_controller.py` | ✓ hash/带宽/模拟 |
| 3.2.4 相机攻击模拟（全局/卷帘/长曝光/离轴） | `attack/camera_simulator.py` | 数字域诊断 |
| 4.2 驱动层注入 | — | 未来工作（需内核） |
| 4.3 HDR 亮度补偿 + HLG + ALS | `core/hdr_compensation.py` + `core/subframe_composer.py` | ✓ PQ/HLG/环境光/HDR 积分单测 |
| 5.1 配置持久化 + 预生成缓冲 | `core/config.py` + `core/mask_generator.py` | ✓ JSON/环形缓冲单测 |
| 6.3 数字视觉代理指标（FPI/ΔE/均匀性） | `evaluation/metrics.py` | 数字模型，不等同于用户证据 |
| 7.4 视觉疲劳策略 | `core/fatigue_policy.py` | ✓ 刷新率/蓝光/距离单测 |

---

## 7. 工程说明

- **亮度补偿默认采用背光提升模型（γ=1）**：子帧像素不放大，亮度恢复由硬件背光增益 `B=n` 完成（`integrate_subframes` 的 `boost=n/γ`）。`main.py demo`、benchmark 和实时窗口默认都使用该模型；实时窗口可通过配置 `brightness_model="pixel"` 演示交底书的 SDR 像素空间补偿 `γ=n·β`，但该模式只适合暗内容，对亮背景文档会饱和裁剪。
- **HDR 补偿是数值 PoC，不是真实 HDR 输出链路**：`hdr_compensation.py` 实现 PQ/HLG、ICtCp 软裁剪与峰值亮度 headroom；`SubframeComposer` 在 HDR 模式下按 `peak_nits/content_peak_nits` 做 HDR 感知积分回归。普通 SDR 窗口仍不能输出真实 PQ/HLG 帧，真实 HDR framebuffer/系统色彩管理接入属于未来工作。
- **噪声基底电平（pedestal）**：屏幕无法显示负光，黑像素处的负噪声会被裁剪而破坏 `ΣN_k=0`。给每个子帧加基底 `ε` 留出下探空间、积分时扣除，代价是黑位抬升 `ε/255` 的微小对比度损失。
- **FPI、ΔE 和 SSIM**：这些量只描述数字模型，不能替代真实面板亮度、闪烁、可读性或舒适度测量。
- **回放演示模式（`main.py playback`）**：该模式离线预生成子帧，再通过 vsync 循环播放。它用于复现实验条件和用户研究刺激，不应被描述为已验证的生产防护。实际画面受刷新率、面板响应、合成器抖动和显示亮度影响；手机自动曝光、连续录像、VLM 或图像增强都可能恢复内容。`capture_hardened` 是历史代码中的高抑制配置名，旧的 `vlm` 参数仅作为兼容别名保留。
