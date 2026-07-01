"""Shared matplotlib style + helpers for the paper figures.

All paper data figures import this module so that font, sizing, palette and the
headless/vector-PDF setup live in exactly one place (previously duplicated in
``src/evaluation/benchmark.py`` and ``experiments/pareto_sweep.py``).

Design choices:
* English labels (IEEE Access is an English venue) -> no CJK font needed.
* Vector PDF output with ``pdf.fonttype=42`` (embed TrueType, avoid Type-3).
* IEEE Access column widths: single ``COL_W`` in, double ``FULL_W`` in.
* One colour per protection grade, kept consistent across every figure.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

# Headless + writable cache dir must be set before importing pyplot.
os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "privacy-display-matplotlib")
)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[2]          # privacy-display/
RESULTS = ROOT / "experiments" / "results"
REPO = ROOT.parent                                  # repo root
FIG_OUT = REPO / "paper" / "figures"                # paper/figures/*.pdf

# ---------------------------------------------------------------- sizes (inches)
COL_W = 3.5      # IEEE Access single column (\columnwidth)
FULL_W = 7.16    # IEEE Access double column (\textwidth, figure*)

# ---------------------------------------------------------------- palette
# Saturated qualitative palette (matches the user's SCI plotting convention:
# red / blue / green / purple / orange named colours + distinct line styles),
# with one stable colour per protection grade / attack state.
GRADE_COLORS = {
    "original": "dimgray",          # neutral — unprotected baseline
    "unprotected": "dimgray",
    "clean": "dimgray",
    "mask_only": "green",
    "mask_noise": "teal",
    "deployed": "blue",             # blue  — readable / deployed grade
    "anti_ocr": "purple",           # purple
    "vlm": "red",                   # red   — capture-hardened grade
    "capture_hardened": "red",
    "protected": "blue",
}
# Qualitative series palette + line styles for multi-series comparison plots.
SERIES = ["blue", "red", "green", "purple", "orange", "dimgray"]
LINESTYLES = ["-", "--", ":", "-."]


def _apply_rc() -> None:
    matplotlib.rcParams.update({
        # SCI-standard typography: serif / Times New Roman, STIX math.
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8,
        # Boxed legend: white face, grey edge, rounded.
        "legend.frameon": True,
        "legend.facecolor": "white",
        "legend.edgecolor": "0.5",
        "legend.fancybox": True,
        "legend.framealpha": 0.9,
        # Embed TrueType (avoid Type-3) for the vector PDFs.
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        # Boxed axes with inward ticks on all four sides.
        "axes.linewidth": 0.8,
        "axes.grid": False,
        "axes.axisbelow": True,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "xtick.major.size": 3.5,
        "ytick.major.size": 3.5,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.minor.visible": False,
        # Faint grid (only shown where a script explicitly enables it).
        "grid.color": "0.85",
        "grid.linewidth": 0.5,
        "grid.alpha": 0.7,
        "lines.linewidth": 1.6,
        "lines.markersize": 5,
        "savefig.dpi": 600,
        "figure.dpi": 150,
    })


_apply_rc()


# ---------------------------------------------------------------- data helpers
def load(name: str) -> dict:
    """Load a results JSON by file name from experiments/results/."""
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def mean_hw(node) -> tuple[float | None, float | None]:
    """Return (mean, ci95_half_width) from a ``{mean, ci95:{half_width}}`` metric
    dict, or (value, None) for a bare scalar."""
    if isinstance(node, dict):
        ci = node.get("ci95") or {}
        hw = ci.get("half_width") if isinstance(ci, dict) else None
        return node.get("mean"), hw
    return node, None


def pct(node) -> float:
    """Mean of a metric expressed as a percentage (0-100)."""
    v, _ = mean_hw(node)
    return (v or 0.0) * 100.0


def pct_err(node) -> float:
    """CI95 half-width of a metric as a percentage, 0 if absent."""
    _, hw = mean_hw(node)
    return (hw or 0.0) * 100.0


def save(fig, stem: str) -> Path:
    """Write ``paper/figures/<stem>.pdf`` (vector) and close the figure."""
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    out = FIG_OUT / f"{stem}.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[figstyle] saved {out}")
    return out
