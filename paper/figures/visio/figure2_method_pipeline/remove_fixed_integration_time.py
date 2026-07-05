"""Remove the unsupported fixed integration time from Figure 2 assets."""
from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream


ROOT = Path(__file__).resolve().parent
VSDX = ROOT / "final" / "figure2_method_pipeline.vsdx"
PDF = ROOT / "final" / "figure2_method_pipeline.pdf"
PAGE_XML = "visio/pages/page1.xml"


def patch_vsdx() -> None:
    with ZipFile(VSDX, "r") as src:
        members = [(info, src.read(info.filename)) for info in src.infolist()]
    count = 0
    rewritten = []
    for info, payload in members:
        if info.filename == PAGE_XML:
            text = payload.decode("utf-8")
            count = text.count("≈ 50 ms")
            payload = text.replace("≈ 50 ms", "").encode("utf-8")
        rewritten.append((info, payload))
    if count == 0:
        print(f"already patched {VSDX}")
        return
    if count != 1:
        raise RuntimeError(f"unexpected ≈ 50 ms count in VSDX: {count}")
    with NamedTemporaryFile(dir=VSDX.parent, suffix=".vsdx", delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        with ZipFile(temp_path, "w", compression=ZIP_DEFLATED) as dst:
            for info, payload in rewritten:
                dst.writestr(info, payload)
        temp_path.replace(VSDX)
    finally:
        temp_path.unlink(missing_ok=True)


def patch_pdf() -> None:
    reader = PdfReader(str(PDF))
    page = reader.pages[0]
    content = ContentStream(page.get_contents(), reader)
    kept = []
    removed = []
    for operands, operator in content.operations:
        flattened = ""
        if operator in (b"Tj", b"TJ"):
            flattened = "".join(
                str(item)
                for operand in operands
                for item in (operand if isinstance(operand, list) else [operand])
                if not isinstance(item, (int, float))
            )
        if flattened in {"50 ms", "\x01,"}:
            removed.append(flattened)
            continue
        kept.append((operands, operator))
    if not removed:
        print(f"already patched {PDF}")
        return
    if "50 ms" not in removed:
        raise RuntimeError(f"fixed integration time not found in PDF: {removed}")
    content.operations = kept
    page.replace_contents(content)
    writer = PdfWriter()
    writer.add_page(page)
    with NamedTemporaryFile(dir=PDF.parent, suffix=".pdf", delete=False) as tmp:
        temp_path = Path(tmp.name)
        writer.write(tmp)
    try:
        temp_path.replace(PDF)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> None:
    patch_vsdx()
    patch_pdf()
    print(f"patched {VSDX} and {PDF}")


if __name__ == "__main__":
    main()
