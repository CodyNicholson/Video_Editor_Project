#!/usr/bin/env python3
"""Cut highlight clips (for repurposing long videos into shorts) from a clips.json.

clips.json:
    {"source": "projects/<slug>/raw/long.mp4",
     "clips": [
        {"id": "c01-hook-ai-agent", "title": "Why my agent failed",
         "ranges": [[123.40, 151.90]]},
        {"id": "c02-stitched", "title": "3 lighting tips",
         "ranges": [[310.2, 318.0], [342.5, 371.1]]}   # multiple ranges = stitched
     ]}

Range edges must sit on word boundaries (take them from the transcript) with
~0.05-0.15 s padding. Each clip renders with 30 ms audio fades per range.

Usage:
    .venv/bin/python tools/cut_clips.py clips.json --out-dir projects/<slug>/edit/clips
    .venv/bin/python tools/cut_clips.py clips.json --out-dir ... --only c01-hook-ai-agent
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _media import assert_not_raw, render_segments  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips_json", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    assert_not_raw(a.out_dir, "clips")
    spec = json.loads(a.clips_json.read_text())
    src = Path(spec["source"])
    for c in spec["clips"]:
        if a.only and c["id"] not in a.only:
            continue
        ranges = [(float(s), float(e)) for s, e in c["ranges"]]
        out = a.out_dir / f"{c['id']}.mp4"
        render_segments(src, ranges, out)
        print(f"{c['id']}: {sum(e - s for s, e in ranges):.1f}s -> {out}")


if __name__ == "__main__":
    main()
