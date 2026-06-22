# Presence (recall / precision / class-correctness)

camera_only and fused are IDENTICAL by construction (same YOLO set); expected.

| env | arm | recall | precision | class_acc | TP | FP | GT(assessable) |
|---|---|---|---|---|---|---|---|
| env1 | camera_only | 1.0 | 0.387 | 1.0 | 12 | 19 | 12 |
| env1 | fused | 1.0 | 0.387 | 1.0 | 12 | 19 | 12 |
| env2 | camera_only | 0.302 | 0.644 | 0.828 | 29 | 16 | 96 |
| env2 | fused | 0.302 | 0.644 | 0.828 | 29 | 16 | 96 |

LiDAR-only presence: PointPillars is nuScenes; indoor furniture is out-of-domain, so misses / spurious classes are EXPECTED. Reported via the gate table.
