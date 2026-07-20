"""S1 style review frames STYLE-01/02/03 (M3D-01R compact-cellar round).

Per modeling_input/S1/04_COMPACT_CELLAR_REVISION.md (M3D-01R):
- procedural palette only (style board working colors); no external textures,
  no HDRI, no copied imagery, no inscriptions;
- original kerosene lamp as the warm desk light + cool low ambient so the
  dark corners stay readable (克制、干燥、安静，不阴森);
- the only red accent in the room is the old wooden entry frame;
- every frame rendered at exactly 1600x900 and again at 1280x720
  (re-rendered, never stretched).

Outputs: modeling_delivery/S1/preview/style/STYLE-0X_*.png
Run from repo root:  python modeling_delivery/S1/source/whitebox/render_style_frames.py
"""

import os
import sys

import matplotlib

sys.path.insert(0, __import__("pathlib").Path(sys.executable).parent.parent.parent.as_posix())
try:
    from daimon_runtime import setup_plot
    setup_plot()
except Exception:  # noqa: BLE001
    pass

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout_s1 as L
from render_previews import camera, make_box, make_cyl, shape_tris

STYLE_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "preview", "style"))


# ------------------------------------------------------------ palette (style board working colors)
def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


C_STONE_DARK = hexrgb("#3F4542")   # 山石深灰
C_BRICK = hexrgb("#626965")        # 灰砖
C_STONE = hexrgb("#898A80")        # 粗石
C_WOOD = hexrgb("#49392E")         # 旧木深褐
C_EARTH = hexrgb("#6F5842")        # 土褐（夯土）
C_GREEN = hexrgb("#4D5643")        # 低饱和军绿
C_RED = hexrgb("#78352F")          # 暗朱红（仅入口木框）
C_WARM = hexrgb("#C58B4A")         # 暖灯琥珀
C_INFO = hexrgb("#708489")         # 信息层灰蓝
C_PAPER = hexrgb("#B8AA91")        # 纸张暖灰
C_METER = hexrgb("#10161A")        # 表窗近黑
C_METAL = hexrgb("#3A3D3A")        # 暗金属
C_CABLE = hexrgb("#141312")        # 线缆近黑

NODE_COLORS = {
    "floor": (C_STONE, 0.025), "ceiling": (C_STONE_DARK, 0.02),
    "wall_north": (C_EARTH, 0.025), "wall_east": (C_EARTH, 0.025), "wall_west": (C_EARTH, 0.025),
    "wall_south_a": (C_EARTH, 0.025), "wall_south_b": (C_EARTH, 0.025),
    "wall_south_lintel": (C_EARTH, 0.025),
    "skirt_north": (C_STONE, 0.03), "skirt_east": (C_STONE, 0.03),
    "skirt_south": (C_STONE, 0.03), "skirt_west": (C_STONE, 0.03),
    "brick_patch_a": (C_BRICK, 0.02),
    "entry_frame_left": (C_RED, 0.0), "entry_frame_right": (C_RED, 0.0), "entry_frame_top": (C_RED, 0.0),
    "door_leaf": (C_WOOD, 0.02),
    "guide_plate": (C_INFO, 0.0),
    "desk_top": (C_WOOD, 0.02), "desk_leg_a": (C_WOOD, 0.02), "desk_leg_b": (C_WOOD, 0.02),
    "desk_leg_c": (C_WOOD, 0.02), "desk_leg_d": (C_WOOD, 0.02),
    "stool_seat": (C_WOOD, 0.02), "stool_leg_a": (C_WOOD, 0.02), "stool_leg_b": (C_WOOD, 0.02),
    "stool_leg_c": (C_WOOD, 0.02), "stool_leg_d": (C_WOOD, 0.02),
    "crate_a": (C_WOOD, 0.03),
    "lamp_base": (C_STONE_DARK, 0.0), "lamp_stem": (C_STONE_DARK, 0.0),
    "lamp_glass": (C_WARM, 0.0), "lamp_cap": (C_STONE_DARK, 0.0),
}
EMISSIVE = {"lamp_glass": 1.8, "guide_plate": 1.12}

# review-grade radio: per-node colors; placeholders keep flat colors
RADIO_NODE_COLORS = {
    "radio_body": C_GREEN,
    "dial_main": C_STONE_DARK,
    "meter_window": C_METER, "meter_window_face": C_METER,
    "knob_01": C_METAL, "knob_02": C_METAL, "knob_03": C_METAL,
    "knob_04": C_METAL, "knob_05": C_METAL, "knob_06": C_METAL,
    "cable_socket_01": C_METAL, "cable_socket_02": C_METAL,
    "cable_socket_03": C_METAL, "cable_socket_04": C_METAL,
    "cable_main": C_CABLE,
}
PROP_COLORS = {"p_s1_key": C_STONE_DARK, "p_s1_codebook": C_PAPER}

