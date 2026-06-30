# Publication Result Summary

This file is generated from machine-readable experiment JSON artifacts.

## Source Files

- ocr: `corpus_multi_engine.json`
- strong_camera: `corpus_strong_camera_attack.json`
- detection: `detection_attack_yolo.json`
- coco_detection: `coco_detection_attack.json`
- mot_video_detection: `mot_video_detection.json`
- mot_tracking: `mot_tracking_attack.json`
- view_attack: `view_attack.json`
- vlm: `vlm_qwen3_siliconflow.json`
- real_capture: `real_capture_ocr.json`
- real_capture_coco_detection: `real_capture_coco_detection.json`
- real_capture_mot_detection: `real_capture_mot_detection.json`
- real_capture_mot_tracking: `real_capture_mot_tracking.json`
- component_ablation: `component_ablation.json`
- recognizer_generalization: `recognizer_generalization.json`
- perceptual_ablation: `perceptual_ablation.json`
- pareto_sweep: `pareto_sweep.json`
- strong_attack_extra: `strong_attack_extra.json`
- adaptive_attack_ablation: `adaptive_attack_ablation.json`
- camera_pipeline_ablation: `camera_pipeline_ablation.json`
- screen_privacy_baselines: `screen_privacy_baselines.json`
- vlm_prompt_ablation: `vlm_prompt_ablation.json`
- noise_epsilon_sweep: `noise_epsilon_sweep.json`
- vlm_model_ablation: `vlm_model_ablation.json`
- brightness_compensation_ablation: `brightness_compensation_ablation.json`
- mask_granularity_ablation: `mask_granularity_ablation.json`
- anti_ocr_profile_ablation: `anti_ocr_profile_ablation.json`
- seed_sensitivity: `seed_sensitivity.json`
- usability_pilot: `missing`

## OCR Corpus

| Engine | Samples | Original char acc | Subframe char acc | Paired reduction | Subframe word/exact/sensitive |
|---|---:|---:|---:|---:|---:|
| tesseract | 120 | 94.0% (92.3%-95.5%) | 0.0% (0.0%-0.1%) | 93.9% (92.3%-95.5%) | 0.0% / 0.0% / 0.0% |
| easyocr | 120 | 94.1% (92.7%-95.5%) | 0.0% (0.0%-0.0%) | 94.1% (92.7%-95.5%) | 0.0% / 0.0% / 0.0% |
| paddleocr | 120 | 94.9% (93.7%-96.2%) | 0.0% (0.0%-0.0%) | 94.9% (93.7%-96.2%) | 0.0% / 0.0% / 0.0% |

## Stratified OCR Defense

Primary engine: `tesseract`

### By category

| Value | Rows | Original char acc | Subframe char acc | Reduction |
|---|---:|---:|---:|---:|
| code | 10 | 92.4% (89.3%-95.3%) | 0.1% (0.0%-0.3%) | 92.3% |
| financial | 10 | 96.3% (95.4%-97.1%) | 0.0% (0.0%-0.0%) | 96.3% |
| mixed_credentials | 10 | 93.7% (89.2%-98.1%) | 0.0% (0.0%-0.0%) | 93.7% |
| numbers | 10 | 99.3% (98.2%-100.0%) | 0.2% (0.0%-0.7%) | 99.0% |
| paragraph | 20 | 90.4% (85.4%-94.8%) | 0.0% (0.0%-0.1%) | 90.4% |
| sentence | 20 | 95.6% (91.5%-99.2%) | 0.0% (0.0%-0.0%) | 95.6% |
| short_secret | 20 | 99.6% (98.8%-100.0%) | 0.0% (0.0%-0.0%) | 99.6% |
| table | 10 | 75.7% (73.3%-77.9%) | 0.0% (0.0%-0.0%) | 75.7% |
| url_token | 10 | 99.2% (98.3%-100.0%) | 0.0% (0.0%-0.0%) | 99.2% |

### By language

