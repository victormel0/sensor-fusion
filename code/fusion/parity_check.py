#!/usr/bin/env python3
"""
parity_check.py -- Week 4 Day 2 (d20) parity of the LIVE-node association against the offline fused_out/.

WHAT THIS PROVES (and what it does not)
  The live node's on_pair calls the SAME project() + associate_box() that produced the offline
  code/fusion/fused_out/*.json. This script replays the three stored parity frames' inputs
  (frames_out/NNNNN.png + the per-frame LiDAR .bin) through those SAME functions and diffs the result
  against fused_out/NNNNN.json. Because the math is shared, any disagreement can only come from how the
  inputs are decoded -- which is exactly what parity should catch.

  This is the "input-replay" alignment (week04_step_by_step.md 2.3, recommended): deterministic, no
  stamp/frame alignment. It proves the PORT preserved the math. It does NOT exercise the ROS
  subscribe+sync path; if you want a live-path figure, use the end-to-end stamp-match alternative (the
  node would dump {stamp, detections} and you match by nearest stamp -- needs the offline frame->stamp
  map, see 2.3).

DECODER CROSS-CHECKS (optional, only run if fusion_node imports cleanly, i.e. ROS is sourced):
  - image_to_bgr: a bgra8 buffer is rebuilt from the stored BGR PNG, pushed through the node's
    image_to_bgr(), and asserted byte-identical to the PNG. This tests the node's bgra8 -> BGR branch
    WITHOUT needing a stored raw bgra8 frame.
  - cloud_to_xyz: the .bin xyz is wrapped into a PointCloud2 and read back via the node's cloud_to_xyz();
    asserted equal to the .bin xyz. This tests the 4-field read vs the offline 5-channel reshape.
    `to verify`: the sensor_msgs_py cloud-creation API on this Humble build (guarded; skipped with a note
    if the signature differs).

PARITY BAR (defaults; --pos-tol and the bar are Victor's to confirm -- see the message that ships with
this file). Per frame, PASS iff:
  (a) same number of YOLO boxes as offline (a count mismatch means decode/detection drift);
  (b) each matched box has the SAME source (fused vs camera_only)  -- catches dropped in-box points;
  (c) every fused box agrees on range_m AND centroid within --pos-tol (default 0.05 m);
  (d) the fused-class multiset matches.
The Week-3 narrative (suppression of the near-field vehicle, person-in-chair ~4.3 m, tan chair
recovered, far-room reclassified, 100 cm chair missed) is validated implicitly by (c)+(d): fused_out/
already encodes those outcomes, so matching it reproduces them.

RUN (venv_yolo; source ROS too if you want the decoder cross-checks):
    cd ~/Documents/workspace/sensor-fusion
    source ros2_ws/install/setup.bash            # only needed for the decoder cross-checks
    export PYTHONPATH=$PWD/venv_yolo/lib/python3.10/site-packages:$PWD/code/fusion:$PYTHONPATH
    python3 code/fusion/parity_check.py \
        --frames-dir code/fusion/frames_out \
        --bins-dir   <dir holding the per-frame .bin -- CONFIRM with ls> \
        --offline    code/fusion/fused_out \
        --frames 00100,00300,00500 \
        --pos-tol 0.05
"""

import argparse
import glob
import json
import os
import sys

import numpy as np
import cv2


#region [Imports of the reused + node code]
def import_fusion_code(fusion_code_dir):
    fusion_code_dir = os.path.expanduser(fusion_code_dir)
    if fusion_code_dir not in sys.path:
        sys.path.insert(0, fusion_code_dir)
    try:
        from project_lidar import project
        from frustum_fuse import load_calib, load_dbscan, associate_box
    except ImportError as exc:
        sys.exit(f"ERROR: could not import project_lidar/frustum_fuse from '{fusion_code_dir}': {exc}")
    return project, load_calib, load_dbscan, associate_box


def try_import_node_decoders(node_dir):
    """Return (image_to_bgr, cloud_to_xyz) if fusion_node imports, else (None, None).

    Importing fusion_node pulls rclpy/vision_msgs; that only succeeds with the ROS env sourced. We guard
    it so the core parity still runs in venv_yolo alone (the decoder cross-checks are then skipped)."""
    node_dir = os.path.expanduser(node_dir)
    if node_dir not in sys.path:
        sys.path.insert(0, node_dir)
    try:
        from fusion_node import image_to_bgr, cloud_to_xyz
        return image_to_bgr, cloud_to_xyz
    except Exception as exc:   # noqa: BLE001 -- ROS not sourced, etc.; cross-checks are optional
        print(f"[note] node decoder cross-checks skipped (fusion_node import failed: {exc})")
        return None, None
