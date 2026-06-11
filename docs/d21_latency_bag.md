# Day 3 (d21) latency (bag playback) manifest -- 2026-06-09

**Power profile (nvpmodel -q):**
```
NV Power Mode: MAXN
0
```
# MAXN (mode ID 0) is the current/default mode on this box; closes the 2026-05-26 open
# decision -- see the decision note in 3.2.


## Per-stage latency (bag playback, steady-state, N=66)
| stage | mean ms | p50 | p95 |
|---|---|---|---|
| image decode    |    5.15 |    5.07 |    5.47 |
| pointcloud->xyz |    1.94 |    1.83 |    2.32 |
| yolo inference  |   63.50 |   61.47 |   79.35 |
| projection      |    4.91 |    3.03 |   14.90 |
| dbscan assoc    |   85.81 |   83.57 |   99.93 |
| msg build/pub   |    4.80 |    4.90 |    5.73 |
| END-TO-END (cb) |  166.18 |  161.98 |  198.95 |
- stamp-based end-to-end: N/A on this run (node clock and image header stamp not aligned: use --clock + use_sim_time:=true on the bag, or measure live in d22).
- derived fps (1000 / p50 callback): 6.17 Hz (authoritative published fps = `ros2 topic hz`)
- dominant stage (by p50): dbscan assoc (83.57 ms)
- warmup (first frame) vs steady (p50 callback): 1327.46 ms / 161.98 ms
- published fps (ros2 topic hz /fusion/detections): ~5.9 Hz (settled ~5.93 Hz over the 92-sample window; per-message interval min 0.145 s / max 0.222 s, std dev ~0.015 s). Raw samples:
user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ stdbuf -oL ros2 topic hz /fusion/detections
average rate: 5.808
	min: 0.153s max: 0.220s std dev: 0.02019s window: 8
average rate: 6.046
	min: 0.150s max: 0.220s std dev: 0.01698s window: 15
average rate: 6.079
	min: 0.150s max: 0.220s std dev: 0.01484s window: 22
average rate: 6.053
	min: 0.150s max: 0.220s std dev: 0.01379s window: 28
average rate: 6.070
	min: 0.150s max: 0.220s std dev: 0.01276s window: 35
average rate: 6.023
	min: 0.150s max: 0.220s std dev: 0.01289s window: 41
average rate: 5.976
	min: 0.150s max: 0.220s std dev: 0.01401s window: 47
average rate: 5.981
	min: 0.150s max: 0.220s std dev: 0.01376s window: 54
average rate: 5.969
	min: 0.150s max: 0.222s std dev: 0.01511s window: 60
average rate: 5.958
	min: 0.150s max: 0.222s std dev: 0.01502s window: 66
average rate: 5.965
	min: 0.146s max: 0.222s std dev: 0.01521s window: 73
average rate: 5.947
	min: 0.145s max: 0.222s std dev: 0.01614s window: 80
average rate: 5.946
	min: 0.145s max: 0.222s std dev: 0.01594s window: 86
average rate: 5.931
	min: 0.145s max: 0.222s std dev: 0.01588s window: 92


## Final state (11:03:33)
- Dominant stage: DBSCAN association (p50 83.57 ms, p95 99.93 ms) -- NOT YOLO (p50 61.47 ms); overturns the pre-run anchor. DBSCAN + YOLO together ~145 ms (~90%) of the ~162 ms median.
- End-to-end (callback span) p50 / p95: 161.98 / 198.95 ms. (Six stage means sum to 166.11 ms vs the e2e mean 166.18 ms, so the timers account for essentially all callback time.)
- fps: published ~5.9 Hz (ros2 topic hz, settled ~5.93 over 92 samples); derived fps (1000/p50 cb): 6.17 Hz; power profile: MAXN (mode 0).
- vs the 200 ms aim / 500 ms acceptable (task plan): WITHIN the 200 ms aim across the whole steady-state window (p50 162 ms; p95 198.95 ms, right at the 200 ms boundary); far under the 500 ms acceptable.
- jitter signal (p95 - p50 of callback span): 36.97 ms (~23% of the p50); over-current throttle notices seen?: none in the window.
- N note: window stopped at N=66 (Ctrl-C), not the planned 200; p50s converged (N=50 rolling vs N=66 final differ <1 ms/stage), p95 tail provisional.
- Day 3 outcome: PASS.
