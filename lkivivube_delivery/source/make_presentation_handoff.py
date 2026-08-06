"""Calculate exact Kivicube layout values from model bounds and photo anchors."""

from __future__ import annotations

import json
import pathlib


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
        results.append(
            {
                "asset_id": asset_id,
                "reference_photo": {
                    "source": profile["reference_source"],
                    "crop_uv": profile["reference_crop_uv"],
                    "position": [0.0, profiles["coordinate_contract"]["reference_photo_y"], 0.0],
                    "rotation_degrees": [0.0, 0.0, 0.0],
                    "long_edge_ratio": 1.0,
                    "card_mode": profile.get("reference_display_mode", "square_contain"),
                    "keep_visible_under_model": True,
                    "publish_status": profile["reference_publish_status"],
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
                    "entry_animation": "photo_emerge",
                    "auto_play": True,
                },
                "subject_anchor_uv": profile["subject_anchor_uv"],
                "target_footprint": {
                    "x": [round(value, 6) for value in transformed_x],
                    "z": [round(value, 6) for value in transformed_z],
                    "inside_square_target": footprint_inside,
                },
                "note": profile["transition_note"],
            }
        )
    result = {
        "schema": "red-wave-ar.kivicube-photo-plane-handoff.v1",
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
