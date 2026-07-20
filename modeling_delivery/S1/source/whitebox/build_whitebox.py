"""Build S1 whitebox deliverables: 4 GLBs + scene.json.

Run from repo root:  python modeling_delivery/S1/source/whitebox/build_whitebox.py
Outputs to modeling_delivery/S1/runtime/.

Compact-cellar revision (M3D-01R): 5.3 x 4.7 x 2.25 m room; review-grade
multi-material p_s1_radio; key / codebook placeholders unchanged.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout_s1 as L
from glb import Material, Mesh, MeshBuilder, Node, write_glb

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.normpath(os.path.join(HERE, "..", "..", "runtime"))


def shapes(spec):
    """Convert layout shape tuples into a MeshBuilder."""
    mb = MeshBuilder()
    for kind, args in spec:
        if kind == "box":
            mb.add_box(args[0], args[1])
        elif kind == "cyl":
            mb.add_cylinder_y(args[0], args[1], args[2])
        elif kind == "tube":
            mb.add_tube(args[0], args[1], args[2], args[3], args[4] if len(args) > 4 else True)
        elif kind == "rbox":
            mb.add_rbox(args[0], args[1], args[2])
        else:
            raise ValueError(kind)
    return mb


def make_box(lo, hi):
    return ("box", (tuple(lo), tuple(hi)))


def make_cyl(center, r, h):
    return ("cyl", (tuple(center), r, h))


def _as_list(shape):
    return shape if isinstance(shape, list) else [shape]


def build_environment():
    mat_index = {L.ENV_GRAY: 0, L.GUIDE_BLUE: 1}
    materials = [
        Material(L.ENV_GRAY, L.MATERIALS[L.ENV_GRAY], roughness=0.95),
        Material(L.GUIDE_BLUE, L.MATERIALS[L.GUIDE_BLUE], roughness=0.80),
    ]
    parts = L.build_env_parts(make_box, make_cyl)
    meshes = [Mesh(name, shapes(_as_list(shape)), mat_index[mat]) for name, mat, shape in parts]
    root = Node("env_s1_room", children=[Node(name, mesh_index=i) for i, (name, _, _) in enumerate(parts)])
    out = os.path.join(RUNTIME, "environment_whitebox.glb")
    stats = write_glb(out, materials, meshes, [root])
    stats["asset_id"] = "env_s1_room"
    stats["file"] = "environment_whitebox.glb"
    stats["dims_m"] = [5.8, 2.35, 5.2]  # incl. wall thickness / floor / ceiling slabs
    return stats


def build_prop(prop_id):
    cfg = L.PROPS[prop_id]
    meshes: list[Mesh] = []
    children: list[Node] = []

    if prop_id == "p_s1_radio":
        # review-grade multi-material branch (M3D-01R section 4)
        materials = [Material(k, m["base_color"], m["metallic"], m["roughness"])
                     for k, m in L.RADIO_MATERIALS.items()]
        mat_index = {k: i for i, k in enumerate(L.RADIO_MATERIALS)}
        for name, spec, mkey in L.build_radio_nodes():
            meshes.append(Mesh(name, shapes(spec), mat_index[mkey]))
            children.append(Node(name, mesh_index=len(meshes) - 1))
    else:
        materials = [Material(L.PROP_BROWN, L.MATERIALS[L.PROP_BROWN], roughness=0.85)]
        if prop_id == "p_s1_key":
            local = [("key_base", [make_box((-0.075, 0.0, -0.05), (0.075, 0.025, 0.05))]),
                     ("key_post", [make_cyl((0.0, 0.0425, 0.035), 0.008, 0.035)]),
                     ("key_contact", [make_cyl((0.0, 0.036, -0.030), 0.004, 0.022)])]
            for name, spec in local:
                meshes.append(Mesh(name, shapes(spec), 0))
                children.append(Node(name, mesh_index=len(meshes) - 1))
            # lever assembly in pivot-local space, attached at the pivot node
            lever_spec = [make_box((-0.005, -0.004, -0.080), (0.005, 0.004, 0.005)),
                          make_cyl((0.0, 0.012, -0.070), 0.011, 0.018)]
            meshes.append(Mesh("key_lever", shapes(lever_spec), 0))
            children.append(Node("key_lever", mesh_index=len(meshes) - 1, translation=L.KEY_LEVER_PIVOT))
        else:
            for name, shape in L.build_prop_meshes(prop_id, make_box, make_cyl):
                meshes.append(Mesh(name, shapes([shape]), 0))
                children.append(Node(name, mesh_index=len(meshes) - 1))

    root = Node(prop_id, children=children)
    rel = cfg["file"]
    out = os.path.join(RUNTIME, rel)
    stats = write_glb(out, materials, meshes, [root])
    stats["asset_id"] = prop_id
    stats["file"] = rel
    stats["dims_m"] = cfg["dims_m"]
    return stats


def build_scene_json():
    scene = {
        "schema_version": 1,
        "scene_id": "S1",
        "environment_glb": "environment_whitebox.glb",
        "visitor_start": L.VISITOR_START,
        "movement": L.MOVEMENT,
        "colliders": L.COLLIDERS,
        "move_points": L.MOVE_POINTS,
        "props": [
            {
                "id": pid,
                "glb": cfg["file"],
                "position_m": cfg["position_m"],
                "rotation_deg": cfg["rotation_deg"],
                "scale": cfg["scale"],
                "interaction_radius_m": cfg["interaction_radius_m"],
                "highlight_anchor_m": cfg["highlight_anchor_m"],
            }
            for pid, cfg in L.PROPS.items()
        ],
    }
    out = os.path.join(RUNTIME, "scene.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(scene, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return out


def main():
    os.makedirs(os.path.join(RUNTIME, "props"), exist_ok=True)
    all_stats = [build_environment()]
    for pid in ("p_s1_radio", "p_s1_key", "p_s1_codebook"):
        all_stats.append(build_prop(pid))
    scene_path = build_scene_json()
    print(json.dumps({"scene_json": scene_path, "assets": all_stats}, indent=2))


if __name__ == "__main__":
    main()
