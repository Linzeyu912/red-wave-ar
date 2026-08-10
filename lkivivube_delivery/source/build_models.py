"""Build the nine Kivicube GLB deliverables from reviewed visual constraints.

Run from the repository root with the bundled or system Python:

    python lkivivube_delivery/source/build_models.py

Only numpy and Pillow are required.  Source geometry stays modular in the
functions below; export merges objects by material to keep draw calls low.
"""

from __future__ import annotations

import json
import math
import os
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / ".build"
TEXTURES = BUILD / "textures"
REPORT = HERE / "build_report.json"

sys.path.insert(0, str(HERE))
from glbkit import Material, MeshBuilder, Model  # noqa: E402


def rgb(hex_value: str) -> tuple[float, float, float]:
    value = hex_value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) / 255.0 for index in (0, 2, 4))


def find_font() -> str:
    override = os.environ.get("RED_WAVE_FONT")
    candidates = [
        pathlib.Path(override) if override else None,
        pathlib.Path(r"C:\Windows\Fonts\msyh.ttc"),
        pathlib.Path(r"C:\Windows\Fonts\simhei.ttf"),
        pathlib.Path(r"C:\Windows\Fonts\simsun.ttc"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return str(candidate)
    raise RuntimeError("Set RED_WAVE_FONT to a Chinese-capable font file")


FONT = find_font()


def fit_font(text: str, box: tuple[int, int, int, int], maximum: int, vertical: bool = False) -> ImageFont.FreeTypeFont:
    left, top, right, bottom = box
    for size in range(maximum, 15, -4):
        font = ImageFont.truetype(FONT, size)
        if vertical:
            widths, heights = [], []
            for char in text:
                bounds = font.getbbox(char)
                widths.append(bounds[2] - bounds[0])
                heights.append(bounds[3] - bounds[1])
            if max(widths, default=0) <= right - left and sum(heights) * 1.18 <= bottom - top:
                return font
        else:
            bounds = font.getbbox(text)
            if bounds[2] - bounds[0] <= right - left and bounds[3] - bounds[1] <= bottom - top:
                return font
    return ImageFont.truetype(FONT, 16)


def draw_centered(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fill: tuple[int, int, int],
    maximum: int,
    rtl: bool = False,
) -> None:
    display = text[::-1] if rtl else text
    font = fit_font(display, box, maximum)
    bounds = draw.textbbox((0, 0), display, font=font)
    width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
    left, top, right, bottom = box
    draw.text(
        (left + (right - left - width) / 2.0 - bounds[0],
         top + (bottom - top - height) / 2.0 - bounds[1]),
        display,
        font=font,
        fill=fill,
    )


def draw_vertical(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fill: tuple[int, int, int],
    maximum: int,
) -> None:
    font = fit_font(text, box, maximum, vertical=True)
    left, top, right, bottom = box
    step = (bottom - top) / max(1, len(text))
    for index, char in enumerate(text):
        sub = (left, int(top + index * step), right, int(top + (index + 1) * step))
        draw_centered(draw, sub, char, fill, maximum)


def make_gate_atlas(path: pathlib.Path) -> None:
    image = Image.new("RGB", (2048, 2048), (80, 20, 18))
    draw = ImageDraw.Draw(image)
    # top quarter: horizontal plaque
    draw.rounded_rectangle((18, 18, 2030, 494), radius=28, fill=(93, 24, 20), outline=(45, 12, 10), width=22)
    draw_centered(draw, (90, 70, 1958, 442), "平西情报联络站", (144, 205, 171), 250, rtl=True)
    # lower left/right: two vertical couplets
    for box, text in [
        ((40, 560, 760, 2020), "英雄热血铸丰碑"),
        ((1288, 560, 2008, 2020), "红色电波传密报"),
    ]:
        draw.rounded_rectangle(box, radius=20, fill=(112, 26, 23), outline=(48, 12, 10), width=18)
        inner = (box[0] + 100, box[1] + 70, box[2] - 100, box[3] - 70)
        draw_vertical(draw, inner, text, (155, 211, 179), 165)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def make_sign(path: pathlib.Path, text: str, background: tuple[int, int, int],
              foreground: tuple[int, int, int], rtl: bool = False) -> None:
    image = Image.new("RGB", (1024, 320), background)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((12, 12, 1012, 308), radius=18, outline=tuple(max(0, c - 45) for c in background), width=14)
    draw_centered(draw, (40, 32, 984, 286), text, foreground, 180, rtl=rtl)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def make_memorial_atlas(path: pathlib.Path) -> None:
    image = Image.new("RGB", (1024, 768), (48, 37, 30))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18, 18, 1006, 750), radius=24, outline=(155, 116, 66), width=16)
    # Semantic title is 家国; physical left-to-right character placement is 国 家.
    draw_centered(draw, (80, 55, 944, 275), "国家", (198, 157, 92), 150)
    for y in range(335, 690, 46):
        margin = 95 + (y % 3) * 6
        draw.line((margin, y, 1024 - margin, y), fill=(103, 78, 52), width=4)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def make_telecom_atlas(path: pathlib.Path) -> None:
    image = Image.new("RGB", (2048, 1024), (232, 229, 216))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 2048, 512), fill=(94, 30, 26))
    draw_centered(draw, (70, 50, 1978, 462), "中国电信博物馆", (226, 191, 104), 230)
    draw.rectangle((1536, 512, 2048, 1024), fill=(231, 234, 230))
    draw_vertical(draw, (1610, 530, 1970, 1006), "中国电信博物馆", (176, 38, 32), 94)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def prepare_textures() -> dict[str, pathlib.Path]:
    textures = {
        "gate": TEXTURES / "s1_gate_signage.png",
        "juyong": TEXTURES / "s4_juyong_sign.png",
        "memorial": TEXTURES / "s5_memorial_plaque.png",
        "telecom": TEXTURES / "s7_telecom_signage.png",
    }
    make_gate_atlas(textures["gate"])
    make_sign(textures["juyong"], "天下第一雄关", (237, 227, 195), (35, 31, 25))
    make_memorial_atlas(textures["memorial"])
    make_telecom_atlas(textures["telecom"])
    return textures


def add_window_grid(builder: MeshBuilder, width: float, floors: int, columns: int,
                    y0: float, floor_height: float, z: float,
                    margin_x: float, window_h: float, depth: float = 0.08) -> None:
    usable = width - 2.0 * margin_x
    bay = usable / columns
    for floor in range(floors):
        cy = y0 + floor * floor_height + floor_height * 0.52
        for column in range(columns):
            cx = -usable / 2.0 + bay * (column + 0.5)
            builder.add_box_center((cx, cy, z), (bay * 0.58, window_h, depth))


def add_star(builder: MeshBuilder, center: tuple[float, float, float], radius: float,
             depth: float = 0.08) -> None:
    cx, cy, cz = center
    polygon: list[tuple[float, float]] = []
    for index in range(10):
        current = radius if index % 2 == 0 else radius * 0.42
        angle = -math.pi / 2.0 + index * math.pi / 5.0
        polygon.append((cx + current * math.cos(angle), cy + current * math.sin(angle)))
    builder.add_polygon_prism_z(polygon, cz - depth / 2.0, cz + depth / 2.0)


def add_arch_polygon(builder: MeshBuilder, center_x: float, base_y: float, width: float,
                     vertical_height: float, z_front: float, z_back: float,
                     segments: int = 16) -> None:
    radius = width / 2.0
    polygon = [(center_x - radius, base_y), (center_x + radius, base_y),
               (center_x + radius, base_y + vertical_height)]
    for index in range(segments + 1):
        angle = index * math.pi / segments
        polygon.append((
            center_x + radius * math.cos(angle),
            base_y + vertical_height + radius * math.sin(angle),
        ))
    polygon.append((center_x - radius, base_y + vertical_height))
    builder.add_polygon_prism_z(polygon, z_front, z_back)


def add_front_window(
    glass: MeshBuilder,
    frame: MeshBuilder,
    center: tuple[float, float, float],
    size: tuple[float, float],
    frame_width: float,
    mullions: int = 1,
    transoms: int = 1,
    depth: float = 0.08,
) -> None:
    """Add an inset front window with a readable frame and pane divisions."""
    cx, cy, z = center
    width, height = size
    glass.add_box_center((cx, cy, z), (width, height, depth * 0.55))
    front_z = z - depth * 0.48
    for x in (cx - width / 2.0, cx + width / 2.0):
        frame.add_box_center((x, cy, front_z), (frame_width, height + frame_width, depth))
    for y in (cy - height / 2.0, cy + height / 2.0):
        frame.add_box_center((cx, y, front_z), (width + frame_width, frame_width, depth))
    for index in range(1, mullions + 1):
        x = cx - width / 2.0 + width * index / (mullions + 1)
        frame.add_box_center((x, cy, front_z), (frame_width * 0.70, height, depth * 0.90))
    for index in range(1, transoms + 1):
        y = cy - height / 2.0 + height * index / (transoms + 1)
        frame.add_box_center((cx, y, front_z), (width, frame_width * 0.70, depth * 0.90))


def add_arch_window(
    glass: MeshBuilder,
    frame: MeshBuilder,
    center_x: float,
    base_y: float,
    width: float,
    straight_height: float,
    z: float,
    frame_width: float = 0.07,
    segments: int = 8,
) -> None:
    """Front window with a shallow semicircular head and divided panes."""
    radius = width / 2.0
    add_arch_polygon(
        glass,
        center_x,
        base_y,
        width,
        straight_height,
        z + 0.03,
        z + 0.08,
        segments,
    )
    top_y = base_y + straight_height
    frame.add_box_center(
        (center_x - radius, base_y + straight_height / 2.0, z),
        (frame_width, straight_height, 0.10),
    )
    frame.add_box_center(
        (center_x + radius, base_y + straight_height / 2.0, z),
        (frame_width, straight_height, 0.10),
    )
    frame.add_box_center((center_x, base_y, z), (width, frame_width, 0.10))
    for index in range(segments):
        a0 = math.pi * index / segments
        a1 = math.pi * (index + 1) / segments
        frame.add_tube(
            (
                center_x + radius * math.cos(a0),
                top_y + radius * math.sin(a0),
                z,
            ),
            (
                center_x + radius * math.cos(a1),
                top_y + radius * math.sin(a1),
                z,
            ),
            frame_width * 0.48,
            6,
        )
    frame.add_box_center(
        (center_x, base_y + straight_height * 0.52, z - 0.01),
        (frame_width * 0.65, straight_height * 1.03, 0.09),
    )
    frame.add_box_center(
        (center_x, top_y, z - 0.01),
        (width, frame_width * 0.62, 0.09),
    )


def add_smooth_uv_shape(
    builder: MeshBuilder,
    point_at,
    segments: int,
    rings: int,
) -> None:
    """Append a smooth-normal closed UV surface generated by ``point_at``.

    The lightweight writer normally uses flat primitives.  Character close-ups
    need continuous vertex normals, so this path keeps the authored geometry in
    the same GLB while avoiding the faceted mannequin look.
    """
    points: list[tuple[float, float, float]] = []
    texcoords: list[tuple[float, float]] = []
    for ring in range(rings + 1):
        phi = -math.pi / 2.0 + math.pi * ring / rings
        for segment in range(segments + 1):
            theta = 2.0 * math.pi * segment / segments
            points.append(point_at(phi, theta))
            texcoords.append((segment / segments, ring / rings))

    columns = segments + 1
    triangles: list[tuple[int, int, int]] = []
    for ring in range(rings):
        for segment in range(segments):
            a = ring * columns + segment
            b = a + 1
            d = (ring + 1) * columns + segment
            c = d + 1
            triangles.extend(((a, d, c), (a, c, b)))

    accumulated = [[0.0, 0.0, 0.0] for _ in points]
    for a, b, c in triangles:
        pa, pb, pc = points[a], points[b], points[c]
        ab = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2])
        ac = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
        normal = (
            ab[1] * ac[2] - ab[2] * ac[1],
            ab[2] * ac[0] - ab[0] * ac[2],
            ab[0] * ac[1] - ab[1] * ac[0],
        )
        for index in (a, b, c):
            accumulated[index][0] += normal[0]
            accumulated[index][1] += normal[1]
            accumulated[index][2] += normal[2]

    normals = []
    for normal in accumulated:
        length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
        if length < 1e-12:
            normals.append((0.0, 1.0, 0.0))
        else:
            normals.append((normal[0] / length, normal[1] / length, normal[2] / length))

    offset = len(builder.positions)
    builder.positions.extend(points)
    builder.normals.extend(normals)
    builder.texcoords.extend(texcoords)
    builder.indices.extend(offset + index for triangle in triangles for index in triangle)


