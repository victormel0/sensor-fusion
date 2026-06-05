#!/usr/bin/env python3
"""
project_lidar.py -- project LiDAR points into the rectified camera image and overlay them, to
verify the extrinsic + intrinsics BEFORE any fusion (Week 3 Day 2, steps 2.2 / 2.3).

Runs with numpy + opencv only (venv_yolo or the ROS env both have these).

TRANSFORM DIRECTION (the open question for §2.1):
The calib.json stores T_lidar_camera as [tx, ty, tz, qx, qy, qz, qw]. Koide's
direct_visual_lidar_calibration commonly defines T_lidar_camera as the CAMERA POSE IN THE LIDAR
FRAME (p_lidar = R p_cam + t), in which case projecting LiDAR points needs the INVERSE:
    --direction campose   ->  p_cam = R^T (p_lidar - t)
The alternative is that the stored T already maps LiDAR -> camera:
    --direction lidar2cam ->  p_cam = R p_lidar + t
This script does NOT assume. --direction both (default) renders one overlay per interpretation,
suffixed _lidar2cam / _campose, so the correct one is chosen visually (the empirical check).

SANITY CHECK: the parsed translation is printed; it should read t ~ (+0.123, -0.015, -0.160) m
(the known calib value). If it does not, find_transform grabbed the wrong list -- pass --quat/--trans.

INTRINSICS default to the Day-1 camera_info values (fx=335.13, fy=359.35, cx=486.26, cy=291.70),
which match calib.json (K == P). Override with --fx/--fy/--cx/--cy, or they are taken from --calib
if cleanly present there.
"""

import argparse
import json
import os
import sys

import numpy as np
import cv2


#region [Calibration loading]
def quat_to_R(qx, qy, qz, qw):
    """Unit quaternion [qx, qy, qz, qw] -> 3x3 rotation matrix."""
    n = (qx * qx + qy * qy + qz * qz + qw * qw) ** 0.5
    qx, qy, qz, qw = qx / n, qy / n, qz / n, qw / n
    return np.array([
        [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw),     2 * (qx * qz + qy * qw)],
        [2 * (qx * qy + qz * qw),     1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
        [2 * (qx * qz - qy * qw),     2 * (qy * qz + qx * qw),     1 - 2 * (qx * qx + qy * qy)],
    ], dtype=np.float64)


def find_transform(obj):
    """Find a 7-element [tx,ty,tz,qx,qy,qz,qw] in a parsed calib.json, preferring lidar_camera keys."""
    keyed = []
    bare = []

    def is_seven(x):
        return isinstance(x, list) and len(x) == 7 and all(isinstance(e, (int, float)) for e in x)

    def walk(o):
        if isinstance(o, dict):
            for k, val in o.items():
                if "lidar_camera" in k.lower() and is_seven(val):
                    keyed.append(val)
                walk(val)
        elif isinstance(o, list):
            if is_seven(o):
                bare.append(o)
            for e in o:
                walk(e)

    walk(obj)
    for c in keyed + bare:
        return [float(e) for e in c]
    return None


def find_intrinsics(obj):
    """Find [fx, fy, cx, cy] in a parsed calib.json; return None if not cleanly present."""
    out = {}

    def walk(o):
        if isinstance(o, dict):
            for k, val in o.items():
                kl = k.lower()
                if kl in ("intrinsics", "intrinsic") and isinstance(val, list) and len(val) >= 4 \
                        and all(isinstance(e, (int, float)) for e in val[:4]):
                    out["i"] = [float(e) for e in val[:4]]
                if kl in ("fx", "fy", "cx", "cy") and isinstance(val, (int, float)):
                    out[kl] = float(val)
                walk(val)
        elif isinstance(o, list):
            for e in o:
                walk(e)

    walk(obj)
    if "i" in out:
        return out["i"]
    if all(k in out for k in ("fx", "fy", "cx", "cy")):
        return [out["fx"], out["fy"], out["cx"], out["cy"]]
    return None
#endregion


#region [Projection]
def project(points_xyz, R, t, fx, fy, cx, cy, W, H, direction):
    """Return (u, v, z, front_mask, in_image_mask) for the given transform direction."""
    P = points_xyz.astype(np.float64)
    if direction == "lidar2cam":
        pc = (R @ P.T).T + t                 # p_cam = R p_lidar + t
    elif direction == "campose":
        pc = (R.T @ (P - t).T).T             # invert: p_cam = R^T (p_lidar - t)
    else:
        raise ValueError("direction must be lidar2cam or campose")
    z = pc[:, 2]
    front = z > 0
    u = np.full(z.shape, -1.0)
    v = np.full(z.shape, -1.0)
    u[front] = fx * pc[front, 0] / z[front] + cx
    v[front] = fy * pc[front, 1] / z[front] + cy
    inb = front & (u >= 0) & (u < W) & (v >= 0) & (v < H)
    return u, v, z, front, inb
#endregion


