# Day (d33) Tier-2 capture (varied lighting) -- 2026-07-04 -- STATUS: capture + bag QA DONE

**Scope:** 2 scenes x 3 lighting conditions, rig static per bag, ~60-90 s each, bag QA. Frame export
is d34 scope. Room: the NEW meeting room (env-3 informally; not env-1's room, not the env-2 lab).
**Power profile (nvpmodel -q):**
```
NV Power Mode: MAXN
0
```

## Session context

- Same day as the ZED Box boot-failure recovery (see `docs/incident_report_zedbox_boot_failure_2026-07.md`).
  Pre-capture verification gates all GREEN: camera 29.92 Hz / LiDAR 9.99 Hz / pairing 100.0% on a
  dedicated gate bag; `parity_check.py` on frames 00100/00300/00500 = 3x PASS with 0.0000 m max
  range/centroid deltas, 0 source flips, both decoder cross-checks clean; MAXN confirmed.
- **Lighting conditions (locked mapping, applied to BOTH scenes):**
  bright = ceiling lights ON + blinds CLOSED; dim = lights OFF + blinds CLOSED;
  mixed = lights OFF + blinds OPEN.
- **Morning s2 capture DISCARDED and re-recorded.** A first s2 session (10:58-11:04) was recorded
  with a wrong condition mapping (the bag named bright held blinds-open+lights-off; the bag named
  mixed held blinds-open+lights-on, a non-grid cell; the true bright was never recorded). All
  morning `w6_*` folders were deleted and the full s2 grid re-recorded 15:47-15:52 with the correct
  mapping. Between the sessions only the water bottle and the far potted plant had been moved; both
  were re-placed on their positions using the floor tile lines as alignment. A tape re-check of
  those two d_h values was recommended; `<confirm: tape re-check done? if values differ from
  1.18 / 7.83 m, correct the s2 table below>`.

## Scene s2 -- ranged regime (probes F1 far plant, F2 chair, F3 near bottle, F4 out-of-vocabulary)

Rig on the long axis toward the open door; `<fill: rig support + sensor height>`. Door OPEN in all
three conditions (the F1 plant stands in the doorway against a white wall backdrop). Whiteboard
parked in front of the left glass partition (kills the partition ghost-return risk). LiDAR cloud
eyeballed in RViz before recording: objects return points; a distinct cluster at the far plant
position confirmed visually (screenshot `w6_s2_bright_lidar.png`).

- LiDAR axis plumb point: NOT photographed (scene dismantled; recorded as a known traceability gap). Point was marked physically during blind measurement.
- Scene reference screenshot (camera): `w6_s2_bright.png`

| Object | Class | d_h horizontal (m) | Ref point | Support | Contrast note | Photo |
|---|---|---|---|---|---|---|
| Water bottle | bottle | 1.18 | front-center | floor | dark bottle on light tile | `<confirm>` |
| Yellow box | box | 1.76 | front-center | floor | HIGH-contrast (yellow + checker) | `<confirm>` |
| Middle chair (chair1) | chair | 1.79 | front-center | floor | black frame chair | `<confirm>` |
| Window plant | potted plant | 2.65 | front-center | `<window ledge / hanging -- confirm>` | green on white wall; HIDDEN behind closed blinds in bright/dim (1-2 leaves may leak -> occluded), visible in mixed | `<confirm>` |
| Trash bin | trash bin | 2.93 | front-center | floor | grey bin | `<confirm>` |
| Left chair + black bag (chair2) | chair (+ backpack on seat) | 3.80 | front-center | floor | LOW-contrast marker (dark bag on dark chair) | `<confirm>` |
| Wall TV | tv | 5.91 | front-center | wall mount | black panel on white wall; TV OFF | `<confirm>` |
| Potted plant (F1 probe) | potted plant | 7.83 | front-center | floor (doorway) | green on white backdrop; essentially at the d32-measured F1 range (7.38 m) | `<confirm>` |

s2 design notes: bottle at 1.18 m vs the ~1.0 m F3 target (+0.18 m deviation, accepted -- still
probes the measured ~0.94 m flicker mechanism region). Per-condition GT visibility differs for the
window plant (see its row); note carried to d34 so per-class counts across conditions are read
correctly. Shared-bearing spacing rule (>= 1.5 m) checked: closest same-bearing pair is
chair1/chair2 at 2.01 m separation; near-range objects (bottle/box/chair1) sit on distinct bearings
with horizontally separated 2D boxes.

## Scene s1 -- near-field regime (dense office arrangement)

Rig beside the long meeting table, facing the TV wall, ~2.5 m from it; `<fill: rig support + sensor
height>`. Door CLOSED (removes the corridor background). Hybrid supports: cup/keyboard/laptop on
the table edge, chair and box on the floor, TV on the wall. Trash bin removed from the FOV
`<confirm>`. Scene reference screenshot: `Screenshot_2026-07-04_191917.png` (final layout).

- LiDAR axis plumb point: NOT photographed (scene dismantled; recorded as a known traceability gap). Point was marked physically during blind measurement.

| Object | Class | d_h horizontal (m) | Ref point | Support | Contrast note | Photo |
|---|---|---|---|---|---|---|
| Cup/mug | cup | 1.49 | front-center | table edge | dark mug on dark table | `<confirm>` |
| Keyboard | keyboard | 1.51 | front-center | table edge | dark on dark | `<confirm>` |
| Laptop | laptop | 1.61 | front-center | table edge | white lid on dark table | `<confirm>` |
| Chair + black bag | chair (+ backpack on seat) | 1.66 | front-center | floor | LOW-contrast marker | `<confirm>` |
| Yellow box | box | 2.01 | front-center | floor | HIGH-contrast (yellow + checker) | `<confirm>` |
| Wall TV | tv | 2.49 | front-center | wall mount | black panel on white wall; TV OFF; s1 anchor | `<confirm>` |

s1 design notes, honest deviations: depth spread is SHALLOW (1.49-2.49 m) -- the far half of the
locked "near-field 1-4 m" regime is blocked by the room's short axis (wall directly behind the
chair position); accepted because s2 covers the ranged regime. In s1 the windows sit beside the
rig, so mixed here is SIDE-light rather than the backlight regime of s2 -- expected, and a useful
contrast between the two scenes.

