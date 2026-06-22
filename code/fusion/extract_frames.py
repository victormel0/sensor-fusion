#!/usr/bin/env python3
"""
extract_frames.py -- extract time-synchronized (LiDAR cloud, RGB image) pairs from a ROS 2 bag
for offline frustum fusion.

Run in the ROS 2 environment (NOT venv_openpcdet / venv_yolo). Needs: rosbag2_py, rclpy,
sensor_msgs, sensor_msgs_py, cv2, numpy. NOTE: cv_bridge is NO LONGER required (see the
"Image decode" region) -- the image is decoded directly from the message buffer so the script
does not depend on the numpy-1.x-compiled cv_bridge_boost extension, which fails to import under
numpy 2.x with "AttributeError: _ARRAY_API not found". The only OpenCV use left is cv2.imwrite,
verified working under the ROS-env cv2 4.13.0 + numpy 2.2.6 on this box (d24).

For each selected LiDAR frame (by message index; default the Day-6 PointPillars baseline frames
via --frames, or every Nth via --stride), it writes:
    <out>/<idx>.png    the RGB image whose header stamp is nearest the LiDAR frame's header stamp
    <out>/<idx>.json   pairing metadata: lidar_stamp, image_stamp, dt_ms, within_slop, n_points
    <out>/<idx>.bin    OPTIONAL (--write-bin): 5-channel float32 [x,y,z,intensity,0], LiDAR frame

The LiDAR .bin is OFF by default: the LiDAR-only side of the comparison should use the proven
bag_to_bin.py (same invocation as Day 6) so the bins stay byte-identical. --write-bin is provided
only for convenience; if used, diff one frame against bag_to_bin.py's output to confirm the layout
matches before trusting it.

Memory is bounded: only the selected LiDAR clouds and their matched images are held (a handful),
not the whole bag.

NOTE: the rosbag2_py reader setup mirrors bag_to_bin.py. If bag_to_bin.py uses a different
StorageOptions/ConverterOptions setup on this machine, reuse that exact setup here.
"""

import argparse
import json
import os

import numpy as np

#region [ROS imports]
import rclpy.serialization
import rosbag2_py
from sensor_msgs.msg import Image, PointCloud2
from sensor_msgs_py import point_cloud2
import cv2
#endregion


#region [Bag reading]
def open_reader(bag_path):
    storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    return reader


def iter_topic(bag_path, topic):
    """Yield raw serialized messages for one topic, in bag order."""
    reader = open_reader(bag_path)
    reader.set_filter(rosbag2_py.StorageFilter(topics=[topic]))
    while reader.has_next():
        tname, data, _bag_time = reader.read_next()
        if tname == topic:
            yield data
#endregion


#region [Image decode (cv_bridge-free)]
# sensor_msgs/Image -> BGR uint8 ndarray, driven by msg.encoding. This replaces
# cv_bridge.imgmsg_to_cv2 so the script does not import cv_bridge_boost (compiled against
# numpy 1.x, broken under numpy 2.x). Only 8-bit colour/mono encodings are handled, which is
# all the ZED rect colour stream publishes; a clear error is raised for anything else rather
# than silently mis-decoding.
_CHANNELS = {
    "bgra8": 4,
    "rgba8": 4,
    "bgr8": 3,
    "rgb8": 3,
    "mono8": 1,
}


def imgmsg_to_bgr(msg):
    enc = msg.encoding.lower()
    if enc not in _CHANNELS:
        raise ValueError(
            f"unsupported image encoding '{msg.encoding}'. Supported: {sorted(_CHANNELS)}. "
            "Add a case to _CHANNELS / imgmsg_to_bgr if the camera publishes a different "
            "8-bit encoding (do not guess -- check the topic's actual encoding first)."
        )
    nch = _CHANNELS[enc]
    buf = np.frombuffer(msg.data, dtype=np.uint8)
    # reshape using step (row stride in bytes) to account for any row padding, then slice the
    # actual pixel columns
    buf = buf.reshape(msg.height, msg.step)
    img = buf[:, : msg.width * nch].reshape(msg.height, msg.width, nch)
    if enc == "bgra8":
        return img[:, :, :3].copy()            # B,G,R,A -> B,G,R
    if enc == "rgba8":
        return img[:, :, 2::-1].copy()         # R,G,B,A -> B,G,R
    if enc == "bgr8":
        return img.copy()
    if enc == "rgb8":
        return img[:, :, ::-1].copy()          # R,G,B -> B,G,R
    # mono8
    return np.repeat(img, 3, axis=2).copy()    # gray -> 3-channel BGR
#endregion


