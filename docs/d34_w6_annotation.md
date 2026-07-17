# Day (d34) Tier-2 annotation -- 2026-07-06 -- STATUS: export + annotation + GT verification DONE

**Scope:** export 5 frames + 5 bins per condition (30 + 30 total); annotate 2D GT (boxes + class +
occluded + range_m_tape) in the d24 schema; verify. Room = the meeting room (env-3 informally).
Feeds d35 (metrics.py compares this GT vs the fused and LiDAR-only arms).

## Frame selection

Indices 100/200/300/400/500 per bag (all six bags have >= 626 LiDAR frames, so these exist in every
bag). Exported via extract_frames.py (PNG + JSON pairing metadata) and bag_to_bin.py (5-channel bins).
Bins written to per-condition dirs `code/bag_to_bin/out_w6/<cond>/`, leaving the legacy
`code/bag_to_bin/out/` (d20/d25 parity bins) untouched. Verified PNG=5 BIN=5 for all six conditions.

Slop note: extract_frames pairs each LiDAR frame to the nearest image by header stamp (+-50 ms). No
`[WARN dt over slop]` appeared on the sampled indices, including in w6_s2_dim (the bag with a
~420 ms LiDAR gap during capture); the sampled frames avoided that window. The s1_mixed / s2_mixed
bins show anomalous y-range (down to -39.6 m / -11.4 m) from direct-sun LiDAR returns in the
blinds-open condition; see the sun-anomaly section below.

## Sun-noise anomaly (blinds-open "mixed" conditions) -- investigated, does NOT corrupt the GT

The two mixed bags (blinds open) contain spurious LiDAR returns at object height:
approximately 4.42% of points in s1_mixed frame 00100 (2220 pts, |y|>5 m, reaching y=-39.6 m) and
approximately 2.43% in s2_mixed (1308 pts, reaching y=-11.4 m). The bright/dim bags are effectively
clean (s2_bright 0 such points). Hypothesis: direct sunlight through the open blinds producing
spurious/edge returns (unverified physical mechanism, but the pattern is confined to the blinds-open
condition). Percentages are from a one-off script and are approximate.

Impact check (frustum_fuse.py smoke-test on s2_mixed frame 00100, real calib + rotation): all real
markers fused with sensible ranges tracking the tape d_h (bottle 1.39 vs 1.18, chair1 2.10 vs 1.79,
chair2 4.41 vs 3.80, tv 5.99 vs 5.91, window plant 2.78 vs 2.65). The DBSCAN + per-cluster median in
associate_box filters the sparse sun outliers, so no object range was corrupted. The fused range
runs consistently a little longer than the tape d_h, which is expected: fused range is hypot(x,y) of
the 3D centroid (full object depth), while d_h is horizontal plumb-to-front-face; the exact
tape-to-range conversion lives in metrics.py and defines the d35 tolerance, so these deltas are
"consistent in sign and magnitude", NOT "passed" (d35 decides). Conclusion: the sun noise is a real
property of the mixed data and likely a legitimate finding about LiDAR under direct sun, but it does
NOT contaminate the GT; annotation proceeded on all six conditions.

A separate observation from the same smoke-test: YOLO classified the trash bin as "potted plant".
That is exactly an F4 out-of-vocabulary / misclassification event; it does NOT change the GT (the bin
is annotated as trash bin with its tape d_h). d35 will score it as a class mismatch against the GT.

## Export log (verbatim)

