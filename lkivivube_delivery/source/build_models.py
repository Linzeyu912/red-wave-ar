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


def add_humanoid(builder: MeshBuilder, x: float, ground_y: float, z: float, scale: float,
                 pose: str, female: bool = False) -> None:
    """Low-poly commemorative statue with pose-specific arm silhouettes."""
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
                          ((0.38 if not female else 0.32) * scale, 0.48 * scale, 0.22 * scale), 12, 5)
    if female:
        skirt = [(x - 0.28 * scale, ground_y + 0.55 * scale),
                 (x + 0.28 * scale, ground_y + 0.55 * scale),
                 (x + 0.20 * scale, ground_y + 1.18 * scale),
                 (x - 0.20 * scale, ground_y + 1.18 * scale)]
        builder.add_polygon_prism_z(skirt, z - 0.18 * scale, z + 0.18 * scale)
    builder.add_uv_sphere((x, head_y, z - 0.01 * scale),
                          (0.21 * scale, 0.26 * scale, 0.20 * scale), 12, 6)
    builder.add_tube((x, shoulder_y - 0.10 * scale, z), (x, head_y - 0.23 * scale, z),
                     0.105 * scale, 8)
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
        builder.add_uv_sphere(hand, (0.09 * scale,) * 3, 8, 4)


def build_s1_gate(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s1a_pingxi_gate", [
        Material("brick", rgb("#777a78"), roughness=0.96),
        Material("wood", rgb("#6e1f1d"), roughness=0.78),
        Material("roof", rgb("#55585a"), roughness=0.92),
        Material("stone", rgb("#aaa8a1"), roughness=0.96),
        Material("signage", (1.0, 1.0, 1.0), roughness=0.72, texture_path=textures["gate"]),
    ])
    brick, wood, roof, stone, signage = (model.mesh(name) for name in ("brick", "wood", "roof", "stone", "signage"))
    # one-bay gate body
    for x in (-2.05, 2.05):
        brick.add_box_center((x, 2.05, 0.0), (1.10, 4.10, 1.05))
    brick.add_box_center((0.0, 3.75, 0.0), (3.10, 0.70, 1.05))
    for x in (-1.48, 1.48):
        wood.add_box_center((x, 1.85, -0.59), (0.30, 3.45, 0.18))
    wood.add_box_center((0.0, 3.50, -0.59), (3.20, 0.30, 0.18))
    for x in (-0.72, 0.72):
        wood.add_box_center((x, 1.68, -0.57), (1.38, 3.16, 0.14))
        for row in range(4):
            for column in range(3):
                roof.add_uv_sphere((x - 0.35 + column * 0.35, 0.76 + row * 0.60, -0.68),
                                   (0.045, 0.045, 0.025), 8, 4)
    roof.add_gable_roof((0.0, 4.25, 0.0), 6.10, 2.15, 0.85, 0.10)
    roof.add_tube((-3.12, 5.12, 0.0), (3.12, 5.12, 0.0), 0.09, 8)
    # simple eave brackets
    for x in [value * 0.55 for value in range(-5, 6)]:
        wood.add_box_center((x, 4.23, -0.57), (0.22, 0.18, 0.42))
    # steps and short base
    for index in range(4):
        stone.add_box_center((0.0, 0.09 + index * 0.14, -1.30 - index * 0.26),
                             (5.10 - index * 0.32, 0.18 + index * 0.28, 0.52))
    # plaque and couplets share one atlas/material
    signage.add_textured_quad(
        [(-1.65, 3.25, -0.72), (1.65, 3.25, -0.72), (1.65, 3.92, -0.72), (-1.65, 3.92, -0.72)],
        (0.0, 0.0, 1.0, 0.25),
    )
    signage.add_textured_quad(
        [(-2.43, 0.45, -0.58), (-1.83, 0.45, -0.58), (-1.83, 3.30, -0.58), (-2.43, 3.30, -0.58)],
        (0.625, 0.25, 1.0, 1.0),
    )
    signage.add_textured_quad(
        [(1.83, 0.45, -0.58), (2.43, 0.45, -0.58), (2.43, 3.30, -0.58), (1.83, 3.30, -0.58)],
        (0.0, 0.25, 0.375, 1.0),
    )
    return model, ROOT / "lkivivube_delivery/scenes/S1_pingxi_intelligence_station/model/S1A_pingxi_gate_v001.glb"


