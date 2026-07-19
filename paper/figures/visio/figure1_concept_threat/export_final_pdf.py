from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "final"
VSDX = FINAL / "figure1_concept_threat.vsdx"
PDF = FINAL / "figure1_concept_threat.pdf"


def export_with_pywin32(vsdx: Path, pdf: Path) -> bool:
    try:
        import win32com.client
    except ModuleNotFoundError:
        return False

    app = win32com.client.DispatchEx("Visio.Application")
    app.Visible = False
    try:
        doc = app.Documents.Open(str(vsdx))
        try:
            # 1 = PDF, 1 = print intent, 0 = all pages.
            doc.ExportAsFixedFormat(1, str(pdf), 1, 0)
        finally:
            doc.Close()
    finally:
        app.Quit()
    return True


def export_with_powershell(vsdx: Path, pdf: Path) -> None:
    env = os.environ.copy()
    env["FIGURE1_EXPORT_VSDX"] = str(vsdx.resolve())
    env["FIGURE1_EXPORT_PDF"] = str(pdf.resolve())
    powershell = """
$ErrorActionPreference = 'Stop'
$app = New-Object -ComObject Visio.Application
try {
    $app.Visible = $false
    $doc = $app.Documents.Open($env:FIGURE1_EXPORT_VSDX)
    try {
        $doc.ExportAsFixedFormat(1, $env:FIGURE1_EXPORT_PDF, 1, 0)
    } finally {
        $doc.Close() | Out-Null
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc) | Out-Null
    }
} finally {
    $app.Quit()
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) | Out-Null
}
"""
    subprocess.run(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", powershell],
        check=True,
        env=env,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Figure 1 VSDX to a single-page PDF.")
    parser.add_argument("--vsdx", type=Path, default=VSDX)
    parser.add_argument("--pdf", type=Path, default=PDF)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    vsdx = args.vsdx.resolve()
    pdf = args.pdf.resolve()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if not export_with_pywin32(vsdx, pdf):
        export_with_powershell(vsdx, pdf)
    print(f"Wrote {pdf}")


if __name__ == "__main__":
    main()
