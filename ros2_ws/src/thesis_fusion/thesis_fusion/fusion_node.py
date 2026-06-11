#!/usr/bin/env python3
"""
fusion_node.py -- Week 4 Day 2 (d20) live ROS 2 fusion node (REAL association).

d23 additions: --sub-depth / --sync-queue expose the drop-to-latest queue policy (defaults 10/10
reproduce d19-d22 exactly); --profile-label sets the --profile summary header (was hardcoded
'(bag playback ...)'); main() guards rclpy.shutdown() with rclpy.ok() (the d22 launch Ctrl-C fix).

Day 1 (d19) proved the receive + decode + publish path with a stub. Day 2 swaps the stub body for the
REAL frustum association by CALLING the Week-3 offline functions (no second implementation of the math):
  - project()       from project_lidar.py   (campose projection LiDAR -> image)
  - associate_box() from frustum_fuse.py     (DBSCAN nearest-cluster, DAL: camera classifies / LiDAR locates)
  - load_calib()    from frustum_fuse.py     (R, t, intrinsics from calib.json -- loaded ONCE in __init__)
  - load_dbscan()   from frustum_fuse.py     (returns the sklearn DBSCAN class)

Per synced (RGB, cloud) pair:
  1. decode the Image to BGR (image_to_bgr, no cv_bridge) and the cloud xyz by field name (cloud_to_xyz);
  2. run YOLO once on the BGR frame -> 2D boxes (pixel xyxy, class, conf);
  3. project the cloud once (campose) -> (u, v, z, front, inb);
  4. for each box, associate_box() -> a fused 3D detection (LiDAR centroid + extent) or camera_only;
  5. publish a vision_msgs/Detection3DArray (header.frame_id="rslidar", stamp = image stamp) and a
     visualization_msgs/MarkerArray (one CUBE + one TEXT label per fused detection) for RViz.

DAL mapping into Detection3D (see "Message layout" below):
  - camera gives class + confidence -> results[0].hypothesis.class_id / .score
  - LiDAR  gives 3D centre + extent  -> bbox.center.position / bbox.size
  - camera_only (no qualifying cluster) -> class + conf only, bbox left zero (zero size flags camera_only).

Run (on the ZED Box; venv_yolo on PYTHONPATH so ultralytics/torch/sklearn resolve; ROS env sourced;
code/fusion on PYTHONPATH OR passed via --fusion-code-dir so project_lidar/frustum_fuse import):
    cd ~/Documents/workspace/sensor-fusion
    source ros2_ws/install/setup.bash
    export PYTHONPATH=$PWD/venv_yolo/lib/python3.10/site-packages:$PWD/code/fusion:$PYTHONPATH
    # in another terminal: ros2 bag play recordings/test2_marked_distances --loop
    ros2 run thesis_fusion fusion_node 2>&1 | tee /tmp/d20_node.log

------------------------------------------------------------------------------------------------------
Message layout -- vision_msgs (CONFIRMED against ros-perception/vision_msgs 'ros2' branch source, the
branch Humble is cut from). `to verify` on THIS box once: `ros2 interface show vision_msgs/msg/Detection3D`
and `.../ObjectHypothesisWithPose`. The nested paths the publish code below depends on are:

    Detection3DArray:  std_msgs/Header header ; Detection3D[] detections
    Detection3D:       std_msgs/Header header ; ObjectHypothesisWithPose[] results ;
                       BoundingBox3D bbox ; string id
    ObjectHypothesisWithPose:
                       ObjectHypothesis hypothesis        (-> .hypothesis.class_id [string], .hypothesis.score [float64])
                       geometry_msgs/PoseWithCovariance pose
    BoundingBox3D:     geometry_msgs/Pose center ; geometry_msgs/Vector3 size

Note the key trap this targets: in the Humble/ros2 API the class+score live UNDER `.hypothesis`
(results[i].hypothesis.class_id / .score), NOT directly on results[i]. The pre-4.0 API had
results[i].id / results[i].score. If `ros2 interface show` on this box shows the flat (id/score) form,
the build is older than expected -- adjust the two lines in build_detection() accordingly.
------------------------------------------------------------------------------------------------------
"""

import argparse
import os
import sys
import time

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from rclpy.time import Time   # d21: stamp-based end-to-end (publish-clock - image header stamp)

