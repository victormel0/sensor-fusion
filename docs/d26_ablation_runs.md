# Day 3 (d26) ablation runs -- 2026-06-17

**Scope:** env-2 annotation -> overlay sanity -> 3 arms on all annotated frames -> metrics -> figures.
**Models:** yolov8s.pt (accuracy reference, d23); pp_multihead_nds5823_updated.pth; conf=0.25 / score>=0.30.
**Note:** verbose per-frame run logs are in `/tmp/d26_fused.log` and `/tmp/d26_lidar.log`; this manifest
keeps only the headline numbers and tables (the §3.4 metrics tables are the digest pasted into the log).

## 3.1 Env-2 annotation totals
```
frames=17 instances=102 occluded=6 with_tape_range=96
per-class: {'box': 17, 'bottle': 17, 'trash bin': 17, 'chair1': 17, 'chair2': 17, 'potted plant': 17}
```
- pose1 = 5 frames, pose2 = 6, pose3 = 6. 6 markers/frame (4 COCO: bottle, chair1, chair2, potted plant
  + 2 LiDAR-only: box, trash bin). occluded=6 = the pose2 potted plant (out of FOV, all 6 pose2 frames).
- Scene is sparse (lab room: workbench + cabinets are not COCO); the 6 markers are the in-scope set.
- Combined annotated set: env-1 12 + env-2 102 = 114 instances over ~10 unique objects across 4 scenes.

## 3.2 Env-2 overlay sanity check (PASS)
```
- transform: t=(0.1228, -0.0147, -0.1599)  quat=(-0.4969, 0.5101, -0.5006, 0.4923)
  (matches the accepted extrinsic +0.123 / -0.015 / -0.160)
- intrinsics: fx=335.1257 fy=359.3457 cx=486.2645 cy=291.6999
- [campose] total=54748 in_front=23805 in_image=13097 -> docs/screenshots/d26_env2_overlay.png
```
- PASS: points land on scene structure; small near-range/edge offset only. Confirmed quantitatively by
  the §3.4 projection self-check = 100% and by fused ranges landing on real objects (e.g. pose3 plant
  7.37 m vs GT 7.38 m).

## 3.3 Three-arm runs (verbose logs in /tmp/d26_fused.log + /tmp/d26_lidar.log)
- Fused (frustum_fuse.py): every YOLO box earned a cluster -> **31/31 fused env-1, 45/45 fused env-2**
  (0 camera_only in either environment). Outputs in code/eval/runs/fused/.
- LiDAR-only (PointPillars demo.py): above score 0.30 -> env-1 **4 / 3 / 5** boxes on 00100 / 00300 /
  00500; env-2 **0 above 0.30 on all 17 frames** (nuScenes model is out-of-domain on indoor furniture
  = the expected domain gap, consistent with the Week-2 d13 baseline). env-1 lidar outputs renamed to
  env1_<F>.json. Outputs in code/eval/runs/lidar/.
- Camera-only: derived from the fused JSON by metrics.py (identical detection set); no separate run.
- Honesty checks applied: range stats only on source=="fused"; fused-rate + reason reported; LiDAR-only
  not-assessable kept separate (the env-2 zeros); occluded exclusions counted; operating points untouched.

## 3.4 Metrics

projection self-check: `project_lidar (exact fused-arm projection)` -- fused centroids inside box_xyxy = **100% (OK)**.

### Presence (recall / precision / class-correctness)
camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| env1 | camera_only | 1.0 | 0.387 | 1.0 | 12 | 19 | 12 |
| env1 | fused | 1.0 | 0.387 | 1.0 | 12 | 19 | 12 |
| env2 | camera_only | 0.302 | 0.644 | 0.828 | 29 | 16 | 96 |
| env2 | fused | 0.302 | 0.644 | 0.828 | 29 | 16 | 96 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious
classes are EXPECTED. Reported via the gate table.

### Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.
Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only has NO range. Per env and per object.