| Value | Rows | Original char acc | Subframe char acc | Reduction |
|---|---:|---:|---:|---:|
| code | 10 | 92.4% (89.3%-95.3%) | 0.1% (0.0%-0.3%) | 92.3% |
| en | 40 | 93.3% (89.9%-96.3%) | 0.0% (0.0%-0.1%) | 93.2% |
| mixed | 10 | 93.7% (89.2%-98.1%) | 0.0% (0.0%-0.0%) | 93.7% |
| symbol | 30 | 98.2% (97.6%-98.9%) | 0.1% (0.0%-0.2%) | 98.2% |
| zh | 30 | 91.3% (87.1%-95.1%) | 0.0% (0.0%-0.0%) | 91.3% |

### By layout

| Value | Rows | Original char acc | Subframe char acc | Reduction |
|---|---:|---:|---:|---:|
| multi | 50 | 89.0% (86.1%-91.7%) | 0.0% (0.0%-0.1%) | 89.0% |
| single | 70 | 97.5% (96.0%-98.8%) | 0.0% (0.0%-0.1%) | 97.5% |

### By font_size

| Value | Rows | Original char acc | Subframe char acc | Reduction |
|---|---:|---:|---:|---:|
| 17 | 4 | 87.5% (78.6%-96.4%) | 0.0% (0.0%-0.0%) | 87.5% |
| 18 | 2 | 86.5% (86.1%-87.0%) | 0.0% (0.0%-0.0%) | 86.5% |
| 19 | 8 | 90.5% (82.2%-97.3%) | 0.0% (0.0%-0.0%) | 90.5% |
| 20 | 2 | 86.5% (86.1%-87.0%) | 0.0% (0.0%-0.0%) | 86.5% |
| 21 | 10 | 90.8% (83.7%-96.7%) | 0.0% (0.0%-0.0%) | 90.8% |
| 22 | 2 | 94.5% (93.1%-95.8%) | 0.0% (0.0%-0.0%) | 94.5% |
| 23 | 14 | 92.6% (87.3%-97.5%) | 0.1% (0.0%-0.2%) | 92.5% |
| 24 | 2 | 97.1% (96.4%-97.8%) | 0.4% (0.0%-0.9%) | 96.7% |
| 25 | 16 | 90.8% (86.6%-94.9%) | 0.0% (0.0%-0.0%) | 90.8% |
| 26 | 2 | 97.2% (96.5%-97.9%) | 0.0% (0.0%-0.0%) | 97.2% |
| 27 | 12 | 89.7% (82.0%-97.1%) | 0.0% (0.0%-0.0%) | 89.7% |
| 29 | 10 | 98.6% (97.5%-99.7%) | 0.0% (0.0%-0.0%) | 98.6% |
| 30 | 4 | 100.0% (100.0%-100.0%) | 0.0% (0.0%-0.0%) | 100.0% |
| 31 | 8 | 95.7% (91.2%-99.2%) | 0.0% (0.0%-0.0%) | 95.7% |
| 32 | 4 | 100.0% (100.0%-100.0%) | 0.0% (0.0%-0.0%) | 100.0% |
| 33 | 4 | 100.0% (100.0%-100.0%) | 0.6% (0.0%-1.8%) | 99.4% |
| 34 | 4 | 98.1% (94.2%-100.0%) | 0.0% (0.0%-0.0%) | 98.1% |
| 35 | 2 | 100.0% (100.0%-100.0%) | 0.0% (0.0%-0.0%) | 100.0% |
| 36 | 4 | 100.0% (100.0%-100.0%) | 0.0% (0.0%-0.0%) | 100.0% |
| 37 | 2 | 100.0% (100.0%-100.0%) | 0.0% (0.0%-0.0%) | 100.0% |
| 38 | 4 | 100.0% (100.0%-100.0%) | 0.0% (0.0%-0.0%) | 100.0% |

## Strong Camera Attacks

