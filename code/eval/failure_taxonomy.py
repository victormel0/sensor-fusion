#!/usr/bin/env python3
"""
failure_taxonomy.py -- d32: RGB failure-case taxonomy on the d26 evaluation data.

Run:
  python3 code/eval/failure_taxonomy.py \
      --gt docs/gt \
      --runs code/eval/runs \
      --per-match docs/d26_metrics/per_match.csv \
      --out docs/d32_failure \
      --fig docs/screenshots/d32_fig_failure_modes.png

WHAT IT DOES (and what it deliberately does NOT do):
- IMPORTS iou / greedy_match_2d / canon / loaders from metrics.py and re-runs the SAME class-agnostic
  greedy 2D match (iou >= --iou over NON-occluded GT, detections below --yolo-conf dropped first), so
  every total reconciles with the official d26 numbers BY CONSTRUCTION. metrics.py is not modified.
- Buckets every ASSESSABLE GT instance into: TP_correct_class / TP_wrong_class / FN.
- Buckets every detection into: TP / FP, and sub-buckets each FP into:
    duplicate_detection        (IoU >= thr with an assessable GT already taken by another det)
    matches_occluded_gt        (IoU >= thr with an OCCLUDED GT -- excluded from assessment by design)
    partial_overlap_below_iou  (0 < max IoU with any GT < thr -- localization near-miss)
    no_gt_overlap              (zero IoU with any GT -- outside the annotation scope, e.g. doorway)
- Reconciliation line per env: assessable / TP / FN / FP / class_err. CHECK these against the d26
  presence table before trusting any breakdown.
- Optional cross-check vs per_match.csv: fused rows there must equal TP pairs with source=="fused"
  and a GT tape range here.

OUTPUTS (all under --out):
  instances.csv            one row per assessable GT instance (bucket + pred + conf + range)
  detections.csv           one row per detection (bucket + sub-bucket + max-IoU diagnostics)
  reconciliation.md        the per-env totals to check against d26
  taxonomy_by_object.md    per raw GT class: assessable / TP-correct / TP-wrong-class / FN + ranges
  taxonomy_by_env_pose.md  same buckets split by env and pose
  class_errors.md          every wrong-class match, one line each
  fp_analysis.md           FP sub-buckets per env, with predicted classes
Figure (--fig): stacked per-class outcome bars (env-2 focus) + FP sub-bucket bars per env.
"""

#region [Imports + CLI]
import argparse
import csv
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as M


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True, help="GT root (same as metrics.py --gt)")
    ap.add_argument("--runs", required=True, help="runs root containing fused/ (same as metrics.py --runs)")
    ap.add_argument("--out", required=True, help="output directory for csv/md tables")
    ap.add_argument("--fig", default=None, help="path for the failure-modes figure (png)")
    ap.add_argument("--per-match", default=None, help="optional d26 per_match.csv for a cross-check")
    ap.add_argument("--iou", type=float, default=0.50)
    ap.add_argument("--yolo-conf", type=float, default=0.25)
    return ap.parse_args()
#endregion

