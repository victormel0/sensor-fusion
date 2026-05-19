# Bag analysis report

**Bag folder:** `/home/user/Documents/workspace/sensor-fusion/recordings/test1_first_recording`
**Duration (from arrival ts):** 73.68 s
**Total messages:** 14687

## Per-topic statistics

### `/rslidar_points`
- type: `sensor_msgs/msg/PointCloud2`
- count: **737**
- observed rate: **10.00 Hz**
  - **arrival interval (ms)**: n=736, mean=99.98, median=99.93, stdev=6.54, min=85.97, max=113.58
  - no gaps larger than 3.0× median (299.8 ms)
  - **arrival - header timestamp (ms)**: n=737, mean=106.52, median=103.58, stdev=4.97, min=100.65, max=117.07

### `/tf`
- type: `tf2_msgs/msg/TFMessage`
- count: **0**
- too few messages for interval stats

### `/tf_static`
- type: `tf2_msgs/msg/TFMessage`
- count: **1**
- too few messages for interval stats

### `/zed/zed_node/imu/data`
- type: `sensor_msgs/msg/Imu`
- count: **7336**
- observed rate: **99.56 Hz**
  - **arrival interval (ms)**: n=7335, mean=10.03, median=10.02, stdev=3.50, min=0.02, max=103.50
  - **4 large gap(s) (>3.0× median, >30.1 ms) - largest 103.5 ms**
  - **arrival - header timestamp (ms)**: n=7336, mean=14.21, median=14.03, stdev=3.76, min=8.10, max=105.62

### `/zed/zed_node/rgb/color/rect/camera_info`
- type: `sensor_msgs/msg/CameraInfo`
- count: **2204**
- observed rate: **29.91 Hz**
  - **arrival interval (ms)**: n=2203, mean=33.42, median=33.48, stdev=11.40, min=0.01, max=316.38
  - **4 large gap(s) (>3.0× median, >100.4 ms) - largest 316.4 ms**
  - **arrival - header timestamp (ms)**: n=2204, mean=70.27, median=68.77, stdev=20.81, min=49.67, max=345.72

### `/zed/zed_node/rgb/color/rect/image`
- type: `sensor_msgs/msg/Image`
- count: **2204**
- observed rate: **29.91 Hz**
  - **arrival interval (ms)**: n=2203, mean=33.41, median=33.54, stdev=5.22, min=8.76, max=63.32
  - no gaps larger than 3.0× median (100.6 ms)
  - **arrival - header timestamp (ms)**: n=2204, mean=73.49, median=73.51, stdev=10.20, min=52.68, max=111.52

### `/zed/zed_node/rgb/color/rect/image/camera_info`
- type: `sensor_msgs/msg/CameraInfo`
- count: **2205**
- observed rate: **29.92 Hz**
  - **arrival interval (ms)**: n=2204, mean=33.43, median=33.48, stdev=10.49, min=0.02, max=279.67
  - **6 large gap(s) (>3.0× median, >100.4 ms) - largest 279.7 ms**
  - **arrival - header timestamp (ms)**: n=2205, mean=69.93, median=68.72, stdev=18.30, min=0.43, max=308.96

## Camera ↔ LiDAR pairing (by header timestamp)

For each LiDAR frame, find the nearest camera frame by header timestamp. Slop window: ±50 ms.

- LiDAR frames considered: **737**
- Paired within slop: **736 (99.9%)**
  - **best dt per LiDAR frame (ms)**: n=737, mean=15.23, median=15.16, stdev=2.51, min=13.81, max=81.71

## Verdict

- OK - Camera rate: 29.9 Hz (target ≥25 Hz)
- OK - LiDAR rate: 10.0 Hz (target ≥9.5 Hz)
