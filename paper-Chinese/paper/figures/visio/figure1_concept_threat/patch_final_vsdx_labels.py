"""Apply the reviewed Figure 1 label corrections to the editable final VSDX.

The final diagram was authored in Visio on Windows, while this repository is
also built on macOS.  VSDX files are ZIP packages, so the two text-only fixes
can be applied deterministically without changing geometry or shape IDs.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parent
VSDX = ROOT / "final" / "figure1_concept_threat.vsdx"
PAGE_XML = "visio/pages/page1.xml"


def main() -> None:
    with ZipFile(VSDX, "r") as src:
        members = [(info, src.read(info.filename)) for info in src.infolist()]

    replaced_sampling = 0
    removed_time = 0
    rewritten: list[tuple[ZipInfo, bytes]] = []
    for info, payload in members:
        if info.filename == PAGE_XML:
            text = payload.decode("utf-8")
            replaced_sampling = text.count("Instantaneous")
            removed_time = text.count("≈ 50 ms")
            text = text.replace("Instantaneous", "Short-exposure")
            text = text.replace("≈ 50 ms", "")
            payload = text.encode("utf-8")
        rewritten.append((info, payload))

    already_patched = replaced_sampling == 0 and removed_time == 0
    if already_patched:
        page_text = next(
            payload.decode("utf-8")
            for info, payload in rewritten
            if info.filename == PAGE_XML
        )
        if page_text.count("Short-exposure") != 1:
            raise RuntimeError("Figure 1 VSDX is neither original nor patched")
        print(f"already patched {VSDX}")
        return
    if replaced_sampling != 1 or removed_time != 1:
        raise RuntimeError(
            f"unexpected source counts: Instantaneous={replaced_sampling}, "
            f"≈ 50 ms={removed_time}"
        )

    with NamedTemporaryFile(dir=VSDX.parent, suffix=".vsdx", delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        with ZipFile(temp_path, "w", compression=ZIP_DEFLATED) as dst:
            for info, payload in rewritten:
                dst.writestr(info, payload)
        temp_path.replace(VSDX)
    finally:
        temp_path.unlink(missing_ok=True)

    print(f"patched {VSDX}")


if __name__ == "__main__":
    main()
