# Real-Capture Fixed-Grid Preprocessing Attack

The primary rows use matched content/position/repeat units. Duplicate readability-priority captures are averaged inside their matched unit.

| Oracle | Profile | Matched units | Matched mean | Difference vs original | 95% interval |
|---|---|---:|---:|---:|---:|
| Raw best-of-engine | Original (unprotected) | 288 | 84.9% | -- | -- |
| Raw best-of-engine | Readability-priority | 288 | 3.2% | 81.7 pp | [77.4, 85.5] |
| Raw best-of-engine | High-suppression | 288 | 2.0% | 82.9 pp | [77.7, 87.7] |
| Best-of-preprocessing-and-engine | Original (unprotected) | 288 | 91.8% | -- | -- |
| Best-of-preprocessing-and-engine | Readability-priority | 288 | 10.8% | 81.0 pp | [75.6, 86.4] |
| Best-of-preprocessing-and-engine | High-suppression | 288 | 8.2% | 83.6 pp | [77.3, 89.0] |

## All-Available Descriptive Means

| Oracle | Profile | Captures | Character recovery | Exact match |
|---|---|---:|---:|---:|
| Raw best-of-engine | original | 288 | 84.9% | 53.8% |
| Raw best-of-engine | deployed | 408 | 3.4% | 0.0% |
| Raw best-of-engine | high_suppression | 288 | 2.0% | 0.0% |
| Best-of-preprocessing-and-engine | original | 288 | 91.8% | 65.6% |
| Best-of-preprocessing-and-engine | deployed | 408 | 11.3% | 0.2% |
| Best-of-preprocessing-and-engine | high_suppression | 288 | 8.2% | 0.0% |
