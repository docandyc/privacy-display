# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 48.5% | 23.1% | 82.5% | 58.3% |
| anti_ocr|short | 108 | 10.0% | 0.0% | 21.7% | 22.2% |
| anti_ocr|video|max_proj | 36 | 59.2% | 19.4% | 74.9% | 69.4% |
| anti_ocr|video|single_best | 36 | 23.9% | 2.8% | 27.5% | 38.9% |
| anti_ocr|video|temporal_mean | 36 | 76.2% | 41.7% | 70.5% | 88.9% |
| anti_ocr|video|window_mean_best | 36 | 62.4% | 13.9% | 66.1% | 80.6% |
| deployed|long | 108 | 46.0% | 21.3% | 85.5% | 57.4% |
| deployed|short | 153 | 8.2% | 0.0% | 14.7% | 14.4% |
| deployed|video|max_proj | 51 | 52.9% | 5.9% | 64.9% | 64.7% |
| deployed|video|single_best | 51 | 24.4% | 0.0% | 26.6% | 49.0% |
| deployed|video|temporal_mean | 51 | 69.5% | 39.2% | 71.1% | 86.3% |
| deployed|video|window_mean_best | 51 | 59.2% | 9.8% | 64.4% | 78.4% |
| glyph_0.00|short | 45 | 3.7% | 0.0% | 3.5% | 2.2% |
| glyph_0.00|video|max_proj | 15 | 42.9% | 6.7% | 33.8% | 53.3% |
| glyph_0.00|video|single_best | 15 | 21.8% | 6.7% | 10.3% | 33.3% |
| glyph_0.00|video|temporal_mean | 15 | 45.4% | 40.0% | 38.3% | 60.0% |
| glyph_0.00|video|window_mean_best | 15 | 40.3% | 6.7% | 33.0% | 53.3% |
| glyph_0.12|short | 45 | 2.7% | 0.0% | 6.2% | 2.2% |
| glyph_0.12|video|max_proj | 15 | 39.5% | 6.7% | 42.8% | 46.7% |
| glyph_0.12|video|single_best | 15 | 12.2% | 0.0% | 8.7% | 13.3% |
| glyph_0.12|video|temporal_mean | 15 | 49.5% | 40.0% | 38.6% | 66.7% |
| glyph_0.12|video|window_mean_best | 15 | 40.7% | 13.3% | 25.5% | 53.3% |
| glyph_0.22|short | 45 | 5.5% | 0.0% | 3.6% | 8.9% |
| glyph_0.22|video|max_proj | 15 | 49.4% | 0.0% | 32.4% | 60.0% |
| glyph_0.22|video|single_best | 15 | 25.3% | 0.0% | 4.2% | 40.0% |
| glyph_0.22|video|temporal_mean | 15 | 38.7% | 26.7% | 38.5% | 46.7% |
| glyph_0.22|video|window_mean_best | 15 | 46.1% | 13.3% | 35.9% | 66.7% |
| inversion_0.0|long | 45 | 37.2% | 4.4% | 53.0% | 46.7% |
| inversion_0.0|video|max_proj | 15 | 32.1% | 0.0% | 28.6% | 40.0% |
| inversion_0.0|video|single_best | 15 | 16.2% | 0.0% | 10.6% | 20.0% |
| inversion_0.0|video|temporal_mean | 15 | 55.8% | 33.3% | 31.9% | 66.7% |
| inversion_0.0|video|window_mean_best | 15 | 46.5% | 13.3% | 28.9% | 66.7% |
| inversion_0.2|long | 45 | 31.4% | 8.9% | 46.7% | 44.4% |
| inversion_0.2|video|max_proj | 15 | 62.7% | 6.7% | 55.3% | 73.3% |
| inversion_0.2|video|single_best | 15 | 22.4% | 0.0% | 20.4% | 46.7% |
| inversion_0.2|video|temporal_mean | 15 | 62.6% | 40.0% | 61.9% | 93.3% |
| inversion_0.2|video|window_mean_best | 15 | 51.6% | 6.7% | 48.6% | 66.7% |
| inversion_0.3|long | 45 | 42.2% | 13.3% | 71.8% | 60.0% |
| inversion_0.3|video|max_proj | 15 | 54.6% | 6.7% | 51.5% | 80.0% |
| inversion_0.3|video|single_best | 15 | 39.9% | 6.7% | 27.1% | 53.3% |
| inversion_0.3|video|temporal_mean | 15 | 50.0% | 20.0% | 61.0% | 80.0% |
| inversion_0.3|video|window_mean_best | 15 | 58.4% | 20.0% | 55.3% | 80.0% |
| inversion_0.5|long | 45 | 51.8% | 26.7% | 78.8% | 64.4% |
| inversion_0.5|video|max_proj | 15 | 48.6% | 6.7% | 64.1% | 60.0% |
| inversion_0.5|video|single_best | 15 | 23.2% | 0.0% | 21.3% | 53.3% |
| inversion_0.5|video|temporal_mean | 15 | 53.6% | 33.3% | 60.4% | 73.3% |
| inversion_0.5|video|window_mean_best | 15 | 58.0% | 13.3% | 43.3% | 86.7% |
| inversion_1.0|long | 45 | 14.6% | 0.0% | 27.4% | 26.7% |
| inversion_1.0|video|max_proj | 15 | 13.9% | 6.7% | 9.7% | 20.0% |
| inversion_1.0|video|single_best | 15 | 27.2% | 20.0% | 20.5% | 33.3% |
| inversion_1.0|video|temporal_mean | 15 | 14.6% | 0.0% | 13.4% | 20.0% |
| inversion_1.0|video|window_mean_best | 15 | 36.6% | 13.3% | 21.5% | 46.7% |
| mask_noise|long | 108 | 51.9% | 23.1% | 87.5% | 63.0% |
| mask_noise|short | 108 | 15.2% | 0.0% | 23.1% | 28.7% |
| mask_noise|video|max_proj | 36 | 64.4% | 27.8% | 68.6% | 75.0% |
| mask_noise|video|single_best | 36 | 33.3% | 2.8% | 26.1% | 52.8% |
| mask_noise|video|temporal_mean | 36 | 78.0% | 38.9% | 73.3% | 88.9% |
| mask_noise|video|window_mean_best | 36 | 68.6% | 25.0% | 65.8% | 86.1% |
| mask_only|long | 108 | 49.3% | 18.5% | 86.0% | 60.2% |
| mask_only|short | 108 | 13.6% | 0.0% | 26.0% | 29.6% |
| mask_only|video|max_proj | 36 | 59.5% | 16.7% | 62.4% | 75.0% |
| mask_only|video|single_best | 36 | 39.6% | 0.0% | 29.7% | 63.9% |
| mask_only|video|temporal_mean | 36 | 76.7% | 44.4% | 73.9% | 94.4% |
| mask_only|video|window_mean_best | 36 | 71.9% | 22.2% | 69.9% | 88.9% |
| original|long | 108 | 15.3% | 1.9% | 53.6% | 22.2% |
| original|short | 108 | 64.3% | 33.3% | 87.9% | 71.3% |
| original|video|max_proj | 36 | 49.2% | 19.4% | 46.3% | 61.1% |
| original|video|single_best | 36 | 74.2% | 50.0% | 70.5% | 80.6% |
| original|video|temporal_mean | 36 | 73.2% | 44.4% | 69.5% | 80.6% |
| original|video|window_mean_best | 36 | 74.8% | 47.2% | 71.3% | 80.6% |
| stripe_0.00|short | 45 | 13.6% | 2.2% | 13.1% | 17.8% |
| stripe_0.00|video|max_proj | 15 | 48.8% | 20.0% | 32.7% | 60.0% |
| stripe_0.00|video|single_best | 15 | 12.0% | 0.0% | 17.9% | 20.0% |
| stripe_0.00|video|temporal_mean | 15 | 54.5% | 33.3% | 47.0% | 73.3% |
| stripe_0.00|video|window_mean_best | 15 | 49.3% | 13.3% | 44.6% | 66.7% |
| stripe_0.10|short | 45 | 10.2% | 0.0% | 17.3% | 17.8% |
| stripe_0.10|video|max_proj | 15 | 38.1% | 6.7% | 41.0% | 46.7% |
| stripe_0.10|video|single_best | 15 | 34.2% | 0.0% | 22.1% | 53.3% |
| stripe_0.10|video|temporal_mean | 15 | 44.9% | 33.3% | 43.6% | 60.0% |
| stripe_0.10|video|window_mean_best | 15 | 40.3% | 0.0% | 25.5% | 53.3% |
| stripe_0.18|short | 45 | 2.5% | 0.0% | 5.4% | 0.0% |
| stripe_0.18|video|max_proj | 15 | 50.1% | 6.7% | 33.7% | 66.7% |
| stripe_0.18|video|single_best | 15 | 21.8% | 0.0% | 17.1% | 33.3% |
| stripe_0.18|video|temporal_mean | 15 | 45.9% | 33.3% | 34.7% | 53.3% |
| stripe_0.18|video|window_mean_best | 15 | 44.5% | 6.7% | 37.3% | 53.3% |
| stripe_0.30|short | 45 | 2.4% | 0.0% | 2.3% | 0.0% |
| stripe_0.30|video|max_proj | 15 | 41.7% | 6.7% | 31.3% | 53.3% |
| stripe_0.30|video|single_best | 15 | 22.1% | 6.7% | 19.3% | 40.0% |
| stripe_0.30|video|temporal_mean | 15 | 37.4% | 20.0% | 27.7% | 53.3% |
| stripe_0.30|video|window_mean_best | 15 | 42.7% | 6.7% | 15.8% | 53.3% |
| vlm|long | 108 | 5.2% | 0.0% | 10.6% | 9.3% |
| vlm|short | 108 | 2.5% | 0.0% | 3.0% | 2.8% |
| vlm|video|max_proj | 36 | 10.4% | 0.0% | 5.9% | 8.3% |
| vlm|video|single_best | 36 | 1.4% | 0.0% | 0.2% | 2.8% |
| vlm|video|temporal_mean | 36 | 20.3% | 0.0% | 11.6% | 33.3% |
| vlm|video|window_mean_best | 36 | 3.2% | 0.0% | 3.1% | 5.6% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 85.5% | 55.6% | 95.8% | 97.2% |
| anti_ocr | short | 36 | 28.6% | 0.0% | 62.0% | 66.7% |
| anti_ocr | video:max_proj | 12 | 86.2% | 41.7% | 91.9% | 91.7% |
| anti_ocr | video:single_best | 12 | 42.8% | 8.3% | 65.0% | 83.3% |
| anti_ocr | video:temporal_mean | 12 | 89.4% | 75.0% | 92.5% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 83.0% | 25.0% | 92.3% | 100.0% |
| deployed | long | 36 | 83.7% | 52.8% | 95.5% | 100.0% |
| deployed | short | 51 | 19.8% | 0.0% | 36.9% | 37.3% |
| deployed | video:max_proj | 17 | 80.3% | 17.6% | 88.6% | 88.2% |
| deployed | video:single_best | 17 | 41.9% | 0.0% | 60.2% | 76.5% |
| deployed | video:temporal_mean | 17 | 87.3% | 82.4% | 88.8% | 100.0% |
| deployed | video:window_mean_best | 17 | 78.5% | 29.4% | 88.7% | 100.0% |
| glyph_0.00 | short | 15 | 9.5% | 0.0% | 10.5% | 6.7% |
| glyph_0.00 | video:max_proj | 5 | 55.1% | 20.0% | 54.0% | 60.0% |
| glyph_0.00 | video:single_best | 5 | 46.2% | 20.0% | 26.9% | 60.0% |
| glyph_0.00 | video:temporal_mean | 5 | 60.9% | 60.0% | 64.2% | 80.0% |
| glyph_0.00 | video:window_mean_best | 5 | 56.2% | 20.0% | 58.3% | 80.0% |
| glyph_0.12 | short | 15 | 7.9% | 0.0% | 17.5% | 6.7% |
| glyph_0.12 | video:max_proj | 5 | 56.9% | 20.0% | 53.1% | 60.0% |
| glyph_0.12 | video:single_best | 5 | 29.4% | 0.0% | 25.9% | 40.0% |
| glyph_0.12 | video:temporal_mean | 5 | 60.8% | 60.0% | 54.0% | 80.0% |
| glyph_0.12 | video:window_mean_best | 5 | 55.6% | 40.0% | 53.8% | 60.0% |
| glyph_0.22 | short | 15 | 13.3% | 0.0% | 10.8% | 20.0% |
| glyph_0.22 | video:max_proj | 5 | 56.2% | 0.0% | 53.3% | 60.0% |
| glyph_0.22 | video:single_best | 5 | 42.1% | 0.0% | 11.9% | 60.0% |
| glyph_0.22 | video:temporal_mean | 5 | 58.2% | 60.0% | 53.8% | 60.0% |
| glyph_0.22 | video:window_mean_best | 5 | 58.4% | 40.0% | 53.5% | 80.0% |
| inversion_0.0 | long | 15 | 77.8% | 13.3% | 80.8% | 93.3% |
| inversion_0.0 | video:max_proj | 5 | 56.0% | 0.0% | 48.8% | 60.0% |
| inversion_0.0 | video:single_best | 5 | 33.1% | 0.0% | 31.2% | 40.0% |
| inversion_0.0 | video:temporal_mean | 5 | 80.5% | 60.0% | 55.4% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 74.1% | 40.0% | 53.1% | 100.0% |
| inversion_0.2 | long | 15 | 71.6% | 26.7% | 80.6% | 100.0% |
| inversion_0.2 | video:max_proj | 5 | 73.5% | 20.0% | 78.1% | 80.0% |
| inversion_0.2 | video:single_best | 5 | 43.4% | 0.0% | 36.0% | 80.0% |
| inversion_0.2 | video:temporal_mean | 5 | 79.0% | 80.0% | 79.2% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 73.2% | 20.0% | 78.8% | 100.0% |
| inversion_0.3 | long | 15 | 79.6% | 40.0% | 86.9% | 100.0% |
| inversion_0.3 | video:max_proj | 5 | 75.9% | 20.0% | 77.8% | 100.0% |
| inversion_0.3 | video:single_best | 5 | 56.3% | 20.0% | 50.7% | 60.0% |
| inversion_0.3 | video:temporal_mean | 5 | 78.2% | 60.0% | 79.2% | 100.0% |
| inversion_0.3 | video:window_mean_best | 5 | 77.8% | 60.0% | 78.3% | 80.0% |
| inversion_0.5 | long | 15 | 84.3% | 60.0% | 86.6% | 100.0% |
| inversion_0.5 | video:max_proj | 5 | 73.7% | 20.0% | 78.8% | 80.0% |
| inversion_0.5 | video:single_best | 5 | 33.2% | 0.0% | 60.5% | 60.0% |
| inversion_0.5 | video:temporal_mean | 5 | 71.1% | 60.0% | 79.5% | 100.0% |
| inversion_0.5 | video:window_mean_best | 5 | 77.5% | 40.0% | 78.5% | 100.0% |
| inversion_1.0 | long | 15 | 42.8% | 0.0% | 61.6% | 80.0% |
| inversion_1.0 | video:max_proj | 5 | 29.7% | 20.0% | 27.8% | 40.0% |
| inversion_1.0 | video:single_best | 5 | 38.4% | 40.0% | 26.2% | 40.0% |
| inversion_1.0 | video:temporal_mean | 5 | 33.4% | 0.0% | 25.2% | 40.0% |
| inversion_1.0 | video:window_mean_best | 5 | 41.8% | 40.0% | 28.1% | 60.0% |
| mask_noise | long | 36 | 92.0% | 66.7% | 95.9% | 100.0% |
| mask_noise | short | 36 | 32.6% | 0.0% | 58.6% | 69.4% |
| mask_noise | video:max_proj | 12 | 85.1% | 50.0% | 92.1% | 91.7% |
| mask_noise | video:single_best | 12 | 61.0% | 8.3% | 62.2% | 83.3% |
| mask_noise | video:temporal_mean | 12 | 91.6% | 83.3% | 92.8% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 88.0% | 58.3% | 83.4% | 100.0% |
| mask_only | long | 36 | 88.4% | 50.0% | 97.1% | 97.2% |
| mask_only | short | 36 | 31.9% | 0.0% | 71.4% | 72.2% |
| mask_only | video:max_proj | 12 | 81.5% | 41.7% | 92.2% | 91.7% |
| mask_only | video:single_best | 12 | 66.4% | 0.0% | 69.7% | 91.7% |
| mask_only | video:temporal_mean | 12 | 91.7% | 91.7% | 92.8% | 100.0% |
| mask_only | video:window_mean_best | 12 | 88.2% | 50.0% | 92.5% | 91.7% |
| original | long | 36 | 45.7% | 5.6% | 92.5% | 66.7% |
| original | short | 36 | 94.4% | 63.9% | 98.2% | 100.0% |
| original | video:max_proj | 12 | 89.9% | 58.3% | 93.0% | 100.0% |
| original | video:single_best | 12 | 86.4% | 75.0% | 84.0% | 100.0% |
| original | video:temporal_mean | 12 | 87.5% | 75.0% | 84.0% | 100.0% |
| original | video:window_mean_best | 12 | 84.9% | 75.0% | 83.9% | 91.7% |
| stripe_0.00 | short | 15 | 19.5% | 6.7% | 19.2% | 20.0% |
| stripe_0.00 | video:max_proj | 5 | 76.8% | 60.0% | 53.8% | 80.0% |
| stripe_0.00 | video:single_best | 5 | 21.2% | 0.0% | 42.6% | 40.0% |
| stripe_0.00 | video:temporal_mean | 5 | 79.4% | 60.0% | 79.7% | 100.0% |
| stripe_0.00 | video:window_mean_best | 5 | 77.5% | 40.0% | 79.0% | 100.0% |
| stripe_0.10 | short | 15 | 25.5% | 0.0% | 45.0% | 46.7% |
| stripe_0.10 | video:max_proj | 5 | 73.0% | 20.0% | 78.8% | 80.0% |
| stripe_0.10 | video:single_best | 5 | 63.8% | 0.0% | 62.1% | 80.0% |
| stripe_0.10 | video:temporal_mean | 5 | 63.6% | 60.0% | 79.7% | 80.0% |
| stripe_0.10 | video:window_mean_best | 5 | 69.5% | 0.0% | 53.5% | 80.0% |
| stripe_0.18 | short | 15 | 6.8% | 0.0% | 15.9% | 0.0% |
| stripe_0.18 | video:max_proj | 5 | 57.5% | 20.0% | 53.3% | 80.0% |
| stripe_0.18 | video:single_best | 5 | 47.1% | 0.0% | 51.2% | 60.0% |
| stripe_0.18 | video:temporal_mean | 5 | 59.3% | 60.0% | 53.8% | 60.0% |
| stripe_0.18 | video:window_mean_best | 5 | 57.8% | 20.0% | 57.8% | 60.0% |
| stripe_0.30 | short | 15 | 4.7% | 0.0% | 6.8% | 0.0% |
| stripe_0.30 | video:max_proj | 5 | 57.2% | 20.0% | 53.3% | 60.0% |
| stripe_0.30 | video:single_best | 5 | 37.2% | 20.0% | 50.5% | 40.0% |
| stripe_0.30 | video:temporal_mean | 5 | 57.8% | 40.0% | 53.8% | 80.0% |
| stripe_0.30 | video:window_mean_best | 5 | 54.8% | 20.0% | 28.8% | 60.0% |
| vlm | long | 36 | 13.2% | 0.0% | 27.1% | 25.0% |
| vlm | short | 36 | 6.5% | 0.0% | 8.8% | 8.3% |
| vlm | video:max_proj | 12 | 19.0% | 0.0% | 16.2% | 16.7% |
| vlm | video:single_best | 12 | 4.3% | 0.0% | 0.7% | 8.3% |
| vlm | video:temporal_mean | 12 | 48.4% | 0.0% | 31.1% | 83.3% |
| vlm | video:window_mean_best | 12 | 8.6% | 0.0% | 7.4% | 16.7% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | -39.8% | -50.0% | 45.7% | 5.6% |
| anti_ocr | short | 65.8% | 63.9% | 94.4% | 63.9% |
| anti_ocr | video:max_proj | 3.7% | 16.7% | 89.9% | 58.3% |
| anti_ocr | video:single_best | 43.6% | 66.7% | 86.4% | 75.0% |
| anti_ocr | video:temporal_mean | -1.9% | 0.0% | 87.5% | 75.0% |
| anti_ocr | video:window_mean_best | 1.8% | 50.0% | 84.9% | 75.0% |
| deployed | long | -38.0% | -47.2% | 45.7% | 5.6% |
| deployed | short | 74.6% | 63.9% | 94.4% | 63.9% |
| deployed | video:max_proj | 9.6% | 40.7% | 89.9% | 58.3% |
| deployed | video:single_best | 44.5% | 75.0% | 86.4% | 75.0% |
| deployed | video:temporal_mean | 0.2% | -7.4% | 87.5% | 75.0% |
| deployed | video:window_mean_best | 6.3% | 45.6% | 84.9% | 75.0% |
| glyph_0.00 | short | 84.9% | 63.9% | 94.4% | 63.9% |
| glyph_0.00 | video:max_proj | 34.8% | 38.3% | 89.9% | 58.3% |
| glyph_0.00 | video:single_best | 40.2% | 55.0% | 86.4% | 75.0% |
| glyph_0.00 | video:temporal_mean | 26.5% | 15.0% | 87.5% | 75.0% |
| glyph_0.00 | video:window_mean_best | 28.6% | 55.0% | 84.9% | 75.0% |
| glyph_0.12 | short | 86.5% | 63.9% | 94.4% | 63.9% |
| glyph_0.12 | video:max_proj | 33.0% | 38.3% | 89.9% | 58.3% |
| glyph_0.12 | video:single_best | 57.0% | 75.0% | 86.4% | 75.0% |
| glyph_0.12 | video:temporal_mean | 26.6% | 15.0% | 87.5% | 75.0% |
| glyph_0.12 | video:window_mean_best | 29.3% | 35.0% | 84.9% | 75.0% |
| glyph_0.22 | short | 81.1% | 63.9% | 94.4% | 63.9% |
| glyph_0.22 | video:max_proj | 33.7% | 58.3% | 89.9% | 58.3% |
| glyph_0.22 | video:single_best | 44.3% | 75.0% | 86.4% | 75.0% |
| glyph_0.22 | video:temporal_mean | 29.2% | 15.0% | 87.5% | 75.0% |
| glyph_0.22 | video:window_mean_best | 26.5% | 35.0% | 84.9% | 75.0% |
| inversion_0.0 | long | -32.1% | -7.8% | 45.7% | 5.6% |
| inversion_0.0 | video:max_proj | 33.9% | 58.3% | 89.9% | 58.3% |
| inversion_0.0 | video:single_best | 53.3% | 75.0% | 86.4% | 75.0% |
| inversion_0.0 | video:temporal_mean | 7.0% | 15.0% | 87.5% | 75.0% |
| inversion_0.0 | video:window_mean_best | 10.8% | 35.0% | 84.9% | 75.0% |
| inversion_0.2 | long | -25.9% | -21.1% | 45.7% | 5.6% |
| inversion_0.2 | video:max_proj | 16.4% | 38.3% | 89.9% | 58.3% |
| inversion_0.2 | video:single_best | 42.9% | 75.0% | 86.4% | 75.0% |
| inversion_0.2 | video:temporal_mean | 8.5% | -5.0% | 87.5% | 75.0% |
| inversion_0.2 | video:window_mean_best | 11.7% | 55.0% | 84.9% | 75.0% |
| inversion_0.3 | long | -33.9% | -34.4% | 45.7% | 5.6% |
| inversion_0.3 | video:max_proj | 14.0% | 38.3% | 89.9% | 58.3% |
| inversion_0.3 | video:single_best | 30.1% | 55.0% | 86.4% | 75.0% |
| inversion_0.3 | video:temporal_mean | 9.3% | 15.0% | 87.5% | 75.0% |
| inversion_0.3 | video:window_mean_best | 7.0% | 15.0% | 84.9% | 75.0% |
| inversion_0.5 | long | -38.6% | -54.4% | 45.7% | 5.6% |
| inversion_0.5 | video:max_proj | 16.2% | 38.3% | 89.9% | 58.3% |
| inversion_0.5 | video:single_best | 53.2% | 75.0% | 86.4% | 75.0% |
| inversion_0.5 | video:temporal_mean | 16.4% | 15.0% | 87.5% | 75.0% |
| inversion_0.5 | video:window_mean_best | 7.4% | 35.0% | 84.9% | 75.0% |
| inversion_1.0 | long | 2.9% | 5.6% | 45.7% | 5.6% |
| inversion_1.0 | video:max_proj | 60.2% | 38.3% | 89.9% | 58.3% |
| inversion_1.0 | video:single_best | 48.0% | 35.0% | 86.4% | 75.0% |
| inversion_1.0 | video:temporal_mean | 54.1% | 75.0% | 87.5% | 75.0% |
| inversion_1.0 | video:window_mean_best | 43.0% | 35.0% | 84.9% | 75.0% |
| mask_noise | long | -46.3% | -61.1% | 45.7% | 5.6% |
| mask_noise | short | 61.8% | 63.9% | 94.4% | 63.9% |
| mask_noise | video:max_proj | 4.8% | 8.3% | 89.9% | 58.3% |
| mask_noise | video:single_best | 25.4% | 66.7% | 86.4% | 75.0% |
| mask_noise | video:temporal_mean | -4.1% | -8.3% | 87.5% | 75.0% |
| mask_noise | video:window_mean_best | -3.1% | 16.7% | 84.9% | 75.0% |
| mask_only | long | -42.7% | -44.4% | 45.7% | 5.6% |
| mask_only | short | 62.5% | 63.9% | 94.4% | 63.9% |
| mask_only | video:max_proj | 8.4% | 16.7% | 89.9% | 58.3% |
| mask_only | video:single_best | 20.0% | 75.0% | 86.4% | 75.0% |
| mask_only | video:temporal_mean | -4.3% | -16.7% | 87.5% | 75.0% |
| mask_only | video:window_mean_best | -3.3% | 25.0% | 84.9% | 75.0% |
| original | long | 0.0% | 0.0% | 45.7% | 5.6% |
| original | short | 0.0% | 0.0% | 94.4% | 63.9% |
| original | video:max_proj | 0.0% | 0.0% | 89.9% | 58.3% |
| original | video:single_best | 0.0% | 0.0% | 86.4% | 75.0% |
| original | video:temporal_mean | 0.0% | 0.0% | 87.5% | 75.0% |
| original | video:window_mean_best | 0.0% | 0.0% | 84.9% | 75.0% |
| stripe_0.00 | short | 74.9% | 57.2% | 94.4% | 63.9% |
| stripe_0.00 | video:max_proj | 13.2% | -1.7% | 89.9% | 58.3% |
| stripe_0.00 | video:single_best | 65.2% | 75.0% | 86.4% | 75.0% |
| stripe_0.00 | video:temporal_mean | 8.1% | 15.0% | 87.5% | 75.0% |
| stripe_0.00 | video:window_mean_best | 7.4% | 35.0% | 84.9% | 75.0% |
| stripe_0.10 | short | 68.9% | 63.9% | 94.4% | 63.9% |
| stripe_0.10 | video:max_proj | 16.9% | 38.3% | 89.9% | 58.3% |
| stripe_0.10 | video:single_best | 22.6% | 75.0% | 86.4% | 75.0% |
| stripe_0.10 | video:temporal_mean | 23.9% | 15.0% | 87.5% | 75.0% |
| stripe_0.10 | video:window_mean_best | 15.4% | 75.0% | 84.9% | 75.0% |
| stripe_0.18 | short | 87.6% | 63.9% | 94.4% | 63.9% |
| stripe_0.18 | video:max_proj | 32.4% | 38.3% | 89.9% | 58.3% |
| stripe_0.18 | video:single_best | 39.3% | 75.0% | 86.4% | 75.0% |
| stripe_0.18 | video:temporal_mean | 28.2% | 15.0% | 87.5% | 75.0% |
| stripe_0.18 | video:window_mean_best | 27.0% | 55.0% | 84.9% | 75.0% |
| stripe_0.30 | short | 89.7% | 63.9% | 94.4% | 63.9% |
| stripe_0.30 | video:max_proj | 32.7% | 38.3% | 89.9% | 58.3% |
| stripe_0.30 | video:single_best | 49.2% | 55.0% | 86.4% | 75.0% |
| stripe_0.30 | video:temporal_mean | 29.6% | 35.0% | 87.5% | 75.0% |
| stripe_0.30 | video:window_mean_best | 30.1% | 55.0% | 84.9% | 75.0% |
| vlm | long | 32.5% | 5.6% | 45.7% | 5.6% |
| vlm | short | 87.9% | 63.9% | 94.4% | 63.9% |
| vlm | video:max_proj | 71.0% | 58.3% | 89.9% | 58.3% |
| vlm | video:single_best | 82.0% | 75.0% | 86.4% | 75.0% |
| vlm | video:temporal_mean | 39.1% | 75.0% | 87.5% | 75.0% |
| vlm | video:window_mean_best | 76.2% | 75.0% | 84.9% | 75.0% |