| Attack | Char recovery | Exact match | Sensitive token recall | Leak rate char>=20% |
|---|---:|---:|---:|---:|
| global_shutter_slot0 | 0.0% (0.0%-0.0%) | 0.0% | 0.0% | 0.0% |
| differential_luma | 0.0% (0.0%-0.0%) | 0.0% | 0.0% | 0.0% |
| differential_blue | 0.0% (0.0%-0.0%) | 0.0% | 0.0% | 0.0% |
| temporal_average_cycle | 94.3% (92.6%-95.9%) | 85.8% | 98.4% | 100.0% |
| phase_search_mean | 94.2% (92.3%-95.8%) | 87.5% | 97.2% | 100.0% |
| phase_search_max | 94.3% (92.7%-95.8%) | 85.8% | 96.4% | 100.0% |
| blue_channel_max | 95.0% (93.5%-96.3%) | 90.0% | 98.3% | 100.0% |
| **best_attack_per_sample** | **95.2% (93.8%-96.5%)** | **91.7%** | **98.6%** | **100.0%** |

## Detection Attack

- Engine: `ultralytics-yolo` / `yolov8n.pt`
- Single subframe mAP50: 40.0%; recall: 40.0%
- Temporal average mAP50: 100.0%; recall: 100.0%

## COCO Detection Suite

| Model | Attack | mAP | mAP50 | mAP75 | AP_S | AP_M | AP_L | AR | Images |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| yolo26x | clean | 48.1% | 58.3% | 55.7% | 29.8% | 70.4% | 83.1% | 51.0% | 8 |
| yolo26x | single_subframe | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 8 |
| yolo26x | temporal_average | 14.3% | 18.3% | 15.7% | 3.1% | 23.3% | 36.4% | 14.3% | 8 |
| rtdetr-x | clean | 47.1% | 58.7% | 55.9% | 27.5% | 80.4% | 83.1% | 53.4% | 8 |
| rtdetr-x | single_subframe | 5.2% | 6.0% | 5.8% | 0.0% | 7.9% | 17.9% | 5.2% | 8 |
| rtdetr-x | temporal_average | 16.8% | 23.7% | 19.6% | 6.3% | 23.8% | 49.4% | 17.9% | 8 |
| faster_rcnn | clean | 38.2% | 52.7% | 45.4% | 23.6% | 62.3% | 73.2% | 43.6% | 8 |
| faster_rcnn | single_subframe | 3.0% | 4.4% | 4.2% | 0.0% | 5.5% | 4.7% | 3.0% | 8 |
| faster_rcnn | temporal_average | 11.1% | 16.5% | 11.7% | 2.9% | 15.6% | 26.4% | 11.1% | 8 |
| retinanet | clean | 33.2% | 47.1% | 35.5% | 16.7% | 60.7% | 63.1% | 35.3% | 8 |
| retinanet | single_subframe | 3.3% | 4.2% | 4.2% | 0.0% | 6.0% | 0.2% | 3.3% | 8 |
| retinanet | temporal_average | 9.6% | 13.2% | 11.5% | 2.3% | 14.2% | 20.7% | 9.6% | 8 |

## MOT17 Video Detection

| Model | Attack | mAP | mAP50 | Recall | Precision | Frames |
|---|---|---:|---:|---:|---:|---:|
| yolo26x | clean | 24.3% | 41.2% | 44.3% | 81.6% | 5316 |
| yolo26x | single_subframe | 0.0% | 0.1% | 0.1% | 97.7% | 5316 |
| yolo26x | temporal_average | 8.4% | 15.6% | 17.1% | 73.4% | 5316 |
| rtdetr-x | clean | 30.7% | 54.8% | 61.2% | 64.8% | 5316 |
| rtdetr-x | single_subframe | 3.7% | 8.6% | 10.2% | 49.4% | 5316 |
| rtdetr-x | temporal_average | 9.7% | 19.9% | 23.3% | 42.1% | 5316 |
| faster_rcnn | clean | 33.9% | 62.1% | 69.5% | 53.2% | 5316 |
| faster_rcnn | single_subframe | 2.6% | 7.0% | 8.2% | 48.1% | 5316 |
| faster_rcnn | temporal_average | 7.6% | 16.7% | 19.5% | 49.2% | 5316 |
| retinanet | clean | 31.7% | 60.0% | 68.0% | 50.2% | 5316 |
| retinanet | single_subframe | 1.5% | 4.2% | 5.2% | 60.4% | 5316 |
| retinanet | temporal_average | 6.7% | 14.6% | 17.2% | 48.9% | 5316 |

