from __future__ import annotations

from pathlib import Path

import win32com.client


ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "final"
VSDX = FINAL / "figure2_method_pipeline.vsdx"
PDF = FINAL / "figure2_method_pipeline.pdf"


app = win32com.client.DispatchEx("Visio.Application")
app.Visible = False
try:
    doc = app.Documents.Open(str(VSDX))
    try:
        # 1 = PDF, 1 = print intent, 0 = all pages.
        doc.ExportAsFixedFormat(1, str(PDF), 1, 0)
        print(f"Wrote {PDF}")
    finally:
        doc.Close()
finally:
    app.Quit()
