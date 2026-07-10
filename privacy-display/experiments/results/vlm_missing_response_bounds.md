# VLM Missing-Response Bounds

Bounds include every planned call. Conditional successful-call means must not be used to rank models when failure patterns differ.

| Session | Model | Condition | Success/planned | Exact bounds (%) | Character bounds (%) |
|---|---|---|---:|---:|---:|
| real_capture_vlm.json | Qwen/Qwen3-VL-32B-Instruct | original|short | 36/36 | [83.3, 83.3] | [94.5, 94.5] |
| real_capture_vlm.json | Qwen/Qwen3-VL-32B-Instruct | vlm|long | 34/36 | [77.8, 83.3] | [80.9, 86.5] |
| real_capture_vlm.json | Qwen/Qwen3-VL-32B-Instruct | vlm|short | 36/36 | [77.8, 77.8] | [91.5, 91.5] |
| real_capture_vlm.json | Qwen/Qwen3-VL-32B-Instruct | vlm|video|max_proj | 12/12 | [83.3, 83.3] | [92.0, 92.0] |
| real_capture_vlm.json | Qwen/Qwen3-VL-32B-Instruct | vlm|video|single_best | 12/12 | [66.7, 66.7] | [87.7, 87.7] |
| real_capture_vlm.json | Qwen/Qwen3-VL-32B-Instruct | vlm|video|temporal_mean | 12/12 | [83.3, 83.3] | [94.0, 94.0] |
| real_capture_vlm.json | Qwen/Qwen3-VL-32B-Instruct | vlm|video|window_mean_best | 12/12 | [83.3, 83.3] | [93.7, 93.7] |
| real_capture_vlm.json | Pro/moonshotai/Kimi-K2.6 | original|short | 36/36 | [83.3, 83.3] | [95.6, 95.6] |
| real_capture_vlm.json | Pro/moonshotai/Kimi-K2.6 | vlm|long | 36/36 | [2.8, 2.8] | [7.9, 7.9] |
| real_capture_vlm.json | Pro/moonshotai/Kimi-K2.6 | vlm|short | 36/36 | [47.2, 47.2] | [84.7, 84.7] |
| real_capture_vlm.json | Pro/moonshotai/Kimi-K2.6 | vlm|video|max_proj | 12/12 | [83.3, 83.3] | [90.5, 90.5] |
| real_capture_vlm.json | Pro/moonshotai/Kimi-K2.6 | vlm|video|single_best | 12/12 | [33.3, 33.3] | [64.8, 64.8] |
| real_capture_vlm.json | Pro/moonshotai/Kimi-K2.6 | vlm|video|temporal_mean | 12/12 | [83.3, 83.3] | [95.5, 95.5] |
| real_capture_vlm.json | Pro/moonshotai/Kimi-K2.6 | vlm|video|window_mean_best | 12/12 | [66.7, 66.7] | [89.8, 89.8] |
| real_capture_vlm.json | zai-org/GLM-4.5V | original|short | 26/36 | [52.8, 80.6] | [66.4, 94.2] |
| real_capture_vlm.json | zai-org/GLM-4.5V | vlm|long | 30/36 | [0.0, 16.7] | [4.1, 20.8] |
| real_capture_vlm.json | zai-org/GLM-4.5V | vlm|short | 31/36 | [44.4, 58.3] | [61.0, 74.9] |
| real_capture_vlm.json | zai-org/GLM-4.5V | vlm|video|max_proj | 8/12 | [58.3, 91.7] | [56.3, 89.6] |
| real_capture_vlm.json | zai-org/GLM-4.5V | vlm|video|single_best | 11/12 | [41.7, 50.0] | [77.3, 85.7] |
| real_capture_vlm.json | zai-org/GLM-4.5V | vlm|video|temporal_mean | 8/12 | [58.3, 91.7] | [61.2, 94.5] |
| real_capture_vlm.json | zai-org/GLM-4.5V | vlm|video|window_mean_best | 10/12 | [58.3, 75.0] | [71.9, 88.6] |
| real_capture_vlm_d1_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|long | 32/36 | [75.0, 86.1] | [77.1, 88.2] |
| real_capture_vlm_d1_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|short | 36/36 | [55.6, 55.6] | [79.1, 79.1] |
| real_capture_vlm_d1_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|video|max_proj | 12/12 | [66.7, 66.7] | [89.7, 89.7] |
| real_capture_vlm_d1_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|video|single_best | 12/12 | [25.0, 25.0] | [60.5, 60.5] |
| real_capture_vlm_d1_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|video|temporal_mean | 12/12 | [83.3, 83.3] | [91.1, 91.1] |
| real_capture_vlm_d1_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|video|window_mean_best | 12/12 | [58.3, 58.3] | [89.9, 89.9] |
| real_capture_vlm_d1_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|long | 35/36 | [72.2, 75.0] | [71.9, 74.7] |
| real_capture_vlm_d1_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|short | 36/36 | [38.9, 38.9] | [68.6, 68.6] |
| real_capture_vlm_d1_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|video|max_proj | 12/12 | [75.0, 75.0] | [90.0, 90.0] |
| real_capture_vlm_d1_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|video|single_best | 12/12 | [8.3, 8.3] | [44.5, 44.5] |
| real_capture_vlm_d1_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|video|temporal_mean | 12/12 | [83.3, 83.3] | [90.5, 90.5] |
| real_capture_vlm_d1_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|video|window_mean_best | 12/12 | [75.0, 75.0] | [90.3, 90.3] |
| real_capture_vlm_d1_a0.json | zai-org/GLM-4.5V | capture_hardened|long | 30/36 | [2.8, 19.4] | [2.5, 19.1] |
| real_capture_vlm_d1_a0.json | zai-org/GLM-4.5V | capture_hardened|short | 33/36 | [25.0, 33.3] | [43.1, 51.4] |
| real_capture_vlm_d1_a0.json | zai-org/GLM-4.5V | capture_hardened|video|max_proj | 11/12 | [75.0, 83.3] | [89.6, 98.0] |
| real_capture_vlm_d1_a0.json | zai-org/GLM-4.5V | capture_hardened|video|single_best | 10/12 | [16.7, 33.3] | [66.1, 82.7] |
| real_capture_vlm_d1_a0.json | zai-org/GLM-4.5V | capture_hardened|video|temporal_mean | 10/12 | [58.3, 75.0] | [81.0, 97.7] |
| real_capture_vlm_d1_a0.json | zai-org/GLM-4.5V | capture_hardened|video|window_mean_best | 10/12 | [58.3, 75.0] | [81.0, 97.6] |
| real_capture_vlm_d1.5_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|long | 36/36 | [91.7, 91.7] | [89.3, 89.3] |
| real_capture_vlm_d1.5_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|short | 36/36 | [47.2, 47.2] | [68.9, 68.9] |
| real_capture_vlm_d1.5_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|video|max_proj | 12/12 | [66.7, 66.7] | [90.1, 90.1] |
| real_capture_vlm_d1.5_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|video|single_best | 12/12 | [8.3, 8.3] | [24.8, 24.8] |
| real_capture_vlm_d1.5_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|video|temporal_mean | 12/12 | [66.7, 66.7] | [90.3, 90.3] |
| real_capture_vlm_d1.5_a0.json | Qwen/Qwen3-VL-32B-Instruct | capture_hardened|video|window_mean_best | 12/12 | [58.3, 58.3] | [89.0, 89.0] |
| real_capture_vlm_d1.5_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|long | 36/36 | [88.9, 88.9] | [89.9, 89.9] |
| real_capture_vlm_d1.5_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|short | 36/36 | [33.3, 33.3] | [61.5, 61.5] |
| real_capture_vlm_d1.5_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|video|max_proj | 12/12 | [58.3, 58.3] | [89.2, 89.2] |
| real_capture_vlm_d1.5_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|video|single_best | 12/12 | [0.0, 0.0] | [12.7, 12.7] |
| real_capture_vlm_d1.5_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|video|temporal_mean | 12/12 | [66.7, 66.7] | [90.3, 90.3] |
| real_capture_vlm_d1.5_a0.json | Pro/moonshotai/Kimi-K2.6 | capture_hardened|video|window_mean_best | 12/12 | [41.7, 41.7] | [84.2, 84.2] |
| real_capture_vlm_d1.5_a0.json | zai-org/GLM-4.5V | capture_hardened|long | 36/36 | [58.3, 58.3] | [62.4, 62.4] |
| real_capture_vlm_d1.5_a0.json | zai-org/GLM-4.5V | capture_hardened|short | 36/36 | [36.1, 36.1] | [70.0, 70.0] |
| real_capture_vlm_d1.5_a0.json | zai-org/GLM-4.5V | capture_hardened|video|max_proj | 12/12 | [58.3, 58.3] | [88.7, 88.7] |
| real_capture_vlm_d1.5_a0.json | zai-org/GLM-4.5V | capture_hardened|video|single_best | 12/12 | [0.0, 0.0] | [29.8, 29.8] |
| real_capture_vlm_d1.5_a0.json | zai-org/GLM-4.5V | capture_hardened|video|temporal_mean | 12/12 | [58.3, 58.3] | [88.5, 88.5] |
| real_capture_vlm_d1.5_a0.json | zai-org/GLM-4.5V | capture_hardened|video|window_mean_best | 12/12 | [66.7, 66.7] | [87.2, 87.2] |