## MOT17 Tracking

Tracker: `greedy_bytetrack_fallback`

| Model | Attack | MOTA | MOTP | IDF1 | HOTA | Frames |
|---|---|---:|---:|---:|---:|---:|
| yolo26x | clean | 31.1% | 81.7% | 27.1% | n/a | 5316 |
| yolo26x | single_subframe | 0.1% | 74.8% | 0.1% | n/a | 5316 |
| yolo26x | temporal_average | 9.1% | 78.1% | 12.0% | n/a | 5316 |
| rtdetr-x | clean | 24.1% | 79.8% | 38.2% | n/a | 5316 |
| rtdetr-x | single_subframe | -2.3% | 73.2% | 5.4% | n/a | 5316 |
| rtdetr-x | temporal_average | -11.4% | 75.0% | 14.7% | n/a | 5316 |
| faster_rcnn | clean | 3.8% | 77.9% | 35.6% | n/a | 5316 |
| faster_rcnn | single_subframe | -2.5% | 71.2% | 4.5% | n/a | 5316 |
| faster_rcnn | temporal_average | -2.7% | 73.2% | 14.0% | n/a | 5316 |
| retinanet | clean | -5.4% | 77.1% | 30.5% | n/a | 5316 |
| retinanet | single_subframe | 0.4% | 70.6% | 2.7% | n/a | 5316 |
| retinanet | temporal_average | -2.9% | 73.8% | 11.9% | n/a | 5316 |

## Real-Device Capture (COCO/MOT)

Privacy content shown on a 240Hz screen and photographed with a USB webcam; `real_clean` is the captured unprotected baseline, so the gap to `real_short` (single-frame) / `real_video` (temporal mean) isolates the privacy effect.
MOT17 rows are stop-motion physical-frame validation: each dataset frame is displayed as a static stimulus before capture, so they should not be described as continuous video playback results.

### COCO Real Capture

| Model | Attack | mAP | mAP50 | mAP75 | AP_S | AP_M | AP_L | AR | Images |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| yolo26x | real_clean | 28.6% | 43.9% | 31.4% | 2.4% | 32.5% | 58.0% | 31.0% | 150 |
| yolo26x | real_short | 1.3% | 2.4% | 1.0% | 0.0% | 1.3% | 5.2% | 1.4% | 150 |
| yolo26x | real_video | 3.5% | 5.3% | 4.4% | 0.0% | 2.7% | 9.0% | 3.6% | 150 |
| rtdetr-x | real_clean | 30.1% | 50.2% | 31.8% | 3.6% | 36.4% | 61.0% | 34.8% | 150 |
| rtdetr-x | real_short | 3.5% | 5.8% | 3.2% | 0.0% | 2.9% | 10.7% | 4.1% | 150 |
| rtdetr-x | real_video | 4.6% | 7.3% | 5.2% | 0.1% | 2.9% | 15.4% | 5.5% | 150 |
| faster_rcnn | real_clean | 21.3% | 39.2% | 22.0% | 2.7% | 26.2% | 42.5% | 28.7% | 150 |
| faster_rcnn | real_short | 0.8% | 1.6% | 0.7% | 0.0% | 0.3% | 2.1% | 0.9% | 150 |
| faster_rcnn | real_video | 1.5% | 3.0% | 1.4% | 0.0% | 0.7% | 4.5% | 1.8% | 150 |
| retinanet | real_clean | 22.6% | 39.4% | 22.9% | 3.5% | 23.7% | 46.0% | 27.0% | 150 |
| retinanet | real_short | 0.9% | 1.8% | 0.6% | 0.0% | 0.3% | 1.8% | 1.0% | 150 |
| retinanet | real_video | 1.9% | 3.1% | 2.2% | 0.0% | 0.6% | 5.4% | 2.0% | 150 |

