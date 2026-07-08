# 第四轮审稿核验记录

核验日期：2026-07-07。核验对象为本轮意见点名的参考文献、VLM 标识、数据声明与 P95 数值。

## 参考文献

- `b_fernandez2024`：arXiv `2407.09717` 的作者、题名与当前条目一致；截至核验时未找到可确认的正式出版版本，保留预印本。
- `b_ghiasi2024`：已有 IEEE DCOSS-IoT 2024 正式版本，作者应为 Seyed Keyarash Ghiasi、Marco Kaldenbach、Marco Zuniga，页码 35--43，DOI `10.1109/DCOSS-IoT61029.2024.00016`。已替换预印本条目。来源：<https://research.tudelft.nl/en/publications/passive-screen-to-camera-communication>。
- `b_song2018`：arXiv `1802.05385` 的作者、题名与当前条目一致；未找到可确认的正式出版版本，保留预印本。
- `b_zhao2023`：原 BibTeX 作者信息错误。arXiv `2310.17626` 的正式版本由 Jindong Gu 等发表于 *Transactions on Machine Learning Research*（2024），已替换作者、期刊与年份。来源：<https://openreview.net/forum?id=AYJ3m7BocI>。
- `b_shi2023`：arXiv `2310.16809` 的作者、题名与当前条目一致；未找到可确认的正式出版版本，保留预印本。
- `b_zhong2023`：已有 *Applied Sciences* 13(21):11852 正式版本，DOI `10.3390/app132111852`，已替换预印本。来源：<https://www.mdpi.com/2076-3417/13/21/11852>。
- `b_li2025`：原 BibTeX 作者信息错误。arXiv `2503.13962` 的作者应为 Chengze Jiang、Zhuangzhuang Wang、Minjing Dong、Jie Gui；未找到可确认的正式出版版本，已修正作者并保留预印本。来源：<https://arxiv.org/abs/2503.13962>。

`IEEEtran.bst` v1.14 不输出独立 `doi` 字段，因此正式文献的 DOI 继续放在 `note` 字段，以确保生成的参考文献至少显示 DOI 文本。IEEE 参考规范要求 DOI 信息准确、完整，但没有要求作者源文件中的 DOI 必须是可点击超链接；终稿排版的链接化由 IEEE 制作流程处理。这里优先保证模板实际输出，而不是保留一个不会被当前 bst 渲染的标准字段。

## 2026 年条目

- `b_yolo26`：arXiv `2606.03748` 于 2026-06-02 提交，作者、题名与当前条目一致。当前日期为 2026-07-07，因此它不是未来条目。来源：<https://arxiv.org/abs/2606.03748>。
- `b_wang2026`：arXiv `2603.04930` 于 2026-03-05 提交，注明已被 CHI 2026 接收，并给出关联 DOI `10.1145/3772318.3791848`。作者、题名与当前条目一致。来源：<https://arxiv.org/abs/2603.04930>。

## Kimi K2.6 标识

- 结果文件记录的调用基址为 `https://api.siliconflow.cn/v1`，模型参数为 `Pro/moonshotai/Kimi-K2.6`；该字符串是 SiliconFlow 的供应商限定 API 标识。
- Moonshot AI 的公开上游模型名称为 `moonshotai/Kimi-K2.6`。模型卡明确将其标为原生多模态 `Image-Text-to-Text` 模型，并给出图像输入示例，因此不是仅文本模型，也不应改写成 Kimi-VL。来源：<https://huggingface.co/moonshotai/Kimi-K2.6>。
- 正文已同时说明供应商标识、上游名称和图像能力，保留实验可复现性而不混淆命名层级。

## 数据可用性

- Git 远端 `https://github.com/docandyc/privacy-display.git` 可公开读取。
- 当前远端 HEAD 为 `13977c25d21f2b520112bab6274dcac1f67adacf`，该提交已跟踪实验结果目录中的逐样本 OCR/VLM JSON 与复现清单。
- 数据声明已用该不可变提交 URL 取代存档 URL 占位符，并明确录用稿若有对齐修改将另建不可变版本。

## P95 数值复核

从 `privacy-display/experiments/results/real_capture_ocr.json` 重新筛选 `ablation=deployed`、`attack=short`，按 capture ID 对三引擎取最大字符恢复率，得到 459 个拍摄级样本。NumPy 线性百分位结果为：P50 `8.3333%`、P75 `16.6667%`、P90 `42.9814%`、P95 `60.9365%`、P99 `94.4670%`。因此正文的 P95 `60.9%` 正确。

同一结果文件中，deployed 长曝光的拍摄级均值为 `60.8603%`（324 个样本），四舍五入同样为 `60.9%`。两者数值相同纯属不同统计量的舍入巧合，不应改动。