import message_filters
from std_msgs.msg import Header
from sensor_msgs.msg import Image, PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
from vision_msgs.msg import (
    Detection3DArray,
    Detection3D,
    ObjectHypothesisWithPose,
)
from visualization_msgs.msg import Marker, MarkerArray


#region [Optional heavy deps]
def load_yolo():
    """Import ultralytics.YOLO, with a clear message if venv_yolo is not on PYTHONPATH."""
    try:
        from ultralytics import YOLO
        return YOLO
    except ImportError:
        sys.exit("ERROR: could not import ultralytics. Run the node with venv_yolo on PYTHONPATH:\n"
                 "  export PYTHONPATH=$PWD/venv_yolo/lib/python3.10/site-packages:$PYTHONPATH")


def import_fusion_code(fusion_code_dir):
    """Import the Week-3 offline functions from code/fusion. They are CALLED, never reimplemented.

    frustum_fuse.py inserts its own directory onto sys.path at import time, so it resolves
    project_lidar by itself; we only have to make code/fusion importable here. Returns the four
    callables used by the node."""
    fusion_code_dir = os.path.expanduser(fusion_code_dir)
    if fusion_code_dir not in sys.path:
        sys.path.insert(0, fusion_code_dir)
    try:
        from project_lidar import project
        from frustum_fuse import load_calib, load_dbscan, associate_box
    except ImportError as exc:
        sys.exit(f"ERROR: could not import project_lidar/frustum_fuse from '{fusion_code_dir}'.\n"
                 f"  Pass the right path with --fusion-code-dir or add it to PYTHONPATH.\n"
                 f"  underlying import error: {exc}")
    return project, load_calib, load_dbscan, associate_box
#endregion


#region [Message decoding helpers]
def image_to_bgr(msg):
    """sensor_msgs/Image -> HxWx3 uint8 BGR numpy array, honouring msg.step, without cv_bridge.

    BGR is chosen to match the offline path (frustum_fuse.py fed cv2.imread BGR frames to YOLO), so the
    Day-2 parity holds. Raises on an unhandled encoding instead of guessing."""
    enc = msg.encoding.lower()
    channels = {"rgb8": 3, "bgr8": 3, "rgba8": 4, "bgra8": 4, "mono8": 1}
    if enc not in channels:
        raise ValueError(f"image_to_bgr: unhandled encoding '{msg.encoding}'. "
                         f"Add it to the channels map after checking msg.encoding on the bag.")
    ch = channels[enc]
    buf = np.frombuffer(msg.data, dtype=np.uint8)
    # msg.step is the row stride in bytes and may exceed width*ch (padding); slice it off.
    buf = buf.reshape(msg.height, msg.step)[:, : msg.width * ch].reshape(msg.height, msg.width, ch)
    if enc == "rgb8":
        return buf[:, :, ::-1].copy()
    if enc == "bgr8":
        return buf.copy()
    if enc == "rgba8":
        return buf[:, :, [2, 1, 0]].copy()
    if enc == "bgra8":
        return buf[:, :, [0, 1, 2]].copy()
    # mono8
    return np.repeat(buf, 3, axis=2)


def cloud_to_xyz(msg):
    """sensor_msgs/PointCloud2 -> Nx3 float64 xyz, read BY FIELD NAME (not a 5-channel reshape).

    The live cloud has 4 fields (x,y,z,intensity); the offline .bin had 5. Reading by field name is
    robust to both and to any point_step padding."""
    pts = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
    # In Humble read_points returns a numpy structured array; handle both that and a plain iterable.
    if hasattr(pts, "dtype") and pts.dtype.names is not None:
        xyz = np.stack([pts["x"], pts["y"], pts["z"]], axis=-1)
    else:
        xyz = np.array([[p[0], p[1], p[2]] for p in pts], dtype=np.float64)
    return np.asarray(xyz, dtype=np.float64).reshape(-1, 3)
#endregion


