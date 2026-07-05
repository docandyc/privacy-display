# Reviewer evidence audit (2026-07-05)

## Short-exposure motivation

- The S600 archive uses fixed calibrated exposures (0.49/3.91 ms for short/video frames and 31.25/125 ms for long exposure). It is not a smartphone auto-exposure experiment.
- The manuscript should therefore motivate short exposure as an opportunistic, low-interaction attacker tier (single brief snapshot without calibration or sustained aiming), not claim that all default smartphones select this shutter regime.
- Long exposure and video remain explicit higher attacker tiers; the paper must say a capable attacker can escalate and that the mechanism does not close this boundary.

## Profile count and inversion ablation

- The six main profiles are `original`, `mask_only`, `mask_noise`, `anti_ocr` (Strong), `deployed`, and legacy `vlm` (capture-hardened).
- Stripe/glyph/inversion labels are parameter sweeps rather than additional main profiles.
- `inversion_0.2` records use the Strong overlay (`stripe_alpha=0.10`, `glyph_alpha=0.12`) plus `inversion_alpha=0.2`, matching the deployed parameterization.
- The inversion ablation covers five items (`account_00`, `account_01`, `code_00`, `code_01`, `cet6_p1`) at all nine positions: long exposure N=135 and video temporal mean N=45.
- The deployed main row covers 12 items: long exposure N=324. Therefore, 67.0% versus 60.9% is a content/sample-design difference, not a repeated estimate from the same corpus.

## Missing per-engine Strong profile

Extracted from `privacy-display/experiments/results/real_capture_ocr.json`, filtering `ablation=anti_ocr`, `attack=short`:

| Engine | Char recovery | Exact match | N |
|---|---:|---:|---:|
| Surya | 6.1% | 0.6% | 324 |
| EasyOCR | 16.3% | 0.0% | 324 |
| Tesseract | 2.1% | 0.0% | 324 |

The reproducible fix is to add `strong -> anti_ocr` to `scripts/rebuild_real_capture_per_engine.py` and include Strong in the Figure S5 profile list/test.

## Missing 1.5 m window-mean-best row

Extracted from `real_capture_vlm_d1.5_a0.json` and the same-batch OCR records:

| Condition | OCR BoE exact/char | Qwen exact/char/N | Kimi exact/char/N | GLM exact/char/N |
|---|---|---|---|---|
| `video:window_mean_best` | 0.0/8.6 | 58.3/89.0/12 | 41.7/84.2/12 | 66.7/87.2/12 |

## Figure 1 wording

- Current final VSDX/PDF contains `Instantaneous sampling` and `≈ 50 ms`.
- Replace the former with `Short-exposure sampling` and remove the unsupported fixed time. The caption should explicitly state that the camera path is conceptual and not zero-duration sampling.

## FPI and deployment policy

- From the paper's own formula, base `n=4 @ 240 Hz` gives `0.75 * 625^{-1/2} * 1^2 = 0.030`.
- The 96.5% deployed long-exposure sensitive-token recovery must be surfaced as a deployment restriction: credentials/account fields cannot rely on deployed alone. Hardened or dense small-font rendering are mitigations with unresolved usability/VLM limitations, not complete protection.
