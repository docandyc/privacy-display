from __future__ import annotations

import copy
import json
from pathlib import Path

from build_round1_scene import box, label, node, sty


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "figure1_concept_threat.round2.scene.json"


GLYPH_A_CELLS = {
    (0, 1), (0, 2), (0, 3),
    (1, 0), (1, 4),
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
    (3, 0), (3, 4),
    (4, 0), (4, 4),
}
SUBFRAME_CELLS = (
    {(0, 1), (1, 4), (2, 2), (4, 0)},
    {(0, 2), (1, 0), (2, 3), (3, 4)},
    {(0, 3), (2, 0), (2, 4)},
    {(2, 1), (3, 0), (4, 4)},
)
SELECTED_SUBFRAME_INDEX = 1


def glyph_grid(node_id, x, y, w, h, cells, container):
    return node(
        node_id, "grid_matrix", x, y, w, h,
        container=container, z=13, rows=5, cols=5,
        allow_overlap=True,
        colored_cells=[[row, col, "#17365D"] for row, col in sorted(cells)],
        style=sty(
            cell_fill="#DFF3FA",
            grid_line="#C5DEEA",
            grid_line_weight_pt=0.25,
        ),
    )


def validate_glyph_partition() -> None:
    flattened = [cell for subframe in SUBFRAME_CELLS for cell in subframe]
    if len(flattened) != len(set(flattened)):
        raise ValueError("Complementary A subframes must be mutually exclusive")
    if set(flattened) != GLYPH_A_CELLS:
        raise ValueError("Complementary A subframes must reconstruct the full glyph")


