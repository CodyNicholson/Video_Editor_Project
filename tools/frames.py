#!/usr/bin/env python3
"""Pull thumbnail-candidate frames from a video, ranked, plus a contact sheet.

Scores every sampled frame on sharpness (Laplacian variance), exposure, and
face presence/size (OpenCV), keeps the top N, and writes a numbered contact
sheet so the agent (or you) can pick by eye.

Usage:
    .venv/bin/python tools/frames.py video.mp4 --out-dir projects/<slug>/thumbnails/frames
    .venv/bin/python tools/frames.py video.mp4 --out-dir ... --samples 120 --top 12
    .venv/bin/python tools/frames.py video.mp4 --out-dir ... --at 12.5 47 63.2   # exact times

Outputs: frame_<rank>_<t>s.jpg (full-res) and contact_sheet.jpg
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from _media import FaceDetector  # noqa: E402

FONT = Path(__file__).resolve().parent.parent / "brand" / "fonts" / "ArchivoBlack-Regular.ttf"


def score(frame, detector: FaceDetector):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    small_gray = cv2.resize(gray, (640, int(h * 640 / w)))
    sharp = cv2.Laplacian(small_gray, cv2.CV_64F).var()
    mean = small_gray.mean()
    exposure = 1.0 - abs(mean - 120) / 120  # 1.0 = well exposed
    faces, (sw, sh) = detector.detect(frame, target_w=640)
    face_area = max((fw * fh for (_, _, fw, fh) in faces), default=0) / (sw * sh)
    s = np.log1p(sharp) * 1.0 + exposure * 2.0 + (3.0 + 20 * min(face_area, 0.15) if faces else 0)
    return float(s), dict(sharp=round(sharp, 1), exposure=round(exposure, 2), faces=int(len(faces)),
                          face_area=round(face_area, 3))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--samples", type=int, default=80)
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--at", type=float, nargs="*", default=None, help="explicit timestamps (s)")
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    detector = FaceDetector()
    cap = cv2.VideoCapture(str(a.video))
    dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or 30)
    times = a.at if a.at else [dur * (i + 0.5) / a.samples for i in range(a.samples)]
    results = []
    for t in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        s, meta = score(frame, detector)
        results.append((s, t, frame, meta))
    cap.release()
    if not a.at:
        results.sort(key=lambda r: -r[0])
        # de-duplicate near-identical moments (keep >= 2 s apart)
        picked = []
        for r in results:
            if all(abs(r[1] - p[1]) >= 2.0 for p in picked):
                picked.append(r)
            if len(picked) >= a.top:
                break
        results = picked

    index, thumbs = [], []
    for rank, (s, t, frame, meta) in enumerate(results, 1):
        name = f"frame_{rank:02d}_{t:07.2f}s.jpg"
        cv2.imwrite(str(a.out_dir / name), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        index.append(dict(rank=rank, t=round(t, 2), file=name, score=round(s, 2), **meta))
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img.thumbnail((480, 480))
        thumbs.append((rank, t, img))
    (a.out_dir / "frames.json").write_text(json.dumps(index, indent=1))

    if thumbs:
        cols = 4
        tw = max(t[2].width for t in thumbs); th = max(t[2].height for t in thumbs)
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 10) + 10), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        font = ImageFont.truetype(str(FONT), 28) if FONT.exists() else ImageFont.load_default()
        for i, (rank, t, img) in enumerate(thumbs):
            x = 10 + (i % cols) * (tw + 10); y = 10 + (i // cols) * (th + 10)
            sheet.paste(img, (x, y))
            d.text((x + 8, y + 6), f"#{rank}  {t:.1f}s", fill=(255, 230, 0), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
        sheet.save(a.out_dir / "contact_sheet.jpg", quality=90)
    print(f"wrote {len(index)} frames + contact_sheet.jpg + frames.json to {a.out_dir}")


if __name__ == "__main__":
    main()