## Recording protocol + timing

Loop per scene: set lighting -> confirm rig static -> `ros2 bag record` on
`/zed/zed_node/rgb/color/rect/image`, `.../camera_info`, `/rslidar_points` -> Ctrl-C at ~60-90 s.
Camera on auto-exposure throughout (intentional: exposure adaptation IS part of the probe).
Geometry locked per scene across its 3 bags; nothing moved between conditions.

- s2 session 15:47:02-15:52:22 (bright -> dim -> mixed; inter-bag pauses ~42 s and ~83 s).
- s1 session 18:13:59-18:18:25 (bright -> dim -> mixed; inter-bag pauses ~23 s and ~53 s).
- Thermal note: the LiDAR was NOT powered off between bags; it spun continuously ~5.5 min (s2) and
  ~4.5 min (s1) per session. No formal thermal gate is defined for this project; durations are
  comparable to previous capture sessions. Documented as fact, not as a violation.

## ros2 bag info (all six grid bags)

```
Files:             w6_s2_bright_0.db3
Bag size:          4.8 GiB
Storage id:        sqlite3
Duration:          65.177364392s
Start:             Jul  4 2026 15:47:02.358637875 (1783180022.358637875)
End:               Jul  4 2026 15:48:07.536002267 (1783180087.536002267)
Messages:          4554
Topic information: Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 652 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1951 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1951 | Serialization Format: cdr


Files:             w6_s2_dim_0.db3
Bag size:          4.7 GiB
Storage id:        sqlite3
Duration:          65.365196580s
Start:             Jul  4 2026 15:48:49.195179152 (1783180129.195179152)
End:               Jul  4 2026 15:49:54.560375732 (1783180194.560375732)
Messages:          4482
Topic information: Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1914 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1914 | Serialization Format: cdr
                   Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 654 | Serialization Format: cdr


Files:             w6_s2_mixed_0.db3
Bag size:          4.7 GiB
Storage id:        sqlite3
Duration:          65.015330083s
Start:             Jul  4 2026 15:51:17.376357700 (1783180277.376357700)
End:               Jul  4 2026 15:52:22.391687783 (1783180342.391687783)
Messages:          4543
Topic information: Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1946 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1946 | Serialization Format: cdr
                   Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 651 | Serialization Format: cdr



Files:             w6_s1_bright_0.db3
Bag size:          4.6 GiB
Storage id:        sqlite3
Duration:          63.291720360s
Start:             Jul  4 2026 18:13:58.706806027 (1783188838.706806027)
End:               Jul  4 2026 18:15:01.998526387 (1783188901.998526387)
Messages:          4421
Topic information: Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1894 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1894 | Serialization Format: cdr
                   Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 633 | Serialization Format: cdr


Files:             w6_s1_dim_0.db3
Bag size:          4.8 GiB
Storage id:        sqlite3
Duration:          65.274048257s
Start:             Jul  4 2026 18:15:24.699818435 (1783188924.699818435)
End:               Jul  4 2026 18:16:29.973866692 (1783188989.973866692)
Messages:          4561
Topic information: Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 653 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1954 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1954 | Serialization Format: cdr


Files:             w6_s1_mixed_0.db3
Bag size:          4.6 GiB
Storage id:        sqlite3
Duration:          62.505560210s
Start:             Jul  4 2026 18:17:22.469845189 (1783189042.469845189)
End:               Jul  4 2026 18:18:24.975405399 (1783189104.975405399)
Messages:          4368
Topic information: Topic: /zed/zed_node/rgb/color/rect/image | Type: sensor_msgs/msg/Image | Count: 1871 | Serialization Format: cdr
                   Topic: /zed/zed_node/rgb/color/rect/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1871 | Serialization Format: cdr
                   Topic: /rslidar_points | Type: sensor_msgs/msg/PointCloud2 | Count: 626 | Serialization Format: cdr
```

