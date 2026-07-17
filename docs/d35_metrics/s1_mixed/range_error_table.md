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
