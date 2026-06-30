# Real Camera Capture OCR Summary

This file is generated from manually collected camera photos or video frames.

- Captures: 1175
- OCR rows: 3525

## By Condition

| Condition | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|---:|
| anti_ocr|long | 108 | 59.1% | 23.1% | 56.9% | 77.8% |
| anti_ocr|short | 108 | 0.3% | 0.0% | 1.0% | 0.9% |
| anti_ocr|video|max_proj | 36 | 0.0% | 0.0% | 0.0% | 0.0% |
| anti_ocr|video|single_best | 36 | 0.2% | 0.0% | 0.0% | 0.0% |
| anti_ocr|video|temporal_mean | 36 | 0.0% | 0.0% | 0.0% | 0.0% |
| anti_ocr|video|window_mean_best | 36 | 0.3% | 0.0% | 0.0% | 0.0% |
| deployed|long | 108 | 51.5% | 19.4% | 54.2% | 69.4% |
| deployed|short | 153 | 0.0% | 0.0% | 0.0% | 0.0% |
| deployed|video|max_proj | 51 | 0.0% | 0.0% | 0.0% | 0.0% |
| deployed|video|single_best | 51 | 0.9% | 0.0% | 0.1% | 0.0% |
| deployed|video|temporal_mean | 51 | 0.0% | 0.0% | 0.0% | 0.0% |
| deployed|video|window_mean_best | 51 | 0.7% | 0.0% | 0.0% | 2.0% |
| glyph_0.00|short | 45 | 0.5% | 0.0% | 0.0% | 0.0% |
| glyph_0.00|video|max_proj | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.00|video|single_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.00|video|temporal_mean | 15 | 1.5% | 0.0% | 0.0% | 6.7% |
| glyph_0.00|video|window_mean_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.12|short | 45 | 0.2% | 0.0% | 0.0% | 0.0% |
| glyph_0.12|video|max_proj | 15 | 0.2% | 0.0% | 0.1% | 0.0% |
| glyph_0.12|video|single_best | 15 | 0.5% | 0.0% | 0.0% | 0.0% |
| glyph_0.12|video|temporal_mean | 15 | 0.6% | 0.0% | 0.0% | 0.0% |
| glyph_0.12|video|window_mean_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.22|short | 45 | 0.1% | 0.0% | 0.0% | 0.0% |
| glyph_0.22|video|max_proj | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.22|video|single_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.22|video|temporal_mean | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.22|video|window_mean_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.0|long | 45 | 42.1% | 6.7% | 27.4% | 60.0% |
| inversion_0.0|video|max_proj | 15 | 0.4% | 0.0% | 0.2% | 0.0% |
| inversion_0.0|video|single_best | 15 | 0.7% | 0.0% | 0.0% | 0.0% |
| inversion_0.0|video|temporal_mean | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.0|video|window_mean_best | 15 | 1.1% | 0.0% | 0.2% | 0.0% |
| inversion_0.2|long | 45 | 53.9% | 6.7% | 45.3% | 77.8% |
| inversion_0.2|video|max_proj | 15 | 0.2% | 0.0% | 0.0% | 0.0% |
| inversion_0.2|video|single_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.2|video|temporal_mean | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.2|video|window_mean_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.3|long | 45 | 55.6% | 6.7% | 46.5% | 77.8% |
| inversion_0.3|video|max_proj | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.3|video|single_best | 15 | 0.5% | 0.0% | 0.0% | 0.0% |
| inversion_0.3|video|temporal_mean | 15 | 0.2% | 0.0% | 0.0% | 0.0% |
| inversion_0.3|video|window_mean_best | 15 | 0.7% | 0.0% | 0.0% | 0.0% |
| inversion_0.5|long | 45 | 47.1% | 4.4% | 47.8% | 68.9% |
| inversion_0.5|video|max_proj | 15 | 0.1% | 0.0% | 0.1% | 0.0% |
| inversion_0.5|video|single_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.5|video|temporal_mean | 15 | 0.8% | 0.0% | 0.0% | 0.0% |
| inversion_0.5|video|window_mean_best | 15 | 0.5% | 0.0% | 0.0% | 0.0% |
| inversion_1.0|long | 45 | 33.0% | 13.3% | 28.5% | 46.7% |
| inversion_1.0|video|max_proj | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_1.0|video|single_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_1.0|video|temporal_mean | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_1.0|video|window_mean_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| mask_noise|long | 108 | 58.9% | 6.5% | 58.8% | 78.7% |
| mask_noise|short | 108 | 0.1% | 0.0% | 0.0% | 0.0% |
| mask_noise|video|max_proj | 36 | 0.6% | 0.0% | 0.0% | 2.8% |
| mask_noise|video|single_best | 36 | 0.2% | 0.0% | 0.0% | 0.0% |
| mask_noise|video|temporal_mean | 36 | 0.4% | 0.0% | 0.0% | 0.0% |
| mask_noise|video|window_mean_best | 36 | 0.8% | 0.0% | 0.0% | 2.8% |
| mask_only|long | 108 | 44.7% | 6.5% | 54.7% | 60.2% |
| mask_only|short | 108 | 0.4% | 0.0% | 0.0% | 0.0% |
| mask_only|video|max_proj | 36 | 0.0% | 0.0% | 0.0% | 0.0% |
| mask_only|video|single_best | 36 | 0.5% | 0.0% | 0.0% | 0.0% |
| mask_only|video|temporal_mean | 36 | 0.1% | 0.0% | 0.0% | 0.0% |
| mask_only|video|window_mean_best | 36 | 0.3% | 0.0% | 0.0% | 0.0% |
| original|long | 108 | 29.4% | 2.8% | 31.2% | 37.0% |
| original|short | 108 | 40.4% | 20.4% | 31.4% | 50.9% |
| original|video|max_proj | 36 | 12.7% | 0.0% | 10.3% | 19.4% |
| original|video|single_best | 36 | 34.9% | 11.1% | 30.8% | 44.4% |
| original|video|temporal_mean | 36 | 8.9% | 0.0% | 6.2% | 11.1% |
| original|video|window_mean_best | 36 | 32.5% | 11.1% | 27.5% | 36.1% |
| stripe_0.00|short | 45 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.00|video|max_proj | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.00|video|single_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.00|video|temporal_mean | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.00|video|window_mean_best | 15 | 0.9% | 0.0% | 0.0% | 0.0% |
| stripe_0.10|short | 45 | 0.2% | 0.0% | 0.0% | 0.0% |
| stripe_0.10|video|max_proj | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.10|video|single_best | 15 | 0.8% | 0.0% | 0.0% | 0.0% |
| stripe_0.10|video|temporal_mean | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.10|video|window_mean_best | 15 | 1.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.18|short | 45 | 0.5% | 0.0% | 0.0% | 0.0% |
| stripe_0.18|video|max_proj | 15 | 0.2% | 0.0% | 0.1% | 0.0% |
| stripe_0.18|video|single_best | 15 | 0.6% | 0.0% | 0.0% | 0.0% |
| stripe_0.18|video|temporal_mean | 15 | 0.2% | 0.0% | 0.0% | 0.0% |
| stripe_0.18|video|window_mean_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.30|short | 45 | 0.0% | 0.0% | 0.1% | 0.0% |
| stripe_0.30|video|max_proj | 15 | 0.1% | 0.0% | 0.0% | 0.0% |
| stripe_0.30|video|single_best | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.30|video|temporal_mean | 15 | 2.2% | 0.0% | 0.0% | 0.0% |
| stripe_0.30|video|window_mean_best | 15 | 1.4% | 0.0% | 0.0% | 0.0% |
| vlm|long | 108 | 8.1% | 0.0% | 3.5% | 11.1% |
| vlm|short | 108 | 0.3% | 0.0% | 0.0% | 0.0% |
| vlm|video|max_proj | 36 | 0.6% | 0.0% | 0.0% | 0.0% |
| vlm|video|single_best | 36 | 0.8% | 0.0% | 0.0% | 0.0% |
| vlm|video|temporal_mean | 36 | 0.0% | 0.0% | 0.0% | 0.0% |
| vlm|video|window_mean_best | 36 | 1.7% | 0.0% | 0.0% | 2.8% |

