#!/usr/bin/env python3
"""
metrics.py -- Week-5 ablation metrics for LiDAR-only / camera-only / fused (d26).

Run in venv_yolo.

  cd ~/Documents/workspace/sensor-fusion
  source venv_yolo/bin/activate
  python3 code/eval/metrics.py \
      --gt docs/gt \
      --runs code/eval/runs \
      --calib calibration/calib_T_lidar_camera_2026_05_26.json \
      --project-lidar-dir code/fusion \
      --out docs/d26_metrics

KEY CONVENTION (verified against frustum_fuse.py): the fused arm's range_m is the HORIZONTAL / BEV
range = hypot(x, y) from the LiDAR axis -- NOT 3D Euclidean (height is dropped). So:
- GT range must also be HORIZONTAL (env-2 "floor" measure type, not the 3D slant). env-1's coarse 3D
  values are close enough at the coarse tier. This script just compares range_m to whatever GT range
  is in the json -- so enter HORIZONTAL GT ranges.
- LiDAR-only range is computed here as hypot(x, y) of the box centre (same convention as fused).

PROJECTION: imports project_lidar (the SAME module frustum_fuse.py uses) so LiDAR-only matching uses
the exact projection that produced the fused output. Falls back to an autodetect if the import fails.
A self-check reports what fraction of source=="fused" centroids project inside their own box_xyxy
(must be high; if low, the projection / calib is wrong and LiDAR-only matching is unreliable).

WHAT THIS PRODUCES (frozen spec):
- presence_table.md   recall / precision / class-correctness per arm per env (camera==fused expected).
- range_error_table.md signed err (det - GT) per env AND per object; fused = source=="fused" subset;
                       LiDAR-only where it fires. Footnotes: GT tier + front-face-vs-centroid caveat.
- fused_rate_table.md  count(fused)/count(all YOLO boxes) per env, broken by reason.
- gate_sensitivity.md  LiDAR-only match counts at 0.50 / 0.75 / 1.00 m (0.75 primary).
- per_match.csv        one row per matched range pair (feeds figures.py).

SCHEMA (verified against frustum_fuse.py output + the GT schema; *_KEYS stay tolerant just in case):
- fused det: {class, conf, box_xyxy:[x1,y1,x2,y2], source:"fused"|"camera_only", reason(if cam-only),
  position_lidar:[x,y,z], extent, range_m, n_in_box, n_cluster, n_clusters}.  (range_m is HORIZONTAL.)
- GT obj:    {class, bbox_2d:[x1,y1,x2,y2], range_m_tape(float|null), occluded(bool), notes}.
- lidar det (demo.py dump): {class/label, score, center:[x,y,z] in LiDAR frame}.
"""

#region [Imports + CLI]
import argparse
import csv
import glob
import json
import math
import os
import re
import statistics
import sys

import numpy as np


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--calib", required=True)
    ap.add_argument("--project-lidar-dir", default="code/fusion",
                    help="dir containing project_lidar.py (same one frustum_fuse.py imports)")
    ap.add_argument("--direction", choices=["lidar2cam", "campose"], default="campose")
    ap.add_argument("--intrinsics-fx", type=float, default=335.13)
    ap.add_argument("--intrinsics-fy", type=float, default=359.35)
    ap.add_argument("--intrinsics-cx", type=float, default=486.26)
    ap.add_argument("--intrinsics-cy", type=float, default=291.70)
    ap.add_argument("--image-w", type=int, default=960)
    ap.add_argument("--image-h", type=int, default=600)
    ap.add_argument("--iou", type=float, default=0.50)
    ap.add_argument("--yolo-conf", type=float, default=0.25)
    ap.add_argument("--pp-score", type=float, default=0.30)
    ap.add_argument("--gates", default="0.50,0.75,1.00")
    ap.add_argument("--out", required=True)
    return ap.parse_args()
#endregion

#region [Class alias map (frozen)]
ALIAS = {
    "left monitor": "tv", "right monitor": "tv", "monitor": "tv", "tv": "tv",
    "person": "person", "person-in-chair": "person",
    "chair": "chair", "chair1": "chair", "chair2": "chair",
    "laptop": "laptop", "keyboard": "keyboard", "bottle": "bottle",
    "potted plant": "potted plant", "pottedplant": "potted plant",
    "trash bin": "trash bin", "box": "box",
}


def canon(c):
    if c is None:
        return None
    return ALIAS.get(str(c).strip().lower(), str(c).strip().lower())
#endregion

