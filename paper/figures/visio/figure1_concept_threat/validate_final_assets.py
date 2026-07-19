"""Validate final Figure 1 deliverables and the preserved canonical left panel."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
BASELINE_VSDX = ROOT / "review" / "supervisor_revision" / "baseline" / "figure1_concept_threat.prior.vsdx"
ENGLISH_FINAL = ROOT / "final"
CHINESE_FINAL = (
    ROOT.parents[3]
    / "paper-Chinese"
    / "figures"
    / "visio"
    / "figure1_concept_threat"
    / "final"
)

PAGE_XML = "visio/pages/page1.xml"
VISIO_NS = "http://schemas.microsoft.com/office/visio/2012/main"
SHAPE_TAG = f"{{{VISIO_NS}}}Shape"
SHAPES_TAG = f"{{{VISIO_NS}}}Shapes"
CELL_TAG = f"{{{VISIO_NS}}}Cell"
TEXT_TAG = f"{{{VISIO_NS}}}Text"
DIVIDER_X_IN = 720 / 1536 * 3.5
DIVIDER_TOLERANCE_IN = 0.03
REVISION_RED = "#d94722"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_root(path: Path) -> ET.Element:
    with ZipFile(path, "r") as archive:
        return ET.fromstring(archive.read(PAGE_XML))


def cell_value(shape: ET.Element, name: str) -> float:
    for cell in shape.findall(CELL_TAG):
        if cell.get("N") == name:
            value = cell.get("V")
            if value is not None:
                return float(value)
    raise AssertionError(f"Shape {shape.get('ID', '?')} has no numeric {name} cell")


def cell_text(shape: ET.Element, name: str) -> str:
    for cell in shape.findall(CELL_TAG):
        if cell.get("N") == name:
            return str(cell.get("V", ""))
    return ""


def shape_text(shape: ET.Element) -> str:
    text = shape.find(TEXT_TAG)
    return "" if text is None else "".join(text.itertext()).strip()


def is_left_panel_shape(shape: ET.Element) -> bool:
    pin_x = cell_value(shape, "PinX")
    is_divider = (
        abs(pin_x - DIVIDER_X_IN) <= DIVIDER_TOLERANCE_IN
        and cell_value(shape, "Width") <= 0.03
        and cell_value(shape, "Height") >= 2.0
    )
    return not is_divider and pin_x < DIVIDER_X_IN


def normalized_left_shapes(path: Path) -> list[bytes]:
    root = page_root(path)
    shapes = root.find(SHAPES_TAG)
    require(shapes is not None, f"{path} has no Shapes collection")
    normalized: list[bytes] = []
    for shape in shapes.findall(SHAPE_TAG):
        if not is_left_panel_shape(shape):
            continue
        cloned = copy.deepcopy(shape)
        for descendant in cloned.iter(SHAPE_TAG):
            descendant.attrib.pop("ID", None)
        normalized.append(ET.tostring(cloned, encoding="utf-8"))
    return normalized


def validate_vsdx(path: Path) -> None:
    root = page_root(path)
    shapes = root.find(SHAPES_TAG)
    require(shapes is not None, f"{path} has no Shapes collection")
    texts = [shape_text(shape) for shape in shapes.findall(SHAPE_TAG)]
    normalized_texts = {text.casefold() for text in texts if text}
    require("fast" not in normalized_texts and "fast time" not in normalized_texts, "Fast time remains in VSDX")
    for required_text in (
        "Readable",
        "Temporal",
        "integration",
        "Rapid",
        "complementary",
        "subframes",
        "Camera",
        "Short-exposure",
        "sampling",
        "Unreadable",
        "fragment",
        "OCR",
    ):
        require(required_text in texts, f"Missing VSDX text: {required_text}")

    thick_red_diagonals = []
    for shape in shapes.findall(SHAPE_TAG):
        if cell_text(shape, "LineColor").casefold() != REVISION_RED:
            continue
        try:
            line_weight = cell_value(shape, "LineWeight")
            begin_x = cell_value(shape, "BeginX")
            begin_y = cell_value(shape, "BeginY")
            end_x = cell_value(shape, "EndX")
            end_y = cell_value(shape, "EndY")
        except AssertionError:
            continue
        if line_weight >= 3.0 / 72 and begin_x != end_x and begin_y != end_y:
            thick_red_diagonals.append(shape)
    require(len(thick_red_diagonals) == 2, "Final VSDX must contain exactly two thick red OCR-X diagonals")


def validate_pdf(path: Path) -> None:
    reader = PdfReader(str(path))
    require(len(reader.pages) == 1, f"{path} must be a single-page PDF")
    page = reader.pages[0]
    require(abs(float(page.mediabox.width) - 252.0) < 0.01, "Figure PDF width must be 252 pt")
    require(abs(float(page.mediabox.height) - 168.0) < 0.01, "Figure PDF height must be 168 pt")
    text = page.extract_text()
    require("Fast time" not in text and "Fast\ntime" not in text, "Fast time remains in PDF text")
    for required_text in ("Temporal", "integration", "Short-exposure", "OCR"):
        require(required_text in text, f"Missing PDF text: {required_text}")


def main() -> None:
    english_vsdx = ENGLISH_FINAL / "figure1_concept_threat.vsdx"
    english_pdf = ENGLISH_FINAL / "figure1_concept_threat.pdf"
    english_png = ENGLISH_FINAL / "figure1_concept_threat.png"
    chinese_vsdx = CHINESE_FINAL / "figure1_concept_threat.vsdx"
    chinese_pdf = CHINESE_FINAL / "figure1_concept_threat.pdf"

    for path in (BASELINE_VSDX, english_vsdx, english_pdf, english_png, chinese_vsdx, chinese_pdf):
        require(path.is_file(), f"Missing required deliverable: {path}")

    validate_vsdx(english_vsdx)
    validate_pdf(english_pdf)
    require(
        normalized_left_shapes(BASELINE_VSDX) == normalized_left_shapes(english_vsdx),
        "Canonical panel (a) Shape XML changed",
    )
    require(sha256(english_vsdx) == sha256(chinese_vsdx), "English/Chinese VSDX mirrors differ")
    require(sha256(english_pdf) == sha256(chinese_pdf), "English/Chinese PDF mirrors differ")

    with Image.open(english_png) as image:
        require(image.size == (1050, 700), f"Expected 1050x700 review PNG, found {image.size}")

    print("OK: final Figure 1 assets validated")
    print(f"VSDX SHA-256: {sha256(english_vsdx)}")
    print(f"PDF SHA-256:  {sha256(english_pdf)}")


if __name__ == "__main__":
    main()
