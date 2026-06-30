# Privacy Display 实验结果整理报告

生成日期：2026-06-30
范围：`privacy-display/experiments` 下当前已有的结构化结果文件、真实拍摄元数据、检测/跟踪结果和自动汇总文档。原始图片仅作为数据规模统计，不逐张展开。

## 技术摘要

当前结果基本形成了一条清晰结论：该方案对单帧 OCR、单帧目标检测和短曝光真实拍摄有稳定抑制效果；但一旦攻击者可以做时间聚合、相位搜索、长曝光或更强的多帧恢复，隐私内容仍可能被恢复。因此，论文叙述中应把“防单帧/短曝光采集”与“抗强时间聚合攻击”明确区分。

已完成的合成 OCR 基准上，Tesseract、EasyOCR 和旧版 PaddleOCR 的原始字符识别率约为 94% 到 95%，单个 protected subframe 后降至约 0%，敏感 token 召回也为 0%。当前运行链路已将第三引擎迁移为 Surya，合成语料的 Surya 补跑尚未进行，因此该表中 PaddleOCR 仅作为历史基准。

强相机攻击结果显示，global shutter 单槽、差分亮度、差分蓝通道均无法恢复文本；但 temporal average、phase search、blue-channel max 等多帧攻击可以恢复约 94% 到 95% 字符，best attack exact match 达到 91.7%。这说明威胁模型边界必须写清楚。

真实设备结果支持物理验证：9 组距离/角度 final capture 均已完成 Tesseract、EasyOCR、Surya 三引擎 OCR 行写入与总表合并，三个引擎均无 OCR error。按 attacker-favorable best-of-engine 口径，original short 字符恢复率为 92.5%，deployed short 降到 14.1%，VLM short 降到 4.2%；但 deployed temporal mean 仍达 65.4%，说明多帧聚合仍是主要真实拍摄风险。

检测/跟踪实验同样呈现“单帧防护明显，时间平均可部分恢复”的模式。合成 COCO 检测跨模型平均 mAP 从 clean 41.6% 降到 single subframe 2.9%，temporal average 回升到 13.0%；MOT17 视频检测平均 mAP 从 30.1% 降到 single subframe 2.0%，temporal average 回升到 8.1%。

## 数据与产物覆盖

| 类别 | 当前产物 | 覆盖情况 |
|---|---:|---|
| JSON 结果 | 76 个 | 包括 OCR、检测、跟踪、真实拍摄、消融、复现清单、校准与 capture manifest |
| Markdown 汇总 | 12 个 | `publication_summary.md`、主真实 OCR 汇总、9 组 position OCR 汇总和人工整理报告 |
| TrackEval/TXT | 54 个 | 真实 MOT 跟踪工作区、pedestrian summary、gt/tracker txt |
| 真实拍摄 final 目录 | 9 组 | `d0.5/d1/d1.5` × `0/15/30deg`，每组 1175 张 capture metadata |
| 主结果目录 | `results` | 30 个 JSON、2 个 MD、26 个 TXT |
| 补充检测目录 | `results_d1_a0_detection` | `d1_a0` 的 COCO、MOT 检测与 MOT 跟踪物理验证 |
| 补充检测目录 | `results_d1.5_a0_detection` | `d1.5_a0` 的 MOT 检测与 MOT 跟踪物理验证 |

已有自动总表：`results/publication_summary.md`。本报告是人工整理版，重点补充来源范围、结果解释、边界和缺口。

## 指标定义

| 指标 | 含义 |
|---|---|
| 字符恢复率 / char recovery | OCR 或 VLM 输出与 ground truth 的字符级相似度；越低代表隐私保护越强 |
| Exact match | 完整文本完全匹配比例；越低越好 |
| Sensitive token recall | 敏感字段或 token 被恢复的比例；越低越好 |
| Leak rate char>=20% | 字符恢复率不低于 20% 的样本占比；越低越好 |
| mAP / mAP50 / mAP75 | 检测精度指标；protected 条件下越低代表检测越难 |
| Recall / Precision | 检测召回与精度；召回下降通常代表目标更难被检出 |
| MOTA / MOTP / IDF1 / HOTA | 多目标跟踪指标；protected 条件下降代表跟踪链路受阻 |
| FPI | Flicker Perceptibility Index；用于衡量闪烁可感知风险，越低越好 |
| MI | 单帧 mutual information；越低说明单帧携带的信息越少 |