## By Ablation And Attack (best-of-engine, attacker-favorable)

| Ablation | Attack | Rows | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---|---:|---:|---:|---:|---:|
| anti_ocr | long | 36 | 91.1% | 63.9% | 87.5% | 97.2% |
| anti_ocr | short | 36 | 0.8% | 0.0% | 3.0% | 2.8% |
| anti_ocr | video:max_proj | 12 | 0.0% | 0.0% | 0.1% | 0.0% |
| anti_ocr | video:single_best | 12 | 0.6% | 0.0% | 0.0% | 0.0% |
| anti_ocr | video:temporal_mean | 12 | 0.0% | 0.0% | 0.0% | 0.0% |
| anti_ocr | video:window_mean_best | 12 | 0.9% | 0.0% | 0.0% | 0.0% |
| deployed | long | 36 | 85.6% | 44.4% | 86.0% | 97.2% |
| deployed | short | 51 | 0.0% | 0.0% | 0.0% | 0.0% |
| deployed | video:max_proj | 17 | 0.0% | 0.0% | 0.0% | 0.0% |
| deployed | video:single_best | 17 | 2.8% | 0.0% | 0.2% | 0.0% |
| deployed | video:temporal_mean | 17 | 0.0% | 0.0% | 0.0% | 0.0% |
| deployed | video:window_mean_best | 17 | 2.1% | 0.0% | 0.1% | 5.9% |
| glyph_0.00 | short | 15 | 1.6% | 0.0% | 0.0% | 0.0% |
| glyph_0.00 | video:max_proj | 5 | 0.1% | 0.0% | 0.0% | 0.0% |
| glyph_0.00 | video:single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.00 | video:temporal_mean | 5 | 4.4% | 0.0% | 0.0% | 20.0% |
| glyph_0.00 | video:window_mean_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.12 | short | 15 | 0.7% | 0.0% | 0.0% | 0.0% |
| glyph_0.12 | video:max_proj | 5 | 0.7% | 0.0% | 0.2% | 0.0% |
| glyph_0.12 | video:single_best | 5 | 1.5% | 0.0% | 0.0% | 0.0% |
| glyph_0.12 | video:temporal_mean | 5 | 1.7% | 0.0% | 0.0% | 0.0% |
| glyph_0.12 | video:window_mean_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.22 | short | 15 | 0.2% | 0.0% | 0.0% | 0.0% |
| glyph_0.22 | video:max_proj | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.22 | video:single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.22 | video:temporal_mean | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| glyph_0.22 | video:window_mean_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.0 | long | 15 | 79.2% | 20.0% | 80.1% | 100.0% |
| inversion_0.0 | video:max_proj | 5 | 1.2% | 0.0% | 0.5% | 0.0% |
| inversion_0.0 | video:single_best | 5 | 2.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.0 | video:temporal_mean | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.0 | video:window_mean_best | 5 | 3.2% | 0.0% | 0.7% | 0.0% |
| inversion_0.2 | long | 15 | 82.7% | 20.0% | 94.7% | 100.0% |
| inversion_0.2 | video:max_proj | 5 | 0.5% | 0.0% | 0.0% | 0.0% |
| inversion_0.2 | video:single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.2 | video:temporal_mean | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.2 | video:window_mean_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.3 | long | 15 | 84.7% | 20.0% | 94.7% | 100.0% |
| inversion_0.3 | video:max_proj | 5 | 0.1% | 0.0% | 0.0% | 0.0% |
| inversion_0.3 | video:single_best | 5 | 1.4% | 0.0% | 0.0% | 0.0% |
| inversion_0.3 | video:temporal_mean | 5 | 0.5% | 0.0% | 0.0% | 0.0% |
| inversion_0.3 | video:window_mean_best | 5 | 2.2% | 0.0% | 0.0% | 0.0% |
| inversion_0.5 | long | 15 | 85.9% | 13.3% | 94.5% | 100.0% |
| inversion_0.5 | video:max_proj | 5 | 0.2% | 0.0% | 0.2% | 0.0% |
| inversion_0.5 | video:single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_0.5 | video:temporal_mean | 5 | 2.4% | 0.0% | 0.0% | 0.0% |
| inversion_0.5 | video:window_mean_best | 5 | 1.5% | 0.0% | 0.0% | 0.0% |
| inversion_1.0 | long | 15 | 68.5% | 40.0% | 59.7% | 80.0% |
| inversion_1.0 | video:max_proj | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_1.0 | video:single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_1.0 | video:temporal_mean | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| inversion_1.0 | video:window_mean_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| mask_noise | long | 36 | 84.7% | 19.4% | 85.8% | 91.7% |
| mask_noise | short | 36 | 0.3% | 0.0% | 0.0% | 0.0% |
| mask_noise | video:max_proj | 12 | 1.9% | 0.0% | 0.1% | 8.3% |
| mask_noise | video:single_best | 12 | 0.6% | 0.0% | 0.0% | 0.0% |
| mask_noise | video:temporal_mean | 12 | 1.2% | 0.0% | 0.0% | 0.0% |
| mask_noise | video:window_mean_best | 12 | 2.4% | 0.0% | 0.0% | 8.3% |
| mask_only | long | 36 | 78.6% | 19.4% | 92.0% | 83.3% |
| mask_only | short | 36 | 1.2% | 0.0% | 0.0% | 0.0% |
| mask_only | video:max_proj | 12 | 0.0% | 0.0% | 0.0% | 0.0% |
| mask_only | video:single_best | 12 | 1.6% | 0.0% | 0.0% | 0.0% |
| mask_only | video:temporal_mean | 12 | 0.4% | 0.0% | 0.0% | 0.0% |
| mask_only | video:window_mean_best | 12 | 0.9% | 0.0% | 0.0% | 0.0% |
| original | long | 36 | 54.5% | 8.3% | 51.5% | 58.3% |
| original | short | 36 | 78.1% | 61.1% | 79.8% | 83.3% |
| original | video:max_proj | 12 | 32.6% | 0.0% | 30.9% | 58.3% |
| original | video:single_best | 12 | 64.3% | 33.3% | 69.7% | 66.7% |
| original | video:temporal_mean | 12 | 22.8% | 0.0% | 18.5% | 33.3% |
| original | video:window_mean_best | 12 | 61.7% | 33.3% | 67.4% | 66.7% |
| stripe_0.00 | short | 15 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.00 | video:max_proj | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.00 | video:single_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.00 | video:temporal_mean | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.00 | video:window_mean_best | 5 | 2.8% | 0.0% | 0.0% | 0.0% |
| stripe_0.10 | short | 15 | 0.7% | 0.0% | 0.0% | 0.0% |
| stripe_0.10 | video:max_proj | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.10 | video:single_best | 5 | 2.4% | 0.0% | 0.0% | 0.0% |
| stripe_0.10 | video:temporal_mean | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.10 | video:window_mean_best | 5 | 3.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.18 | short | 15 | 1.4% | 0.0% | 0.0% | 0.0% |
| stripe_0.18 | video:max_proj | 5 | 0.6% | 0.0% | 0.2% | 0.0% |
| stripe_0.18 | video:single_best | 5 | 1.7% | 0.0% | 0.0% | 0.0% |
| stripe_0.18 | video:temporal_mean | 5 | 0.6% | 0.0% | 0.0% | 0.0% |
| stripe_0.18 | video:window_mean_best | 5 | 0.0% | 0.0% | 0.0% | 0.0% |
| stripe_0.30 | short | 15 | 0.1% | 0.0% | 0.3% | 0.0% |
| stripe_0.30 | video:max_proj | 5 | 0.3% | 0.0% | 0.0% | 0.0% |
| stripe_0.30 | video:single_best | 5 | 0.1% | 0.0% | 0.0% | 0.0% |
| stripe_0.30 | video:temporal_mean | 5 | 6.7% | 0.0% | 0.0% | 0.0% |
| stripe_0.30 | video:window_mean_best | 5 | 4.1% | 0.0% | 0.0% | 0.0% |
| vlm | long | 36 | 18.2% | 0.0% | 10.4% | 30.6% |
| vlm | short | 36 | 0.8% | 0.0% | 0.0% | 0.0% |
| vlm | video:max_proj | 12 | 1.6% | 0.0% | 0.0% | 0.0% |
| vlm | video:single_best | 12 | 1.3% | 0.0% | 0.0% | 0.0% |
| vlm | video:temporal_mean | 12 | 0.0% | 0.0% | 0.0% | 0.0% |
| vlm | video:window_mean_best | 12 | 5.1% | 0.0% | 0.1% | 8.3% |

