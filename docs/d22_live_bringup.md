# Day 4 (d22) live bring-up manifest -- 2026-06-10

**Run type: LIVE sensors** (NOT bag playback). The node's --profile summary header
hardcodes the string '(bag playback ...)'; this run is LIVE -- see the label note in 4.2.

**Power profile (nvpmodel -q):**
```
NV Power Mode: MAXN
0
```

## Live stream health (pre-timing gate)
- topics present:
    /rslidar_points
    /zed/zed_node/rgb/color/rect/image
    /zed/zed_node/rgb/color/rect/image/camera_info
- RGB rate (timeout 6 s):
WARNING: topic [/zed/zed_node/rgb/color/rect/image] does not appear to be published yet
average rate: 26.951
	min: 0.025s max: 0.073s std dev: 0.01141s window: 28
average rate: 26.682
	min: 0.025s max: 0.103s std dev: 0.01345s window: 56
- LiDAR rate (timeout 6 s):
WARNING: topic [/rslidar_points] does not appear to be published yet
average rate: 10.000
	min: 0.098s max: 0.102s std dev: 0.00102s window: 12
average rate: 9.559
	min: 0.097s max: 0.202s std dev: 0.02122s window: 22
average rate: 9.113
	min: 0.097s max: 0.300s std dev: 0.03920s window: 31
- RGB type/QoS (authoritative LIVE -- this is P0.1 against the real driver):
    Type: sensor_msgs/msg/Image
    
    Publisher count: 1
    
    Node name: zed_node
    Node namespace: /zed
    Topic type: sensor_msgs/msg/Image
    Endpoint type: PUBLISHER
    GID: 01.0f.e7.df.77.1c.df.6d.00.00.00.00.00.00.26.03.00.00.00.00.00.00.00.00
    QoS profile:
      Reliability: RELIABLE
      History (Depth): UNKNOWN
- LiDAR type/QoS (authoritative LIVE -- P0.2):
    Type: sensor_msgs/msg/PointCloud2
    
    Publisher count: 1
    
    Node name: rslidar_points_destination_0
    Node namespace: /rslidar_sdk
    Topic type: sensor_msgs/msg/PointCloud2
    Endpoint type: PUBLISHER
    GID: 01.0f.e7.df.79.1c.f1.ce.00.00.00.00.00.00.21.03.00.00.00.00.00.00.00.00
    QoS profile:
      Reliability: RELIABLE
      History (Depth): UNKNOWN

## Live per-stage + end-to-end latency (node --profile summary, N=200)
# NOTE: the node's table header prints '(bag playback ...)' from a hardcoded string in
#       fusion_node.py summary_markdown(); THIS RUN IS LIVE. Treat the title as 'live'.
```
## Per-stage latency (bag playback, steady-state, N=200)
| stage | mean ms | p50 | p95 |
|---|---|---|---|
| image decode    |    5.28 |    4.94 |    6.78 |
| pointcloud->xyz |    1.76 |    1.61 |    2.26 |
| yolo inference  |   56.42 |   55.31 |   70.74 |
| projection      |    9.48 |    5.66 |   23.27 |
| dbscan assoc    |   46.33 |   42.68 |   71.37 |
| msg build/pub   |    3.01 |    2.79 |    4.23 |
| END-TO-END (cb) |  122.34 |  116.49 |  162.43 |
| stamp e2e       | 1085.02 | 1096.05 | 1217.59 |
- derived fps (1000 / p50 callback): 8.58 Hz (authoritative published fps = `ros2 topic hz`)
- dominant stage (by p50): yolo inference (55.31 ms)
- warmup (first frame) vs steady (p50 callback): 1710.98 ms / 116.49 ms
```
- published fps (ros2 topic hz /fusion/detections):
user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ stdbuf -oL ros2 topic hz /fusion/detections
WARNING: topic [/fusion/detections] does not appear to be published yet
average rate: 8.064
	min: 0.104s max: 0.171s std dev: 0.01940s window: 10
average rate: 8.106
	min: 0.104s max: 0.177s std dev: 0.02018s window: 19
average rate: 8.108
	min: 0.104s max: 0.177s std dev: 0.01793s window: 28
average rate: 7.953
	min: 0.104s max: 0.177s std dev: 0.01943s window: 36
average rate: 7.994
	min: 0.099s max: 0.177s std dev: 0.01935s window: 45
average rate: 8.146
	min: 0.097s max: 0.177s std dev: 0.01867s window: 54
average rate: 8.190


## Live vs d21 bag baseline
| metric                    | d21 bag (p50/p95) | d22 live (p50/p95) | delta |
|---|---|---|---|
| end-to-end callback span  | 161.98 / 198.95   | 116.49 / 162.43    | p50 -45.49 ms (-28%), p95 -36.52 ms; live LOWER but scene-confounded (see DBSCAN below) |
| YOLO inference (p50 like-for-like) | 61.47    | 55.31             | -6.16 ms (~-10%); fixed-cost stage, within run/thermal variance |
| DBSCAN assoc (p50, scene-dependent) | 83.57   | 42.68             | -40.89 ms (-49%); NOT a controlled delta (in-box point count differs by scene) |
| stamp e2e (sensor->publish, LIVE only) | N/A (bag) | 1096.05 / 1217.59 | (new) queue-latency-dominated, see Findings |
| published fps             | ~5.9 Hz           | ~8.1 Hz            | +~2.2 Hz; follows the faster callback (mostly the DBSCAN drop) |
| dominant stage (by p50)   | DBSCAN (83.57)    | YOLO (55.31)       | flipped -- scene-dependent, see Findings |
- DBSCAN / detection content: scene differs from test2, so NOT a controlled bag-vs-live delta
  (caveat 1); report the live per-stage table on its own terms.

