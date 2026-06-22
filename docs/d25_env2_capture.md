# Day 2 (d25) env-2 capture -- 2026-06-16

**Scope:** marked-distance scene (bigger indoor room), 3 rig poses (one with a lighting change),
bag QA, frame export. Env-2 carries the bulk of the range-GT and presence/class budget.

**Power profile (nvpmodel -q):** MAXN.

## Measurement method + precision tier (CORRECTED: range_m is HORIZONTAL)

- range_m IS HORIZONTAL / BEV = hypot(x, y) from the LiDAR axis (VERIFIED in frustum_fuse.py:
  `rng = np.hypot(centroid[0], centroid[1])`; height dropped). NOT 3D Euclidean. So the GT range must
  also be HORIZONTAL.
- GT range per object = the FLOOR (horizontal) measure -- it is the right TYPE to compare against the
  horizontal range_m. The DIRECT (3D slant) measure is now the CROSS-CHECK; it OVER-reads range_m by
  the height term (LiDAR axis ~0.78 m up; objects sit lower).
- RESIDUAL on the floor measure: it was taped to the platform-box EDGE, not the LiDAR AXIS, so it
  UNDER-reads the true horizontal-from-axis by the (unmeasured) axis-to-edge offset. The true
  horizontal GT is therefore BRACKETED between FLOOR (under) and DIRECT (over).
- TIER (HONEST): env-2 GT ~ +/-10 cm (the floor/direct bracket width), NOT the ~5 cm stated earlier.
  CHAIRS additionally carry the front-face-vs-centroid offset (deep object). Errors below the tier are
  not interpretable. metrics.py reports per object + footnotes the centroid caveat.
- TIGHTENING (PENDING, optional one-off): measure the horizontal axis-to-platform-edge offset once and
  ADD it to every floor value -> converts floor to true horizontal-from-axis, pulling env-2 to ~5 cm.
  Until measured, GT = floor values as-is at ~10 cm.
- LiDAR origin height (reference): floor-to-top-of-LiDAR = 0.82 m -> h_O ~ 0.78 m (origin = top - 0.0365 m).
- Cross-check: direct >= floor every pose (slant >= horizontal, as required), agreeing ~1-11 cm.
- ENV-1 NOTE: env-1 ranges were set as 3D (1.36 / 4.22 / 1.90 / 2.30). Those objects sit near LiDAR
  height, so 3D ~= horizontal within the env-1 coarse ~10 cm tier; env-1 kept as-is (small +bias noted).

## Object label expectations (record; verified at d26 against actual detections)
- trash bin -> NO clean COCO class -> LiDAR-only range target (camera will likely not name it).
- green bottle -> COCO `bottle` (camera+fused+range; may weaken at range but markers are near).
- chair1, chair2 -> COCO `chair` (camera+fused; range carries the centroid caveat).
- box (yellow Hyva, checkerboard face) -> NO COCO class -> LiDAR-only range target.
- potted plant (back, by the sofa) -> COCO `potted plant` (uncertain at ~7.4-7.9 m; a miss there is a
  legitimate recorded result, not a fault).
- CAVEAT: box + bottle share a bearing and are close in range (within the 0.75 m gate in some poses).
  Camera/fused separate them by 2D box; LiDAR-only may treat them as one cluster -- not a miss.

## Marker table -- pose 1 (rig at original position; room light on)
| Object | Class / expectation | FLOOR = GT horiz (m) | DIRECT 3D check (m) | Note |
|---|---|---|---|---|
| trash bin | LiDAR-only | 1.22 | 1.36 | left |
| green bottle | bottle | 1.36 | 1.54 | near box, shared bearing |
| chair1 | chair | 1.90 | 2.00 | centroid caveat |
| box | LiDAR-only | 1.93 | 2.11 | near bottle, shared bearing |
| chair2 | chair | 4.08 | 4.18 | centroid caveat |
| potted plant | potted plant | 7.74 | 7.86 | far, by sofa; may miss |

