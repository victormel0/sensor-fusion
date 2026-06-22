#!/usr/bin/env python3
"""
set_ranges.py -- fill / edit the range_m_tape field of objects in an EXISTING annotate_gt.py GT
file, one frame at a time, by showing each box on the image and prompting for a range in the
terminal.

Use case (Week 5, d25): env-1 boxes + classes were drawn the night before with range left null on
every object except the two original markers. The next day in the office, the still-present objects
(monitors, etc.) are tape-measured, and their ranges are written into the existing GT here -- no
re-drawing.

CONTROL MODEL (same spirit as annotate_gt.py): display-only window; all input is terminal prompts.
Each existing object is highlighted in turn; you type its range or press ENTER to keep the current
value. Order matches the object indices shown by annotate_gt.

    python3 code/eval/set_ranges.py --frames-dir code/fusion/frames_out --gt-dir docs/gt/env1 --frame 00300

Writes the GT file back in place (same schema). range values are RAW TAPE metres; the +offset
conversion stays in metrics.py. This tool does NOT change boxes, classes, occluded, or notes.
"""

#region [Imports and CLI]
import argparse
import json
import os

import cv2


def parse_args():
    ap = argparse.ArgumentParser(description="edit range_m_tape on existing GT objects")
    ap.add_argument("--frames-dir", required=True, help="dir with NNNNN.<img-ext> frames")
    ap.add_argument("--gt-dir", required=True, help="dir with NNNNN.json GT files")
    ap.add_argument("--frame", required=True, help="frame id, e.g. 00300")
    ap.add_argument("--img-ext", default="png")
    ap.add_argument("--scale", type=float, default=1.0)
    return ap.parse_args()
#endregion

#region [Rendering]
def render(base, objects, active_idx, scale):
    img = base.copy()
    for i, obj in enumerate(objects):
        x1, y1, x2, y2 = [int(round(v * scale)) for v in obj["bbox_2d"]]
        if i == active_idx:
            color = (0, 0, 255)        # active object: red, thick
            thick = 3
        else:
            color = (0, 200, 0)
            thick = 1
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thick)
        tag = f"{i}:{obj['class']}"
        if obj.get("range_m_tape") is not None:
            tag += f" {obj['range_m_tape']}m"
        cv2.putText(img, tag, (x1, max(12, y1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    return img
#endregion

#region [Main]
def main():
    args = parse_args()
    img_path = os.path.join(args.frames_dir, f"{args.frame}.{args.img_ext}")
    gt_path = os.path.join(args.gt_dir, f"{args.frame}.json")
    orig = cv2.imread(img_path)
    if orig is None:
        print(f"[skip] cannot read image {img_path}")
        return
    if not os.path.isfile(gt_path):
        print(f"[skip] no GT file {gt_path} -- annotate this frame first")
        return
    with open(gt_path) as fh:
        data = json.load(fh)
    objects = data.get("objects", [])
    if not objects:
        print(f"[skip] {gt_path} has no objects")
        return

    scale = args.scale
    h, w = orig.shape[:2]
    base = orig if scale == 1.0 else cv2.resize(
        orig, (int(round(w * scale)), int(round(h * scale))))
    win = "set_ranges"
    cv2.namedWindow(win)
    print(f"== {args.frame}: {len(objects)} object(s). The RED box is the active one. ==")
    print("   for each: type a range in metres (RAW tape), or ENTER to keep the current value.")

    changed = 0
    for i, obj in enumerate(objects):
        # show the active object (pump a few waitKeys so the window paints before the prompt blocks it)
        for _ in range(3):
            cv2.imshow(win, render(base, objects, i, scale))
            cv2.waitKey(15)
        cur = obj.get("range_m_tape")
        cur_s = "null" if cur is None else f"{cur}"
        ans = input(f"   [{i}] {obj['class']:<12} current range={cur_s}  -> new (ENTER keeps): ").strip()
        if ans == "":
            continue
        if ans.lower() in ("null", "none", "-"):
            if obj.get("range_m_tape") is not None:
                obj["range_m_tape"] = None
                changed += 1
                print("       set to null")
            continue
        try:
            obj["range_m_tape"] = float(ans)
            changed += 1
            print(f"       set to {obj['range_m_tape']}")
        except ValueError:
            print("       not a number -> kept current value")

    cv2.destroyWindow(win)
    if changed:
        with open(gt_path, "w") as fh:
            json.dump(data, fh, indent=2)
        print(f"saved {gt_path} ({changed} range value(s) changed)")
    else:
        print("no changes; file left untouched")


if __name__ == "__main__":
    main()
#endregion
