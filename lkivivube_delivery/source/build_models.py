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
            6,
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
    """Detailed mobile-budget commemorative figure with distinct clothing."""
    pelvis_y = ground_y + 0.83 * scale
    shoulder_y = ground_y + 1.48 * scale
    head_y = ground_y + 1.80 * scale
    # legs and feet
    for offset in (-0.16, 0.16):
        builder.add_tube((x + offset * scale, pelvis_y, z),
                         (x + offset * 0.85 * scale, ground_y + 0.18 * scale, z - 0.01),
                         0.105 * scale, 8)
        builder.add_box_center((x + offset * 0.85 * scale, ground_y + 0.08 * scale, z - 0.10 * scale),
                               (0.22 * scale, 0.12 * scale, 0.40 * scale))
    # torso and clothing mass
    builder.add_uv_sphere((x, ground_y + 1.18 * scale, z),
                          ((0.38 if not female else 0.32) * scale, 0.48 * scale, 0.22 * scale), 16, 7)
    if female:
        skirt = [(x - 0.28 * scale, ground_y + 0.55 * scale),
                 (x + 0.28 * scale, ground_y + 0.55 * scale),
                 (x + 0.20 * scale, ground_y + 1.18 * scale),
                 (x - 0.20 * scale, ground_y + 1.18 * scale)]
        builder.add_polygon_prism_z(skirt, z - 0.18 * scale, z + 0.18 * scale)
    builder.add_uv_sphere((x, head_y, z - 0.01 * scale),
                          (0.21 * scale, 0.26 * scale, 0.20 * scale), 16, 8)
    builder.add_tube((x, shoulder_y - 0.10 * scale, z), (x, head_y - 0.23 * scale, z),
                     0.105 * scale, 8)
    # Nose, ears, brow and collar remain broad enough to survive mobile display.
    builder.add_uv_sphere(
        (x, head_y - 0.01 * scale, z - 0.205 * scale),
        (0.055 * scale, 0.075 * scale, 0.065 * scale),
        8,
        4,
    )
    for side in (-1.0, 1.0):
        builder.add_uv_sphere(
            (x + side * 0.205 * scale, head_y, z),
            (0.045 * scale, 0.075 * scale, 0.035 * scale),
            8,
            4,
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
        builder.add_tube(shoulder, elbow, 0.09 * scale, 8)
        builder.add_tube(elbow, hand, 0.075 * scale, 8)
        builder.add_uv_sphere(hand, (0.09 * scale, 0.065 * scale, 0.10 * scale), 10, 5)


def build_s1_gate(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s1a_pingxi_gate", [
        Material("brick", rgb("#666b69"), roughness=0.97),
        Material("wood", rgb("#6b211f"), roughness=0.82),
        Material("roof", rgb("#4e5455"), roughness=0.94),
        Material("stone", rgb("#a8a69f"), roughness=0.97),
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

    # Stone threshold and short approach steps; no generic display plinth.
    stone.add_box_center((0.0, 0.10, -0.05), (2.80, 0.20, 1.22))
    for index in range(3):
        stone.add_box_center(
            (0.0, 0.08 + index * 0.11, -0.94 - index * 0.26),
            (3.80 - index * 0.22, 0.16 + index * 0.22, 0.52),
        )

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
        Material("bronze", rgb("#8c5a32"), metallic=0.72, roughness=0.62),
        Material("dark_bronze", rgb("#3e3026"), metallic=0.62, roughness=0.70),
        Material("highlight_bronze", rgb("#b07a45"), metallic=0.64, roughness=0.58),
    ])
    figure, equipment, highlight = (model.mesh(name) for name in ("bronze", "dark_bronze", "highlight_bronze"))
    # Seated body facing -Z, with a tapered jacket instead of a single torso blob.
    figure.add_uv_sphere((0.0, 1.48, 0.10), (0.44, 0.58, 0.29), 18, 9)
    figure.add_uv_sphere((0.0, 2.27, -0.15), (0.255, 0.32, 0.24), 18, 9)
    figure.add_tube((0.0, 1.92, 0.0), (0.0, 2.02, -0.07), 0.13, 10)
    # Face planes: nose, ears, brow and chin remain visible at AR scale.
    highlight.add_uv_sphere((0.0, 2.27, -0.37), (0.055, 0.075, 0.065), 9, 5)
    highlight.add_uv_sphere((0.0, 2.10, -0.30), (0.13, 0.07, 0.07), 10, 5)
    for x in (-0.24, 0.24):
        figure.add_uv_sphere((x, 2.27, -0.14), (0.045, 0.075, 0.035), 8, 4)
    # Hair cap and segmented long braid.
    equipment.add_uv_sphere((0.0, 2.38, -0.02), (0.27, 0.20, 0.23), 18, 8)
    braid_points = [
        (0.17, 2.29, 0.08),
        (0.24, 2.05, 0.21),
        (0.28, 1.82, 0.29),
        (0.27, 1.58, 0.33),
        (0.22, 1.34, 0.30),
    ]
    for index, point in enumerate(braid_points):
        radius = 0.090 - index * 0.010
        equipment.add_uv_sphere(point, (radius, radius * 1.18, radius), 10, 5)
        if index:
            equipment.add_tube(braid_points[index - 1], point, radius * 0.68, 8)
    # Collar, diagonal front edge and three visible knot buttons.
    for start, end in [
        ((-0.20, 1.92, -0.24), (0.0, 1.78, -0.33)),
        ((0.20, 1.92, -0.24), (0.0, 1.78, -0.33)),
        ((0.0, 1.78, -0.33), (0.18, 1.28, -0.31)),
    ]:
        highlight.add_tube(start, end, 0.028, 7)
    for y in (1.68, 1.50, 1.32):
        highlight.add_uv_sphere((0.10, y, -0.36), (0.035, 0.026, 0.025), 8, 4)
    # The photograph does not reveal the lower-body pose. Keep the jacket mass
    # behind the desk and do not invent visible legs or shoes.
    figure.add_uv_sphere((0.0, 1.05, 0.04), (0.39, 0.30, 0.27), 16, 8)
    # arms lean towards the desk
    shoulders = [(-0.38, 1.72, -0.02), (0.38, 1.72, -0.02)]
    elbows = [(-0.43, 1.34, -0.32), (0.43, 1.34, -0.32)]
    hands = [(-0.28, 1.13, -0.66), (0.28, 1.13, -0.63)]
    for shoulder, elbow, hand in zip(shoulders, elbows, hands):
        figure.add_tube(shoulder, elbow, 0.145, 10)
        figure.add_tube(elbow, hand, 0.115, 10)
        highlight.add_uv_sphere(hand, (0.12, 0.06, 0.13), 12, 6)
        for finger in range(4):
            fx = hand[0] - 0.075 + finger * 0.05
            highlight.add_tube(
                (fx, hand[1] - 0.01, hand[2] - 0.07),
                (fx + 0.02, hand[1] - 0.015, hand[2] - 0.19),
                0.012,
                6,
            )
    # headphones, headband and cable
    for x in (-0.27, 0.27):
        equipment.add_tube((x, 2.19, -0.13), (x + (0.07 if x > 0 else -0.07), 2.19, -0.13), 0.10, 10)
    for index in range(8):
        a0 = math.pi * index / 8.0
        a1 = math.pi * (index + 1) / 8.0
        p0 = (0.31 * math.cos(a0), 2.29 + 0.33 * math.sin(a0), -0.08)
        p1 = (0.31 * math.cos(a1), 2.29 + 0.33 * math.sin(a1), -0.08)
        equipment.add_tube(p0, p1, 0.035, 7)
    add_catenary(equipment, (0.30, 2.15, -0.08), (0.48, 1.55, -0.32), 0.05, 0.020, 6)
    # Layered rustic exhibition desk seen in the wider photograph.
    for index, (cy, width, depth, rotation) in enumerate(
        (
            (0.91, 1.90, 0.92, -1.5),
            (0.78, 1.82, 0.82, 1.2),
            (0.65, 1.70, 0.72, -0.8),
            (0.52, 1.58, 0.66, 1.0),
            (0.39, 1.48, 0.60, -1.3),
            (0.26, 1.36, 0.56, 0.8),
            (0.13, 1.24, 0.52, -0.6),
        )
    ):
        equipment.add_box_rot_y((0.0, cy, -0.78 + index * 0.02), (width, 0.17, depth), rotation)
    # Historic sloped radio box, seam, handle, terminals and knobs.
    equipment.add_rbox_x((-0.30, 1.16, -0.82), (0.78, 0.42, 0.48), -7.0)
    highlight.add_box_center((-0.30, 1.36, -0.84), (0.74, 0.035, 0.42))
    for x in (-0.53, -0.31, -0.09):
        highlight.add_tube((x, 1.39, -1.04), (x, 1.39, -1.12), 0.047, 9)
    equipment.add_tube((-0.50, 1.43, -0.74), (-0.10, 1.43, -0.74), 0.025, 7)
    # Telegraph key with base, pivot, lever, knob and two binding posts.
    equipment.add_box_center((0.38, 1.02, -1.02), (0.52, 0.10, 0.34))
    equipment.add_tube((0.25, 1.10, -1.02), (0.52, 1.22, -1.08), 0.026, 7)
    highlight.add_uv_sphere((0.55, 1.24, -1.09), (0.055, 0.035, 0.055), 9, 4)
    for x in (0.22, 0.50):
        highlight.add_tube((x, 1.10, -0.90), (x, 1.19, -0.90), 0.035, 8)
    # Paper/operation board.
    highlight.add_box_center((0.02, 1.02, -0.64), (0.66, 0.028, 0.36))
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
    for index in range(4):
        stone.add_box_center(
            (0.0, 0.08 + index * 0.10, -3.30 - index * 0.24),
            (4.80 - index * 0.22, 0.16 + index * 0.20, 0.48),
        )

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
            9,
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
            9,
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
            9,
            0.16,
            0.86,
        )
    # Vertical mullions at each facet boundary.
    for degrees in [202 + index * (136 / 9) for index in range(10)]:
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
        9,
        0.30,
        0.98,
    )

    # Distinct wing windows, entrance canopy and broad observed stairs.
    for x in (-6.10, -5.00, -3.90, 3.75, 4.85, 5.95):
        add_front_window(
            glass,
            detail,
            (x, 1.32, -1.31),
            (0.72, 1.02),
            0.052,
            mullions=1,
            transoms=1,
            depth=0.075,
        )
    trim.add_box_center((3.90, 2.56, -1.55), (3.70, 0.18, 1.10))
    for index in range(6):
        wall.add_box_center(
            (3.90, 0.07 + index * 0.10, -2.03 - index * 0.24),
            (4.30 - index * 0.26, 0.14 + index * 0.20, 0.48),
        )
    # Roof-edge coping and a few supported permanent antenna rods.
    trim.add_box_center((-4.70, 2.55, 0.45), (5.55, 0.16, 3.90))
    trim.add_box_center((4.65, 2.74, 0.45), (5.40, 0.16, 4.00))
    for x in (-6.2, 5.8):
        detail.add_tube((x, 2.72, 0.4), (x, 5.15, 0.4), 0.025, 6)
    return model, ROOT / "lkivivube_delivery/scenes/S3_shortwave_station/model/S3A_shortwave_station_building_v003.glb"


