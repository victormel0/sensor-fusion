# Day 1 (d24) evaluation design freeze -- 2026-06-15

**Scope:** frozen definitions (+ evidence) -> env-1 frame export -> annotation tool smoke test -> env-1 annotation.
**Gates at start of day:** G0 (send date) = flexible; G1 (office) = daily; G2 (camera range arm) = OUT (no range column).
**Env-1 range GT (the FILLED-AT-D25 table near the bottom) completed in the office d25 (2026-06-16).**

## Frozen definitions (before any results)

- GT unit: annotated instance = (frame, object). Both instance counts and unique-object counts are
  reported; the static env-1 bag's frames are pseudo-replicates (4 unique objects), stated as such.
- Annotation schema (one JSON per frame, written by code/eval/annotate_gt.py): per object:
  class (free string; mapped to COCO / nuScenes by the table below), bbox_2d [x1,y1,x2,y2] in
  ORIGINAL 960x600 pixels, range_m_tape (tape-measured; null when not measured), occluded (bool),
  notes (string).
- Class mapping table (extend as env-2 adds classes; record every addition here):
    chair             -> COCO chair   | nuScenes: none (expected LiDAR-arm miss or spurious class)
    person / person-in-chair -> COCO person | nuScenes pedestrian (person-in-chair: chair OR person both correct)
    left monitor / right monitor / tv / monitor -> COCO tv | nuScenes: none
    laptop            -> COCO laptop  | nuScenes: none
    keyboard          -> COCO keyboard| nuScenes: none
    <env-2 additions: fill>
- Person-in-chair rule (2026-06-02): for that object, class is correct for chair OR person, every arm.
- Scope rule (task plan): annotate objects ~2-15 m ahead, not heavily occluded; outside that set
  occluded=true (kept in file, excluded from recall denominators, exclusion count reported).

- CAMERA-ONLY ARM HAS NO RANGE COLUMN (decision d24): a monocular camera cannot measure distance --
  the stated fusion premise. No box-height / monocular range estimator (would contradict
  04_experiments.tex and break on the seated person-in-chair). Range columns are LiDAR-only and
  fused only. Camera-only vs fused presence (recall/precision/class) is IDENTICAL by construction
  (verified against frustum_fuse.py: every YOLO box survives as source=="fused" or
  source=="camera_only"); report as expected, not a finding.

- GT RANGE CONVENTION (RESOLVED; updated d25): all arms report range in the LiDAR frame, so GT range
  is LiDAR-frame too. The clean way to get a LiDAR-frame range is to TAPE FROM THE LIDAR ITSELF.
  - Forward-axis assumption CONFIRMED at 1.1b (person-in-chair position_lidar x ~ +4.31 -> LiDAR +x
    forward).
  - Env-1 was taped from the LiDAR housing FRONT FACE; the housing-front-to-axis offset (= housing
    radius, Helios 32 diameter ~99-100 mm -> radius ~0.05 m, datasheet) is ADDED to each value so the
    GT is a distance from the LiDAR AXIS (its measurement origin). See the Env-1 range GT table.
  - Because env-1 is measured from the LiDAR directly, the old lens-to-plate "+0.123 m" forward
    offset DOES NOT APPLY to env-1 (that offset only converts a plate-front/camera tape into the
    LiDAR frame; env-1 used no such tape). +0.123 m is retired for env-1; it survives only as a
    fallback for any future measurement taken from the plate.
  - REFERENCE-POINT CAVEAT (important, recorded d25): GT is taped to the object's visible FRONT FACE;
    the arms report range_m to the CLUSTER CENTROID. For DEEP objects these differ by ~half the
    object's depth. The env-1 chair (cluster forward-extent ~0.94 m) shows this directly: taped front
    face 1.36 m vs fused centroid 1.76 m, a ~0.40 m gap that is a reference-point difference, NOT a
    sensor/tape error. Thin objects (monitors) and the person agree to a few cm because they have
    little depth. metrics.py MUST report range error PER OBJECT (so the chair offset is visible and
    explainable, not buried in an aggregate), and Limitations states the front-face-vs-centroid
    convention. (To confirm the half-depth explanation quantitatively at metrics time.)

