"""Create the Kivicube image packages for all nine current AR models.

The controlled hand-drawn trigger images are copied byte-for-byte.  Reference
photos retain their original aspect ratio, while ground planes are normalized
to 1024×1024.  This keeps trigger recognition stable and gives every GLB a
separate, appropriately sized ground-image plane.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "modeling_input"
GROUND_INPUTS = Path(__file__).resolve().parent / ".build" / "ground_texture_inputs"
HANDOFF = Path(__file__).resolve().parent / "presentation_handoff_report.json"


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
        "trigger": ref("S1", "平西情报联络站2.jpg"), "reference": ref("S1", "微信图片_20260716203647_1419_5130.jpg"),
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


def save_ground(source: Path, destination: Path) -> dict[str, object]:
    """Normalize the ground texture to a square 1024px image-plane asset."""
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image = ImageOps.fit(image, (1024, 1024), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
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
    width = round((x1 - x0) + 0.06, 6)
    depth = round((z1 - z0) + 0.06, 6)
    return [round((x0 + x1) / 2, 6), 0.004, round((z0 + z1) / 2, 6)], [width, depth]


def write_scene_readme(package: Path, assets: list[dict[str, object]]) -> None:
    rows = "\n".join(
        f"| {asset['asset_id']} | {asset['display_name_zh']} | `{asset['folder']}/` |"
        for asset in assets
    )
    readme = f"""# Kivicube 素材包｜{assets[0]['scene']}

本目录按模型单元分包。每个子目录都有：原手绘触发图、绘制触发图的参考原图副本、独立地面贴图、`kivicube_setup.json`。

| 单元 | 中文名称 | 子目录 |
|---|---|---|
{rows}

## 统一装配顺序

1. 将 `*_trigger_v001.jpg` 作为图片识别图；它是原手绘文件的未修改副本。
2. 识别稳定后第 `0.15s` 显示 `*_reference_reveal_v001.jpg`，保持原图画幅比例。
3. 第 `2.20s` 显示 `*_ground_texture_v001.png` 和 GLB，自动播放 `photo_emerge`。
4. 地面平面在 `Y=0.004`，模型在 `Y=0.006`；地面尺寸小于原图平面、由模型的实际占地推导，详见各自 JSON。

## 尺寸约束

- 原手绘触发图：`1080×1080`，不裁切、不重绘。
- 参考原图：原比例交付；仅长边超过 `2048px` 时下采样。
- 地面贴图：`1024×1024`，每个模型独立一张。

所有参考原图均为 `RIGHTS_PENDING` 或更严格状态，只可先用于内部 Kivicube 适配。文件级状态见 `ASSET_MANIFEST.json`。
"""
    (package / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    layouts = {asset["asset_id"]: asset for asset in handoff["assets"]}
    missing = [str(path) for asset in ASSETS for path in (asset["trigger"], asset["reference"], GROUND_INPUTS / f"{asset['asset_id']}.png") if not path.exists()]
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
        ground_path = unit / f"{prefix}_ground_texture_v001.png"

        trigger_info = copy_trigger(asset["trigger"], trigger_path)
        reference_info = save_reference(asset["reference"], reference_path)
        ground_info = save_ground(GROUND_INPUTS / f"{asset['asset_id']}.png", ground_path)
        handoff_asset = layouts[asset["asset_id"]]
        footprint = handoff_asset["target_footprint"]
        ground_position, ground_size = ground_layout(footprint)
        model = handoff_asset["model"]
        setup = {
            "schema": "red-wave-ar.kivicube-package.v2",
            "asset_id": asset["asset_id"],
            "display_name_zh": asset["display_name_zh"],
            "source_integrity": {
                "trigger": "original_hand_drawn_file_copied_without_redraw_or_crop",
                "reference": "drawing_reference_original_aspect_preserved",
                "ground": "separate_1024_square_image_plane",
            },
            "files": {
                "image_target": trigger_path.name,
                "reference_reveal": reference_path.name,
                "ground_texture": ground_path.name,
                "model_glb": f"../../model/{asset['model']}",
            },
            "animation_sequence": [
                {"start_seconds": 0.0, "action": "recognize_original_hand_drawn_image_target"},
                {"start_seconds": 0.15, "action": "show_reference_reveal", "keep_visible_under_model": True},
                {"start_seconds": 2.2, "action": "show_ground_and_model", "model_animation": "photo_emerge", "auto_play": True},
                {"start_seconds": 3.2, "action": "start_narration", "keep_reference_visible": True},
            ],
            "reference_reveal_plane": {
                "position": [0.0, 0.002, 0.0], "rotation_degrees": [0.0, 0.0, 0.0],
                "long_edge_ratio": 1.0, "fit_mode": "contain_preserve_original_aspect",
            },
            "ground_texture_plane": {
                "position": ground_position, "rotation_degrees": [0.0, 0.0, 0.0],
                "size_target_units": ground_size, "y_offset": 0.004,
                "notes_zh": "仅覆盖模型实际占地及 0.03 单位边界；不覆盖整张原图。",
            },
            "model": {
                "position": model["position"], "rotation_degrees": model["rotation_degrees"],
                "uniform_scale_after_kivicube_auto_fit": model["uniform_scale_after_kivicube_auto_fit"],
                "entry_animation": "photo_emerge", "auto_play": True, "target_footprint": footprint,
            },
        }
        write_json(unit / "kivicube_setup.json", setup)
        asset["delivery"] = {
            "trigger": trigger_info, "reference_reveal": reference_info, "ground_texture": ground_info,
            "ground_plane_position": ground_position, "ground_plane_size_target_units": ground_size,
        }
        by_scene.setdefault(asset["scene"], []).append(asset)

    for scene_name, assets in by_scene.items():
        package = ROOT / "lkivivube_delivery" / "scenes" / scene_name / "kivicube_package"
        write_scene_readme(package, assets)
        manifest = {
            "schema": "red-wave-ar.kivicube-package-manifest.v2",
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
