"""S1 whitebox layout — single source of truth (compact cellar revision).

依据 modeling_input/S1/04_COMPACT_CELLAR_REVISION.md（M3D-01R，2026-07-20）。
旧 8.0 x 8.0 m 白盒口径作废（用户已否决）；唯一基准为原创"地下储洞门内侧
小工作室"：内净 5.3 m(X) x 4.7 m(Z) x 2.25 m(净高)。

Hard rules (unchanged contract):
- Y-up, right-handed, -Z forward, meters. Prop origin = bottom center,
  front faces -Z. Runtime delivery = GLB (textureless, pbrMetallicRoughness
  baseColor); colliders live ONLY in scene.json, never in GLBs.
- No inscriptions / brands / serial numbers / gauge readings / map text /
  people. Do not copy device silhouettes or display layouts from any
  reference image.
- scene_id="S1"; asset IDs env_s1_room / p_s1_radio / p_s1_key /
  p_s1_codebook; scene.json JSON schema (keys & types) and file paths are
  frozen — only numeric values change.

All values are PROVISIONAL whitebox values, not historical dimensions.

shape tuples understood by build_whitebox.shapes() and the renderers:
  ("box",  (lo, hi))                    axis-aligned box
  ("cyl",  (center, r, h))              Y-axis cylinder
  ("tube", (p0, p1, r, seg[, cap]))     arbitrary-axis round tube
  ("rbox", (center, size, rot_x_deg))   box rotated about X through center
build_env_parts may return a single shape or a list of shapes per part.
"""

import math

# ---------------------------------------------------------------- materials
ENV_GRAY = "env_gray"        # environment: shell + furniture (plan-brief gray)
PROP_BROWN = "prop_brown"    # interactive props (key / codebook placeholders)
GUIDE_BLUE = "guide_blue"    # guide objects (small guide plate, wayfinding)

MATERIALS = {
    ENV_GRAY: (0.58, 0.58, 0.60),
    PROP_BROWN: (0.48, 0.34, 0.22),
    GUIDE_BLUE: (0.24, 0.42, 0.72),
}

# p_s1_radio review-grade multi-material set (textureless neutral darks,
# original design; no brand, no text, no serials, no readable gauge).
RADIO_MATERIALS = {
    "mat_radio_body":  {"base_color": (0.263, 0.278, 0.239), "metallic": 0.15, "roughness": 0.75},  # 暗军绿灰
    "mat_radio_panel": {"base_color": (0.149, 0.153, 0.157), "metallic": 0.30, "roughness": 0.60},  # 深灰黑
    "mat_radio_meter": {"base_color": (0.063, 0.086, 0.102), "metallic": 0.50, "roughness": 0.25},  # 近黑玻璃
    "mat_radio_metal": {"base_color": (0.227, 0.239, 0.227), "metallic": 0.75, "roughness": 0.45},  # 暗金属
    "mat_cable":       {"base_color": (0.078, 0.075, 0.071), "metallic": 0.00, "roughness": 0.95},  # 近黑橡胶
}

# ---------------------------------------------------------------- room shell
# Interior clear 5.3 m (X) x 4.7 m (Z) x 2.25 m (H): inner walls x=+-2.65,
# z=+-2.35, ceiling 2.25. Wall thickness 0.25 (outer x=+-2.90, z=+-2.60).
# Floor slab y[-0.10, 0.0], ceiling slab y[2.25, 2.35].
ROOM = {"x": 5.3, "z": 4.7, "h": 2.25, "wall_t": 0.25}

# Low storage-cellar door on the south wall, offset west: opening
# x[-1.9, -1.1] (0.8 m wide), height 1.85 m.
DOOR = {"x0": -1.9, "x1": -1.1, "h": 1.85}

# Small guide plate (modern info layer -> guide blue) on the west wall by the
# door; replaces the old full-wall INFO_PANEL.
GUIDE_PLATE = {"x0": -2.65, "x1": -2.61, "y0": 1.15, "y1": 1.70, "z0": 1.55, "z1": 2.15}

