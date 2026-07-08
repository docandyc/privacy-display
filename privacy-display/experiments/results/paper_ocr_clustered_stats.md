# Paper OCR Clustered Statistics

- Source: `experiments/results/real_capture_ocr.json`
- Engine reduction: best_of_engine_per_capture
- Matching rule: profile + attack + content_item + position + repeat_index
- Resampling unit: content_item
- Bootstrap: seed 20260612, 2000 resamples

## Paired Character-Recovery Contrasts

| Contrast | Matched units | Clusters | Estimate (pp) | 95% CI (pp) | Unmatched baseline/treatment | Duplicate extra rows |
|---|---:|---:|---:|---:|---:|---:|
| original short minus deployed short | 324 | 12 | 78.0 | [75.5, 80.3] | 0/0 | 0/135 |
| original short minus high suppression short | 324 | 12 | 89.1 | [85.0, 92.4] | 0/0 | 0/0 |
| mask only short minus deployed short | 324 | 12 | 3.0 | [-0.5, 6.5] | 0/0 | 0/135 |
| original short minus mask only short | 324 | 12 | 74.9 | [71.2, 78.4] | 0/0 | 0/0 |
| sensitivity excluding d0.5 a15 original short minus deployed short | 288 | 12 | 76.7 | [74.3, 79.2] | 0/0 | 0/120 |
| sensitivity excluding d0.5 a15 original short minus high suppression short | 288 | 12 | 88.9 | [85.5, 91.9] | 0/0 | 0/0 |
| sensitivity excluding d0.5 a15 mask only short minus deployed short | 288 | 12 | 3.4 | [-0.5, 7.1] | 0/0 | 0/120 |
| sensitivity excluding d0.5 a15 original short minus mask only short | 288 | 12 | 73.4 | [70.2, 76.8] | 0/0 | 0/0 |

## Descriptive Best-of-Engine Means

