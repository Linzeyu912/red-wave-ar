"""S1 whitebox layout — single source of truth.

Shared by build_whitebox.py (GLB + scene.json) and render_previews.py so the
delivered files and preview images can never drift apart.

Basis:
- Plan v1.2 §4.3/§4.4/§5.4 (space rules, visitor start, contract examples)
- research/S1_pingxi_intelligence_station/modeling_brief.md §4/§8
  (whitebox allowed; gray=brown=blue category colors; desk group; stool;
  no inscriptions; codebook = untextured closed placeholder only)

All values are PROVISIONAL whitebox values, not historical dimensions
(UNVERIFIED-003: no wartime measurements exist). Every change of position,
start or interaction anchor must be joint-debugged with the coding model.

Convention: Y-up, right-handed, -Z forward, meters.
"""

# ---------------------------------------------------------------- materials
ENV_GRAY = "env_gray"        # environment: shell + furniture (plan-brief gray)
PROP_BROWN = "prop_brown"    # interactive props (radio / key / codebook)
GUIDE_BLUE = "guide_blue"    # guide objects (info panel, wayfinding)

MATERIALS = {
    ENV_GRAY: (0.58, 0.58, 0.60),
    PROP_BROWN: (0.48, 0.34, 0.22),
    GUIDE_BLUE: (0.24, 0.42, 0.72),
}

# ---------------------------------------------------------------- room shell
# Interior exactly 8.0 m x 8.0 m (product whitebox scale, NOT historical),
# ceiling 2.6 m, walls 0.2 m thick extending outward.
ROOM = {"x": 8.0, "z": 8.0, "h": 2.6, "wall_t": 0.2}

# Door (entry frame) on the south wall, behind/beside the visitor start.
DOOR = {"x0": -1.55, "x1": -0.55, "h": 2.0}  # opening 1.0 m wide

# Info surface on the north wall (modern exhibition layer -> guide blue).
INFO_PANEL = {"x0": -2.2, "x1": 2.2, "y0": 0.7, "y1": 2.3, "z0": -3.99, "z1": -3.93}

# ---------------------------------------------------------------- furniture
# Operation desk: hand-reachable height band 0.72-0.82 m (modeling_brief §4.3).
# Footprint 1.80 x 0.75 m per style_reference_board.md §6 ZONE-B frozen baseline
# ("保持桌宽 1.8 m、深 0.75 m、高 0.78 m 的已定占位基准"), same center as v0.1.
DESK = {"x0": -0.1, "x1": 1.7, "z0": 1.125, "z1": 1.875, "top_y0": 0.74, "top_y1": 0.78}
DESK_SURFACE_Y = 0.78

STOOL = {"cx": 0.55, "cz": 0.55, "w": 0.42, "seat_y0": 0.42, "seat_y1": 0.47}

CRATES = [  # supply crates, west wall (transport narrative, modeling_brief §5)
    (-3.70, 0.00, -1.90, -3.00, 0.45, -1.30),
    (-3.65, 0.00, -1.20, -3.05, 0.38, -0.70),
    (-3.62, 0.45, -1.82, -3.10, 0.80, -1.40),
]

LAMP_HANGING = {"x": 0.8, "z": 1.5, "cord_y0": 2.15, "cord_y1": 2.60, "shade_y0": 2.05, "shade_y1": 2.15, "shade_r": 0.14}
LAMP_DESK = {"x": 1.45, "z": 1.70}  # oil-lamp-like placeholder on desk corner

# ---------------------------------------------------------------- props
# Local-space definitions; origin at bottom center of footprint, front -Z.
# World placement goes to scene.json (never baked into prop GLBs).

PROPS = {
    "p_s1_radio": {
        "file": "props/radio_station_whitebox.glb",
        # main box + aux box (modeling_brief §4.2), no inscriptions
        "position_m": [0.55, DESK_SURFACE_Y, 1.60],
        "rotation_deg": [0.0, 0.0, 0.0],
        "scale": 1.0,
        "interaction_radius_m": 1.8,  # reachable from visitor start (1.50 m)
        "highlight_anchor_m": [0.0, 0.42, 0.0],
        "dims_m": [0.60, 0.28, 0.20],
    },
    "p_s1_key": {
        "file": "props/telegraph_key_whitebox.glb",
        # generic straight key; key_lever is a separate node (brief §4.3)
        "position_m": [0.15, DESK_SURFACE_Y, 1.28],
        "rotation_deg": [0.0, 0.0, 0.0],
        "scale": 1.0,
        "interaction_radius_m": 1.5,
        "highlight_anchor_m": [0.0, 0.12, 0.0],
        "dims_m": [0.15, 0.072, 0.10],
    },
    "p_s1_codebook": {
        "file": "props/code_book_whitebox.glb",
        # untextured closed booklet ONLY (FINAL_MODEL_BLOCKED, brief §4.4)
        "position_m": [1.32, DESK_SURFACE_Y, 1.35],
        "rotation_deg": [0.0, 0.0, 0.0],
        "scale": 1.0,
        "interaction_radius_m": 1.5,
        "highlight_anchor_m": [0.0, 0.10, 0.0],
        "dims_m": [0.15, 0.035, 0.21],
    },
}