# ---------------------------------------------------------------- furniture
# Operation desk: center [0, 0, 0.10], 1.80 x 0.75 x 0.78 m (frozen baseline).
DESK = {"x0": -0.9, "x1": 0.9, "z0": -0.275, "z1": 0.475, "top_y0": 0.74, "top_y1": 0.78}
DESK_SURFACE_Y = 0.78

# Stool behind the desk at [0.30, 0, -0.70]; seat 0.42 x 0.42, height 0.45.
STOOL = {"cx": 0.30, "cz": -0.70, "w": 0.42, "seat_y0": 0.40, "seat_y1": 0.45}

# Single supply crate, north-east corner.
CRATES = [
    (1.65, 0.00, -2.10, 2.25, 0.42, -1.60),
]

# Original kerosene lamp on the desk at [0.72, 0.32] (no brand, env_gray).
# Stacked cylinders: base r0.055 h0.02 (bottom on desk y=0.78), stem r0.012
# h0.10, glass r0.045 h0.09, cap r0.05 h0.015.
LAMP = {"x": 0.72, "z": 0.32}

# ---------------------------------------------------------------- props
# Local-space definitions; origin at bottom center of footprint, front -Z.
# World placement goes to scene.json (never baked into prop GLBs).

PROPS = {
    "p_s1_radio": {
        "file": "props/radio_station_whitebox.glb",
        # review-grade generic box radio (M3D-01R section 4), no inscriptions
        "position_m": [0.32, DESK_SURFACE_Y, 0.04],
        # yaw 180：倾斜控制面朝 +Z（朝游客/发报键一侧），第一眼即可读出
        # “正在工作的无线电设备”；线缆随之甩向桌后侧（仍在桌面上）。
        "rotation_deg": [0.0, 180.0, 0.0],
        "scale": 1.0,
        "interaction_radius_m": 1.8,
        "highlight_anchor_m": [0.0, 0.15, -0.10],
        "dims_m": [0.42, 0.28, 0.32],
    },
    "p_s1_key": {
        "file": "props/telegraph_key_whitebox.glb",
        # generic straight key placeholder; key_lever separate node at pivot
        "position_m": [-0.34, DESK_SURFACE_Y, 0.34],
        "rotation_deg": [0.0, 0.0, 0.0],
        "scale": 1.0,
        "interaction_radius_m": 1.6,
        "highlight_anchor_m": [0.0, 0.12, 0.0],
        "dims_m": [0.15, 0.072, 0.10],
    },
    "p_s1_codebook": {
        "file": "props/code_book_whitebox.glb",
        # untextured closed booklet placeholder ONLY (FINAL_MODEL_BLOCKED)
        "position_m": [-0.58, DESK_SURFACE_Y, -0.10],
        "rotation_deg": [0.0, 0.0, 0.0],
        "scale": 1.0,
        "interaction_radius_m": 1.9,
        "highlight_anchor_m": [0.0, 0.10, 0.0],
        "dims_m": [0.15, 0.035, 0.21],
    },
}

# ---------------------------------------------------------------- visitor
VISITOR_START = {
    "position_m": [0.0, 1.55, 1.65],
    # 口径：零旋转 = 朝 -Z（项目约定 plan v1.2 §5.2），即面向木桌。
    # 注意：plan §5.4 示例与同朝向写作 [0,180,0]，轴向约定存在出入，
    # 记为 OQ-I-04，待真机联调确认后再定；本值保持 [0,0,0]。
    "rotation_deg": [0.0, 0.0, 0.0],
}

MOVEMENT = {
    "type": "bounds",
    "speed_mps": 1.2,
    "x_min_m": -2.25,
    "x_max_m": 2.25,
    "z_min_m": -1.95,
    "z_max_m": 1.95,
}

