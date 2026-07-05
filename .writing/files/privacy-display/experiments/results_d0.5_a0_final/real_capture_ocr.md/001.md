# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 18.5% | 0.9% | 78.2% | 27.8% |
| anti_ocr|short | 108 | 3.2% | 0.0% | 2.4% | 0.0% |
| anti_ocr|video|max_proj | 36 | 45.4% | 8.3% | 62.8% | 55.6% |
| anti_ocr|video|single_best | 36 | 4.8% | 0.0% | 6.8% | 5.6% |
| anti_ocr|video|temporal_mean | 36 | 60.8% | 8.3% | 62.2% | 75.0% |
| anti_ocr|video|window_mean_best | 36 | 24.1% | 2.8% | 22.4% | 38.9% |
| deployed|long | 108 | 10.2% | 0.0% | 64.2% | 15.7% |
| deployed|short | 153 | 3.5% | 0.0% | 3.0% | 3.3% |
| deployed|video|max_proj | 51 | 29.2% | 2.0% | 31.3% | 39.2% |
| deployed|video|single_best | 51 | 6.9% | 0.0% | 6.1% | 11.8% |
| deployed|video|temporal_mean | 51 | 24.0% | 3.9% | 42.5% | 41.2% |
| deployed|video|window_mean_best | 51 | 23.2% | 0.0% | 23.1% | 37.3% |
| glyph_0.00|short | 45 | 2.5% | 0.0% | 0.3% | 0.0% |
| glyph_0.00|video|max_proj | 15 | 25.2% | 0.0% | 31.6% | 40.0% |
| glyph_0.00|video|single_best | 15 | 4.6% | 0.0% | 0.6% | 0.0% |
| glyph_0.00|video|temporal_mean | 15 | 25.4% | 0.0% | 53.4% | 40.0% |
| glyph_0.00|video|window_mean_best | 15 | 16.7% | 0.0% | 13.0% | 40.0% |
| glyph_0.12|short | 45 | 2.7% | 0.0% | 0.3% | 0.0% |
| glyph_0.12|video|max_proj | 15 | 25.6% | 0.0% | 32.6% | 33.3% |
| glyph_0.12|video|single_best | 15 | 7.2% | 0.0% | 2.5% | 6.7% |
| glyph_0.12|video|temporal_mean | 15 | 26.6% | 6.7% | 51.4% | 40.0% |
| glyph_0.12|video|window_mean_best | 15 | 12.5% | 0.0% | 5.6% | 26.7% |
| glyph_0.22|short | 45 | 2.3% | 0.0% | 0.3% | 0.0% |
| glyph_0.22|video|max_proj | 15 | 24.4% | 0.0% | 28.1% | 46.7% |
| glyph_0.22|video|single_best | 15 | 7.2% | 0.0% | 5.7% | 20.0% |
| glyph_0.22|video|temporal_mean | 15 | 24.5% | 0.0% | 46.1% | 33.3% |
| glyph_0.22|video|window_mean_best | 15 | 15.1% | 0.0% | 11.8% | 26.7% |
| inversion_0.0|long | 45 | 27.7% | 8.9% | 74.0% | 44.4% |
| inversion_0.0|video|max_proj | 15 | 30.0% | 6.7% | 34.0% | 40.0% |
| inversion_0.0|video|single_best | 15 | 3.4% | 0.0% | 0.8% | 6.7% |
| inversion_0.0|video|temporal_mean | 15 | 58.3% | 20.0% | 69.4% | 80.0% |
| inversion_0.0|video|window_mean_best | 15 | 13.4% | 0.0% | 15.8% | 20.0% |
| inversion_0.2|long | 45 | 13.5% | 0.0% | 68.9% | 24.4% |
| inversion_0.2|video|max_proj | 15 | 32.7% | 0.0% | 21.3% | 46.7% |
| inversion_0.2|video|single_best | 15 | 4.7% | 0.0% | 1.2% | 6.7% |
| inversion_0.2|video|temporal_mean | 15 | 29.9% | 0.0% | 53.3% | 40.0% |
| inversion_0.2|video|window_mean_best | 15 | 13.8% | 0.0% | 5.1% | 26.7% |
| inversion_0.3|long | 45 | 18.7% | 0.0% | 60.4% | 31.1% |
| inversion_0.3|video|max_proj | 15 | 26.8% | 0.0% | 21.5% | 40.0% |
| inversion_0.3|video|single_best | 15 | 7.5% | 0.0% | 0.8% | 20.0% |
| inversion_0.3|video|temporal_mean | 15 | 17.6% | 0.0% | 46.5% | 26.7% |
| inversion_0.3|video|window_mean_best | 15 | 10.7% | 0.0% | 7.3% | 20.0% |
| inversion_0.5|long | 45 | 8.8% | 0.0% | 33.7% | 20.0% |
| inversion_0.5|video|max_proj | 15 | 23.2% | 0.0% | 16.0% | 33.3% |
| inversion_0.5|video|single_best | 15 | 11.6% | 6.7% | 9.2% | 26.7% |
| inversion_0.5|video|temporal_mean | 15 | 24.1% | 0.0% | 40.6% | 33.3% |
| inversion_0.5|video|window_mean_best | 15 | 18.6% | 0.0% | 15.6% | 26.7% |
| inversion_1.0|long | 45 | 4.9% | 0.0% | 31.4% | 11.1% |
| inversion_1.0|video|max_proj | 15 | 31.7% | 6.7% | 37.6% | 40.0% |
| inversion_1.0|video|single_best | 15 | 9.9% | 0.0% | 6.3% | 13.3% |
| inversion_1.0|video|temporal_mean | 15 | 2.7% | 0.0% | 1.7% | 6.7% |
| inversion_1.0|video|window_mean_best | 15 | 10.8% | 0.0% | 9.1% | 13.3% |
| mask_noise|long | 108 | 19.5% | 2.8% | 83.8% | 27.8% |
| mask_noise|short | 108 | 3.6% | 0.0% | 2.8% | 0.0% |
| mask_noise|video|max_proj | 36 | 40.6% | 0.0% | 48.2% | 50.0% |
| mask_noise|video|single_best | 36 | 4.0% | 0.0% | 0.6% | 0.0% |
| mask_noise|video|temporal_mean | 36 | 66.1% | 16.7% | 72.6% | 83.3% |
| mask_noise|video|window_mean_best | 36 | 41.3% | 13.9% | 30.5% | 63.9% |
| mask_only|long | 108 | 17.7% | 2.8% | 80.5% | 26.9% |
| mask_only|short | 108 | 5.8% | 0.0% | 6.2% | 5.6% |
| mask_only|video|max_proj | 36 | 40.9% | 2.8% | 38.1% | 52.8% |
| mask_only|video|single_best | 36 | 3.9% | 0.0% | 1.3% | 2.8% |
| mask_only|video|temporal_mean | 36 | 70.0% | 16.7% | 72.4% | 86.1% |
| mask_only|video|window_mean_best | 36 | 35.8% | 5.6% | 26.5% | 55.6% |
| original|long | 108 | 28.5% | 17.6% | 79.6% | 35.2% |
| original|short | 108 | 66.1% | 32.4% | 87.2% | 75.0% |
| original|video|max_proj | 36 | 61.5% | 13.9% | 60.0% | 83.3% |
| original|video|single_best | 36 | 87.1% | 36.1% | 85.6% | 100.0% |
| original|video|temporal_mean | 36 | 86.2% | 38.9% | 85.6% | 97.2% |
| original|video|window_mean_best | 36 | 88.2% | 36.1% | 88.7% | 100.0% |
| stripe_0.00|short | 45 | 1.6% | 0.0% | 0.5% | 0.0% |
| stripe_0.00|video|max_proj | 15 | 34.4% | 0.0% | 29.1% | 46.7% |
| stripe_0.00|video|single_best | 15 | 5.5% | 0.0% | 5.4% | 13.3% |
| stripe_0.00|video|temporal_mean | 15 | 33.1% | 0.0% | 53.3% | 46.7% |
| stripe_0.00|video|window_mean_best | 15 | 13.9% | 0.0% | 2.1% | 26.7% |
| stripe_0.10|short | 45 | 2.5% | 0.0% | 1.0% | 0.0% |
| stripe_0.10|video|max_proj | 15 | 23.2% | 0.0% | 34.4% | 40.0% |
| stripe_0.10|video|single_best | 15 | 4.3% | 0.0% | 0.5% | 6.7% |
| stripe_0.10|video|temporal_mean | 15 | 26.7% | 6.7% | 47.9% | 40.0% |
| stripe_0.10|video|window_mean_best | 15 | 8.7% | 0.0% | 11.1% | 26.7% |
| stripe_0.18|short | 45 | 2.3% | 0.0% | 0.4% | 0.0% |
| stripe_0.18|video|max_proj | 15 | 23.3% | 0.0% | 23.5% | 33.3% |
| stripe_0.18|video|single_best | 15 | 1.3% | 0.0% | 0.0% | 0.0% |
| stripe_0.18|video|temporal_mean | 15 | 16.4% | 6.7% | 42.2% | 26.7% |
| stripe_0.18|video|window_mean_best | 15 | 12.4% | 0.0% | 7.5% | 26.7% |
| stripe_0.30|short | 45 | 1.5% | 0.0% | 0.3% | 0.0% |
| stripe_0.30|video|max_proj | 15 | 22.4% | 0.0% | 14.9% | 33.3% |
| stripe_0.30|video|single_best | 15 | 3.9% | 0.0% | 0.2% | 6.7% |
| stripe_0.30|video|temporal_mean | 15 | 25.6% | 0.0% | 40.3% | 40.0% |
| stripe_0.30|video|window_mean_best | 15 | 18.0% | 6.7% | 14.8% | 33.3% |
| capture_hardened|long | 108 | 0.9% | 0.0% | 16.6% | 0.0% |
| capture_hardened|short | 108 | 3.3% | 0.0% | 4.4% | 0.9% |
| capture_hardened|video|max_proj | 36 | 9.0% | 0.0% | 20.9% | 11.1% |
| capture_hardened|video|single_best | 36 | 2.5% | 0.0% | 0.8% | 2.8% |
| capture_hardened|video|temporal_mean | 36 | 21.3% | 2.8% | 21.8% | 41.7% |
| capture_hardened|video|window_mean_best | 36 | 12.5% | 0.0% | 13.7% | 22.2% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 49.1% | 2.8% | 90.4% | 66.7% |
| anti_ocr | short | 36 | 8.2% | 0.0% | 6.9% | 0.0% |
| anti_ocr | video:max_proj | 12 | 83.4% | 25.0% | 86.4% | 100.0% |
| anti_ocr | video:single_best | 12 | 11.2% | 0.0% | 11.1% | 16.7% |
| anti_ocr | video:temporal_mean | 12 | 88.4% | 25.0% | 88.8% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 55.7% | 8.3% | 45.5% | 91.7% |
| deployed | long | 36 | 25.1% | 0.0% | 86.4% | 33.3% |
| deployed | short | 51 | 9.4% | 0.0% | 8.6% | 9.8% |
| deployed | video:max_proj | 17 | 74.2% | 5.9% | 54.9% | 100.0% |
| deployed | video:single_best | 17 | 19.4% | 0.0% | 11.4% | 35.3% |
| deployed | video:temporal_mean | 17 | 51.3% | 11.8% | 74.2% | 76.5% |
| deployed | video:window_mean_best | 17 | 63.8% | 0.0% | 50.9% | 100.0% |
| glyph_0.00 | short | 15 | 6.6% | 0.0% | 0.7% | 0.0% |
| glyph_0.00 | video:max_proj | 5 | 56.9% | 0.0% | 66.6% | 100.0% |
| glyph_0.00 | video:single_best | 5 | 12.9% | 0.0% | 1.2% | 0.0% |
| glyph_0.00 | video:temporal_mean | 5 | 61.7% | 0.0% | 87.3% | 100.0% |
| glyph_0.00 | video:window_mean_best | 5 | 42.3% | 0.0% | 30.7% | 100.0% |
| glyph_0.12 | short | 15 | 6.9% | 0.0% | 0.6% | 0.0% |
| glyph_0.12 | video:max_proj | 5 | 61.3% | 0.0% | 46.6% | 100.0% |
| glyph_0.12 | video:single_best | 5 | 17.8% | 0.0% | 6.2% | 20.0% |
| glyph_0.12 | video:temporal_mean | 5 | 61.7% | 20.0% | 86.8% | 80.0% |
| glyph_0.12 | video:window_mean_best | 5 | 29.7% | 0.0% | 15.0% | 60.0% |
| glyph_0.22 | short | 15 | 6.2% | 0.0% | 0.7% | 0.0% |
| glyph_0.22 | video:max_proj | 5 | 54.1% | 0.0% | 47.6% | 100.0% |
| glyph_0.22 | video:single_best | 5 | 20.7% | 0.0% | 16.2% | 60.0% |
| glyph_0.22 | video:temporal_mean | 5 | 63.2% | 0.0% | 85.8% | 80.0% |
| glyph_0.22 | video:window_mean_best | 5 | 41.9% | 0.0% | 34.5% | 80.0% |
| inversion_0.0 | long | 15 | 67.1% | 26.7% | 90.3% | 93.3% |
| inversion_0.0 | video:max_proj | 5 | 71.5% | 20.0% | 49.0% | 100.0% |
| inversion_0.0 | video:single_best | 5 | 9.8% | 0.0% | 1.4% | 20.0% |
| inversion_0.0 | video:temporal_mean | 5 | 82.1% | 40.0% | 89.4% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 31.4% | 0.0% | 45.7% | 60.0% |
| inversion_0.2 | long | 15 | 28.6% | 0.0% | 90.3% | 46.7% |
| inversion_0.2 | video:max_proj | 5 | 61.0% | 0.0% | 53.0% | 100.0% |
| inversion_0.2 | video:single_best | 5 | 14.0% | 0.0% | 1.9% | 20.0% |
| inversion_0.2 | video:temporal_mean | 5 | 79.5% | 0.0% | 88.9% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 33.7% | 0.0% | 13.8% | 60.0% |
| inversion_0.3 | long | 15 | 42.2% | 0.0% | 79.5% | 60.0% |
| inversion_0.3 | video:max_proj | 5 | 63.5% | 0.0% | 39.2% | 100.0% |
| inversion_0.3 | video:single_best | 5 | 21.0% | 0.0% | 1.2% | 60.0% |
| inversion_0.3 | video:temporal_mean | 5 | 44.4% | 0.0% | 87.0% | 60.0% |
| inversion_0.3 | video:window_mean_best | 5 | 25.5% | 0.0% | 20.4% | 60.0% |
| inversion_0.5 | long | 15 | 14.0% | 0.0% | 58.4% | 20.0% |
| inversion_0.5 | video:max_proj | 5 | 65.2% | 0.0% | 38.3% | 100.0% |
| inversion_0.5 | video:single_best | 5 | 29.0% | 20.0% | 26.4% | 60.0% |
| inversion_0.5 | video:temporal_mean | 5 | 59.9% | 0.0% | 84.6% | 80.0% |
| inversion_0.5 | video:window_mean_best | 5 | 50.9% | 0.0% | 36.2% | 80.0% |
| inversion_1.0 | long | 15 | 14.2% | 0.0% | 58.4% | 33.3% |
| inversion_1.0 | video:max_proj | 5 | 52.7% | 20.0% | 65.7% | 80.0% |
| inversion_1.0 | video:single_best | 5 | 19.4% | 0.0% | 15.2% | 20.0% |
| inversion_1.0 | video:temporal_mean | 5 | 7.6% | 0.0% | 4.5% | 20.0% |
| inversion_1.0 | video:window_mean_best | 5 | 26.7% | 0.0% | 25.7% | 40.0% |
| mask_noise | long | 36 | 51.4% | 8.3% | 93.5% | 69.4% |
| mask_noise | short | 36 | 9.2% | 0.0% | 8.3% | 0.0% |
| mask_noise | video:max_proj | 12 | 80.9% | 0.0% | 77.4% | 100.0% |
| mask_noise | video:single_best | 12 | 9.5% | 0.0% | 1.3% | 0.0% |
| mask_noise | video:temporal_mean | 12 | 87.2% | 33.3% | 93.3% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 76.3% | 33.3% | 60.9% | 100.0% |
| mask_only | long | 36 | 46.0% | 8.3% | 93.0% | 61.1% |
| mask_only | short | 36 | 16.3% | 0.0% | 18.5% | 16.7% |
| mask_only | video:max_proj | 12 | 79.2% | 8.3% | 70.1% | 100.0% |
| mask_only | video:single_best | 12 | 9.0% | 0.0% | 2.9% | 8.3% |
| mask_only | video:temporal_mean | 12 | 88.2% | 33.3% | 93.3% | 100.0% |
| mask_only | video:window_mean_best | 12 | 66.6% | 16.7% | 55.5% | 91.7% |
| original | long | 36 | 81.6% | 52.8% | 96.5% | 94.4% |
| original | short | 36 | 92.4% | 58.3% | 96.5% | 100.0% |
| original | video:max_proj | 12 | 84.0% | 33.3% | 96.5% | 100.0% |
| original | video:single_best | 12 | 92.0% | 58.3% | 96.5% | 100.0% |
| original | video:temporal_mean | 12 | 93.0% | 66.7% | 96.5% | 100.0% |
| original | video:window_mean_best | 12 | 92.0% | 58.3% | 96.5% | 100.0% |
| stripe_0.00 | short | 15 | 3.8% | 0.0% | 1.0% | 0.0% |
| stripe_0.00 | video:max_proj | 5 | 69.9% | 0.0% | 68.7% | 100.0% |
| stripe_0.00 | video:single_best | 5 | 12.6% | 0.0% | 15.2% | 40.0% |
| stripe_0.00 | video:temporal_mean | 5 | 78.1% | 0.0% | 88.0% | 100.0% |
| stripe_0.00 | video:window_mean_best | 5 | 35.5% | 0.0% | 4.7% | 60.0% |
| stripe_0.10 | short | 15 | 6.4% | 0.0% | 2.7% | 0.0% |
| stripe_0.10 | video:max_proj | 5 | 57.4% | 0.0% | 64.2% | 100.0% |
| stripe_0.10 | video:single_best | 5 | 11.8% | 0.0% | 1.2% | 20.0% |
| stripe_0.10 | video:temporal_mean | 5 | 69.3% | 20.0% | 76.8% | 100.0% |
| stripe_0.10 | video:window_mean_best | 5 | 21.5% | 0.0% | 24.7% | 60.0% |
| stripe_0.18 | short | 15 | 5.5% | 0.0% | 0.8% | 0.0% |
| stripe_0.18 | video:max_proj | 5 | 62.6% | 0.0% | 41.8% | 100.0% |
| stripe_0.18 | video:single_best | 5 | 3.8% | 0.0% | 0.0% | 0.0% |
| stripe_0.18 | video:temporal_mean | 5 | 41.5% | 20.0% | 80.8% | 60.0% |
| stripe_0.18 | video:window_mean_best | 5 | 34.4% | 0.0% | 15.2% | 80.0% |
| stripe_0.30 | short | 15 | 4.3% | 0.0% | 0.8% | 0.0% |
| stripe_0.30 | video:max_proj | 5 | 59.8% | 0.0% | 28.8% | 100.0% |
| stripe_0.30 | video:single_best | 5 | 11.6% | 0.0% | 0.5% | 20.0% |
| stripe_0.30 | video:temporal_mean | 5 | 66.8% | 0.0% | 84.2% | 100.0% |
| stripe_0.30 | video:window_mean_best | 5 | 44.5% | 20.0% | 43.3% | 80.0% |
| capture_hardened | long | 36 | 2.1% | 0.0% | 49.3% | 0.0% |
| capture_hardened | short | 36 | 8.4% | 0.0% | 12.6% | 2.8% |
| capture_hardened | video:max_proj | 12 | 23.7% | 0.0% | 55.1% | 33.3% |
| capture_hardened | video:single_best | 12 | 6.3% | 0.0% | 1.9% | 8.3% |
| capture_hardened | video:temporal_mean | 12 | 50.7% | 8.3% | 58.2% | 91.7% |
| capture_hardened | video:window_mean_best | 12 | 32.6% | 0.0% | 40.8% | 66.7% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | 32.5% | 50.0% | 81.6% | 52.8% |
| anti_ocr | short | 84.2% | 58.3% | 92.4% | 58.3% |
| anti_ocr | video:max_proj | 0.6% | 8.3% | 84.0% | 33.3% |
| anti_ocr | video:single_best | 80.9% | 58.3% | 92.0% | 58.3% |
| anti_ocr | video:temporal_mean | 4.7% | 41.7% | 93.0% | 66.7% |
| anti_ocr | video:window_mean_best | 36.4% | 50.0% | 92.0% | 58.3% |
| deployed | long | 56.6% | 52.8% | 81.6% | 52.8% |
| deployed | short | 83.0% | 58.3% | 92.4% | 58.3% |
| deployed | video:max_proj | 9.7% | 27.5% | 84.0% | 33.3% |
| deployed | video:single_best | 72.6% | 58.3% | 92.0% | 58.3% |
| deployed | video:temporal_mean | 41.7% | 54.9% | 93.0% | 66.7% |
| deployed | video:window_mean_best | 28.3% | 58.3% | 92.0% | 58.3% |
| glyph_0.00 | short | 85.8% | 58.3% | 92.4% | 58.3% |
| glyph_0.00 | video:max_proj | 27.1% | 33.3% | 84.0% | 33.3% |
| glyph_0.00 | video:single_best | 79.2% | 58.3% | 92.0% | 58.3% |
| glyph_0.00 | video:temporal_mean | 31.3% | 66.7% | 93.0% | 66.7% |
| glyph_0.00 | video:window_mean_best | 49.8% | 58.3% | 92.0% | 58.3% |
| glyph_0.12 | short | 85.5% | 58.3% | 92.4% | 58.3% |
| glyph_0.12 | video:max_proj | 22.7% | 33.3% | 84.0% | 33.3% |
| glyph_0.12 | video:single_best | 74.2% | 58.3% | 92.0% | 58.3% |
| glyph_0.12 | video:temporal_mean | 31.3% | 46.7% | 93.0% | 66.7% |
| glyph_0.12 | video:window_mean_best | 62.3% | 58.3% | 92.0% | 58.3% |
| glyph_0.22 | short | 86.1% | 58.3% | 92.4% | 58.3% |
| glyph_0.22 | video:max_proj | 29.8% | 33.3% | 84.0% | 33.3% |
| glyph_0.22 | video:single_best | 71.3% | 58.3% | 92.0% | 58.3% |
| glyph_0.22 | video:temporal_mean | 29.8% | 66.7% | 93.0% | 66.7% |
| glyph_0.22 | video:window_mean_best | 50.2% | 58.3% | 92.0% | 58.3% |
| inversion_0.0 | long | 14.5% | 26.1% | 81.6% | 52.8% |
| inversion_0.0 | video:max_proj | 12.5% | 13.3% | 84.0% | 33.3% |
| inversion_0.0 | video:single_best | 82.2% | 58.3% | 92.0% | 58.3% |
| inversion_0.0 | video:temporal_mean | 11.0% | 26.7% | 93.0% | 66.7% |
| inversion_0.0 | video:window_mean_best | 60.7% | 58.3% | 92.0% | 58.3% |
| inversion_0.2 | long | 53.1% | 52.8% | 81.6% | 52.8% |
| inversion_0.2 | video:max_proj | 22.9% | 33.3% | 84.0% | 33.3% |
| inversion_0.2 | video:single_best | 78.0% | 58.3% | 92.0% | 58.3% |
| inversion_0.2 | video:temporal_mean | 13.6% | 66.7% | 93.0% | 66.7% |
| inversion_0.2 | video:window_mean_best | 58.3% | 58.3% | 92.0% | 58.3% |
| inversion_0.3 | long | 39.4% | 52.8% | 81.6% | 52.8% |
| inversion_0.3 | video:max_proj | 20.5% | 33.3% | 84.0% | 33.3% |
| inversion_0.3 | video:single_best | 71.1% | 58.3% | 92.0% | 58.3% |
| inversion_0.3 | video:temporal_mean | 48.7% | 66.7% | 93.0% | 66.7% |
| inversion_0.3 | video:window_mean_best | 66.5% | 58.3% | 92.0% | 58.3% |
| inversion_0.5 | long | 67.7% | 52.8% | 81.6% | 52.8% |
| inversion_0.5 | video:max_proj | 18.8% | 33.3% | 84.0% | 33.3% |
| inversion_0.5 | video:single_best | 63.1% | 38.3% | 92.0% | 58.3% |
| inversion_0.5 | video:temporal_mean | 33.2% | 66.7% | 93.0% | 66.7% |
| inversion_0.5 | video:window_mean_best | 41.1% | 58.3% | 92.0% | 58.3% |
| inversion_1.0 | long | 67.5% | 52.8% | 81.6% | 52.8% |
| inversion_1.0 | video:max_proj | 31.3% | 13.3% | 84.0% | 33.3% |
| inversion_1.0 | video:single_best | 72.7% | 58.3% | 92.0% | 58.3% |
| inversion_1.0 | video:temporal_mean | 85.4% | 66.7% | 93.0% | 66.7% |
| inversion_1.0 | video:window_mean_best | 65.4% | 58.3% | 92.0% | 58.3% |
| mask_noise | long | 30.2% | 44.4% | 81.6% | 52.8% |
| mask_noise | short | 83.2% | 58.3% | 92.4% | 58.3% |
| mask_noise | video:max_proj | 3.1% | 33.3% | 84.0% | 33.3% |
| mask_noise | video:single_best | 82.5% | 58.3% | 92.0% | 58.3% |
| mask_noise | video:temporal_mean | 5.8% | 33.3% | 93.0% | 66.7% |
| mask_noise | video:window_mean_best | 15.8% | 25.0% | 92.0% | 58.3% |
| mask_only | long | 35.6% | 44.4% | 81.6% | 52.8% |
| mask_only | short | 76.1% | 58.3% | 92.4% | 58.3% |
| mask_only | video:max_proj | 4.8% | 25.0% | 84.0% | 33.3% |
| mask_only | video:single_best | 83.0% | 58.3% | 92.0% | 58.3% |
| mask_only | video:temporal_mean | 4.8% | 33.3% | 93.0% | 66.7% |
| mask_only | video:window_mean_best | 25.5% | 41.7% | 92.0% | 58.3% |
| original | long | 0.0% | 0.0% | 81.6% | 52.8% |
| original | short | 0.0% | 0.0% | 92.4% | 58.3% |
| original | video:max_proj | 0.0% | 0.0% | 84.0% | 33.3% |
| original | video:single_best | 0.0% | 0.0% | 92.0% | 58.3% |
| original | video:temporal_mean | 0.0% | 0.0% | 93.0% | 66.7% |
| original | video:window_mean_best | 0.0% | 0.0% | 92.0% | 58.3% |
| stripe_0.00 | short | 88.6% | 58.3% | 92.4% | 58.3% |
| stripe_0.00 | video:max_proj | 14.1% | 33.3% | 84.0% | 33.3% |
| stripe_0.00 | video:single_best | 79.5% | 58.3% | 92.0% | 58.3% |
| stripe_0.00 | video:temporal_mean | 14.9% | 66.7% | 93.0% | 66.7% |
| stripe_0.00 | video:window_mean_best | 56.6% | 58.3% | 92.0% | 58.3% |
| stripe_0.10 | short | 85.9% | 58.3% | 92.4% | 58.3% |
| stripe_0.10 | video:max_proj | 26.6% | 33.3% | 84.0% | 33.3% |
| stripe_0.10 | video:single_best | 80.3% | 58.3% | 92.0% | 58.3% |
| stripe_0.10 | video:temporal_mean | 23.8% | 46.7% | 93.0% | 66.7% |
| stripe_0.10 | video:window_mean_best | 70.5% | 58.3% | 92.0% | 58.3% |
| stripe_0.18 | short | 86.9% | 58.3% | 92.4% | 58.3% |
| stripe_0.18 | video:max_proj | 21.4% | 33.3% | 84.0% | 33.3% |
| stripe_0.18 | video:single_best | 88.3% | 58.3% | 92.0% | 58.3% |
| stripe_0.18 | video:temporal_mean | 51.5% | 46.7% | 93.0% | 66.7% |
| stripe_0.18 | video:window_mean_best | 57.7% | 58.3% | 92.0% | 58.3% |
| stripe_0.30 | short | 88.1% | 58.3% | 92.4% | 58.3% |
| stripe_0.30 | video:max_proj | 24.1% | 33.3% | 84.0% | 33.3% |
| stripe_0.30 | video:single_best | 80.4% | 58.3% | 92.0% | 58.3% |
| stripe_0.30 | video:temporal_mean | 26.3% | 66.7% | 93.0% | 66.7% |
| stripe_0.30 | video:window_mean_best | 47.5% | 38.3% | 92.0% | 58.3% |
| capture_hardened | long | 79.6% | 52.8% | 81.6% | 52.8% |
| capture_hardened | short | 84.0% | 58.3% | 92.4% | 58.3% |
| capture_hardened | video:max_proj | 60.2% | 33.3% | 84.0% | 33.3% |
| capture_hardened | video:single_best | 85.8% | 58.3% | 92.0% | 58.3% |
| capture_hardened | video:temporal_mean | 42.4% | 58.3% | 93.0% | 66.7% |
| capture_hardened | video:window_mean_best | 59.5% | 58.3% | 92.0% | 58.3% |
