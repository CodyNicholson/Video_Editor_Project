# Session Memory — `2026-11-23-how-I-build-ai-projects`

## Session 1 — 2026-11-23

**Strategy:** Edit the `21m 22s` `1512×982` 25 fps raw screen-capture + webcam walkthrough into a clean `21:10` YouTube 16:9 master (`1920×1080` centered on `#0F1115` dark studio slate so 100% of VS Code sidebars and top-right webcam PiP stay sharp and uncropped), carve 4 standalone vertical 9:16 shorts (`30–58s`) with custom frame-1 hook cards and word-highlighted `pop` captions for YouTube Shorts, Instagram Reels, TikTok, and LinkedIn, produce 3 distinct A/B YouTube 16:9 thumbnails + 1 vertical cover using studio-relit portrait backgrounds and `Anton` typography, and write full platform-native copy in `post_copy.md`.

**Decisions:**
- **Cold-open hook (`00:00–00:18`):** Pulled the multi-agent orchestrator payoff (`685.10–697.04` + `702.50–708.40`: Blender + Music + Unity agents) to open on immediate concrete value, then trimmed opening silence and `"Hey team. Um,"` (`0.00–4.42`).
- **Live Music Box demos preserved:** Explicitly kept `[83.0–91.3]`, `[97.0–106.5]`, and `[202.8–206.4]` untouched so Greensleeves + piano/drum playback plays cleanly.
- **Public-audience trim (`15:28` aside):** Surgically removed `[942.26–951.72]` (*"not a lawyer / legal ramifications"*) and `[969.92–973.98]` (*"felt entitled / found PDF online"*) on exact word boundaries with 30 ms audio fades.
- **Audio loudness:** Applied 80 Hz high-pass + two-pass EBU R128 loudnorm (`-18.16 LUFS / +0.38 dBTP` -> **`-14.09 LUFS / -0.97 dBTP`** on YouTube master; **`-14.03 to -14.17 LUFS`** across all 4 shorts).
- **LinkedIn strategy:** Because LinkedIn caps native video at 15 minutes, delivered all 4 captioned vertical shorts (`exports/shorts/<id>/<id>__linkedin.mp4` + `.srt`) for native LinkedIn posting with the full 21-min YouTube link in the first comment.
- **Thumbnails:** Generated 3 studio-relit portrait backgrounds via `image-generator` referencing `thumbnails/portraits/frame_03_0022.00s.jpg` (fallback from `gemini-api` Free Tier 429) and composited crisp `Anton` typography (`yt_concept_a_system.jpg`, `yt_concept_b_claude_gemini.jpg`, `yt_concept_c_skills.jpg`). Fixed initial vertical cover overlap caught during visual QA by building a dedicated dark-obsidian top canvas (`vertical_cover_ai_system.jpg`).

**Verification:**
- Visual inspection of all 3 YouTube thumbnail `168×94` previews + vertical cover 3:4 Instagram grid preview passed.
- Visual inspection of burned captions + hook cards on all 4 vertical shorts passed (safe-zone aligned, `Archivo Black` + `#FFD400` active word rendered cleanly).
- Visual inspection of `how-I-build-ai-projects__youtube.mp4` frames and proofread 516-cue SRT passed.

**Outstanding:**
- Fill in `[LINK: ...]` placeholders in `post_copy.md` once the YouTube video URL and TikTok handle are live.
- Optional: Add subtle chapter lower-third cards in Remotion if desired for a v2 pass.
