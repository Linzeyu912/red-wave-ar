"""Ground-centering and stair-contact contracts for the nine AR models.

The ground is an unlit image plane, so it cannot be used to fake vertical
steps.  All visible risers and treads remain physical GLB geometry.  These
contracts reserve a material-consistent approach area in front of that
geometry while keeping the transformed model footprint centred on the ground
plane.
"""

from __future__ import annotations


MODEL_CENTER_POLICY = "ground_plane_center_equals_transformed_model_footprint_center"


GROUND_CONTACTS = {
    "S1A": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.18,
        "has_front_landing": True,
        "landing_width_ratio": 0.62,
        "stair_geometry_zh": "GLB 内保留正面 6–7 级灰石直跑台阶；外侧最低，向门洞逐级升高。",
        "ground_approach_zh": "台阶外侧以居中的低对比灰石铺装承接，不在平面贴图中伪造立体踏步。",
    },
    "S1B": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.12,
        "has_front_landing": False,
        "landing_width_ratio": 0.0,
        "stair_geometry_zh": "人物、桌台和设备为完整 GLB 组合，无外部台阶。",
        "ground_approach_zh": "深棕木质地面仅作居中展陈组合的接触面，不添加虚构台阶或展台。",
    },
    "S2A": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.14,
        "has_front_landing": True,
        "landing_width_ratio": 0.28,
        "stair_geometry_zh": "GLB 内保留中央入口的极短台阶/基座；不扩展为街道设施。",
        "ground_approach_zh": "入口前留出居中的浅灰石质承接区，保持模型位于地面中心。",
    },
    "S3A": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.16,
        "has_front_landing": True,
        "landing_width_ratio": 0.56,
        "stair_geometry_zh": "GLB 内保留低层翼楼前的宽台阶，正面朝 -Z。",
        "ground_approach_zh": "宽台阶外侧以低对比旧混凝土/浅石材过渡，不加入水池、车辆或道路。",
    },
    "S3B": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.12,
        "has_front_landing": False,
        "landing_width_ratio": 0.0,
        "stair_geometry_zh": "GLB 仅保留可读机械地脚，无建筑入口台阶。",
        "ground_approach_zh": "压实中性土/草色从地脚外侧连续铺开，不添加台阶或黑色底座。",
    },
    "S4A": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.12,
        "has_front_landing": False,
        "landing_width_ratio": 0.0,
        "stair_geometry_zh": "城台、券门和城楼基座为 GLB 几何；无资料支持时不伪造入口台阶。",
        "ground_approach_zh": "中灰旧石接触面包围居中的城台，避免用平面贴图绘制假台阶。",
    },
    "S5A": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.14,
        "has_front_landing": False,
        "landing_width_ratio": 0.0,
        "stair_geometry_zh": "人物石质支撑、斜置铜牌石座和层级关系均由 GLB 几何表达。",
        "ground_approach_zh": "浅暖灰石材只承接局部石座，不把平面图做成大面积广场或假台阶。",
    },
    "S6A": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.16,
        "has_front_landing": True,
        "landing_width_ratio": 0.34,
        "stair_geometry_zh": "GLB 内保留中央直跑中深灰石阶，正面朝 -Z 并向门廊逐级升高。",
        "ground_approach_zh": "台阶前以居中的中性灰石/混凝土接触区收口，不扩展到园林。",
    },
    "S7A": {
        "front_axis": "-Z",
        "perimeter_clearance_target_units": 0.15,
        "has_front_landing": True,
        "landing_width_ratio": 0.36,
        "stair_geometry_zh": "GLB 内保留入口前的极短浅米灰石台阶/平台，正面朝 -Z。",
        "ground_approach_zh": "入口前留出居中的提亮中性灰石承接区，不把道路或围栏绘入地面。",
    },
}
