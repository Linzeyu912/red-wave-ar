"""Compose the nine Blender previews into one visual QA contact sheet."""

from __future__ import annotations

import json
import pathlib

from PIL import Image, ImageDraw, ImageFont


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = HERE / "blender_review_report.json"
OUTPUT = HERE / "model_contact_sheet.png"
FONT = pathlib.Path(r"C:\Windows\Fonts\msyh.ttc")


def main() -> None:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    items = data["assets"]
    cell_w, cell_h = 520, 610
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 3), (24, 28, 34))
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.truetype(str(FONT), 29)
    stat_font = ImageFont.truetype(str(FONT), 18)
    for index, item in enumerate(items):
        row, column = divmod(index, 3)
        left, top = column * cell_w, row * cell_h
        image = Image.open(ROOT / item["preview"]).convert("RGB")
        image.thumbnail((500, 500), Image.Resampling.LANCZOS)
        x = left + (cell_w - image.width) // 2
        y = top + 8
        sheet.paste(image, (x, y))
        label_y = top + 515
        draw.text((left + 14, label_y), item["asset_id"], font=title_font, fill=(235, 237, 240))
        stats = (
            f"{item['mesh_objects']} meshes · {item['triangles']} tris · "
            f"{item['materials']} mats · {item['images']} tex"
        )
        dims = " × ".join(f"{value:.2f}" for value in item["dimensions"]) + " m"
        draw.text((left + 14, label_y + 42), stats, font=stat_font, fill=(169, 201, 218))
        draw.text((left + 14, label_y + 70), dims, font=stat_font, fill=(171, 178, 186))
    sheet.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
