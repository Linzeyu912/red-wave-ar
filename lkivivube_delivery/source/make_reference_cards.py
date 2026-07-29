"""Create private QA reference cards that exactly cover square trigger images.

Outputs are written under source/.build and are intentionally ignored.  A card
must not be published until its asset-card rights/privacy state allows it.
"""

from __future__ import annotations

import json
import pathlib

from PIL import Image, ImageEnhance, ImageFilter


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROFILES = HERE / "presentation_profiles.json"
OUTPUT_DIR = HERE / ".build" / "reference_cards"
REPORT = HERE / ".build" / "reference_card_report.json"
CARD_SIZE = 1080
CONTENT_MARGIN = 34


def normalized_crop(
    image: Image.Image, crop: list[float]
) -> Image.Image:
    left, top, right, bottom = crop
    width, height = image.size
    box = (
        round(left * width),
        round(top * height),
        round(right * width),
        round(bottom * height),
    )
    return image.crop(box)


def cover_square(image: Image.Image, size: int) -> Image.Image:
    scale = max(size / image.width, size / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - size) // 2
    top = (resized.height - size) // 2
    return resized.crop((left, top, left + size, top + size))


def contain(image: Image.Image, size: int) -> Image.Image:
    available = size - CONTENT_MARGIN * 2
    scale = min(available / image.width, available / image.height)
    return image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )


def make_card(source: pathlib.Path, crop: list[float], output: pathlib.Path) -> dict:
    with Image.open(source) as opened:
        image = normalized_crop(opened.convert("RGB"), crop)
    background = cover_square(image, CARD_SIZE)
    background = background.filter(ImageFilter.GaussianBlur(radius=38))
    background = ImageEnhance.Brightness(background).enhance(0.34)
    background = ImageEnhance.Color(background).enhance(0.58)

    fitted = contain(image, CARD_SIZE)
    left = (CARD_SIZE - fitted.width) // 2
    top = (CARD_SIZE - fitted.height) // 2
    background.paste(fitted, (left, top))
    output.parent.mkdir(parents=True, exist_ok=True)
    background.save(output, "JPEG", quality=90, optimize=True, progressive=True)
    return {
        "source_size": list(image.size),
        "card_size": [CARD_SIZE, CARD_SIZE],
        "contained_rect": [left, top, left + fitted.width, top + fitted.height],
        "output": output.relative_to(ROOT).as_posix(),
    }


def main() -> None:
    data = json.loads(PROFILES.read_text(encoding="utf-8"))
    report = []
    for profile in data["assets"]:
        source = ROOT / profile["reference_source"]
        output = OUTPUT_DIR / f"{profile['asset_id']}_reference_card_v002.jpg"
        entry = make_card(source, profile["reference_crop_uv"], output)
        entry.update(
            {
                "asset_id": profile["asset_id"],
                "rights_status": profile["reference_publish_status"],
                "public_delivery": False,
            }
        )
        report.append(entry)
        print(f"[REFERENCE CARD] {profile['asset_id']} -> {output}")
    REPORT.write_text(
        json.dumps({"assets": report}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(REPORT)


if __name__ == "__main__":
    main()
