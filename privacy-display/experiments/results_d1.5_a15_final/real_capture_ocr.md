# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 26.7% | 16.7% | 84.0% | 33.3% |
| anti_ocr|short | 108 | 16.4% | 0.0% | 30.2% | 35.2% |
| anti_ocr|video|max_proj | 36 | 63.4% | 25.0% | 71.5% | 77.8% |
| anti_ocr|video|single_best | 36 | 48.9% | 8.3% | 33.5% | 69.4% |
| anti_ocr|video|temporal_mean | 36 | 79.3% | 47.2% | 70.4% | 94.4% |
| anti_ocr|video|window_mean_best | 36 | 72.7% | 25.0% | 54.3% | 88.9% |
| deployed|long | 108 | 33.9% | 15.7% | 80.8% | 44.4% |
| deployed|short | 153 | 12.6% | 0.0% | 23.8% | 24.8% |
| deployed|video|max_proj | 51 | 65.4% | 23.5% | 65.2% | 82.4% |
| deployed|video|single_best | 51 | 46.4% | 7.8% | 35.6% | 70.6% |
| deployed|video|temporal_mean | 51 | 70.9% | 45.1% | 70.1% | 90.2% |
| deployed|video|window_mean_best | 51 | 71.3% | 23.5% | 54.1% | 86.3% |
| glyph_0.00|short | 45 | 16.2% | 0.0% | 21.4% | 26.7% |
| glyph_0.00|video|max_proj | 15 | 46.6% | 0.0% | 52.9% | 60.0% |
| glyph_0.00|video|single_best | 15 | 27.7% | 0.0% | 19.0% | 60.0% |
| glyph_0.00|video|temporal_mean | 15 | 60.0% | 33.3% | 56.9% | 86.7% |
| glyph_0.00|video|window_mean_best | 15 | 60.4% | 20.0% | 43.9% | 80.0% |
| glyph_0.12|short | 45 | 7.0% | 0.0% | 12.4% | 11.1% |
| glyph_0.12|video|max_proj | 15 | 48.0% | 0.0% | 44.3% | 66.7% |
| glyph_0.12|video|single_best | 15 | 32.4% | 0.0% | 22.4% | 60.0% |
| glyph_0.12|video|temporal_mean | 15 | 64.7% | 20.0% | 63.2% | 73.3% |
| glyph_0.12|video|window_mean_best | 15 | 61.9% | 26.7% | 52.5% | 80.0% |
| glyph_0.22|short | 45 | 17.8% | 0.0% | 22.1% | 37.8% |
| glyph_0.22|video|max_proj | 15 | 54.8% | 13.3% | 59.4% | 73.3% |
| glyph_0.22|video|single_best | 15 | 25.7% | 0.0% | 13.8% | 40.0% |
| glyph_0.22|video|temporal_mean | 15 | 60.7% | 40.0% | 63.2% | 66.7% |
| glyph_0.22|video|window_mean_best | 15 | 66.3% | 20.0% | 47.7% | 80.0% |
| inversion_0.0|long | 45 | 34.2% | 13.3% | 78.0% | 48.9% |
| inversion_0.0|video|max_proj | 15 | 50.1% | 13.3% | 63.8% | 60.0% |
| inversion_0.0|video|single_best | 15 | 21.1% | 0.0% | 8.9% | 40.0% |
| inversion_0.0|video|temporal_mean | 15 | 66.0% | 26.7% | 53.8% | 86.7% |
| inversion_0.0|video|window_mean_best | 15 | 58.6% | 20.0% | 54.6% | 80.0% |
| inversion_0.2|long | 45 | 26.0% | 13.3% | 75.1% | 37.8% |
| inversion_0.2|video|max_proj | 15 | 49.8% | 6.7% | 59.8% | 66.7% |
| inversion_0.2|video|single_best | 15 | 33.8% | 6.7% | 19.2% | 60.0% |
| inversion_0.2|video|temporal_mean | 15 | 59.8% | 26.7% | 62.1% | 80.0% |
| inversion_0.2|video|window_mean_best | 15 | 57.8% | 13.3% | 62.5% | 66.7% |
| inversion_0.3|long | 45 | 38.6% | 17.8% | 74.4% | 46.7% |
| inversion_0.3|video|max_proj | 15 | 47.9% | 0.0% | 42.3% | 73.3% |
| inversion_0.3|video|single_best | 15 | 18.8% | 0.0% | 20.2% | 26.7% |
| inversion_0.3|video|temporal_mean | 15 | 58.6% | 33.3% | 61.5% | 86.7% |
| inversion_0.3|video|window_mean_best | 15 | 58.5% | 13.3% | 32.9% | 80.0% |
| inversion_0.5|long | 45 | 33.6% | 17.8% | 75.3% | 51.1% |
| inversion_0.5|video|max_proj | 15 | 39.8% | 0.0% | 39.5% | 53.3% |
| inversion_0.5|video|single_best | 15 | 35.8% | 6.7% | 26.0% | 66.7% |
| inversion_0.5|video|temporal_mean | 15 | 59.8% | 40.0% | 56.9% | 73.3% |
| inversion_0.5|video|window_mean_best | 15 | 64.1% | 26.7% | 48.7% | 80.0% |
| inversion_1.0|long | 45 | 12.6% | 0.0% | 31.8% | 22.2% |
| inversion_1.0|video|max_proj | 15 | 28.8% | 0.0% | 27.7% | 40.0% |
| inversion_1.0|video|single_best | 15 | 56.2% | 26.7% | 62.7% | 80.0% |
| inversion_1.0|video|temporal_mean | 15 | 11.3% | 0.0% | 35.5% | 26.7% |
| inversion_1.0|video|window_mean_best | 15 | 63.4% | 6.7% | 59.4% | 80.0% |
| mask_noise|long | 108 | 28.2% | 12.0% | 87.2% | 35.2% |
| mask_noise|short | 108 | 23.0% | 1.9% | 31.1% | 41.7% |
| mask_noise|video|max_proj | 36 | 75.3% | 38.9% | 73.2% | 86.1% |
| mask_noise|video|single_best | 36 | 42.2% | 11.1% | 30.0% | 66.7% |
| mask_noise|video|temporal_mean | 36 | 82.8% | 52.8% | 72.5% | 97.2% |
| mask_noise|video|window_mean_best | 36 | 73.9% | 36.1% | 66.5% | 91.7% |
| mask_only|long | 108 | 33.0% | 13.0% | 88.4% | 41.7% |
| mask_only|short | 108 | 12.9% | 0.0% | 25.9% | 27.8% |
| mask_only|video|max_proj | 36 | 72.8% | 27.8% | 69.9% | 86.1% |
| mask_only|video|single_best | 36 | 45.0% | 11.1% | 32.1% | 63.9% |
| mask_only|video|temporal_mean | 36 | 79.4% | 50.0% | 62.8% | 94.4% |
| mask_only|video|window_mean_best | 36 | 77.0% | 47.2% | 63.8% | 88.9% |
| original|long | 108 | 5.7% | 0.0% | 54.8% | 10.2% |
| original|short | 108 | 61.4% | 38.0% | 87.1% | 68.5% |
| original|video|max_proj | 36 | 55.3% | 13.9% | 61.1% | 75.0% |
| original|video|single_best | 36 | 78.7% | 38.9% | 70.1% | 88.9% |
| original|video|temporal_mean | 36 | 85.8% | 52.8% | 77.1% | 97.2% |
| original|video|window_mean_best | 36 | 76.4% | 41.7% | 70.2% | 86.1% |
| stripe_0.00|short | 45 | 6.1% | 0.0% | 11.2% | 11.1% |
| stripe_0.00|video|max_proj | 15 | 46.9% | 13.3% | 53.1% | 66.7% |
| stripe_0.00|video|single_best | 15 | 35.5% | 0.0% | 29.0% | 66.7% |
| stripe_0.00|video|temporal_mean | 15 | 62.6% | 40.0% | 61.6% | 80.0% |
| stripe_0.00|video|window_mean_best | 15 | 66.2% | 33.3% | 57.2% | 80.0% |
| stripe_0.10|short | 45 | 9.4% | 0.0% | 12.9% | 17.8% |
| stripe_0.10|video|max_proj | 15 | 50.9% | 6.7% | 57.6% | 66.7% |
| stripe_0.10|video|single_best | 15 | 31.1% | 0.0% | 16.9% | 53.3% |
| stripe_0.10|video|temporal_mean | 15 | 59.6% | 40.0% | 62.2% | 86.7% |
| stripe_0.10|video|window_mean_best | 15 | 62.7% | 20.0% | 45.6% | 80.0% |
| stripe_0.18|short | 45 | 7.4% | 0.0% | 9.7% | 13.3% |
| stripe_0.18|video|max_proj | 15 | 44.2% | 0.0% | 62.0% | 60.0% |
| stripe_0.18|video|single_best | 15 | 25.8% | 0.0% | 14.4% | 53.3% |
| stripe_0.18|video|temporal_mean | 15 | 63.9% | 40.0% | 66.7% | 80.0% |
| stripe_0.18|video|window_mean_best | 15 | 64.4% | 20.0% | 55.6% | 80.0% |
| stripe_0.30|short | 45 | 8.4% | 0.0% | 16.1% | 13.3% |
| stripe_0.30|video|max_proj | 15 | 58.2% | 20.0% | 63.9% | 66.7% |
| stripe_0.30|video|single_best | 15 | 30.9% | 0.0% | 15.2% | 66.7% |
| stripe_0.30|video|temporal_mean | 15 | 61.2% | 26.7% | 65.3% | 80.0% |
| stripe_0.30|video|window_mean_best | 15 | 55.3% | 13.3% | 59.0% | 80.0% |
| vlm|long | 108 | 3.7% | 0.0% | 9.4% | 3.7% |
| vlm|short | 108 | 2.3% | 0.0% | 1.3% | 4.6% |
| vlm|video|max_proj | 36 | 7.5% | 0.0% | 4.2% | 8.3% |
| vlm|video|single_best | 36 | 2.1% | 0.0% | 3.6% | 2.8% |
| vlm|video|temporal_mean | 36 | 21.0% | 0.0% | 9.2% | 36.1% |
| vlm|video|window_mean_best | 36 | 4.7% | 0.0% | 6.3% | 8.3% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 72.3% | 50.0% | 93.6% | 83.3% |
| anti_ocr | short | 36 | 40.2% | 0.0% | 73.2% | 86.1% |
| anti_ocr | video:max_proj | 12 | 84.4% | 50.0% | 92.1% | 91.7% |
| anti_ocr | video:single_best | 12 | 82.6% | 25.0% | 72.9% | 91.7% |
| anti_ocr | video:temporal_mean | 12 | 91.1% | 83.3% | 93.1% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 89.8% | 66.7% | 83.0% | 91.7% |
| deployed | long | 36 | 75.8% | 41.7% | 95.5% | 88.9% |
| deployed | short | 51 | 30.0% | 0.0% | 55.1% | 54.9% |
| deployed | video:max_proj | 17 | 82.9% | 52.9% | 85.9% | 94.1% |
| deployed | video:single_best | 17 | 71.6% | 23.5% | 71.5% | 88.2% |
| deployed | video:temporal_mean | 17 | 86.4% | 82.4% | 88.5% | 94.1% |
| deployed | video:window_mean_best | 17 | 85.5% | 47.1% | 81.8% | 88.2% |
| glyph_0.00 | short | 15 | 33.8% | 0.0% | 51.7% | 60.0% |
| glyph_0.00 | video:max_proj | 5 | 68.4% | 0.0% | 78.5% | 80.0% |
| glyph_0.00 | video:single_best | 5 | 46.2% | 0.0% | 37.1% | 80.0% |
| glyph_0.00 | video:temporal_mean | 5 | 79.5% | 60.0% | 79.0% | 100.0% |
| glyph_0.00 | video:window_mean_best | 5 | 77.6% | 60.0% | 78.5% | 80.0% |
| glyph_0.12 | short | 15 | 16.5% | 0.0% | 34.3% | 26.7% |
| glyph_0.12 | video:max_proj | 5 | 68.6% | 0.0% | 52.6% | 80.0% |
| glyph_0.12 | video:single_best | 5 | 54.1% | 0.0% | 51.2% | 80.0% |
| glyph_0.12 | video:temporal_mean | 5 | 77.2% | 60.0% | 78.1% | 80.0% |
| glyph_0.12 | video:window_mean_best | 5 | 78.5% | 60.0% | 79.0% | 80.0% |
| glyph_0.22 | short | 15 | 28.5% | 0.0% | 52.6% | 53.3% |
| glyph_0.22 | video:max_proj | 5 | 75.5% | 20.0% | 77.4% | 100.0% |
| glyph_0.22 | video:single_best | 5 | 44.0% | 0.0% | 31.4% | 60.0% |
| glyph_0.22 | video:temporal_mean | 5 | 77.4% | 60.0% | 78.5% | 80.0% |
| glyph_0.22 | video:window_mean_best | 5 | 76.9% | 40.0% | 54.5% | 80.0% |
| inversion_0.0 | long | 15 | 76.8% | 40.0% | 88.0% | 100.0% |
| inversion_0.0 | video:max_proj | 5 | 73.9% | 20.0% | 78.5% | 80.0% |
| inversion_0.0 | video:single_best | 5 | 32.0% | 0.0% | 16.7% | 60.0% |
| inversion_0.0 | video:temporal_mean | 5 | 78.7% | 80.0% | 79.0% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 77.6% | 60.0% | 77.8% | 100.0% |
| inversion_0.2 | long | 15 | 64.7% | 40.0% | 81.6% | 80.0% |
| inversion_0.2 | video:max_proj | 5 | 75.1% | 20.0% | 77.8% | 100.0% |
| inversion_0.2 | video:single_best | 5 | 49.0% | 20.0% | 47.1% | 80.0% |
| inversion_0.2 | video:temporal_mean | 5 | 77.7% | 80.0% | 78.1% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 75.6% | 40.0% | 78.3% | 80.0% |
| inversion_0.3 | long | 15 | 84.3% | 46.7% | 88.8% | 100.0% |
| inversion_0.3 | video:max_proj | 5 | 67.9% | 0.0% | 53.3% | 100.0% |
| inversion_0.3 | video:single_best | 5 | 38.5% | 0.0% | 47.1% | 40.0% |
| inversion_0.3 | video:temporal_mean | 5 | 74.5% | 60.0% | 78.3% | 100.0% |
| inversion_0.3 | video:window_mean_best | 5 | 76.8% | 40.0% | 54.0% | 80.0% |
| inversion_0.5 | long | 15 | 73.6% | 53.3% | 84.0% | 93.3% |
| inversion_0.5 | video:max_proj | 5 | 60.6% | 0.0% | 51.9% | 80.0% |
| inversion_0.5 | video:single_best | 5 | 56.4% | 20.0% | 64.3% | 80.0% |
| inversion_0.5 | video:temporal_mean | 5 | 78.4% | 80.0% | 78.5% | 100.0% |
| inversion_0.5 | video:window_mean_best | 5 | 77.5% | 60.0% | 78.1% | 80.0% |
| inversion_1.0 | long | 15 | 26.4% | 0.0% | 53.3% | 46.7% |
| inversion_1.0 | video:max_proj | 5 | 61.1% | 0.0% | 48.8% | 100.0% |
| inversion_1.0 | video:single_best | 5 | 72.9% | 60.0% | 76.4% | 100.0% |
| inversion_1.0 | video:temporal_mean | 5 | 28.7% | 0.0% | 78.8% | 60.0% |
| inversion_1.0 | video:window_mean_best | 5 | 76.3% | 20.0% | 77.8% | 80.0% |
| mask_noise | long | 36 | 63.8% | 36.1% | 95.8% | 72.2% |
| mask_noise | short | 36 | 45.5% | 5.6% | 71.2% | 83.3% |
| mask_noise | video:max_proj | 12 | 89.4% | 83.3% | 92.2% | 91.7% |
| mask_noise | video:single_best | 12 | 70.7% | 33.3% | 70.3% | 91.7% |
| mask_noise | video:temporal_mean | 12 | 91.6% | 91.7% | 93.0% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 89.6% | 75.0% | 92.1% | 100.0% |
| mask_only | long | 36 | 73.2% | 38.9% | 97.1% | 80.6% |
| mask_only | short | 36 | 32.3% | 0.0% | 71.1% | 66.7% |
| mask_only | video:max_proj | 12 | 87.1% | 58.3% | 92.3% | 91.7% |
| mask_only | video:single_best | 12 | 74.1% | 33.3% | 71.8% | 83.3% |
| mask_only | video:temporal_mean | 12 | 91.4% | 91.7% | 92.6% | 100.0% |
| mask_only | video:window_mean_best | 12 | 90.8% | 83.3% | 92.1% | 100.0% |
| original | long | 36 | 16.9% | 0.0% | 93.3% | 30.6% |
| original | short | 36 | 94.2% | 66.7% | 98.2% | 100.0% |
| original | video:max_proj | 12 | 86.1% | 25.0% | 83.6% | 100.0% |
| original | video:single_best | 12 | 91.1% | 75.0% | 83.4% | 100.0% |
| original | video:temporal_mean | 12 | 92.3% | 91.7% | 92.7% | 100.0% |
| original | video:window_mean_best | 12 | 91.1% | 66.7% | 83.6% | 100.0% |
| stripe_0.00 | short | 15 | 16.4% | 0.0% | 28.6% | 33.3% |
| stripe_0.00 | video:max_proj | 5 | 71.5% | 20.0% | 77.8% | 100.0% |
| stripe_0.00 | video:single_best | 5 | 53.6% | 0.0% | 61.2% | 80.0% |
| stripe_0.00 | video:temporal_mean | 5 | 78.2% | 80.0% | 78.3% | 100.0% |
| stripe_0.00 | video:window_mean_best | 5 | 77.6% | 60.0% | 77.8% | 80.0% |
| stripe_0.10 | short | 15 | 20.4% | 0.0% | 34.7% | 40.0% |
| stripe_0.10 | video:max_proj | 5 | 71.0% | 20.0% | 77.8% | 80.0% |
| stripe_0.10 | video:single_best | 5 | 54.8% | 0.0% | 30.7% | 80.0% |
| stripe_0.10 | video:temporal_mean | 5 | 79.3% | 80.0% | 78.1% | 100.0% |
| stripe_0.10 | video:window_mean_best | 5 | 77.3% | 60.0% | 79.0% | 80.0% |
| stripe_0.18 | short | 15 | 16.0% | 0.0% | 28.2% | 26.7% |
| stripe_0.18 | video:max_proj | 5 | 72.7% | 0.0% | 77.6% | 100.0% |
| stripe_0.18 | video:single_best | 5 | 44.8% | 0.0% | 39.8% | 80.0% |
| stripe_0.18 | video:temporal_mean | 5 | 79.5% | 80.0% | 78.3% | 100.0% |
| stripe_0.18 | video:window_mean_best | 5 | 77.2% | 40.0% | 79.7% | 80.0% |
| stripe_0.30 | short | 15 | 18.3% | 0.0% | 35.4% | 33.3% |
| stripe_0.30 | video:max_proj | 5 | 75.4% | 40.0% | 77.8% | 80.0% |
| stripe_0.30 | video:single_best | 5 | 53.4% | 0.0% | 41.9% | 80.0% |
| stripe_0.30 | video:temporal_mean | 5 | 78.4% | 60.0% | 78.1% | 80.0% |
| stripe_0.30 | video:window_mean_best | 5 | 74.8% | 40.0% | 78.5% | 100.0% |
| vlm | long | 36 | 10.1% | 0.0% | 27.7% | 11.1% |
| vlm | short | 36 | 6.5% | 0.0% | 3.9% | 13.9% |
| vlm | video:max_proj | 12 | 16.7% | 0.0% | 12.5% | 25.0% |
| vlm | video:single_best | 12 | 6.1% | 0.0% | 10.8% | 8.3% |
| vlm | video:temporal_mean | 12 | 49.2% | 0.0% | 26.9% | 91.7% |
| vlm | video:window_mean_best | 12 | 12.6% | 0.0% | 18.9% | 25.0% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | -55.4% | -50.0% | 16.9% | 0.0% |
| anti_ocr | short | 54.0% | 66.7% | 94.2% | 66.7% |
| anti_ocr | video:max_proj | 1.7% | -25.0% | 86.1% | 25.0% |
| anti_ocr | video:single_best | 8.6% | 50.0% | 91.1% | 75.0% |
| anti_ocr | video:temporal_mean | 1.2% | 8.3% | 92.3% | 91.7% |
| anti_ocr | video:window_mean_best | 1.3% | 0.0% | 91.1% | 66.7% |
| deployed | long | -59.0% | -41.7% | 16.9% | 0.0% |
| deployed | short | 64.2% | 66.7% | 94.2% | 66.7% |
| deployed | video:max_proj | 3.2% | -27.9% | 86.1% | 25.0% |
| deployed | video:single_best | 19.6% | 51.5% | 91.1% | 75.0% |
| deployed | video:temporal_mean | 5.9% | 9.3% | 92.3% | 91.7% |
| deployed | video:window_mean_best | 5.6% | 19.6% | 91.1% | 66.7% |
| glyph_0.00 | short | 60.4% | 66.7% | 94.2% | 66.7% |
| glyph_0.00 | video:max_proj | 17.7% | 25.0% | 86.1% | 25.0% |
| glyph_0.00 | video:single_best | 44.9% | 75.0% | 91.1% | 75.0% |
| glyph_0.00 | video:temporal_mean | 12.8% | 31.7% | 92.3% | 91.7% |
| glyph_0.00 | video:window_mean_best | 13.5% | 6.7% | 91.1% | 66.7% |
| glyph_0.12 | short | 77.7% | 66.7% | 94.2% | 66.7% |
| glyph_0.12 | video:max_proj | 17.5% | 25.0% | 86.1% | 25.0% |
| glyph_0.12 | video:single_best | 37.0% | 75.0% | 91.1% | 75.0% |
| glyph_0.12 | video:temporal_mean | 15.0% | 31.7% | 92.3% | 91.7% |
| glyph_0.12 | video:window_mean_best | 12.6% | 6.7% | 91.1% | 66.7% |
| glyph_0.22 | short | 65.7% | 66.7% | 94.2% | 66.7% |
| glyph_0.22 | video:max_proj | 10.6% | 5.0% | 86.1% | 25.0% |
| glyph_0.22 | video:single_best | 47.1% | 75.0% | 91.1% | 75.0% |
| glyph_0.22 | video:temporal_mean | 14.9% | 31.7% | 92.3% | 91.7% |
| glyph_0.22 | video:window_mean_best | 14.2% | 26.7% | 91.1% | 66.7% |
| inversion_0.0 | long | -59.9% | -40.0% | 16.9% | 0.0% |
| inversion_0.0 | video:max_proj | 12.2% | 5.0% | 86.1% | 25.0% |
| inversion_0.0 | video:single_best | 59.1% | 75.0% | 91.1% | 75.0% |
| inversion_0.0 | video:temporal_mean | 13.6% | 11.7% | 92.3% | 91.7% |
| inversion_0.0 | video:window_mean_best | 13.5% | 6.7% | 91.1% | 66.7% |
| inversion_0.2 | long | -47.8% | -40.0% | 16.9% | 0.0% |
| inversion_0.2 | video:max_proj | 11.0% | 5.0% | 86.1% | 25.0% |
| inversion_0.2 | video:single_best | 42.1% | 55.0% | 91.1% | 75.0% |
| inversion_0.2 | video:temporal_mean | 14.5% | 11.7% | 92.3% | 91.7% |
| inversion_0.2 | video:window_mean_best | 15.5% | 26.7% | 91.1% | 66.7% |
| inversion_0.3 | long | -67.4% | -46.7% | 16.9% | 0.0% |
| inversion_0.3 | video:max_proj | 18.2% | 25.0% | 86.1% | 25.0% |
| inversion_0.3 | video:single_best | 52.6% | 75.0% | 91.1% | 75.0% |
| inversion_0.3 | video:temporal_mean | 17.7% | 31.7% | 92.3% | 91.7% |
| inversion_0.3 | video:window_mean_best | 14.3% | 26.7% | 91.1% | 66.7% |
| inversion_0.5 | long | -56.8% | -53.3% | 16.9% | 0.0% |
| inversion_0.5 | video:max_proj | 25.5% | 25.0% | 86.1% | 25.0% |
| inversion_0.5 | video:single_best | 34.7% | 55.0% | 91.1% | 75.0% |
| inversion_0.5 | video:temporal_mean | 13.8% | 11.7% | 92.3% | 91.7% |
| inversion_0.5 | video:window_mean_best | 13.7% | 6.7% | 91.1% | 66.7% |
| inversion_1.0 | long | -9.5% | 0.0% | 16.9% | 0.0% |
| inversion_1.0 | video:max_proj | 25.0% | 25.0% | 86.1% | 25.0% |
| inversion_1.0 | video:single_best | 18.2% | 15.0% | 91.1% | 75.0% |
| inversion_1.0 | video:temporal_mean | 63.6% | 91.7% | 92.3% | 91.7% |
| inversion_1.0 | video:window_mean_best | 14.8% | 46.7% | 91.1% | 66.7% |
| mask_noise | long | -46.9% | -36.1% | 16.9% | 0.0% |
| mask_noise | short | 48.7% | 61.1% | 94.2% | 66.7% |
| mask_noise | video:max_proj | -3.3% | -58.3% | 86.1% | 25.0% |
| mask_noise | video:single_best | 20.4% | 41.7% | 91.1% | 75.0% |
| mask_noise | video:temporal_mean | 0.6% | 0.0% | 92.3% | 91.7% |
| mask_noise | video:window_mean_best | 1.5% | -8.3% | 91.1% | 66.7% |
| mask_only | long | -56.3% | -38.9% | 16.9% | 0.0% |
| mask_only | short | 61.9% | 66.7% | 94.2% | 66.7% |
| mask_only | video:max_proj | -1.0% | -33.3% | 86.1% | 25.0% |
| mask_only | video:single_best | 17.0% | 41.7% | 91.1% | 75.0% |
| mask_only | video:temporal_mean | 0.8% | 0.0% | 92.3% | 91.7% |
| mask_only | video:window_mean_best | 0.3% | -16.7% | 91.1% | 66.7% |
| original | long | 0.0% | 0.0% | 16.9% | 0.0% |
| original | short | 0.0% | 0.0% | 94.2% | 66.7% |
| original | video:max_proj | 0.0% | 0.0% | 86.1% | 25.0% |
| original | video:single_best | 0.0% | 0.0% | 91.1% | 75.0% |
| original | video:temporal_mean | 0.0% | 0.0% | 92.3% | 91.7% |
| original | video:window_mean_best | 0.0% | 0.0% | 91.1% | 66.7% |
| stripe_0.00 | short | 77.8% | 66.7% | 94.2% | 66.7% |
| stripe_0.00 | video:max_proj | 14.5% | 5.0% | 86.1% | 25.0% |
| stripe_0.00 | video:single_best | 37.5% | 75.0% | 91.1% | 75.0% |
| stripe_0.00 | video:temporal_mean | 14.1% | 11.7% | 92.3% | 91.7% |
| stripe_0.00 | video:window_mean_best | 13.5% | 6.7% | 91.1% | 66.7% |
| stripe_0.10 | short | 73.8% | 66.7% | 94.2% | 66.7% |
| stripe_0.10 | video:max_proj | 15.0% | 5.0% | 86.1% | 25.0% |
| stripe_0.10 | video:single_best | 36.3% | 75.0% | 91.1% | 75.0% |
| stripe_0.10 | video:temporal_mean | 13.0% | 11.7% | 92.3% | 91.7% |
| stripe_0.10 | video:window_mean_best | 13.8% | 6.7% | 91.1% | 66.7% |
| stripe_0.18 | short | 78.2% | 66.7% | 94.2% | 66.7% |
| stripe_0.18 | video:max_proj | 13.4% | 25.0% | 86.1% | 25.0% |
| stripe_0.18 | video:single_best | 46.3% | 75.0% | 91.1% | 75.0% |
| stripe_0.18 | video:temporal_mean | 12.7% | 11.7% | 92.3% | 91.7% |
| stripe_0.18 | video:window_mean_best | 14.0% | 26.7% | 91.1% | 66.7% |
| stripe_0.30 | short | 75.9% | 66.7% | 94.2% | 66.7% |
| stripe_0.30 | video:max_proj | 10.7% | -15.0% | 86.1% | 25.0% |
| stripe_0.30 | video:single_best | 37.7% | 75.0% | 91.1% | 75.0% |
| stripe_0.30 | video:temporal_mean | 13.9% | 31.7% | 92.3% | 91.7% |
| stripe_0.30 | video:window_mean_best | 16.4% | 26.7% | 91.1% | 66.7% |
| vlm | long | 6.8% | 0.0% | 16.9% | 0.0% |
| vlm | short | 87.7% | 66.7% | 94.2% | 66.7% |
| vlm | video:max_proj | 69.4% | 25.0% | 86.1% | 25.0% |
| vlm | video:single_best | 85.0% | 75.0% | 91.1% | 75.0% |
| vlm | video:temporal_mean | 43.1% | 91.7% | 92.3% | 91.7% |
| vlm | video:window_mean_best | 78.6% | 66.7% | 91.1% | 66.7% |
