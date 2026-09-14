"""Reproduce the explicitly requested, post-hoc per-metric trim of Fig. 6."""
from pathlib import Path
import csv
import hashlib
import json
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / "analysis_data/typing_participant_means.csv"
SEED = 20260703
B = 10000
METRICS = [
    ("accuracy", "Accuracy (%)", 100.0),
    ("wpm", "WPM", 1.0),
    ("first_key_latency_ms", "First-key\nlatency (ms)", 1.0),
]


def write_csv(name, rows):
    with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(a, b):
    rng = np.random.default_rng(SEED)
    indices = rng.integers(0, len(a), size=(B, len(a)))
    result = {"n": len(a)}
    for name, values in [("control", a), ("masked", b), ("difference", b-a)]:
        lo, hi = np.quantile(values[indices].mean(axis=1), [.025, .975])
        result.update({f"{name}_mean": float(values.mean()),
                       f"{name}_sd": float(values.std(ddof=1)),
                       f"{name}_ci_low": float(lo), f"{name}_ci_high": float(hi)})
    return result


def main(trim=3, output_dir=None):
    global OUT
    OUT = Path(output_dir).resolve() if output_dir else Path(__file__).resolve().parent
    OUT.mkdir(parents=True, exist_ok=True)
    if not 0 <= trim < 53:
        raise ValueError("trim must leave at least two participants")
    original_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 106
    assert len({r["participant_code"] for r in rows}) == len(rows)
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
                         "mathtext.fontset": "stix", "font.size": 9, "axes.labelsize": 11,
                         "xtick.direction": "in", "ytick.direction": "in", "pdf.fonttype": 42,
                         "savefig.dpi": 600, "figure.facecolor": "white", "axes.facecolor": "white"})
    fig, axes = plt.subplots(1, 3, figsize=(5.5, 3.3))
    summary, membership, exclusions = [], [], []
    for ax, (metric, label, scale) in zip(axes, METRICS):
        ordered = sorted(rows, key=lambda r: (float(r[f"masked_{metric}"])-float(r[f"control_{metric}"]), r["participant_code"]))
        low = {r["participant_code"] for r in ordered[:trim]}
        high = {r["participant_code"] for r in ordered[-trim:]} if trim else set()
        assert low.isdisjoint(high)
        kept = []
        for r in rows:
            a, b = float(r[f"control_{metric}"])*scale, float(r[f"masked_{metric}"])*scale
            assert np.isfinite([a,b]).all()
            assert np.isclose((b-a)/scale, float(r[f"delta_{metric}"]))
            status = f"lowest_{trim}" if r["participant_code"] in low else f"highest_{trim}" if r["participant_code"] in high else "retained"
            record = {"metric": metric, "participant_code": r["participant_code"], "status": status,
                      "control": a, "masked": b, "delta_masked_minus_control": b-a}
            membership.append(record)
            if status == "retained":
                kept.append(record)
            else:
                exclusions.append(record)
        assert len(kept) == len(rows) - 2 * trim
        assert all(r["delta_masked_minus_control"] < 0 for r in exclusions if r["metric"] == metric and r["status"] == f"lowest_{trim}")
        assert all(r["delta_masked_minus_control"] > 0 for r in exclusions if r["metric"] == metric and r["status"] == f"highest_{trim}")
        for sample, records in [("original", [r for r in membership if r["metric"] == metric]), ("trimmed", kept)]:
            a, b = np.array([r["control"] for r in records]), np.array([r["masked"] for r in records])
            stats = summarize(a, b)
            summary.append({"metric": metric, "sample": sample, **stats})
        write_csv(f"retained_{metric}.csv", kept)
        for r in kept:
            ax.plot([0,1], [r["control"],r["masked"]], color="0.7", alpha=.45, linewidth=.55, zorder=1)
        for x, name, color in [(0,"control","#666666"),(1,"masked","#2929EF")]:
            m = stats[f"{name}_mean"]
            ax.errorbar(x,m, yerr=[[m-stats[f"{name}_ci_low"]],[stats[f"{name}_ci_high"]-m]],
                        fmt="o", color=color, markersize=5.5, capsize=3, linewidth=1.2, zorder=3)
        ax.set(xlim=(-.45,1.45), xticks=[0,1], xticklabels=["Ctrl","Mask"], ylabel=label)
        ax.set_title(f"n = {len(kept)}", fontsize=9)
        ax.tick_params(top=True, right=True)
        if metric == "accuracy":
            ax.set_ylim(min(r["control"] for r in kept + [{"control": r["masked"]} for r in kept])-1, 101)
    fig.subplots_adjust(left=.12, right=.98, bottom=.22, top=.89, wspace=1.25)
    fig.text(.5,.075,f"Post-hoc sensitivity analysis: {trim} participants removed from each tail per metric.", ha="center", fontsize=7)
    fig.text(.5,.035,"Participant sets differ across panels; dots: means; error bars: bootstrap 95% CIs.", ha="center", fontsize=7)
    for ext in ["png","pdf","svg"]:
        fig.savefig(OUT / f"Fig6_trimmed_sensitivity.{ext}")
    plt.close(fig)
    write_csv("summary_comparison.csv", summary)
    write_csv("membership_all_metrics.csv", membership)
    write_csv("excluded_participants.csv", exclusions)
    manifest = {"source": str(SOURCE), "source_sha256": original_hash, "seed": SEED,
                "bootstrap_samples": B, "trim_per_tail": trim, "rule": f"Per metric, sort masked-control; remove first {trim} and last {trim}; break exact ties by participant_code ascending.",
                "interpretation": "Post-hoc descriptive sensitivity analysis. Bootstrap conditional on selected retained sample; selection is not repeated in resamples. No confirmatory p-values.",
                "original_n": len(rows), "retained_n_per_metric": len(rows) - 2 * trim}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
    report = [f"# Fig.6 两端各去除 {trim} 人的敏感性分析", "",
              f"按用户指定，三个指标分别以 Mask−Ctrl 排序，去掉差值最小的 {trim} 人和最大的 {trim} 人。每幅图由 106 人变为 {len(rows) - 2 * trim} 人，三幅图的受试者集合不同。准确率以百分比表示，其差值单位为百分点；WPM 和延迟分别使用 WPM 和 ms。完全相同的差值按匿名编号升序打破平局。", "",
              f"原始数据与论文原图均保留。这里的极端变化不等于无效数据，固定去除两端各 {trim} 人是事后筛选，不是经验证的异常值判断。", "",
              "| 指标 | 样本 | N | Ctrl 均值 | Mask 均值 | Mask−Ctrl | 差值 95% CI |",
              "|---|---|---:|---:|---:|---:|---|" ]
    for r in summary:
        report.append(f"| {r['metric']} | {r['sample']} | {r['n']} | {r['control_mean']:.4f} | {r['masked_mean']:.4f} | {r['difference_mean']:.4f} | [{r['difference_ci_low']:.4f}, {r['difference_ci_high']:.4f}] |")
    report += ["", "## 排除名单", ""]
    for metric, _, _ in METRICS:
        for status in [f"lowest_{trim}", f"highest_{trim}"]:
            selected = [r for r in exclusions if r["metric"] == metric and r["status"] == status]
            report.append(f"- {metric} / {status}: " + "; ".join(f"{r['participant_code']} (Δ={r['delta_masked_minus_control']:.4f})" for r in selected))
    report += ["", f"置信区间使用参与者配对 bootstrap，10,000 次、固定种子 20260703。图中误差线为各条件均值的区间，表中为配对均值差区间。重采样固定在已筛选的 {len(rows) - 2 * trim} 人内，没有在每次重采样时重新筛选，因而没有纳入事后选样带来的不确定性；不据此作总体显著性结论。未重新计算用于确认性结论的 p 值。", "",
               f"所有汇总值及标准差见 summary_comparison.csv，各指标完整纳入/排除状态见 membership_all_metrics.csv。用本脚本运行 --trim {trim} 并指定本输出目录可复现图片与表格。"]
    (OUT / "重算说明.md").write_text("\n".join(report)+"\n", encoding="utf-8")
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == original_hash
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trim", type=int, default=3, help="participants removed from each tail per metric")
    parser.add_argument("--output-dir", type=Path, help="directory for outputs; defaults to this script's directory")
    args = parser.parse_args()
    main(trim=args.trim, output_dir=args.output_dir)