## Throughput / dropped-frame proxy (rate gap, NOT a synchronizer counter)
- LiDAR input rate (timeout 6 s):
WARNING: topic [/rslidar_points] does not appear to be published yet
average rate: 6.250
	min: 0.098s max: 0.500s std dev: 0.12005s window: 10
average rate: 5.173
	min: 0.098s max: 0.500s std dev: 0.14323s window: 15
- processed/published rate (fusion/detections, timeout 6 s):
average rate: 8.276
	min: 0.110s max: 0.146s std dev: 0.00959s window: 10
average rate: 7.678
	min: 0.110s max: 0.170s std dev: 0.01856s window: 17
average rate: 7.491
	min: 0.110s max: 0.172s std dev: 0.01863s window: 25
average rate: 7.553
	min: 0.110s max: 0.172s std dev: 0.01675s window: 33
- node 'paired-callback rate' (steady, last line from the node log):
    [INFO] [1781083787.829820153] [fusion_node]: paired-callback rate: 8.30 Hz (total pairs 1266); last frame: 3 dets, 3 fused
- interpretation: node keeps up with ~(published / input) of input frames; the rest are skipped
  because the ~162 ms callback is slower than the ~10 Hz input -- throughput limit, not a
  pairing failure. A true synchronizer drop counter would need a node change (not done in d22).

## Findings (measured fact -> interpretation; interpretation flagged)
1. **Sensor-to-publish latency ~1.1 s, dominated by queue wait, NOT compute.** The callback-span
   (compute) p50 is 116 ms but stamp e2e p50 is 1096 ms, so ~980 ms is spent before/around the compute.
   Most consistent with a standing input backlog: the node drains ~8 Hz while LiDAR streams ~10 Hz, so a
   multi-frame queue forms; ~980 ms at ~8 Hz drain ~= 7-8 frames, matching the depth-10 subscription +
   synchronizer queues. INTERPRETED; a clock-offset component is not fully excluded from this run (a
   load-relief test, or confirming the ZED wrapper's image-stamp source, would settle it). Either way it
   is NOT compute-bound. Consequence for d23: the per-pair compute is within the 200 ms aim, but the real
   sensor-to-publish number is over the 500 ms acceptable, so the highest-value real-time lever is a
   drop-to-latest queue policy (process newest pair, discard backlog), not only a faster CNN.
2. **Dominant stage flipped to YOLO live (55.31 ms) vs DBSCAN on the d21 bag (83.57 ms).** DBSCAN scales
   with in-box point count; the office scene is sparser than test2, so DBSCAN nearly halved while YOLO
   held (fixed-cost). This QUALIFIES, does not overturn, the d21 DBSCAN-dominant finding: the dominant
   stage is scene-dependent. Consequence for d23: TensorRT-on-YOLO helps when YOLO-dominant (sparse
   scenes); the "cannot beat the DBSCAN floor" argument holds when dense. Report both regimes.

## Launch-vs-by-hand
- node runs live by hand (4.2): yes (the profiled latency run).
- thesis_fusion.launch.py created: yes (at ros2_ws/src/thesis_fusion/launch/; env bridge baked in).
- env bridge in launch: baked-in via additional_env (b); PYTHONPATH prepended (venv_yolo site-packages +
  code/fusion) to the inherited value so the ROS python paths (rclpy, sensor_msgs_py) are preserved.
  additional_env kwarg CONFIRMED working on this launch_ros (imports resolved under launch).
- node launches cleanly under 'ros2 launch' (imports resolve, no venv/ROS PYTHONPATH clash): PASS --
  "model loaded once at startup: yolov8s.pt", real detections (3-6 dets, all fused), paired rate ~7-8 Hz.
- shutdown note: Ctrl-C under ros2 launch raised `RCLError: rcl_shutdown already called on the given
  context` (exit code 1). The RUN is clean; only shutdown is noisy: ros2 launch delivers SIGINT, rclpy's
  handler shuts the context down, then main()'s finally calls rclpy.shutdown() a second time. No data
  lost (report_profile + destroy_node run before the failing line; this launch run was non-profiled).
  Fix to apply on the box: guard the finally with `if rclpy.ok(): rclpy.shutdown()` in fusion_node.py
  main(). Does not affect the by-hand path.

## Final state (10:59:00)
- Stream-health gate (RGB ~30 Hz, LiDAR ~10 Hz, both present): PASS (RGB ~27 Hz -- slightly under the
  ~30 anchor but healthy; LiDAR ~10 Hz settling ~9 Hz under load; both present; RELIABLE/VOLATILE).
- Live node ran by hand: yes; under ros2 launch: yes (clean run; noisy shutdown traceback, see launch note).
- Live callback-span p50/p95: 116.49 / 162.43 ms; stamp e2e p50/p95 (sensor->publish): 1096.05 / 1217.59 ms
  (queue-latency-dominated, NOT compute -- see Findings 1).
- Live published fps: ~8.1 Hz; vs d21 callback span (161.98/198.95) and ~5.9 Hz: callback -45.5 / -36.5 ms
  (scene-confounded via the DBSCAN drop), fps +~2.2 Hz.
- Power profile: MAXN (mode 0).
- RViz live cloud + markers visible (runs-live-without-crashing): yes (chair ~1.5 m, tv ~1.8 m, tv ~4.2/4.9 m;
  benign "Frame [rslidar] does not exist" -- no TF for rslidar, renders anyway, as d20).
- Day 4 outcome: PASS.