def add_smooth_ellipsoid(
    builder: MeshBuilder,
    center: tuple[float, float, float],
    radii: tuple[float, float, float],
    segments: int,
    rings: int,
    yaw_degrees: float = 0.0,
    pitch_degrees: float = 0.0,
) -> None:
    cx, cy, cz = center
    rx, ry, rz = radii
    yaw = math.radians(yaw_degrees)
    pitch = math.radians(pitch_degrees)
    cyaw, syaw = math.cos(yaw), math.sin(yaw)
    cpitch, spitch = math.cos(pitch), math.sin(pitch)

    def point_at(phi: float, theta: float) -> tuple[float, float, float]:
        cp = math.cos(phi)
        x = rx * cp * math.cos(theta)
        y = ry * math.sin(phi)
        z = rz * cp * math.sin(theta)
        y, z = cpitch * y - spitch * z, spitch * y + cpitch * z
        x, z = cyaw * x + syaw * z, -syaw * x + cyaw * z
        return (cx + x, cy + y, cz + z)

    add_smooth_uv_shape(builder, point_at, segments, rings)


def add_smooth_limb(
    builder: MeshBuilder,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    start_radius: float,
    end_radius: float,
    segments: int = 32,
    rings: int = 10,
) -> None:
    """Append a smoothly shaded, gently tapered sleeve or limb segment."""
    axis = tuple(end[index] - start[index] for index in range(3))
    length = math.sqrt(sum(value * value for value in axis))
    if length < 1e-9:
        return
    direction = tuple(value / length for value in axis)
    reference = (0.0, 1.0, 0.0) if abs(direction[1]) < 0.90 else (1.0, 0.0, 0.0)
    basis_u = (
        direction[1] * reference[2] - direction[2] * reference[1],
        direction[2] * reference[0] - direction[0] * reference[2],
        direction[0] * reference[1] - direction[1] * reference[0],
    )
    basis_length = math.sqrt(sum(value * value for value in basis_u))
    basis_u = tuple(value / basis_length for value in basis_u)
    basis_v = (
        direction[1] * basis_u[2] - direction[2] * basis_u[1],
        direction[2] * basis_u[0] - direction[0] * basis_u[2],
        direction[0] * basis_u[1] - direction[1] * basis_u[0],
    )

    offset = len(builder.positions)
    for ring in range(rings + 1):
        t = ring / rings
        centre = tuple(start[index] + axis[index] * t for index in range(3))
        radius = (1.0 - t) * start_radius + t * end_radius
        radius *= 1.0 + 0.055 * math.sin(math.pi * t)
        for segment in range(segments + 1):
            angle = 2.0 * math.pi * segment / segments
            radial = tuple(
                math.cos(angle) * basis_u[index] + math.sin(angle) * basis_v[index]
                for index in range(3)
            )
            builder.positions.append(tuple(centre[index] + radius * radial[index] for index in range(3)))
            builder.normals.append(radial)
            builder.texcoords.append((segment / segments, t))
    columns = segments + 1
    for ring in range(rings):
        for segment in range(segments):
            a = offset + ring * columns + segment
            b = a + 1
            d = offset + (ring + 1) * columns + segment
            c = d + 1
            builder.indices.extend((a, b, c, a, c, d))


def add_sculpted_head(
    builder: MeshBuilder,
    center: tuple[float, float, float],
    radii: tuple[float, float, float],
    yaw_degrees: float,
    pitch_degrees: float,
    segments: int,
    rings: int,
) -> None:
    """Organic female head with photo-guided jaw, brow, nose, cheeks and lips."""
    cx, cy, cz = center
    rx, ry, rz = radii
    yaw = math.radians(yaw_degrees)
    pitch = math.radians(pitch_degrees)
    cyaw, syaw = math.cos(yaw), math.sin(yaw)
    cpitch, spitch = math.cos(pitch), math.sin(pitch)

    def gaussian(x: float, y: float, gx: float, gy: float, sx: float, sy: float) -> float:
        return math.exp(-((x - gx) / sx) ** 2 - ((y - gy) / sy) ** 2)

    def point_at(phi: float, theta: float) -> tuple[float, float, float]:
        cp = math.cos(phi)
        x = rx * cp * math.cos(theta)
        y = ry * math.sin(phi)
        z = rz * cp * math.sin(theta)
        yn = y / ry
        jaw = max(0.0, min(1.0, (-yn - 0.08) / 0.78))
        x *= 1.0 - 0.27 * jaw ** 1.35
        xn = x / rx
        front = max(0.0, -math.sin(theta)) ** 5
        bridge = 0.022 * gaussian(xn, yn, 0.0, 0.17, 0.16, 0.34)
        nose = 0.052 * gaussian(xn, yn, 0.0, -0.01, 0.105, 0.19)
        brow = 0.012 * (
            gaussian(xn, yn, -0.30, 0.19, 0.22, 0.12)
            + gaussian(xn, yn, 0.30, 0.19, 0.22, 0.12)
        )
        eye_socket = 0.012 * (
            gaussian(xn, yn, -0.31, 0.09, 0.17, 0.10)
            + gaussian(xn, yn, 0.31, 0.09, 0.17, 0.10)
        )
        cheeks = 0.010 * (
            gaussian(xn, yn, -0.43, -0.05, 0.25, 0.25)
            + gaussian(xn, yn, 0.43, -0.05, 0.25, 0.25)
        )
        lips = 0.013 * gaussian(xn, yn, 0.0, -0.34, 0.30, 0.075)
        chin = 0.012 * gaussian(xn, yn, 0.0, -0.58, 0.28, 0.18)
        z -= front * (bridge + nose + brow + cheeks + lips + chin - eye_socket)
        y, z = cpitch * y - spitch * z, spitch * y + cpitch * z
        x, z = cyaw * x + syaw * z, -syaw * x + cyaw * z
        return (cx + x, cy + y, cz + z)

    add_smooth_uv_shape(builder, point_at, segments, rings)


def add_arc_band_panels(
    builder: MeshBuilder,
    center: tuple[float, float],
    radii: tuple[float, float],
    y: float,
    height: float,
    start_degrees: float,
    end_degrees: float,
    segments: int,
    thickness: float,
    gap_ratio: float = 0.92,
) -> None:
    """Approximate a curved façade band with tangent-aligned flat panels."""
    cx, cz = center
    radius_x, radius_z = radii
    angles = [
        math.radians(start_degrees + (end_degrees - start_degrees) * index / segments)
        for index in range(segments + 1)
    ]
    for a0, a1 in zip(angles[:-1], angles[1:]):
        mid = (a0 + a1) / 2.0
        p0 = (cx + radius_x * math.cos(a0), cz + radius_z * math.sin(a0))
        p1 = (cx + radius_x * math.cos(a1), cz + radius_z * math.sin(a1))
        px = cx + radius_x * math.cos(mid)
        pz = cz + radius_z * math.sin(mid)
        chord = math.dist(p0, p1) * gap_ratio
        tangent_x = p1[0] - p0[0]
        tangent_z = p1[1] - p0[1]
        tangent_angle = math.degrees(math.atan2(tangent_z, tangent_x))
        builder.add_box_rot_y(
            (px, y, pz),
            (chord, height, thickness),
            -tangent_angle,
        )


def add_catenary(
    builder: MeshBuilder,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    sag: float,
    radius: float,
    segments: int = 8,
) -> None:
    """Piecewise parabolic cable between two observed connection points."""
    points = []
    for index in range(segments + 1):
        t = index / segments
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t - 4.0 * sag * t * (1.0 - t)
        z = start[2] + (end[2] - start[2]) * t
        points.append((x, y, z))
    for point_a, point_b in zip(points[:-1], points[1:]):
        builder.add_tube(point_a, point_b, radius, 6)


def add_approach_steps(
    builder: MeshBuilder,
    center_x: float,
    outer_z: float,
    count: int,
    width: float,
    run: float,
    rise: float,
    taper: float = 0.0,
) -> None:
    """Build stairs that rise from the outer foreground toward the entrance.

    The authored front faces -Z, so ``outer_z`` is the most negative step and
    every subsequent tread moves in +Z toward the building.  Keeping this in a
    shared helper prevents the old reversed-stair formula from recurring.
    """
    for index in range(count):
        height = rise * (index + 1)
        builder.add_box_center(
            (center_x, height / 2.0, outer_z + index * run),
            (width - index * taper, height, run * 1.08),
        )


def add_balustrade(
    builder: MeshBuilder,
    x0: float,
    x1: float,
    base_y: float,
    top_y: float,
    z: float,
    spacing: float,
    rail_radius: float = 0.035,
) -> None:
    builder.add_tube((x0, base_y, z), (x1, base_y, z), rail_radius, 6)
    builder.add_tube((x0, top_y, z), (x1, top_y, z), rail_radius, 6)
    count = max(2, round((x1 - x0) / spacing))
    for index in range(count + 1):
        x = x0 + (x1 - x0) * index / count
        builder.add_tube((x, base_y, z), (x, top_y, z), rail_radius * 0.72, 6)


def add_roof_tile_ribs(
    builder: MeshBuilder,
    width: float,
    base_y: float,
    depth: float,
    rise: float,
    z_front: float,
    count: int,
    radius: float = 0.035,
) -> None:
    """Visible front roof tile rhythm and ridge-end silhouette."""
    for index in range(count):
        x = -width / 2.0 + width * (index + 0.5) / count
        builder.add_tube(
            (x, base_y, z_front),
            (x, base_y + rise, z_front + depth / 2.0),
            radius,
            10,
        )


def add_brick_courses(
    builder: MeshBuilder,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z: float,
    course_height: float,
    depth: float = 0.025,
) -> None:
    """Low-frequency mortar relief for a front-facing brick wall."""
    rows = max(1, round((y1 - y0) / course_height))
    for row in range(rows + 1):
        y = y0 + (y1 - y0) * row / rows
        builder.add_box_center(((x0 + x1) / 2.0, y, z), (x1 - x0, 0.025, depth))
    brick_width = course_height * 2.5
    for row in range(rows):
        y = y0 + (y1 - y0) * (row + 0.5) / rows
        offset = 0.0 if row % 2 == 0 else brick_width / 2.0
        x = x0 + offset
        while x < x1:
            builder.add_box_center((x, y, z - 0.002), (0.022, course_height * 0.82, depth))
            x += brick_width


