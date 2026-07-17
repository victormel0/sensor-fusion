#!/usr/bin/env python3
"""
figures.py -- d26 figures from metrics.py outputs.

Run in venv_yolo (needs matplotlib; pip install matplotlib --break-system-packages if missing).

  cd ~/Documents/workspace/sensor-fusion
  source venv_yolo/bin/activate
  python3 code/eval/figures.py --metrics docs/d26_metrics --out docs/screenshots
  python3 code/eval/figures.py --metrics docs/d35_metrics/s1_bright --out docs/screenshots --prefix d35_s1_bright

Reads {per_match.csv, presence_table.md, fused_rate_table.md} from --metrics and writes (stem set by
--prefix, default "d26"):
  <prefix>_fig_range_scatter.png   (GT range vs detected range, 1:1 line, per arm)
  <prefix>_fig_presence_bars.png   (recall/precision/class per env+arm)
  <prefix>_fig_fused_rate.png      (fused vs camera_only-by-reason, per env)
With no --prefix the names are d26_fig_*.png (unchanged). Qualitative overlay panels
(<prefix>_fig_qual_*.png) are made by hand from the overlay tool, not here.

Each figure is skipped (with a message) if its input is missing, so a partial run still produces what it can.
"""

#region [Imports + CLI]
import argparse
import csv
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="docs/d26_metrics")
    ap.add_argument("--out", required=True, help="docs/screenshots")
    ap.add_argument("--prefix", default="d26",
                    help="filename stem before '_fig_' (default 'd26' -> d26_fig_*.png; "
                         "e.g. --prefix d35_s1_bright -> d35_s1_bright_fig_*.png)")
    return ap.parse_args()
#endregion

#region [Tiny markdown-table reader]
def read_md_table(path):
    """Parse the FIRST pipe-table in a markdown file -> list of dict rows (header from row 1)."""
    if not os.path.isfile(path):
        return None
    rows, header = [], None
    for line in open(path):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):  # separator row
            continue
        if header is None:
            header = cells
        else:
            if len(cells) == len(header):
                rows.append(dict(zip(header, cells)))
    return rows
#endregion

#region [Range scatter]
def fig_range_scatter(metrics_dir, out_dir, prefix):
    csv_path = os.path.join(metrics_dir, "per_match.csv")
    if not os.path.isfile(csv_path):
        print("[scatter] skip: no per_match.csv")
        return
    rows = list(csv.DictReader(open(csv_path)))
    if not rows:
        print("[scatter] skip: per_match.csv empty")
        return
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = {"fused": "#1f77b4", "lidar_only": "#d62728"}
    markers = {"env1": "o", "env2": "s"}
    maxr = 1.0
    for r in rows:
        try:
            gx, dy = float(r["gt_range"]), float(r["det_range"])
        except (ValueError, KeyError):
            continue
        ax.scatter(gx, dy, c=colors.get(r["arm"], "#555"),
                   marker=markers.get(r["env"], "x"), s=42, alpha=0.8,
                   edgecolors="k", linewidths=0.4)
        maxr = max(maxr, gx, dy)
    lim = maxr * 1.08
    ax.plot([0, lim], [0, lim], "k--", lw=1, label="1:1 (perfect range)")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("Tape GT range (m)")
    ax.set_ylabel("Detected range_m (m)")
    ax.set_title("Range: detected vs GT (fused + LiDAR-only)")
    handles = [plt.Line2D([], [], marker="o", ls="", color=colors["fused"], label="fused"),
               plt.Line2D([], [], marker="o", ls="", color=colors["lidar_only"], label="lidar_only"),
               plt.Line2D([], [], marker="o", ls="", color="#888", label="env1 (circle)"),
               plt.Line2D([], [], marker="s", ls="", color="#888", label="env2 (square)"),
               plt.Line2D([], [], ls="--", color="k", label="1:1")]
    ax.legend(handles=handles, fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.3)
    p = os.path.join(out_dir, f"{prefix}_fig_range_scatter.png")
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    print(f"[scatter] wrote {p} ({len(rows)} points)")
#endregion

#region [Presence bars]
def fig_presence(metrics_dir, out_dir, prefix):
    rows = read_md_table(os.path.join(metrics_dir, "presence_table.md"))
    if not rows:
        print("[presence] skip: no presence_table.md")
        return
    labels, recall, prec, cls = [], [], [], []
    for r in rows:
        if "recall" not in r:
            continue
        labels.append(f"{r['env']}\n{r['arm']}")
        recall.append(float(r["recall"]))
        prec.append(float(r["precision"]))
        cls.append(float(r["class_acc"]))
    if not labels:
        print("[presence] skip: no parseable rows")
        return
    x = range(len(labels))
    w = 0.27
    fig, ax = plt.subplots(figsize=(max(6, 1.4 * len(labels)), 4.5))
    ax.bar([i - w for i in x], recall, w, label="recall", color="#1f77b4")
    ax.bar(list(x), prec, w, label="precision", color="#ff7f0e")
    ax.bar([i + w for i in x], cls, w, label="class acc", color="#2ca02c")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("score")
    ax.set_title("Presence: recall / precision / class-correctness")
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    p = os.path.join(out_dir, f"{prefix}_fig_presence_bars.png")
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    print(f"[presence] wrote {p}")
#endregion

#region [Fused-rate stacked bars]
def fig_fused_rate(metrics_dir, out_dir, prefix):
    rows = read_md_table(os.path.join(metrics_dir, "fused_rate_table.md"))
    if not rows:
        print("[fused_rate] skip: no fused_rate_table.md")
        return
    envs, fused, tfp, nqc = [], [], [], []
    for r in rows:
        if "fused" not in r:
            continue
        envs.append(r["env"])
        fused.append(int(r["fused"]))
        tfp.append(int(r["too_few_points"]))
        nqc.append(int(r["no_qualifying_cluster"]))
    if not envs:
        print("[fused_rate] skip: no parseable rows")
        return
    x = range(len(envs))
    fig, ax = plt.subplots(figsize=(max(6.5, 2.2 * len(envs)), 4.8))
    ax.bar(list(x), fused, label="fused (got range)", color="#2ca02c")
    ax.bar(list(x), tfp, bottom=fused, label="camera_only: too_few_points", color="#ff7f0e")
    bottom2 = [f + t for f, t in zip(fused, tfp)]
    ax.bar(list(x), nqc, bottom=bottom2, label="camera_only: no_qualifying_cluster", color="#d62728")
    tops = [f + t + n for f, t, n in zip(fused, tfp, nqc)]
    ax.set_ylim(0, (max(tops) if tops else 1) * 1.18)   # headroom so the tallest bar is not clipped
    ax.set_xticks(list(x))
    ax.set_xticklabels(envs)
    ax.set_ylabel("YOLO boxes")
    ax.set_title("Fused-rate: boxes that earned a LiDAR range", fontsize=11)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, axis="y", alpha=0.3)
    p = os.path.join(out_dir, f"{prefix}_fig_fused_rate.png")
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    print(f"[fused_rate] wrote {p}")
#endregion

#region [Main]
def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)
    fig_range_scatter(args.metrics, args.out, args.prefix)
    fig_presence(args.metrics, args.out, args.prefix)
    fig_fused_rate(args.metrics, args.out, args.prefix)
    print("figures.py done.")
#endregion


if __name__ == "__main__":
    main()
