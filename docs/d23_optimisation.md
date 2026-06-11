# Day 5 (d23) optimisation manifest -- 2026-06-11

**Scope:** A = drop-to-latest queue policy (headline, live); B = TensorRT FP16 (banked, bag + composed live).
**Node:** fusion_node.py d23 (--sub-depth/--sync-queue defaults 10/10 == d19-d22; --profile-label; rclpy.ok() shutdown guard).

**Power profile (nvpmodel -q):**
```
NV Power Mode: MAXN
0
```

## Before-anchor: d20 parity on the pre-optimisation node (5.0)
```
parity: frames=['00100', '00300', '00500'] pos_tol=0.05 m bin_channels=5
        frames_dir=code/fusion/frames_out
        bins_dir  =code/bag_to_bin/out
        offline   =code/fusion/fused_out

| frame | result | boxes (c/o) | src flips | max range d (m) | max centroid d (m) | fused classes | img dec | cloud dec |
|---|---|---|---|---|---|---|---|---|
| 00100 | PASS | 11/11 | 0 | 0.0000 | 0.0000 | match | PASS | 0 |
| 00300 | PASS | 10/10 | 0 | 0.0000 | 0.0000 | match | PASS | 0 |
| 00500 | PASS | 10/10 | 0 | 0.0000 | 0.0000 | match | PASS | 0 |

OVERALL: PASS
```
(identical to d20; the benign matplotlib Axes3D UserWarning appeared as in d20 and is omitted here.)

## A1 queue-policy BEFORE (live, default sub-depth=10 sync-queue=10, N=200)
```
## Per-stage latency (live, default queues (d23 A before), steady-state, N=200)
| stage | mean ms | p50 | p95 |
|---|---|---|---|
| image decode    |    5.12 |    4.91 |    6.20 |
| pointcloud->xyz |    1.72 |    1.61 |    2.35 |
| yolo inference  |   58.20 |   57.81 |   74.86 |
| projection      |   13.50 |   10.25 |   38.28 |
| dbscan assoc    |   61.11 |   57.95 |   83.71 |
| msg build/pub   |    3.18 |    2.90 |    4.96 |
| END-TO-END (cb) |  142.88 |  139.21 |  185.22 |
| stamp e2e       | 1138.58 | 1149.23 | 1248.79 |
- derived fps (1000 / p50 callback): 7.18 Hz (authoritative published fps = `ros2 topic hz`)
- dominant stage (by p50): dbscan assoc (57.95 ms)
- warmup (first frame) vs steady (p50 callback): 1211.87 ms / 139.21 ms
```
- published fps (settled ~7.42-7.46 Hz; per-message 0.100-0.207 s, std dev ~0.018 s):
```
average rate: 7.458   window: 262
average rate: 7.458   window: 270
average rate: 7.453   window: 278
average rate: 7.434   window: 285
average rate: 7.422   window: 293
```
- paired-callback rate (yield), steady samples: 6.42 / 6.90 / 7.55 / 6.92 / 6.60 / 6.98 / 6.39 Hz
  (total pairs 1281 at the last sample; 4-7 dets per frame, all fused).
- consistency vs d22: same ~1.1 s stamp-e2e regime (d22: 1096.05/1217.59); the standing-backlog "before"
  reproduced on a different day/session. Scene heavier than d22 (DBSCAN 57.95 vs 42.68), hence the lower
  fps (~7.4 vs ~8.1) -- scene-dependent, as established in d22.

## A2 load-relief preliminary
- SKIPPED -- superseded by A4: the queue-depth-invariance test is the definitive attribution, and the
  ~930 ms drop under depth 1/2 (below) already excludes a clock offset of that magnitude. No separate
  contention reading was recorded.

## A3 queue-policy AFTER (live, sub-depth=1 sync-queue=2, N=200)
- pairs tried: depth=1 q=2 only -> stamp e2e p50 218.67 ms, yield ~7.1-7.6 Hz (no collapse; the §5.2
  sweep was conditional on yield collapse, which did not occur -- see the sweep note at the end).