def add_humanoid(builder: MeshBuilder, x: float, ground_y: float, z: float, scale: float,
                 pose: str, female: bool = False) -> None:
    """Smooth commemorative figure whose pose and clothing stay source-led."""
    pelvis_y = ground_y + 0.83 * scale
    shoulder_y = ground_y + 1.48 * scale
    head_y = ground_y + 1.80 * scale
    # legs and feet
    for offset in (-0.16, 0.16):
        add_smooth_limb(
            builder,
            (x + offset * scale, pelvis_y, z),
            (x + offset * 0.85 * scale, ground_y + 0.18 * scale, z - 0.01),
            0.115 * scale,
            0.090 * scale,
            24,
            8,
        )
        builder.add_box_center((x + offset * 0.85 * scale, ground_y + 0.08 * scale, z - 0.10 * scale),
                               (0.22 * scale, 0.12 * scale, 0.40 * scale))
    # torso and clothing mass
    add_smooth_ellipsoid(
        builder,
        (x, ground_y + 1.18 * scale, z),
        ((0.38 if not female else 0.32) * scale, 0.48 * scale, 0.22 * scale),
        36,
        18,
    )
    if female:
        skirt = [(x - 0.28 * scale, ground_y + 0.55 * scale),
                 (x + 0.28 * scale, ground_y + 0.55 * scale),
                 (x + 0.20 * scale, ground_y + 1.18 * scale),
                 (x - 0.20 * scale, ground_y + 1.18 * scale)]
        builder.add_polygon_prism_z(skirt, z - 0.18 * scale, z + 0.18 * scale)
    add_sculpted_head(
        builder,
        (x, head_y, z - 0.01 * scale),
        (0.205 * scale, 0.265 * scale, 0.195 * scale),
        -2.5 if x < 0.0 else 2.5,
        -2.0,
        48,
        24,
    )
    builder.add_tube((x, shoulder_y - 0.10 * scale, z), (x, head_y - 0.23 * scale, z),
                     0.105 * scale, 8)
    # Ears, collar and hair masses remain broad enough to survive mobile display.
    for side in (-1.0, 1.0):
        add_smooth_ellipsoid(
            builder,
            (x + side * 0.205 * scale, head_y, z),
            (0.045 * scale, 0.075 * scale, 0.035 * scale),
            20,
            10,
        )
    add_smooth_ellipsoid(
        builder,
        (x, head_y + 0.105 * scale, z + 0.015 * scale),
        (0.205 * scale, 0.155 * scale, 0.190 * scale),
        32,
        16,
    )
    builder.add_tube(
        (x - 0.16 * scale, shoulder_y + 0.02 * scale, z - 0.18 * scale),
        (x, shoulder_y - 0.10 * scale, z - 0.23 * scale),
        0.035 * scale,
        6,
    )
    builder.add_tube(
        (x + 0.16 * scale, shoulder_y + 0.02 * scale, z - 0.18 * scale),
        (x, shoulder_y - 0.10 * scale, z - 0.23 * scale),
        0.035 * scale,
        6,
    )
    left_shoulder = (x - 0.31 * scale, shoulder_y, z)
    right_shoulder = (x + 0.31 * scale, shoulder_y, z)
    if pose == "crossed":
        left_elbow = (x - 0.36 * scale, ground_y + 1.16 * scale, z - 0.02)
        right_elbow = (x + 0.36 * scale, ground_y + 1.16 * scale, z - 0.02)
        left_hand = (x + 0.16 * scale, ground_y + 1.28 * scale, z - 0.24 * scale)
        right_hand = (x - 0.16 * scale, ground_y + 1.22 * scale, z - 0.26 * scale)
    elif pose == "hands_front":
        left_elbow = (x - 0.33 * scale, ground_y + 1.14 * scale, z - 0.05)
        right_elbow = (x + 0.33 * scale, ground_y + 1.14 * scale, z - 0.05)
        left_hand = (x - 0.06 * scale, ground_y + 0.96 * scale, z - 0.25 * scale)
        right_hand = (x + 0.06 * scale, ground_y + 0.96 * scale, z - 0.25 * scale)
    elif pose == "coat":
        left_elbow = (x - 0.38 * scale, ground_y + 1.05 * scale, z)
        right_elbow = (x + 0.37 * scale, ground_y + 1.10 * scale, z)
        left_hand = (x - 0.18 * scale, ground_y + 0.93 * scale, z - 0.22 * scale)
        right_hand = (x + 0.24 * scale, ground_y + 0.84 * scale, z - 0.12 * scale)
        builder.add_box_center((x - 0.25 * scale, ground_y + 0.74 * scale, z + 0.10 * scale),
                               (0.34 * scale, 0.86 * scale, 0.18 * scale))
    else:  # pockets
        left_elbow = (x - 0.36 * scale, ground_y + 1.06 * scale, z)
        right_elbow = (x + 0.36 * scale, ground_y + 1.06 * scale, z)
        left_hand = (x - 0.21 * scale, ground_y + 0.84 * scale, z - 0.10 * scale)
        right_hand = (x + 0.21 * scale, ground_y + 0.84 * scale, z - 0.10 * scale)
    for shoulder, elbow, hand in [
        (left_shoulder, left_elbow, left_hand),
        (right_shoulder, right_elbow, right_hand),
    ]:
        add_smooth_limb(builder, shoulder, elbow, 0.105 * scale, 0.090 * scale, 24, 8)
        add_smooth_limb(builder, elbow, hand, 0.090 * scale, 0.065 * scale, 24, 8)
        add_smooth_ellipsoid(
            builder,
            hand,
            (0.09 * scale, 0.065 * scale, 0.10 * scale),
            28,
            14,
        )
        # Four readable fingers are enough at the intended AR distance; the
        # rear of each hand remains deliberately conservative.
        for finger_index in range(4):
            finger_x = hand[0] + (finger_index - 1.5) * 0.028 * scale
            finger_start = (finger_x, hand[1] - 0.015 * scale, hand[2] - 0.045 * scale)
            finger_end = (
                finger_x + (hand[0] - elbow[0]) * 0.055,
                hand[1] - (0.055 + finger_index * 0.004) * scale,
                hand[2] - (0.10 + finger_index * 0.006) * scale,
            )
            add_smooth_limb(
                builder,
                finger_start,
                finger_end,
                0.014 * scale,
                0.008 * scale,
                14,
                4,
            )


def build_s1_gate(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s1a_pingxi_gate", [
        Material("brick", rgb("#424846"), roughness=0.97),
        Material("wood", rgb("#491716"), roughness=0.84),
        Material("roof", rgb("#33393a"), roughness=0.95),
        Material("stone", rgb("#77756e"), roughness=0.97),
        Material("signage", (1.0, 1.0, 1.0), roughness=0.72, texture_path=textures["gate"]),
    ])
    brick, wood, roof, stone, signage = (model.mesh(name) for name in ("brick", "wood", "roof", "stone", "signage"))
    # One-bay gate with a truly open passage and visible jamb depth.
    opening_half = 1.34
    for x in (-2.04, 2.04):
        brick.add_box_center((x, 2.05, 0.0), (1.38, 4.10, 1.18))
    brick.add_box_center((0.0, 3.74, 0.0), (2.72, 0.72, 1.18))
    # Short wall returns stabilize the silhouette without recreating the courtyard.
    for x in (-3.05, 3.05):
        brick.add_box_center((x, 1.55, 0.17), (0.64, 3.10, 1.00))

    # Thick wine-red timber surround and recessed inner return.
    for x in (-1.48, 1.48):
        wood.add_box_center((x, 1.82, -0.66), (0.31, 3.50, 0.20))
        wood.add_box_center((x * 0.91, 1.82, -0.05), (0.16, 3.48, 1.02))
    wood.add_box_center((0.0, 3.48, -0.66), (3.27, 0.31, 0.20))
    wood.add_box_center((0.0, 3.38, -0.05), (2.90, 0.16, 1.02))

    # Low-frequency brick bond and the stepped corbel courses above the plaque.
    for x0, x1 in ((-2.74, -1.36), (1.36, 2.74)):
        add_brick_courses(stone, x0, x1, 0.22, 3.72, -0.615, 0.24, 0.035)
    # The outer returns and lintel are visible in several front/oblique references.
    # Keep the rear court unarticulated because no controlled image covers it.
    for x0, x1 in ((-3.34, -2.74), (2.74, 3.34)):
        add_brick_courses(stone, x0, x1, 0.20, 3.02, -0.595, 0.24, 0.032)
    add_brick_courses(stone, -1.34, 1.34, 3.48, 4.02, -0.615, 0.22, 0.032)
    for level, (width, y, depth) in enumerate(
        ((5.55, 4.08, 1.34), (5.82, 4.24, 1.48), (6.06, 4.40, 1.62))
    ):
        brick.add_box_center((0.0, y, 0.02), (width, 0.18, depth))
        if level < 2:
            for x in [(-2.55 + index * 0.51) for index in range(11)]:
                brick.add_box_center((x, y + 0.13, -depth / 2.0 - 0.05), (0.24, 0.18, 0.26))

    # Thin grey-tile roof, individual visible tile ribs and low ridge.
    roof.add_gable_roof((0.0, 4.54, 0.02), 6.45, 2.16, 0.68, 0.10)
    add_roof_tile_ribs(roof, 6.20, 4.53, 2.02, 0.62, -1.05, 22, 0.032)
    roof.add_tube((-3.20, 5.23, 0.02), (3.20, 5.23, 0.02), 0.085, 8)
    for x in (-3.18, 3.18):
        roof.add_uv_sphere((x, 5.23, 0.02), (0.13, 0.16, 0.12), 10, 5)

    # Three photographed short timber brackets below the horizontal plaque.
    for x in (-0.92, 0.0, 0.92):
        wood.add_box_center((x, 3.40, -0.86), (0.24, 0.24, 0.36))

    # Stone threshold and the photographed approach: lowest at the street,
    # highest beside the gate.  The previous formula accidentally reversed it.
    stone.add_box_center((0.0, 0.10, -0.05), (2.80, 0.20, 1.22))
    add_approach_steps(stone, 0.0, -2.34, 6, 3.86, 0.28, 0.11, 0.08)
    for index in range(6):
        width = 3.86 - index * 0.08
        z = -2.34 + index * 0.28 - 0.145
        y = 0.11 * (index + 1) + 0.012
        stone.add_box_center((0.0, y, z), (width, 0.024, 0.035))

    # Plaque and couplet boards have real thickness; the atlas supplies only lettering.
    wood.add_box_center((0.0, 3.79, -0.78), (3.72, 0.92, 0.16))
    for x in (-2.17, 2.17):
        wood.add_box_center((x, 1.84, -0.75), (0.72, 3.12, 0.15))
    # plaque and couplets share one atlas/material
    signage.add_textured_quad(
        [(-1.78, 3.39, -0.872), (1.78, 3.39, -0.872), (1.78, 4.19, -0.872), (-1.78, 4.19, -0.872)],
        (0.0, 0.0, 1.0, 0.25),
    )
    signage.add_textured_quad(
        [(-2.50, 0.34, -0.833), (-1.84, 0.34, -0.833), (-1.84, 3.34, -0.833), (-2.50, 3.34, -0.833)],
        (0.625, 0.25, 1.0, 1.0),
    )
    signage.add_textured_quad(
        [(1.84, 0.34, -0.833), (2.50, 0.34, -0.833), (2.50, 3.34, -0.833), (1.84, 3.34, -0.833)],
        (0.0, 0.25, 0.375, 1.0),
    )
    return model, ROOT / "lkivivube_delivery/scenes/S1_pingxi_intelligence_station/model/S1A_pingxi_gate_v003.glb"


