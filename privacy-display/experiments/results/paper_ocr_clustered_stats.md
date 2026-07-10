# Paper OCR Clustered Statistics

- Source: `experiments/results/real_capture_ocr.json`
- Engine reduction: best_of_engine_per_capture
- Matching rule: profile + attack + content_item + position + repeat_index
- Resampling unit: content_item
- Bootstrap: seed 20260612, 2000 resamples

## Paired Character-Recovery Contrasts

| Contrast | Matched units | Clusters | Matched baseline (%) | Matched treatment (%) | Estimate (pp) | 95% CI (pp) | Unmatched baseline/treatment | Duplicate extra rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| original short minus deployed short | 324 | 12 | 94.1 | 16.2 | 78.0 | [75.5, 80.3] | 0/0 | 0/135 |
| original short minus high suppression short | 324 | 12 | 94.1 | 5.0 | 89.1 | [85.0, 92.4] | 0/0 | 0/0 |
| mask only short minus deployed short | 324 | 12 | 19.2 | 16.2 | 3.0 | [-0.5, 6.5] | 0/0 | 0/135 |
| original short minus mask only short | 324 | 12 | 94.1 | 19.2 | 74.9 | [71.2, 78.4] | 0/0 | 0/0 |
| sensitivity excluding d0.5 a15 original short minus deployed short | 288 | 12 | 94.5 | 17.8 | 76.7 | [74.3, 79.2] | 0/0 | 0/120 |
| sensitivity excluding d0.5 a15 original short minus high suppression short | 288 | 12 | 94.5 | 5.6 | 88.9 | [85.5, 91.9] | 0/0 | 0/0 |
| sensitivity excluding d0.5 a15 mask only short minus deployed short | 288 | 12 | 21.1 | 17.8 | 3.4 | [-0.5, 7.1] | 0/0 | 0/120 |
| sensitivity excluding d0.5 a15 original short minus mask only short | 288 | 12 | 94.5 | 21.1 | 73.4 | [70.2, 76.8] | 0/0 | 0/0 |

## Primary Matched Common-Setting Means

| Profile | Matched cells | Character recovery (%) | Exact match (%) | P99 character recovery (%) |
|---|---:|---:|---:|---:|
| original | 288 | 94.5 | 64.6 | 100.0 |
| deployed | 288 | 17.8 | 0.5 | 95.0 |
| high suppression | 288 | 5.6 | 0.0 | 22.6 |

The primary estimand excludes d0.5/a15 because it used a different logged UVC exposure setting. All profiles use the same duplicate-averaged matched keys.

## Descriptive Best-of-Engine Means

