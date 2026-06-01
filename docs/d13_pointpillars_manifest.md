# Day 6 PointPillars baseline manifest -- 2026-05-28

**Goal:** nuScenes-pretrained PointPillars-MultiHead detections on `test2_marked_distances`, qualitative + quantitative.

## .bin conversion
- Script: code/bag_to_bin/bag_to_bin.py (run in ROS env, not venv)
- Source bag: recordings/test2_marked_distances
- Output dir: code/bag_to_bin/out
- Format: nuscenes (5-channel)
- Frame selection: --stride 100 (frames 00000, 00100, ... 00800)
- Files produced: 9
- Conversion duration: 1s
- Sample-frame file size: 1072860 bytes

## PointPillars-MultiHead inference - NO GUI
- Config: cfgs/nuscenes_models/cbgs_pp_multihead.yaml
- Checkpoint: checkpoints/pp_multihead_nds5823_updated.pth
- Checkpoint SHA256: 0d241edcfc089a1d1901c2747ea9cb8cb3eec80c9e86a551727ac526e063e77d

### Frame 00100
- Inference start: 10:19:57.901
- Inference end: 10:20:14.825
- Duration: 16.919s
- Detection summary (last lines of log):
      if not hasattr(_np_compat, _name):
    /home/user/Documents/workspace/sensor-fusion/third_party/OpenPCDet/pcdet/utils/loss_utils.py:152: FutureWarning: `torch.cuda.amp.custom_fwd(args...)` is deprecated. Please use `torch.amp.custom_fwd(args..., device_type='cuda')` instead.
      @torch.cuda.amp.custom_fwd(cast_inputs=torch.float16)
    2026-05-28 10:20:12,070   INFO  -----------------Quick Demo of OpenPCDet-------------------------
    2026-05-28 10:20:12,070   INFO  Total number of samples: 	1
    /home/user/Documents/workspace/sensor-fusion/venv_openpcdet/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /opt/pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
      return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
    2026-05-28 10:20:12,357   INFO  ==> Loading parameters from checkpoint checkpoints/pp_multihead_nds5823_updated.pth to CPU
    2026-05-28 10:20:12,498   INFO  ==> Done (loaded 421/421)
    2026-05-28 10:20:12,598   INFO  Visualized sample index: 	1
    2026-05-28 10:20:13,178   INFO  [DETECTIONS] 30 raw boxes, 3 above score 0.30
    2026-05-28 10:20:13,179   INFO    trailer              score=0.368 pos=(+0.79,-0.49,+0.06) size=(10.01,2.90,2.96) range=0.94m
    2026-05-28 10:20:13,179   INFO    pedestrian           score=0.358 pos=(+5.29,-0.39,-0.59) size=(0.61,0.62,1.76) range=5.30m
    2026-05-28 10:20:13,179   INFO    pedestrian           score=0.336 pos=(+5.23,+0.66,-0.57) size=(0.63,0.64,1.77) range=5.27m
    2026-05-28 10:20:13,179   INFO  Demo done.

### Frame 00300
- Inference start: 10:20:14.836
- Inference end: 10:20:31.631
- Duration: 16.788s
- Detection summary (last lines of log):
      if not hasattr(_np_compat, _name):
    /home/user/Documents/workspace/sensor-fusion/third_party/OpenPCDet/pcdet/utils/loss_utils.py:152: FutureWarning: `torch.cuda.amp.custom_fwd(args...)` is deprecated. Please use `torch.amp.custom_fwd(args..., device_type='cuda')` instead.
      @torch.cuda.amp.custom_fwd(cast_inputs=torch.float16)
    2026-05-28 10:20:28,930   INFO  -----------------Quick Demo of OpenPCDet-------------------------
    2026-05-28 10:20:28,931   INFO  Total number of samples: 	1
    /home/user/Documents/workspace/sensor-fusion/venv_openpcdet/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /opt/pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
      return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
    2026-05-28 10:20:29,214   INFO  ==> Loading parameters from checkpoint checkpoints/pp_multihead_nds5823_updated.pth to CPU
    2026-05-28 10:20:29,340   INFO  ==> Done (loaded 421/421)
    2026-05-28 10:20:29,425   INFO  Visualized sample index: 	1
    2026-05-28 10:20:30,007   INFO  [DETECTIONS] 26 raw boxes, 3 above score 0.30
    2026-05-28 10:20:30,008   INFO    trailer              score=0.431 pos=(+1.15,-0.60,+0.08) size=(9.31,2.94,2.97) range=1.29m
    2026-05-28 10:20:30,008   INFO    pedestrian           score=0.370 pos=(+4.33,+0.13,-0.61) size=(0.62,0.64,1.78) range=4.33m
    2026-05-28 10:20:30,008   INFO    pedestrian           score=0.316 pos=(+5.25,+0.65,-0.59) size=(0.61,0.63,1.75) range=5.29m
    2026-05-28 10:20:30,008   INFO  Demo done.