def build_s1_statue(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s1b_radio_operator_statue", [
        Material("bronze", rgb("#3b2416"), metallic=0.34, roughness=0.82),
        Material("dark_bronze", rgb("#17100c"), metallic=0.28, roughness=0.86),
        Material("highlight_bronze", rgb("#815027"), metallic=0.42, roughness=0.76),
        Material("aged_patina", rgb("#242a26"), metallic=0.40, roughness=0.82),
    ])
    figure, dark, highlight, patina = (
        model.mesh(name)
        for name in ("bronze", "dark_bronze", "highlight_bronze", "aged_patina")
    )

    # The reference is a three-quarter seated pose, not a frontal symmetric bust.
    body_x = -0.40
    torso = [
        (-0.92, 0.78), (0.06, 0.78), (0.04, 1.42),
        (-0.12, 1.82), (-0.68, 1.88), (-0.94, 1.48),
    ]
    figure.add_polygon_prism_z(torso, -0.31, 0.28)
    add_smooth_ellipsoid(figure, (body_x, 1.58, -0.01), (0.48, 0.38, 0.21), 80, 40)
    for shoulder in ((-0.78, 1.68, -0.01), (-0.06, 1.66, -0.04)):
        add_smooth_ellipsoid(figure, shoulder, (0.205, 0.235, 0.205), 48, 24)
    figure.add_tube((body_x, 1.82, -0.02), (-0.40, 1.98, -0.05), 0.13, 12)

    # Head turns about 28 degrees toward the equipment and tips slightly down.
    head = (-0.40, 2.21, -0.04)
    yaw = math.radians(-28.0)
    pitch = math.radians(-12.0)
    forward = (-math.sin(yaw), 0.0, -math.cos(yaw))
    right = (math.cos(yaw), 0.0, -math.sin(yaw))

    def face_point(lateral: float, vertical: float, depth: float) -> tuple[float, float, float]:
        local_y = math.cos(pitch) * vertical + math.sin(pitch) * depth
        local_z = math.sin(pitch) * vertical - math.cos(pitch) * depth
        return (
            head[0] + math.cos(yaw) * lateral + math.sin(yaw) * local_z,
            head[1] + local_y,
            head[2] - math.sin(yaw) * lateral + math.cos(yaw) * local_z,
        )

    head_yaw = -28.0
    head_pitch = -12.0
    # All three independent photographs show a long, narrow face with a soft
    # jaw—not the former round mannequin head.
    add_sculpted_head(figure, head, (0.202, 0.342, 0.205), head_yaw, head_pitch, 192, 96)
    # Ears, cheek planes, nose, chin and lips give the face a readable profile.
    for lateral in (-0.228, 0.228):
        ear = face_point(lateral, 0.0, 0.0)
        add_smooth_ellipsoid(figure, ear, (0.044, 0.073, 0.032), 24, 12, head_yaw, head_pitch)
    # The sculpted surface carries the bridge and jaw; only subtle accents are
    # layered over it so the face does not revert to a primitive mannequin.
    for lateral in (-0.082, 0.082):
        # Almond-shaped eye with separate upper/lower lids.  The period bronze
        # sculpture shows narrow, focused eyes rather than the former dark bar.
        inner = face_point(lateral - 0.044, 0.047, 0.226)
        upper = face_point(lateral, 0.057, 0.232)
        outer = face_point(lateral + 0.044, 0.045, 0.226)
        lower = face_point(lateral, 0.039, 0.229)
        figure.add_tube(inner, upper, 0.0032, 10)
        figure.add_tube(upper, outer, 0.0032, 10)
        figure.add_tube(inner, lower, 0.0022, 10)
        figure.add_tube(lower, outer, 0.0022, 10)
        add_smooth_ellipsoid(
            dark,
            face_point(lateral, 0.047, 0.233),
            (0.015, 0.0050, 0.0055),
            20,
            10,
            head_yaw,
            head_pitch,
        )
        # Gently arched brow follows the three-quarter reference.
        brow_inner = face_point(lateral - 0.046, 0.100, 0.211)
        brow_peak = face_point(lateral - 0.006, 0.112, 0.216)
        brow_outer = face_point(lateral + 0.050, 0.096, 0.209)
        figure.add_tube(brow_inner, brow_peak, 0.0026, 10)
        figure.add_tube(brow_peak, brow_outer, 0.0024, 10)
    for lateral in (-0.024, 0.024):
        add_smooth_ellipsoid(
            dark,
            face_point(lateral, -0.025, 0.250),
            (0.008, 0.0045, 0.0045),
            12,
            6,
            head_yaw,
            head_pitch,
        )
    # Nose wings and a neutral two-part mouth preserve the continuous profile
    # without reintroducing a cylindrical nose or a single horizontal lip bar.
    for lateral in (-0.044, 0.044):
        highlight.add_tube(
            face_point(lateral * 0.55, -0.018, 0.241),
            face_point(lateral, -0.036, 0.232),
            0.0032,
            10,
        )
    upper_lip_left = face_point(-0.054, -0.109, 0.224)
    upper_lip_mid = face_point(0.0, -0.101, 0.234)
    upper_lip_right = face_point(0.054, -0.109, 0.224)
    lower_lip_mid = face_point(0.0, -0.123, 0.232)
    dark.add_tube(upper_lip_left, upper_lip_mid, 0.0022, 10)
    dark.add_tube(upper_lip_mid, upper_lip_right, 0.0022, 10)
    highlight.add_tube(upper_lip_left, lower_lip_mid, 0.0018, 10)
    highlight.add_tube(lower_lip_mid, upper_lip_right, 0.0018, 10)

    # Swept hair, separated fringe ridges and a long segmented braid.
    add_smooth_ellipsoid(
        dark,
        (head[0] - forward[0] * 0.055, head[1] + 0.105, head[2] - forward[2] * 0.055),
        (0.260, 0.230, 0.220),
        96,
        48,
        head_yaw,
        head_pitch,
    )
    # Raised swept fringe seen clearly in the close reference, separate from the
    # rear scalp mass so the silhouette reads as hair instead of a bald cap.
    add_smooth_ellipsoid(
        dark,
        face_point(0.0, 0.245, 0.040),
        (0.188, 0.060, 0.080),
        56,
        28,
        head_yaw,
        head_pitch,
    )
    # Individual photographed grooves are represented by the smooth raised
    # fringe mass above.  Free-standing strand tubes read as spikes in AR and
    # are intentionally omitted.
    braid_points = []
    for index in range(10):
        t = index / 9.0
        braid_points.append((
            -0.61 - 0.085 * math.sin(math.pi * t) + 0.018 * (-1) ** index,
            2.24 - 0.105 * index,
            0.08 + 0.24 * math.sin(math.pi * t) + 0.012 * index,
        ))
    for index, point in enumerate(braid_points):
        radius = 0.090 - index * 0.0058
        add_smooth_ellipsoid(
            dark,
            point,
            (radius * 1.08, radius * 1.18, radius),
            32,
            16,
            yaw_degrees=-18.0 if index % 2 else 18.0,
        )
        if index:
            dark.add_tube(braid_points[index - 1], point, radius * 0.58, 12)
    for side in (-1.0, 1.0):
        for start, end in zip(braid_points[:-1], braid_points[1:]):
            highlight.add_tube(
                (start[0] + side * 0.025, start[1], start[2] - 0.018),
                (end[0] - side * 0.018, end[1], end[2] - 0.018),
                0.0035,
                8,
            )

    # Large round period headphones, headband and the cable visible against the torso.
    ear_points = [face_point(-0.238, 0.01, 0.0), face_point(0.238, 0.01, 0.0)]
    for lateral, ear in zip((-1.0, 1.0), ear_points):
        p0 = (ear[0] - right[0] * 0.035 * lateral, ear[1], ear[2] - right[2] * 0.035 * lateral)
        p1 = (ear[0] + right[0] * 0.095 * lateral, ear[1], ear[2] + right[2] * 0.095 * lateral)
        dark.add_tube(p0, p1, 0.088, 20)
        patina.add_tube(p0, p1, 0.049, 16)
    band_points = [
        face_point(-0.29 + 0.58 * index / 10.0, 0.09 + 0.23 * math.sin(math.pi * index / 10.0), -0.015)
        for index in range(11)
    ]
    for p0, p1 in zip(band_points[:-1], band_points[1:]):
        dark.add_tube(p0, p1, 0.022, 12)
    add_catenary(dark, ear_points[1], (0.45, 1.10, -0.72), 0.10, 0.015, 10)

    # High standing collar, diagonal overlap and five knot buttons.
    for start, end in [
        ((-0.63, 1.92, -0.25), (-0.40, 1.78, -0.35)),
        ((-0.17, 1.92, -0.25), (-0.40, 1.78, -0.35)),
        ((-0.40, 1.78, -0.35), (-0.15, 1.12, -0.34)),
    ]:
        highlight.add_tube(start, end, 0.028, 7)
    for y in (1.67, 1.53, 1.39, 1.25, 1.12):
        highlight.add_uv_sphere((-0.25, y, -0.37), (0.033, 0.025, 0.025), 9, 4)

    # Broad sleeves bend toward the operating surface; raised seams read as folds.
    shoulders = [(-0.79, 1.69, -0.02), (-0.08, 1.66, -0.05)]
    elbows = [(-0.83, 1.30, -0.38), (0.13, 1.31, -0.31)]
    hands = [(-0.23, 1.02, -1.12), (0.38, 1.02, -1.08)]
    for index, (shoulder, elbow, hand) in enumerate(zip(shoulders, elbows, hands)):
        add_smooth_limb(figure, shoulder, elbow, 0.168, 0.145, 40, 14)
        add_smooth_ellipsoid(figure, elbow, (0.17, 0.15, 0.16), 36, 18)
        add_smooth_limb(figure, elbow, hand, 0.145, 0.102, 40, 14)
        # Three reference-confirmed cloth folds wrap each bent broad sleeve.
        for fold_index, offset in enumerate((-0.065, 0.0, 0.065)):
            dark.add_tube(
                (elbow[0] - 0.11, elbow[1] + 0.035 + offset * 0.22, elbow[2] - 0.10 + offset),
                (elbow[0] + 0.11, elbow[1] - 0.025 - offset * 0.18, elbow[2] - 0.12 - offset),
                0.012 - fold_index * 0.001,
                10,
            )

    def add_hand(center: tuple[float, float, float], direction: tuple[float, float]) -> None:
        cx, cy, cz = center
        dx, dz = direction
        length = math.hypot(dx, dz)
        dx, dz = dx / length, dz / length
        side_x, side_z = -dz, dx
        add_smooth_ellipsoid(highlight, center, (0.130, 0.052, 0.112), 40, 20)
        for finger, finger_length in enumerate((0.145, 0.172, 0.184, 0.160)):
            offset = (finger - 1.5) * 0.037
            start = (
                cx + dx * 0.060 + side_x * offset,
                cy - 0.004,
                cz + dz * 0.060 + side_z * offset,
            )
            joint = (
                start[0] + dx * finger_length * 0.54,
                cy - 0.010 - 0.003 * finger,
                start[2] + dz * finger_length * 0.54,
            )
            end = (
                start[0] + dx * finger_length,
                cy - 0.018 - 0.002 * finger,
                start[2] + dz * finger_length,
            )
            add_smooth_limb(highlight, start, joint, 0.0125, 0.0100, 18, 5)
            add_smooth_limb(highlight, joint, end, 0.0100, 0.0065, 18, 5)
            add_smooth_ellipsoid(highlight, joint, (0.013, 0.009, 0.013), 12, 6)
        thumb_start = (
            cx + dx * 0.010 - side_x * 0.072,
            cy - 0.003,
            cz + dz * 0.010 - side_z * 0.072,
        )
        thumb_end = (
            thumb_start[0] + dx * 0.090 - side_x * 0.045,
            cy - 0.020,
            thumb_start[2] + dz * 0.090 - side_z * 0.045,
        )
        thumb_joint = (
            (thumb_start[0] + thumb_end[0]) / 2.0,
            cy - 0.010,
            (thumb_start[2] + thumb_end[2]) / 2.0,
        )
        add_smooth_limb(highlight, thumb_start, thumb_joint, 0.0145, 0.011, 18, 5)
        add_smooth_limb(highlight, thumb_joint, thumb_end, 0.011, 0.0075, 18, 5)

    add_hand(hands[0], (0.98, 0.10))
    add_hand(hands[1], (0.82, -0.36))

    # The rough timber table is layered but no longer shaped like a display plinth.
    dark.add_box_center((0.0, 0.82, -0.77), (2.30, 0.18, 0.94))
    for cy, width, depth, rotation in (
        (0.66, 2.32, 0.54, -1.2),
        (0.49, 2.22, 0.50, 1.0),
        (0.32, 2.30, 0.48, -0.7),
    ):
        dark.add_box_rot_y((0.0, cy, -0.88), (width, 0.20, depth), rotation)
    for x in (-0.86, 0.86):
        dark.add_box_rot_y((x, 0.25, -0.55), (0.38, 0.50, 0.52), -3.0 if x < 0 else 3.0)
    for x in (-0.92, -0.32, 0.27, 0.90):
        dark.add_uv_sphere((x, 0.56, -1.16), (0.08, 0.045, 0.025), 8, 4)

    # Historic sloped radio box, raised lid seam, handle, terminals and knobs.
    dark.add_rbox_x((0.56, 1.06, -0.72), (0.92, 0.40, 0.58), -7.0)
    highlight.add_rbox_x((0.56, 1.26, -0.72), (0.86, 0.035, 0.52), -7.0)
    for x in (0.20, 0.50, 0.80):
        highlight.add_tube((x, 1.37, -0.92), (x, 1.37, -1.01), 0.042, 9)
        dark.add_uv_sphere((x, 1.37, -1.02), (0.050, 0.035, 0.050), 9, 4)
        patina.add_tube((x, 1.365, -0.92), (x, 1.365, -1.015), 0.017, 10)
    dark.add_tube((0.26, 1.41, -0.57), (0.74, 1.41, -0.57), 0.024, 8)
    dark.add_tube((0.26, 1.34, -0.57), (0.26, 1.41, -0.57), 0.024, 8)
    dark.add_tube((0.74, 1.34, -0.57), (0.74, 1.41, -0.57), 0.024, 8)

    # Telegraph key with base, pivot, lever, knob and two binding posts.
    dark.add_box_center((0.72, 0.94, -1.18), (0.66, 0.10, 0.32))
    dark.add_tube((0.53, 1.01, -1.18), (0.86, 1.14, -1.22), 0.026, 8)
    highlight.add_uv_sphere((0.90, 1.16, -1.23), (0.060, 0.038, 0.058), 10, 5)
    for x in (0.50, 0.86):
        highlight.add_tube((x, 1.00, -1.07), (x, 1.11, -1.07), 0.034, 9)
        dark.add_uv_sphere((x, 1.115, -1.07), (0.045, 0.026, 0.045), 16, 8)
    # Cable terminals and small fastening bolts visible around the operating box.
    for x, z in ((0.18, -0.52), (0.92, -0.52), (0.18, -0.98), (0.92, -0.98)):
        patina.add_cylinder_y((x, 1.285, z), 0.021, 0.030, 12)
    # Paper/operation board.
    highlight.add_rbox_x((0.00, 0.96, -0.76), (0.58, 0.028, 0.38), -4.0)
    return model, ROOT / "lkivivube_delivery/scenes/S1_pingxi_intelligence_station/model/S1B_radio_operator_statue_v003.glb"


