# Day 3 recording manifest -- 2026-05-25

**Location:** office, 14:04
**Free disk before recording:** 178G

## Scene description

Open-plan office. Rig (RoboSense H32F70 + ZED X One on the two-level chipboard mount from Week 1) sitting on the wooden desk at the workspace edge, base plate ~75 cm above the tiled floor, LiDAR centre ~14 cm above the base. Mixed lighting from overhead LED ceiling panels and daylight through the windows on the left of the room.

Scene content (geometric and reflectance variety for Koide's NID cost surface):

- Foreground (~1 m): wooden-frame chair with dark leather seat back, ~100 cm tall - the "Black chair" ground-truth marker.
- Mid (~1.8 m): open aluminium-framed doorway between the two rooms - the 180 cm-tall reference.
- Far (~4 m): blue swivel chair in the adjoining office, visible through the doorway - the "Blue chair @ 4 m" marker.
- Surrounding clutter useful as anchors during the slow-tilt calibration bags: dual-monitor and triple-monitor Dell desk setups left and right, glass partitions with painted-metal mullions, painted blue accent wall behind the doorway, a whiteboard with markings, exposed cable runs, ceiling tile grid, tiled floor.
- Reflectance variety: matte painted walls, fabric chair upholstery, dark plastic monitor bezels, glossy whiteboard, glass partitions (glass returns expected to be noisy - known LiDAR limitation, flag in Discussion).

Scene wide-shot: `docs/screenshots/d10_scene_wide.jpg`.

## Marked-distance ground truth

Marker-tape distance is the on-floor distance from the front of the rig base plate (≈ camera lens front per §3.3 of `week02_step_by_step.md`) to the floor projection of the object. The camera-lens-front and LiDAR-centre columns are **derived** from the marker distance and the Week 1 rig geometry (`T_lidar→camera ≈ (+0.08, 0.00, −0.14) m`, R = I - i.e. camera is 8 cm in front of the LiDAR centre and 14 cm below it). Horizontal-distance only; vertical offsets to chair tops / door top not separated out at this stage.


| Object | Marker tape (m) | From camera lens front (m) | From LiDAR centre (m) |
|---|---|---|---|
| Black chair (100 cm tall) | 1.00 | 1.00 (derived) | 1.08 (derived) |
| Door / tall reference (180 cm) | 1.80 | 1.80 (derived) | 1.88 (derived) |
| Blue chair @ 4 m | 4.00 | 4.00 (derived) | 4.08 (derived) |

(No "extra" object row logged for this session - remove the placeholder row when finalising.)

- test2_marked_distances start: 2026-05-25 14:07:36
- test2_marked_distances end: 2026-05-25 14:09:02, duration 86s
- ros2 bag info output:
    
    Files:             test2_marked_distances_0.db3
    Bag size:          5.8 GiB
    Storage id:        sqlite3
    Duration:          80.221530322s
    Start:             May 25 2026 14:07:38.873805203 (1779718058.873805203)
    End:               May 25 2026 14:08:59.095335525 (1779718139.095335525)
    Messages:          13596
    Topic information: Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 2399 | Serialization Format: cdr
                       Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 2399 | Serialization Format: cdr
                       Topic: /zed/zed_node/imu/data | Type: sensor_msgs/msg/Imu | Count: 7994 | Serialization Format: cdr
                       Topic: /tf_static | Type: tf2_msgs/msg/TFMessage | Count: 1 | Serialization Format: cdr
                       Topic: /tf | Type: tf2_msgs/msg/TFMessage | Count: 0 | Serialization Format: cdr
                       Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 803 | Serialization Format: cdr
    
- Size on disk: 5.9G

**Rate sanity check on test2_marked_distances** (image ~30 Hz × 80.2 s ≈ 2406 expected vs 2399 actual; LiDAR ~10 Hz × 80.2 s ≈ 802 expected vs 803 actual; IMU ~100 Hz × 80.2 s ≈ 8022 expected vs 7994 actual). All three within <0.4 % of nominal - bag is healthy, no dropped publishers.

## Calibration bag set: calib_set_2026_05_25

- bag_01 pose: straight - rig in the same forward orientation as `test2_marked_distances` (LiDAR pointed through the open doorway, blue chair as the far depth anchor).
  - record start: 14:15:59
  - record end: 14:16:44
    Duration:          32.918495953s
    Messages:          2298
- bag_02 pose: bit left - small yaw left of bag_01 (see `docs/screenshots/d10_calib_pose_02.jpg`).
  - record start: 14:18:08
  - record end: 14:18:50
    Duration:          33.953755814s
    Messages:          2372
- bag_03 pose: bit right - small yaw right of bag_01 (see `docs/screenshots/d10_calib_pose_03.jpg`).
  - record start: 14:20:28
  - record end: 14:21:14
    Duration:          39.883221212s
    Messages:          2785
- bag_04 pose: moved right - rig translated laterally to the right of the bag_01 position (yaw kept roughly straight).
  - record start: 14:23:27
  - record end: 14:24:10
    Duration:          38.452762630s
    Messages:          2687
- bag_05 pose: moved left - rig translated laterally to the left of the bag_01 position (yaw kept roughly straight).
  - record start: 14:25:31
  - record end: 14:26:20
    Duration:          44.152981307s
    Messages:          3084


## On-site sanity sweep (14:29:04)

```
=== bag_01 ===
Duration:          32.918495953s
Messages:          2298
Topic information: Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 985 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 984 | Serialization Format: cdr
                   Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 329 | Serialization Format: cdr
=== bag_02 ===
Duration:          33.953755814s
Messages:          2372
Topic information: Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1016 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1016 | Serialization Format: cdr
                   Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 340 | Serialization Format: cdr
=== bag_03 ===
Duration:          39.883221212s
Messages:          2785
Topic information: Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 399 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1193 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1193 | Serialization Format: cdr
=== bag_04 ===
Duration:          38.452762630s
Messages:          2687
Topic information: Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1151 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1151 | Serialization Format: cdr
                   Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 385 | Serialization Format: cdr
=== bag_05 ===
Duration:          44.152981307s
Messages:          3084
Topic information: Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 442 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1321 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1321 | Serialization Format: cdr
```

**Sanity sweep verdict:** all 5 calibration bags healthy. Image and LiDAR counts match the expected per-second rates (≈ 30 × duration for images, ≈ 10 × duration for LiDAR) to within a couple of frames in every bag. Three topics per bag - no IMU, no tf - as the calibrator requires.

- Total size: 14G
- test2_marked_distances size: 5.9G
- Free disk after recording: 158G

**Disk-use accounting:** 178 G → 158 G = 20 G consumed, matches the 14 G + 5.9 G recorded payload to within rounding. No silent rosbag fragmentation.

## Photos saved this session

- `docs/screenshots/d10_scene_wide.jpg` - scene wide-shot with the rig + doorway + blue-chair anchor visible.
- `docs/screenshots/d10_calib_pose_02.jpg` - one of the 5 calibration rig poses.
- `docs/screenshots/d10_calib_pose_03.jpg` - another of the 5 calibration rig poses.
- `docs/screenshots/d10_scene_marker_2m.jpg` - marker-tape close-up 2m.
- `docs/screenshots/d10_scene_marker_4m.jpg` - marker-tape close-up 4m.
