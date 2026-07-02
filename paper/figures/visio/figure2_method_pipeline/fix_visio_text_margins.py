from __future__ import annotations

from pathlib import Path

import win32com.client


ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "final"
VSDX = FINAL / "figure2_method_pipeline.vsdx"


app = win32com.client.DispatchEx("Visio.Application")
app.Visible = False
try:
    doc = app.Documents.Open(str(VSDX))
    try:
        page = doc.Pages.Item(1)
        changed = 0
        replacements = {
            "1  Source and secure decomposition": "1  Secure mask generation",
            "sum": "Σ",
            "sum ": "Σ ",
            " = I * ": " = I ⊙ ",
            "about 50 ms": "≈ 50 ms",
            "OCR x": "OCR ×",
        }
        for shape in page.Shapes:
            try:
                text = str(shape.Text or "")
            except Exception:
                text = ""
            if not text.strip():
                continue
            if text in replacements:
                shape.Text = replacements[text]
                text = replacements[text]
            if text == "Unreadable":
                shape.CellsU("Width").FormulaU = "0.62 in"
                shape.CellsU("TxtWidth").FormulaU = "0.62 in"
            for cell_name, formula in (
                ("LeftMargin", "0.01 in"),
                ("RightMargin", "0.01 in"),
                ("TopMargin", "0 in"),
                ("BottomMargin", "0 in"),
            ):
                shape.CellsU(cell_name).FormulaU = formula
            changed += 1
        doc.Save()
        page.Export(str(FINAL / "figure2_method_pipeline.svg"))
        page.Export(str(FINAL / "figure2_method_pipeline.png"))
        print(f"Updated text margins on {changed} shapes")
    finally:
        doc.Close()
finally:
    app.Quit()
