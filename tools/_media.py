"""Shared ffmpeg helpers for tools/*.py (segment extract + lossless concat)."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

FADE = 0.03  # 30 ms audio fades at every cut -> no pops


def probe(path: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,avg_frame_rate:format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    fps = 30.0
    if v and v.get("avg_frame_rate", "0/0") != "0/0":
        n, dd = v["avg_frame_rate"].split("/")
        fps = float(n) / float(dd)
    return dict(w=v["width"] if v else 0, h=v["height"] if v else 0, fps=fps,
                dur=float(d["format"]["duration"]),
                audio=any(s["codec_type"] == "audio" for s in d["streams"]))


def render_segments(src: Path, segments: list[tuple[float, float]], out: Path,
                    crf: int = 18, extra_vf: str | None = None) -> Path:
    """Extract each [start, end) with 30 ms audio fades, then concat with -c copy."""
    info = probe(src)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        parts = []
        for i, (s, e) in enumerate(segments):
            dur = max(0.05, e - s)
            part = tmpd / f"seg_{i:04d}.mp4"
            cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{s:.3f}", "-i", str(src), "-t", f"{dur:.3f}"]
            vf = "format=yuv420p" if not extra_vf else f"{extra_vf},format=yuv420p"
            cmd += ["-vf", vf, "-c:v", "libx264", "-crf", str(crf), "-preset", "fast",
                    "-r", f"{info['fps']:.3f}"]
            if info["audio"]:
                fo = max(0.0, dur - FADE)
                cmd += ["-af", f"afade=t=in:st=0:d={FADE},afade=t=out:st={fo:.3f}:d={FADE}",
                        "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
            cmd.append(str(part))
            subprocess.run(cmd, check=True)
            parts.append(part)
        lst = tmpd / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    return out


def speech_segments_from_transcript(transcript: Path, pad: float, min_gap: float,
                                    total: float, drop_words: set[str] | None = None) -> list[tuple[float, float]]:
    data = json.loads(transcript.read_text())
    words = [w for w in data.get("words", []) if w.get("type", "word") == "word"]
    if drop_words:
        words = [w for w in words if w["text"].lower().strip(".,!?") not in drop_words]
    segs: list[list[float]] = []
    for w in words:
        s, e = max(0.0, w["start"] - pad), min(total, w["end"] + pad)
        if segs and s - segs[-1][1] < min_gap:
            segs[-1][1] = max(segs[-1][1], e)
        else:
            segs.append([s, e])
    return [(s, e) for s, e in segs]


def speech_segments_from_silence(src: Path, noise_db: float, min_silence: float, pad: float,
                                 total: float) -> list[tuple[float, float]]:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-vn", "-af",
                        f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-"],
                       capture_output=True, text=True)
    silences, start = [], None
    for line in r.stderr.splitlines():
        if "silence_start:" in line:
            start = float(line.split("silence_start:")[1].split()[0])
        elif "silence_end:" in line and start is not None:
            end = float(line.split("silence_end:")[1].split()[0])
            silences.append((start, end)); start = None
    if start is not None:
        silences.append((start, total))
    keep, cur = [], 0.0
    for s, e in silences:
        if s - cur > 0.05:
            keep.append((max(0.0, cur - pad if cur else 0.0), min(total, s + pad)))
        cur = e
    if total - cur > 0.05:
        keep.append((max(0.0, cur - pad), total))
    return keep


YUNET_MODEL = Path(__file__).resolve().parent / "models" / "face_detection_yunet_2023mar.onnx"


class FaceDetector:
    """Detect faces in a BGR frame; returns list of (x, y, w, h) in the resized 640px-wide image."""

    def __init__(self, score_threshold: float = 0.65):
        import cv2
        self._cv2 = cv2
        self._yunet = None
        self._cascade = None
        self._size = None
        if YUNET_MODEL.exists() and hasattr(cv2, "FaceDetectorYN"):
            self._yunet = cv2.FaceDetectorYN.create(str(YUNET_MODEL), "", (640, 360), score_threshold)
        elif hasattr(cv2, "CascadeClassifier"):
            self._cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def detect(self, frame_bgr, target_w: int = 640) -> tuple[list[tuple[int, int, int, int]], tuple[int, int]]:
        cv2 = self._cv2
        h, w = frame_bgr.shape[:2]
        th = max(2, int(round(h * target_w / w)))
        small = cv2.resize(frame_bgr, (target_w, th))
        if self._yunet is not None:
            if self._size != (target_w, th):
                self._yunet.setInputSize((target_w, th))
                self._size = (target_w, th)
            _, faces = self._yunet.detect(small)
            if faces is None or len(faces) == 0:
                return [], (target_w, th)
            return [(int(f[0]), int(f[1]), int(f[2]), int(f[3])) for f in faces], (target_w, th)
        if self._cascade is not None:
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            faces = self._cascade.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
            return [(int(x), int(y), int(fw), int(fh)) for (x, y, fw, fh) in faces], (target_w, th)
        return [], (target_w, th)
