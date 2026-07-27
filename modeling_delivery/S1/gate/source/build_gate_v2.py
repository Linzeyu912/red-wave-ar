# -*- coding: utf-8 -*-
"""
平西情报联络站门楼 v2 —— 写实精细版
依据 4 张参考图 + 用户描述:8级石阶/不锈钢栏杆/无障碍坡道/国旗阵/
石磨/大树/右侧廊房/院内景深/斗拱/六角灯笼/风化材质
坐标:平台(门楼基座)顶面 y=0,街面 y=-1.12,前方 +z
"""
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
BUILD = ROOT / ".build"
font_override = os.environ.get("S1_GATE_FONT")
font_candidates = ([pathlib.Path(font_override)] if font_override else []) + [
    pathlib.Path(r"C:\Windows\Fonts\msyh.ttc"),
    pathlib.Path(r"C:\Windows\Fonts\simhei.ttf"),
]
FONT = next((str(path) for path in font_candidates if path.is_file()), None)
if FONT is None:
    raise RuntimeError("Set S1_GATE_FONT to a Chinese-capable TrueType/OpenType font before rebuilding.")
TEX = BUILD / "tex2"
TEX.mkdir(parents=True, exist_ok=True)
RUNTIME.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)

# ============================================================ 贴图
def add_noise(img, sigma=6):
    a = np.asarray(img).astype(np.int16)
    a += rng.normal(0, sigma, a.shape).astype(np.int16)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def tex_brick(path, w=512, h=512):
    """灰青色旧砖:色差 + 砂浆缝 + 风化污渍"""
    img = Image.new("RGB", (w, h), (88, 92, 92))
    d = ImageDraw.Draw(img)
    bh, bw = 16, 64
    for row in range(h // bh):
        y0 = row * bh
        off = (bw // 2) if row % 2 else 0
        for x0 in range(-bw, w + bw, bw):
            shade = int(rng.integers(-14, 14))
            base = 118 + shade
            tint = int(rng.integers(-4, 8))       # 部分砖偏青
            d.rectangle([x0+off+2, y0+2, x0+off+bw-2, y0+bh-2],
                        fill=(base-4, base+tint//2, base+tint))
    # 风化污渍
    for _ in range(14):
        x, y = rng.integers(0, w), rng.integers(0, h)
        r = int(rng.integers(15, 60))
        d.ellipse([x-r, y-r, x+r, y+r], fill=(78, 82, 80, ))
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    add_noise(img, 5).save(path)

def tex_stone(path, w=512, h=512):
    """不规则毛石(左侧墙基座)"""
    img = Image.new("RGB", (w, h), (96, 94, 90))
    d = ImageDraw.Draw(img)
    for _ in range(60):
        x, y = rng.integers(-30, w), rng.integers(-20, h)
        rw, rh = int(rng.integers(40, 110)), int(rng.integers(30, 70))
        base = int(rng.integers(140, 180))
        pts = [(x+rw*0.1, y), (x+rw*0.9, y+rh*0.05), (x+rw, y+rh*0.6),
               (x+rw*0.7, y+rh), (x+rw*0.15, y+rh*0.9), (x, y+rh*0.4)]
        d.polygon(pts, fill=(base, base-2, base-6), outline=(80, 78, 74))
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    add_noise(img, 6).save(path)

def tex_wood(path, base=(110, 26, 26), w=256, h=512):
    """暗红旧漆木:竖向木纹 + 褪色磨损"""
    img = Image.new("RGB", (w, h), base)
    d = ImageDraw.Draw(img)
    for x in range(w):
        shade = int(10 * np.sin(x * 0.35) + rng.integers(-8, 8))
        d.line([(x, 0), (x, h)], fill=tuple(max(0, c + shade) for c in base))
    for _ in range(26):        # 露木/褪色条
        x = int(rng.integers(0, w))
        y0 = int(rng.integers(0, h))
        ln = int(rng.integers(20, 120))
        d.line([(x, y0), (x + int(rng.integers(-3, 3)), y0 + ln)],
               fill=(96, 62, 44), width=int(rng.integers(1, 3)))
    add_noise(img, 4).save(path)

def tex_plaque(path, w=1536, h=400):
    img = Image.open(TEX / "wood_red.png").resize((w, h))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, w-11, h-11], outline=(52, 16, 12), width=12)
    font = ImageFont.truetype(FONT, 195)
    small = ImageFont.truetype(FONT, 42)
    _draw_center(d, (150, 25, w-25, h-25), "平西情报联络站"[::-1], font, (70, 190, 145))
    d.text((48, 80), "焦\n若\n愚\n题", font=small, fill=(70, 190, 145))
    img.save(path)

def _draw_center(d, box, text, font, fill):
    l, t, r, b = box
    bb = d.textbbox((0, 0), text, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d.text((l+(r-l-tw)/2-bb[0], t+(b-t-th)/2-bb[1]), text, font=font, fill=fill)

def tex_couplet(path, text, w=256, h=1408):
    img = Image.open(TEX / "wood_red.png").resize((w, h))
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, w-7, h-7], outline=(52, 16, 12), width=8)
    font = ImageFont.truetype(FONT, 140)
    step = (h - 110) / len(text)
    for i, ch in enumerate(text):
        _draw_center(d, (0, 55+i*step, w, 55+(i+1)*step), ch, font, (70, 190, 145))
    img.save(path)

def tex_roof(path, w=512, h=512):
    """筒瓦屋面:竖向瓦垄 + 横向瓦层 + 阴影"""
    img = Image.new("RGB", (w, h))
    px = img.load()
    for x in range(w):
        ph = (x % 28) / 28.0 * np.pi * 2
        sh = int(26 * np.sin(ph))
        for y in range(h):
            row = int(10 * np.sin((y % 56) / 56.0 * np.pi))
            edge = 14 if (y % 56) < 4 else 0
            v = int(np.clip(104 + sh + row - edge, 30, 190))
            px[x, y] = (v, v, v+4)
    add_noise(img, 4).save(path)

def tex_ground(path, w=512, h=512):
    """街巷石板地面"""
    img = Image.new("RGB", (w, h), (100, 99, 95))
    d = ImageDraw.Draw(img)
    sw, sh = 128, 96
    for row in range(h // sh + 1):
        off = (sw // 2) if row % 2 else 0
        for col in range(-1, w // sw + 1):
            x0, y0 = col*sw + off, row*sh
            base = int(rng.integers(125, 160))
            d.rectangle([x0+3, y0+3, x0+sw-3, y0+sh-3],
                        fill=(base, base-2, base-6))
    img = img.filter(ImageFilter.GaussianBlur(0.7))
    add_noise(img, 7).save(path)

def tex_bark(path, w=256, h=512):
    img = Image.new("RGB", (w, h), (92, 74, 58))
    d = ImageDraw.Draw(img)
    for _ in range(90):
        x = int(rng.integers(0, w)); y0 = int(rng.integers(0, h))
        ln = int(rng.integers(30, 140))
        c = int(rng.integers(-22, 22))
        d.line([(x, y0), (x+int(rng.integers(-4, 4)), y0+ln)],
               fill=(92+c, 74+c, 58+c), width=int(rng.integers(2, 5)))
    add_noise(img, 5).save(path)

def tex_flag(path, w=300, h=200):
    img = Image.new("RGB", (w, h), (222, 41, 16))
    d = ImageDraw.Draw(img)
    def star(cx, cy, r, rot=-np.pi/2):
        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.382
            a = rot + i*np.pi/5
            pts.append((cx+rr*np.cos(a), cy+rr*np.sin(a)))
        d.polygon(pts, fill=(255, 222, 0))
    star(50, 50, 28)
    for cx, cy in [(100, 20), (120, 40), (120, 70), (100, 90)]:
        star(cx, cy, 10)
    img.save(path)

tex_brick(TEX/"brick.png"); tex_stone(TEX/"stone.png")
tex_wood(TEX/"wood_red.png"); tex_wood(TEX/"wood_dark.png", base=(62, 40, 30))
tex_plaque(TEX/"plaque.png")
tex_couplet(TEX/"couplet_l.png", "英雄热血铸丰碑")
tex_couplet(TEX/"couplet_r.png", "红色电波传密报")
tex_roof(TEX/"roof.png"); tex_ground(TEX/"ground.png")
tex_bark(TEX/"bark.png"); tex_flag(TEX/"flag.png")
print("textures done")

# ============================================================ 网格工具
def box_uv(w, h, d, scale=None):
    x, y, z = w/2, h/2, d/2
    F = [([(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)], w, h),
         ([(x,-y,-z),(-x,-y,-z),(-x,y,-z),(x,y,-z)], w, h),
         ([(-x,-y,-z),(-x,-y,z),(-x,y,z),(-x,y,-z)], d, h),
         ([(x,-y,z),(x,-y,-z),(x,y,-z),(x,y,z)], d, h),
         ([(-x,y,z),(x,y,z),(x,y,-z),(-x,y,-z)], w, d),
         ([(-x,-y,-z),(x,-y,-z),(x,-y,z),(-x,-y,z)], w, d)]
    verts, fcs, uvs = [], [], []
    for i, (q, du, dv) in enumerate(F):
        b = i*4
        verts += q; fcs += [[b,b+1,b+2],[b,b+2,b+3]]
        u1, v1 = (du/scale, dv/scale) if scale else (1.0, 1.0)
        uvs += [(0,0),(u1,0),(u1,v1),(0,v1)]
    m = trimesh.Trimesh(vertices=verts, faces=fcs, process=False)
    m.visual = trimesh.visual.TextureVisuals(uv=np.array(uvs, float))
    return m

def textured(mesh, img):
    mesh.visual = trimesh.visual.TextureVisuals(
        uv=mesh.visual.uv,
        material=trimesh.visual.material.SimpleMaterial(image=Image.open(img)))
    return mesh

def colored(mesh, rgb):
    mesh.visual = trimesh.visual.ColorVisuals(
        mesh, face_colors=np.tile(list(rgb)+[255], (len(mesh.faces), 1)))
    return mesh

def quad(p0, p1, p2, p3, uv=((0,0),(1,0),(1,1),(0,1))):
    m = trimesh.Trimesh(vertices=[p0,p1,p2,p3],
                        faces=[[0,1,2],[0,2,3]], process=False)
    m.visual = trimesh.visual.TextureVisuals(uv=np.array(uv, float))
    return m

def tube(p0, p1, r, rgb, sections=10):
    """两点之间的圆柱"""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    vec = p1 - p0; L = np.linalg.norm(vec)
    c = trimesh.creation.cylinder(r, L, sections=sections)
    z = np.array([0, 0, 1.0])
    d = vec / L
    axis = np.cross(z, d)
    if np.linalg.norm(axis) > 1e-6:
        ang = np.arccos(np.clip(np.dot(z, d), -1, 1))
        c.apply_transform(trimesh.transformations.rotation_matrix(ang, axis))
    elif d[2] < 0:
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    c.apply_translation((p0 + p1) / 2)
    return colored(c, rgb)

def board(w, h, thick, img, frame_rgb=(95, 18, 20)):
    b = colored(box_uv(w, h, thick), frame_rgb)
    f = quad((-w/2,-h/2,thick/2+0.002),(w/2,-h/2,thick/2+0.002),
             (w/2,h/2,thick/2+0.002),(-w/2,h/2,thick/2+0.002))
    textured(f, img)
    return trimesh.util.concatenate([b, f])

def roof_prism(half_w, eave_y, ridge_y, half_d, z0=0.0, rgb=(70,70,72),
               tex=True, tex_scale=0.9):
    """两坡屋顶:实体 + 瓦贴图坡面 + 正脊 + 檐口瓦当"""
    g = []
    prof = [(-half_d, eave_y), (0, ridge_y), (half_d, eave_y)]
    vs = [(x, y, z + z0) for x in (-half_w, half_w) for z, y in prof]
    fs = [[0,1,2],[3,5,4],[0,3,4],[0,4,1],[1,4,5],[1,5,2],[2,5,3],[2,3,0]]
    g.append(colored(trimesh.Trimesh(vertices=vs, faces=fs, process=False), rgb))
    slope = np.hypot(half_d, ridge_y - eave_y)
    for sgn in (-1, 1):
        q = quad((-half_w, ridge_y+0.012, z0), (half_w, ridge_y+0.012, z0),
                 (half_w, eave_y+0.012, z0+sgn*half_d), (-half_w, eave_y+0.012, z0+sgn*half_d),
                 uv=((0,0),(half_w*2/tex_scale,0),(half_w*2/tex_scale,slope/tex_scale),(0,slope/tex_scale)))
        if tex: textured(q, TEX/"roof.png")
        else: colored(q, rgb)
        g.append(q)
    g.append(tube((-half_w, ridge_y+0.05, z0), (half_w, ridge_y+0.05, z0), 0.09, (110,110,112)))
    for sx in (-1, 1):
        cap = colored(box_uv(0.16, 0.22, 0.24), (110,110,112))
        cap.apply_translation((sx*half_w, ridge_y+0.08, z0))
        g.append(cap)
    for sgn in (-1, 1):  # 檐口瓦当圆片
        n = max(6, int(half_w * 2 / 0.21))
        for i in range(n):
            x = -half_w + (i+0.5)*(2*half_w/n)
            d = colored(trimesh.creation.cylinder(0.05, 0.05, sections=8), (110,110,112))
            d.apply_translation((x, eave_y-0.02, z0+sgn*(half_d+0.03)))
            g.append(d)
    return g

scene = trimesh.Scene()
add = scene.add_geometry

RED = (110, 26, 26); STEEL = (198, 204, 210); GOLD = (212, 175, 55)

# ============================================================ 门楼主体
OPEN_HALF = 1.45           # 门洞净宽 2.9
OPEN_H = 3.5
# 砖门柱
for sx in (-1, 1):
    pier = box_uv(0.9, 4.15, 0.9, scale=0.5)
    textured(pier, TEX/"brick.png")
    pier.apply_translation((sx*(1.85+0.45), 4.15/2, 0))
    add(pier)
# 木门框(立柱+横梁) —— 旧红漆木
for sx in (-1, 1):
    post = box_uv(0.4, OPEN_H, 0.45, scale=1.0)
    textured(post, TEX/"wood_red.png")
    post.apply_translation((sx*(OPEN_HALF+0.2), OPEN_H/2, 0))
    add(post)
beam = box_uv(3.7, 0.45, 0.45, scale=1.0)
textured(beam, TEX/"wood_red.png"); beam.apply_translation((0, OPEN_H+0.225, 0))
add(beam)
beam2 = box_uv(3.7, 0.22, 0.4, scale=1.0)     # 上枋
textured(beam2, TEX/"wood_dark.png"); beam2.apply_translation((0, OPEN_H+0.56, 0))
add(beam2)

# 斗拱/托木:檐下深色木构件一排
for i in range(9):
    x = -2.4 + i * 0.6
    b1 = colored(box_uv(0.2, 0.14, 0.34), (58, 38, 28)); b1.apply_translation((x, 4.02, 0.28)); add(b1)
    b2 = colored(box_uv(0.3, 0.1, 0.24), (58, 38, 28));  b2.apply_translation((x, 4.14, 0.30)); add(b2)
# 檐口垫板
pad = box_uv(5.6, 0.16, 0.5, scale=1.0)
textured(pad, TEX/"wood_dark.png"); pad.apply_translation((0, 4.28, 0.1)); add(pad)

# 匾额
plaque = board(3.6, 0.8, 0.09, TEX/"plaque.png")
plaque.apply_translation((0, 3.98, 0.50)); add(plaque)

# 对联
for sx, img in [(-1, TEX/"couplet_l.png"), (1, TEX/"couplet_r.png")]:
    cp = board(0.52, 3.0, 0.06, img)
    cp.apply_translation((sx*2.3, 1.95, 0.48)); add(cp)

# 六角灯笼 ×2(梁下)
def lantern(x, y_top):
    body = colored(trimesh.creation.cylinder(0.17, 0.34, sections=6), (150, 30, 30))
    body.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0]))
    body.apply_translation((x, y_top-0.28, 0.24)); add(body)
    for dy, r in [( -0.06, 0.10), (-0.50, 0.10)]:
        cap = colored(trimesh.creation.cylinder(r, 0.06, sections=6), GOLD)
        cap.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0]))
        cap.apply_translation((x, y_top-0.28+dy+0.28, 0.24)); add(cap)
    add(tube((x, y_top, 0.24), (x, y_top-0.11, 0.24), 0.012, GOLD, 6))          # 挂绳
    add(tube((x, y_top-0.50, 0.24), (x, y_top-0.72, 0.24), 0.015, (200, 60, 40), 6))  # 穗
