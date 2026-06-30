# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 20.4% | 13.0% | 87.3% | 25.0% |
| anti_ocr|short | 108 | 4.6% | 0.0% | 8.2% | 4.6% |
| anti_ocr|video|max_proj | 36 | 33.7% | 2.8% | 44.1% | 47.2% |
| anti_ocr|video|single_best | 36 | 10.1% | 2.8% | 16.3% | 11.1% |
| anti_ocr|video|temporal_mean | 36 | 49.3% | 22.2% | 75.5% | 61.1% |
| anti_ocr|video|window_mean_best | 36 | 41.3% | 2.8% | 61.3% | 55.6% |
| deployed|long | 108 | 26.2% | 15.7% | 87.3% | 29.6% |
| deployed|short | 153 | 4.1% | 0.0% | 10.0% | 3.9% |
| deployed|video|max_proj | 51 | 30.7% | 2.0% | 46.0% | 45.1% |
| deployed|video|single_best | 51 | 6.4% | 0.0% | 11.7% | 5.9% |
| deployed|video|temporal_mean | 51 | 35.4% | 11.8% | 67.4% | 49.0% |
| deployed|video|window_mean_best | 51 | 37.5% | 3.9% | 58.8% | 52.9% |
| glyph_0.00|short | 45 | 3.4% | 0.0% | 4.1% | 2.2% |
| glyph_0.00|video|max_proj | 15 | 30.0% | 6.7% | 29.4% | 53.3% |
| glyph_0.00|video|single_best | 15 | 4.0% | 0.0% | 5.4% | 0.0% |
| glyph_0.00|video|temporal_mean | 15 | 31.5% | 6.7% | 51.0% | 40.0% |
| glyph_0.00|video|window_mean_best | 15 | 25.6% | 0.0% | 31.8% | 33.3% |
| glyph_0.12|short | 45 | 3.1% | 0.0% | 9.5% | 4.4% |
| glyph_0.12|video|max_proj | 15 | 35.7% | 0.0% | 36.0% | 46.7% |
| glyph_0.12|video|single_best | 15 | 5.3% | 0.0% | 0.9% | 0.0% |
| glyph_0.12|video|temporal_mean | 15 | 22.1% | 6.7% | 53.6% | 40.0% |
| glyph_0.12|video|window_mean_best | 15 | 22.2% | 0.0% | 41.7% | 33.3% |
| glyph_0.22|short | 45 | 2.8% | 0.0% | 3.4% | 0.0% |
| glyph_0.22|video|max_proj | 15 | 28.2% | 0.0% | 30.1% | 46.7% |
| glyph_0.22|video|single_best | 15 | 7.1% | 0.0% | 16.3% | 6.7% |
| glyph_0.22|video|temporal_mean | 15 | 26.2% | 6.7% | 55.0% | 40.0% |
| glyph_0.22|video|window_mean_best | 15 | 39.9% | 0.0% | 56.7% | 66.7% |
| inversion_0.0|long | 45 | 25.6% | 13.3% | 84.2% | 33.3% |
| inversion_0.0|video|max_proj | 15 | 24.3% | 0.0% | 22.4% | 46.7% |
| inversion_0.0|video|single_best | 15 | 6.2% | 0.0% | 7.1% | 13.3% |
| inversion_0.0|video|temporal_mean | 15 | 48.2% | 6.7% | 60.3% | 73.3% |
| inversion_0.0|video|window_mean_best | 15 | 25.1% | 0.0% | 45.1% | 53.3% |
| inversion_0.2|long | 45 | 28.8% | 13.3% | 83.9% | 40.0% |
| inversion_0.2|video|max_proj | 15 | 32.1% | 0.0% | 39.2% | 46.7% |
| inversion_0.2|video|single_best | 15 | 5.4% | 0.0% | 8.0% | 6.7% |
| inversion_0.2|video|temporal_mean | 15 | 30.0% | 13.3% | 53.1% | 46.7% |
| inversion_0.2|video|window_mean_best | 15 | 26.0% | 0.0% | 39.7% | 46.7% |
| inversion_0.3|long | 45 | 28.5% | 15.6% | 82.8% | 35.6% |
| inversion_0.3|video|max_proj | 15 | 12.7% | 0.0% | 22.6% | 20.0% |
| inversion_0.3|video|single_best | 15 | 8.5% | 0.0% | 9.0% | 6.7% |
| inversion_0.3|video|temporal_mean | 15 | 28.0% | 13.3% | 56.2% | 46.7% |
| inversion_0.3|video|window_mean_best | 15 | 25.6% | 6.7% | 49.4% | 46.7% |
| inversion_0.5|long | 45 | 23.5% | 11.1% | 71.2% | 28.9% |
| inversion_0.5|video|max_proj | 15 | 17.6% | 0.0% | 33.7% | 33.3% |
| inversion_0.5|video|single_best | 15 | 6.9% | 0.0% | 0.3% | 6.7% |
| inversion_0.5|video|temporal_mean | 15 | 30.1% | 6.7% | 53.8% | 46.7% |
| inversion_0.5|video|window_mean_best | 15 | 28.0% | 0.0% | 42.8% | 46.7% |
| inversion_1.0|long | 45 | 6.8% | 0.0% | 39.9% | 13.3% |
| inversion_1.0|video|max_proj | 15 | 36.9% | 6.7% | 21.7% | 53.3% |
| inversion_1.0|video|single_best | 15 | 60.3% | 26.7% | 52.5% | 73.3% |
| inversion_1.0|video|temporal_mean | 15 | 11.3% | 0.0% | 15.3% | 20.0% |
| inversion_1.0|video|window_mean_best | 15 | 31.9% | 6.7% | 45.9% | 46.7% |
| mask_noise|long | 108 | 32.3% | 18.5% | 89.3% | 38.0% |
| mask_noise|short | 108 | 6.2% | 0.0% | 10.6% | 7.4% |
| mask_noise|video|max_proj | 36 | 34.2% | 0.0% | 50.7% | 52.8% |
| mask_noise|video|single_best | 36 | 6.9% | 0.0% | 10.4% | 8.3% |
| mask_noise|video|temporal_mean | 36 | 49.2% | 11.1% | 73.9% | 63.9% |
| mask_noise|video|window_mean_best | 36 | 39.7% | 5.6% | 62.6% | 58.3% |
| mask_only|long | 108 | 30.5% | 15.7% | 88.4% | 36.1% |
| mask_only|short | 108 | 11.5% | 0.0% | 9.3% | 17.6% |
| mask_only|video|max_proj | 36 | 25.8% | 0.0% | 39.8% | 47.2% |
| mask_only|video|single_best | 36 | 7.6% | 0.0% | 15.3% | 8.3% |
| mask_only|video|temporal_mean | 36 | 54.2% | 22.2% | 70.2% | 69.4% |
| mask_only|video|window_mean_best | 36 | 40.2% | 2.8% | 60.0% | 55.6% |
| original|long | 108 | 3.9% | 0.0% | 57.5% | 5.6% |
| original|short | 108 | 63.7% | 31.5% | 89.2% | 72.2% |
| original|video|max_proj | 36 | 22.2% | 5.6% | 44.0% | 30.6% |
| original|video|single_best | 36 | 64.7% | 38.9% | 79.5% | 72.2% |
| original|video|temporal_mean | 36 | 68.4% | 41.7% | 85.2% | 77.8% |
| original|video|window_mean_best | 36 | 66.7% | 38.9% | 82.6% | 75.0% |
| stripe_0.00|short | 45 | 2.5% | 0.0% | 3.8% | 0.0% |
| stripe_0.00|video|max_proj | 15 | 33.7% | 0.0% | 54.4% | 40.0% |
| stripe_0.00|video|single_best | 15 | 2.8% | 0.0% | 14.7% | 0.0% |
| stripe_0.00|video|temporal_mean | 15 | 32.4% | 13.3% | 53.6% | 46.7% |
| stripe_0.00|video|window_mean_best | 15 | 20.5% | 0.0% | 43.0% | 33.3% |
| stripe_0.10|short | 45 | 2.5% | 0.0% | 1.1% | 0.0% |
| stripe_0.10|video|max_proj | 15 | 28.8% | 0.0% | 30.5% | 46.7% |
| stripe_0.10|video|single_best | 15 | 7.7% | 0.0% | 13.7% | 13.3% |
| stripe_0.10|video|temporal_mean | 15 | 21.9% | 0.0% | 53.8% | 40.0% |
| stripe_0.10|video|window_mean_best | 15 | 14.2% | 0.0% | 31.0% | 20.0% |
| stripe_0.18|short | 45 | 3.0% | 0.0% | 3.6% | 0.0% |
| stripe_0.18|video|max_proj | 15 | 31.3% | 0.0% | 48.6% | 46.7% |
| stripe_0.18|video|single_best | 15 | 6.3% | 0.0% | 7.3% | 6.7% |
| stripe_0.18|video|temporal_mean | 15 | 15.6% | 0.0% | 52.0% | 26.7% |
| stripe_0.18|video|window_mean_best | 15 | 22.6% | 0.0% | 41.2% | 33.3% |
| stripe_0.30|short | 45 | 3.6% | 0.0% | 5.6% | 2.2% |
| stripe_0.30|video|max_proj | 15 | 30.4% | 0.0% | 32.7% | 53.3% |
| stripe_0.30|video|single_best | 15 | 4.4% | 0.0% | 9.1% | 0.0% |
| stripe_0.30|video|temporal_mean | 15 | 27.7% | 6.7% | 56.6% | 46.7% |
| stripe_0.30|video|window_mean_best | 15 | 28.1% | 0.0% | 44.3% | 53.3% |
| vlm|long | 108 | 5.8% | 0.0% | 14.7% | 8.3% |
| vlm|short | 108 | 1.2% | 0.0% | 3.0% | 0.0% |
| vlm|video|max_proj | 36 | 5.7% | 0.0% | 9.5% | 5.6% |
| vlm|video|single_best | 36 | 1.2% | 0.0% | 3.3% | 0.0% |
| vlm|video|temporal_mean | 36 | 26.1% | 2.8% | 18.3% | 36.1% |
| vlm|video|window_mean_best | 36 | 6.0% | 0.0% | 12.9% | 5.6% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 56.1% | 38.9% | 96.6% | 63.9% |
| anti_ocr | short | 36 | 12.7% | 0.0% | 24.1% | 13.9% |
| anti_ocr | video:max_proj | 12 | 66.8% | 8.3% | 78.0% | 91.7% |
| anti_ocr | video:single_best | 12 | 20.0% | 8.3% | 48.1% | 16.7% |
| anti_ocr | video:temporal_mean | 12 | 86.1% | 58.3% | 94.7% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 73.1% | 8.3% | 89.9% | 91.7% |
| deployed | long | 36 | 67.3% | 47.2% | 97.9% | 72.2% |
| deployed | short | 51 | 11.4% | 0.0% | 29.9% | 11.8% |
| deployed | video:max_proj | 17 | 63.3% | 5.9% | 77.2% | 88.2% |
| deployed | video:single_best | 17 | 14.3% | 0.0% | 30.3% | 11.8% |
| deployed | video:temporal_mean | 17 | 77.9% | 35.3% | 90.4% | 100.0% |
| deployed | video:window_mean_best | 17 | 67.8% | 5.9% | 86.2% | 88.2% |
| glyph_0.00 | short | 15 | 9.0% | 0.0% | 12.4% | 6.7% |
| glyph_0.00 | video:max_proj | 5 | 66.5% | 20.0% | 71.1% | 100.0% |
| glyph_0.00 | video:single_best | 5 | 9.9% | 0.0% | 15.5% | 0.0% |
| glyph_0.00 | video:temporal_mean | 5 | 70.4% | 20.0% | 85.4% | 100.0% |
| glyph_0.00 | video:window_mean_best | 5 | 51.9% | 0.0% | 79.2% | 60.0% |
| glyph_0.12 | short | 15 | 8.4% | 0.0% | 28.6% | 13.3% |
| glyph_0.12 | video:max_proj | 5 | 64.8% | 0.0% | 50.0% | 80.0% |
| glyph_0.12 | video:single_best | 5 | 10.7% | 0.0% | 1.7% | 0.0% |
| glyph_0.12 | video:temporal_mean | 5 | 53.0% | 20.0% | 82.8% | 80.0% |
| glyph_0.12 | video:window_mean_best | 5 | 51.1% | 0.0% | 78.5% | 80.0% |
| glyph_0.22 | short | 15 | 7.9% | 0.0% | 10.1% | 0.0% |
| glyph_0.22 | video:max_proj | 5 | 52.0% | 0.0% | 49.7% | 100.0% |
| glyph_0.22 | video:single_best | 5 | 15.3% | 0.0% | 47.8% | 20.0% |
| glyph_0.22 | video:temporal_mean | 5 | 60.4% | 20.0% | 84.0% | 80.0% |
| glyph_0.22 | video:window_mean_best | 5 | 69.4% | 0.0% | 78.5% | 100.0% |
| inversion_0.0 | long | 15 | 64.1% | 40.0% | 94.6% | 73.3% |
| inversion_0.0 | video:max_proj | 5 | 53.5% | 0.0% | 51.1% | 100.0% |
| inversion_0.0 | video:single_best | 5 | 13.4% | 0.0% | 20.9% | 40.0% |
| inversion_0.0 | video:temporal_mean | 5 | 83.1% | 20.0% | 88.9% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 57.2% | 0.0% | 78.3% | 100.0% |
| inversion_0.2 | long | 15 | 70.8% | 40.0% | 97.2% | 80.0% |
| inversion_0.2 | video:max_proj | 5 | 60.8% | 0.0% | 71.6% | 100.0% |
| inversion_0.2 | video:single_best | 5 | 13.3% | 0.0% | 23.1% | 20.0% |
| inversion_0.2 | video:temporal_mean | 5 | 74.7% | 40.0% | 85.6% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 54.4% | 0.0% | 77.8% | 100.0% |
| inversion_0.3 | long | 15 | 63.6% | 46.7% | 94.2% | 73.3% |
| inversion_0.3 | video:max_proj | 5 | 32.7% | 0.0% | 44.7% | 60.0% |
| inversion_0.3 | video:single_best | 5 | 20.2% | 0.0% | 26.2% | 20.0% |
| inversion_0.3 | video:temporal_mean | 5 | 70.2% | 40.0% | 82.8% | 100.0% |
| inversion_0.3 | video:window_mean_best | 5 | 58.3% | 20.0% | 79.0% | 100.0% |
| inversion_0.5 | long | 15 | 63.0% | 33.3% | 93.9% | 73.3% |
| inversion_0.5 | video:max_proj | 5 | 49.6% | 0.0% | 72.8% | 100.0% |
| inversion_0.5 | video:single_best | 5 | 16.1% | 0.0% | 0.7% | 20.0% |
| inversion_0.5 | video:temporal_mean | 5 | 62.9% | 20.0% | 81.4% | 100.0% |
| inversion_0.5 | video:window_mean_best | 5 | 54.7% | 0.0% | 79.0% | 80.0% |
| inversion_1.0 | long | 15 | 19.2% | 0.0% | 77.7% | 40.0% |
| inversion_1.0 | video:max_proj | 5 | 67.5% | 20.0% | 45.2% | 80.0% |
| inversion_1.0 | video:single_best | 5 | 74.3% | 60.0% | 75.5% | 80.0% |
| inversion_1.0 | video:temporal_mean | 5 | 29.1% | 0.0% | 44.7% | 60.0% |
| inversion_1.0 | video:window_mean_best | 5 | 57.4% | 20.0% | 78.5% | 80.0% |
| mask_noise | long | 36 | 87.7% | 55.6% | 99.0% | 94.4% |
| mask_noise | short | 36 | 17.7% | 0.0% | 31.8% | 22.2% |
| mask_noise | video:max_proj | 12 | 70.3% | 0.0% | 92.9% | 100.0% |
| mask_noise | video:single_best | 12 | 18.5% | 0.0% | 30.8% | 25.0% |
| mask_noise | video:temporal_mean | 12 | 86.1% | 33.3% | 95.9% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 67.0% | 8.3% | 83.2% | 91.7% |
| mask_only | long | 36 | 80.0% | 47.2% | 99.3% | 86.1% |
| mask_only | short | 36 | 26.3% | 0.0% | 27.9% | 41.7% |
| mask_only | video:max_proj | 12 | 62.2% | 0.0% | 83.4% | 100.0% |
| mask_only | video:single_best | 12 | 18.8% | 0.0% | 43.1% | 25.0% |
| mask_only | video:temporal_mean | 12 | 89.4% | 50.0% | 95.7% | 100.0% |
| mask_only | video:window_mean_best | 12 | 73.9% | 8.3% | 91.3% | 91.7% |
| original | long | 36 | 10.6% | 0.0% | 97.9% | 16.7% |
| original | short | 36 | 94.3% | 55.6% | 99.7% | 100.0% |
| original | video:max_proj | 12 | 51.2% | 8.3% | 83.8% | 66.7% |
| original | video:single_best | 12 | 90.5% | 75.0% | 92.5% | 100.0% |
| original | video:temporal_mean | 12 | 95.3% | 75.0% | 97.9% | 100.0% |
| original | video:window_mean_best | 12 | 91.1% | 75.0% | 92.1% | 100.0% |
| stripe_0.00 | short | 15 | 7.2% | 0.0% | 11.4% | 0.0% |
| stripe_0.00 | video:max_proj | 5 | 66.3% | 0.0% | 77.8% | 80.0% |
| stripe_0.00 | video:single_best | 5 | 8.3% | 0.0% | 43.6% | 0.0% |
| stripe_0.00 | video:temporal_mean | 5 | 73.9% | 40.0% | 79.5% | 100.0% |
| stripe_0.00 | video:window_mean_best | 5 | 47.3% | 0.0% | 79.5% | 80.0% |
| stripe_0.10 | short | 15 | 7.4% | 0.0% | 3.2% | 0.0% |
| stripe_0.10 | video:max_proj | 5 | 68.2% | 0.0% | 74.2% | 100.0% |
| stripe_0.10 | video:single_best | 5 | 18.3% | 0.0% | 25.7% | 20.0% |
| stripe_0.10 | video:temporal_mean | 5 | 55.0% | 0.0% | 84.2% | 80.0% |
| stripe_0.10 | video:window_mean_best | 5 | 33.9% | 0.0% | 78.1% | 40.0% |
| stripe_0.18 | short | 15 | 7.6% | 0.0% | 10.9% | 0.0% |
| stripe_0.18 | video:max_proj | 5 | 53.2% | 0.0% | 78.5% | 80.0% |
| stripe_0.18 | video:single_best | 5 | 14.7% | 0.0% | 21.2% | 20.0% |
| stripe_0.18 | video:temporal_mean | 5 | 38.9% | 0.0% | 82.5% | 60.0% |
| stripe_0.18 | video:window_mean_best | 5 | 55.0% | 0.0% | 79.0% | 100.0% |
| stripe_0.30 | short | 15 | 10.3% | 0.0% | 16.8% | 6.7% |
| stripe_0.30 | video:max_proj | 5 | 60.7% | 0.0% | 50.0% | 100.0% |
| stripe_0.30 | video:single_best | 5 | 11.0% | 0.0% | 26.4% | 0.0% |
| stripe_0.30 | video:temporal_mean | 5 | 63.9% | 20.0% | 82.1% | 100.0% |
| stripe_0.30 | video:window_mean_best | 5 | 50.5% | 0.0% | 78.3% | 100.0% |
| vlm | long | 36 | 16.2% | 0.0% | 36.7% | 25.0% |
| vlm | short | 36 | 3.6% | 0.0% | 8.9% | 0.0% |
| vlm | video:max_proj | 12 | 13.4% | 0.0% | 28.3% | 16.7% |
| vlm | video:single_best | 12 | 3.2% | 0.0% | 9.8% | 0.0% |
| vlm | video:temporal_mean | 12 | 61.1% | 8.3% | 54.9% | 83.3% |
| vlm | video:window_mean_best | 12 | 14.7% | 0.0% | 37.1% | 16.7% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | -45.5% | -38.9% | 10.6% | 0.0% |
| anti_ocr | short | 81.6% | 55.6% | 94.3% | 55.6% |
| anti_ocr | video:max_proj | -15.6% | 0.0% | 51.2% | 8.3% |
| anti_ocr | video:single_best | 70.5% | 66.7% | 90.5% | 75.0% |
| anti_ocr | video:temporal_mean | 9.2% | 16.7% | 95.3% | 75.0% |
| anti_ocr | video:window_mean_best | 18.0% | 66.7% | 91.1% | 75.0% |
| deployed | long | -56.7% | -47.2% | 10.6% | 0.0% |
| deployed | short | 82.9% | 55.6% | 94.3% | 55.6% |
| deployed | video:max_proj | -12.1% | 2.5% | 51.2% | 8.3% |
| deployed | video:single_best | 76.2% | 75.0% | 90.5% | 75.0% |
| deployed | video:temporal_mean | 17.4% | 39.7% | 95.3% | 75.0% |
| deployed | video:window_mean_best | 23.3% | 69.1% | 91.1% | 75.0% |
| glyph_0.00 | short | 85.3% | 55.6% | 94.3% | 55.6% |
| glyph_0.00 | video:max_proj | -15.3% | -11.7% | 51.2% | 8.3% |
| glyph_0.00 | video:single_best | 80.7% | 75.0% | 90.5% | 75.0% |
| glyph_0.00 | video:temporal_mean | 24.9% | 55.0% | 95.3% | 75.0% |
| glyph_0.00 | video:window_mean_best | 39.2% | 75.0% | 91.1% | 75.0% |
| glyph_0.12 | short | 85.9% | 55.6% | 94.3% | 55.6% |
| glyph_0.12 | video:max_proj | -13.6% | 8.3% | 51.2% | 8.3% |
| glyph_0.12 | video:single_best | 79.8% | 75.0% | 90.5% | 75.0% |
| glyph_0.12 | video:temporal_mean | 42.3% | 55.0% | 95.3% | 75.0% |
| glyph_0.12 | video:window_mean_best | 40.0% | 75.0% | 91.1% | 75.0% |
| glyph_0.22 | short | 86.4% | 55.6% | 94.3% | 55.6% |
| glyph_0.22 | video:max_proj | -0.8% | 8.3% | 51.2% | 8.3% |
| glyph_0.22 | video:single_best | 75.2% | 75.0% | 90.5% | 75.0% |
| glyph_0.22 | video:temporal_mean | 35.0% | 55.0% | 95.3% | 75.0% |
| glyph_0.22 | video:window_mean_best | 21.7% | 75.0% | 91.1% | 75.0% |
| inversion_0.0 | long | -53.5% | -40.0% | 10.6% | 0.0% |
| inversion_0.0 | video:max_proj | -2.3% | 8.3% | 51.2% | 8.3% |
| inversion_0.0 | video:single_best | 77.1% | 75.0% | 90.5% | 75.0% |
| inversion_0.0 | video:temporal_mean | 12.2% | 55.0% | 95.3% | 75.0% |
| inversion_0.0 | video:window_mean_best | 33.9% | 75.0% | 91.1% | 75.0% |
| inversion_0.2 | long | -60.2% | -40.0% | 10.6% | 0.0% |
| inversion_0.2 | video:max_proj | -9.6% | 8.3% | 51.2% | 8.3% |
| inversion_0.2 | video:single_best | 77.2% | 75.0% | 90.5% | 75.0% |
| inversion_0.2 | video:temporal_mean | 20.6% | 35.0% | 95.3% | 75.0% |
| inversion_0.2 | video:window_mean_best | 36.7% | 75.0% | 91.1% | 75.0% |
| inversion_0.3 | long | -53.0% | -46.7% | 10.6% | 0.0% |
| inversion_0.3 | video:max_proj | 18.5% | 8.3% | 51.2% | 8.3% |
| inversion_0.3 | video:single_best | 70.4% | 75.0% | 90.5% | 75.0% |
| inversion_0.3 | video:temporal_mean | 25.1% | 35.0% | 95.3% | 75.0% |
| inversion_0.3 | video:window_mean_best | 32.8% | 55.0% | 91.1% | 75.0% |
| inversion_0.5 | long | -52.5% | -33.3% | 10.6% | 0.0% |
| inversion_0.5 | video:max_proj | 1.6% | 8.3% | 51.2% | 8.3% |
| inversion_0.5 | video:single_best | 74.4% | 75.0% | 90.5% | 75.0% |
| inversion_0.5 | video:temporal_mean | 32.4% | 55.0% | 95.3% | 75.0% |
| inversion_0.5 | video:window_mean_best | 36.4% | 75.0% | 91.1% | 75.0% |
| inversion_1.0 | long | -8.6% | 0.0% | 10.6% | 0.0% |
| inversion_1.0 | video:max_proj | -16.3% | -11.7% | 51.2% | 8.3% |
| inversion_1.0 | video:single_best | 16.2% | 15.0% | 90.5% | 75.0% |
| inversion_1.0 | video:temporal_mean | 66.2% | 75.0% | 95.3% | 75.0% |
| inversion_1.0 | video:window_mean_best | 33.7% | 55.0% | 91.1% | 75.0% |
| mask_noise | long | -77.2% | -55.6% | 10.6% | 0.0% |
| mask_noise | short | 76.6% | 55.6% | 94.3% | 55.6% |
| mask_noise | video:max_proj | -19.1% | 8.3% | 51.2% | 8.3% |
| mask_noise | video:single_best | 72.0% | 75.0% | 90.5% | 75.0% |
| mask_noise | video:temporal_mean | 9.2% | 41.7% | 95.3% | 75.0% |
| mask_noise | video:window_mean_best | 24.1% | 66.7% | 91.1% | 75.0% |
| mask_only | long | -69.5% | -47.2% | 10.6% | 0.0% |
| mask_only | short | 68.0% | 55.6% | 94.3% | 55.6% |
| mask_only | video:max_proj | -11.0% | 8.3% | 51.2% | 8.3% |
| mask_only | video:single_best | 71.8% | 75.0% | 90.5% | 75.0% |
| mask_only | video:temporal_mean | 5.9% | 25.0% | 95.3% | 75.0% |
| mask_only | video:window_mean_best | 17.1% | 66.7% | 91.1% | 75.0% |
| original | long | 0.0% | 0.0% | 10.6% | 0.0% |
| original | short | 0.0% | 0.0% | 94.3% | 55.6% |
| original | video:max_proj | 0.0% | 0.0% | 51.2% | 8.3% |
| original | video:single_best | 0.0% | 0.0% | 90.5% | 75.0% |
| original | video:temporal_mean | 0.0% | 0.0% | 95.3% | 75.0% |
| original | video:window_mean_best | 0.0% | 0.0% | 91.1% | 75.0% |
| stripe_0.00 | short | 87.1% | 55.6% | 94.3% | 55.6% |
| stripe_0.00 | video:max_proj | -15.1% | 8.3% | 51.2% | 8.3% |
| stripe_0.00 | video:single_best | 82.2% | 75.0% | 90.5% | 75.0% |
| stripe_0.00 | video:temporal_mean | 21.4% | 35.0% | 95.3% | 75.0% |
| stripe_0.00 | video:window_mean_best | 43.8% | 75.0% | 91.1% | 75.0% |
| stripe_0.10 | short | 86.9% | 55.6% | 94.3% | 55.6% |
| stripe_0.10 | video:max_proj | -17.0% | 8.3% | 51.2% | 8.3% |
| stripe_0.10 | video:single_best | 72.3% | 75.0% | 90.5% | 75.0% |
| stripe_0.10 | video:temporal_mean | 40.3% | 75.0% | 95.3% | 75.0% |
| stripe_0.10 | video:window_mean_best | 57.2% | 75.0% | 91.1% | 75.0% |
| stripe_0.18 | short | 86.7% | 55.6% | 94.3% | 55.6% |
| stripe_0.18 | video:max_proj | -2.0% | 8.3% | 51.2% | 8.3% |
| stripe_0.18 | video:single_best | 75.8% | 75.0% | 90.5% | 75.0% |
| stripe_0.18 | video:temporal_mean | 56.4% | 75.0% | 95.3% | 75.0% |
| stripe_0.18 | video:window_mean_best | 36.1% | 75.0% | 91.1% | 75.0% |
| stripe_0.30 | short | 84.0% | 55.6% | 94.3% | 55.6% |
| stripe_0.30 | video:max_proj | -9.5% | 8.3% | 51.2% | 8.3% |
| stripe_0.30 | video:single_best | 79.6% | 75.0% | 90.5% | 75.0% |
| stripe_0.30 | video:temporal_mean | 31.4% | 55.0% | 95.3% | 75.0% |
| stripe_0.30 | video:window_mean_best | 40.6% | 75.0% | 91.1% | 75.0% |
| vlm | long | -5.6% | 0.0% | 10.6% | 0.0% |
| vlm | short | 90.7% | 55.6% | 94.3% | 55.6% |
| vlm | video:max_proj | 37.7% | 8.3% | 51.2% | 8.3% |
| vlm | video:single_best | 87.3% | 75.0% | 90.5% | 75.0% |
| vlm | video:temporal_mean | 34.2% | 66.7% | 95.3% | 75.0% |
| vlm | video:window_mean_best | 76.4% | 75.0% | 91.1% | 75.0% |
