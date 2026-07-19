"""Apply the reviewed second-pass text placement to VSDX and vector PDF.

This is a deterministic Open XML/PDF-content adjustment.  It preserves every
shape and path while updating only the four text boxes whose publication-size
review required more vertical room or clearance from the display stand.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import xml.etree.ElementTree as ET

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, FloatObject


PAGE_XML = "visio/pages/page1.xml"
VISIO_NS = "http://schemas.microsoft.com/office/visio/2012/main"
SHAPE_TAG = f"{{{VISIO_NS}}}Shape"
SHAPES_TAG = f"{{{VISIO_NS}}}Shapes"
CELL_TAG = f"{{{VISIO_NS}}}Cell"
TEXT_TAG = f"{{{VISIO_NS}}}Text"
PX_TO_IN = 3.5 / 1536
PX_TO_PT = PX_TO_IN * 72
PAGE_HEIGHT_IN = 1024 * PX_TO_IN

ET.register_namespace("", VISIO_NS)

TEXT_RECTS = {
    "Temporal": (1300, 330, 200, 45),
    "integration": (1300, 375, 200, 45),
    "Short-exposure": (1020, 700, 300, 45),
    "sampling": (1020, 745, 300, 45),
}

# Existing vector text origins in the reviewed round-one PDF.  Exact origin
# checks prevent this script from silently moving an unrelated hyphen/run.
PDF_TEXT_MOVES = (
    ("Temporal", 211.06, 113.83, 4.1015625, -5.66015625),
    ("integration", 208.90, 107.93, 4.1015625, -7.13671875),
    ("Short", 168.02, 46.512, 0.0, 0.90234375),
    ("-", 184.99, 46.512, 0.0, 0.90234375),
    ("exposure", 187.15, 46.512, 0.0, 0.90234375),
    ("sampling", 177.77, 40.272, 0.0, -0.24609375),
)


def shape_text(shape: ET.Element) -> str:
    text = shape.find(TEXT_TAG)
    return "" if text is None else "".join(text.itertext()).strip()


def set_cell(shape: ET.Element, name: str, value: float) -> None:
    for cell in shape.findall(CELL_TAG):
        if cell.get("N") == name:
            cell.set("V", f"{value:.15g}")
            return
    raise ValueError(f"Shape {shape.get('ID', '?')} has no {name} cell")


def patch_text_shape(shape: ET.Element, rect: tuple[int, int, int, int]) -> None:
    x, y, width_px, height_px = rect
    width = width_px * PX_TO_IN
    height = height_px * PX_TO_IN
    pin_x = (x + width_px / 2) * PX_TO_IN
    pin_y = PAGE_HEIGHT_IN - (y + height_px / 2) * PX_TO_IN
    values = {
        "PinX": pin_x,
        "PinY": pin_y,
        "Width": width,
        "Height": height,
        "LocPinX": width / 2,
        "LocPinY": height / 2,
        "TxtPinX": width / 2,
        "TxtPinY": height / 2,
        "TxtWidth": width,
        "TxtHeight": height,
        "TxtLocPinX": width / 2,
        "TxtLocPinY": height / 2,
    }
    for name, value in values.items():
        set_cell(shape, name, value)


def patch_vsdx(input_path: Path, output_path: Path) -> None:
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output_path}")
    with ZipFile(input_path, "r") as src:
        members = [(info, src.read(info.filename)) for info in src.infolist()]

    page_payload = next(payload for info, payload in members if info.filename == PAGE_XML)
    root = ET.fromstring(page_payload)
    shapes = root.find(SHAPES_TAG)
    if shapes is None:
        raise RuntimeError("VSDX page has no top-level Shapes collection")

    matched: set[str] = set()
    for shape in shapes.findall(SHAPE_TAG):
        text = shape_text(shape)
        if text in TEXT_RECTS:
            if text in matched:
                raise RuntimeError(f"Duplicate target text shape: {text}")
            patch_text_shape(shape, TEXT_RECTS[text])
            matched.add(text)
    if matched != set(TEXT_RECTS):
        raise RuntimeError(f"Missing target text shapes: {sorted(set(TEXT_RECTS) - matched)}")

    patched_page = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=output_path.parent, suffix=".vsdx", delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        with ZipFile(temp_path, "w", compression=ZIP_DEFLATED) as dst:
            for info, payload in members:
                dst.writestr(info, patched_page if info.filename == PAGE_XML else payload)
        temp_path.replace(output_path)
    finally:
        temp_path.unlink(missing_ok=True)


def flattened_text(operands: list[object]) -> str:
    return "".join(
        str(item)
        for operand in operands
        for item in (operand if isinstance(operand, list) else [operand])
        if not isinstance(item, (int, float))
    )


def patch_pdf(input_path: Path, output_path: Path) -> None:
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output_path}")
    reader = PdfReader(str(input_path))
    if len(reader.pages) != 1:
        raise RuntimeError(f"Expected one PDF page, found {len(reader.pages)}")
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    page = writer.pages[0]
    content = ContentStream(page.get_contents(), reader)
    operations = content.operations

    matched: set[tuple[str, float, float]] = set()
    for index, (operands, operator) in enumerate(operations):
        if operator not in (b"Tj", b"TJ"):
            continue
        text = flattened_text(operands)
        for target, expected_x, expected_y, delta_x, delta_y in PDF_TEXT_MOVES:
            key = (target, expected_x, expected_y)
            if text != target or key in matched:
                continue
            matrix_index = next(
                (
                    candidate
                    for candidate in range(index - 1, max(-1, index - 9), -1)
                    if operations[candidate][1] == b"Tm"
                ),
                None,
            )
            if matrix_index is None:
                continue
            matrix = operations[matrix_index][0]
            actual_x = float(matrix[4])
            actual_y = float(matrix[5])
            if abs(actual_x - expected_x) > 0.02 or abs(actual_y - expected_y) > 0.02:
                continue
            matrix[4] = FloatObject(actual_x + delta_x)
            matrix[5] = FloatObject(actual_y + delta_y)
            matched.add(key)
            break

    expected = {(text, x, y) for text, x, y, _, _ in PDF_TEXT_MOVES}
    if matched != expected:
        missing = sorted(expected - matched)
        raise RuntimeError(f"Missing expected PDF text matrices: {missing}")

    page.replace_contents(content)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as stream:
        writer.write(stream)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-vsdx", type=Path, required=True)
    parser.add_argument("--output-vsdx", type=Path, required=True)
    parser.add_argument("--input-pdf", type=Path, required=True)
    parser.add_argument("--output-pdf", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    patch_vsdx(args.input_vsdx.resolve(), args.output_vsdx.resolve())
    patch_pdf(args.input_pdf.resolve(), args.output_pdf.resolve())
    print(f"Wrote {args.output_vsdx.resolve()}")
    print(f"Wrote {args.output_pdf.resolve()}")


if __name__ == "__main__":
    main()