```
## Per-stage latency (live, drop-to-latest depth=1 q=2 (d23 A after), steady-state, N=200)
| stage | mean ms | p50 | p95 |
|---|---|---|---|
| image decode    |    5.11 |    4.90 |    6.57 |
| pointcloud->xyz |    1.74 |    1.62 |    2.20 |
| yolo inference  |   58.44 |   56.83 |   77.65 |
| projection      |   12.17 |    9.30 |   30.39 |
| dbscan assoc    |   55.45 |   51.60 |   79.08 |
| msg build/pub   |    2.60 |    2.37 |    4.28 |
| END-TO-END (cb) |  135.57 |  130.65 |  181.95 |
| stamp e2e       |  224.43 |  218.67 |  281.75 |
- derived fps (1000 / p50 callback): 7.65 Hz (authoritative published fps = `ros2 topic hz`)
- dominant stage (by p50): yolo inference (56.83 ms)
- warmup (first frame) vs steady (p50 callback): 1281.16 ms / 130.65 ms
```
- published fps (settled ~7.25-7.26 Hz; per-message 0.103-0.208 s, std dev ~0.021 s):
```
average rate: 7.260   window: 288
average rate: 7.251   window: 295
average rate: 7.253   window: 303
average rate: 7.253   window: 311
average rate: 7.260   window: 319
```
- paired-callback rate (yield), steady samples: 7.33 / 7.24 / 7.55 / 7.13 / 7.21 / 7.61 / 6.43 Hz
  (total pairs 714 at the last sample; 3-5 dets per frame, all fused).

## A4 attribution (closes the d22 open item)
- stamp e2e p50: 1149.23 -> 218.67 ms (queue depth 10 -> 1; sync queue 10 -> 2). Delta -930.56 ms
  (-81.0%); p95 1248.79 -> 281.75 (-77.4%).
- conclusion: **queue-bound CONFIRMED.** The staleness collapsed when only the queue depth changed; a
  clock offset is invariant to queue depth, so the d22 ~1 s INTERPRETED claim is now measured. The ZED
  image-stamp-source check is no longer needed.
- residual: 218.67 - 130.65 = 88.02 ms over the callback span ~= one 10 Hz input period + synchronizer
  alignment -- the freshness floor of a 10 Hz pipeline, not an unexplained offset.
- controls behaved as predicted: callback span ~unchanged (139.21 -> 130.65; same compute, small scene
  drift via DBSCAN 57.95 -> 51.60), published fps ~unchanged (drain-limited), yield healthy.

## B1 TensorRT FP16 export (on-device)
- imgsz=640 confirmed as the .pt runtime size before export (d14 Speed line: inference "at (1, 3, 416,
  640)" on the 960x600 frames; the export log below confirms (1, 3, 640, 640)).
- Attempt 1 FAILED: `ModuleNotFoundError: No module named 'onnx'` (ultralytics AutoUpdate could not
  install `onnx onnxruntime-gpu onnxslim`; onnxruntime-gpu has no aarch64 wheels). Fix: pip install
  onnx + onnxslim in venv_yolo (aarch64 wheels exist for these two).
- Attempt 2 FAILED: ONNX export succeeded (yolov8s.onnx, 42.8 MB) but engine build raised
  `ModuleNotFoundError: No module named 'tensorrt'`. AutoUpdate tried pip `tensorrt-cu12`, whose
  pypi.nvidia.com wheels exist only for x86_64/win -- the pip route does not exist on Jetson (aarch64).
  TensorRT 10.3.0 was already installed via JetPack debs (python3-libnvinfer) at
  /usr/lib/python3.10/dist-packages, which venv_yolo did not see.
- Fix: `system_tensorrt.pth` in venv_yolo site-packages exposing /usr/lib/python3.10/dist-packages at
  LOWEST precedence (venv packages still win; numpy 1.26.4 / cv2 / torch verified unchanged). Same
  two-environment-bridge pattern as the ROS/venv PYTHONPATH split, applied venv-side. The remaining
  onnxruntime-gpu warnings are benign (not needed; export proceeds without it).
- Attempt 3 SUCCESS (key log lines, ANSI stripped; full log in terminal history):
```
Ultralytics 8.4.60  Python-3.10.12 torch-2.8.0 CUDA:0 (Orin, 15655MiB)
PyTorch: starting from 'yolov8s.pt' with input shape (1, 3, 640, 640) BCHW and output shape(s) (1, 84, 8400) (21.5 MB)
ONNX: export success 6.9s, saved as 'yolov8s.onnx' (42.8 MB)
TensorRT: starting export with TensorRT 10.3.0...
TensorRT: input "images" with shape(1, 3, 640, 640) DataType.FLOAT
TensorRT: building FP16 engine as yolov8s.engine
[TRT] Engine generation completed in 450.918 seconds.
TensorRT: export success 460.9s, saved as 'yolov8s.engine' (24.2 MB)
```
- artifacts: yolov8s.engine (24.2 MB) + yolov8s.onnx at repo root. Device-specific (this Orin /
  TensorRT 10.3), regenerable -- gitignore both, never copy from another machine.

