#!/usr/bin/env python3
"""
annotate_gt.py -- minimal 2D ground-truth annotation tool (Week 5, d24).

CONTROL MODEL (revised d24): the mouse draws boxes in the OpenCV window; EVERYTHING ELSE is a
terminal prompt. There are no control keystrokes into the window (the old u/n/q-in-window flow
trapped input because cv2.waitKey only sees keys when the window has focus). After you drag a box
you answer its prompts in the terminal, then a single control prompt decides what happens next.

Per-frame loop:
    1. window shows the image (display-only)
    2. you DRAG one box with the left mouse button
    3. terminal asks: class / range_m_tape / occluded / notes
    4. terminal asks the control prompt:
         [Enter] = draw another box
         u       = undo the last box
         d       = done with this frame (save + go to next frame)
         q       = save this frame + quit
    5. after each frame it prints  saved <path> (N objects)

IMPORTANT: the window FREEZES while a terminal prompt is open (cv2 event loop is paused). So the
rhythm is draw -> answer -> draw -> answer, NOT draw-draw-draw. Draw exactly one box, then answer.

Output: one JSON per frame in --out, schema per the d24 frozen definitions:
    {
        "frame": "00300",
        "image": "00300.png",
        "image_size": [w, h],
        "created": "<iso timestamp>",
        "objects": [
            {"class": "...", "bbox_2d": [x1, y1, x2, y2],
             "range_m_tape": <float or null>, "occluded": <bool>, "notes": "..."}
        ]
    }

Boxes are stored in ORIGINAL image pixels regardless of --scale (display-only zoom).
Resume-safe: if the output JSON already exists, its objects are pre-loaded.
"""

#region [Imports and CLI]
import argparse
import datetime
import json
import os
import sys

import cv2


def parse_args():
    ap = argparse.ArgumentParser(description="2D GT annotation (d24 schema)")
    ap.add_argument("--frames-dir", required=True,
                    help="directory containing NNNNN.<img-ext> frames")
    ap.add_argument("--frames", required=True,
                    help="comma-separated frame ids, e.g. 00100,00300 (zero-padded as on disk)")
    ap.add_argument("--out", required=True,
                    help="output directory for per-frame JSON (created if missing)")
    ap.add_argument("--img-ext", default="png")
    ap.add_argument("--scale", type=float, default=1.0,
                    help="display zoom only; stored boxes are in original pixels")
    return ap.parse_args()
#endregion

#region [Mouse state]
# module-level state shared with the OpenCV mouse callback
STATE = {
    "drag": False,
    "x0": 0, "y0": 0,
    "x1": 0, "y1": 0,
    "pending": None,    # (x0, y0, x1, y1) in DISPLAY pixels, set on mouse-up
}


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        STATE["drag"] = True
        STATE["x0"], STATE["y0"] = x, y
        STATE["x1"], STATE["y1"] = x, y
    elif event == cv2.EVENT_MOUSEMOVE and STATE["drag"]:
        STATE["x1"], STATE["y1"] = x, y
    elif event == cv2.EVENT_LBUTTONUP and STATE["drag"]:
        STATE["drag"] = False
        STATE["x1"], STATE["y1"] = x, y
        x0, x1 = sorted((STATE["x0"], STATE["x1"]))
        y0, y1 = sorted((STATE["y0"], STATE["y1"]))
        if (x1 - x0) >= 4 and (y1 - y0) >= 4:
            STATE["pending"] = (x0, y0, x1, y1)
#endregion

