from __future__ import annotations

import argparse
from pathlib import Path

import win32com.client


def update_margins(vsdx: Path) -> int:
    app = win32com.client.DispatchEx("Visio.Application")
    app.Visible = False
    try:
        doc = app.Documents.Open(str(vsdx))
        try:
            page = doc.Pages.Item(1)
            changed = 0
            for shape in page.Shapes:
                try:
                    text = str(shape.Text or "")
                except Exception:
                    text = ""
                if not text.strip():
                    continue
                for cell_name, formula in (
                    ("LeftMargin", "0.005 in"),
                    ("RightMargin", "0.005 in"),
                    ("TopMargin", "0 in"),
                    ("BottomMargin", "0 in"),
                ):
                    shape.CellsU(cell_name).FormulaU = formula
                changed += 1
            doc.Save()
            return changed
        finally:
            doc.Close()
    finally:
        app.Quit()


def export_fresh(vsdx: Path) -> None:
    app = win32com.client.DispatchEx("Visio.Application")
    app.Visible = False
    try:
        doc = app.Documents.Open(str(vsdx))
        try:
            page = doc.Pages.Item(1)
            page.Export(str(vsdx.with_suffix(".svg")))
            page.Export(str(vsdx.with_suffix(".png")))
        finally:
            doc.Close()
    finally:
        app.Quit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("vsdx", type=Path)
    args = parser.parse_args()
    vsdx = args.vsdx.resolve()
    changed = update_margins(vsdx)
    export_fresh(vsdx)
    print(f"Updated text margins on {changed} shapes")
    print(f"Re-exported {vsdx.with_suffix('.svg')}")
    print(f"Re-exported {vsdx.with_suffix('.png')}")


if __name__ == "__main__":
    main()
