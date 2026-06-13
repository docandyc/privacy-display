# Publication Result Summary

This file is generated from machine-readable experiment JSON artifacts.

## Source Files

- ocr: `corpus_multi_engine.json`
- strong_camera: `corpus_strong_camera_attack.json`
- detection: `detection_attack_yolo.json`
- view_attack: `view_attack.json`
- vlm: `vlm_qwen3_siliconflow.json`
- real_capture: `missing`

## OCR Corpus

| Engine | Samples | Original char acc | Subframe char acc | Paired reduction | Subframe word/exact/sensitive |
|---|---:|---:|---:|---:|---:|
| tesseract | 120 | 94.0% (92.3%-95.5%) | 0.0% (0.0%-0.1%) | 93.9% (92.3%-95.5%) | 0.0% / 0.0% / 0.0% |
| easyocr | 120 | 94.1% (92.7%-95.5%) | 0.0% (0.0%-0.0%) | 94.1% (92.7%-95.5%) | 0.0% / 0.0% / 0.0% |
| paddleocr | 120 | 94.9% (93.7%-96.2%) | 0.0% (0.0%-0.0%) | 94.9% (93.7%-96.2%) | 0.0% / 0.0% / 0.0% |

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

## View Attack

- Angle: 35.0 degrees
- Frontal/off-axis/corrected OCR: 100.0% / 100.0% / 100.0%
- Off-axis SSIM drop: 0.064

## VLM Readability

- Not available: VLM result file exists, but all live API calls failed; do not cite recovery metrics.

## Real Camera Capture

- Not available: Real camera capture analysis is implemented, but no real photo/video-frame result has been generated.
