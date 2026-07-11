## Content Summary

源稿是一篇面向 IEEE Access 的显示隐私实验论文。论文研究“时序像素掩蔽”：将屏幕内容分解为高速交替的互补子帧，并叠加档位相关的条纹、字形扰动和可选反色帧，以降低短曝光物理拍摄后的传统 OCR 恢复率。稿件将贡献严格限定为单一 UVC 摄像头链路、一个标称曝光控制设置下的档位级物理测量，并用长曝光、150 帧均值、固定预处理网格和商业 VLM 探针呈现失效边界。用户体验研究仍是待执行协议，作者信息与结果占位必须保留。

译文面向中文学术读者，目的不是改写科学主张，而是完整同步当前英文稿的结构、数字、证据层级和限制条件。中文稿必须避免沿用旧版中的过时结果，例如 94.1/15.1/5.0 的非匹配池化主结果、四帧视频表述或旧表号。

## Terminology

| English | 中文统一译法 |
|---|---|
| Temporal pixel masking | 时序像素掩蔽 |
| profile-level measurement | 档位级测量 |
| conventional OCR | 传统 OCR |
| character recovery | 字符恢复率 |
| exact match | 完全匹配率 |
| field-micro exact recovery | 字段微平均完全恢复率 |
| readability-priority | 可读性优先档 |
| high-suppression | 高抑制档 |
| unprotected | 未保护档 / 未保护条件（依语境） |
| mask-only | 仅掩蔽档 |
| mask + noise | 掩蔽加噪声档 |
| Strong profile | Strong 档（首次说明为强 anti-OCR 档） |
| common-setting analysis | 共同设置分析 |
| matched unit | 匹配单元 |
| duplicate averaging | 重复采集平均 |
| content-cluster resampling | 内容项聚类重采样 |
| failure boundary | 失效边界 |
| fixed preprocessing grid | 固定预处理网格 |
| oracle | 网格最优选择（oracle） |
| attack upper bound | 攻击上界 |
| temporal mean | 时域均值 |
| full-cycle integration | 全周期积分 |
| sustained video attacker | 持续视频攻击者 |
| vision-language model (VLM) | 视觉语言模型（VLM） |
| screen--camera link | 屏幕—相机链路 |
| capture geometry | 拍摄几何条件 |
| duty-cycle luminance | 占空比亮度 |
| luminance-matched static control | 亮度匹配的静态对照 |
| panel response | 面板响应 |
| rolling-shutter row mixing | 滚动快门行混合 |
| proof of concept (PoC) | 概念验证（PoC） |
| visual eavesdropping | 视觉窃听 |
| leak rate | 泄漏率 |
| evidence hierarchy | 证据层级 |
| claim scope | 主张范围 |
| fixed-link association | 固定链路关联 |

## Tone & Style

采用正式、克制、证据导向的中文学术文体。保持 IEEE 工程论文的结构和密度，但避免逐词翻译造成的欧化长句。Results 只报告观察，Discussion 才解释机制；“可能”“假设”“不能支持”等证据限定词必须完整保留。不得把 association 译成“证明”，不得把 mitigation 译成“阻止”。

## Translation Challenges

- LaTeX 结构：保留所有命令、公式、标签、引用键、图路径、表格列结构和百分号转义；只翻译自然语言参数。
- 中文排版：最终主稿沿用 `paper-Chinese/main.tex` 的 xeCJK 配置，但正文结构必须与当前 `paper/main.tex` 一致。
- 数字密集段落：逐项核对 N、百分比、区间、距离、角度、曝光标签和比较方向，不允许沿用旧中文稿数字。
- 指标术语：全文统一“字符恢复率”，不再使用“字符准确率”；exact match 统一为“完全匹配率”。
- 档位命名：`readability-priority` 统一为“可读性优先档”，`high-suppression` 统一为“高抑制档”；归档标识保留代码字体。
- Oracle：避免生硬使用“预言机”，首次写“网格最优选择（oracle）”，后文可写“最优选择”。
- 固定相位与亮度：准确翻译为显示器亮度设置和采集相位在整个采集过程中保持固定；同时保留物理显示亮度未做光度测量的区别。
- 用户研究：完整翻译协议和待填写占位，不得虚构参与者数据或结果。
- 浮动体：标题和表头翻译后可能显著变长，需在编译阶段检查是否溢出，必要时只做不改变含义的压缩。
- 图内文字：本任务不翻译嵌入式 PDF 图中的英文标签，最终需提醒用户。
