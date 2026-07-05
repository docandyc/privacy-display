# VLM Result Inventory

## Evidence Status

| File | Position | Captures | API calls | Success | Status | Use in manuscript |
|---|---:|---:|---:|---:|---|---|
| `real_capture_vlm.json` | 0.5 m / 0 deg | 156 | 468 | 434 | incomplete older probe | Retain as close-range adversarial probe if needed. |
| `real_capture_vlm_d1_a0.json` | 1.0 m / 0 deg | 120 | 360 | 339 | incomplete, partial retained | Supplementary/descriptive only. |
| `real_capture_vlm_d1.5_a0.json` | 1.5 m / 0 deg | 120 | 360 | 360 | complete | Primary new completed evidence. |

## Completed 1.5 m Run

Exact-match / character recovery / successful calls:

| Condition | Qwen3-VL | Kimi-K2.6 | GLM-4.5V |
|---|---:|---:|---:|
| short | 47.2 / 68.9 / 36 | 33.3 / 61.5 / 36 | 36.1 / 70.0 / 36 |
| long | 91.7 / 89.3 / 36 | 88.9 / 89.9 / 36 | 58.3 / 62.4 / 36 |
| video:single_best | 8.3 / 24.8 / 12 | 0.0 / 12.7 / 12 | 0.0 / 29.8 / 12 |
| video:temporal_mean | 66.7 / 90.3 / 12 | 66.7 / 90.3 / 12 | 58.3 / 88.5 / 12 |
| video:window_mean_best | 58.3 / 89.0 / 12 | 41.7 / 84.2 / 12 | 66.7 / 87.2 / 12 |
| video:max_proj | 66.7 / 90.1 / 12 | 58.3 / 89.2 / 12 | 58.3 / 88.7 / 12 |

## Incomplete 1.0 m Run

Exact-match / character recovery / successful calls:

| Condition | Qwen3-VL | Kimi-K2.6 | GLM-4.5V |
|---|---:|---:|---:|
| short | 55.6 / 79.1 / 36 | 38.9 / 68.6 / 36 | 27.3 / 47.0 / 33 |
| long | 84.4 / 86.8 / 32 | 74.3 / 74.0 / 35 | 3.3 / 3.0 / 30 |
| video:single_best | 25.0 / 60.5 / 12 | 8.3 / 44.5 / 12 | 20.0 / 79.3 / 10 |
| video:temporal_mean | 83.3 / 91.1 / 12 | 83.3 / 90.5 / 12 | 70.0 / 97.2 / 10 |
| video:window_mean_best | 58.3 / 89.9 / 12 | 75.0 / 90.3 / 12 | 70.0 / 97.1 / 10 |
| video:max_proj | 66.7 / 89.7 / 12 | 75.0 / 90.0 / 12 | 81.8 / 97.8 / 11 |

## Claim Candidates

* Claim: The completed 1.5 m run confirms that VLM leakage is not limited to the earlier 0.5 m probe.
  * Source evidence: short exact remains 33.3--47.2%; long exact is 58.3--91.7%; temporal-mean exact is 58.3--66.7%.
  * Allowed wording: "remains observable", "persists at 1.5 m", "varies by attack view and model".
  * Forbidden stronger wording: "all VLMs defeat the defense", "VLMs always recover the text", "distance has no effect".
  * Uncertainty: only one camera, one angle, one completed additional distance, commercial API model versions.

* Claim: Single best video frames are less effective than temporal aggregation for VLMs in the completed 1.5 m run.
  * Source evidence: single-best exact 0.0--8.3% vs temporal-mean exact 58.3--66.7%; char recovery 12.7--29.8% vs 88.5--90.3%.
  * Allowed wording: "in this run", "temporal aggregation is substantially stronger than selecting one sharp frame".
  * Forbidden stronger wording: "single frames are safe", because short-exposure still has 33.3--47.2% exact.

* Claim: Dense small text remains the strongest protected category under short exposure, while large short strings remain vulnerable.
  * Source evidence: in the 1.5 m short run, CET6 dense page has 0% exact and 0% char for all three VLMs; digit strings and English short sentences remain high.
  * Allowed wording: "consistent with the earlier content-type pattern".
  * Forbidden stronger wording: "all dense documents are protected" or "all large-text categories fail".