#region [Detection + marker construction]
def build_detection(header, cname, conf, assoc):
    """One associate_box() result -> one vision_msgs/Detection3D.

    fused      -> class+conf in results[0].hypothesis, 3D centre in bbox.center, extent in bbox.size.
    camera_only-> class+conf only; bbox left zero (a zero-size bbox is the camera_only flag downstream)."""
    det = Detection3D()
    det.header = header

    hyp = ObjectHypothesisWithPose()
    # CONFIRMED (ros2-branch source): class+score live under .hypothesis, not flat on results[i].
    hyp.hypothesis.class_id = str(cname)
    hyp.hypothesis.score = float(conf)
    det.results = [hyp]

    # identity orientation so RViz does not warn on a zero quaternion
    det.bbox.center.orientation.w = 1.0
    if assoc.get("source") == "fused":
        cx, cy, cz = assoc["position_lidar"]
        ex, ey, ez = assoc["extent"]
        det.bbox.center.position.x = float(cx)
        det.bbox.center.position.y = float(cy)
        det.bbox.center.position.z = float(cz)
        det.bbox.size.x = float(ex)
        det.bbox.size.y = float(ey)
        det.bbox.size.z = float(ez)
    # camera_only: bbox.size stays (0,0,0)
    return det


def build_markers(header, fused_list, ns="fusion"):
    """One MarkerArray for the frame: a leading DELETEALL clears the previous frame's markers, then a
    CUBE + a TEXT label ('class range_m') per fused detection. fused_list is a list of (cname, assoc)."""
    arr = MarkerArray()

    clear = Marker()
    clear.header = header
    clear.ns = ns
    clear.id = 0
    clear.action = Marker.DELETEALL
    arr.markers.append(clear)

    # Real markers start at id 1 so they never collide with the DELETEALL marker's (ns, id)=(fusion, 0).
    # RViz warns "Multiple Markers ... had the same ns and id" if any (ns, id) repeats within one array.
    mid = 1
    for cname, assoc in fused_list:
        cx, cy, cz = assoc["position_lidar"]
        ex, ey, ez = assoc["extent"]

        cube = Marker()
        cube.header = header
        cube.ns = ns
        cube.id = mid
        mid += 1
        cube.type = Marker.CUBE
        cube.action = Marker.ADD
        cube.pose.position.x = float(cx)
        cube.pose.position.y = float(cy)
        cube.pose.position.z = float(cz)
        cube.pose.orientation.w = 1.0
        # floor each side so a near-flat cluster still renders a visible box
        cube.scale.x = max(float(ex), 0.05)
        cube.scale.y = max(float(ey), 0.05)
        cube.scale.z = max(float(ez), 0.05)
        cube.color.r = 0.0
        cube.color.g = 0.8
        cube.color.b = 0.0
        cube.color.a = 0.5
        arr.markers.append(cube)

        text = Marker()
        text.header = header
        text.ns = ns
        text.id = mid
        mid += 1
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD
        text.pose.position.x = float(cx)
        text.pose.position.y = float(cy)
        text.pose.position.z = float(cz) + max(float(ez), 0.05) / 2.0 + 0.2
        text.pose.orientation.w = 1.0
        text.scale.z = 0.3
        text.color.r = 1.0
        text.color.g = 1.0
        text.color.b = 1.0
        text.color.a = 1.0
        text.text = f"{cname} {assoc['range_m']:.1f}m"
        arr.markers.append(text)

    return arr
#endregion


#region [Profiling]
# Per-stage latency profiler for --profile runs (d21). Holds steady-state samples after a warmup drop,
# computes mean/p50/p95 per stage, and renders a markdown summary table. OFF by default so the
# production path stays clean: when --profile is absent self.profiler is None and on_pair takes no
# timing measurements (its tic()/toc() helpers short-circuit without touching the clock).

PROFILE_STAGES = [
    ("image_decode", "image decode"),
    ("pc_to_xyz", "pointcloud->xyz"),
    ("yolo", "yolo inference"),
    ("projection", "projection"),
    ("dbscan", "dbscan assoc"),
    ("msg_build_pub", "msg build/pub"),
]


