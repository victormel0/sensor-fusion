#!/usr/bin/env python3
"""
make_figure.py -- compose a labelled multi-panel figure from existing images, for thesis figures
(before/after, blue-chair, cluster viz). Lays panels in a row (default) or column, each resized to a
common size, with a caption strip above each. numpy + opencv only.

Example (true fused-vs-baseline, fused panel on the right):
  python3 code/fusion/make_figure.py \
      --inputs docs/screenshots/d13_pointpillars_frame_00300.png docs/screenshots/d16_clusters_00300.png \
      --labels "LiDAR-only (PointPillars): near-field vehicle hallucination" \
               "Fused (DAL): no near-field box; classes from camera" \
      --out docs/screenshots/d17_fused_vs_baseline.png
"""

import argparse
import os
import sys

import numpy as np
import cv2


#region [Panel building]
def resize_to_height(img, h):
    scale = h / img.shape[0]
    return cv2.resize(img, (max(1, int(round(img.shape[1] * scale))), h), interpolation=cv2.INTER_AREA)


def resize_to_width(img, w):
    scale = w / img.shape[1]
    return cv2.resize(img, (w, max(1, int(round(img.shape[0] * scale)))), interpolation=cv2.INTER_AREA)


def add_label(img, text, bar_h=34):
    """Add a black caption strip with white text above the image."""
    if not text:
        return img
    w = img.shape[1]
    bar = np.zeros((bar_h, w, 3), dtype=np.uint8)
    font, scale, thick = cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
    text = text if len(text) < 90 else text[:87] + "..."
    cv2.putText(bar, text, (8, int(bar_h * 0.68)), font, scale, (255, 255, 255), thick, cv2.LINE_AA)
    return np.vstack([bar, img])


def pad_to(img, h, w):
    """Centre-pad an image (dark grey) to (h, w)."""
    out = np.full((h, w, 3), 30, dtype=np.uint8)
    y, x = (h - img.shape[0]) // 2, (w - img.shape[1]) // 2
    out[y:y + img.shape[0], x:x + img.shape[1]] = img
    return out
#endregion


#region [Main]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True, help="image paths, in panel order")
    ap.add_argument("--labels", nargs="*", default=None, help="one caption per input (optional)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--layout", choices=["h", "v"], default="h")
    ap.add_argument("--size", type=int, default=600, help="common panel height (h) or width (v), px")
    ap.add_argument("--gap", type=int, default=8, help="gap between panels, px")
    args = ap.parse_args()

    labels = args.labels if args.labels else [""] * len(args.inputs)
    if len(labels) != len(args.inputs):
        sys.exit(f"ERROR: {len(args.labels)} labels for {len(args.inputs)} inputs; give one label per input.")

    panels = []
    for path, lab in zip(args.inputs, labels):
        img = cv2.imread(path)
        if img is None:
            sys.exit(f"ERROR: could not read {path}")
        img = resize_to_height(img, args.size) if args.layout == "h" else resize_to_width(img, args.size)
        panels.append(add_label(img, lab))

    if args.layout == "h":
        H = max(p.shape[0] for p in panels)
        panels = [pad_to(p, H, p.shape[1]) for p in panels]
        sep = np.full((H, args.gap, 3), 30, dtype=np.uint8)
        rows = []
        for i, p in enumerate(panels):
            rows.append(p)
            if i < len(panels) - 1:
                rows.append(sep)
        fig = np.hstack(rows)
    else:
        W = max(p.shape[1] for p in panels)
        panels = [pad_to(p, p.shape[0], W) for p in panels]
        sep = np.full((args.gap, W, 3), 30, dtype=np.uint8)
        cols = []
        for i, p in enumerate(panels):
            cols.append(p)
            if i < len(panels) - 1:
                cols.append(sep)
        fig = np.vstack(cols)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    cv2.imwrite(args.out, fig)
    print(f"- {len(panels)} panels ({args.layout}) -> {args.out} ({fig.shape[1]}x{fig.shape[0]})")


if __name__ == "__main__":
    main()
#endregion
