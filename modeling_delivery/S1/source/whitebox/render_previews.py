"""Render S1 whitebox preview images with a small numpy software renderer.

Outputs (modeling_delivery/S1/preview/):
- scene_overview.png       axonometric cutaway + colliders + markers + dims
- visitor_start.png        true first-person view from visitor_start
- props_contact_sheet.png  front / side / back / wireframe per prop
- layout_top.png           orthographic top-down layout plan

Compact-cellar revision (M3D-01R): 5.3 x 4.7 x 2.25 m room.
Run from repo root:  python modeling_delivery/S1/source/whitebox/render_previews.py
"""

import math
import os
import sys

import matplotlib

# managed-runtime CJK font setup (must precede pyplot import)
sys.path.insert(0, __import__("pathlib").Path(sys.executable).parent.parent.parent.as_posix())
try:
    from daimon_runtime import setup_plot
    setup_plot()
except Exception:  # noqa: BLE001 - fall back to plain matplotlib
    pass

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon as MplPolygon, Rectangle
from matplotlib.collections import PolyCollection

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout_s1 as L

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW = os.path.normpath(os.path.join(HERE, "..", "..", "preview"))

LIGHT = np.array([0.45, 1.0, 0.3])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


# ------------------------------------------------------------ geometry soup
def box_tris(lo, hi):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    quads = [
        [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        [(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)],
        [(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)],
        [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)],
    ]
    tris = []
    for q in quads:
        tris.append([q[0], q[1], q[2]])
        tris.append([q[0], q[2], q[3]])
    return np.array(tris, dtype=float)


def rbox_tris(center, size, rot_x_deg):
    """Box rotated about X through `center` (+deg leans the top back, +Z)."""
    th = math.radians(rot_x_deg)
    c, s = math.cos(th), math.sin(th)
    cx, cy, cz = center
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    tris = box_tris((-hx, -hy, -hz), (hx, hy, hz))
    x = tris[..., 0]
    y = tris[..., 1]
    z = tris[..., 2]
    ry = c * y - s * z
    rz = s * y + c * z
    return np.stack([x + cx, ry + cy, rz + cz], axis=-1)


def cyl_tris(center, r, h, seg=12):
    cx, cy, cz = center
    h2 = h / 2
    tris = []
    for i in range(seg):
        a0 = 2 * np.pi * i / seg
        a1 = 2 * np.pi * (i + 1) / seg
        p = [(cx + r * np.cos(a0), cy - h2, cz + r * np.sin(a0)),
             (cx + r * np.cos(a0), cy + h2, cz + r * np.sin(a0)),
             (cx + r * np.cos(a1), cy + h2, cz + r * np.sin(a1)),
             (cx + r * np.cos(a1), cy - h2, cz + r * np.sin(a1))]
        tris.append([p[0], p[1], p[2]])
        tris.append([p[0], p[2], p[3]])
        for sign in (1, -1):
            c = (cx, cy + sign * h2, cz)
            v0 = (cx + r * np.cos(2 * np.pi * i / seg), cy + sign * h2, cz + r * np.sin(2 * np.pi * i / seg))
            v1 = (cx + r * np.cos(2 * np.pi * ((i + 1) % seg) / seg), cy + sign * h2, cz + r * np.sin(2 * np.pi * ((i + 1) % seg) / seg))
            tris.append([c, v1, v0] if sign > 0 else [c, v0, v1])
    return np.array(tris, dtype=float)


