"""Publish a 3×3 visual QA sheet for static ground/model continuity."""

from __future__ import annotations

import json
import pathlib

from PIL import Image, ImageDraw, ImageFont


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = HERE / ".build" / "static_ground_review" / "static_ground_review_report.json"
OUTPUT = HERE / ".build" / "static_ground_review" / "static_ground_contact_3x3.png"
PUBLISHED = ROOT / "lkivivube_delivery" / "images" / "kivicube_model_ground_contact_3x3.png"
FONT = pathlib.Path(r"C:\Windows\Fonts\msyh.ttc")
LABELS = {
    "S1A": "S1A 平西情报联络站｜入口门楼",
    "S1B": "S1B 平西情报联络站｜女报务员与报务设备",
    "S2A": "S2A 电报大楼｜主楼与钟塔",
    "S3A": "S3A 短波通信局（暂定）｜通信楼",
    "S3B": "S3B 短波通信局（暂定）｜天线阵列",
    "S4A": "S4A 居庸关｜城台与城楼",
    "S5A": "S5A 西山无名英雄纪念广场｜雕塑群",
    "S6A": "S6A 香山镇芳楼｜主体建筑",
    "S7A": "S7A 中国电信博物馆｜主体建筑",
}


def main() -> None:
    items = json.loads(REPORT.read_text(encoding="utf-8"))["assets"]
    cell_w, cell_h = 520, 490
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 3), (24, 28, 34))
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.truetype(str(FONT), 21)
    note_font = ImageFont.truetype(str(FONT), 15)
    for index, item in enumerate(items):
        row, column = divmod(index, 3)
        left, top = column * cell_w, row * cell_h
        image = Image.open(ROOT / item["preview"]).convert("RGB")
        image.thumbnail((500, 410), Image.Resampling.LANCZOS)
        sheet.paste(image, (left + (cell_w - image.width) // 2, top + 8))
        draw.text((left + 12, top + 420), LABELS[item["asset_id"]], font=title_font, fill=(235, 237, 240))
        draw.text((left + 12, top + 452), "V002 地面＋静态 GLB｜材质与贴地检查", font=note_font, fill=(168, 200, 218))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PUBLISHED.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT, optimize=True)
    sheet.save(PUBLISHED, optimize=True)
    print(OUTPUT)
    print(PUBLISHED)


if __name__ == "__main__":
    main()
