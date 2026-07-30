"""Patch two terminology labels while preserving the existing vector figures.

Run from the repository root in two stages:

1. Project Python (matplotlib installed):
   privacy-display/.venv/Scripts/python.exe <this-file> overlays
2. Bundled Codex Python (pypdf installed):
   <bundled-python> <this-file> merge

The split is necessary because the Windows checkout contains
``privacy-display/experiments`` as an unresolved macOS symlink, so the original
figure generators cannot run in this workspace.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path.cwd()
BUILD = ROOT / ".trellis" / "tasks" / "07-30-fix-paper-experiment-consistency" / "build"
FIGURES = ROOT / "paper" / "figures"


def _configure_matplotlib() -> None:
    import matplotlib

    matplotlib.use("Agg")
    matplotlib.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"],
            "pdf.fonttype": 42,
        }
    )


def _save_overlay(
    name: str,
    width_pt: float,
    height_pt: float,
    erase_rect: tuple[float, float, float, float],
    text_xy: tuple[float, float],
    text: str,
    *,
    rotation: float = 0,
    fontsize: float,
) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    fig = plt.figure(figsize=(width_pt / 72, height_pt / 72), dpi=72)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width_pt)
    ax.set_ylim(0, height_pt)
    ax.axis("off")
    ax.add_patch(Rectangle(erase_rect[:2], erase_rect[2], erase_rect[3],
                           facecolor="white", edgecolor="none"))
    ax.text(
        text_xy[0],
        text_xy[1],
        text,
        rotation=rotation,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="black",
    )
    fig.savefig(BUILD / name, format="pdf", transparent=True, dpi=72)
    plt.close(fig)


def make_overlays() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()
    _save_overlay(
        "multiengine_ocr_overlay.pdf",
        239.04375,
        179.52337,
        (0.0, 43.0, 18.0, 98.0),
        (10.0, 92.0),
        "Character recovery (%)",
        rotation=90,
        fontsize=9.5,
    )
    _save_overlay(
        "all_attackers_overlay.pdf",
        238.590625,
        202.525125,
        (42.0, 5.0, 55.0, 11.5),
        (69.412562, 10.5),
        "(char. recovery)",
        fontsize=7.5,
    )


def _operation_text(operands: list[object]) -> str:
    if not operands or not isinstance(operands[0], list):
        return ""
    return "".join(item for item in operands[0] if isinstance(item, str))


def _merge_one(base_name: str, overlay_name: str, old_text: str) -> None:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import ContentStream, NameObject

    source = FIGURES / base_name
    reader = PdfReader(source)
    page = reader.pages[0]
    content = ContentStream(page["/Contents"], reader)
    content.operations = [
        (operands, operator)
        for operands, operator in content.operations
        if not (operator == b"TJ" and _operation_text(operands) == old_text)
    ]
    page[NameObject("/Contents")] = content
    overlay = PdfReader(BUILD / overlay_name).pages[0]
    page.merge_page(overlay)

    writer = PdfWriter()
    writer.add_page(page)
    if reader.metadata:
        writer.add_metadata(reader.metadata)
    with (BUILD / base_name).open("wb") as handle:
        writer.write(handle)


def merge_overlays() -> None:
    _merge_one(
        "multiengine_ocr.pdf",
        "multiengine_ocr_overlay.pdf",
        "Char accuracy (%)",
    )
    _merge_one(
        "all_attackers.pdf",
        "all_attackers_overlay.pdf",
        "(char acc)",
    )


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"overlays", "merge"}:
        print("usage: patch_figure_metric_labels.py {overlays|merge}")
        return 2
    if sys.argv[1] == "overlays":
        make_overlays()
    else:
        merge_overlays()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
