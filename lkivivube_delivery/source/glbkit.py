"""Small dependency-light GLB construction kit for the Kivicube deliverables.

The project intentionally keeps the modeling source reproducible on machines
without Blender.  Geometry is assembled from low-poly closed primitives, merged
by material, and exported as glTF 2.0 binary.

Coordinate contract:
- right handed, Y up;
- one unit is one metre;
- the authored front faces -Z;
- origin is the bottom centre of the model footprint.
"""

from __future__ import annotations

import json
import math
import mimetypes
import pathlib
import struct
from dataclasses import dataclass

import numpy as np


def _norm(v: np.ndarray) -> np.ndarray:
    length = float(np.linalg.norm(v))
    return v / length if length > 1e-12 else np.array([0.0, 1.0, 0.0])


class MeshBuilder:
    """Accumulate flat-shaded triangles with optional texture coordinates."""

    def __init__(self) -> None:
        self.positions: list[tuple[float, float, float]] = []
        self.normals: list[tuple[float, float, float]] = []
        self.texcoords: list[tuple[float, float]] = []
        self.indices: list[int] = []

    @property
    def empty(self) -> bool:
        return not self.indices

    def _face(
        self,
        corners: list[tuple[float, float, float]],
        triangles: list[tuple[int, int, int]] | None = None,
        uvs: list[tuple[float, float]] | None = None,
        normal: tuple[float, float, float] | None = None,
    ) -> None:
        if len(corners) < 3:
            return
        if normal is None:
            a = np.asarray(corners[1], float) - np.asarray(corners[0], float)
            b = np.asarray(corners[2], float) - np.asarray(corners[0], float)
            normal = tuple(_norm(np.cross(a, b)))
        base = len(self.positions)
        self.positions.extend(corners)
        self.normals.extend([normal] * len(corners))
        self.texcoords.extend(uvs or [(0.0, 0.0)] * len(corners))
        triangles = triangles or [(0, i, i + 1) for i in range(1, len(corners) - 1)]
        self.indices.extend(base + index for tri in triangles for index in tri)

    def add_box(
        self,
        lo: tuple[float, float, float],
        hi: tuple[float, float, float],
    ) -> None:
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        faces = [
            ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0.0, 0.0, 1.0)),
            ([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], (0.0, 0.0, -1.0)),
            ([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], (0.0, 1.0, 0.0)),
            ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0.0, -1.0, 0.0)),
            ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1.0, 0.0, 0.0)),
            ([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], (-1.0, 0.0, 0.0)),
        ]
        for corners, normal in faces:
            self._face(corners, [(0, 1, 2), (0, 2, 3)], normal=normal)

    def add_box_center(
        self,
        center: tuple[float, float, float],
        size: tuple[float, float, float],
    ) -> None:
        cx, cy, cz = center
        sx, sy, sz = size
        self.add_box(
            (cx - sx / 2.0, cy - sy / 2.0, cz - sz / 2.0),
            (cx + sx / 2.0, cy + sy / 2.0, cz + sz / 2.0),
        )

    def add_box_rot_y(
        self,
        center: tuple[float, float, float],
        size: tuple[float, float, float],
        degrees: float,
    ) -> None:
        cx, cy, cz = center
        sx, sy, sz = size
        th = math.radians(degrees)
        c, s = math.cos(th), math.sin(th)

        def transform(point: tuple[float, float, float]) -> tuple[float, float, float]:
            x, y, z = point
            return (cx + c * x + s * z, cy + y, cz - s * x + c * z)

        hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
        local = [
            ([(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]),
            ([(hx, -hy, -hz), (-hx, -hy, -hz), (-hx, hy, -hz), (hx, hy, -hz)]),
            ([(-hx, hy, -hz), (-hx, hy, hz), (hx, hy, hz), (hx, hy, -hz)]),
            ([(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz)]),
            ([(hx, -hy, hz), (hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz)]),
            ([(-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz), (-hx, hy, -hz)]),
        ]
        for corners in local:
            self._face([transform(point) for point in corners], [(0, 1, 2), (0, 2, 3)])

    def add_rbox_x(
        self,
        center: tuple[float, float, float],
        size: tuple[float, float, float],
        degrees: float,
    ) -> None:
        cx, cy, cz = center
        sx, sy, sz = size
        th = math.radians(degrees)
        c, s = math.cos(th), math.sin(th)

        def transform(point: tuple[float, float, float]) -> tuple[float, float, float]:
            x, y, z = point
            return (cx + x, cy + c * y - s * z, cz + s * y + c * z)

        hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
        faces = [
            [(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)],
            [(hx, -hy, -hz), (-hx, -hy, -hz), (-hx, hy, -hz), (hx, hy, -hz)],
            [(-hx, hy, -hz), (-hx, hy, hz), (hx, hy, hz), (hx, hy, -hz)],
            [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz)],
            [(hx, -hy, hz), (hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz)],
            [(-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz), (-hx, hy, -hz)],
        ]
        for corners in faces:
            self._face([transform(point) for point in corners], [(0, 1, 2), (0, 2, 3)])

    def add_cylinder_y(
        self,
        center: tuple[float, float, float],
        radius: float,
        height: float,
        segments: int = 12,
        radius_z: float | None = None,
    ) -> None:
        cx, cy, cz = center
        rz = radius if radius_z is None else radius_z
        h2 = height / 2.0
        for index in range(segments):
            a0 = 2.0 * math.pi * index / segments
            a1 = 2.0 * math.pi * (index + 1) / segments
            p0 = (cx + radius * math.cos(a0), cy - h2, cz + rz * math.sin(a0))
            p1 = (cx + radius * math.cos(a1), cy - h2, cz + rz * math.sin(a1))
            p2 = (cx + radius * math.cos(a1), cy + h2, cz + rz * math.sin(a1))
            p3 = (cx + radius * math.cos(a0), cy + h2, cz + rz * math.sin(a0))
            self._face([p0, p1, p2, p3], [(0, 1, 2), (0, 2, 3)])
        bottom = [(cx + radius * math.cos(2 * math.pi * i / segments), cy - h2,
                   cz + rz * math.sin(2 * math.pi * i / segments)) for i in reversed(range(segments))]
        top = [(cx + radius * math.cos(2 * math.pi * i / segments), cy + h2,
                cz + rz * math.sin(2 * math.pi * i / segments)) for i in range(segments)]
        self._face(bottom, normal=(0.0, -1.0, 0.0))
        self._face(top, normal=(0.0, 1.0, 0.0))

    def add_tube(
        self,
        p0: tuple[float, float, float],
        p1: tuple[float, float, float],
        radius: float,
        segments: int = 8,
        cap: bool = True,
    ) -> None:
        start = np.asarray(p0, float)
        end = np.asarray(p1, float)
        axis = end - start
        length = float(np.linalg.norm(axis))
        if length < 1e-9:
            return
        along = axis / length
        reference = np.array([0.0, 1.0, 0.0]) if abs(along[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
        u = _norm(np.cross(along, reference))
        v = np.cross(along, u)

        def ring(point: np.ndarray, angle: float) -> tuple[float, float, float]:
            return tuple(point + radius * (math.cos(angle) * u + math.sin(angle) * v))

        for index in range(segments):
            a0 = 2.0 * math.pi * index / segments
            a1 = 2.0 * math.pi * (index + 1) / segments
            self._face(
                [ring(start, a0), ring(start, a1), ring(end, a1), ring(end, a0)],
                [(0, 1, 2), (0, 2, 3)],
            )
        if cap:
            start_ring = [ring(start, 2.0 * math.pi * i / segments) for i in reversed(range(segments))]
            end_ring = [ring(end, 2.0 * math.pi * i / segments) for i in range(segments)]
            self._face(start_ring, normal=tuple(-along))
            self._face(end_ring, normal=tuple(along))

    def add_uv_sphere(
        self,
        center: tuple[float, float, float],
        radii: tuple[float, float, float],
        segments: int = 12,
        rings: int = 6,
    ) -> None:
        cx, cy, cz = center
        rx, ry, rz = radii
        for ring in range(rings):
            p0 = -math.pi / 2.0 + math.pi * ring / rings
            p1 = -math.pi / 2.0 + math.pi * (ring + 1) / rings
            for segment in range(segments):
                t0 = 2.0 * math.pi * segment / segments
                t1 = 2.0 * math.pi * (segment + 1) / segments

                def point(phi: float, theta: float) -> tuple[float, float, float]:
                    cp = math.cos(phi)
                    return (
                        cx + rx * cp * math.cos(theta),
                        cy + ry * math.sin(phi),
                        cz + rz * cp * math.sin(theta),
                    )

                a, b, c, d = point(p0, t0), point(p0, t1), point(p1, t1), point(p1, t0)
                self._face([a, b, c, d], [(0, 1, 2), (0, 2, 3)])

    def add_polygon_prism_z(
        self,
        polygon_xy: list[tuple[float, float]],
        z_front: float,
        z_back: float,
    ) -> None:
        """Extrude a simple CCW X/Y polygon between two Z planes."""
        front = [(x, y, z_front) for x, y in reversed(polygon_xy)]
        back = [(x, y, z_back) for x, y in polygon_xy]
        self._face(front, normal=(0.0, 0.0, -1.0))
        self._face(back, normal=(0.0, 0.0, 1.0))
        count = len(polygon_xy)
        for index in range(count):
            a = polygon_xy[index]
            b = polygon_xy[(index + 1) % count]
            self._face(
                [(a[0], a[1], z_front), (b[0], b[1], z_front),
                 (b[0], b[1], z_back), (a[0], a[1], z_back)],
                [(0, 1, 2), (0, 2, 3)],
            )

    def add_gable_roof(
        self,
        center: tuple[float, float, float],
        width: float,
        depth: float,
        rise: float,
        thickness: float = 0.12,
    ) -> None:
        """Closed low-poly two-slope roof, ridge along X."""
        cx, base_y, cz = center
        x0, x1 = cx - width / 2.0, cx + width / 2.0
        z0, z1 = cz - depth / 2.0, cz + depth / 2.0
        ridge = base_y + rise
        top = [
            (x0, base_y, z0), (x1, base_y, z0), (x1, ridge, cz), (x0, ridge, cz),
            (x0, ridge, cz), (x1, ridge, cz), (x1, base_y, z1), (x0, base_y, z1),
        ]
        self._face(top[:4], [(0, 1, 2), (0, 2, 3)])
        self._face(top[4:], [(0, 1, 2), (0, 2, 3)])
        # front/back gables and thin underside close the solid.
        self._face([(x0, base_y, z0), (x0, ridge, cz), (x0, base_y, z1)])
        self._face([(x1, base_y, z1), (x1, ridge, cz), (x1, base_y, z0)])
        self.add_box((x0, base_y - thickness, z0), (x1, base_y, z1))

    def add_textured_quad(
        self,
        corners: list[tuple[float, float, float]],
        uv_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
    ) -> None:
        # Callers provide front-facing quads in bottom-left, bottom-right,
        # top-right, top-left order.  The project front is -Z, so reverse the
        # default winding used by _face and supply the corresponding normal.
        u0, v0, u1, v1 = uv_rect
        c0, c1, c2 = (np.asarray(corners[index], float) for index in (0, 1, 2))
        normal = tuple(_norm(np.cross(c2 - c0, c1 - c0)))
        self._face(
            corners,
            [(0, 2, 1), (0, 3, 2)],
            # Front-facing -Z quads appear horizontally reflected after the
            # glTF Y-up -> Blender Z-up import rotation unless U is assigned
            # in the authored facing direction.
            uvs=[(u1, v1), (u0, v1), (u0, v0), (u1, v0)],
            normal=normal,
        )


@dataclass(frozen=True)
class Material:
    name: str
    base_color: tuple[float, float, float]
    metallic: float = 0.0
    roughness: float = 0.85
    texture_path: pathlib.Path | None = None
    alpha_mode: str = "OPAQUE"
    double_sided: bool = False


@dataclass
class Model:
    asset_id: str
    materials: list[Material]

    def __post_init__(self) -> None:
        self.builders = {material.name: MeshBuilder() for material in self.materials}

    def mesh(self, material_name: str) -> MeshBuilder:
        return self.builders[material_name]

    def normalize_ground(self) -> float:
        """Move the authored model so its lowest vertex touches the image plane.

        Image-AR models emerge from a reference-photo plane, so even a small
        negative Y value can make the object look buried in or detached from
        the card.  Returning the applied offset keeps the operation auditable.
        """
        positions = [
            position
            for builder in self.builders.values()
            for position in builder.positions
        ]
        if not positions:
            return 0.0
        minimum_y = min(position[1] for position in positions)
        if abs(minimum_y) <= 1e-9:
            return 0.0
        for builder in self.builders.values():
            builder.positions = [
                (x, y - minimum_y, z) for x, y, z in builder.positions
            ]
        return -minimum_y

    def export(self, path: pathlib.Path) -> dict:
        ground_offset = self.normalize_ground()
        stats = write_glb(path, self.asset_id, self.materials, self.builders)
        stats["ground_normalization_offset"] = ground_offset
        return stats


def _pad4(data: bytes, byte: bytes) -> bytes:
    remainder = len(data) % 4
    return data if remainder == 0 else data + byte * (4 - remainder)


def write_glb(
    path: pathlib.Path,
    asset_id: str,
    materials: list[Material],
    builders: dict[str, MeshBuilder],
) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = bytearray()
    buffer_views: list[dict] = []
    accessors: list[dict] = []

    def add_blob(raw: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(raw)
        while len(blob) % 4:
            blob.append(0)
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(raw)}
        if target is not None:
            view["target"] = target
        buffer_views.append(view)
        return len(buffer_views) - 1

    def add_accessor(
        array: np.ndarray,
        component_type: int,
        accessor_type: str,
        target: int | None,
        with_minmax: bool = False,
    ) -> int:
        view_index = add_blob(array.tobytes(), target)
        accessor = {
            "bufferView": view_index,
            "componentType": component_type,
            "count": int(array.shape[0]),
            "type": accessor_type,
        }
        if with_minmax:
            minimum = np.atleast_1d(array.min(axis=0))
            maximum = np.atleast_1d(array.max(axis=0))
            accessor["min"] = [float(value) for value in minimum]
            accessor["max"] = [float(value) for value in maximum]
        accessors.append(accessor)
        return len(accessors) - 1

    textures: list[dict] = []
    images: list[dict] = []
    samplers: list[dict] = []
    texture_for_material: dict[int, int] = {}
    for material_index, material in enumerate(materials):
        if material.texture_path is None:
            continue
        texture_data = material.texture_path.read_bytes()
        mime = mimetypes.guess_type(material.texture_path.name)[0] or "image/png"
        image_view = add_blob(texture_data)
        images.append({"name": f"{material.name}_image", "bufferView": image_view, "mimeType": mime})
        samplers.append({"magFilter": 9729, "minFilter": 9987, "wrapS": 33071, "wrapT": 33071})
        textures.append({
            "name": f"{material.name}_texture",
            "sampler": len(samplers) - 1,
            "source": len(images) - 1,
        })
        texture_for_material[material_index] = len(textures) - 1

    gltf_materials: list[dict] = []
    for index, material in enumerate(materials):
        pbr = {
            "baseColorFactor": [
                float(material.base_color[0]), float(material.base_color[1]),
                float(material.base_color[2]), 1.0,
            ],
            "metallicFactor": float(material.metallic),
            "roughnessFactor": float(material.roughness),
        }
        if index in texture_for_material:
            pbr["baseColorTexture"] = {"index": texture_for_material[index]}
        entry = {
            "name": material.name,
            "pbrMetallicRoughness": pbr,
            "doubleSided": material.double_sided,
        }
        if material.alpha_mode != "OPAQUE":
            entry["alphaMode"] = material.alpha_mode
            entry["alphaCutoff"] = 0.3
        gltf_materials.append(entry)

    gltf_meshes: list[dict] = []
    nodes: list[dict] = [{"name": asset_id, "children": []}]
    total_triangles = 0
    total_vertices = 0
    used_materials = 0
    all_positions: list[np.ndarray] = []
    for material_index, material in enumerate(materials):
        builder = builders[material.name]
        if builder.empty:
            continue
        positions = np.asarray(builder.positions, dtype=np.float32).reshape(-1, 3)
        all_positions.append(positions)
        normals = np.asarray(builder.normals, dtype=np.float32).reshape(-1, 3)
        texcoords = np.asarray(builder.texcoords, dtype=np.float32).reshape(-1, 2)
        if positions.shape[0] > 65535:
            raise ValueError(f"{asset_id}:{material.name} exceeds uint16 vertex limit")
        indices = np.asarray(builder.indices, dtype=np.uint16)
        attributes = {
            "POSITION": add_accessor(positions, 5126, "VEC3", 34962, with_minmax=True),
            "NORMAL": add_accessor(normals, 5126, "VEC3", 34962),
            "TEXCOORD_0": add_accessor(texcoords, 5126, "VEC2", 34962),
        }
        primitive = {
            "attributes": attributes,
            "indices": add_accessor(indices, 5123, "SCALAR", 34963),
            "material": material_index,
            "mode": 4,
        }
        gltf_meshes.append({"name": f"{asset_id}_{material.name}", "primitives": [primitive]})
        nodes.append({"name": f"{asset_id}_{material.name}", "mesh": len(gltf_meshes) - 1})
        nodes[0]["children"].append(len(nodes) - 1)
        total_triangles += int(indices.shape[0] // 3)
        total_vertices += int(positions.shape[0])
        used_materials += 1

    if not all_positions:
        raise ValueError(f"{asset_id} contains no geometry")
    combined_positions = np.concatenate(all_positions, axis=0)
    bounds_min = combined_positions.min(axis=0)
    bounds_max = combined_positions.max(axis=0)

    # One cross-platform transform animation turns the model from a shallow
    # relief into full 3D while its bottom remains locked to the reference
    # image.  All scale components remain positive to satisfy Kivicube rules.
    emergence_times = np.asarray([0.0, 0.16, 0.70, 1.10, 1.40], dtype=np.float32)
    emergence_scales = np.asarray(
        [
            (0.98, 0.025, 0.08),
            (0.99, 0.10, 0.16),
            (1.00, 0.72, 0.70),
            (1.00, 1.05, 1.02),
            (1.00, 1.00, 1.00),
        ],
        dtype=np.float32,
    )
    animation = {
        "name": "photo_emerge",
        "samplers": [{
            "input": add_accessor(emergence_times, 5126, "SCALAR", None, with_minmax=True),
            "output": add_accessor(emergence_scales, 5126, "VEC3", None, with_minmax=True),
            "interpolation": "LINEAR",
        }],
        "channels": [{"sampler": 0, "target": {"node": 0, "path": "scale"}}],
        "extras": {
            "purpose": "reference_photo_plane_to_full_3d",
            "keep_reference_photo_visible": True,
            "bottom_locked_to_image_plane": True,
        },
    }

    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "red-wave-ar kivicube procedural model pipeline 1.1",
            "copyright": "Project-authored low-poly geometry; reference images are not embedded",
        },
        "scene": 0,
        "scenes": [{"name": asset_id, "nodes": [0]}],
        "nodes": nodes,
        "meshes": gltf_meshes,
        "materials": gltf_materials,
        "bufferViews": buffer_views,
        "accessors": accessors,
        "buffers": [{"byteLength": len(blob)}],
        "animations": [animation],
        "extras": {
            "red_wave_ar_presentation": {
                "layout": "reference_photo_plane",
                "ground_plane_y": 0.0,
                "front_axis": "-Z",
                "entry_animation": "photo_emerge",
                "reference_photo_is_separate_asset": True,
            }
        },
    }
    if images:
        gltf["images"] = images
        gltf["textures"] = textures
        gltf["samplers"] = samplers

    json_chunk = _pad4(json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), b"\x20")
    bin_chunk = _pad4(bytes(blob), b"\x00")
    total = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
    with path.open("wb") as handle:
        handle.write(struct.pack("<III", 0x46546C67, 2, total))
        handle.write(struct.pack("<II", len(json_chunk), 0x4E4F534A))
        handle.write(json_chunk)
        handle.write(struct.pack("<II", len(bin_chunk), 0x004E4942))
        handle.write(bin_chunk)

    return {
        "asset_id": asset_id,
        "file": str(path),
        "size_bytes": total,
        "triangles": total_triangles,
        "vertices": total_vertices,
        "meshes": len(gltf_meshes),
        "materials": used_materials,
        "textures": len(images),
        "animations": 1,
        "bounds_min": [float(value) for value in bounds_min],
        "bounds_max": [float(value) for value in bounds_max],
    }
