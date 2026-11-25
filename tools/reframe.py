#!/usr/bin/env python3
"""Reframe a video to another aspect ratio (typically 16:9 -> 9:16 or 4:5).

Modes:
  face     detect faces (OpenCV) on sampled frames, crop centered on the
           median face position (best for a static talking-head camera)
  crop     crop at a fixed horizontal position --x (0=left, 0.5=center, 1=right)
  blurpad  keep the full frame, fit it inside the target, fill the rest with a
           blurred/zoomed copy (good for screen recordings, wide b-roll, photos)

Usage:
    .venv/bin/python tools/reframe.py in.mp4 out.mp4 --aspect 9:16 --mode face
    .venv/bin/python tools/reframe.py in.mp4 out.mp4 --aspect 4:5 --mode crop --x 0.4
    .venv/bin/python tools/reframe.py in.mp4 out.mp4 --aspect 9:16 --mode blurpad

Output is 1080 px wide (1080x1920, 1080x1350, 1080x1080) unless --width.
Encodes H.264 CRF 18 and copies audio. Prints the crop it chose so the agent
can verify / override (--x).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:stream_side_data=rotation:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True)
    d = json.loads(out.stdout)
    s = d["streams"][0]
    w, h = s["width"], s["height"]
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", 0) or 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    return {"w": w, "h": h, "duration": float(d["format"].get("duration", 0) or 0)}


def face_center_x(path: Path, duration: float, samples: int = 24) -> float | None:
    import cv2
    import numpy as np
    sys.path.insert(0, str(Path(__file__).parent))
    from _media import FaceDetector

    detector = FaceDetector()
    cap = cv2.VideoCapture(str(path))
    xs = []
    for i in range(samples):
        t = duration * (i + 0.5) / samples
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        faces, (sw, _) = detector.detect(frame, target_w=640)
        if faces:
            x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            xs.append((x + fw / 2) / sw)
    cap.release()
    if not xs:
        return None
    return float(np.median(xs))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--mode", choices=["face", "crop", "blurpad"], default="face")
    ap.add_argument("--x", type=float, default=None, help="crop center 0..1 (overrides face detection)")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()
    sys.path.insert(0, str(Path(__file__).parent))
    from _media import assert_not_raw
    assert_not_raw(a.output)

    info = probe(a.input)
    W, H = info["w"], info["h"]
    an, ad = (int(v) for v in a.aspect.split(":"))
    tw = a.width - a.width % 2
    th = int(round(tw * ad / an / 2) * 2)

    if a.mode == "blurpad":
        vf = (f"split=2[bg][fg];"
              f"[bg]scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},gblur=sigma=40,eq=brightness=-0.08[bgb];"
              f"[fg]scale={tw}:{th}:force_original_aspect_ratio=decrease[fgs];"
              f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1")
        chosen = "blurpad"
    else:
        target_ratio = an / ad
        if W / H > target_ratio:  # source wider -> crop width
            cw, ch = int(H * target_ratio) // 2 * 2, H
        else:
            cw, ch = W, int(W / target_ratio) // 2 * 2
        cx = a.x
        if cx is None and a.mode == "face":
            cx = face_center_x(a.input, info["duration"])
            if cx is None:
                print("no face found; falling back to center crop", file=sys.stderr)
        if cx is None:
            cx = 0.5
        x0 = int(min(max(cx * W - cw / 2, 0), W - cw))
        y0 = (H - ch) // 2
        vf = f"crop={cw}:{ch}:{x0}:{y0},scale={tw}:{th}:flags=lanczos,setsar=1"
        chosen = f"crop {cw}x{ch} at x={x0} (center {cx:.3f})"

    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(a.input),
           "-filter_complex" if a.mode == "blurpad" else "-vf", vf,
           "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium", "-pix_fmt", "yuv420p",
           "-c:a", "copy", "-movflags", "+faststart", str(a.output)]
    print(f"{a.input.name} {W}x{H} -> {tw}x{th}: {chosen}")
    subprocess.run(cmd, check=True)
    print(f"wrote {a.output}")


if __name__ == "__main__":
    main()
