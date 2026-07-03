"""Rebuild experiments/results/real_capture_per_engine.json from raw captures.

Reads the engine-level records in real_capture_ocr.json and aggregates
per (profile | attack | engine). Fixes an earlier aggregation bug where the
``capture_hardened`` label had merged two different ablation labels
(``vlm`` = capture-hardened profile AND ``anti_ocr`` = strong overlay,
stripe 0.10 / glyph 0.12, no inversion), inflating N to 648 and distorting
the per-engine means. ``capture_hardened`` now maps to ablation ``vlm`` only,
matching the paper's per-engine table (tab:real_ocr_engine).

Usage: python scripts/rebuild_real_capture_per_engine.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "experiments" / "results"
SOURCE = RESULTS / "real_capture_ocr.json"
TARGET = RESULTS / "real_capture_per_engine.json"

# output profile label -> raw ablation label in real_capture_ocr.json
PROFILE_MAP = {
    "original": "original",
    "mask_only": "mask_only",
    "mask_noise": "mask_noise",
    "deployed": "deployed",
    "capture_hardened": "vlm",  # historical label for the capture-hardened profile
}

# output attack label -> raw attack label
ATTACK_MAP = {
    "short": "short",
    "long": "long",
    "video_temporal_mean": "video:temporal_mean",
}

ENGINES = ("tesseract", "easyocr", "surya")
METRICS = ("char_accuracy", "exact_match", "sensitive_token_recall")
BOOTSTRAP_RESAMPLES = 2000
SEED = 20260702


def bootstrap_half_width(values: list[float], rng: random.Random) -> float:
    """95% percentile-bootstrap CI half-width, mirroring the summary block."""
    if len(values) < 2:
        return 0.0
    means = []
    n = len(values)
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    low = means[int(0.025 * BOOTSTRAP_RESAMPLES)]
    high = means[min(int(0.975 * BOOTSTRAP_RESAMPLES), BOOTSTRAP_RESAMPLES - 1)]
    return (high - low) / 2


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    captures = data["captures"]
    rng = random.Random(SEED)

    out: dict[str, dict] = {}
    for profile, ablation in PROFILE_MAP.items():
        for attack, raw_attack in ATTACK_MAP.items():
            for engine in ENGINES:
                recs = [
                    c for c in captures
                    if c["ablation"] == ablation
                    and c["attack"] == raw_attack
                    and c["engine"] == engine
                ]
                if not recs:
                    continue
                entry: dict[str, dict] = {}
                for metric in METRICS:
                    values = [float(c[metric] or 0.0) for c in recs]
                    entry[metric] = {
                        "mean": sum(values) / len(values),
                        "ci95": {"half_width": bootstrap_half_width(values, rng)},
                        "count": len(values),
                    }
                out[f"{profile}|{attack}|{engine}"] = entry

    TARGET.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TARGET} with {len(out)} keys")


if __name__ == "__main__":
    main()
