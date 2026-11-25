# I Built an AI Video Editor in Claude Code (Full Workflow)

- **Format:** medium (YouTube 16:9, ~12–13 min) + 7 modular vertical Shorts (9:16, 35–55s each)
- **Pillar:** Building AI Projects × Content Creation
- **Platforms:** YouTube (16:9), YouTube Shorts, Instagram Reels, TikTok, LinkedIn
- **Core idea (1 sentence):** Show how I built a real, non-slop AI video editing and publishing studio inside my terminal using Claude Code, Gemini, custom shared skills, and deterministic Python/FFmpeg tools — and prove it by editing this exact video (and spinning out 7 Shorts) with it.
- **Hook (first 2 seconds):** Split-screen of raw talking-head footage going into `raw/` → terminal command → finished captioned clip. *"I didn't open Premiere or DaVinci once to edit this video."*
- **Payoff / takeaway:** Pure-AI video tools fail when you let the LLM guess timestamps and pixels; the real unlock is pairing agent skills (`SKILL.md`) with deterministic local Python/FFmpeg scripts so you eliminate 80% of tedious prep, assembly, captioning, reframing, thumbnail QA, and export work while keeping human creative taste.
- **CTA:** Subscribe for weekly AI builds and creator workflows / grab the skills and repo setup in the description (and save/follow on Shorts/Reels/TikTok).
- **Must-keep moments / notes:**
  - Leave a clean **1.5-second silent pause** before and after every `[SHORT #N START]` / `[SHORT #N END]` boundary while filming so `tools/cut_clips.py` can slice every Short cleanly.
  - Frame A-roll with face centered horizontally (so `tools/reframe.py --mode face` crops cleanly to 9:16 without cutting off hands/shoulders).
  - Zoom terminal font up to **18–22pt** during screen recordings so commands and tables stay readable on mobile vertical screens.
  - Record live screen captures for: (1) `fetch_trends.py` 273× outlier table, (2) `transcribe_local.py` + `jumpcut.py`, (3) `cut_clips.py` + `reframe.py` + `captions.py`, (4) `frames.py` contact sheet + `thumbnail.py preview` 168×94 sheet.
