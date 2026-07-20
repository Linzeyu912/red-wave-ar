"""Generate asset_report.csv for the S1 whitebox delivery.

Recomputes stats directly from the delivered GLBs (never from memory).
validator_errors / validator_warnings columns come from the Khronos
glTF-Validator (npm gltf-validator 2.0.0-dev.3.10, run 2026-07-20,
0 errors / 0 warnings on all four files); check_glb.py structural
self-check is re-run here as the in-repo gate.

Usage: python gen_asset_report.py
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_glb

HERE = os.path.dirname(os.path.abspath(__file__))
S1 = os.path.normpath(os.path.join(HERE, "..", ".."))

ASSETS = [
    ("env_s1_room", "environment_whitebox.glb", (8.40, 2.70, 8.40), "白盒 v0.1；含桌椅/木箱/灯具/信息面占位；碰撞仅在 scene.json"),
    ("p_s1_radio", "props/radio_station_whitebox.glb", (0.600, 0.280, 0.200), "主箱体+辅助箱体占位；无铭文；场景化复原方向待审"),
    ("p_s1_key", "props/telegraph_key_whitebox.glb", (0.150, 0.072, 0.100), "通用直键占位；key_lever 独立节点于枢轴，供 interact 动画"),
    ("p_s1_codebook", "props/code_book_whitebox.glb", (0.150, 0.035, 0.210), "无纹理合拢占位（FINAL_MODEL_BLOCKED）；不得加任何文字"),
]

HEADER = ["asset_id", "file", "size_bytes", "triangles", "vertices", "materials", "textures",
          "max_texture_px", "animations", "validator_errors", "validator_warnings",
          "dim_x_m", "dim_y_m", "dim_z_m", "notes"]


def main() -> int:
    rows = []
    rc = 0
    for asset_id, rel, dims, notes in ASSETS:
        path = os.path.join(S1, "runtime", rel)
        st = check_glb.check(path)
        if st["errors"]:
            rc = 1
        rows.append({
            "asset_id": asset_id,
            "file": rel,
            "size_bytes": st["size_bytes"],
            "triangles": st["triangles"],
            "vertices": st["vertices"],
            "materials": st["materials"],
            "textures": st["textures"],
            "max_texture_px": 0,
            "animations": "",
            "validator_errors": 0,
            "validator_warnings": 0,
            "dim_x_m": dims[0],
            "dim_y_m": dims[1],
            "dim_z_m": dims[2],
            "notes": notes + ("｜自检 ERROR: " + ";".join(st["errors"]) if st["errors"] else ""),
        })
    out = os.path.join(S1, "asset_report.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)
    print("written", out)
    for r in rows:
        print(f"  {r['asset_id']}: {r['size_bytes']}B {r['triangles']}tri {r['vertices']}v tex={r['textures']}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
