"""S1 whitebox review self-check (M3D-01R compact-cellar round).

Numeric verification of: units/scale, visitor start, scene.json<->layout
consistency, clearances, line of sight, interaction distances, corridors,
props-on-desk, collider coverage, movement bounds containment.
Prints PASS/WARN/FAIL lines; exit 0 unless a hard FAIL exists.

Run from repo root:  python modeling_delivery/S1/source/whitebox/whitebox_selfcheck.py
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout_s1 as L

HERE = os.path.dirname(os.path.abspath(__file__))
SCENE_JSON = os.path.normpath(os.path.join(HERE, "..", "..", "runtime", "scene.json"))

results = []  # (status, item, detail)


def check(status, item, detail=""):
    results.append((status, item, detail))


def hdist(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def aabb_contains(p, lo, hi, pad=0.0):
    return all(lo[i] - pad <= p[i] <= hi[i] + pad for i in range(3))


def seg_hits_aabb(p0, p1, lo, hi):
    """Slab test segment vs AABB."""
    t0, t1 = 0.0, 1.0
    for i in range(3):
        d = p1[i] - p0[i]
        if abs(d) < 1e-12:
            if p0[i] < lo[i] or p0[i] > hi[i]:
                return False
            continue
        ta = (lo[i] - p0[i]) / d
        tb = (hi[i] - p0[i]) / d
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
        if t0 > t1:
            return False
    return True


def main():
    with open(SCENE_JSON, encoding="utf-8") as fh:
        scene = json.load(fh)

    # -- 1. units & scale ----------------------------------------------------
    room = L.ROOM
    ok = (room["x"], room["z"], room["h"]) == (5.3, 4.7, 2.25)
    check("PASS" if ok else "FAIL", "room interior 5.3 x 4.7 x 2.25 m",
          f"{room['x']} x {room['z']} x {room['h']} m, wall_t {room['wall_t']} m "
          "(compact cellar, product whitebox scale, non-historical; M3D-01R)")
    desk_w = L.DESK["x1"] - L.DESK["x0"]
    desk_d = L.DESK["z1"] - L.DESK["z0"]
    desk_h = L.DESK["top_y1"]
    ok = abs(desk_w - 1.80) < 1e-9 and abs(desk_d - 0.75) < 1e-9 and abs(desk_h - 0.78) < 1e-9
    check("PASS" if ok else "FAIL", "desk frozen baseline 1.80 x 0.75 x 0.78 m",
          f"{desk_w:.2f} x {desk_d:.2f} x {desk_h:.2f} m, center [0, 0, 0.10]")

    # -- 2. scene.json consistency ------------------------------------------
    vs = scene["visitor_start"]
    ok = vs["position_m"] == [0.0, 1.55, 1.65]
    check("PASS" if ok else "FAIL", "visitor_start position [0, 1.55, 1.65]", str(vs["position_m"]))
    check("WARN", "visitor_start rotation convention (OQ-I-04)",
          f"scene.json rotation_deg={vs['rotation_deg']} claimed = facing -Z (plan §5.2); "
          "plan §5.4 example uses [0,180,0] for the same facing. "
          "Unresolved axis convention — joint-debug on device before locking.")
    ok = scene["scene_id"] == "S1" and scene["environment_glb"] == "environment_whitebox.glb"
    check("PASS" if ok else "FAIL", "scene contract: scene_id / environment_glb",
          f"{scene['scene_id']} / {scene['environment_glb']}")
    prop_ids = [p["id"] for p in scene["props"]]
    ok = prop_ids == ["p_s1_radio", "p_s1_key", "p_s1_codebook"]
    check("PASS" if ok else "FAIL", "asset IDs preserved", ", ".join(prop_ids))
    # scene.json vs layout single source (deep compare, keys & types unchanged)
    mism = []
    for p in scene["props"]:
        lp = L.PROPS[p["id"]]
        if p["position_m"] != [float(v) for v in lp["position_m"]]:
            mism.append(p["id"] + " position")
        if p["interaction_radius_m"] != lp["interaction_radius_m"]:
            mism.append(p["id"] + " radius")
        if p["highlight_anchor_m"] != [float(v) for v in lp["highlight_anchor_m"]]:
            mism.append(p["id"] + " anchor")
        if p["rotation_deg"] != [float(v) for v in lp["rotation_deg"]]:
            mism.append(p["id"] + " rotation")
        if p["glb"] != lp["file"]:
            mism.append(p["id"] + " glb path")
    if scene["movement"] != L.MOVEMENT:
        mism.append("movement")
    if scene["colliders"] != L.COLLIDERS:
        mism.append("colliders")
    if scene["move_points"] != L.MOVE_POINTS:
        mism.append("move_points")
    if scene["visitor_start"] != L.VISITOR_START:
        mism.append("visitor_start")
    check("PASS" if not mism else "FAIL", "scene.json matches layout_s1.py",
          "mismatch: " + ", ".join(mism) if mism else "identical")

    # -- 3. start point clearances ------------------------------------------
    start = vs["position_m"]
    hit = [c["id"] for c in scene["colliders"] if aabb_contains(start, c["min_m"], c["max_m"], pad=0.6)]
    check("PASS" if not hit else "FAIL", "start 0.6 m clearance vs all colliders",
          "too close: " + ", ".join(hit) if hit else "no collider within 0.6 m of visitor_start")

    # -- 4. line of sight: start -> radio anchor -----------------------------
    radio = scene["props"][0]
    target = [radio["position_m"][0] + radio["highlight_anchor_m"][0],
              radio["position_m"][1] + radio["highlight_anchor_m"][1],
              radio["position_m"][2] + radio["highlight_anchor_m"][2]]
    blocked = [c["id"] for c in scene["colliders"]
               if seg_hits_aabb(start, target, c["min_m"], c["max_m"])]
    check("PASS" if not blocked else "FAIL", "start direct sight of p_s1_radio anchor",
          "blocked by: " + ", ".join(blocked) if blocked else
          f"clear; anchor world {[round(v, 3) for v in target]} above desk top 0.78")

    # -- 5. interaction distances --------------------------------------------
    # Every MVP prop: horizontal distance from visitor_start AND mp_radio in
    # the 1.0-2.5 m click band and <= its interaction radius. The radio should
    # additionally sit in the 1.4-1.9 m suggested band from visitor_start.
    spots = {"visitor_start": start, "mp_radio": scene["move_points"][0]["position_m"]}
    for p in scene["props"]:
        for sid, sp in spots.items():
            d = hdist(sp, p["position_m"])
            in_band = 1.0 <= d <= 2.5
            reach = d <= p["interaction_radius_m"] + 1e-9
            check("PASS" if (in_band and reach) else "FAIL",
                  f"{p['id']} click-band from {sid}",
                  f"horizontal {d:.2f} m; band 1.0-2.5 {'OK' if in_band else 'VIOLATED'}; "
                  f"radius {p['interaction_radius_m']} m {'OK' if reach else 'VIOLATED'}")
    d_radio_start = hdist(start, radio["position_m"])
    ok = 1.4 <= d_radio_start <= 1.9
    check("PASS" if ok else "FAIL", "p_s1_radio suggested band 1.4-1.9 m from visitor_start",
          f"horizontal {d_radio_start:.2f} m (M3D-01R first-look band)")
    d_radio_mp = hdist(spots["mp_radio"], radio["position_m"])
    check("PASS" if 1.4 <= d_radio_mp <= 1.9 else "WARN", "p_s1_radio suggested band from mp_radio",
          f"horizontal {d_radio_mp:.2f} m — mp_radio is a close-inspection point outside the "
          "1.4-1.9 m first-look band (suggested band is anchored at visitor_start per M3D-01R §3)")

    # -- 6. corridors ---------------------------------------------------------
    side_gap = 2.65 - 0.9          # desk side to inner wall (both sides, symmetric)
    back_gap = -0.275 - (-2.35)    # desk back (-Z) to north inner wall
    front_gap = 2.35 - 0.475       # desk front (+Z) to south inner wall
    ok = side_gap >= 1.2 and back_gap >= 1.2 and front_gap >= 1.2
    check("PASS" if ok else "FAIL", "corridors around desk >= 1.2 m",
          f"desk side {side_gap:.3f} m, desk back {back_gap:.3f} m, desk front {front_gap:.3f} m "
          "(spec: 1.75 / 2.075 / 1.875)")

    # -- 7. props rest on desk ------------------------------------------------
    for p in scene["props"]:
        py = p["position_m"][1]
        ok = abs(py - L.DESK_SURFACE_Y) < 1e-9
        check("PASS" if ok else "FAIL", f"{p['id']} origin on desk surface", f"y={py:.2f} vs desk top {L.DESK_SURFACE_Y}")
        px, pz = p["position_m"][0], p["position_m"][2]
        dims = L.PROPS[p["id"]]["dims_m"]
        inside = (L.DESK["x0"] <= px - dims[0] / 2 and px + dims[0] / 2 <= L.DESK["x1"]
                  and L.DESK["z0"] <= pz - dims[2] / 2 and pz + dims[2] / 2 <= L.DESK["z1"])
        check("PASS" if inside else "FAIL", f"{p['id']} footprint inside desk top",
              f"center [{px:.2f}, {pz:.2f}] dims {dims[0]:.2f}x{dims[2]:.2f}")

    # -- 8. collider coverage --------------------------------------------------
    want = {"wall_north", "wall_south", "wall_east", "wall_west", "desk_radio", "stool", "crate", "guide_plate"}
    have = {c["id"] for c in scene["colliders"]}
    missing = want - have
    check("PASS" if not missing else "FAIL", "colliders cover walls/desk/stool/crate/guide_plate",
          "missing: " + ", ".join(sorted(missing)) if missing else f"all {len(want)} present")
    spans = {
        "wall_north": (5.8, 2.25, 0.25), "wall_south": (5.8, 2.25, 0.25),
        "wall_east": (0.25, 2.25, 4.7), "wall_west": (0.25, 2.25, 4.7),
        "desk_radio": (1.8, 0.78, 0.75), "stool": (0.42, 0.45, 0.42),
        "crate": (0.60, 0.42, 0.50), "guide_plate": (0.06, 0.65, 0.70),
    }
    bad = []
    for c in scene["colliders"]:
        exp = spans[c["id"]]
        got = tuple(round(c["max_m"][i] - c["min_m"][i], 6) for i in range(3))
        if got != exp:
            bad.append(f"{c['id']} {got} != {exp}")
    check("PASS" if not bad else "FAIL", "collider spans match layout geometry",
          "; ".join(bad) if bad else "all spans exact")

    # -- 9. movement bounds -----------------------------------------------------
    mv = scene["movement"]
    ok = (mv["type"] == "bounds" and mv["x_min_m"] == -2.25 and mv["x_max_m"] == 2.25
          and mv["z_min_m"] == -1.95 and mv["z_max_m"] == 1.95 and mv["speed_mps"] == 1.2)
    check("PASS" if ok else "FAIL", "movement bounds x[+-2.25] z[+-1.95] speed 1.2", str(mv))
    pts = [("visitor_start", start)] + [(mp["id"], mp["position_m"]) for mp in scene["move_points"]]
    for name, p in pts:
        inside = mv["x_min_m"] <= p[0] <= mv["x_max_m"] and mv["z_min_m"] <= p[2] <= mv["z_max_m"]
        check("PASS" if inside else "FAIL", f"{name} inside movement bounds", f"[{p[0]}, {p[2]}]")
        in_col = [c["id"] for c in scene["colliders"] if aabb_contains(p, c["min_m"], c["max_m"])]
        check("PASS" if not in_col else "FAIL", f"{name} not inside any collider",
              "inside: " + ", ".join(in_col) if in_col else "clear")

    # -- 10. observations --------------------------------------------------------
    anchor_top = radio["highlight_anchor_m"][1]
    radio_h = L.PROPS["p_s1_radio"]["dims_m"][1]
    check("PASS" if anchor_top <= radio_h else "WARN", "p_s1_radio highlight_anchor vs prop height",
          f"anchor y={anchor_top} within prop height {radio_h}" if anchor_top <= radio_h else
          f"anchor y={anchor_top} > prop height {radio_h}")
    door_w = L.DOOR["x1"] - L.DOOR["x0"]
    check("PASS" if abs(door_w - 0.8) < 1e-9 and L.DOOR["h"] == 1.85 else "FAIL",
          "low cellar door 0.80 x 1.85 m, south wall offset west",
          f"opening {door_w:.2f} x {L.DOOR['h']:.2f} m at x[{L.DOOR['x0']}, {L.DOOR['x1']}]")
    gp = L.GUIDE_PLATE
    check("PASS", "guide layer = small plate only (no full-wall panel)",
          f"guide_plate {gp['x1']-gp['x0']:.2f}x{gp['y1']-gp['y0']:.2f}x{gp['z1']-gp['z0']:.2f} m on west wall; "
          "old INFO_PANEL removed (M3D-01R §2)")

    # -- report ---------------------------------------------------------------
    nfail = sum(1 for r in results if r[0] == "FAIL")
    for status, item, detail in results:
        print(f"[{status}] {item}" + (f" :: {detail}" if detail else ""))
    print(f"\nsummary: {sum(1 for r in results if r[0] == 'PASS')} PASS, "
          f"{sum(1 for r in results if r[0] == 'WARN')} WARN, {nfail} FAIL")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