lantern(-0.85, OPEN_H); lantern(0.85, OPEN_H)

# 双开红门(向内开)+ 门钉
def door(sx):
    ang = np.radians(75) * sx
    leaf = box_uv(1.42, 3.3, 0.06, scale=1.0)
    textured(leaf, TEX/"wood_red.png")
    parts = [leaf]
    for r_ in range(6):      # 门钉 5×6
        for c_ in range(5):
            s = colored(trimesh.creation.icosphere(0, 0.028), GOLD)
            s.apply_translation((-0.56+c_*0.28, -1.35+r_*0.54, 0.05))
            parts.append(s)
    m = trimesh.util.concatenate(parts)
    m.apply_translation((sx*1.42/2, 1.65+0.1, 0))     # 先就位(合页在 x=0 侧)
    rot = trimesh.transformations.rotation_matrix(-ang, [0,1,0])
    m.apply_transform(trimesh.transformations.translation_matrix((sx*OPEN_HALF, 0, -0.22)) @ rot
                      @ trimesh.transformations.translation_matrix((-sx*OPEN_HALF, 0, 0.22))
                      @ trimesh.transformations.translation_matrix((0, 0, 0)))
    return m
add(door(-1)); add(door(1))

# 门楼屋顶
for g in roof_prism(3.35, 4.45, 5.30, 1.5):
    add(g)
