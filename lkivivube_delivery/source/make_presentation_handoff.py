"""Calculate exact Kivicube static-ground layout values from model bounds."""

from __future__ import annotations

import json
import pathlib

from ground_contact_contracts import GROUND_CONTACTS, MODEL_CENTER_POLICY


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROFILES = HERE / "presentation_profiles.json"
BUILD_REPORT = HERE / "build_report.json"
OUTPUT = HERE / "presentation_handoff_report.json"


def main() -> None:
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
    builds = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    by_file = {entry["relative_file"]: entry for entry in builds["assets"]}
    results = []
    for profile in profiles["assets"]:
        asset_id = profile["asset_id"]
        contact = GROUND_CONTACTS[asset_id]
        build = by_file[profile["model"]]
        minimum = build["bounds_min"]
        maximum = build["bounds_max"]
        dimensions = [maximum[index] - minimum[index] for index in range(3)]
        width = dimensions[0]
        longest = max(dimensions)
        target_scale = profile["model_width_ratio"] / width

        anchor_x = profile["subject_anchor_uv"][0] - 0.5
        anchor_z = profile["subject_anchor_uv"][1] - 0.5
        model_center_x = (minimum[0] + maximum[0]) * 0.5
        # Authored front is -Z, so the frontmost point is bounds_min.z.
        position_x = anchor_x - model_center_x * target_scale
        position_z = anchor_z + minimum[2] * target_scale
        position_y = profiles["coordinate_contract"]["model_ground_y"]

        transformed_x = (
            position_x + minimum[0] * target_scale,
            position_x + maximum[0] * target_scale,
        )
        transformed_z = (
            position_z + minimum[2] * target_scale,
            position_z + maximum[2] * target_scale,
        )
        footprint_inside = (
            transformed_x[0] >= -0.5
            and transformed_x[1] <= 0.5
            and transformed_z[0] >= -0.5
            and transformed_z[1] <= 0.5
        )
        # Kivicube initially auto-fits the model's longest dimension to the
        # target long edge; this is the relative scale expected after that fit.
        scale_after_kivicube_auto_fit = (
            profile["model_width_ratio"] / (width / longest)
        )
        clearance = contact["perimeter_clearance_target_units"]
        ground_edge = max(
            transformed_x[1] - transformed_x[0] + clearance * 2,
            transformed_z[1] - transformed_z[0] + clearance * 2,
        )
        results.append(
            {
                "asset_id": asset_id,
                "ground_texture": {
                    "version": "v002",
                    "position": [
                        round((transformed_x[0] + transformed_x[1]) / 2.0, 6),
                        profiles["coordinate_contract"]["ground_texture_y"],
                        round((transformed_z[0] + transformed_z[1]) / 2.0, 6),
                    ],
                    "rotation_degrees": [0.0, 0.0, 0.0],
                    "size_target_units": [round(ground_edge, 6), round(ground_edge, 6)],
                    "material_mode": "unlit",
                    "contact_bridge": "matching_ground_material_family_plus_subtle_ambient_occlusion",
                    "model_center_policy": MODEL_CENTER_POLICY,
                    "perimeter_clearance_target_units": clearance,
                    "front_axis": contact["front_axis"],
                    "stair_transition": {
                        "has_front_landing": contact["has_front_landing"],
                        "landing_width_ratio": contact["landing_width_ratio"],
                        "stair_geometry_zh": contact["stair_geometry_zh"],
                        "ground_approach_zh": contact["ground_approach_zh"],
                    },
                },
                "model": {
                    "file": profile["model"],
                    "position": [
                        round(position_x, 6),
                        round(position_y, 6),
                        round(position_z, 6),
                    ],
                    "rotation_degrees": [0.0, 0.0, 0.0],
                    "uniform_scale_target_units_per_model_metre": round(target_scale, 8),
                    "uniform_scale_after_kivicube_auto_fit": round(
                        scale_after_kivicube_auto_fit, 6
                    ),
                    "entry_animation": "none",
                    "auto_play": False,
                },
                "subject_anchor_uv": profile["subject_anchor_uv"],
                "target_footprint": {
                    "x": [round(value, 6) for value in transformed_x],
                    "z": [round(value, 6) for value in transformed_z],
                    "inside_square_target": footprint_inside,
                },
                "drawing_reference_source": profile["reference_source"],
                "placement_note": "The transformed model footprint is centred on the v002 ground plane. Physical stairs stay in the GLB and meet its front material approach; do not show the drawing reference after recognition.",
            }
        )
    result = {
        "schema": "red-wave-ar.kivicube-static-ground-handoff.v2",
        "coordinate_contract": profiles["coordinate_contract"],
        "sequence": profiles["sequence"],
        "assets": results,
    }
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
