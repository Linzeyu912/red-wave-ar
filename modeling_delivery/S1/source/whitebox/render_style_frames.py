"""S1 style review frames STYLE-01/02/03 (M3D-01 review round).

Simple original-material previews per modeling_input/S1/02_MODELING_HANDOFF §4
and research/S1_pingxi_intelligence_station/style_reference_board.md §10:
- procedural palette only (style board §4 working colors); no external
  textures, no HDRI, no copied imagery;
- warm desk task light + cool ambient + weak self-lit info layer;
- every frame rendered at exactly 1600x900 and again at 1280x720
  (re-rendered, never stretched).

STYLE-03 contains ONE preview-only candidate element (guide-blue location
card beside the door, ZONE-A) that is NOT in the runtime GLB / scene.json;
it exists so the review can judge history-layer vs info-layer separation.

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

# ------------------------------------------------------------ palette (style board §4)
def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


C_STONE_DARK = hexrgb("#3F4542")   # 山石深灰
C_BRICK = hexrgb("#626965")        # 灰砖
C_STONE = hexrgb("#898A80")        # 粗石
C_WOOD = hexrgb("#49392E")         # 旧木深褐
C_EARTH = hexrgb("#6F5842")        # 土褐
C_GREEN = hexrgb("#4D5643")        # 低饱和军绿
C_RED = hexrgb("#78352F")          # 暗朱红（仅入口木框）
C_WARM = hexrgb("#C58B4A")         # 暖灯琥珀
C_INFO = hexrgb("#708489")         # 信息层灰蓝
C_PAPER = hexrgb("#B8AA91")        # 纸张暖灰

NODE_COLORS = {
    "floor": (C_STONE, 0.025), "ceiling": (C_STONE_DARK, 0.02),
    "wall_north": (C_BRICK, 0.025), "wall_east": (C_BRICK, 0.025), "wall_west": (C_BRICK, 0.025),
    "wall_south_a": (C_BRICK, 0.025), "wall_south_b": (C_BRICK, 0.025),
    "wall_south_lintel": (C_BRICK, 0.025),
    "entry_frame_left": (C_RED, 0.0), "entry_frame_right": (C_RED, 0.0), "entry_frame_top": (C_RED, 0.0),
    "door_leaf": (C_WOOD, 0.02),
    "info_panel": (C_INFO, 0.0),
    "desk_top": (C_WOOD, 0.02), "desk_leg_a": (C_WOOD, 0.02), "desk_leg_b": (C_WOOD, 0.02),
    "desk_leg_c": (C_WOOD, 0.02), "desk_leg_d": (C_WOOD, 0.02),
    "stool_seat": (C_WOOD, 0.02), "stool_leg_a": (C_WOOD, 0.02), "stool_leg_b": (C_WOOD, 0.02),
    "stool_leg_c": (C_WOOD, 0.02), "stool_leg_d": (C_WOOD, 0.02),
    "crate_a": (C_EARTH, 0.03), "crate_b": (C_EARTH, 0.03), "crate_c": (C_EARTH, 0.03),
    "lamp_cord": (C_STONE_DARK, 0.0), "lamp_base": (C_STONE_DARK, 0.0), "lamp_stem": (C_STONE_DARK, 0.0),
    "lamp_shade": (C_WARM, 0.0), "lamp_shade_desk": (C_WARM, 0.0),
}
EMISSIVE = {"lamp_shade": 1.9, "lamp_shade_desk": 1.7, "info_panel": 1.12, "zone_a_card": 1.12}

PROP_COLORS = {"p_s1_radio": C_GREEN, "p_s1_key": C_STONE_DARK, "p_s1_codebook": C_PAPER}

# preview-only candidate (NOT in runtime GLB / scene.json): ZONE-A location card
ZONE_A_CARD = ("zone_a_card", make_box((0.30, 1.20, 3.955), (0.95, 1.80, 3.985)))

# ------------------------------------------------------------ lighting
AMB = np.array([0.34, 0.36, 0.40]) * 0.95          # cool neutral ambient (暗部可辨)
FILL_DIR = np.array([0.15, 0.9, -0.2]); FILL_DIR /= np.linalg.norm(FILL_DIR)
FILL_COL = np.array([0.50, 0.56, 0.64]) * 0.30     # cool sky-ish fill from above
WARM_COL = np.array(C_WARM)
COOL_COL = np.array([0.55, 0.62, 0.70])
WARM_LIGHTS = [
    (np.array([L.LAMP_HANGING["x"], 2.02, L.LAMP_HANGING["z"]]), 2.4, 1.15, WARM_COL),   # hanging, over desk
    (np.array([L.LAMP_DESK["x"], 1.12, L.LAMP_DESK["z"]]), 1.2, 0.55, WARM_COL),         # desk oil lamp
    (np.array([0.0, 2.30, -2.5]), 0.9, 2.2, COOL_COL),                                   # dim cool fill, route area
]


def box_tris_sub(lo, hi, max_seg=0.5):
    """Subdivided box faces: keeps the painter sort honest for large faces."""
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    tris = []
    # faces: (fixed axis, fixed value, var axis u, var axis v, flip)
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


def soup(include_card=False):
    """Return list of (tri_array, [per-face base colors], [emissive boosts])."""
    groups = []
    seed = 0
    for name, _mat, shape in L.build_env_parts(make_box, make_cyl):
        t = shape_tris_sub(shape)
        color, amp = NODE_COLORS[name]
        cols, ems = [], []
        for i in range(len(t)):
            seed += 1
            cols.append(tuple(np.array(color) * jitter(seed, amp)))
            ems.append(EMISSIVE.get(name, 0.0))
        groups.append((t, cols, ems))
    if include_card:
        name, shape = ZONE_A_CARD
        t = shape_tris_sub(shape)
        groups.append((t, [C_INFO] * len(t), [EMISSIVE[name]] * len(t)))
    for pid, spec in L.PROPS.items():
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
        arr = np.concatenate(tris) + np.array(spec["position_m"], float)
        groups.append((arr, [PROP_COLORS[pid]] * len(arr), [0.0] * len(arr)))
    return groups


# ------------------------------------------------------------ render
def render_frame(path, eye, target, fov, caption, include_card=False, size=(16.0, 9.0)):
    w_in, h_in = size
    fig = plt.figure(figsize=(w_in, h_in), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#1A1C1B")
    fig.patch.set_facecolor("#1A1C1B")
    cam = camera(eye, target)
    aspect = w_in / h_in
    polys, cols, depth = [], [], []          # lit pass
    epolys, ecols, edepth = [], [], []       # emissive pass (always drawn last)
    for arr, base_cols, ems in soup(include_card=include_card):
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
            target_lists = (epolys, ecols, edepth) if ems[i] else (polys, cols, depth)
            target_lists[0].append(np.stack([sx[i], sy[i]], axis=1))
            target_lists[1].append(tuple(shade(base_cols[i], cent[i], norms[i], ems[i])))
            target_lists[2].append(z[i].mean())
    for pl, cl, dl in ((polys, cols, depth), (epolys, ecols, edepth)):
        if not pl:
            continue
        order = np.argsort(dl)[::-1]
        coll = PolyCollection([pl[i] for i in order],
                              facecolors=[cl[i] for i in order],
                              edgecolors=[tuple(np.array(cl[i]) * 0.85) for i in order],
                              linewidths=0.15)
        ax.add_collection(coll)
    ax.set_xlim(-1.02, 1.02)
    ax.set_ylim(-1.02, 1.02)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(0.012, 0.018, caption, fontsize=8, color="#C9CDC9", ha="left", va="bottom")
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
    radio = L.PROPS["p_s1_radio"]["position_m"]
    desk_c = [(L.DESK["x0"] + L.DESK["x1"]) / 2, (L.DESK["z0"] + L.DESK["z1"]) / 2]
    door_c = [(L.DOOR["x0"] + L.DOOR["x1"]) / 2, 1.25, 4.0]
    views = [
        ("STYLE-01_visitor_start", [0.0, 1.6, 3.0], [desk_c[0], 1.05, desk_c[1]], 55, False,
         "STYLE-01 游客起点 [0,1.6,3.0] 眼高1.6m · 暖光电台桌第一眼 · 背景灰蓝信息层 · 程序色板审核图 2026-07-20"),
        ("STYLE-02_operator_45deg", [-0.50, 1.55, 2.85], [0.72, 0.95, 1.42], 52, False,
         "STYLE-02 操作区前左45° · radio/key/资料包互不遮挡 · 桌面暖光任务区 · 程序色板审核图 2026-07-20"),
        ("STYLE-03_route_to_entry", [0.4, 1.6, -2.4], door_c, 65, True,
         "STYLE-03 路线区回望入口 · 灰砖/粗石/旧木历史层 vs 灰蓝信息层 · 含预览候选元素(导览蓝地点卡,未入运行时GLB) · 2026-07-20"),
    ]
    all_metrics = {}
    for name, eye, tgt, fov, card, caption in views:
        all_metrics[name] = {}
        for tag, size in (("", (16.0, 9.0)), ("_720p", (12.8, 7.2))):
            out = os.path.join(STYLE_DIR, f"{name}{tag}.png")
            m = render_frame(out, eye, tgt, fov, caption, include_card=card, size=size)
            all_metrics[name][tag or "_1600"] = m
            print(f"wrote {out}")
    for name, sizes in all_metrics.items():
        m = sizes["_1600"]
        print(f"{name}: red={m['red_share_pct']:.2f}% warm={m['warm_share_pct']:.2f}% "
              f"warm_in_center={m['warm_in_center_pct']:.1f}% center_luma={m['center_luma']:.3f} "
              f"global_luma={m['global_luma']:.3f} dark_p02={m['dark_p02_luma']:.3f}")


if __name__ == "__main__":
    main()
