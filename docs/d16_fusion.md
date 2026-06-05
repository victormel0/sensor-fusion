# Day 3 (d16) frustum-fusion manifest -- 2026-06-04

**Strategy (D2):** DBSCAN -> nearest qualifying cluster; min-point guard; central-box shrink; AABB extent; position in LiDAR frame.

## scikit-learn install check
    numpy=1.26.4 sklearn=1.7.2 torch_cuda=True
    bridge [1. 2.]
## Parameters
- YOLO model: yolov8s.pt; conf threshold: 0.25
- direction: campose (Day-2 confirmed); DBSCAN eps: 0.3 m; min_samples: 5
- min-point guard: 10 (below -> camera-only); central-box shrink: off (1.0)

## Per-frame association (in-box points -> chosen cluster)
### Frame 00100
frame 00100.png: 11 boxes, 24624 pts in front, image 960x600
  box 0 chair 0.94: in_box=2766 clusters=5 -> FUSED pos=(1.50,-0.92,-0.33) range=1.76m extent=(0.95,1.50,1.30) n=2310
  box 1 tv 0.84: in_box=374 clusters=2 -> FUSED pos=(1.74,1.59,0.09) range=2.35m extent=(0.46,0.63,0.37) n=324
  box 2 tv 0.83: in_box=575 clusters=3 -> FUSED pos=(1.73,1.03,0.09) range=2.01m extent=(0.30,0.72,0.32) n=467
  box 3 tv 0.68: in_box=108 clusters=1 -> FUSED pos=(1.69,2.00,0.07) range=2.62m extent=(0.17,0.35,0.25) n=106
  box 4 chair 0.62: in_box=393 clusters=6 -> FUSED pos=(4.46,0.09,-0.40) range=4.46m extent=(0.67,0.62,1.11) n=284
  box 5 laptop 0.53: in_box=113 clusters=1 -> FUSED pos=(1.81,-1.99,-0.11) range=2.69m extent=(0.42,0.61,0.23) n=113
  box 6 tv 0.40: in_box=93 clusters=3 -> FUSED pos=(5.27,-0.44,0.03) range=5.29m extent=(0.38,0.46,0.25) n=60
  box 7 laptop 0.34: in_box=100 clusters=3 -> FUSED pos=(5.28,-0.43,0.03) range=5.29m extent=(0.38,0.48,0.25) n=62
  box 8 keyboard 0.34: in_box=177 clusters=1 -> FUSED pos=(1.55,1.70,-0.19) range=2.30m extent=(0.80,0.75,0.18) n=177
  box 9 person 0.32: in_box=398 clusters=6 -> FUSED pos=(4.46,0.10,-0.41) range=4.46m extent=(0.67,0.64,1.11) n=287
  box 10 tv 0.26: in_box=49 clusters=1 -> FUSED pos=(8.03,0.69,0.77) range=8.06m extent=(0.10,0.44,0.43) n=48
  viz -> docs/screenshots/d16_clusters_00100.png
  11/11 fused (rest camera-only) -> code/fusion/fused_out/00100.json
### Frame 00300
frame 00300.png: 10 boxes, 24653 pts in front, image 960x600
  box 0 chair 0.95: in_box=2752 clusters=5 -> FUSED pos=(1.50,-0.92,-0.33) range=1.76m extent=(0.94,1.50,1.30) n=2295
  box 1 tv 0.82: in_box=382 clusters=2 -> FUSED pos=(1.73,1.59,0.09) range=2.35m extent=(0.64,0.69,0.39) n=327
  box 2 tv 0.70: in_box=568 clusters=4 -> FUSED pos=(1.73,1.03,0.09) range=2.01m extent=(0.30,0.72,0.32) n=466
  box 3 tv 0.70: in_box=109 clusters=1 -> FUSED pos=(1.69,2.00,0.06) range=2.62m extent=(0.19,0.36,0.25) n=109
  box 4 person 0.55: in_box=502 clusters=8 -> FUSED pos=(4.31,0.12,-0.43) range=4.31m extent=(0.60,0.76,1.11) n=303
  box 5 chair 0.52: in_box=442 clusters=6 -> FUSED pos=(4.31,0.11,-0.45) range=4.31m extent=(0.60,0.73,1.11) n=281
  box 6 laptop 0.47: in_box=107 clusters=1 -> FUSED pos=(1.81,-1.98,-0.12) range=2.68m extent=(0.42,0.61,0.23) n=107
  box 7 tv 0.36: in_box=93 clusters=3 -> FUSED pos=(5.27,-0.44,0.03) range=5.29m extent=(0.39,0.47,0.25) n=60
  box 8 tv 0.32: in_box=53 clusters=2 -> FUSED pos=(8.03,0.69,0.77) range=8.06m extent=(0.11,0.44,0.44) n=48
  box 9 laptop 0.30: in_box=92 clusters=2 -> FUSED pos=(5.28,-0.44,0.03) range=5.29m extent=(0.39,0.47,0.25) n=61
  viz -> docs/screenshots/d16_clusters_00300.png
  10/10 fused (rest camera-only) -> code/fusion/fused_out/00300.json
