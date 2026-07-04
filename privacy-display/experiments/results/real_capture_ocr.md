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
| anti_ocr|long | 972 | 26.2% | 14.2% | 85.1% | 32.5% |
| anti_ocr|short | 972 | 8.2% | 0.2% | 12.1% | 12.9% |
| anti_ocr|video|max_proj | 324 | 46.5% | 10.8% | 56.9% | 57.4% |
| anti_ocr|video|single_best | 324 | 17.0% | 1.9% | 16.3% | 23.5% |
| anti_ocr|video|temporal_mean | 324 | 57.3% | 24.1% | 62.4% | 70.1% |
| anti_ocr|video|window_mean_best | 324 | 44.8% | 9.9% | 46.5% | 60.2% |
| deployed|long | 972 | 27.2% | 13.2% | 83.0% | 33.8% |
| deployed|short | 1377 | 6.1% | 0.1% | 9.0% | 8.6% |
| deployed|video|max_proj | 459 | 43.7% | 6.8% | 51.8% | 55.6% |
| deployed|video|single_best | 459 | 17.4% | 1.7% | 17.1% | 27.0% |
| deployed|video|temporal_mean | 459 | 45.2% | 20.0% | 57.7% | 60.3% |
| deployed|video|window_mean_best | 459 | 38.1% | 6.8% | 42.7% | 53.4% |
| glyph_0.00|short | 405 | 6.9% | 0.5% | 6.1% | 7.7% |
| glyph_0.00|video|max_proj | 135 | 39.4% | 4.4% | 41.0% | 55.6% |
| glyph_0.00|video|single_best | 135 | 13.2% | 0.7% | 9.9% | 19.3% |
| glyph_0.00|video|temporal_mean | 135 | 39.6% | 15.6% | 46.1% | 55.6% |
| glyph_0.00|video|window_mean_best | 135 | 30.0% | 4.4% | 28.8% | 45.2% |
| glyph_0.12|short | 405 | 5.9% | 0.0% | 5.9% | 6.7% |
| glyph_0.12|video|max_proj | 135 | 39.7% | 3.7% | 39.7% | 52.6% |
| glyph_0.12|video|single_best | 135 | 12.4% | 0.0% | 10.0% | 17.8% |
| glyph_0.12|video|temporal_mean | 135 | 39.5% | 13.3% | 43.4% | 56.3% |
| glyph_0.12|video|window_mean_best | 135 | 30.6% | 6.7% | 30.4% | 44.4% |
| glyph_0.22|short | 405 | 6.3% | 0.5% | 6.0% | 9.6% |
| glyph_0.22|video|max_proj | 135 | 38.2% | 3.0% | 38.2% | 52.6% |
| glyph_0.22|video|single_best | 135 | 13.8% | 0.0% | 9.6% | 20.7% |
| glyph_0.22|video|temporal_mean | 135 | 37.4% | 13.3% | 43.1% | 49.6% |
| glyph_0.22|video|window_mean_best | 135 | 35.2% | 7.4% | 31.1% | 53.3% |
| inversion_0.0|long | 405 | 29.6% | 9.4% | 67.2% | 39.5% |
| inversion_0.0|video|max_proj | 135 | 37.9% | 3.7% | 39.5% | 51.1% |
| inversion_0.0|video|single_best | 135 | 10.5% | 0.0% | 6.7% | 17.0% |
| inversion_0.0|video|temporal_mean | 135 | 50.2% | 20.7% | 51.3% | 68.9% |
| inversion_0.0|video|window_mean_best | 135 | 32.3% | 6.7% | 36.1% | 50.4% |
| inversion_0.2|long | 405 | 29.9% | 11.6% | 75.6% | 40.7% |
| inversion_0.2|video|max_proj | 135 | 39.4% | 3.7% | 41.2% | 54.8% |
| inversion_0.2|video|single_best | 135 | 12.9% | 2.2% | 10.4% | 19.3% |
| inversion_0.2|video|temporal_mean | 135 | 43.0% | 20.0% | 49.4% | 61.5% |
| inversion_0.2|video|window_mean_best | 135 | 32.0% | 4.4% | 33.2% | 47.4% |
| inversion_0.3|long | 405 | 33.6% | 13.3% | 74.9% | 44.7% |
| inversion_0.3|video|max_proj | 135 | 34.3% | 3.0% | 37.8% | 49.6% |
| inversion_0.3|video|single_best | 135 | 15.0% | 0.7% | 11.7% | 23.0% |
| inversion_0.3|video|temporal_mean | 135 | 38.3% | 11.1% | 48.4% | 57.8% |
| inversion_0.3|video|window_mean_best | 135 | 31.3% | 7.4% | 33.7% | 48.1% |
| inversion_0.5|long | 405 | 29.2% | 9.4% | 64.9% | 39.5% |
| inversion_0.5|video|max_proj | 135 | 30.9% | 1.5% | 38.1% | 44.4% |
| inversion_0.5|video|single_best | 135 | 13.8% | 2.2% | 10.5% | 23.7% |
| inversion_0.5|video|temporal_mean | 135 | 39.8% | 17.8% | 48.9% | 54.8% |
| inversion_0.5|video|window_mean_best | 135 | 33.8% | 7.4% | 33.9% | 51.1% |
| inversion_1.0|long | 405 | 6.8% | 0.0% | 29.1% | 12.6% |
| inversion_1.0|video|max_proj | 135 | 31.2% | 3.0% | 23.5% | 41.5% |
| inversion_1.0|video|single_best | 135 | 37.8% | 15.6% | 32.5% | 49.6% |
| inversion_1.0|video|temporal_mean | 135 | 10.9% | 0.0% | 14.5% | 19.3% |
| inversion_1.0|video|window_mean_best | 135 | 32.8% | 5.9% | 30.4% | 45.9% |
| mask_noise|long | 972 | 30.4% | 13.8% | 85.5% | 37.2% |
| mask_noise|short | 972 | 11.3% | 0.9% | 12.9% | 16.5% |
| mask_noise|video|max_proj | 324 | 48.8% | 11.7% | 55.6% | 60.2% |
| mask_noise|video|single_best | 324 | 16.8% | 1.5% | 13.7% | 25.3% |
| mask_noise|video|temporal_mean | 324 | 57.4% | 23.5% | 63.7% | 71.3% |
| mask_noise|video|window_mean_best | 324 | 48.0% | 13.9% | 51.5% | 63.6% |
| mask_only|long | 972 | 29.5% | 12.1% | 83.0% | 36.5% |
| mask_only|short | 972 | 7.7% | 0.1% | 10.8% | 12.7% |
| mask_only|video|max_proj | 324 | 45.8% | 11.4% | 50.7% | 57.4% |
| mask_only|video|single_best | 324 | 17.8% | 1.9% | 15.6% | 26.2% |
| mask_only|video|temporal_mean | 324 | 57.9% | 24.1% | 62.0% | 71.3% |
| mask_only|video|window_mean_best | 324 | 45.1% | 13.6% | 45.6% | 59.3% |
| original|long | 972 | 16.9% | 6.3% | 63.2% | 21.2% |
| original|short | 972 | 67.0% | 32.8% | 83.6% | 76.1% |
| original|video|max_proj | 324 | 40.7% | 10.5% | 45.2% | 55.6% |
| original|video|single_best | 324 | 70.9% | 37.0% | 71.7% | 80.6% |
| original|video|temporal_mean | 324 | 62.9% | 33.3% | 69.3% | 71.9% |
| original|video|window_mean_best | 324 | 70.6% | 37.0% | 72.9% | 80.2% |
| stripe_0.00|short | 405 | 4.8% | 0.5% | 5.3% | 5.4% |
| stripe_0.00|video|max_proj | 135 | 39.3% | 7.4% | 40.9% | 54.1% |
| stripe_0.00|video|single_best | 135 | 13.2% | 0.0% | 14.0% | 20.7% |
| stripe_0.00|video|temporal_mean | 135 | 42.2% | 19.3% | 47.2% | 59.3% |
| stripe_0.00|video|window_mean_best | 135 | 32.7% | 8.9% | 34.8% | 48.9% |
| stripe_0.10|short | 405 | 5.9% | 0.0% | 6.8% | 7.7% |
| stripe_0.10|video|max_proj | 135 | 36.9% | 3.7% | 40.7% | 50.4% |
| stripe_0.10|video|single_best | 135 | 13.5% | 0.0% | 10.4% | 20.7% |
| stripe_0.10|video|temporal_mean | 135 | 40.1% | 20.0% | 47.5% | 57.8% |
| stripe_0.10|video|window_mean_best | 135 | 28.4% | 4.4% | 30.2% | 45.2% |
| stripe_0.18|short | 405 | 4.9% | 0.0% | 4.5% | 5.2% |
| stripe_0.18|video|max_proj | 135 | 37.2% | 1.5% | 44.7% | 52.6% |
| stripe_0.18|video|single_best | 135 | 10.6% | 0.0% | 8.1% | 16.3% |
| stripe_0.18|video|temporal_mean | 135 | 38.5% | 17.8% | 47.2% | 52.6% |
| stripe_0.18|video|window_mean_best | 135 | 32.0% | 4.4% | 34.4% | 48.1% |
| stripe_0.30|short | 405 | 5.3% | 0.0% | 5.1% | 5.7% |
| stripe_0.30|video|max_proj | 135 | 37.8% | 3.7% | 37.9% | 51.9% |
| stripe_0.30|video|single_best | 135 | 12.3% | 0.7% | 6.9% | 20.0% |
| stripe_0.30|video|temporal_mean | 135 | 37.7% | 14.1% | 43.9% | 53.3% |
| stripe_0.30|video|window_mean_best | 135 | 30.2% | 3.7% | 30.6% | 45.2% |
| capture_hardened|long | 972 | 3.4% | 0.0% | 13.0% | 4.8% |
| capture_hardened|short | 972 | 1.9% | 0.0% | 2.2% | 1.2% |
| capture_hardened|video|max_proj | 324 | 7.1% | 0.0% | 10.5% | 7.4% |
| capture_hardened|video|single_best | 324 | 2.1% | 0.0% | 1.7% | 2.5% |
| capture_hardened|video|temporal_mean | 324 | 20.1% | 1.9% | 15.8% | 33.3% |
| capture_hardened|video|window_mean_best | 324 | 7.2% | 0.3% | 8.7% | 12.7% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 324 | 61.6% | 39.8% | 95.7% | 71.3% |
| anti_ocr | short | 324 | 20.7% | 0.6% | 33.7% | 32.4% |
| anti_ocr | video:max_proj | 108 | 72.5% | 24.1% | 77.7% | 85.2% |
| anti_ocr | video:single_best | 108 | 31.1% | 5.6% | 38.8% | 37.0% |
| anti_ocr | video:temporal_mean | 108 | 78.6% | 50.9% | 83.3% | 88.9% |
| anti_ocr | video:window_mean_best | 108 | 68.1% | 25.9% | 72.5% | 83.3% |
| deployed | long | 324 | 60.9% | 36.4% | 96.5% | 69.1% |
| deployed | short | 459 | 15.1% | 0.4% | 24.0% | 20.5% |
| deployed | video:max_proj | 153 | 69.5% | 18.3% | 70.8% | 83.7% |
| deployed | video:single_best | 153 | 31.6% | 5.2% | 40.1% | 43.8% |
| deployed | video:temporal_mean | 153 | 71.1% | 42.5% | 78.5% | 85.0% |
| deployed | video:window_mean_best | 153 | 61.1% | 17.0% | 69.4% | 79.7% |
| glyph_0.00 | short | 135 | 14.9% | 1.5% | 14.8% | 15.6% |
| glyph_0.00 | video:max_proj | 45 | 60.5% | 13.3% | 63.0% | 80.0% |
| glyph_0.00 | video:single_best | 45 | 25.2% | 2.2% | 22.4% | 31.1% |
| glyph_0.00 | video:temporal_mean | 45 | 64.9% | 33.3% | 73.1% | 86.7% |
| glyph_0.00 | video:window_mean_best | 45 | 52.8% | 13.3% | 56.6% | 73.3% |
| glyph_0.12 | short | 135 | 12.7% | 0.0% | 15.5% | 13.3% |
| glyph_0.12 | video:max_proj | 45 | 60.8% | 11.1% | 55.1% | 75.6% |
| glyph_0.12 | video:single_best | 45 | 24.1% | 0.0% | 24.5% | 28.9% |
| glyph_0.12 | video:temporal_mean | 45 | 62.0% | 33.3% | 68.3% | 77.8% |
| glyph_0.12 | video:window_mean_best | 45 | 52.7% | 17.8% | 57.0% | 68.9% |
| glyph_0.22 | short | 135 | 12.8% | 1.5% | 15.4% | 16.3% |
| glyph_0.22 | video:max_proj | 45 | 58.5% | 6.7% | 55.2% | 80.0% |
| glyph_0.22 | video:single_best | 45 | 25.3% | 0.0% | 23.1% | 37.8% |
| glyph_0.22 | video:temporal_mean | 45 | 64.2% | 31.1% | 66.6% | 77.8% |
| glyph_0.22 | video:window_mean_best | 45 | 54.8% | 20.0% | 54.0% | 77.8% |
| inversion_0.0 | long | 135 | 68.6% | 28.1% | 85.1% | 83.7% |
| inversion_0.0 | video:max_proj | 45 | 60.7% | 8.9% | 57.4% | 80.0% |
| inversion_0.0 | video:single_best | 45 | 20.5% | 0.0% | 16.6% | 35.6% |
| inversion_0.0 | video:temporal_mean | 45 | 72.7% | 46.7% | 72.9% | 88.9% |
| inversion_0.0 | video:window_mean_best | 45 | 53.1% | 20.0% | 62.5% | 80.0% |
| inversion_0.2 | long | 135 | 67.0% | 33.3% | 92.1% | 82.2% |
| inversion_0.2 | video:max_proj | 45 | 60.7% | 11.1% | 60.1% | 84.4% |
| inversion_0.2 | video:single_best | 45 | 24.2% | 6.7% | 24.6% | 33.3% |
| inversion_0.2 | video:temporal_mean | 45 | 69.8% | 48.9% | 74.4% | 88.9% |
| inversion_0.2 | video:window_mean_best | 45 | 52.8% | 13.3% | 59.4% | 77.8% |
| inversion_0.3 | long | 135 | 72.0% | 38.5% | 92.3% | 85.9% |
| inversion_0.3 | video:max_proj | 45 | 57.3% | 8.9% | 55.6% | 80.0% |
| inversion_0.3 | video:single_best | 45 | 27.9% | 2.2% | 27.1% | 35.6% |
| inversion_0.3 | video:temporal_mean | 45 | 64.3% | 28.9% | 73.5% | 84.4% |
| inversion_0.3 | video:window_mean_best | 45 | 52.5% | 22.2% | 57.8% | 73.3% |
| inversion_0.5 | long | 135 | 61.7% | 25.9% | 89.0% | 74.1% |
| inversion_0.5 | video:max_proj | 45 | 58.0% | 4.4% | 59.4% | 84.4% |
| inversion_0.5 | video:single_best | 45 | 24.7% | 6.7% | 26.6% | 33.3% |
| inversion_0.5 | video:temporal_mean | 45 | 66.4% | 40.0% | 73.4% | 86.7% |
| inversion_0.5 | video:window_mean_best | 45 | 55.3% | 20.0% | 62.4% | 77.8% |
| inversion_1.0 | long | 135 | 18.1% | 0.0% | 62.7% | 35.6% |
| inversion_1.0 | video:max_proj | 45 | 55.6% | 8.9% | 43.8% | 68.9% |
| inversion_1.0 | video:single_best | 45 | 49.9% | 33.3% | 43.4% | 60.0% |
| inversion_1.0 | video:temporal_mean | 45 | 28.4% | 0.0% | 38.3% | 53.3% |
| inversion_1.0 | video:window_mean_best | 45 | 51.0% | 17.8% | 50.8% | 68.9% |
| mask_noise | long | 324 | 68.0% | 39.8% | 95.7% | 76.2% |
| mask_noise | short | 324 | 25.6% | 2.8% | 34.4% | 36.1% |
| mask_noise | video:max_proj | 108 | 73.7% | 26.9% | 79.0% | 85.2% |
| mask_noise | video:single_best | 108 | 33.7% | 4.6% | 35.2% | 47.2% |
| mask_noise | video:temporal_mean | 108 | 79.2% | 49.1% | 83.9% | 88.9% |
| mask_noise | video:window_mean_best | 108 | 71.2% | 33.3% | 75.4% | 85.2% |
| mask_only | long | 324 | 67.2% | 35.5% | 94.0% | 75.0% |
| mask_only | short | 324 | 19.2% | 0.3% | 30.8% | 30.6% |
| mask_only | video:max_proj | 108 | 71.7% | 25.9% | 75.6% | 84.3% |
| mask_only | video:single_best | 108 | 33.6% | 5.6% | 38.2% | 43.5% |
| mask_only | video:temporal_mean | 108 | 79.0% | 48.1% | 84.0% | 88.0% |
| mask_only | video:window_mean_best | 108 | 66.8% | 29.6% | 71.9% | 79.6% |
| original | long | 324 | 47.3% | 18.8% | 95.7% | 58.6% |
| original | short | 324 | 94.1% | 65.7% | 98.4% | 99.4% |
| original | video:max_proj | 108 | 70.2% | 25.0% | 79.0% | 86.1% |
| original | video:single_best | 108 | 86.4% | 64.8% | 86.9% | 95.4% |
| original | video:temporal_mean | 108 | 79.9% | 61.1% | 85.6% | 86.1% |
| original | video:window_mean_best | 108 | 86.4% | 65.7% | 85.9% | 95.4% |
| stripe_0.00 | short | 135 | 10.3% | 1.5% | 12.0% | 10.4% |
| stripe_0.00 | video:max_proj | 45 | 63.3% | 20.0% | 66.4% | 82.2% |
| stripe_0.00 | video:single_best | 45 | 25.3% | 0.0% | 32.7% | 40.0% |
| stripe_0.00 | video:temporal_mean | 45 | 69.0% | 44.4% | 73.4% | 86.7% |
| stripe_0.00 | video:window_mean_best | 45 | 53.4% | 22.2% | 58.8% | 77.8% |
| stripe_0.10 | short | 135 | 14.3% | 0.0% | 18.0% | 17.8% |
| stripe_0.10 | video:max_proj | 45 | 62.7% | 11.1% | 64.8% | 80.0% |
| stripe_0.10 | video:single_best | 45 | 26.3% | 0.0% | 24.8% | 35.6% |
| stripe_0.10 | video:temporal_mean | 45 | 64.8% | 42.2% | 72.8% | 84.4% |
| stripe_0.10 | video:window_mean_best | 45 | 47.7% | 13.3% | 61.0% | 66.7% |
| stripe_0.18 | short | 135 | 10.5% | 0.0% | 11.8% | 9.6% |
| stripe_0.18 | video:max_proj | 45 | 59.8% | 4.4% | 63.6% | 80.0% |
| stripe_0.18 | video:single_best | 45 | 22.7% | 0.0% | 23.7% | 31.1% |
| stripe_0.18 | video:temporal_mean | 45 | 59.3% | 40.0% | 70.1% | 75.6% |
| stripe_0.18 | video:window_mean_best | 45 | 51.8% | 11.1% | 56.4% | 77.8% |
| stripe_0.30 | short | 135 | 11.7% | 0.0% | 12.7% | 10.4% |
| stripe_0.30 | video:max_proj | 45 | 60.5% | 8.9% | 56.0% | 77.8% |
| stripe_0.30 | video:single_best | 45 | 23.8% | 2.2% | 17.5% | 31.1% |
| stripe_0.30 | video:temporal_mean | 45 | 63.3% | 33.3% | 69.8% | 82.2% |
| stripe_0.30 | video:window_mean_best | 45 | 51.0% | 11.1% | 57.0% | 75.6% |
| capture_hardened | long | 324 | 9.3% | 0.0% | 34.9% | 14.2% |
| capture_hardened | short | 324 | 5.0% | 0.0% | 6.5% | 3.7% |
| capture_hardened | video:max_proj | 108 | 16.4% | 0.0% | 30.3% | 21.3% |
| capture_hardened | video:single_best | 108 | 5.5% | 0.0% | 5.0% | 7.4% |
| capture_hardened | video:temporal_mean | 108 | 47.9% | 5.6% | 45.6% | 76.9% |
| capture_hardened | video:window_mean_best | 108 | 18.6% | 0.9% | 25.2% | 35.2% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | -14.4% | -21.0% | 47.3% | 18.8% |
| anti_ocr | short | 73.4% | 65.1% | 94.1% | 65.7% |
| anti_ocr | video:max_proj | -2.3% | 0.9% | 70.2% | 25.0% |
| anti_ocr | video:single_best | 55.3% | 59.3% | 86.4% | 64.8% |
| anti_ocr | video:temporal_mean | 1.3% | 10.2% | 79.9% | 61.1% |
| anti_ocr | video:window_mean_best | 18.3% | 39.8% | 86.4% | 65.7% |
| deployed | long | -13.6% | -17.6% | 47.3% | 18.8% |
| deployed | short | 79.0% | 65.3% | 94.1% | 65.7% |
| deployed | video:max_proj | 0.6% | 6.7% | 70.2% | 25.0% |
| deployed | video:single_best | 54.8% | 59.6% | 86.4% | 64.8% |
| deployed | video:temporal_mean | 8.8% | 18.6% | 79.9% | 61.1% |
| deployed | video:window_mean_best | 25.3% | 48.7% | 86.4% | 65.7% |
| glyph_0.00 | short | 79.2% | 64.3% | 94.1% | 65.7% |
| glyph_0.00 | video:max_proj | 9.7% | 11.7% | 70.2% | 25.0% |
| glyph_0.00 | video:single_best | 61.2% | 62.6% | 86.4% | 64.8% |
| glyph_0.00 | video:temporal_mean | 15.0% | 27.8% | 79.9% | 61.1% |
| glyph_0.00 | video:window_mean_best | 33.6% | 52.4% | 86.4% | 65.7% |
| glyph_0.12 | short | 81.4% | 65.7% | 94.1% | 65.7% |
| glyph_0.12 | video:max_proj | 9.4% | 13.9% | 70.2% | 25.0% |
| glyph_0.12 | video:single_best | 62.3% | 64.8% | 86.4% | 64.8% |
| glyph_0.12 | video:temporal_mean | 17.9% | 27.8% | 79.9% | 61.1% |
| glyph_0.12 | video:window_mean_best | 33.7% | 48.0% | 86.4% | 65.7% |
| glyph_0.22 | short | 81.3% | 64.3% | 94.1% | 65.7% |
| glyph_0.22 | video:max_proj | 11.6% | 18.3% | 70.2% | 25.0% |
| glyph_0.22 | video:single_best | 61.1% | 64.8% | 86.4% | 64.8% |
| glyph_0.22 | video:temporal_mean | 15.7% | 30.0% | 79.9% | 61.1% |
| glyph_0.22 | video:window_mean_best | 31.6% | 45.7% | 86.4% | 65.7% |
| inversion_0.0 | long | -21.3% | -9.3% | 47.3% | 18.8% |
| inversion_0.0 | video:max_proj | 9.5% | 16.1% | 70.2% | 25.0% |
| inversion_0.0 | video:single_best | 65.9% | 64.8% | 86.4% | 64.8% |
| inversion_0.0 | video:temporal_mean | 7.2% | 14.4% | 79.9% | 61.1% |
| inversion_0.0 | video:window_mean_best | 33.3% | 45.7% | 86.4% | 65.7% |
| inversion_0.2 | long | -19.7% | -14.5% | 47.3% | 18.8% |
| inversion_0.2 | video:max_proj | 9.5% | 13.9% | 70.2% | 25.0% |
| inversion_0.2 | video:single_best | 62.2% | 58.1% | 86.4% | 64.8% |
| inversion_0.2 | video:temporal_mean | 10.1% | 12.2% | 79.9% | 61.1% |
| inversion_0.2 | video:window_mean_best | 33.6% | 52.4% | 86.4% | 65.7% |
| inversion_0.3 | long | -24.7% | -19.7% | 47.3% | 18.8% |
| inversion_0.3 | video:max_proj | 12.9% | 16.1% | 70.2% | 25.0% |
| inversion_0.3 | video:single_best | 58.5% | 62.6% | 86.4% | 64.8% |
| inversion_0.3 | video:temporal_mean | 15.6% | 32.2% | 79.9% | 61.1% |
| inversion_0.3 | video:window_mean_best | 33.9% | 43.5% | 86.4% | 65.7% |
| inversion_0.5 | long | -14.4% | -7.1% | 47.3% | 18.8% |
| inversion_0.5 | video:max_proj | 12.2% | 20.6% | 70.2% | 25.0% |
| inversion_0.5 | video:single_best | 61.7% | 58.1% | 86.4% | 64.8% |
| inversion_0.5 | video:temporal_mean | 13.5% | 21.1% | 79.9% | 61.1% |
| inversion_0.5 | video:window_mean_best | 31.1% | 45.7% | 86.4% | 65.7% |
| inversion_1.0 | long | 29.1% | 18.8% | 47.3% | 18.8% |
| inversion_1.0 | video:max_proj | 14.6% | 16.1% | 70.2% | 25.0% |
| inversion_1.0 | video:single_best | 36.5% | 31.5% | 86.4% | 64.8% |
| inversion_1.0 | video:temporal_mean | 51.5% | 61.1% | 79.9% | 61.1% |
| inversion_1.0 | video:window_mean_best | 35.4% | 48.0% | 86.4% | 65.7% |
| mask_noise | long | -20.8% | -21.0% | 47.3% | 18.8% |
| mask_noise | short | 68.5% | 63.0% | 94.1% | 65.7% |
| mask_noise | video:max_proj | -3.6% | -1.9% | 70.2% | 25.0% |
| mask_noise | video:single_best | 52.7% | 60.2% | 86.4% | 64.8% |
| mask_noise | video:temporal_mean | 0.7% | 12.0% | 79.9% | 61.1% |
| mask_noise | video:window_mean_best | 15.2% | 32.4% | 86.4% | 65.7% |
| mask_only | long | -19.9% | -16.7% | 47.3% | 18.8% |
| mask_only | short | 74.9% | 65.4% | 94.1% | 65.7% |
| mask_only | video:max_proj | -1.6% | -0.9% | 70.2% | 25.0% |
| mask_only | video:single_best | 52.8% | 59.3% | 86.4% | 64.8% |
| mask_only | video:temporal_mean | 0.9% | 13.0% | 79.9% | 61.1% |
| mask_only | video:window_mean_best | 19.6% | 36.1% | 86.4% | 65.7% |
| original | long | 0.0% | 0.0% | 47.3% | 18.8% |
| original | short | 0.0% | 0.0% | 94.1% | 65.7% |
| original | video:max_proj | 0.0% | 0.0% | 70.2% | 25.0% |
| original | video:single_best | 0.0% | 0.0% | 86.4% | 64.8% |
| original | video:temporal_mean | 0.0% | 0.0% | 79.9% | 61.1% |
| original | video:window_mean_best | 0.0% | 0.0% | 86.4% | 65.7% |
| stripe_0.00 | short | 83.8% | 64.3% | 94.1% | 65.7% |
| stripe_0.00 | video:max_proj | 6.8% | 5.0% | 70.2% | 25.0% |
| stripe_0.00 | video:single_best | 61.1% | 64.8% | 86.4% | 64.8% |
| stripe_0.00 | video:temporal_mean | 10.9% | 16.7% | 79.9% | 61.1% |
| stripe_0.00 | video:window_mean_best | 33.0% | 43.5% | 86.4% | 65.7% |
| stripe_0.10 | short | 79.8% | 65.7% | 94.1% | 65.7% |
| stripe_0.10 | video:max_proj | 7.4% | 13.9% | 70.2% | 25.0% |
| stripe_0.10 | video:single_best | 60.2% | 64.8% | 86.4% | 64.8% |
| stripe_0.10 | video:temporal_mean | 15.1% | 18.9% | 79.9% | 61.1% |
| stripe_0.10 | video:window_mean_best | 38.7% | 52.4% | 86.4% | 65.7% |
| stripe_0.18 | short | 83.6% | 65.7% | 94.1% | 65.7% |
| stripe_0.18 | video:max_proj | 10.3% | 20.6% | 70.2% | 25.0% |
| stripe_0.18 | video:single_best | 63.7% | 64.8% | 86.4% | 64.8% |
| stripe_0.18 | video:temporal_mean | 20.6% | 21.1% | 79.9% | 61.1% |
| stripe_0.18 | video:window_mean_best | 34.6% | 54.6% | 86.4% | 65.7% |
| stripe_0.30 | short | 82.5% | 65.7% | 94.1% | 65.7% |
| stripe_0.30 | video:max_proj | 9.6% | 16.1% | 70.2% | 25.0% |
| stripe_0.30 | video:single_best | 62.6% | 62.6% | 86.4% | 64.8% |
| stripe_0.30 | video:temporal_mean | 16.7% | 27.8% | 79.9% | 61.1% |
| stripe_0.30 | video:window_mean_best | 35.4% | 54.6% | 86.4% | 65.7% |
| capture_hardened | long | 37.9% | 18.8% | 47.3% | 18.8% |
| capture_hardened | short | 89.1% | 65.7% | 94.1% | 65.7% |
| capture_hardened | video:max_proj | 53.8% | 25.0% | 70.2% | 25.0% |
| capture_hardened | video:single_best | 80.9% | 64.8% | 86.4% | 64.8% |
| capture_hardened | video:temporal_mean | 32.0% | 55.6% | 79.9% | 61.1% |
| capture_hardened | video:window_mean_best | 67.9% | 64.8% | 86.4% | 65.7% |
