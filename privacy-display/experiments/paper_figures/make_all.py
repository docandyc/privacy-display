"""Regenerate every paper figure PDF into paper/figures/ in one command.

Usage (from repo root, using the project venv):
    privacy-display/.venv/bin/python privacy-display/experiments/paper_figures/make_all.py
"""
from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# order: concept diagrams F1/F2 are not matplotlib and are excluded on purpose
MODULES = [
    "fig_f3_montage",            # F3 real-capture montage (PIL/imshow)
    "fig_f4_attack_bar",         # F4 grade x attack-mode OCR bars
    "fig_f5_tradeoff",           # F5 readability vs integration robustness
    "fig_f6_detection_drop",     # F6 real-capture detection mAP50 drop
    "fig_f7_pareto",             # F7 security/usability Pareto sweep
    "fig_s1_antiocr_heatmap",    # S1 stripe x glyph heatmaps
    "fig_s2_multiengine_ocr",    # S2 OCR-engine generalization
    "fig_s3_baselines_scatter",  # S3 privacy vs usability baselines
    "fig_s4_all_attackers",      # S4 one subframe defeats every attacker family
]


def main() -> int:
    failures = []
    for name in MODULES:
        try:
            mod = importlib.import_module(name)
            mod.main()
        except Exception:  # noqa: BLE001 - report and continue
            failures.append(name)
            print(f"[make_all] FAILED {name}:")
            traceback.print_exc()
    print(f"\n[make_all] {len(MODULES) - len(failures)}/{len(MODULES)} figures OK")
    if failures:
        print(f"[make_all] failed: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