# ---------------------------------------------------------------- visitor
VISITOR_START = {
    "position_m": [0.0, 1.6, 3.0],
    # Zero rotation = facing -Z per project convention (plan §5.2), i.e. toward
    # the radio desk. NOTE: plan §5.4 example shows [0,180,0]; discrepancy is
    # tracked as OQ-I-04 pending joint-debug with the coding model.
    "rotation_deg": [0.0, 0.0, 0.0],
}

MOVEMENT = {
    "type": "bounds",
    "speed_mps": 1.2,
    "x_min_m": -3.6,
    "x_max_m": 3.6,
    "z_min_m": -3.6,
    "z_max_m": 3.6,
}

# Simplified AABBs only (modeling_brief §7); never exported into render GLBs.
COLLIDERS = [
    {"id": "wall_north", "min_m": [-4.2, 0.0, -4.2], "max_m": [4.2, 2.6, -4.0]},
    {"id": "wall_south", "min_m": [-4.2, 0.0, 4.0], "max_m": [4.2, 2.6, 4.2]},   # door leaf is closed geometry; exit is handled by UI
    {"id": "wall_east", "min_m": [4.0, 0.0, -4.0], "max_m": [4.2, 2.6, 4.0]},
    {"id": "wall_west", "min_m": [-4.2, 0.0, -4.0], "max_m": [-4.0, 2.6, 4.0]},
    {"id": "desk_radio", "min_m": [-0.1, 0.0, 1.125], "max_m": [1.7, 0.78, 1.875]},
    {"id": "stool", "min_m": [0.34, 0.0, 0.34], "max_m": [0.76, 0.47, 0.76]},
    {"id": "crates", "min_m": [-3.7, 0.0, -1.9], "max_m": [-3.0, 0.8, -0.7]},
]

MOVE_POINTS = [
    {"id": "mp_radio", "position_m": [1.15, 1.6, 0.75], "look_at_m": [0.55, 1.0, 1.55]},
    {"id": "mp_info_wall", "position_m": [0.0, 1.6, -1.6], "look_at_m": [0.0, 1.5, -3.96]},
]


