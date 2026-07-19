"""Validate final Figure 1 deliverables and the preserved canonical left panel."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import re
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
NAVY = "#17365d"
PALE_BLUE = "#dff3fa"
SCENE_WIDTH_PX = 1536
SCENE_HEIGHT_PX = 1024
TARGET_WIDTH_IN = 3.5
PX_TO_IN = TARGET_WIDTH_IN / SCENE_WIDTH_PX
PAGE_HEIGHT_IN = SCENE_HEIGHT_PX * PX_TO_IN
GRID_TOLERANCE_IN = 1e-6

GLYPH_A_CELLS = {
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 0),
    (1, 4),
    (2, 0),
    (2, 1),
    (2, 2),
    (2, 3),
    (2, 4),
    (3, 0),
    (3, 4),
    (4, 0),
    (4, 4),
}
SUBFRAME_CELLS = (
    {(0, 1), (1, 4), (2, 2), (4, 0)},
    {(0, 2), (1, 0), (2, 3), (3, 4)},
    {(0, 3), (2, 0), (2, 4)},
    {(2, 1), (3, 0), (4, 4)},
)
GRID_SPECS = {
    "subframe 1": (809, 475, 72, 72, SUBFRAME_CELLS[0]),
    "subframe 2": (959, 475, 72, 72, SUBFRAME_CELLS[1]),
    "subframe 3": (1109, 475, 72, 72, SUBFRAME_CELLS[2]),
    "subframe 4": (1259, 475, 72, 72, SUBFRAME_CELLS[3]),
    "human-readable A": (1340, 155, 90, 90, GLYPH_A_CELLS),
    "camera fragment": (1218, 812, 60, 60, SUBFRAME_CELLS[1]),
}
PNG_OVERLAY_ROWS = {
    "subframe 1": {2},
    "subframe 2": {2},
    "subframe 3": {2},
    "subframe 4": {2},
    "camera fragment": {2},
}


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


def grid_cells_from_vsdx(
    shapes: ET.Element, grid_name: str, x: int, y: int, width: int, height: int
) -> set[tuple[int, int]]:
    """Recover one rendered 5x5 grid from cell-shape geometry and fills."""

    cell_width = width / 5 * PX_TO_IN
    cell_height = height / 5 * PX_TO_IN
    active: set[tuple[int, int]] = set()
    top_level_shapes = shapes.findall(SHAPE_TAG)
    for row in range(5):
        for column in range(5):
            expected_pin_x = (x + (column + 0.5) * width / 5) * PX_TO_IN
            expected_pin_y = PAGE_HEIGHT_IN - (y + (row + 0.5) * height / 5) * PX_TO_IN
            matches = []
            for shape in top_level_shapes:
                try:
                    values = (
                        cell_value(shape, "PinX"),
                        cell_value(shape, "PinY"),
                        cell_value(shape, "Width"),
                        cell_value(shape, "Height"),
                    )
                except AssertionError:
                    continue
                if (
                    abs(values[0] - expected_pin_x) <= GRID_TOLERANCE_IN
                    and abs(values[1] - expected_pin_y) <= GRID_TOLERANCE_IN
                    and abs(values[2] - cell_width) <= GRID_TOLERANCE_IN
                    and abs(values[3] - cell_height) <= GRID_TOLERANCE_IN
                ):
                    matches.append(shape)
            require(
                len(matches) == 1,
                f"Expected one VSDX cell shape for {grid_name} {(row, column)}, found {len(matches)}",
            )
            fill = cell_text(matches[0], "FillForegnd").casefold()
            require(
                fill in {NAVY, PALE_BLUE},
                f"Unexpected VSDX fill for {grid_name} {(row, column)}: {fill or '<missing>'}",
            )
            if fill == NAVY:
                active.add((row, column))
    return active


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
    require(
        not {"fast", "time", "fast time"} & normalized_texts,
        "A retired Fast/time label remains in VSDX",
    )
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

    for grid_name, (x, y, width, height, expected_cells) in GRID_SPECS.items():
        actual_cells = grid_cells_from_vsdx(shapes, grid_name, x, y, width, height)
        require(
            actual_cells == expected_cells,
            f"VSDX {grid_name} cells differ: expected {sorted(expected_cells)}, found {sorted(actual_cells)}",
        )


def validate_pdf(path: Path) -> None:
    reader = PdfReader(str(path))
    require(len(reader.pages) == 1, f"{path} must be a single-page PDF")
    page = reader.pages[0]
    require(abs(float(page.mediabox.width) - 252.0) < 0.01, "Figure PDF width must be 252 pt")
    require(abs(float(page.mediabox.height) - 168.0) < 0.01, "Figure PDF height must be 168 pt")
    text = page.extract_text()
    words = set(re.findall(r"[a-z]+(?:-[a-z]+)?", text.casefold()))
    require(not {"fast", "time"} & words, "A retired Fast/time label remains in PDF text")
    for required_text in ("Temporal", "integration", "Short-exposure", "OCR"):
        require(required_text in text, f"Missing PDF text: {required_text}")


def validate_png(path: Path) -> None:
    """Use interior-majority sampling so overlaid arrows do not look like lit cells."""

    with Image.open(path) as image:
        require(image.size == (1050, 700), f"Expected 1050x700 review PNG, found {image.size}")
        rgb = image.convert("RGB")
        scale_x = rgb.width / SCENE_WIDTH_PX
        scale_y = rgb.height / SCENE_HEIGHT_PX
        navy_rgb = (23, 54, 93)
        pale_rgb = (223, 243, 250)

        for grid_name, (x, y, width, height, expected_cells) in GRID_SPECS.items():
            actual_cells: set[tuple[int, int]] = set()
            overlay_rows = PNG_OVERLAY_ROWS.get(grid_name, set())
            for row in range(5):
                if row in overlay_rows:
                    continue
                for column in range(5):
                    navy_votes = 0
                    for y_fraction in (0.2, 0.8):
                        for x_fraction in (0.2, 0.5, 0.8):
                            sample_x = round(
                                (x + (column + x_fraction) * width / 5) * scale_x
                            )
                            sample_y = round(
                                (y + (row + y_fraction) * height / 5) * scale_y
                            )
                            color = rgb.getpixel((sample_x, sample_y))
                            navy_distance = sum(
                                (channel - target) ** 2
                                for channel, target in zip(color, navy_rgb)
                            )
                            pale_distance = sum(
                                (channel - target) ** 2
                                for channel, target in zip(color, pale_rgb)
                            )
                            navy_votes += navy_distance < pale_distance
                    if navy_votes >= 4:
                        actual_cells.add((row, column))
            expected_visible_cells = {
                cell for cell in expected_cells if cell[0] not in overlay_rows
            }
            require(
                actual_cells == expected_visible_cells,
                f"PNG {grid_name} visible cells differ: "
                f"expected {sorted(expected_visible_cells)}, found {sorted(actual_cells)}",
            )


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
    validate_png(english_png)
    require(
        normalized_left_shapes(BASELINE_VSDX) == normalized_left_shapes(english_vsdx),
        "Canonical panel (a) Shape XML changed",
    )
    require(sha256(english_vsdx) == sha256(chinese_vsdx), "English/Chinese VSDX mirrors differ")
    require(sha256(english_pdf) == sha256(chinese_pdf), "English/Chinese PDF mirrors differ")

    print("OK: final Figure 1 assets validated")
    print(f"VSDX SHA-256: {sha256(english_vsdx)}")
    print(f"PDF SHA-256:  {sha256(english_pdf)}")


if __name__ == "__main__":
    main()
