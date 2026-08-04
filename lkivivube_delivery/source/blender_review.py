"""Import every generated GLB in Blender, save editable sources, and render QA previews.

Usage:
    blender.exe --background --factory-startup \
      --python lkivivube_delivery/source/blender_review.py

Blender 5.1.2 is the reference review runtime for this repository.
"""

from __future__ import annotations

import json
import math
import pathlib
import re

import bpy
from mathutils import Vector


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD_REPORT = HERE / "build_report.json"
BLEND_DIR = HERE / "blend"
REVIEW_REPORT = HERE / "blender_review_report.json"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                       bpy.data.cameras, bpy.data.lights, bpy.data.actions):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)
    for image in list(bpy.data.images):
        if image.users == 0 and image.name not in {"Render Result", "Viewer Node"}:
            bpy.data.images.remove(image)


def mesh_objects() -> list[bpy.types.Object]:
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    minimum = Vector((min(point.x for point in corners), min(point.y for point in corners),
                      min(point.z for point in corners)))
    maximum = Vector((max(point.x for point in corners), max(point.y for point in corners),
                      max(point.z for point in corners)))
    return minimum, maximum


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_review_world(minimum: Vector, maximum: Vector, asset_id: str = "") -> None:
    """Create a Blender Z-up review rig.

    Blender's glTF importer converts authored glTF axes as:
    glTF X -> Blender X, glTF Y(up) -> Blender Z(up), glTF -Z(front) -> Blender +Y.
    """
    centre = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    extent = max(dimensions.x, dimensions.y, dimensions.z)

    world = bpy.context.scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.064, 0.075, 1.0)
    background.inputs["Strength"].default_value = 0.42

    bpy.ops.mesh.primitive_plane_add(size=max(dimensions.x, dimensions.y) * 3.2,
                                     location=(centre.x, centre.y, minimum.z - 0.025))
    ground = bpy.context.object
    ground.name = "qa_ground"
    material = bpy.data.materials.new("qa_ground_material")
    material.diffuse_color = (0.12, 0.14, 0.16, 1.0)
    material.roughness = 0.94
    ground.data.materials.append(material)

    light_scale = 0.35 if asset_id == "s1b_radio_operator_statue" else 1.0

    bpy.ops.object.light_add(type="AREA")
    key = bpy.context.object
    key.name = "qa_key"
    key.data.energy = 1400.0 * light_scale
    key.data.shape = "DISK"
    key.data.size = extent * 0.85
    key.location = centre + Vector((-extent * 0.85, extent * 1.05, extent * 1.45))
    look_at(key, centre)

    bpy.ops.object.light_add(type="AREA")
    fill = bpy.context.object
    fill.name = "qa_fill"
    fill.data.energy = 850.0 * light_scale
    fill.data.size = extent * 0.72
    fill.location = centre + Vector((extent * 1.15, extent * 0.55, extent * 0.75))
    look_at(fill, centre)

    bpy.ops.object.light_add(type="AREA")
    rim = bpy.context.object
    rim.name = "qa_rim"
    rim.data.energy = 1100.0 * light_scale
    rim.data.size = extent * 0.55
    rim.location = centre + Vector((0.0, -extent * 1.20, extent * 1.10))
    look_at(rim, centre)

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "qa_camera"
    camera.data.lens = 64.0 if asset_id == "s1b_radio_operator_statue" else 58.0
    camera.data.sensor_width = 36.0
    target = Vector((centre.x, centre.y, minimum.z + dimensions.z * 0.46))
    if asset_id == "s1b_radio_operator_statue":
        camera.location = target + Vector((-extent * 0.72, extent * 1.90, extent * 0.68))
    else:
        camera.location = target + Vector((extent * 1.05, extent * 1.72, extent * 0.78))
    look_at(camera, target)
    bpy.context.scene.camera = camera


def render_preview(output: pathlib.Path) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filepath = str(output)
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(output)
    scene.view_settings.look = "AgX - Medium High Contrast"
    bpy.ops.render.render(write_still=True)


def main() -> None:
    BLEND_DIR.mkdir(parents=True, exist_ok=True)
    # The checked-in source file is the canonical editable copy; Blender's local
    # numbered backup would duplicate every binary and is intentionally disabled.
    bpy.context.preferences.filepaths.save_version = 0
    report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    review: list[dict] = []
    for asset in report["assets"]:
        glb_path = ROOT / asset["relative_file"]
        clear_scene()
        bpy.ops.import_scene.gltf(filepath=str(glb_path))
        imported = mesh_objects()
        if not imported:
            raise RuntimeError(f"No mesh imported from {glb_path}")
        action_names = sorted(action.name for action in bpy.data.actions)
        if action_names:
            final_frame = max(
                math.ceil(action.frame_range[1])
                for action in bpy.data.actions
            )
            bpy.context.scene.frame_end = max(bpy.context.scene.frame_start, final_frame)
            bpy.context.scene.frame_set(bpy.context.scene.frame_end)
            bpy.context.view_layer.update()
        minimum, maximum = bounds(imported)
        triangles = sum(len(obj.data.loop_triangles) for obj in imported)
        materials = {slot.material.name for obj in imported for slot in obj.material_slots if slot.material}
        images = {image.name for image in bpy.data.images if image.type == "IMAGE" and image.name != "Render Result"}

        # Save only the authored model. Embedded images are packed for portability.
        bpy.ops.file.pack_all()
        source_path = BLEND_DIR / f"{glb_path.stem}_source.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(source_path), compress=True)

        add_review_world(minimum, maximum, asset["asset_id"])
        image_dir = glb_path.parent.parent / "images"
        version_match = re.search(r"_(v\d{3})$", glb_path.stem)
        version = version_match.group(1) if version_match else "v001"
        base_name = re.sub(r"_v\d{3}$", "", glb_path.stem)
        preview_name = f"{base_name}_preview_{version}.png"
        preview_path = image_dir / preview_name
        render_preview(preview_path)

        entry = {
            "asset_id": asset["asset_id"],
            "glb": glb_path.relative_to(ROOT).as_posix(),
            "blend": source_path.relative_to(ROOT).as_posix(),
            "preview": preview_path.relative_to(ROOT).as_posix(),
            "mesh_objects": len(imported),
            "triangles": triangles,
            "materials": len(materials),
            "images": len(images),
            "animations": len(action_names),
            "animation_names": action_names,
            "review_frame": bpy.context.scene.frame_current,
            "bounds_min": [round(value, 4) for value in minimum],
            "bounds_max": [round(value, 4) for value in maximum],
            "dimensions": [round(value, 4) for value in (maximum - minimum)],
        }
        review.append(entry)
        print(
            f"[BLENDER PASS] {entry['asset_id']} meshes={entry['mesh_objects']} "
            f"tris={entry['triangles']} mats={entry['materials']} images={entry['images']} "
            f"animations={entry['animations']}"
        )
    REVIEW_REPORT.write_text(json.dumps({"blender": bpy.app.version_string, "assets": review},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"review report: {REVIEW_REPORT}")


if __name__ == "__main__":
    main()