## 合成 OCR 结果：单帧保护非常强

`corpus_multi_engine.json` 显示三种 OCR 引擎在原始图像上均能高精度恢复文本，而 protected subframe 基本无法恢复。

| OCR 引擎 | 样本数 | 原始字符准确率 | Subframe 字符准确率 | Paired reduction | Subframe word / exact / sensitive |
|---|---:|---:|---:|---:|---:|
| Tesseract | 120 | 94.0% | 0.0% | 93.9% | 0.0% / 0.0% / 0.0% |
| EasyOCR | 120 | 94.1% | 0.0% | 94.1% | 0.0% / 0.0% / 0.0% |
| PaddleOCR | 120 | 94.9% | 0.0% | 94.9% | 0.0% / 0.0% / 0.0% |

分层结果也稳定：不同文本类型、语言、版式和字号下，subframe 字符恢复率基本为 0%。原始 OCR 中表格类最低，约 75.7%；数字、短密钥和 URL token 原始准确率接近 99% 到 100%。

## 强相机攻击：时间聚合是主要风险

`corpus_strong_camera_attack.json` 和 `attack_analysis_strong_camera.json` 表明，单帧与差分类攻击失败，但多帧聚合攻击可恢复文本。

实验做法：先用 `build_corpus.py` 的 120 张合成文本语料作为输入，覆盖英文、中文、数字、账号、URL、代码、表格和段落等类型；每张图按 `n=4`、`epsilon=8/255` 生成受保护子帧，并保留 2 个完整显示周期。随后用 `CameraSimulator` 构造强相机攻击帧：`global_shutter_slot0` 只取单个子帧，`temporal_average_cycle` 平均一个完整周期，`phase_search_mean/max` 假设攻击者不知道周期起点但知道周期长度并枚举候选窗口，`differential_luma/blue` 累加相邻帧差分，`blue_channel_max` 只用蓝通道做最大值聚合。每个攻击帧都送入 Tesseract OCR，再与 ground truth 比较字符恢复率、exact match、敏感 token recall 和泄露率；泄露率口径为字符恢复率不低于 20%。`best_attack_per_sample` 是每张样本在所有攻击中取恢复效果最强的一项。

补充单样例实验使用 `The quick brown fox 12345 PASSWORD` 作为 ground truth，逐项测试单帧、不同帧数的时域平均、相位搜索、蓝通道恢复和长曝光积分。该实验用于解释机制边界：当叠加帧数覆盖完整周期时，互斥完备掩模会被线性平均还原；而插入 inversion frame 时，长曝光积分趋向中性灰，从而抑制 OCR。

复现命令：

```powershell
python experiments\attack_analysis.py
```

| 攻击方式 | 字符恢复率 | Exact match | Sensitive token recall | 泄露率 |
|---|---:|---:|---:|---:|
| global_shutter_slot0 | 0.0% | 0.0% | 0.0% | 0.0% |
| differential_luma | 0.0% | 0.0% | 0.0% | 0.0% |
| differential_blue | 0.0% | 0.0% | 0.0% | 0.0% |
| temporal_average_cycle | 94.3% | 85.8% | 98.4% | 100.0% |
| phase_search_mean | 94.2% | 87.5% | 97.2% | 100.0% |
| phase_search_max | 94.3% | 85.8% | 96.4% | 100.0% |
| blue_channel_max | 95.0% | 90.0% | 98.3% | 100.0% |
| best_attack_per_sample | 95.2% | 91.7% | 98.6% | 100.0% |

补充单样例攻击中，`phase_search_mean`、`phase_search_max` 和 `blue_channel_max` 都能完整恢复 `The quick brown fox 12345 PASSWORD`；带 inversion 的 long exposure 字符恢复率为 0%，不带 inversion 则为 100%。这支持 inversion 在长曝光防护中的必要性。

## 参数与性能：推荐点是 n=6 @ 360Hz

`pareto_sweep.json` 与 `benchmark_results.json` 给出隐私、安全与可感知闪烁之间的取舍。自动推荐为 `n=6 @ 360Hz`，FPI 为 0.0333，single-frame MI 为 0.249。

