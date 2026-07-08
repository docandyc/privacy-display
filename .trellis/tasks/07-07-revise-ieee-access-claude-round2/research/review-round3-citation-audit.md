# 第三轮审稿引用核验

核验日期：2026-07-07。仅记录本轮审稿点名或因改写而直接影响的文献。

## Rainbow (`b_rainbow2018`)

- 上一轮独立证据审计已核验：Lin Yang、Wei Wang、Zeyu Wang、Qian Zhang，IEEE INFOCOM 2018，1061--1069，DOI `10.1109/INFOCOM.2018.8485881`。
- 本轮没有发现元数据冲突。
- 因 `IEEEtran.bst` v1.14 不处理独立 `doi` 字段，已改为 `note = {doi: ...}`。

## Lim (`b_lim2007`)

- 上一轮独立证据审计已核验：Johnny Lim，SOUPS 2007，147--148，DOI `10.1145/1280680.1280701`。
- 本轮没有发现元数据冲突。
- DOI 已由独立 `doi` 字段移入 `note`。

## Wang et al. (`b_wang2026`)

- arXiv `2603.04930` 给出作者 Xueyang Wang、Kewen Peng、Xin Yi、Hewu Li。
- 论文前置信息列出 CHI 2026（2026-04-13 至 2026-04-17，Barcelona）及 DOI `10.1145/3772318.3791848`。
- 当前 BibTeX 的作者、题名、年份与 DOI 一致，保留。
- 来源：<https://arxiv.org/abs/2603.04930>。

## Ultralytics YOLO26 (`b_yolo26`)

- 原条目把 Jocher/Qiu、GitHub 页面和 `arXiv:2509.25164` 混在一起；后者实际是 Sapkota 等人的二手架构评测，不是 Ultralytics 原始论文。
- 已改引 2026 年原始技术报告：Glenn Jocher、Jing Qiu、Mengyu Liu、Shuai Lyu、Fatih Cagatay Akyon、Muhammet Esat Kalfaoglu，*Ultralytics YOLO26: Unified Real-Time End-to-End Vision Models*，arXiv `2606.03748`，DOI `10.48550/arXiv.2606.03748`。
- 来源：<https://arxiv.org/abs/2606.03748>。

## 闪烁与 CFF (`b_davis2015`)

- Davis、Hsieh、Lee 的 Scientific Reports 论文题名、卷号、文章号与 DOI `10.1038/srep07861` 已核验。
- 该文并不支持把 CFF 写成普适的 `50--70 Hz` 固定阈值。文中均匀调制条件接近传统范围，但含高空间频率边缘时可在 500 Hz 以上观察到伪影。
- 因此正文已删除固定阈值断言，改写为 CFF 强依赖空间内容、亮度、对比度与眼动，并把 48/60 Hz 配置的可接受性留给计划中的用户研究。
- 来源：<https://www.nature.com/articles/srep07861>。

## 同步性

- `paper/refs.bib` 与 `paper-Chinese/refs.bib` 已同步修改，后续构建前后用字节级 `diff` 复核。