# Simplified AABBs only; never exported into render GLBs.
COLLIDERS = [
    {"id": "wall_north", "min_m": [-2.9, 0.0, -2.6], "max_m": [2.9, 2.25, -2.35]},
    {"id": "wall_south", "min_m": [-2.9, 0.0, 2.35], "max_m": [2.9, 2.25, 2.6]},  # door leaf is closed geometry; exit is handled by UI
    {"id": "wall_east", "min_m": [2.65, 0.0, -2.35], "max_m": [2.9, 2.25, 2.35]},
    {"id": "wall_west", "min_m": [-2.9, 0.0, -2.35], "max_m": [-2.65, 2.25, 2.35]},
    {"id": "desk_radio", "min_m": [-0.9, 0.0, -0.275], "max_m": [0.9, 0.78, 0.475]},
    {"id": "stool", "min_m": [0.09, 0.0, -0.91], "max_m": [0.51, 0.45, -0.49]},
    {"id": "crate", "min_m": [1.65, 0.0, -2.10], "max_m": [2.25, 0.42, -1.60]},
    {"id": "guide_plate", "min_m": [-2.66, 1.10, 1.50], "max_m": [-2.60, 1.75, 2.20]},
]

MOVE_POINTS = [
    {"id": "mp_radio", "position_m": [0.75, 1.55, 0.95], "look_at_m": [0.32, 1.0, 0.04]},
    {"id": "mp_guide", "position_m": [-1.5, 1.55, 1.15], "look_at_m": [-2.63, 1.42, 1.85]},
]


# ---------------------------------------------------------------- builders
def build_env_parts(make_box, make_cyl):
    """Return env parts: list of (node_name, material, shape) built in WORLD
    space. `shape` may be a single shape tuple or a list of shape tuples."""
    parts = []
    B, C = make_box, make_cyl
    g, bl = ENV_GRAY, GUIDE_BLUE

    parts += [
        ("floor", g, B((-2.90, -0.10, -2.60), (2.90, 0.0, 2.60))),
        ("ceiling", g, B((-2.90, 2.25, -2.60), (2.90, 2.35, 2.60))),
        ("wall_north", g, B((-2.90, 0.0, -2.60), (2.90, 2.25, -2.35))),
        ("wall_east", g, B((2.65, 0.0, -2.35), (2.90, 2.25, 2.35))),
        ("wall_west", g, B((-2.90, 0.0, -2.35), (-2.65, 2.25, 2.35))),
        ("wall_south_a", g, B((-2.90, 0.0, 2.35), (DOOR["x0"], 2.25, 2.60))),
        ("wall_south_b", g, B((DOOR["x1"], 0.0, 2.35), (2.90, 2.25, 2.60))),
        ("wall_south_lintel", g, B((DOOR["x0"], DOOR["h"], 2.35), (DOOR["x1"], 2.25, 2.60))),
        # old wooden entry frame at the inner wall face (z 2.30..2.35)
        ("entry_frame_left", g, B((DOOR["x0"] - 0.05, 0.0, 2.30), (DOOR["x0"], 1.90, 2.35))),
        ("entry_frame_right", g, B((DOOR["x1"], 0.0, 2.30), (DOOR["x1"] + 0.05, 1.90, 2.35))),
        ("entry_frame_top", g, B((DOOR["x0"] - 0.05, DOOR["h"], 2.30), (DOOR["x1"] + 0.05, 1.90, 2.35))),
        # closed door leaf (exit is handled by UI, not by walking)
        ("door_leaf", g, B((-1.88, 0.02, 2.37), (-1.12, 1.83, 2.45))),
        # rough-stone skirting along the four inner wall bases, h 0.25,
        # protruding 0.02; south run flanks the doorway and the brick patch
        ("skirt_north", g, B((-2.65, 0.0, -2.35), (2.65, 0.25, -2.33))),
        ("skirt_east", g, B((2.63, 0.0, -2.35), (2.65, 0.25, 2.35))),
        ("skirt_west", g, B((-2.65, 0.0, -2.35), (-2.63, 0.25, 2.35))),
        ("skirt_south", g, [
            B((-2.65, 0.0, 2.33), (-2.45, 0.25, 2.35)),   # west of brick patch
            B((-1.05, 0.0, 2.33), (2.65, 0.25, 2.35)),    # east of door frame
        ]),
        # gray-brick repair patch on the inner south wall face
        ("brick_patch_a", g, B((-2.45, 0.0, 2.33), (-1.95, 1.30, 2.36))),
        # small guide plate (modern info layer), west wall by the door
        ("guide_plate", bl, B((GUIDE_PLATE["x0"], GUIDE_PLATE["y0"], GUIDE_PLATE["z0"]),
                              (GUIDE_PLATE["x1"], GUIDE_PLATE["y1"], GUIDE_PLATE["z1"]))),
        # operation desk: top + four 0.06 sq legs inset 0.05
        ("desk_top", g, B((DESK["x0"], DESK["top_y0"], DESK["z0"]), (DESK["x1"], DESK["top_y1"], DESK["z1"]))),
        ("desk_leg_a", g, B((-0.85, 0.0, -0.225), (-0.79, 0.74, -0.165))),
        ("desk_leg_b", g, B((0.79, 0.0, -0.225), (0.85, 0.74, -0.165))),
        ("desk_leg_c", g, B((-0.85, 0.0, 0.365), (-0.79, 0.74, 0.425))),
        ("desk_leg_d", g, B((0.79, 0.0, 0.365), (0.85, 0.74, 0.425))),
        # stool behind the desk: seat + four 0.05 sq legs inset 0.03
        ("stool_seat", g, B((0.09, 0.40, -0.91), (0.51, 0.45, -0.49))),
        ("stool_leg_a", g, B((0.12, 0.0, -0.88), (0.17, 0.40, -0.83))),
        ("stool_leg_b", g, B((0.43, 0.0, -0.88), (0.48, 0.40, -0.83))),
        ("stool_leg_c", g, B((0.12, 0.0, -0.57), (0.17, 0.40, -0.52))),
        ("stool_leg_d", g, B((0.43, 0.0, -0.57), (0.48, 0.40, -0.52))),
        # single supply crate, north-east corner
        ("crate_a", g, B(CRATES[0][:3], CRATES[0][3:])),
        # original kerosene lamp on the desk (no brand)
        ("lamp_base", g, C((LAMP["x"], 0.79, LAMP["z"]), 0.055, 0.02)),
        ("lamp_stem", g, C((LAMP["x"], 0.85, LAMP["z"]), 0.012, 0.10)),
        ("lamp_glass", g, C((LAMP["x"], 0.945, LAMP["z"]), 0.045, 0.09)),
        ("lamp_cap", g, C((LAMP["x"], 0.9975, LAMP["z"]), 0.05, 0.015)),
    ]
    return parts


