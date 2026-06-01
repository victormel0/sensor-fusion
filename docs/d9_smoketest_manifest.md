# Day 2 smoke-test manifest -- 2026-05-20

**Goal:** confirm the install from Day 1 by running the full pipeline on Koide's Ouster sample bag.

## direct_visual_lidar_calibration
- Repo: https://github.com/koide3/direct_visual_lidar_calibration (--recursive)
- Cloned at: 2026-05-20 13:33:09
- Commit: `02a0dc039f5509708f384be4ff3228e0ae09352d`
- Branch: main
- colcon build start: 2026-05-20 13:34:44
- colcon build end: 2026-05-20 13:37:21
- Duration: 140s (2m 20s)
- Warning count: 2
- Error count: 0
direct_visual_lidar_calibration calibrate
direct_visual_lidar_calibration find_matches_superglue.py
direct_visual_lidar_calibration initial_guess_auto
direct_visual_lidar_calibration initial_guess_manual
direct_visual_lidar_calibration preprocess
direct_visual_lidar_calibration preprocess_map
direct_visual_lidar_calibration viewer

## Sample dataset
- Sample chosen: Ouster (spinning-LiDAR-class, closer to H32F70)
- Disk footprint after extract: 2.4G
- Bag contents:
[INFO] [1779286664.159720160] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_25_54/rosbag2_2023_03_28-16_25_54_0.db3' for READ_ONLY.
Files:             ouster/rosbag2_2023_03_28-16_25_54/rosbag2_2023_03_28-16_25_54_0.db3
Bag size:          1.2 GiB
Storage id:        sqlite3
Duration:          29.014213562s
Start:             Mar 28 2023 07:25:54.559472320 (1679988354.559472320)
End:               Mar 28 2023 07:26:23.573685882 (1679988383.573685882)
Messages:          407
Topic information: Topic: /points | Type: sensor_msgs/msg/PointCloud2 | Count: 291 | Serialization Format: cdr
                   Topic: /image | Type: sensor_msgs/msg/Image | Count: 58 | Serialization Format: cdr
                   Topic: /camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 58 | Serialization Format: cdr
[INFO] [1779286699.987714172] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_26_51/rosbag2_2023_03_28-16_26_51_0.db3' for READ_ONLY.
Files:             ouster/rosbag2_2023_03_28-16_26_51/rosbag2_2023_03_28-16_26_51_0.db3
Bag size:          1.1 GiB
Storage id:        sqlite3
Duration:          26.435193932s
Start:             Mar 28 2023 07:26:51.943603450 (1679988411.943603450)
End:               Mar 28 2023 07:27:18.378797382 (1679988438.378797382)
Messages:          371
Topic information: Topic: /points | Type: sensor_msgs/msg/PointCloud2 | Count: 265 | Serialization Format: cdr
                   Topic: /image | Type: sensor_msgs/msg/Image | Count: 53 | Serialization Format: cdr
                   Topic: /camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 53 | Serialization Format: cdr

- Preprocess start: 2026-05-20 14:29:15
- Preprocess start: 2026-05-20 14:32:41

---

## Debug session - OpenCV mixed-ABI conflict (2026-05-20 20:19:34)

Symptom: `preprocess ouster ouster_preprocessed -a -d` aborts with
`cv::Exception in setSize (Assertion failed: s >= 0)` at startup.
Prior ldd showed libopencv_core.so.408 (NVIDIA 4.8.0) and libopencv_core.so.4.5d
(Ubuntu 4.5.4) co-loaded into the same process. This section is the diagnostic
sweep before any system change.

### Check 1 - apt packages shipping libopencv*.so.4.5d