### Frame 00500
- Inference start: 10:20:31.641
- Inference end: 10:20:48.489
- Duration: 16.842s
- Detection summary (last lines of log):
      @torch.cuda.amp.custom_fwd(cast_inputs=torch.float16)
    2026-05-28 10:20:45,709   INFO  -----------------Quick Demo of OpenPCDet-------------------------
    2026-05-28 10:20:45,709   INFO  Total number of samples: 	1
    /home/user/Documents/workspace/sensor-fusion/venv_openpcdet/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /opt/pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
      return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
    2026-05-28 10:20:45,999   INFO  ==> Loading parameters from checkpoint checkpoints/pp_multihead_nds5823_updated.pth to CPU
    2026-05-28 10:20:46,153   INFO  ==> Done (loaded 421/421)
    2026-05-28 10:20:46,246   INFO  Visualized sample index: 	1
    2026-05-28 10:20:46,830   INFO  [DETECTIONS] 28 raw boxes, 5 above score 0.30
    2026-05-28 10:20:46,831   INFO    truck                score=0.518 pos=(+0.97,-0.12,-0.29) size=(11.46,3.12,3.27) range=0.97m
    2026-05-28 10:20:46,831   INFO    pedestrian           score=0.340 pos=(+5.21,+0.66,-0.66) size=(0.62,0.62,1.76) range=5.25m
    2026-05-28 10:20:46,831   INFO    pedestrian           score=0.319 pos=(+4.33,+0.10,-0.70) size=(0.62,0.64,1.78) range=4.33m
    2026-05-28 10:20:46,831   INFO    trailer              score=0.315 pos=(+1.20,-0.49,+0.06) size=(9.12,2.99,2.87) range=1.30m
    2026-05-28 10:20:46,831   INFO    pedestrian           score=0.314 pos=(+5.29,-0.47,-0.67) size=(0.62,0.61,1.74) range=5.31m
    2026-05-28 10:20:46,831   INFO  Demo done.

## PointPillars-MultiHead inference - With GUI + screenshots
- Config: cfgs/nuscenes_models/cbgs_pp_multihead.yaml
- Checkpoint: checkpoints/pp_multihead_nds5823_updated.pth
- Checkpoint SHA256: 0d241edcfc089a1d1901c2747ea9cb8cb3eec80c9e86a551727ac526e063e77d

### Frame 00100
- Inference start: 11:11:51.951
- Inference end: 11:13:59.192
- Duration: 127.235s
- Detection summary (last lines of log):
      if not hasattr(_np_compat, _name):
    /home/user/Documents/workspace/sensor-fusion/third_party/OpenPCDet/pcdet/utils/loss_utils.py:152: FutureWarning: `torch.cuda.amp.custom_fwd(args...)` is deprecated. Please use `torch.amp.custom_fwd(args..., device_type='cuda')` instead.
      @torch.cuda.amp.custom_fwd(cast_inputs=torch.float16)
    2026-05-28 11:12:05,803   INFO  -----------------Quick Demo of OpenPCDet-------------------------
    2026-05-28 11:12:05,804   INFO  Total number of samples: 	1
    /home/user/Documents/workspace/sensor-fusion/venv_openpcdet/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /opt/pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
      return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
    2026-05-28 11:12:06,079   INFO  ==> Loading parameters from checkpoint checkpoints/pp_multihead_nds5823_updated.pth to CPU
    2026-05-28 11:12:06,213   INFO  ==> Done (loaded 421/421)
    2026-05-28 11:12:06,309   INFO  Visualized sample index: 	1
    2026-05-28 11:12:06,879   INFO  [DETECTIONS] 29 raw boxes, 3 above score 0.30
    2026-05-28 11:12:06,879   INFO    pedestrian           score=0.344 pos=(+5.30,-0.58,-0.61) size=(0.65,0.66,1.75) range=5.33m
    2026-05-28 11:12:06,879   INFO    pedestrian           score=0.337 pos=(+5.23,+0.64,-0.57) size=(0.63,0.65,1.77) range=5.27m
    2026-05-28 11:12:06,880   INFO    pedestrian           score=0.300 pos=(+4.45,+0.11,-0.62) size=(0.61,0.65,1.77) range=4.45m
    2026-05-28 11:13:57,497   INFO  Demo done.