## Protection Delta vs Unprotected Baseline (best-of-engine)

Recovery reduction relative to the `original` capture under the same attack (higher = stronger protection).

| Ablation | Attack | Char recovery drop | Exact match drop | Baseline char | Baseline exact |
|---|---|---:|---:|---:|---:|
| anti_ocr | long | -36.6% | -55.6% | 54.5% | 8.3% |
| anti_ocr | short | 77.3% | 61.1% | 78.1% | 61.1% |
| anti_ocr | video:max_proj | 32.5% | 0.0% | 32.6% | 0.0% |
| anti_ocr | video:single_best | 63.7% | 33.3% | 64.3% | 33.3% |
| anti_ocr | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| anti_ocr | video:window_mean_best | 60.7% | 33.3% | 61.7% | 33.3% |
| deployed | long | -31.1% | -36.1% | 54.5% | 8.3% |
| deployed | short | 78.1% | 61.1% | 78.1% | 61.1% |
| deployed | video:max_proj | 32.6% | 0.0% | 32.6% | 0.0% |
| deployed | video:single_best | 61.5% | 33.3% | 64.3% | 33.3% |
| deployed | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| deployed | video:window_mean_best | 59.6% | 33.3% | 61.7% | 33.3% |
| glyph_0.00 | short | 76.5% | 61.1% | 78.1% | 61.1% |
| glyph_0.00 | video:max_proj | 32.5% | 0.0% | 32.6% | 0.0% |
| glyph_0.00 | video:single_best | 64.3% | 33.3% | 64.3% | 33.3% |
| glyph_0.00 | video:temporal_mean | 18.4% | 0.0% | 22.8% | 0.0% |
| glyph_0.00 | video:window_mean_best | 61.7% | 33.3% | 61.7% | 33.3% |
| glyph_0.12 | short | 77.4% | 61.1% | 78.1% | 61.1% |
| glyph_0.12 | video:max_proj | 31.9% | 0.0% | 32.6% | 0.0% |
| glyph_0.12 | video:single_best | 62.8% | 33.3% | 64.3% | 33.3% |
| glyph_0.12 | video:temporal_mean | 21.1% | 0.0% | 22.8% | 0.0% |
| glyph_0.12 | video:window_mean_best | 61.7% | 33.3% | 61.7% | 33.3% |
| glyph_0.22 | short | 77.9% | 61.1% | 78.1% | 61.1% |
| glyph_0.22 | video:max_proj | 32.6% | 0.0% | 32.6% | 0.0% |
| glyph_0.22 | video:single_best | 64.3% | 33.3% | 64.3% | 33.3% |
| glyph_0.22 | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| glyph_0.22 | video:window_mean_best | 61.7% | 33.3% | 61.7% | 33.3% |
| inversion_0.0 | long | -24.7% | -11.7% | 54.5% | 8.3% |
| inversion_0.0 | video:max_proj | 31.4% | 0.0% | 32.6% | 0.0% |
| inversion_0.0 | video:single_best | 62.3% | 33.3% | 64.3% | 33.3% |
| inversion_0.0 | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| inversion_0.0 | video:window_mean_best | 58.5% | 33.3% | 61.7% | 33.3% |
| inversion_0.2 | long | -28.2% | -11.7% | 54.5% | 8.3% |
| inversion_0.2 | video:max_proj | 32.1% | 0.0% | 32.6% | 0.0% |
| inversion_0.2 | video:single_best | 64.3% | 33.3% | 64.3% | 33.3% |
| inversion_0.2 | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| inversion_0.2 | video:window_mean_best | 61.7% | 33.3% | 61.7% | 33.3% |
| inversion_0.3 | long | -30.2% | -11.7% | 54.5% | 8.3% |
| inversion_0.3 | video:max_proj | 32.5% | 0.0% | 32.6% | 0.0% |
| inversion_0.3 | video:single_best | 62.8% | 33.3% | 64.3% | 33.3% |
| inversion_0.3 | video:temporal_mean | 22.3% | 0.0% | 22.8% | 0.0% |
| inversion_0.3 | video:window_mean_best | 59.4% | 33.3% | 61.7% | 33.3% |
| inversion_0.5 | long | -31.5% | -5.0% | 54.5% | 8.3% |
| inversion_0.5 | video:max_proj | 32.4% | 0.0% | 32.6% | 0.0% |
| inversion_0.5 | video:single_best | 64.3% | 33.3% | 64.3% | 33.3% |
| inversion_0.5 | video:temporal_mean | 20.4% | 0.0% | 22.8% | 0.0% |
| inversion_0.5 | video:window_mean_best | 60.2% | 33.3% | 61.7% | 33.3% |
| inversion_1.0 | long | -14.0% | -31.7% | 54.5% | 8.3% |
| inversion_1.0 | video:max_proj | 32.6% | 0.0% | 32.6% | 0.0% |
| inversion_1.0 | video:single_best | 64.3% | 33.3% | 64.3% | 33.3% |
| inversion_1.0 | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| inversion_1.0 | video:window_mean_best | 61.7% | 33.3% | 61.7% | 33.3% |
| mask_noise | long | -30.3% | -11.1% | 54.5% | 8.3% |
| mask_noise | short | 77.8% | 61.1% | 78.1% | 61.1% |
| mask_noise | video:max_proj | 30.6% | 0.0% | 32.6% | 0.0% |
| mask_noise | video:single_best | 63.7% | 33.3% | 64.3% | 33.3% |
| mask_noise | video:temporal_mean | 21.6% | 0.0% | 22.8% | 0.0% |
| mask_noise | video:window_mean_best | 59.2% | 33.3% | 61.7% | 33.3% |
| mask_only | long | -24.1% | -11.1% | 54.5% | 8.3% |
| mask_only | short | 76.9% | 61.1% | 78.1% | 61.1% |
| mask_only | video:max_proj | 32.5% | 0.0% | 32.6% | 0.0% |
| mask_only | video:single_best | 62.7% | 33.3% | 64.3% | 33.3% |
| mask_only | video:temporal_mean | 22.4% | 0.0% | 22.8% | 0.0% |
| mask_only | video:window_mean_best | 60.7% | 33.3% | 61.7% | 33.3% |
| original | long | 0.0% | 0.0% | 54.5% | 8.3% |
| original | short | 0.0% | 0.0% | 78.1% | 61.1% |
| original | video:max_proj | 0.0% | 0.0% | 32.6% | 0.0% |
| original | video:single_best | 0.0% | 0.0% | 64.3% | 33.3% |
| original | video:temporal_mean | 0.0% | 0.0% | 22.8% | 0.0% |
| original | video:window_mean_best | 0.0% | 0.0% | 61.7% | 33.3% |
| stripe_0.00 | short | 78.1% | 61.1% | 78.1% | 61.1% |
| stripe_0.00 | video:max_proj | 32.6% | 0.0% | 32.6% | 0.0% |
| stripe_0.00 | video:single_best | 64.3% | 33.3% | 64.3% | 33.3% |
| stripe_0.00 | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| stripe_0.00 | video:window_mean_best | 58.8% | 33.3% | 61.7% | 33.3% |
| stripe_0.10 | short | 77.3% | 61.1% | 78.1% | 61.1% |
| stripe_0.10 | video:max_proj | 32.6% | 0.0% | 32.6% | 0.0% |
| stripe_0.10 | video:single_best | 61.9% | 33.3% | 64.3% | 33.3% |
| stripe_0.10 | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| stripe_0.10 | video:window_mean_best | 58.7% | 33.3% | 61.7% | 33.3% |
| stripe_0.18 | short | 76.6% | 61.1% | 78.1% | 61.1% |
| stripe_0.18 | video:max_proj | 32.0% | 0.0% | 32.6% | 0.0% |
| stripe_0.18 | video:single_best | 62.6% | 33.3% | 64.3% | 33.3% |
| stripe_0.18 | video:temporal_mean | 22.3% | 0.0% | 22.8% | 0.0% |
| stripe_0.18 | video:window_mean_best | 61.7% | 33.3% | 61.7% | 33.3% |
| stripe_0.30 | short | 78.0% | 61.1% | 78.1% | 61.1% |
| stripe_0.30 | video:max_proj | 32.3% | 0.0% | 32.6% | 0.0% |
| stripe_0.30 | video:single_best | 64.1% | 33.3% | 64.3% | 33.3% |
| stripe_0.30 | video:temporal_mean | 16.1% | 0.0% | 22.8% | 0.0% |
| stripe_0.30 | video:window_mean_best | 57.5% | 33.3% | 61.7% | 33.3% |
| vlm | long | 36.3% | 8.3% | 54.5% | 8.3% |
| vlm | short | 77.3% | 61.1% | 78.1% | 61.1% |
| vlm | video:max_proj | 31.0% | 0.0% | 32.6% | 0.0% |
| vlm | video:single_best | 63.0% | 33.3% | 64.3% | 33.3% |
| vlm | video:temporal_mean | 22.8% | 0.0% | 22.8% | 0.0% |
| vlm | video:window_mean_best | 56.5% | 33.3% | 61.7% | 33.3% |
