#!/usr/bin/env python3
"""Build social-style captions (ASS with active-word highlight) + a plain SRT.

Input is a Scribe-shaped transcript JSON (from tools/transcribe_local.py or
video-use's helpers/transcribe.py). Caption the FINAL cut: transcribe the
rendered video, then run this on that transcript, so timings already match the
output timeline. Burn captions LAST, after every overlay.

Usage:
    .venv/bin/python tools/captions.py <transcript.json> --out-dir <dir> \
        [--res 1080x1920] [--style pop|clean|boxed] [--words 3] [--upper] \
        [--font "Archivo Black"] [--size 84] [--highlight "#FFD400"] [--y 0.68]

Outputs:
    <dir>/<stem>.ass   styled, word-highlighted captions for burning in
    <dir>/<stem>.srt   plain sentence-level SRT (upload as closed captions on
                       YouTube / LinkedIn / TikTok for accessibility + SEO)

Burn in (fontsdir makes libass find the brand fonts):
    ffmpeg -i final.mp4 -vf "subtitles=<dir>/<stem>.ass:fontsdir=brand/fonts" \
        -c:v libx264 -crf 18 -preset medium -c:a copy final_captioned.mp4

Styles:
    pop    big bold uppercase-friendly text, thick outline, active word in
           highlight color and scaled up ~8%  (default for shorts)
    clean  white text, softer outline + shadow, active word highlighted
           (good for medium-form / LinkedIn)
    boxed  white text on a translucent dark box, no per-word color pop
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PUNCT_BREAK = re.compile(r"[.!?;:,]$")


def hex_to_ass(hex_color: str, alpha: int = 0) -> str:
    h = hex_color.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def ts_ass(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ts_srt(t: float) -> str:
    t = max(0.0, t)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600_000); m, ms = divmod(ms, 60_000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def clean(text: str) -> str:
    return text.replace("{", "(").replace("}", ")").replace("\\", "/")


def load_words(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    return [w for w in data.get("words", []) if w.get("type", "word") == "word" and w.get("text", "").strip()]


def chunk_words(words: list[dict], max_words: int, max_chars: int, gap: float) -> list[list[dict]]:
    chunks: list[list[dict]] = []
    cur: list[dict] = []
    for w in words:
        if cur:
            long_gap = w["start"] - cur[-1]["end"] > gap
            too_many = len(cur) >= max_words
            too_long = len(" ".join(x["text"] for x in cur + [w])) > max_chars
            if long_gap or too_many or too_long:
                chunks.append(cur); cur = []
        cur.append(w)
        if PUNCT_BREAK.search(w["text"]) and len(cur) >= 1:
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(chunks, W, H, style, font, size, hl, upper, ypos, strip_punct):
    white = "&H00FFFFFF"; black = "&H00000000"
    if style == "pop":
        outline, shadow, border, back = max(4, size // 12), 0, 1, "&H80000000"
    elif style == "clean":
        outline, shadow, border, back = max(2, size // 22), 3, 1, "&H96000000"
    else:  # boxed
        outline, shadow, border, back = 14, 0, 3, "&H5A000000"
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},{white},{white},{black if border == 1 else back},{back},0,0,0,0,100,100,0,0,{border},{outline},{shadow},5,{int(W*0.08)},{int(W*0.08)},0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    x, y = W // 2, int(H * ypos)
    hl_ass = hex_to_ass(hl)
    lines = []

    def fmt(t: str) -> str:
        t = clean(t)
        if strip_punct:
            t = re.sub(r"[.,!?;:]+$", "", t)
        return t.upper() if upper else t

    for ci, ch in enumerate(chunks):
        chunk_end = ch[-1]["end"] + 0.12
        if ci + 1 < len(chunks):
            chunk_end = min(chunk_end, chunks[ci + 1][0]["start"])
        if style == "boxed":
            text = " ".join(fmt(w["text"]) for w in ch)
            lines.append(f"Dialogue: 0,{ts_ass(ch[0]['start'])},{ts_ass(chunk_end)},Cap,,0,0,0,,{{\\pos({x},{y})}}{text}")
            continue
        for wi, w in enumerate(ch):
            start = w["start"] if wi else ch[0]["start"]
            end = ch[wi + 1]["start"] if wi + 1 < len(ch) else chunk_end
            if end <= start:
                continue
            parts = []
            for wj, w2 in enumerate(ch):
                t = fmt(w2["text"])
                if wj == wi:
                    scale = "\\fscx108\\fscy108" if style == "pop" else ""
                    parts.append(f"{{\\c{hl_ass}{scale}}}{t}{{\\c{white}\\fscx100\\fscy100}}")
                else:
                    parts.append(t)
            pop_in = "\\fad(40,0)" if wi == 0 else ""
            lines.append(f"Dialogue: 0,{ts_ass(start)},{ts_ass(end)},Cap,,0,0,0,,{{\\pos({x},{y}){pop_in}}}{' '.join(parts)}")
    return header + "\n".join(lines) + "\n"


def build_srt(words, max_chars=42, gap=0.6):
    cues, cur = [], []
    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap or len(" ".join(x["text"] for x in cur + [w])) > max_chars):
            cues.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.!?]$", w["text"]):
            cues.append(cur); cur = []
    if cur:
        cues.append(cur)
    out = []
    for i, c in enumerate(cues, 1):
        out.append(f"{i}\n{ts_srt(c[0]['start'])} --> {ts_srt(c[-1]['end'])}\n{' '.join(x['text'] for x in c)}\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--res", default="1080x1920", help="WxH of the video being captioned")
    ap.add_argument("--style", choices=["pop", "clean", "boxed"], default="pop")
    ap.add_argument("--words", type=int, default=3, help="max words per caption chunk")
    ap.add_argument("--max-chars", type=int, default=None)
    ap.add_argument("--upper", action="store_true")
    ap.add_argument("--keep-punct", action="store_true", help="keep trailing punctuation (stripped by default for pop)")
    ap.add_argument("--font", default="Archivo Black", help="family name of a font in brand/fonts")
    ap.add_argument("--size", type=int, default=None, help="font px at --res (default scales with width)")
    ap.add_argument("--highlight", default="#FFD400")
    ap.add_argument("--y", type=float, default=None, help="vertical center as fraction of height")
    a = ap.parse_args()

    W, H = (int(v) for v in a.res.lower().split("x"))
    vertical = H > W
    size = a.size or int(W * (0.078 if vertical else 0.042))
    ypos = a.y if a.y is not None else (0.68 if vertical else 0.84)
    max_chars = a.max_chars or (18 if vertical else 32)
    words = load_words(a.transcript)
    if not words:
        raise SystemExit("no words in transcript")
    chunks = chunk_words(words, a.words, max_chars, gap=0.45)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    stem = a.transcript.stem
    strip = (a.style == "pop") and not a.keep_punct
    (a.out_dir / f"{stem}.ass").write_text(build_ass(chunks, W, H, a.style, a.font, size, a.highlight, a.upper, ypos, strip))
    (a.out_dir / f"{stem}.srt").write_text(build_srt(words))
    print(f"wrote {a.out_dir / (stem + '.ass')} ({len(chunks)} chunks) and {a.out_dir / (stem + '.srt')}")


if __name__ == "__main__":
    main()