#region [Overlay]
def draw_overlay(img, u, v, z, inb, out_path, highlight=None):
    """Draw in-image points coloured by depth (near = blue, far = red) and save.

    If `highlight` (a full-length bool mask) is given, in-image points in the mask are over-drawn
    larger in magenta (used to mark a range band, e.g. the ~4.33 m blue-chair returns)."""
    vis = img.copy()
    zin = z[inb]
    if zin.size > 0:
        zmin, zmax = float(np.percentile(zin, 2)), float(np.percentile(zin, 98))
        rng = max(zmax - zmin, 1e-6)
        tnorm = np.clip((zin - zmin) / rng, 0.0, 1.0)
        gray = (tnorm * 255).astype(np.uint8).reshape(-1, 1)
        colors = cv2.applyColorMap(gray, cv2.COLORMAP_JET).reshape(-1, 3)   # BGR
        uu = u[inb].astype(int)
        vv = v[inb].astype(int)
        for i in range(uu.shape[0]):
            cv2.circle(vis, (int(uu[i]), int(vv[i])), 2,
                       (int(colors[i, 0]), int(colors[i, 1]), int(colors[i, 2])), -1)
    if highlight is not None:
        hl = inb & highlight
        uu, vv = u[hl].astype(int), v[hl].astype(int)
        for i in range(uu.shape[0]):
            cv2.circle(vis, (int(uu[i]), int(vv[i])), 3, (255, 0, 255), -1)   # magenta
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
    ap.add_argument("--direction", choices=["lidar2cam", "campose", "both"], default="both")
    ap.add_argument("--fx", type=float, default=335.13)
    ap.add_argument("--fy", type=float, default=359.35)
    ap.add_argument("--cx", type=float, default=486.26)
    ap.add_argument("--cy", type=float, default=291.70)
    ap.add_argument("--quat", type=float, nargs=4, default=None, help="qx qy qz qw (overrides --calib)")
    ap.add_argument("--trans", type=float, nargs=3, default=None, help="tx ty tz (overrides --calib)")
    ap.add_argument("--highlight-range", type=float, default=None,
                    help="mark points whose LiDAR-frame range hypot(x,y) is near this value, in metres")
    ap.add_argument("--highlight-band", type=float, default=0.3, help="half-width of the highlight band (m)")
    args = ap.parse_args()

    if args.quat is not None and args.trans is not None:
        tx, ty, tz = args.trans
        qx, qy, qz, qw = args.quat
    else:
        with open(args.calib) as f:
            calib = json.load(f)
        seven = find_transform(calib)
        if seven is None:
            sys.exit("ERROR: no [tx,ty,tz,qx,qy,qz,qw] transform found in the calib JSON. "
                     "Pass --quat and --trans, or share the JSON so the loader can be matched to it.")
        tx, ty, tz, qx, qy, qz, qw = seven
        ints = find_intrinsics(calib)
        if ints is not None:
            args.fx, args.fy, args.cx, args.cy = ints

    R = quat_to_R(qx, qy, qz, qw)
    t = np.array([tx, ty, tz], dtype=np.float64)
    print(f"- transform: t=({tx:.4f}, {ty:.4f}, {tz:.4f})  quat=({qx:.4f}, {qy:.4f}, {qz:.4f}, {qw:.4f})")
    print(f"  sanity: t should read ~ (+0.123, -0.015, -0.160); if not, --quat/--trans were needed")
    print(f"- intrinsics: fx={args.fx} fy={args.fy} cx={args.cx} cy={args.cy}")

    raw = np.fromfile(args.bin, dtype=np.float32)
    if raw.size % 5 != 0:
        sys.exit(f"ERROR: {args.bin} is not a multiple of 5 floats (expected 5-channel .bin)")
    pts = raw.reshape(-1, 5)[:, :3]

    img = cv2.imread(args.image)
    if img is None:
        sys.exit(f"ERROR: could not read image {args.image}")
    H, W = img.shape[:2]

    dirs = ["lidar2cam", "campose"] if args.direction == "both" else [args.direction]
    base, ext = os.path.splitext(args.out)
    highlight = None
    if args.highlight_range is not None:
        range_l = np.hypot(pts[:, 0], pts[:, 1])
        highlight = np.abs(range_l - args.highlight_range) <= args.highlight_band
    for d in dirs:
        u, v, z, front, inb = project(pts, R, t, args.fx, args.fy, args.cx, args.cy, W, H, d)
        out_path = args.out if len(dirs) == 1 else f"{base}_{d}{ext}"
        draw_overlay(img, u, v, z, inb, out_path, highlight)
        print(f"- [{d}] total={pts.shape[0]} in_front={int(front.sum())} in_image={int(inb.sum())} -> {out_path}")

    if args.direction == "both":
        print("- compare the two overlays; keep the direction whose points land on the objects, "
              "then re-run with --direction <that> to write the canonical d15_overlay_<frame>.png")


if __name__ == "__main__":
    main()
#endregion