def build_s1_statue(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s1b_radio_operator_statue", [
        Material("bronze", rgb("#8c5a32"), metallic=0.72, roughness=0.62),
        Material("dark_bronze", rgb("#3e3026"), metallic=0.62, roughness=0.70),
        Material("highlight_bronze", rgb("#b07a45"), metallic=0.64, roughness=0.58),
    ])
    figure, equipment, highlight = (model.mesh(name) for name in ("bronze", "dark_bronze", "highlight_bronze"))
    # seated body facing -Z
    figure.add_uv_sphere((0.0, 1.48, 0.10), (0.46, 0.58, 0.30), 14, 7)
    figure.add_uv_sphere((0.0, 2.28, -0.12), (0.28, 0.34, 0.27), 14, 7)
    figure.add_tube((0.0, 1.92, 0.0), (0.0, 2.02, -0.07), 0.13, 10)
    # long braid down the back
    braid_points = [(0.12, 2.25, 0.12), (0.22, 1.95, 0.25), (0.28, 1.62, 0.30), (0.22, 1.30, 0.28)]
    for start, end in zip(braid_points[:-1], braid_points[1:]):
        figure.add_tube(start, end, 0.075, 8)
    # seated legs and shoes
    for x in (-0.20, 0.20):
        figure.add_tube((x, 1.12, 0.12), (x * 1.15, 0.70, -0.15), 0.14, 9)
        figure.add_tube((x * 1.15, 0.70, -0.15), (x * 1.10, 0.18, -0.48), 0.12, 9)
        equipment.add_box_center((x * 1.10, 0.10, -0.62), (0.30, 0.16, 0.50))
    # arms lean towards the desk
    shoulders = [(-0.38, 1.72, -0.02), (0.38, 1.72, -0.02)]
    elbows = [(-0.43, 1.34, -0.32), (0.43, 1.34, -0.32)]
    hands = [(-0.28, 1.13, -0.66), (0.28, 1.13, -0.63)]
    for shoulder, elbow, hand in zip(shoulders, elbows, hands):
        figure.add_tube(shoulder, elbow, 0.11, 9)
        figure.add_tube(elbow, hand, 0.09, 9)
        highlight.add_uv_sphere(hand, (0.105, 0.075, 0.10), 9, 4)
    # headphones, headband and cable
    for x in (-0.27, 0.27):
        equipment.add_tube((x, 2.19, -0.13), (x + (0.07 if x > 0 else -0.07), 2.19, -0.13), 0.10, 10)
    for index in range(8):
        a0 = math.pi * index / 8.0
        a1 = math.pi * (index + 1) / 8.0
        p0 = (0.31 * math.cos(a0), 2.29 + 0.33 * math.sin(a0), -0.08)
        p1 = (0.31 * math.cos(a1), 2.29 + 0.33 * math.sin(a1), -0.08)
        equipment.add_tube(p0, p1, 0.035, 7)
    equipment.add_tube((0.30, 2.15, -0.08), (0.48, 1.55, -0.32), 0.022, 7)
    # low table and historic radio equipment
    equipment.add_box_center((0.0, 1.00, -0.80), (1.65, 0.12, 0.80))
    equipment.add_box_center((-0.34, 1.22, -0.82), (0.62, 0.38, 0.40))
    for x in (-0.48, -0.27, -0.05):
        highlight.add_tube((x, 1.22, -1.04), (x, 1.22, -1.10), 0.055, 9)
    equipment.add_box_center((0.36, 1.09, -0.89), (0.46, 0.10, 0.30))
    equipment.add_tube((0.28, 1.15, -0.88), (0.52, 1.25, -0.88), 0.025, 7)
    highlight.add_box_center((0.0, 1.075, -0.70), (0.56, 0.028, 0.34))
    return model, ROOT / "lkivivube_delivery/scenes/S1_pingxi_intelligence_station/model/S1B_radio_operator_statue_v001.glb"