```
libopencv-calib3d4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_calib3d.so.4.5.4d
libopencv-calib3d4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_calib3d.so.4.5d
libopencv-calib3d4.5d:arm64: /usr/share/doc/libopencv-calib3d4.5d
libopencv-calib3d4.5d:arm64: /usr/share/doc/libopencv-calib3d4.5d/changelog.Debian.gz
libopencv-calib3d4.5d:arm64: /usr/share/doc/libopencv-calib3d4.5d/copyright
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_alphamat.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_alphamat.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_aruco.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_aruco.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_barcode.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_barcode.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_bgsegm.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_bgsegm.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_bioinspired.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_bioinspired.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_ccalib.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_ccalib.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_datasets.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_datasets.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_dnn_objdetect.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_dnn_objdetect.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_dnn_superres.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_dnn_superres.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_dpm.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_dpm.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_face.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_face.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_freetype.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_freetype.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_fuzzy.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_fuzzy.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_hdf.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_hdf.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_hfs.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_hfs.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_img_hash.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_img_hash.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_intensity_transform.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_intensity_transform.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_line_descriptor.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_line_descriptor.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_mcc.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_mcc.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_optflow.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_optflow.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_phase_unwrapping.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_phase_unwrapping.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_plot.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_plot.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_quality.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_quality.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_rapid.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_rapid.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_reg.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_reg.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_rgbd.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_rgbd.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_saliency.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_saliency.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_stereo.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_stereo.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_structured_light.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_structured_light.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_surface_matching.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_surface_matching.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_text.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_text.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_tracking.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_tracking.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_wechat_qrcode.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_wechat_qrcode.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_ximgproc.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_ximgproc.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_xobjdetect.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_xobjdetect.so.4.5d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_xphoto.so.4.5.4d
libopencv-contrib4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_xphoto.so.4.5d
libopencv-contrib4.5d:arm64: /usr/share/doc/libopencv-contrib4.5d
libopencv-contrib4.5d:arm64: /usr/share/doc/libopencv-contrib4.5d/changelog.Debian.gz
libopencv-contrib4.5d:arm64: /usr/share/doc/libopencv-contrib4.5d/copyright
libopencv-contrib4.5d:arm64: /usr/share/lintian/overrides/libopencv-contrib4.5d
libopencv-core4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_core.so.4.5.4d
libopencv-core4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_core.so.4.5d
libopencv-core4.5d:arm64: /usr/share/doc/libopencv-core4.5d
libopencv-core4.5d:arm64: /usr/share/doc/libopencv-core4.5d/changelog.Debian.gz
libopencv-core4.5d:arm64: /usr/share/doc/libopencv-core4.5d/copyright
libopencv-dnn4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_dnn.so.4.5.4d
libopencv-dnn4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_dnn.so.4.5d
libopencv-dnn4.5d:arm64: /usr/share/doc/libopencv-dnn4.5d
libopencv-dnn4.5d:arm64: /usr/share/doc/libopencv-dnn4.5d/changelog.Debian.gz
libopencv-dnn4.5d:arm64: /usr/share/doc/libopencv-dnn4.5d/copyright
libopencv-features2d4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_features2d.so.4.5.4d
libopencv-features2d4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_features2d.so.4.5d
libopencv-features2d4.5d:arm64: /usr/share/doc/libopencv-features2d4.5d
libopencv-features2d4.5d:arm64: /usr/share/doc/libopencv-features2d4.5d/changelog.Debian.gz
libopencv-features2d4.5d:arm64: /usr/share/doc/libopencv-features2d4.5d/copyright
libopencv-flann4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_flann.so.4.5.4d
libopencv-flann4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_flann.so.4.5d
libopencv-flann4.5d:arm64: /usr/share/doc/libopencv-flann4.5d
libopencv-flann4.5d:arm64: /usr/share/doc/libopencv-flann4.5d/changelog.Debian.gz
libopencv-flann4.5d:arm64: /usr/share/doc/libopencv-flann4.5d/copyright
libopencv-highgui4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_highgui.so.4.5.4d
libopencv-highgui4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_highgui.so.4.5d
libopencv-highgui4.5d:arm64: /usr/share/doc/libopencv-highgui4.5d
libopencv-highgui4.5d:arm64: /usr/share/doc/libopencv-highgui4.5d/changelog.Debian.gz
libopencv-highgui4.5d:arm64: /usr/share/doc/libopencv-highgui4.5d/copyright
libopencv-imgcodecs4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_imgcodecs.so.4.5.4d
libopencv-imgcodecs4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_imgcodecs.so.4.5d
libopencv-imgcodecs4.5d:arm64: /usr/share/doc/libopencv-imgcodecs4.5d
libopencv-imgcodecs4.5d:arm64: /usr/share/doc/libopencv-imgcodecs4.5d/changelog.Debian.gz
libopencv-imgcodecs4.5d:arm64: /usr/share/doc/libopencv-imgcodecs4.5d/copyright
libopencv-imgproc4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_imgproc.so.4.5.4d
libopencv-imgproc4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_imgproc.so.4.5d
libopencv-imgproc4.5d:arm64: /usr/share/doc/libopencv-imgproc4.5d
libopencv-imgproc4.5d:arm64: /usr/share/doc/libopencv-imgproc4.5d/changelog.Debian.gz
libopencv-imgproc4.5d:arm64: /usr/share/doc/libopencv-imgproc4.5d/copyright
libopencv-ml4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_ml.so.4.5.4d
libopencv-ml4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_ml.so.4.5d
libopencv-ml4.5d:arm64: /usr/share/doc/libopencv-ml4.5d
libopencv-ml4.5d:arm64: /usr/share/doc/libopencv-ml4.5d/changelog.Debian.gz
libopencv-ml4.5d:arm64: /usr/share/doc/libopencv-ml4.5d/copyright
libopencv-objdetect4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_objdetect.so.4.5.4d
libopencv-objdetect4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_objdetect.so.4.5d
libopencv-objdetect4.5d:arm64: /usr/share/doc/libopencv-objdetect4.5d
libopencv-objdetect4.5d:arm64: /usr/share/doc/libopencv-objdetect4.5d/changelog.Debian.gz
libopencv-objdetect4.5d:arm64: /usr/share/doc/libopencv-objdetect4.5d/copyright
libopencv-photo4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_photo.so.4.5.4d
libopencv-photo4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_photo.so.4.5d
libopencv-photo4.5d:arm64: /usr/share/doc/libopencv-photo4.5d
libopencv-photo4.5d:arm64: /usr/share/doc/libopencv-photo4.5d/changelog.Debian.gz
libopencv-photo4.5d:arm64: /usr/share/doc/libopencv-photo4.5d/copyright
libopencv-shape4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_shape.so.4.5.4d
libopencv-shape4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_shape.so.4.5d
libopencv-shape4.5d:arm64: /usr/share/doc/libopencv-shape4.5d
libopencv-shape4.5d:arm64: /usr/share/doc/libopencv-shape4.5d/changelog.Debian.gz
libopencv-shape4.5d:arm64: /usr/share/doc/libopencv-shape4.5d/copyright
libopencv-stitching4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_stitching.so.4.5.4d
libopencv-stitching4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_stitching.so.4.5d
libopencv-stitching4.5d:arm64: /usr/share/doc/libopencv-stitching4.5d
libopencv-stitching4.5d:arm64: /usr/share/doc/libopencv-stitching4.5d/changelog.Debian.gz
libopencv-stitching4.5d:arm64: /usr/share/doc/libopencv-stitching4.5d/copyright
libopencv-video4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_video.so.4.5.4d
libopencv-video4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_video.so.4.5d
libopencv-video4.5d:arm64: /usr/share/doc/libopencv-video4.5d
libopencv-video4.5d:arm64: /usr/share/doc/libopencv-video4.5d/changelog.Debian.gz
libopencv-video4.5d:arm64: /usr/share/doc/libopencv-video4.5d/copyright
libopencv-videoio4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_videoio.so.4.5.4d
libopencv-videoio4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_videoio.so.4.5d
libopencv-videoio4.5d:arm64: /usr/share/doc/libopencv-videoio4.5d
libopencv-videoio4.5d:arm64: /usr/share/doc/libopencv-videoio4.5d/changelog.Debian.gz
libopencv-videoio4.5d:arm64: /usr/share/doc/libopencv-videoio4.5d/copyright
libopencv-viz4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_viz.so.4.5.4d
libopencv-viz4.5d:arm64: /usr/lib/aarch64-linux-gnu/libopencv_viz.so.4.5d
libopencv-viz4.5d:arm64: /usr/share/doc/libopencv-viz4.5d
libopencv-viz4.5d:arm64: /usr/share/doc/libopencv-viz4.5d/changelog.Debian.gz
libopencv-viz4.5d:arm64: /usr/share/doc/libopencv-viz4.5d/copyright
```