实验做法：`pareto_sweep.py` 在同一套合成文本语料上扫描 `n=2,4,6,8`、刷新率 `144/240/360Hz` 和固定噪声预算 `epsilon=8/255`。当前结果采用按类别分层抽样，最多 120 张样本。对每个 `n`，脚本先生成一个完整周期的 protected subframes，然后计算单帧 OCR、完整周期 OCR、单帧互信息和视觉指标；由于图像域指标只依赖 `n` 与 `epsilon`，脚本会先缓存每个 `(n, epsilon)` 的 OCR/图像指标，再展开不同刷新率计算 FPI。

指标口径：`Single-frame OCR` 是对单个 protected subframe 做 OCR 后取平均；`Full-cycle OCR` 是把一个完整周期的 `n` 张子帧做时域平均后再 OCR；`Single-frame MI` 对应代码里的 `entropy_ratio`，即单子帧相对原图的归一化互信息，越低代表单帧泄露越少；`FPI` 只由刷新率和 `n` 计算，阈值为 `<0.1` 视为闪烁不可感知。自动推荐规则是先筛选 `FPI < 0.1` 的配置，再从中选择 `Single-frame MI` 最低的配置，因此得到 `n=6 @ 360Hz`。`benchmark_results.json` 是更早的固定配置基准，主要作为趋势和基础指标补充；推荐点以 `pareto_sweep.json` 为准。

复现命令：

```powershell
python experiments\pareto_sweep.py --samples-per-category 20 --max-samples 120
```

| n | Single-frame OCR | Full-cycle OCR | Single-frame MI | FPI 结论 |
|---:|---:|---:|---:|---|
| 2 | 0.0% | 94.3% | 0.566 | 144/240/360Hz 均通过 |
| 4 | 0.0% | 94.5% | 0.377 | 240/360Hz 通过，144Hz 不通过 |
| 6 | 0.0% | 94.2% | 0.249 | 360Hz 通过，144/240Hz 不通过 |
| 8 | 0.0% | 94.5% | 0.217 | 144/240/360Hz 均不通过 |

`benchmark_results.json` 额外包含 6 个配置。所有配置的 subframe OCR 都为 0%，但 FPI 只在 `n=2@144Hz` 和 `n=4@240Hz` 等高刷新配置下为 safe。

## 检测与跟踪：single subframe 明显削弱检测链路

合成 COCO 与 MOT17 结果说明，该方案不只影响 OCR，也显著影响目标检测与跟踪。下表为四个检测模型的跨模型均值。

| 实验 | 条件 | mAP | mAP50 | Recall / IDF1 |
|---|---|---:|---:|---:|
| COCO 检测 | clean | 41.6% | 54.2% | n/a |
| COCO 检测 | single_subframe | 2.9% | 3.7% | n/a |
| COCO 检测 | temporal_average | 13.0% | 17.9% | n/a |
| MOT17 视频检测 | clean | 30.1% | 54.5% | Recall 60.8% |
| MOT17 视频检测 | single_subframe | 2.0% | 5.0% | Recall 5.9% |
| MOT17 视频检测 | temporal_average | 8.1% | 16.7% | Recall 19.3% |
| MOT17 跟踪 | clean | MOTA 13.4% | n/a | IDF1 32.9% |
| MOT17 跟踪 | single_subframe | MOTA -1.1% | n/a | IDF1 3.2% |
| MOT17 跟踪 | temporal_average | MOTA -2.0% | n/a | IDF1 13.1% |

解释上应注意：temporal average 会让检测/跟踪部分恢复，但仍显著低于 clean；跟踪的 MOTA 在某些模型下为负，说明错误跟踪、漏检和误检综合后超过了正贡献。

## 真实设备 COCO/MOT：物理验证支持保护效果

真实设备结果来自 240Hz 屏幕和 USB 摄像头。`real_clean` 是被摄像头拍摄到的未保护基线，`real_short` 是短曝光/单帧 protected，`real_video` 是 temporal mean。MOT17 真实拍摄是 stop-motion physical-frame validation，每个数据集帧被静态展示后采集；不应写成连续视频播放同步实验。

