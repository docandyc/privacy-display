# Real-Capture Fixed-Grid Preprocessing Attack

The primary rows use matched content/position/repeat units. Duplicate readability-priority captures are averaged inside their matched unit.

| Oracle | Profile | Matched units | Matched mean | Difference vs original | 95% interval |
|---|---|---:|---:|---:|---:|
| Raw best-of-engine | Original (unprotected) | 288 | 85.1% | -- | -- |
| Raw best-of-engine | Readability-priority | 288 | 14.2% | 70.9 pp | [63.5, 75.9] |
| Raw best-of-engine | High-suppression | 288 | 2.3% | 82.8 pp | [72.9, 89.7] |
| Best-of-preprocessing-and-engine | Original (unprotected) | 288 | 88.4% | -- | -- |
| Best-of-preprocessing-and-engine | Readability-priority | 288 | 33.9% | 54.5 pp | [49.2, 59.5] |
| Best-of-preprocessing-and-engine | High-suppression | 288 | 6.5% | 81.9 pp | [72.8, 87.8] |

## All-Available Descriptive Means

| Oracle | Profile | Captures | Character recovery | Exact match |
|---|---|---:|---:|---:|
| Raw best-of-engine | original | 288 | 85.1% | 31.2% |
| Raw best-of-engine | deployed | 408 | 13.2% | 0.0% |
| Raw best-of-engine | high_suppression | 288 | 2.3% | 0.0% |
| Best-of-preprocessing-and-engine | original | 288 | 88.4% | 44.1% |
| Best-of-preprocessing-and-engine | deployed | 408 | 31.7% | 0.5% |
| Best-of-preprocessing-and-engine | high_suppression | 288 | 6.5% | 0.0% |