class LatencyProfiler:
    def __init__(self, warmup, window, report_every, label="bag playback"):
        self.warmup = int(warmup)
        self.window = int(window)
        self.report_every = int(report_every)
        self.label = str(label)         # d23: run label for the summary header (was hardcoded)
        self.n_seen = 0                 # profiled callbacks, including the dropped warmup ones
        self.first_ms = None            # first callback span (the warmup signal)
        self.full_reported = False
        keys = [k for k, _ in PROFILE_STAGES] + ["callback", "stamp"]
        self.data = {k: [] for k in keys}

    def add(self, stage_ms, callback_ms, stamp_ms):
        """Record one frame. Returns a log string when a rolling/full report is due, else None.

        callback_ms = wall-clock span of on_pair (entry -> just after publish): the robust,
        clock-alignment-independent end-to-end on bag playback. stamp_ms = publish-clock minus the
        image header stamp (only meaningful when clocks are aligned; guarded in the summary)."""
        self.n_seen += 1
        if self.first_ms is None:
            self.first_ms = callback_ms
        if self.n_seen <= self.warmup:
            return None
        if len(self.data["callback"]) >= self.window:
            if not self.full_reported:
                self.full_reported = True
                return ("steady-state window complete (N=%d):\n%s"
                        % (self.window, self.summary_markdown()))
            return None
        for k, _ in PROFILE_STAGES:
            self.data[k].append(float(stage_ms.get(k, float("nan"))))
        self.data["callback"].append(float(callback_ms))
        self.data["stamp"].append(float(stamp_ms))
        n = len(self.data["callback"])
        if self.report_every and (n % self.report_every == 0):
            return ("profiling %d/%d steady frames:\n%s"
                    % (n, self.window, self.summary_markdown()))
        return None

    def n_steady(self):
        return len(self.data["callback"])

    def _stats(self, key):
        arr = np.asarray(self.data[key], dtype=np.float64)
        if arr.size == 0 or np.all(np.isnan(arr)):
            return (float("nan"), float("nan"), float("nan"))
        return (float(np.nanmean(arr)),
                float(np.nanpercentile(arr, 50)),
                float(np.nanpercentile(arr, 95)))

    def summary_markdown(self):
        n = self.n_steady()
        lines = ["## Per-stage latency (%s, steady-state, N=%d)" % (self.label, n),
                 "| stage | mean ms | p50 | p95 |",
                 "|---|---|---|---|"]
        p50s = {}
        for key, label in PROFILE_STAGES:
            mean, p50, p95 = self._stats(key)
            p50s[label] = p50
            lines.append("| %-15s | %7.2f | %7.2f | %7.2f |" % (label, mean, p50, p95))

        cb_mean, cb_p50, cb_p95 = self._stats("callback")
        lines.append("| %-15s | %7.2f | %7.2f | %7.2f |"
                     % ("END-TO-END (cb)", cb_mean, cb_p50, cb_p95))

        # stamp-based end-to-end (publish-clock minus image header stamp): only meaningful when the
        # node clock and the header stamp share a timeline (live sensor in d22, or a bag played with
        # --clock and the node run with use_sim_time:=true). Reported only if the median is plausible.
        st_mean, st_p50, st_p95 = self._stats("stamp")
        if 0.0 < st_p50 < 5000.0:
            lines.append("| %-15s | %7.2f | %7.2f | %7.2f |"
                         % ("stamp e2e", st_mean, st_p50, st_p95))
        else:
            lines.append("- stamp-based end-to-end: N/A on this run (node clock and image header "
                         "stamp not aligned: use --clock + use_sim_time:=true on the bag, or "
                         "measure live in d22).")

        if cb_p50 == cb_p50 and cb_p50 > 0:   # not NaN and positive
            lines.append("- derived fps (1000 / p50 callback): %.2f Hz "
                         "(authoritative published fps = `ros2 topic hz`)" % (1000.0 / cb_p50))

        valid_p50 = {lab: p for lab, p in p50s.items() if p == p}
        if valid_p50:
            dom = max(valid_p50, key=valid_p50.get)
            lines.append("- dominant stage (by p50): %s (%.2f ms)" % (dom, valid_p50[dom]))

        warm = ("%.2f ms" % self.first_ms) if self.first_ms is not None else "<n/a>"
        steady = ("%.2f ms" % cb_p50) if cb_p50 == cb_p50 else "<n/a>"
        lines.append("- warmup (first frame) vs steady (p50 callback): %s / %s" % (warm, steady))
        return "\n".join(lines)

    def write_markdown(self, path):
        with open(os.path.expanduser(path), "w") as f:
            f.write(self.summary_markdown() + "\n")

    def write_csv(self, path):
        keys = [k for k, _ in PROFILE_STAGES] + ["callback", "stamp"]
        n = self.n_steady()
        with open(os.path.expanduser(path), "w") as f:
            f.write("frame," + ",".join(keys) + "\n")
            for i in range(n):
                row = [str(i)] + ["%.4f" % self.data[k][i] for k in keys]
                f.write(",".join(row) + "\n")