### MOT17 Real Capture — Detection

| Model | Attack | mAP | mAP50 | Recall | Precision | Frames |
|---|---|---:|---:|---:|---:|---:|
| yolo26x | real_clean | 1.2% | 8.3% | 19.5% | 19.0% | 450 |
| yolo26x | real_short | 0.7% | 3.7% | 11.5% | 19.7% | 450 |
| yolo26x | real_video | 0.6% | 3.9% | 12.5% | 22.3% | 450 |
| rtdetr-x | real_clean | 1.3% | 7.5% | 21.3% | 14.2% | 450 |
| rtdetr-x | real_short | 0.7% | 4.3% | 13.5% | 11.0% | 450 |
| rtdetr-x | real_video | 0.8% | 4.3% | 14.3% | 12.3% | 450 |
| faster_rcnn | real_clean | 1.1% | 7.3% | 22.1% | 12.7% | 450 |
| faster_rcnn | real_short | 0.6% | 3.2% | 10.2% | 20.6% | 450 |
| faster_rcnn | real_video | 0.7% | 3.7% | 13.2% | 17.6% | 450 |
| retinanet | real_clean | 1.4% | 8.0% | 26.5% | 16.1% | 450 |
| retinanet | real_short | 0.4% | 2.1% | 8.5% | 19.9% | 450 |
| retinanet | real_video | 0.7% | 3.5% | 11.0% | 20.5% | 450 |

### MOT17 Real Capture — Tracking

| Model | Attack | MOTA | MOTP | IDF1 | HOTA | Frames |
|---|---|---:|---:|---:|---:|---:|
| yolo26x | real_clean | -65.0% | 58.4% | 12.1% | 15.8% | 450 |
| yolo26x | real_short | -37.2% | 60.6% | 6.5% | 8.7% | 450 |
| yolo26x | real_video | -32.8% | 59.9% | 8.7% | 10.0% | 450 |
| rtdetr-x | real_clean | -109.5% | 58.9% | 10.4% | 14.2% | 450 |
| rtdetr-x | real_short | -99.4% | 60.5% | 5.2% | 8.1% | 450 |
| rtdetr-x | real_video | -90.5% | 60.6% | 6.8% | 9.6% | 450 |
| faster_rcnn | real_clean | -133.5% | 59.0% | 9.6% | 14.4% | 450 |
| faster_rcnn | real_short | -32.8% | 60.1% | 6.0% | 6.8% | 450 |
| faster_rcnn | real_video | -51.7% | 60.8% | 7.1% | 10.5% | 450 |
| retinanet | real_clean | -118.2% | 60.1% | 9.8% | 14.2% | 450 |
| retinanet | real_short | -28.9% | 61.2% | 4.4% | 5.1% | 450 |
| retinanet | real_video | -34.3% | 61.3% | 5.9% | 6.8% | 450 |

## View Attack

- Angle: 35.0 degrees
- Frontal/off-axis/corrected OCR: 100.0% / 100.0% / 100.0%
- Off-axis SSIM drop: 0.064

## VLM Readability

- Model: `Qwen/Qwen3-VL-32B-Instruct`
- Best attack char recovery: 96.3%
- Best attack read success rate: 100.0%

## Multi-VLM Cross-Attack Recovery

Verbatim recovery (exact line-match rate) per VLM family and attack frame.

| Attack frame | Qwen3-VL-32B-Instruct | Kimi-K2.6 | GLM-4.5V |
|---|---:|---:|---:|
| original | 100.0% | 77.8% | 100.0% |
| global_shutter_slot0 | 0.0% | 0.0% | 0.0% |
| temporal_average_cycle | 92.6% | 74.1% | 100.0% |
| phase_search_max | 100.0% | 74.1% | 100.0% |

## Real Camera Capture

- Captures: 10575
- Positions: 9

### Position Matrix

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

## n vs Security / Usability