### Check 2 - installed reverse-deps of each 4.5.4 OpenCV package

**libopencv-calib3d4.5d** depended on by:
```
  libopencv-contrib4.5d
  libopencv-dev
  libopencv-objdetect4.5d
  libopencv-shape4.5d
  libopencv-stitching4.5d
  libopencv-video4.5d
  python3-opencv
  ros-humble-image-geometry
```

**libopencv-contrib4.5d** depended on by:
```
  libopencv-dev
  python3-opencv
```

**libopencv-core4.5d** depended on by:
```
  libgstreamer-opencv1.0-0
  libopencv-calib3d4.5d
  libopencv-contrib4.5d
  libopencv-dev
  libopencv-dnn4.5d
  libopencv-features2d4.5d
  libopencv-flann4.5d
  libopencv-highgui4.5d
  libopencv-imgcodecs4.5d
  libopencv-imgproc4.5d
  libopencv-ml4.5d
  libopencv-objdetect4.5d
  libopencv-photo4.5d
  libopencv-shape4.5d
  libopencv-stitching4.5d
  libopencv-video4.5d
  libopencv-videoio4.5d
  libopencv-viz4.5d
  python3-opencv
  ros-humble-compressed-depth-image-transport
  ros-humble-compressed-image-transport
  ros-humble-cv-bridge
  ros-humble-depthimage-to-laserscan
  ros-humble-ffmpeg-encoder-decoder
  ros-humble-image-geometry
  ros-humble-image-tools
  ros-humble-intra-process-demo
  ros-humble-rqt-image-view
  ros-humble-theora-image-transport
```

**libopencv-dnn4.5d** depended on by:
```
  libopencv-contrib4.5d
  libopencv-dev
  libopencv-objdetect4.5d
  libopencv-video4.5d
  python3-opencv
```

**libopencv-features2d4.5d** depended on by:
```
  libopencv-calib3d4.5d
  libopencv-contrib4.5d
  libopencv-dev
  libopencv-stitching4.5d
  python3-opencv
```

**libopencv-flann4.5d** depended on by:
```
  libopencv-calib3d4.5d
  libopencv-contrib4.5d
  libopencv-features2d4.5d
  libopencv-stitching4.5d
  python3-opencv
  ros-humble-depthimage-to-laserscan
```

**libopencv-highgui4.5d** depended on by:
```
  libopencv-contrib4.5d
  libopencv-dev
  python3-opencv
  ros-humble-image-tools
  ros-humble-intra-process-demo
```

**libopencv-imgcodecs4.5d** depended on by:
```
  libopencv-contrib4.5d
  libopencv-dev
  libopencv-highgui4.5d
  libopencv-videoio4.5d
  python3-opencv
  ros-humble-compressed-depth-image-transport
  ros-humble-compressed-image-transport
  ros-humble-cv-bridge
  ros-humble-image-tools
```

