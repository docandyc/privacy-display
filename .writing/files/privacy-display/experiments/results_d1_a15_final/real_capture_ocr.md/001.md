# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 22.7% | 14.8% | 88.8% | 27.8% |
| anti_ocr|short | 108 | 4.6% | 0.0% | 7.6% | 5.6% |
| anti_ocr|video|max_proj | 36 | 61.6% | 5.6% | 65.9% | 77.8% |
| anti_ocr|video|single_best | 36 | 14.2% | 0.0% | 17.1% | 16.7% |
| anti_ocr|video|temporal_mean | 36 | 62.6% | 27.8% | 75.6% | 77.8% |
| anti_ocr|video|window_mean_best | 36 | 53.7% | 11.1% | 60.8% | 75.0% |
| deployed|long | 108 | 24.0% | 13.9% | 86.4% | 29.6% |
| deployed|short | 153 | 4.5% | 0.0% | 7.7% | 4.6% |
| deployed|video|max_proj | 51 | 51.4% | 7.8% | 59.7% | 66.7% |
| deployed|video|single_best | 51 | 10.7% | 0.0% | 18.6% | 15.7% |
| deployed|video|temporal_mean | 51 | 46.1% | 13.7% | 67.8% | 64.7% |
| deployed|video|window_mean_best | 51 | 40.9% | 3.9% | 47.5% | 64.7% |
| glyph_0.00|short | 45 | 3.4% | 0.0% | 3.0% | 0.0% |
| glyph_0.00|video|max_proj | 15 | 57.6% | 13.3% | 51.4% | 80.0% |
| glyph_0.00|video|single_best | 15 | 5.5% | 0.0% | 7.4% | 0.0% |
| glyph_0.00|video|temporal_mean | 15 | 51.0% | 20.0% | 55.1% | 73.3% |
| glyph_0.00|video|window_mean_best | 15 | 35.8% | 0.0% | 24.1% | 53.3% |
| glyph_0.12|short | 45 | 2.6% | 0.0% | 1.2% | 0.0% |
| glyph_0.12|video|max_proj | 15 | 46.8% | 6.7% | 51.4% | 60.0% |
| glyph_0.12|video|single_best | 15 | 5.4% | 0.0% | 14.4% | 6.7% |
| glyph_0.12|video|temporal_mean | 15 | 50.3% | 6.7% | 51.9% | 73.3% |
| glyph_0.12|video|window_mean_best | 15 | 40.3% | 6.7% | 39.9% | 53.3% |
| glyph_0.22|short | 45 | 2.3% | 0.0% | 4.1% | 0.0% |
| glyph_0.22|video|max_proj | 15 | 46.1% | 6.7% | 41.1% | 60.0% |
| glyph_0.22|video|single_best | 15 | 7.7% | 0.0% | 3.7% | 13.3% |
| glyph_0.22|video|temporal_mean | 15 | 49.2% | 6.7% | 51.0% | 60.0% |
| glyph_0.22|video|window_mean_best | 15 | 45.4% | 20.0% | 28.3% | 73.3% |
| inversion_0.0|long | 45 | 33.9% | 17.8% | 85.0% | 44.4% |
| inversion_0.0|video|max_proj | 15 | 53.2% | 6.7% | 55.3% | 73.3% |
| inversion_0.0|video|single_best | 15 | 7.4% | 0.0% | 6.8% | 6.7% |
| inversion_0.0|video|temporal_mean | 15 | 62.5% | 33.3% | 60.2% | 86.7% |
| inversion_0.0|video|window_mean_best | 15 | 38.4% | 6.7% | 40.9% | 60.0% |
| inversion_0.2|long | 45 | 35.1% | 11.1% | 81.8% | 46.7% |
| inversion_0.2|video|max_proj | 15 | 44.8% | 6.7% | 59.3% | 66.7% |
| inversion_0.2|video|single_best | 15 | 13.9% | 6.7% | 26.0% | 13.3% |
| inversion_0.2|video|temporal_mean | 15 | 55.6% | 40.0% | 53.9% | 73.3% |
| inversion_0.2|video|window_mean_best | 15 | 33.3% | 6.7% | 30.7% | 53.3% |
| inversion_0.3|long | 45 | 27.7% | 13.3% | 81.7% | 40.0% |
| inversion_0.3|video|max_proj | 15 | 45.2% | 6.7% | 50.6% | 60.0% |
| inversion_0.3|video|single_best | 15 | 10.4% | 0.0% | 9.5% | 13.3% |
| inversion_0.3|video|temporal_mean | 15 | 45.0% | 20.0% | 41.2% | 66.7% |
| inversion_0.3|video|window_mean_best | 15 | 25.1% | 6.7% | 36.5% | 46.7% |
| inversion_0.5|long | 45 | 27.4% | 4.4% | 71.0% | 40.0% |
| inversion_0.5|video|max_proj | 15 | 24.0% | 0.0% | 42.3% | 40.0% |
| inversion_0.5|video|single_best | 15 | 4.3% | 0.0% | 4.0% | 0.0% |
| inversion_0.5|video|temporal_mean | 15 | 51.3% | 20.0% | 52.5% | 73.3% |
| inversion_0.5|video|window_mean_best | 15 | 34.4% | 13.3% | 36.0% | 60.0% |
| inversion_1.0|long | 45 | 4.9% | 0.0% | 27.6% | 6.7% |
| inversion_1.0|video|max_proj | 15 | 46.0% | 6.7% | 28.7% | 60.0% |
| inversion_1.0|video|single_best | 15 | 70.9% | 40.0% | 64.5% | 80.0% |
| inversion_1.0|video|temporal_mean | 15 | 15.4% | 0.0% | 15.7% | 33.3% |
| inversion_1.0|video|window_mean_best | 15 | 44.1% | 20.0% | 37.9% | 66.7% |
| mask_noise|long | 108 | 24.7% | 15.7% | 85.2% | 28.7% |
| mask_noise|short | 108 | 9.8% | 1.9% | 12.3% | 12.0% |
| mask_noise|video|max_proj | 36 | 62.2% | 13.9% | 68.3% | 80.6% |
| mask_noise|video|single_best | 36 | 10.9% | 0.0% | 9.1% | 19.4% |
| mask_noise|video|temporal_mean | 36 | 54.0% | 19.4% | 69.1% | 72.2% |
| mask_noise|video|window_mean_best | 36 | 50.9% | 5.6% | 59.8% | 69.4% |
| mask_only|long | 108 | 28.6% | 14.8% | 89.1% | 35.2% |
| mask_only|short | 108 | 7.8% | 0.0% | 7.2% | 10.2% |
| mask_only|video|max_proj | 36 | 53.1% | 5.6% | 68.9% | 63.9% |
| mask_only|video|single_best | 36 | 13.4% | 0.0% | 16.3% | 22.2% |
| mask_only|video|temporal_mean | 36 | 57.8% | 19.4% | 71.5% | 72.2% |
| mask_only|video|window_mean_best | 36 | 43.3% | 2.8% | 51.0% | 63.9% |
| original|long | 108 | 19.4% | 7.4% | 73.5% | 23.1% |
| original|short | 108 | 75.2% | 38.9% | 90.6% | 82.4% |
| original|video|max_proj | 36 | 47.0% | 13.9% | 47.1% | 63.9% |
| original|video|single_best | 36 | 80.1% | 50.0% | 77.1% | 88.9% |
| original|video|temporal_mean | 36 | 65.2% | 30.6% | 78.4% | 75.0% |
| original|video|window_mean_best | 36 | 80.7% | 52.8% | 77.8% | 88.9% |
| stripe_0.00|short | 45 | 2.1% | 0.0% | 0.4% | 0.0% |
| stripe_0.00|video|max_proj | 15 | 46.1% | 6.7% | 46.5% | 73.3% |
| stripe_0.00|video|single_best | 15 | 12.9% | 0.0% | 10.1% | 13.3% |
| stripe_0.00|video|temporal_mean | 15 | 53.2% | 20.0% | 52.1% | 80.0% |
| stripe_0.00|video|window_mean_best | 15 | 39.7% | 6.7% | 44.2% | 60.0% |
| stripe_0.10|short | 45 | 3.7% | 0.0% | 3.7% | 0.0% |
| stripe_0.10|video|max_proj | 15 | 47.7% | 6.7% | 60.0% | 60.0% |
| stripe_0.10|video|single_best | 15 | 3.9% | 0.0% | 0.5% | 0.0% |
| stripe_0.10|video|temporal_mean | 15 | 53.4% | 33.3% | 53.9% | 73.3% |
| stripe_0.10|video|window_mean_best | 15 | 29.0% | 6.7% | 30.3% | 53.3% |
| stripe_0.18|short | 45 | 2.8% | 0.0% | 2.6% | 0.0% |
| stripe_0.18|video|max_proj | 15 | 37.9% | 0.0% | 59.7% | 53.3% |
| stripe_0.18|video|single_best | 15 | 4.4% | 0.0% | 0.5% | 0.0% |
| stripe_0.18|video|temporal_mean | 15 | 52.2% | 20.0% | 53.5% | 73.3% |
| stripe_0.18|video|window_mean_best | 15 | 41.1% | 0.0% | 48.1% | 60.0% |
| stripe_0.30|short | 45 | 3.1% | 0.0% | 2.1% | 0.0% |
| stripe_0.30|video|max_proj | 15 | 40.5% | 0.0% | 53.4% | 53.3% |
| stripe_0.30|video|single_best | 15 | 9.2% | 0.0% | 0.6% | 13.3% |
| stripe_0.30|video|temporal_mean | 15 | 53.3% | 26.7% | 51.9% | 66.7% |
| stripe_0.30|video|window_mean_best | 15 | 35.0% | 0.0% | 32.0% | 53.3% |
| vlm|long | 108 | 1.2% | 0.0% | 15.7% | 0.9% |
| vlm|short | 108 | 2.5% | 0.0% | 1.7% | 0.9% |
| vlm|video|max_proj | 36 | 7.1% | 0.0% | 12.6% | 5.6% |
| vlm|video|single_best | 36 | 2.2% | 0.0% | 3.4% | 0.0% |
| vlm|video|temporal_mean | 36 | 28.0% | 5.6% | 21.6% | 44.4% |
| vlm|video|window_mean_best | 36 | 13.1% | 0.0% | 10.6% | 22.2% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 59.2% | 44.4% | 99.2% | 63.9% |
| anti_ocr | short | 36 | 13.2% | 0.0% | 22.3% | 16.7% |
| anti_ocr | video:max_proj | 12 | 85.5% | 16.7% | 89.3% | 100.0% |
| anti_ocr | video:single_best | 12 | 26.6% | 0.0% | 51.1% | 25.0% |
| anti_ocr | video:temporal_mean | 12 | 90.7% | 58.3% | 94.9% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 80.2% | 33.3% | 92.2% | 100.0% |
| deployed | long | 36 | 65.8% | 41.7% | 98.9% | 72.2% |
| deployed | short | 51 | 11.7% | 0.0% | 23.1% | 11.8% |
| deployed | video:max_proj | 17 | 77.2% | 23.5% | 80.0% | 88.2% |
| deployed | video:single_best | 17 | 23.2% | 0.0% | 52.8% | 35.3% |
| deployed | video:temporal_mean | 17 | 80.8% | 29.4% | 90.0% | 100.0% |
| deployed | video:window_mean_best | 17 | 68.8% | 11.8% | 86.4% | 94.1% |
| glyph_0.00 | short | 15 | 7.8% | 0.0% | 9.0% | 0.0% |
| glyph_0.00 | video:max_proj | 5 | 74.1% | 40.0% | 80.2% | 100.0% |
| glyph_0.00 | video:single_best | 5 | 12.6% | 0.0% | 21.4% | 0.0% |
| glyph_0.00 | video:temporal_mean | 5 | 81.6% | 60.0% | 85.4% | 100.0% |
| glyph_0.00 | video:window_mean_best | 5 | 71.4% | 0.0% | 53.5% | 80.0% |
| glyph_0.12 | short | 15 | 6.6% | 0.0% | 3.3% | 0.0% |
| glyph_0.12 | video:max_proj | 5 | 69.9% | 20.0% | 80.0% | 80.0% |
| glyph_0.12 | video:single_best | 5 | 13.3% | 0.0% | 43.3% | 20.0% |
| glyph_0.12 | video:temporal_mean | 5 | 79.3% | 20.0% | 84.4% | 100.0% |
| glyph_0.12 | video:window_mean_best | 5 | 75.7% | 20.0% | 78.3% | 100.0% |
| glyph_0.22 | short | 15 | 6.6% | 0.0% | 12.4% | 0.0% |
| glyph_0.22 | video:max_proj | 5 | 68.1% | 20.0% | 54.0% | 80.0% |
| glyph_0.22 | video:single_best | 5 | 14.4% | 0.0% | 11.2% | 20.0% |
| glyph_0.22 | video:temporal_mean | 5 | 80.0% | 20.0% | 81.4% | 100.0% |
| glyph_0.22 | video:window_mean_best | 5 | 74.5% | 60.0% | 79.0% | 80.0% |
| inversion_0.0 | long | 15 | 87.4% | 53.3% | 96.3% | 100.0% |
| inversion_0.0 | video:max_proj | 5 | 72.9% | 20.0% | 78.5% | 100.0% |
| inversion_0.0 | video:single_best | 5 | 19.5% | 0.0% | 20.5% | 20.0% |
| inversion_0.0 | video:temporal_mean | 5 | 86.8% | 80.0% | 87.0% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 57.2% | 20.0% | 77.4% | 80.0% |
| inversion_0.2 | long | 15 | 76.1% | 33.3% | 98.0% | 86.7% |
| inversion_0.2 | video:max_proj | 5 | 70.1% | 20.0% | 78.3% | 100.0% |
| inversion_0.2 | video:single_best | 5 | 28.3% | 20.0% | 72.6% | 40.0% |
| inversion_0.2 | video:temporal_mean | 5 | 83.8% | 80.0% | 84.7% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 60.3% | 20.0% | 78.3% | 80.0% |
| inversion_0.3 | long | 15 | 68.2% | 40.0% | 97.4% | 80.0% |
| inversion_0.3 | video:max_proj | 5 | 65.7% | 20.0% | 74.7% | 80.0% |
| inversion_0.3 | video:single_best | 5 | 25.2% | 0.0% | 28.3% | 20.0% |
| inversion_0.3 | video:temporal_mean | 5 | 83.5% | 60.0% | 84.0% | 100.0% |
| inversion_0.3 | video:window_mean_best | 5 | 51.5% | 20.0% | 79.0% | 80.0% |
| inversion_0.5 | long | 15 | 69.3% | 13.3% | 96.5% | 80.0% |
| inversion_0.5 | video:max_proj | 5 | 58.3% | 0.0% | 78.3% | 100.0% |
| inversion_0.5 | video:single_best | 5 | 10.7% | 0.0% | 6.2% | 0.0% |
| inversion_0.5 | video:temporal_mean | 5 | 82.7% | 60.0% | 83.0% | 100.0% |
| inversion_0.5 | video:window_mean_best | 5 | 62.7% | 40.0% | 79.0% | 100.0% |
| inversion_1.0 | long | 15 | 13.1% | 0.0% | 70.0% | 20.0% |
| inversion_1.0 | video:max_proj | 5 | 76.6% | 20.0% | 50.0% | 80.0% |
| inversion_1.0 | video:single_best | 5 | 77.8% | 80.0% | 76.4% | 80.0% |
| inversion_1.0 | video:temporal_mean | 5 | 40.6% | 0.0% | 45.4% | 100.0% |
| inversion_1.0 | video:window_mean_best | 5 | 77.0% | 60.0% | 78.3% | 100.0% |
| mask_noise | long | 36 | 65.6% | 47.2% | 92.6% | 72.2% |
| mask_noise | short | 36 | 20.5% | 5.6% | 32.5% | 19.4% |
| mask_noise | video:max_proj | 12 | 85.7% | 41.7% | 92.2% | 100.0% |
| mask_noise | video:single_best | 12 | 26.5% | 0.0% | 25.8% | 58.3% |
| mask_noise | video:temporal_mean | 12 | 88.8% | 50.0% | 95.4% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 78.9% | 16.7% | 92.7% | 91.7% |
| mask_only | long | 36 | 75.6% | 44.4% | 99.6% | 83.3% |
| mask_only | short | 36 | 18.4% | 0.0% | 21.5% | 22.2% |
| mask_only | video:max_proj | 12 | 83.3% | 16.7% | 93.1% | 91.7% |
| mask_only | video:single_best | 12 | 29.7% | 0.0% | 45.1% | 41.7% |
| mask_only | video:temporal_mean | 12 | 88.6% | 33.3% | 95.6% | 100.0% |
| mask_only | video:window_mean_best | 12 | 70.7% | 8.3% | 89.5% | 100.0% |
| original | long | 36 | 52.9% | 22.2% | 98.5% | 61.1% |
| original | short | 36 | 96.4% | 77.8% | 99.9% | 100.0% |
| original | video:max_proj | 12 | 80.4% | 33.3% | 83.1% | 91.7% |
| original | video:single_best | 12 | 91.9% | 75.0% | 86.0% | 100.0% |
| original | video:temporal_mean | 12 | 85.9% | 58.3% | 87.5% | 91.7% |
| original | video:window_mean_best | 12 | 94.4% | 83.3% | 86.8% | 100.0% |
| stripe_0.00 | short | 15 | 6.4% | 0.0% | 1.1% | 0.0% |
| stripe_0.00 | video:max_proj | 5 | 64.2% | 20.0% | 79.7% | 100.0% |
| stripe_0.00 | video:single_best | 5 | 31.9% | 0.0% | 29.8% | 40.0% |
| stripe_0.00 | video:temporal_mean | 5 | 83.3% | 60.0% | 84.0% | 100.0% |
| stripe_0.00 | video:window_mean_best | 5 | 63.8% | 20.0% | 78.3% | 100.0% |
| stripe_0.10 | short | 15 | 9.4% | 0.0% | 11.0% | 0.0% |
| stripe_0.10 | video:max_proj | 5 | 70.9% | 20.0% | 79.2% | 80.0% |
| stripe_0.10 | video:single_best | 5 | 10.2% | 0.0% | 0.9% | 0.0% |
| stripe_0.10 | video:temporal_mean | 5 | 84.5% | 80.0% | 84.7% | 100.0% |
| stripe_0.10 | video:window_mean_best | 5 | 56.3% | 20.0% | 78.8% | 80.0% |
| stripe_0.18 | short | 15 | 8.3% | 0.0% | 7.8% | 0.0% |
| stripe_0.18 | video:max_proj | 5 | 70.7% | 0.0% | 79.5% | 80.0% |
| stripe_0.18 | video:single_best | 5 | 10.6% | 0.0% | 1.2% | 0.0% |
| stripe_0.18 | video:temporal_mean | 5 | 77.6% | 60.0% | 83.7% | 100.0% |
| stripe_0.18 | video:window_mean_best | 5 | 70.8% | 0.0% | 78.5% | 100.0% |
| stripe_0.30 | short | 15 | 9.4% | 0.0% | 6.3% | 0.0% |
| stripe_0.30 | video:max_proj | 5 | 68.4% | 0.0% | 79.2% | 80.0% |
| stripe_0.30 | video:single_best | 5 | 23.0% | 0.0% | 0.9% | 40.0% |
| stripe_0.30 | video:temporal_mean | 5 | 79.0% | 60.0% | 82.3% | 100.0% |
| stripe_0.30 | video:window_mean_best | 5 | 73.3% | 0.0% | 75.9% | 100.0% |
| vlm | long | 36 | 3.2% | 0.0% | 46.8% | 2.8% |
| vlm | short | 36 | 6.2% | 0.0% | 5.0% | 2.8% |
| vlm | video:max_proj | 12 | 17.0% | 0.0% | 37.7% | 16.7% |
| vlm | video:single_best | 12 | 6.0% | 0.0% | 9.9% | 0.0% |
| vlm | video:temporal_mean | 12 | 63.2% | 16.7% | 62.4% | 83.3% |
| vlm | video:window_mean_best | 12 | 32.4% | 0.0% | 31.8% | 58.3% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | -6.2% | -22.2% | 52.9% | 22.2% |
| anti_ocr | short | 83.2% | 77.8% | 96.4% | 77.8% |
| anti_ocr | video:max_proj | -5.1% | 16.7% | 80.4% | 33.3% |
| anti_ocr | video:single_best | 65.3% | 75.0% | 91.9% | 75.0% |
| anti_ocr | video:temporal_mean | -4.7% | 0.0% | 85.9% | 58.3% |
| anti_ocr | video:window_mean_best | 14.2% | 50.0% | 94.4% | 83.3% |
| deployed | long | -12.9% | -19.4% | 52.9% | 22.2% |
| deployed | short | 84.7% | 77.8% | 96.4% | 77.8% |
| deployed | video:max_proj | 3.1% | 9.8% | 80.4% | 33.3% |
| deployed | video:single_best | 68.7% | 75.0% | 91.9% | 75.0% |
| deployed | video:temporal_mean | 5.2% | 28.9% | 85.9% | 58.3% |
| deployed | video:window_mean_best | 25.6% | 71.6% | 94.4% | 83.3% |
| glyph_0.00 | short | 88.6% | 77.8% | 96.4% | 77.8% |
| glyph_0.00 | video:max_proj | 6.3% | -6.7% | 80.4% | 33.3% |
| glyph_0.00 | video:single_best | 79.3% | 75.0% | 91.9% | 75.0% |
| glyph_0.00 | video:temporal_mean | 4.3% | -1.7% | 85.9% | 58.3% |
| glyph_0.00 | video:window_mean_best | 23.0% | 83.3% | 94.4% | 83.3% |
| glyph_0.12 | short | 89.7% | 77.8% | 96.4% | 77.8% |
| glyph_0.12 | video:max_proj | 10.5% | 13.3% | 80.4% | 33.3% |
| glyph_0.12 | video:single_best | 78.7% | 75.0% | 91.9% | 75.0% |
| glyph_0.12 | video:temporal_mean | 6.7% | 38.3% | 85.9% | 58.3% |
| glyph_0.12 | video:window_mean_best | 18.7% | 63.3% | 94.4% | 83.3% |
| glyph_0.22 | short | 89.7% | 77.8% | 96.4% | 77.8% |
| glyph_0.22 | video:max_proj | 12.3% | 13.3% | 80.4% | 33.3% |
| glyph_0.22 | video:single_best | 77.5% | 75.0% | 91.9% | 75.0% |
| glyph_0.22 | video:temporal_mean | 6.0% | 38.3% | 85.9% | 58.3% |
| glyph_0.22 | video:window_mean_best | 19.9% | 23.3% | 94.4% | 83.3% |
| inversion_0.0 | long | -34.5% | -31.1% | 52.9% | 22.2% |
| inversion_0.0 | video:max_proj | 7.5% | 13.3% | 80.4% | 33.3% |
| inversion_0.0 | video:single_best | 72.4% | 75.0% | 91.9% | 75.0% |
| inversion_0.0 | video:temporal_mean | -0.9% | -21.7% | 85.9% | 58.3% |
| inversion_0.0 | video:window_mean_best | 37.1% | 63.3% | 94.4% | 83.3% |
| inversion_0.2 | long | -23.1% | -11.1% | 52.9% | 22.2% |
| inversion_0.2 | video:max_proj | 10.3% | 13.3% | 80.4% | 33.3% |
| inversion_0.2 | video:single_best | 63.6% | 55.0% | 91.9% | 75.0% |
| inversion_0.2 | video:temporal_mean | 2.2% | -21.7% | 85.9% | 58.3% |
| inversion_0.2 | video:window_mean_best | 34.1% | 63.3% | 94.4% | 83.3% |
| inversion_0.3 | long | -15.2% | -17.8% | 52.9% | 22.2% |
| inversion_0.3 | video:max_proj | 14.7% | 13.3% | 80.4% | 33.3% |
| inversion_0.3 | video:single_best | 66.7% | 75.0% | 91.9% | 75.0% |
| inversion_0.3 | video:temporal_mean | 2.4% | -1.7% | 85.9% | 58.3% |
| inversion_0.3 | video:window_mean_best | 42.9% | 63.3% | 94.4% | 83.3% |
| inversion_0.5 | long | -16.3% | 8.9% | 52.9% | 22.2% |
| inversion_0.5 | video:max_proj | 22.1% | 33.3% | 80.4% | 33.3% |
| inversion_0.5 | video:single_best | 81.2% | 75.0% | 91.9% | 75.0% |
| inversion_0.5 | video:temporal_mean | 3.2% | -1.7% | 85.9% | 58.3% |
| inversion_0.5 | video:window_mean_best | 31.7% | 43.3% | 94.4% | 83.3% |
| inversion_1.0 | long | 39.8% | 22.2% | 52.9% | 22.2% |
| inversion_1.0 | video:max_proj | 3.8% | 13.3% | 80.4% | 33.3% |
| inversion_1.0 | video:single_best | 14.2% | -5.0% | 91.9% | 75.0% |
| inversion_1.0 | video:temporal_mean | 45.3% | 58.3% | 85.9% | 58.3% |
| inversion_1.0 | video:window_mean_best | 17.3% | 23.3% | 94.4% | 83.3% |
| mask_noise | long | -12.6% | -25.0% | 52.9% | 22.2% |
| mask_noise | short | 75.9% | 72.2% | 96.4% | 77.8% |
| mask_noise | video:max_proj | -5.4% | -8.3% | 80.4% | 33.3% |
| mask_noise | video:single_best | 65.4% | 75.0% | 91.9% | 75.0% |
| mask_noise | video:temporal_mean | -2.9% | 8.3% | 85.9% | 58.3% |
| mask_noise | video:window_mean_best | 15.4% | 66.7% | 94.4% | 83.3% |
| mask_only | long | -22.7% | -22.2% | 52.9% | 22.2% |
| mask_only | short | 78.0% | 77.8% | 96.4% | 77.8% |
| mask_only | video:max_proj | -2.9% | 16.7% | 80.4% | 33.3% |
| mask_only | video:single_best | 62.2% | 75.0% | 91.9% | 75.0% |
| mask_only | video:temporal_mean | -2.6% | 25.0% | 85.9% | 58.3% |
| mask_only | video:window_mean_best | 23.7% | 75.0% | 94.4% | 83.3% |
| original | long | 0.0% | 0.0% | 52.9% | 22.2% |
| original | short | 0.0% | 0.0% | 96.4% | 77.8% |
| original | video:max_proj | 0.0% | 0.0% | 80.4% | 33.3% |
| original | video:single_best | 0.0% | 0.0% | 91.9% | 75.0% |
| original | video:temporal_mean | 0.0% | 0.0% | 85.9% | 58.3% |
| original | video:window_mean_best | 0.0% | 0.0% | 94.4% | 83.3% |
| stripe_0.00 | short | 90.0% | 77.8% | 96.4% | 77.8% |
| stripe_0.00 | video:max_proj | 16.2% | 13.3% | 80.4% | 33.3% |
| stripe_0.00 | video:single_best | 60.1% | 75.0% | 91.9% | 75.0% |
| stripe_0.00 | video:temporal_mean | 2.6% | -1.7% | 85.9% | 58.3% |
| stripe_0.00 | video:window_mean_best | 30.6% | 63.3% | 94.4% | 83.3% |
| stripe_0.10 | short | 87.0% | 77.8% | 96.4% | 77.8% |
| stripe_0.10 | video:max_proj | 9.5% | 13.3% | 80.4% | 33.3% |
| stripe_0.10 | video:single_best | 81.8% | 75.0% | 91.9% | 75.0% |
| stripe_0.10 | video:temporal_mean | 1.4% | -21.7% | 85.9% | 58.3% |
| stripe_0.10 | video:window_mean_best | 38.1% | 63.3% | 94.4% | 83.3% |
| stripe_0.18 | short | 88.1% | 77.8% | 96.4% | 77.8% |
| stripe_0.18 | video:max_proj | 9.7% | 33.3% | 80.4% | 33.3% |
| stripe_0.18 | video:single_best | 81.3% | 75.0% | 91.9% | 75.0% |
| stripe_0.18 | video:temporal_mean | 8.3% | -1.7% | 85.9% | 58.3% |
| stripe_0.18 | video:window_mean_best | 23.6% | 83.3% | 94.4% | 83.3% |
| stripe_0.30 | short | 87.0% | 77.8% | 96.4% | 77.8% |
| stripe_0.30 | video:max_proj | 12.0% | 33.3% | 80.4% | 33.3% |
| stripe_0.30 | video:single_best | 69.0% | 75.0% | 91.9% | 75.0% |
| stripe_0.30 | video:temporal_mean | 7.0% | -1.7% | 85.9% | 58.3% |
| stripe_0.30 | video:window_mean_best | 21.1% | 83.3% | 94.4% | 83.3% |
| vlm | long | 49.8% | 22.2% | 52.9% | 22.2% |
| vlm | short | 90.1% | 77.8% | 96.4% | 77.8% |
| vlm | video:max_proj | 63.4% | 33.3% | 80.4% | 33.3% |
| vlm | video:single_best | 85.9% | 75.0% | 91.9% | 75.0% |
| vlm | video:temporal_mean | 22.7% | 41.7% | 85.9% | 58.3% |
| vlm | video:window_mean_best | 62.0% | 83.3% | 94.4% | 83.3% |