| n | Single-frame OCR | Full-cycle OCR | Single-frame MI | FPI @ refresh |
|---:|---:|---:|---:|---|
| 2 | 0.0% | 94.3% | 0.566 | 144Hz:0.0139✓, 240Hz:0.0050✓, 360Hz:0.0022✓ |
| 4 | 0.0% | 94.5% | 0.377 | 144Hz:0.3000✗, 240Hz:0.0300✓, 360Hz:0.0133✓ |
| 6 | 0.0% | 94.2% | 0.249 | 144Hz:0.5000✗, 240Hz:0.2778✗, 360Hz:0.0333✓ |
| 8 | 0.0% | 94.5% | 0.217 | 144Hz:0.6125✗, 240Hz:0.4375✗, 360Hz:0.2188✗ |

Recommended: n=6 @ 360.0Hz (FPI 0.0333, single-frame MI 0.249)

## Supplemental Ablations

| Experiment | Status | Highlight |
|---|---|---|
| component_ablation | available | baseline: char recovery 94.0% (92.3%-95.6%), leak 0.0%, errors 0 |
| recognizer_generalization | available | tesseract/original: char recovery 94.0% (92.3%-95.6%), exact 84.2% (77.5%-90.8%), leak 100.0%, errors 0 |
| perceptual_ablation | available | rgb_full: char recovery 0.0% (0.0%-0.1%), leak 0.0%, errors 0 |
| pareto_sweep | available | recommended n=6 @ 360.0Hz, FPI 0.0333, MI 0.249 |
| strong_attack_extra | available | single_subframe: char recovery 0.0% (0.0%-0.0%), exact 0.0% (0.0%-0.0%), leak 0.0%, errors 0 |
| adaptive_attack_ablation | available | raw_subframe: char recovery 0.2% (0.0%-0.4%), exact 0.0% (0.0%-0.0%), leak 0.0%, errors 0 |
| camera_pipeline_ablation | available | clean_subframe: char recovery 0.1% (0.0%-0.2%), exact 0.0% (0.0%-0.0%), leak 0.0%, errors 0 |
| screen_privacy_baselines | available | unprotected: char recovery 92.9% (87.8%-97.2%), exact 66.7% (33.3%-88.9%), leak 100.0%, errors 0 |
| vlm_prompt_ablation | available | strict_transcription: char recovery 72.7% (58.1%-85.6%), exact 75.0% (61.1%-88.9%), leak 0.0%, errors 0 |
| noise_epsilon_sweep | available | eps_0.0000: char recovery 0.0% (0.0%-0.0%), leak 0.0%, errors 0 |
| vlm_model_ablation | available | Qwen/Qwen3-VL-32B-Instruct: char recovery 96.3% (92.5%-99.2%), leak 0.0%, errors 1 |
| brightness_compensation_ablation | available | gamma_1.00: char recovery 0.0% (0.0%-0.1%), leak 0.0%, errors 0 |
| mask_granularity_ablation | available | block_1: char recovery 0.0% (0.0%-0.1%), leak 0.0%, errors 0 |
| anti_ocr_profile_ablation | available | block1/off: temporal_average 93.0% (88.4%-96.9%), exact 81.2% (62.5%-100.0%), worst-case char 93.0%, inv-frame char 0.0%, leak 0.0%, errors 0 |
| seed_sensitivity | available | single_frame_ocr: char recovery 0.0% (0.0%-0.1%), leak 0.0%, errors 0 |
| usability_pilot | missing | `usability_pilot.json` |

### Supplemental Ablation Detail


#### component_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline |  | 94.0% (92.3%-95.6%) |  |  |  | 0.0% | 0 |
| single_mask_only |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| single_mask_noise |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| inpaint_mask_only |  | 50.9% (44.7%-56.8%) |  |  |  | 0.0% | 0 |
| inpaint_noise_pedestal |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| inpaint_noise_no_pedestal |  | 9.6% (4.9%-14.7%) |  |  |  | 0.0% | 0 |
| long_exposure_no_inv |  | 94.3% (92.7%-95.9%) |  |  |  | 0.0% | 0 |
| long_exposure_with_inv |  | 0.0% (0.0%-0.0%) |  |  |  | 0.0% | 0 |
| ae_real_subframe_no_black |  | 0.1% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| ae_real_subframe_with_black |  | 0.0% (0.0%-0.0%) |  |  |  | 0.0% | 0 |
| weak_mask_only |  | 32.2% (24.2%-40.4%) |  |  |  | 0.0% | 0 |
| weak_mask_noise |  | 26.8% (22.5%-31.1%) |  |  |  | 0.0% | 0 |

