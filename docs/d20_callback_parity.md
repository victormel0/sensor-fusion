# Day 2 (d20) callback port + parity manifest -- 2026-06-09

**Goal:** real frustum association in the callback (reusing files 6-7) + detections + markers + parity vs fused_out/.

**Reused unchanged:** code/fusion/project_lidar.py (project, campose); code/fusion/frustum_fuse.py (load_calib, load_dbscan, associate_box).
**Extrinsic/intrinsics:** calibration/calib_T_lidar_camera_2026_05_26.json; fx=335.13 fy=359.35 cx=486.26 cy=291.70.

## Callback wiring
- project / associate_box / load_calib / load_dbscan imported from files 6-7 (NOT reimplemented): yes (exact parity confirms it)
- calib loaded once in __init__ (R,t,intrinsics): yes
- Detection3D built (fused: class+conf+3D; camera_only: class+conf, zero bbox): yes
- Detection3DArray.header.frame_id=rslidar, stamp=image stamp: yes
- vision_msgs nesting confirmed on this box: yes (empirical -- node builds/publishes Detection3DArray via results[].hypothesis.class_id/.score with no AttributeError, and parity PASSED; explicit `ros2 interface show` dump not separately captured)

## Node run (bag playback)
- 'model loaded' lines (must be 1): 1
- last rate + det counts: [INFO] [1780993330.698314308] [fusion_node]: paired-callback rate: 6.24 Hz (total pairs 337); last frame: 8 dets, 8 fused
- detections publish rate (5 s sample):
average rate: 6.344
	min: 0.151s max: 0.169s std dev: 0.00552s window: 8
average rate: 6.320
	min: 0.146s max: 0.169s std dev: 0.00747s window: 15
average rate: 6.274
	min: 0.146s max: 0.172s std dev: 0.00724s window: 22
average rate: 6.222
	min: 0.146s max: 0.177s std dev: 0.00754s window: 29
average rate: 6.209
	min: 0.146s max: 0.178s std dev: 0.00743s window: 36
average rate: 6.186
	min: 0.146s max: 0.194s std dev: 0.00875s window: 43
average rate: 6.184
	min: 0.146s max: 0.194s std dev: 0.00859s window: 50

/home/user/Documents/workspace/sensor-fusion/venv_yolo/lib/python3.10/site-packages/matplotlib/projections/__init__.py:63: UserWarning: Unable to import Axes3D. This may be due to multiple versions of Matplotlib being installed (e.g. as a system package and as a pip package). As a result, the 3D projection is not available.
  warnings.warn("Unable to import Axes3D. This may be due to multiple versions of "
parity: frames=['00100', '00300', '00500'] pos_tol=0.05 m bin_channels=5
        frames_dir=code/fusion/frames_out
        bins_dir  =code/bag_to_bin/out
        offline   =code/fusion/fused_out

ERROR: missing input for frame 00100: code/bag_to_bin/out/00100.bin
# ^ first attempt: parity_check.py looked for a bare 00100.bin, but the .bin files carry the recording
#   prefix (test2_marked_distances_00100.bin). Fixed the script to auto-resolve the prefix; re-ran below -> PASS.
/home/user/Documents/workspace/sensor-fusion/venv_yolo/lib/python3.10/site-packages/matplotlib/projections/__init__.py:63: UserWarning: Unable to import Axes3D. This may be due to multiple versions of Matplotlib being installed (e.g. as a system package and as a pip package). As a result, the 3D projection is not available.
  warnings.warn("Unable to import Axes3D. This may be due to multiple versions of "
parity: frames=['00100', '00300', '00500'] pos_tol=0.05 m bin_channels=5
        frames_dir=code/fusion/frames_out
        bins_dir  =code/bag_to_bin/out
        offline   =code/fusion/fused_out

| frame | result | boxes (c/o) | src flips | max range d (m) | max centroid d (m) | fused classes | img dec | cloud dec |
|---|---|---|---|---|---|---|---|---|
| 00100 | PASS | 11/11 | 0 | 0.0000 | 0.0000 | match | PASS | 0 |
| 00300 | PASS | 10/10 | 0 | 0.0000 | 0.0000 | match | PASS | 0 |
| 00500 | PASS | 10/10 | 0 | 0.0000 | 0.0000 | match | PASS | 0 |


OVERALL: PASS

## Final state (09:31:47)
- Real detections + markers publishing: yes (8 dets / 8 fused on the sampled frame; markers in RViz, 425 received)
- vision_msgs nesting confirmed on this box: yes (empirical, see Callback wiring above)
- Parity vs fused_out/ on 00100/00300/00500: PASS on all three (11/11, 10/10, 10/10 boxes; 0 source flips; classes match; image-decoder PASS; cloud-decoder delta 0)
- Measured max range / centroid delta (m): 0.0000 / 0.0000
- Day 2 outcome: PASS
- Runtime note: detections publish ~6.2 Hz vs ~10 Hz input (per pair 0.146-0.194 s); on_pair (YOLO+projection+DBSCAN) is the bottleneck -> Day-3 latency target.
