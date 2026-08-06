"""Validate static ground/model placement for all Kivicube delivery packages."""

from __future__ import annotations

import json
import pathlib

from PIL import Image


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL_VALIDATION = HERE / "validation_report.json"
OUTPUT = HERE / "static_ground_validation_report.json"
EXPECTED_SEQUENCE = [
    "recognize_original_hand_drawn_image_target",
    "show_ground_texture_plane",
    "show_model_static",
    "start_narration",
]


def close_enough(actual: float, expected: float, tolerance: float = 1e-6) -> bool:
    return abs(actual - expected) <= tolerance


def validate_setup(path: pathlib.Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    asset_id = data.get("asset_id", path.parent.name)
    errors: list[str] = []
    if data.get("schema") != "red-wave-ar.kivicube-static-ground-package.v3":
        errors.append("unexpected schema")
    if [item.get("action") for item in data.get("display_sequence", [])] != EXPECTED_SEQUENCE:
        errors.append("display sequence is not static-ground flow")

    ground = data.get("ground_texture_plane", {})
    model = data.get("model", {})
    files = data.get("files", {})
    size = ground.get("size_target_units", [])
    position = ground.get("position", [])
    model_position = model.get("position", [])
    footprint = model.get("target_footprint", {})
    if len(size) != 2 or not close_enough(float(size[0]), float(size[1])):
        errors.append("ground is not square")
    if len(position) != 3 or not close_enough(float(position[1]), 0.002):
        errors.append("ground Y must be 0.002")
    if len(model_position) != 3 or not close_enough(float(model_position[1]), 0.004):
        errors.append("model Y must be 0.004")
    if ground.get("material_mode") != "unlit":
        errors.append("ground must use unlit material")
    if model.get("entry_animation") != "none" or model.get("auto_play") is not False:
        errors.append("model animation must be disabled")
    if "reference_reveal_plane" in data:
        errors.append("reference photo plane must not be configured")

    contract = data.get("reference_derived_surface_contract", {})
    if not isinstance(contract, dict) or not all(
        isinstance(contract.get(key), str) and contract[key].strip()
        for key in ("constraint_file", "front_evidence", "model_surface_evidence_zh", "ground_scope_zh")
    ):
        errors.append("missing reference-derived surface contract")
    elif not (ROOT / contract["constraint_file"]).exists():
        errors.append("surface contract constraint file is missing")

    x = footprint.get("x", [])
    z = footprint.get("z", [])
    if len(x) != 2 or len(z) != 2 or len(size) != 2:
        errors.append("missing target footprint")
    else:
        expected_edge = round(max(float(x[1]) - float(x[0]) + 0.20, float(z[1]) - float(z[0]) + 0.20), 6)
        if not close_enough(float(size[0]), expected_edge):
            errors.append(f"ground edge {size[0]} does not cover footprint with 0.10-unit border")

    texture = path.parent / str(files.get("ground_texture", ""))
    if not texture.exists():
        errors.append("ground texture file is missing")
    else:
        with Image.open(texture) as image:
            if image.size != (1024, 1024):
                errors.append(f"ground texture is {image.size}, expected 1024×1024")

    return {
        "asset_id": asset_id,
        "setup": path.relative_to(ROOT).as_posix(),
        "ground_texture": texture.relative_to(ROOT).as_posix() if texture.exists() else str(texture),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def main() -> None:
    setups = sorted(ROOT.glob("lkivivube_delivery/scenes/*/kivicube_package/*/kivicube_setup.json"))
    results = [validate_setup(path) for path in setups]
    model_report = json.loads(MODEL_VALIDATION.read_text(encoding="utf-8"))
    model_bottoms = [entry.get("ground_plane", {}).get("status") for entry in model_report.get("assets", [])]
    if len(results) != 9:
        raise RuntimeError(f"Expected 9 setup files, found {len(results)}")
    if model_report.get("status") != "PASS" or model_bottoms != ["PASS"] * 9:
        raise RuntimeError("GLB validation does not prove all nine model bottoms are at local Y=0")

    report = {
        "schema": "red-wave-ar.static-ground-validation.v1",
        "model_bottom_contract": "validation_report.json proves all nine GLBs have minimum local Y=0",
        "status": "PASS" if all(entry["status"] == "PASS" for entry in results) else "FAIL",
        "assets": results,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for entry in results:
        print(f"[{entry['status']}] {entry['asset_id']}")
    if report["status"] != "PASS":
        raise SystemExit(1)
    print(OUTPUT)


if __name__ == "__main__":
    main()
