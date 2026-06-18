# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 1175

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 36 | 41.2% | 2.8% | 66.9% | 61.1% |
| anti_ocr|short | 36 | 1.3% | 0.0% | 0.2% | 0.0% |
| anti_ocr|video|max_proj | 12 | 54.4% | 8.3% | 60.6% | 66.7% |
| anti_ocr|video|single_best | 12 | 5.0% | 0.0% | 9.6% | 8.3% |
| anti_ocr|video|temporal_mean | 12 | 78.7% | 16.7% | 78.9% | 91.7% |
| anti_ocr|video|window_mean_best | 12 | 21.5% | 8.3% | 18.5% | 25.0% |
| deployed|long | 36 | 22.1% | 0.0% | 33.0% | 30.6% |
| deployed|short | 51 | 2.0% | 0.0% | 0.4% | 2.0% |
| deployed|video|max_proj | 17 | 14.2% | 0.0% | 19.2% | 17.6% |
| deployed|video|single_best | 17 | 4.0% | 0.0% | 0.8% | 5.9% |
| deployed|video|temporal_mean | 17 | 37.3% | 11.8% | 53.4% | 52.9% |
| deployed|video|window_mean_best | 17 | 10.3% | 0.0% | 9.2% | 11.8% |
| glyph_0.00|short | 15 | 3.2% | 0.0% | 0.6% | 0.0% |
| glyph_0.00|video|max_proj | 5 | 21.1% | 0.0% | 48.8% | 20.0% |
| glyph_0.00|video|single_best | 5 | 8.7% | 0.0% | 1.2% | 0.0% |
| glyph_0.00|video|temporal_mean | 5 | 59.1% | 0.0% | 83.5% | 100.0% |
| glyph_0.00|video|window_mean_best | 5 | 7.8% | 0.0% | 0.9% | 20.0% |
| glyph_0.12|short | 15 | 3.4% | 0.0% | 0.5% | 0.0% |
| glyph_0.12|video|max_proj | 5 | 13.6% | 0.0% | 22.6% | 0.0% |
| glyph_0.12|video|single_best | 5 | 7.8% | 0.0% | 1.4% | 20.0% |
| glyph_0.12|video|temporal_mean | 5 | 55.8% | 20.0% | 57.3% | 80.0% |
| glyph_0.12|video|window_mean_best | 5 | 5.1% | 0.0% | 1.7% | 20.0% |
| glyph_0.22|short | 15 | 1.9% | 0.0% | 0.5% | 0.0% |
| glyph_0.22|video|max_proj | 5 | 17.4% | 0.0% | 43.6% | 40.0% |
| glyph_0.22|video|single_best | 5 | 4.5% | 0.0% | 0.9% | 20.0% |
| glyph_0.22|video|temporal_mean | 5 | 57.8% | 0.0% | 55.7% | 80.0% |
| glyph_0.22|video|window_mean_best | 5 | 3.2% | 0.0% | 0.7% | 0.0% |
| inversion_0.0|long | 15 | 61.5% | 20.0% | 69.5% | 93.3% |
| inversion_0.0|video|max_proj | 5 | 21.6% | 0.0% | 28.1% | 20.0% |
| inversion_0.0|video|single_best | 5 | 4.6% | 0.0% | 1.2% | 20.0% |
| inversion_0.0|video|temporal_mean | 5 | 77.4% | 20.0% | 80.8% | 100.0% |
| inversion_0.0|video|window_mean_best | 5 | 7.5% | 0.0% | 1.4% | 0.0% |
| inversion_0.2|long | 15 | 20.4% | 0.0% | 53.4% | 33.3% |
| inversion_0.2|video|max_proj | 5 | 34.4% | 0.0% | 27.6% | 40.0% |
| inversion_0.2|video|single_best | 5 | 3.3% | 0.0% | 1.7% | 0.0% |
| inversion_0.2|video|temporal_mean | 5 | 74.1% | 0.0% | 81.6% | 100.0% |
| inversion_0.2|video|window_mean_best | 5 | 9.9% | 0.0% | 1.7% | 20.0% |
| inversion_0.3|long | 15 | 36.7% | 0.0% | 39.4% | 53.3% |
| inversion_0.3|video|max_proj | 5 | 14.4% | 0.0% | 2.4% | 20.0% |
| inversion_0.3|video|single_best | 5 | 4.8% | 0.0% | 1.4% | 20.0% |
| inversion_0.3|video|temporal_mean | 5 | 37.7% | 0.0% | 57.5% | 60.0% |
| inversion_0.3|video|window_mean_best | 5 | 5.3% | 0.0% | 1.7% | 0.0% |
| inversion_0.5|long | 15 | 9.8% | 0.0% | 6.8% | 20.0% |
| inversion_0.5|video|max_proj | 5 | 2.0% | 0.0% | 1.2% | 0.0% |
| inversion_0.5|video|single_best | 5 | 22.0% | 20.0% | 1.9% | 40.0% |
| inversion_0.5|video|temporal_mean | 5 | 55.9% | 0.0% | 69.4% | 80.0% |
| inversion_0.5|video|window_mean_best | 5 | 5.0% | 0.0% | 0.0% | 0.0% |
| inversion_1.0|long | 15 | 9.6% | 0.0% | 2.4% | 13.3% |
| inversion_1.0|video|max_proj | 5 | 19.2% | 0.0% | 25.2% | 20.0% |
| inversion_1.0|video|single_best | 5 | 3.7% | 0.0% | 0.9% | 0.0% |
| inversion_1.0|video|temporal_mean | 5 | 0.6% | 0.0% | 0.7% | 0.0% |
| inversion_1.0|video|window_mean_best | 5 | 2.7% | 0.0% | 0.9% | 0.0% |
| mask_noise|long | 36 | 49.1% | 8.3% | 73.2% | 66.7% |
| mask_noise|short | 36 | 2.3% | 0.0% | 0.7% | 0.0% |
| mask_noise|video|max_proj | 12 | 39.9% | 0.0% | 43.2% | 41.7% |
| mask_noise|video|single_best | 12 | 3.5% | 0.0% | 1.4% | 0.0% |
| mask_noise|video|temporal_mean | 12 | 82.8% | 16.7% | 86.3% | 100.0% |
| mask_noise|video|window_mean_best | 12 | 27.5% | 0.0% | 30.1% | 41.7% |
| mask_only|long | 36 | 41.8% | 8.3% | 67.6% | 55.6% |
| mask_only|short | 36 | 1.5% | 0.0% | 0.1% | 0.0% |
| mask_only|video|max_proj | 12 | 38.2% | 0.0% | 39.5% | 50.0% |
| mask_only|video|single_best | 12 | 5.3% | 0.0% | 0.3% | 8.3% |
| mask_only|video|temporal_mean | 12 | 82.2% | 16.7% | 87.6% | 100.0% |
| mask_only|video|window_mean_best | 12 | 27.4% | 0.0% | 27.1% | 41.7% |
| original|long | 36 | 77.8% | 52.8% | 69.3% | 88.9% |
| original|short | 36 | 87.6% | 50.0% | 79.4% | 100.0% |
| original|video|max_proj | 12 | 45.8% | 8.3% | 21.5% | 58.3% |
| original|video|single_best | 12 | 88.1% | 58.3% | 79.3% | 100.0% |
| original|video|temporal_mean | 12 | 90.8% | 66.7% | 88.6% | 100.0% |
| original|video|window_mean_best | 12 | 88.7% | 58.3% | 88.7% | 100.0% |
| stripe_0.00|short | 15 | 1.8% | 0.0% | 0.3% | 0.0% |
| stripe_0.00|video|max_proj | 5 | 36.5% | 0.0% | 22.6% | 40.0% |
| stripe_0.00|video|single_best | 5 | 8.9% | 0.0% | 15.5% | 40.0% |
| stripe_0.00|video|temporal_mean | 5 | 74.3% | 0.0% | 82.3% | 100.0% |
| stripe_0.00|video|window_mean_best | 5 | 4.5% | 0.0% | 1.7% | 20.0% |
| stripe_0.10|short | 15 | 2.0% | 0.0% | 1.6% | 0.0% |
| stripe_0.10|video|max_proj | 5 | 10.0% | 0.0% | 22.1% | 20.0% |
| stripe_0.10|video|single_best | 5 | 6.0% | 0.0% | 1.2% | 0.0% |
| stripe_0.10|video|temporal_mean | 5 | 64.3% | 20.0% | 66.6% | 100.0% |
| stripe_0.10|video|window_mean_best | 5 | 4.3% | 0.0% | 0.9% | 20.0% |
| stripe_0.18|short | 15 | 3.3% | 0.0% | 0.6% | 0.0% |
| stripe_0.18|video|max_proj | 5 | 4.6% | 0.0% | 22.1% | 0.0% |
| stripe_0.18|video|single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.18|video|temporal_mean | 5 | 34.2% | 20.0% | 45.7% | 60.0% |
| stripe_0.18|video|window_mean_best | 5 | 2.8% | 0.0% | 0.0% | 0.0% |
| stripe_0.30|short | 15 | 1.1% | 0.0% | 0.2% | 0.0% |
| stripe_0.30|video|max_proj | 5 | 5.7% | 0.0% | 1.2% | 0.0% |
| stripe_0.30|video|single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.30|video|temporal_mean | 5 | 63.0% | 0.0% | 41.6% | 100.0% |
| stripe_0.30|video|window_mean_best | 5 | 4.1% | 0.0% | 1.2% | 0.0% |
| vlm|long | 36 | 1.3% | 0.0% | 0.2% | 0.0% |
| vlm|short | 36 | 3.3% | 0.0% | 0.6% | 2.8% |
| vlm|video|max_proj | 12 | 4.2% | 0.0% | 7.7% | 8.3% |
| vlm|video|single_best | 12 | 1.9% | 0.0% | 2.0% | 8.3% |
| vlm|video|temporal_mean | 12 | 0.4% | 0.0% | 6.0% | 0.0% |
| vlm|video|window_mean_best | 12 | 0.9% | 0.0% | 0.3% | 0.0% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 41.2% | 2.8% | 66.9% | 61.1% |
| anti_ocr | short | 36 | 1.3% | 0.0% | 0.2% | 0.0% |
| anti_ocr | video:max_proj | 12 | 54.4% | 8.3% | 60.6% | 66.7% |
| anti_ocr | video:single_best | 12 | 5.0% | 0.0% | 9.6% | 8.3% |
| anti_ocr | video:temporal_mean | 12 | 78.7% | 16.7% | 78.9% | 91.7% |
| anti_ocr | video:window_mean_best | 12 | 21.5% | 8.3% | 18.5% | 25.0% |
| deployed | long | 36 | 22.1% | 0.0% | 33.0% | 30.6% |
| deployed | short | 51 | 2.0% | 0.0% | 0.4% | 2.0% |
| deployed | video:max_proj | 17 | 14.2% | 0.0% | 19.2% | 17.6% |
| deployed | video:single_best | 17 | 4.0% | 0.0% | 0.8% | 5.9% |
| deployed | video:temporal_mean | 17 | 37.3% | 11.8% | 53.4% | 52.9% |
| deployed | video:window_mean_best | 17 | 10.3% | 0.0% | 9.2% | 11.8% |
| glyph_0.00 | short | 15 | 3.2% | 0.0% | 0.6% | 0.0% |
| glyph_0.00 | video:max_proj | 5 | 21.1% | 0.0% | 48.8% | 20.0% |
| glyph_0.00 | video:single_best | 5 | 8.7% | 0.0% | 1.2% | 0.0% |
| glyph_0.00 | video:temporal_mean | 5 | 59.1% | 0.0% | 83.5% | 100.0% |
| glyph_0.00 | video:window_mean_best | 5 | 7.8% | 0.0% | 0.9% | 20.0% |
| glyph_0.12 | short | 15 | 3.4% | 0.0% | 0.5% | 0.0% |
| glyph_0.12 | video:max_proj | 5 | 13.6% | 0.0% | 22.6% | 0.0% |
| glyph_0.12 | video:single_best | 5 | 7.8% | 0.0% | 1.4% | 20.0% |
| glyph_0.12 | video:temporal_mean | 5 | 55.8% | 20.0% | 57.3% | 80.0% |
| glyph_0.12 | video:window_mean_best | 5 | 5.1% | 0.0% | 1.7% | 20.0% |
| glyph_0.22 | short | 15 | 1.9% | 0.0% | 0.5% | 0.0% |
| glyph_0.22 | video:max_proj | 5 | 17.4% | 0.0% | 43.6% | 40.0% |
| glyph_0.22 | video:single_best | 5 | 4.5% | 0.0% | 0.9% | 20.0% |
| glyph_0.22 | video:temporal_mean | 5 | 57.8% | 0.0% | 55.7% | 80.0% |
| glyph_0.22 | video:window_mean_best | 5 | 3.2% | 0.0% | 0.7% | 0.0% |
| inversion_0.0 | long | 15 | 61.5% | 20.0% | 69.5% | 93.3% |
| inversion_0.0 | video:max_proj | 5 | 21.6% | 0.0% | 28.1% | 20.0% |
| inversion_0.0 | video:single_best | 5 | 4.6% | 0.0% | 1.2% | 20.0% |
| inversion_0.0 | video:temporal_mean | 5 | 77.4% | 20.0% | 80.8% | 100.0% |
| inversion_0.0 | video:window_mean_best | 5 | 7.5% | 0.0% | 1.4% | 0.0% |
| inversion_0.2 | long | 15 | 20.4% | 0.0% | 53.4% | 33.3% |
| inversion_0.2 | video:max_proj | 5 | 34.4% | 0.0% | 27.6% | 40.0% |
| inversion_0.2 | video:single_best | 5 | 3.3% | 0.0% | 1.7% | 0.0% |
| inversion_0.2 | video:temporal_mean | 5 | 74.1% | 0.0% | 81.6% | 100.0% |
| inversion_0.2 | video:window_mean_best | 5 | 9.9% | 0.0% | 1.7% | 20.0% |
| inversion_0.3 | long | 15 | 36.7% | 0.0% | 39.4% | 53.3% |
| inversion_0.3 | video:max_proj | 5 | 14.4% | 0.0% | 2.4% | 20.0% |
| inversion_0.3 | video:single_best | 5 | 4.8% | 0.0% | 1.4% | 20.0% |
| inversion_0.3 | video:temporal_mean | 5 | 37.7% | 0.0% | 57.5% | 60.0% |
| inversion_0.3 | video:window_mean_best | 5 | 5.3% | 0.0% | 1.7% | 0.0% |
| inversion_0.5 | long | 15 | 9.8% | 0.0% | 6.8% | 20.0% |
| inversion_0.5 | video:max_proj | 5 | 2.0% | 0.0% | 1.2% | 0.0% |
| inversion_0.5 | video:single_best | 5 | 22.0% | 20.0% | 1.9% | 40.0% |
| inversion_0.5 | video:temporal_mean | 5 | 55.9% | 0.0% | 69.4% | 80.0% |
| inversion_0.5 | video:window_mean_best | 5 | 5.0% | 0.0% | 0.0% | 0.0% |
| inversion_1.0 | long | 15 | 9.6% | 0.0% | 2.4% | 13.3% |
| inversion_1.0 | video:max_proj | 5 | 19.2% | 0.0% | 25.2% | 20.0% |
| inversion_1.0 | video:single_best | 5 | 3.7% | 0.0% | 0.9% | 0.0% |
| inversion_1.0 | video:temporal_mean | 5 | 0.6% | 0.0% | 0.7% | 0.0% |
| inversion_1.0 | video:window_mean_best | 5 | 2.7% | 0.0% | 0.9% | 0.0% |
| mask_noise | long | 36 | 49.1% | 8.3% | 73.2% | 66.7% |
| mask_noise | short | 36 | 2.3% | 0.0% | 0.7% | 0.0% |
| mask_noise | video:max_proj | 12 | 39.9% | 0.0% | 43.2% | 41.7% |
| mask_noise | video:single_best | 12 | 3.5% | 0.0% | 1.4% | 0.0% |
| mask_noise | video:temporal_mean | 12 | 82.8% | 16.7% | 86.3% | 100.0% |
| mask_noise | video:window_mean_best | 12 | 27.5% | 0.0% | 30.1% | 41.7% |
| mask_only | long | 36 | 41.8% | 8.3% | 67.6% | 55.6% |
| mask_only | short | 36 | 1.5% | 0.0% | 0.1% | 0.0% |
| mask_only | video:max_proj | 12 | 38.2% | 0.0% | 39.5% | 50.0% |
| mask_only | video:single_best | 12 | 5.3% | 0.0% | 0.3% | 8.3% |
| mask_only | video:temporal_mean | 12 | 82.2% | 16.7% | 87.6% | 100.0% |
| mask_only | video:window_mean_best | 12 | 27.4% | 0.0% | 27.1% | 41.7% |
| original | long | 36 | 77.8% | 52.8% | 69.3% | 88.9% |
| original | short | 36 | 87.6% | 50.0% | 79.4% | 100.0% |
| original | video:max_proj | 12 | 45.8% | 8.3% | 21.5% | 58.3% |
| original | video:single_best | 12 | 88.1% | 58.3% | 79.3% | 100.0% |
| original | video:temporal_mean | 12 | 90.8% | 66.7% | 88.6% | 100.0% |
| original | video:window_mean_best | 12 | 88.7% | 58.3% | 88.7% | 100.0% |
| stripe_0.00 | short | 15 | 1.8% | 0.0% | 0.3% | 0.0% |
| stripe_0.00 | video:max_proj | 5 | 36.5% | 0.0% | 22.6% | 40.0% |
| stripe_0.00 | video:single_best | 5 | 8.9% | 0.0% | 15.5% | 40.0% |
| stripe_0.00 | video:temporal_mean | 5 | 74.3% | 0.0% | 82.3% | 100.0% |
| stripe_0.00 | video:window_mean_best | 5 | 4.5% | 0.0% | 1.7% | 20.0% |
| stripe_0.10 | short | 15 | 2.0% | 0.0% | 1.6% | 0.0% |
| stripe_0.10 | video:max_proj | 5 | 10.0% | 0.0% | 22.1% | 20.0% |
| stripe_0.10 | video:single_best | 5 | 6.0% | 0.0% | 1.2% | 0.0% |
| stripe_0.10 | video:temporal_mean | 5 | 64.3% | 20.0% | 66.6% | 100.0% |
| stripe_0.10 | video:window_mean_best | 5 | 4.3% | 0.0% | 0.9% | 20.0% |
| stripe_0.18 | short | 15 | 3.3% | 0.0% | 0.6% | 0.0% |
| stripe_0.18 | video:max_proj | 5 | 4.6% | 0.0% | 22.1% | 0.0% |
| stripe_0.18 | video:single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.18 | video:temporal_mean | 5 | 34.2% | 20.0% | 45.7% | 60.0% |
| stripe_0.18 | video:window_mean_best | 5 | 2.8% | 0.0% | 0.0% | 0.0% |
| stripe_0.30 | short | 15 | 1.1% | 0.0% | 0.2% | 0.0% |
| stripe_0.30 | video:max_proj | 5 | 5.7% | 0.0% | 1.2% | 0.0% |
| stripe_0.30 | video:single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.30 | video:temporal_mean | 5 | 63.0% | 0.0% | 41.6% | 100.0% |
| stripe_0.30 | video:window_mean_best | 5 | 4.1% | 0.0% | 1.2% | 0.0% |
| vlm | long | 36 | 1.3% | 0.0% | 0.2% | 0.0% |
| vlm | short | 36 | 3.3% | 0.0% | 0.6% | 2.8% |
| vlm | video:max_proj | 12 | 4.2% | 0.0% | 7.7% | 8.3% |
| vlm | video:single_best | 12 | 1.9% | 0.0% | 2.0% | 8.3% |
| vlm | video:temporal_mean | 12 | 0.4% | 0.0% | 6.0% | 0.0% |
| vlm | video:window_mean_best | 12 | 0.9% | 0.0% | 0.3% | 0.0% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | 36.5% | 50.0% | 77.8% | 52.8% |
| anti_ocr | short | 86.3% | 50.0% | 87.6% | 50.0% |
| anti_ocr | video:max_proj | -8.7% | 0.0% | 45.8% | 8.3% |
| anti_ocr | video:single_best | 83.1% | 58.3% | 88.1% | 58.3% |
| anti_ocr | video:temporal_mean | 12.1% | 50.0% | 90.8% | 66.7% |
| anti_ocr | video:window_mean_best | 67.2% | 50.0% | 88.7% | 58.3% |
| deployed | long | 55.7% | 52.8% | 77.8% | 52.8% |
| deployed | short | 85.6% | 50.0% | 87.6% | 50.0% |
| deployed | video:max_proj | 31.6% | 8.3% | 45.8% | 8.3% |
| deployed | video:single_best | 84.1% | 58.3% | 88.1% | 58.3% |
| deployed | video:temporal_mean | 53.5% | 54.9% | 90.8% | 66.7% |
| deployed | video:window_mean_best | 78.4% | 58.3% | 88.7% | 58.3% |
| glyph_0.00 | short | 84.4% | 50.0% | 87.6% | 50.0% |
| glyph_0.00 | video:max_proj | 24.6% | 8.3% | 45.8% | 8.3% |
| glyph_0.00 | video:single_best | 79.4% | 58.3% | 88.1% | 58.3% |
| glyph_0.00 | video:temporal_mean | 31.7% | 66.7% | 90.8% | 66.7% |
| glyph_0.00 | video:window_mean_best | 81.0% | 58.3% | 88.7% | 58.3% |
| glyph_0.12 | short | 84.2% | 50.0% | 87.6% | 50.0% |
| glyph_0.12 | video:max_proj | 32.1% | 8.3% | 45.8% | 8.3% |
| glyph_0.12 | video:single_best | 80.3% | 58.3% | 88.1% | 58.3% |
| glyph_0.12 | video:temporal_mean | 35.0% | 46.7% | 90.8% | 66.7% |
| glyph_0.12 | video:window_mean_best | 83.7% | 58.3% | 88.7% | 58.3% |
| glyph_0.22 | short | 85.6% | 50.0% | 87.6% | 50.0% |
| glyph_0.22 | video:max_proj | 28.4% | 8.3% | 45.8% | 8.3% |
| glyph_0.22 | video:single_best | 83.6% | 58.3% | 88.1% | 58.3% |
| glyph_0.22 | video:temporal_mean | 33.1% | 66.7% | 90.8% | 66.7% |
| glyph_0.22 | video:window_mean_best | 85.5% | 58.3% | 88.7% | 58.3% |
| inversion_0.0 | long | 16.3% | 32.8% | 77.8% | 52.8% |
| inversion_0.0 | video:max_proj | 24.2% | 8.3% | 45.8% | 8.3% |
| inversion_0.0 | video:single_best | 83.5% | 58.3% | 88.1% | 58.3% |
| inversion_0.0 | video:temporal_mean | 13.4% | 46.7% | 90.8% | 66.7% |
| inversion_0.0 | video:window_mean_best | 81.2% | 58.3% | 88.7% | 58.3% |
| inversion_0.2 | long | 57.4% | 52.8% | 77.8% | 52.8% |
| inversion_0.2 | video:max_proj | 11.4% | 8.3% | 45.8% | 8.3% |
| inversion_0.2 | video:single_best | 84.8% | 58.3% | 88.1% | 58.3% |
| inversion_0.2 | video:temporal_mean | 16.7% | 66.7% | 90.8% | 66.7% |
| inversion_0.2 | video:window_mean_best | 78.9% | 58.3% | 88.7% | 58.3% |
| inversion_0.3 | long | 41.1% | 52.8% | 77.8% | 52.8% |
| inversion_0.3 | video:max_proj | 31.4% | 8.3% | 45.8% | 8.3% |
| inversion_0.3 | video:single_best | 83.3% | 58.3% | 88.1% | 58.3% |
| inversion_0.3 | video:temporal_mean | 53.1% | 66.7% | 90.8% | 66.7% |
| inversion_0.3 | video:window_mean_best | 83.4% | 58.3% | 88.7% | 58.3% |
| inversion_0.5 | long | 68.0% | 52.8% | 77.8% | 52.8% |
| inversion_0.5 | video:max_proj | 43.8% | 8.3% | 45.8% | 8.3% |
| inversion_0.5 | video:single_best | 66.1% | 38.3% | 88.1% | 58.3% |
| inversion_0.5 | video:temporal_mean | 34.9% | 66.7% | 90.8% | 66.7% |
| inversion_0.5 | video:window_mean_best | 83.7% | 58.3% | 88.7% | 58.3% |
| inversion_1.0 | long | 68.2% | 52.8% | 77.8% | 52.8% |
| inversion_1.0 | video:max_proj | 26.6% | 8.3% | 45.8% | 8.3% |
| inversion_1.0 | video:single_best | 84.4% | 58.3% | 88.1% | 58.3% |
| inversion_1.0 | video:temporal_mean | 90.3% | 66.7% | 90.8% | 66.7% |
| inversion_1.0 | video:window_mean_best | 86.1% | 58.3% | 88.7% | 58.3% |
| mask_noise | long | 28.7% | 44.4% | 77.8% | 52.8% |
| mask_noise | short | 85.2% | 50.0% | 87.6% | 50.0% |
| mask_noise | video:max_proj | 5.9% | 8.3% | 45.8% | 8.3% |
| mask_noise | video:single_best | 84.6% | 58.3% | 88.1% | 58.3% |
| mask_noise | video:temporal_mean | 8.0% | 50.0% | 90.8% | 66.7% |
| mask_noise | video:window_mean_best | 61.2% | 58.3% | 88.7% | 58.3% |
| mask_only | long | 36.0% | 44.4% | 77.8% | 52.8% |
| mask_only | short | 86.1% | 50.0% | 87.6% | 50.0% |
| mask_only | video:max_proj | 7.5% | 8.3% | 45.8% | 8.3% |
| mask_only | video:single_best | 82.8% | 58.3% | 88.1% | 58.3% |
| mask_only | video:temporal_mean | 8.6% | 50.0% | 90.8% | 66.7% |
| mask_only | video:window_mean_best | 61.4% | 58.3% | 88.7% | 58.3% |
| original | long | 0.0% | 0.0% | 77.8% | 52.8% |
| original | short | 0.0% | 0.0% | 87.6% | 50.0% |
| original | video:max_proj | 0.0% | 0.0% | 45.8% | 8.3% |
| original | video:single_best | 0.0% | 0.0% | 88.1% | 58.3% |
| original | video:temporal_mean | 0.0% | 0.0% | 90.8% | 66.7% |
| original | video:window_mean_best | 0.0% | 0.0% | 88.7% | 58.3% |
| stripe_0.00 | short | 85.8% | 50.0% | 87.6% | 50.0% |
| stripe_0.00 | video:max_proj | 9.3% | 8.3% | 45.8% | 8.3% |
| stripe_0.00 | video:single_best | 79.2% | 58.3% | 88.1% | 58.3% |
| stripe_0.00 | video:temporal_mean | 16.5% | 66.7% | 90.8% | 66.7% |
| stripe_0.00 | video:window_mean_best | 84.2% | 58.3% | 88.7% | 58.3% |
| stripe_0.10 | short | 85.6% | 50.0% | 87.6% | 50.0% |
| stripe_0.10 | video:max_proj | 35.7% | 8.3% | 45.8% | 8.3% |
| stripe_0.10 | video:single_best | 82.1% | 58.3% | 88.1% | 58.3% |
| stripe_0.10 | video:temporal_mean | 26.5% | 46.7% | 90.8% | 66.7% |
| stripe_0.10 | video:window_mean_best | 84.4% | 58.3% | 88.7% | 58.3% |
| stripe_0.18 | short | 84.2% | 50.0% | 87.6% | 50.0% |
| stripe_0.18 | video:max_proj | 41.2% | 8.3% | 45.8% | 8.3% |
| stripe_0.18 | video:single_best | 88.1% | 58.3% | 88.1% | 58.3% |
| stripe_0.18 | video:temporal_mean | 56.6% | 46.7% | 90.8% | 66.7% |
| stripe_0.18 | video:window_mean_best | 85.9% | 58.3% | 88.7% | 58.3% |
| stripe_0.30 | short | 86.5% | 50.0% | 87.6% | 50.0% |
| stripe_0.30 | video:max_proj | 40.1% | 8.3% | 45.8% | 8.3% |
| stripe_0.30 | video:single_best | 88.1% | 58.3% | 88.1% | 58.3% |
| stripe_0.30 | video:temporal_mean | 27.8% | 66.7% | 90.8% | 66.7% |
| stripe_0.30 | video:window_mean_best | 84.6% | 58.3% | 88.7% | 58.3% |
| vlm | long | 76.5% | 52.8% | 77.8% | 52.8% |
| vlm | short | 84.2% | 50.0% | 87.6% | 50.0% |
| vlm | video:max_proj | 41.5% | 8.3% | 45.8% | 8.3% |
| vlm | video:single_best | 86.2% | 58.3% | 88.1% | 58.3% |
| vlm | video:temporal_mean | 90.4% | 66.7% | 90.8% | 66.7% |
| vlm | video:window_mean_best | 87.8% | 58.3% | 88.7% | 58.3% |