#region [Bucketing (mirrors metrics.py main() accounting exactly)]
def bucket_env(gt, fused, env, iou_thr, conf_thr):
    inst_rows, det_rows = [], []
    tot = {"assessable": 0, "tp": 0, "fn": 0, "fp": 0, "class_err": 0, "tp_range_rows": 0}
    fkeys = sorted(k for k in gt if gt[k]["env"] == env)
    for k in fkeys:
        pose = gt[k]["pose"] or "-"
        frame = gt[k]["frame"]
        assess = [g for g in gt[k]["objects"] if not g["occluded"]]
        occl = [g for g in gt[k]["objects"] if g["occluded"]]
        tot["assessable"] += len(assess)
        dets = []
        for d in fused.get(k, []):
            c = M.det_conf(d)
            if c is not None and c < conf_thr:
                continue
            dets.append({"box": M.det_box(d), "canon": M.canon(M.det_class(d)),
                         "raw_class": M.det_class(d), "conf": c,
                         "src": str(M.first_key(d, M.SOURCE_KEYS)).lower()})
        matches = M.greedy_match_2d(assess, dets, iou_thr)
        matched_g = {gi: (di, v) for gi, di, v in matches}
        matched_d = {di: (gi, v) for gi, di, v in matches}
        tot["tp"] += len(matches)
        tot["fp"] += len(dets) - len(matched_d)
        for gi, g in enumerate(assess):
            row = {"env": env, "pose": pose, "frame": frame,
                   "gt_class_raw": g["class"], "gt_canon": g["canon"],
                   "gt_range_m": g["range"] if g["range"] is not None else ""}
            if gi in matched_g:
                di, v = matched_g[gi]
                d = dets[di]
                pic = "person-in-chair" in str(g["class"]).lower()
                ok = (g["canon"] == d["canon"]) or (pic and d["canon"] in ("person", "chair"))
                row.update({"bucket": "TP_correct_class" if ok else "TP_wrong_class",
                            "pred_class": d["raw_class"], "pred_conf": round(d["conf"], 3) if d["conf"] is not None else "",
                            "match_iou": round(v, 3), "det_source": d["src"]})
                if not ok:
                    tot["class_err"] += 1
                if d["src"] == "fused" and g["range"] is not None:
                    tot["tp_range_rows"] += 1
            else:
                tot["fn"] += 1
                row.update({"bucket": "FN", "pred_class": "", "pred_conf": "",
                            "match_iou": "", "det_source": ""})
            inst_rows.append(row)
        for di, d in enumerate(dets):
            row = {"env": env, "pose": pose, "frame": frame,
                   "pred_class": d["raw_class"], "pred_conf": round(d["conf"], 3) if d["conf"] is not None else "",
                   "det_source": d["src"]}
            if di in matched_d:
                gi, v = matched_d[di]
                row.update({"bucket": "TP", "sub_bucket": "",
                            "matched_gt": assess[gi]["class"], "max_iou_assessable": round(v, 3),
                            "max_iou_occluded": ""})
            else:
                mia = max((M.iou(g["box"], d["box"]) for g in assess
                           if g["box"] is not None and d["box"] is not None), default=0.0)
                mio = max((M.iou(g["box"], d["box"]) for g in occl
                           if g["box"] is not None and d["box"] is not None), default=0.0)
                if mia >= iou_thr:
                    sub = "duplicate_detection"
                elif mio >= iou_thr:
                    sub = "matches_occluded_gt"
                elif max(mia, mio) > 0.0:
                    sub = "partial_overlap_below_iou"
                else:
                    sub = "no_gt_overlap"
                row.update({"bucket": "FP", "sub_bucket": sub, "matched_gt": "",
                            "max_iou_assessable": round(mia, 3), "max_iou_occluded": round(mio, 3)})
            det_rows.append(row)
    return inst_rows, det_rows, tot
#endregion

#region [Aggregations]
def by_object(inst_rows):
    agg = {}
    for r in inst_rows:
        key = (r["env"], r["gt_class_raw"])
        a = agg.setdefault(key, {"assessable": 0, "TP_correct_class": 0, "TP_wrong_class": 0,
                                 "FN": 0, "rng_fn": [], "rng_tp": []})
        a["assessable"] += 1
        a[r["bucket"]] += 1
        if r["gt_range_m"] != "":
            (a["rng_fn"] if r["bucket"] == "FN" else a["rng_tp"]).append(float(r["gt_range_m"]))
    return agg


def by_env_pose(inst_rows):
    agg = {}
    for r in inst_rows:
        key = (r["env"], r["pose"])
        a = agg.setdefault(key, {"assessable": 0, "TP_correct_class": 0, "TP_wrong_class": 0, "FN": 0})
        a["assessable"] += 1
        a[r["bucket"]] += 1
    return agg


def med(v):
    return round(statistics.median(v), 2) if v else "-"
#endregion

