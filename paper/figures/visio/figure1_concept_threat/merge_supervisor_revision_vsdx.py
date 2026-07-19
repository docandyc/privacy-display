"""Preserve canonical panel (a) while replacing panel (b) in an editable VSDX.

The maintained scene generator is authoritative for the revised right panel,
but the previously reviewed canonical VSDX contains the exact left-panel art
the supervisor asked us to retain.  Both files use the same lower-left
3.50 x 2.333 inch publication viewport.  Their Visio masters and page
relationships are identical, so the canonical left-panel Shape XML can be
transplanted into the revised package without rasterization.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import xml.etree.ElementTree as ET


PAGE_XML = "visio/pages/page1.xml"
PAGE_RELS = "visio/pages/_rels/page1.xml.rels"
VISIO_NS = "http://schemas.microsoft.com/office/visio/2012/main"
SHAPE_TAG = f"{{{VISIO_NS}}}Shape"
SHAPES_TAG = f"{{{VISIO_NS}}}Shapes"
CELL_TAG = f"{{{VISIO_NS}}}Cell"
DIVIDER_X_IN = 720 / 1536 * 3.5
DIVIDER_TOLERANCE_IN = 0.03

ET.register_namespace("", VISIO_NS)


def archive_payloads(path: Path) -> dict[str, bytes]:
    with ZipFile(path, "r") as archive:
        return {info.filename: archive.read(info.filename) for info in archive.infolist()}


def cell_value(shape: ET.Element, name: str) -> float:
    for cell in shape.findall(CELL_TAG):
        if cell.get("N") == name:
            value = cell.get("V")
            if value is None:
                break
            return float(value)
    raise ValueError(f"Shape {shape.get('ID', '?')} has no numeric {name} cell")


def is_panel_divider(shape: ET.Element) -> bool:
    return (
        abs(cell_value(shape, "PinX") - DIVIDER_X_IN) <= DIVIDER_TOLERANCE_IN
        and cell_value(shape, "Width") <= 0.03
        and cell_value(shape, "Height") >= 2.0
    )


def is_left_panel_shape(shape: ET.Element) -> bool:
    return not is_panel_divider(shape) and cell_value(shape, "PinX") < DIVIDER_X_IN


def assert_shared_visio_vocabulary(
    prior_payloads: dict[str, bytes], revised_payloads: dict[str, bytes]
) -> None:
    shared_parts = sorted(
        name
        for name in prior_payloads
        if name.startswith("visio/masters/") or name == PAGE_RELS
    )
    if not shared_parts:
        raise RuntimeError("Canonical VSDX has no Visio master vocabulary")
    for name in shared_parts:
        if revised_payloads.get(name) != prior_payloads[name]:
            raise RuntimeError(f"Cannot safely transplant shapes: package part differs: {name}")


def merged_page_xml(prior_xml: bytes, revised_xml: bytes) -> tuple[bytes, int, int]:
    prior_root = ET.fromstring(prior_xml)
    revised_root = ET.fromstring(revised_xml)
    prior_shapes = prior_root.find(SHAPES_TAG)
    revised_shapes = revised_root.find(SHAPES_TAG)
    if prior_shapes is None or revised_shapes is None:
        raise RuntimeError("Both VSDX pages must contain a top-level Shapes collection")

    canonical_left = [shape for shape in prior_shapes.findall(SHAPE_TAG) if is_left_panel_shape(shape)]
    generated_left = [shape for shape in revised_shapes.findall(SHAPE_TAG) if is_left_panel_shape(shape)]
    if not canonical_left or not generated_left:
        raise RuntimeError("Could not identify both canonical and generated panel-(a) shapes")

    for shape in generated_left:
        revised_shapes.remove(shape)

    existing_ids = {
        int(shape_id)
        for shape in revised_root.iter(SHAPE_TAG)
        if (shape_id := shape.get("ID")) is not None
    }
    next_id = max(existing_ids, default=0) + 1
    for canonical_shape in canonical_left:
        cloned_shape = copy.deepcopy(canonical_shape)
        for shape in cloned_shape.iter(SHAPE_TAG):
            shape.set("ID", str(next_id))
            next_id += 1
        revised_shapes.append(cloned_shape)

    payload = ET.tostring(revised_root, encoding="utf-8", xml_declaration=True)
    return payload, len(generated_left), len(canonical_left)


def write_merged_package(
    prior_vsdx: Path, revised_vsdx: Path, output_vsdx: Path
) -> tuple[int, int]:
    if output_vsdx.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output_vsdx}")

    prior_payloads = archive_payloads(prior_vsdx)
    revised_payloads = archive_payloads(revised_vsdx)
    assert_shared_visio_vocabulary(prior_payloads, revised_payloads)
    page_xml, removed, copied = merged_page_xml(
        prior_payloads[PAGE_XML], revised_payloads[PAGE_XML]
    )

    output_vsdx.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(revised_vsdx, "r") as src:
        members: list[tuple[ZipInfo, bytes]] = []
        for info in src.infolist():
            payload = page_xml if info.filename == PAGE_XML else src.read(info.filename)
            members.append((info, payload))

    with NamedTemporaryFile(dir=output_vsdx.parent, suffix=".vsdx", delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        with ZipFile(temp_path, "w", compression=ZIP_DEFLATED) as dst:
            for info, payload in members:
                dst.writestr(info, payload)
        temp_path.replace(output_vsdx)
    finally:
        temp_path.unlink(missing_ok=True)
    return removed, copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prior_vsdx", type=Path)
    parser.add_argument("revised_vsdx", type=Path)
    parser.add_argument("output_vsdx", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_vsdx = args.output_vsdx.resolve()
    removed, copied = write_merged_package(
        args.prior_vsdx.resolve(), args.revised_vsdx.resolve(), output_vsdx
    )
    print(f"Removed {removed} generated panel-(a) shapes")
    print(f"Copied {copied} canonical panel-(a) shapes")
    print(f"Wrote {output_vsdx}")


if __name__ == "__main__":
    main()