def build_s3_antenna(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s3b_shortwave_antenna_array", [
        Material("steel", rgb("#56595a"), metallic=0.74, roughness=0.64),
        Material("rust", rgb("#6e4630"), metallic=0.58, roughness=0.74),
        Material("cable", rgb("#292827"), metallic=0.52, roughness=0.68),
    ])
    steel, rust, cable = (model.mesh(name) for name in ("steel", "rust", "cable"))
    # four-legged lattice mast
    mast_h = 7.40
    for x in (-0.34, 0.34):
        for z in (-0.34, 0.34):
            steel.add_tube((x, 0.0, z), (x * 0.45, mast_h, z * 0.45), 0.055, 7)
    for level in range(8):
        y0, y1 = level * mast_h / 8.0, (level + 1) * mast_h / 8.0
        width0 = 0.34 - 0.34 * 0.55 * level / 8.0
        width1 = 0.34 - 0.34 * 0.55 * (level + 1) / 8.0
        for zsign in (-1, 1):
            steel.add_tube((-width0, y0, zsign * width0), (width1, y1, zsign * width1), 0.032, 6)
            steel.add_tube((width0, y0, zsign * width0), (-width1, y1, zsign * width1), 0.032, 6)
        for xsign in (-1, 1):
            steel.add_tube((xsign * width0, y0, -width0), (xsign * width1, y1, width1), 0.032, 6)
            steel.add_tube((xsign * width0, y0, width0), (xsign * width1, y1, -width1), 0.032, 6)
        # Horizontal rings make the four-legged mast connection readable.
        for y, width in ((y0, width0), (y1, width1)):
            steel.add_tube((-width, y, -width), (width, y, -width), 0.028, 6)
            steel.add_tube((width, y, -width), (width, y, width), 0.028, 6)
    # four horizontal triangular truss arms
    hub_y = 7.05
    arm_len = 5.80
    directions = [(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)]
    arm_endpoints = []
    for dx, dz in directions:
        side_x, side_z = -dz, dx
        start = 0.25
        stations = 8
        for station in range(stations):
            a0 = start + arm_len * station / stations
            a1 = start + arm_len * (station + 1) / stations
            half0 = 0.34 * (1.0 - 0.55 * station / stations)
            half1 = 0.34 * (1.0 - 0.55 * (station + 1) / stations)
            p0a = (dx * a0 + side_x * half0, hub_y, dz * a0 + side_z * half0)
            p0b = (dx * a0 - side_x * half0, hub_y, dz * a0 - side_z * half0)
            p1a = (dx * a1 + side_x * half1, hub_y, dz * a1 + side_z * half1)
            p1b = (dx * a1 - side_x * half1, hub_y, dz * a1 - side_z * half1)
            p0top = (dx * a0, hub_y + 0.38, dz * a0)
            p1top = (dx * a1, hub_y + 0.38, dz * a1)
            rust.add_tube(p0a, p1a, 0.045, 6)
            rust.add_tube(p0b, p1b, 0.045, 6)
            rust.add_tube(p0top, p1top, 0.040, 6)
            rust.add_tube(p0a, p1b, 0.028, 6)
            rust.add_tube(p0b, p1a, 0.028, 6)
            rust.add_tube(p0a, p1top, 0.026, 6)
            rust.add_tube(p0b, p1top, 0.026, 6)
        endpoint = (dx * (start + arm_len), hub_y, dz * (start + arm_len))
        arm_endpoints.append(endpoint)
        rust.add_tube((0.0, hub_y + 0.35, 0.0), endpoint, 0.035, 6)
        cable.add_uv_sphere(endpoint, (0.09, 0.09, 0.09), 8, 4)
    # representative curtain wires; visible thickness is intentional for mobile
    for endpoint in arm_endpoints:
        ex, ey, ez = endpoint
        for index in range(6):
            factor = 0.20 + index * 0.13
            top = (ex * factor, ey - 0.08 * index, ez * factor)
            bottom = (ex * (0.12 + index * 0.12), 2.10 + 0.28 * index, ez * (0.12 + index * 0.12))
            cable.add_tube(top, bottom, 0.018, 6)
        for level in range(4):
            factor0 = 0.25 + level * 0.16
            factor1 = factor0 + 0.18
            y = 3.20 + level * 0.75
            cable.add_tube((ex * factor0, y, ez * factor0),
                           (ex * factor1, y - 0.10, ez * factor1), 0.015, 6)
    # Curved curtain wires between adjacent arms and representative insulator beads.
    for pair_index in range(4):
        endpoint_a = arm_endpoints[pair_index]
        endpoint_b = arm_endpoints[(pair_index + 1) % 4]
        for ring in range(1, 6):
            factor = 0.24 + ring * 0.13
            start = (endpoint_a[0] * factor, hub_y - 0.05 * ring, endpoint_a[2] * factor)
            end = (endpoint_b[0] * factor, hub_y - 0.05 * ring, endpoint_b[2] * factor)
            add_catenary(cable, start, end, 0.25 + ring * 0.05, 0.014, 8)
            if ring in (2, 4):
                midpoint = (
                    (start[0] + end[0]) / 2.0,
                    (start[1] + end[1]) / 2.0 - (0.25 + ring * 0.05),
                    (start[2] + end[2]) / 2.0,
                )
                for bead in (-0.05, 0.0, 0.05):
                    cable.add_uv_sphere(
                        (midpoint[0], midpoint[1] + bead, midpoint[2]),
                        (0.025, 0.035, 0.025),
                        8,
                        4,
                    )
    # Structural feet only, not a display disk.
    for x in (-0.52, 0.52):
        for z in (-0.52, 0.52):
            steel.add_box_center((x, 0.08, z), (0.34, 0.16, 0.34))
    steel.add_cylinder_y((0.0, 7.15, 0.0), 0.42, 0.58, 16)
    return model, ROOT / "lkivivube_delivery/scenes/S3_shortwave_station/model/S3B_shortwave_antenna_array_v003.glb"