def build_s2(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s2a_telegraph_building", [
        Material("wall", rgb("#a85f3f"), roughness=0.92),
        Material("trim", rgb("#e6dfcf"), roughness=0.86),
        Material("glass", rgb("#334d59"), metallic=0.05, roughness=0.34),
        Material("dark", rgb("#252a2c"), metallic=0.28, roughness=0.55),
        Material("stone", rgb("#aaa79d"), roughness=0.92),
    ])
    wall, trim, glass, dark, stone = (model.mesh(name) for name in ("wall", "trim", "glass", "dark", "stone"))
    wall.add_box_center((0.0, 3.10, 0.0), (18.0, 6.20, 3.50))
    wall.add_box_center((0.0, 4.40, -1.95), (4.40, 5.60, 0.55))
    # white frame and dark window matrix
    for x in [(-9.0 + index * 1.5) for index in range(13)]:
        trim.add_box_center((x, 3.20, -1.81), (0.13, 5.75, 0.14))
    for y in [0.55 + index * 1.10 for index in range(6)]:
        trim.add_box_center((0.0, y, -1.82), (18.0, 0.12, 0.14))
    add_window_grid(glass, 17.5, 5, 12, 0.15, 1.10, -1.89, 0.25, 0.68, 0.09)
    # centre entrance and tall open corridor
    glass.add_box_center((0.0, 2.85, -2.27), (3.05, 4.50, 0.10))
    for x in (-1.58, 1.58):
        trim.add_box_center((x, 2.85, -2.23), (0.18, 4.90, 0.20))
    stone.add_box_center((0.0, 0.12, -2.90), (6.00, 0.24, 1.50))
    # clock tower and modern crown
    trim.add_box_center((0.0, 8.10, 0.0), (3.30, 4.00, 2.50))
    dark.add_box_center((0.0, 8.15, -1.30), (2.20, 2.35, 0.12))
    trim.add_tube((0.0, 8.15, -1.38), (0.0, 8.15, -1.47), 0.78, 28)
    dark.add_tube((0.0, 8.15, -1.47), (0.0, 8.15, -1.54), 0.62, 28)
    trim.add_tube((0.0, 8.15, -1.55), (0.0, 8.15, -1.60), 0.57, 28)
    # clock marks and hands on the front
    for index in range(12):
        angle = math.pi / 2.0 - index * 2.0 * math.pi / 12.0
        x = 0.48 * math.cos(angle)
        y = 8.15 + 0.48 * math.sin(angle)
        dark.add_box_center((x, y, -1.64), (0.055, 0.13, 0.035))
    dark.add_tube((0.0, 8.15, -1.66), (0.0, 8.55, -1.66), 0.035, 7)
    dark.add_tube((0.0, 8.15, -1.67), (0.34, 8.00, -1.67), 0.035, 7)
    # open crown and antenna
    for x in (-1.35, 1.35):
        for z in (-1.00, 1.00):
            trim.add_tube((x, 10.10, z), (x, 11.05, z), 0.085, 8)
    trim.add_box_center((0.0, 11.05, 0.0), (3.25, 0.18, 2.40))
    dark.add_tube((0.0, 11.14, 0.0), (0.0, 14.00, 0.0), 0.055, 8)
    return model, ROOT / "lkivivube_delivery/scenes/S2_telegraph_building/model/S2A_telegraph_building_v001.glb"


