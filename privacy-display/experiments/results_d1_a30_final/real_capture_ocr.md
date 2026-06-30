# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 21.3% | 12.0% | 89.8% | 26.9% |
| anti_ocr|short | 108 | 5.9% | 0.0% | 12.3% | 7.4% |
| anti_ocr|video|max_proj | 36 | 57.8% | 16.7% | 74.7% | 69.4% |
| anti_ocr|video|single_best | 36 | 13.1% | 0.0% | 24.0% | 19.4% |
| anti_ocr|video|temporal_mean | 36 | 65.2% | 30.6% | 74.8% | 80.6% |
| anti_ocr|video|window_mean_best | 36 | 54.9% | 8.3% | 63.8% | 72.2% |
| deployed|long | 108 | 16.4% | 12.0% | 88.1% | 20.4% |
| deployed|short | 153 | 5.1% | 0.0% | 9.3% | 6.5% |
| deployed|video|max_proj | 51 | 53.5% | 2.0% | 67.4% | 66.7% |
| deployed|video|single_best | 51 | 14.6% | 0.0% | 20.9% | 27.5% |
| deployed|video|temporal_mean | 51 | 50.2% | 17.6% | 68.1% | 68.6% |
| deployed|video|window_mean_best | 51 | 42.3% | 3.9% | 60.0% | 60.8% |
| glyph_0.00|short | 45 | 2.6% | 0.0% | 5.8% | 2.2% |
| glyph_0.00|video|max_proj | 15 | 42.1% | 6.7% | 59.3% | 66.7% |
| glyph_0.00|video|single_best | 15 | 12.8% | 0.0% | 24.1% | 26.7% |
| glyph_0.00|video|temporal_mean | 15 | 61.6% | 26.7% | 60.0% | 86.7% |
| glyph_0.00|video|window_mean_best | 15 | 31.1% | 0.0% | 56.3% | 46.7% |
| glyph_0.12|short | 45 | 3.0% | 0.0% | 5.8% | 4.4% |
| glyph_0.12|video|max_proj | 15 | 58.5% | 0.0% | 51.3% | 86.7% |
| glyph_0.12|video|single_best | 15 | 15.6% | 0.0% | 25.5% | 20.0% |
| glyph_0.12|video|temporal_mean | 15 | 65.6% | 26.7% | 57.1% | 93.3% |
| glyph_0.12|video|window_mean_best | 15 | 36.2% | 0.0% | 45.7% | 60.0% |
| glyph_0.22|short | 45 | 3.6% | 0.0% | 7.5% | 6.7% |
| glyph_0.22|video|max_proj | 15 | 47.8% | 0.0% | 59.4% | 66.7% |
| glyph_0.22|video|single_best | 15 | 19.8% | 0.0% | 25.9% | 26.7% |
| glyph_0.22|video|temporal_mean | 15 | 55.5% | 26.7% | 57.2% | 80.0% |
| glyph_0.22|video|window_mean_best | 15 | 43.0% | 13.3% | 41.4% | 66.7% |
| inversion_0.0|long | 45 | 27.2% | 15.6% | 83.3% | 40.0% |
| inversion_0.0|video|max_proj | 15 | 53.9% | 0.0% | 57.5% | 73.3% |
| inversion_0.0|video|single_best | 15 | 7.0% | 0.0% | 6.6% | 13.3% |
| inversion_0.0|video|temporal_mean | 15 | 51.6% | 20.0% | 63.4% | 73.3% |
| inversion_0.0|video|window_mean_best | 15 | 31.2% | 6.7% | 52.9% | 53.3% |
| inversion_0.2|long | 45 | 26.7% | 11.1% | 79.7% | 35.6% |
| inversion_0.2|video|max_proj | 15 | 39.4% | 0.0% | 37.7% | 66.7% |
| inversion_0.2|video|single_best | 15 | 2.7% | 0.0% | 0.3% | 0.0% |
| inversion_0.2|video|temporal_mean | 15 | 63.4% | 26.7% | 61.5% | 86.7% |
| inversion_0.2|video|window_mean_best | 15 | 31.2% | 0.0% | 44.0% | 40.0% |
| inversion_0.3|long | 45 | 25.8% | 11.1% | 81.8% | 37.8% |
| inversion_0.3|video|max_proj | 15 | 38.0% | 0.0% | 59.5% | 53.3% |
| inversion_0.3|video|single_best | 15 | 11.1% | 0.0% | 13.6% | 20.0% |
| inversion_0.3|video|temporal_mean | 15 | 54.2% | 6.7% | 60.5% | 80.0% |
| inversion_0.3|video|window_mean_best | 15 | 29.7% | 6.7% | 56.8% | 46.7% |
| inversion_0.5|long | 45 | 21.7% | 4.4% | 80.5% | 28.9% |
| inversion_0.5|video|max_proj | 15 | 26.7% | 0.0% | 35.6% | 40.0% |
| inversion_0.5|video|single_best | 15 | 3.9% | 0.0% | 8.4% | 6.7% |
| inversion_0.5|video|temporal_mean | 15 | 46.1% | 26.7% | 60.0% | 66.7% |
| inversion_0.5|video|window_mean_best | 15 | 43.8% | 13.3% | 44.1% | 73.3% |
| inversion_1.0|long | 45 | 2.1% | 0.0% | 28.5% | 6.7% |
| inversion_1.0|video|max_proj | 15 | 42.6% | 0.0% | 26.3% | 53.3% |
| inversion_1.0|video|single_best | 15 | 57.4% | 13.3% | 41.1% | 73.3% |
| inversion_1.0|video|temporal_mean | 15 | 19.5% | 0.0% | 14.8% | 26.7% |
| inversion_1.0|video|window_mean_best | 15 | 34.6% | 6.7% | 46.7% | 60.0% |
| mask_noise|long | 108 | 29.7% | 16.7% | 89.9% | 36.1% |
| mask_noise|short | 108 | 6.8% | 0.0% | 12.2% | 11.1% |
| mask_noise|video|max_proj | 36 | 55.3% | 5.6% | 66.7% | 66.7% |
| mask_noise|video|single_best | 36 | 13.1% | 0.0% | 19.6% | 27.8% |
| mask_noise|video|temporal_mean | 36 | 55.7% | 19.4% | 70.8% | 75.0% |
| mask_noise|video|window_mean_best | 36 | 49.8% | 5.6% | 66.0% | 66.7% |
| mask_only|long | 108 | 23.9% | 13.0% | 87.4% | 30.6% |
| mask_only|short | 108 | 5.3% | 0.0% | 9.9% | 4.6% |
| mask_only|video|max_proj | 36 | 50.9% | 8.3% | 62.4% | 63.9% |
| mask_only|video|single_best | 36 | 11.1% | 0.0% | 18.9% | 19.4% |
| mask_only|video|temporal_mean | 36 | 57.3% | 13.9% | 70.5% | 75.0% |
| mask_only|video|window_mean_best | 36 | 47.9% | 8.3% | 60.9% | 63.9% |
| original|long | 108 | 18.1% | 7.4% | 70.2% | 24.1% |
| original|short | 108 | 63.1% | 29.6% | 91.1% | 71.3% |
| original|video|max_proj | 36 | 42.1% | 8.3% | 51.0% | 61.1% |
| original|video|single_best | 36 | 78.7% | 41.7% | 80.9% | 88.9% |
| original|video|temporal_mean | 36 | 67.8% | 36.1% | 85.5% | 80.6% |
| original|video|window_mean_best | 36 | 78.0% | 41.7% | 80.4% | 88.9% |
| stripe_0.00|short | 45 | 3.9% | 0.0% | 2.0% | 6.7% |
| stripe_0.00|video|max_proj | 15 | 43.1% | 6.7% | 48.1% | 60.0% |
| stripe_0.00|video|single_best | 15 | 15.7% | 0.0% | 22.9% | 26.7% |
| stripe_0.00|video|temporal_mean | 15 | 60.4% | 40.0% | 55.8% | 86.7% |
| stripe_0.00|video|window_mean_best | 15 | 34.7% | 6.7% | 55.9% | 53.3% |
| stripe_0.10|short | 45 | 3.2% | 0.0% | 6.6% | 4.4% |
| stripe_0.10|video|max_proj | 15 | 47.9% | 6.7% | 51.8% | 66.7% |
| stripe_0.10|video|single_best | 15 | 9.9% | 0.0% | 18.8% | 20.0% |
| stripe_0.10|video|temporal_mean | 15 | 67.1% | 26.7% | 59.9% | 93.3% |
| stripe_0.10|video|window_mean_best | 15 | 42.3% | 0.0% | 51.7% | 66.7% |
| stripe_0.18|short | 45 | 2.8% | 0.0% | 1.8% | 2.2% |
| stripe_0.18|video|max_proj | 15 | 40.4% | 0.0% | 56.9% | 66.7% |
| stripe_0.18|video|single_best | 15 | 8.1% | 0.0% | 21.9% | 13.3% |
| stripe_0.18|video|temporal_mean | 15 | 60.6% | 33.3% | 59.5% | 80.0% |
| stripe_0.18|video|window_mean_best | 15 | 37.5% | 0.0% | 62.6% | 60.0% |
| stripe_0.30|short | 45 | 2.4% | 0.0% | 3.3% | 0.0% |
| stripe_0.30|video|max_proj | 15 | 45.7% | 0.0% | 39.8% | 66.7% |
| stripe_0.30|video|single_best | 15 | 9.9% | 0.0% | 0.3% | 13.3% |
| stripe_0.30|video|temporal_mean | 15 | 58.4% | 26.7% | 61.6% | 80.0% |
| stripe_0.30|video|window_mean_best | 15 | 37.3% | 6.7% | 47.8% | 53.3% |
| vlm|long | 108 | 3.9% | 0.0% | 19.3% | 3.7% |
| vlm|short | 108 | 1.2% | 0.0% | 2.3% | 0.0% |
| vlm|video|max_proj | 36 | 9.2% | 0.0% | 15.4% | 11.1% |
| vlm|video|single_best | 36 | 3.3% | 0.0% | 0.4% | 5.6% |
| vlm|video|temporal_mean | 36 | 29.1% | 5.6% | 15.1% | 47.2% |
| vlm|video|window_mean_best | 36 | 12.3% | 2.8% | 10.3% | 25.0% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 56.7% | 36.1% | 99.2% | 63.9% |
| anti_ocr | short | 36 | 17.0% | 0.0% | 36.4% | 22.2% |
| anti_ocr | video:max_proj | 12 | 84.9% | 33.3% | 92.5% | 100.0% |
| anti_ocr | video:single_best | 12 | 25.8% | 0.0% | 54.0% | 33.3% |
| anti_ocr | video:temporal_mean | 12 | 88.7% | 58.3% | 94.4% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 82.0% | 25.0% | 92.5% | 91.7% |
| deployed | long | 36 | 41.5% | 36.1% | 98.3% | 47.2% |
| deployed | short | 51 | 14.5% | 0.0% | 25.7% | 19.6% |
| deployed | video:max_proj | 17 | 81.8% | 5.9% | 89.1% | 100.0% |
| deployed | video:single_best | 17 | 33.0% | 0.0% | 51.9% | 64.7% |
| deployed | video:temporal_mean | 17 | 83.9% | 35.3% | 91.5% | 100.0% |
| deployed | video:window_mean_best | 17 | 71.7% | 11.8% | 86.0% | 88.2% |
| glyph_0.00 | short | 15 | 7.9% | 0.0% | 15.6% | 6.7% |
| glyph_0.00 | video:max_proj | 5 | 71.0% | 20.0% | 78.5% | 100.0% |
| glyph_0.00 | video:single_best | 5 | 26.8% | 0.0% | 48.1% | 60.0% |
| glyph_0.00 | video:temporal_mean | 5 | 80.8% | 60.0% | 84.0% | 100.0% |
| glyph_0.00 | video:window_mean_best | 5 | 59.4% | 0.0% | 77.8% | 80.0% |
| glyph_0.12 | short | 15 | 9.0% | 0.0% | 17.4% | 13.3% |
| glyph_0.12 | video:max_proj | 5 | 72.9% | 0.0% | 79.0% | 100.0% |
| glyph_0.12 | video:single_best | 5 | 28.9% | 0.0% | 51.2% | 20.0% |
| glyph_0.12 | video:temporal_mean | 5 | 82.2% | 80.0% | 83.5% | 100.0% |
| glyph_0.12 | video:window_mean_best | 5 | 60.2% | 0.0% | 78.3% | 80.0% |
| glyph_0.22 | short | 15 | 10.8% | 0.0% | 22.4% | 20.0% |
| glyph_0.22 | video:max_proj | 5 | 71.7% | 0.0% | 78.8% | 100.0% |
| glyph_0.22 | video:single_best | 5 | 31.2% | 0.0% | 47.1% | 40.0% |
| glyph_0.22 | video:temporal_mean | 5 | 81.7% | 80.0% | 80.7% | 100.0% |
| glyph_0.22 | video:window_mean_best | 5 | 65.7% | 40.0% | 79.2% | 100.0% |
| inversion_0.0 | long | 15 | 70.0% | 46.7% | 96.1% | 80.0% |
| inversion_0.0 | video:max_proj | 5 | 70.1% | 0.0% | 74.7% | 100.0% |
| inversion_0.0 | video:single_best | 5 | 17.7% | 0.0% | 19.5% | 40.0% |
| inversion_0.0 | video:temporal_mean | 5 | 80.8% | 60.0% | 84.7% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 61.1% | 20.0% | 79.0% | 100.0% |
| inversion_0.2 | long | 15 | 68.2% | 33.3% | 93.1% | 80.0% |
| inversion_0.2 | video:max_proj | 5 | 62.6% | 0.0% | 53.1% | 100.0% |
| inversion_0.2 | video:single_best | 5 | 7.8% | 0.0% | 0.7% | 0.0% |
| inversion_0.2 | video:temporal_mean | 5 | 80.3% | 60.0% | 83.0% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 61.0% | 0.0% | 78.8% | 80.0% |
| inversion_0.3 | long | 15 | 64.2% | 33.3% | 97.4% | 73.3% |
| inversion_0.3 | video:max_proj | 5 | 71.0% | 0.0% | 78.8% | 100.0% |
| inversion_0.3 | video:single_best | 5 | 23.8% | 0.0% | 40.5% | 40.0% |
| inversion_0.3 | video:temporal_mean | 5 | 79.4% | 20.0% | 82.3% | 100.0% |
| inversion_0.3 | video:window_mean_best | 5 | 61.9% | 20.0% | 79.0% | 80.0% |
| inversion_0.5 | long | 15 | 57.0% | 13.3% | 96.2% | 66.7% |
| inversion_0.5 | video:max_proj | 5 | 63.7% | 0.0% | 54.2% | 100.0% |
| inversion_0.5 | video:single_best | 5 | 9.7% | 0.0% | 25.2% | 20.0% |
| inversion_0.5 | video:temporal_mean | 5 | 80.4% | 60.0% | 83.5% | 100.0% |
| inversion_0.5 | video:window_mean_best | 5 | 64.7% | 40.0% | 79.0% | 100.0% |
| inversion_1.0 | long | 15 | 6.1% | 0.0% | 70.0% | 20.0% |
| inversion_1.0 | video:max_proj | 5 | 70.2% | 0.0% | 49.3% | 80.0% |
| inversion_1.0 | video:single_best | 5 | 74.9% | 40.0% | 50.2% | 80.0% |
| inversion_1.0 | video:temporal_mean | 5 | 52.1% | 0.0% | 44.5% | 80.0% |
| inversion_1.0 | video:window_mean_best | 5 | 65.3% | 20.0% | 78.3% | 100.0% |
| mask_noise | long | 36 | 74.5% | 50.0% | 99.6% | 80.6% |
| mask_noise | short | 36 | 19.6% | 0.0% | 36.0% | 33.3% |
| mask_noise | video:max_proj | 12 | 84.2% | 16.7% | 89.4% | 100.0% |
| mask_noise | video:single_best | 12 | 31.8% | 0.0% | 55.6% | 75.0% |
| mask_noise | video:temporal_mean | 12 | 88.6% | 41.7% | 94.8% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 80.7% | 16.7% | 92.3% | 91.7% |
| mask_only | long | 36 | 58.8% | 38.9% | 99.7% | 66.7% |
| mask_only | short | 36 | 15.3% | 0.0% | 29.6% | 13.9% |
| mask_only | video:max_proj | 12 | 83.4% | 16.7% | 83.5% | 100.0% |
| mask_only | video:single_best | 12 | 24.8% | 0.0% | 49.2% | 50.0% |
| mask_only | video:temporal_mean | 12 | 88.0% | 25.0% | 95.3% | 100.0% |
| mask_only | video:window_mean_best | 12 | 78.4% | 16.7% | 88.1% | 91.7% |
| original | long | 36 | 52.9% | 22.2% | 98.4% | 72.2% |
| original | short | 36 | 94.7% | 58.3% | 99.9% | 100.0% |
| original | video:max_proj | 12 | 81.8% | 25.0% | 96.4% | 100.0% |
| original | video:single_best | 12 | 93.1% | 66.7% | 94.6% | 100.0% |
| original | video:temporal_mean | 12 | 92.6% | 75.0% | 95.7% | 100.0% |
| original | video:window_mean_best | 12 | 93.8% | 83.3% | 95.3% | 100.0% |
| stripe_0.00 | short | 15 | 11.7% | 0.0% | 5.9% | 20.0% |
| stripe_0.00 | video:max_proj | 5 | 69.1% | 20.0% | 78.5% | 100.0% |
| stripe_0.00 | video:single_best | 5 | 41.6% | 0.0% | 50.9% | 80.0% |
| stripe_0.00 | video:temporal_mean | 5 | 81.0% | 80.0% | 83.3% | 100.0% |
| stripe_0.00 | video:window_mean_best | 5 | 63.6% | 20.0% | 79.0% | 100.0% |
| stripe_0.10 | short | 15 | 8.4% | 0.0% | 19.8% | 13.3% |
| stripe_0.10 | video:max_proj | 5 | 72.8% | 20.0% | 78.5% | 100.0% |
| stripe_0.10 | video:single_best | 5 | 25.6% | 0.0% | 50.9% | 60.0% |
| stripe_0.10 | video:temporal_mean | 5 | 81.7% | 40.0% | 83.7% | 100.0% |
| stripe_0.10 | video:window_mean_best | 5 | 71.4% | 0.0% | 78.3% | 100.0% |
| stripe_0.18 | short | 15 | 7.9% | 0.0% | 5.5% | 6.7% |
| stripe_0.18 | video:max_proj | 5 | 69.3% | 0.0% | 79.5% | 100.0% |
| stripe_0.18 | video:single_best | 5 | 23.1% | 0.0% | 65.5% | 40.0% |
| stripe_0.18 | video:temporal_mean | 5 | 82.1% | 80.0% | 82.1% | 100.0% |
| stripe_0.18 | video:window_mean_best | 5 | 69.4% | 0.0% | 78.3% | 100.0% |
| stripe_0.30 | short | 15 | 7.0% | 0.0% | 8.7% | 0.0% |
| stripe_0.30 | video:max_proj | 5 | 70.2% | 0.0% | 53.8% | 100.0% |
| stripe_0.30 | video:single_best | 5 | 19.2% | 0.0% | 0.5% | 40.0% |
| stripe_0.30 | video:temporal_mean | 5 | 81.0% | 60.0% | 81.1% | 100.0% |
| stripe_0.30 | video:window_mean_best | 5 | 61.0% | 20.0% | 76.7% | 80.0% |
| vlm | long | 36 | 11.5% | 0.0% | 48.0% | 11.1% |
| vlm | short | 36 | 3.1% | 0.0% | 6.8% | 0.0% |
| vlm | video:max_proj | 12 | 20.8% | 0.0% | 45.7% | 33.3% |
| vlm | video:single_best | 12 | 7.7% | 0.0% | 0.9% | 16.7% |
| vlm | video:temporal_mean | 12 | 69.4% | 16.7% | 44.8% | 100.0% |
| vlm | video:window_mean_best | 12 | 31.3% | 8.3% | 27.8% | 66.7% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | -3.8% | -13.9% | 52.9% | 22.2% |
| anti_ocr | short | 77.6% | 58.3% | 94.7% | 58.3% |
| anti_ocr | video:max_proj | -3.1% | -8.3% | 81.8% | 25.0% |
| anti_ocr | video:single_best | 67.3% | 66.7% | 93.1% | 66.7% |
| anti_ocr | video:temporal_mean | 3.9% | 16.7% | 92.6% | 75.0% |
| anti_ocr | video:window_mean_best | 11.8% | 58.3% | 93.8% | 83.3% |
| deployed | long | 11.3% | -13.9% | 52.9% | 22.2% |
| deployed | short | 80.2% | 58.3% | 94.7% | 58.3% |
| deployed | video:max_proj | -0.0% | 19.1% | 81.8% | 25.0% |
| deployed | video:single_best | 60.2% | 66.7% | 93.1% | 66.7% |
| deployed | video:temporal_mean | 8.7% | 39.7% | 92.6% | 75.0% |
| deployed | video:window_mean_best | 22.2% | 71.6% | 93.8% | 83.3% |
| glyph_0.00 | short | 86.8% | 58.3% | 94.7% | 58.3% |
| glyph_0.00 | video:max_proj | 10.8% | 5.0% | 81.8% | 25.0% |
| glyph_0.00 | video:single_best | 66.3% | 66.7% | 93.1% | 66.7% |
| glyph_0.00 | video:temporal_mean | 11.8% | 15.0% | 92.6% | 75.0% |
| glyph_0.00 | video:window_mean_best | 34.4% | 83.3% | 93.8% | 83.3% |
| glyph_0.12 | short | 85.7% | 58.3% | 94.7% | 58.3% |
| glyph_0.12 | video:max_proj | 8.9% | 25.0% | 81.8% | 25.0% |
| glyph_0.12 | video:single_best | 64.2% | 66.7% | 93.1% | 66.7% |
| glyph_0.12 | video:temporal_mean | 10.5% | -5.0% | 92.6% | 75.0% |
| glyph_0.12 | video:window_mean_best | 33.6% | 83.3% | 93.8% | 83.3% |
| glyph_0.22 | short | 83.9% | 58.3% | 94.7% | 58.3% |
| glyph_0.22 | video:max_proj | 10.1% | 25.0% | 81.8% | 25.0% |
| glyph_0.22 | video:single_best | 62.0% | 66.7% | 93.1% | 66.7% |
| glyph_0.22 | video:temporal_mean | 10.9% | -5.0% | 92.6% | 75.0% |
| glyph_0.22 | video:window_mean_best | 28.2% | 43.3% | 93.8% | 83.3% |
| inversion_0.0 | long | -17.1% | -24.4% | 52.9% | 22.2% |
| inversion_0.0 | video:max_proj | 11.6% | 25.0% | 81.8% | 25.0% |
| inversion_0.0 | video:single_best | 75.4% | 66.7% | 93.1% | 66.7% |
| inversion_0.0 | video:temporal_mean | 11.8% | 15.0% | 92.6% | 75.0% |
| inversion_0.0 | video:window_mean_best | 32.7% | 63.3% | 93.8% | 83.3% |
| inversion_0.2 | long | -15.3% | -11.1% | 52.9% | 22.2% |
| inversion_0.2 | video:max_proj | 19.2% | 25.0% | 81.8% | 25.0% |
| inversion_0.2 | video:single_best | 85.3% | 66.7% | 93.1% | 66.7% |
| inversion_0.2 | video:temporal_mean | 12.3% | 15.0% | 92.6% | 75.0% |
| inversion_0.2 | video:window_mean_best | 32.8% | 83.3% | 93.8% | 83.3% |
| inversion_0.3 | long | -11.4% | -11.1% | 52.9% | 22.2% |
| inversion_0.3 | video:max_proj | 10.8% | 25.0% | 81.8% | 25.0% |
| inversion_0.3 | video:single_best | 69.4% | 66.7% | 93.1% | 66.7% |
| inversion_0.3 | video:temporal_mean | 13.2% | 55.0% | 92.6% | 75.0% |
| inversion_0.3 | video:window_mean_best | 31.9% | 63.3% | 93.8% | 83.3% |
| inversion_0.5 | long | -4.1% | 8.9% | 52.9% | 22.2% |
| inversion_0.5 | video:max_proj | 18.1% | 25.0% | 81.8% | 25.0% |
| inversion_0.5 | video:single_best | 83.4% | 66.7% | 93.1% | 66.7% |
| inversion_0.5 | video:temporal_mean | 12.2% | 15.0% | 92.6% | 75.0% |
| inversion_0.5 | video:window_mean_best | 29.1% | 43.3% | 93.8% | 83.3% |
| inversion_1.0 | long | 46.8% | 22.2% | 52.9% | 22.2% |
| inversion_1.0 | video:max_proj | 11.5% | 25.0% | 81.8% | 25.0% |
| inversion_1.0 | video:single_best | 18.2% | 26.7% | 93.1% | 66.7% |
| inversion_1.0 | video:temporal_mean | 40.5% | 75.0% | 92.6% | 75.0% |
| inversion_1.0 | video:window_mean_best | 28.5% | 63.3% | 93.8% | 83.3% |
| mask_noise | long | -21.6% | -27.8% | 52.9% | 22.2% |
| mask_noise | short | 75.1% | 58.3% | 94.7% | 58.3% |
| mask_noise | video:max_proj | -2.4% | 8.3% | 81.8% | 25.0% |
| mask_noise | video:single_best | 61.3% | 66.7% | 93.1% | 66.7% |
| mask_noise | video:temporal_mean | 4.0% | 33.3% | 92.6% | 75.0% |
| mask_noise | video:window_mean_best | 13.1% | 66.7% | 93.8% | 83.3% |
| mask_only | long | -6.0% | -16.7% | 52.9% | 22.2% |
| mask_only | short | 79.4% | 58.3% | 94.7% | 58.3% |
| mask_only | video:max_proj | -1.6% | 8.3% | 81.8% | 25.0% |
| mask_only | video:single_best | 68.3% | 66.7% | 93.1% | 66.7% |
| mask_only | video:temporal_mean | 4.6% | 50.0% | 92.6% | 75.0% |
| mask_only | video:window_mean_best | 15.4% | 66.7% | 93.8% | 83.3% |
| original | long | 0.0% | 0.0% | 52.9% | 22.2% |
| original | short | 0.0% | 0.0% | 94.7% | 58.3% |
| original | video:max_proj | 0.0% | 0.0% | 81.8% | 25.0% |
| original | video:single_best | 0.0% | 0.0% | 93.1% | 66.7% |
| original | video:temporal_mean | 0.0% | 0.0% | 92.6% | 75.0% |
| original | video:window_mean_best | 0.0% | 0.0% | 93.8% | 83.3% |
| stripe_0.00 | short | 83.0% | 58.3% | 94.7% | 58.3% |
| stripe_0.00 | video:max_proj | 12.7% | 5.0% | 81.8% | 25.0% |
| stripe_0.00 | video:single_best | 51.5% | 66.7% | 93.1% | 66.7% |
| stripe_0.00 | video:temporal_mean | 11.6% | -5.0% | 92.6% | 75.0% |
| stripe_0.00 | video:window_mean_best | 30.3% | 63.3% | 93.8% | 83.3% |
| stripe_0.10 | short | 86.3% | 58.3% | 94.7% | 58.3% |
| stripe_0.10 | video:max_proj | 9.0% | 5.0% | 81.8% | 25.0% |
| stripe_0.10 | video:single_best | 67.6% | 66.7% | 93.1% | 66.7% |
| stripe_0.10 | video:temporal_mean | 10.9% | 35.0% | 92.6% | 75.0% |
| stripe_0.10 | video:window_mean_best | 22.4% | 83.3% | 93.8% | 83.3% |
| stripe_0.18 | short | 86.7% | 58.3% | 94.7% | 58.3% |
| stripe_0.18 | video:max_proj | 12.5% | 25.0% | 81.8% | 25.0% |
| stripe_0.18 | video:single_best | 70.0% | 66.7% | 93.1% | 66.7% |
| stripe_0.18 | video:temporal_mean | 10.5% | -5.0% | 92.6% | 75.0% |
| stripe_0.18 | video:window_mean_best | 24.4% | 83.3% | 93.8% | 83.3% |
| stripe_0.30 | short | 87.7% | 58.3% | 94.7% | 58.3% |
| stripe_0.30 | video:max_proj | 11.6% | 25.0% | 81.8% | 25.0% |
| stripe_0.30 | video:single_best | 73.9% | 66.7% | 93.1% | 66.7% |
| stripe_0.30 | video:temporal_mean | 11.6% | 15.0% | 92.6% | 75.0% |
| stripe_0.30 | video:window_mean_best | 32.9% | 63.3% | 93.8% | 83.3% |
| vlm | long | 41.4% | 22.2% | 52.9% | 22.2% |
| vlm | short | 91.6% | 58.3% | 94.7% | 58.3% |
| vlm | video:max_proj | 61.0% | 25.0% | 81.8% | 25.0% |
| vlm | video:single_best | 85.4% | 66.7% | 93.1% | 66.7% |
| vlm | video:temporal_mean | 23.2% | 58.3% | 92.6% | 75.0% |
| vlm | video:window_mean_best | 62.5% | 75.0% | 93.8% | 83.3% |