#endregion


#region [Decoder cross-checks]
def check_image_decoder(image_to_bgr, bgr):
    """Rebuild a bgra8 buffer from the BGR PNG, run it through the node decoder, assert equality."""
    import types
    H, W = bgr.shape[:2]
    alpha = np.full((H, W, 1), 255, dtype=np.uint8)
    bgra = np.concatenate([bgr, alpha], axis=2)            # B,G,R,A in that byte order = 'bgra8'
    msg = types.SimpleNamespace(
        encoding="bgra8", height=H, width=W, step=W * 4, data=bgra.tobytes())
    out = image_to_bgr(msg)
    return bool(np.array_equal(out, bgr))


def check_cloud_decoder(cloud_to_xyz, xyz):
    """Wrap the .bin xyz into a PointCloud2 and read it back via the node decoder.

    `to verify`: the create_cloud API on this Humble build. Guarded -- returns None (skipped) on any
    mismatch rather than failing the whole run."""
    try:
        from std_msgs.msg import Header
        from sensor_msgs_py import point_cloud2 as pc2
        header = Header()
        header.frame_id = "rslidar"
        cloud = pc2.create_cloud_xyz32(header, xyz.astype(np.float32).tolist())
        back = cloud_to_xyz(cloud)
        if back.shape != xyz.shape:
            return None
        return float(np.max(np.abs(back - xyz)))
    except Exception as exc:   # noqa: BLE001
        print(f"[note] cloud decoder cross-check skipped (create_cloud API to verify): {exc}")
        return None
#endregion


#region [Association replay]
def associate_frame(project, associate_box, DBSCAN, model, bgr, xyz, calib, params):
    """Run the SAME association the node runs: YOLO -> project (campose) -> associate_box per box.
    Returns a list of dicts mirroring fused_out's schema for the fields parity compares."""
    R, t, fx, fy, cx, cy = calib
    H, W = bgr.shape[:2]
    res = model(bgr, conf=params["conf"], verbose=False)[0]
    names = res.names
    xyxy = res.boxes.xyxy.cpu().numpy()
    cls = res.boxes.cls.cpu().numpy().astype(int)
    conf = res.boxes.conf.cpu().numpy()

    u, v, z, front, inb = project(xyz, R, t, fx, fy, cx, cy, W, H, "campose")

    dets = []
    for i in range(len(xyxy)):
        box = [float(c) for c in xyxy[i]]
        a = associate_box(box, xyz, u, v, front, DBSCAN,
                          params["eps"], params["min_samples"], params["min_points"], params["shrink"])
        d = {"class": names[cls[i]], "conf": float(conf[i]),
             "box_xyxy": [round(c, 1) for c in box], "source": a.get("source")}
        if a.get("source") == "fused":
            d["range_m"] = float(a["range_m"])
            d["position_lidar"] = [float(c) for c in a["position_lidar"]]
        dets.append(d)
    return dets
#endregion


#region [Comparison]
def _box_key(d):
    return tuple(round(c, 1) for c in d["box_xyxy"])


