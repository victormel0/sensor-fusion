# Fused-rate (fraction of YOLO boxes that earned a LiDAR range)

| env | all boxes | fused | fused-rate | camera_only | too_few_points | no_qualifying_cluster |
|---|---|---|---|---|---|---|
| env1 | 31 | 31 | 1.000 | 0 | 0 | 0 |
| env2 | 45 | 45 | 1.000 | 0 | 0 | 0 |

Expect ~100% on dense scenes, lower where the LiDAR is sparse = the reportable result.