print("gate body done")

# ============================================================ 平台 / 台阶 / 坡道
STREET = -1.12
plat = box_uv(11.2, 0.15, 1.3, scale=0.8)
textured(plat, TEX/"ground.png"); plat.apply_translation((-1.2, -0.075, -0.55)); add(plat)
plat2 = box_uv(4.4, 0.15, 2.5, scale=0.8)
textured(plat2, TEX/"ground.png"); plat2.apply_translation((6.2, -0.075, -1.15)); add(plat2)

NST, SH, SD, SW = 8, 0.14, 0.32, 4.6      # 8 级台阶
for i in range(NST):
    top = STREET + (i+1)*SH
    st = box_uv(SW, top-STREET, SD, scale=0.8)
    textured(st, TEX/"ground.png")
    st.apply_translation((0, (STREET+top)/2, NST*SD - i*SD - SD/2))
    add(st)
def step_y(z):                              # 台阶表面高度
    return min(0.0, STREET + max(0, np.ceil((NST*SD - z)/SD)) * SH)

# 无障碍坡道(右侧)
ramp = trimesh.Trimesh(vertices=[
    (2.3, 0, 0.06), (3.5, 0, 0.06), (3.5, STREET, 3.6), (2.3, STREET, 3.6),
    (2.3, -0.12, 0.06), (3.5, -0.12, 0.06), (3.5, STREET-0.12, 3.6), (2.3, STREET-0.12, 3.6)],
    faces=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],
           [1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]], process=False)