| Profile | Attack | N | Char (%) | Exact (%) |
|---|---|---:|---:|---:|
| deployed | long | 324 | 60.9 | 36.4 |
| deployed | short | 459 | 15.1 | 0.4 |
| deployed | video:max_proj | 153 | 69.5 | 18.3 |
| deployed | video:single_best | 153 | 31.6 | 5.2 |
| deployed | video:temporal_mean | 153 | 71.1 | 42.5 |
| deployed | video:window_mean_best | 153 | 61.1 | 17.0 |
| glyph_0.00 | short | 135 | 14.9 | 1.5 |
| glyph_0.00 | video:max_proj | 45 | 60.5 | 13.3 |
| glyph_0.00 | video:single_best | 45 | 25.2 | 2.2 |
| glyph_0.00 | video:temporal_mean | 45 | 64.9 | 33.3 |
| glyph_0.00 | video:window_mean_best | 45 | 52.8 | 13.3 |
| glyph_0.12 | short | 135 | 12.7 | 0.0 |
| glyph_0.12 | video:max_proj | 45 | 60.8 | 11.1 |
| glyph_0.12 | video:single_best | 45 | 24.1 | 0.0 |
| glyph_0.12 | video:temporal_mean | 45 | 62.0 | 33.3 |
| glyph_0.12 | video:window_mean_best | 45 | 52.7 | 17.8 |
| glyph_0.22 | short | 135 | 12.8 | 1.5 |
| glyph_0.22 | video:max_proj | 45 | 58.5 | 6.7 |
| glyph_0.22 | video:single_best | 45 | 25.3 | 0.0 |
| glyph_0.22 | video:temporal_mean | 45 | 64.2 | 31.1 |
| glyph_0.22 | video:window_mean_best | 45 | 54.8 | 20.0 |
| high_suppression | long | 324 | 9.3 | 0.0 |
| high_suppression | short | 324 | 5.0 | 0.0 |
| high_suppression | video:max_proj | 108 | 16.4 | 0.0 |
| high_suppression | video:single_best | 108 | 5.5 | 0.0 |
| high_suppression | video:temporal_mean | 108 | 47.9 | 5.6 |
| high_suppression | video:window_mean_best | 108 | 18.6 | 0.9 |
| inversion_0.0 | long | 135 | 68.6 | 28.1 |
| inversion_0.0 | video:max_proj | 45 | 60.7 | 8.9 |
| inversion_0.0 | video:single_best | 45 | 20.5 | 0.0 |
| inversion_0.0 | video:temporal_mean | 45 | 72.7 | 46.7 |
| inversion_0.0 | video:window_mean_best | 45 | 53.1 | 20.0 |
| inversion_0.2 | long | 135 | 67.0 | 33.3 |
| inversion_0.2 | video:max_proj | 45 | 60.7 | 11.1 |
| inversion_0.2 | video:single_best | 45 | 24.2 | 6.7 |
| inversion_0.2 | video:temporal_mean | 45 | 69.8 | 48.9 |
| inversion_0.2 | video:window_mean_best | 45 | 52.8 | 13.3 |
| inversion_0.3 | long | 135 | 72.0 | 38.5 |
| inversion_0.3 | video:max_proj | 45 | 57.3 | 8.9 |
| inversion_0.3 | video:single_best | 45 | 27.9 | 2.2 |
| inversion_0.3 | video:temporal_mean | 45 | 64.3 | 28.9 |
| inversion_0.3 | video:window_mean_best | 45 | 52.5 | 22.2 |
| inversion_0.5 | long | 135 | 61.7 | 25.9 |
| inversion_0.5 | video:max_proj | 45 | 58.0 | 4.4 |
| inversion_0.5 | video:single_best | 45 | 24.7 | 6.7 |
| inversion_0.5 | video:temporal_mean | 45 | 66.4 | 40.0 |
| inversion_0.5 | video:window_mean_best | 45 | 55.3 | 20.0 |
| inversion_1.0 | long | 135 | 18.1 | 0.0 |
| inversion_1.0 | video:max_proj | 45 | 55.6 | 8.9 |
| inversion_1.0 | video:single_best | 45 | 49.9 | 33.3 |
| inversion_1.0 | video:temporal_mean | 45 | 28.4 | 0.0 |
| inversion_1.0 | video:window_mean_best | 45 | 51.0 | 17.8 |
| mask_noise | long | 324 | 68.0 | 39.8 |
| mask_noise | short | 324 | 25.6 | 2.8 |
| mask_noise | video:max_proj | 108 | 73.7 | 26.9 |
| mask_noise | video:single_best | 108 | 33.7 | 4.6 |
| mask_noise | video:temporal_mean | 108 | 79.2 | 49.1 |
| mask_noise | video:window_mean_best | 108 | 71.2 | 33.3 |
| mask_only | long | 324 | 67.2 | 35.5 |
| mask_only | short | 324 | 19.2 | 0.3 |
| mask_only | video:max_proj | 108 | 71.7 | 25.9 |
| mask_only | video:single_best | 108 | 33.6 | 5.6 |
| mask_only | video:temporal_mean | 108 | 79.0 | 48.1 |
| mask_only | video:window_mean_best | 108 | 66.8 | 29.6 |
| original | long | 324 | 47.3 | 18.8 |
| original | short | 324 | 94.1 | 65.7 |
| original | video:max_proj | 108 | 70.2 | 25.0 |
| original | video:single_best | 108 | 86.4 | 64.8 |
| original | video:temporal_mean | 108 | 79.9 | 61.1 |
| original | video:window_mean_best | 108 | 86.4 | 65.7 |
| stripe_0.00 | short | 135 | 10.3 | 1.5 |
| stripe_0.00 | video:max_proj | 45 | 63.3 | 20.0 |
| stripe_0.00 | video:single_best | 45 | 25.3 | 0.0 |
| stripe_0.00 | video:temporal_mean | 45 | 69.0 | 44.4 |
| stripe_0.00 | video:window_mean_best | 45 | 53.4 | 22.2 |
| stripe_0.10 | short | 135 | 14.3 | 0.0 |
| stripe_0.10 | video:max_proj | 45 | 62.7 | 11.1 |
| stripe_0.10 | video:single_best | 45 | 26.3 | 0.0 |
| stripe_0.10 | video:temporal_mean | 45 | 64.8 | 42.2 |
| stripe_0.10 | video:window_mean_best | 45 | 47.7 | 13.3 |
| stripe_0.18 | short | 135 | 10.5 | 0.0 |
| stripe_0.18 | video:max_proj | 45 | 59.8 | 4.4 |
| stripe_0.18 | video:single_best | 45 | 22.7 | 0.0 |
| stripe_0.18 | video:temporal_mean | 45 | 59.3 | 40.0 |
| stripe_0.18 | video:window_mean_best | 45 | 51.8 | 11.1 |
| stripe_0.30 | short | 135 | 11.7 | 0.0 |
| stripe_0.30 | video:max_proj | 45 | 60.5 | 8.9 |
| stripe_0.30 | video:single_best | 45 | 23.8 | 2.2 |
| stripe_0.30 | video:temporal_mean | 45 | 63.3 | 33.3 |
| stripe_0.30 | video:window_mean_best | 45 | 51.0 | 11.1 |
| strong | long | 324 | 61.6 | 39.8 |
| strong | short | 324 | 20.7 | 0.6 |
| strong | video:max_proj | 108 | 72.5 | 24.1 |
| strong | video:single_best | 108 | 31.1 | 5.6 |
| strong | video:temporal_mean | 108 | 78.6 | 50.9 |
| strong | video:window_mean_best | 108 | 68.1 | 25.9 |
