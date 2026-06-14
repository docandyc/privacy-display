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
- noise_epsilon_sweep: `noise_epsilon_sweep.json`
- vlm_model_ablation: `vlm_model_ablation.json`
- brightness_compensation_ablation: `brightness_compensation_ablation.json`
- mask_granularity_ablation: `mask_granularity_ablation.json`
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

- Not available: Real camera capture analysis is implemented, but no real photo/video-frame result has been generated.

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
| recognizer_generalization | available | tesseract/original: char recovery 94.0% (92.3%-95.6%), leak 100.0%, errors 0 |
| perceptual_ablation | available | rgb_full: char recovery 0.0% (0.0%-0.1%), leak 0.0%, errors 0 |
| pareto_sweep | available | recommended n=6 @ 360.0Hz, FPI 0.0333, MI 0.249 |
| strong_attack_extra | available | single_subframe: char recovery 0.0% (0.0%-0.0%), leak 0.0%, errors 0 |
| adaptive_attack_ablation | available | raw_subframe: char recovery 0.2% (0.0%-0.4%), leak 0.0%, errors 0 |
| camera_pipeline_ablation | available | clean_subframe: char recovery 0.1% (0.0%-0.2%), leak 0.0%, errors 0 |
| screen_privacy_baselines | available | unprotected: char recovery 92.9% (87.8%-97.2%), leak 100.0%, errors 0 |
| vlm_prompt_ablation | available | strict_transcription: char recovery 72.7% (58.1%-85.6%), leak 0.0%, errors 0 |
| noise_epsilon_sweep | available | eps_0.0000: char recovery 0.0% (0.0%-0.0%), leak 0.0%, errors 0 |
| vlm_model_ablation | available | Qwen/Qwen3-VL-32B-Instruct: char recovery 96.3% (92.5%-99.2%), leak 0.0%, errors 1 |
| brightness_compensation_ablation | available | gamma_1.00: char recovery 0.0% (0.0%-0.1%), leak 0.0%, errors 0 |
| mask_granularity_ablation | available | block_1: char recovery 0.0% (0.0%-0.1%), leak 0.0%, errors 0 |
| seed_sensitivity | available | single_frame_ocr: char recovery 0.0% (0.0%-0.1%), leak 0.0%, errors 0 |
| usability_pilot | missing | `usability_pilot.json` |

### Supplemental Ablation Detail


#### component_ablation

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| baseline | 94.0% (92.3%-95.6%) | 0.0% | 0 |
| single_mask_only | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| single_mask_noise | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| inpaint_mask_only | 50.9% (44.7%-56.8%) | 0.0% | 0 |
| inpaint_noise_pedestal | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| inpaint_noise_no_pedestal | 9.6% (4.9%-14.7%) | 0.0% | 0 |
| long_exposure_no_inv | 94.3% (92.7%-95.9%) | 0.0% | 0 |
| long_exposure_with_inv | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| ae_real_subframe_no_black | 0.1% (0.0%-0.1%) | 0.0% | 0 |
| ae_real_subframe_with_black | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| weak_mask_only | 32.2% (24.2%-40.4%) | 0.0% | 0 |
| weak_mask_noise | 26.8% (22.5%-31.1%) | 0.0% | 0 |

#### recognizer_generalization

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| tesseract/original | 94.0% (92.3%-95.6%) | 100.0% | 0 |
| tesseract/single_subframe | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| tesseract/temporal_average_cycle | 94.3% (92.6%-95.9%) | 100.0% | 0 |
| tesseract/phase_search_max | 94.2% (92.4%-95.8%) | 100.0% | 0 |
| tesseract/blue_channel_max | 94.6% (93.0%-96.0%) | 100.0% | 0 |

#### perceptual_ablation

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| rgb_full | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| blue_residual_0.5 | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| blue_kept | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| green_kept | 0.0% (0.0%-0.1%) | 0.0% | 0 |

