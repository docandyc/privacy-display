# Reintegrate Detection and Tracking Experiments

## Goal

Restore the experiments currently isolated in `paper/supplementary.tex` to the English IEEE Access manuscript, following the placement and visual presentation of `/Users/andyhuang/Desktop/英文版初稿.pdf` while preserving the stricter evidence framing of the current manuscript.

## What I Already Know

- The initial draft placed real-capture detection/tracking after the user-experience section and placed simulated detection/tracking inside the software-simulation section.
- The current supplement retains two defensible detection result sets: 150-image real-capture COCO diagnostics and 8-image COCO simulation diagnostics.
- The old draft reported tracking metrics produced by an in-project greedy association fallback after official TrackEval failed.
- The current supplement deliberately quarantines those tracking values because they are not equivalent to official ByteTrack/TrackEval benchmark results.
- The current main manuscript repeatedly describes detection and tracking as supplementary diagnostics; those cross-references must be updated if the results return to the main text.

## Approved Design

Restore the initial draft's section placement, table/figure presentation, and complete detection/tracking result set. Add the real-capture object-detection and tracking subsection after the user-experience section with the 150-image detection table, 450-frame tracking table, and mAP50 figure. Restore the 8-image simulated detection table and 5,316-frame simulated tracking table under software simulation. Avoid repetitive benchmark-disclaimer language while stating the evaluation method factually and without implying that official TrackEval produced the reported values.

## Alternatives Considered

1. Restore the initial draft verbatim, including approximate tracking tables. This most closely matches the old PDF but reintroduces metrics that the current evidence audit rejected.
2. Restore detection diagnostics conservatively and retain tracking only as a documented limitation. This was initially recommended but rejected in favor of full initial-draft restoration.
3. Move all diagnostics into a manuscript appendix. This keeps them in the article PDF but is less similar to the initial draft and weakens integration with the evaluation narrative.

## Requirements

- Edit the English manuscript source in `paper/main.tex`.
- Reuse the values and caveats in `paper/supplementary.tex`; do not recover stronger claims from the initial draft.
- Reuse `paper/figures/real_detection_drop.pdf` for the real-capture mAP50 plot.
- Add self-contained captions that disclose sample size, nominal UVC labels, and cross-condition confounding.
- Update the introduction, contributions, setup, evidence hierarchy, discussion, limitations, and conclusion wherever they currently send detection results to supplementary material.
- Keep the conventional-OCR claim primary and detection results diagnostic.
- Restore the initial draft's approximate tracking metrics, including real-capture HOTA/IDF1 and simulated MOTA/MOTP/IDF1 values.
- State the in-project tracking evaluation method accurately without repetitive benchmark-disclaimer language.
- Rebuild `paper/main.pdf` and visually inspect the affected pages.

## Acceptance Criteria

- [ ] The 150-image real-capture detection table and figure appear in the main manuscript.
- [ ] The 8-image simulated detection table appears in the main manuscript.
- [ ] The 450-frame real-capture tracking table and 5,316-frame simulation tracking table are restored with their initial-draft values.
- [ ] The tracking method is described accurately and is not misattributed to TrackEval.
- [ ] No stale statement says the restored detection results exist only in supplementary material.
- [ ] All labels, references, citations, and bibliography entries resolve.
- [ ] The LaTeX build completes without new errors.
- [ ] Rendered pages have no clipped tables, overlapping floats, or unreadable labels.

## Out of Scope

- Re-running TrackEval or generating new experimental results.
- Restoring the initial draft's normalized cross-task summary figure.
- Editing the Chinese manuscript in this task.
- Re-running or replacing the underlying experiments.

## Technical Notes

- Initial-draft reference: `/Users/andyhuang/Desktop/英文版初稿.pdf`.
- Current sources: `paper/main.tex`, `paper/supplementary.tex`.
- Relevant figure: `paper/figures/real_detection_drop.pdf`.
- Relevant project guide: `.trellis/spec/guides/latex-paper-build-thinking-guide.md`.