### Frame 00500
frame 00500.png: 10 boxes, 24511 pts in front, image 960x600
  box 0 chair 0.94: in_box=2765 clusters=5 -> FUSED pos=(1.50,-0.92,-0.33) range=1.76m extent=(0.96,1.49,1.30) n=2303
  box 1 tv 0.83: in_box=373 clusters=2 -> FUSED pos=(1.74,1.59,0.09) range=2.35m extent=(0.46,0.64,0.37) n=322
  box 2 tv 0.79: in_box=572 clusters=5 -> FUSED pos=(1.73,1.03,0.09) range=2.01m extent=(0.30,0.73,0.31) n=467
  box 3 tv 0.77: in_box=109 clusters=1 -> FUSED pos=(1.69,2.00,0.06) range=2.62m extent=(0.20,0.37,0.25) n=109
  box 4 tv 0.43: in_box=93 clusters=3 -> FUSED pos=(5.27,-0.45,0.03) range=5.29m extent=(0.37,0.45,0.25) n=59
  box 5 chair 0.39: in_box=416 clusters=6 -> FUSED pos=(4.31,0.09,-0.40) range=4.31m extent=(0.90,0.67,1.10) n=312
  box 6 keyboard 0.37: in_box=191 clusters=1 -> FUSED pos=(1.56,1.71,-0.19) range=2.31m extent=(0.80,0.76,0.19) n=191
  box 7 laptop 0.33: in_box=100 clusters=1 -> FUSED pos=(1.80,-1.97,-0.11) range=2.67m extent=(0.49,0.61,0.23) n=100
  box 8 tv 0.31: in_box=52 clusters=1 -> FUSED pos=(8.03,0.69,0.77) range=8.06m extent=(0.11,0.44,0.44) n=48
  box 9 person 0.28: in_box=416 clusters=6 -> FUSED pos=(4.31,0.09,-0.40) range=4.31m extent=(0.90,0.67,1.10) n=312
  viz -> docs/screenshots/d16_clusters_00500.png
  10/10 fused (rest camera-only) -> code/fusion/fused_out/00500.json

## Final state (12:34:15)
- Fused detections produced for 00100/00300/00500: yes -- 11/11, 10/10, 10/10 boxes fused.
- Camera-only fallbacks triggered (too few points): none. Every box had >=49 in-box points (min 49 for the far-back tv @8 m), all above the 10-point guard. The guard was not exercised on this dense indoor scene; it will matter more on sparse/distant objects.
- Day 3 outcome: PASS.

## Key findings (for Day 4 / thesis)
- Depth disambiguation validated: the doorway box (person-in-blue-chair) contained 6-8 clusters because the frustum sweeps through the open door/glass to the far room (5-8 m); the nearest-cluster rule selected the ~4.3 m cluster and rejected the far-room background. The exact case the design targeted, handled.
- Cross-validation: the fused centroid of the ~4.3 m object is 4.31 m (00300) / 4.46 m (00100), agreeing to a few cm with the Day-6 LiDAR-only `pedestrian @4.33 m`. Both are LiDAR-derived, so the match confirms projection + clustering are geometrically sound.
- Stable foreground: the tan high-back chair is `chair` @1.76 m across all three frames (conf 0.94-0.95).
- Person-in-chair: detected as both `chair` and `person` (overlapping boxes), both fusing to the same cluster/range -> duplicate fused detections at one object (no cross-class NMS).
- Near field: no camera box and no fused detection at ~1 m (the Day-6 trailer/truck hallucination region). Suppression to be stated as before/after once aligned against the Day-6 per-frame detections.
- Limitations: at eps=0.3 m the tan-chair cluster over-merged with the adjacent desk (y-extent 1.50 m inflated); range/centroid still reasonable but extents for large near boxes are unreliable. Far-room objects (tv/laptop @5.3-8 m) are detected through glass/doorway (noisy returns, d10) but clustered enough to localise.