| 结果文件 | 场景 | 条件 | 跨模型平均关键指标 |
|---|---|---|---|
| `results/real_capture_coco_detection.json` | `d1.5_a0` COCO | real_clean | mAP 25.6%, mAP50 43.2% |
| 同上 | `d1.5_a0` COCO | real_short | mAP 1.6%, mAP50 2.9% |
| 同上 | `d1.5_a0` COCO | real_video | mAP 2.9%, mAP50 4.7% |
| `results_d1_a0_detection/real_capture_coco_detection.json` | `d1_a0` COCO | real_clean | mAP 11.9%, mAP50 23.8% |
| 同上 | `d1_a0` COCO | real_short | mAP 0.0%, mAP50 0.0% |
| 同上 | `d1_a0` COCO | real_video | mAP 0.0%, mAP50 0.0% |
| `results_d1_a0_detection/real_capture_mot_detection.json` | `d1_a0` MOT | real_clean | mAP 14.8%, mAP50 48.5%, recall 56.7% |
| 同上 | `d1_a0` MOT | real_short | mAP 0.1%, mAP50 0.2%, recall 0.2% |
| 同上 | `d1_a0` MOT | real_video | mAP 0.0%, mAP50 0.0%, recall 0.0% |
| `results_d1.5_a0_detection/results/real_capture_mot_detection.json` | `d1.5_a0` MOT | real_clean | mAP 1.3%, mAP50 7.8%, recall 22.4% |
| 同上 | `d1.5_a0` MOT | real_short | mAP 0.6%, mAP50 3.3%, recall 11.0% |
| 同上 | `d1.5_a0` MOT | real_video | mAP 0.7%, mAP50 3.9%, recall 12.7% |

跟踪方面，`d1_a0` 的 protected tracking 基本退化到 0 附近；`d1.5_a0` 因 clean 本身已经较弱，protected 条件仍让 IDF1/HOTA 约减半。

| 结果文件 | 条件 | MOTA | IDF1 | HOTA |
|---|---|---:|---:|---:|
| `results_d1_a0_detection/real_capture_mot_tracking.json` real_clean | clean | -41.7% | 25.1% | n/a |
| 同上 real_short | protected short | -0.1% | 0.1% | n/a |
| 同上 real_video | protected video | 0.0% | 0.0% | n/a |
| `results_d1.5_a0_detection/results/real_capture_mot_tracking.json` real_clean | clean | -106.6% | 10.5% | 14.6% |
| 同上 real_short | protected short | -49.6% | 5.5% | 7.2% |
| 同上 real_video | protected video | -52.3% | 7.1% | 9.2% |

## 真实拍摄 OCR：9 组距离/角度已完成三引擎整合

真实拍摄 final 目录覆盖 `d0.5/d1/d1.5` × `0/15/30deg`，每组 metadata 都有 1175 个 captures。当前每组均已生成 `results_<position>_final/real_capture_ocr.json` 与 `.md`，主汇总 `results/real_capture_ocr.json` 合并 9 组、10575 个 captures、31725 条 OCR rows。

三个引擎均成功完成 10575 行，且错误行均为 0。下表给出各引擎的原始指标；后续场景表采用 `real_capture.py` 的 attacker-favorable `best_of` 口径，即同一 capture 在 Tesseract、EasyOCR 和 Surya 中取恢复效果最强的一项。

| OCR 引擎 | OCR rows | Error rows | 字符恢复率 | Exact match | Sensitive recall | 泄露率 |
|---|---:|---:|---:|---:|---:|---:|
| Tesseract | 10575 | 0 | 30.4% | 12.5% | 30.9% | 37.3% |
| EasyOCR | 10575 | 0 | 24.9% | 2.9% | 25.3% | 36.7% |
| Surya | 10575 | 0 | 19.7% | 8.3% | 54.1% | 24.5% |

关键距离/角度结果如下，数值为字符恢复率。`VLM` 对应当前 metadata 中的 `vlm` ablation，不是在线 VLM 模型读取结果。

