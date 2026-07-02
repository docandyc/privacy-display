# Citation Verification Report

Date: 2026-06-13

Scope: thesis references used to motivate screen-camera privacy, screen-side protection, screen-shooting watermarking, and strong camera attacks.

## CORRECTION (2026-07-02): Kaleido and LiShield are REAL, verified with DOIs

The 2026-06-13 conclusion below ("no canonical record found") was a **false negative**, most likely caused by sandboxed/restricted network access during that verification run. Both papers were re-verified on 2026-07-02 against ACM DL and Crossref:

| Work | Verified metadata | Canonical entry |
|---|---|---|
| Kaleido: You Can Watch It But Cannot Record It | Lan Zhang, Cheng Bo, Jiahui Hou, Xiang-Yang Li, Yu Wang, Kebin Liu, Yunhao Liu; MobiCom 2015, pp. 372-385; DOI 10.1145/2789168.2790106 (Crossref confirmed) | https://dl.acm.org/doi/10.1145/2789168.2790106 |
| LiShield: Automating Visual Privacy Protection Using a Smart LED | Shilin Zhu, Chi Zhang, Xinyu Zhang; MobiCom 2017; DOI 10.1145/3117811.3117820 | https://dl.acm.org/doi/10.1145/3117811.3117820 |

Actions taken (2026-07-02):
- `paper/main.tex` + `paper/refs.bib`: Kaleido added as `b_kaleido2015` in Related Work (closest prior work: multi-frame re-encoding so screen content is watchable but not recordable) with explicit differentiation; LiShield citation (`b_zhu2017`) confirmed correct and kept.
- Do **not** remove these two citations again based on the table below.
- The thesis (`thesis/chapters/ch1.tex` / `references.tex`), if still maintained, should restore these citations as well.

## Removed Unverified References (SUPERSEDED — see CORRECTION above)

| Original citation | Status | Action |
|---|---|---|
| `Kaleido: You can watch it but cannot record it`, claimed MobiCom 2015 | ~~No canonical record found~~ **Verified real on 2026-07-02** | ~~Removed~~ Re-added to IEEE Access manuscript |
| `LiShield: Automating visual privacy protection using a smart LED`, claimed MobiCom 2017 | ~~No canonical record found~~ **Verified real on 2026-07-02** | Kept in IEEE Access manuscript (`b_zhu2017`) |

## Verified Replacement Sources

| Work | Verified metadata | Canonical entry |
|---|---|---|
| ScreenAvoider | Mohammed Korayem, Robert Templeman, Dennis Chen, David Crandall, Apu Kapadia; 2014; arXiv:1412.0008 | https://arxiv.org/abs/1412.0008 |
| Eye-Shield | Brian Tang, Kang G. Shin; USENIX Security 2023; arXiv:2308.03868 | https://arxiv.org/abs/2308.03868 |
| Screen-shooting resilient document watermarking | Sulong Ge, Zhihua Xia, Yao Tong, Jian Weng, Jianan Liu; 2022; arXiv:2203.05198 | https://arxiv.org/abs/2203.05198 |
| DeepLight | Vu Tran, Gihan Jayatilaka, Ashwin Ashok, Archan Misra; IPSN 2021; DOI 10.1145/3412382.3458269 | https://arxiv.org/abs/2105.05092 |
| Revelio | Abbaas Alif Mohamed Nishar, Shrinivas Kudekar, Bernard Kintzing, Ashwin Ashok; ICASSP 2025; arXiv:2501.02349 | https://arxiv.org/abs/2501.02349 |
| BRIGHTNESS | Mordechai Guri, Dima Bykhovsky, Yuval Elovici; CMI 2019; DOI 10.1109/CMI48017.2019.8962137 | https://arxiv.org/abs/2002.01078 |

## Thesis Changes

- `thesis/chapters/ch1.tex`: rewrote related-work paragraph to cite verified screen privacy, shoulder-surfing, screen-shooting watermarking, screen-camera communication, and brightness covert-channel work.
- `thesis/chapters/references.tex`: replaced unverifiable reference items 3-5 and added verified items 18-20 for strong camera attack motivation.
- `IEEE_Access_literature_gap_analysis.md`: updated the citation-risk item and next-step priority list to reflect that the unverifiable citations have been removed.

## Remaining Citation Work Before IEEE Access Submission

- ~~Convert manual thesis references to BibTeX or BibLaTeX for the IEEE Access manuscript.~~ DONE 2026-07-02: `paper/refs.bib` (47 entries) + IEEEtran.bst; reference list now follows first-citation order automatically.
- Verify every final manuscript claim against publisher/arXiv/DOI pages before submission.
- For product/web references such as Ray-Ban Meta and Apple Vision Pro, capture access dates and stable URLs in the final bibliography.