## Bag QA summary (bag_analysis.py, arrival-timestamp based)

| Bag | Camera Hz | LiDAR Hz | Pairing yield (+-50 ms) | Verdict | Notes |
|---|---|---|---|---|---|
| w6_s1_bright | 29.92 | 10.00 | 633/633 = 100.0% | PASS | |
| w6_s1_dim | 29.94 | 10.00 | 653/653 = 100.0% | PASS | |
| w6_s1_mixed | 29.93 | 10.02 | 626/626 = 100.0% | PASS | |
| w6_s2_bright | 29.93 | 10.00 | 652/652 = 100.0% | PASS | |
| w6_s2_dim | 29.28 | 10.01 | 639/654 = **97.7%** | PASS (tool targets) | DEVIATION vs the ~99% project yield target: one LiDAR inter-arrival gap of 420 ms; worst best-dt 1473.7 ms (brief hiccup window). Assessment: d34 selects ~5 frames per condition and avoids the hiccup window; not a re-record trigger. |
| w6_s2_mixed | 29.93 | 10.01 | 651/651 = 100.0% | PASS | |

Five of six bags at 100.0% pairing; all six pass the tool verdicts (camera >= 25 Hz, LiDAR >= 9.5 Hz).

## Pending after d33

- d34: frame export (~5 frames per condition, ~30 total), annotation. Window-plant per-condition
  visibility note applies to the s2 GT.
- Copy the six `w6_*` bag folders + this manifest to the external backup disk (the bags currently
  exist ONLY on the box; the incident-day backup predates them).
