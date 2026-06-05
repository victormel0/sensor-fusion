# Day 2 (d15) projection manifest -- 2026-06-03

**Goal:** LiDAR-to-image projection (calib.json extrinsic + intrinsics) verified by overlay on 00100/00300/00500.

**Extrinsic file:** calibration/calib_T_lidar_camera_2026_05_26.json
**Intrinsics (calib.json):** fx=335.13 fy=359.35 cx=486.26 cy=291.70 on 960x600

## Transform direction
- Stored T_lidar_camera interpreted as: **camera-pose-in-LiDAR -> project via the inverse** (`--direction campose`, `p_cam = R^T (p_lidar - t)`). This is Koide's documented convention for T_lidar_camera.
- Source of the decision: **overlay empirical** (campose lands points on the objects with correct depth ordering and no mirror/flip; lidar2cam was the rejected alternative). Consistent with Koide docs.
- Cross-checks: parsed t=(0.1228, -0.0147, -0.1599) matches the known (+0.123, -0.015, -0.160); intrinsics auto-loaded from calib.json (fx=335.1257...) match camera_info K to 5 decimals (calib.json is self-contained).
## Overlay -- direction check (frame 00300, both interpretations)
- transform: t=(0.1228, -0.0147, -0.1599)  quat=(-0.4969, 0.5101, -0.5006, 0.4923)
  sanity: t should read ~ (+0.123, -0.015, -0.160); if not, --quat/--trans were needed
- intrinsics: fx=335.125732421875 fy=359.345703125 cx=486.26446533203125 cy=291.699951171875
- [lidar2cam] total=53651 in_front=23061 in_image=9090 -> docs/screenshots/d15_overlay_00300_lidar2cam.png
- [campose] total=53651 in_front=24653 in_image=13750 -> docs/screenshots/d15_overlay_00300_campose.png
- compare the two overlays; keep the direction whose points land on the objects, then re-run with --direction <that> to write the canonical d15_overlay_<frame>.png
## Overlay -- canonical (chosen direction: campose)
- transform: t=(0.1228, -0.0147, -0.1599)  quat=(-0.4969, 0.5101, -0.5006, 0.4923)
  sanity: t should read ~ (+0.123, -0.015, -0.160); if not, --quat/--trans were needed
- intrinsics: fx=335.125732421875 fy=359.345703125 cx=486.26446533203125 cy=291.699951171875
- [campose] total=53643 in_front=24624 in_image=13758 -> docs/screenshots/d15_overlay_00100.png
- transform: t=(0.1228, -0.0147, -0.1599)  quat=(-0.4969, 0.5101, -0.5006, 0.4923)
  sanity: t should read ~ (+0.123, -0.015, -0.160); if not, --quat/--trans were needed
- intrinsics: fx=335.125732421875 fy=359.345703125 cx=486.26446533203125 cy=291.699951171875
- [campose] total=53651 in_front=24653 in_image=13750 -> docs/screenshots/d15_overlay_00300.png
- transform: t=(0.1228, -0.0147, -0.1599)  quat=(-0.4969, 0.5101, -0.5006, 0.4923)
  sanity: t should read ~ (+0.123, -0.015, -0.160); if not, --quat/--trans were needed
- intrinsics: fx=335.125732421875 fy=359.345703125 cx=486.26446533203125 cy=291.699951171875
- [campose] total=53519 in_front=24511 in_image=13755 -> docs/screenshots/d15_overlay_00500.png

## Final state (18:39:57)
- Overlay verdict (points on right objects?): PASS -- floor arcs on the floor, depth jump at the doorway, near points on the tan chair, no mirror/flip; campose only.
- Transform direction confirmed: campose (camera-pose-in-LiDAR; project via inverse). lidar2cam rejected.
- Per-frame in_image point counts (campose): 00100 = 13758, 00300 = 13750, 00500 = 13755 (of ~53.6k total each).
- Observations for Day 4: the near-field foreground (~1 m, where LiDAR-only hallucinated trailer/truck) shows floor returns, no object -> supports the hallucination reading. The doorway blob carries the person-in-blue-chair + far-room returns at ~4-6 m. The 100 cm black chair @1 m is still not clearly resolvable in the overlay (likely below/outside the monocular view); confirm or drop in Day 4.
- Day 2 outcome: PASS = cleared to build fusion.