| Profile | Attack | N | Char (%) | Exact (%) | Sensitive token (%) |
|---|---|---:|---:|---:|---:|
| deployed | long | 324 | 60.9 | 36.4 | 88.4 |
| deployed | short | 459 | 15.1 | 0.4 | 21.1 |
| deployed | video:max_proj | 153 | 69.5 | 18.3 | 62.5 |
| deployed | video:single_best | 153 | 31.6 | 5.2 | 35.4 |
| deployed | video:temporal_mean | 153 | 71.1 | 42.5 | 69.3 |
| deployed | video:window_mean_best | 153 | 61.1 | 17.0 | 61.3 |
| glyph_0.00 | short | 135 | 14.9 | 1.5 | 11.8 |
| glyph_0.00 | video:max_proj | 45 | 60.5 | 13.3 | 50.4 |
| glyph_0.00 | video:single_best | 45 | 25.2 | 2.2 | 17.9 |
| glyph_0.00 | video:temporal_mean | 45 | 64.9 | 33.3 | 58.5 |
| glyph_0.00 | video:window_mean_best | 45 | 52.8 | 13.3 | 45.3 |
| glyph_0.12 | short | 135 | 12.7 | 0.0 | 12.4 |
| glyph_0.12 | video:max_proj | 45 | 60.8 | 11.1 | 44.1 |
| glyph_0.12 | video:single_best | 45 | 24.1 | 0.0 | 19.6 |
| glyph_0.12 | video:temporal_mean | 45 | 62.0 | 33.3 | 54.6 |
| glyph_0.12 | video:window_mean_best | 45 | 52.7 | 17.8 | 45.6 |
| glyph_0.22 | short | 135 | 12.8 | 1.5 | 12.3 |
| glyph_0.22 | video:max_proj | 45 | 58.5 | 6.7 | 44.1 |
| glyph_0.22 | video:single_best | 45 | 25.3 | 0.0 | 18.5 |
| glyph_0.22 | video:temporal_mean | 45 | 64.2 | 31.1 | 53.3 |
| glyph_0.22 | video:window_mean_best | 45 | 54.8 | 20.0 | 43.2 |
| high_suppression | long | 324 | 9.3 | 0.0 | 32.0 |
| high_suppression | short | 324 | 5.0 | 0.0 | 6.0 |
| high_suppression | video:max_proj | 108 | 16.4 | 0.0 | 27.7 |
| high_suppression | video:single_best | 108 | 5.5 | 0.0 | 4.6 |
| high_suppression | video:temporal_mean | 108 | 47.9 | 5.6 | 41.8 |
| high_suppression | video:window_mean_best | 108 | 18.6 | 0.9 | 23.1 |
| inversion_0.0 | long | 135 | 68.6 | 28.1 | 68.1 |
| inversion_0.0 | video:max_proj | 45 | 60.7 | 8.9 | 46.0 |
| inversion_0.0 | video:single_best | 45 | 20.5 | 0.0 | 13.3 |
| inversion_0.0 | video:temporal_mean | 45 | 72.7 | 46.7 | 58.3 |
| inversion_0.0 | video:window_mean_best | 45 | 53.1 | 20.0 | 50.0 |
| inversion_0.2 | long | 135 | 67.0 | 33.3 | 73.7 |
| inversion_0.2 | video:max_proj | 45 | 60.7 | 11.1 | 48.1 |
| inversion_0.2 | video:single_best | 45 | 24.2 | 6.7 | 19.7 |
| inversion_0.2 | video:temporal_mean | 45 | 69.8 | 48.9 | 59.6 |
| inversion_0.2 | video:window_mean_best | 45 | 52.8 | 13.3 | 47.5 |
| inversion_0.3 | long | 135 | 72.0 | 38.5 | 73.8 |
| inversion_0.3 | video:max_proj | 45 | 57.3 | 8.9 | 44.5 |
| inversion_0.3 | video:single_best | 45 | 27.9 | 2.2 | 21.6 |
| inversion_0.3 | video:temporal_mean | 45 | 64.3 | 28.9 | 58.8 |
| inversion_0.3 | video:window_mean_best | 45 | 52.5 | 22.2 | 46.3 |
| inversion_0.5 | long | 135 | 61.7 | 25.9 | 71.2 |
| inversion_0.5 | video:max_proj | 45 | 58.0 | 4.4 | 47.5 |
| inversion_0.5 | video:single_best | 45 | 24.7 | 6.7 | 21.3 |
| inversion_0.5 | video:temporal_mean | 45 | 66.4 | 40.0 | 58.7 |
| inversion_0.5 | video:window_mean_best | 45 | 55.3 | 20.0 | 49.9 |
| inversion_1.0 | long | 135 | 18.1 | 0.0 | 50.1 |
| inversion_1.0 | video:max_proj | 45 | 55.6 | 8.9 | 35.0 |
| inversion_1.0 | video:single_best | 45 | 49.9 | 33.3 | 34.7 |
| inversion_1.0 | video:temporal_mean | 45 | 28.4 | 0.0 | 30.6 |
| inversion_1.0 | video:window_mean_best | 45 | 51.0 | 17.8 | 40.7 |
| mask_noise | long | 324 | 68.0 | 39.8 | 87.7 |
| mask_noise | short | 324 | 25.6 | 2.8 | 31.5 |
| mask_noise | video:max_proj | 108 | 73.7 | 26.9 | 72.4 |
| mask_noise | video:single_best | 108 | 33.7 | 4.6 | 32.2 |
| mask_noise | video:temporal_mean | 108 | 79.2 | 49.1 | 76.9 |
| mask_noise | video:window_mean_best | 108 | 71.2 | 33.3 | 69.1 |
| mask_only | long | 324 | 67.2 | 35.5 | 86.2 |
| mask_only | short | 324 | 19.2 | 0.3 | 28.2 |
| mask_only | video:max_proj | 108 | 71.7 | 25.9 | 69.3 |
| mask_only | video:single_best | 108 | 33.6 | 5.6 | 35.0 |
| mask_only | video:temporal_mean | 108 | 79.0 | 48.1 | 77.0 |
| mask_only | video:window_mean_best | 108 | 66.8 | 29.6 | 65.9 |
| original | long | 324 | 47.3 | 18.8 | 87.7 |
| original | short | 324 | 94.1 | 65.7 | 90.2 |
| original | video:max_proj | 108 | 70.2 | 25.0 | 72.5 |
| original | video:single_best | 108 | 86.4 | 64.8 | 79.6 |
| original | video:temporal_mean | 108 | 79.9 | 61.1 | 78.5 |
| original | video:window_mean_best | 108 | 86.4 | 65.7 | 78.8 |
| stripe_0.00 | short | 135 | 10.3 | 1.5 | 9.6 |
| stripe_0.00 | video:max_proj | 45 | 63.3 | 20.0 | 53.1 |
| stripe_0.00 | video:single_best | 45 | 25.3 | 0.0 | 26.2 |
| stripe_0.00 | video:temporal_mean | 45 | 69.0 | 44.4 | 58.7 |
| stripe_0.00 | video:window_mean_best | 45 | 53.4 | 22.2 | 47.0 |
| stripe_0.10 | short | 135 | 14.3 | 0.0 | 14.4 |
| stripe_0.10 | video:max_proj | 45 | 62.7 | 11.1 | 51.9 |
| stripe_0.10 | video:single_best | 45 | 26.3 | 0.0 | 19.8 |
| stripe_0.10 | video:temporal_mean | 45 | 64.8 | 42.2 | 58.2 |
| stripe_0.10 | video:window_mean_best | 45 | 47.7 | 13.3 | 48.8 |
| stripe_0.18 | short | 135 | 10.5 | 0.0 | 9.4 |
| stripe_0.18 | video:max_proj | 45 | 59.8 | 4.4 | 50.8 |
| stripe_0.18 | video:single_best | 45 | 22.7 | 0.0 | 19.0 |
| stripe_0.18 | video:temporal_mean | 45 | 59.3 | 40.0 | 56.1 |
| stripe_0.18 | video:window_mean_best | 45 | 51.8 | 11.1 | 45.1 |
| stripe_0.30 | short | 135 | 11.7 | 0.0 | 10.2 |
| stripe_0.30 | video:max_proj | 45 | 60.5 | 8.9 | 44.8 |
| stripe_0.30 | video:single_best | 45 | 23.8 | 2.2 | 14.0 |
| stripe_0.30 | video:temporal_mean | 45 | 63.3 | 33.3 | 55.8 |
| stripe_0.30 | video:window_mean_best | 45 | 51.0 | 11.1 | 45.6 |
| strong | long | 324 | 61.6 | 39.8 | 87.7 |
| strong | short | 324 | 20.7 | 0.6 | 30.9 |
| strong | video:max_proj | 108 | 72.5 | 24.1 | 71.2 |
| strong | video:single_best | 108 | 31.1 | 5.6 | 35.5 |
| strong | video:temporal_mean | 108 | 78.6 | 50.9 | 76.3 |
| strong | video:window_mean_best | 108 | 68.1 | 25.9 | 66.5 |