```
[INFO] [1783350544.612401960] [rosbag2_storage]: Opened database 'recordings/w6_s1_bright/w6_s1_bright_0.db3' for READ_ONLY.
[INFO] [1783350547.266677075] [rosbag2_storage]: Opened database 'recordings/w6_s1_bright/w6_s1_bright_0.db3' for READ_ONLY.
00100: dt= 10.00 ms
00200: dt=  9.09 ms
00300: dt=  9.34 ms
00400: dt=  9.31 ms
00500: dt=  9.20 ms
done: 5 frame(s) -> code/eval/frames_w6/s1_bright
[frame 00300]  50679 pts -> w6_s1_bright_00300.bin  x[  -5.2,  +4.1] y[  -1.9,  +9.8] z[  -1.1,  +2.1] i[1.0,255.0]
[frame 00400]  50660 pts -> w6_s1_bright_00400.bin  x[  -5.2,  +4.1] y[  -1.9,  +9.8] z[  -1.1,  +2.0] i[1.0,255.0]
[frame 00500]  50683 pts -> w6_s1_bright_00500.bin  x[  -5.2,  +4.1] y[  -1.9,  +9.8] z[  -1.1,  +2.0] i[1.0,255.0]
------------------------------------------------------------------------
Done. Wrote 5 .bin file(s) to /home/user/Documents/workspace/sensor-fusion/code/bag_to_bin/out_w6/s1_bright

Format written: N x 5 float32 little-endian, columns [x, y, z, intensity, time_offset].
Feed these to OpenPCDet from inside venv_openpcdet (§6.2).
[INFO] [1783350585.759719655] [rosbag2_storage]: Opened database 'recordings/w6_s1_dim/w6_s1_dim_0.db3' for READ_ONLY.
[INFO] [1783350588.536616260] [rosbag2_storage]: Opened database 'recordings/w6_s1_dim/w6_s1_dim_0.db3' for READ_ONLY.
00100: dt=  8.28 ms
00200: dt=  8.60 ms
00300: dt=  8.62 ms
00400: dt=  8.83 ms
00500: dt=  8.94 ms
done: 5 frame(s) -> code/eval/frames_w6/s1_dim
[frame 00300]  50640 pts -> w6_s1_dim_00300.bin  x[  -5.2,  +4.1] y[  -1.9,  +9.8] z[  -1.1,  +2.0] i[1.0,255.0]
[frame 00400]  50683 pts -> w6_s1_dim_00400.bin  x[  -5.2,  +4.1] y[  -1.9,  +9.8] z[  -1.1,  +2.0] i[1.0,255.0]
[frame 00500]  50686 pts -> w6_s1_dim_00500.bin  x[  -5.2,  +4.1] y[  -1.9,  +9.8] z[  -1.1,  +2.0] i[1.0,255.0]
------------------------------------------------------------------------
Done. Wrote 5 .bin file(s) to /home/user/Documents/workspace/sensor-fusion/code/bag_to_bin/out_w6/s1_dim

Format written: N x 5 float32 little-endian, columns [x, y, z, intensity, time_offset].
Feed these to OpenPCDet from inside venv_openpcdet (§6.2).
[INFO] [1783350628.499429061] [rosbag2_storage]: Opened database 'recordings/w6_s1_mixed/w6_s1_mixed_0.db3' for READ_ONLY.
[INFO] [1783350631.340876979] [rosbag2_storage]: Opened database 'recordings/w6_s1_mixed/w6_s1_mixed_0.db3' for READ_ONLY.
00100: dt=  8.30 ms
00200: dt=  7.21 ms
00300: dt=  5.91 ms
00400: dt=  7.24 ms
00500: dt=  6.78 ms
done: 5 frame(s) -> code/eval/frames_w6/s1_mixed
[frame 00300]  50280 pts -> w6_s1_mixed_00300.bin  x[  -8.3, +10.8] y[ -39.5,  +9.8] z[  -1.1,  +2.3] i[1.0,255.0]
[frame 00400]  50300 pts -> w6_s1_mixed_00400.bin  x[  -8.3, +10.9] y[ -39.6,  +9.8] z[  -1.1,  +2.3] i[1.0,255.0]
[frame 00500]  50310 pts -> w6_s1_mixed_00500.bin  x[  -8.3, +10.8] y[ -39.5,  +9.8] z[  -1.1,  +2.3] i[1.0,255.0]
------------------------------------------------------------------------
Done. Wrote 5 .bin file(s) to /home/user/Documents/workspace/sensor-fusion/code/bag_to_bin/out_w6/s1_mixed

Format written: N x 5 float32 little-endian, columns [x, y, z, intensity, time_offset].
Feed these to OpenPCDet from inside venv_openpcdet (§6.2).
[INFO] [1783350684.635791021] [rosbag2_storage]: Opened database 'recordings/w6_s2_bright/w6_s2_bright_0.db3' for READ_ONLY.
[INFO] [1783350693.526775028] [rosbag2_storage]: Opened database 'recordings/w6_s2_bright/w6_s2_bright_0.db3' for READ_ONLY.
00100: dt=  7.34 ms
00200: dt=  6.90 ms
00300: dt=  6.74 ms
00400: dt=  6.51 ms
00500: dt=  6.52 ms
done: 5 frame(s) -> code/eval/frames_w6/s2_bright
[frame 00300]  54204 pts -> w6_s2_bright_00300.bin  x[  -2.1,  +8.2] y[  -2.6,  +3.3] z[  -1.0,  +1.9] i[1.0,202.0]
[frame 00400]  54165 pts -> w6_s2_bright_00400.bin  x[  -2.1,  +8.2] y[  -2.6,  +3.3] z[  -1.0,  +1.9] i[1.0,206.0]
[frame 00500]  54172 pts -> w6_s2_bright_00500.bin  x[  -2.1,  +8.2] y[  -2.6,  +3.3] z[  -1.0,  +1.9] i[1.0,215.0]
------------------------------------------------------------------------
Done. Wrote 5 .bin file(s) to /home/user/Documents/workspace/sensor-fusion/code/bag_to_bin/out_w6/s2_bright

Format written: N x 5 float32 little-endian, columns [x, y, z, intensity, time_offset].
Feed these to OpenPCDet from inside venv_openpcdet (§6.2).
[INFO] [1783350791.654138506] [rosbag2_storage]: Opened database 'recordings/w6_s2_dim/w6_s2_dim_0.db3' for READ_ONLY.
[INFO] [1783350801.633423963] [rosbag2_storage]: Opened database 'recordings/w6_s2_dim/w6_s2_dim_0.db3' for READ_ONLY.
00100: dt=  6.93 ms
00200: dt=  6.18 ms
00300: dt=  6.16 ms
00400: dt=  6.20 ms
00500: dt=  6.92 ms
done: 5 frame(s) -> code/eval/frames_w6/s2_dim
[frame 00300]  54146 pts -> w6_s2_dim_00300.bin  x[  -2.1,  +8.2] y[  -2.6,  +3.3] z[  -1.0,  +1.9] i[1.0,216.0]
[frame 00400]  54154 pts -> w6_s2_dim_00400.bin  x[  -2.1,  +8.2] y[  -2.6,  +3.3] z[  -1.0,  +1.9] i[1.0,216.0]
[frame 00500]  54139 pts -> w6_s2_dim_00500.bin  x[  -2.1,  +8.2] y[  -2.6,  +3.3] z[  -1.0,  +1.9] i[1.0,215.0]
------------------------------------------------------------------------
Done. Wrote 5 .bin file(s) to /home/user/Documents/workspace/sensor-fusion/code/bag_to_bin/out_w6/s2_dim

Format written: N x 5 float32 little-endian, columns [x, y, z, intensity, time_offset].
Feed these to OpenPCDet from inside venv_openpcdet (§6.2).
[INFO] [1783350886.711742445] [rosbag2_storage]: Opened database 'recordings/w6_s2_mixed/w6_s2_mixed_0.db3' for READ_ONLY.
[INFO] [1783350896.443386492] [rosbag2_storage]: Opened database 'recordings/w6_s2_mixed/w6_s2_mixed_0.db3' for READ_ONLY.
00100: dt=  4.56 ms
00200: dt=  5.60 ms
00300: dt=  5.10 ms
00400: dt=  4.71 ms
00500: dt=  5.62 ms
done: 5 frame(s) -> code/eval/frames_w6/s2_mixed
[frame 00300]  53710 pts -> w6_s2_mixed_00300.bin  x[  -3.1,  +8.2] y[ -11.4,  +3.3] z[  -1.0,  +2.0] i[1.0,255.0]
[frame 00400]  53730 pts -> w6_s2_mixed_00400.bin  x[  -3.1,  +8.2] y[ -11.4,  +3.3] z[  -1.0,  +2.0] i[1.0,255.0]
[frame 00500]  53746 pts -> w6_s2_mixed_00500.bin  x[  -3.1,  +8.2] y[ -11.5,  +3.3] z[  -1.0,  +2.0] i[1.0,255.0]
------------------------------------------------------------------------
Done. Wrote 5 .bin file(s) to /home/user/Documents/workspace/sensor-fusion/code/bag_to_bin/out_w6/s2_mixed

Format written: N x 5 float32 little-endian, columns [x, y, z, intensity, time_offset].
Feed these to OpenPCDet from inside venv_openpcdet (§6.2).
```

