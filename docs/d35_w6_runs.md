# Day (d35) Tier-2 evaluation -- 2026-07-06

**Scope:** 3 arms per condition -> per-condition metrics -> figures -> qual panels; cross-condition summary; Tier-2 failure cases.
**Settings identical to d26:** conf=0.25 / score>=0.30 / iou 0.50 / campose / gates 0.5,0.75,1.0.

- transform: t=(0.1228, -0.0147, -0.1599)  quat=(-0.4969, 0.5101, -0.5006, 0.4923)
  sanity: t should read ~ (+0.123, -0.015, -0.160); if not, --quat/--trans were needed
- intrinsics: fx=335.125732421875 fy=359.345703125 cx=486.26446533203125 cy=291.699951171875
- [campose] total=50679 in_front=25726 in_image=13494 -> docs/screenshots/d35_overlay.png

## 5.3 Per-condition metrics

### s1_bright
self-check:
projection [project_lidar (exact fused-arm projection)] self-check: fused centroids inside box_xyxy = 100% (OK)
# Presence (recall / precision / class-correctness)

camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| unknown | camera_only | 0.667 | 1.0 | 1.0 | 20 | 0 | 30 |
| unknown | fused | 0.667 | 1.0 | 1.0 | 20 | 0 | 30 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious classes are EXPECTED. Reported via the gate table.

# Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.

Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only has NO range. Per env and per object (class).

| env | arm | object | N | median | IQR | RMSE |
|---|---|---|---|---|---|---|
| unknown | fused | chair | 5 | 0.481 | 0.0 | 0.481 |
| unknown | fused | keyboard | 5 | 0.084 | 0.001 | 0.085 |
| unknown | fused | laptop | 5 | 0.141 | 0.007 | 0.138 |
| unknown | fused | tv | 5 | 0.269 | 0.0 | 0.269 |

## per-env aggregate

| env | arm | N | median | IQR | RMSE |
|---|---|---|---|---|---|
| unknown | fused | 20 | 0.207 | 0.184 | 0.287 |