#endregion


#region [Fusion node]
class FusionNode(Node):
    def __init__(self, args):
        super().__init__("fusion_node")

        # ---- imports of the reused offline math (CALL, do not reimplement) ----
        (self.project, load_calib, load_dbscan,
         self.associate_box) = import_fusion_code(args.fusion_code_dir)
        self.DBSCAN = load_dbscan()

        # ---- calibration loaded ONCE here, never per callback ----
        calib_path = os.path.expanduser(args.calib)
        if not os.path.isfile(calib_path):
            sys.exit(f"ERROR: calib file not found: {calib_path} (pass --calib).")
        # load_calib returns (R, t, fx, fy, cx, cy); intrinsics come from the JSON when present.
        self.R, self.t, self.fx, self.fy, self.cx, self.cy = load_calib(
            calib_path, args.fx, args.fy, args.cx, args.cy)

        # ---- association params (defaults match frustum_fuse.py) ----
        self.conf = args.conf
        self.eps = args.eps
        self.min_samples = args.min_samples
        self.min_points = args.min_points
        self.shrink = args.shrink
        self.frame_id = args.frame_id

        # default reliable QoS: matches both publishers (P0 d19: RELIABLE/VOLATILE).
        # d23: depth is now an arg (--sub-depth, default 10 == d19-d22 behaviour); lowering it is half
        # of the drop-to-latest queue policy (the other half is --sync-queue below).
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=args.sub_depth,
        )

        # ---- model-load-ONCE: construct here, never in the callback ----
        YOLO = load_yolo()
        self.model = YOLO(args.model)
        self.get_logger().info(f"model loaded once at startup: {args.model}")

        # ---- publishers ----
        self.pub_det = self.create_publisher(Detection3DArray, args.det_topic, 10)
        self.pub_mark = self.create_publisher(MarkerArray, args.marker_topic, 10)

        # ---- synced subscribers (qos_profile kwarg CONFIRMED working on this Humble build in d19) ----
        self.sub_rgb = message_filters.Subscriber(self, Image, args.rgb_topic, qos_profile=qos)
        self.sub_cloud = message_filters.Subscriber(self, PointCloud2, args.cloud_topic, qos_profile=qos)
        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.sub_rgb, self.sub_cloud], queue_size=args.sync_queue, slop=0.1)   # d23: was 10
        self.sync.registerCallback(self.on_pair)

        # ---- rate bookkeeping ----
        self.n_pairs = 0
        self.n_since_log = 0
        self.t_last_log = time.monotonic()

        # ---- latency profiling (d21; OFF unless --profile) ----
        self.profile = bool(args.profile)
        self.profiler = (LatencyProfiler(args.profile_warmup, args.profile_window,
                                         args.profile_report_every, args.profile_label)
                         if self.profile else None)
        self._profile_csv = args.profile_csv
        self._profile_out = args.profile_out
        if self.profile:
            self.get_logger().info(
                f"PROFILE ON: drop first {args.profile_warmup} frames, then record the next "
                f"{args.profile_window} (rolling report every {args.profile_report_every}); "
                f"csv='{args.profile_csv}' summary='{args.profile_out}'.")

        self.get_logger().info(
            f"subscribed RGB='{args.rgb_topic}' CLOUD='{args.cloud_topic}'; "
            f"publishing detections='{args.det_topic}' markers='{args.marker_topic}'; "
            f"frame_id='{self.frame_id}'; ApproximateTimeSynchronizer "
            f"queue={args.sync_queue} slop=0.1; sub_depth={args.sub_depth}; "
            f"conf={self.conf} eps={self.eps} min_samples={self.min_samples} "
            f"min_points={self.min_points} shrink={self.shrink}")

    def _publish_empty(self, stamp):
        """Heartbeat on a decode/association failure: empty detections + a DELETEALL marker so the node
        never goes silent and stale markers do not linger."""
        hdr = Header()
        hdr.stamp = stamp
        hdr.frame_id = self.frame_id
        out = Detection3DArray()
        out.header = hdr
        out.detections = []
        self.pub_det.publish(out)
        self.pub_mark.publish(build_markers(hdr, []))

    def on_pair(self, img_msg, cloud_msg):
        self.n_pairs += 1
        self.n_since_log += 1

        prof = self.profiler            # None unless --profile

        def tic():
            return time.perf_counter() if prof is not None else 0.0

        def toc(t0):
            return (time.perf_counter() - t0) * 1e3 if prof is not None else 0.0

        t_cb0 = tic()
        stage_ms = {}

        # header for everything downstream: LiDAR frame (where centroid/extent live), image stamp
        # (keeps the stamp-based end-to-end anchor = publish_stamp - image_header_stamp for d22 live).
        hdr = Header()
        hdr.stamp = img_msg.header.stamp
        hdr.frame_id = self.frame_id

        try:
            # (1) image decode (bgra8 -> BGR, no cv_bridge)
            _t = tic()
            bgr = image_to_bgr(img_msg)
            stage_ms["image_decode"] = toc(_t)

            # (2) pointcloud -> xyz (read by field name)
            _t = tic()
            xyz = cloud_to_xyz(cloud_msg)
            stage_ms["pc_to_xyz"] = toc(_t)

            H, W = bgr.shape[:2]

            # (3) YOLO once on the BGR frame. The .cpu().numpy() extraction forces the CUDA sync, so
            #     this span captures the real GPU inference time, not just the async kernel launch.
            _t = tic()
            res = self.model(bgr, conf=self.conf, verbose=False)[0]
            names = res.names
            xyxy = res.boxes.xyxy.cpu().numpy()
            cls = res.boxes.cls.cpu().numpy().astype(int)
            conf = res.boxes.conf.cpu().numpy()
            stage_ms["yolo"] = toc(_t)

            # (4) project the cloud once (campose)
            _t = tic()
            u, v, z, front, inb = self.project(
                xyz, self.R, self.t, self.fx, self.fy, self.cx, self.cy, W, H, "campose")
            stage_ms["projection"] = toc(_t)

            # (5) associate every box (DBSCAN nearest-cluster). Association is now separated from
            #     message building so the two stages time cleanly; box order is unchanged so parity
            #     vs fused_out/ is unaffected.
            _t = tic()
            assoc_results = []
            for i in range(len(xyxy)):
                box = [float(c) for c in xyxy[i]]
                assoc = self.associate_box(
                    box, xyz, u, v, front, self.DBSCAN,
                    self.eps, self.min_samples, self.min_points, self.shrink)
                assoc_results.append((names[cls[i]], conf[i], assoc))
            stage_ms["dbscan"] = toc(_t)

            # (6) build the Detection3DArray + MarkerArray and publish
            _t = tic()
            out = Detection3DArray()
            out.header = hdr
            fused_for_markers = []
            n_fused = 0
            for cname, cconf, assoc in assoc_results:
                out.detections.append(build_detection(hdr, cname, cconf, assoc))
                if assoc.get("source") == "fused":
                    n_fused += 1
                    fused_for_markers.append((cname, assoc))
            self.pub_det.publish(out)
            self.pub_mark.publish(build_markers(hdr, fused_for_markers))
            stage_ms["msg_build_pub"] = toc(_t)

        except Exception as exc:   # noqa: BLE001 -- keep the live node alive; surface error, heartbeat empty
            self.get_logger().error(f"on_pair failed (publishing empty heartbeat): {exc}")
            self._publish_empty(img_msg.header.stamp)
            return

        # ---- profiling bookkeeping (only after a successful publish) ----
        if prof is not None:
            callback_ms = toc(t_cb0)
            try:
                t_hdr = Time.from_msg(img_msg.header.stamp)
                stamp_ms = (self.get_clock().now() - t_hdr).nanoseconds / 1e6
            except Exception:   # noqa: BLE001 -- never let timing kill the live node
                stamp_ms = float("nan")
            report = prof.add(stage_ms, callback_ms, stamp_ms)
            if report:
                self.get_logger().info(report)

        # once-per-second rate + a compact detection count
        now = time.monotonic()
        if now - self.t_last_log >= 1.0:
            rate = self.n_since_log / (now - self.t_last_log)
            self.get_logger().info(
                f"paired-callback rate: {rate:.2f} Hz (total pairs {self.n_pairs}); "
                f"last frame: {len(out.detections)} dets, {n_fused} fused")
            self.n_since_log = 0
            self.t_last_log = now

    def report_profile(self):
        """Print the steady-state summary and write CSV + markdown. Called once at shutdown; a no-op
        when --profile is off or no steady samples were collected."""
        if self.profiler is None:
            return
        if self.profiler.n_steady() == 0:
            self.get_logger().warn(
                "PROFILE: no steady-state samples collected (window not reached). Lower "
                "--profile-warmup or run the bag longer before stopping the node.")
            return
        self.get_logger().info("PROFILE final summary:\n" + self.profiler.summary_markdown())
        try:
            if self._profile_csv:
                self.profiler.write_csv(self._profile_csv)
                self.get_logger().info(f"PROFILE: per-frame CSV -> {self._profile_csv}")
            if self._profile_out:
                self.profiler.write_markdown(self._profile_out)
                self.get_logger().info(f"PROFILE: summary markdown -> {self._profile_out}")
        except Exception as exc:   # noqa: BLE001
            self.get_logger().error(f"PROFILE: failed writing outputs: {exc}")
