from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "figure1_concept_threat.scene.json"


def sty(**kwargs):
    return kwargs


def node(node_id, node_type, x, y, w, h, *, text="", container=None, z=10, **kwargs):
    item = {"id": node_id, "type": node_type, "x": x, "y": y, "w": w, "h": h, "text": text, "z": z}
    if container:
        item["container_id"] = container
    item.update(kwargs)
    return item


def label(node_id, x, y, w, h, text, container, *, size=7.0, color="#17365D",
          weight=None, role="small_label", align=1):
    text_style = sty(
        source_font_family="Arial",
        font_family="Arial",
        font_family_candidates=["Arial", "Helvetica", "Calibri"],
        font_role="sans",
        font_size_pt=size,
        min_font_size_pt=max(6.5, size - 0.7),
        text_fit="single_line",
        constrain_text_box=True,
        text_margin_in=0.0,
        text_align=align,
        text_color=color,
    )
    if weight:
        text_style["font_weight"] = weight
    return node(
        node_id, "text_block", x, y, w, h,
        text=text, container=container, z=20,
        semantic_role=role, text_role=role, style=text_style,
    )


def box(node_id, x, y, w, h, container, *, fill="#FFFFFF", line="#17365D",
        weight=1.1, rounded=False, z=10, **kwargs):
    return node(
        node_id, "rounded_process" if rounded else "process_box",
        x, y, w, h, container=container, z=z,
        style=sty(
            fill=fill, line=line, line_weight_pt=weight,
            rounding_in=0.025 if rounded else 0.0,
            shadow=None,
        ),
        **kwargs,
    )


def grid(node_id, x, y, w, h, cells, container):
    return node(
        node_id, "grid_matrix", x, y, w, h,
        container=container, z=13, rows=4, cols=5,
        colored_cells=[[r, c, "#17365D"] for r, c in cells],
        style=sty(
            cell_fill="#DFF3FA",
            grid_line="#C5DEEA",
            grid_line_weight_pt=0.25,
        ),
    )


def arrow_plan(plan_id, source_region, source_fact, from_object, from_anchor, to_object,
               to_anchor, direction, route_shape, line_style, arrowhead, intent, bbox,
               must_not_cross, relative):
    return {
        "id": plan_id,
        "source_region": source_region,
        "source_fact": source_fact,
        "from_visual_object": from_object,
        "from": f"{from_object} ({from_anchor})",
        "from_anchor_description": from_anchor,
        "to_visual_object": to_object,
        "to": f"{to_object} ({to_anchor})",
        "to_anchor_description": to_anchor,
        "direction": direction,
        "route_shape": route_shape,
        "line_style": line_style,
        "arrowhead": arrowhead,
        "semantic_intent": intent,
        "source_bbox_px": bbox,
        "must_not_cross": must_not_cross,
        "relative_position_facts": relative,
        "certainty": "certain",
    }


