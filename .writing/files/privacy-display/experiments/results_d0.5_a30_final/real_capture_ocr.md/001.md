# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 20.8% | 14.8% | 89.7% | 25.0% |
| anti_ocr|short | 108 | 4.0% | 0.0% | 2.9% | 3.7% |
| anti_ocr|video|max_proj | 36 | 55.4% | 19.4% | 76.6% | 66.7% |
| anti_ocr|video|single_best | 36 | 3.8% | 0.0% | 2.3% | 0.0% |
| anti_ocr|video|temporal_mean | 36 | 48.5% | 8.3% | 65.1% | 61.1% |
| anti_ocr|video|window_mean_best | 36 | 29.8% | 0.0% | 32.6% | 50.0% |
| deployed|long | 108 | 21.3% | 6.5% | 82.6% | 26.9% |
| deployed|short | 153 | 2.7% | 0.0% | 1.2% | 1.3% |
| deployed|video|max_proj | 51 | 53.3% | 9.8% | 74.6% | 66.7% |
| deployed|video|single_best | 51 | 5.0% | 0.0% | 2.8% | 2.0% |
| deployed|video|temporal_mean | 51 | 44.2% | 5.9% | 63.7% | 64.7% |
| deployed|video|window_mean_best | 51 | 11.8% | 0.0% | 21.8% | 23.5% |
| glyph_0.00|short | 45 | 2.2% | 0.0% | 0.3% | 0.0% |
| glyph_0.00|video|max_proj | 15 | 49.3% | 0.0% | 68.2% | 66.7% |
| glyph_0.00|video|single_best | 15 | 3.6% | 0.0% | 0.3% | 0.0% |
| glyph_0.00|video|temporal_mean | 15 | 32.7% | 0.0% | 60.1% | 46.7% |
| glyph_0.00|video|window_mean_best | 15 | 14.2% | 0.0% | 28.2% | 33.3% |
| glyph_0.12|short | 45 | 3.3% | 0.0% | 0.7% | 0.0% |
| glyph_0.12|video|max_proj | 15 | 49.0% | 13.3% | 65.0% | 66.7% |
| glyph_0.12|video|single_best | 15 | 3.6% | 0.0% | 0.3% | 0.0% |
| glyph_0.12|video|temporal_mean | 15 | 41.2% | 6.7% | 49.1% | 66.7% |
| glyph_0.12|video|window_mean_best | 15 | 20.0% | 0.0% | 34.4% | 33.3% |
| glyph_0.22|short | 45 | 2.5% | 0.0% | 0.2% | 2.2% |
| glyph_0.22|video|max_proj | 15 | 47.6% | 0.0% | 63.0% | 66.7% |
| glyph_0.22|video|single_best | 15 | 5.0% | 0.0% | 2.9% | 0.0% |
| glyph_0.22|video|temporal_mean | 15 | 43.8% | 6.7% | 53.4% | 66.7% |
| glyph_0.22|video|window_mean_best | 15 | 24.3% | 0.0% | 30.5% | 53.3% |
| inversion_0.0|long | 45 | 25.3% | 2.2% | 65.2% | 33.3% |
| inversion_0.0|video|max_proj | 15 | 55.2% | 6.7% | 64.3% | 73.3% |
| inversion_0.0|video|single_best | 15 | 5.6% | 0.0% | 0.4% | 6.7% |
| inversion_0.0|video|temporal_mean | 15 | 44.7% | 0.0% | 64.4% | 66.7% |
| inversion_0.0|video|window_mean_best | 15 | 21.0% | 0.0% | 38.1% | 40.0% |
| inversion_0.2|long | 45 | 25.4% | 4.4% | 78.1% | 35.6% |
| inversion_0.2|video|max_proj | 15 | 48.5% | 6.7% | 65.7% | 66.7% |
| inversion_0.2|video|single_best | 15 | 3.8% | 0.0% | 1.4% | 0.0% |
| inversion_0.2|video|temporal_mean | 15 | 34.3% | 6.7% | 48.4% | 60.0% |
| inversion_0.2|video|window_mean_best | 15 | 21.2% | 0.0% | 19.2% | 46.7% |
| inversion_0.3|long | 45 | 33.9% | 15.6% | 81.4% | 46.7% |
| inversion_0.3|video|max_proj | 15 | 39.9% | 6.7% | 63.2% | 60.0% |
| inversion_0.3|video|single_best | 15 | 3.6% | 0.0% | 1.6% | 0.0% |
| inversion_0.3|video|temporal_mean | 15 | 39.6% | 0.0% | 58.0% | 60.0% |
| inversion_0.3|video|window_mean_best | 15 | 24.4% | 0.0% | 28.8% | 46.7% |
| inversion_0.5|long | 45 | 22.5% | 4.4% | 69.6% | 33.3% |
| inversion_0.5|video|max_proj | 15 | 46.4% | 0.0% | 64.3% | 66.7% |
| inversion_0.5|video|single_best | 15 | 5.3% | 0.0% | 4.5% | 0.0% |
| inversion_0.5|video|temporal_mean | 15 | 42.6% | 6.7% | 68.0% | 60.0% |
| inversion_0.5|video|window_mean_best | 15 | 18.9% | 0.0% | 37.2% | 33.3% |
| inversion_1.0|long | 45 | 3.8% | 0.0% | 40.6% | 6.7% |
| inversion_1.0|video|max_proj | 15 | 39.6% | 0.0% | 30.8% | 53.3% |
| inversion_1.0|video|single_best | 15 | 37.1% | 13.3% | 27.8% | 53.3% |
| inversion_1.0|video|temporal_mean | 15 | 15.2% | 0.0% | 22.0% | 26.7% |
| inversion_1.0|video|window_mean_best | 15 | 25.1% | 0.0% | 15.9% | 33.3% |
| mask_noise|long | 108 | 17.4% | 6.5% | 82.2% | 22.2% |
| mask_noise|short | 108 | 4.4% | 0.0% | 2.5% | 3.7% |
| mask_noise|video|max_proj | 36 | 50.2% | 5.6% | 77.0% | 61.1% |
| mask_noise|video|single_best | 36 | 5.7% | 0.0% | 1.3% | 5.6% |
| mask_noise|video|temporal_mean | 36 | 51.3% | 5.6% | 71.2% | 66.7% |
| mask_noise|video|window_mean_best | 36 | 35.0% | 2.8% | 47.0% | 52.8% |
| mask_only|long | 108 | 24.5% | 9.3% | 89.8% | 28.7% |
| mask_only|short | 108 | 4.0% | 0.0% | 4.4% | 5.6% |
| mask_only|video|max_proj | 36 | 50.0% | 19.4% | 71.8% | 55.6% |
| mask_only|video|single_best | 36 | 4.4% | 0.0% | 0.1% | 2.8% |
| mask_only|video|temporal_mean | 36 | 48.8% | 8.3% | 71.5% | 61.1% |
| mask_only|video|window_mean_best | 36 | 20.2% | 2.8% | 22.6% | 30.6% |
| original|long | 108 | 27.2% | 13.0% | 82.1% | 31.5% |
| original|short | 108 | 70.5% | 28.7% | 90.8% | 78.7% |
| original|video|max_proj | 36 | 36.1% | 2.8% | 55.9% | 52.8% |
| original|video|single_best | 36 | 69.2% | 22.2% | 76.6% | 77.8% |
| original|video|temporal_mean | 36 | 66.4% | 25.0% | 79.7% | 77.8% |
| original|video|window_mean_best | 36 | 64.3% | 25.0% | 80.6% | 72.2% |
| stripe_0.00|short | 45 | 2.9% | 0.0% | 0.4% | 0.0% |
| stripe_0.00|video|max_proj | 15 | 50.2% | 13.3% | 67.2% | 66.7% |
| stripe_0.00|video|single_best | 15 | 4.1% | 0.0% | 0.6% | 6.7% |
| stripe_0.00|video|temporal_mean | 15 | 42.0% | 6.7% | 61.5% | 60.0% |
| stripe_0.00|video|window_mean_best | 15 | 14.0% | 0.0% | 25.6% | 33.3% |
| stripe_0.10|short | 45 | 2.5% | 0.0% | 0.2% | 0.0% |
| stripe_0.10|video|max_proj | 15 | 49.5% | 6.7% | 65.8% | 66.7% |
| stripe_0.10|video|single_best | 15 | 3.4% | 0.0% | 3.3% | 0.0% |
| stripe_0.10|video|temporal_mean | 15 | 35.0% | 6.7% | 59.4% | 60.0% |
| stripe_0.10|video|window_mean_best | 15 | 13.0% | 0.0% | 31.2% | 26.7% |
| stripe_0.18|short | 45 | 1.7% | 0.0% | 0.2% | 0.0% |
| stripe_0.18|video|max_proj | 15 | 49.2% | 0.0% | 66.9% | 66.7% |
| stripe_0.18|video|single_best | 15 | 4.2% | 0.0% | 0.3% | 0.0% |
| stripe_0.18|video|temporal_mean | 15 | 36.5% | 0.0% | 62.0% | 60.0% |
| stripe_0.18|video|window_mean_best | 15 | 14.9% | 0.0% | 19.0% | 33.3% |
| stripe_0.30|short | 45 | 2.0% | 0.0% | 0.6% | 0.0% |
| stripe_0.30|video|max_proj | 15 | 48.0% | 0.0% | 64.3% | 66.7% |
| stripe_0.30|video|single_best | 15 | 3.3% | 0.0% | 0.1% | 0.0% |
| stripe_0.30|video|temporal_mean | 15 | 41.6% | 6.7% | 58.4% | 66.7% |
| stripe_0.30|video|window_mean_best | 15 | 11.1% | 0.0% | 31.2% | 26.7% |
| vlm|long | 108 | 2.0% | 0.0% | 12.5% | 2.8% |
| vlm|short | 108 | 1.2% | 0.0% | 2.8% | 0.0% |
| vlm|video|max_proj | 36 | 8.2% | 0.0% | 24.0% | 11.1% |
| vlm|video|single_best | 36 | 1.7% | 0.0% | 0.3% | 0.0% |
| vlm|video|temporal_mean | 36 | 12.2% | 0.0% | 30.2% | 27.8% |
| vlm|video|window_mean_best | 36 | 8.3% | 0.0% | 19.6% | 19.4% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 53.3% | 44.4% | 99.7% | 58.3% |
| anti_ocr | short | 36 | 11.3% | 0.0% | 8.8% | 11.1% |
| anti_ocr | video:max_proj | 12 | 87.7% | 41.7% | 94.1% | 100.0% |
| anti_ocr | video:single_best | 12 | 9.7% | 0.0% | 6.8% | 0.0% |
| anti_ocr | video:temporal_mean | 12 | 83.7% | 16.7% | 98.5% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 60.1% | 0.0% | 65.3% | 91.7% |
| deployed | long | 36 | 54.9% | 19.4% | 99.5% | 61.1% |
| deployed | short | 51 | 7.8% | 0.0% | 3.7% | 3.9% |
| deployed | video:max_proj | 17 | 84.7% | 29.4% | 91.0% | 100.0% |
| deployed | video:single_best | 17 | 11.9% | 0.0% | 8.2% | 5.9% |
| deployed | video:temporal_mean | 17 | 82.5% | 17.6% | 94.3% | 100.0% |
| deployed | video:window_mean_best | 17 | 32.8% | 0.0% | 56.3% | 64.7% |
| glyph_0.00 | short | 15 | 6.7% | 0.0% | 0.8% | 0.0% |
| glyph_0.00 | video:max_proj | 5 | 78.8% | 0.0% | 84.7% | 100.0% |
| glyph_0.00 | video:single_best | 5 | 9.0% | 0.0% | 0.9% | 0.0% |
| glyph_0.00 | video:temporal_mean | 5 | 72.3% | 0.0% | 92.0% | 100.0% |
| glyph_0.00 | video:window_mean_best | 5 | 37.0% | 0.0% | 77.1% | 80.0% |
| glyph_0.12 | short | 15 | 9.0% | 0.0% | 1.9% | 0.0% |
| glyph_0.12 | video:max_proj | 5 | 79.5% | 40.0% | 82.1% | 100.0% |
| glyph_0.12 | video:single_best | 5 | 8.9% | 0.0% | 0.9% | 0.0% |
| glyph_0.12 | video:temporal_mean | 5 | 83.6% | 20.0% | 90.1% | 100.0% |
| glyph_0.12 | video:window_mean_best | 5 | 48.0% | 0.0% | 76.2% | 60.0% |
| glyph_0.22 | short | 15 | 6.9% | 0.0% | 0.6% | 6.7% |
| glyph_0.22 | video:max_proj | 5 | 75.7% | 0.0% | 82.1% | 100.0% |
| glyph_0.22 | video:single_best | 5 | 10.3% | 0.0% | 8.8% | 0.0% |
| glyph_0.22 | video:temporal_mean | 5 | 81.9% | 20.0% | 87.0% | 100.0% |
| glyph_0.22 | video:window_mean_best | 5 | 49.9% | 0.0% | 53.3% | 100.0% |
| inversion_0.0 | long | 15 | 60.3% | 6.7% | 89.7% | 73.3% |
| inversion_0.0 | video:max_proj | 5 | 80.6% | 20.0% | 82.8% | 100.0% |
| inversion_0.0 | video:single_best | 5 | 11.5% | 0.0% | 1.2% | 20.0% |
| inversion_0.0 | video:temporal_mean | 5 | 82.4% | 0.0% | 91.7% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 40.4% | 0.0% | 72.1% | 80.0% |
| inversion_0.2 | long | 15 | 61.8% | 13.3% | 99.0% | 73.3% |
| inversion_0.2 | video:max_proj | 5 | 78.8% | 20.0% | 82.5% | 100.0% |
| inversion_0.2 | video:single_best | 5 | 9.2% | 0.0% | 4.0% | 0.0% |
| inversion_0.2 | video:temporal_mean | 5 | 75.4% | 20.0% | 91.3% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 37.7% | 0.0% | 50.2% | 100.0% |
| inversion_0.3 | long | 15 | 71.4% | 46.7% | 98.7% | 86.7% |
| inversion_0.3 | video:max_proj | 5 | 72.8% | 20.0% | 84.0% | 100.0% |
| inversion_0.3 | video:single_best | 5 | 8.2% | 0.0% | 4.5% | 0.0% |
| inversion_0.3 | video:temporal_mean | 5 | 71.6% | 0.0% | 89.2% | 100.0% |
| inversion_0.3 | video:window_mean_best | 5 | 39.5% | 0.0% | 77.6% | 100.0% |
| inversion_0.5 | long | 15 | 55.0% | 13.3% | 98.4% | 66.7% |
| inversion_0.5 | video:max_proj | 5 | 76.8% | 0.0% | 82.8% | 100.0% |
| inversion_0.5 | video:single_best | 5 | 13.1% | 0.0% | 13.1% | 0.0% |
| inversion_0.5 | video:temporal_mean | 5 | 83.2% | 20.0% | 90.6% | 100.0% |
| inversion_0.5 | video:window_mean_best | 5 | 46.4% | 0.0% | 78.1% | 80.0% |
| inversion_1.0 | long | 15 | 8.1% | 0.0% | 80.5% | 20.0% |
| inversion_1.0 | video:max_proj | 5 | 67.5% | 0.0% | 54.0% | 80.0% |
| inversion_1.0 | video:single_best | 5 | 49.0% | 20.0% | 34.0% | 60.0% |
| inversion_1.0 | video:temporal_mean | 5 | 40.1% | 0.0% | 65.0% | 80.0% |
| inversion_1.0 | video:window_mean_best | 5 | 39.9% | 0.0% | 37.8% | 60.0% |
| mask_noise | long | 36 | 43.9% | 19.4% | 96.6% | 50.0% |
| mask_noise | short | 36 | 13.1% | 0.0% | 7.4% | 11.1% |
| mask_noise | video:max_proj | 12 | 86.1% | 16.7% | 93.8% | 100.0% |
| mask_noise | video:single_best | 12 | 15.1% | 0.0% | 3.9% | 16.7% |
| mask_noise | video:temporal_mean | 12 | 86.8% | 16.7% | 97.1% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 67.7% | 8.3% | 81.7% | 91.7% |
| mask_only | long | 36 | 56.1% | 27.8% | 99.7% | 61.1% |
| mask_only | short | 36 | 11.8% | 0.0% | 13.3% | 16.7% |
| mask_only | video:max_proj | 12 | 89.3% | 41.7% | 84.8% | 100.0% |
| mask_only | video:single_best | 12 | 11.3% | 0.0% | 0.2% | 8.3% |
| mask_only | video:temporal_mean | 12 | 81.7% | 25.0% | 97.9% | 91.7% |
| mask_only | video:window_mean_best | 12 | 42.2% | 8.3% | 45.9% | 58.3% |
| original | long | 36 | 78.2% | 38.9% | 99.6% | 86.1% |
| original | short | 36 | 94.1% | 61.1% | 100.0% | 100.0% |
| original | video:max_proj | 12 | 65.7% | 8.3% | 87.4% | 91.7% |
| original | video:single_best | 12 | 92.4% | 41.7% | 89.1% | 100.0% |
| original | video:temporal_mean | 12 | 93.3% | 50.0% | 89.8% | 100.0% |
| original | video:window_mean_best | 12 | 92.6% | 50.0% | 89.3% | 100.0% |
| stripe_0.00 | short | 15 | 7.8% | 0.0% | 1.2% | 0.0% |
| stripe_0.00 | video:max_proj | 5 | 80.4% | 40.0% | 82.8% | 100.0% |
| stripe_0.00 | video:single_best | 5 | 11.1% | 0.0% | 1.2% | 20.0% |
| stripe_0.00 | video:temporal_mean | 5 | 81.3% | 20.0% | 88.7% | 100.0% |
| stripe_0.00 | video:window_mean_best | 5 | 36.3% | 0.0% | 53.1% | 80.0% |
| stripe_0.10 | short | 15 | 7.4% | 0.0% | 0.5% | 0.0% |
| stripe_0.10 | video:max_proj | 5 | 80.0% | 20.0% | 82.1% | 100.0% |
| stripe_0.10 | video:single_best | 5 | 9.8% | 0.0% | 9.5% | 0.0% |
| stripe_0.10 | video:temporal_mean | 5 | 70.3% | 20.0% | 89.9% | 100.0% |
| stripe_0.10 | video:window_mean_best | 5 | 29.7% | 0.0% | 77.6% | 60.0% |
| stripe_0.18 | short | 15 | 5.2% | 0.0% | 0.5% | 0.0% |
| stripe_0.18 | video:max_proj | 5 | 79.0% | 0.0% | 82.5% | 100.0% |
| stripe_0.18 | video:single_best | 5 | 10.8% | 0.0% | 0.5% | 0.0% |
| stripe_0.18 | video:temporal_mean | 5 | 72.9% | 0.0% | 89.6% | 100.0% |
| stripe_0.18 | video:window_mean_best | 5 | 32.4% | 0.0% | 45.7% | 80.0% |
| stripe_0.30 | short | 15 | 6.1% | 0.0% | 1.7% | 0.0% |
| stripe_0.30 | video:max_proj | 5 | 78.4% | 0.0% | 83.0% | 100.0% |
| stripe_0.30 | video:single_best | 5 | 9.7% | 0.0% | 0.2% | 0.0% |
| stripe_0.30 | video:temporal_mean | 5 | 79.2% | 20.0% | 88.4% | 100.0% |
| stripe_0.30 | video:window_mean_best | 5 | 26.3% | 0.0% | 77.8% | 80.0% |
| vlm | long | 36 | 5.8% | 0.0% | 33.6% | 8.3% |
| vlm | short | 36 | 3.2% | 0.0% | 8.4% | 0.0% |
| vlm | video:max_proj | 12 | 20.4% | 0.0% | 71.9% | 33.3% |
| vlm | video:single_best | 12 | 4.4% | 0.0% | 0.4% | 0.0% |
| vlm | video:temporal_mean | 12 | 33.8% | 0.0% | 90.6% | 83.3% |
| vlm | video:window_mean_best | 12 | 20.3% | 0.0% | 57.2% | 50.0% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | 24.9% | -5.6% | 78.2% | 38.9% |
| anti_ocr | short | 82.8% | 61.1% | 94.1% | 61.1% |
| anti_ocr | video:max_proj | -22.0% | -33.3% | 65.7% | 8.3% |
| anti_ocr | video:single_best | 82.7% | 41.7% | 92.4% | 41.7% |
| anti_ocr | video:temporal_mean | 9.6% | 33.3% | 93.3% | 50.0% |
| anti_ocr | video:window_mean_best | 32.4% | 50.0% | 92.6% | 50.0% |
| deployed | long | 23.4% | 19.4% | 78.2% | 38.9% |
| deployed | short | 86.3% | 61.1% | 94.1% | 61.1% |
| deployed | video:max_proj | -18.9% | -21.1% | 65.7% | 8.3% |
| deployed | video:single_best | 80.5% | 41.7% | 92.4% | 41.7% |
| deployed | video:temporal_mean | 10.8% | 32.4% | 93.3% | 50.0% |
| deployed | video:window_mean_best | 59.8% | 50.0% | 92.6% | 50.0% |
| glyph_0.00 | short | 87.4% | 61.1% | 94.1% | 61.1% |
| glyph_0.00 | video:max_proj | -13.0% | 8.3% | 65.7% | 8.3% |
| glyph_0.00 | video:single_best | 83.4% | 41.7% | 92.4% | 41.7% |
| glyph_0.00 | video:temporal_mean | 21.0% | 50.0% | 93.3% | 50.0% |
| glyph_0.00 | video:window_mean_best | 55.5% | 50.0% | 92.6% | 50.0% |
| glyph_0.12 | short | 85.1% | 61.1% | 94.1% | 61.1% |
| glyph_0.12 | video:max_proj | -13.8% | -31.7% | 65.7% | 8.3% |
| glyph_0.12 | video:single_best | 83.5% | 41.7% | 92.4% | 41.7% |
| glyph_0.12 | video:temporal_mean | 9.7% | 30.0% | 93.3% | 50.0% |
| glyph_0.12 | video:window_mean_best | 44.6% | 50.0% | 92.6% | 50.0% |
| glyph_0.22 | short | 87.2% | 61.1% | 94.1% | 61.1% |
| glyph_0.22 | video:max_proj | -9.9% | 8.3% | 65.7% | 8.3% |
| glyph_0.22 | video:single_best | 82.1% | 41.7% | 92.4% | 41.7% |
| glyph_0.22 | video:temporal_mean | 11.4% | 30.0% | 93.3% | 50.0% |
| glyph_0.22 | video:window_mean_best | 42.6% | 50.0% | 92.6% | 50.0% |
| inversion_0.0 | long | 18.0% | 32.2% | 78.2% | 38.9% |
| inversion_0.0 | video:max_proj | -14.8% | -11.7% | 65.7% | 8.3% |
| inversion_0.0 | video:single_best | 80.9% | 41.7% | 92.4% | 41.7% |
| inversion_0.0 | video:temporal_mean | 10.9% | 50.0% | 93.3% | 50.0% |
| inversion_0.0 | video:window_mean_best | 52.2% | 50.0% | 92.6% | 50.0% |
| inversion_0.2 | long | 16.4% | 25.6% | 78.2% | 38.9% |
| inversion_0.2 | video:max_proj | -13.1% | -11.7% | 65.7% | 8.3% |
| inversion_0.2 | video:single_best | 83.2% | 41.7% | 92.4% | 41.7% |
| inversion_0.2 | video:temporal_mean | 17.9% | 30.0% | 93.3% | 50.0% |
| inversion_0.2 | video:window_mean_best | 54.8% | 50.0% | 92.6% | 50.0% |
| inversion_0.3 | long | 6.8% | -7.8% | 78.2% | 38.9% |
| inversion_0.3 | video:max_proj | -7.1% | -11.7% | 65.7% | 8.3% |
| inversion_0.3 | video:single_best | 84.2% | 41.7% | 92.4% | 41.7% |
| inversion_0.3 | video:temporal_mean | 21.7% | 50.0% | 93.3% | 50.0% |
| inversion_0.3 | video:window_mean_best | 53.0% | 50.0% | 92.6% | 50.0% |
| inversion_0.5 | long | 23.2% | 25.6% | 78.2% | 38.9% |
| inversion_0.5 | video:max_proj | -11.1% | 8.3% | 65.7% | 8.3% |
| inversion_0.5 | video:single_best | 79.3% | 41.7% | 92.4% | 41.7% |
| inversion_0.5 | video:temporal_mean | 10.1% | 30.0% | 93.3% | 50.0% |
| inversion_0.5 | video:window_mean_best | 46.2% | 50.0% | 92.6% | 50.0% |
| inversion_1.0 | long | 70.1% | 38.9% | 78.2% | 38.9% |
| inversion_1.0 | video:max_proj | -1.8% | 8.3% | 65.7% | 8.3% |
| inversion_1.0 | video:single_best | 43.3% | 21.7% | 92.4% | 41.7% |
| inversion_1.0 | video:temporal_mean | 53.2% | 50.0% | 93.3% | 50.0% |
| inversion_1.0 | video:window_mean_best | 52.6% | 50.0% | 92.6% | 50.0% |
| mask_noise | long | 34.3% | 19.4% | 78.2% | 38.9% |
| mask_noise | short | 81.0% | 61.1% | 94.1% | 61.1% |
| mask_noise | video:max_proj | -20.4% | -8.3% | 65.7% | 8.3% |
| mask_noise | video:single_best | 77.2% | 41.7% | 92.4% | 41.7% |
| mask_noise | video:temporal_mean | 6.4% | 33.3% | 93.3% | 50.0% |
| mask_noise | video:window_mean_best | 24.8% | 41.7% | 92.6% | 50.0% |
| mask_only | long | 22.1% | 11.1% | 78.2% | 38.9% |
| mask_only | short | 82.3% | 61.1% | 94.1% | 61.1% |
| mask_only | video:max_proj | -23.5% | -33.3% | 65.7% | 8.3% |
| mask_only | video:single_best | 81.1% | 41.7% | 92.4% | 41.7% |
| mask_only | video:temporal_mean | 11.6% | 25.0% | 93.3% | 50.0% |
| mask_only | video:window_mean_best | 50.3% | 41.7% | 92.6% | 50.0% |
| original | long | 0.0% | 0.0% | 78.2% | 38.9% |
| original | short | 0.0% | 0.0% | 94.1% | 61.1% |
| original | video:max_proj | 0.0% | 0.0% | 65.7% | 8.3% |
| original | video:single_best | 0.0% | 0.0% | 92.4% | 41.7% |
| original | video:temporal_mean | 0.0% | 0.0% | 93.3% | 50.0% |
| original | video:window_mean_best | 0.0% | 0.0% | 92.6% | 50.0% |
| stripe_0.00 | short | 86.2% | 61.1% | 94.1% | 61.1% |
| stripe_0.00 | video:max_proj | -14.7% | -31.7% | 65.7% | 8.3% |
| stripe_0.00 | video:single_best | 81.2% | 41.7% | 92.4% | 41.7% |
| stripe_0.00 | video:temporal_mean | 12.0% | 30.0% | 93.3% | 50.0% |
| stripe_0.00 | video:window_mean_best | 56.2% | 50.0% | 92.6% | 50.0% |
| stripe_0.10 | short | 86.6% | 61.1% | 94.1% | 61.1% |
| stripe_0.10 | video:max_proj | -14.3% | -11.7% | 65.7% | 8.3% |
| stripe_0.10 | video:single_best | 82.5% | 41.7% | 92.4% | 41.7% |
| stripe_0.10 | video:temporal_mean | 23.0% | 30.0% | 93.3% | 50.0% |
| stripe_0.10 | video:window_mean_best | 62.9% | 50.0% | 92.6% | 50.0% |
| stripe_0.18 | short | 88.8% | 61.1% | 94.1% | 61.1% |
| stripe_0.18 | video:max_proj | -13.3% | 8.3% | 65.7% | 8.3% |
| stripe_0.18 | video:single_best | 81.6% | 41.7% | 92.4% | 41.7% |
| stripe_0.18 | video:temporal_mean | 20.4% | 50.0% | 93.3% | 50.0% |
| stripe_0.18 | video:window_mean_best | 60.2% | 50.0% | 92.6% | 50.0% |
| stripe_0.30 | short | 87.9% | 61.1% | 94.1% | 61.1% |
| stripe_0.30 | video:max_proj | -12.7% | 8.3% | 65.7% | 8.3% |
| stripe_0.30 | video:single_best | 82.6% | 41.7% | 92.4% | 41.7% |
| stripe_0.30 | video:temporal_mean | 14.1% | 30.0% | 93.3% | 50.0% |
| stripe_0.30 | video:window_mean_best | 66.2% | 50.0% | 92.6% | 50.0% |
| vlm | long | 72.5% | 38.9% | 78.2% | 38.9% |
| vlm | short | 90.8% | 61.1% | 94.1% | 61.1% |
| vlm | video:max_proj | 45.3% | 8.3% | 65.7% | 8.3% |
| vlm | video:single_best | 87.9% | 41.7% | 92.4% | 41.7% |
| vlm | video:temporal_mean | 59.5% | 50.0% | 93.3% | 50.0% |
| vlm | video:window_mean_best | 72.2% | 50.0% | 92.6% | 50.0% |