def main():
    validate_glyph_partition()
    inventory_scene = json.loads((ROOT / "figure1_concept_threat.scene.json").read_text(encoding="utf-8"))
    metadata = copy.deepcopy(inventory_scene["metadata"])
    metadata.update({
        "created_by": "codex.visiomaster.supervisor_revision",
        "replica_stage": "detail_polish",
        "prior_scene_policy": "reuse_source_inventory_and_arrow_plan_only; reauthor_all_visible_nodes",
        "notes": [
            "Supervisor-approved semantic revision of the editable round-two scene.",
            "Human, subframe, and camera zones use independent vertical bands.",
            "Every long English label uses dedicated rows and explicit text margins.",
            "Office geometry is reauthored as simplified editable editorial line art.",
            "Panel (a) remains unchanged; panel (b) uses complementary 5x5 A glyph subsets.",
            "Fast time text is removed; three local rightward arrows encode sequence order.",
            "The selected camera fragment exactly matches subframe 2.",
            "OCR failure is shown with a large editable red X.",
        ],
    })
    inventory_regions = {
        region["id"]: region
        for region in metadata["source_visual_inventory"]["regions"]
    }
    inventory_regions["subframe_row"].update({
        "required_labels": ["Rapid complementary subframes"],
        "required_component_motifs": [
            "four 5x5 displays containing mutually exclusive subsets of one capital A",
            "one selected exposure bracket around subframe 2",
        ],
        "required_edge_motifs": ["three unobstructed rightward inter-frame sequence arrows"],
        "text_layout_facts": ["four thumbnails share one baseline", "no Fast time text"],
    })
    inventory_regions["human_output"].update({
        "required_labels": ["Human eye", "Temporal integration", "Readable"],
        "required_component_motifs": ["eye", "readable display containing the complete 5x5 A"],
    })
    inventory_regions["camera_output"].update({
        "required_component_motifs": [
            "camera",
            "fragment identical to selected subframe 2",
            "OCR symbol overlaid by a large red X",
        ],
    })

    metadata["arrow_plan"] = [
        plan for plan in metadata["arrow_plan"] if plan["id"] != "A003"
    ]
    metadata["arrow_plan"].extend([
        {
            "id": "A003a", "source_region": "subframe_row",
            "source_fact": "A short rightward arrow connects subframe 1 to subframe 2.",
            "from_visual_object": "subframe_1", "from_anchor_description": "right-side gap",
            "from": "subframe_1 (right-side gap)",
            "to_visual_object": "subframe_2", "to_anchor_description": "left-side gap",
            "to": "subframe_2 (left-side gap)",
            "direction": "left_to_right", "route_shape": "straight_horizontal",
            "line_style": "solid", "arrowhead": "end", "semantic_intent": "annotation",
            "source_bbox_px": [905, 500, 935, 530], "must_not_cross": [],
            "relative_position_facts": ["centered in the gap between adjacent displays"],
            "certainty": "certain",
        },
        {
            "id": "A003b", "source_region": "subframe_row",
            "source_fact": "A short rightward arrow connects subframe 2 to subframe 3.",
            "from_visual_object": "subframe_2", "from_anchor_description": "right-side gap",
            "from": "subframe_2 (right-side gap)",
            "to_visual_object": "subframe_3", "to_anchor_description": "left-side gap",
            "to": "subframe_3 (left-side gap)",
            "direction": "left_to_right", "route_shape": "straight_horizontal",
            "line_style": "solid", "arrowhead": "end", "semantic_intent": "annotation",
            "source_bbox_px": [1055, 500, 1085, 530], "must_not_cross": [],
            "relative_position_facts": ["centered in the gap between adjacent displays"],
            "certainty": "certain",
        },
        {
            "id": "A003c", "source_region": "subframe_row",
            "source_fact": "A short rightward arrow connects subframe 3 to subframe 4.",
            "from_visual_object": "subframe_3", "from_anchor_description": "right-side gap",
            "from": "subframe_3 (right-side gap)",
            "to_visual_object": "subframe_4", "to_anchor_description": "left-side gap",
            "to": "subframe_4 (left-side gap)",
            "direction": "left_to_right", "route_shape": "straight_horizontal",
            "line_style": "solid", "arrowhead": "end", "semantic_intent": "annotation",
            "source_bbox_px": [1205, 500, 1235, 530], "must_not_cross": [],
            "relative_position_facts": ["centered in the gap between adjacent displays"],
            "certainty": "certain",
        },
        {
            "id": "A012", "source_region": "camera_output",
            "source_fact": "The first thick diagonal stroke forms half of the large red OCR X.",
            "from_visual_object": "ocr_failure", "from_anchor_description": "upper-left interior",
            "from": "ocr_failure (upper-left interior)",
            "to_visual_object": "ocr_failure", "to_anchor_description": "lower-right interior",
            "to": "ocr_failure (lower-right interior)",
            "direction": "none", "route_shape": "diagonal",
            "line_style": "solid", "arrowhead": "none", "semantic_intent": "annotation",
            "source_bbox_px": [1395, 798, 1500, 890], "must_not_cross": [],
            "relative_position_facts": ["overlays the OCR symbol"], "certainty": "certain",
        },
        {
            "id": "A013", "source_region": "camera_output",
            "source_fact": "The second thick diagonal stroke completes the large red OCR X.",
            "from_visual_object": "ocr_failure", "from_anchor_description": "upper-right interior",
            "from": "ocr_failure (upper-right interior)",
            "to_visual_object": "ocr_failure", "to_anchor_description": "lower-left interior",
            "to": "ocr_failure (lower-left interior)",
            "direction": "none", "route_shape": "diagonal",
            "line_style": "solid", "arrowhead": "none", "semantic_intent": "annotation",
            "source_bbox_px": [1395, 798, 1500, 890], "must_not_cross": [],
            "relative_position_facts": ["overlays the OCR symbol"], "certainty": "certain",
        },
    ])
    metadata["region_plan"] = [
        {"id":"global_layout","crop_type":"global","source_bbox_px":[0,0,1536,1024],
         "target_bbox":[0,0,1536,1024],"review_focus":"global layout and two-panel balance"},
        {"id":"physical_input","crop_type":"input","source_bbox_px":[0,0,730,1024],
         "target_bbox":[20,20,710,1000],"container_id":"physical_scene",
         "review_focus":"physical eavesdropping scene and labels"},
        {"id":"subframe_core","crop_type":"core","source_bbox_px":[760,350,1500,650],
         "target_bbox":[750,370,1510,690],"container_id":"subframe_region",
         "review_focus":"four subframes time axis and selected frame"},
        {"id":"human_output","crop_type":"output","source_bbox_px":[900,60,1510,350],
         "target_bbox":[830,80,1510,440],"container_id":"human_region",
         "review_focus":"right output human integration"},
        {"id":"camera_output","crop_type":"output","source_bbox_px":[870,610,1536,940],
         "target_bbox":[850,650,1520,1000],"container_id":"camera_region",
         "review_focus":"right output camera sampling"},
        {"id":"arrow_dense","crop_type":"arrow_dense","source_bbox_px":[760,120,1536,900],
         "target_bbox":[760,120,1520,930],"review_focus":"human fan-in and camera selection topology"},
        {"id":"small_text","crop_type":"small_text","source_bbox_px":[20,0,1536,960],
         "target_bbox":[20,0,1520,960],"review_focus":"small text display words and captions"},
    ]

    navy = "#17365D"
    green = "#177A36"
    red = "#D94722"
    pale_blue = "#DFF3FA"

    nodes = [
        node("page_background", "page_background", 0, 0, 1536, 1024, z=-100),
        node("physical_scene", "audit_region", 20, 20, 690, 980, z=-10,
             label="Physical visual eavesdropping", source_bbox_px=[0,0,730,1024],
             source_aspect_ratio=0.713, style=sty(fill="none", line="none")),
        node("subframe_region", "audit_region", 750, 370, 760, 320, z=-10,
             label="Rapid complementary subframes", source_bbox_px=[760,350,1500,650],
             source_aspect_ratio=2.467, style=sty(fill="none", line="none")),
        node("human_region", "audit_region", 830, 80, 680, 360, z=-10,
             label="Human integration", source_bbox_px=[900,60,1510,350],
             source_aspect_ratio=2.103, style=sty(fill="none", line="none")),
        node("camera_region", "audit_region", 850, 650, 670, 350, z=-10,
             label="Camera sampling", source_bbox_px=[870,610,1536,940],
             source_aspect_ratio=2.018, style=sty(fill="none", line="none")),
        node("panel_divider", "polygon_node", 720, 20, 4, 980, z=5,
             points=[[0,0],[1,0],[1,1],[0,1]],
             style=sty(fill=navy, line=navy, line_weight_pt=0.6)),

        label("panel_a_title", 30, 22, 675, 62, "(a)  Physical visual eavesdropping",
              "physical_scene", size=6.5, weight="bold", role="panel_title", align=0),
        label("authorized_line1", 25, 230, 245, 60, "Authorized", "physical_scene",
              size=6.5, weight="bold"),
        label("authorized_line2", 25, 278, 245, 60, "user", "physical_scene",
              size=6.7, weight="bold"),
        label("sensitive_line1", 270, 175, 230, 60, "Sensitive", "physical_scene",
              size=6.7, weight="bold"),
        label("sensitive_line2", 270, 222, 230, 60, "display", "physical_scene",
              size=6.7, weight="bold"),
        label("phone_line1", 440, 820, 260, 60, "Smartphone", "physical_scene",
              size=6.5, color=red, weight="bold"),
        label("phone_line2", 440, 868, 260, 60, "camera", "physical_scene",
              size=6.6, color=red, weight="bold"),

        box("chair_back", 48, 505, 130, 300, "physical_scene", rounded=True, weight=1.15,
            allow_overlap=True),
        box("chair_seat", 105, 730, 190, 55, "physical_scene", rounded=True, weight=1.15,
            allow_overlap=True),
        node("chair_support", "polygon_node", 105, 782, 150, 165, container="physical_scene", z=8,
             allow_overlap=True, points=[[0.42,0],[0.58,0],[0.58,0.60],[1,1],[0.5,0.72],[0,1],[0.42,0.60]],
             style=sty(fill="none", line=navy, line_weight_pt=1.05)),
        node("user_torso", "polygon_node", 92, 455, 235, 285, container="physical_scene", z=11,
             allow_overlap=True,
             points=[[0.30,0],[0.62,0.08],[0.84,0.35],[1,0.73],[0.76,1],[0.18,0.88],[0,0.38]],
             style=sty(fill="#F7FAFC", line=navy, line_weight_pt=1.2)),
        node("user_head", "ellipse_node", 150, 335, 92, 116, container="physical_scene", z=12,
             allow_overlap=True, style=sty(fill="#FFFFFF", line=navy, line_weight_pt=1.2,
                                           font_family="Arial", font_size_pt=7.0)),
        node("user_hair", "polygon_node", 137, 320, 108, 84, container="physical_scene", z=13,
             allow_overlap=True,
             points=[[0.05,0.6],[0.20,0.18],[0.55,0],[0.90,0.18],[1,0.48],[0.72,0.55],[0.62,1],[0.35,0.8]],
             style=sty(fill="#3B4F75", line=navy, line_weight_pt=1.0)),
        node("user_arm", "polygon_node", 225, 505, 180, 105, container="physical_scene", z=13,
             allow_overlap=True,
             points=[[0,0.10],[0.22,0],[0.62,0.53],[1,0.53],[1,0.82],[0.55,0.90],[0.18,0.50]],
             style=sty(fill="#FFFFFF", line=navy, line_weight_pt=1.1)),
        box("desk_top", 42, 580, 545, 44, "physical_scene", fill="#FFFFFF", weight=1.2,
            allow_overlap=True),
        box("desk_cabinet", 430, 624, 155, 260, "physical_scene", fill="#FFFFFF", weight=1.2),
        node("desk_leg", "polygon_node", 65, 624, 26, 230, container="physical_scene", z=8,
             points=[[0,0],[1,0],[1,1],[0,1]], style=sty(fill="#FFFFFF", line=navy, line_weight_pt=1.0)),
        box("keyboard", 275, 540, 150, 34, "physical_scene", fill="#FFFFFF", weight=1.0,
            allow_overlap=True),
        box("bookshelf", 560, 235, 105, 240, "physical_scene", fill="#FFFFFF", weight=1.0),
        node("bookshelf_lines", "grid_matrix", 566, 242, 93, 225, container="physical_scene", z=9,
             rows=3, cols=1, colored_cells=[], style=sty(cell_fill="#FFFFFF", grid_line="#17365D",
                                                         grid_line_weight_pt=0.55)),

        box("sensitive_display", 245, 280, 250, 210, "physical_scene", fill="#FFFFFF",
            weight=1.35, rounded=True),
        box("display_screen", 260, 300, 220, 150, "physical_scene", fill=pale_blue, weight=1.0),
        label("display_private", 270, 318, 200, 60, "PRIVATE", "physical_scene",
              size=6.8, weight="bold", role="node_text"),
        label("display_data", 270, 385, 200, 60, "DATA", "physical_scene",
              size=6.8, weight="bold", role="node_text"),
        box("display_stand", 350, 490, 40, 45, "physical_scene", fill="#FFFFFF", weight=1.0),
        node("display_base", "polygon_node", 310, 532, 120, 16, container="physical_scene", z=11,
             points=[[0,0],[1,0],[1,1],[0,1]], style=sty(fill="#FFFFFF", line=navy, line_weight_pt=1.0)),

        node("phone_hand", "ellipse_node", 585, 635, 105, 185, container="physical_scene", z=9,
             allow_overlap=True, style=sty(fill="#FFF7F2", line=red, line_weight_pt=1.0,
                                           font_family="Arial", font_size_pt=7.0)),
        box("smartphone", 608, 520, 72, 155, "physical_scene", fill="#FFFFFF", line=red,
            weight=1.35, rounded=True, z=14, allow_overlap=True),
        box("phone_screen", 618, 540, 52, 108, "physical_scene", fill="#FFF6F2", line=red,
            weight=0.8, z=15),
        node("phone_lens", "ellipse_node", 620, 527, 11, 11, container="physical_scene", z=16,
             allow_overlap=True, style=sty(fill="#FFFFFF", line=red, line_weight_pt=0.8,
                                           font_family="Arial", font_size_pt=7.0)),

        label("panel_b_title", 760, 22, 740, 62, "(b)  Asymmetric perception",
              "human_region", size=7.8, weight="bold", role="panel_title", align=1),
        label("human_eye_label", 875, 90, 260, 58, "Human eye", "human_region",
              size=6.8, color=green, weight="bold"),
        node("human_eye", "ellipse_node", 920, 145, 165, 92, container="human_region", z=13,
             style=sty(fill="#FFFFFF", line=green, line_weight_pt=1.35,
                       font_family="Arial", font_size_pt=7.0)),
        node("human_pupil", "ellipse_node", 982, 162, 42, 56, container="human_region", z=14,
             allow_overlap=True, style=sty(fill="#179447", line=green, line_weight_pt=1.0,
                                           font_family="Arial", font_size_pt=7.0)),
        label("integration_line1", 1300, 330, 200, 45, "Temporal", "human_region",
              size=6.5, color=green, weight="bold"),
        label("integration_line2", 1300, 375, 200, 45, "integration", "human_region",
              size=6.5, color=green, weight="bold"),
        box("readable_display", 1270, 130, 230, 160, "human_region", fill="#FFFFFF",
            line=navy, weight=1.35, rounded=True),
        box("readable_screen", 1285, 148, 200, 105, "human_region", fill=pale_blue, line=navy,
            weight=0.9, allow_overlap=True),
        glyph_grid("readable_glyph_grid", 1340, 155, 90, 90, GLYPH_A_CELLS, "human_region"),
        box("readable_stand", 1378, 290, 30, 27, "human_region", fill="#FFFFFF", weight=0.9),
        node("readable_base", "polygon_node", 1355, 315, 78, 12, container="human_region", z=11,
             points=[[0,0],[1,0],[1,1],[0,1]], style=sty(fill=navy, line=navy, line_weight_pt=0.5)),
        label("readable_label", 1235, 82, 265, 48, "Readable", "human_region",
              size=6.5, color=green, weight="bold", role="output_label"),

        box("subframe_1", 785, 465, 120, 100, "subframe_region", fill="#FFFFFF", weight=1.1, rounded=True),
        glyph_grid("subframe_grid_1", 809, 475, 72, 72, SUBFRAME_CELLS[0], "subframe_region"),
        node("subframe_1_base", "polygon_node", 820, 565, 50, 12, container="subframe_region", z=12,
             points=[[0,0],[1,0],[1,1],[0,1]], style=sty(fill=navy,line=navy,line_weight_pt=0.5)),
        box("subframe_2", 935, 465, 120, 100, "subframe_region", fill="#FFFFFF", weight=1.1, rounded=True),
        glyph_grid("subframe_grid_2", 959, 475, 72, 72, SUBFRAME_CELLS[1], "subframe_region"),
        node("subframe_2_base", "polygon_node", 970, 565, 50, 12, container="subframe_region", z=12,
             points=[[0,0],[1,0],[1,1],[0,1]], style=sty(fill=navy,line=navy,line_weight_pt=0.5)),
        box("subframe_3", 1085, 465, 120, 100, "subframe_region", fill="#FFFFFF", weight=1.1, rounded=True),
        glyph_grid("subframe_grid_3", 1109, 475, 72, 72, SUBFRAME_CELLS[2], "subframe_region"),
        node("subframe_3_base", "polygon_node", 1120, 565, 50, 12, container="subframe_region", z=12,
             points=[[0,0],[1,0],[1,1],[0,1]], style=sty(fill=navy,line=navy,line_weight_pt=0.5)),
        box("subframe_4", 1235, 465, 120, 100, "subframe_region", fill="#FFFFFF", weight=1.1, rounded=True),
        glyph_grid("subframe_grid_4", 1259, 475, 72, 72, SUBFRAME_CELLS[3], "subframe_region"),
        node("subframe_4_base", "polygon_node", 1270, 565, 50, 12, container="subframe_region", z=12,
             points=[[0,0],[1,0],[1,1],[0,1]], style=sty(fill=navy,line=navy,line_weight_pt=0.5)),
        node("selection_left", "bracket", 925, 450, 16, 135, container="subframe_region", z=18,
             orientation="left", shape="square", tick_positions=[0,1],
             style=sty(line=red, line_weight_pt=1.2)),
        node("selection_right", "bracket", 1050, 450, 16, 135, container="subframe_region", z=18,
             orientation="right", shape="square", tick_positions=[0,1],
             style=sty(line=red, line_weight_pt=1.2)),
        label("subframe_label_1", 1120, 580, 350, 38, "Rapid", "subframe_region",
              size=6.5, weight="bold"),
        label("subframe_label_2", 1120, 615, 350, 38, "complementary", "subframe_region",
              size=6.5, weight="bold"),
        label("subframe_label_3", 1120, 650, 350, 38, "subframes", "subframe_region",
              size=6.5, weight="bold"),

        box("camera_icon", 900, 800, 115, 88, "camera_region", fill="#FFFFFF", line=red,
            weight=1.35, rounded=True),
        node("camera_lens", "ellipse_node", 937, 819, 42, 42, container="camera_region", z=14,
             allow_overlap=True, style=sty(fill="#FFFFFF", line=red, line_weight_pt=1.2,
                                           font_family="Arial", font_size_pt=7.0)),
        node("camera_top", "polygon_node", 928, 786, 34, 16, container="camera_region", z=13,
             allow_overlap=True, points=[[0,0],[1,0],[1,1],[0,1]],
             style=sty(fill="#FFFFFF", line=red, line_weight_pt=1.0)),
        label("camera_label", 850, 905, 180, 48, "Camera", "camera_region",
              size=6.7, color=red, weight="bold"),
        label("sampling_label_1", 1020, 700, 300, 45, "Short-exposure", "camera_region",
              size=6.5, color=red, weight="bold"),
        label("sampling_label_2", 1020, 745, 300, 45, "sampling", "camera_region",
              size=6.5, color=red, weight="bold"),
        box("fragment_display", 1190, 800, 115, 88, "camera_region", fill="#FFFFFF",
            line=navy, weight=1.1, rounded=True),
        glyph_grid(
            "fragment_grid", 1218, 812, 60, 60,
            SUBFRAME_CELLS[SELECTED_SUBFRAME_INDEX], "camera_region",
        ),
        node("fragment_base", "polygon_node", 1222, 888, 50, 12, container="camera_region", z=12,
             points=[[0,0],[1,0],[1,1],[0,1]], style=sty(fill=navy,line=navy,line_weight_pt=0.5)),
        label("fragment_label_1", 1170, 905, 240, 48, "Unreadable", "camera_region",
              size=6.5, color=red, weight="bold"),
        label("fragment_label_2", 1170, 943, 240, 48, "fragment", "camera_region",
              size=6.5, color=red, weight="bold"),
        node("ocr_failure", "ellipse_node", 1395, 798, 105, 92, text="OCR", container="camera_region", z=13,
             style=sty(fill="#FFFFFF", line=red, line_weight_pt=1.25, text_color=navy,
                       source_font_family="Arial", font_family="Arial", font_family_candidates=["Arial","Calibri"],
                       font_role="sans", font_size_pt=6.8, min_font_size_pt=6.5, font_weight="bold",
                       text_fit="single_line", constrain_text_box=True, text_margin_in=0.0)),
    ]

    edges = [
        {"id":"capture_ray_upper","type":"line_segment","arrow_plan_id":"A001",
         "from_point":[480,365],"to_point":[610,545],"route":"straight","allow_diagonal":True,
         "style":{"line":red,"line_weight_pt":1.0,"line_dash":"dash","end_arrow":"none"},"z":30},
        {"id":"capture_ray_lower","type":"line_segment","arrow_plan_id":"A002",
         "from_point":[480,430],"to_point":[610,630],"route":"straight","allow_diagonal":True,
         "style":{"line":red,"line_weight_pt":1.0,"line_dash":"dash","end_arrow":"none"},"z":30},
        {"id":"sequence_1_to_2","type":"lane_arrow","arrow_plan_id":"A003a",
         "from_point":[912,515],"to_point":[928,515],"route":"horizontal","lane_axis":"horizontal",
         "style":{"line":navy,"line_weight_pt":1.15,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"sequence_2_to_3","type":"lane_arrow","arrow_plan_id":"A003b",
         "from_point":[1062,515],"to_point":[1078,515],"route":"horizontal","lane_axis":"horizontal",
         "style":{"line":navy,"line_weight_pt":1.15,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"sequence_3_to_4","type":"lane_arrow","arrow_plan_id":"A003c",
         "from_point":[1212,515],"to_point":[1228,515],"route":"horizontal","lane_axis":"horizontal",
         "style":{"line":navy,"line_weight_pt":1.15,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"frame1_to_eye","type":"arrow_connector","arrow_plan_id":"A004",
         "from":"subframe_1:top@0.50","to":"human_eye:bottom@0.15","route":"straight",
         "allow_diagonal":True,"allow_cross_container":True,
         "style":{"line":green,"line_weight_pt":1.2,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"frame2_to_eye","type":"arrow_connector","arrow_plan_id":"A005",
         "from":"subframe_2:top@0.50","to":"human_eye:bottom@0.38","route":"straight",
         "allow_diagonal":True,"allow_cross_container":True,
         "style":{"line":green,"line_weight_pt":1.2,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"frame3_to_eye","type":"arrow_connector","arrow_plan_id":"A006",
         "from":"subframe_3:top@0.50","to":"human_eye:bottom@0.62","route":"straight",
         "allow_diagonal":True,"allow_cross_container":True,
         "style":{"line":green,"line_weight_pt":1.2,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"frame4_to_eye","type":"arrow_connector","arrow_plan_id":"A007",
         "from":"subframe_4:top@0.50","to":"human_eye:bottom@0.85","route":"straight",
         "allow_diagonal":True,"allow_cross_container":True,
         "style":{"line":green,"line_weight_pt":1.2,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"eye_to_readable","type":"lane_arrow","arrow_plan_id":"A008",
         "from":"human_eye:right@0.50","to":"readable_display:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":green,"line_weight_pt":1.25,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"selected_to_camera","type":"lane_arrow","arrow_plan_id":"A009",
         "from":"subframe_2:bottom@0.50","to":"camera_icon:top@0.50","route":"vertical","lane_axis":"vertical",
         "allow_cross_container":True,
         "style":{"line":red,"line_weight_pt":1.25,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"camera_to_fragment","type":"lane_arrow","arrow_plan_id":"A010",
         "from":"camera_icon:right@0.50","to":"fragment_display:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":red,"line_weight_pt":1.25,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"fragment_to_ocr","type":"lane_arrow","arrow_plan_id":"A011",
         "from":"fragment_display:right@0.50","to":"ocr_failure:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":red,"line_weight_pt":1.25,"end_arrow":"triangle","arrow_size":"small"},"z":25},
        {"id":"ocr_x_down","type":"line_segment","arrow_plan_id":"A012",
         "from_point":[1403,806],"to_point":[1492,882],"route":"straight","allow_diagonal":True,
         "style":{"line":red,"line_weight_pt":3.2,"end_arrow":"none"},"z":31},
        {"id":"ocr_x_up","type":"line_segment","arrow_plan_id":"A013",
         "from_point":[1492,806],"to_point":[1403,882],"route":"straight","allow_diagonal":True,
         "style":{"line":red,"line_weight_pt":3.2,"end_arrow":"none"},"z":31},
    ]

    scene = {
        "version": "0.1",
        "metadata": metadata,
        "page": {"width":1536,"height":1024,"units":"px","origin":"top-left",
                 "target_width_in":3.5,"background":"#FFFFFF"},
        "nodes": nodes,
        "edges": edges,
        "assets": [],
    }
    OUTPUT.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
