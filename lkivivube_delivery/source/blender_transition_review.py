"""Render the final model standing on its square reference-photo card.

This is private visual QA.  Reference-card derivatives remain in `.build/`
because their public-display rights have not been cleared.
"""

from __future__ import annotations

import json
import math
import pathlib

import bpy
from mathutils import Vector


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROFILES = HERE / "presentation_profiles.json"
CARD_DIR = HERE / ".build" / "reference_cards"
OUTPUT_DIR = HERE / ".build" / "transition_review"
REPORT = HERE / ".build" / "transition_review_report.json"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.actions,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)
    for image in list(bpy.data.images):
        if image.users == 0 and image.name not in {"Render Result", "Viewer Node"}:
            bpy.data.images.remove(image)


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def mesh_objects(objects: list[bpy.types.Object]) -> list[bpy.types.Object]:
    return [obj for obj in objects if obj.type == "MESH"]


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[i] for point in corners) for i in range(3))),
        Vector(tuple(max(point[i] for point in corners) for i in range(3))),
    )


def add_reference_card(path: pathlib.Path) -> None:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.008))
    backing = bpy.context.object
    backing.name = "qa_reference_card_backing"
    backing.dimensions = (1.02, 1.02, 0.012)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    backing_material = bpy.data.materials.new("qa_reference_card_edge")
    backing_material.diffuse_color = (0.18, 0.035, 0.035, 1.0)
    backing_material.roughness = 0.95
    backing.data.materials.append(backing_material)

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, 0.0))
    card = bpy.context.object
    card.name = "qa_reference_photo_plane"
    # The image bottom faces +Y, matching the camera-facing/front edge and the
    # +Z target convention recorded in presentation_profiles.json.
    card.rotation_euler[2] = math.pi
    material = bpy.data.materials.new("qa_reference_photo")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    image_node = nodes.new("ShaderNodeTexImage")
    image_node.image = bpy.data.images.load(str(path), check_existing=False)
    principled = nodes.get("Principled BSDF")
    links.new(image_node.outputs["Color"], principled.inputs["Base Color"])
    principled.inputs["Roughness"].default_value = 0.93
    principled.inputs["Metallic"].default_value = 0.0
    card.data.materials.append(material)


def add_world() -> None:
    world = bpy.context.scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.035, 0.043, 0.052, 1.0)
    background.inputs["Strength"].default_value = 0.62

    bpy.ops.object.light_add(type="AREA", location=(-1.1, 0.95, 1.55))
    key = bpy.context.object
    key.data.energy = 620.0
    key.data.size = 1.2
    look_at(key, Vector((0.0, 0.10, 0.24)))

    bpy.ops.object.light_add(type="AREA", location=(1.2, 0.35, 0.85))
    fill = bpy.context.object
    fill.data.energy = 390.0
    fill.data.size = 1.0
    look_at(fill, Vector((0.0, 0.10, 0.22)))

    bpy.ops.object.camera_add(location=(1.08, 1.34, 1.04))
    camera = bpy.context.object
    camera.data.lens = 55.0
    look_at(camera, Vector((0.0, 0.10, 0.25)))
    bpy.context.scene.camera = camera


def render(path: pathlib.Path) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(path)
    scene.view_settings.look = "AgX - Medium High Contrast"
    bpy.ops.render.render(write_still=True)


def main() -> None:
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))["assets"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = []
    for profile in profiles:
        clear_scene()
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT / profile["model"]))
        imported_objects = [obj for obj in bpy.context.scene.objects if obj not in before]
        imported_meshes = mesh_objects(imported_objects)
        if not imported_meshes:
            raise RuntimeError(f"No mesh imported for {profile['asset_id']}")

        action_end = max(
            [math.ceil(action.frame_range[1]) for action in bpy.data.actions] or [1]
        )
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = action_end
        bpy.context.scene.frame_set(action_end)
        bpy.context.view_layer.update()
        minimum, maximum = bounds(imported_meshes)
        width = maximum.x - minimum.x

        stage = bpy.data.objects.new(f"{profile['asset_id']}_photo_plane_stage", None)
        bpy.context.collection.objects.link(stage)
        roots = [obj for obj in imported_objects if obj.parent is None]
        for root in roots:
            matrix = root.matrix_world.copy()
            root.parent = stage
            root.matrix_world = matrix
        uniform_scale = profile["model_width_ratio"] / width
        stage.scale = (uniform_scale,) * 3
        anchor_x = profile["subject_anchor_uv"][0] - 0.5
        anchor_front = profile["subject_anchor_uv"][1] - 0.5
        model_center_x = (minimum.x + maximum.x) * 0.5
        # Align the model's visible front edge—not its footprint centre—to the
        # subject baseline in the photo, so depth extends toward the card back.
        position_x = anchor_x - model_center_x * uniform_scale
        position_target_z = anchor_front - maximum.y * uniform_scale
        ground_clearance = 0.006
        stage.location = (position_x, position_target_z, ground_clearance)

        card_path = CARD_DIR / f"{profile['asset_id']}_reference_card_v002.jpg"
        add_reference_card(card_path)
        add_world()

        frames = [
            ("start", 1),
            ("mid", max(1, round(action_end * 0.55))),
            ("final", action_end),
        ]
        outputs = {}
        for label, frame in frames:
            bpy.context.scene.frame_set(frame)
            bpy.context.view_layer.update()
            output = OUTPUT_DIR / f"{profile['asset_id']}_{label}.png"
            render(output)
            outputs[label] = output.relative_to(ROOT).as_posix()
        report.append(
            {
                "asset_id": profile["asset_id"],
                "model_width_ratio": profile["model_width_ratio"],
                "model_position": [position_x, ground_clearance, position_target_z],
                "frames": outputs,
                "public_delivery": False,
            }
        )
        print(f"[TRANSITION REVIEW] {profile['asset_id']} frames={frames}")

    REPORT.write_text(
        json.dumps({"assets": report}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(REPORT)


if __name__ == "__main__":
    main()
