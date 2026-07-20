"""Render S1 whitebox preview images with a small numpy software renderer.

Outputs (modeling_delivery/S1/preview/):
- scene_overview.png    axonometric cutaway + colliders + markers + dims
- visitor_start.png     true first-person view from visitor_start
- props_contact_sheet.png  front / side / back / wireframe per prop

Run from repo root:  python modeling_delivery/S1/source/whitebox/render_previews.py
"""

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
from matplotlib.patches import Polygon as MplPolygon
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


def cyl_tris(center, r, h, seg=12):
    cx, cy, cz = center
    h2 = h / 2
    tris = []
    for i in range(seg):
        a0 = 2 * np.pi * i / seg
        a1 = 2 * np.pi * (i + 1) / seg
        p = [(cx + r * np.cos(a0), cy - h2, cz + r * np.sin(a0)),
             (cx + r * np.cos(a1), cy - h2, cz + r * np.sin(a1)),
             (cx + r * np.cos(a1), cy + h2, cz + r * np.sin(a1)),
             (cx + r * np.cos(a0), cy + h2, cz + r * np.sin(a0))]
        tris.append([p[0], p[1], p[2]])
        tris.append([p[0], p[2], p[3]])
        for sign in (1, -1):
            c = (cx, cy + sign * h2, cz)
            v0 = (cx + r * np.cos(2 * np.pi * i / seg), cy + sign * h2, cz + r * np.sin(2 * np.pi * i / seg))
            v1 = (cx + r * np.cos(2 * np.pi * ((i + 1) % seg) / seg), cy + sign * h2, cz + r * np.sin(2 * np.pi * ((i + 1) % seg) / seg))
            tris.append([c, v1, v0] if sign > 0 else [c, v0, v1])
    return np.array(tris, dtype=float)


def shape_tris(shape):
    kind, args = shape
    if kind == "box":
        return box_tris(args[0], args[1])
    return cyl_tris(args[0], args[1], args[2])


def make_box(lo, hi):
    return ("box", (tuple(lo), tuple(hi)))


def make_cyl(center, r, h):
    return ("cyl", (tuple(center), r, h))


def env_soup(skip=()):
    tris, colors = [], []
    for name, mat, shape in L.build_env_parts(make_box, make_cyl):
        if name in skip:
            continue
        t = shape_tris(shape)
        tris.append(t)
        colors += [L.MATERIALS[mat]] * len(t)
    return tris, colors