def compare_frame(computed, offline, pos_tol):
    """Compare computed dets to offline dets. Returns (passed, info dict)."""
    info = {"n_computed": len(computed), "n_offline": len(offline),
            "source_mismatches": 0, "max_range_delta": 0.0, "max_centroid_delta": 0.0,
            "fused_classes_match": None, "notes": []}

    if len(computed) != len(offline):
        info["notes"].append(f"box count differs: computed {len(computed)} vs offline {len(offline)}")
        return False, info

    # order-independent pairing: sort both by rounded box, pair by index
    comp = sorted(computed, key=_box_key)
    offl = sorted(offline, key=_box_key)

    passed = True
    for c, o in zip(comp, offl):
        if _box_key(c) != _box_key(o):
            info["notes"].append(f"box mismatch: {_box_key(c)} vs {_box_key(o)}")
            passed = False
        if c.get("source") != o.get("source"):
            info["source_mismatches"] += 1
            info["notes"].append(
                f"source flip on box {_box_key(o)}: computed {c.get('source')} vs offline {o.get('source')}")
            passed = False
        if c.get("source") == "fused" and o.get("source") == "fused":
            rd = abs(float(c["range_m"]) - float(o["range_m"]))
            cc = np.asarray(c["position_lidar"], dtype=float)
            oo = np.asarray(o["position_lidar"], dtype=float)
            cd = float(np.linalg.norm(cc - oo))
            info["max_range_delta"] = max(info["max_range_delta"], rd)
            info["max_centroid_delta"] = max(info["max_centroid_delta"], cd)
            if rd > pos_tol or cd > pos_tol:
                info["notes"].append(
                    f"over tol on box {_box_key(o)}: range_delta={rd:.4f} centroid_delta={cd:.4f} (tol {pos_tol})")
                passed = False

    comp_fused = sorted(c["class"] for c in computed if c.get("source") == "fused")
    offl_fused = sorted(o["class"] for o in offline if o.get("source") == "fused")
    info["fused_classes_match"] = (comp_fused == offl_fused)
    if not info["fused_classes_match"]:
        info["notes"].append(f"fused class multiset differs: computed {comp_fused} vs offline {offl_fused}")
        passed = False

    return passed, info
#endregion


#region [Main]
def resolve_bin(bins_dir, frame, ext, prefix):
    """Find the per-frame .bin. Files may be bare (NNNNN.bin) or carry a recording prefix
    (e.g. test2_marked_distances_NNNNN.bin). --bin-prefix forces a prefix; otherwise auto-resolve:
    try the bare name, then '*_NNNNN', then '*NNNNN'. Errors (not guesses) on an ambiguous match."""
    if prefix is not None:
        cand = os.path.join(bins_dir, f"{prefix}{frame}.{ext}")
        return cand if os.path.isfile(cand) else None
    exact = os.path.join(bins_dir, f"{frame}.{ext}")
    if os.path.isfile(exact):
        return exact
    for pat in (f"*_{frame}.{ext}", f"*{frame}.{ext}"):
        matches = sorted(glob.glob(os.path.join(bins_dir, pat)))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            sys.exit(f"ERROR: multiple .bin match '{pat}' in {bins_dir} for frame {frame}:\n  "
                     + "\n  ".join(matches) + "\n  disambiguate with --bin-prefix.")
    return None


def load_bin_xyz(path, channels):
    raw = np.fromfile(path, dtype=np.float32)
    if channels <= 0 or raw.size % channels != 0:
        sys.exit(f"ERROR: {path} size {raw.size} is not a multiple of --bin-channels={channels}. "
                 f"Confirm the .bin layout (offline frustum_fuse.py used 5-channel float32).")
    return raw.reshape(-1, channels)[:, :3].astype(np.float64)


