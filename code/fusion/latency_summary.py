#!/usr/bin/env python3
"""
latency_summary.py -- re-derive the d21 per-stage latency table from the per-frame CSV that
fusion_node.py --profile writes (default /tmp/d21_latency.csv).

Purpose: regenerate the mean/p50/p95 table + dominant stage WITHOUT re-running the node -- for the
d21 manifest, the Results-chapter figure, or to recompute over a different frame slice. The node
already prints this table at shutdown; this is the offline re-analysis path on the retained samples.

Needs numpy only, so it runs in either environment (venv_yolo or the ROS env).

Run:
    python3 latency_summary.py --csv /tmp/d21_latency.csv
    python3 latency_summary.py --csv /tmp/d21_latency.csv --start 0 --end 200 --out /tmp/d21_table.md
"""

import argparse
import sys

import numpy as np


#region [Stage labels]
# (csv column, printed label) -- must match fusion_node.py PROFILE_STAGES.
STAGES = [
    ("image_decode", "image decode"),
    ("pc_to_xyz", "pointcloud->xyz"),
    ("yolo", "yolo inference"),
    ("projection", "projection"),
    ("dbscan", "dbscan assoc"),
    ("msg_build_pub", "msg build/pub"),
]
#endregion


#region [Load]
def load_csv(path, start, end):
    """Return ({column: np.ndarray}, n_rows). Slices rows [start:end] when given."""
    with open(path) as f:
        header = f.readline().strip().split(",")
        rows = [ln.strip().split(",") for ln in f if ln.strip()]
    if not rows:
        sys.exit(f"ERROR: no data rows in {path}")
    if end is None:
        end = len(rows)
    rows = rows[start:end]
    cols = {}
    for j, name in enumerate(header):
        vals = []
        for r in rows:
            try:
                vals.append(float(r[j]))
            except (ValueError, IndexError):
                vals.append(float("nan"))
        cols[name] = np.asarray(vals, dtype=np.float64)
    return cols, len(rows)
#endregion


#region [Summary]
def stats(arr):
    if arr.size == 0 or np.all(np.isnan(arr)):
        return (float("nan"), float("nan"), float("nan"))
    return (float(np.nanmean(arr)),
            float(np.nanpercentile(arr, 50)),
            float(np.nanpercentile(arr, 95)))


def summary(cols, n):
    lines = ["## Per-stage latency (re-derived from CSV, N=%d)" % n,
             "| stage | mean ms | p50 | p95 |",
             "|---|---|---|---|"]
    p50s = {}
    for key, label in STAGES:
        if key not in cols:
            continue
        mean, p50, p95 = stats(cols[key])
        p50s[label] = p50
        lines.append("| %-15s | %7.2f | %7.2f | %7.2f |" % (label, mean, p50, p95))

    if "callback" in cols:
        mean, p50, p95 = stats(cols["callback"])
        lines.append("| %-15s | %7.2f | %7.2f | %7.2f |" % ("END-TO-END (cb)", mean, p50, p95))
        if p50 == p50 and p50 > 0:
            lines.append("- derived fps (1000 / p50 callback): %.2f Hz" % (1000.0 / p50))

    if "stamp" in cols:
        mean, p50, p95 = stats(cols["stamp"])
        if 0.0 < p50 < 5000.0:
            lines.append("| %-15s | %7.2f | %7.2f | %7.2f |" % ("stamp e2e", mean, p50, p95))
        else:
            lines.append("- stamp-based end-to-end: N/A (node clock / image header stamp not "
                         "aligned on this run).")

    valid = {lab: p for lab, p in p50s.items() if p == p}
    if valid:
        dom = max(valid, key=valid.get)
        lines.append("- dominant stage (by p50): %s (%.2f ms)" % (dom, valid[dom]))
    return "\n".join(lines)
#endregion


#region [Main]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--start", type=int, default=0, help="first row to include (0-based)")
    ap.add_argument("--end", type=int, default=None, help="one past the last row to include")
    ap.add_argument("--out", default=None, help="optional markdown output path")
    args = ap.parse_args()

    cols, n = load_csv(args.csv, args.start, args.end)
    table = summary(cols, n)
    print(table)
    if args.out:
        with open(args.out, "w") as f:
            f.write(table + "\n")
        print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
#endregion
