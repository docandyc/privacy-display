"""F7 - Security / usability Pareto front (n x refresh sweep).

Re-draws the plot that ``experiments/pareto_sweep.py::_plot`` already produces
(FPI vs single-frame mutual information, one line per subframe count n, refresh
annotated, model-selected candidate circled) but via the shared ``figstyle`` so it
matches the other figures and is exported as a vector PDF. Reads the committed
``pareto_sweep.json`` rather than recomputing.
"""
from __future__ import annotations

import figstyle as fs


def main() -> None:
    data = fs.load("pareto_sweep.json")
    configs = data["configs"]
    rec = data["recommended"]
    rec_key = (rec["n"], rec["refresh_hz"], rec["epsilon"])

    fig, ax = fs.plt.subplots(figsize=(fs.COL_W, 2.8))
    ns = sorted({c["n"] for c in configs})
    markers = ["o", "s", "^", "D", "v"]

    for i, n in enumerate(ns):
        pts = sorted([c for c in configs if c["n"] == n], key=lambda c: c["fpi"])
        ax.plot([c["fpi"] for c in pts], [c["entropy_ratio"] for c in pts],
                marker=markers[i % len(markers)],
                ls=fs.LINESTYLES[i % len(fs.LINESTYLES)],
                color=fs.SERIES[i % len(fs.SERIES)], label=f"n={n}", alpha=0.9,
                markeredgecolor="black", markeredgewidth=0.4)
        for c in pts:
            ax.annotate(f"{c['refresh_hz']:.0f}Hz", (c["fpi"], c["entropy_ratio"]),
                        fontsize=5.5, alpha=0.6,
                        xytext=(2, 3), textcoords="offset points")

    rc = next(c for c in configs
              if (c["n"], c["refresh_hz"], c["epsilon"]) == rec_key)
    ax.scatter([rc["fpi"]], [rc["entropy_ratio"]], s=150, facecolors="none",
               edgecolors="black", linewidths=1.6, zorder=5,
               label=f"model-selected (n={rec['n']}@{rec['refresh_hz']:.0f}Hz)")

    ax.set_xlabel("FPI proxy (lower)")
    ax.set_ylabel("Normalized MI proxy (lower)")
    # title in LaTeX caption
    ax.grid(True)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3,
              handlelength=1.4, columnspacing=0.6, frameon=False, fontsize=7)
    fs.save(fig, "pareto_sweep")


if __name__ == "__main__":
    main()