#region [Flexible field access]
def first_key(d, keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            return d[k]
    return None


BOX_KEYS = ["box_xyxy", "bbox_2d", "bbox", "xyxy", "box_2d", "box2d"]   # fused uses box_xyxy; GT uses bbox_2d
CLASS_KEYS = ["class", "label", "name", "cls", "category"]
CONF_KEYS = ["conf", "score", "confidence"]
SOURCE_KEYS = ["source", "src", "origin"]
REASON_KEYS = ["reason", "why", "camera_only_reason"]
RANGE_KEYS = ["range_m", "range", "distance_m", "dist"]
CENTER3D_KEYS = ["center", "box_center", "xyz", "position_lidar", "center_lidar", "loc"]


def det_box(d):
    b = first_key(d, BOX_KEYS)
    return [float(x) for x in b] if b is not None else None


def det_class(d):
    return first_key(d, CLASS_KEYS)


def det_conf(d):
    c = first_key(d, CONF_KEYS)
    return float(c) if c is not None else None
#endregion

#region [IoU + greedy 2D match]
def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    ua = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / ua if ua > 0 else 0.0


def greedy_match_2d(gts, dets, thr):
    pairs = []
    for gi, g in enumerate(gts):
        for di, d in enumerate(dets):
            if g["box"] is None or d["box"] is None:
                continue
            v = iou(g["box"], d["box"])
            if v >= thr:
                pairs.append((v, gi, di))
    pairs.sort(reverse=True)
    used_g, used_d, out = set(), set(), []
    for v, gi, di in pairs:
        if gi in used_g or di in used_d:
            continue
        used_g.add(gi)
        used_d.add(di)
        out.append((gi, di, v))
    return out
#endregion

#region [Path -> (env, pose, frame)]
def parse_key(path):
    p = path.replace("\\", "/")
    m_frame = re.search(r"(\d{5})", os.path.basename(p))
    frame = m_frame.group(1) if m_frame else os.path.splitext(os.path.basename(p))[0]
    env = "env2" if "env2" in p else ("env1" if "env1" in p else "unknown")
    m_pose = re.search(r"(pose\d+)", p)
    pose = m_pose.group(1) if m_pose else None
    return env, pose, frame


def key_str(env, pose, frame):
    return f"{env}/{pose}/{frame}" if pose else f"{env}/{frame}"
#endregion

#region [Loaders]
def load_gt(root):
    out = {}
    for f in sorted(glob.glob(os.path.join(root, "**", "*.json"), recursive=True)):
        try:
            data = json.load(open(f))
        except Exception as e:
            print(f"[gt] skip {f}: {e}")
            continue
        env, pose, frame = parse_key(f)
        objs = []
        for o in data.get("objects", []):
            objs.append({
                "box": [float(x) for x in o["bbox_2d"]] if o.get("bbox_2d") else None,
                "class": o.get("class"),
                "canon": canon(o.get("class")),
                "range": o.get("range_m_tape"),
                "occluded": bool(o.get("occluded")),
            })
        out[key_str(env, pose, frame)] = {"env": env, "pose": pose, "frame": frame, "objects": objs}
    return out


def load_run(subdir):
    out = {}
    if not os.path.isdir(subdir):
        print(f"[run] missing dir {subdir} (ok if that arm not run yet)")
        return out
    for f in sorted(glob.glob(os.path.join(subdir, "**", "*.json"), recursive=True)):
        try:
            data = json.load(open(f))
        except Exception as e:
            print(f"[run] skip {f}: {e}")
            continue
        dets = data.get("detections") if isinstance(data, dict) else data
        if dets is None and isinstance(data, dict):
            dets = next((v for v in data.values() if isinstance(v, list)), [])
        env, pose, frame = parse_key(f)
        out[key_str(env, pose, frame)] = dets or []
    return out
#endregion

#region [Projection: prefer the repo's project_lidar (exact fused-arm projection)]
def setup_projection(args):
    """Returns (proj_fn, label). proj_fn(points Nx3) -> (u, v, z_cam)."""
    try:
        sys.path.insert(0, args.project_lidar_dir)
        from project_lidar import quat_to_R, find_transform, find_intrinsics, project as pl_project
        calib = json.load(open(args.calib))
        seven = find_transform(calib)
        if seven is None:
            raise ValueError("find_transform returned None")
        R = quat_to_R(seven[3], seven[4], seven[5], seven[6])
        t = np.array(seven[:3], dtype=float)
        ints = find_intrinsics(calib)
        fx, fy, cx, cy = ints if ints else (args.intrinsics_fx, args.intrinsics_fy,
                                            args.intrinsics_cx, args.intrinsics_cy)
        W, H = args.image_w, args.image_h

        def proj(points):
            P = np.asarray(points, dtype=float).reshape(-1, 3)
            res = pl_project(P, R, t, fx, fy, cx, cy, W, H, args.direction)
            u, v, z = res[0], res[1], res[2]
            return np.asarray(u), np.asarray(v), np.asarray(z)

        return proj, "project_lidar (exact fused-arm projection)"
    except Exception as e:
        print(f"[proj] project_lidar import failed ({e}); falling back to autodetect-from-fused.")
        return None, "autodetect-fallback"


def autodetect_from_calib_matrix(args, fused_runs):
    """Fallback only. Load any 4x4 from calib, try it and its inverse, pick what self-validates."""
    data = json.load(open(args.calib))

    def find_mat(obj):
        if isinstance(obj, list):
            arr = np.array(obj, dtype=float)
            if arr.shape in [(4, 4), (3, 4)]:
                return np.vstack([arr, [0, 0, 0, 1]]) if arr.shape == (3, 4) else arr
        if isinstance(obj, dict):
            for v in obj.values():
                r = find_mat(v)
                if r is not None:
                    return r
        return None

    M = find_mat(data)
    fx, fy, cx, cy = args.intrinsics_fx, args.intrinsics_fy, args.intrinsics_cx, args.intrinsics_cy

    def make(T):
        def proj(points):
            P = np.asarray(points, dtype=float).reshape(-1, 3)
            Ph = np.hstack([P, np.ones((P.shape[0], 1))])
            Xc = (T @ Ph.T).T[:, :3]
            z = Xc[:, 2]
            return fx * Xc[:, 0] / z + cx, fy * Xc[:, 1] / z + cy, z
        return proj

    if M is None:
        return make(np.eye(4))
    best, best_frac = make(M), -1.0
    for T in [M, np.linalg.inv(M)]:
        pj = make(T)
        ok = tot = 0
        for dets in fused_runs.values():
            for d in dets:
                if str(first_key(d, SOURCE_KEYS)).lower() != "fused":
                    continue
                pos = first_key(d, CENTER3D_KEYS)
                box = det_box(d)
                if pos is None or box is None:
                    continue
                u, v, z = pj([pos[:3]])
                tot += 1
                if z[0] > 0 and box[0] - 5 <= u[0] <= box[2] + 5 and box[1] - 5 <= v[0] <= box[3] + 5:
                    ok += 1
        frac = ok / tot if tot else 0.0
        if frac > best_frac:
            best, best_frac = pj, frac
    return best


def selfcheck(proj, fused_runs):
    ok = tot = 0
    for dets in fused_runs.values():
        for d in dets:
            if str(first_key(d, SOURCE_KEYS)).lower() != "fused":
                continue
            pos = first_key(d, CENTER3D_KEYS)
            box = det_box(d)
            if pos is None or box is None:
                continue
            u, v, z = proj([pos[:3]])
            tot += 1
            if z[0] > 0 and box[0] - 5 <= u[0] <= box[2] + 5 and box[1] - 5 <= v[0] <= box[3] + 5:
                ok += 1
    return (ok / tot) if tot else 0.0
#endregion

#region [Stats]
def err_stats(errs):
    if not errs:
        return {"n": 0, "median": None, "iqr": None, "rmse": None}
    a = sorted(errs)
    n = len(a)
    q1 = a[int(0.25 * (n - 1))]
    q3 = a[int(0.75 * (n - 1))]
    rmse = math.sqrt(sum(e * e for e in a) / n)
    return {"n": n, "median": round(statistics.median(a), 3),
            "iqr": round(q3 - q1, 3), "rmse": round(rmse, 3)}
#endregion

#region [Main]
def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)
    gates = [float(x) for x in args.gates.split(",")]

    gt = load_gt(args.gt)
    fused = load_run(os.path.join(args.runs, "fused"))
    lidar = load_run(os.path.join(args.runs, "lidar"))
    print(f"loaded: GT frames={len(gt)} fused frames={len(fused)} lidar frames={len(lidar)}")

    proj, label = setup_projection(args)
    if proj is None:
        proj = autodetect_from_calib_matrix(args, fused)
    frac = selfcheck(proj, fused)
    print(f"projection [{label}] self-check: fused centroids inside box_xyxy = {frac*100:.0f}% "
          f"({'OK' if frac >= 0.8 else 'LOW -> LiDAR-only matching UNRELIABLE; check calib/direction'})")
    lidar_proj_ok = frac >= 0.8

    envs = sorted({v["env"] for v in gt.values()})
    per_match_rows, presence_rows = [], []
    range_by = {}
    fused_rate = {}
    gate_counts = {}

    for env in envs:
        fkeys = [k for k in gt if gt[k]["env"] == env]
        tp = fp = gt_assessable = class_ok = class_tot = 0
        for k in fkeys:
            assess = [g for g in gt[k]["objects"] if not g["occluded"]]
            gt_assessable += len(assess)
            dets = []
            for d in fused.get(k, []):
                c = det_conf(d)
                if c is not None and c < args.yolo_conf:
                    continue
                dets.append({"box": det_box(d), "canon": canon(det_class(d)),
                             "src": str(first_key(d, SOURCE_KEYS)).lower(), "raw": d})
            fr = fused_rate.setdefault(env, {"fused": 0, "camera_only": 0,
                                             "too_few_points": 0, "no_qualifying_cluster": 0})
            for d in dets:
                if d["src"] == "fused":
                    fr["fused"] += 1
                else:
                    fr["camera_only"] += 1
                    reason = str(first_key(d["raw"], REASON_KEYS)).lower()
                    if reason in fr:
                        fr[reason] += 1
            matches = greedy_match_2d(assess, dets, args.iou)
            matched_d = {di for _, di, _ in matches}
            tp += len(matches)
            fp += len(dets) - len(matched_d)
            for gi, di, _ in matches:
                gc, dc = assess[gi]["canon"], dets[di]["canon"]
                pic = "person-in-chair" in str(assess[gi]["class"]).lower()
                class_ok += 1 if ((gc == dc) or (pic and dc in ("person", "chair"))) else 0
                class_tot += 1
                if dets[di]["src"] == "fused" and assess[gi]["range"] is not None:
                    dr = first_key(dets[di]["raw"], RANGE_KEYS)   # already horizontal
                    if dr is not None:
                        gr = float(assess[gi]["range"])
                        signed = float(dr) - gr
                        range_by.setdefault((env, "fused", gc), []).append(signed)
                        per_match_rows.append({"env": env, "arm": "fused", "gt_class": gc,
                                               "gt_range": round(gr, 3), "det_range": round(float(dr), 3),
                                               "signed_err": round(signed, 3),
                                               "abs_err": round(abs(signed), 3), "source": "fused"})
        recall = tp / gt_assessable if gt_assessable else 0.0
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        clsacc = class_ok / class_tot if class_tot else 0.0
        for arm in ("camera_only", "fused"):
            presence_rows.append({"env": env, "arm": arm, "recall": round(recall, 3),
                                  "precision": round(prec, 3), "class_acc": round(clsacc, 3),
                                  "tp": tp, "fp": fp, "gt_assessable": gt_assessable})

        gate_counts[env] = {g: 0 for g in gates}
        if lidar_proj_ok:
            for k in fkeys:
                gobjs = [g for g in gt[k]["objects"]
                         if not g["occluded"] and g["range"] is not None and g["box"] is not None]
                ldets = []
                for d in lidar.get(k, []):
                    sc = det_conf(d)
                    if sc is not None and sc < args.pp_score:
                        continue
                    ctr = first_key(d, CENTER3D_KEYS)
                    if ctr is None:
                        continue
                    ctr = [float(x) for x in ctr[:3]]
                    rng = math.hypot(ctr[0], ctr[1])              # HORIZONTAL, matches fused range_m
                    u, v, z = proj([ctr])
                    ldets.append({"u": float(u[0]), "z": float(z[0]),
                                  "range": rng, "canon": canon(det_class(d))})
                for g in gobjs:
                    x1, _, x2, _ = g["box"]
                    for gate in gates:
                        for d in ldets:
                            if (x1 <= d["u"] <= x2) and d["z"] > 0 and abs(d["range"] - float(g["range"])) <= gate:
                                gate_counts[env][gate] += 1
                                if gate == 0.75:
                                    signed = d["range"] - float(g["range"])
                                    range_by.setdefault((env, "lidar_only", g["canon"]), []).append(signed)
                                    per_match_rows.append({"env": env, "arm": "lidar_only",
                                                           "gt_class": g["canon"],
                                                           "gt_range": round(float(g["range"]), 3),
                                                           "det_range": round(d["range"], 3),
                                                           "signed_err": round(signed, 3),
                                                           "abs_err": round(abs(signed), 3),
                                                           "source": "lidar_only"})
                                break

    _write_csv(args.out, per_match_rows)
    _write_presence(args.out, presence_rows)
    _write_range(args.out, range_by)
    _write_fused_rate(args.out, fused_rate)
    _write_gate(args.out, gate_counts, gates)
    print(f"done -> {args.out}")
