from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INVENTORY_SCENE = ROOT / "figure2_method_pipeline.round2.scene.json"
OUTPUT_SCENE = ROOT / "figure2_method_pipeline.round3.scene.json"


def style(**kwargs):
    return kwargs


def node(node_id, node_type, x, y, w, h, *, text="", container_id=None, z=10, **kwargs):
    item = {
        "id": node_id,
        "type": node_type,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "text": text,
        "z": z,
    }
    if container_id:
        item["container_id"] = container_id
    item.update(kwargs)
    return item


def label(node_id, x, y, w, h, text, container_id, *, size=7.5, color="#17365D",
          weight=None, role="small_label", font="Arial", z=12):
    text_style = style(
        source_font_family=font,
        font_family=font,
        font_role="math" if font == "Cambria Math" else "sans",
        font_size_pt=size,
        min_font_size_pt=max(6.5, size - 0.6),
        text_fit="single_line",
        constrain_text_box=True,
        text_margin_in=0.0,
        text_color=color,
    )
    if weight:
        text_style["font_weight"] = weight
    return node(
        node_id,
        "math_text" if font == "Cambria Math" else "text_block",
        x, y, w, h,
        text=text,
        container_id=container_id,
        z=z,
        text_role=role,
        style=text_style,
    )


def grid(node_id, x, y, w, h, rows, cols, cells, container_id, *, line="#D8E0EA", z=12):
    return node(
        node_id, "grid_matrix", x, y, w, h,
        container_id=container_id,
        z=z,
        rows=rows,
        cols=cols,
        colored_cells=[[r, c, "#17365D"] for r, c in cells],
        style=style(cell_fill="#FFFFFF", grid_line=line, grid_line_weight_pt=0.25),
    )