def tube_tris(p0, p1, r, seg=10, cap=True):
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    a = p1 - p0
    ln = np.linalg.norm(a)
    if ln < 1e-9:
        return np.zeros((0, 3, 3))
    a = a / ln
    ref = np.array([0.0, 1.0, 0.0]) if abs(a[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(a, ref)
    u = u / np.linalg.norm(u)
    v = np.cross(a, u)
    tris = []

    def ring(p, t):
        return p + r * (np.cos(t) * u + np.sin(t) * v)

    for i in range(seg):
        t0 = 2 * np.pi * i / seg
        t1 = 2 * np.pi * (i + 1) / seg
        A, B = ring(p0, t0), ring(p0, t1)
        C, D = ring(p1, t1), ring(p1, t0)
        tris.append([A, B, C])
        tris.append([A, C, D])
        if cap:
            tris.append([p1, B, C])   # +a cap
            tris.append([p0, D, A])   # -a cap
    return np.array(tris, dtype=float)


def shape_tris(shape):
    kind, args = shape
    if kind == "box":
        return box_tris(args[0], args[1])
    if kind == "cyl":
        return cyl_tris(args[0], args[1], args[2])
    if kind == "tube":
        return tube_tris(args[0], args[1], args[2], args[3], args[4] if len(args) > 4 else True)
    if kind == "rbox":
        return rbox_tris(args[0], args[1], args[2])
    raise ValueError(kind)


def make_box(lo, hi):
    return ("box", (tuple(lo), tuple(hi)))


def make_cyl(center, r, h):
    return ("cyl", (tuple(center), r, h))


def _as_list(shape):
    return shape if isinstance(shape, list) else [shape]


def env_soup(skip=()):
    tris, colors = [], []
    for name, mat, shape in L.build_env_parts(make_box, make_cyl):
        if name in skip:
            continue
        for sp in _as_list(shape):
            t = shape_tris(sp)
            tris.append(t)
            colors += [L.MATERIALS[mat]] * len(t)
    return tris, colors


def prop_soup(prop_id, world=True):
    """Triangles (+colors) of a prop; world=True applies scene.json placement."""
    tris, colors = [], []
    if prop_id == "p_s1_radio":
        for _name, spec, mkey in L.build_radio_nodes():
            t = np.concatenate([shape_tris(sp) for sp in spec])
            tris.append(t)
            colors += [L.RADIO_MATERIALS[mkey]["base_color"]] * len(t)
    elif prop_id == "p_s1_key":
        specs = [make_box((-0.075, 0.0, -0.05), (0.075, 0.025, 0.05)),
                 make_cyl((0.0, 0.0425, 0.035), 0.008, 0.035),
                 make_cyl((0.0, 0.036, -0.030), 0.004, 0.022),
                 make_box((-0.005, 0.042 - 0.004, 0.035 - 0.080), (0.005, 0.042 + 0.004, 0.035 + 0.005)),
                 make_cyl((0.0, 0.042 + 0.012, 0.035 - 0.070), 0.011, 0.018)]
        for sp in specs:
            t = shape_tris(sp)
            tris.append(t)
            colors += [L.MATERIALS[L.PROP_BROWN]] * len(t)
    else:
        for _name, shape in L.build_prop_meshes(prop_id, make_box, make_cyl):
            t = shape_tris(shape)
            tris.append(t)
            colors += [L.MATERIALS[L.PROP_BROWN]] * len(t)
    arr = np.concatenate(tris)
    if world:
        yaw = math.radians(L.PROPS[prop_id].get("rotation_deg", [0, 0, 0])[1])
        if yaw:
            c, s = math.cos(yaw), math.sin(yaw)
            rot = np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
            arr = arr @ rot.T
        off = np.array(L.PROPS[prop_id]["position_m"], dtype=float)
        arr = arr + off
    return arr, colors


# ------------------------------------------------------------ camera
def camera(eye, target, up=(0, 1, 0)):
    eye = np.asarray(eye, float)
    fwd = np.asarray(target, float) - eye
    fwd = fwd / np.linalg.norm(fwd)
    right = np.cross(fwd, np.asarray(up, float))
    right = right / np.linalg.norm(right)
    up2 = np.cross(right, fwd)
    return eye, right, up2, fwd


def project(pts, cam, fov_deg, aspect, ortho=False, ortho_scale=1.0):
    eye, right, up2, fwd = cam
    rel = pts - eye
    x = rel @ right
    y = rel @ up2
    z = rel @ fwd
    if ortho:
        return x / ortho_scale, y / ortho_scale, z
    f = 1.0 / np.tan(np.radians(fov_deg) / 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        sx = x * f / aspect / z
        sy = y * f / z
    return sx, sy, z


def render(ax, tri_groups, cam, fov=50, aspect=1.6, ortho=False, ortho_scale=1.0,
           wireframe=False, shade=True, near=0.05, light=None, amb=0.55):
    """tri_groups: list of (tri_array, [colors]). Painter's algorithm."""
    light = LIGHT if light is None else np.asarray(light, float) / np.linalg.norm(light)
    polys = []
    depth = []
    facecolors = []
    edges = []
    for arr, colors in tri_groups:
        n = len(arr)
        flat = arr.reshape(-1, 3)
        sx, sy, z = project(flat, cam, fov, aspect, ortho, ortho_scale)
        sx = sx.reshape(n, 3)
        sy = sy.reshape(n, 3)
        z = z.reshape(n, 3)
        keep = (z > near).all(axis=1)
        norms = np.cross(arr[:, 1] - arr[:, 0], arr[:, 2] - arr[:, 0])
        nl = np.linalg.norm(norms, axis=1, keepdims=True)
        norms = norms / np.maximum(nl, 1e-12)
        lambert = np.clip(norms @ light, 0, 1)
        for i in range(n):
            if not keep[i]:
                continue
            pts2 = np.stack([sx[i], sy[i]], axis=1)
            base = np.array(colors[i])
            if wireframe:
                edges.append((pts2, tuple(base)))
            else:
                f = amb + (1.0 - amb) * (lambert[i] if shade else 0.7)
                polys.append(pts2)
                facecolors.append(tuple(np.clip(base * f, 0, 1)))
                depth.append(z[i].mean())
    if wireframe:
        for pts2, c in edges:
            closed = np.vstack([pts2, pts2[0]])
            ax.plot(closed[:, 0], closed[:, 1], color=c, lw=0.6)
    else:
        order = np.argsort(depth)[::-1]
        coll = PolyCollection([polys[i] for i in order], facecolors=[facecolors[i] for i in order],
                              edgecolors=[tuple(np.array(fc) * 0.55) for fc in [facecolors[i] for i in order]],
                              linewidths=0.4)
        ax.add_collection(coll)


def wire_box(ax, cam, lo, hi, color, fov=50, aspect=1.6, lw=1.0, ls="--"):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    corners = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1],
                        [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]])
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    sx, sy, z = project(corners, cam, fov, aspect)
    for a, b in edges:
        if z[a] > 0.05 and z[b] > 0.05:
            ax.plot([sx[a], sx[b]], [sy[a], sy[b]], color=color, lw=lw, ls=ls)


