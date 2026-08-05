"""Make nine-grid review sheets for the original triggers and their references.

The review output is deliberately isolated under ``source/.build``.  It never
rewrites the controlled source photographs or hand-drawn trigger files.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / ".build" / "trigger_reference_review"
FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/msyhbd.ttc"),
]


def source(scene: str, filename: str) -> Path:
    return ROOT / "modeling_input" / scene / "local_reference" / "source_folder_20260727" / filename


ASSETS = [
    {
        "asset_id": "S1A",
        "display_name_zh": "平西情报联络站：入口门楼",
        "trigger": source("S1", "trigger_hand_drawn.jpg"),
        "reference": source("S1", "微信图片_20260712203953_1152_5130.jpg"),
    },
    {
        "asset_id": "S1B",
        "display_name_zh": "平西情报联络站：女报务员雕塑",
        "trigger": source("S1", "平西情报联络站2.jpg"),
        "reference": source("S1", "微信图片_20260716203647_1419_5130.jpg"),
    },
    {
        "asset_id": "S2A",
        "display_name_zh": "电报大楼",
        "trigger": source("S2", "trigger_hand_drawn.jpg"),
        "reference": source("S2", "微信图片_20260727183423_918_1.jpg"),
    },
    {
        "asset_id": "S3A",
        "display_name_zh": "短波通信局：通信楼",
        "trigger": source("S3", "trigger_hand_drawn.jpg"),
        "reference": source("S3", "微信图片_20260727183421_916_1.jpg"),
    },
    {
        "asset_id": "S3B",
        "display_name_zh": "短波通信局：天线阵列",
        "trigger": source("S3", "短波通信局2.jpg"),
        "reference": source("S3", "微信图片_20260727183422_917_1.jpg"),
    },
    {
        "asset_id": "S4A",
        "display_name_zh": "居庸关城楼",
        "trigger": source("S4", "trigger_hand_drawn.jpg"),
        "reference": source("S4", "微信图片_20260727183424_919_1.jpg"),
    },
    {
        "asset_id": "S5A",
        "display_name_zh": "西山无名英雄纪念广场",
        "trigger": source("S5", "trigger_hand_drawn.jpg"),
        "reference": source("S5", "18b017b5eb0df80ff4c70fc5991203b5.jpg"),
    },
    {
        "asset_id": "S6A",
        "display_name_zh": "香山镇芳楼",
        "trigger": source("S6", "trigger_hand_drawn.jpg"),
        "reference": source("S6", "a4c5a574525a3f829e286f6eea4b9e08.jpg"),
    },
    {
        "asset_id": "S7A",
        "display_name_zh": "中国电信博物馆",
        "trigger": source("S7", "trigger_hand_drawn.jpg"),
        "reference": source("S7", "d10d05331791c52d672efca4212a9012.png"),
    },
]

GROUND_BY_ID = {
    "S1A": ROOT / "lkivivube_delivery/scenes/S1_pingxi_intelligence_station/kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_ground_texture_v001.png",
    "S1B": ROOT / "lkivivube_delivery/scenes/S1_pingxi_intelligence_station/kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_ground_texture_v001.png",
    "S2A": ROOT / "lkivivube_delivery/scenes/S2_telegraph_building/kivicube_package/S2A_telegraph_building/S2A_telegraph_building_ground_texture_v001.png",
    "S3A": ROOT / "lkivivube_delivery/scenes/S3_shortwave_station/kivicube_package/S3A_shortwave_station_building/S3A_shortwave_station_building_ground_texture_v001.png",
    "S3B": ROOT / "lkivivube_delivery/scenes/S3_shortwave_station/kivicube_package/S3B_shortwave_antenna_array/S3B_shortwave_antenna_array_ground_texture_v001.png",
    "S4A": ROOT / "lkivivube_delivery/scenes/S4_juyong_pass/kivicube_package/S4A_juyong_pass_tower/S4A_juyong_pass_tower_ground_texture_v001.png",
    "S5A": ROOT / "lkivivube_delivery/scenes/S5_memorial_plaza/kivicube_package/S5A_memorial_sculpture/S5A_memorial_sculpture_ground_texture_v001.png",
    "S6A": ROOT / "lkivivube_delivery/scenes/S6_zhenfang_lou/kivicube_package/S6A_zhenfang_lou/S6A_zhenfang_lou_ground_texture_v001.png",
    "S7A": ROOT / "lkivivube_delivery/scenes/S7_telecom_museum/kivicube_package/S7A_telecom_museum/S7A_telecom_museum_ground_texture_v001.png",
}

GRID = 3
CELL_W = 520
CELL_H = 520
HEADER_H = 64
MARGIN = 28
GUTTER = 16


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def image_metadata(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        return {
            "source": path.relative_to(ROOT).as_posix(),
            "width": image.width,
            "height": image.height,
            "aspect_ratio": round(image.width / image.height, 5),
            "bytes": path.stat().st_size,
        }


def make_sheet(kind: str, title: str, output: Path) -> None:
    width = MARGIN * 2 + GRID * CELL_W + (GRID - 1) * GUTTER
    height = MARGIN * 2 + HEADER_H + GRID * CELL_H + (GRID - 1) * GUTTER
    canvas = Image.new("RGB", (width, height), "#f3f0e8")
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, MARGIN), title, fill="#1b1b1b", font=font(30))

    for index, asset in enumerate(ASSETS):
        column = index % GRID
        row = index // GRID
        x = MARGIN + column * (CELL_W + GUTTER)
        y = MARGIN + HEADER_H + row * (CELL_H + GUTTER)
        draw.rounded_rectangle((x, y, x + CELL_W, y + CELL_H), radius=10, fill="white", outline="#beb8ac", width=2)
        source_image = asset[kind]
        with Image.open(source_image) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
            image.thumbnail((CELL_W - 28, CELL_H - 92), Image.Resampling.LANCZOS)
            image_x = x + (CELL_W - image.width) // 2
            image_y = y + 58 + ((CELL_H - 70 - image.height) // 2)
            canvas.paste(image, (image_x, image_y))
        draw.text((x + 16, y + 14), f"{asset['asset_id']}  {asset['display_name_zh']}", fill="#1b1b1b", font=font(20))
        metadata = image_metadata(source_image)
        draw.text(
            (x + 16, y + CELL_H - 28),
            f"{metadata['width']}×{metadata['height']}  {metadata['bytes'] / 1024 / 1024:.2f} MB",
            fill="#66615a",
            font=font(15),
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=92)


def main() -> None:
    for asset in ASSETS:
        asset["ground"] = GROUND_BY_ID[asset["asset_id"]]
    missing = [str(path) for asset in ASSETS for path in (asset["trigger"], asset["reference"]) if not path.exists()]
    missing.extend(str(asset["ground"]) for asset in ASSETS if not asset["ground"].exists())
    if missing:
        raise FileNotFoundError("Missing controlled input:\n" + "\n".join(missing))
    make_sheet("trigger", "原手绘触发图｜9 个模型", OUT / "trigger_images_3x3.png")
    make_sheet("reference", "绘制触发图的参考原图｜9 个模型", OUT / "trigger_reference_images_3x3.png")
    make_sheet("ground", "模型出现时的地面贴图｜9 个模型", OUT / "ground_textures_3x3.png")

    manifest = {
        "schema": "red-wave-ar.trigger-reference-dimension-review.v1",
        "delivery_rules": {
            "trigger_images": "Preserve original hand-drawn source. No redraw or crop. Existing square targets stay at native dimensions.",
            "reference_images": "Preserve aspect ratio. Delivery copy may downscale only when its longest edge exceeds 2048 pixels.",
            "ground_images": "Use a square image plane, 1024–1280 pixels per side, and keep its plane smaller than the reference image plane.",
        },
        "assets": [
            {
                "asset_id": asset["asset_id"],
                "display_name_zh": asset["display_name_zh"],
                "trigger": image_metadata(asset["trigger"]),
                "trigger_drawing_reference": image_metadata(asset["reference"]),
                "ground_texture": image_metadata(asset["ground"]),
            }
            for asset in ASSETS
        ],
    }
    (OUT / "trigger_reference_dimensions.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(OUT)


if __name__ == "__main__":
    main()
