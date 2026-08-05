"""Prepare the S1 (Pingxi) Kivicube image package.

The script makes deterministic delivery copies of the supplied trigger-reference
photos and writes placement manifests.  The S1B hand-drawn trigger and the two
ground textures are authored image assets and must already be present in the
package directories before this script is run.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
SCENE = ROOT / "lkivivube_delivery" / "scenes" / "S1_pingxi_intelligence_station"
PACKAGE = SCENE / "kivicube_package"
SOURCE = ROOT / "modeling_input" / "S1" / "local_reference" / "source_folder_20260727"


def save_delivery_copy(source: Path, destination: Path, longest_edge: int = 2048) -> dict[str, int]:
    """Make an orientation-correct, aspect-preserving JPEG delivery copy."""
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail((longest_edge, longest_edge), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, "JPEG", quality=92, optimize=True, progressive=True)
        return {"width": image.width, "height": image.height}


def file_info(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {
            "file": path.name,
            "width": image.width,
            "height": image.height,
            "bytes": path.stat().st_size,
        }


def write_json(path: Path, content: dict[str, object]) -> None:
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def setup(asset_id: str, display_name: str, trigger: str, reference: str, ground: str, model: str,
          model_position: list[float], model_scale: float, footprint: dict[str, list[float]],
          ground_center: list[float], ground_size: list[float]) -> dict[str, object]:
    return {
        "schema": "red-wave-ar.kivicube-s1-package.v1",
        "asset_id": asset_id,
        "display_name_zh": display_name,
        "target_coordinate_contract": {
            "unit": "target_image_long_edge",
            "target_plane": "XZ",
            "up_axis": "Y",
            "image_bottom_axis": "+Z",
        },
        "files": {
            "image_target": trigger,
            "reference_reveal": reference,
            "ground_texture": ground,
            "model_glb": model,
        },
        "animation_sequence": [
            {
                "start_seconds": 0.0,
                "action": "recognize_image_target",
                "notes_zh": "识别红白黑手绘触发图；触发图为实体识别图，不再额外盖一张数字触发图。",
            },
            {
                "start_seconds": 0.15,
                "action": "show_reference_reveal",
                "notes_zh": "显示对应原图，作为模型出现前的第一画面。",
            },
            {
                "start_seconds": 2.2,
                "action": "show_ground_and_model",
                "model_animation": "photo_emerge",
                "auto_play": True,
                "notes_zh": "地面贴图和 GLB 同时出现；地面只覆盖模型脚下区域，不遮住整张原图。",
            },
            {
                "start_seconds": 3.2,
                "action": "start_narration",
                "notes_zh": "保持原图、地面和模型可见。",
            },
        ],
        "reference_reveal_plane": {
            "position": [0.0, 0.002, 0.0],
            "rotation_degrees": [0.0, 0.0, 0.0],
            "long_edge_ratio": 1.0,
            "fit_mode": "contain_preserve_original_aspect",
        },
        "ground_texture_plane": {
            "position": ground_center,
            "rotation_degrees": [0.0, 0.0, 0.0],
            "size_target_units": ground_size,
            "y_offset": 0.004,
            "notes_zh": "这是平面贴图，不是厚展台；按模型出现时再显示。",
        },
        "model": {
            "position": model_position,
            "rotation_degrees": [0.0, 0.0, 0.0],
            "uniform_scale_after_kivicube_auto_fit": model_scale,
            "entry_animation": "photo_emerge",
            "auto_play": True,
            "target_footprint": footprint,
        },
    }


def main() -> None:
    gate = PACKAGE / "S1A_pingxi_gate"
    operator = PACKAGE / "S1B_radio_operator_statue"

    required_authored = [
        operator / "S1B_radio_operator_statue_trigger_v001.png",
        gate / "S1A_pingxi_gate_ground_texture_v001.png",
        operator / "S1B_radio_operator_statue_ground_texture_v001.png",
    ]
    missing = [str(path) for path in required_authored if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing authored package assets:\n" + "\n".join(missing))

    save_delivery_copy(
        SOURCE / "trigger_hand_drawn.jpg",
        gate / "S1A_pingxi_gate_trigger_v001.jpg",
        longest_edge=1280,
    )
    save_delivery_copy(
        SOURCE / "微信图片_20260712203953_1152_5130.jpg",
        gate / "S1A_pingxi_gate_reference_reveal_v001.jpg",
    )
    save_delivery_copy(
        SOURCE / "平西情报联络站2.jpg",
        operator / "S1B_radio_operator_statue_reference_reveal_v001.jpg",
    )

    gate_setup = setup(
        "S1A",
        "平西情报联络站：入口门楼",
        "S1A_pingxi_gate_trigger_v001.jpg",
        "S1A_pingxi_gate_reference_reveal_v001.jpg",
        "S1A_pingxi_gate_ground_texture_v001.png",
        "../../model/S1A_pingxi_gate_v003.glb",
        [0.0, 0.006, 0.113878],
        0.72,
        {"x": [-0.36, 0.36], "z": [-0.152245, 0.231385]},
        [0.0, 0.004, 0.04],
        [0.76, 0.46],
    )
    operator_setup = setup(
        "S1B",
        "平西情报联络站：女报务员雕塑及发报设备",
        "S1B_radio_operator_statue_trigger_v001.png",
        "S1B_radio_operator_statue_reference_reveal_v001.jpg",
        "S1B_radio_operator_statue_ground_texture_v001.png",
        "../../model/S1B_radio_operator_statue_v003.glb",
        [-0.12, 0.006, 0.113032],
        0.392401,
        {"x": [-0.30, 0.06], "z": [-0.093935, 0.168018]},
        [-0.12, 0.004, 0.04],
        [0.46, 0.36],
    )
    write_json(gate / "kivicube_setup.json", gate_setup)
    write_json(operator / "kivicube_setup.json", operator_setup)

    manifest = {
        "schema": "red-wave-ar.kivicube-s1-package-manifest.v1",
        "scope": "S1 Pingxi intelligence station only",
        "status": "INTERNAL_KIVICUBE_TEST_ONLY_RIGHTS_PENDING",
        "assets": [
            {
                "asset_id": "S1A",
                "display_name_zh": "平西情报联络站：入口门楼",
                "trigger_reference_source": "modeling_input/S1/local_reference/source_folder_20260727/微信图片_20260712203953_1152_5130.jpg",
                "files": [
                    file_info(gate / "S1A_pingxi_gate_trigger_v001.jpg"),
                    file_info(gate / "S1A_pingxi_gate_reference_reveal_v001.jpg"),
                    file_info(gate / "S1A_pingxi_gate_ground_texture_v001.png"),
                ],
            },
            {
                "asset_id": "S1B",
                "display_name_zh": "平西情报联络站：女报务员雕塑及发报设备",
                "trigger_reference_source": "modeling_input/S1/local_reference/source_folder_20260727/平西情报联络站2.jpg",
                "files": [
                    file_info(operator / "S1B_radio_operator_statue_trigger_v001.png"),
                    file_info(operator / "S1B_radio_operator_statue_reference_reveal_v001.jpg"),
                    file_info(operator / "S1B_radio_operator_statue_ground_texture_v001.png"),
                ],
            },
        ],
    }
    write_json(PACKAGE / "ASSET_MANIFEST.json", manifest)

    readme = """# 平西情报联络站｜Kivicube 触发图、原图与地面贴图包

