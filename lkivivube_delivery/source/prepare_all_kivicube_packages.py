"""Create static-ground Kivicube packages for all nine AR models.

The controlled hand-drawn trigger images are copied byte-for-byte. Drawing
references remain internal support files only: after recognition Kivicube shows
the ground texture and a static GLB directly, without relying on an unclear
photo-reveal or model-entry animation.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "modeling_input"
GROUND_INPUTS = Path(__file__).resolve().parent / "ground_texture_inputs"
HANDOFF = Path(__file__).resolve().parent / "presentation_handoff_report.json"
GROUND_VERSION = "v002"


def ref(scene: str, filename: str) -> Path:
    return SOURCE / scene / "local_reference" / "source_folder_20260727" / filename


ASSETS = [
    {
        "asset_id": "S1A", "scene": "S1_pingxi_intelligence_station", "folder": "S1A_pingxi_gate",
        "display_name_zh": "平西情报联络站：入口门楼", "model": "S1A_pingxi_gate_v003.glb",
        "trigger": ref("S1", "trigger_hand_drawn.jpg"), "reference": ref("S1", "微信图片_20260712203953_1152_5130.jpg"),
        "status": "RIGHTS_PENDING",
    },
    {
        "asset_id": "S1B", "scene": "S1_pingxi_intelligence_station", "folder": "S1B_radio_operator_statue",
        "display_name_zh": "平西情报联络站：女报务员雕塑及发报设备", "model": "S1B_radio_operator_statue_v003.glb",
        "trigger": ref("S1", "S1B_radio_operator_trigger_hand_drawn.jpg"), "reference": ref("S1", "微信图片_20260716203647_1419_5130.jpg"),
        "status": "PRIVACY_AND_RIGHTS_PENDING",
    },
    {
        "asset_id": "S2A", "scene": "S2_telegraph_building", "folder": "S2A_telegraph_building",
        "display_name_zh": "电报大楼", "model": "S2A_telegraph_building_v003.glb",
        "trigger": ref("S2", "trigger_hand_drawn.jpg"), "reference": ref("S2", "微信图片_20260727183423_918_1.jpg"),
        "status": "PRIVACY_AND_RIGHTS_PENDING",
    },
    {
        "asset_id": "S3A", "scene": "S3_shortwave_station", "folder": "S3A_shortwave_station_building",
        "display_name_zh": "短波通信局：通信楼", "model": "S3A_shortwave_station_building_v003.glb",
        "trigger": ref("S3", "trigger_hand_drawn.jpg"), "reference": ref("S3", "微信图片_20260727183421_916_1.jpg"),
        "status": "IDENTITY_AND_RIGHTS_PENDING",
    },
    {
        "asset_id": "S3B", "scene": "S3_shortwave_station", "folder": "S3B_shortwave_antenna_array",
        "display_name_zh": "短波通信局：天线阵列", "model": "S3B_shortwave_antenna_array_v003.glb",
        "trigger": ref("S3", "短波通信局2.jpg"), "reference": ref("S3", "微信图片_20260727183422_917_1.jpg"),
        "status": "IDENTITY_AND_RIGHTS_PENDING",
    },
    {
        "asset_id": "S4A", "scene": "S4_juyong_pass", "folder": "S4A_juyong_pass_tower",
        "display_name_zh": "居庸关城楼", "model": "S4A_juyong_pass_tower_v003.glb",
        "trigger": ref("S4", "trigger_hand_drawn.jpg"), "reference": ref("S4", "微信图片_20260727183424_919_1.jpg"),
        "status": "RIGHTS_PENDING",
    },
    {
        "asset_id": "S5A", "scene": "S5_memorial_plaza", "folder": "S5A_memorial_sculpture",
        "display_name_zh": "西山无名英雄纪念广场雕塑群", "model": "S5A_memorial_sculpture_v003.glb",
        "trigger": ref("S5", "trigger_hand_drawn.jpg"), "reference": ref("S5", "18b017b5eb0df80ff4c70fc5991203b5.jpg"),
        "status": "BLOCKED_WATERMARK_AND_RIGHTS",
    },
    {
        "asset_id": "S6A", "scene": "S6_zhenfang_lou", "folder": "S6A_zhenfang_lou",
        "display_name_zh": "香山镇芳楼", "model": "S6A_zhenfang_lou_v003.glb",
        "trigger": ref("S6", "trigger_hand_drawn.jpg"), "reference": ref("S6", "a4c5a574525a3f829e286f6eea4b9e08.jpg"),
        "status": "RIGHTS_PENDING",
    },
    {
        "asset_id": "S7A", "scene": "S7_telecom_museum", "folder": "S7A_telecom_museum",
        "display_name_zh": "中国电信博物馆", "model": "S7A_telecom_museum_v003.glb",
        "trigger": ref("S7", "trigger_hand_drawn.jpg"), "reference": ref("S7", "d10d05331791c52d672efca4212a9012.png"),
        "status": "RIGHTS_PENDING",
    },
]


# These bridge colours use the lowest, ground-facing material of each GLB.
# The generated material image is only gently shifted toward this colour; it
# never replaces the visible model material or invents a freestanding plinth.
GROUND_SURFACES = {
    "S1A": {"family": "courtyard_grey_flagstone", "bridge_rgb": (119, 117, 110)},
    "S1B": {"family": "warm_dark_hardwood", "bridge_rgb": (59, 36, 22)},
    "S2A": {"family": "urban_granite_paving", "bridge_rgb": (170, 167, 158)},
    "S3A": {"family": "aged_service_concrete", "bridge_rgb": (126, 124, 117)},
    "S3B": {"family": "compacted_grass_earth", "bridge_rgb": (69, 72, 73)},
    "S4A": {"family": "historic_slate_flagstone", "bridge_rgb": (114, 115, 111)},
    "S5A": {"family": "memorial_granite_plaza", "bridge_rgb": (199, 195, 184)},
    "S6A": {"family": "heritage_courtyard_stone", "bridge_rgb": (136, 137, 134)},
    "S7A": {
        "family": "soft_graphite_paving",
        "bridge_rgb": (155, 155, 150),
        # The original graphite source reads as a black plinth beneath the
        # museum's pale stone/metal base at AR scale.  Keep its paving grain,
        # but lift it toward a neutral mid-grey for a continuous transition.
        "bridge_strength": 0.60,
    },
}


def file_info(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        return {
            "file": path.name,
            "width": image.width,
            "height": image.height,
            "aspect_ratio": round(image.width / image.height, 5),
            "bytes": path.stat().st_size,
        }


def copy_trigger(source: Path, destination: Path) -> dict[str, object]:
    """Copy, never redraw/crop/resave, the user-provided trigger image."""
    shutil.copy2(source, destination)
    info = file_info(destination)
    if (info["width"], info["height"]) != (1080, 1080):
        raise ValueError(f"{source} must remain the existing 1080×1080 trigger image")
    return info


def save_reference(source: Path, destination: Path) -> dict[str, object]:
    """Save an orientation-correct, aspect-preserving ≤2048px JPEG copy."""
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
        image.save(destination, "JPEG", quality=92, optimize=True, progressive=True)
    return file_info(destination)


def save_ground(
    source: Path,
    destination: Path,
    footprint: dict[str, list[float]],
    ground_position: list[float],
    ground_size: list[float],
    bridge_rgb: tuple[int, int, int],
    bridge_strength: float = 0.10,
) -> dict[str, object]:
    """Normalize a restrained ground material and add a soft contact bridge."""
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image = ImageOps.fit(image, (1024, 1024), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        # These are support surfaces, not a second hero asset.  Suppress small
        # texture noise and contrast so the material reads at AR scale without
        # competing with the model silhouette or its own surface detail.
        image = image.resize((512, 512), Image.Resampling.LANCZOS).resize((1024, 1024), Image.Resampling.BICUBIC)
        image = ImageEnhance.Contrast(image).enhance(0.72)
        image = Image.blend(image, Image.new("RGB", image.size, bridge_rgb), bridge_strength)

        # Use a very low-contrast oval under the actual footprint, never a
        # dark rectangular badge.  It only prevents the independently uploaded
        # GLB and plane from looking disconnected on renderers without shadow.
        edge = ground_size[0]
        center_x, _, center_z = ground_position
        x0, x1 = footprint["x"]
        z0, z1 = footprint["z"]
        box = (
            round(((x0 - center_x) / edge + 0.5) * 1024),
            round((1.0 - ((z1 - center_z) / edge + 0.5)) * 1024),
            round(((x1 - center_x) / edge + 0.5) * 1024),
            round((1.0 - ((z0 - center_z) / edge + 0.5)) * 1024),
        )
        shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse(box, fill=(18, 18, 16, 16))
        shadow = shadow.filter(ImageFilter.GaussianBlur(38))
        image = Image.alpha_composite(image.convert("RGBA"), shadow).convert("RGB")
        image.save(destination, "PNG", optimize=True)
    info = file_info(destination)
    if (info["width"], info["height"]) != (1024, 1024):
        raise ValueError(f"{destination} was not normalized to 1024×1024")
    return info


def write_json(path: Path, content: dict[str, object]) -> None:
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ground_layout(footprint: dict[str, list[float]]) -> tuple[list[float], list[float]]:
    x0, x1 = footprint["x"]
    z0, z1 = footprint["z"]
    # Square plane prevents a square material image from being stretched on a
    # long building footprint. The 0.10-unit border leaves enough visible
    # context for the texture and contact shadow to merge with the GLB base.
    edge = round(max((x1 - x0) + 0.20, (z1 - z0) + 0.20), 6)
    return [round((x0 + x1) / 2, 6), 0.002, round((z0 + z1) / 2, 6)], [edge, edge]


def write_scene_readme(package: Path, assets: list[dict[str, object]]) -> None:
    rows = "\n".join(
        f"| {asset['asset_id']} | {asset['display_name_zh']} | `{asset['folder']}/` |"
        for asset in assets
    )
    readme = f"""# Kivicube 素材包｜{assets[0]['scene']}

