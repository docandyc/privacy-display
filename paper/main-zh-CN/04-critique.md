## Accuracy

- **Exact-match terminology drift**: VLM 段落的若干 `exact recovery` / `exact match` 被译为“完全恢复率”，应统一为论文指标“完全匹配率”；字段级 exact recovery 则应译为“字段完整恢复率”，以便与全文完全匹配指标区分。
- **Effect-size wording**: “did not produce a large observed reduction” 被译成“未产生显著下降”，容易误读为统计显著性检验；应改为“未产生较大的观测下降”。
- **Image clipping wording**: 长曝光反转段落中的 `clipping` 应明确为“饱和截断”，而不是可能被理解为空间裁剪的“裁剪现象”。
- **No numerical discrepancies found**: 三个分段的数字多重集、引用键、标签、图路径和 LaTeX 环境均与对应英文源范围一致。

## Native Voice

- **Real-capture inconsistency**: 同一概念交替使用“真实拍摄”和“真机拍摄”。项目既有中文术语为“真机拍摄”，应统一。
- **VLM probe inconsistency**: `probe` 在“探测实验”“边界探测”“探针”之间切换。建议统一为“VLM 探针”或“边界探针”，避免暗示完整验证实验。
- **Simulation-to-real wording**: “仿真--现实差距”略生硬且不够具体，应改为“仿真--实拍差距”。
- **Full-cycle wording**: `full-cycle` 在“完整循环”和“全周期”之间切换。统一为“全周期”更符合显示时序语境。
- **Inversion terminology**: “反色”和“反相”混用。图像操作统一为“反色帧/反色时隙”。
- **Minor density**: 摘要和部分 caption 很长，但属于源稿信息密度；优先在编译后根据实际溢出压缩，不预先删除信息。

## Notes & Adaptation

- 不需要在正文增加译者注；专业缩写已在首次出现时给出中文名称与英文缩写。
- 嵌入式结果图和原理图仍含英文标签，属于图片本地化问题，不应在本次文本翻译中擅自重绘。
- 作者、单位、基金、致谢和用户研究结果占位均正确保留。

## Summary

初译在结构、数字和证据强度上可靠，无关键内容缺失。需修复 3 类指标/证据措辞问题，并统一 5 组跨分段术语；之后进入编译驱动的排版精修。