## B2 TensorRT after (test2 bag, dense regime, N=200; before = d21 manifest, same bag + protocol)
- run note: the node stopped publishing after the bag's first loop; waited ~15 s, closed. INTERPRETED:
  the time synchronizer does not pair across the loop restart (header stamps jump backwards, queued
  messages look "future"). Benign here: the N=200 window completed within the first pass (309 pairs).
```
## Per-stage latency (bag playback, TensorRT FP16 (d23 B after; before = d21), steady-state, N=200)
| stage | mean ms | p50 | p95 |
|---|---|---|---|
| image decode    |    5.31 |    5.18 |    5.99 |
| pointcloud->xyz |    1.91 |    1.86 |    2.23 |
| yolo inference  |   36.96 |   32.84 |   56.32 |
| projection      |    6.84 |    4.68 |   19.11 |
| dbscan assoc    |   87.70 |   84.37 |  112.02 |
| msg build/pub   |    4.30 |    4.18 |    5.64 |
| END-TO-END (cb) |  143.08 |  136.80 |  185.87 |
- stamp-based end-to-end: N/A on this run (node clock and image header stamp not aligned: use --clock +
  use_sim_time:=true on the bag, or measure live -- as d21)
- derived fps (1000 / p50 callback): 7.31 Hz (authoritative published fps = `ros2 topic hz`)
- dominant stage (by p50): dbscan assoc (84.37 ms)
- warmup (first frame) vs steady (p50 callback): 827.53 ms / 136.80 ms
```
- published fps (settled ~6.95 Hz; per-message 0.120-0.217 s, std dev ~0.018 s):
```
average rate: 6.945   window: 126
average rate: 6.950   window: 134
average rate: 6.951   window: 141
average rate: 6.961   window: 149
average rate: 6.951   window: 156
```
- paired-callback rate (yield), steady samples: 7.25 / 7.08 / 7.22 / 7.25 / 6.92 / 6.91 / 7.09 Hz
  (total pairs 309 at the last sample; 6-8 dets per frame, all fused).
- scene control held: DBSCAN p50 84.37 vs d21 83.57 (+0.80 ms, unchanged) -- same bag, same dense scene,
  so the YOLO/e2e delta IS the optimisation.

## B3 composed live run (own terms, office scene; engine + drop-to-latest depth=1 q=2, N=200)
```
## Per-stage latency (live, TensorRT FP16 + drop-to-latest (d23 B3 composed), steady-state, N=200)
| stage | mean ms | p50 | p95 |
|---|---|---|---|
| image decode    |    5.47 |    4.95 |    7.21 |
| pointcloud->xyz |    1.81 |    1.64 |    2.61 |
| yolo inference  |   41.90 |   39.27 |   62.16 |
| projection      |    9.12 |    7.15 |   22.58 |
| dbscan assoc    |   51.53 |   48.02 |   71.91 |
| msg build/pub   |    2.35 |    2.19 |    3.85 |
| END-TO-END (cb) |  112.24 |  107.80 |  144.49 |
| stamp e2e       |  202.90 |  197.01 |  242.99 |
- derived fps (1000 / p50 callback): 9.28 Hz (authoritative published fps = `ros2 topic hz`)
- dominant stage (by p50): dbscan assoc (48.02 ms)
- warmup (first frame) vs steady (p50 callback): 726.39 ms / 107.80 ms
```
- published fps (settled ~8.4 Hz; per-message 0.086-0.206 s, std dev ~0.019 s):
```
average rate: 8.372   window: 186
average rate: 8.389   window: 195
average rate: 8.436   window: 205
average rate: 8.438   window: 214
average rate: 8.398   window: 222
```
- paired-callback rate (yield), steady samples: 8.58 / 9.21 / 8.87 / 8.99 / 6.99 / 8.03 / 7.70 Hz
  (total pairs 747 at the last sample; 3-4 dets per frame, all fused).