- Fill the `<confirm>` / `<fill>` fields above (photo filenames, rig support + height, tape
  re-check outcome, bin-removal confirm).

## Full bag_analysis.py outputs (verbatim)

## Bag QA (rates + pairing yield)
### w6_s1_bright
[INFO] [1783189183.656257340] [rosbag2_storage]: Opened database 'recordings/w6_s1_bright/w6_s1_bright_0.db3' for READ_ONLY.
# Bag analysis report

**Bag folder:** `/home/user/Documents/workspace/sensor-fusion/recordings/w6_s1_bright`
**Duration (from arrival ts):** 63.29 s
**Total messages:** 4421

## Per-topic statistics

### `/rslidar_points`
- type: `sensor_msgs/msg/PointCloud2`
- count: **633**
- observed rate: **10.00 Hz**
  - **arrival interval (ms)**: n=632, mean=99.98, median=99.99, stdev=5.70, min=83.14, max=116.35
  - no gaps larger than 3.0× median (300.0 ms)
  - **arrival - header timestamp (ms)**: n=633, mean=104.04, median=102.51, stdev=4.00, min=97.69, max=117.65

### `/zed/zed_node/rgb/color/rect/camera_info`
- type: `sensor_msgs/msg/CameraInfo`
- count: **1894**
- observed rate: **29.92 Hz**
  - **arrival interval (ms)**: n=1893, mean=33.43, median=33.41, stdev=14.25, min=0.01, max=344.89
  - **8 large gap(s) (>3.0× median, >100.2 ms) — largest 344.9 ms**
  - **arrival - header timestamp (ms)**: n=1894, mean=70.43, median=67.37, stdev=25.06, min=48.93, max=379.56

### `/zed/zed_node/rgb/color/rect/image`
- type: `sensor_msgs/msg/Image`
- count: **1894**
- observed rate: **29.92 Hz**
  - **arrival interval (ms)**: n=1893, mean=33.42, median=33.42, stdev=5.66, min=1.48, max=79.61
  - no gaps larger than 3.0× median (100.3 ms)
  - **arrival - header timestamp (ms)**: n=1894, mean=71.80, median=71.64, stdev=10.33, min=51.40, max=114.65

## Camera ↔ LiDAR pairing (by header timestamp)

For each LiDAR frame, find the nearest camera frame by header timestamp. Slop window: ±50 ms.

- LiDAR frames considered: **633**
- Paired within slop: **633 (100.0%)**
  - **best dt per LiDAR frame (ms)**: n=633, mean=9.50, median=9.53, stdev=0.54, min=5.53, max=10.69

## Verdict

- ✓ Camera rate: 29.9 Hz (target ≥25 Hz)
- ✓ LiDAR rate: 10.0 Hz (target ≥9.5 Hz)
### w6_s1_dim
[INFO] [1783189201.100135301] [rosbag2_storage]: Opened database 'recordings/w6_s1_dim/w6_s1_dim_0.db3' for READ_ONLY.
# Bag analysis report

**Bag folder:** `/home/user/Documents/workspace/sensor-fusion/recordings/w6_s1_dim`
**Duration (from arrival ts):** 65.27 s
**Total messages:** 4561

## Per-topic statistics

### `/rslidar_points`
- type: `sensor_msgs/msg/PointCloud2`
- count: **653**
- observed rate: **10.00 Hz**
  - **arrival interval (ms)**: n=652, mean=99.98, median=100.01, stdev=5.66, min=85.20, max=113.94
  - no gaps larger than 3.0× median (300.0 ms)
  - **arrival - header timestamp (ms)**: n=653, mean=104.64, median=102.93, stdev=4.20, min=93.89, max=117.17