### Frame 00300
- Inference start: 11:13:59.202
- Inference end: 11:15:55.034
- Duration: 115.827s
- Detection summary (last lines of log):
      if not hasattr(_np_compat, _name):
    /home/user/Documents/workspace/sensor-fusion/third_party/OpenPCDet/pcdet/utils/loss_utils.py:152: FutureWarning: `torch.cuda.amp.custom_fwd(args...)` is deprecated. Please use `torch.amp.custom_fwd(args..., device_type='cuda')` instead.
      @torch.cuda.amp.custom_fwd(cast_inputs=torch.float16)
    2026-05-28 11:14:13,403   INFO  -----------------Quick Demo of OpenPCDet-------------------------
    2026-05-28 11:14:13,404   INFO  Total number of samples: 	1
    /home/user/Documents/workspace/sensor-fusion/venv_openpcdet/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /opt/pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
      return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
    2026-05-28 11:14:13,693   INFO  ==> Loading parameters from checkpoint checkpoints/pp_multihead_nds5823_updated.pth to CPU
    2026-05-28 11:14:13,816   INFO  ==> Done (loaded 421/421)
    2026-05-28 11:14:13,924   INFO  Visualized sample index: 	1
    2026-05-28 11:14:14,513   INFO  [DETECTIONS] 25 raw boxes, 3 above score 0.30
    2026-05-28 11:14:14,513   INFO    trailer              score=0.531 pos=(+1.17,-0.50,+0.07) size=(9.57,2.98,2.95) range=1.27m
    2026-05-28 11:14:14,513   INFO    pedestrian           score=0.370 pos=(+4.34,+0.12,-0.63) size=(0.62,0.64,1.78) range=4.34m
    2026-05-28 11:14:14,513   INFO    pedestrian           score=0.302 pos=(+5.26,+0.66,-0.63) size=(0.62,0.63,1.74) range=5.30m
    2026-05-28 11:15:53,329   INFO  Demo done.

### Frame 00500
- Inference start: 11:15:55.054
- Inference end: 11:17:38.128
- Duration: 103.066s
- Detection summary (last lines of log):
    /home/user/Documents/workspace/sensor-fusion/third_party/OpenPCDet/pcdet/utils/loss_utils.py:152: FutureWarning: `torch.cuda.amp.custom_fwd(args...)` is deprecated. Please use `torch.amp.custom_fwd(args..., device_type='cuda')` instead.
      @torch.cuda.amp.custom_fwd(cast_inputs=torch.float16)
    2026-05-28 11:16:09,310   INFO  -----------------Quick Demo of OpenPCDet-------------------------
    2026-05-28 11:16:09,310   INFO  Total number of samples: 	1
    /home/user/Documents/workspace/sensor-fusion/venv_openpcdet/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /opt/pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
      return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
    2026-05-28 11:16:09,598   INFO  ==> Loading parameters from checkpoint checkpoints/pp_multihead_nds5823_updated.pth to CPU
    2026-05-28 11:16:09,720   INFO  ==> Done (loaded 421/421)
    2026-05-28 11:16:09,826   INFO  Visualized sample index: 	1
    2026-05-28 11:16:10,411   INFO  [DETECTIONS] 29 raw boxes, 4 above score 0.30
    2026-05-28 11:16:10,411   INFO    truck                score=0.499 pos=(+0.99,-0.19,-0.31) size=(11.37,3.14,3.27) range=1.01m
    2026-05-28 11:16:10,411   INFO    pedestrian           score=0.340 pos=(+5.22,+0.65,-0.65) size=(0.62,0.62,1.77) range=5.26m
    2026-05-28 11:16:10,411   INFO    pedestrian           score=0.332 pos=(+4.34,+0.09,-0.70) size=(0.63,0.64,1.79) range=4.34m
    2026-05-28 11:16:10,411   INFO    pedestrian           score=0.325 pos=(+5.31,-0.47,-0.66) size=(0.62,0.61,1.75) range=5.33m
    2026-05-28 11:17:36,469   INFO  Demo done.