def build_s2(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s2a_telegraph_building", [
        Material("wall", rgb("#a96343"), roughness=0.94),
        Material("trim", rgb("#dfd8c8"), roughness=0.88),
        Material("glass", rgb("#3d5358"), metallic=0.04, roughness=0.38),
        Material("dark", rgb("#343332"), metallic=0.24, roughness=0.62),
        Material("stone", rgb("#aaa79e"), roughness=0.94),
    ])
    wall, trim, glass, dark, stone = (model.mesh(name) for name in ("wall", "trim", "glass", "dark", "stone"))
    # Real stepped massing: two wings, a forward central axis and lower stone base.
    wall.add_box_center((-5.45, 3.55, 0.0), (7.90, 7.10, 4.20))
    wall.add_box_center((5.45, 3.55, 0.0), (7.90, 7.10, 4.20))
    wall.add_box_center((0.0, 3.85, -0.18), (3.15, 7.70, 4.35))
    stone.add_box_center((0.0, 0.20, -0.05), (19.15, 0.40, 4.45))
    stone.add_box_center((0.0, 0.14, -2.92), (5.50, 0.28, 1.40))
    add_approach_steps(stone, 0.0, -4.02, 4, 4.80, 0.24, 0.20, 0.22)

    # Lower two levels are denser; upper floors use repeated tall framed windows.
    for side in (-1, 1):
        side_center = side * 5.45
        for floor, y in enumerate((0.80, 1.52, 2.35, 3.20, 4.05, 4.90, 5.75)):
            for column in range(5):
                x = side_center - 3.15 + column * 1.575
                height = 0.50 if floor < 2 else 0.62
                add_front_window(
                    glass,
                    trim,
                    (x, y, -2.14),
                    (0.88, height),
                    0.065,
                    mullions=1,
                    transoms=1 if floor >= 2 else 0,
                    depth=0.09,
                )
        # Narrow top clerestory band.
        for column in range(6):
            x = side_center - 3.28 + column * 1.31
            add_front_window(
                glass,
                trim,
                (x, 6.60, -2.14),
                (0.84, 0.48),
                0.060,
                mullions=1,
                transoms=0,
                depth=0.09,
            )

    # Central entrance and stacked three-bay glazing.
    trim.add_box_center((0.0, 0.92, -2.48), (2.50, 1.65, 0.18))
    glass.add_box_center((0.0, 0.92, -2.59), (2.12, 1.35, 0.06))
    for x in (-0.70, 0.0, 0.70):
        trim.add_box_center((x, 0.92, -2.64), (0.075, 1.35, 0.08))
    for floor, y in enumerate((2.10, 2.94, 3.78, 4.62, 5.46, 6.30)):
        for x in (-0.78, 0.0, 0.78):
            add_front_window(
                glass,
                trim,
                (x, y, -2.40),
                (0.58, 0.60),
                0.055,
                mullions=1,
                transoms=1,
                depth=0.08,
            )

    # Continuous horizontal cornices and roof edge.
    for y, depth in ((1.88, 0.22), (6.98, 0.28), (7.18, 0.20)):
        trim.add_box_center((0.0, y, -2.18 - (depth - 0.20)), (19.20, 0.18, depth))
    for x in (-9.45, -1.72, 1.72, 9.45):
        trim.add_box_center((x, 3.55, -2.16), (0.18, 7.10, 0.18))

    # Clock-tower plinth, red-brown grille and heavy pale corner piers.
    trim.add_box_center((0.0, 7.50, 0.0), (4.70, 0.62, 3.35))
    wall.add_box_center((0.0, 9.30, 0.0), (2.85, 3.45, 2.70))
    dark.add_box_center((0.0, 9.18, -1.39), (2.12, 2.62, 0.10))
    for x in (-1.34, 1.34):
        trim.add_box_center((x, 9.28, -1.42), (0.24, 3.34, 0.22))
    for y in (8.02, 8.55, 9.08, 9.61, 10.14, 10.67):
        trim.add_box_center((0.0, y, -1.47), (2.60, 0.10, 0.14))
    for x in (-0.72, 0.0, 0.72):
        trim.add_box_center((x, 9.20, -1.48), (0.075, 2.58, 0.13))

    # Clock projects in front of the grille.
    trim.add_tube((0.0, 9.52, -1.54), (0.0, 9.52, -1.68), 0.78, 32)
    dark.add_tube((0.0, 9.52, -1.69), (0.0, 9.52, -1.76), 0.64, 32)
    trim.add_tube((0.0, 9.52, -1.77), (0.0, 9.52, -1.83), 0.58, 32)
    # Clock marks and hands.
    for index in range(12):
        angle = math.pi / 2.0 - index * 2.0 * math.pi / 12.0
        x = 0.47 * math.cos(angle)
        y = 9.52 + 0.47 * math.sin(angle)
        dark.add_box_center((x, y, -1.865), (0.052, 0.13, 0.035))
    dark.add_tube((0.0, 9.52, -1.88), (0.0, 9.92, -1.88), 0.032, 7)
    dark.add_tube((0.0, 9.52, -1.89), (0.34, 9.37, -1.89), 0.032, 7)

    # Open multi-column crown, guard rail and antenna.
    trim.add_box_center((0.0, 11.18, 0.0), (3.25, 0.20, 2.90))
    for x in (-1.32, -0.44, 0.44, 1.32):
        for z in (-1.08, 1.08):
            trim.add_tube((x, 11.18, z), (x, 12.08, z), 0.072, 8)
    trim.add_box_center((0.0, 12.10, 0.0), (3.15, 0.18, 2.70))
    for z in (-1.34, 1.34):
        add_balustrade(dark, -1.58, 1.58, 11.30, 11.60, z, 0.40, 0.022)
    dark.add_tube((0.0, 12.18, 0.0), (0.0, 14.80, 0.0), 0.048, 8)

    # Sparse permanent roof rods only.
    for x in (-8.4, -6.0, -3.8, 3.8, 6.0, 8.4):
        dark.add_tube((x, 7.18, 0.80), (x, 8.05, 0.80), 0.022, 6)

    # Oblique independent photographs confirm real side depth and repeated end
    # windows.  These are confined to the two observed wing end walls.
    for side in (-1.0, 1.0):
        x = side * 9.47
        for floor, y in enumerate((0.82, 1.70, 2.58, 3.46, 4.34, 5.22, 6.10)):
            for z in (-1.36, 0.0, 1.36):
                glass.add_box_center((x + side * 0.035, y, z), (0.045, 0.54, 0.82))
                trim.add_box_center((x + side * 0.065, y - 0.30, z), (0.055, 0.055, 0.94))
                trim.add_box_center((x + side * 0.065, y + 0.30, z), (0.055, 0.055, 0.94))
                trim.add_box_center((x + side * 0.065, y, z - 0.47), (0.055, 0.65, 0.055))
                trim.add_box_center((x + side * 0.065, y, z + 0.47), (0.055, 0.65, 0.055))
                if floor >= 2:
                    trim.add_box_center((x + side * 0.070, y, z), (0.060, 0.055, 0.82))
    return model, ROOT / "lkivivube_delivery/scenes/S2_telegraph_building/model/S2A_telegraph_building_v003.glb"


def build_s3_building(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s3a_shortwave_station_building", [
        Material("aged_wall", rgb("#a8a69d"), roughness=0.98),
        Material("faded_trim", rgb("#b8755f"), roughness=0.92),
        Material("old_glass", rgb("#506862"), metallic=0.03, roughness=0.48),
        Material("dark_detail", rgb("#444541"), metallic=0.12, roughness=0.76),
    ])
    wall, trim, glass, detail = (model.mesh(name) for name in ("aged_wall", "faded_trim", "old_glass", "dark_detail"))
    # Asymmetric low wings and the photographed tall blind wall.
    wall.add_box_center((-4.65, 1.25, 0.55), (5.40, 2.50, 3.65))
    wall.add_box_center((4.55, 1.35, 0.48), (5.10, 2.70, 3.80))
    wall.add_box_center((3.25, 5.35, 0.95), (3.15, 10.70, 3.00))
    # Low-frequency aged-brick joints on the blind wall, not a photo texture.
    add_brick_courses(detail, 1.72, 4.78, 0.28, 10.30, -0.59, 0.42, 0.026)

    # Solid polygonal tower base and rear core.
    wall.add_box_center((-1.15, 1.45, 0.12), (4.05, 2.10, 3.10))
    wall.add_box_center((-1.15, 5.25, 0.70), (3.65, 7.50, 2.35))
    tower_center = (-1.15, -0.02)
    tower_radii = (2.10, 1.56)
    # Seven separate glazed floors: tangent panels, projecting slabs and mullions.
    # Eighteen facets preserve the photographed rounded silhouette at close AR
    # range without falsely inventing a perfectly cylindrical curtain wall.
    tower_facets = 18
    for floor in range(7):
        floor_base = 2.18 + floor * 0.91
        add_arc_band_panels(
            glass,
            tower_center,
            tower_radii,
            floor_base + 0.34,
            0.62,
            202,
            338,
            tower_facets,
            0.13,
            0.92,
        )
        add_arc_band_panels(
            trim,
            tower_center,
            (2.25, 1.70),
            floor_base + 0.72,
            0.17,
            198,
            342,
            tower_facets,
            0.30,
            0.97,
        )
        # A thin inner transom reads through the large glass panels.
        add_arc_band_panels(
            detail,
            tower_center,
            (2.13, 1.59),
            floor_base + 0.38,
            0.045,
            202,
            338,
            tower_facets,
            0.16,
            0.86,
        )
    # Vertical mullions at each facet boundary.
    for degrees in [202 + index * (136 / tower_facets) for index in range(tower_facets + 1)]:
        angle = math.radians(degrees)
        x = tower_center[0] + tower_radii[0] * math.cos(angle)
        z = tower_center[1] + tower_radii[1] * math.sin(angle)
        detail.add_tube((x, 2.18, z - 0.02), (x, 8.64, z - 0.02), 0.042, 7)
    # Tower cap is a pale parapet following the same polygonal curve.
    add_arc_band_panels(
        wall,
        tower_center,
        (2.18, 1.62),
        8.87,
        0.42,
        198,
        342,
        tower_facets,
        0.30,
        0.98,
    )

    # Distinct wing windows, entrance canopy and broad observed stairs.
    for x in (-6.10, -5.00, -3.90, 3.75, 4.85, 5.95):
        for y, height in ((0.83, 0.70), (1.78, 0.72)):
            add_front_window(
                glass,
                detail,
                (x, y, -1.31),
                (0.72, height),
                0.052,
                mullions=1,
                transoms=1,
                depth=0.075,
            )
    # A few narrow openings are repeatedly visible on the exposed tall-wall
    # side.  They are not mirrored to the unphotographed rear face.
    for y in (3.10, 5.05, 7.00, 8.95):
        glass.add_box_center((4.835, y, 0.78), (0.045, 0.72, 0.42))
        for dy in (-0.40, 0.40):
            detail.add_box_center((4.865, y + dy, 0.78), (0.055, 0.055, 0.50))
        for dz in (-0.25, 0.25):
            detail.add_box_center((4.865, y, 0.78 + dz), (0.055, 0.82, 0.055))
    trim.add_box_center((3.90, 2.56, -1.55), (3.70, 0.18, 1.10))
    add_approach_steps(wall, 3.90, -3.23, 6, 4.30, 0.24, 0.20, 0.20)
    # Roof-edge coping and a few supported permanent antenna rods.
    trim.add_box_center((-4.70, 2.55, 0.45), (5.55, 0.16, 3.90))
    trim.add_box_center((4.65, 2.74, 0.45), (5.40, 0.16, 4.00))
    for x in (-6.2, 5.8):
        detail.add_tube((x, 2.72, 0.4), (x, 5.15, 0.4), 0.025, 6)
    return model, ROOT / "lkivivube_delivery/scenes/S3_shortwave_station/model/S3A_shortwave_station_building_v003.glb"


