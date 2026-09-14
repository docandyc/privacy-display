"""Plot Fig. 6 as participant-level paired changes with estimation summaries."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "analysis_data" / "typing_participant_means.csv"
SEED = 20260703
BOOTSTRAP_SAMPLES = 10_000

METRICS = (
    {
        "key": "accuracy",
        "title": "Accuracy",
        "ylabel": "Change (percentage points)",
        "scale": 100.0,
        "direction": 1.0,
        "tick": 10.0,
        "decimals": 2,
        "definition": "(Mask - Ctrl) x 100",
    },
    {
        "key": "wpm",
        "title": "Typing speed",
        "ylabel": "Change (WPM)",
        "scale": 1.0,
        "direction": 1.0,
        "tick": 4.0,
        "decimals": 2,
        "definition": "Mask - Ctrl",
    },
    {
        "key": "first_key_latency_ms",
        "title": "First-key latency",
        "ylabel": "Change (ms)",
        "scale": 1.0,
        "direction": -1.0,
        "tick": 1000.0,
        "decimals": 1,
        "definition": "Ctrl - Mask (sign reversed so positive is better)",
    },
)


def bootstrap_mean_ci(values: np.ndarray, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(BOOTSTRAP_SAMPLES, values.size))
    boot_means = values[indices].mean(axis=1)
    low, high = np.quantile(boot_means, (0.025, 0.975))
    return float(low), float(high)


def load_rows() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 106
    assert len({row["participant_code"] for row in rows}) == 106
    return rows


def apply_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 6.4,
            "axes.labelsize": 6.7,
            "axes.titlesize": 7.2,
            "xtick.labelsize": 5.8,
            "ytick.labelsize": 5.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "axes.linewidth": 0.75,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def main() -> None:
    rows = load_rows()
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    apply_style()

    fig, axes = plt.subplots(1, 3, figsize=(5.3, 2.25))
    jitter_rng = np.random.default_rng(SEED)
    summaries: list[dict[str, object]] = []
    plotted: dict[str, np.ndarray] = {}

    for ax, spec in zip(axes, METRICS):
        key = str(spec["key"])
        raw_delta = np.array(
            [float(row[f"masked_{key}"]) - float(row[f"control_{key}"]) for row in rows],
            dtype=float,
        )
        delta = raw_delta * float(spec["scale"]) * float(spec["direction"])
        plotted[key] = delta
        mean = float(delta.mean())
        sd = float(delta.std(ddof=1))
        ci_low, ci_high = bootstrap_mean_ci(delta, SEED)

        violin = ax.violinplot(
            delta,
            positions=[0.0],
            widths=0.48,
            showmeans=False,
            showmedians=False,
            showextrema=False,
            bw_method=0.35,
        )
        for body in violin["bodies"]:
            body.set_facecolor("#D9D9D9")
            body.set_edgecolor("#A8A8A8")
            body.set_linewidth(0.45)
            body.set_alpha(0.55)

        jitter = np.clip(jitter_rng.normal(0.0, 0.055, delta.size), -0.15, 0.15)
        ax.scatter(
            jitter,
            delta,
            s=5.0,
            color="#707070",
            alpha=0.42,
            linewidths=0,
            rasterized=True,
            zorder=2,
        )
        ax.errorbar(
            0.52,
            mean,
            yerr=[[mean - ci_low], [ci_high - mean]],
            fmt="D",
            color="#2929EF",
            markeredgecolor="#16168C",
            markeredgewidth=0.45,
            markersize=4.2,
            elinewidth=1.0,
            capsize=2.3,
            capthick=1.0,
            zorder=4,
        )
        ax.axhline(0.0, color="#4C4C4C", linewidth=0.7, linestyle=(0, (3, 2)), zorder=0)

        max_abs = float(np.max(np.abs(delta)))
        tick = float(spec["tick"])
        limit = np.ceil((max_abs * 1.08) / tick) * tick
        ax.set_ylim(-limit, limit)
        ax.yaxis.set_major_locator(MultipleLocator(tick))
        ax.set_xlim(-0.34, 0.78)
        ax.set_xticks([0.0, 0.52], labels=["Individuals", "Mean"])
        ax.set_title(str(spec["title"]), pad=4.0)
        ax.set_ylabel(str(spec["ylabel"]), labelpad=2.0)
        ax.tick_params(top=True, right=True, length=2.5, width=0.7)
        ax.text(
            0.52,
            ci_high + 0.045 * (2 * limit),
            f"{mean:+.{int(spec['decimals'])}f}",
            color="#16168C",
            fontsize=5.8,
            ha="center",
            va="bottom",
        )

        summaries.append(
            {
                "metric": key,
                "n": len(rows),
                "displayed_change": spec["definition"],
                "mean": mean,
                "sd": sd,
                "bootstrap_95ci_low": ci_low,
                "bootstrap_95ci_high": ci_high,
                "participants_better": int(np.sum(delta > 1e-12)),
                "participants_worse": int(np.sum(delta < -1e-12)),
                "participants_unchanged": int(np.sum(np.abs(delta) <= 1e-12)),
            }
        )

    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.19, top=0.88, wspace=0.78)
    fig.text(
        0.5,
        0.035,
        "Positive values indicate improved performance under masking.",
        ha="center",
        va="bottom",
        fontsize=5.9,
    )

    for extension in ("png", "pdf", "svg"):
        fig.savefig(HERE / f"Fig6_delta_estimation.{extension}")
    plt.close(fig)

    with (HERE / "summary.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    with (HERE / "participant_changes.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = ["participant_code", *[str(spec["key"]) for spec in METRICS]]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row_index, row in enumerate(rows):
            writer.writerow(
                {
                    "participant_code": row["participant_code"],
                    **{str(spec["key"]): plotted[str(spec["key"])][row_index] for spec in METRICS},
                }
            )

    manifest = {
        "source": str(SOURCE),
        "source_sha256": source_hash,
        "n": len(rows),
        "bootstrap_samples": BOOTSTRAP_SAMPLES,
        "seed": SEED,
        "figure_encoding": {
            "gray_points": "participant-level paired changes",
            "gray_violin": "distribution density",
            "blue_diamond": "mean paired change",
            "blue_error_bar": "participant bootstrap 95% confidence interval for the mean paired change",
            "zero_line": "no within-subject change",
            "direction": "positive values indicate improved performance; first-key latency sign is reversed",
        },
    }
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
