"""Minimal glTF 2.0 binary (GLB) writer for the Red Wave AR whitebox stage.

Convention (project contract, plan v1.2 §5.2 / §5.9):
- Y-up, right-handed, -Z forward, 1 unit = 1 meter.
- Prop origin at bottom center of the prop footprint, front faces -Z.
- Root nodes keep identity transform (unit scale, zero rotation).

Only POSITION + NORMAL + uint16 indices, pbrMetallicRoughness materials,
no textures. Flat-shaded solids; every mesh is a closed solid so
single-sided rendering is safe.
"""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field

import numpy as np


# ---------------------------------------------------------------- primitives

class MeshBuilder:
    """Accumulates flat-shaded triangles (positions, normals, indices)."""

    def __init__(self) -> None:
        self.positions: list[tuple[float, float, float]] = []
        self.normals: list[tuple[float, float, float]] = []
        self.indices: list[int] = []

    def add_box(self, lo: tuple[float, float, float], hi: tuple[float, float, float]) -> None:
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        # (normal, 4 corners CCW seen from outside)
        faces = [
            ((0.0, 0.0, 1.0), [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]),
            ((0.0, 0.0, -1.0), [(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)]),
            ((0.0, 1.0, 0.0), [(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)]),
            ((0.0, -1.0, 0.0), [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]),
            ((1.0, 0.0, 0.0), [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]),
            ((-1.0, 0.0, 0.0), [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)]),
        ]
        for normal, corners in faces:
            base = len(self.positions)
            self.positions.extend(corners)
            self.normals.extend([normal] * 4)
            self.indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    def add_cylinder_y(self, center: tuple[float, float, float], radius: float, height: float, segments: int = 12) -> None:
        """Cylinder along Y, flat-shaded, capped. `center` is the geometric center."""
        cx, cy, cz = center
        h2 = height / 2.0
        # side quads
        for i in range(segments):
            a0 = 2.0 * np.pi * i / segments
            a1 = 2.0 * np.pi * (i + 1) / segments
            am = 0.5 * (a0 + a1)
            n = (float(np.cos(am)), 0.0, float(np.sin(am)))
            c0, s0 = float(np.cos(a0)), float(np.sin(a0))
            c1, s1 = float(np.cos(a1)), float(np.sin(a1))
            v = [
                (cx + radius * c0, cy - h2, cz + radius * s0),
                (cx + radius * c1, cy - h2, cz + radius * s1),
                (cx + radius * c1, cy + h2, cz + radius * s1),
                (cx + radius * c0, cy + h2, cz + radius * s0),
            ]
            base = len(self.positions)
            self.positions.extend(v)
            self.normals.extend([n] * 4)
            self.indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])
        # caps (separate verts, fan around center)
        for sign, ny in ((1.0, 1.0), (-1.0, -1.0)):
            base = len(self.positions)
            self.positions.append((cx, cy + sign * h2, cz))
            self.normals.append((0.0, ny, 0.0))
            for i in range(segments):
                a = 2.0 * np.pi * i / segments
                self.positions.append((cx + radius * float(np.cos(a)), cy + sign * h2, cz + radius * float(np.sin(a))))
                self.normals.append((0.0, ny, 0.0))
            for i in range(segments):
                i0 = base + 1 + i
                i1 = base + 1 + (i + 1) % segments
                if sign > 0:
                    self.indices.extend([base, i1, i0])  # CCW from +Y
                else:
                    self.indices.extend([base, i0, i1])  # CCW from -Y


# ---------------------------------------------------------------- glTF scene

@dataclass
class Material:
    name: str
    base_color: tuple[float, float, float]
    metallic: float = 0.0
    roughness: float = 0.9


@dataclass
class Mesh:
    name: str
    builder: MeshBuilder
    material_index: int


@dataclass
class Node:
    name: str
    mesh_index: int | None = None
    translation: tuple[float, float, float] | None = None
    children: list["Node"] = field(default_factory=list)


def _pad4(data: bytes, pad: bytes) -> bytes:
    rem = len(data) % 4
    return data if rem == 0 else data + pad * (4 - rem)