## [OLD] 4.2 Annotation totals per condition
s1_bright: frames=1 instances=6 occluded=0 with_tape_range=6 per={'box': 1, 'laptop': 1, 'cup': 1, 'keyboard': 1, 'tv': 1, 'chair': 1}
s1_dim: frames=1 instances=6 occluded=0 with_tape_range=6 per={'cup': 1, 'keyboard': 1, 'laptop': 1, 'chair': 1, 'box': 1, 'tv': 1}
s1_mixed: frames=1 instances=6 occluded=0 with_tape_range=6 per={'cup': 1, 'keyboard': 1, 'laptop': 1, 'chair': 1, 'box': 1, 'tv': 1}
s2_bright: frames=1 instances=8 occluded=2 with_tape_range=8 per={'bottle': 1, 'box': 1, 'chair': 2, 'potted plant': 2, 'trash bin': 1, 'tv': 1}
s2_dim: frames=1 instances=8 occluded=2 with_tape_range=8 per={'bottle': 1, 'box': 1, 'chair': 2, 'potted plant': 2, 'trash bin': 1, 'tv': 1}
s2_mixed: frames=1 instances=8 occluded=1 with_tape_range=8 per={'bottle': 1, 'box': 1, 'chair': 2, 'potted plant': 2, 'trash bin': 1, 'tv': 1}