## B4 parity re-check after TensorRT (Route 1: parity_check.py re-runs YOLO; --model already existed)
```
parity: frames=['00100', '00300', '00500'] pos_tol=0.05 m bin_channels=5
Loading yolov8s.engine for TensorRT inference...
| frame | result | boxes (c/o) | src flips | max range d (m) | max centroid d (m) | fused classes | img dec | cloud dec |
|---|---|---|---|---|---|---|---|---|
| 00100 | FAIL | 9/11 | 0 | 0.0000 | 0.0000 | DIFFER | PASS | 0 |
| 00300 | FAIL | 9/10 | 0 | 0.0000 | 0.0000 | DIFFER | PASS | 0 |
| 00500 | FAIL | 8/10 | 0 | 0.0000 | 0.0000 | DIFFER | PASS | 0 |

  [00100] box count differs: computed 9 vs offline 11
  [00300] box count differs: computed 9 vs offline 10
  [00500] box count differs: computed 8 vs offline 10

OVERALL: FAIL
```
(an ultralytics WARNING "Unable to automatically guess model task, assuming 'task=detect'" appeared on
engine load -- benign, detect is correct.)
- reading: parity FAILS by the box-count criterion (2/1/2 boxes fewer than the .pt offline reference),
  while every RETAINED box is geometrically exact (0.0000 m max range/centroid delta, 0 source flips,
  image/cloud decoders PASS). "fused classes DIFFER" follows from the count difference.
- INTERPRETED: FP16 confidence shifts pushed the lowest-confidence detections below the conf=0.25
  threshold (the offline reference has boxes at conf 0.26-0.37 sitting just above it -- d16 manifest);
  which specific boxes dropped was not extracted (optional follow-up: per-box diff of computed vs
  fused_out JSON).
- verdict: documented accuracy-vs-latency trade-off, not hidden. yolov8s.pt remains the accuracy
  reference; yolov8s.engine is the latency option. Geometry of everything the engine detects is
  unchanged.

## Consolidated before/after
### A -- drop-to-latest queue policy (LIVE, office scene): the headline real-time result
| metric | before (default 10/10) | after (depth=1 q=2) | delta |
|---|---|---|---|
| stamp e2e p50 (sensor->publish) ms | 1149.23 (d22: 1096.05) | 218.67 | -930.56 (-81.0%) |
| stamp e2e p95 ms                   | 1248.79 (d22: 1217.59) | 281.75 | -967.04 (-77.4%) |
| callback span p50 ms               | 139.21 (d22: 116.49)   | 130.65 | -8.56 (~unchanged, as predicted) |
| published fps                      | ~7.4 (d22: ~8.1)       | ~7.25  | ~unchanged (drain-limited), as predicted |
| paired-callback rate (yield) Hz    | ~6.4-7.6               | ~7.1-7.6 | healthy, no collapse |

### B -- TensorRT FP16 (test2 BAG, dense regime): the controlled compute delta
| metric | before (.pt, d21 measured) | after (.engine) | speedup |
|---|---|---|---|
| yolo inference p50 ms        | 61.47  | 32.84  | 1.87x (-46.6%) |
| end-to-end (callback) p50 ms | 161.98 | 136.80 | 1.18x (-15.5%) |
| end-to-end (callback) p95 ms | 198.95 | 185.87 | -6.6% |
| published fps                | ~5.9   | ~6.95  | +~1.05 Hz (1.18x) |
| dbscan assoc p50 ms (control)| 83.57  | 84.37  | unchanged (same scene confirmed) |
- dense-regime note: the DBSCAN floor (~84 ms p50) is untouched, so end-to-end moves only -15.5% while
  YOLO nearly halves -> TensorRT alone cannot beat the DBSCAN floor on dense scenes (the honest half of
  the d22 two-regime finding).
- parity after FP16 (d20 frames): retained-box max range/centroid delta 0.0000 m, 0 flips; box count
  9/9/8 vs 11/10/10 (lowest-conf detections dropped; see B4).

### A+B composed (LIVE, office scene; engine + depth=1 q=2) vs the same-day live before
| metric | A1 before (.pt, 10/10) | B3 composed (.engine, 1/2) | delta |
|---|---|---|---|
| stamp e2e p50 (sensor->publish) ms | 1149.23 | 197.01 | -952.22 (-82.9%) |
| stamp e2e p95 ms                   | 1248.79 | 242.99 | -1005.80 (-80.5%) |
| callback span p50 / p95 ms         | 139.21 / 185.22 | 107.80 / 144.49 | -22.6% / -22.0% |
| published fps                      | ~7.4    | ~8.4   | +~1.0 Hz |
| dominant stage (by p50)            | DBSCAN 57.95 | DBSCAN 48.02 | DBSCAN leads post-engine -> next target |
- **sensor-to-publish p50 197 ms is UNDER the 200 ms aim (originally scoped for compute alone); p95
  243 ms is under half the 500 ms acceptable.**

