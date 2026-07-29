"""Build private, high-resolution reference sheets for detail extraction.

The sheets contain rights-pending source photographs and therefore stay under
the ignored ``source/.build`` directory.  They are review aids, not delivery
assets.
"""

from __future__ import annotations

import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageOps


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT_ROOT = ROOT / "modeling_input"
OUTPUT_ROOT = HERE / ".build" / "reference_detail_sheets"
FONT_PATH = pathlib.Path(r"C:\Windows\Fonts\msyh.ttc")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
CELL_WIDTH = 760
IMAGE_HEIGHT = 520
CAPTION_HEIGHT = 92
COLUMNS = 2


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def fit_image(path: pathlib.Path) -> Image.Image:
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
    image.thumbnail((CELL_WIDTH - 24, IMAGE_HEIGHT - 24), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (CELL_WIDTH, IMAGE_HEIGHT), (32, 35, 40))
    left = (CELL_WIDTH - image.width) // 2
    top = (IMAGE_HEIGHT - image.height) // 2
    canvas.paste(image, (left, top))
    return canvas


def caption_for(path: pathlib.Path, scene_root: pathlib.Path) -> str:
    relative = path.relative_to(scene_root).as_posix()
    return "\n".join(textwrap.wrap(relative, width=48))


def make_scene_sheet(scene_id: str) -> pathlib.Path:
    scene_root = INPUT_ROOT / scene_id
    paths = sorted(
        (
            path
            for path in (scene_root / "local_reference").rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        ),
        key=lambda path: path.as_posix().casefold(),
    )
    rows = (len(paths) + COLUMNS - 1) // COLUMNS
    header_height = 70
    sheet = Image.new(
        "RGB",
        (CELL_WIDTH * COLUMNS, header_height + rows * (IMAGE_HEIGHT + CAPTION_HEIGHT)),
        (19, 22, 27),
    )
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (24, 18),
        f"{scene_id} 全部参考图细节复核（仅内部）",
        font=load_font(30),
        fill=(238, 238, 238),
    )
    caption_font = load_font(20)
    for index, path in enumerate(paths):
        column = index % COLUMNS
        row = index // COLUMNS
        left = column * CELL_WIDTH
        top = header_height + row * (IMAGE_HEIGHT + CAPTION_HEIGHT)
        sheet.paste(fit_image(path), (left, top))
        draw.text(
            (left + 18, top + IMAGE_HEIGHT + 10),
            caption_for(path, scene_root),
            font=caption_font,
            fill=(224, 196, 156),
            spacing=4,
        )
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_ROOT / f"{scene_id}_reference_detail_sheet.png"
    sheet.save(output, optimize=True)
    print(f"[REFERENCE DETAIL] {scene_id}: {len(paths)} images -> {output}")
    return output


def main() -> None:
    for scene_number in range(1, 8):
        make_scene_sheet(f"S{scene_number}")


if __name__ == "__main__":
    main()