uv = np.array([(0,0),(1.2/0.8,0),(1.2/0.8,3.8/0.8),(0,3.8/0.8),
               (0,0),(1,0),(1,1),(0,1)])
ramp.visual = trimesh.visual.TextureVisuals(uv=uv)
textured(ramp, TEX/"ground.png"); add(ramp)

# ============================================================ 不锈钢栏杆
def railing(points, top_h=0.92, mid_h=0.5):
    """沿折线的不锈钢栏杆:立柱 + 扶手 + 横杆"""
    tops, mids = [], []
    for x, y, z in points:
        add(tube((x, y, z), (x, y+top_h, z), 0.022, STEEL))
        tops.append((x, y+top_h, z)); mids.append((x, y+mid_h, z))
    for a, b in zip(tops[:-1], tops[1:]): add(tube(a, b, 0.028, STEEL))
    for a, b in zip(mids[:-1], mids[1:]): add(tube(a, b, 0.02, STEEL))

for sx in (-1, 1):                          # 台阶两侧
    pts = [(sx*(SW/2+0.06), step_y(z), z) for z in np.linspace(NST*SD-0.05, 0.05, 7)]
    pts.append((sx*(SW/2+0.06), 0.0, -0.5))
    railing(pts)
railing([(3.44, STREET, 3.55), (3.44, STREET+0.37, 2.4),    # 坡道外侧
         (3.44, STREET+0.75, 1.2), (3.44, 0.0, 0.05)])

