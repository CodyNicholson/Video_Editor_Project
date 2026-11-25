#!/usr/bin/env python3
"""Quick automatic jump-cut: remove dead air (and optionally filler words).

Fast path for talking-head shorts when you don't need a hand-crafted EDL.
For editorial cuts (retakes, story order, b-roll) use the video-use skill.

Usage:
    # transcript-driven (preferred: word-accurate, can drop fillers)
    .venv/bin/python tools/jumpcut.py in.mp4 out.mp4 --transcript edit/transcripts/in.json --drop-fillers
    # audio-only fallback (no transcript needed)
    .venv/bin/python tools/jumpcut.py in.mp4 out.mp4 --noise -35 --min-silence 0.4

Tuning:
    --pad       seconds kept before/after speech (0.06 tight/fast .. 0.20 relaxed)
    --min-gap   gaps shorter than this are kept (breaths); default 0.30
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _media import assert_not_raw, probe, render_segments, speech_segments_from_silence, speech_segments_from_transcript  # noqa: E402

FILLERS = {"um", "umm", "uh", "uhh", "erm", "hmm", "mm", "ah"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--transcript", type=Path, default=None)
    ap.add_argument("--drop-fillers", action="store_true")
    ap.add_argument("--pad", type=float, default=0.10)
    ap.add_argument("--min-gap", type=float, default=0.30)
    ap.add_argument("--noise", type=float, default=-35.0)
    ap.add_argument("--min-silence", type=float, default=0.40)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    assert_not_raw(a.output)
    info = probe(a.input)
    if a.transcript:
        segs = speech_segments_from_transcript(a.transcript, a.pad, a.min_gap, info["dur"],
                                               FILLERS if a.drop_fillers else None)
    else:
        segs = speech_segments_from_silence(a.input, a.noise, a.min_silence, a.pad, info["dur"])
    kept = sum(e - s for s, e in segs)
    print(f"{len(segs)} segments, {info['dur']:.1f}s -> {kept:.1f}s ({100 * (1 - kept / info['dur']):.0f}% removed)")
    if a.dry_run:
        for s, e in segs:
            print(f"  {s:8.2f} - {e:8.2f}")
        return
    render_segments(a.input, segs, a.output)
    print(f"wrote {a.output}")


if __name__ == "__main__":
    main()
