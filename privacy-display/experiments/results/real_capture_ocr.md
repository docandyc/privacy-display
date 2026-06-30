# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 10575
- OCR rows: 31725

## Position Matrix

| Position | Distance | Angle | Captures | OCR rows |
|---|---:|---:|---:|---:|
| d0.5_a0 | 0.5 m | 0 deg | 1175 | 3525 |
| d0.5_a15 | 0.5 m | 15 deg | 1175 | 3525 |
| d0.5_a30 | 0.5 m | 30 deg | 1175 | 3525 |
| d1_a0 | 1 m | 0 deg | 1175 | 3525 |
| d1_a15 | 1 m | 15 deg | 1175 | 3525 |
| d1_a30 | 1 m | 30 deg | 1175 | 3525 |
| d1.5_a0 | 1.5 m | 0 deg | 1175 | 3525 |
| d1.5_a15 | 1.5 m | 15 deg | 1175 | 3525 |
| d1.5_a30 | 1.5 m | 30 deg | 1175 | 3525 |

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 972 | 30.7% | 16.7% | 82.7% | 38.1% |
| anti_ocr|short | 972 | 7.8% | 0.2% | 11.9% | 13.0% |
| anti_ocr|video|max_proj | 324 | 41.5% | 9.9% | 50.0% | 51.2% |
| anti_ocr|video|single_best | 324 | 16.5% | 1.9% | 15.6% | 22.8% |
| anti_ocr|video|temporal_mean | 324 | 50.6% | 23.1% | 55.5% | 61.7% |
| anti_ocr|video|window_mean_best | 324 | 42.2% | 9.6% | 44.0% | 55.9% |
| deployed|long | 972 | 31.8% | 15.3% | 81.8% | 39.8% |
| deployed|short | 1377 | 5.7% | 0.1% | 8.7% | 8.2% |
| deployed|video|max_proj | 459 | 40.5% | 6.5% | 48.4% | 51.2% |
| deployed|video|single_best | 459 | 16.7% | 1.7% | 16.4% | 25.7% |
| deployed|video|temporal_mean | 459 | 42.6% | 19.6% | 52.9% | 55.8% |
| deployed|video|window_mean_best | 459 | 35.6% | 6.8% | 40.2% | 49.5% |
| glyph_0.00|short | 405 | 6.7% | 0.5% | 6.1% | 7.7% |
| glyph_0.00|video|max_proj | 135 | 36.6% | 4.4% | 37.5% | 51.1% |
| glyph_0.00|video|single_best | 135 | 12.6% | 0.7% | 9.9% | 19.3% |
| glyph_0.00|video|temporal_mean | 135 | 37.0% | 15.6% | 40.2% | 51.9% |
| glyph_0.00|video|window_mean_best | 135 | 28.1% | 4.4% | 27.3% | 40.7% |
| glyph_0.12|short | 405 | 5.6% | 0.0% | 5.9% | 6.7% |
| glyph_0.12|video|max_proj | 135 | 36.9% | 3.7% | 36.1% | 48.9% |
| glyph_0.12|video|single_best | 135 | 11.6% | 0.0% | 9.8% | 17.0% |
| glyph_0.12|video|temporal_mean | 135 | 36.6% | 12.6% | 37.7% | 51.9% |
| glyph_0.12|video|window_mean_best | 135 | 29.2% | 6.7% | 29.7% | 41.5% |
| glyph_0.22|short | 405 | 6.1% | 0.5% | 6.0% | 9.6% |
| glyph_0.22|video|max_proj | 135 | 35.5% | 3.0% | 35.1% | 47.4% |
| glyph_0.22|video|single_best | 135 | 13.0% | 0.0% | 8.9% | 18.5% |
| glyph_0.22|video|temporal_mean | 135 | 34.7% | 13.3% | 38.0% | 45.9% |
| glyph_0.22|video|window_mean_best | 135 | 33.5% | 7.4% | 29.8% | 50.4% |
| inversion_0.0|long | 405 | 31.2% | 9.1% | 62.0% | 41.2% |
| inversion_0.0|video|max_proj | 135 | 34.6% | 3.0% | 35.7% | 46.7% |
| inversion_0.0|video|single_best | 135 | 10.2% | 0.0% | 6.6% | 16.3% |
| inversion_0.0|video|temporal_mean | 135 | 43.7% | 18.5% | 43.6% | 60.0% |
| inversion_0.0|video|window_mean_best | 135 | 31.0% | 6.7% | 34.4% | 48.1% |
| inversion_0.2|long | 405 | 34.4% | 12.3% | 72.9% | 46.7% |
| inversion_0.2|video|max_proj | 135 | 35.8% | 3.7% | 38.8% | 49.6% |
| inversion_0.2|video|single_best | 135 | 12.4% | 2.2% | 10.3% | 18.5% |
| inversion_0.2|video|temporal_mean | 135 | 39.7% | 20.0% | 43.5% | 57.0% |
| inversion_0.2|video|window_mean_best | 135 | 30.5% | 4.4% | 32.6% | 44.4% |
| inversion_0.3|long | 405 | 37.8% | 14.1% | 73.3% | 49.9% |
| inversion_0.3|video|max_proj | 135 | 31.3% | 3.0% | 35.5% | 45.2% |
| inversion_0.3|video|single_best | 135 | 14.2% | 0.7% | 11.6% | 20.7% |
| inversion_0.3|video|temporal_mean | 135 | 36.4% | 11.1% | 43.3% | 54.8% |
| inversion_0.3|video|window_mean_best | 135 | 30.2% | 7.4% | 32.9% | 45.9% |
| inversion_0.5|long | 405 | 33.4% | 9.9% | 66.4% | 44.9% |
| inversion_0.5|video|max_proj | 135 | 28.3% | 1.5% | 36.3% | 40.7% |
| inversion_0.5|video|single_best | 135 | 12.5% | 1.5% | 9.4% | 20.7% |
| inversion_0.5|video|temporal_mean | 135 | 37.2% | 17.8% | 44.4% | 51.1% |
| inversion_0.5|video|window_mean_best | 135 | 31.8% | 7.4% | 32.2% | 48.1% |
| inversion_1.0|long | 405 | 9.9% | 1.5% | 28.8% | 16.5% |
| inversion_1.0|video|max_proj | 135 | 27.7% | 2.2% | 19.3% | 37.0% |
| inversion_1.0|video|single_best | 135 | 36.7% | 15.6% | 31.8% | 48.1% |
| inversion_1.0|video|temporal_mean | 135 | 10.6% | 0.0% | 14.3% | 18.5% |
| inversion_1.0|video|window_mean_best | 135 | 31.6% | 5.9% | 29.4% | 44.4% |
| mask_noise|long | 972 | 34.7% | 14.2% | 82.7% | 42.9% |
| mask_noise|short | 972 | 10.9% | 0.9% | 12.6% | 16.5% |
| mask_noise|video|max_proj | 324 | 44.3% | 11.7% | 50.3% | 54.9% |
| mask_noise|video|single_best | 324 | 16.4% | 1.5% | 13.6% | 25.3% |
| mask_noise|video|temporal_mean | 324 | 50.1% | 21.6% | 55.6% | 62.0% |
| mask_noise|video|window_mean_best | 324 | 43.5% | 12.3% | 48.1% | 56.8% |
| mask_only|long | 972 | 32.5% | 12.6% | 80.1% | 40.2% |
| mask_only|short | 972 | 7.1% | 0.1% | 10.1% | 12.0% |
| mask_only|video|max_proj | 324 | 41.3% | 11.1% | 46.5% | 51.5% |
| mask_only|video|single_best | 324 | 17.5% | 1.9% | 15.5% | 25.9% |
| mask_only|video|temporal_mean | 324 | 50.1% | 22.2% | 54.0% | 61.7% |
| mask_only|video|window_mean_best | 324 | 41.2% | 13.0% | 42.6% | 53.1% |
| original|long | 972 | 17.0% | 4.6% | 57.8% | 21.4% |
| original|short | 972 | 64.1% | 31.5% | 77.4% | 73.5% |
| original|video|max_proj | 324 | 35.3% | 9.0% | 39.6% | 48.5% |
| original|video|single_best | 324 | 65.1% | 34.3% | 65.6% | 74.4% |
| original|video|temporal_mean | 324 | 54.3% | 29.0% | 60.4% | 62.3% |
| original|video|window_mean_best | 324 | 64.4% | 34.3% | 66.1% | 73.1% |
| stripe_0.00|short | 405 | 4.7% | 0.5% | 5.2% | 5.4% |
| stripe_0.00|video|max_proj | 135 | 35.5% | 7.4% | 37.7% | 48.9% |
| stripe_0.00|video|single_best | 135 | 12.6% | 0.0% | 13.4% | 19.3% |
| stripe_0.00|video|temporal_mean | 135 | 38.5% | 19.3% | 41.3% | 54.1% |
| stripe_0.00|video|window_mean_best | 135 | 31.3% | 8.9% | 34.5% | 45.9% |
| stripe_0.10|short | 405 | 5.7% | 0.0% | 6.6% | 7.7% |
| stripe_0.10|video|max_proj | 135 | 34.3% | 3.7% | 36.9% | 45.9% |
| stripe_0.10|video|single_best | 135 | 13.1% | 0.0% | 10.3% | 20.0% |
| stripe_0.10|video|temporal_mean | 135 | 37.1% | 19.3% | 42.1% | 53.3% |
| stripe_0.10|video|window_mean_best | 135 | 27.6% | 4.4% | 29.0% | 42.2% |
| stripe_0.18|short | 405 | 4.7% | 0.0% | 4.4% | 5.2% |
| stripe_0.18|video|max_proj | 135 | 34.6% | 1.5% | 42.1% | 48.9% |
| stripe_0.18|video|single_best | 135 | 10.5% | 0.0% | 8.1% | 16.3% |
| stripe_0.18|video|temporal_mean | 135 | 36.7% | 17.0% | 42.5% | 49.6% |
| stripe_0.18|video|window_mean_best | 135 | 30.6% | 4.4% | 33.5% | 45.2% |
| stripe_0.30|short | 405 | 5.1% | 0.0% | 5.1% | 5.7% |
| stripe_0.30|video|max_proj | 135 | 35.3% | 3.7% | 36.2% | 48.1% |
| stripe_0.30|video|single_best | 135 | 11.9% | 0.7% | 6.9% | 19.3% |
| stripe_0.30|video|temporal_mean | 135 | 35.1% | 14.1% | 39.4% | 48.9% |
| stripe_0.30|video|window_mean_best | 135 | 28.3% | 3.0% | 29.0% | 41.5% |
| vlm|long | 972 | 4.3% | 0.0% | 11.5% | 6.1% |
| vlm|short | 972 | 1.6% | 0.0% | 1.7% | 1.1% |
| vlm|video|max_proj | 324 | 6.2% | 0.0% | 8.1% | 6.2% |
| vlm|video|single_best | 324 | 1.9% | 0.0% | 1.6% | 2.2% |
| vlm|video|temporal_mean | 324 | 17.7% | 1.5% | 13.3% | 28.7% |
| vlm|video|window_mean_best | 324 | 6.0% | 0.3% | 7.2% | 10.5% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 324 | 66.3% | 46.6% | 95.4% | 74.7% |
| anti_ocr | short | 324 | 19.9% | 0.6% | 33.2% | 32.7% |
| anti_ocr | video:max_proj | 108 | 63.2% | 21.3% | 68.1% | 74.1% |
| anti_ocr | video:single_best | 108 | 30.0% | 5.6% | 37.5% | 35.2% |
| anti_ocr | video:temporal_mean | 108 | 68.8% | 48.1% | 73.4% | 77.8% |
| anti_ocr | video:window_mean_best | 108 | 62.0% | 25.0% | 67.5% | 73.1% |
| deployed | long | 324 | 67.6% | 41.4% | 96.4% | 76.2% |
| deployed | short | 459 | 14.1% | 0.4% | 23.0% | 19.4% |
| deployed | video:max_proj | 153 | 61.3% | 17.6% | 64.7% | 72.5% |
| deployed | video:single_best | 153 | 29.7% | 5.2% | 38.9% | 39.9% |
| deployed | video:temporal_mean | 153 | 65.4% | 41.2% | 70.2% | 76.5% |
| deployed | video:window_mean_best | 153 | 54.2% | 17.0% | 63.8% | 69.3% |
| glyph_0.00 | short | 135 | 14.3% | 1.5% | 14.7% | 15.6% |
| glyph_0.00 | video:max_proj | 45 | 54.2% | 13.3% | 55.6% | 68.9% |
| glyph_0.00 | video:single_best | 45 | 23.8% | 2.2% | 22.3% | 31.1% |
| glyph_0.00 | video:temporal_mean | 45 | 58.6% | 33.3% | 63.4% | 77.8% |
| glyph_0.00 | video:window_mean_best | 45 | 48.1% | 13.3% | 53.2% | 62.2% |
| glyph_0.12 | short | 135 | 12.0% | 0.0% | 15.4% | 13.3% |
| glyph_0.12 | video:max_proj | 45 | 54.0% | 11.1% | 50.0% | 64.4% |
| glyph_0.12 | video:single_best | 45 | 22.3% | 0.0% | 23.8% | 26.7% |
| glyph_0.12 | video:temporal_mean | 45 | 55.3% | 31.1% | 58.6% | 68.9% |
| glyph_0.12 | video:window_mean_best | 45 | 49.4% | 17.8% | 55.3% | 62.2% |
| glyph_0.22 | short | 135 | 12.2% | 1.5% | 15.3% | 16.3% |
| glyph_0.22 | video:max_proj | 45 | 52.5% | 6.7% | 49.9% | 68.9% |
| glyph_0.22 | video:single_best | 45 | 23.0% | 0.0% | 21.3% | 31.1% |
| glyph_0.22 | video:temporal_mean | 45 | 57.2% | 31.1% | 57.1% | 68.9% |
| glyph_0.22 | video:window_mean_best | 45 | 50.1% | 20.0% | 50.2% | 68.9% |
| inversion_0.0 | long | 135 | 69.9% | 27.4% | 84.0% | 84.4% |
| inversion_0.0 | video:max_proj | 45 | 52.9% | 6.7% | 52.1% | 68.9% |
| inversion_0.0 | video:single_best | 45 | 19.7% | 0.0% | 16.4% | 33.3% |
| inversion_0.0 | video:temporal_mean | 45 | 63.6% | 42.2% | 62.9% | 77.8% |
| inversion_0.0 | video:window_mean_best | 45 | 50.0% | 20.0% | 57.5% | 73.3% |
| inversion_0.2 | long | 135 | 73.0% | 35.6% | 92.6% | 88.1% |
| inversion_0.2 | video:max_proj | 45 | 53.9% | 11.1% | 54.2% | 73.3% |
| inversion_0.2 | video:single_best | 45 | 22.7% | 6.7% | 24.4% | 31.1% |
| inversion_0.2 | video:temporal_mean | 45 | 61.0% | 48.9% | 64.6% | 77.8% |
| inversion_0.2 | video:window_mean_best | 45 | 49.0% | 13.3% | 57.9% | 71.1% |
| inversion_0.3 | long | 135 | 76.7% | 40.7% | 94.0% | 90.4% |
| inversion_0.3 | video:max_proj | 45 | 50.3% | 8.9% | 51.2% | 68.9% |
| inversion_0.3 | video:single_best | 45 | 25.7% | 2.2% | 26.9% | 28.9% |
| inversion_0.3 | video:temporal_mean | 45 | 59.5% | 28.9% | 63.8% | 77.8% |
| inversion_0.3 | video:window_mean_best | 45 | 49.9% | 22.2% | 55.6% | 66.7% |
| inversion_0.5 | long | 135 | 69.7% | 27.4% | 93.0% | 83.0% |
| inversion_0.5 | video:max_proj | 45 | 50.8% | 4.4% | 55.2% | 73.3% |
| inversion_0.5 | video:single_best | 45 | 21.5% | 4.4% | 23.6% | 26.7% |
| inversion_0.5 | video:temporal_mean | 45 | 60.0% | 40.0% | 64.0% | 77.8% |
| inversion_0.5 | video:window_mean_best | 45 | 49.8% | 20.0% | 58.4% | 68.9% |
| inversion_1.0 | long | 135 | 24.2% | 4.4% | 62.8% | 40.7% |
| inversion_1.0 | video:max_proj | 45 | 49.7% | 6.7% | 36.5% | 60.0% |
| inversion_1.0 | video:single_best | 45 | 47.8% | 33.3% | 41.7% | 57.8% |
| inversion_1.0 | video:temporal_mean | 45 | 27.5% | 0.0% | 37.8% | 51.1% |
| inversion_1.0 | video:window_mean_best | 45 | 48.0% | 17.8% | 48.0% | 64.4% |
| mask_noise | long | 324 | 71.7% | 41.0% | 94.9% | 78.7% |
| mask_noise | short | 324 | 24.7% | 2.8% | 33.5% | 36.1% |
| mask_noise | video:max_proj | 108 | 64.9% | 26.9% | 70.4% | 75.0% |
| mask_noise | video:single_best | 108 | 32.7% | 4.6% | 35.0% | 47.2% |
| mask_noise | video:temporal_mean | 108 | 69.6% | 45.4% | 73.6% | 77.8% |
| mask_noise | video:window_mean_best | 108 | 63.0% | 29.6% | 68.6% | 75.0% |
| mask_only | long | 324 | 70.8% | 36.7% | 93.9% | 77.5% |
| mask_only | short | 324 | 17.5% | 0.3% | 28.7% | 28.7% |
| mask_only | video:max_proj | 108 | 62.9% | 25.0% | 67.9% | 73.1% |
| mask_only | video:single_best | 108 | 32.8% | 5.6% | 37.9% | 42.6% |
| mask_only | video:temporal_mean | 108 | 69.3% | 44.4% | 73.7% | 76.9% |
| mask_only | video:window_mean_best | 108 | 59.5% | 27.8% | 65.8% | 69.4% |
| original | long | 324 | 44.2% | 13.9% | 90.7% | 54.6% |
| original | short | 324 | 92.5% | 66.0% | 96.5% | 97.5% |
| original | video:max_proj | 108 | 64.4% | 21.3% | 71.8% | 81.5% |
| original | video:single_best | 108 | 83.3% | 62.0% | 83.9% | 91.7% |
| original | video:temporal_mean | 108 | 72.1% | 53.7% | 77.0% | 78.7% |
| original | video:window_mean_best | 108 | 83.0% | 63.0% | 82.7% | 91.7% |
| stripe_0.00 | short | 135 | 9.9% | 1.5% | 11.9% | 10.4% |
| stripe_0.00 | video:max_proj | 45 | 55.6% | 20.0% | 58.7% | 71.1% |
| stripe_0.00 | video:single_best | 45 | 23.9% | 0.0% | 31.1% | 35.6% |
| stripe_0.00 | video:temporal_mean | 45 | 60.4% | 44.4% | 63.7% | 75.6% |
| stripe_0.00 | video:window_mean_best | 45 | 49.8% | 22.2% | 58.3% | 71.1% |
| stripe_0.10 | short | 135 | 13.7% | 0.0% | 17.7% | 17.8% |
| stripe_0.10 | video:max_proj | 45 | 56.3% | 11.1% | 57.7% | 68.9% |
| stripe_0.10 | video:single_best | 45 | 25.2% | 0.0% | 24.6% | 33.3% |
| stripe_0.10 | video:temporal_mean | 45 | 57.1% | 40.0% | 64.2% | 73.3% |
| stripe_0.10 | video:window_mean_best | 45 | 45.7% | 13.3% | 58.3% | 60.0% |
| stripe_0.18 | short | 135 | 10.1% | 0.0% | 11.7% | 9.6% |
| stripe_0.18 | video:max_proj | 45 | 52.9% | 4.4% | 58.9% | 68.9% |
| stripe_0.18 | video:single_best | 45 | 22.5% | 0.0% | 23.7% | 31.1% |
| stripe_0.18 | video:temporal_mean | 45 | 54.8% | 37.8% | 61.1% | 68.9% |
| stripe_0.18 | video:window_mean_best | 45 | 48.0% | 11.1% | 54.7% | 68.9% |
| stripe_0.30 | short | 135 | 11.2% | 0.0% | 12.7% | 10.4% |
| stripe_0.30 | video:max_proj | 45 | 53.9% | 8.9% | 52.9% | 66.7% |
| stripe_0.30 | video:single_best | 45 | 22.6% | 2.2% | 17.5% | 28.9% |
| stripe_0.30 | video:temporal_mean | 45 | 56.6% | 33.3% | 60.4% | 71.1% |
| stripe_0.30 | video:window_mean_best | 45 | 46.6% | 8.9% | 52.2% | 66.7% |
| vlm | long | 324 | 11.1% | 0.0% | 30.6% | 17.6% |
| vlm | short | 324 | 4.2% | 0.0% | 5.1% | 3.4% |
| vlm | video:max_proj | 108 | 13.9% | 0.0% | 24.1% | 17.6% |
| vlm | video:single_best | 108 | 4.9% | 0.0% | 4.8% | 6.5% |
| vlm | video:temporal_mean | 108 | 42.3% | 4.6% | 39.1% | 66.7% |
| vlm | video:window_mean_best | 108 | 15.5% | 0.9% | 20.7% | 28.7% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | -22.1% | -32.7% | 44.2% | 13.9% |
| anti_ocr | short | 72.6% | 65.4% | 92.5% | 66.0% |
| anti_ocr | video:max_proj | 1.2% | 0.0% | 64.4% | 21.3% |
| anti_ocr | video:single_best | 53.4% | 56.5% | 83.3% | 62.0% |
| anti_ocr | video:temporal_mean | 3.3% | 5.6% | 72.1% | 53.7% |
| anti_ocr | video:window_mean_best | 21.0% | 38.0% | 83.0% | 63.0% |
| deployed | long | -23.3% | -27.5% | 44.2% | 13.9% |
| deployed | short | 78.5% | 65.6% | 92.5% | 66.0% |
| deployed | video:max_proj | 3.1% | 3.6% | 64.4% | 21.3% |
| deployed | video:single_best | 53.6% | 56.8% | 83.3% | 62.0% |
| deployed | video:temporal_mean | 6.7% | 12.5% | 72.1% | 53.7% |
| deployed | video:window_mean_best | 28.8% | 46.0% | 83.0% | 63.0% |
| glyph_0.00 | short | 78.2% | 64.6% | 92.5% | 66.0% |
| glyph_0.00 | video:max_proj | 10.3% | 8.0% | 64.4% | 21.3% |
| glyph_0.00 | video:single_best | 59.5% | 59.8% | 83.3% | 62.0% |
| glyph_0.00 | video:temporal_mean | 13.6% | 20.4% | 72.1% | 53.7% |
| glyph_0.00 | video:window_mean_best | 34.9% | 49.6% | 83.0% | 63.0% |
| glyph_0.12 | short | 80.5% | 66.0% | 92.5% | 66.0% |
| glyph_0.12 | video:max_proj | 10.4% | 10.2% | 64.4% | 21.3% |
| glyph_0.12 | video:single_best | 61.0% | 62.0% | 83.3% | 62.0% |
| glyph_0.12 | video:temporal_mean | 16.8% | 22.6% | 72.1% | 53.7% |
| glyph_0.12 | video:window_mean_best | 33.7% | 45.2% | 83.0% | 63.0% |
| glyph_0.22 | short | 80.4% | 64.6% | 92.5% | 66.0% |
| glyph_0.22 | video:max_proj | 11.9% | 14.6% | 64.4% | 21.3% |
| glyph_0.22 | video:single_best | 60.3% | 62.0% | 83.3% | 62.0% |
| glyph_0.22 | video:temporal_mean | 15.0% | 22.6% | 72.1% | 53.7% |
| glyph_0.22 | video:window_mean_best | 32.9% | 43.0% | 83.0% | 63.0% |
| inversion_0.0 | long | -25.7% | -13.5% | 44.2% | 13.9% |
| inversion_0.0 | video:max_proj | 11.6% | 14.6% | 64.4% | 21.3% |
| inversion_0.0 | video:single_best | 63.6% | 62.0% | 83.3% | 62.0% |
| inversion_0.0 | video:temporal_mean | 8.5% | 11.5% | 72.1% | 53.7% |
| inversion_0.0 | video:window_mean_best | 33.0% | 43.0% | 83.0% | 63.0% |
| inversion_0.2 | long | -28.7% | -21.7% | 44.2% | 13.9% |
| inversion_0.2 | video:max_proj | 10.5% | 10.2% | 64.4% | 21.3% |
| inversion_0.2 | video:single_best | 60.7% | 55.4% | 83.3% | 62.0% |
| inversion_0.2 | video:temporal_mean | 11.1% | 4.8% | 72.1% | 53.7% |
| inversion_0.2 | video:window_mean_best | 34.0% | 49.6% | 83.0% | 63.0% |
| inversion_0.3 | long | -32.4% | -26.9% | 44.2% | 13.9% |
| inversion_0.3 | video:max_proj | 14.2% | 12.4% | 64.4% | 21.3% |
| inversion_0.3 | video:single_best | 57.6% | 59.8% | 83.3% | 62.0% |
| inversion_0.3 | video:temporal_mean | 12.7% | 24.8% | 72.1% | 53.7% |
| inversion_0.3 | video:window_mean_best | 33.1% | 40.7% | 83.0% | 63.0% |
| inversion_0.5 | long | -25.5% | -13.5% | 44.2% | 13.9% |
| inversion_0.5 | video:max_proj | 13.7% | 16.9% | 64.4% | 21.3% |
| inversion_0.5 | video:single_best | 61.9% | 57.6% | 83.3% | 62.0% |
| inversion_0.5 | video:temporal_mean | 12.1% | 13.7% | 72.1% | 53.7% |
| inversion_0.5 | video:window_mean_best | 33.2% | 43.0% | 83.0% | 63.0% |
| inversion_1.0 | long | 20.1% | 9.4% | 44.2% | 13.9% |
| inversion_1.0 | video:max_proj | 14.7% | 14.6% | 64.4% | 21.3% |
| inversion_1.0 | video:single_best | 35.5% | 28.7% | 83.3% | 62.0% |
| inversion_1.0 | video:temporal_mean | 44.6% | 53.7% | 72.1% | 53.7% |
| inversion_1.0 | video:window_mean_best | 35.0% | 45.2% | 83.0% | 63.0% |
| mask_noise | long | -27.5% | -27.2% | 44.2% | 13.9% |
| mask_noise | short | 67.9% | 63.3% | 92.5% | 66.0% |
| mask_noise | video:max_proj | -0.5% | -5.6% | 64.4% | 21.3% |
| mask_noise | video:single_best | 50.6% | 57.4% | 83.3% | 62.0% |
| mask_noise | video:temporal_mean | 2.5% | 8.3% | 72.1% | 53.7% |
| mask_noise | video:window_mean_best | 20.0% | 33.3% | 83.0% | 63.0% |
| mask_only | long | -26.5% | -22.8% | 44.2% | 13.9% |
| mask_only | short | 75.0% | 65.7% | 92.5% | 66.0% |
| mask_only | video:max_proj | 1.5% | -3.7% | 64.4% | 21.3% |
| mask_only | video:single_best | 50.6% | 56.5% | 83.3% | 62.0% |
| mask_only | video:temporal_mean | 2.9% | 9.3% | 72.1% | 53.7% |
| mask_only | video:window_mean_best | 23.6% | 35.2% | 83.0% | 63.0% |
| original | long | 0.0% | 0.0% | 44.2% | 13.9% |
| original | short | 0.0% | 0.0% | 92.5% | 66.0% |
| original | video:max_proj | 0.0% | 0.0% | 64.4% | 21.3% |
| original | video:single_best | 0.0% | 0.0% | 83.3% | 62.0% |
| original | video:temporal_mean | 0.0% | 0.0% | 72.1% | 53.7% |
| original | video:window_mean_best | 0.0% | 0.0% | 83.0% | 63.0% |
| stripe_0.00 | short | 82.6% | 64.6% | 92.5% | 66.0% |
| stripe_0.00 | video:max_proj | 8.9% | 1.3% | 64.4% | 21.3% |
| stripe_0.00 | video:single_best | 59.4% | 62.0% | 83.3% | 62.0% |
| stripe_0.00 | video:temporal_mean | 11.8% | 9.3% | 72.1% | 53.7% |
| stripe_0.00 | video:window_mean_best | 33.2% | 40.7% | 83.0% | 63.0% |
| stripe_0.10 | short | 78.8% | 66.0% | 92.5% | 66.0% |
| stripe_0.10 | video:max_proj | 8.1% | 10.2% | 64.4% | 21.3% |
| stripe_0.10 | video:single_best | 58.1% | 62.0% | 83.3% | 62.0% |
| stripe_0.10 | video:temporal_mean | 15.0% | 13.7% | 72.1% | 53.7% |
| stripe_0.10 | video:window_mean_best | 37.3% | 49.6% | 83.0% | 63.0% |
| stripe_0.18 | short | 82.4% | 66.0% | 92.5% | 66.0% |
| stripe_0.18 | video:max_proj | 11.5% | 16.9% | 64.4% | 21.3% |
| stripe_0.18 | video:single_best | 60.9% | 62.0% | 83.3% | 62.0% |
| stripe_0.18 | video:temporal_mean | 17.3% | 15.9% | 72.1% | 53.7% |
| stripe_0.18 | video:window_mean_best | 35.0% | 51.9% | 83.0% | 63.0% |
| stripe_0.30 | short | 81.3% | 66.0% | 92.5% | 66.0% |
| stripe_0.30 | video:max_proj | 10.6% | 12.4% | 64.4% | 21.3% |
| stripe_0.30 | video:single_best | 60.7% | 59.8% | 83.3% | 62.0% |
| stripe_0.30 | video:temporal_mean | 15.5% | 20.4% | 72.1% | 53.7% |
| stripe_0.30 | video:window_mean_best | 36.5% | 54.1% | 83.0% | 63.0% |
| vlm | long | 33.1% | 13.9% | 44.2% | 13.9% |
| vlm | short | 88.3% | 66.0% | 92.5% | 66.0% |
| vlm | video:max_proj | 50.5% | 21.3% | 64.4% | 21.3% |
| vlm | video:single_best | 78.4% | 62.0% | 83.3% | 62.0% |
| vlm | video:temporal_mean | 29.8% | 49.1% | 72.1% | 53.7% |
| vlm | video:window_mean_best | 67.5% | 62.0% | 83.0% | 63.0% |