# ============================================================ 国旗阵
def flag(x, z, base_y, pole_h=1.7, fw=0.55, fh=0.37, phase=0.0):
    add(tube((x, base_y, z), (x, base_y+pole_h, z), 0.014, STEEL, 8))
    nx, ny = 10, 6
    vs, fs, uv = [], [], []
    for iy in range(ny+1):
        for ix in range(nx+1):
            u, v = ix/nx, iy/ny
            vs.append((x + u*fw, base_y+pole_h-0.03-v*fh,
                       z + 0.05*np.sin(u*4.5+phase) * u))
            uv.append((u, 1-v))
    for iy in range(ny):
        for ix in range(nx):
            a = iy*(nx+1)+ix
            fs += [[a,a+1,a+nx+2],[a,a+nx+2,a+nx+1]]
    m = trimesh.Trimesh(vertices=vs, faces=fs, process=False)
    m.visual = trimesh.visual.TextureVisuals(uv=np.array(uv))
    textured(m, TEX/"flag.png"); add(m)

k = 0
for sx in (-1, 1):
    for z in (0.5, 1.25, 2.0):
        flag(sx*2.85, z, step_y(z), phase=k); k += 1.3
flag(-3.15, -0.3, 0.0, pole_h=3.2, fw=0.95, fh=0.63, phase=0.5)   # 门前大旗
flag( 3.15, -0.3, 0.0, pole_h=3.2, fw=0.95, fh=0.63, phase=2.1)

