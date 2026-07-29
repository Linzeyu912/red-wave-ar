"""Validate generated GLB files against the repository's Kivicube budget.

This is intentionally dependency-free so the final gate can run anywhere that
has Python 3, independently of Blender.
"""

from __future__ import annotations

import json
import math
import pathlib
import struct
import sys
from typing import Any


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD_REPORT = HERE / "build_report.json"
BLENDER_REPORT = HERE / "blender_review_report.json"
OUTPUT = HERE / "validation_report.json"

TARGET_BYTES = 5 * 1024 * 1024
MAX_BYTES = 10 * 1024 * 1024
MAX_MESHES = 5
MAX_TRIANGLES = 30_000
MAX_MATERIALS = 5
MAX_TEXTURES = 10
MAX_ANIMATIONS = 5
ALLOWED_IMAGE_MIME = {"image/png", "image/jpeg"}
ALLOWED_PRIMITIVE_MODES = {4}  # TRIANGLES


class ValidationError(RuntimeError):
    pass


def read_glb(path: pathlib.Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    if len(raw) < 20:
        raise ValidationError("file is shorter than a GLB header and JSON chunk")
    magic, version, declared_length = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF":
        raise ValidationError(f"invalid GLB magic {magic!r}")
    if version != 2:
        raise ValidationError(f"GLB version must be 2, found {version}")
    if declared_length != len(raw):
        raise ValidationError(
            f"header length {declared_length} does not match file length {len(raw)}"
        )

    offset = 12
    chunks: list[tuple[bytes, bytes]] = []
    while offset < len(raw):
        if offset + 8 > len(raw):
            raise ValidationError("truncated GLB chunk header")
        chunk_length, chunk_type = struct.unpack_from("<I4s", raw, offset)
        offset += 8
        end = offset + chunk_length
        if end > len(raw):
            raise ValidationError("truncated GLB chunk payload")
        chunks.append((chunk_type, raw[offset:end]))
        offset = end
    if not chunks or chunks[0][0] != b"JSON":
        raise ValidationError("first GLB chunk is not JSON")
    if len(chunks) != 2 or chunks[1][0] != b"BIN\x00":
        raise ValidationError("expected exactly one JSON chunk and one BIN chunk")

    try:
        document = json.loads(chunks[0][1].rstrip(b" \t\r\n\x00").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid glTF JSON: {exc}") from exc
    return document, chunks[1][1]


def accessor_count(document: dict[str, Any], accessor_index: int) -> int:
    accessors = document.get("accessors", [])
    if not 0 <= accessor_index < len(accessors):
        raise ValidationError(f"invalid accessor index {accessor_index}")
    count = accessors[accessor_index].get("count")
    if not isinstance(count, int) or count < 0:
        raise ValidationError(f"invalid accessor count at {accessor_index}")
    return count


def validate_document(path: pathlib.Path) -> dict[str, Any]:
    document, binary = read_glb(path)
    errors: list[str] = []
    warnings: list[str] = []

    asset = document.get("asset", {})
    if asset.get("version") != "2.0":
        errors.append("asset.version must be 2.0")

    buffers = document.get("buffers", [])
    if len(buffers) != 1:
        errors.append(f"expected one embedded buffer, found {len(buffers)}")
    elif "uri" in buffers[0]:
        errors.append("external buffer URI is not allowed")
    elif not isinstance(buffers[0].get("byteLength"), int):
        errors.append("buffer byteLength is missing")
    elif buffers[0]["byteLength"] > len(binary):
        errors.append("buffer byteLength exceeds BIN chunk length")

    scenes = document.get("scenes", [])
    scene_index = document.get("scene")
    if not scenes:
        errors.append("no scene is defined")
    elif not isinstance(scene_index, int) or not 0 <= scene_index < len(scenes):
        errors.append("default scene index is missing or invalid")
    if not document.get("nodes"):
        errors.append("no nodes are defined")

    meshes = document.get("meshes", [])
    materials = document.get("materials", [])
    textures = document.get("textures", [])
    images = document.get("images", [])
    animations = document.get("animations", [])
    triangles = 0
    primitives = 0
    position_min_y: list[float] = []
    position_max_y: list[float] = []
    for mesh_index, mesh in enumerate(meshes):
        for primitive_index, primitive in enumerate(mesh.get("primitives", [])):
            primitives += 1
            mode = primitive.get("mode", 4)
            if mode not in ALLOWED_PRIMITIVE_MODES:
                errors.append(
                    f"mesh {mesh_index} primitive {primitive_index} uses unsupported mode {mode}"
                )
            attributes = primitive.get("attributes", {})
            if "POSITION" not in attributes:
                errors.append(f"mesh {mesh_index} primitive {primitive_index} has no POSITION")
            else:
                position_accessor = document.get("accessors", [])[attributes["POSITION"]]
                minimum = position_accessor.get("min", [])
                maximum = position_accessor.get("max", [])
                if len(minimum) == 3 and len(maximum) == 3:
                    position_min_y.append(float(minimum[1]))
                    position_max_y.append(float(maximum[1]))
            try:
                index_count = accessor_count(document, primitive["indices"])
                if index_count % 3:
                    errors.append(
                        f"mesh {mesh_index} primitive {primitive_index} index count is not divisible by 3"
                    )
                triangles += index_count // 3
            except (KeyError, ValidationError) as exc:
                errors.append(
                    f"mesh {mesh_index} primitive {primitive_index} has invalid indices: {exc}"
                )
            material_index = primitive.get("material")
            if material_index is not None and (
                not isinstance(material_index, int)
                or not 0 <= material_index < len(materials)
            ):
                errors.append(
                    f"mesh {mesh_index} primitive {primitive_index} has invalid material index"
                )

    for accessor_index, accessor in enumerate(document.get("accessors", [])):
        for key in ("min", "max"):
            values = accessor.get(key, [])
            if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
                errors.append(f"accessor {accessor_index} contains non-finite {key} values")

    for image_index, image in enumerate(images):
        if "uri" in image:
            errors.append(f"image {image_index} uses an external URI")
        if "bufferView" not in image:
            errors.append(f"image {image_index} is not embedded in a bufferView")
        if image.get("mimeType") not in ALLOWED_IMAGE_MIME:
            errors.append(
                f"image {image_index} has unsupported MIME type {image.get('mimeType')!r}"
            )

    for animation_index, animation in enumerate(animations):
        samplers_for_animation = animation.get("samplers", [])
        for channel_index, channel in enumerate(animation.get("channels", [])):
            sampler_index = channel.get("sampler")
            target = channel.get("target", {})
            node_index = target.get("node")
            path_name = target.get("path")
            if not isinstance(sampler_index, int) or not 0 <= sampler_index < len(samplers_for_animation):
                errors.append(f"animation {animation_index} channel {channel_index} has invalid sampler")
                continue
            if not isinstance(node_index, int) or not 0 <= node_index < len(document.get("nodes", [])):
                errors.append(f"animation {animation_index} channel {channel_index} has invalid node")
            if path_name not in {"translation", "rotation", "scale", "weights"}:
                errors.append(
                    f"animation {animation_index} channel {channel_index} has invalid path {path_name!r}"
                )
            if path_name == "scale":
                output_index = samplers_for_animation[sampler_index].get("output")
                if isinstance(output_index, int) and 0 <= output_index < len(document.get("accessors", [])):
                    scale_min = document["accessors"][output_index].get("min", [])
                    if len(scale_min) != 3 or any(float(value) <= 0.0 for value in scale_min):
                        errors.append(
                            f"animation {animation_index} scale contains zero or negative values"
                        )

    minimum_ground_y = min(position_min_y) if position_min_y else None
    maximum_ground_y = max(position_max_y) if position_max_y else None
    if minimum_ground_y is None:
        errors.append("unable to determine the model ground plane")
    elif abs(minimum_ground_y) > 1e-5:
        errors.append(
            f"model bottom must touch Y=0 reference-photo plane, found {minimum_ground_y}"
        )
    if maximum_ground_y is not None and maximum_ground_y <= 0.0:
        errors.append("model has no geometry above the reference-photo plane")

    extensions_required = set(document.get("extensionsRequired", []))
    extensions_used = set(document.get("extensionsUsed", []))
    if extensions_required:
        errors.append(
            "required glTF extensions are not allowed for the baseline delivery: "
            + ", ".join(sorted(extensions_required))
        )
    if extensions_used - extensions_required:
        warnings.append(
            "optional extensions used: " + ", ".join(sorted(extensions_used - extensions_required))
        )

    size = path.stat().st_size
    budgets = {
        "file_bytes": {"value": size, "target": TARGET_BYTES, "maximum": MAX_BYTES},
        "meshes": {"value": len(meshes), "maximum": MAX_MESHES},
        "triangles": {"value": triangles, "maximum": MAX_TRIANGLES},
        "materials": {"value": len(materials), "maximum": MAX_MATERIALS},
        "textures": {"value": len(textures), "maximum": MAX_TEXTURES},
        "animations": {"value": len(animations), "maximum": MAX_ANIMATIONS},
    }
    for name, budget in budgets.items():
        if budget["value"] > budget["maximum"]:
            errors.append(
                f"{name} budget exceeded: {budget['value']} > {budget['maximum']}"
            )
    if size > TARGET_BYTES:
        warnings.append(f"file exceeds the preferred 5 MiB target ({size} bytes)")

    return {
        "file": path.relative_to(ROOT).as_posix(),
        "status": "PASS" if not errors else "FAIL",
        "generator": asset.get("generator"),
        "glb_version": asset.get("version"),
        "primitives": primitives,
        "images": len(images),
        "ground_plane": {
            "axis": "Y",
            "minimum": minimum_ground_y,
            "maximum": maximum_ground_y,
            "status": "PASS" if minimum_ground_y is not None and abs(minimum_ground_y) <= 1e-5 else "FAIL",
        },
        "budgets": budgets,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    if not BUILD_REPORT.exists():
        raise SystemExit("build_report.json is missing; run build_models.py first")
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    blender_by_id: dict[str, dict[str, Any]] = {}
    if BLENDER_REPORT.exists():
        blender = json.loads(BLENDER_REPORT.read_text(encoding="utf-8"))
        blender_by_id = {entry["asset_id"]: entry for entry in blender.get("assets", [])}

    assets: list[dict[str, Any]] = []
    failed = False
    for build_entry in build.get("assets", []):
        path = ROOT / build_entry["relative_file"]
        if not path.exists():
            entry = {
                "asset_id": build_entry["asset_id"],
                "file": build_entry["relative_file"],
                "status": "FAIL",
                "errors": ["file does not exist"],
                "warnings": [],
            }
        else:
            try:
                entry = validate_document(path)
            except (OSError, ValidationError) as exc:
                entry = {
                    "file": build_entry["relative_file"],
                    "status": "FAIL",
                    "errors": [str(exc)],
                    "warnings": [],
                }
            entry["asset_id"] = build_entry["asset_id"]

        blender_entry = blender_by_id.get(build_entry["asset_id"])
        entry["blender_import"] = {
            "status": "PASS" if blender_entry else "NOT_RUN",
            "version": (
                json.loads(BLENDER_REPORT.read_text(encoding="utf-8")).get("blender")
                if blender_entry
                else None
            ),
            "mesh_objects": blender_entry.get("mesh_objects") if blender_entry else None,
            "triangles": blender_entry.get("triangles") if blender_entry else None,
            "materials": blender_entry.get("materials") if blender_entry else None,
            "images": blender_entry.get("images") if blender_entry else None,
        }
        if not blender_entry:
            entry["errors"].append("Blender import review has not been run")
            entry["status"] = "FAIL"
        elif "budgets" in entry:
            comparisons = {
                "meshes": "mesh_objects",
                "triangles": "triangles",
                "materials": "materials",
                "textures": "images",
                "animations": "animations",
            }
            for budget_name, blender_name in comparisons.items():
                authored = entry["budgets"][budget_name]["value"]
                imported = blender_entry[blender_name]
                if authored != imported:
                    entry["errors"].append(
                        f"Blender {blender_name} count {imported} does not match GLB count {authored}"
                    )
                    entry["status"] = "FAIL"
        failed = failed or entry["status"] != "PASS"
        assets.append(entry)
        print(
            f"[{entry['status']}] {entry['asset_id']} "
            f"{entry.get('budgets', {}).get('file_bytes', {}).get('value', 0)} bytes"
        )

    result = {
        "platform": "Kivicube",
        "policy": {
            "preferred_file_bytes": TARGET_BYTES,
            "maximum_file_bytes": MAX_BYTES,
            "maximum_meshes": MAX_MESHES,
            "maximum_triangles": MAX_TRIANGLES,
            "maximum_materials": MAX_MATERIALS,
            "maximum_textures": MAX_TEXTURES,
            "maximum_animations": MAX_ANIMATIONS,
        },
        "status": "FAIL" if failed else "PASS",
        "assets": assets,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"validation report: {OUTPUT}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
