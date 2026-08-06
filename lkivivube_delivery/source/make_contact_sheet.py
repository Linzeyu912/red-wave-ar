"""Compose the nine Blender previews into one visual QA contact sheet."""

from __future__ import annotations

import json
import pathlib

from PIL import Image, ImageDraw, ImageFont


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = HERE / "blender_review_report.json"
OUTPUT = HERE / "model_contact_sheet.png"
PUBLISHED_OUTPUT = ROOT / "lkivivube_delivery" / "images" / "kivicube_model_previews_3x3.png"
FONT = pathlib.Path(r"C:\Windows\Fonts\msyh.ttc")
DISPLAY_LABELS = {
    "s1a_pingxi_gate": "S1A 平西情报联络站｜入口门楼",
    "s1b_radio_operator_statue": "S1B 平西情报联络站｜女报务员与报务设备",
    "s2a_telegraph_building": "S2A 电报大楼｜主楼与钟塔",
    "s3a_shortwave_station_building": "S3A 短波通信局（暂定）｜通信楼",
    "s3b_shortwave_antenna_array": "S3B 短波通信局（暂定）｜四臂天线阵列",
    "s4a_juyong_pass_tower": "S4A 居庸关｜城台与城楼",
    "s5a_memorial_sculpture": "S5A 西山无名英雄纪念广场｜雕塑群",
    "s6a_zhenfang_lou": "S6A 香山镇芳楼｜主体建筑",
    "s7a_telecom_museum": "S7A 中国电信博物馆｜主体建筑",
}


def main() -> None:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    items = data["assets"]
    cell_w, cell_h = 520, 665
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 3), (24, 28, 34))
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.truetype(str(FONT), 24)
    filename_font = ImageFont.truetype(str(FONT), 14)
    stat_font = ImageFont.truetype(str(FONT), 16)
    for index, item in enumerate(items):
        row, column = divmod(index, 3)
        left, top = column * cell_w, row * cell_h
        image = Image.open(ROOT / item["preview"]).convert("RGB")
        image.thumbnail((500, 500), Image.Resampling.LANCZOS)
        x = left + (cell_w - image.width) // 2
        y = top + 8
        sheet.paste(image, (x, y))
        label_y = top + 515
        label = DISPLAY_LABELS.get(item["asset_id"], item["asset_id"])
        filename = pathlib.PurePosixPath(item["glb"]).name
        draw.text((left + 14, label_y), label, font=title_font, fill=(235, 237, 240))
        draw.text((left + 14, label_y + 36), filename, font=filename_font, fill=(194, 199, 205))
        stats = (
            f"{item['mesh_objects']} meshes · {item['triangles']} tris · "
            f"{item['materials']} mats · {item['images']} tex"
        )
        dims = " × ".join(f"{value:.2f}" for value in item["dimensions"]) + " m"
        draw.text((left + 14, label_y + 62), stats, font=stat_font, fill=(169, 201, 218))
        draw.text((left + 14, label_y + 87), dims, font=stat_font, fill=(171, 178, 186))
    sheet.save(OUTPUT, optimize=True)
    PUBLISHED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(PUBLISHED_OUTPUT, optimize=True)
    print(OUTPUT)
    print(PUBLISHED_OUTPUT)


if __name__ == "__main__":
    main()