# ---------------------------------------------------------------- builders
def build_env_parts(make_box, make_cyl):
    """Return env parts: list of (node_name, material, shape) built in WORLD space."""
    parts = []
    B, C = make_box, make_cyl
    g, bl = ENV_GRAY, GUIDE_BLUE

    parts += [
        ("floor", g, B((-4.2, -0.10, -4.2), (4.2, 0.0, 4.2))),
        ("ceiling", g, B((-4.2, 2.6, -4.2), (4.2, 2.7, 4.2))),
        ("wall_north", g, B((-4.2, 0.0, -4.2), (4.2, 2.6, -4.0))),
        ("wall_east", g, B((4.0, 0.0, -4.0), (4.2, 2.6, 4.0))),
        ("wall_west", g, B((-4.2, 0.0, -4.0), (-4.0, 2.6, 4.0))),
        ("wall_south_a", g, B((-4.2, 0.0, 4.0), (DOOR["x0"], 2.6, 4.2))),
        ("wall_south_b", g, B((DOOR["x1"], 0.0, 4.0), (4.2, 2.6, 4.2))),
        ("wall_south_lintel", g, B((DOOR["x0"], DOOR["h"], 4.0), (DOOR["x1"], 2.6, 4.2))),
        # entry frame trim + closed leaf (exit is handled by UI, not by walking)
        ("entry_frame_left", g, B((DOOR["x0"] - 0.05, 0.0, 3.94), (DOOR["x0"] + 0.05, 2.05, 4.0))),
        ("entry_frame_right", g, B((DOOR["x1"] - 0.05, 0.0, 3.94), (DOOR["x1"] + 0.05, 2.05, 4.0))),
        ("entry_frame_top", g, B((DOOR["x0"] - 0.05, 2.0, 3.94), (DOOR["x1"] + 0.05, 2.08, 4.0))),
        ("door_leaf", g, B((DOOR["x0"] + 0.02, 0.02, 4.02), (DOOR["x1"] - 0.02, 1.98, 4.10))),
        # back-wall info surface (modern guide layer)
        ("info_panel", bl, B((INFO_PANEL["x0"], INFO_PANEL["y0"], INFO_PANEL["z0"]),
                             (INFO_PANEL["x1"], INFO_PANEL["y1"], INFO_PANEL["z1"]))),
        # operation desk
        ("desk_top", g, B((DESK["x0"], DESK["top_y0"], DESK["z0"]), (DESK["x1"], DESK["top_y1"], DESK["z1"]))),
        ("desk_leg_a", g, B((-0.05, 0.0, 1.175), (0.01, 0.74, 1.235))),
        ("desk_leg_b", g, B((1.59, 0.0, 1.175), (1.65, 0.74, 1.235))),
        ("desk_leg_c", g, B((-0.05, 0.0, 1.765), (0.01, 0.74, 1.825))),
        ("desk_leg_d", g, B((1.59, 0.0, 1.765), (1.65, 0.74, 1.825))),
        # stool (wooden stool per brief; not a chair)
        ("stool_seat", g, B((STOOL["cx"] - 0.21, 0.42, STOOL["cz"] - 0.21), (STOOL["cx"] + 0.21, 0.47, STOOL["cz"] + 0.21))),
        ("stool_leg_a", g, B((0.36, 0.0, 0.36), (0.41, 0.42, 0.41))),
        ("stool_leg_b", g, B((0.69, 0.0, 0.36), (0.74, 0.42, 0.41))),
        ("stool_leg_c", g, B((0.36, 0.0, 0.69), (0.41, 0.42, 0.74))),
        ("stool_leg_d", g, B((0.69, 0.0, 0.69), (0.74, 0.42, 0.74))),
        # supply crates, west wall
        ("crate_a", g, B(CRATES[0][:3], CRATES[0][3:])),
        ("crate_b", g, B(CRATES[1][:3], CRATES[1][3:])),
        ("crate_c", g, B(CRATES[2][:3], CRATES[2][3:])),
        # hanging lamp above the desk (guide light position per plan §4.4)
        ("lamp_cord", g, C((LAMP_HANGING["x"], (LAMP_HANGING["cord_y0"] + LAMP_HANGING["cord_y1"]) / 2, LAMP_HANGING["z"]),
                           0.012, LAMP_HANGING["cord_y1"] - LAMP_HANGING["cord_y0"])),
        ("lamp_shade", g, C((LAMP_HANGING["x"], (LAMP_HANGING["shade_y0"] + LAMP_HANGING["shade_y1"]) / 2, LAMP_HANGING["z"]),
                            LAMP_HANGING["shade_r"], LAMP_HANGING["shade_y1"] - LAMP_HANGING["shade_y0"])),
        # desk lamp placeholder (original-design oil-lamp-like; never labeled as relic)
        ("lamp_base", g, C((LAMP_DESK["x"], DESK_SURFACE_Y + 0.01, LAMP_DESK["z"]), 0.06, 0.02)),
        ("lamp_stem", g, C((LAMP_DESK["x"], DESK_SURFACE_Y + 0.15, LAMP_DESK["z"]), 0.012, 0.28)),
        ("lamp_shade_desk", g, C((LAMP_DESK["x"], DESK_SURFACE_Y + 0.32, LAMP_DESK["z"]), 0.08, 0.08)),
    ]
    return parts


def build_prop_meshes(prop_id, make_box, make_cyl):
    """Return list of (node_name, shape) in LOCAL prop space (origin bottom center, front -Z)."""
    B, C = make_box, make_cyl
    if prop_id == "p_s1_radio":
        return [
            ("radio_body", B((-0.30, 0.0, -0.10), (0.10, 0.28, 0.10))),
            ("radio_aux", B((0.14, 0.0, -0.08), (0.30, 0.18, 0.08))),
        ]
    if prop_id == "p_s1_key":
        return [
            ("key_base", B((-0.075, 0.0, -0.05), (0.075, 0.025, 0.05))),
            ("key_post", C((0.0, 0.0425, 0.035), 0.008, 0.035)),
            ("key_contact", C((0.0, 0.036, -0.030), 0.004, 0.022)),
            # key_lever is a separate node with origin at the pivot so the
            # future interact animation can rotate it (brief §4.3, OQ-K-03)
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