#endregion

#region [Writers]
TIER = {"env1": "~10 cm coarse (reconstructed d25; d10 superseded; values are 3D but ~= horizontal "
                "for these near-LiDAR-height objects)",
        "env2": "~10 cm medium (range_m is HORIZONTAL; GT should be the floor/horizontal measure; "
                "direct-slant over-reads by the height term; chairs also carry the centroid offset)"}
CENTROID_NOTE = ("range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the "
                 "cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset "
                 "(env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.")


def _write_csv(out, rows):
    cols = ["env", "arm", "gt_class", "gt_range", "det_range", "signed_err", "abs_err", "source"]
    with open(os.path.join(out, "per_match.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_presence(out, rows):
    with open(os.path.join(out, "presence_table.md"), "w") as f:
        f.write("# Presence (recall / precision / class-correctness)\n\n")
        f.write("camera_only and fused are IDENTICAL by construction (same YOLO set); expected.\n\n")
        f.write("| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['env']} | {r['arm']} | {r['recall']} | {r['precision']} | "
                    f"{r['class_acc']} | {r['tp']} | {r['fp']} | {r['gt_assessable']} |\n")
        f.write("\nLiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, "
                "so misses / spurious classes are EXPECTED. Reported via the gate table.\n")


def _write_range(out, by):
    with open(os.path.join(out, "range_error_table.md"), "w") as f:
        f.write("# Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.\n\n")
        f.write("Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only "
                "has NO range. Per env and per object (class).\n\n")
        f.write("| env | arm | object | N | median | IQR | RMSE |\n|---|---|---|---|---|---|---|\n")
        for (env, arm, obj), errs in sorted(by.items()):
            s = err_stats(errs)
            f.write(f"| {env} | {arm} | {obj} | {s['n']} | {s['median']} | {s['iqr']} | {s['rmse']} |\n")
        f.write("\n## per-env aggregate\n\n| env | arm | N | median | IQR | RMSE |\n|---|---|---|---|---|---|\n")
        agg = {}
        for (env, arm, obj), errs in by.items():
            agg.setdefault((env, arm), []).extend(errs)
        for (env, arm), errs in sorted(agg.items()):
            s = err_stats(errs)
            f.write(f"| {env} | {arm} | {s['n']} | {s['median']} | {s['iqr']} | {s['rmse']} |\n")
        f.write("\nFOOTNOTES:\n")
        for env, t in TIER.items():
            f.write(f"- {env} GT tier: {t}. Errors below the tier are not interpretable.\n")
        f.write(f"- {CENTROID_NOTE}\n")


def _write_fused_rate(out, fr):
    with open(os.path.join(out, "fused_rate_table.md"), "w") as f:
        f.write("# Fused-rate (fraction of YOLO boxes that earned a LiDAR range)\n\n")
        f.write("| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for env, d in sorted(fr.items()):
            total = d["fused"] + d["camera_only"]
            rate = d["fused"] / total if total else 0.0
            f.write(f"| {env} | {total} | {d['fused']} | {rate:.3f} | {d['camera_only']} | "
                    f"{d['too_few_points']} | {d['no_qualifying_cluster']} |\n")
        f.write("\nExpect ~100% on dense scenes, lower where the LiDAR is sparse = the reportable result.\n")


def _write_gate(out, gc, gates):
    with open(os.path.join(out, "gate_sensitivity.md"), "w") as f:
        f.write("# LiDAR-only match counts by BEV range gate (0.75 m primary; pre-declared)\n\n")
        f.write("| env | " + " | ".join(f"{g:.2f} m" for g in gates) + " |\n")
        f.write("|---|" + "|".join("---" for _ in gates) + "|\n")
        for env, d in sorted(gc.items()):
            f.write(f"| {env} | " + " | ".join(str(d.get(g, 0)) for g in gates) + " |\n")
        f.write("\nBearing proxy = LiDAR detection projects inside the GT box x-extent. If the "
                "projection self-check was LOW, treat as unreliable.\n")
#endregion


if __name__ == "__main__":
    main()