def build_s3_antenna(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s3b_shortwave_antenna_array", [
        Material("steel", rgb("#454849"), metallic=0.72, roughness=0.68),
        Material("rust", rgb("#44352e"), metallic=0.55, roughness=0.78),
        Material("cable_primary", rgb("#1f2020"), metallic=0.48, roughness=0.72),
        Material("cable_secondary", rgb("#292827"), metallic=0.42, roughness=0.76),
        Material("insulator", rgb("#171817"), metallic=0.18, roughness=0.66),
    ])
    steel, rust, cable_primary, cable_secondary, insulator = (
        model.mesh(name)
        for name in ("steel", "rust", "cable_primary", "cable_secondary", "insulator")
    )

    # Four tapered legs, fourteen X-braced bays and horizontal ties reproduce the
    # photographed support tower without turning it into a generic power pylon.
    mast_h = 7.30
    mast_levels = 14
    for x in (-0.34, 0.34):
        for z in (-0.34, 0.34):
            steel.add_tube((x, 0.0, z), (x * 0.48, mast_h, z * 0.48), 0.052, 10)
    for level in range(mast_levels):
        y0, y1 = level * mast_h / mast_levels, (level + 1) * mast_h / mast_levels
        width0 = 0.34 - 0.34 * 0.52 * level / mast_levels
        width1 = 0.34 - 0.34 * 0.52 * (level + 1) / mast_levels
        for zsign in (-1, 1):
            steel.add_tube((-width0, y0, zsign * width0), (width1, y1, zsign * width1), 0.032, 8)
            steel.add_tube((width0, y0, zsign * width0), (-width1, y1, zsign * width1), 0.032, 8)
        for xsign in (-1, 1):
            steel.add_tube((xsign * width0, y0, -width0), (xsign * width1, y1, width1), 0.032, 8)
            steel.add_tube((xsign * width0, y0, width0), (xsign * width1, y1, -width1), 0.032, 8)
        # Horizontal rings make the four-legged mast connection readable.
        for y, width in ((y0, width0), (y1, width1)):
            steel.add_tube((-width, y, -width), (width, y, -width), 0.028, 8)
            steel.add_tube((width, y, -width), (width, y, width), 0.028, 8)
            steel.add_tube((width, y, width), (-width, y, width), 0.028, 8)
            steel.add_tube((-width, y, width), (-width, y, -width), 0.028, 8)

    # Bearing stack and offset drive brace visible beside the top of the mast.
    steel.add_cylinder_y((0.0, 6.98, 0.0), 0.40, 0.52, 16)
    rust.add_cylinder_y((0.0, 7.32, 0.0), 0.25, 0.26, 14)
    steel.add_tube((0.18, 6.35, 0.18), (0.88, 7.12, 0.35), 0.055, 7)
    steel.add_tube((0.18, 6.35, -0.18), (0.88, 7.12, -0.35), 0.055, 7)

    # Two opposing collinear pairs form a near-orthogonal plan cross.  The
    # structural angle is locked at 90 degrees; only the whole-array yaw is
    # rotated so the review projection matches the photographed acute/obtuse X.
    hub_y = 6.92
    arm_len = 5.95
    arm_start = 0.30
    structural_axis_angle_degrees = 90.0
    assert abs(structural_axis_angle_degrees - 90.0) <= 5.0
    array_rotation = math.radians(18.0)
    directions = [
        (math.cos(array_rotation + math.radians(index * structural_axis_angle_degrees)),
         math.sin(array_rotation + math.radians(index * structural_axis_angle_degrees)))
        for index in range(4)
    ]
    arm_endpoints = []
    for dx, dz in directions:
        side_x, side_z = -dz, dx
        stations = 16
        for station in range(stations):
            a0 = arm_start + arm_len * station / stations
            a1 = arm_start + arm_len * (station + 1) / stations
            half0 = 0.36 * (1.0 - 0.58 * station / stations)
            half1 = 0.36 * (1.0 - 0.58 * (station + 1) / stations)
            p0a = (dx * a0 + side_x * half0, hub_y, dz * a0 + side_z * half0)
            p0b = (dx * a0 - side_x * half0, hub_y, dz * a0 - side_z * half0)
            p1a = (dx * a1 + side_x * half1, hub_y, dz * a1 + side_z * half1)
            p1b = (dx * a1 - side_x * half1, hub_y, dz * a1 - side_z * half1)
            p0top = (dx * a0, hub_y + 0.40, dz * a0)
            p1top = (dx * a1, hub_y + 0.40, dz * a1)
            rust.add_tube(p0a, p1a, 0.045, 8)
            rust.add_tube(p0b, p1b, 0.045, 8)
            rust.add_tube(p0top, p1top, 0.040, 8)
            rust.add_tube(p0a, p1b, 0.028, 8)
            rust.add_tube(p0b, p1a, 0.028, 8)
            rust.add_tube(p0a, p1top, 0.026, 8)
            rust.add_tube(p0b, p1top, 0.026, 8)
        endpoint = (dx * (arm_start + arm_len), hub_y, dz * (arm_start + arm_len))
        arm_endpoints.append(endpoint)
        # Triangular end frame and the main stay from the central upper node.
        end_half = 0.36 * (1.0 - 0.58)
        enda = (endpoint[0] + side_x * end_half, hub_y, endpoint[2] + side_z * end_half)
        endb = (endpoint[0] - side_x * end_half, hub_y, endpoint[2] - side_z * end_half)
        endtop = (endpoint[0], hub_y + 0.40, endpoint[2])
        rust.add_tube(enda, endb, 0.036, 8)
        rust.add_tube(enda, endtop, 0.034, 8)
        rust.add_tube(endb, endtop, 0.034, 8)
        add_catenary(cable_primary, (0.0, 7.58, 0.0), endtop, 0.10, 0.020, 16)
        insulator.add_uv_sphere(endpoint, (0.09, 0.09, 0.09), 16, 8)

    # Hanging fan wires below each boom.  Their endpoints step downward toward
    # the outer edge instead of forming the old uniform vertical comb.
    for endpoint in arm_endpoints:
        ex, ey, ez = endpoint
        for index in range(12):
            factor = 0.12 + index * 0.071
            top = (ex * factor, ey - 0.02 * index, ez * factor)
            lower_factor = factor + 0.043
            bottom = (
                ex * lower_factor,
                1.95 + 0.30 * index,
                ez * lower_factor,
            )
            target = cable_primary if index in (0, 3, 6, 9, 11) else cable_secondary
            add_catenary(target, top, bottom, 0.08 + 0.010 * index, 0.013, 8)
            if index in (2, 5, 8, 11):
                for bead in range(4):
                    t = 0.42 + bead * 0.055
                    bx = top[0] + (bottom[0] - top[0]) * t
                    by = top[1] + (bottom[1] - top[1]) * t - 0.08
                    bz = top[2] + (bottom[2] - top[2]) * t
                    insulator.add_uv_sphere((bx, by, bz), (0.026, 0.040, 0.026), 12, 6)

    # Twelve nested catenaries in each quadrant establish the four triangular
    # curtain planes seen in the photo and drawing.
    for pair_index in range(4):
        endpoint_a = arm_endpoints[pair_index]
        endpoint_b = arm_endpoints[(pair_index + 1) % 4]
        quadrant_rings = []
        for ring in range(1, 13):
            factor = 0.12 + ring * 0.068
            start = (endpoint_a[0] * factor, hub_y - 0.025 * ring, endpoint_a[2] * factor)
            end = (endpoint_b[0] * factor, hub_y - 0.025 * ring, endpoint_b[2] * factor)
            sag = 0.14 + ring * 0.035
            add_catenary(cable_secondary, start, end, sag, 0.012, 14)
            quadrant_rings.append((start, end, sag))
            if ring in (3, 6, 9, 12):
                midpoint = (
                    (start[0] + end[0]) / 2.0,
                    (start[1] + end[1]) / 2.0 - sag,
                    (start[2] + end[2]) / 2.0,
                )
                for bead in (-0.070, -0.023, 0.023, 0.070):
                    insulator.add_uv_sphere(
                        (midpoint[0], midpoint[1] + bead, midpoint[2]),
                        (0.025, 0.035, 0.025),
                        12,
                        6,
                    )
        # Radial linking wires turn the nested arcs into the observed diamond
        # curtain instead of a set of disconnected parallel catenaries.
        for fraction in (0.20, 0.40, 0.60, 0.80):
            points = []
            for start, end, sag in quadrant_rings:
                points.append((
                    start[0] + (end[0] - start[0]) * fraction,
                    start[1] + (end[1] - start[1]) * fraction
                    - 4.0 * sag * fraction * (1.0 - fraction),
                    start[2] + (end[2] - start[2]) * fraction,
                ))
            for p0, p1 in zip(points[:-1], points[1:]):
                cable_primary.add_tube(p0, p1, 0.010, 7)
    # Structural feet only, not a display disk.
    for x in (-0.52, 0.52):
        for z in (-0.52, 0.52):
            steel.add_box_center((x, 0.08, z), (0.34, 0.16, 0.34))
    return model, ROOT / "lkivivube_delivery/scenes/S3_shortwave_station/model/S3B_shortwave_antenna_array_v003.glb"