### `/zed/zed_node/rgb/color/rect/camera_info`
- type: `sensor_msgs/msg/CameraInfo`
- count: **1954**
- observed rate: **29.94 Hz**
  - **arrival interval (ms)**: n=1953, mean=33.42, median=33.41, stdev=12.34, min=0.02, max=311.61
  - **8 large gap(s) (>3.0× median, >100.2 ms) — largest 311.6 ms**
  - **arrival - header timestamp (ms)**: n=1954, mean=67.34, median=63.95, stdev=20.77, min=48.40, max=338.16

### `/zed/zed_node/rgb/color/rect/image`
- type: `sensor_msgs/msg/Image`
- count: **1954**
- observed rate: **29.94 Hz**
  - **arrival interval (ms)**: n=1953, mean=33.41, median=33.42, stdev=5.95, min=9.27, max=61.71
  - no gaps larger than 3.0× median (100.3 ms)
  - **arrival - header timestamp (ms)**: n=1954, mean=69.60, median=67.99, stdev=10.98, min=50.05, max=100.39

## Camera ↔ LiDAR pairing (by header timestamp)

For each LiDAR frame, find the nearest camera frame by header timestamp. Slop window: ±50 ms.

- LiDAR frames considered: **653**
- Paired within slop: **653 (100.0%)**
  - **best dt per LiDAR frame (ms)**: n=653, mean=8.73, median=8.67, stdev=1.26, min=2.06, max=25.54

## Verdict

- ✓ Camera rate: 29.9 Hz (target ≥25 Hz)
- ✓ LiDAR rate: 10.0 Hz (target ≥9.5 Hz)
### w6_s1_mixed
[INFO] [1783189220.174360493] [rosbag2_storage]: Opened database 'recordings/w6_s1_mixed/w6_s1_mixed_0.db3' for READ_ONLY.
# Bag analysis report

**Bag folder:** `/home/user/Documents/workspace/sensor-fusion/recordings/w6_s1_mixed`
**Duration (from arrival ts):** 62.51 s
**Total messages:** 4368

## Per-topic statistics

### `/rslidar_points`
- type: `sensor_msgs/msg/PointCloud2`
- count: **626**
- observed rate: **10.02 Hz**
  - **arrival interval (ms)**: n=625, mean=99.98, median=99.94, stdev=5.75, min=77.86, max=115.30
  - no gaps larger than 3.0× median (299.8 ms)
  - **arrival - header timestamp (ms)**: n=626, mean=104.61, median=102.87, stdev=4.29, min=93.95, max=124.26

### `/zed/zed_node/rgb/color/rect/camera_info`
- type: `sensor_msgs/msg/CameraInfo`
- count: **1871**
- observed rate: **29.93 Hz**
  - **arrival interval (ms)**: n=1870, mean=33.42, median=33.41, stdev=11.96, min=0.01, max=345.69
  - **4 large gap(s) (>3.0× median, >100.2 ms) — largest 345.7 ms**
  - **arrival - header timestamp (ms)**: n=1871, mean=67.58, median=64.45, stdev=22.01, min=48.58, max=373.36

### `/zed/zed_node/rgb/color/rect/image`
- type: `sensor_msgs/msg/Image`
- count: **1871**
- observed rate: **29.93 Hz**
  - **arrival interval (ms)**: n=1870, mean=33.42, median=33.41, stdev=5.12, min=5.93, max=59.78
  - no gaps larger than 3.0× median (100.2 ms)
  - **arrival - header timestamp (ms)**: n=1871, mean=69.48, median=67.92, stdev=10.46, min=50.44, max=97.40

## Camera ↔ LiDAR pairing (by header timestamp)

For each LiDAR frame, find the nearest camera frame by header timestamp. Slop window: ±50 ms.

- LiDAR frames considered: **626**
- Paired within slop: **626 (100.0%)**
  - **best dt per LiDAR frame (ms)**: n=626, mean=7.65, median=7.63, stdev=1.45, min=0.10, max=40.83

## Verdict

