"""Render each static Kivicube GLB on its assigned v002 ground texture.

This is visual QA for material, scale and contact continuity.  It deliberately
uses the same static transforms stored in presentation_handoff_report.json;
the historical photo-reveal animation is not part of this review.
"""

from __future__ import annotations

import json
import pathlib

import bpy
from mathutils import Vector


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HANDOFF = HERE / "presentation_handoff_report.json"
OUTPUT_DIR = HERE / ".build" / "static_ground_review"
REPORT = OUTPUT_DIR / "static_ground_review_report.json"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(collection):
            if item.users == 0:
                collection.remove(item)


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[index] for point in points) for index in range(3))),
        Vector(tuple(max(point[index] for point in points) for index in range(3))),
    )


def setup_by_asset() -> dict[str, tuple[pathlib.Path, dict[str, object]]]:
    result: dict[str, tuple[pathlib.Path, dict[str, object]]] = {}
    for path in ROOT.glob("lkivivube_delivery/scenes/*/kivicube_package/*/kivicube_setup.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        result[data["asset_id"]] = (path, data)
    if len(result) != 9:
        raise RuntimeError(f"Expected 9 Kivicube setup files, found {len(result)}")
    return result


def add_ground(texture_path: pathlib.Path, ground: dict[str, object]) -> bpy.types.Object:
    position = ground["position"]
    size = ground["size_target_units"]
    # Kivicube uses XZ as its target plane with Y up. Blender uses XY with Z up.
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(position[0], position[2], 0.0))
    plane = bpy.context.object
    plane.name = "qa_v002_ground_unlit"
    plane.dimensions = (size[0], size[1], 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    material = bpy.data.materials.new("qa_v002_ground_texture")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    # Do not depend on Blender's version-specific default node set.  Blender
    # 5.1 can create an empty material here after repeated scene cleanup.
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    image_node = nodes.new("ShaderNodeTexImage")
    image_node.image = bpy.data.images.load(str(texture_path), check_existing=False)
    links.new(image_node.outputs["Color"], principled.inputs["Base Color"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    principled.inputs["Roughness"].default_value = 0.94
    plane.data.materials.append(material)
    return plane


def add_lights_and_camera(minimum: Vector, maximum: Vector, asset_id: str) -> None:
    span_xy = max(maximum.x - minimum.x, maximum.y - minimum.y, 0.8)
    height = max(maximum.z - minimum.z, 0.35)
    extent = max(span_xy, height)
    target = Vector(((minimum.x + maximum.x) / 2, (minimum.y + maximum.y) / 2, minimum.z + height * 0.34))

    world = bpy.context.scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.035, 0.043, 0.052, 1.0)
    background.inputs["Strength"].default_value = 0.45

    # Area-light energy follows the square of the review scale.  The static
    # Kivicube scene is usually around one target unit wide, unlike the source
    # GLBs measured in metres; fixed metre-scale lighting would overexpose it.
    # Kivicube/model front is -Z.  After the glTF-to-Blender coordinate
    # conversion used above, that front is Blender +Y, so front lighting and
    # review cameras must be placed on +Y.  The former -Y view rendered the
    # backs of the models in the 3×3 contact sheet.
    for location, energy, size in (
        (target + Vector((-span_xy, span_xy * 0.8, height * 1.4)), 30.0 * extent * extent, span_xy),
        (target + Vector((span_xy, span_xy * 0.25, height * 0.8)), 18.0 * extent * extent, span_xy * 0.8),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        look_at(light, target)

    # Front-evidence view presets.  They retain enough perspective to inspect
    # surface/ground contact without replacing each asset's documented main
    # reference angle.  S1B is deliberately a front-left three-quarter view:
    # the evidence specifies "person left-back, equipment right-front", not a
    # symmetric portrait.  S5A stays near frontal so the relief and plaque are
    # not hidden behind the figures.
    view = {
        "S1B": (-0.72, 1.90, 0.68),
        "S5A": (0.25, 1.85, 0.72),
    }.get(asset_id, (0.58, 1.75, 0.86))
    bpy.ops.object.camera_add(
        location=target + Vector((span_xy * view[0], span_xy * view[1], height * view[2]))
    )
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(span_xy * 2.2, height * 1.45)
    look_at(camera, target)
    bpy.context.scene.camera = camera


def render(output: pathlib.Path) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 620
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = str(output)
    scene.view_settings.look = "AgX - Medium High Contrast"
    bpy.ops.render.render(write_still=True)


def main() -> None:
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))["assets"]
    setups = setup_by_asset()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = []
    for entry in handoff:
        asset_id = entry["asset_id"]
        setup_path, setup = setups[asset_id]
        clear_scene()

        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT / entry["model"]["file"]))
        imported = [object_ for object_ in bpy.context.scene.objects if object_ not in before]
        meshes = [object_ for object_ in imported if object_.type == "MESH"]
        if not meshes:
            raise RuntimeError(f"No mesh imported for {asset_id}")

        # The last frame is the complete model.  Static Kivicube configuration
        # does not play it; this only neutralizes imported Blender actions for
        # an unambiguous full-geometry contact inspection.
        end_frame = max([round(action.frame_range[1]) for action in bpy.data.actions] or [1])
        bpy.context.scene.frame_set(end_frame)
        roots = [object_ for object_ in imported if object_.parent is None]
        stage = bpy.data.objects.new(f"{asset_id}_static_stage", None)
        bpy.context.collection.objects.link(stage)
        for root in roots:
            matrix = root.matrix_world.copy()
            root.parent = stage
            root.matrix_world = matrix

        model = entry["model"]
        target_position = model["position"]
        stage.scale = (model["uniform_scale_target_units_per_model_metre"],) * 3
        stage.location = (target_position[0], target_position[2], target_position[1])
        bpy.context.view_layer.update()

        ground = entry["ground_texture"]
        texture_path = setup_path.parent / setup["files"]["ground_texture"]
        plane = add_ground(texture_path, ground)
        bpy.context.view_layer.update()
        minimum, maximum = bounds(meshes + [plane])
        add_lights_and_camera(minimum, maximum, asset_id)

        output = OUTPUT_DIR / f"{asset_id}_ground_contact.png"
        render(output)
        report.append(
            {
                "asset_id": asset_id,
                "preview": output.relative_to(ROOT).as_posix(),
                "ground_texture": texture_path.relative_to(ROOT).as_posix(),
                "ground_material_mode": ground["material_mode"],
                "ground_size_target_units": ground["size_target_units"],
                "model_entry_animation": model["entry_animation"],
                "model_auto_play": model["auto_play"],
            }
        )
        print(f"[STATIC GROUND REVIEW] {asset_id}")

    REPORT.write_text(json.dumps({"assets": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(REPORT)


if __name__ == "__main__":
    main()
