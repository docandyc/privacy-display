# Real-Capture Fixed-Grid Preprocessing Attack

The primary rows use matched content/position/repeat units. Duplicate readability-priority captures are averaged inside their matched unit.

| Oracle | Profile | Matched units | Matched mean | Difference vs original | 95% interval |
|---|---|---:|---:|---:|---:|
| Raw best-of-engine | Original (unprotected) | 288 | 30.6% | -- | -- |
| Raw best-of-engine | Readability-priority | 288 | 4.1% | 26.5 pp | [16.1, 39.6] |
| Raw best-of-engine | High-suppression | 288 | 2.0% | 28.6 pp | [19.1, 40.0] |
| Best-of-preprocessing-and-engine | Original (unprotected) | 288 | 49.3% | -- | -- |
| Best-of-preprocessing-and-engine | Readability-priority | 288 | 20.2% | 29.1 pp | [20.8, 39.1] |
| Best-of-preprocessing-and-engine | High-suppression | 288 | 6.0% | 43.3 pp | [36.7, 50.4] |

## All-Available Descriptive Means

| Oracle | Profile | Captures | Character recovery | Exact match |
|---|---|---:|---:|---:|
| Raw best-of-engine | original | 288 | 30.6% | 16.3% |
| Raw best-of-engine | deployed | 408 | 3.6% | 0.5% |
| Raw best-of-engine | high_suppression | 288 | 2.0% | 0.0% |
| Best-of-preprocessing-and-engine | original | 288 | 49.3% | 28.1% |
| Best-of-preprocessing-and-engine | deployed | 408 | 19.0% | 1.7% |
| Best-of-preprocessing-and-engine | high_suppression | 288 | 6.0% | 0.0% |