- ENV-1 RANGE GT (decision d24, supersedes d10; measured d25): the d10 marker ranges (1.00 m chair /
  4.00 m blue chair) are SUPERSEDED. The d10 "1 m chair" was a perpendicular / misread value; the
  tan/brown high-back chair sits on the DIAGONAL at ~1.4-1.8 m true (Euclidean) range. ALL env-1
  ranges were measured fresh in the office d25, BLIND of the d16/fused numbers (anti-anchoring;
  cross-check done only AFTER entry). Env-1 is the COARSE range tier: uncertainty = the d25
  rig-reposition match (a few cm with the rigid plate + table/wall reference) PLUS the
  front-face-vs-centroid reference-point offset above. env-2 is the PRECISE tier (~2-3 cm).
  Limitations: env-1 range errors below the env-1 tier uncertainty are not interpretable.

- Matching rules: camera-only and fused detections match a GT instance at 2D IoU >= 0.5, one-to-one,
  greedy by descending IoU. LiDAR-only (no 2D box) matches by BEV gate: detection bearing inside the
  GT object's angular extent (GT 2D box through the intrinsics) AND range within +/- 0.75 m of the GT
  range where a tape range exists, else +/- 0.75 m of the fused range if fused localised it; if
  neither exists, that GT instance is NOT ASSESSABLE for LiDAR-only (counted separately, never a miss).
- GATE VALUE 0.75 m (RESOLVED): bracketed between the largest legitimate range offset for a correct
  detection (~+0.33 m centroid-vs-floor on the person-in-chair) and the smallest same-bearing object
  separation (~1 m). Safeguards: (a) d25 scene rule -- distinct env-2 objects on a shared bearing
  >= 1.5 m apart in range; (b) metrics.py reports LiDAR-only match counts at 0.50 / 0.75 / 1.00 m
  (pre-declared sensitivity, not tuning). Primary gate 0.75 m. NOTE: the chair's ~0.40 m
  front-face-vs-centroid offset sits inside the 0.75 m gate, so it does not flip the chair's
  LiDAR-only assessability, but it does inflate the chair's reported range error -- hence per-object
  reporting.
- Metrics per arm per environment: recall = matched GT / assessable GT; precision = matched detections
  / detections above the operating point; class correctness = correct-class matches / matches; range
  error vs GT_lidar_range (TAPE-derived only, never LiDAR-derived) -- median, IQR, RMSE, N per cell,
  AND per object. Range-error denominator for the fused arm = the source=="fused" SUBSET only.
  FUSED-RATE (count(fused) / count(all YOLO boxes)) reported per environment, broken down by the
  reason field (too_few_points / no_qualifying_cluster).
- Operating points (frozen, as published in the draft): YOLO conf=0.25; PointPillars score >= 0.30.
- Frame sample: env-1 (test2_marked_distances) = CANONICAL 3 frames 00100/00300/00500 (continuity with
  the qualitative chapter / d14); env-1 is the 12-instance, 4-object continuity ANCHOR. Env-2 carries
  the 200-300 budget: 18 frames across >= 3 rig poses (6 per pose). CenterPoint second LiDAR baseline:
  OUT (time box).

## 1.1b evidence -- LiDAR forward-axis check (fused_out/00300.json)

Person-in-chair entry: position_lidar = [4.31, 0.12, -0.43], range_m = 4.312. x ~ +4.31 with small
y -> LiDAR +x is the forward axis. (Full fused_out/00300.json dump retained in the repo / earlier
manifest revision.)
- 1.1b verdict: LiDAR +x is forward CONFIRMED.

## d13-bins integrity check
- `git status` shows the bins as `??` (untracked -> gitignored scratch).
- `ls` shows code/bag_to_bin/out/ bins dated 2026-05-28 09:12 (the d13/Week-2 build) UNTOUCHED.
- The earlier mislocated re-run wrote into the PARENT code/bag_to_bin/, not out/, so the d13 baseline
  was never overwritten. Conclusion: no loss; bins are deterministic/regenerable; baseline preserved.
- Parent-dir stray copies removed after relocation.

