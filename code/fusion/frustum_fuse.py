#!/usr/bin/env python3
"""
frustum_fuse.py -- Week 3 Day 3 frustum association (DAL principle: camera classifies, LiDAR locates).

Pipeline per frame:
  1. Run YOLOv8 in-process on the rectified RGB -> 2D boxes (pixel xyxy, class, conf).
  2. Project the LiDAR .bin into the image (reuses project_lidar.py; direction campose by default).
  3. For each box: gather points with z_cam>0 whose (u,v) falls inside the box (optionally a central
     shrink of the box), DBSCAN them in the LiDAR frame, and pick the NEAREST qualifying cluster
     (smallest median range, cluster size >= --min-points). DAL: the camera gives class+conf, the
     LiDAR cluster gives the 3D centroid + axis-aligned extent, reported in the LiDAR frame.
  4. Below the guard (no qualifying cluster) the box becomes a camera-only detection (class+2D, no 3D).

Outputs:
  --out  per-frame JSON: list of detections {class, conf, source, box_xyxy, position_lidar, extent,
         range_m, n_in_box, n_cluster, n_clusters}
  --viz  overlay PNG: boxes + in-box points (chosen cluster highlighted) + class/range labels

Run in venv_yolo. Needs ultralytics, scikit-learn, numpy, opencv, and project_lidar.py beside it.
Position is reported in the LiDAR frame (range = hypot(x, y)) to match the Day-6 PointPillars baseline.
"""

import argparse
import json
import os
import sys

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from project_lidar import quat_to_R, find_transform, find_intrinsics, project   # noqa: E402


#region [Dependencies]
def load_dbscan():
    try:
        from sklearn.cluster import DBSCAN
        return DBSCAN
    except ImportError:
        sys.exit("ERROR: scikit-learn not installed. In venv_yolo run:\n"
                 "  pip install scikit-learn\n"
                 "then check numpy is still 1.26.x (pip should keep it; re-pin numpy<2 if not).")


def load_yolo():
    try:
        from ultralytics import YOLO
        return YOLO
    except ImportError:
        sys.exit("ERROR: ultralytics not installed in this venv (expected venv_yolo).")
#endregion


#region [Calibration]
def load_calib(path, fx, fy, cx, cy):
    with open(path) as f:
        calib = json.load(f)
    seven = find_transform(calib)
    if seven is None:
        sys.exit("ERROR: no [tx,ty,tz,qx,qy,qz,qw] transform found in the calib JSON.")
    tx, ty, tz, qx, qy, qz, qw = seven
    R = quat_to_R(qx, qy, qz, qw)
    t = np.array([tx, ty, tz], dtype=np.float64)
    ints = find_intrinsics(calib)
    if ints is not None:
        fx, fy, cx, cy = ints
    return R, t, fx, fy, cx, cy
#endregion


#region [Frustum association]
def associate_box(box, lidar_xyz, u, v, front, dbscan, eps, min_samples, min_points, shrink):
    """Return a detection dict for one 2D box. box = (x1,y1,x2,y2)."""
    x1, y1, x2, y2 = box
    if shrink < 1.0:
        cxb, cyb = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        hw, hh = (x2 - x1) / 2.0 * shrink, (y2 - y1) / 2.0 * shrink
        x1, y1, x2, y2 = cxb - hw, cyb - hh, cxb + hw, cyb + hh

    in_box = front & (u >= x1) & (u < x2) & (v >= y1) & (v < y2)
    n_in_box = int(in_box.sum())
    if n_in_box < min_points:
        return {"source": "camera_only", "reason": "too_few_points",
                "n_in_box": n_in_box, "n_clusters": 0, "chosen_mask": None}

    pts = lidar_xyz[in_box]
    labels = dbscan(eps=eps, min_samples=min_samples).fit_predict(pts)
    cluster_ids = [c for c in set(labels.tolist()) if c != -1]

    best = None
    for cid in cluster_ids:
        sub = labels == cid
        if int(sub.sum()) < min_points:
            continue
        cl = pts[sub]
        rng = float(np.median(np.hypot(cl[:, 0], cl[:, 1])))
        if best is None or rng < best["range"]:
            best = {"range": rng, "sub": sub, "n": int(sub.sum())}

    if best is None:
        return {"source": "camera_only", "reason": "no_qualifying_cluster",
                "n_in_box": n_in_box, "n_clusters": len(cluster_ids), "chosen_mask": None}

    cl = pts[best["sub"]]
    centroid = cl.mean(axis=0)
    extent = (cl.max(axis=0) - cl.min(axis=0))
    rng = float(np.hypot(centroid[0], centroid[1]))
    # map the chosen sub-mask back onto the full point array (for visualization)
    full_idx = np.where(in_box)[0][best["sub"]]
    chosen_mask = np.zeros(lidar_xyz.shape[0], dtype=bool)
    chosen_mask[full_idx] = True
    return {
        "source": "fused",
        "position_lidar": [float(centroid[0]), float(centroid[1]), float(centroid[2])],
        "extent": [float(extent[0]), float(extent[1]), float(extent[2])],
        "range_m": round(rng, 3),
        "n_in_box": n_in_box,
        "n_cluster": best["n"],
        "n_clusters": len(cluster_ids),
        "chosen_mask": chosen_mask,
    }