本目录按模型单元分包。每个子目录都有：原手绘触发图、绘制触发图的内部参考原图副本、独立地面贴图、`kivicube_setup.json`。

| 单元 | 中文名称 | 子目录 |
|---|---|---|
{rows}

## 统一装配顺序

1. 将 `*_trigger_v001.jpg` 作为图片识别图；它是原手绘文件的未修改副本。
2. 识别稳定后立即显示 `*_ground_texture_v002.png`，作为独立、无光照的方形地面平面。
3. 同时显示 GLB，**不**自动播放 `photo_emerge` 或其他入场动画；模型静态贴地摆放。
4. 地面平面在 `Y=0.002`，模型最低点在 `Y=0.004`；地面为不拉伸的方形，覆盖模型占地外侧 0.10 单位边界，详见各自 JSON。

## 尺寸约束

- 原手绘触发图：`1080×1080`，不裁切、不重绘。
- 参考原图：原比例交付，仅供绘制关系和内部核对，不进入识别后的展示流程。
- 地面贴图：`1024×1024`、v002；每个模型独立一张，按模型底部材质色系制作，并带轻微接触阴影。

所有参考原图均为 `RIGHTS_PENDING` 或更严格状态，只可先用于内部 Kivicube 适配。文件级状态见 `ASSET_MANIFEST.json`。
"""
    (package / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    layouts = {asset["asset_id"]: asset for asset in handoff["assets"]}
    missing = [str(path) for asset in ASSETS for path in (asset["trigger"], asset["reference"], GROUND_INPUTS / f"{asset['asset_id']}_{GROUND_VERSION}.png") if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required package inputs:\n" + "\n".join(missing))

    by_scene: dict[str, list[dict[str, object]]] = {}
    for asset in ASSETS:
        scene = ROOT / "lkivivube_delivery" / "scenes" / asset["scene"]
        package = scene / "kivicube_package"
        unit = package / asset["folder"]
        unit.mkdir(parents=True, exist_ok=True)
        prefix = asset["folder"]
        trigger_path = unit / f"{prefix}_trigger_v001.jpg"
        reference_path = unit / f"{prefix}_reference_reveal_v001.jpg"
        ground_path = unit / f"{prefix}_ground_texture_{GROUND_VERSION}.png"

        trigger_info = copy_trigger(asset["trigger"], trigger_path)
        reference_info = save_reference(asset["reference"], reference_path)
        handoff_asset = layouts[asset["asset_id"]]
        footprint = handoff_asset["target_footprint"]
        ground_position, ground_size = ground_layout(footprint)
        surface = GROUND_SURFACES[asset["asset_id"]]
        ground_info = save_ground(
            GROUND_INPUTS / f"{asset['asset_id']}_{GROUND_VERSION}.png",
            ground_path,
            footprint,
            ground_position,
            ground_size,
            surface["bridge_rgb"],
            surface.get("bridge_strength", 0.10),
        )
        model = handoff_asset["model"]
        setup = {
            "schema": "red-wave-ar.kivicube-static-ground-package.v3",
            "asset_id": asset["asset_id"],
            "display_name_zh": asset["display_name_zh"],
            "source_integrity": {
                "trigger": "original_hand_drawn_file_copied_without_redraw_or_crop",
                "drawing_reference": "internal_original_aspect_preserved_not_used_for_ar_display",
                "ground": "separate_1024_square_unlit_image_plane_with_model_contact_bridge",
            },
            "files": {
                "image_target": trigger_path.name,
                "drawing_reference_internal": reference_path.name,
                "ground_texture": ground_path.name,
                "model_glb": f"../../model/{asset['model']}",
            },
            "display_sequence": [
                {"start_seconds": 0.0, "action": "recognize_original_hand_drawn_image_target"},
                {"start_seconds": 0.1, "action": "show_ground_texture_plane", "material_mode": "unlit"},
                {"start_seconds": 0.1, "action": "show_model_static", "play_model_animation": False},
                {"start_seconds": 0.8, "action": "start_narration"},
            ],
            "ground_texture_plane": {
                "position": ground_position, "rotation_degrees": [0.0, 0.0, 0.0],
                "size_target_units": ground_size, "y_offset": 0.002,
                "material_mode": "unlit",
                "surface_family": surface["family"],
                "model_material_bridge_rgb": surface["bridge_rgb"],
                "notes_zh": "方形地面不拉伸；以同材质色系和轻微接触阴影衔接模型底部，不添加独立展台。",
            },
            "model": {
                "position": [model["position"][0], 0.004, model["position"][2]], "rotation_degrees": model["rotation_degrees"],
                "uniform_scale_after_kivicube_auto_fit": model["uniform_scale_after_kivicube_auto_fit"],
                "entry_animation": "none", "auto_play": False, "target_footprint": footprint,
            },
        }
        write_json(unit / "kivicube_setup.json", setup)
        asset["delivery"] = {
            "trigger": trigger_info, "drawing_reference_internal": reference_info, "ground_texture": ground_info,
            "ground_plane_position": ground_position, "ground_plane_size_target_units": ground_size,
        }
        by_scene.setdefault(asset["scene"], []).append(asset)

    for scene_name, assets in by_scene.items():
        package = ROOT / "lkivivube_delivery" / "scenes" / scene_name / "kivicube_package"
        write_scene_readme(package, assets)
        manifest = {
            "schema": "red-wave-ar.kivicube-static-ground-package-manifest.v3",
            "scope": scene_name,
            "status": "INTERNAL_KIVICUBE_TEST_ONLY_RIGHTS_PENDING",
            "assets": [
                {
                    "asset_id": asset["asset_id"], "display_name_zh": asset["display_name_zh"],
                    "trigger_source": asset["trigger"].relative_to(ROOT).as_posix(),
                    "trigger_drawing_reference_source": asset["reference"].relative_to(ROOT).as_posix(),
                    "reference_publish_status": asset["status"], "delivery": asset["delivery"],
                }
                for asset in assets
            ],
        }
        write_json(package / "ASSET_MANIFEST.json", manifest)
        print(package)


if __name__ == "__main__":
    main()