def build_s4(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s4a_juyong_pass_tower", [
        Material("brick", rgb("#72736f"), roughness=0.98),
        Material("mortar", rgb("#8b8b84"), roughness=0.98),
        Material("wood", rgb("#7a2925"), roughness=0.84),
        Material("roof", rgb("#4f675c"), roughness=0.90),
        Material("painted_trim", rgb("#33736f"), roughness=0.80),
        Material("signage", (1.0, 1.0, 1.0), roughness=0.74, texture_path=textures["juyong"]),
    ])
    brick, mortar, wood, roof, painted, signage = (
        model.mesh(name)
        for name in ("brick", "mortar", "wood", "roof", "painted_trim", "signage")
    )
    # Wide city platform built around a deep, fully open arched passage.
    platform_width = 11.8
    platform_depth = 5.4
    for x in (-4.12, 4.12):
        brick.add_box_center((x, 2.45, 0.0), (3.56, 4.90, platform_depth))
    brick.add_box_center((0.0, 4.25, 0.0), (4.72, 1.30, platform_depth))
    # Recessed tunnel side and ceiling returns.
    for x in (-1.82, 1.82):
        brick.add_box_center((x, 2.05, 0.30), (0.36, 3.60, 4.70))
    brick.add_box_center((0.0, 4.05, 0.30), (3.30, 0.34, 4.70))

    # Two rings of visible wedge-like arch masonry.
    for ring_radius, block_size, z in ((1.64, (0.36, 0.50, 0.30), -2.78), (1.94, (0.38, 0.52, 0.24), -2.82)):
        for index in range(17):
            angle = math.pi * index / 16.0
            x = ring_radius * math.cos(angle)
            y = 2.42 + ring_radius * math.sin(angle)
            brick.add_box_rot_y(
                (x, y, z),
                block_size,
                -math.degrees(angle) + 90.0,
            )
    # Brick-course relief stays deliberately low frequency.
    for x0, x1 in ((-5.86, -2.00), (2.00, 5.86)):
        add_brick_courses(mortar, x0, x1, 0.25, 4.70, -2.73, 0.30, 0.025)
    add_brick_courses(mortar, -2.0, 2.0, 4.00, 4.74, -2.73, 0.30, 0.025)

    # Battlements with alternating openings and small shooting holes.
    for index in range(13):
        x = -5.40 + index * 0.90
        brick.add_box_center((x, 5.18, -2.18), (0.56, 0.76, 0.78))
        if index % 2 == 0:
            roof.add_box_center((x, 5.03, -2.61), (0.13, 0.22, 0.05))

    # First storey: red wall bays behind columns and the lowest broad eave.
    lower_base = 5.06
    lower_h = 1.38
    wood.add_box_center((0.0, lower_base + lower_h / 2.0, 0.15), (8.25, lower_h, 2.35))
    for column in range(8):
        x = -4.30 + column * (8.60 / 7.0)
        wood.add_tube((x, lower_base, -1.48), (x, lower_base + lower_h, -1.48), 0.10, 10)
    # Dark red doors and lattice divisions.
    for x in (-2.65, -1.32, 0.0, 1.32, 2.65):
        painted.add_box_center((x, lower_base + 0.69, -1.40), (0.74, 1.08, 0.08))
        wood.add_box_center((x, lower_base + 0.69, -1.46), (0.06, 1.08, 0.08))
        wood.add_box_center((x, lower_base + 0.70, -1.46), (0.72, 0.06, 0.08))
    painted.add_box_center((0.0, lower_base + lower_h + 0.05, -1.55), (9.25, 0.20, 0.34))
    # Simplified repeated dougong color blocks.
    for x in [(-4.15 + index * 0.55) for index in range(16)]:
        painted.add_box_center((x, lower_base + lower_h + 0.18, -1.62), (0.30, 0.16, 0.38))
    roof.add_gable_roof((0.0, lower_base + lower_h + 0.18, 0.0), 10.35, 3.85, 0.70, 0.10)
    add_roof_tile_ribs(roof, 9.90, lower_base + lower_h + 0.18, 3.60, 0.64, -1.92, 30, 0.030)
    roof.add_tube((-5.12, 7.24, 0.0), (5.12, 7.24, 0.0), 0.075, 8)

    # Second storey with exterior gallery and red balustrade.
    upper_base = 7.12
    upper_h = 1.34
    wood.add_box_center((0.0, upper_base + upper_h / 2.0, 0.08), (6.65, upper_h, 2.05))
    for column in range(7):
        x = -3.45 + column * 1.15
        wood.add_tube((x, upper_base, -1.28), (x, upper_base + upper_h, -1.28), 0.085, 10)
    for bay in range(6):
        x0 = -3.42 + bay * 1.14 + 0.10
        x1 = x0 + 0.94
        add_balustrade(wood, x0, x1, upper_base + 0.12, upper_base + 0.50, -1.43, 0.18, 0.025)
    painted.add_box_center((0.0, upper_base + upper_h + 0.04, -1.36), (7.70, 0.18, 0.32))
    for x in [(-3.40 + index * 0.52) for index in range(14)]:
        painted.add_box_center((x, upper_base + upper_h + 0.16, -1.43), (0.29, 0.15, 0.34))
    roof.add_gable_roof((0.0, upper_base + upper_h + 0.17, 0.0), 8.50, 3.30, 0.65, 0.10)
    add_roof_tile_ribs(roof, 8.10, upper_base + upper_h + 0.17, 3.05, 0.59, -1.65, 26, 0.028)
    roof.add_tube((-4.18, 9.28, 0.0), (4.18, 9.28, 0.0), 0.070, 8)

    # Third eave sits over a short clerestory band, not a third full storey.
    painted.add_box_center((0.0, 9.18, -0.94), (5.55, 0.52, 1.65))
    for x in (-2.22, -1.11, 0.0, 1.11, 2.22):
        wood.add_tube((x, 8.96, -1.22), (x, 9.52, -1.22), 0.065, 8)
    roof.add_gable_roof((0.0, 9.46, 0.0), 6.75, 2.80, 0.60, 0.10)
    add_roof_tile_ribs(roof, 6.42, 9.46, 2.55, 0.55, -1.40, 22, 0.026)
    roof.add_tube((-3.30, 10.65, 0.0), (3.30, 10.65, 0.0), 0.068, 8)
    # Upturned end silhouettes on all three eaves.
    for x, y, z in (
        (-5.15, 7.08, -1.92), (5.15, 7.08, -1.92),
        (-4.22, 9.12, -1.65), (4.22, 9.12, -1.65),
        (-3.34, 10.49, -1.40), (3.34, 10.49, -1.40),
    ):
        roof.add_tube((x * 0.94, y - 0.10, z + 0.10), (x, y + 0.12, z), 0.050, 7)

    signage.add_textured_quad(
        [(-1.52, 8.04, -1.47), (1.52, 8.04, -1.47), (1.52, 8.62, -1.47), (-1.52, 8.62, -1.47)]
    )
    return model, ROOT / "lkivivube_delivery/scenes/S4_juyong_pass/model/S4A_juyong_pass_tower_v003.glb"


def build_s5(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s5a_memorial_sculpture", [
        Material("stone", rgb("#c7c3b8"), roughness=0.97),
        Material("stone_figures", rgb("#cbc7bc"), roughness=0.96),
        Material("shadow_stone", rgb("#9e9b93"), roughness=0.97),
        Material("bronze", rgb("#4a372b"), metallic=0.64, roughness=0.72),
        Material("plaque", (1.0, 1.0, 1.0), metallic=0.16, roughness=0.68, texture_path=textures["memorial"]),
    ])
    stone, figures, shadow, bronze, plaque = (
        model.mesh(name)
        for name in ("stone", "stone_figures", "shadow_stone", "bronze", "plaque")
    )
    # Five slightly folded panels with an irregular photographed top edge.
    panels = [
        (-4.45, 1.98, 2.15, 3.45, -10.0),
        (-2.35, 2.10, 2.20, 3.72, -5.0),
        (0.0, 2.16, 2.60, 3.84, 0.0),
        (2.50, 2.10, 2.30, 3.72, 5.0),
        (4.65, 1.99, 2.05, 3.47, 10.0),
    ]
    for x, center_y, width, height, rotation in panels:
        stone.add_box_rot_y((x, center_y, 0.30), (width, height, 0.46), rotation)
    stone.add_box_center((0.0, 0.22, 0.28), (11.00, 0.44, 1.38))
    shadow.add_box_center((0.0, 0.48, -0.06), (10.70, 0.24, 0.18))

    # Varied low-relief groups: different heights, directions and arm gestures.
    relief_data = [
        (-4.75, 1.42, 0.76, -1), (-4.18, 1.30, 0.62, 1),
        (-3.58, 1.52, 0.82, 1), (-3.02, 1.38, 0.68, -1),
        (-2.40, 1.58, 0.88, -1), (-1.82, 1.34, 0.64, 1),
        (-1.20, 1.48, 0.78, 1), (-0.58, 1.64, 0.92, -1),
        (0.02, 1.42, 0.70, 1), (0.62, 1.54, 0.84, -1),
        (1.24, 1.34, 0.65, -1), (1.84, 1.60, 0.90, 1),
        (2.44, 1.48, 0.76, 1), (3.05, 1.62, 0.88, -1),
        (3.65, 1.35, 0.66, 1), (4.28, 1.52, 0.80, -1),
        (4.82, 1.38, 0.68, 1),
    ]
    for index, (x, base_y, height, direction) in enumerate(relief_data):
        head_y = base_y + height
        shadow.add_uv_sphere((x, head_y, -0.10), (0.095, 0.12, 0.060), 9, 5)
        shadow.add_tube((x, head_y - 0.11, -0.10), (x + 0.03 * direction, base_y + 0.18, -0.13), 0.075, 7)
        arm_y = base_y + height * 0.55
        reach = 0.24 + 0.04 * (index % 3)
        shadow.add_tube((x, arm_y, -0.12), (x + direction * reach, arm_y + 0.10 * (index % 2), -0.15), 0.034, 6)
        shadow.add_tube((x, arm_y - 0.04, -0.12), (x - direction * reach * 0.70, arm_y - 0.16, -0.15), 0.034, 6)
        if index % 4 == 0:
            # Broad leaf/plant mass seen among the historical groups.
            shadow.add_uv_sphere((x - 0.28, base_y + 0.18, -0.12), (0.20, 0.28, 0.06), 10, 5)

    # Four distinct foreground figures; front-facing detail is intentionally richer.
    positions = [-3.15, -1.05, 1.25, 3.35]
    poses = ["crossed", "hands_front", "coat", "pockets"]
    females = [False, True, False, False]
    scales = [1.23, 1.16, 1.25, 1.20]
    for index, (x, pose, female, scale) in enumerate(zip(positions, poses, females, scales)):
        add_humanoid(figures, x, 0.38, -1.08, scale, pose, female)
        # Irregular photographed stone support beside/behind each lower leg.
        support_x = x + (-0.28 if index % 2 == 0 else 0.28)
        figures.add_uv_sphere((support_x, 0.52, -0.76), (0.34, 0.52, 0.26), 16, 8)
        figures.add_box_center((x, 0.27, -1.00), (0.88, 0.26, 0.70))
        # Clothing-specific front edges.
        if pose == "crossed":
            shadow.add_tube((x - 0.25, 1.68, -1.34), (x + 0.25, 1.52, -1.35), 0.030, 6)
        elif pose == "hands_front":
            shadow.add_tube((x, 1.63, -1.34), (x, 0.92, -1.34), 0.025, 6)
        elif pose == "coat":
            shadow.add_box_center((x - 0.26, 1.00, -0.88), (0.34, 1.00, 0.18))
        else:
            for side in (-1, 1):
                shadow.add_tube((x + side * 0.18, 1.30, -1.31), (x + side * 0.24, 1.02, -1.32), 0.025, 6)

    # Inclined bronze plaque, thick rim, stone support and textured face.
    stone.add_box_center((0.0, 0.15, -3.03), (4.70, 0.30, 1.28))
    bronze.add_rbox_x((0.0, 0.48, -3.10), (4.30, 0.30, 1.86), -27.0)
    bronze.add_rbox_x((0.0, 0.50, -3.11), (4.02, 0.12, 1.55), -27.0)
    plaque.add_textured_quad(
        [(-1.94, 0.14, -3.70), (1.94, 0.14, -3.70), (1.94, 1.00, -2.96), (-1.94, 1.00, -2.96)]
    )
    return model, ROOT / "lkivivube_delivery/scenes/S5_memorial_plaza/model/S5A_memorial_sculpture_v003.glb"