- ✓ Camera rate: 29.9 Hz (target ≥25 Hz)
- ✓ LiDAR rate: 10.0 Hz (target ≥9.5 Hz)
### w6_s2_bright
[INFO] [1783189237.595184630] [rosbag2_storage]: Opened database 'recordings/w6_s2_bright/w6_s2_bright_0.db3' for READ_ONLY.
# Bag analysis report

**Bag folder:** `/home/user/Documents/workspace/sensor-fusion/recordings/w6_s2_bright`
**Duration (from arrival ts):** 65.18 s
**Total messages:** 4554

## Per-topic statistics

### `/rslidar_points`
- type: `sensor_msgs/msg/PointCloud2`
- count: **652**
- observed rate: **10.00 Hz**
  - **arrival interval (ms)**: n=651, mean=100.00, median=99.95, stdev=6.64, min=81.75, max=118.73
  - no gaps larger than 3.0× median (299.8 ms)
  - **arrival - header timestamp (ms)**: n=652, mean=105.49, median=102.92, stdev=4.81, min=95.01, max=120.84

### `/zed/zed_node/rgb/color/rect/camera_info`
- type: `sensor_msgs/msg/CameraInfo`
- count: **1951**
- observed rate: **29.93 Hz**
  - **arrival interval (ms)**: n=1950, mean=33.42, median=33.41, stdev=15.11, min=0.01, max=350.61
  - **8 large gap(s) (>3.0× median, >100.2 ms) — largest 350.6 ms**
  - **arrival - header timestamp (ms)**: n=1951, mean=70.61, median=66.93, stdev=26.90, min=48.29, max=391.25

### `/zed/zed_node/rgb/color/rect/image`
- type: `sensor_msgs/msg/Image`
- count: **1951**
- observed rate: **29.93 Hz**
  - **arrival interval (ms)**: n=1950, mean=33.41, median=33.52, stdev=6.52, min=7.67, max=56.91
  - no gaps larger than 3.0× median (100.6 ms)
  - **arrival - header timestamp (ms)**: n=1951, mean=71.90, median=71.95, stdev=10.35, min=51.17, max=105.10

## Camera ↔ LiDAR pairing (by header timestamp)

For each LiDAR frame, find the nearest camera frame by header timestamp. Slop window: ±50 ms.

- LiDAR frames considered: **652**
- Paired within slop: **652 (100.0%)**
  - **best dt per LiDAR frame (ms)**: n=652, mean=6.97, median=6.97, stdev=1.23, min=0.36, max=26.24

## Verdict

- ✓ Camera rate: 29.9 Hz (target ≥25 Hz)
- ✓ LiDAR rate: 10.0 Hz (target ≥9.5 Hz)
### w6_s2_dim
[INFO] [1783189284.063148959] [rosbag2_storage]: Opened database 'recordings/w6_s2_dim/w6_s2_dim_0.db3' for READ_ONLY.
# Bag analysis report

**Bag folder:** `/home/user/Documents/workspace/sensor-fusion/recordings/w6_s2_dim`
**Duration (from arrival ts):** 65.37 s
**Total messages:** 4482

## Per-topic statistics

### `/rslidar_points`
- type: `sensor_msgs/msg/PointCloud2`
- count: **654**
- observed rate: **10.01 Hz**
  - **arrival interval (ms)**: n=653, mean=99.98, median=99.96, stdev=15.65, min=0.66, max=420.33
  - **1 large gap(s) (>3.0× median, >299.9 ms) — largest 420.3 ms**
  - **arrival - header timestamp (ms)**: n=654, mean=106.19, median=102.77, stdev=16.55, min=94.86, max=423.06

### `/zed/zed_node/rgb/color/rect/camera_info`
- type: `sensor_msgs/msg/CameraInfo`
- count: **1914**
- observed rate: **29.28 Hz**
  - **arrival interval (ms)**: n=1913, mean=33.42, median=33.42, stdev=14.63, min=0.01, max=313.55
  - **10 large gap(s) (>3.0× median, >100.3 ms) — largest 313.6 ms**
  - **arrival - header timestamp (ms)**: n=1914, mean=70.01, median=66.25, stdev=23.73, min=49.45, max=342.26

