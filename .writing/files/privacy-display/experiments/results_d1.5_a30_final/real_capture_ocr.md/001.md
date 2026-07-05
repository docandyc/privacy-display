# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 41.0% | 20.4% | 82.0% | 49.1% |
| anti_ocr|short | 108 | 24.5% | 1.9% | 23.3% | 37.0% |
| anti_ocr|video|max_proj | 36 | 41.2% | 0.0% | 41.8% | 52.8% |
| anti_ocr|video|single_best | 36 | 33.9% | 2.8% | 19.5% | 50.0% |
| anti_ocr|video|temporal_mean | 36 | 74.2% | 30.6% | 67.5% | 91.7% |
| anti_ocr|video|window_mean_best | 36 | 64.4% | 25.0% | 57.2% | 80.6% |
| deployed|long | 108 | 49.7% | 19.4% | 86.5% | 61.1% |
| deployed|short | 153 | 13.1% | 1.3% | 11.5% | 18.3% |
| deployed|video|max_proj | 51 | 56.7% | 7.8% | 57.4% | 68.6% |
| deployed|video|single_best | 51 | 41.3% | 7.8% | 31.8% | 60.8% |
| deployed|video|temporal_mean | 51 | 65.9% | 43.1% | 68.2% | 78.4% |
| deployed|video|window_mean_best | 51 | 56.8% | 15.7% | 54.9% | 76.5% |
| glyph_0.00|short | 45 | 27.6% | 4.4% | 16.6% | 35.6% |
| glyph_0.00|video|max_proj | 15 | 61.3% | 6.7% | 42.4% | 80.0% |
| glyph_0.00|video|single_best | 15 | 38.4% | 0.0% | 22.3% | 53.3% |
| glyph_0.00|video|temporal_mean | 15 | 49.2% | 13.3% | 40.5% | 66.7% |
| glyph_0.00|video|window_mean_best | 15 | 45.0% | 13.3% | 28.6% | 66.7% |
| glyph_0.12|short | 45 | 28.3% | 0.0% | 17.0% | 37.8% |
| glyph_0.12|video|max_proj | 15 | 53.9% | 6.7% | 33.6% | 66.7% |
| glyph_0.12|video|single_best | 15 | 29.5% | 0.0% | 15.8% | 53.3% |
| glyph_0.12|video|temporal_mean | 15 | 34.5% | 6.7% | 25.8% | 53.3% |
| glyph_0.12|video|window_mean_best | 15 | 41.5% | 13.3% | 27.9% | 60.0% |
| glyph_0.22|short | 45 | 20.1% | 4.4% | 13.2% | 31.1% |
| glyph_0.22|video|max_proj | 15 | 45.7% | 6.7% | 30.3% | 53.3% |
| glyph_0.22|video|single_best | 15 | 26.5% | 0.0% | 13.5% | 40.0% |
| glyph_0.22|video|temporal_mean | 15 | 38.1% | 6.7% | 23.6% | 53.3% |
| glyph_0.22|video|window_mean_best | 15 | 36.5% | 0.0% | 27.8% | 46.7% |
| inversion_0.0|long | 45 | 38.4% | 8.9% | 69.7% | 46.7% |
| inversion_0.0|video|max_proj | 15 | 41.6% | 0.0% | 29.3% | 53.3% |
| inversion_0.0|video|single_best | 15 | 26.2% | 0.0% | 18.7% | 46.7% |
| inversion_0.0|video|temporal_mean | 15 | 64.7% | 46.7% | 58.7% | 86.7% |
| inversion_0.0|video|window_mean_best | 15 | 56.2% | 13.3% | 48.9% | 80.0% |
| inversion_0.2|long | 45 | 55.2% | 24.4% | 81.1% | 64.4% |
| inversion_0.2|video|max_proj | 15 | 42.6% | 6.7% | 31.8% | 60.0% |
| inversion_0.2|video|single_best | 15 | 27.7% | 6.7% | 17.1% | 40.0% |
| inversion_0.2|video|temporal_mean | 15 | 51.1% | 26.7% | 50.3% | 73.3% |
| inversion_0.2|video|window_mean_best | 15 | 52.2% | 13.3% | 48.6% | 80.0% |
| inversion_0.3|long | 45 | 51.6% | 17.8% | 74.3% | 62.2% |
| inversion_0.3|video|max_proj | 15 | 42.4% | 6.7% | 29.3% | 60.0% |
| inversion_0.3|video|single_best | 15 | 34.2% | 0.0% | 23.3% | 66.7% |
| inversion_0.3|video|temporal_mean | 15 | 52.0% | 6.7% | 50.9% | 73.3% |
| inversion_0.3|video|window_mean_best | 15 | 47.2% | 13.3% | 36.7% | 66.7% |
| inversion_0.5|long | 45 | 51.5% | 15.6% | 69.3% | 60.0% |
| inversion_0.5|video|max_proj | 15 | 50.9% | 6.7% | 47.3% | 73.3% |
| inversion_0.5|video|single_best | 15 | 33.6% | 6.7% | 20.5% | 53.3% |
| inversion_0.5|video|temporal_mean | 15 | 49.5% | 26.7% | 47.8% | 66.7% |
| inversion_0.5|video|window_mean_best | 15 | 37.3% | 0.0% | 37.4% | 53.3% |
| inversion_1.0|long | 45 | 9.1% | 0.0% | 15.5% | 13.3% |
| inversion_1.0|video|max_proj | 15 | 40.5% | 0.0% | 29.0% | 53.3% |
| inversion_1.0|video|single_best | 15 | 20.8% | 0.0% | 17.1% | 40.0% |
| inversion_1.0|video|temporal_mean | 15 | 8.3% | 0.0% | 12.2% | 13.3% |
| inversion_1.0|video|window_mean_best | 15 | 48.3% | 0.0% | 37.5% | 66.7% |
| mask_noise|long | 108 | 55.4% | 20.4% | 87.2% | 68.5% |
| mask_noise|short | 108 | 32.2% | 4.6% | 21.5% | 43.5% |
| mask_noise|video|max_proj | 36 | 55.7% | 13.9% | 47.7% | 69.4% |
| mask_noise|video|single_best | 36 | 34.9% | 0.0% | 26.0% | 47.2% |
| mask_noise|video|temporal_mean | 36 | 79.3% | 47.2% | 69.9% | 94.4% |
| mask_noise|video|window_mean_best | 36 | 72.2% | 30.6% | 65.3% | 83.3% |
| mask_only|long | 108 | 40.9% | 12.0% | 60.8% | 50.9% |
| mask_only|short | 108 | 7.0% | 0.9% | 7.9% | 13.0% |
| mask_only|video|max_proj | 36 | 58.6% | 22.2% | 43.2% | 72.2% |
| mask_only|video|single_best | 36 | 34.9% | 5.6% | 26.6% | 52.8% |
| mask_only|video|temporal_mean | 36 | 77.1% | 41.7% | 65.4% | 88.9% |
| mask_only|video|window_mean_best | 36 | 69.7% | 30.6% | 55.3% | 86.1% |
| original|long | 108 | 33.6% | 9.3% | 52.5% | 38.9% |
| original|short | 108 | 70.5% | 38.0% | 62.0% | 80.6% |
| original|video|max_proj | 36 | 36.6% | 11.1% | 23.5% | 52.8% |
| original|video|single_best | 36 | 61.2% | 30.6% | 56.3% | 69.4% |
| original|video|temporal_mean | 36 | 44.6% | 25.0% | 37.1% | 52.8% |
| original|video|window_mean_best | 36 | 63.4% | 30.6% | 56.4% | 72.2% |
| stripe_0.00|short | 45 | 10.7% | 2.2% | 16.2% | 13.3% |
| stripe_0.00|video|max_proj | 15 | 50.0% | 6.7% | 37.5% | 73.3% |
| stripe_0.00|video|single_best | 15 | 29.0% | 0.0% | 25.9% | 40.0% |
| stripe_0.00|video|temporal_mean | 15 | 40.0% | 20.0% | 39.9% | 60.0% |
| stripe_0.00|video|window_mean_best | 15 | 55.7% | 20.0% | 40.4% | 86.7% |
| stripe_0.10|short | 45 | 19.2% | 0.0% | 18.1% | 28.9% |
| stripe_0.10|video|max_proj | 15 | 44.4% | 0.0% | 25.5% | 60.0% |
| stripe_0.10|video|single_best | 15 | 26.8% | 0.0% | 17.5% | 40.0% |
| stripe_0.10|video|temporal_mean | 15 | 52.0% | 33.3% | 46.5% | 66.7% |
| stripe_0.10|video|window_mean_best | 15 | 45.2% | 13.3% | 45.6% | 80.0% |
| stripe_0.18|short | 45 | 21.7% | 0.0% | 16.6% | 31.1% |
| stripe_0.18|video|max_proj | 15 | 58.1% | 6.7% | 51.2% | 80.0% |
| stripe_0.18|video|single_best | 15 | 23.1% | 0.0% | 11.5% | 40.0% |
| stripe_0.18|video|temporal_mean | 15 | 54.6% | 26.7% | 53.9% | 73.3% |
| stripe_0.18|video|window_mean_best | 15 | 50.7% | 13.3% | 38.0% | 86.7% |
| stripe_0.30|short | 45 | 23.8% | 0.0% | 15.8% | 35.6% |
| stripe_0.30|video|max_proj | 15 | 53.4% | 6.7% | 40.5% | 73.3% |
| stripe_0.30|video|single_best | 15 | 27.4% | 0.0% | 17.2% | 40.0% |
| stripe_0.30|video|temporal_mean | 15 | 33.5% | 13.3% | 33.5% | 46.7% |
| stripe_0.30|video|window_mean_best | 15 | 43.8% | 0.0% | 30.9% | 53.3% |
| vlm|long | 108 | 6.6% | 0.0% | 12.6% | 13.0% |
| vlm|short | 108 | 2.7% | 0.0% | 1.4% | 1.9% |
| vlm|video|max_proj | 36 | 6.3% | 0.0% | 1.6% | 5.6% |
| vlm|video|single_best | 36 | 3.3% | 0.0% | 3.6% | 5.6% |
| vlm|video|temporal_mean | 36 | 23.0% | 0.0% | 13.9% | 33.3% |
| vlm|video|window_mean_best | 36 | 4.4% | 0.0% | 1.8% | 5.6% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 74.7% | 50.0% | 93.7% | 86.1% |
| anti_ocr | short | 36 | 54.6% | 5.6% | 69.1% | 75.0% |
| anti_ocr | video:max_proj | 12 | 69.6% | 0.0% | 74.8% | 91.7% |
| anti_ocr | video:single_best | 12 | 59.2% | 8.3% | 39.9% | 66.7% |
| anti_ocr | video:temporal_mean | 12 | 89.4% | 83.3% | 92.5% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 88.8% | 66.7% | 92.1% | 91.7% |
| deployed | long | 36 | 87.3% | 47.2% | 96.2% | 97.2% |
| deployed | short | 51 | 28.9% | 3.9% | 32.3% | 35.3% |
| deployed | video:max_proj | 17 | 79.9% | 23.5% | 70.5% | 94.1% |
| deployed | video:single_best | 17 | 66.7% | 23.5% | 75.0% | 76.5% |
| deployed | video:temporal_mean | 17 | 87.2% | 88.2% | 88.6% | 94.1% |
| deployed | video:window_mean_best | 17 | 79.9% | 47.1% | 88.7% | 94.1% |
| glyph_0.00 | short | 15 | 52.1% | 13.3% | 32.5% | 60.0% |
| glyph_0.00 | video:max_proj | 5 | 73.5% | 20.0% | 53.1% | 80.0% |
| glyph_0.00 | video:single_best | 5 | 63.5% | 0.0% | 50.7% | 80.0% |
| glyph_0.00 | video:temporal_mean | 5 | 77.0% | 40.0% | 80.4% | 100.0% |
| glyph_0.00 | video:window_mean_best | 5 | 77.5% | 40.0% | 54.2% | 100.0% |
| glyph_0.12 | short | 15 | 49.4% | 0.0% | 35.6% | 60.0% |
| glyph_0.12 | video:max_proj | 5 | 73.0% | 20.0% | 52.8% | 80.0% |
| glyph_0.12 | video:single_best | 5 | 53.7% | 0.0% | 40.2% | 80.0% |
| glyph_0.12 | video:temporal_mean | 5 | 57.8% | 20.0% | 54.7% | 80.0% |
| glyph_0.12 | video:window_mean_best | 5 | 75.2% | 40.0% | 53.8% | 100.0% |
| glyph_0.22 | short | 15 | 35.5% | 13.3% | 29.0% | 46.7% |
| glyph_0.22 | video:max_proj | 5 | 73.2% | 20.0% | 53.8% | 80.0% |
| glyph_0.22 | video:single_best | 5 | 48.7% | 0.0% | 33.3% | 80.0% |
| glyph_0.22 | video:temporal_mean | 5 | 74.8% | 20.0% | 48.3% | 100.0% |
| glyph_0.22 | video:window_mean_best | 5 | 56.2% | 0.0% | 53.5% | 80.0% |
| inversion_0.0 | long | 15 | 69.9% | 26.7% | 94.2% | 86.7% |
| inversion_0.0 | video:max_proj | 5 | 65.2% | 0.0% | 53.5% | 80.0% |
| inversion_0.0 | video:single_best | 5 | 44.1% | 0.0% | 37.6% | 80.0% |
| inversion_0.0 | video:temporal_mean | 5 | 80.2% | 80.0% | 79.5% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 77.2% | 40.0% | 79.2% | 100.0% |
| inversion_0.2 | long | 15 | 88.1% | 60.0% | 89.3% | 100.0% |
| inversion_0.2 | video:max_proj | 5 | 58.8% | 20.0% | 45.2% | 80.0% |
| inversion_0.2 | video:single_best | 5 | 48.6% | 20.0% | 36.0% | 60.0% |
| inversion_0.2 | video:temporal_mean | 5 | 78.0% | 80.0% | 79.2% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 76.5% | 40.0% | 78.8% | 100.0% |
| inversion_0.3 | long | 15 | 84.8% | 46.7% | 88.4% | 100.0% |
| inversion_0.3 | video:max_proj | 5 | 61.9% | 20.0% | 47.1% | 80.0% |
| inversion_0.3 | video:single_best | 5 | 55.5% | 0.0% | 45.0% | 80.0% |
| inversion_0.3 | video:temporal_mean | 5 | 77.2% | 20.0% | 78.3% | 100.0% |
| inversion_0.3 | video:window_mean_best | 5 | 76.5% | 40.0% | 53.1% | 80.0% |
| inversion_0.5 | long | 15 | 85.2% | 46.7% | 87.0% | 100.0% |
| inversion_0.5 | video:max_proj | 5 | 70.6% | 20.0% | 77.4% | 100.0% |
| inversion_0.5 | video:single_best | 5 | 53.9% | 20.0% | 42.9% | 60.0% |
| inversion_0.5 | video:temporal_mean | 5 | 76.4% | 60.0% | 79.2% | 100.0% |
| inversion_0.5 | video:window_mean_best | 5 | 59.3% | 0.0% | 53.8% | 80.0% |
| inversion_1.0 | long | 15 | 26.8% | 0.0% | 38.3% | 40.0% |
| inversion_1.0 | video:max_proj | 5 | 72.5% | 0.0% | 52.8% | 80.0% |
| inversion_1.0 | video:single_best | 5 | 42.8% | 0.0% | 36.9% | 80.0% |
| inversion_1.0 | video:temporal_mean | 5 | 24.0% | 0.0% | 36.6% | 40.0% |
| inversion_1.0 | video:window_mean_best | 5 | 74.2% | 0.0% | 53.1% | 100.0% |
| mask_noise | long | 36 | 90.8% | 50.0% | 97.6% | 100.0% |
| mask_noise | short | 36 | 71.3% | 13.9% | 63.7% | 86.1% |
| mask_noise | video:max_proj | 12 | 78.3% | 33.3% | 81.0% | 83.3% |
| mask_noise | video:single_best | 12 | 68.7% | 0.0% | 66.7% | 75.0% |
| mask_noise | video:temporal_mean | 12 | 91.9% | 91.7% | 93.2% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 91.2% | 83.3% | 92.1% | 100.0% |
| mask_only | long | 36 | 75.4% | 33.3% | 78.8% | 83.3% |
| mask_only | short | 36 | 17.0% | 2.8% | 23.7% | 25.0% |
| mask_only | video:max_proj | 12 | 77.8% | 50.0% | 81.3% | 83.3% |
| mask_only | video:single_best | 12 | 67.2% | 16.7% | 61.6% | 83.3% |
| mask_only | video:temporal_mean | 12 | 92.1% | 83.3% | 93.0% | 100.0% |
| mask_only | video:window_mean_best | 12 | 90.1% | 75.0% | 92.5% | 91.7% |
| original | long | 36 | 85.4% | 27.8% | 93.3% | 100.0% |
| original | short | 36 | 95.6% | 75.0% | 94.1% | 100.0% |
| original | video:max_proj | 12 | 62.2% | 25.0% | 48.7% | 83.3% |
| original | video:single_best | 12 | 70.6% | 58.3% | 65.1% | 75.0% |
| original | video:temporal_mean | 12 | 69.2% | 50.0% | 63.9% | 75.0% |
| original | video:window_mean_best | 12 | 72.6% | 58.3% | 65.1% | 83.3% |
| stripe_0.00 | short | 15 | 20.3% | 6.7% | 40.1% | 20.0% |
| stripe_0.00 | video:max_proj | 5 | 70.7% | 20.0% | 78.1% | 80.0% |
| stripe_0.00 | video:single_best | 5 | 43.9% | 0.0% | 50.2% | 60.0% |
| stripe_0.00 | video:temporal_mean | 5 | 61.8% | 60.0% | 79.5% | 80.0% |
| stripe_0.00 | video:window_mean_best | 5 | 78.3% | 60.0% | 77.8% | 100.0% |
| stripe_0.10 | short | 15 | 42.8% | 0.0% | 44.7% | 60.0% |
| stripe_0.10 | video:max_proj | 5 | 67.6% | 0.0% | 48.6% | 80.0% |
| stripe_0.10 | video:single_best | 5 | 42.0% | 0.0% | 41.9% | 60.0% |
| stripe_0.10 | video:temporal_mean | 5 | 79.8% | 80.0% | 77.8% | 100.0% |
| stripe_0.10 | video:window_mean_best | 5 | 69.2% | 40.0% | 79.0% | 100.0% |
| stripe_0.18 | short | 15 | 37.1% | 0.0% | 36.6% | 53.3% |
| stripe_0.18 | video:max_proj | 5 | 72.4% | 20.0% | 78.8% | 80.0% |
| stripe_0.18 | video:single_best | 5 | 49.4% | 0.0% | 34.0% | 80.0% |
| stripe_0.18 | video:temporal_mean | 5 | 78.7% | 60.0% | 79.7% | 100.0% |
| stripe_0.18 | video:window_mean_best | 5 | 69.4% | 40.0% | 73.1% | 100.0% |
| stripe_0.30 | short | 15 | 44.7% | 0.0% | 38.0% | 53.3% |
| stripe_0.30 | video:max_proj | 5 | 73.8% | 20.0% | 78.1% | 80.0% |
| stripe_0.30 | video:single_best | 5 | 49.5% | 0.0% | 36.9% | 60.0% |
| stripe_0.30 | video:temporal_mean | 5 | 61.8% | 40.0% | 78.1% | 80.0% |
| stripe_0.30 | video:window_mean_best | 5 | 74.3% | 0.0% | 53.5% | 80.0% |
| vlm | long | 36 | 16.7% | 0.0% | 32.1% | 38.9% |
| vlm | short | 36 | 7.1% | 0.0% | 4.2% | 5.6% |
| vlm | video:max_proj | 12 | 14.3% | 0.0% | 4.8% | 16.7% |
| vlm | video:single_best | 12 | 8.9% | 0.0% | 10.6% | 16.7% |
| vlm | video:temporal_mean | 12 | 55.5% | 0.0% | 41.3% | 75.0% |
| vlm | video:window_mean_best | 12 | 12.9% | 0.0% | 5.5% | 16.7% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | 10.7% | -22.2% | 85.4% | 27.8% |
| anti_ocr | short | 41.0% | 69.4% | 95.6% | 75.0% |
| anti_ocr | video:max_proj | -7.4% | 25.0% | 62.2% | 25.0% |
| anti_ocr | video:single_best | 11.4% | 50.0% | 70.6% | 58.3% |
| anti_ocr | video:temporal_mean | -20.1% | -33.3% | 69.2% | 50.0% |
| anti_ocr | video:window_mean_best | -16.2% | -8.3% | 72.6% | 58.3% |
| deployed | long | -1.9% | -19.4% | 85.4% | 27.8% |
| deployed | short | 66.7% | 71.1% | 95.6% | 75.0% |
| deployed | video:max_proj | -17.7% | 1.5% | 62.2% | 25.0% |
| deployed | video:single_best | 3.9% | 34.8% | 70.6% | 58.3% |
| deployed | video:temporal_mean | -17.9% | -38.2% | 69.2% | 50.0% |
| deployed | video:window_mean_best | -7.3% | 11.3% | 72.6% | 58.3% |
| glyph_0.00 | short | 43.5% | 61.7% | 95.6% | 75.0% |
| glyph_0.00 | video:max_proj | -11.3% | 5.0% | 62.2% | 25.0% |
| glyph_0.00 | video:single_best | 7.2% | 58.3% | 70.6% | 58.3% |
| glyph_0.00 | video:temporal_mean | -7.8% | 10.0% | 69.2% | 50.0% |
| glyph_0.00 | video:window_mean_best | -4.9% | 18.3% | 72.6% | 58.3% |
| glyph_0.12 | short | 46.2% | 75.0% | 95.6% | 75.0% |
| glyph_0.12 | video:max_proj | -10.8% | 5.0% | 62.2% | 25.0% |
| glyph_0.12 | video:single_best | 16.9% | 58.3% | 70.6% | 58.3% |
| glyph_0.12 | video:temporal_mean | 11.4% | 30.0% | 69.2% | 50.0% |
| glyph_0.12 | video:window_mean_best | -2.6% | 18.3% | 72.6% | 58.3% |
| glyph_0.22 | short | 60.2% | 61.7% | 95.6% | 75.0% |
| glyph_0.22 | video:max_proj | -11.0% | 5.0% | 62.2% | 25.0% |
| glyph_0.22 | video:single_best | 21.9% | 58.3% | 70.6% | 58.3% |
| glyph_0.22 | video:temporal_mean | -5.6% | 30.0% | 69.2% | 50.0% |
| glyph_0.22 | video:window_mean_best | 16.5% | 58.3% | 72.6% | 58.3% |
| inversion_0.0 | long | 15.5% | 1.1% | 85.4% | 27.8% |
| inversion_0.0 | video:max_proj | -3.0% | 25.0% | 62.2% | 25.0% |
| inversion_0.0 | video:single_best | 26.5% | 58.3% | 70.6% | 58.3% |
| inversion_0.0 | video:temporal_mean | -11.0% | -30.0% | 69.2% | 50.0% |
| inversion_0.0 | video:window_mean_best | -4.6% | 18.3% | 72.6% | 58.3% |
| inversion_0.2 | long | -2.6% | -32.2% | 85.4% | 27.8% |
| inversion_0.2 | video:max_proj | 3.3% | 5.0% | 62.2% | 25.0% |
| inversion_0.2 | video:single_best | 22.1% | 38.3% | 70.6% | 58.3% |
| inversion_0.2 | video:temporal_mean | -8.8% | -30.0% | 69.2% | 50.0% |
| inversion_0.2 | video:window_mean_best | -3.9% | 18.3% | 72.6% | 58.3% |
| inversion_0.3 | long | 0.6% | -18.9% | 85.4% | 27.8% |
| inversion_0.3 | video:max_proj | 0.3% | 5.0% | 62.2% | 25.0% |
| inversion_0.3 | video:single_best | 15.1% | 58.3% | 70.6% | 58.3% |
| inversion_0.3 | video:temporal_mean | -8.0% | 30.0% | 69.2% | 50.0% |
| inversion_0.3 | video:window_mean_best | -3.8% | 18.3% | 72.6% | 58.3% |
| inversion_0.5 | long | 0.2% | -18.9% | 85.4% | 27.8% |
| inversion_0.5 | video:max_proj | -8.4% | 5.0% | 62.2% | 25.0% |
| inversion_0.5 | video:single_best | 16.8% | 38.3% | 70.6% | 58.3% |
| inversion_0.5 | video:temporal_mean | -7.2% | -10.0% | 69.2% | 50.0% |
| inversion_0.5 | video:window_mean_best | 13.3% | 58.3% | 72.6% | 58.3% |
| inversion_1.0 | long | 58.6% | 27.8% | 85.4% | 27.8% |
| inversion_1.0 | video:max_proj | -10.3% | 25.0% | 62.2% | 25.0% |
| inversion_1.0 | video:single_best | 27.9% | 58.3% | 70.6% | 58.3% |
| inversion_1.0 | video:temporal_mean | 45.2% | 50.0% | 69.2% | 50.0% |
| inversion_1.0 | video:window_mean_best | -1.6% | 58.3% | 72.6% | 58.3% |
| mask_noise | long | -5.4% | -22.2% | 85.4% | 27.8% |
| mask_noise | short | 24.4% | 61.1% | 95.6% | 75.0% |
| mask_noise | video:max_proj | -16.2% | -8.3% | 62.2% | 25.0% |
| mask_noise | video:single_best | 1.9% | 58.3% | 70.6% | 58.3% |
| mask_noise | video:temporal_mean | -22.7% | -41.7% | 69.2% | 50.0% |
| mask_noise | video:window_mean_best | -18.5% | -25.0% | 72.6% | 58.3% |
| mask_only | long | 10.0% | -5.6% | 85.4% | 27.8% |
| mask_only | short | 78.6% | 72.2% | 95.6% | 75.0% |
| mask_only | video:max_proj | -15.6% | -25.0% | 62.2% | 25.0% |
| mask_only | video:single_best | 3.4% | 41.7% | 70.6% | 58.3% |
| mask_only | video:temporal_mean | -22.9% | -33.3% | 69.2% | 50.0% |
| mask_only | video:window_mean_best | -17.5% | -16.7% | 72.6% | 58.3% |
| original | long | 0.0% | 0.0% | 85.4% | 27.8% |
| original | short | 0.0% | 0.0% | 95.6% | 75.0% |
| original | video:max_proj | 0.0% | 0.0% | 62.2% | 25.0% |
| original | video:single_best | 0.0% | 0.0% | 70.6% | 58.3% |
| original | video:temporal_mean | 0.0% | 0.0% | 69.2% | 50.0% |
| original | video:window_mean_best | 0.0% | 0.0% | 72.6% | 58.3% |
| stripe_0.00 | short | 75.3% | 68.3% | 95.6% | 75.0% |
| stripe_0.00 | video:max_proj | -8.5% | 5.0% | 62.2% | 25.0% |
| stripe_0.00 | video:single_best | 26.8% | 58.3% | 70.6% | 58.3% |
| stripe_0.00 | video:temporal_mean | 7.4% | -10.0% | 69.2% | 50.0% |
| stripe_0.00 | video:window_mean_best | -5.7% | -1.7% | 72.6% | 58.3% |
| stripe_0.10 | short | 52.8% | 75.0% | 95.6% | 75.0% |
| stripe_0.10 | video:max_proj | -5.5% | 25.0% | 62.2% | 25.0% |
| stripe_0.10 | video:single_best | 28.6% | 58.3% | 70.6% | 58.3% |
| stripe_0.10 | video:temporal_mean | -10.6% | -30.0% | 69.2% | 50.0% |
| stripe_0.10 | video:window_mean_best | 3.4% | 18.3% | 72.6% | 58.3% |
| stripe_0.18 | short | 58.5% | 75.0% | 95.6% | 75.0% |
| stripe_0.18 | video:max_proj | -10.2% | 5.0% | 62.2% | 25.0% |
| stripe_0.18 | video:single_best | 21.2% | 58.3% | 70.6% | 58.3% |
| stripe_0.18 | video:temporal_mean | -9.5% | -10.0% | 69.2% | 50.0% |
| stripe_0.18 | video:window_mean_best | 3.2% | 18.3% | 72.6% | 58.3% |
| stripe_0.30 | short | 50.9% | 75.0% | 95.6% | 75.0% |
| stripe_0.30 | video:max_proj | -11.7% | 5.0% | 62.2% | 25.0% |
| stripe_0.30 | video:single_best | 21.1% | 58.3% | 70.6% | 58.3% |
| stripe_0.30 | video:temporal_mean | 7.4% | 10.0% | 69.2% | 50.0% |
| stripe_0.30 | video:window_mean_best | -1.6% | 58.3% | 72.6% | 58.3% |
| vlm | long | 68.7% | 27.8% | 85.4% | 27.8% |
| vlm | short | 88.5% | 75.0% | 95.6% | 75.0% |
| vlm | video:max_proj | 47.8% | 25.0% | 62.2% | 25.0% |
| vlm | video:single_best | 61.7% | 58.3% | 70.6% | 58.3% |
| vlm | video:temporal_mean | 13.7% | 50.0% | 69.2% | 50.0% |
| vlm | video:window_mean_best | 59.7% | 58.3% | 72.6% | 58.3% |
