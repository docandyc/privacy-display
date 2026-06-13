"""
Experiment E — security/usability Pareto sweep.

Sweeps the subframe count n, display refresh, and noise budget epsilon, then
plots the trade-off between usability (flicker perception index, FPI) and
security (single-subframe information retention = normalized mutual information,
which falls ~1/n). Image-domain metrics depend only on (n, epsilon); FPI also
depends on refresh, so we compute image metrics once per (n, epsilon) and expand
with refresh for FPI to avoid redundant OCR.

Outputs experiments/results/pareto_sweep.json and (if matplotlib is available)
pareto_sweep.png with the Pareto front and the recommended operating point
(lowest information retention among configs with FPI < 0.1).

Run:
    python experiments/pareto_sweep.py --max-samples 8
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.build_corpus import load_corpus, load_corpus_metadata  # noqa: E402
from src.attack.camera_simulator import CameraSimulator  # noqa: E402
from src.attack.ocr_evaluator import OCREvaluator  # noqa: E402
from src.core.subframe_composer import SubframeComposer  # noqa: E402
from src.evaluation.benchmark import _mean_std, compose_protected_subframes  # noqa: E402
from src.evaluation.metrics import (  # noqa: E402
    compute_delta_e, compute_ssim, compute_entropy_ratio, compute_fpi, fpi_is_safe,
)
from src.evaluation.sampling import select_publication_subset, take_indices  # noqa: E402


def image_metrics(images, truths, n, epsilon, ev, cam, max_samples):
    """Metrics that depend only on (n, epsilon): aggregated over the sample subset."""
    delta_e, ssim, entropy, single_ocr, fullcycle_ocr = [], [], [], [], []
    composer = SubframeComposer(n=n, gamma=1.0)
    for idx, (img, gt) in enumerate(zip(images[:max_samples], truths[:max_samples])):
        sf = compose_protected_subframes(img, n=n, epsilon=epsilon, cycles=1, cycle_start=idx * 13)
        integrated = composer.integrate_subframes(sf, pedestal=epsilon * 255)
        delta_e.append(compute_delta_e(img, integrated))
        ssim.append(compute_ssim(img, integrated))
        entropy.append(float(np.mean([compute_entropy_ratio(s, img) for s in sf])))
        single_ocr.append(float(np.mean([ev.evaluate_single(s, gt, "tesseract").char_accuracy for s in sf])))
        full = cam.temporal_averaging_attack(sf, n, randomize_order=False)
        fullcycle_ocr.append(ev.evaluate_single(full, gt, "tesseract").char_accuracy)
    return {
        "delta_e": _mean_std(delta_e),
        "ssim": _mean_std(ssim),
        "entropy_ratio": _mean_std(entropy),
        "single_frame_ocr": _mean_std(single_ocr),
        "full_cycle_ocr": _mean_std(fullcycle_ocr),
    }


def _nums(text, cast):
    return [cast(x.strip()) for x in str(text).split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Experiment E: security/usability Pareto sweep")
    p.add_argument("--ns", default="2,4,6,8")
    p.add_argument("--refreshes", default="144,240,360")
    p.add_argument("--epsilons", default="0.031372549")  # 8/255
    p.add_argument("--max-samples", type=int, default=8)
    p.add_argument("--samples-per-category", type=int, default=None)
    p.add_argument("--ocr-timeout", type=float, default=4.0)
    p.add_argument("--output-dir", default=str(ROOT / "experiments" / "results"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    images, truths, names = load_corpus()
    metadata = load_corpus_metadata()
    selected_indices, sample_policy = select_publication_subset(
        names,
        metadata,
        max_samples=args.max_samples,
        samples_per_category=args.samples_per_category,
    )
    images = take_indices(images, selected_indices)
    truths = take_indices(truths, selected_indices)
    ev = OCREvaluator(engines=["tesseract"], timeout=args.ocr_timeout)
    cam = CameraSimulator()
    ns = _nums(args.ns, int)
    refreshes = _nums(args.refreshes, float)
    epsilons = _nums(args.epsilons, float)

    # Compute (n, epsilon) image metrics once.
    img_cache: dict[tuple, dict] = {}
    for n in ns:
        for eps in epsilons:
            print(f"  image metrics n={n}, eps={eps:.4f} ...")
            img_cache[(n, eps)] = image_metrics(images, truths, n, eps, ev, cam, len(images))

    configs = []
    for n in ns:
        for eps in epsilons:
            m = img_cache[(n, eps)]
            for refresh in refreshes:
                fpi = compute_fpi(refresh, n)
                configs.append({
                    "n": n, "refresh_hz": refresh, "epsilon": eps,
                    "effective_fps": refresh / n,
                    "fpi": fpi, "fpi_safe": bool(fpi_is_safe(fpi)),
                    "delta_e": m["delta_e"]["mean"], "ssim": m["ssim"]["mean"],
                    "entropy_ratio": m["entropy_ratio"]["mean"],
                    "single_frame_ocr": m["single_frame_ocr"]["mean"],
                    "full_cycle_ocr": m["full_cycle_ocr"]["mean"],
                })

    # Pareto front on (FPI ↓ usability, entropy_ratio ↓ security); both minimized.
    def dominated(c, others):
        return any(
            o is not c and o["fpi"] <= c["fpi"] and o["entropy_ratio"] <= c["entropy_ratio"]
            and (o["fpi"] < c["fpi"] or o["entropy_ratio"] < c["entropy_ratio"])
            for o in others
        )
    for c in configs:
        c["pareto_optimal"] = not dominated(c, configs)

    safe = [c for c in configs if c["fpi_safe"]]
    recommended = min(safe, key=lambda c: c["entropy_ratio"]) if safe else min(configs, key=lambda c: c["fpi"])
    recommended_key = (recommended["n"], recommended["refresh_hz"], recommended["epsilon"])

    report = {
        "config": {"ns": ns, "refreshes": refreshes, "epsilons": epsilons,
                   "max_samples": args.max_samples,
                   "sample_policy": sample_policy,
                   "axes": {"usability": "fpi (lower better)",
                            "security": "entropy_ratio = single-frame normalized MI (lower better)"}},
        "recommended": recommended,
        "image_metrics_by_n_epsilon": {f"n{n}_eps{eps:.4f}": img_cache[(n, eps)]
                                       for n in ns for eps in epsilons},
        "configs": configs,
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "pareto_sweep.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== Security/Usability sweep (eps=%s) ===" % args.epsilons)
    print("| n | refresh | eff.fps | FPI | safe | ΔE | SSIM | 1-frame MI | 1-frame OCR | full-cycle OCR | Pareto |")
    print("|" + "---|" * 11)
    for c in sorted(configs, key=lambda x: (x["n"], x["refresh_hz"])):
        star = "★" if (c["n"], c["refresh_hz"], c["epsilon"]) == recommended_key else ""
        print(f"| {c['n']} | {c['refresh_hz']:.0f} | {c['effective_fps']:.0f} | "
              f"{c['fpi']:.4f} | {'✓' if c['fpi_safe'] else '✗'} | {c['delta_e']:.2f} | "
              f"{c['ssim']:.3f} | {c['entropy_ratio']:.3f} | {c['single_frame_ocr'] * 100:.0f}% | "
              f"{c['full_cycle_ocr'] * 100:.0f}% | {'●' if c['pareto_optimal'] else ''}{star} |")
    print(f"\nRecommended (FPI<0.1, lowest 1-frame MI): "
          f"n={recommended['n']}, refresh={recommended['refresh_hz']:.0f}Hz "
          f"(FPI={recommended['fpi']:.4f}, MI={recommended['entropy_ratio']:.3f})")

    _plot(configs, recommended_key, out_dir)
    print(f"Saved: {out}")
    return 0


def _plot(configs, recommended_key, out_dir):
    try:
        os.environ.setdefault(
            "MPLCONFIGDIR",
            str(Path(tempfile.gettempdir()) / "privacy-display-matplotlib"),
        )
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[note] matplotlib not available; skipped pareto_sweep.png")
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    ns = sorted({c["n"] for c in configs})
    cmap = plt.get_cmap("viridis")
    for n in ns:
        pts = sorted([c for c in configs if c["n"] == n], key=lambda c: c["fpi"])
        ax.plot([c["fpi"] for c in pts], [c["entropy_ratio"] for c in pts],
                "o-", color=cmap(ns.index(n) / max(1, len(ns) - 1)), label=f"n={n}", alpha=0.8)
        for c in pts:
            ax.annotate(f"{c['refresh_hz']:.0f}Hz", (c["fpi"], c["entropy_ratio"]),
                        fontsize=6, alpha=0.6)
    rec = next(c for c in configs if (c["n"], c["refresh_hz"], c["epsilon"]) == recommended_key)
    ax.scatter([rec["fpi"]], [rec["entropy_ratio"]], s=200, facecolors="none",
               edgecolors="red", linewidths=2, label="recommended", zorder=5)
    ax.axvline(0.1, color="red", ls="--", alpha=0.5, label="FPI=0.1 (flicker-safe)")
    ax.set_xlabel("FPI — usability (lower = less flicker)")
    ax.set_ylabel("single-frame MI — security (lower = safer)")
    ax.set_title("Security / Usability Pareto sweep")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "pareto_sweep.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved plot: {out_dir / 'pareto_sweep.png'}")


if __name__ == "__main__":
    raise SystemExit(main())