## 4.2 Annotation totals per condition
s1_bright: frames=5 instances=30 occluded=0 with_tape_range=30 per={'box': 5, 'laptop': 5, 'cup': 5, 'keyboard': 5, 'tv': 5, 'chair': 5}
s1_dim: frames=5 instances=30 occluded=0 with_tape_range=30 per={'cup': 5, 'keyboard': 5, 'laptop': 5, 'chair': 5, 'box': 5, 'tv': 5}
s1_mixed: frames=5 instances=30 occluded=0 with_tape_range=30 per={'cup': 5, 'keyboard': 5, 'laptop': 5, 'chair': 5, 'box': 5, 'tv': 5}
s2_bright: frames=5 instances=40 occluded=5 with_tape_range=40 per={'bottle': 5, 'box': 5, 'chair': 10, 'potted plant': 10, 'trash bin': 5, 'tv': 5}
s2_dim: frames=5 instances=40 occluded=5 with_tape_range=40 per={'bottle': 5, 'box': 5, 'chair': 10, 'potted plant': 10, 'trash bin': 5, 'tv': 5}
s2_mixed: frames=5 instances=40 occluded=0 with_tape_range=40 per={'bottle': 5, 'box': 5, 'chair': 10, 'potted plant': 10, 'trash bin': 5, 'tv': 5}