#endregion


#region [Main]
def main():
    home = os.path.expanduser("~")
    repo = os.path.join(home, "Documents", "workspace", "sensor-fusion")

    ap = argparse.ArgumentParser()
    # topics / output
    ap.add_argument("--rgb-topic", default="/zed/zed_node/rgb/color/rect/image")
    ap.add_argument("--cloud-topic", default="/rslidar_points")
    ap.add_argument("--det-topic", default="/fusion/detections")
    ap.add_argument("--marker-topic", default="/fusion/markers")
    ap.add_argument("--frame-id", default="rslidar",
                    help="frame of the published detections/markers (LiDAR frame)")
    # model + reused code
    ap.add_argument("--model", default="yolov8s.pt")
    ap.add_argument("--fusion-code-dir", default=os.path.join(repo, "code", "fusion"),
                    help="directory holding project_lidar.py + frustum_fuse.py")
    ap.add_argument("--calib", default=os.path.join(repo, "calibration",
                                                    "calib_T_lidar_camera_2026_05_26.json"))
    # association params (defaults match frustum_fuse.py)
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--eps", type=float, default=0.3)
    ap.add_argument("--min-samples", type=int, default=5)
    ap.add_argument("--min-points", type=int, default=10)
    ap.add_argument("--shrink", type=float, default=1.0)
    # intrinsics fallback (load_calib overrides these from the JSON when present)
    ap.add_argument("--fx", type=float, default=335.13)
    ap.add_argument("--fy", type=float, default=359.35)
    ap.add_argument("--cx", type=float, default=486.26)
    ap.add_argument("--cy", type=float, default=291.70)
    # profiling (d21) -- OFF by default so the production path stays clean
    ap.add_argument("--profile", action="store_true",
                    help="enable per-stage + end-to-end latency timing (d21)")
    ap.add_argument("--profile-warmup", type=int, default=30,
                    help="drop this many frames before recording (model/CUDA warmup)")
    ap.add_argument("--profile-window", type=int, default=200,
                    help="record this many steady-state frames, then stop recording")
    ap.add_argument("--profile-report-every", type=int, default=50,
                    help="log a rolling summary every N recorded frames (0 = only at the end)")
    ap.add_argument("--profile-csv", default="/tmp/d21_latency.csv",
                    help="per-frame stage times CSV (re-analysed by latency_summary.py)")
    ap.add_argument("--profile-out", default="/tmp/d21_latency_summary.md",
                    help="markdown summary table written at shutdown")
    ap.add_argument("--profile-label", default="bag playback",
                    help="run label printed in the --profile summary header "
                         "(d23; e.g. 'live, default queues' / 'live, drop-to-latest' / 'bag, TensorRT')")
    # d23 drop-to-latest queue policy: shallow subscription depth + small synchronizer queue cap the
    # standing input backlog so the node processes the FRESHEST pair instead of draining a stale queue.
    # Defaults 10/10 reproduce d19-d22 exactly (a defaults run == the d22 'before').
    ap.add_argument("--sub-depth", type=int, default=10,
                    help="per-topic subscription QoS KEEP_LAST depth (d23: lower for drop-to-latest)")
    ap.add_argument("--sync-queue", type=int, default=10,
                    help="ApproximateTimeSynchronizer queue_size (d23: lower for drop-to-latest)")
    # rclpy may inject its own args under ros2 run; parse only ours.
    args, _ = ap.parse_known_args()

    rclpy.init()
    node = FusionNode(args)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.report_profile()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
#endregion
