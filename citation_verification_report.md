# Citation Verification Report

Date: 2026-06-13

Scope: thesis references used to motivate screen-camera privacy, screen-side protection, screen-shooting watermarking, and strong camera attacks.

## Removed Unverified References

| Original citation | Status | Action |
|---|---|---|
| `Kaleido: You can watch it but cannot record it`, claimed MobiCom 2015 | No canonical record found via public search, arXiv, ACM-style query, or title search | Removed from thesis references and related-work prose |
| `LiShield: Automating visual privacy protection using a smart LED`, claimed MobiCom 2017 | No canonical record found via public search, arXiv, ACM-style query, or title search | Removed from thesis references and related-work prose |

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

- Convert manual thesis references to BibTeX or BibLaTeX for the IEEE Access manuscript.
- Verify every final manuscript claim against publisher/arXiv/DOI pages before submission.
- For product/web references such as Ray-Ban Meta and Apple Vision Pro, capture access dates and stable URLs in the final bibliography.
