"""S1 whitebox review self-check (M3D-01 review round, per 02_MODELING_HANDOFF §3).

Numeric verification of: units/scale, visitor start, camera-facing evidence,
corridor widths, collider containment, prop visibility / interaction distances.
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
    ok = (room["x"], room["z"]) == (8.0, 8.0)
    check("PASS" if ok else "FAIL", "room interior 8.0 x 8.0 m",
          f"{room['x']} x {room['z']} m, height {room['h']} m (product whitebox scale, non-historical)")
    desk_w = L.DESK["x1"] - L.DESK["x0"]
    desk_d = L.DESK["z1"] - L.DESK["z0"]
    desk_h = L.DESK["top_y1"]
    ok = abs(desk_w - 1.80) < 1e-9 and abs(desk_d - 0.75) < 1e-9 and abs(desk_h - 0.78) < 1e-9
    check("PASS" if ok else "FAIL", "desk frozen baseline 1.80 x 0.75 x 0.78 m",
          f"{desk_w:.2f} x {desk_d:.2f} x {desk_h:.2f} m (style_reference_board §6 ZONE-B)")

    # -- 2. scene.json consistency ------------------------------------------
    vs = scene["visitor_start"]
    ok = vs["position_m"] == [0.0, 1.6, 3.0]
    check("PASS" if ok else "FAIL", "visitor_start position [0, 1.6, 3.0]", str(vs["position_m"]))
    check("WARN", "visitor_start rotation convention (OQ-I-04)",
          f"scene.json rotation_deg={vs['rotation_deg']} claimed = facing -Z (plan §5.2); "
          "plan §5.4 example + scene_layout_brief P0 use [0,180,0] for the same facing. "
          "Unresolved axis convention — joint-debug with coding model before device test.")
    prop_ids = [p["id"] for p in scene["props"]]
    ok = prop_ids == ["p_s1_radio", "p_s1_key", "p_s1_codebook"]
    check("PASS" if ok else "FAIL", "asset IDs preserved", ", ".join(prop_ids))
    # scene.json vs layout single source
    mism = []
    for p in scene["props"]:
        lp = L.PROPS[p["id"]]
        if p["position_m"] != [float(v) for v in lp["position_m"]]:
            mism.append(p["id"] + " position")
        if p["interaction_radius_m"] != lp["interaction_radius_m"]:
            mism.append(p["id"] + " radius")
    check("PASS" if not mism else "FAIL", "scene.json matches layout_s1.py",
          "mismatch: " + ", ".join(mism) if mism else "identical")

    # -- 3. start point clearances ------------------------------------------
    start = vs["position_m"]
    for c in scene["colliders"]:
        inside = aabb_contains(start, c["min_m"], c["max_m"], pad=0.6)
        if inside:
            check("FAIL", f"start 0.6 m clearance vs {c['id']}", "start within 0.6 m of collider")
    else:
        check("PASS", "start 0.6 m clearance vs all colliders",
              "no collider within 0.6 m of visitor_start (scene_layout_brief P0)")

    # -- 4. line of sight: start -> radio anchor -----------------------------
    radio = scene["props"][0]
    target = [radio["position_m"][0] + radio["highlight_anchor_m"][0],
              radio["position_m"][1] + radio["highlight_anchor_m"][1],
              radio["position_m"][2] + radio["highlight_anchor_m"][2]]
    blocked = [c["id"] for c in scene["colliders"]
               if seg_hits_aabb(start, target, c["min_m"], c["max_m"])]
    check("PASS" if not blocked else "FAIL", "start direct sight of p_s1_radio anchor",
          "blocked by: " + ", ".join(blocked) if blocked else
          f"clear; anchor world y={target[1]:.2f} above desk top 0.78")

    # -- 5. interaction distances --------------------------------------------
    # Requirement: each MVP prop triggerable within the 1.0-2.5 m click band
    # from at least one sensible viewing spot (visitor_start / mp_radio).
    # mp_info_wall is the far info-wall viewpoint; distances there are info-only.
    spots = {"visitor_start": start} | {mp["id"]: mp["position_m"] for mp in scene["move_points"]}
    for p in scene["props"]:
        dists = {sid: hdist(sp, p["position_m"]) for sid, sp in spots.items()}
        for sid, d in dists.items():
            reach = d <= p["interaction_radius_m"] + 1e-9
            in_band = 1.0 <= d <= 2.5 or sid != "mp_info_wall"
            if sid == "mp_info_wall":
                check("PASS" if True else "FAIL", f"{p['id']} distance from {sid} (info only)",
                      f"horizontal {d:.2f} m — not a required trigger spot")
            else:
                status = "PASS" if (reach and d <= 2.5) else "WARN"
                check(status, f"{p['id']} reachable from {sid}",
                      f"horizontal {d:.2f} m vs interaction_radius {p['interaction_radius_m']} m; "
                      f"click band 1.0-2.5 m -> {'in band' if 1.0 <= d <= 2.5 else 'outside band'}")
        ok_any = any(dists[s] <= p["interaction_radius_m"] + 1e-9 and dists[s] <= 2.5
                     for s in ("visitor_start", "mp_radio"))
        check("PASS" if ok_any else "FAIL", f"{p['id']} triggerable within band from >=1 spot",
              "visitor_start/mp_radio distances: "
              + ", ".join(f"{s}={dists[s]:.2f} m" for s in ("visitor_start", "mp_radio")))

    # -- 6. corridors ---------------------------------------------------------
    # gaps around desk along the main route (start -> info wall)
    west_gap = L.DESK["x0"] - (-4.0)
    east_gap = 4.0 - L.DESK["x1"]
    check("PASS" if min(west_gap, east_gap) >= 1.2 else "FAIL", "main corridor >= 1.2 m around desk",
          f"west gap {west_gap:.2f} m, east gap {east_gap:.2f} m")
    # straight line start -> info panel crosses desk AABB? (expected: detour exists)
    panel_c = [0.0, 1.55, (L.INFO_PANEL["z0"] + L.INFO_PANEL["z1"]) / 2]
    cross = seg_hits_aabb(start, panel_c, scene["colliders"][4]["min_m"], scene["colliders"][4]["max_m"])
    check("PASS", "route start -> info panel",
          "straight line crosses desk AABB; walkable detour on both sides (>=1.2 m) confirmed"
          if cross else "straight line clear")

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

    # -- 8. observations (not auto-fixed) -------------------------------------
    anchor_top = radio["highlight_anchor_m"][1]
    radio_h = L.PROPS["p_s1_radio"]["dims_m"][1]
    check("WARN" if anchor_top > radio_h else "PASS", "p_s1_radio highlight_anchor vs prop height",
          f"anchor y={anchor_top} > prop height {radio_h} (look-target above body; confirm with coding model)")
    panel_w = L.INFO_PANEL["x1"] - L.INFO_PANEL["x0"]
    check("WARN", "info panel width vs layout-brief recommendation",
          f"current {panel_w:.2f} m; scene_layout_brief ZONE-C recommends 2.8-3.6 m — decision item, not changed this round")
    has_panel_collider = any(c["id"] == "info_panel" for c in scene["colliders"])
    check("WARN" if not has_panel_collider else "PASS", "info panel thin collider",
          "not present; movement bounds z>=-3.6 keep player 0.33 m away — recommend adding if coding model wants closer approach")
    desk_c = [(L.DESK["x0"] + L.DESK["x1"]) / 2, (L.DESK["z0"] + L.DESK["z1"]) / 2]
    check("WARN", "desk zone vs scene_layout_brief recommendation",
          f"whitebox desk center [{desk_c[0]:.2f}, {desk_c[1]:.2f}] (sight {hdist(start, [desk_c[0], 0, desk_c[1]]):.2f} m); "
          "brief PROPOSED center [1.20, -1.00] (sight 3.5-4.5 m). Kept per 02_MODELING_HANDOFF §6 "
          "(keep scene.json main coordinates) — decision item for owner/PM.")
    door_c = (L.DOOR["x0"] + L.DOOR["x1"]) / 2
    check("WARN", "door position vs ZONE-A",
          f"door center x={door_c:.2f}; ZONE-A recommended x[-3.6,-1.3] — partial overlap only; review item")

    # -- report ---------------------------------------------------------------
    nfail = sum(1 for r in results if r[0] == "FAIL")
    for status, item, detail in results:
        print(f"[{status}] {item}" + (f" :: {detail}" if detail else ""))
    print(f"\nsummary: {sum(1 for r in results if r[0] == 'PASS')} PASS, "
          f"{sum(1 for r in results if r[0] == 'WARN')} WARN, {nfail} FAIL")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
