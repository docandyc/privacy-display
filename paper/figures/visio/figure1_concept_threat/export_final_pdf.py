from __future__ import annotations

from pathlib import Path

import win32com.client


ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "final"
VSDX = FINAL / "figure1_concept_threat.vsdx"
PDF = FINAL / "figure1_concept_threat.pdf"


app = win32com.client.DispatchEx("Visio.Application")
app.Visible = False
try:
    doc = app.Documents.Open(str(VSDX))
    try:
        doc.ExportAsFixedFormat(1, str(PDF), 1, 0)
        print(f"Wrote {PDF}")
    finally:
        doc.Close()
finally:
    app.Quit()