# painter-sort layers: appliqué faces (skirts / patch / frames / plate) sit a
# few cm proud of the shell, so mean-depth sort interleaves them ("zebra").
# Sort by (layer, depth) instead of depth alone.
NODE_LAYER = {}
for _n in ("floor", "ceiling", "wall_north", "wall_east", "wall_west",
           "wall_south_a", "wall_south_b", "wall_south_lintel"):
    NODE_LAYER[_n] = 0
for _n in ("skirt_north", "skirt_east", "skirt_south", "skirt_west", "brick_patch_a",
           "guide_plate", "entry_frame_left", "entry_frame_right", "entry_frame_top", "door_leaf"):
    NODE_LAYER[_n] = 1
for _n in ("desk_top", "desk_leg_a", "desk_leg_b", "desk_leg_c", "desk_leg_d",
           "stool_seat", "stool_leg_a", "stool_leg_b", "stool_leg_c", "stool_leg_d",
           "crate_a", "lamp_base", "lamp_stem", "lamp_glass", "lamp_cap"):
    NODE_LAYER[_n] = 2

# ------------------------------------------------------------ lighting
AMB = np.array([0.34, 0.36, 0.40]) * 0.90          # cool low ambient (暗部可辨)
FILL_DIR = np.array([0.15, 0.9, -0.2]); FILL_DIR /= np.linalg.norm(FILL_DIR)
FILL_COL = np.array([0.50, 0.56, 0.64]) * 0.28     # cool sky-ish fill from above
WARM_COL = np.array(C_WARM)
COOL_COL = np.array([0.55, 0.62, 0.70])
WARM_LIGHTS = [
    (np.array([0.72, 0.95, 0.32]), 1.6, 0.9, WARM_COL),    # kerosene lamp on the desk
    (np.array([0.0, 1.9, 0.1]), 0.8, 1.2, WARM_COL),       # warm pool above the desk
    (np.array([-1.5, 2.0, 2.2]), 0.5, 1.5, COOL_COL),      # cool spill at the doorway
]


def box_tris_sub(lo, hi, max_seg=0.5):
    """Subdivided box faces: keeps the painter sort honest for large faces."""
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    tris = []
    faces = [
        (2, hi[2], 0, 1, False), (2, lo[2], 0, 1, True),
        (1, hi[1], 0, 2, True), (1, lo[1], 0, 2, False),
        (0, hi[0], 1, 2, False), (0, lo[0], 1, 2, True),
    ]
    for axis, val, au, av, flip in faces:
        nu = max(1, int(np.ceil((hi[au] - lo[au]) / max_seg)))
        nv = max(1, int(np.ceil((hi[av] - lo[av]) / max_seg)))
        us = np.linspace(lo[au], hi[au], nu + 1)
        vs = np.linspace(lo[av], hi[av], nv + 1)
        for i in range(nu):
            for j in range(nv):
                quad = []
                for uu, vv in ((us[i], vs[j]), (us[i + 1], vs[j]),
                               (us[i + 1], vs[j + 1]), (us[i], vs[j + 1])):
                    p = [0.0, 0.0, 0.0]
                    p[axis] = val
                    p[au] = uu
                    p[av] = vv
                    quad.append(tuple(p))
                if flip:
                    quad = [quad[0], quad[3], quad[2], quad[1]]
                tris.append([quad[0], quad[1], quad[2]])
                tris.append([quad[0], quad[2], quad[3]])
    return np.array(tris, dtype=float)


def shape_tris_sub(shape):
    kind, args = shape
    if kind == "box":
        return box_tris_sub(args[0], args[1])
    return shape_tris(shape)


def shade(base, centroid, normal, emissive_boost=0.0):
    base = np.array(base, float)
    if emissive_boost:
        return np.clip(base * emissive_boost, 0, 1)
    col = base * AMB
    col = col + base * FILL_COL * max(float(normal @ FILL_DIR), 0.0)
    for pos, i0, d0, lcol in WARM_LIGHTS:
        vec = pos - centroid
        d = float(np.linalg.norm(vec))
        lam = max(float(normal @ (vec / max(d, 1e-9))), 0.0) + 0.12  # soft wrap
        att = i0 / (1.0 + (d / d0) ** 2)
        col = col + base * lcol * lam * att
    return np.clip(col, 0, 1)


