# Range error vs TAPE GT (signed = det - GT; m). range_m is HORIZONTAL.

Fused denominator = source=='fused' subset; LiDAR-only where it fires; camera-only has NO range. Per env and per object (class).

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

## per-env aggregate

| env | arm | N | median | IQR | RMSE |
|---|---|---|---|---|---|
| env1 | fused | 12 | 0.11 | 0.191 | 0.225 |
| env1 | lidar_only | 6 | 0.0 | 0.442 | 0.248 |
| env2 | fused | 29 | 0.259 | 0.194 | 0.332 |

FOOTNOTES:
- env1 GT tier: ~10 cm coarse (reconstructed d25; d10 superseded; values are 3D but ~= horizontal for these near-LiDAR-height objects). Errors below the tier are not interpretable.
- env2 GT tier: ~10 cm medium (range_m is HORIZONTAL; GT should be the floor/horizontal measure; direct-slant over-reads by the height term; chairs also carry the centroid offset). Errors below the tier are not interpretable.
- range_m is HORIZONTAL (hypot x,y). GT is to the object FRONT FACE; range_m is to the cluster CENTROID, so DEEP objects (chairs) carry a ~half-depth horizontal offset (env-1 chair: taped 1.36 vs fused 1.76) -- reference-point difference, not error.