def build_s6(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s6a_zhenfang_lou", [
        Material("brick", rgb("#888986"), roughness=0.97),
        Material("wood", rgb("#722b27"), roughness=0.82),
        Material("roof", rgb("#575b5a"), roughness=0.92),
        Material("glass", rgb("#40515a"), metallic=0.04, roughness=0.42),
        Material("detail", rgb("#b1aaa0"), roughness=0.93),
    ])
    brick, wood, roof, glass, detail = (model.mesh(name) for name in ("brick", "wood", "roof", "glass", "detail"))
    # Rear wall volume is simple; the photographed front is rebuilt bay by bay.
    brick.add_box_center((0.0, 2.42, 0.30), (9.20, 4.84, 3.90))
    bay_centers = (-3.60, -1.80, 0.0, 1.80, 3.60)
    bay_edges = (-4.55, -2.70, -0.90, 0.90, 2.70, 4.55)

    # Square grey-brick piers, including side depth visible in oblique photos.
    for x in bay_edges:
        brick.add_box_center((x, 2.40, -2.12), (0.28, 4.80, 0.62))
    for z in (-0.80, 0.55):
        for x in (-4.55, 4.55):
            brick.add_box_center((x, 2.40, z), (0.28, 4.80, 0.44))
    # The central bay projects beyond the regular veranda line.
    brick.add_box_center((0.0, 2.44, -2.38), (1.92, 4.88, 0.78))

    # Ground-floor arched timber doors/windows in all five bays.
    for index, x in enumerate(bay_centers):
        width = 1.06 if index == 2 else 0.92
        front_z = -2.83 if index == 2 else -2.14
        add_arch_window(glass, wood, x, 0.40, width, 0.95, front_z, 0.075, 16)
        # Lower timber panels below the glazing.
        wood.add_box_center((x, 0.54, front_z - 0.03), (width * 0.86, 0.26, 0.10))
        for mullion in (-0.24, 0.24):
            wood.add_box_center((x + mullion * width, 0.54, front_z - 0.08), (0.035, 0.25, 0.08))

    # Balcony slab and repeated perforated friezes across every bay.
    detail.add_box_center((0.0, 2.42, -2.30), (9.40, 0.22, 0.72))
    for bay_index in range(5):
        x0, x1 = bay_edges[bay_index] + 0.15, bay_edges[bay_index + 1] - 0.15
        for row_y in (2.24, 4.52):
            count = 7
            for slot in range(count):
                x = x0 + (x1 - x0) * (slot + 0.5) / count
                detail.add_box_center((x, row_y, -2.52 if row_y < 3.0 else -2.30), (0.11, 0.16, 0.10))

    # Open second-floor gallery with divided arched doors behind the balustrade.
    for index, x in enumerate(bay_centers):
        width = 1.02 if index == 2 else 0.90
        front_z = -2.80 if index == 2 else -2.12
        add_arch_window(glass, wood, x, 2.78, width, 0.86, front_z, 0.070, 16)
        if index != 2:
            x0 = bay_edges[index] + 0.22
            x1 = bay_edges[index + 1] - 0.22
            add_balustrade(wood, x0, x1, 2.58, 3.18, -2.47, 0.14, 0.030)
    add_balustrade(wood, -0.78, 0.78, 2.58, 3.22, -2.96, 0.13, 0.032)

    # Red/cream cornices and a low-pitched broad roof—no temple-style upturn.
    detail.add_box_center((0.0, 4.66, -2.06), (9.65, 0.22, 0.70))
    wood.add_box_center((0.0, 4.82, -2.03), (9.80, 0.12, 0.72))
    roof.add_gable_roof((0.0, 4.84, 0.20), 10.05, 4.95, 0.72, 0.10)
    roof.add_tube((-4.98, 5.58, 0.20), (4.98, 5.58, 0.20), 0.055, 8)

    # Central double-edged pediment and correctly recessed five-point star.
    outer = [(-1.25, 4.70), (1.25, 4.70), (0.0, 5.90)]
    inner = [(-0.98, 4.85), (0.98, 4.85), (0.0, 5.66)]
    wood.add_polygon_prism_z(outer, -2.98, -2.68)
    detail.add_polygon_prism_z(inner, -3.02, -2.97)
    add_star(wood, (0.0, 5.24, -3.08), 0.23, 0.08)

    # Straight approach stairs aligned to the central entrance and rising inward.
    add_approach_steps(detail, 0.0, -4.82, 7, 2.55, 0.24, 0.20, 0.12)
    # Readable pale mortar on the central and outer pier faces.
    for x0, x1 in ((-4.69, -4.41), (4.41, 4.69)):
        add_brick_courses(detail, x0, x1, 0.12, 4.58, -2.45, 0.22, 0.022)
    # The central projection is closer to the viewer; the old relief sat behind
    # its face and was invisible.  Place it on the observed front plane.
    add_brick_courses(detail, -0.94, 0.94, 0.12, 4.58, -2.79, 0.22, 0.022)
    # Mortar rhythm on the recessed front wall remains behind doors and columns,
    # so it adds material scale without covering the timber openings.
    for x0, x1 in ((-4.38, -2.82), (-2.58, -1.02), (1.02, 2.58), (2.82, 4.38)):
        add_brick_courses(detail, x0, x1, 0.12, 4.45, -1.665, 0.23, 0.018)
    return model, ROOT / "lkivivube_delivery/scenes/S6_zhenfang_lou/model/S6A_zhenfang_lou_v003.glb"


def build_s7(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s7a_telecom_museum", [
        Material("metal", rgb("#c9ced0"), metallic=0.48, roughness=0.55),
        Material("glass", rgb("#2f5962"), metallic=0.08, roughness=0.30),
        Material("red", rgb("#7f2928"), roughness=0.76),
        Material("stone", rgb("#c8c3b6"), roughness=0.94),
        Material("signage", (1.0, 1.0, 1.0), roughness=0.70, texture_path=textures["telecom"]),
    ])
    metal, glass, red, stone, signage = (model.mesh(name) for name in ("metal", "glass", "red", "stone", "signage"))
    # Left three-storey drum: only the photographed front half is curved.
    left_center = (-3.35, 0.30)
    metal.add_box_center((-3.35, 1.75, 1.45), (7.70, 3.50, 3.00))
    for y, height in ((0.55, 0.72), (1.48, 0.48), (2.14, 0.68), (3.00, 0.48), (3.44, 0.38)):
        target = glass if height < 0.55 else metal
        add_arc_band_panels(
            target,
            left_center,
            (4.15, 2.78),
            y,
            height,
            184,
            356,
            36,
            0.20,
            0.94,
        )
    # Clear metal-panel seams across the drum.
    for degrees in [184 + index * (172 / 36) for index in range(37)]:
        angle = math.radians(degrees)
        x = left_center[0] + 4.16 * math.cos(angle)
        z = left_center[1] + 2.79 * math.sin(angle)
        glass.add_tube((x, 0.18, z - 0.02), (x, 3.66, z - 0.02), 0.018, 6)

    # Central recessed, full-height glazed entrance and divided curtain wall.
    metal.add_box_center((0.95, 2.75, 0.82), (4.60, 5.50, 3.80))
    glass.add_box_center((0.55, 2.32, -1.68), (3.05, 4.30, 0.10))
    for x in (-0.82, -0.14, 0.54, 1.22, 1.90):
        metal.add_box_center((x, 2.32, -1.76), (0.055, 4.28, 0.10))
    for y in (0.70, 1.42, 2.14, 2.86, 3.58, 4.30):
        metal.add_box_center((0.54, y, -1.77), (3.02, 0.055, 0.10))
    # Dark revolving-door cylinder and side doors are visible through the lower glazing.
    glass.add_cylinder_y((0.54, 0.72, -1.88), 0.48, 1.38, 16, radius_z=0.34)
    for side in (-1, 1):
        glass.add_box_center((0.54 + side * 0.86, 0.72, -1.88), (0.54, 1.36, 0.08))

    # Broad thin canopy and two deep-red inscription columns.
    metal.add_box_center((0.60, 4.66, -2.34), (5.65, 0.28, 1.55))
    metal.add_box_center((0.60, 4.48, -2.18), (5.40, 0.14, 1.30))
    for x in (-0.55, 1.75):
        red.add_tube((x, 0.12, -2.03), (x, 4.48, -2.03), 0.18, 14)
        # Narrow gold-colored inscription strokes are represented by raised signage-colored bars.
        for y in (1.20, 1.72, 2.24, 2.76, 3.28):
            stone.add_box_center((x, y, -2.215), (0.07, 0.26, 0.035))

    # Right low rounded volume, again only a front arc rather than a black disk.
    right_center = (4.55, 0.60)
    metal.add_box_center((4.55, 1.50, 1.35), (4.10, 3.00, 2.80))
    for y, height in ((0.55, 0.88), (1.72, 0.48), (2.42, 0.92)):
        target = glass if height < 0.60 else metal
        add_arc_band_panels(
            target,
            right_center,
            (2.18, 2.06),
            y,
            height,
            186,
            354,
            24,
            0.18,
            0.94,
        )

    # Tall silver tower and segmented convex blue-green vertical glazing.
    metal.add_box_center((2.60, 7.10, 1.30), (3.20, 8.95, 3.10))
    for segment in range(12):
        y = 3.18 + segment * 0.62
        add_arc_band_panels(
            glass,
            (2.60, -0.32),
            (0.38, 0.18),
            y,
            0.52,
            190,
            350,
            10,
            0.10,
            0.90,
        )
    # Tower metal-panel seams.
    for x in (1.15, 1.85, 2.60, 3.35, 4.05):
        glass.add_box_center((x, 7.10, -0.27), (0.018, 8.70, 0.025))
    for y in (3.2, 4.7, 6.2, 7.7, 9.2, 10.7):
        glass.add_box_center((2.60, y, -0.27), (3.00, 0.018, 0.025))

    # Stepped rear wing with rounded transition and real horizontal window bands.
    for index, (x, y, width, height) in enumerate(
        ((5.35, 3.40, 4.40, 4.80), (5.05, 5.55, 3.80, 2.50), (4.72, 7.20, 3.10, 1.40))
    ):
        metal.add_box_center((x, y, 2.18 + index * 0.18), (width, height, 3.20))
    for y in (2.35, 3.35, 4.35, 5.55, 6.35, 7.18):
        glass.add_box_center((5.10, y, 0.52), (3.90 if y < 5.0 else 3.05, 0.34, 0.10))
        for x in (-1.20, -0.40, 0.40, 1.20):
            metal.add_box_center((5.10 + x, y, 0.46), (0.04, 0.34, 0.10))

    # Permanent relief wall with varied running/communication silhouettes.
    stone.add_box_center((-5.25, 0.88, -3.05), (4.45, 1.76, 0.34))
    for index in range(9):
        x = -6.95 + index * 0.43
        head_y = 1.10 + (index % 3) * 0.12
        stone.add_uv_sphere((x, head_y, -3.25), (0.085, 0.11, 0.055), 8, 4)
        stone.add_tube((x, head_y - 0.10, -3.25), (x + 0.16, 0.62, -3.27), 0.050, 6)
        stone.add_tube((x + 0.05, 0.88, -3.26), (x + 0.28, 0.98 + 0.08 * (index % 2), -3.28), 0.030, 6)
        stone.add_tube((x + 0.13, 0.68, -3.26), (x - 0.02, 0.38, -3.28), 0.035, 6)
        stone.add_tube((x + 0.13, 0.68, -3.26), (x + 0.30, 0.40, -3.28), 0.035, 6)

    # Horizontal name and selected primary-photo tower state.
    signage.add_textured_quad(
        [(-2.12, 4.38, -3.13), (3.34, 4.38, -3.13), (3.34, 4.92, -3.13), (-2.12, 4.92, -3.13)],
        (0.0, 0.0, 1.0, 0.50),
    )
    signage.add_textured_quad(
        [(3.42, 5.28, -0.36), (3.98, 5.28, -0.36), (3.98, 10.30, -0.36), (3.42, 10.30, -0.36)],
        (0.75, 0.50, 1.0, 1.0),
    )
    # Entrance steps remain architectural, not a generic base, and rise inward.
    add_approach_steps(stone, 0.55, -3.24, 4, 3.40, 0.20, 0.16, 0.14)
    return model, ROOT / "lkivivube_delivery/scenes/S7_telecom_museum/model/S7A_telecom_museum_v003.glb"


BUILDERS = [
    build_s1_gate,
    build_s1_statue,
    build_s2,
    build_s3_building,
    build_s3_antenna,
    build_s4,
    build_s5,
    build_s6,
    build_s7,
]


def main() -> int:
    textures = prepare_textures()
    report = []
    for builder in BUILDERS:
        model, output = builder(textures)
        stats = model.export(output)
        stats["relative_file"] = output.relative_to(ROOT).as_posix()
        report.append(stats)
        print(
            f"[BUILT] {stats['asset_id']}  meshes={stats['meshes']} "
            f"tris={stats['triangles']} mats={stats['materials']} "
            f"tex={stats['textures']} size={stats['size_bytes']}B"
        )
    REPORT.write_text(json.dumps({"assets": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