def build_prop_meshes(prop_id, make_box, make_cyl):
    """Return list of (node_name, shape) in LOCAL prop space (origin bottom
    center, front -Z). Placeholder props only (key / codebook); the radio is
    built by build_radio_nodes() with its own material set."""
    B, C = make_box, make_cyl
    if prop_id == "p_s1_key":
        return [
            ("key_base", B((-0.075, 0.0, -0.05), (0.075, 0.025, 0.05))),
            ("key_post", C((0.0, 0.0425, 0.035), 0.008, 0.035)),
            ("key_contact", C((0.0, 0.036, -0.030), 0.004, 0.022)),
            # key_lever is a separate node with origin at the pivot so the
            # future interact animation can rotate it (OQ-K-03)
            ("key_lever", B((-0.005, -0.004, -0.080), (0.005, 0.004, 0.005))),
            ("key_knob", C((0.0, 0.012, -0.070), 0.011, 0.018)),
        ]
    if prop_id == "p_s1_codebook":
        return [
            ("book_cover_bottom", B((-0.075, 0.0, -0.105), (0.075, 0.006, 0.105))),
            ("book_pages", B((-0.068, 0.006, -0.098), (0.068, 0.029, 0.098))),
            ("book_cover_top", B((-0.075, 0.029, -0.105), (0.075, 0.035, 0.105))),
        ]
    raise KeyError(prop_id)

# key_lever pivot (world of local node translation); lever + knob attach here
KEY_LEVER_PIVOT = (0.0, 0.042, 0.035)