def prop_soup(prop_id, world=True):
    """Triangles (+colors) of a prop; world=True applies scene.json placement."""
    tris, colors = [], []
    if prop_id == "p_s1_key":
        specs = [make_box((-0.075, 0.0, -0.05), (0.075, 0.025, 0.05)),
                 make_cyl((0.0, 0.0425, 0.035), 0.008, 0.035),
                 make_cyl((0.0, 0.036, -0.030), 0.004, 0.022),
                 make_box((-0.005, 0.042 - 0.004, 0.035 - 0.080), (0.005, 0.042 + 0.004, 0.035 + 0.005)),
                 make_cyl((0.0, 0.042 + 0.012, 0.035 - 0.070), 0.011, 0.018)]
    else:
        specs = [shape for _, shape in L.build_prop_meshes(prop_id, make_box, make_cyl)]
    for sp in specs:
        t = shape_tris(sp)
        tris.append(t)
        colors += [L.MATERIALS[L.PROP_BROWN]] * len(t)
    arr = np.concatenate(tris)
    if world:
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
           wireframe=False, shade=True, near=0.05):
    """tri_groups: list of (tri_array, [colors]). Painter's algorithm."""
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
        lambert = np.clip(norms @ LIGHT, 0, 1)
        for i in range(n):
            if not keep[i]:
                continue
            pts2 = np.stack([sx[i], sy[i]], axis=1)
            base = np.array(colors[i])
            if wireframe:
                edges.append((pts2, tuple(base)))
            else:
                f = 0.55 + 0.45 * (lambert[i] if shade else 0.7)
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
    cam = camera((10.5, 7.2, 10.2), (0.0, 0.6, 0.2))
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
    # colliders as red dashed wire boxes
    for c in L.COLLIDERS:
        wire_box(ax, cam, c["min_m"], c["max_m"], "#c0392b", fov, aspect)
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
    wtext((0, 0.02, -4.25), "8.00 m（产品白盒尺度，非历史尺寸）")
    wtext((-4.35, 0.02, 0), "8.00 m")
    wtext((4.3, 1.3, -4.1), "2.60 m")
    wtext(tuple(p0 + np.array([0.9, 0.15, 0.1])), "visitor_start [0, 1.6, 3.0]", "#1e8449")
    wtext((0.8, 1.35, 1.5), "p_s1_radio + key + codebook（桌面操作组）", "#7b3f00")
    wtext((0, 2.0, -3.9), "info_panel（导览蓝）", "#1a5276")
    wtext((-3.3, 1.05, -1.3), "crates", "#444444")
    finish(ax, "S1 白盒 · scene_overview · 灰=环境 棕=可交互 蓝=导览 ｜ 红虚线=colliders 橙点线=movement bounds 绿=起点 蓝钻=move_points ｜ 2026-07-20 v0.1 临时坐标待真机联调")
    fig.tight_layout()
    fig.savefig(os.path.join(PREVIEW, "scene_overview.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------ 2) visitor start
def visitor_start():
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=150)
    eye = L.VISITOR_START["position_m"]
    cam = camera(eye, (0.55, 1.0, 1.55))
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
    finish(ax, "S1 白盒 · visitor_start 第一人称近似 [0, 1.6, 3.0] 朝 -Z ｜ 起点直视可见电台桌（§4.3 首个交互目标 <2m）｜ 软件渲染示意，真实材质/光照以 Filament 真机为准")
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
    titles = {"p_s1_radio": "p_s1_radio 秘密电台（占位）", "p_s1_key": "p_s1_key 发报键（占位）",
              "p_s1_codebook": "p_s1_codebook 密码本（无纹理占位）"}
    for row, pid in enumerate(("p_s1_radio", "p_s1_key", "p_s1_codebook")):
        d = L.PROPS[pid]["dims_m"]
        arr, cols = prop_soup(pid, world=False)
        scale = 0.75 * max(d)
        for col, (vname, camfn) in enumerate(views):
            ax = axes[row][col]
            eye, target = camfn(d)
            cam = camera(eye, target)
            if col == 3:
                render(ax, [(arr, cols)], cam, ortho=True, ortho_scale=scale, wireframe=True)
                # origin tripod: X red, Y green, Z blue
                for vec, c in (((0.08, 0, 0), "red"), ((0, 0.08, 0), "green"), ((0, 0, 0.08), "blue")):
                    p = project(np.array([[0, 0, 0], vec], float), cam, 50, 1, True, scale)
                    ax.plot(p[0], p[1], color=c, lw=1.5)
            else:
                render(ax, [(arr, cols)], cam, ortho=True, ortho_scale=scale)
            ax.set_xlim(-0.85, 0.85)
            ax.set_ylim(-0.85, 0.85)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_title(vname, fontsize=9)
        fig.text(0.015, 0.78 - row * 0.30, f"{titles[pid]}\n{d[0]:.3f}×{d[1]:.3f}×{d[2]:.3f} m\n原点=底面中心\n正面=-Z",
                 fontsize=8, ha="left", va="center",
                 bbox=dict(boxstyle="round", fc="#f4f4f4", ec="#999999"))
    fig.suptitle("S1 白盒 · props_contact_sheet · 占位文物三视图 + 线框 ｜ 无铭文/无贴图 ｜ 2026-07-20 v0.1", fontsize=11)
    fig.tight_layout(rect=(0.12, 0, 1, 0.95))
    fig.savefig(os.path.join(PREVIEW, "props_contact_sheet.png"), bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(PREVIEW, exist_ok=True)
    scene_overview()
    visitor_start()
    contact_sheet()
    print("previews written to", PREVIEW)


if __name__ == "__main__":
    main()
