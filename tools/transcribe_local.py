#!/usr/bin/env python3
"""Local, offline word-level transcription with mlx-whisper (Apple Silicon GPU).

Writes an ElevenLabs-Scribe-compatible JSON so every video-use helper
(pack_transcripts.py, timeline_view.py, render.py) works unchanged, plus the
transcript is cached exactly where video-use looks for it:

    <edit_dir>/transcripts/<video_stem>.json

Scribe shape:
    {"language_code": "en", "text": "...", "source": "...", "words": [
        {"text": "Hello", "start": 0.12, "end": 0.40, "type": "word", "speaker_id": "speaker_0"},
        {"text": " ",     "start": 0.40, "end": 0.55, "type": "spacing", "speaker_id": "speaker_0"},
        ...]}

Usage:
    .venv/bin/python tools/transcribe_local.py <video> --edit-dir projects/<slug>/edit
    .venv/bin/python tools/transcribe_local.py <video> --edit-dir ... --language en --force
    .venv/bin/python tools/transcribe_local.py a.mp4 b.mp4 c.mp4 --edit-dir ...   # batch

Notes:
  * Cached: an existing transcript is reused unless --force.
  * Whisper tends to drop filler words. We bias it to keep them with an
    initial prompt full of fillers; still, verify "um/uh" removal visually
    with video-use's timeline_view at ambiguous cut points.
  * No diarization: every word is speaker_0. For multi-speaker interviews,
    use video-use's ElevenLabs path (helpers/transcribe.py) if a key exists.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"
FILLER_PROMPT = (
    "Umm, uh, so, like, you know, I mean... Okay, uh, let's, um, get into it. "
    "Hmm, yeah, uh-huh."
)


def transcript_path(edit_dir: Path, video: Path) -> Path:
    return edit_dir / "transcripts" / f"{video.stem}.json"


def extract_audio(video: Path, wav: Path) -> None:
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-map", "0:a:0",
           "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg audio extract failed for {video}:\n{r.stderr[-800:]}")


def to_scribe(result: dict, source: str) -> dict:
    words_out: list[dict] = []
    prev_end: float | None = None
    for seg in result.get("segments", []):
        for w in seg.get("words", []) or []:
            text = (w.get("word") or "").strip()
            if not text:
                continue
            start = round(float(w["start"]), 3)
            end = round(float(w["end"]), 3)
            if end < start:
                end = start
            if prev_end is not None and start > prev_end:
                words_out.append({"text": " ", "start": prev_end, "end": start,
                                  "type": "spacing", "speaker_id": "speaker_0"})
            words_out.append({"text": text, "start": start, "end": end,
                              "type": "word", "speaker_id": "speaker_0",
                              "probability": round(float(w.get("probability", 0.0)), 3)})
            prev_end = end
    return {
        "language_code": result.get("language", ""),
        "text": (result.get("text") or "").strip(),
        "source": source,
        "engine": "mlx-whisper",
        "words": words_out,
    }


def transcribe_one(video: Path, edit_dir: Path, model: str, language: str | None,
                   force: bool) -> Path:
    import mlx_whisper  # imported lazily so --help is fast

    out = transcript_path(edit_dir, video)
    if out.exists() and not force:
        print(f"cached: {out}")
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / f"{video.stem}.wav"
        extract_audio(video, wav)
        kwargs = dict(path_or_hf_repo=model, word_timestamps=True,
                      initial_prompt=FILLER_PROMPT,
                      condition_on_previous_text=False, verbose=None)
        if language:
            kwargs["language"] = language
        result = mlx_whisper.transcribe(str(wav), **kwargs)
    payload = to_scribe(result, str(video))
    out.write_text(json.dumps(payload, indent=1))
    n = sum(1 for w in payload["words"] if w["type"] == "word")
    print(f"saved: {out}  ({n} words, {time.time() - t0:.1f}s)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("videos", nargs="+", type=Path)
    ap.add_argument("--edit-dir", type=Path, default=None,
                    help="default: <video_dir>/edit (video-use convention)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--language", default=None, help="e.g. en; auto-detect if omitted")
    ap.add_argument("--force", action="store_true", help="ignore cache")
    a = ap.parse_args()
    for v in a.videos:
        v = v.resolve()
        if not v.exists():
            sys.exit(f"not found: {v}")
        edit_dir = (a.edit_dir or v.parent / "edit").resolve()
        transcribe_one(v, edit_dir, a.model, a.language, a.force)


if __name__ == "__main__":
    main()
