# Explicit Sensitive-Field Recovery

Canonical OCR archive SHA-256: `c3a23b6b5597195bc1c1b27a24198008d14f86a17fb396c793d02008b472007c`.

Fields were annotated before scoring; ordinary prose is excluded. Recovery is exact after the documented case/spacing/punctuation normalization.

## Matched Common-Setting Short-Exposure Estimand

| Profile | All matched cells | Field-bearing cells | Field opportunities | Field micro exact recovery (%) | Sample macro exact recovery (%) |
|---|---:|---:|---:|---:|---:|
| original | 288 | 216 | 432 | 91.4 | 86.8 |
| deployed | 288 | 216 | 432 | 17.7 | 17.5 |
| high suppression | 288 | 216 | 432 | 1.2 | 1.1 |

The primary pool excludes `d0.5_a15` and contains 288 duplicate-averaged keys per profile.

## All-Available Sensitivity

| Profile | All cells | Field-bearing cells | Field micro exact recovery (%) | Sample macro exact recovery (%) |
|---|---:|---:|---:|---:|
| original | 324 | 243 | 90.1 | 85.5 |
| deployed | 324 | 243 | 15.7 | 15.6 |
| high suppression | 324 | 243 | 1.0 | 1.0 |
