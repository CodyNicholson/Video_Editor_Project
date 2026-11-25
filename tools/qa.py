#!/usr/bin/env python3
"""Pre-handoff QA gate: check deliverables against the platform specs.

Checks every file and exits 1 if anything FAILs, so it can gate a handoff.
Specs come from .agents/skills/social-video-specs/SKILL.md and tools/export.py.

Usage:
    .venv/bin/python tools/qa.py projects/<p>                     # everything in exports/ + final thumbnails
    .venv/bin/python tools/qa.py projects/<p>/exports/x__tiktok.mp4
    .venv/bin/python tools/qa.py exports/*.mp4 --platform tiktok   # force the platform
    .venv/bin/python tools/qa.py projects/<p>/edit/captions/x.ass  # caption safe-zone check
    .venv/bin/python tools/qa.py projects/<p> --json               # machine-readable

Video (.mp4/.mov):
    container + faststart, H.264 High yuv420p, BT.709 tags, frame size for the
    platform, fps <= 60, length limits, AAC 48 kHz stereo >= 256k,
    loudness -14 LUFS +/-1 LU and true peak <= -1 dBTP, no black first frame
    on vertical shorts, SRT sidecar present + valid for youtube/linkedin.
Captions (.srt / .ass):
    parseable, monotonic, no overlaps or empty cues, ends before the video;
    .ass vertical captions centred inside y = 0.55-0.72 of the frame.
Thumbnails (.jpg/.png):
    exact size for its aspect (1280x720, 1080x1920, 1080x1350), < 2 MB.

Platform comes from the export filename suffix (<stem>__<platform>.mp4),
then --platform, then the frame aspect.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# platform: frame size(s), hard max length (s), vertical?
SPECS = {
    "youtube":        dict(sizes=[(1920, 1080), (2560, 1440), (3840, 2160)], max_s=None, vertical=False),
    "youtube-shorts": dict(sizes=[(1080, 1920)], max_s=180, vertical=True),
    "instagram-reel": dict(sizes=[(1080, 1920)], max_s=180, vertical=True),
    "instagram-feed": dict(sizes=[(1080, 1350)], max_s=3600, vertical=False),
    "tiktok":         dict(sizes=[(1080, 1920)], max_s=600, vertical=True),
    "linkedin":       dict(sizes=[(1080, 1920), (1080, 1350), (1080, 1080), (1920, 1080)], max_s=900, vertical=None),
}
NEEDS_SRT = {"youtube", "linkedin"}
LUFS_TARGET, LUFS_TOL, TP_MAX = -14.0, 1.0, -0.9  # -1 dBTP target, 0.1 dB meter tolerance
THUMB_SIZES = {16 / 9: (1280, 720), 9 / 16: (1080, 1920), 4 / 5: (1080, 1350)}
VIDEO_EXT = {".mp4", ".mov", ".m4v"}
IMAGE_EXT = {".jpg", ".jpeg", ".png"}


@dataclass
class Report:
    path: Path
    kind: str
    platform: str | None = None
    checks: list[tuple[str, str, str]] = field(default_factory=list)  # (status, check, detail)

    def add(self, status: str, check: str, detail: str = "") -> None:
        self.checks.append((status, check, detail))

    def ok(self, cond: bool, check: str, detail: str, warn_only: bool = False) -> None:
        self.add("PASS" if cond else ("WARN" if warn_only else "FAIL"), check, detail)

    @property
    def status(self) -> str:
        s = {c[0] for c in self.checks}
        return "FAIL" if "FAIL" in s else "WARN" if "WARN" in s else "PASS"


# --- helpers -----------------------------------------------------------------

def ffprobe(path: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                       capture_output=True, text=True)
    if r.returncode:
        raise ValueError(r.stderr.strip() or "ffprobe failed")
    return json.loads(r.stdout)


def loudness(path: Path) -> dict | None:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af",
                        "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stderr[r.stderr.rindex("{"): r.stderr.rindex("}") + 1])
    except ValueError:
        return None


def first_frame_black(path: Path) -> bool:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-t", "0.25", "-i", str(path), "-an",
                        "-vf", "blackdetect=d=0.04:pix_th=0.10:pic_th=0.98", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"black_start:\s*([\d.]+)", r.stderr)
    return bool(m and float(m.group(1)) < 0.05)


def moov_before_mdat(path: Path) -> bool | None:
    """Walk top-level MP4 atoms: +faststart puts moov ahead of mdat."""
    try:
        with open(path, "rb") as f:
            while True:
                head = f.read(8)
                if len(head) < 8:
                    return None
                size, kind = struct.unpack(">I4s", head)
                if kind == b"moov":
                    return True
                if kind == b"mdat":
                    return False
                if size == 1:
                    size = struct.unpack(">Q", f.read(8))[0]
                    f.seek(size - 16, 1)
                elif size == 0:
                    return None
                else:
                    f.seek(size - 8, 1)
    except OSError:
        return None


def ts(t: str) -> float:
    h, m, s = t.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        line = next((l for l in lines if "-->" in l), None)
        if not line:
            raise ValueError(f"cue without timing: {block[:40]!r}")
        a, b = (x.strip().split()[0] for x in line.split("-->"))
        text = " ".join(lines[lines.index(line) + 1:])
        cues.append((ts(a), ts(b), text))
    return cues


def sidecar_srt(video: Path) -> Path:
    own = video.with_suffix(".srt")
    shared = video.with_name(re.sub(r"__[a-z-]+$", "", video.stem) + ".srt")
    return own if own.exists() or not shared.exists() else shared


def platform_of(path: Path, forced: str | None, w: int, h: int) -> str | None:
    m = re.search(r"__([a-z-]+)$", path.stem)
    if m and m.group(1) in SPECS:
        return m.group(1)
    if forced:
        return forced
    if w and h:
        r = w / h
        if r < 0.7:
            return "youtube-shorts"
        if r < 0.9:
            return "instagram-feed"
        if r > 1.6:
            return "youtube"
    return None


# --- checks ------------------------------------------------------------------

def check_srt_cues(rep: Report, cues, duration: float | None, label: str = "srt") -> None:
    rep.ok(bool(cues), f"{label} cues", f"{len(cues)} cues")
    if not cues:
        return
    bad = [i for i, (a, b, _) in enumerate(cues, 1) if b <= a]
    rep.ok(not bad, f"{label} timing", f"end <= start at cue(s) {bad[:5]}" if bad else "all cues have positive length")
    back = [i for i in range(1, len(cues)) if cues[i][0] < cues[i - 1][0]]
    rep.ok(not back, f"{label} order", f"out of order at cue(s) {back[:5]}" if back else "monotonic")
    overlap = [i + 1 for i in range(1, len(cues)) if cues[i][0] < cues[i - 1][1] - 0.01]
    rep.ok(not overlap, f"{label} overlaps", f"{len(overlap)} overlapping cues, e.g. #{overlap[:3]}" if overlap
           else "none", warn_only=True)
    empty = [i for i, c in enumerate(cues, 1) if not c[2].strip()]
    rep.ok(not empty, f"{label} empty cues", f"empty text at {empty[:5]}" if empty else "none", warn_only=True)
    if duration:
        end = max(b for _, b, _ in cues)
        rep.ok(end <= duration + 0.5, f"{label} length", f"last cue ends {end:.2f}s, video {duration:.2f}s")


def check_video(path: Path, forced: str | None, skip_loudness: bool, require_srt: bool = True) -> Report:
    rep = Report(path, "video")
    try:
        d = ffprobe(path)
    except ValueError as e:
        rep.add("FAIL", "probe", str(e))
        return rep
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    dur = float(d["format"].get("duration", 0) or 0)
    if not v:
        rep.add("FAIL", "video stream", "missing")
        return rep
    w, h = int(v["width"]), int(v["height"])
    rot = next((int(sd.get("rotation", 0)) for sd in v.get("side_data_list", []) or [] if "rotation" in sd), 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    plat = platform_of(path, forced, w, h)
    rep.platform = plat
    spec = SPECS.get(plat or "")

    # container
    if path.suffix.lower() in (".mp4", ".m4v"):
        fs = moov_before_mdat(path)
        rep.ok(fs is True, "faststart", "moov before mdat" if fs else "moov after mdat (re-mux with -movflags +faststart)")
    else:
        rep.add("WARN", "container", f"{path.suffix} - deliver .mp4")

    # video stream
    rep.ok(v.get("codec_name") == "h264", "video codec", v.get("codec_name", "?"))
    rep.ok((v.get("profile") or "").lower() == "high", "h264 profile", v.get("profile", "?"), warn_only=True)
    rep.ok(v.get("pix_fmt") == "yuv420p", "pixel format", v.get("pix_fmt", "?"))
    tags = {k: v.get(k) for k in ("color_primaries", "color_transfer", "color_space")}
    rep.ok(all(t == "bt709" for t in tags.values()), "BT.709 tags",
           ", ".join(f"{k.split('_')[1]}={t or 'unset'}" for k, t in tags.items()), warn_only=True)
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den or 0) else 0
    rep.ok(0 < fps <= 60.01, "frame rate", f"{fps:.3f} fps")
    rep.ok(rot == 0, "rotation", "none" if not rot else f"rotation metadata {rot} (bake it in)", warn_only=True)

    if spec:
        rep.ok((w, h) in spec["sizes"], "frame size", f"{w}x{h} (want {' or '.join(f'{a}x{b}' for a, b in spec['sizes'])})")
        if spec["max_s"]:
            rep.ok(dur <= spec["max_s"], "length", f"{dur:.1f}s (max {spec['max_s']}s for {plat})")
        else:
            rep.add("PASS", "length", f"{dur:.1f}s")
    else:
        rep.add("WARN", "platform", f"unknown - name the file <stem>__<platform>.mp4 or pass --platform ({w}x{h})")

    # audio
    if not a:
        rep.add("FAIL", "audio stream", "missing (platforms penalise silent uploads; add room tone or music)")
    else:
        rep.ok(a.get("codec_name") == "aac", "audio codec", a.get("codec_name", "?"))
        rep.ok(a.get("sample_rate") == "48000", "sample rate", f"{a.get('sample_rate')} Hz")
        rep.ok(a.get("channels") == 2, "channels", str(a.get("channels")), warn_only=True)
        br = int(a.get("bit_rate") or 0)
        rep.ok(br == 0 or br >= 250_000, "audio bitrate", f"{br // 1000} kbps" if br else "unknown", warn_only=True)
        if not skip_loudness:
            L = loudness(path)
            if L is None:
                rep.add("FAIL", "loudness", "could not measure")
            else:
                i, tp = float(L["input_i"]), float(L["input_tp"])
                rep.ok(abs(i - LUFS_TARGET) <= LUFS_TOL, "integrated loudness", f"{i:.2f} LUFS (target -14 +/-1)")
                rep.ok(tp <= TP_MAX, "true peak", f"{tp:.2f} dBTP (max -1)")

    # shorts: first frame must already be the hook
    vertical = spec["vertical"] if spec and spec["vertical"] is not None else h > w
    if vertical:
        black = first_frame_black(path)
        rep.ok(not black, "first frame", "black/fade-in first frame - open on the hook" if black else "not black")

    # srt sidecar: <stem>.srt, or one shared <base>.srt for all <base>__<platform>.mp4 exports
    srt = sidecar_srt(path)
    if plat in NEEDS_SRT or srt.exists():
        if not srt.exists():
            rep.add("FAIL" if require_srt else "WARN", "srt sidecar", f"missing {path.with_suffix('.srt').name} or "
                                           f"{re.sub(r'__[a-z-]+$', '', path.stem)}.srt (upload closed captions on {plat})")
        else:
            try:
                check_srt_cues(rep, parse_srt(srt), dur, "srt")
            except (ValueError, UnicodeDecodeError) as e:
                rep.add("FAIL", "srt parse", str(e))
    return rep


def check_srt(path: Path) -> Report:
    rep = Report(path, "srt")
    dur = None
    vids = [path.with_suffix(e) for e in (".mp4", ".mov")] + sorted(path.parent.glob(f"{path.stem}__*.mp4"))
    for v in vids:
        if v.exists():
            try:
                dur = float(ffprobe(v)["format"]["duration"])
                break
            except (ValueError, KeyError):
                pass
    try:
        check_srt_cues(rep, parse_srt(path), dur)
    except (ValueError, UnicodeDecodeError) as e:
        rep.add("FAIL", "srt parse", str(e))
    return rep


def check_ass(path: Path) -> Report:
    rep = Report(path, "ass")
    text = path.read_text(encoding="utf-8-sig")
    W = int(re.search(r"PlayResX:\s*(\d+)", text).group(1)) if "PlayResX" in text else 0
    H = int(re.search(r"PlayResY:\s*(\d+)", text).group(1)) if "PlayResY" in text else 0
    rep.ok(W > 0 and H > 0, "PlayRes", f"{W}x{H}")
    events = re.findall(r"^Dialogue:\s*\d+,([^,]+),([^,]+),[^\n]*$", text, re.M)
    rep.ok(bool(events), "events", f"{len(events)} dialogue lines")
    cues = [(ts(a), ts(b), "x") for a, b in events]
    bad = sum(1 for a, b, _ in cues if b <= a)
    rep.ok(bad == 0, "ass timing", f"{bad} zero/negative-length events" if bad else "ok")
    if H > W > 0:
        ys = [float(y) for y in re.findall(r"\\pos\(\s*[\d.]+\s*,\s*([\d.]+)", text)]
        if ys:
            lo, hi = min(ys) / H, max(ys) / H
            rep.ok(0.55 <= lo and hi <= 0.72, "vertical safe zone",
                   f"captions at y={lo:.2f}-{hi:.2f} of height (keep 0.55-0.72; bottom 480 px is platform UI)")
        else:
            rep.add("WARN", "vertical safe zone", "no \\pos tags - check MarginV manually")
        m = re.search(r"^Style:[^\n]*", text, re.M)
        if m:
            f = [x.strip() for x in m.group(0).split(",")]
            try:
                mr = int(f[20])
                rep.ok(mr >= 100, "right rail margin", f"MarginR={mr}px (action rail ~140 px)", warn_only=True)
            except (IndexError, ValueError):
                pass
    return rep


def check_image(path: Path) -> Report:
    from PIL import Image
    rep = Report(path, "thumbnail")
    with Image.open(path) as im:
        w, h = im.size
    r = w / h
    want = min(THUMB_SIZES.items(), key=lambda kv: abs(kv[0] - r))[1]
    rep.ok((w, h) == want, "size", f"{w}x{h} (want {want[0]}x{want[1]})")
    mb = path.stat().st_size / 1e6
    rep.ok(mb < 2.0, "file size", f"{mb:.2f} MB (YouTube limit 2 MB)")
    return rep


# --- discovery ----------------------------------------------------------------

def collect(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            exp = p / "exports" if (p / "exports").is_dir() else p
            out += sorted(f for f in exp.rglob("*") if f.suffix.lower() in VIDEO_EXT | {".srt", ".ass"})
            th = p / "thumbnails"
            if th.is_dir():  # finished thumbnails only, not frame grabs / previews / AI backgrounds
                out += sorted(f for f in th.glob("*") if f.suffix.lower() in IMAGE_EXT
                              and not re.search(r"(_preview|^bg_|^frame_|contact_sheet)", f.name))
        elif p.exists():
            out.append(p)
        else:
            print(f"not found: {p}", file=sys.stderr)
    # an .srt next to a video is checked as part of that video
    vids = {sidecar_srt(f) for f in out if f.suffix.lower() in VIDEO_EXT}
    return [f for f in out if not (f.suffix.lower() == ".srt" and f in vids)]


def run(paths: list[Path], platform: str | None = None, skip_loudness: bool = False) -> list[Report]:
    reps = []
    for f in collect(paths):
        ext = f.suffix.lower()
        if ext in VIDEO_EXT:
            reps.append(check_video(f, platform, skip_loudness))
        elif ext == ".srt":
            reps.append(check_srt(f))
        elif ext == ".ass":
            reps.append(check_ass(f))
        elif ext in IMAGE_EXT:
            reps.append(check_image(f))
    return reps


def print_reports(reps: list[Report], verbose: bool = False) -> None:
    for r in reps:
        tag = f" [{r.platform}]" if r.platform else ""
        print(f"{r.status:4}  {r.path}{tag}")
        for st, name, detail in r.checks:
            if verbose or st != "PASS":
                print(f"      {st:4}  {name}: {detail}")
    n = {s: sum(r.status == s for r in reps) for s in ("PASS", "WARN", "FAIL")}
    print(f"\nQA: {len(reps)} files - {n['PASS']} pass, {n['WARN']} warn, {n['FAIL']} fail")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--platform", choices=list(SPECS), default=None)
    ap.add_argument("--no-loudness", action="store_true", help="skip the (slow) loudness pass")
    ap.add_argument("-v", "--verbose", action="store_true", help="also list passing checks")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    reps = run(a.paths, a.platform, a.no_loudness)
    if a.json:
        print(json.dumps([dict(path=str(r.path), kind=r.kind, platform=r.platform, status=r.status,
                               checks=[dict(status=s, check=c, detail=d) for s, c, d in r.checks]) for r in reps], indent=1))
    else:
        print_reports(reps, a.verbose)
    if not reps:
        sys.exit("QA: nothing to check")
    sys.exit(1 if any(r.status == "FAIL" for r in reps) else 0)


if __name__ == "__main__":
    main()