def write_glb(path: str, materials: list[Material], meshes: list[Mesh], roots: list[Node]) -> dict:
    """Write a GLB and return stats {size_bytes, triangles, vertices, materials}."""
    blob = bytearray()
    buffer_views: list[dict] = []
    accessors: list[dict] = []

    def add_accessor(array: np.ndarray, component_type: int, acc_type: str, target: int, with_minmax: bool = False) -> int:
        nonlocal blob
        raw = array.tobytes()
        offset = len(blob)
        blob.extend(raw)
        while len(blob) % 4:
            blob.append(0)
        buffer_views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(raw), "target": target})
        count = array.shape[0]
        acc: dict = {
            "bufferView": len(buffer_views) - 1,
            "componentType": component_type,
            "count": int(count),
            "type": acc_type,
        }
        if with_minmax:
            acc["min"] = [float(v) for v in array.min(axis=0)]
            acc["max"] = [float(v) for v in array.max(axis=0)]
        accessors.append(acc)
        return len(accessors) - 1

    gltf_meshes: list[dict] = []
    total_tris = 0
    total_verts = 0
    for m in meshes:
        pos = np.asarray(m.builder.positions, dtype=np.float32).reshape(-1, 3)
        nrm = np.asarray(m.builder.normals, dtype=np.float32).reshape(-1, 3)
        idx = np.asarray(m.builder.indices, dtype=np.uint16)
        if pos.shape[0] > 65535:
            raise ValueError(f"mesh {m.name} exceeds uint16 vertex budget")
        prim = {
            "attributes": {
                "POSITION": add_accessor(pos, 5126, "VEC3", 34962, with_minmax=True),
                "NORMAL": add_accessor(nrm, 5126, "VEC3", 34962),
            },
            "indices": add_accessor(idx, 5123, "SCALAR", 34963),
            "material": m.material_index,
            "mode": 4,
        }
        gltf_meshes.append({"name": m.name, "primitives": [prim]})
        total_tris += idx.shape[0] // 3
        total_verts += pos.shape[0]

    flat_nodes: list[dict] = []

    def add_node(n: Node) -> int:
        node: dict = {"name": n.name}
        if n.mesh_index is not None:
            node["mesh"] = n.mesh_index
        if n.translation is not None:
            node["translation"] = [float(v) for v in n.translation]
        flat_nodes.append(node)
        self_index = len(flat_nodes) - 1
        if n.children:
            node["children"] = [add_node(c) for c in n.children]
        return self_index

    root_indices = [add_node(r) for r in roots]

    gltf = {
        "asset": {"version": "2.0", "generator": "red-wave-ar whitebox generator 0.1 (pure-python)"},
        "scene": 0,
        "scenes": [{"name": "whitebox", "nodes": root_indices}],
        "nodes": flat_nodes,
        "meshes": gltf_meshes,
        "materials": [
            {
                "name": mat.name,
                "pbrMetallicRoughness": {
                    "baseColorFactor": [float(mat.base_color[0]), float(mat.base_color[1]), float(mat.base_color[2]), 1.0],
                    "metallicFactor": float(mat.metallic),
                    "roughnessFactor": float(mat.roughness),
                },
                "doubleSided": False,
            }
            for mat in materials
        ],
        "bufferViews": buffer_views,
        "accessors": accessors,
        "buffers": [{"byteLength": len(blob)}],
    }

    json_chunk = _pad4(json.dumps(gltf, separators=(",", ":")).encode("utf-8"), b"\x20")
    bin_chunk = _pad4(bytes(blob), b"\x00")
    total = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
    with open(path, "wb") as fh:
        fh.write(struct.pack("<III", 0x46546C67, 2, total))
        fh.write(struct.pack("<II", len(json_chunk), 0x4E4F534A))
        fh.write(json_chunk)
        fh.write(struct.pack("<II", len(bin_chunk), 0x004E4942))
        fh.write(bin_chunk)

    return {
        "size_bytes": total,
        "triangles": int(total_tris),
        "vertices": int(total_verts),
        "materials": len(materials),
    }