def build_s3_building(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s3a_shortwave_station_building", [
        Material("aged_wall", rgb("#aaa9a0"), roughness=0.97),
        Material("faded_trim", rgb("#c98267"), roughness=0.90),
        Material("old_glass", rgb("#526b65"), metallic=0.04, roughness=0.46),
        Material("dark_detail", rgb("#4a4741"), metallic=0.16, roughness=0.72),
    ])
    wall, trim, glass, detail = (model.mesh(name) for name in ("aged_wall", "faded_trim", "old_glass", "dark_detail"))
    # low wings and tall blind wall
    wall.add_box_center((0.0, 1.05, 0.50), (13.50, 2.10, 3.80))
    wall.add_box_center((3.20, 4.65, 0.65), (3.90, 7.20, 3.40))
    # rounded tower formed by alternating elliptical glass and slab bands
    for floor in range(7):
        glass.add_cylinder_y((-1.10, 2.05 + floor * 0.88, -0.95), 2.25, 0.68, 18, radius_z=1.55)
        trim.add_cylinder_y((-1.10, 2.43 + floor * 0.88, -0.95), 2.35, 0.16, 18, radius_z=1.65)
    wall.add_cylinder_y((-1.10, 1.65, -0.95), 2.30, 0.55, 18, radius_z=1.60)
    # vertical mullions on visible front arc
    for angle in [math.radians(value) for value in range(205, 336, 22)]:
        x = -1.10 + 2.28 * math.cos(angle)
        z = -0.95 + 1.62 * math.sin(angle)
        detail.add_tube((x, 1.80, z - 0.05), (x, 8.55, z - 0.05), 0.045, 7)
    # windows on the side wings and entrance stair
    for x in (-5.50, -4.35, 3.55, 4.70, 5.85):
        glass.add_box_center((x, 1.15, -1.45), (0.78, 0.78, 0.09))
    for index in range(4):
        wall.add_box_center((0.0, 0.08 + index * 0.10, -2.25 - index * 0.25),
                            (4.60 - index * 0.35, 0.16 + index * 0.20, 0.50))
    # optional modern communications pole remains a separate dark-detail mesh
    detail.add_tube((-5.30, 0.0, -0.25), (-5.30, 5.80, -0.25), 0.055, 8)
    for y, radius in ((4.20, 0.48), (5.15, 0.40)):
        segments = 20
        for index in range(segments):
            a0 = 2 * math.pi * index / segments
            a1 = 2 * math.pi * (index + 1) / segments
            detail.add_tube((-5.30 + radius * math.cos(a0), y, -0.25 + radius * math.sin(a0)),
                            (-5.30 + radius * math.cos(a1), y, -0.25 + radius * math.sin(a1)),
                            0.025, 6)
    return model, ROOT / "lkivivube_delivery/scenes/S3_shortwave_station/model/S3A_shortwave_station_building_v001.glb"


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
            rust.add_tube(p0a, p1a, 0.045, 6)
            rust.add_tube(p0b, p1b, 0.045, 6)
            rust.add_tube(p0a, p1b, 0.028, 6)
            rust.add_tube(p0b, p1a, 0.028, 6)
        endpoint = (dx * (start + arm_len), hub_y, dz * (start + arm_len))
        arm_endpoints.append(endpoint)
        rust.add_tube((0.0, hub_y + 0.35, 0.0), endpoint, 0.035, 6)
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
    steel.add_cylinder_y((0.0, 0.12, 0.0), 0.90, 0.24, 16)
    return model, ROOT / "lkivivube_delivery/scenes/S3_shortwave_station/model/S3B_shortwave_antenna_array_v001.glb"


