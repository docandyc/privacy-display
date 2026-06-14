# Publication Result Summary

This file is generated from machine-readable experiment JSON artifacts.

## Source Files

- ocr: `corpus_multi_engine.json`
- strong_camera: `corpus_strong_camera_attack.json`
- detection: `detection_attack_yolo.json`
- view_attack: `view_attack.json`
- vlm: `vlm_qwen3_siliconflow.json`
- real_capture: `missing`
- component_ablation: `component_ablation.json`
- recognizer_generalization: `recognizer_generalization.json`
- perceptual_ablation: `perceptual_ablation.json`
- pareto_sweep: `pareto_sweep.json`
- strong_attack_extra: `strong_attack_extra.json`
- adaptive_attack_ablation: `adaptive_attack_ablation.json`
- camera_pipeline_ablation: `camera_pipeline_ablation.json`
- screen_privacy_baselines: `screen_privacy_baselines.json`
- vlm_prompt_ablation: `vlm_prompt_ablation.json`
- usability_pilot: `missing`

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

- Model: `Qwen/Qwen3-VL-32B-Instruct`
- Best attack char recovery: 96.3%
- Best attack read success rate: 100.0%

## Real Camera Capture

- Not available: Real camera capture analysis is implemented, but no real photo/video-frame result has been generated.

## Supplemental Ablations

| Experiment | Status | Highlight |
|---|---|---|
| component_ablation | available | baseline: char recovery 92.9%, leak 0.0%, errors 0 |
| recognizer_generalization | available | tesseract/original: char recovery 92.9%, leak 100.0%, errors 0 |
| perceptual_ablation | available | rgb_full: char recovery 0.0%, leak 0.0%, errors 0 |
| pareto_sweep | available | recommended n=6 @ 360.0Hz, FPI 0.0333, MI 0.263 |
| strong_attack_extra | available | single_subframe: char recovery 0.0%, leak 0.0%, errors 0 |
| adaptive_attack_ablation | available | raw_subframe: char recovery 0.0%, leak 0.0%, errors 0 |
| camera_pipeline_ablation | available | clean_subframe: char recovery 0.0%, leak 0.0%, errors 0 |
| screen_privacy_baselines | available | unprotected: char recovery 92.9%, leak 100.0%, errors 0 |
| vlm_prompt_ablation | available | strict_transcription: char recovery 72.7%, leak 0.0%, errors 0 |
| usability_pilot | missing | `usability_pilot.json` |