#endregion


#region [Visualization]
def draw(image, dets, u, v, out_path):
    vis = image.copy()
    for d in dets:
        x1, y1, x2, y2 = [int(round(c)) for c in d["box_xyxy"]]
        fused = d["source"] == "fused"
        box_color = (0, 200, 0) if fused else (0, 140, 255)   # BGR: green fused, orange camera-only
        cv2.rectangle(vis, (x1, y1), (x2, y2), box_color, 2)
        if d.get("_chosen_mask") is not None:
            cm = d["_chosen_mask"]
            uu, vv = u[cm].astype(int), v[cm].astype(int)
            for i in range(uu.shape[0]):
                cv2.circle(vis, (int(uu[i]), int(vv[i])), 2, (0, 255, 0), -1)
        label = f"{d['class']} {d['conf']:.2f}"
        label += f" {d['range_m']:.1f}m" if fused else " cam-only"
        cv2.putText(vis, label, (x1, max(y1 - 5, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2, cv2.LINE_AA)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    cv2.imwrite(out_path, vis)
#endregion


#region [Main]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--viz", default=None)
    ap.add_argument("--model", default="yolov8s.pt")
    ap.add_argument("--direction", choices=["lidar2cam", "campose"], default="campose")
    ap.add_argument("--conf", type=float, default=0.25, help="YOLO confidence threshold")
    ap.add_argument("--eps", type=float, default=0.3, help="DBSCAN eps in metres")
    ap.add_argument("--min-samples", type=int, default=5, help="DBSCAN core min_samples")
    ap.add_argument("--min-points", type=int, default=10, help="guard: min points for a 3D detection")
    ap.add_argument("--shrink", type=float, default=1.0, help="central-box fraction (1.0 = off, e.g. 0.8)")
    ap.add_argument("--fx", type=float, default=335.13)
    ap.add_argument("--fy", type=float, default=359.35)
    ap.add_argument("--cx", type=float, default=486.26)
    ap.add_argument("--cy", type=float, default=291.70)
    args = ap.parse_args()

    DBSCAN = load_dbscan()
    YOLO = load_yolo()

    R, t, fx, fy, cx, cy = load_calib(args.calib, args.fx, args.fy, args.cx, args.cy)

    raw = np.fromfile(args.bin, dtype=np.float32)
    if raw.size % 5 != 0:
        sys.exit(f"ERROR: {args.bin} is not a multiple of 5 floats (expected 5-channel .bin)")
    lidar_xyz = raw.reshape(-1, 5)[:, :3].astype(np.float64)

    img = cv2.imread(args.image)
    if img is None:
        sys.exit(f"ERROR: could not read image {args.image}")
    H, W = img.shape[:2]

    # project all points once (campose by default)
    u, v, z, front, _inb = project(lidar_xyz, R, t, fx, fy, cx, cy, W, H, args.direction)

    # YOLO in-process
    model = YOLO(args.model)
    res = model(args.image, conf=args.conf, verbose=False)[0]
    names = res.names
    xyxy = res.boxes.xyxy.cpu().numpy()
    cls = res.boxes.cls.cpu().numpy().astype(int)
    conf = res.boxes.conf.cpu().numpy()

    dets = []
    print(f"frame {os.path.basename(args.image)}: {len(xyxy)} boxes, "
          f"{int(front.sum())} pts in front, image {W}x{H}")
    for i in range(len(xyxy)):
        box = [float(c) for c in xyxy[i]]
        r = associate_box(box, lidar_xyz, u, v, front, DBSCAN,
                          args.eps, args.min_samples, args.min_points, args.shrink)
        cname = names[cls[i]]
        det = {"class": cname, "conf": round(float(conf[i]), 3), "box_xyxy": [round(c, 1) for c in box]}
        det.update({k: val for k, val in r.items() if k != "chosen_mask"})
        det["_chosen_mask"] = r.get("chosen_mask")
        dets.append(det)
        if r["source"] == "fused":
            p = r["position_lidar"]
            print(f"  box {i} {cname} {conf[i]:.2f}: in_box={r['n_in_box']} clusters={r['n_clusters']} "
                  f"-> FUSED pos=({p[0]:.2f},{p[1]:.2f},{p[2]:.2f}) range={r['range_m']:.2f}m "
                  f"extent=({r['extent'][0]:.2f},{r['extent'][1]:.2f},{r['extent'][2]:.2f}) n={r['n_cluster']}")
        else:
            print(f"  box {i} {cname} {conf[i]:.2f}: in_box={r['n_in_box']} clusters={r['n_clusters']} "
                  f"-> CAMERA-ONLY ({r['reason']})")

    if args.viz:
        draw(img, dets, u, v, args.viz)
        print(f"  viz -> {args.viz}")

    # strip the non-serialisable mask before writing JSON
    for d in dets:
        d.pop("_chosen_mask", None)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(dets, f, indent=2)
    n_fused = sum(1 for d in dets if d["source"] == "fused")
    print(f"  {n_fused}/{len(dets)} fused (rest camera-only) -> {args.out}")


if __name__ == "__main__":
    main()
#endregion