#region [Helpers]
def stamp_ns(header):
    return int(header.stamp.sec) * 1_000_000_000 + int(header.stamp.nanosec)


def cloud_to_bin_array(cloud_msg):
    """5-channel float32 [x, y, z, intensity, 0]; matches the nuScenes layout bag_to_bin.py uses.

    Handles both the structured-ndarray return of sensor_msgs_py.read_points (Humble, and the
    only path that works cleanly under numpy 2.x) and the older tuple-iterable return.
    """
    pts = point_cloud2.read_points(
        cloud_msg, field_names=("x", "y", "z", "intensity"), skip_nans=True
    )
    if isinstance(pts, np.ndarray) and pts.dtype.names is not None:
        n = pts.shape[0]
        out = np.zeros((n, 5), dtype=np.float32)
        out[:, 0] = pts["x"]
        out[:, 1] = pts["y"]
        out[:, 2] = pts["z"]
        out[:, 3] = pts["intensity"]
        return out
    arr = np.array([[r[0], r[1], r[2], r[3]] for r in pts], dtype=np.float32)
    if arr.shape[0] == 0:
        return arr.reshape(-1, 5)
    time_col = np.zeros((arr.shape[0], 1), dtype=np.float32)
    return np.hstack([arr, time_col]).astype(np.float32)
#endregion


#region [Main]
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bag", required=True, help="path to the bag directory")
    parser.add_argument("--lidar-topic", default="/rslidar_points")
    parser.add_argument("--image-topic", default="/zed/zed_node/rgb/color/rect/image")
    parser.add_argument("--out", default="code/fusion/frames_out")
    parser.add_argument("--stride", type=int, default=100)
    parser.add_argument("--frames", default="", help="comma-separated explicit LiDAR indices; overrides --stride")
    parser.add_argument("--max-dt-ms", type=float, default=50.0)
    parser.add_argument("--write-bin", action="store_true", help="also write the 5-ch .bin (see header note)")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # Pass 1: pick the selected LiDAR frames; keep only their stamps (and clouds if --write-bin).
    wanted = set(int(x) for x in args.frames.split(",")) if args.frames.strip() else None
    selected = {}  # idx -> {"l_ns": int, "cloud": PointCloud2 or None, "best_dt": float, "img": cv or None, "img_ns": int}
    for idx, raw in enumerate(iter_topic(args.bag, args.lidar_topic)):
        keep = (idx in wanted) if wanted is not None else (idx % args.stride == 0)
        if not keep:
            continue
        cloud = rclpy.serialization.deserialize_message(raw, PointCloud2)
        selected[idx] = {
            "l_ns": stamp_ns(cloud.header),
            "cloud": cloud if args.write_bin else None,
            "best_dt": float("inf"),
            "img": None,
            "img_ns": None,
        }
    if not selected:
        print("no LiDAR frames matched the selection")
        return

    # Pass 2: walk the images once; for each selected frame keep the nearest-stamp image only.
    for raw in iter_topic(args.bag, args.image_topic):
        img_msg = rclpy.serialization.deserialize_message(raw, Image)
        i_ns = stamp_ns(img_msg.header)
        for idx, rec in selected.items():
            dt = abs(i_ns - rec["l_ns"]) / 1e6
            if dt < rec["best_dt"]:
                rec["best_dt"] = dt
                rec["img"] = imgmsg_to_bgr(img_msg)
                rec["img_ns"] = i_ns

    # Write outputs.
    for idx in sorted(selected):
        rec = selected[idx]
        name = f"{idx:05d}"
        if rec["img"] is None:
            print(f"{name}: no image found, skipped")
            continue
        cv2.imwrite(os.path.join(args.out, name + ".png"), rec["img"])

        n_points = None
        if args.write_bin and rec["cloud"] is not None:
            arr = cloud_to_bin_array(rec["cloud"])
            arr.tofile(os.path.join(args.out, name + ".bin"))
            n_points = int(arr.shape[0])

        meta = {
            "frame": name,
            "lidar_stamp_ns": rec["l_ns"],
            "image_stamp_ns": rec["img_ns"],
            "dt_ms": round(rec["best_dt"], 3),
            "within_slop": bool(rec["best_dt"] <= args.max_dt_ms),
            "n_points": n_points,
        }
        with open(os.path.join(args.out, name + ".json"), "w") as f:
            json.dump(meta, f, indent=2)

        flag = "" if rec["best_dt"] <= args.max_dt_ms else "  [WARN dt over slop]"
        print(f"{name}: dt={rec['best_dt']:6.2f} ms{flag}")

    print(f"done: {len(selected)} frame(s) -> {args.out}")


if __name__ == "__main__":
    main()
#endregion