# ---------------------------------------------------------------- radio
# Review-grade generic box radio (M3D-01R section 4). Local space: origin at
# bottom center of the body footprint, front panel faces -Z.
#
# Tilted control panel: center C=[0, 0.135, -0.14], 0.38 x 0.215 x 0.012 m,
# rotated a=13.4 deg about X so the top leans back (+Z). Panel-local frame:
#   ex=(1,0,0), ey=(0,cos a,sin a), n=(0,sin a,-cos a)
#   face point = C + u*ex + v*ey + 0.006*n
#
# DOCUMENTED DEVIATION (PANEL_SHIFT): with the spec'd center z=-0.14 the
# tilted panel front surface only exits the body front face (z=-0.16) for
# v < -0.061, which would bury the meter and 4 of the 6 knobs inside the
# body solid. The whole front assembly (panel + screws + meter + knobs +
# sockets) is therefore shifted 0.0412 m along the panel normal n so the
# panel top edge clears the body face by ~1 mm (panel center becomes
# [0, 0.14455, -0.18008]). Panel-local (u,v) coordinates, the 13.4 deg tilt,
# all radii and the cable polyline are kept EXACTLY as specified;
# cable_socket_01 (whose tube length is unpinned) is lengthened to bridge
# from its shifted panel position to the pinned cable start point.

_A = math.radians(13.4)
_COS_A, _SIN_A = math.cos(_A), math.sin(_A)
PANEL_CENTER = (0.0, 0.135, -0.14)
PANEL_N = (0.0, _SIN_A, -_COS_A)
PANEL_EX = (1.0, 0.0, 0.0)
PANEL_EY = (0.0, _COS_A, _SIN_A)
PANEL_SHIFT = 0.0412

_SHIFTED_C = (
    PANEL_CENTER[0] + PANEL_SHIFT * PANEL_N[0],
    PANEL_CENTER[1] + PANEL_SHIFT * PANEL_N[1],
    PANEL_CENTER[2] + PANEL_SHIFT * PANEL_N[2],
)


def _face_pt(u, v, out=0.006):
    """Point on the dial panel front surface: C' + u*ex + v*ey + out*n."""
    return (
        _SHIFTED_C[0] + u * PANEL_EX[0] + v * PANEL_EY[0] + out * PANEL_N[0],
        _SHIFTED_C[1] + u * PANEL_EX[1] + v * PANEL_EY[1] + out * PANEL_N[1],
        _SHIFTED_C[2] + u * PANEL_EX[2] + v * PANEL_EY[2] + out * PANEL_N[2],
    )


def _along(p, dist):
    """Move point p by dist along the panel normal n."""
    return (p[0] + dist * PANEL_N[0], p[1] + dist * PANEL_N[1], p[2] + dist * PANEL_N[2])


# 6 knobs, varying size: (node, u, v, radius)
_RADIO_KNOBS = [
    ("knob_01", 0.03, 0.055, 0.014),
    ("knob_02", 0.11, 0.055, 0.011),
    ("knob_03", -0.12, -0.01, 0.010),
    ("knob_04", -0.04, -0.01, 0.013),
    ("knob_05", 0.05, -0.01, 0.010),
    ("knob_06", 0.13, -0.01, 0.008),
]

# 4 cable sockets: (node, u, v, radius)
_RADIO_SOCKETS = [
    ("cable_socket_01", -0.10, -0.075, 0.0065),
    ("cable_socket_02", -0.02, -0.075, 0.006),
    ("cable_socket_03", 0.06, -0.075, 0.007),
    ("cable_socket_04", 0.13, -0.075, 0.006),
]

# single dark cable: droops from cable_socket_01 to the desk, then runs along
# the desk front edge. Pinned polyline (local), r0.0055, capped ends.
RADIO_CABLE = [
    (-0.100, 0.066, -0.175),
    (-0.105, 0.038, -0.185),
    (-0.10, 0.012, -0.16),
    (-0.08, 0.0, -0.10),
    (-0.05, 0.0, 0.02),
    (-0.02, 0.0, 0.14),
    (0.0, 0.0, 0.26),
    # 末端 z 截短到 0.29：radio 以 yaw 180 摆放后，末端世界 z = 0.04-0.29 = -0.25，
    # 仍在桌面上（桌后缘 -0.275），不悬空。
    (0.0, 0.0, 0.29),
]