**libopencv-imgproc4.5d** depended on by:
```
  libopencv-calib3d4.5d
  libopencv-contrib4.5d
  libopencv-dev
  libopencv-dnn4.5d
  libopencv-features2d4.5d
  libopencv-highgui4.5d
  libopencv-imgcodecs4.5d
  libopencv-objdetect4.5d
  libopencv-photo4.5d
  libopencv-shape4.5d
  libopencv-stitching4.5d
  libopencv-video4.5d
  libopencv-videoio4.5d
  python3-opencv
  ros-humble-compressed-image-transport
  ros-humble-cv-bridge
  ros-humble-image-geometry
  ros-humble-image-tools
  ros-humble-intra-process-demo
  ros-humble-rqt-image-view
  ros-humble-theora-image-transport
```

**libopencv-ml4.5d** depended on by:
```
  libopencv-contrib4.5d
  python3-opencv
```

**libopencv-objdetect4.5d** depended on by:
```
  libopencv-contrib4.5d
  python3-opencv
```

**libopencv-photo4.5d** depended on by:
```
  python3-opencv
```

**libopencv-shape4.5d** depended on by:
```
  python3-opencv
```

**libopencv-stitching4.5d** depended on by:
```
  python3-opencv
```

**libopencv-video4.5d** depended on by:
```
  libopencv-contrib4.5d
  python3-opencv
```

**libopencv-videoio4.5d** depended on by:
```
  libopencv-dev
  python3-opencv
  ros-humble-image-tools
  ros-humble-intra-process-demo
```

**libopencv-viz4.5d** depended on by:
```
  python3-opencv
```

### Check 3 - ldd on every .so shipped by ros-humble-cv-bridge

```
# /opt/ros/humble/lib/libcv_bridge.so
	libopencv_imgcodecs.so.4.5d => /lib/aarch64-linux-gnu/libopencv_imgcodecs.so.4.5d (0x0000ffff987a0000)
	libopencv_imgproc.so.4.5d => /lib/aarch64-linux-gnu/libopencv_imgproc.so.4.5d (0x0000ffff98430000)
	libopencv_core.so.4.5d => /lib/aarch64-linux-gnu/libopencv_core.so.4.5d (0x0000ffff981a0000)

# /opt/ros/humble/local/lib/python3.10/dist-packages/cv_bridge/boost/cv_bridge_boost.so
	libopencv_core.so.4.5d => /lib/aarch64-linux-gnu/libopencv_core.so.4.5d (0x0000ffff87330000)
	libopencv_imgcodecs.so.4.5d => /lib/aarch64-linux-gnu/libopencv_imgcodecs.so.4.5d (0x0000ffff86e70000)
	libopencv_imgproc.so.4.5d => /lib/aarch64-linux-gnu/libopencv_imgproc.so.4.5d (0x0000ffff86b00000)

```

### Check 4 - ldd on image_geometry / image_transport siblings

```
## ros-humble-image-geometry
# /opt/ros/humble/lib/libimage_geometry.so
	libopencv_calib3d.so.4.5d => /lib/aarch64-linux-gnu/libopencv_calib3d.so.4.5d (0x0000ffffb7c70000)
	libopencv_imgproc.so.4.5d => /lib/aarch64-linux-gnu/libopencv_imgproc.so.4.5d (0x0000ffffb7900000)
	libopencv_core.so.4.5d => /lib/aarch64-linux-gnu/libopencv_core.so.4.5d (0x0000ffffb7670000)
	libopencv_features2d.so.4.5d => /lib/aarch64-linux-gnu/libopencv_features2d.so.4.5d (0x0000ffffb71d0000)
	libopencv_flann.so.4.5d => /lib/aarch64-linux-gnu/libopencv_flann.so.4.5d (0x0000ffffb7160000)

## ros-humble-image-transport
# /opt/ros/humble/lib/aarch64-linux-gnu/libimage_transport.so
  (no opencv in NEEDED)
# /opt/ros/humble/lib/libimage_transport.so
  (no opencv in NEEDED)
# /opt/ros/humble/lib/libimage_transport_plugins.so
  (no opencv in NEEDED)

## ros-humble-image-transport-plugins

```

### Check 5 - preprocess binary's direct NEEDED list

Resolved binary path: `/home/user/Documents/workspace/sensor-fusion/ros2_ws/build/direct_visual_lidar_calibration/preprocess`

```
  NEEDED               ld-linux-aarch64.so.1
  NEEDED               libc.so.6
  NEEDED               libcv_bridge.so
  NEEDED               libdirect_visual_lidar_calibration.so
  NEEDED               libgcc_s.so.1
  NEEDED               libopencv_core.so.408
  NEEDED               librclcpp.so
  NEEDED               librosbag2_cpp.so
  NEEDED               librosbag2_storage.so
  NEEDED               libsensor_msgs__rosidl_typesupport_cpp.so
  NEEDED               libstdc++.so.6
```

### Check 6 - calibrator CMakeLists.txt OpenCV / cv_bridge references