| 场景 | original short | deployed short | deployed temporal mean | VLM short | VLM long |
|---|---:|---:|---:|---:|---:|
| `d0.5_a0` | 78.1% | 0.0% | 0.0% | 0.8% | 18.2% |
| `d0.5_a15` | 91.0% | 2.6% | 2.6% | 0.5% | 5.2% |
| `d0.5_a30` | 94.1% | 7.8% | 82.5% | 3.2% | 5.8% |
| `d1_a0` | 94.3% | 11.4% | 77.9% | 3.6% | 16.2% |
| `d1_a15` | 96.4% | 11.7% | 80.8% | 6.2% | 3.2% |
| `d1_a30` | 94.7% | 14.5% | 83.9% | 3.1% | 11.5% |
| `d1.5_a0` | 94.4% | 19.8% | 87.3% | 6.5% | 13.2% |
| `d1.5_a15` | 94.2% | 30.0% | 86.4% | 6.5% | 10.1% |
| `d1.5_a30` | 95.6% | 28.9% | 87.2% | 7.1% | 16.7% |
| **总体** | **92.5%** | **14.1%** | **65.4%** | **4.2%** | **11.1%** |

解释：`deployed short` 在所有距离/角度下均显著低于 unprotected original，但距离变远或角度变化后仍可能出现 10% 到 30% 左右的字符恢复。`vlm short` 在 9 组中最稳定，整体字符恢复率为 4.2%、泄露率为 3.4%。然而 `deployed temporal mean` 在 0.5m/30deg 及多个更远距离场景下恢复率超过 80%，说明真实相机多帧时间聚合仍然是必须写入限制条件的主要攻击路径。

## VLM 可读性：模型能读 temporal/phase 攻击帧

`vlm_qwen3_siliconflow.json` 和 `vlm_model_ablation.json` 显示，多模态大模型对原始图和时间聚合/相位搜索恢复帧有较高读取能力。

| Attack frame | Qwen3-VL-32B | Kimi-K2.6 | GLM-4.5V |
|---|---:|---:|---:|
| original | 100.0% | 77.8% | 100.0% |
| global_shutter_slot0 | 0.0% | 0.0% | 0.0% |
| temporal_average_cycle | 92.6% | 74.1% | 100.0% |
| phase_search_max | 100.0% | 74.1% | 100.0% |

VLM prompt ablation 中，strict transcription、relaxed readability、sensitive field extraction 三类 prompt 的字符恢复率都约 72.7%。VLM model ablation 中，Qwen、Kimi、GLM 的字符恢复率分别约 96.3%、96.0%、93.2%。

## 消融实验：组件贡献和失败模式已经较完整

| 实验文件 | 状态 | 关键结论 |
|---|---|---|
| `component_ablation.json` | 可用 | baseline 94.0%；single mask/noise 接近 0%；inpaint mask only 可恢复 50.9%；long exposure with inversion 为 0% |
| `recognizer_generalization.json` | 可用 | Tesseract original 94.0%；single subframe 0.0%；temporal/phase/blue attack 约 94% |
| `perceptual_ablation.json` | 可用 | RGB full、blue residual、blue kept、green kept 的 char recovery 都约 0% |
| `pareto_sweep.json` | 可用 | 推荐 `n=6 @ 360Hz`，FPI 0.0333，MI 0.249 |
| `strong_attack_extra.json` | 可用 | rolling shutter row alignment 92.9%，temporal superresolution 91.4%；single subframe 0% |
| `adaptive_attack_ablation.json` | 可用 | Otsu、adaptive threshold、CLAHE、unsharp、denoise、upscale 等单帧后处理均约 0% |
| `camera_pipeline_ablation.json` | 可用 | JPEG、sensor noise、motion blur、zoom、auto contrast 后仍约 0%；temporal average boundary 94.4% |
| `screen_privacy_baselines.json` | 可用 | unprotected/dim 约 92.9%；gaussian blur 52.6%；privacy filter proxy 84.7%；pixelate 和 temporal mask 接近 0% |
| `vlm_prompt_ablation.json` | 可用 | 三类 prompt 结果接近，约 72.7% 字符恢复 |
| `noise_epsilon_sweep.json` | 可用 | epsilon 从 0 到 0.3765，single-frame OCR 都接近 0% |
| `vlm_model_ablation.json` | 可用 | 三个 VLM family 对恢复帧均可读，字符恢复率约 93% 到 96% |
| `brightness_compensation_ablation.json` | 可用 | gamma 1/2/4 下 single-frame OCR 仍接近 0% |
| `mask_granularity_ablation.json` | 可用 | block 1/2/4 接近 0%，block 8 升到 0.8% |
| `anti_ocr_profile_ablation.json` | 可用 | block2/s0.30_g0.22 temporal average 降到 10.7%；block1/vlm 降到 49.1% |
| `seed_sensitivity.json` | 可用 | 10 seeds、45 samples 下 single-frame OCR 均值约 0.04%，seed 敏感性很低 |
| `usability_pilot.json` | 缺失 | 有 `usability_pilot.py`，但没有对应结果 JSON |

