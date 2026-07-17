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