## Env-1 frame export (canonical 3: 00100/00300/00500), cv_bridge-free script
```
00100: dt=  6.85 ms
00300: dt=  7.35 ms
00500: dt=  7.14 ms
done: 3 frame(s) -> code/fusion/frames_out
- pair check (canonical 3):
    00100 png:OK bin:OK
    00300 png:OK bin:OK
    00500 png:OK bin:OK
```
Note: the earlier export crash was ROS-env numpy 2.2.6 vs numpy-1.x-compiled cv_bridge_boost; fixed
by the cv_bridge-free extract_frames.py (decodes the Image directly). ROS-env cv2 4.13.0 writes PNGs
fine under numpy 2.x. No package change.

## Annotation tool smoke test (frame 00300, annotated twice)
```
objects: A=4 B=4
  chair        best IoU vs B: 0.94 (B class: chair)
  person-in-chair best IoU vs B: 0.89 (B class: person-in-chair)
  right monitor best IoU vs B: 0.93 (B class: right monitor)
  left monitor best IoU vs B: 0.93 (B class: left monitor)
```
-> PASS (IoU 0.89-0.94, classes match; well above the 0.5 matching threshold).

## Env-1 annotation (boxes + classes; ranges filled d25)
- Object set (Victor's scope call): 4 objects/frame -- chair (tan/brown high-back, diagonal ~1.4-1.8 m),
  person-in-chair (~4 m doorway), left monitor, right monitor. Laptop and the far ~8 m doorway monitor
  deliberately NOT annotated: cannot be repositioned / tape-measured at d25, so no trustworthy range GT.
- 4 distinct range measurements feed all 12 instances (static scene).

## Env-1 range GT (reconstructed d25-office; supersedes d10; measured BLIND)
- Rig repositioned via the rigid LiDAR+camera plate against the table/wall reference, framing matched
  to 00300.png. Match quality not separately quantified (estimated within a few cm); env-1 treated as
  the COARSE tier regardless.
- Measured from the LiDAR housing FRONT FACE; +0.05 m housing-radius correction added to reach the
  LiDAR AXIS (Helios 32, diameter ~99-100 mm -> radius ~0.05 m). 3D. Lens-to-plate / +0.123 m NOT
  applied (measured from the LiDAR directly).
- Measured BLIND of fused numbers; fused values below are an AFTER-THE-FACT cross-check only.

| Object | Raw face (m) | +0.05 housing radius -> GT (m) | Fused centroid (cross-check) | Delta | Note |
|---|---|---|---|---|---|
| chair (tan/brown high-back) | 1.31 | 1.36 | 1.76 | 0.40 | front-face vs centroid; chair fwd-depth ~0.94 m -> ~half-depth offset, NOT an error; keep 1.36 |
| person-in-chair | 4.18 | 4.22* | 4.31 | 0.09 | *4.18+0.05=4.23, entered 4.22 (1 cm rounding, immaterial) |
| right monitor | 1.85 | 1.90 | 2.01 | 0.11 | thin object; agrees |
| left monitor | 2.25 | 2.30 | 2.35 | 0.05 | thin object; agrees |

- Same 4 values written into 00100/00300/00500 via set_ranges.py (static scene).
- CAVEAT carried to metrics/Limitations: GT = front face, arm range_m = cluster centroid; deep objects
  (chair) carry a known ~half-depth offset. Report range error per object.

### Annotation totals (after set_ranges.py)
```
frames=3 instances=12 occluded(excluded)=0 with_tape_range=12
per-class: {'chair': 3, 'person-in-chair': 3, 'right monitor': 3, 'left monitor': 3}
```

## Final state
- Env: ROS-env numpy 2.2.6 (left as-is); extract_frames cv_bridge-free; cv2 imwrite OK 4.13.0.
- d13-bins integrity: gitignored scratch; d13 baseline in out/ (2026-05-28) UNTOUCHED; no loss.
- Frozen definitions: corrected (camera arm no range; env-1 ranges reconstructed d25, d10 superseded;
  measured-from-LiDAR convention; front-face-vs-centroid caveat; canonical-3 frames).
- Env-1 export: 3/3 pairs OK.
- Tool smoke test: PASS (IoU 0.89-0.94).
- Env-1 annotation: 12 instances, 0 occluded; ranges filled d25, with_tape_range=12.
- Day 1 outcome: PASS -- cleared for d25 env-2 capture.