FOOTNOTES:
- env1 GT tier: ~10 cm coarse (reconstructed d25; d10 superseded; values are 3D but ~= horizontal for these near-LiDAR-height objects). Errors below the tier are not interpretable.
- env2 GT tier: ~10 cm medium (range_m is HORIZONTAL; GT should be the floor/horizontal measure; direct-slant over-reads by the height term; chairs also carry the centroid offset). Errors below the tier are not interpretable.
- range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset (env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.

# Fused-rate (fraction of YOLO boxes that earned a LiDAR range)

| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |
|---|---|---|---|---|---|---|
| unknown | 20 | 20 | 1.000 | 0 | 0 | 0 |

Expect ~100% on dense scenes, lower where the LiDAR is sparse = the reportable result.

### s1_dim
self-check:
projection [project_lidar (exact fused-arm projection)] self-check: fused centroids inside box_xyxy = 100% (OK)
# Presence (recall / precision / class-correctness)

camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| unknown | camera_only | 0.5 | 0.938 | 1.0 | 15 | 1 | 30 |
| unknown | fused | 0.5 | 0.938 | 1.0 | 15 | 1 | 30 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious classes are EXPECTED. Reported via the gate table.

# Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.

Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only has NO range. Per env and per object (class).

| env | arm | object | N | median | IQR | RMSE |
|---|---|---|---|---|---|---|
| unknown | fused | chair | 5 | 0.485 | 0.002 | 0.484 |
| unknown | fused | laptop | 5 | -0.463 | 0.003 | 0.419 |
| unknown | fused | tv | 5 | 0.267 | 0.001 | 0.267 |

## per-env aggregate

| env | arm | N | median | IQR | RMSE |
|---|---|---|---|---|---|
| unknown | fused | 15 | 0.267 | 0.942 | 0.4 |

FOOTNOTES:
- env1 GT tier: ~10 cm coarse (reconstructed d25; d10 superseded; values are 3D but ~= horizontal for these near-LiDAR-height objects). Errors below the tier are not interpretable.
- env2 GT tier: ~10 cm medium (range_m is HORIZONTAL; GT should be the floor/horizontal measure; direct-slant over-reads by the height term; chairs also carry the centroid offset). Errors below the tier are not interpretable.
- range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset (env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.

# Fused-rate (fraction of YOLO boxes that earned a LiDAR range)

| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |
|---|---|---|---|---|---|---|
| unknown | 16 | 16 | 1.000 | 0 | 0 | 0 |

Expect ~100% on dense scenes, lower where the LiDAR is sparse = the reportable result.

### s1_mixed
self-check:
projection [project_lidar (exact fused-arm projection)] self-check: fused centroids inside box_xyxy = 100% (OK)
# Presence (recall / precision / class-correctness)

camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| unknown | camera_only | 0.5 | 1.0 | 1.0 | 15 | 0 | 30 |
| unknown | fused | 0.5 | 1.0 | 1.0 | 15 | 0 | 30 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious classes are EXPECTED. Reported via the gate table.

# Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.

Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only has NO range. Per env and per object (class).

| env | arm | object | N | median | IQR | RMSE |
|---|---|---|---|---|---|---|
| unknown | fused | chair | 5 | 0.478 | 0.001 | 0.478 |
| unknown | fused | keyboard | 5 | 0.101 | 0.007 | 0.103 |
| unknown | fused | tv | 5 | 0.268 | 0.0 | 0.268 |

## per-env aggregate

| env | arm | N | median | IQR | RMSE |
|---|---|---|---|---|---|
| unknown | fused | 15 | 0.268 | 0.372 | 0.322 |

FOOTNOTES:
- env1 GT tier: ~10 cm coarse (reconstructed d25; d10 superseded; values are 3D but ~= horizontal for these near-LiDAR-height objects). Errors below the tier are not interpretable.
- env2 GT tier: ~10 cm medium (range_m is HORIZONTAL; GT should be the floor/horizontal measure; direct-slant over-reads by the height term; chairs also carry the centroid offset). Errors below the tier are not interpretable.
- range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset (env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.

# Fused-rate (fraction of YOLO boxes that earned a LiDAR range)

| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |
|---|---|---|---|---|---|---|
| unknown | 15 | 15 | 1.000 | 0 | 0 | 0 |

Expect ~100% on dense scenes, lower where the LiDAR is sparse = the reportable result.

### s2_bright
self-check:
projection [project_lidar (exact fused-arm projection)] self-check: fused centroids inside box_xyxy = 100% (OK)
# Presence (recall / precision / class-correctness)

camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| unknown | camera_only | 0.857 | 0.75 | 0.833 | 30 | 10 | 35 |
| unknown | fused | 0.857 | 0.75 | 0.833 | 30 | 10 | 35 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious classes are EXPECTED. Reported via the gate table.

# Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.

Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only has NO range. Per env and per object (class).

| env | arm | object | N | median | IQR | RMSE |
|---|---|---|---|---|---|---|
| unknown | fused | bottle | 5 | 0.217 | 0.003 | 0.217 |
| unknown | fused | chair | 10 | 0.47 | 0.279 | 0.491 |
| unknown | fused | potted plant | 5 | -5.611 | 0.001 | 5.611 |
| unknown | fused | trash bin | 5 | 0.135 | 0.002 | 0.126 |
| unknown | fused | tv | 5 | 0.076 | 0.0 | 0.076 |

## per-env aggregate

| env | arm | N | median | IQR | RMSE |
|---|---|---|---|---|---|
| unknown | fused | 30 | 0.175 | 0.252 | 2.311 |

FOOTNOTES:
- env1 GT tier: ~10 cm coarse (reconstructed d25; d10 superseded; values are 3D but ~= horizontal for these near-LiDAR-height objects). Errors below the tier are not interpretable.
- env2 GT tier: ~10 cm medium (range_m is HORIZONTAL; GT should be the floor/horizontal measure; direct-slant over-reads by the height term; chairs also carry the centroid offset). Errors below the tier are not interpretable.
- range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset (env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.

# Fused-rate (fraction of YOLO boxes that earned a LiDAR range)

| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |
|---|---|---|---|---|---|---|
| unknown | 40 | 40 | 1.000 | 0 | 0 | 0 |

Expect ~100% on dense scenes, lower where the LiDAR is sparse = the reportable result.

### s2_dim
self-check:
projection [project_lidar (exact fused-arm projection)] self-check: fused centroids inside box_xyxy = 100% (OK)
# Presence (recall / precision / class-correctness)

camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| unknown | camera_only | 0.857 | 0.75 | 0.833 | 30 | 10 | 35 |
| unknown | fused | 0.857 | 0.75 | 0.833 | 30 | 10 | 35 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious classes are EXPECTED. Reported via the gate table.

# Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.

Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only has NO range. Per env and per object (class).

| env | arm | object | N | median | IQR | RMSE |
|---|---|---|---|---|---|---|
| unknown | fused | bottle | 5 | 0.211 | 0.006 | 0.212 |
| unknown | fused | chair | 10 | 0.452 | 0.318 | 0.48 |
| unknown | fused | potted plant | 5 | -5.612 | 0.003 | 5.613 |
| unknown | fused | trash bin | 5 | 0.139 | 0.001 | 0.139 |
| unknown | fused | tv | 5 | 0.074 | 0.001 | 0.074 |

## per-env aggregate

| env | arm | N | median | IQR | RMSE |
|---|---|---|---|---|---|
| unknown | fused | 30 | 0.173 | 0.217 | 2.311 |

FOOTNOTES:
- env1 GT tier: ~10 cm coarse (reconstructed d25; d10 superseded; values are 3D but ~= horizontal for these near-LiDAR-height objects). Errors below the tier are not interpretable.
- env2 GT tier: ~10 cm medium (range_m is HORIZONTAL; GT should be the floor/horizontal measure; direct-slant over-reads by the height term; chairs also carry the centroid offset). Errors below the tier are not interpretable.
- range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset (env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.

# Fused-rate (fraction of YOLO boxes that earned a LiDAR range)

| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |
|---|---|---|---|---|---|---|
| unknown | 40 | 40 | 1.000 | 0 | 0 | 0 |

Expect ~100% on dense scenes, lower where the LiDAR is sparse = the reportable result.

### s2_mixed
self-check:
projection [project_lidar (exact fused-arm projection)] self-check: fused centroids inside box_xyxy = 100% (OK)
# Presence (recall / precision / class-correctness)

camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| unknown | camera_only | 0.875 | 0.854 | 0.857 | 35 | 6 | 40 |
| unknown | fused | 0.875 | 0.854 | 0.857 | 35 | 6 | 40 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious classes are EXPECTED. Reported via the gate table.

# Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.

Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only has NO range. Per env and per object (class).

| env | arm | object | N | median | IQR | RMSE |
|---|---|---|---|---|---|---|
| unknown | fused | bottle | 5 | 0.209 | 0.004 | 0.21 |
| unknown | fused | chair | 10 | 0.458 | 0.305 | 0.483 |
| unknown | fused | potted plant | 10 | -2.743 | 5.743 | 3.971 |
| unknown | fused | trash bin | 5 | 0.137 | 0.001 | 0.137 |
| unknown | fused | tv | 5 | 0.077 | 0.002 | 0.078 |

## per-env aggregate

| env | arm | N | median | IQR | RMSE |
|---|---|---|---|---|---|
| unknown | fused | 35 | 0.137 | 0.222 | 2.141 |

FOOTNOTES:
- env1 GT tier: ~10 cm coarse (reconstructed d25; d10 superseded; values are 3D but ~= horizontal for these near-LiDAR-height objects). Errors below the tier are not interpretable.
- env2 GT tier: ~10 cm medium (range_m is HORIZONTAL; GT should be the floor/horizontal measure; direct-slant over-reads by the height term; chairs also carry the centroid offset). Errors below the tier are not interpretable.
- range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset (env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.

# Fused-rate (fraction of YOLO boxes that earned a LiDAR range)

| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |
|---|---|---|---|---|---|---|
| unknown | 41 | 41 | 1.000 | 0 | 0 | 0 |

Expect ~100% on dense scenes, lower where the LiDAR is sparse = the reportable result.


## 5.4 Cross-condition summary (INDICATIVE, small N; near-object range EXCLUDES the far plant)

| condition | recall | precision | class_acc | near range med (m) | far plant signed err (m) | fused-rate |
|---|---|---|---|---|---|---|
| s1_bright | 0.667 | 1.00 | 1.00 | tv +0.27, laptop +0.14, keyboard +0.08, chair +0.48* | n/a (no far plant in s1) | 1.000 |
| s1_dim    | 0.500 | 0.94 | 1.00 | tv +0.27, laptop -0.46, chair +0.49* | n/a | 1.000 |
| s1_mixed  | 0.500 | 1.00 | 1.00 | tv +0.27, keyboard +0.10, chair +0.48* | n/a | 1.000 |
| s2_bright | 0.857 | 0.75 | 0.83 | tv +0.08, trash +0.14, bottle +0.22, chair +0.47* | -5.61 (-> ~2.22 m) | 1.000 |
| s2_dim    | 0.857 | 0.75 | 0.83 | tv +0.07, trash +0.14, bottle +0.21, chair +0.45* | -5.61 (-> ~2.22 m) | 1.000 |
| s2_mixed  | 0.875 | 0.85 | 0.86 | tv +0.08, trash +0.14, bottle +0.21, chair +0.46* | -2.74 (N=10, pools window+far; split first) | 1.000 |

*chair = front-face-vs-centroid reference offset, NOT a lighting effect (same as env1/env2).
Fused aggregate median | RMSE per condition: s1_bright 0.207|0.287, s1_dim 0.267|0.400,
s1_mixed 0.268|0.322, s2_bright 0.175|2.311, s2_dim 0.173|2.311, s2_mixed 0.137|2.141 (s2 RMSE
dominated by the far plant). All transcribed from docs/d35_w6_runs.md.

## 5.4 Tier-2 failure cases (synthesised with d32 in the thesis)
- Far plant (F1 probe, 7.83 m) mislocalised by fusion to ~2.2 m in ALL s2 conditions
  (signed median approx -5.61 m bright/dim; s2_mixed row pools window+far plant, split before quoting).
  Mechanism (FLAGGED, not fully verified): point sparsity at 7-8 m -> degenerate ~13-14 pt cluster ->
  association collapses onto a nearer surface in the 2D box. NEW failure vs env-1/env-2: LiDAR-side
  (fused detection with bad range), not a camera-side miss. Report separately (inflates s2 RMSE to ~2.3 m).
- Low-light effect on NEAR objects: small. Near-object fused range medians move only ~cm across
  bright/dim/mixed (tv +0.07..+0.27, trash +0.135..+0.139, bottle +0.21). Presence recall:
  s1 0.667 (bright) vs 0.50 (dim/mixed); s2 0.857 (bright/dim) vs 0.875 (mixed). Camera-side, small.
- Backlit / mixed: no extra NEAR-object range degradation; the sun-noise LiDAR blob (approx 4.4% s1,
  2.4% s2 of points at object height, blinds-open only) is filtered by DBSCAN for the fused arm but
  triggers a phantom construction_vehicle in the LiDAR-only arm (s1_mixed ~8.5 m, s2_mixed ~6 m).
- LiDAR-only: ~0 above score 0.30 in the 4 non-sun conditions (reproduces env2's 0/0/0 domain gap);
  recall ~0 partly by VOCABULARY (nuScenes names never map to indoor GT via canon()).
- Range stability under lighting (fused aggregate median | RMSE): s1_bright 0.207|0.287,
  s1_dim 0.267|0.400, s1_mixed 0.268|0.322; s2_bright 0.175|2.311, s2_dim 0.173|2.311,
  s2_mixed 0.137|2.141. s2 RMSE dominated by the far plant; near-object medians are stable.
  All values transcribed from docs/d35_w6_runs.md; verify against per_match.csv before final quote.

---

# d35 DIGEST + POLISH (added 2026-07-07)

Self-check = 100% (fused centroids inside box_xyxy) in every condition, so the extrinsic/projection is
sound. Both arms ran on all 30 frames. The per-condition tables above are the raw result; this section
is the digest.

## Headline (fused arm, the substantive result)

Near-field fused range tracks the tape GT and is STABLE across lighting:
- tv +0.07..+0.27 m; trash bin +0.135..+0.139 m; bottle +0.209..+0.217 m (at/near the ~10 cm GT tier).
- chair +0.45..+0.49 m in every condition = the KNOWN front-face-vs-centroid reference offset (same as
  env1/env2), NOT a lighting effect.
- Presence: s1 recall 0.50-0.667, s2 recall 0.857-0.875; precision 0.75-1.0; class-acc 0.83-1.0.
  camera_only == fused by construction (shared YOLO set). Fused-rate = 1.000 in ALL conditions.
- Lighting effect on the NEAR objects is small (near-object medians move only ~cm across bright/dim/mixed).
  FLAGGED: this "roughly lighting-invariant" reading rests on the manifest medians; verify per-object in
  per_match.csv before making a strong invariance claim.

## F1 far-plant failure (the designed probe) -- report SEPARATELY

Far plant (taped 7.83 m) is grossly mislocalised by the fusion:
- s2_bright: signed median -5.611 m -> fused approx 2.22 m
- s2_dim:    signed median -5.612 m -> fused approx 2.22 m
- s2_mixed:  the "potted plant" row is N=10 (pools window plant 2.65 m + far plant 7.83 m, because the
  window plant is occluded=false ONLY in mixed), median -2.743 m, IQR 5.743 -> split before quoting.

Likely mechanism (FLAGGED, NOT fully verified): at 7-8 m the plant returns too few LiDAR points to form
a valid cluster (raw fusion showed a degenerate ~13-14 point cluster, extent ~0.02 x 0.10 x 0.00), so the
association collapses onto a nearer surface inside the 2D box and the range drops to ~2.2 m. This is the
F1 point-sparsity-at-range mechanism. A table edge partly occluding the returns is a POSSIBLE minor
contributor but does NOT explain a ~5.6 m collapse. Confirming which nearer cluster is grabbed needs
per_match.csv or the fusion viz for that box (not done here). This one object inflates the s2 aggregate
RMSE to ~2.3 m, so do NOT report a pooled s2 RMSE as headline.

## LiDAR-only arm

Consistent with env2 (d26): PointPillars (nuScenes) is out-of-domain indoors and fires ~0 above score 0.30
in the four non-sun conditions. In the two blinds-open "mixed" conditions the sun-noise LiDAR blob crosses
threshold and the model hallucinates ONE construction_vehicle at large negative y (s1_mixed ~8.5 m,
s2_mixed ~6 m), score approximately 0.30-0.62. Two framing notes: recall ~0 is partly a VOCABULARY effect
(nuScenes class names never map to the indoor GT via canon()), not only a detection failure; and this
strengthens the fusion argument (LiDAR-only both misses indoor objects and, under sun, invents one).
Percentages of anomalous points are approximate (one-off script).

## Cross-condition summary table (near-object range EXCLUDES the far plant)

| condition | recall | precision | class_acc | near range med (m) | far plant signed err (m) | fused-rate |
|---|---|---|---|---|---|---|
| s1_bright | 0.667 | 1.00 | 1.00 | tv +0.27, laptop +0.14, keyboard +0.08, chair +0.48* | n/a (no far plant in s1) | 1.000 |
| s1_dim    | 0.500 | 0.94 | 1.00 | tv +0.27, laptop -0.46, chair +0.49* | n/a | 1.000 |
| s1_mixed  | 0.500 | 1.00 | 1.00 | tv +0.27, keyboard +0.10, chair +0.48* | n/a | 1.000 |
| s2_bright | 0.857 | 0.75 | 0.83 | tv +0.08, trash +0.14, bottle +0.22, chair +0.47* | -5.61 (-> ~2.22 m) | 1.000 |
| s2_dim    | 0.857 | 0.75 | 0.83 | tv +0.07, trash +0.14, bottle +0.21, chair +0.45* | -5.61 (-> ~2.22 m) | 1.000 |
| s2_mixed  | 0.875 | 0.85 | 0.86 | tv +0.08, trash +0.14, bottle +0.21, chair +0.46* | -2.74 (N=10, pools window+far; split first) | 1.000 |

*chair = front-face-vs-centroid reference offset, NOT a lighting effect. Fused aggregate median | RMSE:
s1_bright 0.207|0.287, s1_dim 0.267|0.400, s1_mixed 0.268|0.322, s2_bright 0.175|2.311, s2_dim 0.173|2.311,
s2_mixed 0.137|2.141 (s2 RMSE dominated by the far plant). All transcribed from the tables above; verify
against per_match.csv before final quoting.

## Qualitative panels (5.4) -- REVISED to Option 2a (2026-07-07)

Panel selection changed from the first 4-panel success/fail set to a CONDITION ILLUSTRATION of one
scene. Reason: the first set (success_s1_bright, fail_s1_dim_lowlight, fail_s2_mixed_backlit,
success_s2_bright) was flawed: (a) the s2 "success" and s2 "fail" panels were the SAME frame (s2,
00300) under different lighting, so labelling one success and one fail is not meaningful, since
geometry is locked across a scene's lighting bags and every s2 frame shows the same objects fused the
same way; and (b) the s2 "success" panel visibly mislabels the trash bin as potted plant and the s1
"success" panel misses the cup, so "success" was not an accurate label.

REVISED (Option 2a): three panels of scene s2 across bright/dim/mixed, frame 00300, condition-named
(no success/fail): docs/screenshots/d35_fig_qual_s2_{bright,dim,mixed}.png. The near-identical panels
ARE the evidence for range-stability across lighting. Two behaviours appear in ALL three conditions
(so they are NOT lighting-induced, which is a useful point for the caption): the trash bin
misclassified as potted plant (camera-side vocabulary error), and the far plant fused at ~2.2 m
against its 7.83 m tape (F1 point-sparsity collapse). The four old PNGs should be deleted from
docs/screenshots/. Re-render runs on the box; verify each panel before thesis use. (Panel choice and
caption framing are partly the writing chat's territory; this records the selection and the reason.)

## SUGGESTIONS FOR THE WRITING CHAT (env-3 integration; flagged as proposals, not prose)

These come from reading the four thesis chapters (03_methodology, 04_experiments, 05_results,
06_discussion). Context: those chapters currently describe ONLY env-1 and env-2 ("two environments");
the env-3 lighting study (this week) is NOT yet in them. T2.5 is where it gets integrated. The approach in
the .tex and the env-3 work are consistent; these notes are what env-3 adds or changes.

1. NEW failure mode, LiDAR-side. The current discussion (06, sec:disc-fusion) says "the design has a cost,
   and it is camera-side." Env-3's F1 far-plant collapse (7.83 m -> ~2.2 m) is a DIFFERENT cost: a fused
   detection that fired but localised badly due to LiDAR point sparsity at range. This is not a camera-side
   miss. It slightly complicates the clean "all failures are camera-side" story and is worth stating
   carefully. I believe it strengthens the thesis (a second, characterised failure mode), but that is a
   judgement for the writing chat.

2. Two factual claims in the current text interact with env-3:
   - Fused-rate 1.000 / "fusion localised every detection" (05 sec:res-fusedrate, 06): still holds in env-3
     (fused-rate 1.000 everywhere). BUT the far plant shows that "fused" does not mean "localised well" --
     it fused via a degenerate cluster and still collapsed in range. The honest framing is that the failure
     moved from the fused-rate column to the range-error column.
   - The fused-rate hypothesis ("a sparser scene would lower the rate; it did not") could finally be tested
     by env-3's far plant (the sparsest object). It still fused (>=10 pts), so the rate stayed 1.000 and the
     failure appeared as range error, not a camera-only fallback. A subtle, honest result.

3. Env-3 partly fills a limitation the thesis already names. 06 (sec:disc-fusion) says env-2's daylight pose
   was "a single uncontrolled lighting variation rather than the controlled condition study that
   cafuser2025 would require." Env-3 IS a more controlled lighting study (bright/dim/mixed at fixed
   geometry). Surfacing "we named this gap, then partly filled it" is a strong move. (cafuser2025 is a
   citation already present in the .tex; I did not verify the reference itself.)

4. The sun-induced LiDAR phantom (construction_vehicle in the blinds-open conditions) is a concrete NEW
   instance of the same domain-gap point the discussion already makes with the near-field vehicle
   hallucination, and it ties to the existing cafuser2025 condition-aware thread.

5. Keep the small-N framing consistent. 04 is careful that env-1/env-2 frames are pseudo-replicates, not
   independent samples. Env-3 has the same property (5 near-identical static frames per condition, tiny
   within-cell variance by construction). Apply the same honest denominator; do not let 30 frames read as
   30 independent samples.

CAVEAT on these suggestions (rule 1): analysing/suggesting on thesis content borders on the writing chat's
territory per the working contract. These are flagged proposals for that chat to weigh, not instructions,
and not prose. I did not re-verify the .tex's own numbers (calibration NID cost, latency figures,
env-1/env-2 range tables); I have no independent source for those and did not recompute them.