```
14:  find_package(catkin REQUIRED COMPONENTS rosbag sensor_msgs cv_bridge)
18:  find_package(ament_cmake_auto REQUIRED)
19:  find_package(ament_cmake_python REQUIRED)
23:find_package(PCL REQUIRED)
24:find_package(Ceres REQUIRED)
25:find_package(GTSAM REQUIRED)
26:find_package(OpenCV REQUIRED)
27:find_package(Boost REQUIRED COMPONENTS filesystem program_options date_time)
28:find_package(Iridescence REQUIRED)
37:find_package(OpenMP)
74:  ${OpenCV_INCLUDE_DIRS}
76:target_link_libraries(direct_visual_lidar_calibration
82:  ${OpenCV_LIBRARIES}
92:  target_link_libraries(preprocess
98:  target_link_libraries(preprocess
106:  target_link_libraries(preprocess
118:target_link_libraries(preprocess_map
129:target_link_libraries(initial_guess_manual
140:target_link_libraries(initial_guess_auto
151:target_link_libraries(calibrate
162:target_link_libraries(viewer
```


### Check 7 - pkg-config opencv4 resolution

```
modversion: 4.8.0
prefix:     /usr/local
libdir:     /usr/local/lib
includedir: /usr/local/include/opencv4

pkg-config search path (PKG_CONFIG_PATH + defaults):
/usr/local/lib/aarch64-linux-gnu/pkgconfig:/usr/local/lib/pkgconfig:/usr/local/share/pkgconfig:/usr/lib/aarch64-linux-gnu/pkgconfig:/usr/lib/pkgconfig:/usr/share/pkgconfig

All opencv4.pc files on the system:
/usr/lib/pkgconfig/opencv4.pc
```

### Check 8 - CMake config files for OpenCV (find_package looks for these first)

```
All OpenCVConfig.cmake on the system:
/usr/lib/cmake/opencv4/OpenCVConfig.cmake
/snap/gnome-46-2404/154/usr/lib/aarch64-linux-gnu/cmake/opencv4/OpenCVConfig.cmake

OpenCVConfig-version.cmake versions (if multiple):
# /usr/lib/cmake/opencv4/OpenCVConfig-version.cmake
set(PACKAGE_VERSION ${OpenCV_VERSION})
set(PACKAGE_VERSION_EXACT False)
set(PACKAGE_VERSION_COMPATIBLE False)
# /snap/gnome-46-2404/154/usr/lib/aarch64-linux-gnu/cmake/opencv4/OpenCVConfig-version.cmake
set(PACKAGE_VERSION ${OpenCV_VERSION})
set(PACKAGE_VERSION_EXACT False)
set(PACKAGE_VERSION_COMPATIBLE False)
```

### Check 9 - NVIDIA OpenCV package(s) installed

```
ii  libgstreamer-opencv1.0-0:arm64                    1.20.3-0ubuntu1.1                           arm64        GStreamer OpenCV libraries
ii  libopencv                                         4.8.0-1-g6371ee1                            arm64        Open Computer Vision Library
ii  libopencv-dev                                     4.8.0-1-g6371ee1                            arm64        Open Computer Vision Library
ii  libopencv-python                                  4.8.0-1-g6371ee1                            arm64        Open Computer Vision Library
ii  libopencv-samples                                 4.8.0-1-g6371ee1                            arm64        Open Computer Vision Library
ii  nvidia-opencv                                     6.2.1+b38                                   arm64        NVIDIA OpenCV Meta Package
ii  nvidia-opencv-dev                                 6.2.1+b38                                   arm64        NVIDIA OpenCV dev Meta Package
ii  opencv-licenses                                   4.8.0-1-g6371ee1                            arm64        Open Computer Vision Library
ii  opencv-samples-data                               4.8.0-1-g6371ee1                            arm64        Open Computer Vision Library
ii  ros-humble-cv-bridge                              3.2.1-1jammy.20260307.203259                arm64        This contains CvBridge, which converts between ROS2 Image messages and OpenCV images.
```

### Check 10 - alternatives system (in case OpenCV is alternative-managed)

```
  (no opencv-config alternative registered)
  (no opencv-named alternatives in /etc/alternatives/)
```

### Check 11 - simulate what cv_bridge's find_package(OpenCV) will resolve to

```
-- Found OpenCV: /usr (found version "4.8.0") 
-- OpenCV_VERSION:      4.8.0
-- OpenCV_INCLUDE_DIRS: /usr/include/opencv4
-- OpenCV_LIB_DIR:      
-- OpenCV_DIR:          /usr/lib/cmake/opencv4
-- OpenCV_LIBS:         opencv_calib3d;opencv_core;opencv_dnn;opencv_features2d;opencv_flann;opencv_gapi;opencv_highgui;opencv_imgcodecs;opencv_imgproc;opencv_ml;opencv_objdetect;opencv_photo;opencv_stitching;opencv_video;opencv_videoio
```


---

## Fix - rebuild cv_bridge + image_geometry against NVIDIA OpenCV 4.8.0 (2026-05-20 20:35:22)

Phase 1.5 confirmed find_package(OpenCV) resolves to /usr/lib/cmake/opencv4 (NVIDIA 4.8.0).
Clone ros-perception/vision_opencv (humble branch) as workspace overlay. The overlay's
libcv_bridge.so will shadow the apt one via colcon's environment hooks, removing the
4.5.4 closure from any process that sources install/setup.bash.