# ============================================================ 两侧院墙
# 左侧:下毛石 + 上青砖
st = box_uv(3.9, 1.15, 0.6, scale=0.9)
textured(st, TEX/"stone.png"); st.apply_translation((-4.7, 1.15/2, 0)); add(st)
br = box_uv(3.9, 2.15, 0.55, scale=0.5)
textured(br, TEX/"brick.png"); br.apply_translation((-4.7, 1.15+2.15/2, 0)); add(br)
cap = colored(box_uv(4.0, 0.09, 0.75), (110,110,112)); cap.apply_translation((-4.7, 3.35, 0)); add(cap)
add(tube((-6.65, 3.44, 0), (-2.75, 3.44, 0), 0.055, (80,80,82)))
# 右侧:整砖墙
br = box_uv(1.35, 2.9, 0.55, scale=0.5)
textured(br, TEX/"brick.png"); br.apply_translation((3.45, 1.45, 0)); add(br)
cap = colored(box_uv(1.45, 0.09, 0.75), (110,110,112)); cap.apply_translation((3.45, 2.95, 0)); add(cap)
add(tube((2.75, 3.04, 0), (4.15, 3.04, 0), 0.055, (80,80,82)))

# ============================================================ 右侧廊房(两层小楼)
CX0, CX1, CZ0, CZ1 = 4.15, 8.35, -2.3, 0.35
bw = box_uv(CX1-CX0, 2.5, CZ1-CZ0, scale=0.5)
textured(bw, TEX/"brick.png"); bw.apply_translation(((CX0+CX1)/2, 1.25, (CZ0+CZ1)/2)); add(bw)
# 二层:凹进的深色板壁 + 红柱 + 红栏杆
inw = colored(box_uv(CX1-CX0-0.3, 1.15, 0.2), (70, 42, 32))
inw.apply_translation(((CX0+CX1)/2, 3.1, CZ1-0.55)); add(inw)
for cx in np.linspace(CX0+0.25, CX1-0.25, 5):
    add(tube((cx, 2.5, CZ1-0.12), (cx, 3.68, CZ1-0.12), 0.07, (120, 40, 32)))
rail = colored(box_uv(CX1-CX0, 0.07, 0.07), (140, 40, 36))
rail.apply_translation(((CX0+CX1)/2, 3.02, CZ1-0.05)); add(rail)
rail2 = colored(box_uv(CX1-CX0, 0.06, 0.06), (140, 40, 36))
rail2.apply_translation(((CX0+CX1)/2, 2.58, CZ1-0.05)); add(rail2)
for cx in np.arange(CX0+0.15, CX1-0.1, 0.17):
    b = colored(box_uv(0.045, 0.44, 0.045), (140, 40, 36))
    b.apply_translation((cx, 2.8, CZ1-0.05)); add(b)
for g in roof_prism((CX1-CX0)/2+0.25, 3.72, 4.55, 1.55, z0=(CZ0+CZ1)/2):
    g.apply_translation(((CX0+CX1)/2, 0, 0)); add(g)

# ============================================================ 院内景深(透过门洞可见)
# 院内两步下阶 + 青砖地面
for i in range(2):
    top = -(i)*0.15
    st = box_uv(2.9, 0.15, 0.35, scale=0.8)
    textured(st, TEX/"ground.png")
    st.apply_translation((0, top-0.075, -0.55-i*0.35)); add(st)
