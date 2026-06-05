# Day 1 (d14) camera-detection manifest -- 2026-06-02

**Goal:** resolve lens/FoV from camera_info; stand up venv_yolo; run YOLOv8 on the 3 comparison RGB frames.

**Initial free disk on $HOME:** 153G

## camera_info (read directly from the bag)
[INFO] [1780435901.463968618] [rosbag2_storage]: Opened database 'recordings/test2_marked_distances/test2_marked_distances_0.db3' for READ_ONLY.
- image size: 960x600
- distortion_model: rational_polynomial
- D: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- K:  fx=335.13 fy=359.35 cx=486.26 cy=291.70
- P:  fx'=335.13 fy'=359.35 cx'=486.26 cy'=291.70 Tx=0.0000
- implied HFOV=110.2 deg  VFOV=79.7 deg  fx/fy=0.933
- matches calib.json fx=335.13 ? yes -> ~110 deg confirmed

## venv_yolo
- Path: ~/Documents/workspace/sensor-fusion/venv_yolo
- Python: Python 3.10.12
- pip check:
    No broken requirements found.
- torch/cuda/numpy-bridge check:
    torch=2.8.0 cuda_available=True cuda_build=12.6
    numpy=1.26.4 ultralytics=8.4.60 opencv=4.9.0
    gpu=Orin
    torch->numpy bridge: [          1           2           3]
- pip-freeze snapshot: docs/d14_venv_yolo_freeze.txt

## Frame extraction (time-matched RGB for LiDAR frames 100/300/500)
[INFO] [1780437450.930737970] [rosbag2_storage]: Opened database 'recordings/test2_marked_distances/test2_marked_distances_0.db3' for READ_ONLY.
[INFO] [1780437454.197569320] [rosbag2_storage]: Opened database 'recordings/test2_marked_distances/test2_marked_distances_0.db3' for READ_ONLY.
00100: dt=  6.85 ms
00300: dt=  7.35 ms
00500: dt=  7.14 ms
done: 3 frame(s) -> code/fusion/frames_out

## YOLOv8 inference (yolov8s, COCO)
- Model: yolov8s.pt (COCO-pretrained); weights auto-download on first run
- Start: 22:00:09
- End: 22:00:22, duration 13s
- Per-image timing (from the ultralytics Speed line, authoritative):
    7.5 ms preprocess, 92.1 ms inference, 12.0 ms postprocess per image at (1, 3, 416, 640)
    first image cold-start 132.9 ms; steady-state inference ~70-92 ms; ~111 ms/frame total (~9 fps, yolov8s, Orin, no TensorRT)
- Per-image detections (clean, from the annotated output; the earlier grep captured model-summary noise and is superseded):
    00100: chair 0.94 (tan, R), chair 0.62 + person 0.34 (blue chair w/ seated person, centre), tv 0.84/0.83/0.68/0.26 + 1 more (monitors), keyboard 0.34, laptop 0.53 (+1 low)  -> log count: 1 person, 2 chairs, 5 tvs, 2 laptops, 1 keyboard
    00300: chair 0.95 (tan, R), person 0.55 + chair ~0.30 (blue chair w/ seated person, centre), tv 0.82/0.70/0.70/0.32 + 1 more, laptop 0.47 (+1 low)  -> log count: 1 person, 2 chairs, 5 tvs, 2 laptops
    00500: chair 0.94 (tan, R), chair + person (blue chair w/ seated person, centre), tv 0.83/0.79/0.77/0.43/0.31, keyboard 0.37, laptop 0.33  -> log count: 1 person, 2 chairs, 5 tvs, 1 laptop, 1 keyboard
- Class set across the three frames: {person, chair, tv, laptop, keyboard}. No construction classes (expected; COCO).
- Annotated images saved to: code/fusion/yolo_out/d14/ (moved there from runs/detect/code/fusion/yolo_out/d14/;
  ultralytics treats a relative `project` as relative to its runs_dir -- step-by-step §1.4 now uses an absolute path).

## Qualitative inspection (against the d10 scene + ground-truth note)
- Tan high-back leather chair, right foreground: detected consistently as `chair` at 0.94-0.95. Not a d10 GT marker but a real, unambiguous chair; good high-confidence anchor.
- Blue chair @ ~4 m through the doorway (d10 GT "blue chair @4.00 m"), in `test2_marked_distances` only: **a person is seated in it, but barely visible** -- not facing the camera, ~4 m through the doorway, only shoes, part of the legs, and one arm showing. YOLO accordingly puts overlapping `chair` and `person` boxes on it with the dominant label flipping per frame (chair 00100/00500, person 00300). The object is a person-in-chair: neither the camera's chair/person nor the Day-6 LiDAR-only `pedestrian @4.33 m` is clearly wrong, but **we cannot determine whether either model detected the person or the chair** -- it stays a candidate / ambiguous correspondence, NOT a confirmed person detection. An ambiguous or missed person here is expected given the visibility, not a method failure. The d10 GT label (scoped to test2) omitted the person and should be annotated; other recordings did not have a person in the blue chair.
- Monitors on the left and right desks -> `tv` (0.26-0.84). Laptops -> `laptop` (0.33-0.53). A keyboard on the left desk -> `keyboard` (0.34-0.37). All plausible COCO mappings of the office.
- 100 cm black chair @1 m (d10 foreground GT, which LiDAR-only MISSED): not clearly visible in these frames either (likely below/outside the monocular FoV or occluded by the desk ledge in the lower foreground). Confirm against the Day-2 LiDAR overlay before concluding either modality "sees" it.

## Final state (22:06:11)
- Free disk on $HOME: 151G
- Lens/FoV verdict: ~110 deg confirmed (camera_info K matches calib.json; the "59 deg" readout was the anomaly)
- venv_yolo: cuda True, numpy 1.26.4, ultralytics 8.4.60, opencv-python 4.9.0.80; pip check clean; venv_openpcdet untouched
- YOLOv8 class set + steady ms/frame: {person, chair, tv, laptop, keyboard}; ~92 ms inference/frame (yolov8s, Orin, no TensorRT)
- Scene note (test2 only): the ~4 m doorway object is a person seated in the blue chair but barely visible (shoes/partial legs/one arm, not facing camera). Person-in-chair; cannot confirm whether camera or LiDAR detected the person vs the chair -- candidate/ambiguous, not a confirmed person detection. Near-field trailer/truck stays the clean fusion-suppression case. See Qualitative inspection.
- Day 1 outcome: PASS