def build_radio_nodes():
    """Return [(node_name, [shape, ...], material_key)] in LOCAL prop space.
    material_key indexes RADIO_MATERIALS."""
    T = lambda p0, p1, r, seg, cap=True: ("tube", (tuple(p0), tuple(p1), r, seg, cap))
    RB = lambda c, s: ("rbox", (tuple(c), tuple(s), 13.4))
    BX = lambda lo, hi: ("box", (tuple(lo), tuple(hi)))

    nodes = []

    # -- radio_body: main box + lid + feet + vents + handle (one mesh) -------
    body = [
        BX((-0.21, 0.01, -0.16), (0.21, 0.27, 0.16)),          # main box
        BX((-0.215, 0.25, -0.165), (0.215, 0.28, 0.165)),      # lid, slight overhang
    ]
    for sx in (-0.17, 0.17):                                   # 4 rubber feet, y[0,0.01]
        for sz in (-0.12, 0.12):
            body.append(T((sx, 0.0, sz), (sx, 0.01, sz), 0.018, 12))
    for side in (1, -1):                                       # 5 vent slits per side
        x0, x1 = (0.21, 0.212) if side > 0 else (-0.212, -0.21)
        for k in range(5):
            zc = -0.10 + 0.045 * k
            body.append(BX((x0, 0.08, zc - 0.01), (x1, 0.16, zc + 0.01)))
    body += [                                                  # top-rear carry handle
        BX((-0.09, 0.28, 0.06), (-0.07, 0.295, 0.10)),         # mount block L
        BX((0.07, 0.28, 0.06), (0.09, 0.295, 0.10)),           # mount block R
        T((-0.08, 0.29, 0.08), (-0.08, 0.305, 0.08), 0.006, 10),
        T((0.08, 0.29, 0.08), (0.08, 0.305, 0.08), 0.006, 10),
        T((-0.08, 0.305, 0.08), (0.08, 0.305, 0.08), 0.006, 10),
    ]
    nodes.append(("radio_body", body, "mat_radio_body"))

    # -- dial_main: tilted panel + 4 corner screws (one mesh) ----------------
    dial = [RB(_SHIFTED_C, (0.38, 0.215, 0.012))]
    for su in (-0.175, 0.175):
        for sv in (-0.0925, 0.0925):
            p = _face_pt(su, sv)
            dial.append(T(p, _along(p, 0.008), 0.004, 12))
    nodes.append(("dial_main", dial, "mat_radio_panel"))

    # -- meter_window (bezel) + meter_window_face (glass), upper-left --------
    # NOTE: two nodes because one GLB mesh carries one material; node names
    # keep the meter_window* namespace per spec fallback.
    mb = _along(_face_pt(-0.09, 0.055), 0.002)
    mg = _along(_face_pt(-0.09, 0.055), 0.0045)
    nodes.append(("meter_window", [RB(mb, (0.10, 0.06, 0.004))], "mat_radio_metal"))
    nodes.append(("meter_window_face", [RB(mg, (0.085, 0.048, 0.002))], "mat_radio_meter"))

    # -- knob_01..06: knob tube + one flat washer each (metal) ---------------
    for name, u, v, r in _RADIO_KNOBS:
        p = _face_pt(u, v)
        nodes.append((name, [
            T(p, _along(p, 0.003), r + 0.004, 28),             # flat washer
            T(_along(p, 0.003), _along(p, 0.021), r, 28),      # knob
        ], "mat_radio_metal"))

    # -- cable_socket_01..04 (metal); socket_01 bridges to the cable start ---
    for name, u, v, r in _RADIO_SOCKETS:
        p = _face_pt(u, v)
        if name == "cable_socket_01":
            # lengthened connector: shifted panel position -> pinned cable start
            nodes.append((name, [T(p, RADIO_CABLE[0], r, 16)], "mat_radio_metal"))
        else:
            nodes.append((name, [T(p, _along(p, 0.014), r, 16)], "mat_radio_metal"))

    # -- cable_main: single dark cable, r0.0055, 12 sides, capped ends -------
    cable = []
    for i in range(len(RADIO_CABLE) - 1):
        cable.append(T(RADIO_CABLE[i], RADIO_CABLE[i + 1], 0.0055, 12))
    nodes.append(("cable_main", cable, "mat_cable"))

    return nodes