## Qualitative inspection

**Consistent detection pattern across all three frames (static scene, thresholded at score >= 0.30):**

| Detection | Range | Box size (L×W×H) | Score range | Interpretation |
|---|---|---|---|---|
| "trailer" / "truck" | ~0.9-1.3 m | ~9-11 × ~3 × ~3 m | 0.32-0.53 | **False positive (near-field hallucination).** A ~10 m vehicle centred essentially at the sensor origin. The dense near-field returns (floor plane around the tripod, the rig, possibly the operator's legs) get explained by the model's "large vehicle near the ego" prior. The ~10 m length + near-zero centre range is the diagnostic signature. Class flips between `trailer` and `truck` across frames - itself a low-confidence instability marker. |
| "pedestrian" @ ~4.3 m | 4.33 m | ~0.6 × 0.6 × 1.77 m | 0.32-0.37 | Physically pedestrian-shaped box (0.6 m footprint, 1.77 m tall). **Candidate match to the blue-chair ground-truth marker at 4.00 m** (range over-estimate ~0.33 m; misclassified chair → pedestrian). NOTE: this is an interpretation, not confirmed - needs cross-check against the camera frame; a chair's vertical profile is plausibly pedestrian-like to the model, but the identity is not proven from LiDAR alone. |
| "pedestrian" @ ~5.3 m | 5.25-5.33 m | ~0.6 × 0.6 × 1.76 m | 0.31-0.36 | Pedestrian-shaped. No floor-tape ground-truth marker at this range; likely a real vertical object in the office (person, column, coat rack) outside the marked set. Not verifiable from the current ground truth. |

- **Frame 00100:** near-field false `trailer` (0.37) + two `pedestrian` @ 5.3 m (0.36, 0.34). (GUI re-run: three `pedestrian` 4.45-5.33 m, the trailer dropped just under threshold - score jitter around 0.30.)
- **Frame 00300:** near-field false `trailer` (0.43) + `pedestrian` @ 4.33 m (0.37) + `pedestrian` @ 5.30 m (0.32).
- **Frame 00500:** near-field false `truck` (0.50-0.52, highest-confidence detection of the run) + three/four `pedestrian` @ 4.33-5.33 m + a second near-field `trailer` (0.32).
- **Construction-class triggers observed:** **none.** No `construction_vehicle`, `barrier`, or `traffic_cone` above threshold in any frame. (The marked scene contained chairs and a doorway, none of which are construction objects, so this is expected; it does not test the construction-class hypothesis. A genuine construction-site recording is needed for that, Week 5+.)
- **Spurious detections:** the dominant spurious detection is the single large near-field `trailer`/`truck` present in every frame (1 per frame, occasionally 2 in frame 00500). Below the 0.30 threshold there are ~25-30 additional raw boxes per frame (visible as the grey wireframe clutter in the screenshots) - all low-confidence proposals the model is unsure about.

**Screenshots:** `docs/screenshots/d13_pointpillars_frame_{00100,00300,00500}.png` (Open3D, manual `box_colormap` extension to 11 entries to avoid the IndexError - see Patches below). The large cyan/magenta/yellow wireframe boxes spanning the cloud are the near-field hallucinated vehicle plus its lower-score siblings; the concentric arcs at frame centre are LiDAR rings on the floor immediately around the sensor; the red/green/blue triad marks the sensor origin. **Colour-to-class legend caveat:** `box_colormap` was extended in arbitrary colour order purely to stop the crash, so the box *colours* in these screenshots do NOT encode class in any documented way. The authoritative class labels are the printed `[DETECTIONS]` lines above, not the screenshot colours. For a thesis figure, either reorder `box_colormap` to match `cfg.CLASS_NAMES` and add a legend, or annotate the figure directly from the printed detections.

## Ground-truth distance read-out (§6.4)

Floor-tape markers from Day 3 recording (`d10_recording_manifest.md`), LiDAR-centre distances:

| Ground-truth object | GT range | Detected? | Detected as | Detected range | Notes |
|---|---|---|---|---|---|
| 100 cm chair | 1.00 m | No (not above threshold) | - | - | Sits inside the hallucinated near-field vehicle's footprint; also below the model's car/pedestrian size priors. The near field is dominated by the false trailer/truck. |
| doorway | 1.80 m | No (correctly) | - | - | A doorway is not an object class in the nuScenes label set; correctly produces no detection. |
| blue chair | 4.00 m | Candidate (unconfirmed) | pedestrian | 4.33 m | Range over-estimate ~0.33 m; class wrong (chair → pedestrian). Match is plausible but NOT confirmed - requires camera cross-check. |

**Range-accuracy note:** the one candidate match (blue chair) shows ~0.33 m over-estimate at 4 m (~8%). With only one unconfirmed correspondence this is anecdotal, not a calibrated range-accuracy figure; it cannot be reported as a measured error until the correspondence is confirmed against the camera and more markers are detected. Logged as a qualitative observation only.

## Patches applied to make Day 6 work (2026-05-28)

Four "2022 codebase on a 2026 dependency stack" patches were needed; all are recorded in `week02_step_by_step.md` §6 and `week02_log.md` Day 6 so a fresh clone can re-apply them:
1. **`pcdet/__init__.py`** - numpy>=1.24 compatibility shim restoring the removed `np.int` / `np.float` / `np.bool` / etc. aliases (OpenPCDet 0.6.0 uses them). Backup at `pcdet/__init__.py.bak`.
2. **`tools/demo.py` DemoDataset.__getitem__** - `reshape(-1, 4)` changed to read the channel count from the config (`len(self.dataset_cfg.POINT_FEATURE_ENCODING.src_feature_list)` = 5 for nuScenes), so the 5-channel `.bin` loads correctly.
3. **`tools/demo.py` main()** - replaced the GUI-only `V.draw_scenes(...)` call with a headless detection-summary print (class/score/position/size/range per box above threshold), and guarded the optional Open3D visualization behind a `VISUALIZE` flag. This is what produces the `[DETECTIONS]` log lines.
4. **`tools/visual_utils/open3d_vis_utils.py`** - `box_colormap` extended from 4 to >=11 entries so the 10-class nuScenes labels don't run off the end of the colour list (the IndexError that crashed the first GUI attempt). Cosmetic only; needed solely for the optional screenshots.

## Performance note
- Headless per-frame wall-clock ~17 s; GUI per-frame ~105-127 s. The difference is **not** compute - the GUI run blocks while the Open3D window is open (human view time). The ~17 s headless figure is itself dominated by cold-start overhead (Python imports + CUDA init + checkpoint load on each separate `demo.py` invocation); the actual forward pass is sub-second (the `[DETECTIONS]` line prints ~0.5-0.6 s after the checkpoint finishes loading). For the real-time fusion node in Week 4+, the model is loaded once and frames streamed, so per-frame latency will be governed by the forward pass, not the cold start.

## Final state (11:39:11)
- Free disk on $HOME: 153G
- **Outcome: PASS** - nuScenes-pretrained PointPillars-MultiHead runs end-to-end on Jetson on real bag-derived frames, produces stable detections across frames, and the results cleanly exhibit the expected LiDAR-only domain gap (near-field vehicle hallucination + chair→pedestrian misclassification + missed small objects + uniformly low confidence). This is the intended "before fusion" baseline and directly motivates the camera-classification fusion arm (DAL principle) in Week 3+.
