from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "final"
VSDX = FINAL / "figure2_method_pipeline.vsdx"
PDF = FINAL / "figure2_method_pipeline.pdf"


def export_with_pywin32() -> bool:
    try:
        import win32com.client
    except ModuleNotFoundError:
        return False

    app = win32com.client.DispatchEx("Visio.Application")
    app.Visible = False
    try:
        doc = app.Documents.Open(str(VSDX))
        try:
            # 1 = PDF, 1 = print intent, 0 = all pages.
            doc.ExportAsFixedFormat(1, str(PDF), 1, 0)
        finally:
            doc.Close()
    finally:
        app.Quit()
    return True


def export_with_powershell() -> None:
    env = os.environ.copy()
    env["FIGURE2_EXPORT_VSDX"] = str(VSDX.resolve())
    env["FIGURE2_EXPORT_PDF"] = str(PDF.resolve())
    powershell = """
$ErrorActionPreference = 'Stop'
$app = New-Object -ComObject Visio.Application
try {
    $app.Visible = $false
    $doc = $app.Documents.Open($env:FIGURE2_EXPORT_VSDX)
    try {
        $doc.ExportAsFixedFormat(1, $env:FIGURE2_EXPORT_PDF, 1, 0)
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


def main() -> None:
    if not export_with_pywin32():
        export_with_powershell()
    print(f"Wrote {PDF}")


if __name__ == "__main__":
    main()
