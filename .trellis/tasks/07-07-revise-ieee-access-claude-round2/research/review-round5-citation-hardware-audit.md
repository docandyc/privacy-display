# Round-5 citation and hardware audit (2026-07-07)

## Scope and decision rule

The six references named by the reviewer were checked against primary metadata sources (arXiv, Crossref/ACM, the published paper, DBLP, or the conference proceedings). A preprint is upgraded only when an identifiable formal version with matching title/authors exists. Product specifications are retained only when supported by the manufacturer.

## Findings

### `b_yolo26`

- **Status:** real, not a hallucinated citation.
- **Evidence:** arXiv record `2606.03748`, *Ultralytics YOLO26: Unified Real-Time End-to-End Vision Models*, v1 dated 2 June 2026: <https://arxiv.org/abs/2606.03748>.
- **Independent official corroboration:** Ultralytics' model documentation cites the same paper and DOI: <https://docs.ultralytics.com/models/yolo26/>.
- **Decision:** retain the arXiv technical report and URL. The manuscript uses YOLO26x in an exploratory simulation, so the primary technical report is the most specific citation.

### `b_wang2026`

- **Status:** real CHI 2026 proceedings paper.
- **Crossref/ACM metadata:** DOI `10.1145/3772318.3791848`, 28 pages, Xueyang Wang, Kewen Peng, Xin Yi, and Hewu Li, *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems*: <https://doi.org/10.1145/3772318.3791848>.
- **Ray-Ban Meta support:** the paper's introduction explicitly states that Ray-Ban Meta Smart Glasses had surpassed two million units and discusses them as a camera-glasses product; the paper also uses Ray-Ban Meta in brand examples. The arXiv record is `2603.04930`: <https://arxiv.org/abs/2603.04930>.
- **Decision:** retain the citation and the manuscript's Ray-Ban Meta example.

### `b_fernandez2024` (Deep-TEMPEST)

- **Status:** arXiv `2407.09717` is real, but a formal version exists.
- **Formal version:** Santiago Fernández, Emilio Martínez, Gabriel Varela, Pablo Musé, and Federico Larroca, LADC 2024, pp. 91--100, DOI `10.1145/3697090.3697094`: <https://doi.org/10.1145/3697090.3697094>.
- **Proceedings copy:** <https://www.colibri.udelar.edu.uy/jspui/bitstream/20.500.12008/47587/1/FMVML24.pdf>.
- **Decision:** replace the arXiv-only BibTeX entry with the LADC proceedings version.

### `b_song2018`

- **Status:** arXiv `1802.05385` is real: <https://arxiv.org/abs/1802.05385>.
- **Publication check:** arXiv exposes no journal reference; DBLP still classifies it only as CoRR/informal publication: <https://dblp.org/rec/journals/corr/abs-1802-05385>.
- **Decision:** retain as an arXiv preprint and add a stable arXiv DOI/URL.

### `b_shi2023`

- **Status:** arXiv `2310.16809` is real: <https://arxiv.org/abs/2310.16809>.
- **Publication check:** arXiv exposes no journal reference; DBLP still lists only the CoRR record: <https://dblp.org/rec/journals/corr/abs-2310-16809>.
- **Decision:** retain as an arXiv preprint and add a stable arXiv DOI/URL.

### `b_li2025` / Jiang et al.

- **Status:** arXiv `2503.13962` is real: <https://arxiv.org/abs/2503.13962>.
- **Metadata:** first author is Chengze Jiang, followed by Zhuangzhuang Wang, Minjing Dong, and Jie Gui. DBLP still lists only the CoRR record: <https://dblp.org/rec/journals/corr/abs-2503-13962>.
- **Decision:** retain as an arXiv preprint, add the arXiv DOI/URL, and rename the local key to `b_jiang2025`.

## DOI consistency checks

The reviewer-named peer-reviewed entries have the following formal DOIs:

- Backes et al., *Tempest in a Teapot*: `10.1109/SP.2009.20`.
- Raguram et al., *iSpy*: `10.1145/2046707.2046769`.
- Eiband et al., *Understanding Shoulder Surfing in the Wild*: `10.1145/3025453.3025636`.
- Zhang et al., *Kaleido*: `10.1145/2789168.2790106`.
- Zhu et al., *Automating Visual Privacy Protection Using a Smart LED*: `10.1145/3117811.3117820` (conference version cited by the manuscript; the later CACM article has a different DOI).
- Nguyen et al., *High-rate Flicker-free Screen-Camera Communication*: `10.1109/INFOCOM.2016.7524512`.
- Tran et al., *DeepLight*: `10.1145/3412382.3458269`; the current page range should be 238--253, not 97--110.
- Tang and Shin's USENIX Security 2023 paper has no Crossref DOI; its USENIX proceedings citation and pages are retained.

`b_zhao2023` is Gu et al., TMLR 2024 and is renamed `b_gu2024`; its OpenReview URL remains the publication locator.

## EMEET S600 hardware claim

- The manufacturer's S600 page supports an 8-megapixel UHD 4K sensor and 1080p at 60 fps, but does **not** identify a Sony sensor: <https://emeet.com/en-eu/products/webcam-s600>.
- A manufacturer comparison page lists the S600 sensor size as 1/2.5 inch, while 1/2.55 inch is shown for the C960 4K; only the S800 is explicitly described as Sony: <https://emeet.co.jp/en/products/emeet-smartcam-s800>.
- **Decision:** remove “Sony 1/2.55-inch” from the manuscript. Also remove the unmeasured 10--16 ms readout-time estimate. Retain only the observed camera model, UVC operation, output mode, exposure metadata, and a cautious statement that rolling-shutter phase mixing was not directly measured.

## VLM statistic scope

Table `tab:real_vlm` proves that 77.8% is Qwen3-VL's exact-match rate for the 0.5 m, high-suppression, short-exposure cell pooled over all 36 captures from the 12-item content pool. Kimi-K2.6 and GLM-4.5V report 47.2% and 51.6% exact match, respectively. Table `tab:vlm_content` separately shows character recovery by content category. Therefore, “77.8% exact on large-font snippets” is not a valid description of the statistic. The correct combined wording must keep the two observations distinct.