## 重建攻击与 inpainting

`unet_reconstruction.json` 显示 tiny U-Net 在 5 个训练样本、3 个 epoch 的设置下，holdout 上 PSNR 为 9.54 dB、SSIM 为 0.783，但 OCR 字符准确率为 0。相比之下，inpaint baseline 虽然 SSIM 更高，为 0.929，但 OCR 字符准确率为 1.0。

该结果说明视觉相似度并不等价于隐私泄露；报告中更应优先引用 OCR、sensitive recall、exact match 等隐私指标。pedestal ablation 中，clean subframe inpaint OCR 为 1.0，noised subframe inpaint OCR 为 0.0，支持 noise pedestal 对抗 inpainting 的作用。

## 复现与工程产物

`reproducibility_manifest.json` 已记录 git、环境、命令、结果文件和源文件，便于论文复现实验链路。`results/trackeval_workspace_real`、`results_d1_a0_detection/trackeval_workspace_real` 下保留了 MOT gt、tracker data 和 pedestrian summary；这些应作为跟踪实验的审计材料，而不是正文主表。

校准文件位于 `real_captures/calibration`，包括 `exposure.json` 和多个 ROI homography，例如 `roi_d1_a0.json`、`roi_d1.5_a30.json` 等。真实检测/跟踪 manifest 中记录了 exposure、camera settings、burst、reduce、crop 等采集元信息。

## 当前缺口与建议

1. `usability_pilot.json` 缺失。若论文需要人眼可用性或主观体验证据，需要运行或补录 `usability_pilot.py` 的结构化结果。
2. 真实拍摄已使用 Surya 替换 PaddleOCR 并完成九个位置；但合成语料 `corpus_multi_engine.json` 仍保留旧 PaddleOCR 历史基准。若论文要求三引擎名称完全一致，还需对 120 张合成语料补跑 Surya。
3. `publication_summary.md` 已重新生成；但真实检测/跟踪路径仍分布在 `results_d1_a0_detection` 和 `results_d1.5_a0_detection/results`，正文引用时应写清来源路径。
4. 强攻击结果必须在论文中作为威胁模型边界呈现。可以主张“防短曝光/单帧采集”，但不应泛化成“防所有多帧聚合相机攻击”。
5. 真实 MOT 是静态逐帧 physical validation，不是连续视频播放同步验证；正文表述需要保留这个限定。

## 可直接写入论文的结论表述

在合成 OCR 语料上，所提方案将三种 OCR 引擎的单帧字符恢复率从约 94% 到 95% 降至近 0%，且敏感 token 召回为 0。该结果表明，受限于短曝光或单帧采集的攻击者难以从单个 protected subframe 中恢复文本。

在强攻击设定下，多帧 temporal average、phase search 和 blue-channel max 可恢复约 94% 到 95% 的字符，并达到最高 91.7% 的 exact match。这说明系统的安全性依赖于攻击者是否能够跨完整周期采样并进行时间聚合。

真实设备拍摄进一步验证了短曝光防护效果：9 组距离/角度下，original short 的 best-of-engine 字符恢复率为 92.5%，deployed short 降至 14.1%，VLM short 降至 4.2%。但 deployed temporal mean 仍达到 65.4%，在多个远距离或斜视角场景超过 80%，需作为多帧时间聚合限制说明。真实设备 OCR 结论现基于 Tesseract、EasyOCR、Surya 三引擎及 attacker-favorable best-of 结果。

目标检测与跟踪实验显示，隐私帧也会干扰视觉检测链路。COCO 合成检测跨模型平均 mAP 从 clean 的 41.6% 降至 single subframe 的 2.9%；MOT17 视频检测平均 mAP 从 30.1% 降至 2.0%。真实设备 COCO/MOT 结果同样显示 protected short 条件显著降低检测与跟踪指标。