def build_s4(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s4a_juyong_pass_tower", [
        Material("brick", rgb("#72736f"), roughness=0.98),
        Material("wood", rgb("#7a2925"), roughness=0.84),
        Material("roof", rgb("#4f675c"), roughness=0.90),
        Material("painted_trim", rgb("#33736f"), roughness=0.80),
        Material("signage", (1.0, 1.0, 1.0), roughness=0.74, texture_path=textures["juyong"]),
    ])
    brick, wood, roof, painted, signage = (model.mesh(name) for name in ("brick", "wood", "roof", "painted_trim", "signage"))
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
        add_brick_courses(roof, x0, x1, 0.25, 4.70, -2.73, 0.30, 0.025)
    add_brick_courses(roof, -2.0, 2.0, 4.00, 4.74, -2.73, 0.30, 0.025)

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
        Material("shadow_stone", rgb("#9e9b93"), roughness=0.97),
        Material("bronze", rgb("#4a372b"), metallic=0.64, roughness=0.72),
        Material("plaque", (1.0, 1.0, 1.0), metallic=0.16, roughness=0.68, texture_path=textures["memorial"]),
    ])
    stone, shadow, bronze, plaque = (model.mesh(name) for name in ("stone", "shadow_stone", "bronze", "plaque"))
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
        add_humanoid(stone, x, 0.38, -1.08, scale, pose, female)
        # Irregular photographed stone support beside/behind each lower leg.
        support_x = x + (-0.28 if index % 2 == 0 else 0.28)
        stone.add_uv_sphere((support_x, 0.52, -0.76), (0.34, 0.52, 0.26), 10, 5)
        stone.add_box_center((x, 0.27, -1.00), (0.88, 0.26, 0.70))
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
        add_arch_window(glass, wood, x, 0.40, width, 0.95, front_z, 0.075, 10)
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
        add_arch_window(glass, wood, x, 2.78, width, 0.86, front_z, 0.070, 10)
        if index != 2:
            x0 = bay_edges[index] + 0.22
            x1 = bay_edges[index + 1] - 0.22
            add_balustrade(wood, x0, x1, 2.58, 3.18, -2.47, 0.20, 0.033)
    add_balustrade(wood, -0.78, 0.78, 2.58, 3.22, -2.96, 0.18, 0.035)

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

    # Straight approach stairs aligned to the central entrance.
    for index in range(7):
        detail.add_box_center(
            (0.0, 0.07 + index * 0.10, -3.38 - index * 0.24),
            (2.55 - index * 0.14, 0.14 + index * 0.20, 0.48),
        )
    # Readable pale mortar on the central and outer pier faces.
    for x0, x1 in ((-4.69, -4.41), (-0.94, 0.94), (4.41, 4.69)):
        add_brick_courses(detail, x0, x1, 0.12, 4.58, -2.46 if abs(x0) < 1.0 else -2.45, 0.22, 0.022)
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
            18,
            0.20,
            0.94,
        )
    # Clear metal-panel seams across the drum.
    for degrees in [184 + index * (172 / 18) for index in range(19)]:
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
            12,
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
            5,
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
    # Entrance steps remain architectural, not a generic base.
    for index in range(4):
        stone.add_box_center(
            (0.55, 0.07 + index * 0.08, -2.64 - index * 0.20),
            (3.40 - index * 0.14, 0.14 + index * 0.16, 0.40),
        )
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