def marker(ax, cam, pos, color, size=90, fov=50, aspect=1.6, shape="o"):
    sx, sy, z = project(np.array([pos], float), cam, fov, aspect)
    if z[0] > 0.05:
        ax.scatter([sx[0]], [sy[0]], s=size, c=color, marker=shape, zorder=10, edgecolors="black", linewidths=0.8)


def finish(ax, title):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11, loc="left")


# ------------------------------------------------------------ 1) overview
def scene_overview():
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=150)
    cam = camera((5.6, 4.1, 5.6), (0.0, 0.3, 0.05))
    fov, aspect = 46, 11 / 8.5
    skip = {"ceiling", "wall_south_a", "wall_south_b", "wall_south_lintel", "wall_east",
            "entry_frame_left", "entry_frame_right", "entry_frame_top", "door_leaf"}
    groups = []
    tris, colors = env_soup(skip=skip)
    groups.append((np.concatenate(tris), colors))
    for pid in L.PROPS:
        arr, cols = prop_soup(pid, world=True)
        groups.append((arr, cols))
    render(ax, groups, cam, fov=fov, aspect=aspect)
    # colliders as red dashed wire boxes (wall shells subtle, furniture strong)
    for c in L.COLLIDERS:
        subtle = c["id"].startswith("wall_")
        wire_box(ax, cam, c["min_m"], c["max_m"], "#c0392b", fov, aspect,
                 lw=0.5 if subtle else 1.0, ls=(0, (2, 3)) if subtle else "--")
    # visitor start + facing arrow
    marker(ax, cam, L.VISITOR_START["position_m"], "#2ecc71", shape="o")
    p0 = np.array(L.VISITOR_START["position_m"], float)
    p1 = p0 + np.array([0.0, -0.35, -1.3])
    s0 = project(np.array([p0]), cam, fov, aspect)
    s1 = project(np.array([p1]), cam, fov, aspect)
    ax.annotate("", xy=(s1[0][0], s1[1][0]), xytext=(s0[0][0], s0[1][0]),
                arrowprops=dict(arrowstyle="->", color="#2ecc71", lw=1.6))
    # move points
    for mp in L.MOVE_POINTS:
        marker(ax, cam, mp["position_m"], "#2980b9", shape="D", size=60)
    # bounds wire on floor
    wire_box(ax, cam, (L.MOVEMENT["x_min_m"], 0.01, L.MOVEMENT["z_min_m"]),
             (L.MOVEMENT["x_max_m"], 0.01, L.MOVEMENT["z_max_m"]), "#e67e22", fov, aspect, lw=1.4, ls=":")
    # dimension annotations (world-anchored text)
    def wtext(pos, s, color="#222222", fs=9):
        sx, sy, z = project(np.array([pos], float), cam, fov, aspect)
        if z[0] > 0:
            ax.text(sx[0], sy[0], s, fontsize=fs, color=color, ha="center")
    wtext((0, 0.55, -2.88), "5.30 m（产品白盒尺度，非历史尺寸）")
    wtext((-3.18, 0.42, 0.3), "4.70 m")
    wtext((2.88, 1.5, -2.78), "2.25 m")
    wtext(tuple(p0 + np.array([-1.35, 0.52, 0.0])), "visitor_start [0, 1.55, 1.65]", "#1e8449")
    wtext((0.42, 1.72, 0.55), "p_s1_radio + key + codebook（桌面操作组）", "#7b3f00")
    wtext((-2.28, 2.08, 1.85), "guide_plate（导览蓝）", "#1a5276")
    wtext((1.95, 0.68, -1.85), "crate", "#444444")
    finish(ax, "S1 白盒 · scene_overview · 灰=环境 棕=可交互 蓝=导览 ｜ 红虚线=colliders 橙点线=movement bounds 绿=起点 蓝钻=move_points ｜ M3D-01R 紧凑储洞小室 v0.3 临时坐标待真机联调")
    fig.tight_layout()
    fig.savefig(os.path.join(PREVIEW, "scene_overview.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------ 2) visitor start
def visitor_start():
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=150)
    eye = L.VISITOR_START["position_m"]
    cam = camera(eye, (0.05, 1.0, 0.1))
    fov, aspect = 62, 16 / 9
    groups = []
    tris, colors = env_soup(skip={"door_leaf", "entry_frame_left", "entry_frame_right", "entry_frame_top",
                                  "wall_south_a", "wall_south_b", "wall_south_lintel"})
    groups.append((np.concatenate(tris), colors))
    for pid in L.PROPS:
        arr, cols = prop_soup(pid, world=True)
        groups.append((arr, cols))
    render(ax, groups, cam, fov=fov, aspect=aspect, near=0.08)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    finish(ax, "S1 白盒 · visitor_start 第一人称近似 [0, 1.55, 1.65] 朝 -Z ｜ 起点直视暖光电台桌（首个交互目标 <2m）｜ 软件渲染示意，真实材质/光照以 Filament 真机为准 ｜ M3D-01R")
    fig.tight_layout()
    fig.savefig(os.path.join(PREVIEW, "visitor_start.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------ 3) contact sheet
def contact_sheet():
    fig, axes = plt.subplots(3, 4, figsize=(13, 10), dpi=150)
    views = [
        ("正面 front（朝 -Z）", lambda d: ((0, d[1] * 0.5, -2.2 * d[2]), (0, d[1] * 0.5, 0))),
        ("侧面 side（自 +X）", lambda d: ((2.2 * d[0], d[1] * 0.5, 0), (0, d[1] * 0.5, 0))),
        ("背面 back（自 +Z）", lambda d: ((0, d[1] * 0.5, 2.2 * d[2]), (0, d[1] * 0.5, 0))),
        ("线框 wireframe（iso）", lambda d: ((1.6 * d[0], 1.4 * d[1], -1.6 * d[2]), (0, d[1] * 0.45, 0))),
    ]
    titles = {"p_s1_radio": "p_s1_radio 通用箱式电台（审核级）", "p_s1_key": "p_s1_key 发报键（占位）",
              "p_s1_codebook": "p_s1_codebook 密码本（无纹理占位）"}
    scale_override = {"p_s1_radio": 0.62}  # cable trails beyond body dims
    SHEET_LIGHT = (0.30, 1.0, -0.55)  # biased toward -Z so the front views read
    for row, pid in enumerate(("p_s1_radio", "p_s1_key", "p_s1_codebook")):
        d = L.PROPS[pid]["dims_m"]
        arr, cols = prop_soup(pid, world=False)
        scale = 0.75 * max(max(d), scale_override.get(pid, 0.0))
        for col, (vname, camfn) in enumerate(views):
            ax = axes[row][col]
            eye, target = camfn(d)
            cam = camera(eye, target)
            if col == 3:
                render(ax, [(arr, cols)], cam, ortho=True, ortho_scale=scale, wireframe=True,
                       light=SHEET_LIGHT, amb=0.80)
                # origin tripod: X red, Y green, Z blue
                for vec, c in (((0.08, 0, 0), "red"), ((0, 0.08, 0), "green"), ((0, 0, 0.08), "blue")):
                    p = project(np.array([[0, 0, 0], vec], float), cam, 50, 1, True, scale)
                    ax.plot(p[0], p[1], color=c, lw=1.5)
            else:
                render(ax, [(arr, cols)], cam, ortho=True, ortho_scale=scale,
                       light=SHEET_LIGHT, amb=0.80)
            ax.set_xlim(-0.85, 0.85)
            ax.set_ylim(-0.85, 0.85)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_title(vname, fontsize=9)
        fig.text(0.015, 0.78 - row * 0.30, f"{titles[pid]}\n{d[0]:.3f}×{d[1]:.3f}×{d[2]:.3f} m\n原点=底面中心\n正面=-Z",
                 fontsize=8, ha="left", va="center",
                 bbox=dict(boxstyle="round", fc="#f4f4f4", ec="#999999"))
    fig.suptitle("S1 白盒 · props_contact_sheet · 文物三视图 + 线框 ｜ 无铭文/无贴图/无品牌 ｜ M3D-01R v0.3", fontsize=11)
    fig.tight_layout(rect=(0.12, 0, 1, 0.95))
    fig.savefig(os.path.join(PREVIEW, "props_contact_sheet.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------ 4) top view
def top_view():
    """Orthographic top-down layout plan (x right, -Z up => north up)."""
    fig, ax = plt.subplots(figsize=(11.5, 10.5), dpi=150)
    C_WALL = "#9aa0a3"
    C_ROOM = "#eceae4"
    C_WOOD = "#b08d5f"
    C_GUIDE = "#4a7fbf"
    C_PROP = "#c07a3e"

    # wall ring + interior (door gap punched on the south wall)
    ax.add_patch(Rectangle((-2.9, -2.6), 5.8, 5.2, fc=C_WALL, ec="none", zorder=1))
    ax.add_patch(Rectangle((-2.65, -2.35), 5.3, 4.7, fc=C_ROOM, ec="none", zorder=2))
    ax.add_patch(Rectangle((-1.9, 2.35), 0.8, 0.25, fc=C_ROOM, ec="none", zorder=3))  # door opening
    # brick patch / guide plate / skirt hint
    ax.add_patch(Rectangle((-2.45, 2.33), 0.5, 0.03, fc="#7f8a86", ec="none", zorder=4))
    ax.add_patch(Rectangle((-2.65, 1.55), 0.04, 0.60, fc=C_GUIDE, ec="none", zorder=4))
    for lo, hi in (((-2.65, -2.35), (2.65, -2.33)), ((-2.65, 2.33), (-2.45, 2.35)),
                   ((-1.05, 2.33), (2.65, 2.35)), ((2.63, -2.35), (2.65, 2.35)),
                   ((-2.65, -2.35), (-2.63, 2.35))):
        ax.add_patch(Rectangle(lo, hi[0] - lo[0], hi[1] - lo[1], fc="#b7b3a8", ec="none", zorder=3))
    # door leaf + frames
    ax.add_patch(Rectangle((-1.88, 2.37), 0.76, 0.08, fc="#8b6f4d", ec="#5b4630", lw=0.5, zorder=4))
    for x0, x1 in ((-1.95, -1.90), (-1.10, -1.05)):
        ax.add_patch(Rectangle((x0, 2.30), x1 - x0, 0.05, fc="#7a3b34", ec="none", zorder=4))

    # furniture
    ax.add_patch(Rectangle((-0.9, -0.275), 1.80, 0.75, fc=C_WOOD, ec="#6e5334", lw=1.0, zorder=5))
    ax.add_patch(Rectangle((0.09, -0.91), 0.42, 0.42, fc=C_WOOD, ec="#6e5334", lw=0.8, zorder=5))
    ax.add_patch(Rectangle((1.65, -2.10), 0.60, 0.50, fc=C_WOOD, ec="#6e5334", lw=0.8, zorder=5))
    ax.add_patch(Circle((0.72, 0.32), 0.055, fc="#c9a24d", ec="#6e5334", lw=0.6, zorder=6))

    # prop footprints + IDs
    for pid, (dx, _dy, dz) in ((p, L.PROPS[p]["dims_m"]) for p in L.PROPS):
        px, _py, pz = L.PROPS[pid]["position_m"]
        ax.add_patch(Rectangle((px - dx / 2, pz - dz / 2), dx, dz, fc=C_PROP, ec="#7a4a1d",
                               lw=0.9, zorder=7, alpha=0.92))
    ax.text(0.36, -0.335, "p_s1_radio", fontsize=7.5, ha="center", color="#7a4a1d", zorder=8)
    ax.text(-0.34, 0.56, "p_s1_key", fontsize=7.5, ha="center", color="#7a4a1d", zorder=8)
    ax.text(-0.62, -0.335, "p_s1_codebook", fontsize=7.5, ha="center", color="#7a4a1d", zorder=8)
    ax.text(0.86, 0.32, "煤油灯", fontsize=7, ha="left", va="center", color="#6e5334", zorder=8)

    # furniture labels
    ax.text(1.02, 0.10, "desk 1.80×0.75", fontsize=8, ha="left", va="center", color="#3d2c17", zorder=8)
    ax.text(0.30, -0.70, "stool", fontsize=7, ha="center", va="center", color="#3d2c17", zorder=8)
    ax.text(1.95, -1.85, "crate", fontsize=7, ha="center", va="center", color="#3d2c17", zorder=8)
    ax.text(-2.45, 2.30, "guide_plate", fontsize=7.5, ha="left", va="center", color=C_GUIDE, zorder=8)
    ax.text(-1.5, 2.72, "门洞 0.80 m（低矮储洞门）", fontsize=8, ha="center", color="#333333", zorder=8)

    # movement bounds (dotted) + colliders (dashed)
    ax.add_patch(Rectangle((-2.25, -1.95), 4.5, 3.9, fill=False, ec="#e67e22", lw=1.6, ls=":", zorder=6))
    for c in L.COLLIDERS:
        lo, hi = c["min_m"], c["max_m"]
        ax.add_patch(Rectangle((lo[0], lo[2]), hi[0] - lo[0], hi[2] - lo[2],
                               fill=False, ec="#c0392b", lw=0.8, ls="--", zorder=6))

    # visitor start + heading arrow (zero rotation = -Z)
    sx, sz = L.VISITOR_START["position_m"][0], L.VISITOR_START["position_m"][2]
    ax.scatter([sx], [sz], s=90, c="#2ecc71", marker="o", zorder=9, edgecolors="black", linewidths=0.8)
    ax.annotate("", xy=(sx, sz - 0.75), xytext=(sx, sz),
                arrowprops=dict(arrowstyle="->", color="#2ecc71", lw=1.8), zorder=9)
    ax.text(sx + 0.10, sz + 0.42, "visitor_start [0,1.55,1.65]\n朝 -Z", fontsize=8,
            color="#1e8449", zorder=9, va="center")

    # move points + look_at
    for mp in L.MOVE_POINTS:
        mx, mz = mp["position_m"][0], mp["position_m"][2]
        lx, lz = mp["look_at_m"][0], mp["look_at_m"][2]
        ax.scatter([mx], [mz], s=55, c="#2980b9", marker="D", zorder=9, edgecolors="black", linewidths=0.6)
        ax.plot([mx, lx], [mz, lz], color="#2980b9", lw=0.8, ls=":", zorder=8)
        ax.text(mx + 0.08, mz - 0.10, mp["id"], fontsize=7.5, color="#1a5276", zorder=9)

    # dimension chains (outside the walls)
    ax.annotate("", xy=(-2.65, 3.02), xytext=(2.65, 3.02),
                arrowprops=dict(arrowstyle="<->", color="#222222", lw=1.0))
    ax.text(0, 3.14, "5.30 m 净宽（产品白盒尺度，非历史尺寸）", fontsize=9, ha="center", color="#222222")
    ax.annotate("", xy=(-3.28, -2.35), xytext=(-3.28, 2.35),
                arrowprops=dict(arrowstyle="<->", color="#222222", lw=1.0))
    ax.text(-3.42, 0, "4.70 m 净深", fontsize=9, ha="center", va="center", rotation=90, color="#222222")
    ax.text(2.98, -1.2, "净高 2.25 m", fontsize=9, ha="left", color="#222222")

    # corridor clear widths
    ax.annotate("", xy=(-2.65, -0.95), xytext=(-0.9, -0.95),
                arrowprops=dict(arrowstyle="<->", color="#555555", lw=0.7))
    ax.text(-1.78, -1.06, "1.75", fontsize=7.5, ha="center", color="#555555")
    ax.annotate("", xy=(1.35, -2.35), xytext=(1.35, -0.275),
                arrowprops=dict(arrowstyle="<->", color="#555555", lw=0.7))
    ax.text(1.46, -1.3, "2.075", fontsize=7.5, ha="left", color="#555555")
    ax.annotate("", xy=(1.60, 0.475), xytext=(1.60, 2.35),
                arrowprops=dict(arrowstyle="<->", color="#555555", lw=0.7))
    ax.text(1.71, 1.4, "1.875", fontsize=7.5, ha="left", color="#555555")

    ax.set_xlim(-3.85, 3.55)
    ax.set_ylim(3.45, -3.35)  # inverted: -Z (north) up
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("S1 白盒 · layout_top 正交顶视 · 内净 5.30×4.70×2.25 m ｜ 红虚线=colliders 橙点线=bounds 绿=起点 蓝钻=move_points ｜ M3D-01R v0.3",
                 fontsize=10, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(PREVIEW, "layout_top.png"), bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(PREVIEW, exist_ok=True)
    scene_overview()
    visitor_start()
    contact_sheet()
    top_view()
    print("previews written to", PREVIEW)


if __name__ == "__main__":
    main()