yard = box_uv(7.0, 0.1, 6.5, scale=0.8)
textured(yard, TEX/"ground.png"); yard.apply_translation((0, -0.35, -4.2)); add(yard)
# 后院正房:灰砖墙 + 红柱 + 灰瓦顶
hw = box_uv(5.6, 2.6, 3.2, scale=0.5)
textured(hw, TEX/"brick.png"); hw.apply_translation((0, 1.0, -6.2)); add(hw)
for cx in (-1.6, -0.55, 0.55, 1.6):
    add(tube((cx, -0.3, -4.45), (cx, 2.15, -4.45), 0.08, (120, 40, 32)))
e = box_uv(5.6, 0.25, 0.3, scale=1.0)
textured(e, TEX/"wood_dark.png"); e.apply_translation((0, 2.28, -4.45)); add(e)
for g in roof_prism(3.1, 2.55, 3.55, 1.9, z0=-6.0):
    add(g)
# 院两侧配房屋顶剪影
for sx in (-1, 1):
    roof = colored(box_uv(2.2, 0.5, 2.6), (85, 85, 88))
    roof.apply_transform(trimesh.transformations.rotation_matrix(np.radians(12)*sx, [0,0,1]))
    roof.apply_translation((sx*2.9, 1.6, -3.4)); add(roof)

# ============================================================ 石磨 + 石槽(左墙前)
mill_base = colored(trimesh.creation.cylinder(0.72, 0.18, sections=20), (140,138,132))
mill_base.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0]))
mill_base.apply_translation((-3.6, STREET+0.09, 1.5)); add(mill_base)
for i, (r, h) in enumerate([(0.5, 0.18), (0.46, 0.16)]):
    ms = colored(trimesh.creation.cylinder(r, h, sections=24), (150+i*8, 148+i*8, 142+i*8))
    ms.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0]))
    ms.apply_translation((-3.6, STREET+0.18+0.09+i*0.17, 1.5)); add(ms)
handle = colored(box_uv(0.08, 0.08, 0.7), (96, 62, 44))
handle.apply_translation((-3.6, STREET+0.55, 1.85)); add(handle)
trough = colored(box_uv(0.95, 0.42, 0.5), (145,143,137))
trough.apply_translation((-2.55, STREET+0.21, 1.45)); add(trough)
tin = colored(box_uv(0.8, 0.06, 0.36), (90, 88, 84))
tin.apply_translation((-2.55, STREET+0.40, 1.45)); add(tin)

# ============================================================ 大树(右侧,树冠遮檐)
trunk = box_uv(0.5, 5.6, 0.5, scale=0.6)
textured(trunk, TEX/"bark.png"); trunk.apply_translation((3.85, STREET+2.8, 1.35)); add(trunk)
add(tube((3.85, 3.2, 1.35), (2.9, 4.6, 0.7), 0.14, (80, 64, 50)))
add(tube((3.85, 3.6, 1.35), (4.7, 4.9, 1.0), 0.12, (80, 64, 50)))
def canopy_blob(cx, cy, cz, s, rgb):
    b = trimesh.creation.icosphere(2, 1.0)
    b.apply_scale((s, s*0.72, s))
    b.apply_translation((cx, cy, cz))
    fc = np.tile(list(rgb)+[255], (len(b.faces), 1))
    jit = rng.integers(-16, 16, (len(b.faces), 1))
    fc[:, :3] = np.clip(fc[:, :3] + jit, 0, 255)
    b.visual = trimesh.visual.ColorVisuals(b, face_colors=fc)
    add(b)
canopy_blob(3.6, 5.6, 1.0, 1.5, (66, 116, 52))
canopy_blob(4.7, 5.1, 1.5, 1.2, (76, 128, 58))
canopy_blob(2.7, 6.2, 0.5, 1.3, (58, 104, 46))
canopy_blob(3.9, 6.6, 1.6, 1.4, (70, 122, 54))
canopy_blob(4.9, 6.1, 0.6, 1.1, (62, 110, 48))

# ============================================================ 街面地面
gnd = box_uv(20, 0.12, 9.0, scale=0.8)
textured(gnd, TEX/"ground.png"); gnd.apply_translation((0, STREET-0.06, 4.4)); add(gnd)

# ============================================================ 导出
out = RUNTIME / "s1_gate_v2.glb"
scene.export(str(out))
print("exported:", out, out.stat().st_size, "bytes,", len(scene.geometry), "geometries")
