#!/usr/bin/env python3
"""
bag_to_bin.py  --  Convert /rslidar_points frames from a ROS 2 bag into the
N x 5 float32 .bin format expected by OpenPCDet's nuScenes PointPillars config
(cbgs_pp_multihead.yaml).

Thesis: LiDAR-camera sensor fusion (Victor, PoliTO @ Deepware), Week 2 Day 6, step §6.1.

WHERE TO RUN THIS
-----------------
Run in the ROS 2 environment, NOT in venv_openpcdet. The venv was created
(step-by-step §5.2) deliberately isolated from system/ROS packages to avoid
numpy/PyYAML conflicts, so it cannot import rosbag2_py / rclpy / sensor_msgs.
This conversion needs only ROS + numpy (no torch / pcdet), so it belongs in
the ROS environment:

    source /opt/ros/humble/setup.bash
    source ~/Documents/workspace/sensor-fusion/ros2_ws/install/setup.bash
    python3 code/bag_to_bin/bag_to_bin.py --bag recordings/test2_marked_distances

The .bin files this writes are plain little-endian float32 (environment-neutral)
and are then consumed from inside venv_openpcdet in §6.2 for inference. That
ROS-env -> .bin -> venv-inference split is the intended workflow; do not try to
run this script inside the activated venv.

OUTPUT FORMAT
-------------
Each frame -> one little-endian float32 file, N x 5, columns in order:

    [ x, y, z, intensity, time_offset ]

  - x, y, z       : metres, in the LiDAR frame. ROS REP-103 convention
                    (x forward, y left, z up) matches what OpenPCDet's nuScenes
                    loader expects for the LiDAR/ego frame, so NO axis swap is
                    applied here. If detections come out rotated 90 deg, this is
                    the first thing to revisit.
  - intensity     : RoboSense publishes intensity in [0, 255]; nuScenes weights
                    were trained on Velodyne intensity (also ~[0, 255]), so no
                    rescale is applied. (If the model's scores look uniformly
                    poor, try dividing intensity by 255.0 -- some nuScenes
                    pipelines normalise to [0, 1]. Documented as a knob below.)
  - time_offset   : 0.0 for every point. nuScenes uses this channel for the
                    per-point time delta across its 10 accumulated sweeps; we do
                    single-frame inference, so it is zero.

We do NOT range-crop the cloud here -- OpenPCDet's POINT_CLOUD_RANGE in the model
config handles cropping. We only drop non-finite (NaN/inf) points, which the
detector cannot ingest.

USAGE EXAMPLES
--------------
  # All LiDAR frames in the bag:
  python3 bag_to_bin.py --bag recordings/test2_marked_distances

  # The static marked-distance scene: one representative middle frame is enough.
  # (Bag has ~803 LiDAR frames; pick e.g. frame 400.)
  python3 bag_to_bin.py --bag recordings/test2_marked_distances \
      --start-frame 400 --max-frames 1

  # Every 50th frame, to spot-check a handful:
  python3 bag_to_bin.py --bag recordings/test2_marked_distances --stride 50

  # Normalise intensity to [0, 1] instead of leaving it in [0, 255]:
  python3 bag_to_bin.py --bag recordings/test2_marked_distances --intensity-scale 0.00392156862
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

# ROS 2 imports -- these only resolve when the ROS environment is sourced.
try:
    import rosbag2_py
    from rclpy.serialization import deserialize_message
    from sensor_msgs.msg import PointCloud2
    import sensor_msgs_py.point_cloud2 as pc2
except ImportError as e:
    sys.stderr.write(
        "\nERROR: ROS 2 Python packages not found.\n"
        "This script must be run with the ROS 2 environment sourced:\n"
        "    source /opt/ros/humble/setup.bash\n"
        "    source ~/Documents/workspace/sensor-fusion/ros2_ws/install/setup.bash\n"
        "Do NOT run it inside venv_openpcdet.\n"
        f"(import error: {e})\n\n"
    )
    sys.exit(1)


def detect_storage_id(bag_dir: Path, override: str | None) -> str:
    """Return the rosbag2 storage identifier (sqlite3 or mcap).

    If --storage-id was given, trust it. Otherwise read it from the bag's
    metadata.yaml; fall back to inspecting file extensions; final fallback
    is sqlite3.
    """
    if override:
        return override

    meta = bag_dir / "metadata.yaml"
    if meta.is_file():
        # Cheap line-scan instead of pulling in a YAML dep; the field looks like
        #   storage_identifier: sqlite3
        for line in meta.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("storage_identifier:"):
                value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value

    # Fall back to file extensions inside the bag directory.
    if any(bag_dir.glob("*.mcap")):
        return "mcap"
    if any(bag_dir.glob("*.db3")):
        return "sqlite3"

    return "sqlite3"


def open_reader(bag_dir: Path, storage_id: str) -> rosbag2_py.SequentialReader:
    """Open a SequentialReader on the given bag directory."""
    reader = rosbag2_py.SequentialReader()
    storage_options = rosbag2_py.StorageOptions(uri=str(bag_dir), storage_id=storage_id)
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )
    reader.open(storage_options, converter_options)
    return reader


def topic_exists(reader: rosbag2_py.SequentialReader, topic: str) -> bool:
    """Check whether the requested topic is present in the bag."""
    topic_names = {t.name for t in reader.get_all_topics_and_types()}
    return topic in topic_names


def cloud_to_array(msg: PointCloud2, intensity_scale: float) -> np.ndarray:
    """Convert a PointCloud2 message to an N x 5 float32 array.

    Columns: x, y, z, intensity * intensity_scale, 0.0 (time_offset).
    Non-finite points are dropped.
    """
    pts = pc2.read_points(
        msg, field_names=("x", "y", "z", "intensity"), skip_nans=True
    )

    # Humble's read_points returns a structured ndarray (fields accessed by name).
    # Older APIs returned a generator/list of tuples -- handle both.
    if isinstance(pts, np.ndarray) and pts.dtype.names is not None:
        n = pts.shape[0]
        out = np.zeros((n, 5), dtype=np.float32)
        out[:, 0] = pts["x"]
        out[:, 1] = pts["y"]
        out[:, 2] = pts["z"]
        out[:, 3] = pts["intensity"]
    else:
        arr = np.asarray(list(pts), dtype=np.float32)
        if arr.ndim != 2 or arr.shape[1] < 4:
            return np.empty((0, 5), dtype=np.float32)
        out = np.zeros((arr.shape[0], 5), dtype=np.float32)
        out[:, :4] = arr[:, :4]

    # Apply intensity scaling (default 1.0 = leave in [0, 255]).
    if intensity_scale != 1.0:
        out[:, 3] *= intensity_scale

    # Column 4 (time_offset) stays 0.0.

    # Drop any remaining non-finite points (skip_nans handles NaN; this also
    # catches inf, which the detector's voxeliser cannot ingest).
    finite_mask = np.isfinite(out[:, :4]).all(axis=1)
    if not finite_mask.all():
        out = out[finite_mask]

    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert /rslidar_points frames from a ROS 2 bag to "
        "OpenPCDet nuScenes-PointPillars .bin files (N x 5 float32).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--bag",
        required=True,
        type=Path,
        help="Path to the ROS 2 bag directory (the folder containing metadata.yaml).",
    )
    parser.add_argument(
        "--topic",
        default="/rslidar_points",
        help="LiDAR PointCloud2 topic to extract.",
    )
    parser.add_argument(
        "--out",
        "--out-dir",
        dest="out_dir",
        type=Path,
        default=Path("code/bag_to_bin"),
        help="Directory to write .bin files into (created if missing). "
        "(--out and --out-dir are aliases.)",
    )
    parser.add_argument(
        "--format",
        choices=["nuscenes", "kitti"],
        default="nuscenes",
        help="Output channel layout. 'nuscenes' = 5 channels "
        "[x, y, z, intensity, time_offset] for cbgs_pp_multihead.yaml; "
        "'kitti' = 4 channels [x, y, z, intensity] for kitti_models/*.yaml.",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Output filename prefix. Defaults to the bag directory name.",
    )
    parser.add_argument(
        "--storage-id",
        default=None,
        help="rosbag2 storage id (sqlite3 / mcap). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--start-frame",
        type=int,
        default=0,
        help="Index of the first LiDAR frame to write (0-based).",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Maximum number of frames to write (after --start-frame and --stride). "
        "Default: all.",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Write every Nth frame (1 = every frame).",
    )
    parser.add_argument(
        "--intensity-scale",
        type=float,
        default=1.0,
        help="Multiply intensity by this. 1.0 keeps [0,255]; use ~0.00392157 "
        "(=1/255) to normalise to [0,1] if the model expects that.",
    )
    args = parser.parse_args()

    bag_dir = args.bag.expanduser().resolve()
    if not bag_dir.is_dir():
        sys.stderr.write(f"ERROR: bag directory not found: {bag_dir}\n")
        return 1

    prefix = args.prefix or bag_dir.name
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    storage_id = detect_storage_id(bag_dir, args.storage_id)
    print(f"Bag:           {bag_dir}")
    print(f"Storage id:    {storage_id}")
    print(f"Topic:         {args.topic}")
    print(f"Output dir:    {out_dir}")
    print(f"Output prefix: {prefix}")
    print(f"Format:        {args.format} "
          f"({'5 channels [x,y,z,intensity,time_offset]' if args.format == 'nuscenes' else '4 channels [x,y,z,intensity]'})")
    print(f"Selection:     start={args.start_frame}, stride={args.stride}, "
          f"max={args.max_frames if args.max_frames is not None else 'all'}")
    print(f"Intensity:     x{args.intensity_scale} "
          f"({'kept in [0,255]' if args.intensity_scale == 1.0 else 'rescaled'})")
    print("-" * 72)

    reader = open_reader(bag_dir, storage_id)
    if not topic_exists(reader, args.topic):
        available = ", ".join(sorted(t.name for t in reader.get_all_topics_and_types()))
        sys.stderr.write(
            f"ERROR: topic '{args.topic}' not in bag.\nAvailable topics: {available}\n"
        )
        return 1

    # Restrict the reader to just the LiDAR topic for speed.
    storage_filter = rosbag2_py.StorageFilter(topics=[args.topic])
    reader.set_filter(storage_filter)

    msg_index = -1   # index over all messages on the topic
    written = 0      # number of .bin files written
    while reader.has_next():
        topic, data, _t = reader.read_next()
        if topic != args.topic:
            continue
        msg_index += 1

        # Apply start-frame / stride selection.
        if msg_index < args.start_frame:
            continue
        if (msg_index - args.start_frame) % args.stride != 0:
            continue
        if args.max_frames is not None and written >= args.max_frames:
            break

        msg = deserialize_message(data, PointCloud2)
        arr = cloud_to_array(msg, args.intensity_scale)

        if arr.shape[0] == 0:
            print(f"[frame {msg_index:05d}] WARNING: 0 valid points after "
                  f"filtering -- skipped, no file written.")
            continue

        # nuscenes = 5 channels [x,y,z,intensity,time_offset]; kitti = 4 channels.
        arr_to_write = arr if args.format == "nuscenes" else arr[:, :4]

        out_path = out_dir / f"{prefix}_{msg_index:05d}.bin"
        arr_to_write.astype("<f4").tofile(out_path)   # little-endian float32
        written += 1

        # Per-frame sanity line: point count + value ranges. Cheap insurance
        # against silent coordinate/units problems before running the model.
        x, y, z, inten = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]
        print(
            f"[frame {msg_index:05d}] {arr.shape[0]:6d} pts -> {out_path.name}  "
            f"x[{x.min():+6.1f},{x.max():+6.1f}] "
            f"y[{y.min():+6.1f},{y.max():+6.1f}] "
            f"z[{z.min():+6.1f},{z.max():+6.1f}] "
            f"i[{inten.min():.1f},{inten.max():.1f}]"
        )

    print("-" * 72)
    print(f"Done. Wrote {written} .bin file(s) to {out_dir}")
    if written == 0:
        sys.stderr.write(
            "WARNING: no frames written. Check --start-frame / --max-frames / "
            "--stride and that the topic actually carries messages.\n"
        )
        return 1

    # Echo the exact format string for the §6.2 inference step.
    if args.format == "nuscenes":
        print("\nFormat written: N x 5 float32 little-endian, columns [x, y, z, intensity, time_offset].")
    else:
        print("\nFormat written: N x 4 float32 little-endian, columns [x, y, z, intensity].")
    print("Feed these to OpenPCDet from inside venv_openpcdet (§6.2).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