def build_s4(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s4a_juyong_pass_tower", [
        Material("brick", rgb("#777875"), roughness=0.97),
        Material("wood", rgb("#7f2924"), roughness=0.80),
        Material("roof", rgb("#526d62"), roughness=0.88),
        Material("painted_trim", rgb("#397b78"), roughness=0.78),
        Material("signage", (1.0, 1.0, 1.0), roughness=0.74, texture_path=textures["juyong"]),
    ])
    brick, wood, roof, painted, signage = (model.mesh(name) for name in ("brick", "wood", "roof", "painted_trim", "signage"))
    # city gate platform constructed around an arched dark recess
    brick.add_box_center((-3.70, 2.30, 0.0), (4.60, 4.60, 4.00))
    brick.add_box_center((3.70, 2.30, 0.0), (4.60, 4.60, 4.00))
    brick.add_box_center((0.0, 4.00, 0.0), (2.80, 1.20, 4.00))
    # arch ring blocks
    radius = 1.42
    for index in range(13):
        angle = math.pi * index / 12.0
        x = radius * math.cos(angle)
        y = 2.62 + radius * math.sin(angle)
        brick.add_box_rot_y((x, y, -2.08), (0.34, 0.48, 0.25), -math.degrees(angle) + 90.0)
    # battlements
    for x in [(-4.70 + index * 0.94) for index in range(11)]:
        brick.add_box_center((x, 4.95, -1.45), (0.55, 0.70, 0.75))
        brick.add_box_center((x, 4.95, 1.45), (0.55, 0.70, 0.75))
    # three progressively smaller timber levels and eaves
    levels = [(0.0, 5.10, 8.70, 3.00), (0.0, 7.10, 7.50, 2.65), (0.0, 8.85, 6.10, 2.30)]
    for level_index, (cx, base_y, width, depth) in enumerate(levels):
        hall_h = 1.25 if level_index < 2 else 1.05
        wood.add_box_center((cx, base_y + hall_h / 2.0, 0.0), (width * 0.82, hall_h, depth * 0.70))
        columns = 8 - level_index * 2
        for column in range(columns):
            x = -width * 0.39 + column * (width * 0.78 / max(1, columns - 1))
            wood.add_tube((x, base_y, -depth * 0.39), (x, base_y + hall_h, -depth * 0.39), 0.09, 8)
        painted.add_box_center((cx, base_y + hall_h + 0.07, -depth * 0.40), (width * 0.94, 0.18, 0.28))
        roof.add_gable_roof((cx, base_y + hall_h + 0.18, 0.0), width, depth, 0.72 - level_index * 0.08, 0.10)
        roof.add_tube((-width / 2.0, base_y + hall_h + 0.90 - level_index * 0.08, 0.0),
                      (width / 2.0, base_y + hall_h + 0.90 - level_index * 0.08, 0.0), 0.075, 8)
    signage.add_textured_quad(
        [(-1.55, 9.08, -1.68), (1.55, 9.08, -1.68), (1.55, 9.72, -1.68), (-1.55, 9.72, -1.68)]
    )
    return model, ROOT / "lkivivube_delivery/scenes/S4_juyong_pass/model/S4A_juyong_pass_tower_v001.glb"


def build_s5(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s5a_memorial_sculpture", [
        Material("stone", rgb("#c7c3b8"), roughness=0.97),
        Material("shadow_stone", rgb("#9e9b93"), roughness=0.97),
        Material("bronze", rgb("#4a372b"), metallic=0.64, roughness=0.72),
        Material("plaque", (1.0, 1.0, 1.0), metallic=0.16, roughness=0.68, texture_path=textures["memorial"]),
    ])
    stone, shadow, bronze, plaque = (model.mesh(name) for name in ("stone", "shadow_stone", "bronze", "plaque"))
    # folded relief wall
    stone.add_box_rot_y((-3.55, 2.05, 0.15), (3.20, 3.55, 0.42), -7.0)
    stone.add_box_center((0.0, 2.10, 0.35), (4.20, 3.70, 0.42))
    stone.add_box_rot_y((3.55, 2.05, 0.15), (3.20, 3.55, 0.42), 7.0)
    stone.add_box_center((0.0, 0.20, 0.15), (10.20, 0.40, 1.30))
    # simplified low relief silhouettes on wall front
    for index in range(13):
        x = -4.45 + index * 0.74
        y = 1.35 + (index % 3) * 0.20
        shadow.add_uv_sphere((x, y + 0.72, -0.12), (0.12, 0.15, 0.07), 8, 4)
        shadow.add_tube((x, y + 0.60, -0.12), (x + 0.05 * ((index % 2) * 2 - 1), y + 0.18, -0.14), 0.09, 7)
        shadow.add_tube((x, y + 0.48, -0.13), (x - 0.20, y + 0.30, -0.15), 0.045, 6)
        shadow.add_tube((x, y + 0.48, -0.13), (x + 0.20, y + 0.28, -0.15), 0.045, 6)
    # four foreground statues remain separate during source construction, merged by stone material at export
    positions = [-3.0, -1.0, 1.15, 3.25]
    poses = ["crossed", "hands_front", "coat", "pockets"]
    females = [False, True, False, False]
    for x, pose, female in zip(positions, poses, females):
        add_humanoid(stone, x, 0.40, -1.05, 1.18, pose, female)
        stone.add_box_center((x, 0.28, -1.00), (0.90, 0.28, 0.72))
    # inclined bronze plaque and textured face
    bronze.add_rbox_x((0.0, 0.42, -3.05), (4.20, 0.28, 1.80), -27.0)
    plaque.add_textured_quad(
        [(-1.95, 0.07, -3.66), (1.95, 0.07, -3.66), (1.95, 0.94, -2.95), (-1.95, 0.94, -2.95)]
    )
    return model, ROOT / "lkivivube_delivery/scenes/S5_memorial_plaza/model/S5A_memorial_sculpture_v001.glb"