#### strong_attack_extra

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| single_subframe | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| rolling_shutter_single | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| rolling_shutter_row_alignment | 92.9% (87.8%-97.2%) | 100.0% | 0 |
| temporal_superresolution | 91.4% (85.3%-96.6%) | 100.0% | 0 |

#### adaptive_attack_ablation

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| raw_subframe | 0.2% (0.0%-0.4%) | 0.0% | 0 |
| otsu_binarize | 0.1% (0.0%-0.2%) | 0.0% | 0 |
| adaptive_threshold | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| clahe_luma | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| unsharp_mask | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| denoise | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| upscale_2x | 0.0% (0.0%-0.0%) | 0.0% | 0 |

#### camera_pipeline_ablation

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| clean_subframe | 0.1% (0.0%-0.2%) | 0.0% | 0 |
| jpeg_q50 | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| sensor_noise_iso_high | 0.1% (0.0%-0.3%) | 0.0% | 0 |
| motion_blur | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| digital_zoom_2x | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| auto_contrast | 0.1% (0.0%-0.3%) | 0.0% | 0 |
| rolling_shutter_single | 0.1% (0.0%-0.2%) | 0.0% | 0 |
| temporal_average_boundary | 94.4% (92.7%-96.0%) | 100.0% | 0 |

#### screen_privacy_baselines

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| unprotected | 92.9% (87.8%-97.2%) | 100.0% | 0 |
| dim_50pct | 92.9% (87.8%-97.2%) | 100.0% | 0 |
| gaussian_blur | 52.6% (30.2%-74.5%) | 77.8% | 0 |
| pixelate_12px | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| privacy_filter_offaxis_proxy | 84.7% (64.1%-96.8%) | 88.9% | 0 |
| temporal_mask_single_subframe | 0.0% (0.0%-0.0%) | 0.0% | 0 |

#### vlm_prompt_ablation

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| strict_transcription | 72.7% (58.1%-85.6%) | 0.0% | 0 |
| relaxed_readability | 72.7% (58.1%-85.6%) | 0.0% | 0 |
| sensitive_field_extraction | 72.8% (58.2%-85.8%) | 0.0% | 0 |

#### noise_epsilon_sweep

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| eps_0.0000 | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| eps_0.0078 | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| eps_0.0157 | 0.1% (0.0%-0.3%) | 0.0% | 0 |
| eps_0.0314 | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| eps_0.0627 | 0.1% (0.0%-0.3%) | 0.0% | 0 |
| eps_0.1255 | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| eps_0.2510 | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| eps_0.3765 | 0.0% (0.0%-0.1%) | 0.0% | 0 |

#### vlm_model_ablation

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| Qwen/Qwen3-VL-32B-Instruct | 96.3% (92.5%-99.2%) | 0.0% | 1 |
| Pro/moonshotai/Kimi-K2.6 | 96.0% (93.1%-98.2%) | 0.0% | 2 |
| zai-org/GLM-4.5V | 93.2% (84.9%-98.7%) | 0.0% | 0 |

#### brightness_compensation_ablation

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| gamma_1.00 | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| gamma_2.00 | 0.1% (0.0%-0.1%) | 0.0% | 0 |
| gamma_4.00 | 0.1% (0.0%-0.1%) | 0.0% | 0 |

#### mask_granularity_ablation

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| block_1 | 0.0% (0.0%-0.1%) | 0.0% | 0 |
| block_2 | 0.0% (0.0%-0.0%) | 0.0% | 0 |
| block_4 | 0.1% (0.0%-0.2%) | 0.0% | 0 |
| block_8 | 0.8% (0.5%-1.2%) | 0.0% | 0 |

#### seed_sensitivity

| Condition | Char recovery | Leak rate char>=20% | Errors |
|---|---:|---:|---:|
| single_frame_ocr | 0.0% (0.0%-0.1%) | 0.0% | 0 |
