#!/usr/bin/env python3
"""One-line-per-file media summary (resolution, fps, duration, codecs, loudness).

Usage:
    .venv/bin/python tools/probe.py projects/<slug>/raw/*
    .venv/bin/python tools/probe.py final.mp4 --loudness
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--loudness", action="store_true", help="also measure integrated LUFS / true peak")
    a = ap.parse_args()
    for f in a.files:
        if f.is_dir() or f.name.startswith("."):
            continue
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "stream=codec_type,codec_name,width,height,avg_frame_rate,channels,sample_rate,pix_fmt,color_transfer:"
                            "stream_side_data=rotation:format=duration,bit_rate,size",
                            "-of", "json", str(f)], capture_output=True, text=True)
        if r.returncode:
            print(f"{f.name}: not a media file"); continue
        d = json.loads(r.stdout)
        fmt = d.get("format", {})
        parts = [f.name, f"{float(fmt.get('duration', 0)):.2f}s", f"{int(fmt.get('size', 0)) / 1e6:.1f}MB"]
        for s in d.get("streams", []):
            if s["codec_type"] == "video":
                fr = s.get("avg_frame_rate", "0/1").split("/")
                fps = float(fr[0]) / float(fr[1]) if float(fr[1] or 0) else 0
                rot = next((sd.get("rotation") for sd in s.get("side_data_list", []) or [] if "rotation" in sd), None)
                hdr = " HDR/HLG" if s.get("color_transfer") in ("smpte2084", "arib-std-b67") else ""
                parts.append(f"video {s['codec_name']} {s['width']}x{s['height']} {fps:.2f}fps {s.get('pix_fmt', '')}"
                             f"{' rot=' + str(rot) if rot else ''}{hdr}")
            elif s["codec_type"] == "audio":
                parts.append(f"audio {s['codec_name']} {s.get('channels')}ch {s.get('sample_rate')}Hz")
        if a.loudness:
            lr = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-vn", "-af",
                                 "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True)
            try:
                j = json.loads(lr.stderr[lr.stderr.rindex("{"): lr.stderr.rindex("}") + 1])
                parts.append(f"{j['input_i']} LUFS, TP {j['input_tp']} dBTP")
            except ValueError:
                pass
        print(" | ".join(parts))


if __name__ == "__main__":
    main()