def main():
    home = os.path.expanduser("~")
    repo = os.path.join(home, "Documents", "workspace", "sensor-fusion")

    ap = argparse.ArgumentParser()
    ap.add_argument("--frames-dir", default=os.path.join(repo, "code", "fusion", "frames_out"),
                    help="dir holding the parity PNGs (NNNNN.png)")
    ap.add_argument("--bins-dir", required=True,
                    help="dir holding the per-frame LiDAR .bin (NNNNN.bin) -- CONFIRM with ls "
                         "(code/bag_to_bin/out or frames_out)")
    ap.add_argument("--offline", default=os.path.join(repo, "code", "fusion", "fused_out"),
                    help="dir holding the offline fused_out JSON (NNNNN.json)")
    ap.add_argument("--frames", default="00100,00300,00500")
    ap.add_argument("--pos-tol", type=float, default=0.05, help="range/centroid tolerance in metres")
    ap.add_argument("--bin-channels", type=int, default=5,
                    help="floats per point in the .bin (offline path = 5)")
    ap.add_argument("--bin-ext", default="bin")
    ap.add_argument("--bin-prefix", default=None,
                    help="explicit .bin filename prefix, e.g. test2_marked_distances_ . "
                         "Default: auto-resolve bare (NNNNN.bin) or prefixed (*_NNNNN.bin) naming.")
    ap.add_argument("--img-ext", default="png")
    # reused code + node decoders
    ap.add_argument("--fusion-code-dir", default=os.path.join(repo, "code", "fusion"))
    ap.add_argument("--node-dir",
                    default=os.path.join(repo, "ros2_ws", "src", "thesis_fusion", "thesis_fusion"))
    ap.add_argument("--calib", default=os.path.join(repo, "calibration",
                                                    "calib_T_lidar_camera_2026_05_26.json"))
    # association params (must match the node + frustum_fuse defaults)
    ap.add_argument("--model", default="yolov8s.pt")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--eps", type=float, default=0.3)
    ap.add_argument("--min-samples", type=int, default=5)
    ap.add_argument("--min-points", type=int, default=10)
    ap.add_argument("--shrink", type=float, default=1.0)
    ap.add_argument("--fx", type=float, default=335.13)
    ap.add_argument("--fy", type=float, default=359.35)
    ap.add_argument("--cx", type=float, default=486.26)
    ap.add_argument("--cy", type=float, default=291.70)
    args = ap.parse_args()

    project, load_calib, load_dbscan, associate_box = import_fusion_code(args.fusion_code_dir)
    DBSCAN = load_dbscan()
    image_to_bgr, cloud_to_xyz = try_import_node_decoders(args.node_dir)

    calib_path = os.path.expanduser(args.calib)
    if not os.path.isfile(calib_path):
        sys.exit(f"ERROR: calib file not found: {calib_path}")
    calib = load_calib(calib_path, args.fx, args.fy, args.cx, args.cy)

    from ultralytics import YOLO
    model = YOLO(args.model)

    params = {"conf": args.conf, "eps": args.eps, "min_samples": args.min_samples,
              "min_points": args.min_points, "shrink": args.shrink}

    frames = [f.strip() for f in args.frames.split(",") if f.strip()]
    print(f"parity: frames={frames} pos_tol={args.pos_tol} m bin_channels={args.bin_channels}")
    print(f"        frames_dir={args.frames_dir}")
    print(f"        bins_dir  ={args.bins_dir}")
    print(f"        offline   ={args.offline}")
    print("")

    all_pass = True
    rows = []
    for fr in frames:
        img_path = os.path.join(args.frames_dir, f"{fr}.{args.img_ext}")
        bin_path = resolve_bin(args.bins_dir, fr, args.bin_ext, args.bin_prefix)
        if bin_path is None:
            sys.exit(f"ERROR: no .bin for frame {fr} in {args.bins_dir} "
                     f"(looked for {fr}.{args.bin_ext} and *_{fr}.{args.bin_ext}). "
                     f"Pass --bin-prefix if the naming differs.")
        json_path = os.path.join(args.offline, f"{fr}.json")
        for p in (img_path, json_path):
            if not os.path.isfile(p):
                sys.exit(f"ERROR: missing input for frame {fr}: {p}")

        bgr = cv2.imread(img_path)
        if bgr is None:
            sys.exit(f"ERROR: could not read image {img_path}")
        xyz = load_bin_xyz(bin_path, args.bin_channels)

        # optional decoder cross-checks
        img_dec = None
        cloud_dec = None
        if image_to_bgr is not None:
            img_dec = check_image_decoder(image_to_bgr, bgr)
        if cloud_to_xyz is not None:
            cloud_dec = check_cloud_decoder(cloud_to_xyz, xyz)

        computed = associate_frame(project, associate_box, DBSCAN, model, bgr, xyz, calib, params)
        with open(json_path) as f:
            offline = json.load(f)

        passed, info = compare_frame(computed, offline, args.pos_tol)
        all_pass = all_pass and passed
        rows.append((fr, passed, info, img_dec, cloud_dec))

    # summary table
    print("| frame | result | boxes (c/o) | src flips | max range d (m) | max centroid d (m) | "
          "fused classes | img dec | cloud dec |")
    print("|---|---|---|---|---|---|---|---|---|")
    for fr, passed, info, img_dec, cloud_dec in rows:
        img_s = "PASS" if img_dec else ("FAIL" if img_dec is False else "skip")
        cloud_s = ("%.2g" % cloud_dec) if isinstance(cloud_dec, float) else "skip"
        print(f"| {fr} | {'PASS' if passed else 'FAIL'} | "
              f"{info['n_computed']}/{info['n_offline']} | {info['source_mismatches']} | "
              f"{info['max_range_delta']:.4f} | {info['max_centroid_delta']:.4f} | "
              f"{'match' if info['fused_classes_match'] else 'DIFFER'} | {img_s} | {cloud_s} |")
    print("")
    for fr, passed, info, _i, _c in rows:
        for note in info["notes"]:
            print(f"  [{fr}] {note}")

    print("")
    print(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
#endregion