### vision_opencv source clone

- Repo: https://github.com/ros-perception/vision_opencv
- Branch: `humble`
- Commit: `9800f67cea477c44cfb64e349854bcb6a09dc9ce`
- Cloned at: 2026-05-20 20:35:23

### rosdep check on vision_opencv

```
#All required rosdeps installed successfully
```

### colcon build cv_bridge + image_geometry

- Build start: 2026-05-20 20:35:24
- Build end: 2026-05-20 20:35:46
- Duration: 22s (0m 22s)
- Warning count: 1
- Error count: 1

### ldd on freshly-built cv_bridge (should show ONLY .so.408)

Resolved path: `/home/user/Documents/workspace/sensor-fusion/ros2_ws/build/cv_bridge/src/libcv_bridge.so`

```
	libopencv_imgcodecs.so.408 => /lib/libopencv_imgcodecs.so.408 (0x0000ffffa8900000)
	libopencv_imgproc.so.408 => /lib/libopencv_imgproc.so.408 (0x0000ffffa8530000)
	libopencv_core.so.408 => /lib/libopencv_core.so.408 (0x0000ffffa8220000)
```

### colcon rebuild direct_visual_lidar_calibration

- Calibrator rebuild start: 2026-05-20 20:35:47
- Calibrator rebuild end: 2026-05-20 20:37:53
- Duration: 126s (2m 6s)
- Warning count: 3
- Error count: 0

### HEADLINE - ldd preprocess after fix

Binary: `/home/user/Documents/workspace/sensor-fusion/ros2_ws/build/direct_visual_lidar_calibration/preprocess`

```
	libopencv_core.so.408 => /lib/libopencv_core.so.408 (0x0000ffff818e0000)
	libopencv_imgcodecs.so.408 => /lib/libopencv_imgcodecs.so.408 (0x0000ffff81280000)
	libopencv_imgproc.so.408 => /lib/libopencv_imgproc.so.408 (0x0000ffff80eb0000)
	libopencv_highgui.so.408 => /lib/libopencv_highgui.so.408 (0x0000ffff80360000)
```

Expected: ONLY `.so.408` entries. No `.so.4.5d`. If clean, the mixed-ABI
conflict is resolved and we proceed to re-run §2.5.



### Second crash (post-ABI-fix) - gdb stack trace at cv::error

After the cv_bridge rebuild, ldd preprocess is clean (only .408). The setSize
assertion still fires, but now from a single coherent OpenCV 4.8.0 runtime. This
is a genuine 4.8.0 incompatibility in the per-frame preprocess pipeline. GitHub
issue koide3/direct_visual_lidar_calibration#65 corroborates that 4.8.0 has
historically not been a tested target; Docker humble image uses 4.5.4.

```
-ex: No such file or directory.
Catchpoint 1 (throw)
No executable file specified.
Use the "file" or "exec-file" command.
No stack.
[ros2run]: Process exited with failure 1
```


### Second crash gdb trace (corrected invocation)

