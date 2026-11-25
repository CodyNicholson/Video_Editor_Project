---
name: clip-repurposer
description: >-
  Workflow for turning a medium- or long-form video (YouTube video, build log,
  interview, gear review, workout breakdown) into 3–10 standalone vertical
  shorts for YouTube Shorts, Instagram Reels, TikTok, and LinkedIn. Covers
  transcript mining for self-contained hooks, multi-range stitching via
  tools/cut_clips.py, 9:16 reframing, captions, and batch platform exports.
  Use when the user asks to repurpose, clip, or pull shorts/reels from a longer
  video.
---

# Clip repurposer (long/medium -> vertical shorts)

The best shorts aren't random 45-second slices of a YouTube video — they are
**self-contained micro-stories** with a standalone hook, a concrete payoff, and
zero dangling references ("like I mentioned earlier...").

## 1. Mine the transcript for clip candidates

1. Ensure the source video is transcribed and packed:
   ```bash
   .venv/bin/python tools/transcribe_local.py <source.mp4> --edit-dir <edit_dir> --language en
   .venv/bin/python .agents/skills/video-use/helpers/pack_transcripts.py --edit-dir <edit_dir>
   ```
2. Read `<edit_dir>/takes_packed.md` end to end and shortlist **5–10 candidate
   clips** (typically 20–60 s each). Look for:
   - **Strong contrarian or surprising claim** ("Most people shoot f/1.4 wrong...")
   - **Single complete tip, demo, or framework** (1 AI workflow trick, 1 lighting
     setup, 1 form fix, 1 editing shortcut)
   - **Before/after reveal or milestone moment** (AI app working, graded shot
     reveal, PR lift)
   - **Story with tension + resolution** (a bug that broke the build + the fix)
3. **Multi-range stitching is encouraged:** If the punchy hook line happens at
   `04:12` and the explanation happens at `03:30–04:05`, reorder them in
   `ranges` (`[[252.0, 256.5], [210.0, 245.2]]`) so the short opens with the
   strongest 3 seconds!
4. Present the candidate table to the user and **wait for approval** before
   rendering:
   - Clip ID & working title
   - Opening hook line (exact quote)
   - Time range(s) & estimated duration
   - Best platform fit (Shorts / Reels / TikTok / LinkedIn)
   - Reframe strategy (`face`, `crop`, or `blurpad` for screen demos)

## 2. Write `clips.json` and cut on word boundaries

Snap every `[start, end]` range to exact word timestamps from the raw JSON
transcript (`<edit_dir>/transcripts/<stem>.json`), adding `0.06–0.12 s` of
padding at each edge so words never clip.

Write `projects/<p>/edit/clips.json`:
```json
{
  "source": "projects/<p>/exports/final_master__youtube.mp4",
  "clips": [
    {
      "id": "c01-hook-ai-workflow",
      "title": "Why I ditched manual timelines",
      "ranges": [[12.40, 16.80], [142.10, 174.50]]
    }
  ]
}
```

Cut all approved clips (30 ms audio fades at every splice):
```bash
.venv/bin/python tools/cut_clips.py projects/<p>/edit/clips.json --out-dir projects/<p>/edit/clips
```

## 3. Tighten, reframe, caption, and export each clip

For each clip in `projects/<p>/edit/clips/`:

1. **Optional tight jump-cut** if the clip still has long medium-form pauses:
   re-transcribe the clip and run `tools/jumpcut.py --drop-fillers --pad 0.08`.
2. **Reframe 16:9 -> 9:16:**
   - Talking head: `.venv/bin/python tools/reframe.py clip.mp4 clip_9x16.mp4 --aspect 9:16 --mode face`
   - Screen recording / wide photo / split demo: `--mode blurpad` (or build a
     custom split-screen ffmpeg filtergraph: zoomed screen top 55%, talking head
     bottom 45%!).
3. **Burn word-highlighted captions LAST:**
   - Transcribe `clip_9x16.mp4`, generate `.ass` + `.srt` with
     `tools/captions.py --res 1080x1920 --style pop --words 3 --upper`,
     proofread the `.ass`, and burn with `ffmpeg` (`fontsdir=brand/fonts`).
4. **Export for every vertical channel:**
   ```bash
   .venv/bin/python tools/export.py clip_captioned.mp4 --platform all-vertical --out-dir projects/<p>/exports/<clip_id>
   ```

## 4. Package each clip for posting

- Pull a clean cover frame for each clip (`tools/frames.py`) and optionally add
  a cover headline (`thumbnail-designer`, vertical 9:16 with 3:4 grid check).
- Write platform-specific captions and hooks for all clips in
  `projects/<p>/post_copy.md` (`post-copywriter`).
- Verify at least 2 stills per clip (frame 0 + mid-caption frame) to confirm
  good framing and safe-zone caption placement.
- Put each clip's `.srt` next to its exports as `<clip_id>.srt` (shared by all
  `<clip_id>__<platform>.mp4` files), then run
  `.venv/bin/python tools/qa.py projects/<p> edit/clips/captions_*/*.ass` and fix every FAIL.