def build_s6(_: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s6a_zhenfang_lou", [
        Material("brick", rgb("#888986"), roughness=0.97),
        Material("wood", rgb("#722b27"), roughness=0.82),
        Material("roof", rgb("#575b5a"), roughness=0.92),
        Material("glass", rgb("#40515a"), metallic=0.04, roughness=0.42),
        Material("detail", rgb("#b1aaa0"), roughness=0.93),
    ])
    brick, wood, roof, glass, detail = (model.mesh(name) for name in ("brick", "wood", "roof", "glass", "detail"))
    brick.add_box_center((0.0, 2.45, 0.25), (9.20, 4.90, 3.80))
    # open veranda columns and balcony
    for x in [(-4.15 + index * 1.18) for index in range(8)]:
        detail.add_tube((x, 0.0, -2.05), (x, 4.75, -2.05), 0.11, 8)
    detail.add_box_center((0.0, 2.48, -2.05), (9.15, 0.18, 0.48))
    for x in [(-4.00 + index * 0.28) for index in range(29)]:
        wood.add_tube((x, 2.55, -2.20), (x, 3.15, -2.20), 0.035, 6)
    wood.add_tube((-4.10, 3.15, -2.20), (4.10, 3.15, -2.20), 0.055, 7)
    # central projecting entrance and stairs
    brick.add_box_center((0.0, 2.45, -2.00), (2.45, 4.90, 1.15))
    for index in range(6):
        detail.add_box_center((0.0, 0.08 + index * 0.11, -3.10 - index * 0.24),
                              (2.80 - index * 0.18, 0.16 + index * 0.22, 0.48))
    # windows and doors
    for floor in range(2):
        y = 1.20 + floor * 2.15
        for x in (-3.35, -2.10, 2.10, 3.35):
            glass.add_box_center((x, y, -1.73), (0.70, 1.18, 0.10))
            wood.add_box_center((x, y, -1.79), (0.82, 1.30, 0.06))
            glass.add_box_center((x, y, -1.84), (0.62, 1.08, 0.03))
        glass.add_box_center((0.0, y, -2.62), (0.92, 1.42, 0.06))
        wood.add_box_center((0.0, y, -2.66), (1.04, 1.54, 0.05))
        glass.add_box_center((0.0, y, -2.70), (0.84, 1.34, 0.03))
    roof.add_gable_roof((0.0, 4.95, 0.20), 10.00, 4.80, 1.05, 0.10)
    # central triangular pediment and star
    pediment = [(-1.38, 4.82), (1.38, 4.82), (0.0, 6.10)]
    wood.add_polygon_prism_z(pediment, -2.72, -2.42)
    add_star(detail, (0.0, 5.30, -2.77), 0.30, 0.08)
    # characteristic perforated trim
    for x in [(-1.15 + index * 0.23) for index in range(11)]:
        detail.add_box_center((x, 4.70, -2.78), (0.11, 0.15, 0.08))
    return model, ROOT / "lkivivube_delivery/scenes/S6_zhenfang_lou/model/S6A_zhenfang_lou_v001.glb"