# ------------------------------------------------------------ soup
def jitter(seed, amp):
    return 1.0 + amp * (2.0 * ((seed * 2654435761 % 2**31) / 2**31) - 1.0)


def _as_list(shape):
    return shape if isinstance(shape, list) else [shape]


def _yaw_rot(deg):
    """Right-handed Y-up yaw rotation matrix matching scene.json rotation_deg[1]."""
    r = np.radians(deg)
    c, s = np.cos(r), np.sin(r)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])


def soup():
    """Return list of (tri_array, [per-face base colors], [emissive boosts], layer)."""
    groups = []
    seed = 0
    for name, _mat, shape in L.build_env_parts(make_box, make_cyl):
        color, amp = NODE_COLORS[name]
        layer = NODE_LAYER[name]
        for sp in _as_list(shape):
            t = shape_tris_sub(sp)
            cols, ems = [], []
            for i in range(len(t)):
                seed += 1
                cols.append(tuple(np.array(color) * jitter(seed, amp)))
                ems.append(EMISSIVE.get(name, 0.0))
            groups.append((t, cols, ems, layer))
    for pid, spec in L.PROPS.items():
        rot = _yaw_rot(spec.get("rotation_deg", [0, 0, 0])[1])
        pos = np.array(spec["position_m"], float)
        if pid == "p_s1_radio":
            for nname, shapes_, _mkey in L.build_radio_nodes():
                arr = np.concatenate([shape_tris(sp) for sp in shapes_]) @ rot.T + pos
                groups.append((arr, [RADIO_NODE_COLORS[nname]] * len(arr), [0.0] * len(arr), 3))
            continue
        tris = []
        if pid == "p_s1_key":
            specs = [make_box((-0.075, 0.0, -0.05), (0.075, 0.025, 0.05)),
                     make_cyl((0.0, 0.0425, 0.035), 0.008, 0.035),
                     make_cyl((0.0, 0.036, -0.030), 0.004, 0.022),
                     make_box((-0.005, 0.038, -0.045), (0.005, 0.046, 0.040)),
                     make_cyl((0.0, 0.054, -0.035), 0.011, 0.018)]
        else:
            specs = [s for _, s in L.build_prop_meshes(pid, make_box, make_cyl)]
        for sp in specs:
            tris.append(shape_tris(sp))
        arr = np.concatenate(tris) @ rot.T + pos
        groups.append((arr, [PROP_COLORS[pid]] * len(arr), [0.0] * len(arr), 3))
    return groups


