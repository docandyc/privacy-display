# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 1175

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 36 | 65.2% | 22.2% | 79.1% | 77.8% |
| anti_ocr|short | 36 | 2.3% | 0.0% | 0.0% | 0.0% |
| anti_ocr|video|max_proj | 12 | 18.9% | 0.0% | 9.9% | 33.3% |
| anti_ocr|video|single_best | 12 | 2.7% | 0.0% | 2.1% | 8.3% |
| anti_ocr|video|temporal_mean | 12 | 77.6% | 0.0% | 76.1% | 100.0% |
| anti_ocr|video|window_mean_best | 12 | 10.1% | 0.0% | 4.9% | 16.7% |
| deployed|long | 36 | 29.4% | 2.8% | 34.2% | 36.1% |
| deployed|short | 51 | 2.7% | 0.0% | 0.3% | 3.9% |
| deployed|video|max_proj | 17 | 5.8% | 0.0% | 12.4% | 5.9% |
| deployed|video|single_best | 17 | 3.8% | 0.0% | 0.5% | 0.0% |
| deployed|video|temporal_mean | 17 | 44.2% | 0.0% | 63.0% | 64.7% |
| deployed|video|window_mean_best | 17 | 9.9% | 0.0% | 13.8% | 11.8% |
| glyph_0.00|short | 15 | 3.6% | 0.0% | 0.8% | 0.0% |
| glyph_0.00|video|max_proj | 5 | 12.8% | 0.0% | 12.6% | 20.0% |
| glyph_0.00|video|single_best | 5 | 10.4% | 0.0% | 1.2% | 20.0% |
| glyph_0.00|video|temporal_mean | 5 | 37.8% | 0.0% | 59.0% | 60.0% |
| glyph_0.00|video|window_mean_best | 5 | 31.5% | 0.0% | 17.4% | 40.0% |
| glyph_0.12|short | 15 | 1.2% | 0.0% | 0.2% | 0.0% |
| glyph_0.12|video|max_proj | 5 | 9.2% | 0.0% | 23.8% | 20.0% |
| glyph_0.12|video|single_best | 5 | 2.2% | 0.0% | 0.9% | 0.0% |
| glyph_0.12|video|temporal_mean | 5 | 58.9% | 0.0% | 54.7% | 80.0% |
| glyph_0.12|video|window_mean_best | 5 | 3.8% | 0.0% | 1.9% | 0.0% |
| glyph_0.22|short | 15 | 0.7% | 0.0% | 0.0% | 0.0% |
| glyph_0.22|video|max_proj | 5 | 7.1% | 0.0% | 1.2% | 0.0% |
| glyph_0.22|video|single_best | 5 | 3.9% | 0.0% | 1.7% | 0.0% |
| glyph_0.22|video|temporal_mean | 5 | 50.3% | 0.0% | 47.3% | 80.0% |
| glyph_0.22|video|window_mean_best | 5 | 13.7% | 0.0% | 1.7% | 20.0% |
| inversion_0.0|long | 15 | 48.3% | 20.0% | 88.7% | 73.3% |
| inversion_0.0|video|max_proj | 5 | 9.6% | 0.0% | 24.0% | 20.0% |
| inversion_0.0|video|single_best | 5 | 6.7% | 0.0% | 1.2% | 0.0% |
| inversion_0.0|video|temporal_mean | 5 | 74.9% | 0.0% | 80.8% | 100.0% |
| inversion_0.0|video|window_mean_best | 5 | 22.4% | 0.0% | 16.7% | 40.0% |
| inversion_0.2|long | 15 | 54.9% | 13.3% | 67.0% | 80.0% |
| inversion_0.2|video|max_proj | 5 | 11.6% | 0.0% | 22.8% | 0.0% |
| inversion_0.2|video|single_best | 5 | 8.5% | 0.0% | 1.2% | 20.0% |
| inversion_0.2|video|temporal_mean | 5 | 59.8% | 20.0% | 79.0% | 80.0% |
| inversion_0.2|video|window_mean_best | 5 | 15.6% | 0.0% | 15.2% | 20.0% |
| inversion_0.3|long | 15 | 23.0% | 0.0% | 36.9% | 46.7% |
| inversion_0.3|video|max_proj | 5 | 8.0% | 0.0% | 2.4% | 20.0% |
| inversion_0.3|video|single_best | 5 | 7.5% | 0.0% | 1.2% | 0.0% |
| inversion_0.3|video|temporal_mean | 5 | 47.0% | 0.0% | 83.0% | 80.0% |
| inversion_0.3|video|window_mean_best | 5 | 4.3% | 0.0% | 1.2% | 20.0% |
| inversion_0.5|long | 15 | 4.6% | 0.0% | 20.0% | 6.7% |
| inversion_0.5|video|max_proj | 5 | 3.1% | 0.0% | 1.7% | 0.0% |
| inversion_0.5|video|single_best | 5 | 22.1% | 0.0% | 26.4% | 20.0% |
| inversion_0.5|video|temporal_mean | 5 | 38.2% | 0.0% | 48.5% | 60.0% |
| inversion_0.5|video|window_mean_best | 5 | 18.8% | 0.0% | 0.7% | 20.0% |
| inversion_1.0|long | 15 | 8.5% | 0.0% | 12.1% | 13.3% |
| inversion_1.0|video|max_proj | 5 | 56.1% | 0.0% | 67.1% | 80.0% |
| inversion_1.0|video|single_best | 5 | 9.9% | 0.0% | 4.3% | 20.0% |
| inversion_1.0|video|temporal_mean | 5 | 12.2% | 0.0% | 5.9% | 20.0% |
| inversion_1.0|video|window_mean_best | 5 | 12.1% | 0.0% | 12.6% | 20.0% |
| mask_noise|long | 36 | 53.1% | 11.1% | 76.8% | 63.9% |
| mask_noise|short | 36 | 3.3% | 0.0% | 0.1% | 2.8% |
| mask_noise|video|max_proj | 12 | 12.9% | 0.0% | 25.3% | 16.7% |
| mask_noise|video|single_best | 12 | 4.4% | 0.0% | 0.3% | 0.0% |
| mask_noise|video|temporal_mean | 12 | 84.0% | 16.7% | 86.8% | 100.0% |
| mask_noise|video|window_mean_best | 12 | 16.5% | 0.0% | 23.6% | 25.0% |
| mask_only|long | 36 | 50.1% | 8.3% | 67.5% | 58.3% |
| mask_only|short | 36 | 2.4% | 0.0% | 0.1% | 0.0% |
| mask_only|video|max_proj | 12 | 15.8% | 0.0% | 5.9% | 16.7% |
| mask_only|video|single_best | 12 | 2.1% | 0.0% | 0.5% | 8.3% |
| mask_only|video|temporal_mean | 12 | 59.4% | 0.0% | 55.1% | 83.3% |
| mask_only|video|window_mean_best | 12 | 30.2% | 0.0% | 31.1% | 41.7% |
| original|long | 36 | 80.9% | 55.6% | 77.3% | 91.7% |
| original|short | 36 | 86.0% | 47.2% | 85.8% | 97.2% |
| original|video|max_proj | 12 | 41.2% | 16.7% | 41.1% | 58.3% |
| original|video|single_best | 12 | 88.9% | 50.0% | 88.5% | 100.0% |
| original|video|temporal_mean | 12 | 88.7% | 58.3% | 88.5% | 100.0% |
| original|video|window_mean_best | 12 | 88.3% | 58.3% | 88.4% | 100.0% |
| stripe_0.00|short | 15 | 3.0% | 0.0% | 0.2% | 0.0% |
| stripe_0.00|video|max_proj | 5 | 5.7% | 0.0% | 33.3% | 0.0% |
| stripe_0.00|video|single_best | 5 | 6.1% | 0.0% | 1.7% | 20.0% |
| stripe_0.00|video|temporal_mean | 5 | 58.4% | 0.0% | 84.2% | 80.0% |
| stripe_0.00|video|window_mean_best | 5 | 18.6% | 0.0% | 11.7% | 20.0% |
| stripe_0.10|short | 15 | 1.1% | 0.0% | 0.2% | 0.0% |
| stripe_0.10|video|max_proj | 5 | 7.0% | 0.0% | 2.1% | 0.0% |
| stripe_0.10|video|single_best | 5 | 6.4% | 0.0% | 1.2% | 20.0% |
| stripe_0.10|video|temporal_mean | 5 | 59.2% | 0.0% | 68.7% | 100.0% |
| stripe_0.10|video|window_mean_best | 5 | 5.0% | 0.0% | 0.5% | 0.0% |
| stripe_0.18|short | 15 | 1.3% | 0.0% | 0.0% | 0.0% |
| stripe_0.18|video|max_proj | 5 | 2.8% | 0.0% | 2.4% | 0.0% |
| stripe_0.18|video|single_best | 5 | 4.6% | 0.0% | 1.9% | 20.0% |
| stripe_0.18|video|temporal_mean | 5 | 22.6% | 0.0% | 53.0% | 40.0% |
| stripe_0.18|video|window_mean_best | 5 | 3.5% | 0.0% | 16.2% | 0.0% |
| stripe_0.30|short | 15 | 2.8% | 0.0% | 0.9% | 0.0% |
| stripe_0.30|video|max_proj | 5 | 19.4% | 0.0% | 11.2% | 40.0% |
| stripe_0.30|video|single_best | 5 | 3.6% | 0.0% | 0.2% | 0.0% |
| stripe_0.30|video|temporal_mean | 5 | 51.2% | 0.0% | 75.2% | 80.0% |
| stripe_0.30|video|window_mean_best | 5 | 7.2% | 0.0% | 1.7% | 0.0% |
| vlm|long | 36 | 2.5% | 0.0% | 1.3% | 2.8% |
| vlm|short | 36 | 3.0% | 0.0% | 0.6% | 0.0% |
| vlm|video|max_proj | 12 | 5.7% | 0.0% | 0.4% | 8.3% |
| vlm|video|single_best | 12 | 1.8% | 0.0% | 0.3% | 0.0% |
| vlm|video|temporal_mean | 12 | 4.3% | 0.0% | 0.5% | 0.0% |
| vlm|video|window_mean_best | 12 | 3.9% | 0.0% | 2.4% | 16.7% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 65.2% | 22.2% | 79.1% | 77.8% |
| anti_ocr | short | 36 | 2.3% | 0.0% | 0.0% | 0.0% |
| anti_ocr | video:max_proj | 12 | 18.9% | 0.0% | 9.9% | 33.3% |
| anti_ocr | video:single_best | 12 | 2.7% | 0.0% | 2.1% | 8.3% |
| anti_ocr | video:temporal_mean | 12 | 77.6% | 0.0% | 76.1% | 100.0% |
| anti_ocr | video:window_mean_best | 12 | 10.1% | 0.0% | 4.9% | 16.7% |
| deployed | long | 36 | 29.4% | 2.8% | 34.2% | 36.1% |
| deployed | short | 51 | 2.7% | 0.0% | 0.3% | 3.9% |
| deployed | video:max_proj | 17 | 5.8% | 0.0% | 12.4% | 5.9% |
| deployed | video:single_best | 17 | 3.8% | 0.0% | 0.5% | 0.0% |
| deployed | video:temporal_mean | 17 | 44.2% | 0.0% | 63.0% | 64.7% |
| deployed | video:window_mean_best | 17 | 9.9% | 0.0% | 13.8% | 11.8% |
| glyph_0.00 | short | 15 | 3.6% | 0.0% | 0.8% | 0.0% |
| glyph_0.00 | video:max_proj | 5 | 12.8% | 0.0% | 12.6% | 20.0% |
| glyph_0.00 | video:single_best | 5 | 10.4% | 0.0% | 1.2% | 20.0% |
| glyph_0.00 | video:temporal_mean | 5 | 37.8% | 0.0% | 59.0% | 60.0% |
| glyph_0.00 | video:window_mean_best | 5 | 31.5% | 0.0% | 17.4% | 40.0% |
| glyph_0.12 | short | 15 | 1.2% | 0.0% | 0.2% | 0.0% |
| glyph_0.12 | video:max_proj | 5 | 9.2% | 0.0% | 23.8% | 20.0% |
| glyph_0.12 | video:single_best | 5 | 2.2% | 0.0% | 0.9% | 0.0% |
| glyph_0.12 | video:temporal_mean | 5 | 58.9% | 0.0% | 54.7% | 80.0% |
| glyph_0.12 | video:window_mean_best | 5 | 3.8% | 0.0% | 1.9% | 0.0% |
| glyph_0.22 | short | 15 | 0.7% | 0.0% | 0.0% | 0.0% |
| glyph_0.22 | video:max_proj | 5 | 7.1% | 0.0% | 1.2% | 0.0% |
| glyph_0.22 | video:single_best | 5 | 3.9% | 0.0% | 1.7% | 0.0% |
| glyph_0.22 | video:temporal_mean | 5 | 50.3% | 0.0% | 47.3% | 80.0% |
| glyph_0.22 | video:window_mean_best | 5 | 13.7% | 0.0% | 1.7% | 20.0% |
| inversion_0.0 | long | 15 | 48.3% | 20.0% | 88.7% | 73.3% |
| inversion_0.0 | video:max_proj | 5 | 9.6% | 0.0% | 24.0% | 20.0% |
| inversion_0.0 | video:single_best | 5 | 6.7% | 0.0% | 1.2% | 0.0% |
| inversion_0.0 | video:temporal_mean | 5 | 74.9% | 0.0% | 80.8% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 22.4% | 0.0% | 16.7% | 40.0% |
| inversion_0.2 | long | 15 | 54.9% | 13.3% | 67.0% | 80.0% |
| inversion_0.2 | video:max_proj | 5 | 11.6% | 0.0% | 22.8% | 0.0% |
| inversion_0.2 | video:single_best | 5 | 8.5% | 0.0% | 1.2% | 20.0% |
| inversion_0.2 | video:temporal_mean | 5 | 59.8% | 20.0% | 79.0% | 80.0% |
| inversion_0.2 | video:window_mean_best | 5 | 15.6% | 0.0% | 15.2% | 20.0% |
| inversion_0.3 | long | 15 | 23.0% | 0.0% | 36.9% | 46.7% |
| inversion_0.3 | video:max_proj | 5 | 8.0% | 0.0% | 2.4% | 20.0% |
| inversion_0.3 | video:single_best | 5 | 7.5% | 0.0% | 1.2% | 0.0% |
| inversion_0.3 | video:temporal_mean | 5 | 47.0% | 0.0% | 83.0% | 80.0% |
| inversion_0.3 | video:window_mean_best | 5 | 4.3% | 0.0% | 1.2% | 20.0% |
| inversion_0.5 | long | 15 | 4.6% | 0.0% | 20.0% | 6.7% |
| inversion_0.5 | video:max_proj | 5 | 3.1% | 0.0% | 1.7% | 0.0% |
| inversion_0.5 | video:single_best | 5 | 22.1% | 0.0% | 26.4% | 20.0% |
| inversion_0.5 | video:temporal_mean | 5 | 38.2% | 0.0% | 48.5% | 60.0% |
| inversion_0.5 | video:window_mean_best | 5 | 18.8% | 0.0% | 0.7% | 20.0% |
| inversion_1.0 | long | 15 | 8.5% | 0.0% | 12.1% | 13.3% |
| inversion_1.0 | video:max_proj | 5 | 56.1% | 0.0% | 67.1% | 80.0% |
| inversion_1.0 | video:single_best | 5 | 9.9% | 0.0% | 4.3% | 20.0% |
| inversion_1.0 | video:temporal_mean | 5 | 12.2% | 0.0% | 5.9% | 20.0% |
| inversion_1.0 | video:window_mean_best | 5 | 12.1% | 0.0% | 12.6% | 20.0% |
| mask_noise | long | 36 | 53.1% | 11.1% | 76.8% | 63.9% |
| mask_noise | short | 36 | 3.3% | 0.0% | 0.1% | 2.8% |
| mask_noise | video:max_proj | 12 | 12.9% | 0.0% | 25.3% | 16.7% |
| mask_noise | video:single_best | 12 | 4.4% | 0.0% | 0.3% | 0.0% |
| mask_noise | video:temporal_mean | 12 | 84.0% | 16.7% | 86.8% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 16.5% | 0.0% | 23.6% | 25.0% |
| mask_only | long | 36 | 50.1% | 8.3% | 67.5% | 58.3% |
| mask_only | short | 36 | 2.4% | 0.0% | 0.1% | 0.0% |
| mask_only | video:max_proj | 12 | 15.8% | 0.0% | 5.9% | 16.7% |
| mask_only | video:single_best | 12 | 2.1% | 0.0% | 0.5% | 8.3% |
| mask_only | video:temporal_mean | 12 | 59.4% | 0.0% | 55.1% | 83.3% |
| mask_only | video:window_mean_best | 12 | 30.2% | 0.0% | 31.1% | 41.7% |
| original | long | 36 | 80.9% | 55.6% | 77.3% | 91.7% |
| original | short | 36 | 86.0% | 47.2% | 85.8% | 97.2% |
| original | video:max_proj | 12 | 41.2% | 16.7% | 41.1% | 58.3% |
| original | video:single_best | 12 | 88.9% | 50.0% | 88.5% | 100.0% |
| original | video:temporal_mean | 12 | 88.7% | 58.3% | 88.5% | 100.0% |
| original | video:window_mean_best | 12 | 88.3% | 58.3% | 88.4% | 100.0% |
| stripe_0.00 | short | 15 | 3.0% | 0.0% | 0.2% | 0.0% |
| stripe_0.00 | video:max_proj | 5 | 5.7% | 0.0% | 33.3% | 0.0% |
| stripe_0.00 | video:single_best | 5 | 6.1% | 0.0% | 1.7% | 20.0% |
| stripe_0.00 | video:temporal_mean | 5 | 58.4% | 0.0% | 84.2% | 80.0% |
| stripe_0.00 | video:window_mean_best | 5 | 18.6% | 0.0% | 11.7% | 20.0% |
| stripe_0.10 | short | 15 | 1.1% | 0.0% | 0.2% | 0.0% |
| stripe_0.10 | video:max_proj | 5 | 7.0% | 0.0% | 2.1% | 0.0% |
| stripe_0.10 | video:single_best | 5 | 6.4% | 0.0% | 1.2% | 20.0% |
| stripe_0.10 | video:temporal_mean | 5 | 59.2% | 0.0% | 68.7% | 100.0% |
| stripe_0.10 | video:window_mean_best | 5 | 5.0% | 0.0% | 0.5% | 0.0% |
| stripe_0.18 | short | 15 | 1.3% | 0.0% | 0.0% | 0.0% |
| stripe_0.18 | video:max_proj | 5 | 2.8% | 0.0% | 2.4% | 0.0% |
| stripe_0.18 | video:single_best | 5 | 4.6% | 0.0% | 1.9% | 20.0% |
| stripe_0.18 | video:temporal_mean | 5 | 22.6% | 0.0% | 53.0% | 40.0% |
| stripe_0.18 | video:window_mean_best | 5 | 3.5% | 0.0% | 16.2% | 0.0% |
| stripe_0.30 | short | 15 | 2.8% | 0.0% | 0.9% | 0.0% |
| stripe_0.30 | video:max_proj | 5 | 19.4% | 0.0% | 11.2% | 40.0% |
| stripe_0.30 | video:single_best | 5 | 3.6% | 0.0% | 0.2% | 0.0% |
| stripe_0.30 | video:temporal_mean | 5 | 51.2% | 0.0% | 75.2% | 80.0% |
| stripe_0.30 | video:window_mean_best | 5 | 7.2% | 0.0% | 1.7% | 0.0% |
| vlm | long | 36 | 2.5% | 0.0% | 1.3% | 2.8% |
| vlm | short | 36 | 3.0% | 0.0% | 0.6% | 0.0% |
| vlm | video:max_proj | 12 | 5.7% | 0.0% | 0.4% | 8.3% |
| vlm | video:single_best | 12 | 1.8% | 0.0% | 0.3% | 0.0% |
| vlm | video:temporal_mean | 12 | 4.3% | 0.0% | 0.5% | 0.0% |
| vlm | video:window_mean_best | 12 | 3.9% | 0.0% | 2.4% | 16.7% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | 15.7% | 33.3% | 80.9% | 55.6% |
| anti_ocr | short | 83.7% | 47.2% | 86.0% | 47.2% |
| anti_ocr | video:max_proj | 22.3% | 16.7% | 41.2% | 16.7% |
| anti_ocr | video:single_best | 86.2% | 50.0% | 88.9% | 50.0% |
| anti_ocr | video:temporal_mean | 11.1% | 58.3% | 88.7% | 58.3% |
| anti_ocr | video:window_mean_best | 78.1% | 58.3% | 88.3% | 58.3% |
| deployed | long | 51.5% | 52.8% | 80.9% | 55.6% |
| deployed | short | 83.2% | 47.2% | 86.0% | 47.2% |
| deployed | video:max_proj | 35.4% | 16.7% | 41.2% | 16.7% |
| deployed | video:single_best | 85.1% | 50.0% | 88.9% | 50.0% |
| deployed | video:temporal_mean | 44.5% | 58.3% | 88.7% | 58.3% |
| deployed | video:window_mean_best | 78.3% | 58.3% | 88.3% | 58.3% |
| glyph_0.00 | short | 82.4% | 47.2% | 86.0% | 47.2% |
| glyph_0.00 | video:max_proj | 28.4% | 16.7% | 41.2% | 16.7% |
| glyph_0.00 | video:single_best | 78.5% | 50.0% | 88.9% | 50.0% |
| glyph_0.00 | video:temporal_mean | 50.9% | 58.3% | 88.7% | 58.3% |
| glyph_0.00 | video:window_mean_best | 56.7% | 58.3% | 88.3% | 58.3% |
| glyph_0.12 | short | 84.8% | 47.2% | 86.0% | 47.2% |
| glyph_0.12 | video:max_proj | 32.0% | 16.7% | 41.2% | 16.7% |
| glyph_0.12 | video:single_best | 86.7% | 50.0% | 88.9% | 50.0% |
| glyph_0.12 | video:temporal_mean | 29.9% | 58.3% | 88.7% | 58.3% |
| glyph_0.12 | video:window_mean_best | 84.5% | 58.3% | 88.3% | 58.3% |
| glyph_0.22 | short | 85.3% | 47.2% | 86.0% | 47.2% |
| glyph_0.22 | video:max_proj | 34.1% | 16.7% | 41.2% | 16.7% |
| glyph_0.22 | video:single_best | 85.0% | 50.0% | 88.9% | 50.0% |
| glyph_0.22 | video:temporal_mean | 38.4% | 58.3% | 88.7% | 58.3% |
| glyph_0.22 | video:window_mean_best | 74.6% | 58.3% | 88.3% | 58.3% |
| inversion_0.0 | long | 32.6% | 35.6% | 80.9% | 55.6% |
| inversion_0.0 | video:max_proj | 31.6% | 16.7% | 41.2% | 16.7% |
| inversion_0.0 | video:single_best | 82.2% | 50.0% | 88.9% | 50.0% |
| inversion_0.0 | video:temporal_mean | 13.8% | 58.3% | 88.7% | 58.3% |
| inversion_0.0 | video:window_mean_best | 65.8% | 58.3% | 88.3% | 58.3% |
| inversion_0.2 | long | 26.1% | 42.2% | 80.9% | 55.6% |
| inversion_0.2 | video:max_proj | 29.6% | 16.7% | 41.2% | 16.7% |
| inversion_0.2 | video:single_best | 80.4% | 50.0% | 88.9% | 50.0% |
| inversion_0.2 | video:temporal_mean | 28.9% | 38.3% | 88.7% | 58.3% |
| inversion_0.2 | video:window_mean_best | 72.6% | 58.3% | 88.3% | 58.3% |
| inversion_0.3 | long | 57.9% | 55.6% | 80.9% | 55.6% |
| inversion_0.3 | video:max_proj | 33.2% | 16.7% | 41.2% | 16.7% |
| inversion_0.3 | video:single_best | 81.4% | 50.0% | 88.9% | 50.0% |
| inversion_0.3 | video:temporal_mean | 41.7% | 58.3% | 88.7% | 58.3% |
| inversion_0.3 | video:window_mean_best | 83.9% | 58.3% | 88.3% | 58.3% |
| inversion_0.5 | long | 76.4% | 55.6% | 80.9% | 55.6% |
| inversion_0.5 | video:max_proj | 38.1% | 16.7% | 41.2% | 16.7% |
| inversion_0.5 | video:single_best | 66.8% | 50.0% | 88.9% | 50.0% |
| inversion_0.5 | video:temporal_mean | 50.5% | 58.3% | 88.7% | 58.3% |
| inversion_0.5 | video:window_mean_best | 69.4% | 58.3% | 88.3% | 58.3% |
| inversion_1.0 | long | 72.4% | 55.6% | 80.9% | 55.6% |
| inversion_1.0 | video:max_proj | -14.9% | 16.7% | 41.2% | 16.7% |
| inversion_1.0 | video:single_best | 79.0% | 50.0% | 88.9% | 50.0% |
| inversion_1.0 | video:temporal_mean | 76.5% | 58.3% | 88.7% | 58.3% |
| inversion_1.0 | video:window_mean_best | 76.2% | 58.3% | 88.3% | 58.3% |
| mask_noise | long | 27.8% | 44.4% | 80.9% | 55.6% |
| mask_noise | short | 82.6% | 47.2% | 86.0% | 47.2% |
| mask_noise | video:max_proj | 28.3% | 16.7% | 41.2% | 16.7% |
| mask_noise | video:single_best | 84.5% | 50.0% | 88.9% | 50.0% |
| mask_noise | video:temporal_mean | 4.7% | 41.7% | 88.7% | 58.3% |
| mask_noise | video:window_mean_best | 71.7% | 58.3% | 88.3% | 58.3% |
| mask_only | long | 30.9% | 47.2% | 80.9% | 55.6% |
| mask_only | short | 83.6% | 47.2% | 86.0% | 47.2% |
| mask_only | video:max_proj | 25.4% | 16.7% | 41.2% | 16.7% |
| mask_only | video:single_best | 86.8% | 50.0% | 88.9% | 50.0% |
| mask_only | video:temporal_mean | 29.3% | 58.3% | 88.7% | 58.3% |
| mask_only | video:window_mean_best | 58.1% | 58.3% | 88.3% | 58.3% |
| original | long | 0.0% | 0.0% | 80.9% | 55.6% |
| original | short | 0.0% | 0.0% | 86.0% | 47.2% |
| original | video:max_proj | 0.0% | 0.0% | 41.2% | 16.7% |
| original | video:single_best | 0.0% | 0.0% | 88.9% | 50.0% |
| original | video:temporal_mean | 0.0% | 0.0% | 88.7% | 58.3% |
| original | video:window_mean_best | 0.0% | 0.0% | 88.3% | 58.3% |
| stripe_0.00 | short | 82.9% | 47.2% | 86.0% | 47.2% |
| stripe_0.00 | video:max_proj | 35.5% | 16.7% | 41.2% | 16.7% |
| stripe_0.00 | video:single_best | 82.8% | 50.0% | 88.9% | 50.0% |
| stripe_0.00 | video:temporal_mean | 30.3% | 58.3% | 88.7% | 58.3% |
| stripe_0.00 | video:window_mean_best | 69.6% | 58.3% | 88.3% | 58.3% |
| stripe_0.10 | short | 84.9% | 47.2% | 86.0% | 47.2% |
| stripe_0.10 | video:max_proj | 34.2% | 16.7% | 41.2% | 16.7% |
| stripe_0.10 | video:single_best | 82.5% | 50.0% | 88.9% | 50.0% |
| stripe_0.10 | video:temporal_mean | 29.5% | 58.3% | 88.7% | 58.3% |
| stripe_0.10 | video:window_mean_best | 83.2% | 58.3% | 88.3% | 58.3% |
| stripe_0.18 | short | 84.6% | 47.2% | 86.0% | 47.2% |
| stripe_0.18 | video:max_proj | 38.4% | 16.7% | 41.2% | 16.7% |
| stripe_0.18 | video:single_best | 84.3% | 50.0% | 88.9% | 50.0% |
| stripe_0.18 | video:temporal_mean | 66.1% | 58.3% | 88.7% | 58.3% |
| stripe_0.18 | video:window_mean_best | 84.8% | 58.3% | 88.3% | 58.3% |
| stripe_0.30 | short | 83.2% | 47.2% | 86.0% | 47.2% |
| stripe_0.30 | video:max_proj | 21.8% | 16.7% | 41.2% | 16.7% |
| stripe_0.30 | video:single_best | 85.3% | 50.0% | 88.9% | 50.0% |
| stripe_0.30 | video:temporal_mean | 37.6% | 58.3% | 88.7% | 58.3% |
| stripe_0.30 | video:window_mean_best | 81.0% | 58.3% | 88.3% | 58.3% |
| vlm | long | 78.4% | 55.6% | 80.9% | 55.6% |
| vlm | short | 83.0% | 47.2% | 86.0% | 47.2% |
| vlm | video:max_proj | 35.5% | 16.7% | 41.2% | 16.7% |
| vlm | video:single_best | 87.1% | 50.0% | 88.9% | 50.0% |
| vlm | video:temporal_mean | 84.4% | 58.3% | 88.7% | 58.3% |
| vlm | video:window_mean_best | 84.4% | 58.3% | 88.3% | 58.3% |