def build_s7(textures: dict[str, pathlib.Path]) -> tuple[Model, pathlib.Path]:
    model = Model("s7a_telecom_museum", [
        Material("metal", rgb("#c9ced0"), metallic=0.48, roughness=0.55),
        Material("glass", rgb("#2f5962"), metallic=0.08, roughness=0.30),
        Material("red", rgb("#7f2928"), roughness=0.76),
        Material("stone", rgb("#c8c3b6"), roughness=0.94),
        Material("signage", (1.0, 1.0, 1.0), roughness=0.70, texture_path=textures["telecom"]),
    ])
    metal, glass, red, stone, signage = (model.mesh(name) for name in ("metal", "glass", "red", "stone", "signage"))
    # left rounded low volume and horizontal window bands
    metal.add_cylinder_y((-3.40, 1.70, 0.20), 4.25, 3.40, 24, radius_z=2.85)
    for y in (1.35, 2.35):
        glass.add_cylinder_y((-3.40, y, -0.05), 4.32, 0.46, 24, radius_z=2.92)
    # central recessed entrance and canopy
    metal.add_box_center((1.00, 2.65, 0.50), (4.60, 5.30, 3.80))
    glass.add_box_center((0.70, 2.30, -1.62), (3.10, 4.25, 0.12))
    metal.add_box_center((0.70, 4.65, -2.25), (5.20, 0.25, 1.60))
    for x in (-0.45, 1.85):
        red.add_tube((x, 0.0, -1.95), (x, 4.55, -1.95), 0.18, 12)
    # right rounded low body
    metal.add_cylinder_y((4.60, 1.45, 0.55), 2.20, 2.90, 20, radius_z=2.10)
    glass.add_cylinder_y((4.60, 1.80, 0.30), 2.26, 0.46, 20, radius_z=2.16)
    # rear tower with blue-green vertical strip and rounded cap
    metal.add_box_center((2.45, 6.60, 1.25), (3.10, 8.40, 3.00))
    metal.add_cylinder_y((2.45, 10.84, 1.25), 1.55, 0.48, 20, radius_z=1.50)
    glass.add_box_center((2.45, 6.55, -0.31), (0.58, 7.65, 0.12))
    # stepped rear wing
    metal.add_box_center((5.20, 4.10, 2.00), (4.70, 4.60, 3.30))
    for y in (2.95, 4.05, 5.15):
        glass.add_box_center((5.20, y, 0.30), (4.25, 0.42, 0.10))
    # permanent relief wall at front-left
    stone.add_box_center((-5.10, 0.82, -3.10), (4.30, 1.64, 0.32))
    for index in range(7):
        x = -6.65 + index * 0.52
        stone.add_uv_sphere((x, 1.12 + (index % 2) * 0.10, -3.30), (0.10, 0.13, 0.06), 8, 4)
        stone.add_tube((x, 1.03, -3.30), (x + 0.18, 0.60, -3.31), 0.06, 6)
    # horizontal name and selected primary-photo tower state
    signage.add_textured_quad(
        [(-1.80, 4.36, -3.08), (3.20, 4.36, -3.08), (3.20, 4.92, -3.08), (-1.80, 4.92, -3.08)],
        (0.0, 0.0, 1.0, 0.50),
    )
    signage.add_textured_quad(
        [(3.15, 4.10, -0.39), (3.70, 4.10, -0.39), (3.70, 9.55, -0.39), (3.15, 9.55, -0.39)],
        (0.75, 0.50, 1.0, 1.0),
    )
    return model, ROOT / "lkivivube_delivery/scenes/S7_telecom_museum/model/S7A_telecom_museum_v001.glb"


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