def main():
    navy = "#17365D"
    cyan = "#159FCF"
    green = "#177A36"
    red = "#D94722"
    pale_blue = "#DFF3FA"

    metadata = {
        "title": "Physical visual eavesdropping and asymmetric perception",
        "created_by": "codex.visiomaster.fresh_round1",
        "style_profile": "paper_white",
        "fidelity": "exact",
        "replica_review_mode": "strict_replica",
        "replica_stage": "layout_topology",
        "source_image": str((ROOT / "source" / "original.png").resolve()).replace("\\", "/"),
        "source_aspect_ratio": 1.5,
        "region_strategy": "region_first",
        "font_scale": {
            "panel_title": 8.3,
            "body": 7.0,
            "small_label": 6.7,
            "display_text": 7.5,
        },
        "notes": [
            "Fresh source-driven editorial vector reconstruction.",
            "All scientific labels, displays, subframes, and connectors remain editable.",
            "Office decoration is simplified only where it does not carry scientific meaning.",
        ],
        "source_visual_inventory": {
            "analysis_basis": "visual_llm_source_image",
            "language_profile": "english_labels",
            "do_not_translate": True,
            "unknown_text_policy": "mark_unreadable_do_not_invent",
            "scene_authoring_mode": "fresh_from_source_inventory",
            "prior_scene_policy": "do_not_read_or_patch_prior_round_scene",
            "regions": [
                {
                    "id": "global_layout",
                    "source_bbox_px": [0, 0, 1536, 1024],
                    "required_crop_types": ["global"],
                    "required_labels": [
                        "(a) Physical visual eavesdropping",
                        "(b) Asymmetric perception",
                    ],
                    "required_formulas": [],
                    "required_component_motifs": ["two-panel 3:2 concept figure", "central divider"],
                    "required_edge_motifs": ["physical capture cone", "human and camera outcome branches"],
                    "required_ports_or_boundaries": ["central panel divider"],
                    "text_layout_facts": ["panel headings share the top band"],
                    "box_style_facts": ["white background", "no visible outer frame"],
                    "line_style_facts": ["navy structural line art", "green and orange-red semantic routes"],
                    "shadow_facts": ["none"],
                    "density_facts": ["balanced left scene and right mechanism"],
                    "uncertain_text": [],
                },
                {
                    "id": "physical_scene",
                    "source_bbox_px": [0, 0, 730, 1024],
                    "required_crop_types": ["input", "small_text"],
                    "required_labels": [
                        "(a) Physical visual eavesdropping", "Authorized user",
                        "Sensitive display", "Smartphone camera", "PRIVATE DATA",
                    ],
                    "required_formulas": [],
                    "required_component_motifs": [
                        "seated authorized user", "desktop sensitive display",
                        "one smartphone camera", "office desk and chair",
                    ],
                    "required_edge_motifs": ["two dashed orange-red capture rays"],
                    "required_ports_or_boundaries": ["thin central panel divider"],
                    "text_layout_facts": [
                        "panel heading is one line",
                        "object labels occupy dedicated rows",
                        "PRIVATE and DATA use two centered lines",
                    ],
                    "box_style_facts": ["flat white office line art", "pale blue monitor screen"],
                    "line_style_facts": ["navy structural outlines", "dashed orange-red capture cone"],
                    "shadow_facts": ["none"],
                    "density_facts": ["main person-screen-phone triangle dominates"],
                    "uncertain_text": [],
                },
                {
                    "id": "subframe_row",
                    "source_bbox_px": [760, 350, 1500, 610],
                    "required_crop_types": ["core", "arrow_dense", "small_text"],
                    "required_labels": ["Rapid complementary subframes", "Fast time"],
                    "required_formulas": [],
                    "required_component_motifs": [
                        "four sparse display thumbnails", "one selected exposure bracket",
                    ],
                    "required_edge_motifs": ["right-pointing fast-time arrow"],
                    "required_ports_or_boundaries": ["selected second subframe"],
                    "text_layout_facts": ["four thumbnails share one baseline"],
                    "box_style_facts": ["light-cyan screens", "navy sparse pixels"],
                    "line_style_facts": ["navy time axis", "orange-red selection bracket"],
                    "shadow_facts": ["none"],
                    "density_facts": ["compact row with equal gaps"],
                    "uncertain_text": [],
                },
                {
                    "id": "human_output",
                    "source_bbox_px": [900, 60, 1510, 350],
                    "required_crop_types": ["output", "arrow_dense", "small_text"],
                    "required_labels": [
                        "Human eye", "Temporal integration ≈ 50 ms", "Readable", "PRIVATE DATA",
                    ],
                    "required_formulas": [],
                    "required_component_motifs": ["eye", "readable display"],
                    "required_edge_motifs": [
                        "four green subframe-to-eye arrows", "green eye-to-display arrow",
                    ],
                    "required_ports_or_boundaries": ["four-to-one integration"],
                    "text_layout_facts": ["integration label uses two dedicated lines"],
                    "box_style_facts": ["green outline and labels"],
                    "line_style_facts": ["solid green arrows"],
                    "shadow_facts": ["none"],
                    "density_facts": ["eye and readable display dominate"],
                    "uncertain_text": [],
                },
                {
                    "id": "camera_output",
                    "source_bbox_px": [870, 610, 1536, 940],
                    "required_crop_types": ["output", "arrow_dense", "small_text"],
                    "required_labels": [
                        "Camera", "Instantaneous sampling", "Unreadable fragment", "OCR",
                    ],
                    "required_formulas": [],
                    "required_component_motifs": ["camera", "sparse fragment", "OCR failure"],
                    "required_edge_motifs": [
                        "selected frame to camera", "camera to fragment", "fragment to OCR",
                    ],
                    "required_ports_or_boundaries": ["one-frame selection"],
                    "text_layout_facts": ["labels use separate rows below objects"],
                    "box_style_facts": ["orange-red outline and labels"],
                    "line_style_facts": ["solid orange-red local arrows"],
                    "shadow_facts": ["none"],
                    "density_facts": ["three-object horizontal outcome chain"],
                    "uncertain_text": [],
                },
            ],
        },
        "region_plan": [
            {
                "id": "global_layout", "crop_type": "global",
                "source_bbox_px": [0, 0, 1536, 1024],
                "target_bbox": [0, 0, 1536, 1024],
                "review_focus": "global layout, two panels, page aspect",
            },
            {
                "id": "physical_input", "crop_type": "input",
                "source_bbox_px": [0, 0, 730, 1024],
                "target_bbox": [20, 20, 710, 1000],
                "container_id": "physical_scene",
                "review_focus": "physical input threat and labels",
            },
            {
                "id": "subframe_core", "crop_type": "core",
                "source_bbox_px": [760, 350, 1500, 610],
                "target_bbox": [750, 350, 1510, 620],
                "container_id": "subframe_region",
                "review_focus": "core subframe row and selection",
            },
            {
                "id": "human_output", "crop_type": "output",
                "source_bbox_px": [900, 60, 1510, 350],
                "target_bbox": [830, 80, 1510, 350],
                "container_id": "human_region",
                "review_focus": "right output human integration",
            },
            {
                "id": "camera_output", "crop_type": "output",
                "source_bbox_px": [870, 610, 1536, 940],
                "target_bbox": [850, 650, 1520, 940],
                "container_id": "camera_region",
                "review_focus": "right output camera sampling",
            },
            {
                "id": "arrow_dense", "crop_type": "arrow_dense",
                "source_bbox_px": [760, 120, 1536, 900],
                "target_bbox": [760, 120, 1520, 930],
                "review_focus": "arrow dense topology and selected-frame route",
            },
            {
                "id": "small_text", "crop_type": "small_text",
                "source_bbox_px": [20, 0, 1536, 960],
                "target_bbox": [20, 0, 1520, 960],
                "review_focus": "small text labels and display words",
            },
        ],
        "arrow_plan": [
            arrow_plan("A001", "physical_scene", "Upper dashed capture ray runs from the display to the smartphone.",
                       "sensitive_display", "right edge upper half", "smartphone", "left edge upper half",
                       "left_to_right", "diagonal", "dashed", "none", "callout",
                       [425, 395, 640, 550], ["PRIVATE DATA", "Smartphone camera"], ["upper boundary of capture cone"]),
            arrow_plan("A002", "physical_scene", "Lower dashed capture ray runs from the display to the smartphone.",
                       "sensitive_display", "right edge lower half", "smartphone", "left edge lower half",
                       "left_to_right", "diagonal", "dashed", "none", "callout",
                       [420, 455, 640, 650], ["desk label", "Smartphone camera"], ["lower boundary of capture cone"]),
            arrow_plan("A003", "subframe_row", "Fast-time arrow runs rightward above the four subframes.",
                       "time_start", "free point", "time_end", "free point",
                       "left_to_right", "straight_horizontal", "solid", "end", "annotation",
                       [780, 410, 1410, 450], ["Rapid complementary subframes"], ["above subframe row"]),
            arrow_plan("A004", "human_output", "First subframe feeds the human eye.",
                       "subframe_1", "top edge", "human_eye", "lower-left edge",
                       "bottom_to_top", "diagonal", "solid", "end", "data_flow",
                       [820, 220, 1080, 500], ["Rapid complementary subframes"], ["leftmost integration leg"]),
            arrow_plan("A005", "human_output", "Second subframe feeds the human eye.",
                       "subframe_2", "top edge", "human_eye", "lower-left center",
                       "bottom_to_top", "diagonal", "solid", "end", "data_flow",
                       [950, 220, 1100, 500], ["Rapid complementary subframes"], ["second integration leg"]),
            arrow_plan("A006", "human_output", "Third subframe feeds the human eye.",
                       "subframe_3", "top edge", "human_eye", "lower-right center",
                       "bottom_to_top", "diagonal", "solid", "end", "data_flow",
                       [1080, 220, 1160, 500], ["Rapid complementary subframes"], ["third integration leg"]),
            arrow_plan("A007", "human_output", "Fourth subframe feeds the human eye.",
                       "subframe_4", "top edge", "human_eye", "lower-right edge",
                       "bottom_to_top", "diagonal", "solid", "end", "data_flow",
                       [1170, 220, 1330, 500], ["Rapid complementary subframes"], ["rightmost integration leg"]),
            arrow_plan("A008", "human_output", "The human eye feeds the readable display.",
                       "human_eye", "right edge midpoint", "readable_display", "left edge midpoint",
                       "left_to_right", "straight_horizontal", "solid", "end", "data_flow",
                       [1180, 170, 1310, 230], ["Temporal integration label"], ["upper human lane"]),
            arrow_plan("A009", "camera_output", "The selected second subframe feeds the camera.",
                       "subframe_2", "bottom edge midpoint", "camera_icon", "top edge midpoint",
                       "top_to_bottom", "straight_vertical", "solid", "end", "data_flow",
                       [970, 540, 1030, 730], ["Instantaneous sampling"], ["vertical selection lane"]),
            arrow_plan("A010", "camera_output", "The camera outputs one unreadable fragment.",
                       "camera_icon", "right edge midpoint", "fragment_display", "left edge midpoint",
                       "left_to_right", "straight_horizontal", "solid", "end", "data_flow",
                       [1040, 720, 1190, 770], ["Instantaneous sampling"], ["lower camera lane"]),
            arrow_plan("A011", "camera_output", "The unreadable fragment reaches OCR failure.",
                       "fragment_display", "right edge midpoint", "ocr_failure", "left edge midpoint",
                       "left_to_right", "straight_horizontal", "solid", "end", "data_flow",
                       [1300, 720, 1420, 780], ["Unreadable fragment"], ["lower outcome lane"]),
        ],
    }

    nodes = [
        node("page_background", "page_background", 0, 0, 1536, 1024, z=-100),
        node("physical_scene", "audit_region", 20, 20, 690, 980, z=-10,
             label="Physical visual eavesdropping", source_bbox_px=[0,0,730,1024],
             source_aspect_ratio=0.713, style=sty(fill="none", line="none")),
        node("subframe_region", "audit_region", 750, 350, 760, 270, z=-10,
             label="Rapid complementary subframes", source_bbox_px=[760,350,1500,610],
             source_aspect_ratio=2.846, style=sty(fill="none", line="none")),
        node("human_region", "audit_region", 830, 80, 680, 270, z=-10,
             label="Human integration", source_bbox_px=[900,60,1510,350],
             source_aspect_ratio=2.103, style=sty(fill="none", line="none")),
        node("camera_region", "audit_region", 850, 650, 670, 290, z=-10,
             label="Camera sampling", source_bbox_px=[870,610,1536,940],
             source_aspect_ratio=2.018, style=sty(fill="none", line="none")),
        node("panel_divider", "polygon_node", 720, 20, 4, 980, z=5,
             points=[[0,0],[1,0],[1,1],[0,1]],
             style=sty(fill=navy, line=navy, line_weight_pt=0.6)),

        label("panel_a_title", 38, 22, 665, 60, "(a)  Physical visual eavesdropping",
              "physical_scene", size=7.2, weight="bold", role="panel_title", align=0),
        label("authorized_line1", 38, 235, 190, 48, "Authorized", "physical_scene",
              size=7.0, weight="bold"),
        label("authorized_line2", 38, 278, 190, 48, "user", "physical_scene",
              size=7.0, weight="bold"),
        label("sensitive_line1", 278, 175, 190, 48, "Sensitive", "physical_scene",
              size=7.0, weight="bold"),
        label("sensitive_line2", 278, 218, 190, 48, "display", "physical_scene",
              size=7.0, weight="bold"),
        label("phone_line1", 505, 765, 190, 48, "Smartphone", "physical_scene",
              size=7.0, color=red, weight="bold"),
        label("phone_line2", 505, 808, 190, 48, "camera", "physical_scene",
              size=7.0, color=red, weight="bold"),

        box("chair_back", 55, 500, 120, 300, "physical_scene", rounded=True, weight=1.2),
        box("chair_seat", 105, 725, 185, 52, "physical_scene", rounded=True, weight=1.2),
        box("chair_post", 150, 777, 25, 115, "physical_scene", weight=1.0),
        node("chair_base", "polygon_node", 95, 875, 150, 75, container="physical_scene", z=8,
             points=[[0.5,0],[0.5,0.35],[0,1],[0.5,0.35],[1,1]],
             style=sty(fill="none", line=navy, line_weight_pt=1.1)),
        node("user_torso", "polygon_node", 90, 455, 230, 290, container="physical_scene", z=11,
             points=[[0.32,0],[0.62,0.08],[0.85,0.35],[1,0.75],[0.75,1],[0.18,0.88],[0,0.38]],
             style=sty(fill="#F7FAFC", line=navy, line_weight_pt=1.2)),
        node("user_head", "ellipse_node", 145, 335, 90, 115, container="physical_scene", z=12,
             style=sty(fill="#FFFFFF", line=navy, line_weight_pt=1.2)),
        node("user_hair", "polygon_node", 132, 320, 105, 83, container="physical_scene", z=13,
             points=[[0.05,0.6],[0.2,0.18],[0.55,0],[0.9,0.18],[1,0.48],[0.72,0.55],[0.62,1],[0.35,0.8]],
             style=sty(fill="#3B4F75", line=navy, line_weight_pt=1.0)),
        node("user_arm", "polygon_node", 220, 500, 175, 110, container="physical_scene", z=13,
             points=[[0,0.1],[0.22,0],[0.62,0.55],[1,0.55],[1,0.82],[0.55,0.9],[0.18,0.5]],
             style=sty(fill="#FFFFFF", line=navy, line_weight_pt=1.1)),

        box("desk_top", 45, 575, 535, 45, "physical_scene", fill="#FFFFFF", weight=1.2),
        box("desk_cabinet", 425, 620, 150, 260, "physical_scene", fill="#FFFFFF", weight=1.2),
        box("desk_leg", 65, 620, 25, 225, "physical_scene", fill="#FFFFFF", weight=1.0),
        box("keyboard", 270, 535, 145, 34, "physical_scene", fill="#FFFFFF", weight=1.0),
        box("bookshelf", 560, 225, 105, 250, "physical_scene", fill="#FFFFFF", weight=1.0),
        box("shelf_1", 565, 305, 95, 8, "physical_scene", fill=navy, line=navy, weight=0.5),
        box("shelf_2", 565, 390, 95, 8, "physical_scene", fill=navy, line=navy, weight=0.5),

        box("sensitive_display", 250, 280, 230, 205, "physical_scene", fill="#FFFFFF", weight=1.35, rounded=True),
        box("display_screen", 265, 300, 200, 145, "physical_scene", fill=pale_blue, weight=1.0),
        label("display_private", 280, 320, 170, 52, "PRIVATE", "physical_scene",
              size=7.6, weight="bold", role="node_text"),
        label("display_data", 280, 382, 170, 52, "DATA", "physical_scene",
              size=7.6, weight="bold", role="node_text"),
        box("display_stand", 345, 485, 38, 48, "physical_scene", fill="#FFFFFF", weight=1.0),
        box("display_base", 310, 528, 110, 18, "physical_scene", fill="#FFFFFF", weight=1.0, rounded=True),

        node("phone_hand", "ellipse_node", 585, 625, 100, 190, container="physical_scene", z=9,
             style=sty(fill="#FFF7F2", line=red, line_weight_pt=1.0)),
        box("smartphone", 610, 520, 68, 150, "physical_scene", fill="#FFFFFF", line=red,
            weight=1.35, rounded=True, z=14),
        box("phone_screen", 619, 540, 50, 105, "physical_scene", fill="#FFF6F2", line=red, weight=0.8, z=15),
        node("phone_lens", "ellipse_node", 621, 526, 10, 10, container="physical_scene", z=16,
             style=sty(fill="#FFFFFF", line=red, line_weight_pt=0.8)),

        label("panel_b_title", 760, 22, 740, 60, "(b)  Asymmetric perception",
              "human_region", size=7.8, weight="bold", role="panel_title", align=1),
        label("human_eye_label", 1010, 92, 220, 48, "Human eye", "human_region",
              size=7.2, color=green, weight="bold"),
        node("human_eye", "ellipse_node", 1020, 150, 160, 90, container="human_region", z=13,
             style=sty(fill="#FFFFFF", line=green, line_weight_pt=1.35)),
        node("human_pupil", "ellipse_node", 1080, 167, 42, 56, container="human_region", z=14,
             style=sty(fill="#179447", line=green, line_weight_pt=1.0)),
        label("integration_label", 1280, 285, 210, 42, "Temporal integration", "human_region",
              size=6.6, color=green, weight="bold"),
        label("integration_time", 1280, 325, 210, 42, "≈ 50 ms", "human_region",
              size=6.8, color=green, weight="bold"),
        box("readable_display", 1320, 130, 170, 145, "human_region", fill="#FFFFFF", line=navy,
            weight=1.35, rounded=True),
        box("readable_screen", 1332, 145, 146, 100, "human_region", fill=pale_blue, line=navy, weight=0.9),
        label("readable_private", 1340, 153, 130, 40, "PRIVATE", "human_region",
              size=7.2, weight="bold", role="node_text"),
        label("readable_data", 1340, 198, 130, 40, "DATA", "human_region",
              size=7.2, weight="bold", role="node_text"),
        box("readable_stand", 1390, 275, 30, 28, "human_region", fill="#FFFFFF", weight=0.9),
        box("readable_base", 1365, 300, 80, 12, "human_region", fill=navy, line=navy, weight=0.5),
        label("readable_label", 1120, 285, 140, 42, "Readable", "human_region",
              size=7.0, color=green, weight="bold", role="output_label"),

        label("subframe_label", 1090, 600, 400, 52, "Rapid complementary subframes",
              "subframe_region", size=7.0, weight="bold"),
        label("fast_time_label", 1360, 400, 130, 42, "Fast time", "subframe_region",
              size=6.8, weight="bold"),
        box("subframe_1", 785, 470, 120, 100, "subframe_region", fill="#FFFFFF", weight=1.1, rounded=True),
        grid("subframe_grid_1", 795, 480, 100, 72, [(0,0),(0,2),(2,4),(3,1)], "subframe_region"),
        box("subframe_1_base", 820, 570, 50, 12, "subframe_region", fill=navy, line=navy, weight=0.5),
        box("subframe_2", 935, 470, 120, 100, "subframe_region", fill="#FFFFFF", weight=1.1, rounded=True),
        grid("subframe_grid_2", 945, 480, 100, 72, [(0,1),(0,3),(0,4),(2,2)], "subframe_region"),
        box("subframe_2_base", 970, 570, 50, 12, "subframe_region", fill=navy, line=navy, weight=0.5),
        box("subframe_3", 1085, 470, 120, 100, "subframe_region", fill="#FFFFFF", weight=1.1, rounded=True),
        grid("subframe_grid_3", 1095, 480, 100, 72, [(1,0),(2,1),(3,2),(2,3),(1,4)], "subframe_region"),
        box("subframe_3_base", 1120, 570, 50, 12, "subframe_region", fill=navy, line=navy, weight=0.5),
        box("subframe_4", 1235, 470, 120, 100, "subframe_region", fill="#FFFFFF", weight=1.1, rounded=True),
        grid("subframe_grid_4", 1245, 480, 100, 72, [(0,2),(0,3),(1,3),(2,0),(3,3)], "subframe_region"),
        box("subframe_4_base", 1270, 570, 50, 12, "subframe_region", fill=navy, line=navy, weight=0.5),
        node("selection_left", "bracket", 925, 455, 16, 135, container="subframe_region", z=18,
             orientation="left", shape="square", tick_positions=[0,1],
             style=sty(line=red, line_weight_pt=1.2)),
        node("selection_right", "bracket", 1050, 455, 16, 135, container="subframe_region", z=18,
             orientation="right", shape="square", tick_positions=[0,1],
             style=sty(line=red, line_weight_pt=1.2)),

        box("camera_icon", 920, 700, 120, 90, "camera_region", fill="#FFFFFF", line=red,
            weight=1.35, rounded=True),
        node("camera_lens", "ellipse_node", 958, 720, 44, 44, container="camera_region", z=14,
             allow_overlap=True, style=sty(fill="#FFFFFF", line=red, line_weight_pt=1.2)),
        box("camera_top", 945, 685, 34, 18, "camera_region", fill="#FFFFFF", line=red,
            weight=1.0, z=13, allow_overlap=True),
        label("camera_label", 905, 800, 150, 42, "Camera", "camera_region",
              size=7.0, color=red, weight="bold"),
        label("sampling_label", 1040, 615, 190, 42, "Instantaneous", "camera_region",
              size=6.8, color=red, weight="bold"),
        label("sampling_label_2", 1040, 655, 190, 42, "sampling", "camera_region",
              size=6.8, color=red, weight="bold"),
        box("fragment_display", 1190, 700, 115, 90, "camera_region", fill="#FFFFFF", line=navy,
            weight=1.1, rounded=True),
        grid("fragment_grid", 1200, 710, 95, 62, [(0,0),(3,3)], "camera_region"),
        box("fragment_base", 1222, 790, 50, 12, "camera_region", fill=navy, line=navy, weight=0.5),
        label("fragment_label", 1160, 820, 175, 42, "Unreadable", "camera_region",
              size=6.8, color=red, weight="bold"),
        label("fragment_label_2", 1160, 858, 175, 42, "fragment", "camera_region",
              size=6.8, color=red, weight="bold"),
        node("ocr_failure", "ellipse_node", 1390, 700, 105, 95, text="OCR ×", container="camera_region", z=13,
             style=sty(
                 fill="#FFFFFF", line=red, line_weight_pt=1.25,
                 text_color=navy, source_font_family="Arial", font_family="Arial",
                 font_family_candidates=["Arial", "Calibri"], font_role="sans",
                 font_size_pt=7.0, min_font_size_pt=6.5, font_weight="bold",
                 text_fit="single_line", constrain_text_box=True, text_margin_in=0.0,
             )),
    ]

    edges = [
        {
            "id": "capture_ray_upper", "type": "line_segment", "arrow_plan_id": "A001",
            "from_point": [465, 365], "to_point": [612, 545], "route": "straight",
            "allow_diagonal": True,
            "style": {"line": red, "line_weight_pt": 1.0, "line_dash": "dash", "end_arrow": "none"},
            "z": 30,
        },
        {
            "id": "capture_ray_lower", "type": "line_segment", "arrow_plan_id": "A002",
            "from_point": [465, 430], "to_point": [612, 630], "route": "straight",
            "allow_diagonal": True,
            "style": {"line": red, "line_weight_pt": 1.0, "line_dash": "dash", "end_arrow": "none"},
            "z": 30,
        },
        {
            "id": "time_axis", "type": "lane_arrow", "arrow_plan_id": "A003",
            "from_point": [785, 440], "to_point": [1350, 440], "route": "horizontal",
            "lane_axis": "horizontal",
            "style": {"line": navy, "line_weight_pt": 1.15, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
        {
            "id": "frame1_to_eye", "type": "arrow_connector", "arrow_plan_id": "A004",
            "from": "subframe_1:top@0.50", "to": "human_eye:bottom@0.15", "route": "straight",
            "allow_diagonal": True, "allow_cross_container": True,
            "style": {"line": green, "line_weight_pt": 1.2, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
        {
            "id": "frame2_to_eye", "type": "arrow_connector", "arrow_plan_id": "A005",
            "from": "subframe_2:top@0.50", "to": "human_eye:bottom@0.38", "route": "straight",
            "allow_diagonal": True, "allow_cross_container": True,
            "style": {"line": green, "line_weight_pt": 1.2, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
        {
            "id": "frame3_to_eye", "type": "arrow_connector", "arrow_plan_id": "A006",
            "from": "subframe_3:top@0.50", "to": "human_eye:bottom@0.62", "route": "straight",
            "allow_diagonal": True, "allow_cross_container": True,
            "style": {"line": green, "line_weight_pt": 1.2, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
        {
            "id": "frame4_to_eye", "type": "arrow_connector", "arrow_plan_id": "A007",
            "from": "subframe_4:top@0.50", "to": "human_eye:bottom@0.85", "route": "straight",
            "allow_diagonal": True, "allow_cross_container": True,
            "style": {"line": green, "line_weight_pt": 1.2, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
        {
            "id": "eye_to_readable", "type": "lane_arrow", "arrow_plan_id": "A008",
            "from": "human_eye:right@0.50", "to": "readable_display:left@0.50", "route": "horizontal",
            "lane_axis": "horizontal",
            "style": {"line": green, "line_weight_pt": 1.25, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
        {
            "id": "selected_to_camera", "type": "lane_arrow", "arrow_plan_id": "A009",
            "from": "subframe_2:bottom@0.50", "to": "camera_icon:top@0.50", "route": "vertical",
            "lane_axis": "vertical", "allow_cross_container": True,
            "style": {"line": red, "line_weight_pt": 1.25, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
        {
            "id": "camera_to_fragment", "type": "lane_arrow", "arrow_plan_id": "A010",
            "from": "camera_icon:right@0.50", "to": "fragment_display:left@0.50", "route": "horizontal",
            "lane_axis": "horizontal",
            "style": {"line": red, "line_weight_pt": 1.25, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
        {
            "id": "fragment_to_ocr", "type": "lane_arrow", "arrow_plan_id": "A011",
            "from": "fragment_display:right@0.50", "to": "ocr_failure:left@0.50", "route": "horizontal",
            "lane_axis": "horizontal",
            "style": {"line": red, "line_weight_pt": 1.25, "end_arrow": "triangle", "arrow_size": "small"},
            "z": 25,
        },
    ]

    scene = {
        "version": "0.1",
        "metadata": metadata,
        "page": {
            "width": 1536,
            "height": 1024,
            "units": "px",
            "origin": "top-left",
            "target_width_in": 3.5,
            "background": "#FFFFFF",
        },
        "nodes": nodes,
        "edges": edges,
        "assets": [],
    }
    OUTPUT.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