```
Catchpoint 1 (throw)
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/aarch64-linux-gnu/libthread_db.so.1".
[New Thread 0xffffe4261360 (LWP 178231)]
[New Thread 0xffffe3a51360 (LWP 178232)]
[New Thread 0xffffe1241360 (LWP 178233)]
[New Thread 0xffffdea31360 (LWP 178234)]
[New Thread 0xffffdc221360 (LWP 178235)]
[New Thread 0xffffd7a11360 (LWP 178236)]
[New Thread 0xffffd7201360 (LWP 178237)]
data_path: ouster
dst_path : ouster_preprocessed
[INFO] [1779343369.346770287] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_26_51/rosbag2_2023_03_28-16_26_51_0.db3' for READ_ONLY.
[INFO] [1779343369.366038713] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_25_54/rosbag2_2023_03_28-16_25_54_0.db3' for READ_ONLY.
input_bags:
- ouster/rosbag2_2023_03_28-16_26_51
- ouster/rosbag2_2023_03_28-16_25_54
[INFO] [1779343369.387673594] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_25_54/rosbag2_2023_03_28-16_25_54_0.db3' for READ_ONLY.
topics in ouster/rosbag2_2023_03_28-16_25_54:
- /camera_info : sensor_msgs/msg/CameraInfo
- /image : sensor_msgs/msg/Image
- /points : sensor_msgs/msg/PointCloud2
selected topics:
- camera_info: /camera_info
- image      : /image
- points     : /points
[INFO] [1779343369.407192174] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_25_54/rosbag2_2023_03_28-16_25_54_0.db3' for READ_ONLY.
intensity_channel: reflectivity
[INFO] [1779343369.589134949] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_25_54/rosbag2_2023_03_28-16_25_54_0.db3' for READ_ONLY.
try to get the camera model automatically
[INFO] [1779343369.677130818] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_25_54/rosbag2_2023_03_28-16_25_54_0.db3' for READ_ONLY.
camera_model: plumb_bob
image_size  : 2448 2048
intrinsics  : 1454.66 1455.21 1229.26 1010.66
dist_coeffs :   -0.0507013     0.111236 -0.000881838  0.000141199   -0.0588915
processing images and points (num_threads_per_bag=8)
start processing ouster/rosbag2_2023_03_28-16_25_54
[INFO] [1779343369.716139624] [rosbag2_storage]: Opened database 'ouster/rosbag2_2023_03_28-16_25_54/rosbag2_2023_03_28-16_25_54_0.db3' for READ_ONLY.

Thread 1 "preprocess" hit Catchpoint 1 (exception thrown), 0x0000fffff7672e4c in __cxa_throw () from /lib/aarch64-linux-gnu/libstdc++.so.6
#0  0x0000fffff7672e4c in __cxa_throw () at /lib/aarch64-linux-gnu/libstdc++.so.6
#1  0x0000fffff7a1a64c in cv::error(cv::Exception const&) () at /lib/libopencv_core.so.408
#2  0x0000fffff7a1b5ec in cv::error(int, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, char const*, char const*, int) () at /lib/libopencv_core.so.408
#3  0x0000fffff7947260 in cv::setSize(cv::Mat&, int, int const*, unsigned long const*, bool) [clone .constprop.1] () at /lib/libopencv_core.so.408
#4  0x0000fffff7948b24 in cv::Mat::create(int, int const*, int) () at /lib/libopencv_core.so.408
#5  0x0000fffff7948f7c in cv::Mat::create(int, int, int) () at /lib/libopencv_core.so.408
#6  0x0000fffff6f81e88 in cv::cvtColor(cv::_InputArray const&, cv::_OutputArray const&, int, int) () at /lib/aarch64-linux-gnu/libopencv_imgproc.so.4.5d
#7  0x0000fffff7efdd3c in cv_bridge::toCvCopyImpl(cv::Mat const&, std_msgs::msg::Header_<std::allocator<void> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&) () at /opt/ros/humble/lib/libcv_bridge.so
#8  0x0000fffff7eff918 in cv_bridge::toCvCopy(sensor_msgs::msg::Image_<std::allocator<void> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&) () at /opt/ros/humble/lib/libcv_bridge.so
#9  0x0000aaaaaaaa84b4 in vlcal::PreprocessROS2::get_image(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&) (this=<optimized out>, bag_filename="ouster/rosbag2_2023_03_28-16_25_54", image_topic=<optimized out>) at /home/user/Documents/workspace/sensor-fusion/ros2_ws/src/direct_visual_lidar_calibration/src/preprocess_ros2.cpp:138
#10 0x0000fffff7e776b0 in vlcal::Preprocess::get_image_and_points(boost::program_options::variables_map const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, int) (this=this@entry=0xffffffffe5c0, vm=..., bag_filename="ouster/rosbag2_2023_03_28-16_25_54", image_topic="/image", points_topic="/points", intensity_channel="reflectivity", num_threads=num_threads@entry=8) at /home/user/Documents/workspace/sensor-fusion/ros2_ws/src/direct_visual_lidar_calibration/src/vlcal/preprocess/preprocess.cpp:414
#11 0x0000fffff7e7bb28 in vlcal::Preprocess::run(int, char**) (this=this@entry=0xffffffffe5c0, argc=argc@entry=5, argv=argv@entry=0xffffffffe778) at /home/user/Documents/workspace/sensor-fusion/ros2_ws/src/direct_visual_lidar_calibration/src/vlcal/preprocess/preprocess.cpp:156
#12 0x0000aaaaaaaa465c in main(int, char**) (argc=5, argv=0xffffffffe778) at /home/user/Documents/workspace/sensor-fusion/ros2_ws/src/direct_visual_lidar_calibration/src/preprocess_ros2.cpp:155
```


### Sourcing diagnostic - confirm overlay cv_bridge wins

```
# Overlay cv_bridge.so on disk:
lrwxrwxrwx 1 user user 88 May 20 20:35 install/cv_bridge/lib/libcv_bridge.so -> /home/user/Documents/workspace/sensor-fusion/ros2_ws/build/cv_bridge/src/libcv_bridge.so

# First 8 entries of LD_LIBRARY_PATH:
/home/user/Documents/workspace/sensor-fusion/ros2_ws/install/zed_components/lib
/home/user/Documents/workspace/sensor-fusion/ros2_ws/install/rslidar_msg/lib
/home/user/Documents/workspace/sensor-fusion/ros2_ws/install/image_geometry/lib
/home/user/Documents/workspace/sensor-fusion/ros2_ws/install/direct_visual_lidar_calibration/lib
/home/user/Documents/workspace/sensor-fusion/ros2_ws/install/cv_bridge/lib
/opt/ros/humble/opt/rviz_ogre_vendor/lib
/opt/ros/humble/lib/aarch64-linux-gnu
/opt/ros/humble/lib

# Dynamic linker resolution of libcv_bridge.so for preprocess:
	libcv_bridge.so => /home/user/Documents/workspace/sensor-fusion/ros2_ws/install/cv_bridge/lib/libcv_bridge.so (0x0000ffffb2e80000)
	libopencv_core.so.408 => /lib/libopencv_core.so.408 (0x0000ffffb2790000)
	libopencv_imgcodecs.so.408 => /lib/libopencv_imgcodecs.so.408 (0x0000ffffb2130000)
	libopencv_imgproc.so.408 => /lib/libopencv_imgproc.so.408 (0x0000ffffb1d60000)
	libopencv_highgui.so.408 => /lib/libopencv_highgui.so.408 (0x0000ffffb1210000)
```