def main():
    inventory = json.loads(INVENTORY_SCENE.read_text(encoding="utf-8"))
    metadata = copy.deepcopy(inventory["metadata"])
    metadata.update({
        "created_by": "codex.visiomaster.fresh_round3",
        "replica_stage": "detail_polish",
        "prior_scene_policy": "reuse_source_inventory_and_arrow_plan_only; reauthor_all_visible_nodes",
        "notes": [
            "Fresh full-scene node reauthoring after round-two rendered-text review.",
            "Every multiword label now uses a dedicated fixed single-line text zone.",
            "Camera is a vector camera motif instead of text inside a narrow box.",
            "Color is redundant with solid/dashed routes, explicit labels, and panel geometry.",
        ],
    })
    # Review bboxes use [left, top, right, bottom], not [x, y, width, height].
    metadata["region_plan"] = [
        {"id": "global_layout", "crop_type": "global", "source_bbox_px": [0, 0, 1983, 793],
         "target_bbox": [0, 0, 1983, 793], "review_focus": "page aspect and hierarchy"},
        {"id": "stage_1_input", "crop_type": "input", "source_bbox_px": [0, 80, 705, 700],
         "target_bbox": [20, 20, 540, 773], "container_id": "stage_1", "review_focus": "input security masks"},
        {"id": "central_core", "crop_type": "core", "source_bbox_px": [680, 60, 1350, 735],
         "target_bbox": [550, 20, 1240, 773], "container_id": "stage_2", "review_focus": "GPU noise subframes"},
        {"id": "human_output", "crop_type": "output", "source_bbox_px": [1320, 60, 1983, 330],
         "target_bbox": [1350, 90, 1940, 350], "container_id": "stage_3_human", "review_focus": "right output human"},
        {"id": "camera_output", "crop_type": "output", "source_bbox_px": [1320, 380, 1983, 760],
         "target_bbox": [1350, 390, 1940, 720], "container_id": "stage_3_camera", "review_focus": "right output camera"},
        {"id": "arrow_dense", "crop_type": "arrow_dense", "source_bbox_px": [930, 170, 1760, 620],
         "target_bbox": [900, 150, 1780, 620], "review_focus": "arrow dense topology junction"},
        {"id": "small_text", "crop_type": "small_text", "source_bbox_px": [350, 80, 1900, 720],
         "target_bbox": [300, 90, 1900, 720], "review_focus": "small text formula ports boundary"},
    ]

    navy = "#17365D"
    cyan = "#159FCF"
    cyan_dark = "#087EA8"
    green = "#177A36"
    red = "#D94722"
    magenta = "#A50064"

    nodes = [
        node("page_background", "page_background", 0, 0, 1983, 793, z=-100),
        node("stage_1", "group_container", 20, 20, 520, 753, z=0,
             source_bbox_px=[0, 80, 705, 700], source_aspect_ratio=0.871,
             style=style(fill="#FBFDFF", line="#B7C5D8", line_weight_pt=0.9,
                         line_dash="solid", rounding_in=0.04)),
        node("stage_2", "group_container", 550, 20, 690, 753, z=0,
             source_bbox_px=[680, 60, 1350, 735], source_aspect_ratio=0.993,
             style=style(fill="#FBFDFF", line="#B7C5D8", line_weight_pt=0.9,
                         line_dash="solid", rounding_in=0.04)),
        node("stage_3", "group_container", 1250, 20, 713, 753, z=0,
             source_bbox_px=[1320, 50, 1983, 760], source_aspect_ratio=0.934,
             style=style(fill="#FBFDFF", line="#B7C5D8", line_weight_pt=0.9,
                         line_dash="solid", rounding_in=0.04)),
        label("stage_1_title", 38, 34, 485, 48, "1  Secure mask generation", "stage_1",
              size=8.2, weight="bold", role="panel_title"),
        label("stage_2_title", 568, 34, 655, 48, "2  GPU synthesis and temporal sequence", "stage_2",
              size=8.2, weight="bold", role="panel_title"),
        label("stage_3_title", 1268, 34, 675, 48, "3  Observer asymmetry", "stage_3",
              size=8.2, weight="bold", role="panel_title"),

        node("input_frame", "process_box", 38, 280, 160, 120, container_id="stage_1",
             style=style(fill="#FFFFFF", line=navy, line_weight_pt=1.35, shadow=None), z=10),
        label("input_private", 46, 300, 144, 36, "PRIVATE", "stage_1", size=8.1, weight="bold", role="node_text"),
        label("input_data", 46, 345, 144, 36, "DATA", "stage_1", size=8.1, weight="bold", role="node_text"),
        label("input_label", 38, 414, 160, 34, "Input frame I", "stage_1", size=7.2),
        node("security_module", "rounded_process", 220, 245, 170, 190, container_id="stage_1",
             style=style(fill="#FFFFFF", line=navy, line_weight_pt=1.25,
                         rounding_in=0.035, shadow=None), z=10),
        label("security_chacha", 228, 267, 154, 34, "ChaCha20", "stage_1", size=7.4, role="node_text"),
        label("security_csprng", 228, 304, 154, 34, "CSPRNG", "stage_1", size=7.4, role="node_text"),
        label("security_shuffle", 225, 363, 160, 34, "Fisher-Yates", "stage_1", size=7.0, role="node_text"),
        node("mask_entry", "junction_point", 401, 337, 6, 6, container_id="stage_1", z=8,
             role="boundary_anchor", style=style(fill="none", line="none")),
        grid("mask_1", 414, 265, 48, 48, 6, 6,
             [(0,1),(0,4),(1,0),(1,3),(2,2),(3,5),(4,1),(5,3)], "stage_1", line="#9BCFE2"),
        grid("mask_2", 475, 265, 48, 48, 6, 6,
             [(0,0),(0,3),(1,2),(1,5),(2,1),(3,4),(4,2),(5,5)], "stage_1", line="#9BCFE2"),
        grid("mask_3", 414, 326, 48, 48, 6, 6,
             [(0,2),(0,5),(1,1),(1,4),(2,0),(2,3),(3,2),(5,4)], "stage_1", line="#9BCFE2"),
        grid("mask_4", 475, 326, 48, 48, 6, 6,
             [(0,5),(1,1),(2,4),(3,1),(3,3),(4,5),(5,0),(5,4)], "stage_1", line="#9BCFE2"),
        node("mask_exit", "junction_point", 529, 337, 6, 6, container_id="stage_1", z=8,
             role="boundary_anchor", style=style(fill="none", line="none")),
        label("mask_label", 396, 397, 134, 42, "Masks M_k", "stage_1", size=7.2,
              color=cyan_dark, font="Cambria Math"),
        label("mask_formula", 390, 445, 145, 40, "Σ M_k = 1", "stage_1", size=7.7,
              color=cyan_dark, role="formula", font="Cambria Math"),

        node("optional_enhancement", "dashed_region", 585, 105, 270, 100,
             container_id="stage_2", z=8, source_bbox_px=[690,70,935,155], source_aspect_ratio=2.882,
             style=style(fill="#FFFFFF", line=navy, line_weight_pt=0.9,
                         line_dash="dash", rounding_in=0.03)),
        label("optional_label", 597, 122, 246, 32, "Optional anti-OCR", "optional_enhancement",
              size=7.0, role="annotation"),
        label("optional_label_2", 597, 158, 246, 32, "/ inversion", "optional_enhancement",
              size=7.0, role="annotation"),
        node("optional_out", "boundary_port", 717, 202, 6, 6, container_id="optional_enhancement", z=12,
             side="bottom", shape="none", style=style(fill="none", line="none")),
        node("gpu_synthesis", "group_container", 575, 250, 300, 200, container_id="stage_2", z=8,
             source_bbox_px=[700,225,1000,425], source_aspect_ratio=1.5,
             style=style(fill="#FFFFFF", line=navy, line_weight_pt=1.5,
                         line_dash="solid", rounding_in=0.04)),
        label("gpu_title", 590, 268, 270, 42, "GPU subframe", "gpu_synthesis",
              size=7.7, weight="bold", role="module_title"),
        label("gpu_title_2", 590, 305, 270, 42, "synthesis", "gpu_synthesis",
              size=7.7, weight="bold", role="module_title"),
        label("gpu_formula", 588, 350, 274, 44, "I_k = I ⊙ M_k + N_k", "gpu_synthesis",
              size=8.1, role="formula", font="Cambria Math"),
        node("gpu_in", "boundary_port", 572, 347, 6, 6, container_id="gpu_synthesis", z=12,
             side="left", shape="none", style=style(fill="none", line="none")),
        node("gpu_out", "boundary_port", 872, 347, 6, 6, container_id="gpu_synthesis", z=12,
             side="right", shape="none", style=style(fill="none", line="none")),
        node("gpu_top", "boundary_port", 722, 247, 6, 6, container_id="gpu_synthesis", z=12,
             side="top", shape="none", style=style(fill="none", line="none")),
        node("gpu_bottom", "boundary_port", 722, 447, 6, 6, container_id="gpu_synthesis", z=12,
             side="bottom", shape="none", style=style(fill="none", line="none")),
        node("adversarial_noise", "group_container", 615, 525, 220, 150, container_id="stage_2", z=8,
             source_bbox_px=[720,470,930,615], source_aspect_ratio=1.448,
             style=style(fill="#FFFFFF", line=magenta, line_weight_pt=1.15,
                         line_dash="solid", rounding_in=0.035)),
        label("noise_title", 625, 545, 200, 42, "Adversarial noise", "adversarial_noise",
              size=7.3, color=magenta, role="module_title"),
        label("noise_formula", 625, 615, 200, 42, "Σ N_k = 0", "adversarial_noise",
              size=7.7, color=magenta, role="formula", font="Cambria Math"),
        node("noise_out", "boundary_port", 722, 522, 6, 6, container_id="adversarial_noise", z=12,
             side="top", shape="none", style=style(fill="none", line="none")),
        grid("subframe_1", 915, 295, 55, 115, 9, 5,
             [(0,4),(1,1),(2,0),(2,3),(4,2),(6,4),(7,0),(8,2)], "stage_2"),
        grid("subframe_2", 990, 295, 55, 115, 9, 5,
             [(0,0),(1,3),(3,1),(4,4),(5,2),(7,3),(8,0)], "stage_2"),
        grid("subframe_3", 1065, 295, 55, 115, 9, 5,
             [(0,2),(2,4),(3,0),(5,1),(6,3),(8,4)], "stage_2"),
        grid("subframe_4", 1140, 295, 55, 115, 9, 5,
             [(1,0),(2,2),(3,4),(5,0),(6,2),(7,4),(8,1)], "stage_2"),
        label("high_refresh_label", 895, 420, 320, 34, "High-refresh display", "stage_2",
              size=7.5, weight="bold"),
        label("refresh_rate_label", 895, 457, 320, 34, "240-360 Hz", "stage_2",
              size=7.5, weight="bold"),
        label("time_label", 1000, 526, 110, 34, "time t", "stage_2", size=7.2),

        node("observer_fork", "junction_point", 1260, 347, 8, 8, container_id="stage_3", z=15,
             role="fan_out", style=style(fill=navy, line=navy, line_weight_pt=0.6)),
        node("stage_3_human", "group_container", 1350, 90, 590, 260, container_id="stage_3", z=2,
             source_bbox_px=[1320,60,1983,330], source_aspect_ratio=2.269,
             style=style(fill="#F2FBF5", line=green, line_weight_pt=1.0,
                         line_dash="solid", rounding_in=0.035)),
        label("human_title", 1370, 105, 550, 40, "HUMAN VISUAL SYSTEM", "stage_3_human",
              size=8.2, color=green, weight="bold", role="module_title"),
        node("human_eye", "ellipse_node", 1390, 180, 75, 60, text="o", container_id="stage_3_human", z=12,
             style=style(fill="#FFFFFF", line=green, line_weight_pt=1.3, text_color=green,
                         source_font_family="Cambria Math", font_family="Cambria Math", font_role="math",
                         font_size_pt=12, min_font_size_pt=11, text_fit="single_line",
                         constrain_text_box=True, text_margin_in=0.0)),
        node("temporal_integration", "stacked_process", 1535, 170, 95, 80, text="Σ", layers=4,
             stack_dx_in=-0.018, stack_dy_in=0.018, container_id="stage_3_human", z=12,
             style=style(fill="#FFFFFF", line=green, line_weight_pt=0.9, rounding_in=0.01,
                         text_color=green, source_font_family="Cambria Math", font_family="Cambria Math",
                         font_role="math", font_size_pt=10, min_font_size_pt=9, text_fit="single_line",
                         constrain_text_box=True, text_margin_in=0.0)),
        node("readable_output", "process_box", 1745, 165, 155, 95, container_id="stage_3_human", z=12,
             style=style(fill="#FFFFFF", line=green, line_weight_pt=1.3, shadow=None)),
        label("readable_private", 1753, 178, 139, 32, "PRIVATE", "stage_3_human",
              size=7.7, weight="bold", role="node_text"),
        label("readable_data", 1753, 216, 139, 32, "DATA", "stage_3_human",
              size=7.7, weight="bold", role="node_text"),
        label("integration_label", 1495, 270, 175, 32, "Integration", "stage_3_human",
              size=7.2, color=green),
        label("integration_time", 1495, 305, 175, 30, "≈ 50 ms", "stage_3_human",
              size=7.0, color=green),
        label("readable_label", 1700, 285, 230, 34, "Readable output", "stage_3_human",
              size=7.2, color=green, weight="bold", role="output_label"),

        node("stage_3_camera", "group_container", 1350, 390, 590, 330, container_id="stage_3", z=2,
             source_bbox_px=[1320,380,1983,760], source_aspect_ratio=1.788,
             style=style(fill="#FFF6F2", line=red, line_weight_pt=1.0,
                         line_dash="solid", rounding_in=0.035)),
        label("camera_title", 1370, 405, 550, 40, "CAMERA / MACHINE VISION", "stage_3_camera",
              size=8.2, color=red, weight="bold", role="module_title"),
        label("camera_subtitle", 1370, 450, 550, 34, "Samples one short exposure", "stage_3_camera",
              size=7.2, color=red),
        node("camera_icon", "rounded_process", 1378, 515, 82, 60, container_id="stage_3_camera", z=12,
             style=style(fill="#FFFFFF", line=red, line_weight_pt=1.3,
                         rounding_in=0.025, shadow=None)),
        node("camera_lens", "ellipse_node", 1403, 529, 30, 30, container_id="stage_3_camera", z=14,
             allow_overlap=True, style=style(fill="#FFFFFF", line=red, line_weight_pt=1.1)),
        node("camera_top", "process_box", 1390, 503, 30, 14, container_id="stage_3_camera", z=13,
             allow_overlap=True, style=style(fill="#FFFFFF", line=red, line_weight_pt=1.0)),
        grid("camera_frame_1", 1490, 510, 35, 82, 8, 4,
             [(0,3),(2,0),(3,2),(6,1),(7,3)], "stage_3_camera", line="#E1D4CF"),
        grid("camera_frame_2", 1540, 510, 35, 82, 8, 4,
             [(0,0),(1,2),(3,1),(5,3),(7,0)], "stage_3_camera", line="#E1D4CF"),
        grid("camera_frame_3", 1590, 510, 35, 82, 8, 4,
             [(1,1),(2,3),(4,0),(6,2)], "stage_3_camera", line="#E1D4CF"),
        grid("camera_frame_4", 1640, 510, 35, 82, 8, 4,
             [(0,2),(2,1),(4,3),(5,0),(7,2)], "stage_3_camera", line="#E1D4CF"),
        node("sampling_window", "dashed_region", 1533, 500, 49, 102, container_id="stage_3_camera", z=14,
             source_bbox_px=[1550,450,1610,575], source_aspect_ratio=0.48,
             style=style(fill="none", line=red, line_weight_pt=1.1,
                         line_dash="dash", rounding_in=0.01)),
        grid("sampled_fragment", 1715, 508, 55, 86, 9, 5,
             [(0,4),(2,1),(3,3),(5,0),(6,2),(8,4)], "stage_3_camera", line="#E1D4CF"),
        node("ocr_failure", "ellipse_node", 1810, 520, 105, 62, text="OCR ×", container_id="stage_3_camera", z=12,
             style=style(fill="#FFFFFF", line=red, line_weight_pt=1.2, text_color=red,
                         source_font_family="Arial", font_family="Arial", font_role="sans",
                         font_size_pt=7.5, min_font_size_pt=7.0, font_weight="bold",
                         text_fit="single_line", constrain_text_box=True, text_margin_in=0.0)),
        label("camera_label", 1365, 605, 110, 32, "Camera", "stage_3_camera",
              size=7.0, color=red, weight="bold"),
        label("camera_sampling_label", 1470, 610, 215, 32, "Short-exposure", "stage_3_camera",
              size=7.0, color=red, weight="bold"),
        label("camera_sampling_label_2", 1470, 645, 215, 30, "sampling", "stage_3_camera",
              size=7.0, color=red, weight="bold"),
        label("unreadable_label", 1660, 610, 170, 32, "Unreadable", "stage_3_camera",
              size=6.8, color=red, weight="bold", role="output_label"),
        label("unreadable_label_2", 1660, 645, 170, 30, "fragment", "stage_3_camera",
              size=6.8, color=red, weight="bold", role="output_label"),
    ]

    edges = [
        {"id":"input_to_security","type":"lane_arrow","arrow_plan_id":"A001",
         "from":"input_frame:right@0.50","to":"security_module:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":navy,"line_weight_pt":1.35,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"security_to_masks","type":"lane_arrow","arrow_plan_id":"A002",
         "from":"security_module:right@0.50","to":"mask_entry:center","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":navy,"line_weight_pt":1.35,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"masks_to_gpu","type":"boundary_arrow","arrow_plan_id":"A003",
         "from":"mask_exit:center","to":"gpu_in:center","route":"horizontal","allow_cross_container":True,
         "style":{"line":navy,"line_weight_pt":1.35,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"optional_to_gpu","type":"dashed_feedback_path","arrow_plan_id":"A004",
         "from":"optional_out:center","to":"gpu_top:center","route":"vertical","allow_cross_container":True,
         "style":{"line":navy,"line_weight_pt":0.95,"line_dash":"dash","end_arrow":"none","arrow_size":"tiny"},"z":18},
        {"id":"noise_to_gpu","type":"lane_arrow","arrow_plan_id":"A005",
         "from":"noise_out:center","to":"gpu_bottom:center","route":"vertical","lane_axis":"vertical","allow_cross_container":True,
         "style":{"line":magenta,"line_weight_pt":1.2,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"gpu_to_subframes","type":"lane_arrow","arrow_plan_id":"A006",
         "from":"gpu_out:center","to":"subframe_1:left@0.50","route":"horizontal","lane_axis":"horizontal","allow_cross_container":True,
         "style":{"line":navy,"line_weight_pt":1.35,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"time_axis","type":"lane_arrow","arrow_plan_id":"A007","from_point":[915,510],"to_point":[1195,510],
         "route":"horizontal","lane_axis":"horizontal","style":{"line":navy,"line_weight_pt":1.15,"end_arrow":"triangle","arrow_size":"small"},"z":18},
        {"id":"subframes_to_fork","type":"boundary_arrow","arrow_plan_id":"A008",
         "from":"subframe_4:right@0.50","to":"observer_fork:center","route":"horizontal","allow_cross_container":True,
         "style":{"line":navy,"line_weight_pt":1.35,"end_arrow":"none","arrow_size":"small"},"z":20},
        {"id":"fork_to_human","type":"rounded_orthogonal_connector","arrow_plan_id":"A009",
         "from":"observer_fork:center","points":[[1300,351],[1300,210]],"to":"human_eye:left@0.50",
         "route":"rounded_orthogonal","orthogonalize_points":True,"corner_radius_px":16,"allow_cross_container":True,
         "style":{"line":green,"line_weight_pt":1.5,"line_dash":"solid","end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"human_to_integration","type":"lane_arrow","arrow_plan_id":"A010",
         "from":"human_eye:right@0.50","to":"temporal_integration:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":green,"line_weight_pt":1.35,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"integration_to_output","type":"lane_arrow","arrow_plan_id":"A011",
         "from":"temporal_integration:right@0.50","to":"readable_output:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":green,"line_weight_pt":1.35,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"fork_to_camera","type":"dashed_feedback_path","arrow_plan_id":"A012",
         "from":"observer_fork:center","points":[[1300,351],[1300,545]],"to":"camera_icon:left@0.50",
         "route":"orthogonal","orthogonalize_points":True,"allow_cross_container":True,
         "style":{"line":red,"line_weight_pt":1.5,"line_dash":"dash","end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"camera_to_sequence","type":"lane_arrow","arrow_plan_id":"A013",
         "from":"camera_icon:right@0.50","to":"camera_frame_1:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":red,"line_weight_pt":1.25,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"sequence_to_fragment","type":"lane_arrow","arrow_plan_id":"A014",
         "from":"camera_frame_4:right@0.50","to":"sampled_fragment:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":red,"line_weight_pt":1.25,"end_arrow":"triangle","arrow_size":"small"},"z":20},
        {"id":"fragment_to_ocr","type":"lane_arrow","arrow_plan_id":"A015",
         "from":"sampled_fragment:right@0.50","to":"ocr_failure:left@0.50","route":"horizontal","lane_axis":"horizontal",
         "style":{"line":red,"line_weight_pt":1.25,"end_arrow":"triangle","arrow_size":"small"},"z":20},
    ]

    scene = {
        "version": "0.1",
        "metadata": metadata,
        "page": {"width": 1983, "height": 793, "units": "px", "origin": "top-left",
                 "target_width_in": 7.16, "background": "#FFFFFF"},
        "nodes": nodes,
        "edges": edges,
        "assets": [],
    }
    OUTPUT_SCENE.write_text(json.dumps(scene, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_SCENE}")


if __name__ == "__main__":
    main()
