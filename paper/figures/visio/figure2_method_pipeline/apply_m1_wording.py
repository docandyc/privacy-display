"""Apply the approved M1 wording and measured text fits to Figure 2."""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
VSDX = ROOT / "final" / "figure2_method_pipeline.vsdx"
PAGE_XML = "visio/pages/page1.xml"
PAGE_WIDTH_PX = 1983
TARGET_WIDTH_IN = 7.16

TEXT_REPLACEMENTS = (
    ("1  Secure mask generation", "1  CSPRNG-based mask assignment"),
    ("2  GPU synthesis and temporal sequence", "2  Subframe composition and sequencing"),
    ("GPU subframe", "Offline subframe"),
    ("<cp IX='0'/>synthesis", "<cp IX='0'/>composition"),
    ("240-360 Hz", "nominal 240 Hz"),
    ("Unreadable", "Partially"),
    ("fragment", "observed subframe"),
)


def _replacement_state(page_xml: str) -> str:
    old_counts = {old: page_xml.count(old) for old, _ in TEXT_REPLACEMENTS}
    new_counts = {new: page_xml.count(new) for _, new in TEXT_REPLACEMENTS}
    if all(count == 1 for count in old_counts.values()) and all(
        count == 0 for count in new_counts.values()
    ):
        return "old"
    if all(count == 0 for count in old_counts.values()) and all(
        count == 1 for count in new_counts.values()
    ):
        return "new"
    raise RuntimeError(
        "Figure 2 VSDX is in an unexpected mixed wording state: "
        f"old={old_counts}, new={new_counts}"
    )


def _rewrite_package(source: Path, output: Path) -> str:
    with ZipFile(source, "r") as src:
        members = [(info, src.read(info.filename)) for info in src.infolist()]

    state = ""
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as dst:
        for info, payload in members:
            if info.filename == PAGE_XML:
                page_xml = payload.decode("utf-8")
                state = _replacement_state(page_xml)
                if state == "old":
                    for old, new in TEXT_REPLACEMENTS:
                        page_xml = page_xml.replace(old, new, 1)
                payload = page_xml.encode("utf-8")
            dst.writestr(info, payload)
    if not state:
        raise RuntimeError(f"missing {PAGE_XML} in {source}")
    return state


def _scene_px_to_inches(value: float) -> float:
    return value * TARGET_WIDTH_IN / PAGE_WIDTH_PX


def _apply_measured_text_fits(path: Path) -> None:
    env = os.environ.copy()
    env["FIGURE2_M1_VSDX"] = str(path.resolve())
    powershell = f"""
$ErrorActionPreference = 'Stop'
$app = New-Object -ComObject Visio.Application
try {{
    $app.Visible = $false
    $doc = $app.Documents.Open($env:FIGURE2_M1_VSDX)
    try {{
        $page = $doc.Pages.Item(1)
        $stage1 = $page.Shapes.ItemFromID(14)
        $stage1.CellsU('Width').FormulaU = '{_scene_px_to_inches(510):.12f} in'
        $stage1.CellsU('TxtWidth').FormulaU = 'Width'
        $stage1.CellsU('Char.Size').FormulaU = '7.2 pt'

        $observed = $page.Shapes.ItemFromID(765)
        $observed.CellsU('PinX').FormulaU = '{_scene_px_to_inches(1760):.12f} in'
        $observed.CellsU('Width').FormulaU = '{_scene_px_to_inches(270):.12f} in'
        $observed.CellsU('TxtWidth').FormulaU = 'Width'
        $observed.CellsU('Char.Size').FormulaU = '6.5 pt'
        $doc.Save() | Out-Null
    }} finally {{
        $doc.Close() | Out-Null
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc) | Out-Null
    }}
}} finally {{
    $app.Quit()
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) | Out-Null
}}
"""
    subprocess.run(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", powershell],
        check=True,
        env=env,
    )


def patch_vsdx(*, refresh_fits: bool = False) -> None:
    with NamedTemporaryFile(dir=VSDX.parent, suffix=".vsdx", delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        state = _rewrite_package(VSDX, temp_path)
        if state == "new" and not refresh_fits:
            print(f"already patched {VSDX}")
            return
        _apply_measured_text_fits(temp_path)
        temp_path.replace(VSDX)
        action = "refreshed text fits in" if state == "new" else "patched"
        print(f"{action} {VSDX}")
    finally:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh-fits",
        action="store_true",
        help="Reapply measured text-box geometry when wording is already patched.",
    )
    patch_vsdx(refresh_fits=parser.parse_args().refresh_fits)
