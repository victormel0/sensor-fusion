#!/usr/bin/env python3
"""
Bag analysis for the sensor-fusion thesis.

Reads a ROS 2 sqlite3 bag and prints a markdown report covering:
  - Per-topic message count and observed rate
  - Inter-message arrival interval (mean, median, min, max, stdev)
  - Largest gaps (potential drops)
  - Difference between message arrival time and header timestamp (latency)
  - Camera-LiDAR pairing quality: for each LiDAR frame, nearest image dt

Run from anywhere on the ZED Box, with ROS 2 sourced:
    source /opt/ros/humble/setup.bash
    cd ~/Documents/workspace/sensor-fusion/code/bag_analysis
    python3 bag_analysis.py ~/Documents/workspace/sensor-fusion/recordings/test1_first_recording

To save the report:
    python3 bag_analysis.py <bag_folder> > report.md
"""

import bisect
import statistics
import sys
from pathlib import Path

import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


CAMERA_TOPIC = '/zed/zed_node/rgb/color/rect/image'
LIDAR_TOPIC = '/rslidar_points'
PAIR_SLOP_MS = 50.0          # Day 5 sync target
DROP_GAP_FACTOR = 3.0        # an interval > N * median is a potential drop


def open_reader(bag_path: Path) -> rosbag2_py.SequentialReader:
    storage_options = rosbag2_py.StorageOptions(uri=str(bag_path), storage_id='sqlite3')
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr',
    )
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    return reader


def stat_line(label: str, values):
    if not values:
        return f'  - **{label}**: no data'
    return (
        f'  - **{label}**: '
        f'n={len(values)}, '
        f'mean={statistics.mean(values):.2f}, '
        f'median={statistics.median(values):.2f}, '
        f'stdev={statistics.pstdev(values):.2f}, '
        f'min={min(values):.2f}, '
        f'max={max(values):.2f}'
    )


def analyze(bag_folder: Path) -> None:
    if not bag_folder.is_dir():
        sys.exit(f'Not a directory: {bag_folder}')

    reader = open_reader(bag_folder)
    topic_types = {t.name: t.type for t in reader.get_all_topics_and_types()}

    # topic -> list of (bag_arrival_ns, header_ns_or_None)
    timeline: dict[str, list[tuple[int, int | None]]] = {t: [] for t in topic_types}

    # Resolve message classes once per type
    type_cache: dict[str, object] = {}
    for type_str in set(topic_types.values()):
        try:
            type_cache[type_str] = get_message(type_str)
        except Exception:
            type_cache[type_str] = None

    total_msgs = 0
    while reader.has_next():
        topic, raw_data, bag_ts_ns = reader.read_next()
        total_msgs += 1
        msg_cls = type_cache.get(topic_types[topic])
        header_ns = None
        if msg_cls is not None:
            try:
                msg = deserialize_message(raw_data, msg_cls)
                if hasattr(msg, 'header'):
                    header_ns = (msg.header.stamp.sec * 1_000_000_000
                                 + msg.header.stamp.nanosec)
            except Exception:
                pass
        timeline[topic].append((bag_ts_ns, header_ns))

    # Bag duration from arrival timestamps
    all_ts = [b for events in timeline.values() for b, _ in events]
    bag_start_ns = min(all_ts) if all_ts else 0
    bag_end_ns = max(all_ts) if all_ts else 0
    duration_s = (bag_end_ns - bag_start_ns) / 1e9

    # ---------------- Output ----------------
    print('# Bag analysis report')
    print()
    print(f'**Bag folder:** `{bag_folder.resolve()}`')
    print(f'**Duration (from arrival ts):** {duration_s:.2f} s')
    print(f'**Total messages:** {total_msgs}')
    print()
    print('## Per-topic statistics')
    print()
    for topic in sorted(timeline):
        events = timeline[topic]
        n = len(events)
        print(f'### `{topic}`')
        print(f'- type: `{topic_types[topic]}`')
        print(f'- count: **{n}**')

        if n < 2:
            print('- too few messages for interval stats')
            print()
            continue

        rate = n / duration_s if duration_s > 0 else 0
        print(f'- observed rate: **{rate:.2f} Hz**')

        intervals_ms = [(b - a) / 1e6 for (a, _), (b, _) in zip(events[:-1], events[1:])]
        print(stat_line('arrival interval (ms)', intervals_ms))

        median = statistics.median(intervals_ms)
        big_gaps = [v for v in intervals_ms if v > DROP_GAP_FACTOR * median]
        if big_gaps:
            print(f'  - **{len(big_gaps)} large gap(s) (>{DROP_GAP_FACTOR}× median, '
                  f'>{DROP_GAP_FACTOR * median:.1f} ms) — largest {max(big_gaps):.1f} ms**')
        else:
            print(f'  - no gaps larger than {DROP_GAP_FACTOR}× median ({DROP_GAP_FACTOR * median:.1f} ms)')

        with_header = [(b, h) for b, h in events if h is not None]
        if with_header:
            latencies_ms = [(b - h) / 1e6 for b, h in with_header]
            print(stat_line('arrival - header timestamp (ms)', latencies_ms))
        print()

    # ---------------- Pairing analysis ----------------
    cam = timeline.get(CAMERA_TOPIC, [])
    lid = timeline.get(LIDAR_TOPIC, [])
    if cam and lid:
        print('## Camera ↔ LiDAR pairing (by header timestamp)')
        print()
        print(f'For each LiDAR frame, find the nearest camera frame by header timestamp. '
              f'Slop window: ±{PAIR_SLOP_MS:.0f} ms.')
        print()
        cam_headers = sorted(h for _, h in cam if h is not None)
        lid_headers = sorted(h for _, h in lid if h is not None)
        if not cam_headers or not lid_headers:
            print('Headers missing on one or both topics, cannot pair.')
        else:
            dts_ms = []
            paired = 0
            for L in lid_headers:
                idx = bisect.bisect_left(cam_headers, L)
                candidates = []
                if idx < len(cam_headers):
                    candidates.append(cam_headers[idx])
                if idx > 0:
                    candidates.append(cam_headers[idx - 1])
                if not candidates:
                    continue
                best = min(candidates, key=lambda C: abs(C - L))
                dt_ms = abs(best - L) / 1e6
                dts_ms.append(dt_ms)
                if dt_ms <= PAIR_SLOP_MS:
                    paired += 1

            yield_pct = paired / len(lid_headers) * 100 if lid_headers else 0
            print(f'- LiDAR frames considered: **{len(lid_headers)}**')
            print(f'- Paired within slop: **{paired} ({yield_pct:.1f}%)**')
            print(stat_line('best dt per LiDAR frame (ms)', dts_ms))
            print()

    # ---------------- Verdict ----------------
    print('## Verdict')
    print()
    cam_n = len(timeline.get(CAMERA_TOPIC, []))
    lid_n = len(timeline.get(LIDAR_TOPIC, []))
    cam_rate = cam_n / duration_s if duration_s else 0
    lid_rate = lid_n / duration_s if duration_s else 0

    def verdict(ok: bool, line: str) -> str:
        return f'- {"✓" if ok else "✗"} {line}'

    print(verdict(cam_rate >= 25, f'Camera rate: {cam_rate:.1f} Hz (target ≥25 Hz)'))
    print(verdict(lid_rate >= 9.5, f'LiDAR rate: {lid_rate:.1f} Hz (target ≥9.5 Hz)'))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'Usage: python3 {sys.argv[0]} <bag_folder>')
    analyze(Path(sys.argv[1]))
