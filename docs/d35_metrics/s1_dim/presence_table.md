# Presence (recall / precision / class-correctness)

camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| unknown | camera_only | 0.5 | 0.938 | 1.0 | 15 | 1 | 30 |
| unknown | fused | 0.5 | 0.938 | 1.0 | 15 | 1 | 30 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious classes are EXPECTED. Reported via the gate table.
