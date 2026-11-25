#!/usr/bin/env python3
"""Export a finished edit to platform-ready MP4s (loudness-normalized, H.264).

Usage:
    .venv/bin/python tools/export.py final.mp4 --platform youtube-shorts tiktok instagram-reel
    .venv/bin/python tools/export.py final.mp4 --platform all-vertical --out-dir projects/<slug>/exports
    .venv/bin/python tools/export.py final.mp4 --platform youtube --keep-res      # keep 4K masters

Platforms (see .agents/skills/social-video-specs/SKILL.md for the why):
    youtube          1920x1080  16:9   long/medium form
    youtube-shorts   1080x1920  9:16   <= 3:00
    instagram-reel   1080x1920  9:16   <= 3:00 for Reels reach (longer uploads allowed)
    instagram-feed   1080x1350  4:5    feed video
    tiktok           1080x1920  9:16   <= 10:00 upload
    linkedin         keeps the input aspect (9:16, 4:5, 1:1 or 16:9), <= 15:00
    all-vertical     youtube-shorts + instagram-reel + tiktok + linkedin

Every export: two-pass EBU R128 loudnorm to -14 LUFS integrated / -1 dBTP,
H.264 High yuv420p BT.709 (BT.601 sources such as screen captures are converted,
not just retagged), AAC 320k 48 kHz stereo, +faststart, keyframe every 2 s.
If the input aspect doesn't match the platform, the script stops and tells you
to reframe first (tools/reframe.py) — pass --fit pad|crop to force.

Output goes to projects/<p>/exports/ (never raw/). Each export is then checked
by tools/qa.py; the script exits 1 if any check FAILs (--no-qa to skip). The
SRT sidecar is only a warning here — run tools/qa.py projects/<p> before handoff.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _media import assert_not_raw, project_dir  # noqa: E402

PRESETS = {
    "youtube":        dict(w=1920, h=1080, max_s=None,  maxrate="16M"),
    "youtube-shorts": dict(w=1080, h=1920, max_s=180,   maxrate="12M"),
    "instagram-reel": dict(w=1080, h=1920, max_s=180,   maxrate="10M"),
    "instagram-feed": dict(w=1080, h=1350, max_s=3600,  maxrate="10M"),
    "tiktok":         dict(w=1080, h=1920, max_s=600,   maxrate="12M"),
    "linkedin":       dict(w=None, h=None, max_s=900,   maxrate="10M"),
}
GROUPS = {"all-vertical": ["youtube-shorts", "instagram-reel", "tiktok", "linkedin"]}


def probe(path: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,avg_frame_rate,color_primaries,color_transfer:format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    return dict(w=v["width"], h=v["height"], fps=fps, dur=float(d["format"]["duration"]), audio=has_audio,
                primaries=v.get("color_primaries"), transfer=v.get("color_transfer"))


# SD/screen-capture primaries -> colorspace filter input preset (converts gamut + matrix to BT.709)
BT601 = {"bt470bg": "bt601-6-625", "smpte170m": "bt601-6-525", "bt470m": "bt601-6-525"}
HDR_TRC = {"smpte2084", "arib-std-b67"}


def measure_loudness(path: Path) -> dict | None:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
                        "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr
    try:
        blob = txt[txt.rindex("{"): txt.rindex("}") + 1]
        return json.loads(blob)
    except ValueError:
        return None


def linkedin_size(w: int, h: int) -> tuple[int, int]:
    r = w / h
    if r < 0.7:
        return 1080, 1920
    if r < 0.9:
        return 1080, 1350
    if r < 1.2:
        return 1080, 1080
    return 1920, 1080


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--platform", nargs="+", required=True)
    ap.add_argument("--out-dir", type=Path, default=None, help="default: ../exports next to input's project")
    ap.add_argument("--fit", choices=["error", "pad", "crop"], default="error")
    ap.add_argument("--keep-res", action="store_true", help="youtube only: keep source resolution if larger")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--no-qa", action="store_true", help="skip the tools/qa.py check after export")
    a = ap.parse_args()

    plats: list[str] = []
    for p in a.platform:
        plats += GROUPS.get(p, [p])
    bad = [p for p in plats if p not in PRESETS]
    if bad:
        sys.exit(f"unknown platform(s): {bad}. choose from {list(PRESETS) + list(GROUPS)}")

    info = probe(a.input)
    proj = project_dir(a.input)
    out_dir = a.out_dir or ((proj / "exports") if proj else a.input.resolve().parent / "exports")
    assert_not_raw(out_dir, "exports")
    out_dir.mkdir(parents=True, exist_ok=True)
    color = ""
    if info["transfer"] in HDR_TRC:
        print("WARNING: HDR source - tone-map to SDR BT.709 before exporting (export.py does not tone-map)")
    elif info["primaries"] in BT601:
        color = f",colorspace=all=bt709:iall={BT601[info['primaries']]}:format=yuv420p"
        print(f"converting {info['primaries']} (BT.601) -> BT.709")
    written: list[Path] = []
    fps = min(info["fps"], 60.0)
    loud = measure_loudness(a.input) if info["audio"] else None
    if loud:
        print(f"source loudness: {loud['input_i']} LUFS, true peak {loud['input_tp']} dBTP")

    for p in plats:
        pr = PRESETS[p]
        tw, th = (pr["w"], pr["h"]) if pr["w"] else linkedin_size(info["w"], info["h"])
        if p == "youtube" and a.keep_res and info["w"] > tw and abs(info["w"] / info["h"] - 16 / 9) < 0.02:
            tw, th = info["w"] - info["w"] % 2, info["h"] - info["h"] % 2
        src_r, dst_r = info["w"] / info["h"], tw / th
        if abs(src_r - dst_r) / dst_r > 0.02:
            if a.fit == "error":
                print(f"[{p}] SKIP: input is {info['w']}x{info['h']} but {p} needs {tw}x{th}. "
                      f"Reframe first: .venv/bin/python tools/reframe.py {a.input} <out> --aspect "
                      f"{'9:16' if th > tw else ('4:5' if th == 1350 else '16:9')}  (or pass --fit pad|crop)")
                continue
            if a.fit == "pad":
                vf = f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:black"
            else:
                vf = f"scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th}"
        else:
            vf = f"scale={tw}:{th}:flags=lanczos"
        vf += f",setsar=1,format=yuv420p{color}"
        if pr["max_s"] and info["dur"] > pr["max_s"]:
            print(f"[{p}] WARNING: duration {info['dur']:.1f}s exceeds {pr['max_s']}s recommended max")

        out = out_dir / f"{a.input.stem}__{p}.mp4"
        maxrate = pr["maxrate"]
        if tw * th > 1920 * 1080:
            maxrate = "45M"
        cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(a.input), "-vf", vf,
               "-r", f"{fps:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf),
               "-maxrate", maxrate, "-bufsize", str(int(maxrate[:-1]) * 2) + "M",
               "-profile:v", "high", "-g", str(int(round(fps * 2))),
               "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]
        if info["audio"]:
            if loud:
                af = ("loudnorm=I=-14:TP=-1:LRA=11:linear=true:"
                      f"measured_I={loud['input_i']}:measured_TP={loud['input_tp']}:"
                      f"measured_LRA={loud['input_lra']}:measured_thresh={loud['input_thresh']}:"
                      f"offset={loud['target_offset']}")
            else:
                af = "loudnorm=I=-14:TP=-1:LRA=11"
            cmd += ["-af", af + ",aresample=48000", "-c:a", "aac", "-b:a", "320k", "-ac", "2"]
        cmd += ["-movflags", "+faststart", str(out)]
        print(f"[{p}] -> {out.name} ({tw}x{th})")
        subprocess.run(cmd, check=True)
        written.append(out)
    print(f"done. exports in {out_dir}")

    if written and not a.no_qa:
        import qa
        print("\nQA:")
        reps = [qa.check_video(f, None, skip_loudness=False, require_srt=False) for f in written]
        qa.print_reports(reps)
        if any(r.status == "FAIL" for r in reps):
            sys.exit("export QA failed - fix the FAIL lines above before handing off")


if __name__ == "__main__":
    main()
