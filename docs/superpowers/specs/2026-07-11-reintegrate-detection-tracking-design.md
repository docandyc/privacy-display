# Reintegrate Detection and Tracking Experiments

## Objective

Restore the detection and tracking experiments from `/Users/andyhuang/Desktop/英文版初稿.pdf` to the current English IEEE Access manuscript. The restored material should occupy the same logical positions as in the initial draft and should include all real-capture and simulated detection/tracking values that appeared there.

## Manuscript Structure

After the user-experience section, the manuscript will contain a real-capture object detection and tracking subsection. It will include the 150-image COCO detection table, the 450-frame MOT17-09-FRCNN still-frame tracking table, the four-detector mAP50 figure, and the accompanying interpretation from the initial draft.

The software-simulation section will regain the detection and tracking simulation subsection. It will include the 8-image COCO detection table, the 5,316-frame MOT17 tracking table, and prose interpreting the results as pipeline diagnostics rather than dataset-level performance estimates.

## Evidence Framing

The numerical results will be restored with concise evidence framing. Real-capture detection comparisons differ in protection, exposure, resolution, and frame reduction. Real-capture tracking uses still-display captures rather than synchronized continuous video. The manuscript will state the in-project greedy association and evaluation method factually, without repetitive benchmark-disclaimer language or any implication that TrackEval produced the values.

The conventional-OCR evaluation remains the primary evidence. Detection and tracking remain cross-task stress tests and diagnostic boundary evidence.

## Consistency Changes

Statements in the introduction, contributions, experimental setup, evaluation overview, discussion, limitations, and conclusion that currently place detection/tracking exclusively in supplementary material will be revised. References to the restored tables, figure, metrics, sample sizes, and limitations will be kept internally consistent.

## Files and Assets

The principal source is `paper/main.tex`. Values and prose will be reconstructed from the initial-draft PDF and existing archived sources or Git history where available. The figure `paper/figures/real_detection_drop.pdf` will be reused. The standalone `paper/supplementary.tex` and generated `paper/supplementary.pdf` will be deleted after their content is restored to the main manuscript.

## Verification

The manuscript will be rebuilt through the repository's complete LaTeX workflow. Cross-references and citations must resolve, and the rendered pages containing restored tables and figures must be visually checked for clipping, overlap, excessive whitespace, and unreadable type.

## Out of Scope

This change does not rerun TrackEval, generate new data, edit the Chinese manuscript, or upgrade approximate tracking metrics to official benchmark status.