#### recognizer_generalization

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| tesseract/original |  | 94.0% (92.3%-95.6%) | 84.2% (77.5%-90.8%) |  |  | 100.0% | 0 |
| tesseract/single_subframe |  | 0.0% (0.0%-0.1%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| tesseract/temporal_average_cycle |  | 94.3% (92.6%-95.9%) | 87.5% (81.7%-92.5%) |  |  | 100.0% | 0 |
| tesseract/phase_search_max |  | 94.2% (92.4%-95.8%) | 85.8% (79.2%-91.7%) |  |  | 100.0% | 0 |
| tesseract/blue_channel_max |  | 94.6% (93.0%-96.0%) | 87.5% (81.7%-93.3%) |  |  | 100.0% | 0 |

#### perceptual_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| rgb_full |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| blue_residual_0.5 |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| blue_kept |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| green_kept |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |

#### strong_attack_extra

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| single_subframe |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| rolling_shutter_single |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| rolling_shutter_row_alignment |  | 92.9% (87.8%-97.2%) | 66.7% (33.3%-88.9%) |  |  | 100.0% | 0 |
| temporal_superresolution |  | 91.4% (85.3%-96.6%) | 55.6% (22.2%-88.9%) |  |  | 100.0% | 0 |

#### adaptive_attack_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| raw_subframe |  | 0.2% (0.0%-0.4%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| otsu_binarize |  | 0.1% (0.0%-0.2%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| adaptive_threshold |  | 0.0% (0.0%-0.1%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| clahe_luma |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| unsharp_mask |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| denoise |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| upscale_2x |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |

#### camera_pipeline_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| clean_subframe |  | 0.1% (0.0%-0.2%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| jpeg_q50 |  | 0.0% (0.0%-0.1%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| sensor_noise_iso_high |  | 0.1% (0.0%-0.3%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| motion_blur |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| digital_zoom_2x |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| auto_contrast |  | 0.1% (0.0%-0.3%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| rolling_shutter_single |  | 0.1% (0.0%-0.2%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| temporal_average_boundary |  | 94.4% (92.7%-96.0%) | 85.8% (79.2%-91.7%) |  |  | 100.0% | 0 |

#### screen_privacy_baselines

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| unprotected |  | 92.9% (87.8%-97.2%) | 66.7% (33.3%-88.9%) |  |  | 100.0% | 0 |
| dim_50pct |  | 92.9% (87.8%-97.2%) | 66.7% (33.3%-88.9%) |  |  | 100.0% | 0 |
| gaussian_blur |  | 52.6% (30.2%-74.5%) | 11.1% (0.0%-33.3%) |  |  | 77.8% | 0 |
| pixelate_12px |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| privacy_filter_offaxis_proxy |  | 84.7% (64.1%-96.8%) | 44.4% (11.1%-77.8%) |  |  | 88.9% | 0 |
| temporal_mask_single_subframe |  | 0.0% (0.0%-0.0%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |

#### vlm_prompt_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| strict_transcription |  | 72.7% (58.1%-85.6%) | 75.0% (61.1%-88.9%) |  |  | 0.0% | 0 |
| relaxed_readability |  | 72.7% (58.1%-85.6%) | 75.0% (61.1%-88.9%) |  |  | 0.0% | 0 |
| sensitive_field_extraction |  | 72.8% (58.2%-85.8%) | 75.0% (61.1%-88.9%) |  |  | 0.0% | 0 |

#### noise_epsilon_sweep

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| eps_0.0000 |  | 0.0% (0.0%-0.0%) |  |  |  | 0.0% | 0 |
| eps_0.0078 |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| eps_0.0157 |  | 0.1% (0.0%-0.3%) |  |  |  | 0.0% | 0 |
| eps_0.0314 |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| eps_0.0627 |  | 0.1% (0.0%-0.3%) |  |  |  | 0.0% | 0 |
| eps_0.1255 |  | 0.0% (0.0%-0.0%) |  |  |  | 0.0% | 0 |
| eps_0.2510 |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| eps_0.3765 |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |

#### vlm_model_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3-VL-32B-Instruct |  | 96.3% (92.5%-99.2%) |  |  |  | 0.0% | 1 |
| Pro/moonshotai/Kimi-K2.6 |  | 96.0% (93.1%-98.2%) |  |  |  | 0.0% | 2 |
| zai-org/GLM-4.5V |  | 93.2% (84.9%-98.7%) |  |  |  | 0.0% | 0 |

#### brightness_compensation_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| gamma_1.00 |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| gamma_2.00 |  | 0.1% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| gamma_4.00 |  | 0.1% (0.0%-0.1%) |  |  |  | 0.0% | 0 |

#### mask_granularity_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| block_1 |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
| block_2 |  | 0.0% (0.0%-0.0%) |  |  |  | 0.0% | 0 |
| block_4 |  | 0.1% (0.0%-0.2%) |  |  |  | 0.0% | 0 |
| block_8 |  | 0.8% (0.5%-1.2%) |  |  |  | 0.0% | 0 |

#### anti_ocr_profile_ablation

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| block1/off | temporal_average | 93.0% (88.4%-96.9%) | 81.2% (62.5%-100.0%) | 93.0% | 0.0% | 0.0% | 0 |
| block1/strong@overlay | temporal_average | 90.1% (84.5%-94.8%) | 43.8% (18.8%-62.7%) | 92.5% | 0.0% | 0.0% | 0 |
| block1/strong@deployed | temporal_average | 87.9% (80.8%-93.8%) | 50.0% (25.0%-75.0%) | 94.0% | 93.0% | 0.0% | 0 |
| block1/vlm | temporal_average | 49.1% (30.4%-66.6%) | 6.2% (0.0%-18.8%) | 49.1% | 0.0% | 0.0% | 0 |
| block2/s0.00_g0.00 | temporal_average | 93.0% (88.4%-96.9%) | 81.2% (62.5%-100.0%) |  |  | 0.0% | 0 |
| block2/s0.10_g0.12 | temporal_average | 90.1% (84.5%-94.8%) | 43.8% (18.8%-62.7%) |  |  | 0.0% | 0 |
| block2/s0.18_g0.22 | temporal_average | 82.4% (74.6%-88.7%) | 6.2% (0.0%-18.8%) |  |  | 0.0% | 0 |
| block2/s0.30_g0.22 | temporal_average | 10.7% (0.0%-23.3%) | 0.0% (0.0%-0.0%) |  |  | 0.0% | 0 |
| block3/alpha_0.0 | long_exposure | 92.0% (87.2%-96.0%) | 68.8% (43.8%-87.5%) |  | 0.0% | 0.0% | 0 |
| block3/alpha_0.2 | long_exposure | 88.2% (82.4%-93.6%) | 31.2% (12.5%-56.2%) |  | 93.0% | 0.0% | 0 |
| block3/alpha_0.5 | long_exposure | 79.1% (72.1%-85.3%) | 6.2% (0.0%-18.8%) |  | 93.0% | 0.0% | 0 |
| block3/alpha_1.0 | long_exposure | 57.0% (36.5%-75.0%) | 6.2% (0.0%-18.8%) |  | 93.0% | 0.0% | 0 |

#### seed_sensitivity

| Condition | Metric | Char recovery | Exact match | Worst-case char | Inv-frame char | Leak rate char>=20% | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| single_frame_ocr |  | 0.0% (0.0%-0.1%) |  |  |  | 0.0% | 0 |