#region [Drawing]
def render(base, objects, scale):
    img = base.copy()
    for i, obj in enumerate(objects):
        x1, y1, x2, y2 = [int(round(v * scale)) for v in obj["bbox_2d"]]
        color = (0, 200, 0) if not obj.get("occluded") else (0, 165, 255)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        tag = f"{i}:{obj['class']}"
        if obj.get("range_m_tape") is not None:
            tag += f" {obj['range_m_tape']}m"
        cv2.putText(img, tag, (x1, max(12, y1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    if STATE["drag"]:
        cv2.rectangle(img, (STATE["x0"], STATE["y0"]), (STATE["x1"], STATE["y1"]),
                      (0, 255, 255), 1)
    return img
#endregion

#region [IO]
def out_path(out_dir, frame):
    return os.path.join(out_dir, f"{frame}.json")


def load_existing(out_dir, frame):
    path = out_path(out_dir, frame)
    if os.path.isfile(path):
        with open(path) as fh:
            data = json.load(fh)
        objs = data.get("objects", [])
        print(f"[resume] {path}: {len(objs)} existing objects loaded")
        return objs
    return []


def save_frame(out_dir, frame, image_name, size_wh, objects):
    payload = {
        "frame": frame,
        "image": image_name,
        "image_size": list(size_wh),
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "objects": objects,
    }
    path = out_path(out_dir, frame)
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"saved {path} ({len(objects)} objects)")
#endregion

#region [Prompts]
def prompt_object(box_orig):
    print(f"-- new box {box_orig} (original pixels)")
    cname = input("   class (empty = discard this box): ").strip()
    if not cname:
        print("   discarded")
        return None
    rng_raw = input("   range_m_tape (tape metres, ENTER = null): ").strip()
    rng = None
    if rng_raw:
        try:
            rng = float(rng_raw)
        except ValueError:
            print("   not a number -> stored as null (undo the box and redo if you need a range)")
            rng = None
    occ = input("   occluded / out-of-scope? y/N: ").strip().lower() == "y"
    notes = input("   notes (ENTER = none): ").strip()
    return {
        "class": cname,
        "bbox_2d": list(box_orig),
        "range_m_tape": rng,
        "occluded": occ,
        "notes": notes,
    }


def prompt_control(n_objects):
    """Terminal control prompt. Returns one of: 'continue', 'undo', 'done', 'quit'."""
    print(f"   [{n_objects} object(s) on this frame so far]")
    while True:
        ans = input("   next? [Enter]=another box  u=undo last  d=done frame  q=save+quit: ").strip().lower()
        if ans == "":
            return "continue"
        if ans == "u":
            return "undo"
        if ans == "d":
            return "done"
        if ans == "q":
            return "quit"
        print("   (type nothing, or one of: u / d / q)")
#endregion

#region [Main]
def wait_for_box(base, objects, scale, win):
    """Pump the cv2 event loop until the mouse finishes a box. Returns box (orig px) or None.

    Returns None only if the window was closed via the OS (so the caller can save+quit safely).
    """
    STATE["pending"] = None
    while True:
        cv2.imshow(win, render(base, objects, scale))
        cv2.waitKey(20)
        if STATE["pending"] is not None:
            dx0, dy0, dx1, dy1 = STATE["pending"]
            STATE["pending"] = None
            h, w = base.shape[0], base.shape[1]
            bx = (
                int(round(dx0 / scale)), int(round(dy0 / scale)),
                int(round(dx1 / scale)), int(round(dy1 / scale)),
            )
            bx = (
                max(0, min(bx[0], int(w / scale) - 1)), max(0, min(bx[1], int(h / scale) - 1)),
                max(0, min(bx[2], int(w / scale) - 1)), max(0, min(bx[3], int(h / scale) - 1)),
            )
            return bx
        # window closed by the OS -> getWindowProperty goes < 1
        try:
            if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                return None
        except cv2.error:
            return None


def annotate_frame(args, frame):
    image_name = f"{frame}.{args.img_ext}"
    img_path = os.path.join(args.frames_dir, image_name)
    orig = cv2.imread(img_path)
    if orig is None:
        print(f"[skip] cannot read {img_path}")
        return "next"
    h, w = orig.shape[:2]
    scale = args.scale
    base = orig if scale == 1.0 else cv2.resize(
        orig, (int(round(w * scale)), int(round(h * scale))))
    objects = load_existing(args.out, frame)
    win = "annotate_gt"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)
    print(f"== frame {frame} ({w}x{h}) ==")
    print("   draw ONE box in the window, then answer the prompts here in the terminal.")
    while True:
        box = wait_for_box(base, objects, scale, win)
        if box is None:
            # window closed: save what we have and quit cleanly
            save_frame(args.out, frame, image_name, (w, h), objects)
            cv2.destroyWindow(win)
            return "quit"
        obj = prompt_object(box)
        if obj is not None:
            objects.append(obj)
            # refresh so the new box is visible before the control prompt
            cv2.imshow(win, render(base, objects, scale))
            cv2.waitKey(1)
        action = prompt_control(len(objects))
        if action == "continue":
            continue
        if action == "undo":
            if objects:
                gone = objects.pop()
                print(f"   undone: {gone['class']} {gone['bbox_2d']}")
            else:
                print("   nothing to undo")
            continue
        if action == "done":
            save_frame(args.out, frame, image_name, (w, h), objects)
            cv2.destroyWindow(win)
            return "next"
        if action == "quit":
            save_frame(args.out, frame, image_name, (w, h), objects)
            cv2.destroyWindow(win)
            return "quit"


def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)
    frames = [f.strip() for f in args.frames.split(",") if f.strip()]
    if not frames:
        print("no frames given")
        sys.exit(1)
    for frame in frames:
        outcome = annotate_frame(args, frame)
        if outcome == "quit":
            break
    print("done")


if __name__ == "__main__":
    main()
#endregion