- Preprocess start: 2026-05-21 08:10:16
- Preprocess end: 2026-05-21 08:12:04, duration 108s
- Keyframes selected: 0
- Initial guess (manual) on sample: 4 correspondences clicked, estimate produced
```
user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion/third_party/dvlc_samples$ ros2 run direct_visual_lidar_calibration initial_guess_manual ouster_preprocessed
camera_model:plumb_bob
intrinsics  :4
distortion  :5
loading ouster_preprocessed/rosbag2_2023_03_28-16_25_54.(png|ply)
loading ouster_preprocessed/rosbag2_2023_03_28-16_26_51.(png|ply)
image_size:2448x2048
camera_fov:57.1854[deg]
Gtk-Message: 12:20:49.522: Failed to load module "canberra-gtk-module"
image_size=[2448 x 2048]
image_size=[2448 x 2048]
image_size=[2448 x 2048]
image_size=[2448 x 2048]
estimating bearing vectors
estimating rotation using RANSAC
num_inliers: 2 / 4
--- T_camera_lidar (RANSAC) ---
-0.00686486   -0.999782   0.0197322           0
  0.0198285  -0.0198649   -0.999606           0
    0.99978 -0.00647089   0.0199605           0
          0           0           0           1
Ceres Solver Report: Iterations: 9, Initial cost: 1.556515e+02, Final cost: 4.535937e+01, Termination: CONVERGENCE
--- T_camera_lidar (LSQ) ---
-0.0370121   -0.99923 -0.0130364   0.252752
-0.0103618  0.0134284  -0.999856   0.248878
  0.999261 -0.0368717 -0.0108508   0.094742
         0          0          0          1
```
- Fine calibrate start: 2026-05-21 12:46:01
- Fine calibrate end: 2026-05-21 13:04:58, duration 1137s
- Final NID cost (from log): 

### Calibrate outcome - smoke test PASS, run stopped at start of stage 4

- Initial guess loaded correctly (`use manually estimated initial guess`)
- NID cost converged across 3 pyramid stages: 1.954 → 1.918 (1.8% reduction)
- Stage 4 (full-resolution) hit Wolfe zoom failure at iter 0 and stalled
  in Ceres line-search; reproducible across two attempts. Sample-only issue,
  not a blocker - to investigate before Day 4 if it recurs on our own data.
- Smoke test acceptance criteria (binaries link, full pipeline runs end-to-end,
  GUI works, initial guess writes, calibrate loads + iterates with cost
  decreasing) are all met.
- Final NID cost on sample: 1.918880 (stage 3 final)
- Smoke test outcome: PASS
- Sample calib.json was not produced (stage 4 incomplete); not needed
  because this is sample data, not our calibration.


### CORRECTION - calibrate ran to completion (outer loop converged)

Earlier interpretation of 'stage 4 stall' was incorrect:
- Stages were outer-loop iterations of viewpoint–NID joint refinement, not pyramid levels
- Each inner BFGS hits Wolfe warnings near the minimum (expected; gradient flat)
- Outer loop re-integrates points with new viewpoint and re-runs BFGS
- Convergence reached when delta_t = 0 and delta_r = 0

Calibrate also opens an Iridescence visualizer (not just headless terminal);
convergence trail visible in the GUI panel, includes a Clear button.

### Final smoke-test result

- Final NID cost on Ouster sample: 1.919
- Outer loop converged
- T_lidar_camera saved to ouster_preprocessed/calib.json

```json
{
  "camera": {
    "camera_model": "plumb_bob",
    "distortion_coeffs": [
      -0.05070133726528313,
      0.11123608292999987,
      -0.0008818378436413125,
      0.00014119859233105612,
      -0.05889146884561059
    ],
    "intrinsics": [
      1454.658624776836,
      1455.212234800831,
      1229.262650803659,
      1010.6631200967514
    ]
  },
  "meta": {
    "bag_names": [
      "rosbag2_2023_03_28-16_25_54",
      "rosbag2_2023_03_28-16_26_51"
    ],
    "camera_info_topic": "/camera_info",
    "data_path": "ouster",
    "image_topic": "/image",
    "intensity_channel": "reflectivity",
    "points_topic": "/points"
  },
  "results": {
    "T_lidar_camera": [
      0.04271808171706065,
      -0.003816329698693938,
      0.09890075277770048,
      -0.49535561059879923,
      0.49701159360885805,
      -0.5044294032220341,
      0.5031433911239781
    ],
    "init_T_lidar_camera": [
      -0.0827382504940033,
      0.2527090609073639,
      0.2531648576259613,
      -0.49000262687974755,
      0.5150949736941768,
      -0.5031731862058688,
      0.49131593606019974
    ]
  }
}
```

### Day 2 smoke test outcome: PASS