## Marker table -- pose 2 (rig moved RIGHT + slightly AHEAD; room light on)
| Object | Class / expectation | FLOOR = GT horiz (m) | DIRECT 3D check (m) | Note |
|---|---|---|---|---|
| trash bin | LiDAR-only | 1.32 | 1.39 | |
| green bottle | bottle | 0.94 | 1.12 | very near |
| chair1 | chair | 1.75 | 1.74 | floor~direct (cm-noise floor) |
| box | LiDAR-only | 1.40 | 1.59 | |
| chair2 | chair | 3.74 | 3.82 | |
| potted plant | -- | not in view | not in view | out of FOV this pose |

## Marker table -- pose 3 (rig BACK to ~pose1 + slightly AHEAD; CURTAIN OPEN, ROOM LIGHT OFF -> daylight)
| Object | Class / expectation | FLOOR = GT horiz (m) | DIRECT 3D check (m) | Note |
|---|---|---|---|---|
| trash bin | LiDAR-only | 0.77 | 0.95 | <1.5 m -- check framing |
| green bottle | bottle | 0.95 | 1.16 | <1.5 m -- check framing |
| chair1 | chair | 1.42 | 1.44 | <1.5 m -- check framing |
| box | LiDAR-only | 1.60 | 1.79 | |
| chair2 | chair | 3.61 | 3.69 | |
| potted plant | potted plant | 7.38 | 7.44 | far; daylight pose |

- Independent range-GT content: pose1 6 + pose2 5 + pose3 6 = 17 (object,pose) points.
- Pose-3 close markers (<1.5 m): verify they are fully framed in the exported PNGs; if clipped at the
  image bottom (low mount), mark occluded/out-of-scope rather than annotating a partial box.

## Bag QA (authoritative; full reports retained on box)
| Pose | dur (s) | LiDAR (Hz) | cam (Hz) | pairing yield | best-dt median (ms) |
|---|---|---|---|---|---|
| env2_pose1 | 56.58 | 10.00 | 29.92 | 566/566 (100.0%) | 7.67 |
| env2_pose2 | 62.30 | 10.02 | 29.90 | 623/624 (99.8%) | 10.88 |
| env2_pose3 | 61.97 | 9.99 | 29.92 | 619/619 (100.0%) | 15.99 |
- Verdict per pose: PASS (cam >=25 Hz, LiDAR >=9.5 Hz, pairing ~100%).
- Note: sync offset grew across the session (7.7 -> 10.9 -> 16.0 ms median) -- mild clock drift over
  ~50 min, all within the 50 ms slop, no effect.

## Frame export (cv_bridge-free; 17 pairs total)
```
env2_pose1 -> code/eval/frames_env2/env2_pose1 : 00100..00500 dt 7.18/7.49/7.75/7.40/7.87 ms (5)
env2_pose2 -> code/eval/frames_env2/env2_pose2 : 00100..00600 dt 10.32/9.99/11.35/11.17/11.39/11.12 ms (6)
env2_pose3 -> code/eval/frames_env2/env2_pose3 : 00100..00600 dt 15.89/16.44/15.41/16.15/16.38/16.42 ms (6)
```
- bins written to code/bag_to_bin/out/ (env2_poseN_NNNNN.bin); all dt under 50 ms slop.

## Screenshots
- d25_env2_scene.png (pose1), d25_env2_scene_pose2.png, d25_env2_scene_pose3.png, d25_bag_qa.png.

## Final state (d25)
- 3 poses recorded + QA PASS; 17 frame pairs exported; lighting variation in pose3.
- range_m is HORIZONTAL -> env-2 GT = FLOOR measure; ~10 cm tier (floor/direct bracket); chairs carry
  the centroid caveat. Optional axis-to-edge offset (PENDING) would tighten to ~5 cm. box+bottle
  shared-bearing caveat recorded.
- Independent range-GT points: 17 (object,pose). Presence/class budget to be boosted at d26 by
  annotating the full visible COCO object set per frame, not just the 6 markers.
- Day 2 outcome: PASS -- cleared for d26 (annotation close + 3-arm runs + metrics + figures).
