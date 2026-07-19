"""Validate the semantic contracts of the supervisor-revised Figure 1 scene."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
DEFAULT_SCENE = ROOT / "figure1_concept_threat.round2.scene.json"

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
SUBFRAME_IDS = tuple(f"subframe_grid_{index}" for index in range(1, 5))
SEQUENCE_EDGE_IDS = (
    "sequence_1_to_2",
    "sequence_2_to_3",
    "sequence_3_to_4",
)
OCR_X_EDGE_IDS = ("ocr_x_down", "ocr_x_up")
REVISION_RED = "#D94722"
MINIMUM_OCR_X_WEIGHT_PT = 3.0


def require(condition: bool, message: str) -> None:
    """Raise an assertion with a useful semantic-validation message."""

    if not condition:
        raise AssertionError(message)


def index_by_id(items: Iterable[dict[str, Any]], kind: str) -> dict[str, dict[str, Any]]:
    """Return an ID index while rejecting missing or duplicate scene IDs."""

    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        require(isinstance(item_id, str) and item_id, f"{kind} has a missing ID")
        require(item_id not in indexed, f"duplicate {kind} ID: {item_id}")
        indexed[item_id] = item
    return indexed


def grid_cells(node: dict[str, Any], node_id: str) -> set[tuple[int, int]]:
    """Validate a 5x5 glyph grid and return its occupied cell coordinates."""

    require(node.get("type") == "grid_matrix", f"{node_id} must be a grid_matrix")
    require(node.get("rows") == 5, f"{node_id} must have exactly 5 rows")
    require(node.get("cols") == 5, f"{node_id} must have exactly 5 columns")

    colored_cells = node.get("colored_cells")
    require(isinstance(colored_cells, list), f"{node_id}.colored_cells must be a list")

    cells: list[tuple[int, int]] = []
    for position, colored_cell in enumerate(colored_cells):
        require(
            isinstance(colored_cell, list) and len(colored_cell) >= 2,
            f"{node_id}.colored_cells[{position}] must contain row and column",
        )
        row, column = colored_cell[:2]
        require(
            isinstance(row, int) and not isinstance(row, bool),
            f"{node_id}.colored_cells[{position}] row must be an integer",
        )
        require(
            isinstance(column, int) and not isinstance(column, bool),
            f"{node_id}.colored_cells[{position}] column must be an integer",
        )
        require(0 <= row < 5 and 0 <= column < 5, f"{node_id} cell {(row, column)} is out of bounds")
        cells.append((row, column))

    require(len(cells) == len(set(cells)), f"{node_id} contains duplicate occupied cells")
    return set(cells)


def validate_removed_fast_time(
    nodes: dict[str, dict[str, Any]], edges: dict[str, dict[str, Any]]
) -> None:
    """Reject the retired Fast/time labels and the old global time axis."""

    for retired_id in ("fast_label", "time_label"):
        require(retired_id not in nodes, f"retired node is still present: {retired_id}")
    require("time_axis" not in edges, "retired edge is still present: time_axis")

    visible_text = [node.get("text") for node in nodes.values() if isinstance(node.get("text"), str)]
    normalized_text = {text.strip().casefold() for text in visible_text}
    require("fast" not in normalized_text, "retired visible label 'Fast' is still present")
    require("fast time" not in normalized_text, "retired visible label 'Fast time' is still present")


def validate_glyph_semantics(nodes: dict[str, dict[str, Any]]) -> None:
    """Validate complementary A subframes and the two downstream glyph views."""

    subframes: list[set[tuple[int, int]]] = []
    for node_id in SUBFRAME_IDS:
        require(node_id in nodes, f"missing complementary subframe: {node_id}")
        subframes.append(grid_cells(nodes[node_id], node_id))

    occupied_once: set[tuple[int, int]] = set()
    for node_id, cells in zip(SUBFRAME_IDS, subframes):
        overlap = occupied_once & cells
        require(not overlap, f"{node_id} overlaps earlier subframes at {sorted(overlap)}")
        occupied_once.update(cells)
    require(
        occupied_once == GLYPH_A_CELLS,
        "the four complementary subframes do not reconstruct the expected 5x5 A glyph",
    )

    human_id = "readable_glyph_grid"
    require(human_id in nodes, f"missing human-readable output grid: {human_id}")
    human_cells = grid_cells(nodes[human_id], human_id)
    require(human_cells == GLYPH_A_CELLS, "human-readable output must contain the complete A glyph")

    fragment_id = "fragment_grid"
    require(fragment_id in nodes, f"missing camera fragment grid: {fragment_id}")
    fragment_cells = grid_cells(nodes[fragment_id], fragment_id)
    require(fragment_cells == subframes[1], "camera fragment must exactly match subframe 2")


def validate_sequence_arrows(edges: dict[str, dict[str, Any]]) -> None:
    """Require exactly three local, unobstructed left-to-right sequence arrows."""

    sequence_ids = {edge_id for edge_id in edges if edge_id.startswith("sequence_")}
    require(
        sequence_ids == set(SEQUENCE_EDGE_IDS),
        f"expected exactly three sequence arrows {SEQUENCE_EDGE_IDS}, found {sorted(sequence_ids)}",
    )

    for edge_id in SEQUENCE_EDGE_IDS:
        edge = edges[edge_id]
        require(edge.get("type") == "lane_arrow", f"{edge_id} must be a lane_arrow")
        require(edge.get("route") == "horizontal", f"{edge_id} must use a horizontal route")
        require(edge.get("lane_axis") == "horizontal", f"{edge_id} must use a horizontal lane axis")

        from_point = edge.get("from_point")
        to_point = edge.get("to_point")
        require(
            isinstance(from_point, list) and len(from_point) == 2,
            f"{edge_id}.from_point must be a two-coordinate list",
        )
        require(
            isinstance(to_point, list) and len(to_point) == 2,
            f"{edge_id}.to_point must be a two-coordinate list",
        )
        require(from_point[1] == to_point[1], f"{edge_id} must be visually horizontal")
        require(from_point[0] < to_point[0], f"{edge_id} must point left-to-right")

        style = edge.get("style", {})
        require(style.get("end_arrow") == "triangle", f"{edge_id} must have an end arrowhead")


def validate_ocr_failure_mark(
    nodes: dict[str, dict[str, Any]], edges: dict[str, dict[str, Any]]
) -> None:
    """Validate the exact OCR label and the two-stroke, thick red X overlay."""

    ocr_id = "ocr_failure"
    require(ocr_id in nodes, f"missing OCR node: {ocr_id}")
    ocr_node = nodes[ocr_id]
    require(ocr_node.get("text") == "OCR", "OCR node text must be exactly 'OCR'")

    x_edges: list[dict[str, Any]] = []
    for edge_id in OCR_X_EDGE_IDS:
        require(edge_id in edges, f"missing OCR X stroke: {edge_id}")
        edge = edges[edge_id]
        x_edges.append(edge)
        require(edge.get("type") == "line_segment", f"{edge_id} must be a line_segment")
        require(edge.get("allow_diagonal") is True, f"{edge_id} must explicitly allow a diagonal route")

        style = edge.get("style", {})
        line_color = style.get("line")
        require(
            isinstance(line_color, str) and line_color.upper() == REVISION_RED,
            f"{edge_id} must use revision red {REVISION_RED}",
        )
        line_weight = style.get("line_weight_pt")
        require(
            isinstance(line_weight, (int, float))
            and not isinstance(line_weight, bool)
            and line_weight >= MINIMUM_OCR_X_WEIGHT_PT,
            f"{edge_id} must be at least {MINIMUM_OCR_X_WEIGHT_PT} pt thick",
        )
        require(style.get("end_arrow") == "none", f"{edge_id} must not have an arrowhead")
        require(edge.get("z", 0) > ocr_node.get("z", 0), f"{edge_id} must overlay the OCR node")

    endpoints: list[tuple[list[float], list[float]]] = []
    for edge_id, edge in zip(OCR_X_EDGE_IDS, x_edges):
        from_point = edge.get("from_point")
        to_point = edge.get("to_point")
        require(
            isinstance(from_point, list) and len(from_point) == 2,
            f"{edge_id}.from_point must be a two-coordinate list",
        )
        require(
            isinstance(to_point, list) and len(to_point) == 2,
            f"{edge_id}.to_point must be a two-coordinate list",
        )
        require(
            all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in from_point + to_point),
            f"{edge_id} endpoints must be numeric",
        )
        dx = to_point[0] - from_point[0]
        dy = to_point[1] - from_point[1]
        require(dx != 0 and dy != 0, f"{edge_id} must be diagonal")
        endpoints.append((from_point, to_point))

    first_dx = endpoints[0][1][0] - endpoints[0][0][0]
    first_dy = endpoints[0][1][1] - endpoints[0][0][1]
    second_dx = endpoints[1][1][0] - endpoints[1][0][0]
    second_dy = endpoints[1][1][1] - endpoints[1][0][1]
    require(first_dx * first_dy > 0, "ocr_x_down must descend from upper-left to lower-right")
    require(second_dx * second_dy < 0, "ocr_x_up must rise from lower-left to upper-right")

    first_bounds = (
        min(endpoints[0][0][0], endpoints[0][1][0]),
        min(endpoints[0][0][1], endpoints[0][1][1]),
        max(endpoints[0][0][0], endpoints[0][1][0]),
        max(endpoints[0][0][1], endpoints[0][1][1]),
    )
    second_bounds = (
        min(endpoints[1][0][0], endpoints[1][1][0]),
        min(endpoints[1][0][1], endpoints[1][1][1]),
        max(endpoints[1][0][0], endpoints[1][1][0]),
        max(endpoints[1][0][1], endpoints[1][1][1]),
    )
    require(first_bounds == second_bounds, "the two OCR diagonals must span the same X bounds")

    ocr_bounds = (
        ocr_node.get("x"),
        ocr_node.get("y"),
        ocr_node.get("x", 0) + ocr_node.get("w", 0),
        ocr_node.get("y", 0) + ocr_node.get("h", 0),
    )
    require(
        all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in ocr_bounds),
        "OCR node bounds must be numeric",
    )
    require(
        ocr_bounds[0] <= first_bounds[0] < first_bounds[2] <= ocr_bounds[2]
        and ocr_bounds[1] <= first_bounds[1] < first_bounds[3] <= ocr_bounds[3],
        "the red X must lie within the OCR node bounds",
    )


def validate_scene(scene_path: Path) -> None:
    """Load one round-two scene and validate all supervisor revision contracts."""

    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    require(isinstance(scene, dict), "scene root must be a JSON object")
    require(isinstance(scene.get("nodes"), list), "scene.nodes must be a list")
    require(isinstance(scene.get("edges"), list), "scene.edges must be a list")

    nodes = index_by_id(scene["nodes"], "node")
    edges = index_by_id(scene["edges"], "edge")

    validate_removed_fast_time(nodes, edges)
    validate_glyph_semantics(nodes)
    validate_sequence_arrows(edges)
    validate_ocr_failure_mark(nodes, edges)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scene",
        nargs="?",
        type=Path,
        default=DEFAULT_SCENE,
        help=f"round-two scene JSON (default: {DEFAULT_SCENE})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validate_scene(args.scene)
    print(f"OK: supervisor revision semantics validated: {args.scene}")


if __name__ == "__main__":
    main()