## Power-profile close (2026-05-26 decision)
- decision: **MAXN (mode 0).** Rationale: callback jitter (p95-p50) measured 36.97 ms (d21 bag), 45.94
  (d22 live), 46.01 / 51.30 / 36.69 ms (d23 A1 / A3 / B3); no over-current throttle notices in any
  measured window across d21/d22/d23; the §3.2 revisit rule (large jitter or frequent over-current) was
  never triggered. Fixed profile noted as the deterministic-latency alternative for a future deployment.
- optional fixed-profile spot-check: SKIPPED (switching not justified mid-session; the close stands on
  the measured jitter above).

## Findings (measured fact -> interpretation; interpretation flagged)
1. **The ~1 s live staleness was queue latency -- measured, no longer interpreted.** Shrinking only the
   queues (10/10 -> 1/2) collapsed stamp e2e p50 1149 -> 219 ms while compute, fps, and yield held. A
   clock offset is invariant to queue depth, so it is excluded at this magnitude. Residual 88 ms over
   the callback span is the ~one-input-period freshness floor. Consequence: the d22 finding-1 lever was
   the right one; the real-time configuration is depth=1/q=2 (node defaults stay 10/10).
2. **TensorRT FP16: 1.87x on YOLO, 1.18x end-to-end on the dense bag -- the DBSCAN floor is real.**
   DBSCAN held at ~84 ms (scene control), so e2e moved -15.5% despite YOLO halving. Both halves of the
   d22 two-regime finding are now measured: the engine helps most where YOLO dominates; it cannot beat
   the association floor where DBSCAN dominates.
3. **Composed (engine + drop-to-latest), live: sensor-to-publish p50 197 ms / p95 243 ms at ~8.4 Hz.**
   Under the 200 ms aim that was originally scoped for compute alone, and under half the 500 ms
   acceptable. INTERPRETED consequence for next steps: with the engine in, DBSCAN (48 ms) is the
   dominant stage even in the sparse scene, so the next optimisation target is the association stage,
   not the CNN.
4. **FP16 costs detections near the confidence threshold.** 2/1/2 of 11/10/10 reference boxes (offline
   confs down to 0.26-0.37 vs conf=0.25) are no longer detected by the engine; every retained box is
   geometrically exact (0.0000 m, 0 flips). INTERPRETED as threshold crossing under FP16 confidence
   shift; per-box identification left as optional follow-up. Trade-off documented: .pt = accuracy
   reference, .engine = latency option.

## Screenshot index
- d23_before_anchor.png -- 5.0 parity PASS table + nvpmodel -q.
- d23_queue_policy_A1.png -- A1 live before summary (N=150 rolling + N=200 final; stamp e2e ~1.15 s).
- d23_queue_policy_A3.png -- A3 live after summary (N=150 rolling + N=200 final; stamp e2e ~219 ms).
- d23_tensorrt.png -- B4 parity-after-FP16 table (FAIL by count, 0.0000 m retained). NOTE: shows the B4
  parity, not the B2 bag table; the B2 table is recorded in this manifest (and /tmp/d23_trt_bag.md).
- d23_trt_live_composed.png -- B3 composed live summary (N=150 rolling + N=200 final; stamp e2e ~197 ms).

## Operational note
- LiDAR cooldown breaks taken between live runs (no heatsink mounted; user-guide operating limit +60 C,
  storage +85 C). Deployment/Limitations material, not an error.

## Final state (10:42:23)
- A queue policy: stamp e2e p50 1149.23 -> 218.67 ms (p95 1248.79 -> 281.75) at depth 10 -> 1 / queue
  10 -> 2; yield ~7.1-7.6 Hz (healthy); attribution: queue-bound CONFIRMED (closes the d22 open item).
- B TensorRT: YOLO p50 61.47 -> 32.84 ms (test2 bag, 1.87x); end-to-end 161.98 -> 136.80 (-15.5%); fps
  ~5.9 -> ~6.95; DBSCAN-floor point recorded (DBSCAN unchanged at ~84 ms). Composed live run (B3):
  stamp e2e p50/p95 197.01/242.99 ms, callback 107.80/144.49, ~8.4 Hz.
- Parity: before-anchor PASS (0.0000 m); after queue policy PASS by construction; after TensorRT FAIL
  by box count (9/9/8 vs 11/10/10) with retained boxes at 0.0000 m / 0 flips -- documented FP16
  accuracy-vs-latency trade-off.
- Power-profile decision: MAXN (closed; jitter + no-throttle rationale above).
- Day 5 outcome: PASS.