# ------------------------------------------------------------ render
def render_frame(path, eye, target, fov, caption, size=(16.0, 9.0)):
    w_in, h_in = size
    fig = plt.figure(figsize=(w_in, h_in), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#1A1C1B")
    fig.patch.set_facecolor("#1A1C1B")
    cam = camera(eye, target)
    aspect = w_in / h_in
    polys, cols, depth, layers = [], [], [], []   # lit pass
    epolys, ecols, edepth = [], [], []       # emissive pass (always drawn last)
    for arr, base_cols, ems, layer in soup():
        n = len(arr)
        flat = arr.reshape(-1, 3)
        rel = flat - np.asarray(cam[0])
        x = (rel @ cam[1]).reshape(n, 3)
        y = (rel @ cam[2]).reshape(n, 3)
        z = (rel @ cam[3]).reshape(n, 3)
        keep = (z > 0.05).all(axis=1)
        f = 1.0 / np.tan(np.radians(fov) / 2)
        with np.errstate(divide="ignore", invalid="ignore"):
            sx = x * f / aspect / z
            sy = y * f / z
        norms = np.cross(arr[:, 1] - arr[:, 0], arr[:, 2] - arr[:, 0])
        norms /= np.maximum(np.linalg.norm(norms, axis=1, keepdims=True), 1e-12)
        cent = arr.mean(axis=1)
        for i in range(n):
            if not keep[i]:
                continue
            if ems[i]:
                epolys.append(np.stack([sx[i], sy[i]], axis=1))
                ecols.append(tuple(shade(base_cols[i], cent[i], norms[i], ems[i])))
                edepth.append(z[i].mean())
            else:
                polys.append(np.stack([sx[i], sy[i]], axis=1))
                cols.append(tuple(shade(base_cols[i], cent[i], norms[i], ems[i])))
                depth.append(z[i].mean())
                layers.append(layer)
    # lit pass: painter within painter-sort layers (shell -> appliqué ->
    # furniture -> props) so thin appliqué faces never zebra-fight the shell
    if polys:
        order = sorted(range(len(polys)), key=lambda i: (layers[i], -depth[i]))
        coll = PolyCollection([polys[i] for i in order],
                              facecolors=[cols[i] for i in order],
                              edgecolors=[tuple(np.array(cols[i]) * 0.85) for i in order],
                              linewidths=0.15)
        ax.add_collection(coll)
    if epolys:
        order = np.argsort(edepth)[::-1]
        coll = PolyCollection([epolys[i] for i in order],
                              facecolors=[ecols[i] for i in order],
                              edgecolors=[tuple(np.array(ecols[i]) * 0.85) for i in order],
                              linewidths=0.15)
        ax.add_collection(coll)
    # M3D-01R-P: fill the whole canvas — sx already carries the 1/aspect
    # normalization, so a non-equal axes aspect maps NDC ±1 onto the 16:9
    # frame with correct proportions and no pillar-box bars. Captions are
    # no longer burned in; camera/metric details live in style_review_report.md.
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-1.0, 1.0)
    ax.set_aspect("auto")
    ax.axis("off")
    fig.savefig(path)
    # ---- metrics on the rendered pixels
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].astype(float) / 255.0
    plt.close(fig)
    bg = np.array([0x1A, 0x1C, 0x1B]) / 255.0
    nonbg = (np.abs(buf - bg).sum(axis=2) > 0.06)
    r, g, b = buf[:, :, 0], buf[:, :, 1], buf[:, :, 2]
    # 暗朱红 accent only (excludes warm-lit wood): strong red dominance, low green
    red = nonbg & (r > 0.30) & (r > g * 1.80) & (r > b * 1.60) & (g < 0.40)
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    H, W = luma.shape
    cbox = np.zeros_like(nonbg)
    cbox[int(H * 0.30):int(H * 0.70), int(W * 0.30):int(W * 0.70)] = True
    warm = nonbg & (r > b + 0.10) & (r > 0.45) & (g > b)
    nb_luma = luma[nonbg]
    metrics = {
        "red_share_pct": 100.0 * red.sum() / max(nonbg.sum(), 1),
        "center_luma": float(luma[cbox & nonbg].mean()) if (cbox & nonbg).any() else 0.0,
        "global_luma": float(nb_luma.mean()),
        "dark_p02_luma": float(np.percentile(nb_luma, 2)),
        "warm_share_pct": 100.0 * warm.sum() / max(nonbg.sum(), 1),
        "warm_in_center_pct": 100.0 * (warm & cbox).sum() / max(warm.sum(), 1),
    }
    return metrics


def main():
    os.makedirs(STYLE_DIR, exist_ok=True)
    views = [
        ("STYLE-01_visitor_start", [0.0, 1.55, 1.65], [0.05, 1.0, 0.1], 60,
         "STYLE-01 游客起点 [0,1.55,1.65] 眼高1.55m · 暖光电台桌第一眼 · 紧凑储洞小室 5.3×4.7×2.25m · M3D-01R 程序色板审核图"),
        ("STYLE-02_operator_45deg", [-1.10, 1.45, 1.20], [0.05, 0.95, 0.12], 55,
         "STYLE-02 操作区前左45° · radio/key/codebook互不遮挡 · 煤油灯暖池 · M3D-01R 程序色板审核图"),
        ("STYLE-03_route_to_entry", [0.9, 1.55, -1.55], [-1.5, 1.15, 2.35], 65,
         "STYLE-03 室内回望入口 · 全场唯一红色=旧木门框 · 灰蓝导览牌(信息层) · 夯土/粗石历史层 · M3D-01R 程序色板审核图"),
    ]
    all_metrics = {}
    for name, eye, tgt, fov, caption in views:
        all_metrics[name] = {}
        for tag, size in (("", (16.0, 9.0)), ("_720p", (12.8, 7.2))):
            out = os.path.join(STYLE_DIR, f"{name}{tag}.png")
            m = render_frame(out, eye, tgt, fov, caption, size=size)
            all_metrics[name][tag or "_1600"] = m
            print(f"wrote {out}")
    for name, sizes in all_metrics.items():
        m = sizes["_1600"]
        print(f"{name}: red={m['red_share_pct']:.2f}% warm={m['warm_share_pct']:.2f}% "
              f"warm_in_center={m['warm_in_center_pct']:.1f}% center_luma={m['center_luma']:.3f} "
              f"global_luma={m['global_luma']:.3f} dark_p02={m['dark_p02_luma']:.3f}")


if __name__ == "__main__":
    main()
