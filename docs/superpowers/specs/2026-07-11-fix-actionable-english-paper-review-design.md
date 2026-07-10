# Actionable English Paper Review Repair Design

## Objective

Revise the IEEE Access manuscript with an evidence-preserving pass that fixes currently actionable review findings without adding new experimental claims. The revision uses two author-confirmed acquisition facts: the display brightness setting was fixed, and acquisition phase was controlled and unchanged.

## Evidence Boundary

The manuscript may state that brightness setting and acquisition phase were held fixed during collection. All wording that describes phase as unknown, uncontrolled, or unmeasured will be removed rather than relocated. The fixed brightness setting must not be converted into a claim of measured photometric luminance or panel response, and the manuscript will not add a worst-phase robustness claim. The remaining mechanism boundary is narrower: the existing archive does not isolate temporal sparsity from duty-cycle luminance, overlays, display response, camera exposure, and ISP processing.

## Revision Scope

1. Correct claim-level citation errors and unsupported hardware statements.
2. Replace inaccurate brightness/phase uncertainty wording with the confirmed fixed-setting protocol.
3. Remove repeated boundary language from the Abstract, Introduction, Results, Discussion, Limitations, and Conclusion while retaining one precise statement where necessary.
4. Clarify statistical units by pairing 288 matched units with the 12 content clusters used for resampling.
5. Repair acronym definitions and terminology drift.
6. Recover reproducibility details from current source and archived configurations when they are directly verifiable.
7. Shorten captions and dense paragraphs without deleting necessary methodological disclosures.
8. Rebuild and inspect the main and supplementary PDFs from clean auxiliary state.

## Specific Wording Decisions

- Use “the display brightness setting and acquisition phase were held fixed throughout each collection” or a semantically equivalent statement.
- Do not use “phase was unknown,” “phase was uncontrolled,” “phase was not measured,” or “display brightness was unknown.”
- Do not replace the deleted phase boundary with a new “no phase sweep was performed” statement.
- Keep “photometric luminance was not recorded” only if needed to distinguish a fixed control setting from physical luminance measurement.
- Replace “VLM failures” with “protection failures under VLM attack” or equivalent.
- Use “character recovery” as the canonical OCR metric term.

## Validation

- Search the final sources for stale brightness/phase wording, citation errors, acronym violations, and terminology drift.
- Run focused analysis tests that support paper-facing values.
- Perform clean XeLaTeX/BibTeX builds of both documents.
- Check final logs for undefined citations/references and inspect rendered pages.
- Confirm the generated PDF text matches the final source and contains only intentionally retained author/user-study placeholders.

## Deferred Repairs

The follow-up roadmap will cover new randomized collections, cross-device replication, matched physical/static baselines, photometric timing and luminance measurements if a causal temporal claim is desired, stronger adaptive attackers, and a frozen public artifact release.