## GT verification (all 30 files, computed 2026-07-06)

Verified programmatically after annotation (seed 00100 -> copy to 00200-00500 -> re-open each in
annotate_gt.py to confirm every box still bounds its object under that frame; the rig was static so
the seed boxes needed only confirmation/small nudges).

- 30 files present: 6 conditions x 5 frames (00100-00500). PASS.
- Object counts: 6 per frame in every s1 condition, 8 per frame in every s2 condition. PASS.
- Within-condition consistency: all 5 frames of each condition carry the identical class+range
  multiset (static scene). PASS.
- Bbox sanity: 0 malformed boxes across all 30 files (all x1<x2, y1<y2, within 960x600). PASS.
- Tape ranges identical across each scene's 3 lighting conditions (geometry locked per scene). PASS.

### Occluded handling (VERIFIED against metrics.py) -- affects which objects are scored

metrics.py excludes `occluded=true` objects from BOTH the presence table (line 355:
`assess = [g for g in ... if not g["occluded"]]`) and the range-error table (line 405, same filter).
So `occluded=true` means "not scored", not "scored as a failure". GT set accordingly:

- **Far plant (7.83 m, F1 probe): occluded=false in ALL three s2 conditions**, with the observation
  "slightly occluded by a table edge" kept in `notes` (notes has no metric effect). This is
  deliberate: F1 is the probe designed to test localization at range under lighting change, so it
  MUST be scored in every condition. (A first save had it occluded=true in dim/mixed; caught in
  verification and corrected.)
- **Window plant (2.65 m): occluded=true in bright + dim, false in mixed.** It is genuinely hidden
  behind the closed blinds in bright/dim (only leaves leaking), so excluding it there avoids
  penalising a missed detection of an invisible object; in mixed (blinds open) it is visible and
  scored.

Occluded totals per condition (over 5 frames): s1_bright/dim/mixed = 0; s2_bright = 5 (window plant
x5); s2_dim = 5 (window plant x5); s2_mixed = 0. Per-class instance totals over 5 frames per
condition: s1 = {box, laptop, cup, keyboard, tv, chair} x5 each; s2 = {bottle, box, trash bin, tv}
x5 each and {chair, potted plant} x10 each (two of each per frame).

### Class strings -- UNVERIFIED against the canon

Distinct GT class strings: bottle, box, chair, cup, keyboard, laptop, potted plant, trash bin, tv.
These match the marker tables. NOT verified: whether these survive metrics.py's `canon()` mapping as
intended (I do not have the frozen d24 canon/ALIAS file). Confirm at the start of d35 that the GT
class strings map as expected, or the class-accuracy numbers will be off. box and trash bin are the
intended F4 out-of-vocabulary probes (they map to themselves, never to a COCO label).

## Deviations / notes (for the record)

- Procedure lesson: the first annotation pass used `q` (save + quit the whole loop) at the end of
  each condition instead of `d` (save + advance to next frame), so only 00100 was annotated per
  condition on the first attempt. Recovered by seeding 00100 to the other four frames and verifying
  each. The step_by_step 4.2 note was corrected to make `d` vs `q` explicit.
- N per condition = 5 frames, but the rig was static, so the 5 frames of a condition are nearly
  identical; the within-condition variance will be small by construction. Value is plan-compliance
  and a within-cell spread, not new phenomena across frames. Small-N caveat carries to the thesis.

## Pending after d34

- d35: run the three arms per condition (fused via frustum_fuse.py; LiDAR-only via OpenPCDet demo.py
  IF venv_openpcdet + the PointPillars checkpoint survived the incident -- OPEN QUESTION to confirm
  before d35), then metrics.py to produce presence / range-error / fused-rate tables per condition,
  then figures.py. Verify canon() class mapping and the env-keying of the s1_*/s2_* condition names
  at the start of d35 (both flagged, not yet checked).
- Backup: the 30 GT files + the bins + this manifest to the external disk.

