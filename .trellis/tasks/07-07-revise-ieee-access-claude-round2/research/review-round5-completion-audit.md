# Round-5 completion audit (2026-07-07)

| Requirement | Authoritative evidence | Status |
|---|---|---|
| Verify YOLO26 | arXiv API returns `2606.03748v1`, correct title, date, and six authors; Ultralytics official docs cite the same report | Complete |
| Verify Wang CHI 2026 and Ray-Ban Meta support | Crossref returns DOI `10.1145/3772318.3791848`, CHI 2026, authors and pages; the paper introduction explicitly names Ray-Ban Meta Smart Glasses | Complete |
| Check four arXiv-only references | arXiv API confirms all four IDs; Deep-TEMPEST replaced by LADC 2024 DOI `10.1145/3697090.3697094`; Song, Shi, and Jiang remain CoRR-only in arXiv/DBLP | Complete |
| Correct 77.8% attribution and scope | English/Chinese abstract, introduction, contribution, and conclusion now identify Qwen3-VL, 0.5 m, high-suppression short exposure, pooled 12-item/N=36 exact match; content concentration is explicitly attributed to the separate character-recovery table | Complete |
| Sharpen practical contribution | Abstract, introduction, contribution, and conclusion identify silent/unattended single-frame conventional-OCR bulk collection as the useful niche and distinguish it from 67 ms video and VLM bypasses | Complete |
| Explain retained complementary noise | Method states that composite profiles were frozen before ablation; retention preserves correspondence with archived captures and is not claimed as a benefit; matched noise-off profiles are future work | Complete |
| Reduce over-hedging | Front-door sections now lead with the positive single-frame OCR result and consolidate limits into a separate boundary paragraph; redundant qualifiers were removed from contribution and conclusion | Complete |
| Move user study after attack chain | Extracted English PDF order is C VLM → D real detection/tracking → E simulation → F user study → VI discussion; Chinese PDF has the same order | Complete |
| Disambiguate repeated numbers | Evaluation setup states that 60.9% short-exposure P95 and 60.9% long-exposure mean are different statistics; 5.6% sensitivity character recovery and 5.6% video exact match are explicitly separated | Complete |
| DOI/key consistency | Added verified DOI notes for Backes, Raguram, Eiband, Kaleido, LiShield, Nguyen, and DeepLight; corrected DeepLight pages; renamed keys to `b_gu2024` and `b_jiang2025`; English/Chinese BibTeX files are byte-identical | Complete |
| Verify S600 hardware claim | Removed unsupported “Sony 1/2.55-inch” and unmeasured 10--16 ms readout estimate; cited EMEET's official S600 page for 8 MP/4K and 1080p/60 fps; row mixing is now a non-isolated hypothesis | Complete |
| Build and layout verification | Fresh `latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex` exits 0 for both papers (23/18 pages); final logs have no undefined citations/references or missing BibTeX entries; extracted PDFs have no citation placeholders; key pages and reference pages were visually inspected | Complete |

Detailed source evidence is in `review-round5-citation-hardware-audit.md`.
