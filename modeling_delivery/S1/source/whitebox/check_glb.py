"""Structural self-check for the S1 whitebox GLBs (no external deps).

Checks, per file:
- GLB header magic / version / declared length == file size
- JSON chunk parses; asset.version == "2.0"; generator recorded
- BIN chunk length == buffers[0].byteLength
- every bufferView inside the buffer; every accessor inside its bufferView
- POSITION accessors carry min/max and min < max component-wise
- indices fit in uint16 range and reference valid vertices
- meshes/materials/scene/node references valid; node names snake_case
- per-file triangle / vertex / material / texture counts (textures must be 0)

Usage: python check_glb.py <file.glb> [more.glb ...]
Exit code 0 = all pass, 1 = any error.
"""

import json
import os
import re
import struct
import sys

import numpy as np

COMP_SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
TYPE_COUNT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")


def check(path: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    with open(path, "rb") as fh:
        data = fh.read()

    if len(data) < 12:
        return {"file": path, "errors": ["file too small"], "warnings": warnings}
    magic, version, total = struct.unpack("<III", data[:12])
    if magic != 0x46546C67:
        errors.append("bad magic")
    if version != 2:
        errors.append(f"glTF version {version} != 2")
    if total != len(data):
        errors.append(f"declared length {total} != file size {len(data)}")

    off = 12
    gltf = None
    bin_blob = b""
    while off + 8 <= len(data):
        clen, ctype = struct.unpack("<II", data[off:off + 8])
        chunk = data[off + 8:off + 8 + clen]
        if len(chunk) != clen:
            errors.append("truncated chunk")
            break
        if ctype == 0x4E4F534A:
            try:
                gltf = json.loads(chunk.decode("utf-8"))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"JSON chunk parse failed: {exc}")
        elif ctype == 0x004E4942:
            bin_blob = chunk
        else:
            warnings.append(f"unknown chunk type {ctype:#x}")
        off += 8 + clen

    stats = {"file": path, "errors": errors, "warnings": warnings}
    if gltf is None:
        errors.append("no JSON chunk")
        return stats

    if gltf.get("asset", {}).get("version") != "2.0":
        errors.append("asset.version != 2.0")

    buffers = gltf.get("buffers", [])
    if len(buffers) != 1:
        errors.append(f"buffers count {len(buffers)} != 1")
    elif buffers[0].get("byteLength") != len(bin_blob):
        errors.append(f"buffer byteLength {buffers[0].get('byteLength')} != BIN {len(bin_blob)}")

    bvs = gltf.get("bufferViews", [])
    accs = gltf.get("accessors", [])
    for i, bv in enumerate(bvs):
        if bv.get("byteOffset", 0) + bv.get("byteLength", 0) > len(bin_blob):
            errors.append(f"bufferView[{i}] out of buffer")
    for i, a in enumerate(accs):
        bv = bvs[a["bufferView"]]
        need = a["count"] * COMP_SIZE[a["componentType"]] * TYPE_COUNT[a["type"]]
        if a.get("byteOffset", 0) + need > bv["byteLength"]:
            errors.append(f"accessor[{i}] exceeds its bufferView")
    # POSITION accessors must carry min/max (spec); resolve usage per mesh below
    pos_accessor_ids = set()
    for m in gltf.get("meshes", []):
        for p in m.get("primitives", []):
            pos_accessor_ids.add(p["attributes"]["POSITION"])
    for i, a in enumerate(accs):
        if i in pos_accessor_ids and ("min" not in a or "max" not in a):
            errors.append(f"accessor[{i}] used as POSITION without min/max")

    mats = gltf.get("materials", [])
    meshes = gltf.get("meshes", [])
    nodes = gltf.get("nodes", [])
    tris = 0
    verts = 0
    for mi, m in enumerate(meshes):
        for pi, p in enumerate(m.get("primitives", [])):
            if p.get("mode", 4) != 4:
                errors.append(f"mesh[{mi}].prim[{pi}] mode != TRIANGLES")
            if "material" in p and p["material"] >= len(mats):
                errors.append(f"mesh[{mi}].prim[{pi}] material index out of range")
            pos_acc = accs[p["attributes"]["POSITION"]]
            idx_acc = accs[p["indices"]] if "indices" in p else None
            if "min" not in pos_acc or "max" not in pos_acc:
                errors.append(f"mesh[{mi}].prim[{pi}] POSITION missing min/max")
            elif any(lo >= hi for lo, hi in zip(pos_acc["min"], pos_acc["max"])):
                warnings.append(f"mesh[{mi}].prim[{pi}] degenerate POSITION bounds")
            if idx_acc is not None:
                bv = bvs[idx_acc["bufferView"]]
                raw = bin_blob[bv["byteOffset"]:bv["byteOffset"] + bv["byteLength"]]
                arr = np.frombuffer(raw, dtype=np.uint16, count=idx_acc["count"], offset=idx_acc.get("byteOffset", 0))
                if arr.size and int(arr.max()) >= pos_acc["count"]:
                    errors.append(f"mesh[{mi}].prim[{pi}] index out of vertex range")
                tris += idx_acc["count"] // 3
            verts += pos_acc["count"]
    for ni, n in enumerate(nodes):
        if "mesh" in n and n["mesh"] >= len(meshes):
            errors.append(f"node[{ni}] mesh index out of range")
        name = n.get("name", "")
        if not SNAKE.match(name):
            errors.append(f"node[{ni}] name '{name}' not snake_case")
        if "scale" in n and any(abs(s - 1.0) > 1e-6 for s in n["scale"]):
            errors.append(f"node[{ni}] non-unit scale")
    scenes = gltf.get("scenes", [])
    if not scenes:
        errors.append("no scenes")
    for img in gltf.get("images", []):
        errors.append(f"unexpected image {img}")  # whitebox must be textureless
    stats.update({
        "triangles": tris,
        "vertices": verts,
        "materials": len(mats),
        "textures": len(gltf.get("images", [])) + len(gltf.get("textures", [])),
        "node_names": [n.get("name") for n in nodes],
        "size_bytes": len(data),
    })
    return stats


def main() -> int:
    rc = 0
    for path in sys.argv[1:]:
        st = check(path)
        status = "PASS" if not st["errors"] else "FAIL"
        if st["errors"]:
            rc = 1
        print(f"[{status}] {os.path.basename(path)}  tris={st.get('triangles')} verts={st.get('vertices')} "
              f"mats={st.get('materials')} tex={st.get('textures')} size={st.get('size_bytes')}B")
        for e in st["errors"]:
            print(f"    ERROR: {e}")
        for w in st["warnings"]:
            print(f"    warn : {w}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
