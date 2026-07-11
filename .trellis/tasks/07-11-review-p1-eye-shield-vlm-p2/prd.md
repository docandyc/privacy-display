# 投稿前 review 修复：P1 两项 + P2 七项

来源：2026-07-11 投稿前复审，用户确认修复以下清单（P0 两项不在本任务范围：webstudy 预勾选、调研数据回填清单）。

## 范围（全部在 paper/main.tex，另涉一处图脚本标注一致性与合同测试）

### P1
1. **Eye-Shield 描述失实**（main.tex ~L121）：现文称其"前置摄像头检测旁观者+局部模糊、依赖用户侧硬件"。实际（Tang & Shin, USENIX Sec '23）为显示侧实时渲染：近距离可读、远距离/斜角像素化模糊，纯软件全屏，无摄像头检测。改写为威胁轴对比：面向人眼远距阅读，不针对轴上短曝光相机+机器识别。
2. **VLM 低信息输入 char-acc 幻觉膨胀警示**：§V-C key finding 4（single-best 行 exact 0–1/12、char 12.7–29.8%）补一句：字符指标可能含语言先验驱动补全，prompt 禁猜只能部分抑制，exact-match 是保守读数。

### P2
1. L173 "commercial vision-language models" → "commercially hosted vision-language models"。
2. Kimi-K2.6 加脚注：提供商模型目录/文档 URL（须为真实可达 URL，不得编造深链）。
3. 蒙太奇 caption（L428）补 "(for the unprotected profile this equals the displayed source frame)"；若 `privacy-display/tests/test_fig_f3_montage.py` 锁定 caption token，须同步测试并跑绿。
4. Key finding 3（L414）补高抑制 exact=0% 目标达成（全池短曝光 0 例 exact）；表 3 "strict" → "descriptive" 统一措辞。
5. L88 "stores one image per target" → 改为清晰表述（每次采集事件存档一张图像供离线识别）。
6. L916 段内第二个 "without requiring the mask seed" 删除。
7. 消除正文 3 处轻微 overfull（9.3pt×2、1.6pt×1；37 处 505pt logo 页眉告警为模板固有，不处理）。

## 验收
- xelatex/latexmk 重编译成功，无 undefined references/citations；页数不异常变动。
- 正文 overfull 仅剩模板 logo 505pt 告警（或轻微残留有说明）。
- test_fig_f3_montage.py 通过（若其校验 caption）。
- 所有改写不引入新的事实声明；Eye-Shield 新描述与 USENIX '23 原文机制一致。