#region [Writers]
def write_csv(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_reconciliation(out, totals):
    lines = ["# d32 reconciliation (MUST equal the d26 presence table)", ""]
    for env in sorted(totals):
        t = totals[env]
        lines.append(f"- {env}: assessable={t['assessable']} TP={t['tp']} FN={t['fn']} "
                     f"FP={t['fp']} class_err={t['class_err']} (TP-with-fused-range={t['tp_range_rows']})")
    txt = "\n".join(lines) + "\n"
    open(os.path.join(out, "reconciliation.md"), "w").write(txt)
    return txt


def write_by_object(out, agg):
    lines = ["# Taxonomy by object (raw GT class)", "",
             "| env | object | assessable | TP correct | TP wrong-class | FN | FN rate | med GT range FN (m) | med GT range TP (m) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for (env, cls) in sorted(agg):
        a = agg[(env, cls)]
        fnr = a["FN"] / a["assessable"] if a["assessable"] else 0.0
        lines.append(f"| {env} | {cls} | {a['assessable']} | {a['TP_correct_class']} | "
                     f"{a['TP_wrong_class']} | {a['FN']} | {fnr:.2f} | {med(a['rng_fn'])} | {med(a['rng_tp'])} |")
    open(os.path.join(out, "taxonomy_by_object.md"), "w").write("\n".join(lines) + "\n")


def write_by_env_pose(out, agg):
    lines = ["# Taxonomy by env / pose", "",
             "| env | pose | assessable | TP correct | TP wrong-class | FN | recall |",
             "|---|---|---|---|---|---|---|"]
    for (env, pose) in sorted(agg):
        a = agg[(env, pose)]
        rec = (a["TP_correct_class"] + a["TP_wrong_class"]) / a["assessable"] if a["assessable"] else 0.0
        lines.append(f"| {env} | {pose} | {a['assessable']} | {a['TP_correct_class']} | "
                     f"{a['TP_wrong_class']} | {a['FN']} | {rec:.3f} |")
    open(os.path.join(out, "taxonomy_by_env_pose.md"), "w").write("\n".join(lines) + "\n")


def write_class_errors(out, inst_rows):
    lines = ["# Wrong-class matches (every one, individually)", "",
             "| env | pose | frame | GT class (raw) | predicted | conf | IoU |",
             "|---|---|---|---|---|---|---|"]
    for r in inst_rows:
        if r["bucket"] == "TP_wrong_class":
            lines.append(f"| {r['env']} | {r['pose']} | {r['frame']} | {r['gt_class_raw']} | "
                         f"{r['pred_class']} | {r['pred_conf']} | {r['match_iou']} |")
    open(os.path.join(out, "class_errors.md"), "w").write("\n".join(lines) + "\n")


def write_fp_analysis(out, det_rows):
    lines = ["# FP analysis (sub-buckets; totals must equal the reconciliation FP counts)", ""]
    for env in sorted({r["env"] for r in det_rows}):
        fps = [r for r in det_rows if r["env"] == env and r["bucket"] == "FP"]
        lines.append(f"## {env} -- {len(fps)} FPs")
        subs = {}
        for r in fps:
            subs.setdefault(r["sub_bucket"], []).append(r)
        for sub in sorted(subs):
            preds = {}
            for r in subs[sub]:
                preds[r["pred_class"]] = preds.get(r["pred_class"], 0) + 1
            pred_str = ", ".join(f"{c} x{n}" for c, n in sorted(preds.items(), key=lambda x: -x[1]))
            lines.append(f"- {sub}: {len(subs[sub])}  ({pred_str})")
        lines.append("")
    open(os.path.join(out, "fp_analysis.md"), "w").write("\n".join(lines) + "\n")
#endregion

#region [Figure]
def make_figure(fig_path, agg_obj, det_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [3, 2]})
    env2 = sorted([(cls, a) for (env, cls), a in agg_obj.items() if env == "env2"],
                  key=lambda x: -x[1]["FN"])
    names = [c for c, _ in env2]
    tp_ok = [a["TP_correct_class"] for _, a in env2]
    tp_wc = [a["TP_wrong_class"] for _, a in env2]
    fn = [a["FN"] for _, a in env2]
    y = range(len(names))
    axes[0].barh(y, tp_ok, color="#2a9d8f", label="TP correct class")
    axes[0].barh(y, tp_wc, left=tp_ok, color="#e9c46a", label="TP wrong class")
    axes[0].barh(y, fn, left=[a + b for a, b in zip(tp_ok, tp_wc)], color="#e76f51", label="FN (miss)")
    axes[0].set_yticks(list(y))
    axes[0].set_yticklabels(names)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("assessable GT instances")
    axes[0].set_title("env-2 outcome per object (raw class)")
    axes[0].legend(loc="lower right", fontsize=8)
    envs = sorted({r["env"] for r in det_rows})
    subs = ["no_gt_overlap", "matches_occluded_gt", "partial_overlap_below_iou", "duplicate_detection"]
    x = range(len(subs))
    width = 0.8 / max(len(envs), 1)
    for i, env in enumerate(envs):
        counts = [sum(1 for r in det_rows if r["env"] == env and r["bucket"] == "FP"
                      and r["sub_bucket"] == s) for s in subs]
        axes[1].bar([xi + i * width for xi in x], counts, width=width, label=env)
    axes[1].set_xticks([xi + width * (len(envs) - 1) / 2 for xi in x])
    axes[1].set_xticklabels(["no GT\noverlap", "occluded\nGT", "partial\n< IoU", "duplicate"], fontsize=8)
    axes[1].set_ylabel("FP count")
    axes[1].set_title("FP sub-buckets per env")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    os.makedirs(os.path.dirname(fig_path) or ".", exist_ok=True)
    fig.savefig(fig_path, dpi=150)
    print(f"figure -> {fig_path}")
#endregion

#region [per_match.csv cross-check]
def crosscheck_per_match(path, totals):
    fused_rows = 0
    with open(path) as f:
        for row in csv.DictReader(f):
            if row.get("source") == "fused":
                fused_rows += 1
    mine = sum(t["tp_range_rows"] for t in totals.values())
    verdict = "OK" if fused_rows == mine else "MISMATCH -> STOP, matching drifted"
    print(f"cross-check vs per_match.csv: fused rows there={fused_rows} vs TP-with-fused-range here={mine} [{verdict}]")
    return fused_rows, mine, verdict
#endregion

#region [Main]
def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)
    gt = M.load_gt(args.gt)
    fused = M.load_run(os.path.join(args.runs, "fused"))
    print(f"loaded: GT frames={len(gt)} fused frames={len(fused)}")
    envs = sorted({v["env"] for v in gt.values()})
    all_inst, all_det, totals = [], [], {}
    for env in envs:
        inst, det, tot = bucket_env(gt, fused, env, args.iou, args.yolo_conf)
        all_inst += inst
        all_det += det
        totals[env] = tot
        print(f"RECONCILE {env}: assessable={tot['assessable']} TP={tot['tp']} FN={tot['fn']} "
              f"FP={tot['fp']} class_err={tot['class_err']}")
    write_csv(os.path.join(args.out, "instances.csv"), all_inst,
              ["env", "pose", "frame", "gt_class_raw", "gt_canon", "gt_range_m",
               "bucket", "pred_class", "pred_conf", "match_iou", "det_source"])
    write_csv(os.path.join(args.out, "detections.csv"), all_det,
              ["env", "pose", "frame", "pred_class", "pred_conf", "det_source",
               "bucket", "sub_bucket", "matched_gt", "max_iou_assessable", "max_iou_occluded"])
    print(write_reconciliation(args.out, totals))
    agg_obj = by_object(all_inst)
    write_by_object(args.out, agg_obj)
    write_by_env_pose(args.out, by_env_pose(all_inst))
    write_class_errors(args.out, all_inst)
    write_fp_analysis(args.out, all_det)
    if args.per_match:
        crosscheck_per_match(args.per_match, totals)
    if args.fig:
        make_figure(args.fig, agg_obj, all_det)
    print(f"done -> {args.out}")
#endregion


if __name__ == "__main__":
    main()
