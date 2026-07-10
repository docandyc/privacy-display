# Real-Capture Fixed-Grid Preprocessing Attack

The primary rows use matched content/position/repeat units. Duplicate readability-priority captures are averaged inside their matched unit.

| Oracle | Profile | Matched units | Matched mean | Difference vs original | 95% interval |
|---|---|---:|---:|---:|---:|
| Raw best-of-engine | Original (unprotected) | 288 | 94.5% | -- | -- |
| Raw best-of-engine | Readability-priority | 288 | 17.8% | 76.7 pp | [74.3, 79.2] |
| Raw best-of-engine | High-suppression | 288 | 5.6% | 88.9 pp | [85.5, 91.9] |
| Best-of-preprocessing-and-engine | Original (unprotected) | 288 | 95.9% | -- | -- |
| Best-of-preprocessing-and-engine | Readability-priority | 288 | 40.2% | 55.7 pp | [50.3, 60.5] |
| Best-of-preprocessing-and-engine | High-suppression | 288 | 13.7% | 82.2 pp | [78.5, 85.2] |

## All-Available Descriptive Means

| Oracle | Profile | Captures | Character recovery | Exact match |
|---|---|---:|---:|---:|
| Raw best-of-engine | original | 288 | 94.5% | 64.6% |
| Raw best-of-engine | deployed | 408 | 16.7% | 0.5% |
| Raw best-of-engine | high_suppression | 288 | 5.6% | 0.0% |
| Best-of-preprocessing-and-engine | original | 288 | 95.9% | 78.5% |
| Best-of-preprocessing-and-engine | deployed | 408 | 37.9% | 2.5% |
| Best-of-preprocessing-and-engine | high_suppression | 288 | 13.7% | 0.0% |