### `/zed/zed_node/rgb/color/rect/image`
- type: `sensor_msgs/msg/Image`
- count: **1914**
- observed rate: **29.28 Hz**
  - **arrival interval (ms)**: n=1913, mean=33.41, median=33.48, stdev=6.42, min=7.77, max=62.04
  - no gaps larger than 3.0× median (100.4 ms)
  - **arrival - header timestamp (ms)**: n=1914, mean=71.49, median=71.38, stdev=10.60, min=51.08, max=104.93

## Camera ↔ LiDAR pairing (by header timestamp)

For each LiDAR frame, find the nearest camera frame by header timestamp. Slop window: ±50 ms.

- LiDAR frames considered: **654**
- Paired within slop: **639 (97.7%)**
  - **best dt per LiDAR frame (ms)**: n=654, mean=23.87, median=6.30, stdev=132.16, min=0.65, max=1473.74

## Verdict

- ✓ Camera rate: 29.3 Hz (target ≥25 Hz)
- ✓ LiDAR rate: 10.0 Hz (target ≥9.5 Hz)
### w6_s2_mixed
[INFO] [1783189344.190151103] [rosbag2_storage]: Opened database 'recordings/w6_s2_mixed/w6_s2_mixed_0.db3' for READ_ONLY.
# Bag analysis report

**Bag folder:** `/home/user/Documents/workspace/sensor-fusion/recordings/w6_s2_mixed`
**Duration (from arrival ts):** 65.02 s
**Total messages:** 4543

## Per-topic statistics

### `/rslidar_points`
- type: `sensor_msgs/msg/PointCloud2`
- count: **651**
- observed rate: **10.01 Hz**
  - **arrival interval (ms)**: n=650, mean=99.98, median=99.92, stdev=6.82, min=86.01, max=113.86
  - no gaps larger than 3.0× median (299.8 ms)
  - **arrival - header timestamp (ms)**: n=651, mean=105.39, median=102.67, stdev=4.93, min=99.55, max=119.95

### `/zed/zed_node/rgb/color/rect/camera_info`
- type: `sensor_msgs/msg/CameraInfo`
- count: **1946**
- observed rate: **29.93 Hz**
  - **arrival interval (ms)**: n=1945, mean=33.43, median=33.41, stdev=13.35, min=0.01, max=348.27
  - **9 large gap(s) (>3.0× median, >100.2 ms) — largest 348.3 ms**
  - **arrival - header timestamp (ms)**: n=1946, mean=68.94, median=65.57, stdev=22.17, min=47.89, max=386.22

### `/zed/zed_node/rgb/color/rect/image`
- type: `sensor_msgs/msg/Image`
- count: **1946**
- observed rate: **29.93 Hz**
  - **arrival interval (ms)**: n=1945, mean=33.42, median=33.44, stdev=6.50, min=9.34, max=59.28
  - no gaps larger than 3.0× median (100.3 ms)
  - **arrival - header timestamp (ms)**: n=1946, mean=70.93, median=70.36, stdev=10.70, min=49.40, max=106.58

## Camera ↔ LiDAR pairing (by header timestamp)

For each LiDAR frame, find the nearest camera frame by header timestamp. Slop window: ±50 ms.

- LiDAR frames considered: **651**
- Paired within slop: **651 (100.0%)**
  - **best dt per LiDAR frame (ms)**: n=651, mean=5.40, median=5.30, stdev=1.87, min=2.21, max=38.35

## Verdict

- ✓ Camera rate: 29.9 Hz (target ≥25 Hz)
- ✓ LiDAR rate: 10.0 Hz (target ≥9.5 Hz)
