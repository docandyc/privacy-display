# Fix English paper final review issues

## Goal

Revise the English IEEE Access manuscript to address the final pre-submission review issues identified by the user, while preserving the paper's bounded claim: a narrow single-UVC, calibrated short-exposure, conventional-OCR operating window.

## Requirements

- Compress the abstract to the IEEE-friendly 220--240 word range.
- Keep the abstract focused on problem, method, main result, and one concise boundary statement.
- Reframe the contribution and conclusion language so the positive finding is clear before the boundary findings.
- Avoid making VLM recovery a main contribution in the Abstract and Contributions; keep it positioned as a boundary probe.
- Reword content-cluster intervals as sensitivity/resampling intervals rather than strong population inference.
- Clean the supplementary DOI placeholder from `10.1109/ACCESS.XXXX.DOI`.
- Ensure the final English manuscript PDF has no SimSun residue or unembedded figure fonts.

## Acceptance Criteria

- [x] `paper/main.tex` abstract is 220--240 words by a reasonable plain-text count.
- [x] Abstract still includes the central OCR numbers and a concise limitation/boundary statement.
- [x] The contribution list separates primary positive evidence from boundary evidence.
- [x] The line-339 uncertainty wording and corresponding contribution/conclusion wording use `content-cluster resampling interval` or equivalent.
- [x] Abstract and Contributions do not foreground the exact `Qwen3-VL recovered 28/36` number.
- [x] `paper/supplementary.tex` no longer contains `10.1109/ACCESS.XXXX.DOI`.
- [x] `paper/main.pdf` contains no SimSun fonts and no font with `emb=no`.
- [x] The paper and supplementary material compile successfully.

## Out of Scope

- Filling user-study data, author information, funding, acknowledgment, or final DOI metadata.
- Changing experiment results or regenerating figures.
- Full citation audit beyond preserving existing references.

## Technical Notes

- Main manuscript: `paper/main.tex`
- Supplementary manuscript: `paper/supplementary.tex`
- Existing user-study and author placeholders are intentionally left for later completion unless directly related to the requested fixes.