| env | arm | object | N | median | IQR | RMSE |
|---|---|---|---|---|---|---|
| env1 | fused | chair | 3 | 0.402 | 0.002 | 0.401 |
| env1 | fused | person | 3 | 0.094 | 0.002 | 0.161 |
| env1 | fused | tv | 6 | 0.082 | 0.056 | 0.087 |
| env1 | lidar_only | chair | 3 | -0.332 | 0.075 | 0.31 |
| env1 | lidar_only | person | 3 | 0.115 | 0.005 | 0.164 |
| env2 | fused | bottle | 6 | 0.384 | 0.002 | 0.383 |
| env2 | fused | box | 3 | -0.404 | 0.005 | 0.372 |
| env2 | fused | chair | 13 | 0.256 | 0.527 | 0.316 |
| env2 | fused | potted plant | 5 | 0.326 | 0.006 | 0.326 |
| env2 | fused | trash bin | 2 | 0.187 | 0.0 | 0.187 |

#### per-env aggregate
| env | arm | N | median | IQR | RMSE |
|---|---|---|---|---|---|
| env1 | fused | 12 | 0.11 | 0.191 | 0.225 |
| env1 | lidar_only | 6 | 0.0 | 0.442 | 0.248 |
| env2 | fused | 29 | 0.259 | 0.194 | 0.332 |

FOOTNOTES:
- env1 GT tier: ~10 cm coarse (reconstructed d25; d10 superseded; 3D but ~= horizontal for these near-LiDAR-height objects). Errors below the tier are not interpretable.
- env2 GT tier: ~10 cm medium (range_m is HORIZONTAL; GT = floor/horizontal measure; the 3D slant over-reads by the height term; chairs also carry the centroid offset). Errors below the tier are not interpretable.
- range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset (env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.
- env-2 `bottle` (+0.38) and `box` (-0.40) sit above the tier: bottle and box share a bearing (the d25 caveat), so the chosen cluster can pick up the neighbour / background; reported per object rather than buried.

### Fused-rate (fraction of YOLO boxes that earned a LiDAR range)
| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |
|---|---|---|---|---|---|---|
| env1 | 31 | 31 | 1.000 | 0 | 0 | 0 |
| env2 | 45 | 45 | 1.000 | 0 | 0 | 0 |

Result: fused-rate is 100% in BOTH environments -- the hypothesised drop on the sparser env-2 did NOT
occur, because the env-2 objects are close enough (mostly < 4 m) to carry >= 10 LiDAR points each. So
the honest fused-rate story is "fusion localised every detection here," not "fusion degrades when sparse."

### LiDAR-only match counts by BEV range gate (0.75 m primary; pre-declared)
| env | 0.50 m | 0.75 m | 1.00 m |
|---|---|---|---|
| env1 | 6 | 6 | 6 |
| env2 | 0 | 0 | 0 |

Bearing proxy = LiDAR detection projects inside the GT box x-extent (self-check was 100%, so reliable).
env-2 = 0 at every gate: the nuScenes LiDAR detector produced nothing above 0.30 there.

## Results / artifacts produced
- runs: code/eval/runs/fused/ (env1_*, env2_pose*_*), code/eval/runs/lidar/ (env1_*, env2_pose*_*).
- metrics: docs/d26_metrics/{presence_table.md, range_error_table.md, fused_rate_table.md, gate_sensitivity.md, per_match.csv}.
- figures: d26_fig_range_scatter.png, d26_fig_presence_bars.png, d26_fig_fused_rate.png
- qualitative panels (>= 2 success + >= 2 failure): d26_fig_qual_fail_env2_pose2_chair_missed.png, d26_fig_qual_fail_env2_pose3_box_microwave.png,
d26_fig_qual_success_env1_person_monitors.png, d26_fig_qual_success_env2_pose3_chair_plant.png
- FP16 appendix row: not run (optional).

## Headline
Self-check 100% (projection sound). camera_only == fused presence exactly (expected). env-1: recall 1.0,
precision 0.39 (YOLO over-detects the lab scene through the doorway), class 1.0. env-2: recall 0.30
(2 unclassifiable markers/frame + YOLO out-of-distribution misses), precision 0.64, class 0.83. LiDAR-only
fires only in env-1 (6 matches) and is blank in env-2 (domain gap). Range near 1:1; the per-object
offsets (env-1 chair +0.40 centroid, env-2 bottle/box shared-bearing) are explained, not buried.
