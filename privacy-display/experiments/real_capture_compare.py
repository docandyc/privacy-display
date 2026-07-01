"""Align the real-camera ablation against the simulation ablation.

Produces a side-by-side table so the thesis can show that the real USB-webcam
captures reproduce the simulated ``anti_ocr_profile_ablation`` trend (recovery
falls as defences are added; 0.10/0.12 is the operating point). Best-effort and
schema-tolerant: missing files or labels are reported, not fatal.

Run:
    python experiments/real_capture_compare.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_SIM = "experiments/results/anti_ocr_profile_ablation.json"
DEFAULT_REAL = "experiments/results/real_capture_ocr.json"
DEFAULT_OUT = "experiments/results/real_vs_sim.md"

# real ablation label -> simulation block1 summary key (same operating points).
SIM_LABEL_MAP = {
    "mask_noise": ("block1/off",),
    "anti_ocr": ("block1/strong@overlay",),
    "deployed": ("block1/strong@deployed",),
    "capture_hardened": ("block1/capture_hardened", "block1/vlm"),
}

REAL_LABEL_ALIASES = {
    "capture_hardened": ("capture_hardened", "vlm"),
}


def _nested_mean(node: dict | None, metric: str) -> float | None:
    if not isinstance(node, dict):
        return None
    stat = node.get(metric)
    if isinstance(stat, dict) and "mean" in stat:
        return float(stat["mean"])
    return None


def build_comparison(
    real_report: dict,
    sim_report: dict,
    *,
    real_attack: str = "video:temporal_mean",
    metric: str = "exact_match",
) -> list[dict]:
    """Return rows aligning each real ablation with its simulation counterpart.

    The simulation block1 headline metric is the temporal-average attack, which
    corresponds to the real ``video:temporal_mean`` offline attack.
    """
    sim_summary = sim_report.get("summary", {})
    real_summary = real_report.get("summary", {}).get("by_ablation_attack", {})
    rows: list[dict] = []
    for ablation, sim_keys in SIM_LABEL_MAP.items():
        sim_key = next((key for key in sim_keys if key in sim_summary), sim_keys[0])
        sim_value = _nested_mean(sim_summary.get(sim_key), metric)
        real_labels = REAL_LABEL_ALIASES.get(ablation, (ablation,))
        real_value = next(
            (
                value
                for label in real_labels
                if (value := _nested_mean(
                    real_summary.get(f"{label}|{real_attack}"), metric
                )) is not None
            ),
            None,
        )
        gap = None
        if sim_value is not None and real_value is not None:
            gap = real_value - sim_value
        rows.append({
            "ablation": ablation,
            "sim_key": sim_key,
            "metric": metric,
            "sim": sim_value,
            "real": real_value,
            "real_minus_sim": gap,
        })
    return rows


def render_markdown(rows: list[dict], *, real_attack: str, metric: str) -> str:
    def fmt(value: float | None) -> str:
        return "n/a" if value is None else f"{value * 100:.1f}%"

    lines = [
        "# Real Camera vs Simulation Ablation",
        "",
        f"Metric: **{metric}** (lower = stronger protection). "
        f"Simulation uses the temporal-average attack; real uses `{real_attack}`.",
        "",
        "| Ablation | Sim key | Simulation | Real camera | Real − Sim |",
        "|---|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ablation']} | {row['sim_key']} | {fmt(row['sim'])} | "
            f"{fmt(row['real'])} | {fmt(row['real_minus_sim'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def _load_json(path: str | Path) -> dict | None:
    p = Path(path)
    if not p.exists():
        print(f"[compare] missing: {p}", file=sys.stderr)
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Align real-camera and simulation ablations")
    p.add_argument("--sim", default=DEFAULT_SIM)
    p.add_argument("--real", default=DEFAULT_REAL)
    p.add_argument("--out", default=DEFAULT_OUT)
    p.add_argument("--real-attack", default="video:temporal_mean")
    p.add_argument("--metric", default="exact_match")
    args = p.parse_args(argv)

    sim = _load_json(args.sim)
    real = _load_json(args.real)
    if sim is None or real is None:
        print("[compare] need both sim and real reports; run the experiments first.",
              file=sys.stderr)
        return 1
    rows = build_comparison(real, sim, real_attack=args.real_attack, metric=args.metric)
    md = render_markdown(rows, real_attack=args.real_attack, metric=args.metric)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"Comparison written: {out}")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