本目录用于平西场景（S1）的内部 Kivicube 适配。文件名保持英文；下方使用中文说明。

## 内容与对应关系

| 地点建模 | 触发图（红白黑手绘） | 触发图参考原图 | 地面贴图 | GLB |
|---|---|---|---|---|
| 平西情报联络站：入口门楼（S1A） | `S1A_pingxi_gate/S1A_pingxi_gate_trigger_v001.jpg` | `S1A_pingxi_gate/S1A_pingxi_gate_reference_reveal_v001.jpg` | `S1A_pingxi_gate/S1A_pingxi_gate_ground_texture_v001.png` | `../model/S1A_pingxi_gate_v003.glb` |
| 平西情报联络站：女报务员雕塑及发报设备（S1B） | `S1B_radio_operator_statue/S1B_radio_operator_statue_trigger_v001.png` | `S1B_radio_operator_statue/S1B_radio_operator_statue_reference_reveal_v001.jpg` | `S1B_radio_operator_statue/S1B_radio_operator_statue_ground_texture_v001.png` | `../model/S1B_radio_operator_statue_v003.glb` |

S1B 的旧“触发图”实际上是白底雕塑照片，并非红白黑手绘图。本包已将它作为触发图的参考原图，并补出对应的红白黑手绘触发图；不再使用含讲解员的室内照片作为 AR 首帧。

## Kivicube 装配顺序

1. 将每个目录中的 `*_trigger_*` 上传为对应模型的图片识别图。
2. 识别成功后，在 0.15 秒显示 `*_reference_reveal_*`；该文件是保留画幅比例的原图副本。
3. 到 2.20 秒再显示 `*_ground_texture_*` 和同目录 `kivicube_setup.json` 指定的 GLB，自动播放 `photo_emerge`。
4. 地面贴图放在 `Y=0.004`、模型放在 `Y=0.006`。地面仅铺在模型脚下矩形，不应覆盖整张原图；精确坐标、尺寸、模型缩放见各自 `kivicube_setup.json`。

## 使用边界

- 这是“图片识别图 → 原图 → 模型＋地面贴图”的展示包，不包含新的厚展台模型。
- `ASSET_MANIFEST.json` 记录了每对触发图／参考原图的受控来源、尺寸与文件大小。
- 所有原图的公开展示授权仍为 `RIGHTS_PENDING`。可用于当前内部 Kivicube 调试；上线公开前须确认授权。
"""
    (PACKAGE / "README.md").write_text(readme, encoding="utf-8")

    print(f"Prepared {PACKAGE}")
    for file in sorted(PACKAGE.rglob("*")):
        if file.is_file():
            print(file.relative_to(ROOT))


if __name__ == "__main__":
    main()
