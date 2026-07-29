"""Compose private start/mid/final photo-plane transition renders."""

from __future__ import annotations

import json
import pathlib

from PIL import Image, ImageDraw, ImageFont


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = HERE / ".build" / "transition_review_report.json"
OUTPUT = HERE / ".build" / "transition_contact_sheet.png"
FONT = pathlib.Path(r"C:\Windows\Fonts\msyh.ttc")


def main() -> None:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    items = data["assets"]
    cell = 360
    label_width = 160
    header_height = 54
    sheet = Image.new(
        "RGB",
        (label_width + cell * 3, header_height + cell * len(items)),
        (22, 26, 32),
    )
    draw = ImageDraw.Draw(sheet)
    header_font = ImageFont.truetype(str(FONT), 24)
    label_font = ImageFont.truetype(str(FONT), 22)
    for column, label in enumerate(("参考照片平面", "浅浮雕展开", "完整三维")):
        draw.text(
            (label_width + column * cell + 20, 12),
            label,
            font=header_font,
            fill=(230, 232, 236),
        )
    for row, item in enumerate(items):
        top = header_height + row * cell
        draw.text((18, top + 155), item["asset_id"], font=label_font, fill=(220, 188, 150))
        for column, phase in enumerate(("start", "mid", "final")):
            image = Image.open(ROOT / item["frames"][phase]).convert("RGB")
            image = image.resize((cell, cell), Image.Resampling.LANCZOS)
            sheet.paste(image, (label_width + column * cell, top))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
