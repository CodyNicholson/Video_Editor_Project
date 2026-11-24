---
name: short-form-editor
description: >-
  End-to-end workflow for editing vertical short-form video (YouTube Shorts,
  Instagram Reels, TikTok, LinkedIn vertical) from raw talking-head, b-roll,
  screen-recording, or gym/photo-shoot footage: hook-first structure, tight
  jump cuts, 9:16 reframing, animated word-highlight captions, music/SFX,
  loudness, and multi-platform export. Use when the user asks for a short,
  reel, TikTok, or any vertical clip under 3 minutes.
---

# Short-form editor (9:16, ≤ 3 min)

Run all commands from the repo root. Python is `.venv/bin/python`. Project
folders follow `projects/<date>-<slug>/{raw,assets,edit,exports,thumbnails}`.
Create one with `tools/new_project.sh <slug> short`.

## 0. Understand before cutting

1. Read `brand/brand.md` (voice, colors, fonts, CTA) and the project `brief.md`.
2. Run `.venv/bin/python tools/probe.py projects/<p>/raw/*` to check resolution, fps, rotation, HDR, and audio.
3. Transcribe every take (results are cached):
   `.venv/bin/python tools/transcribe_local.py projects/<p>/raw/*.mp4 --edit-dir projects/<p>/edit --language en`
4. Pack the transcripts into a readable view:
   `.venv/bin/python .agents/skills/video-use/helpers/pack_transcripts.py --edit-dir projects/<p>/edit`
5. Propose the cut in plain English and **wait for approval**: the hook line, beat order, what gets dropped, target length, caption style, and platforms.

## 1. Structure that performs

- **Hook (0–2 s):** start on the most surprising claim, result, or visual. Never open on "Hey guys" or a logo. Put a text hook on screen in frame 1.
- **Re-hook every 5–8 s:** pattern interrupt, new visual, zoom punch-in, or b-roll.
- **Payoff before the last 15%**, then a quick CTA (≤ 2 s). End on a frame that loops cleanly into the opening when it fits.
- **Pacing:** cut every breath and pause > 0.3 s on talking heads. Keep 0.06–0.10 s of padding for a fast feel.
- **Niche notes:**
  - AI builds: show the result first, then the screen recording. Zoom screen recordings to 150–200% so code and UI are readable on a phone.
  - Photography and videography: before→after reveal, settings card overlay (focal length, f-stop, shutter speed, ISO), BTS→final shot.
  - Fitness: demonstrate the move in the first second, use rep counters or form cues as text, cut on the beat.
  - Content creation: tease the tool or result first, then the step-by-step.

## 2. Cut

Choose the lightest path that works:

- **Single talking-head take → automatic jump cut:**
  `.venv/bin/python tools/jumpcut.py raw/take.mp4 edit/cut.mp4 --transcript edit/transcripts/take.json --drop-fillers --pad 0.08`
  Use `--dry-run` first to see the segments and the percentage removed.
- **Multiple takes, retakes, b-roll, or reordering → the `video-use` skill.** Write an EDL from the packed transcript and render with its `helpers/render.py`. Its Hard Rules apply: cuts land on word boundaries, every cut gets a 30 ms audio fade, and subtitles go on LAST.
- **Clips taken from a long video → the `clip-repurposer` skill.**

## 3. Reframe to 9:16 (if the source is horizontal)

`.venv/bin/python tools/reframe.py edit/cut.mp4 edit/cut_9x16.mp4 --aspect 9:16 --mode face`

- `face` crops around the median face position. Check the printed crop. Override it with `--x 0.0–1.0` if needed.
- Use `blurpad` for screen recordings, wide landscape shots, or photos where cropping would lose content.
- Shoot or crop so faces sit in the upper-middle third, clear of the caption zone.

## 4. Graphics, music, SFX (optional, add only what helps)

- **Text hooks, lower thirds, progress bars, animated callouts, settings cards:** build them in Remotion (`remotion-*` skills), render to a transparent ProRes 4444 or MOV, and overlay with ffmpeg. Alternatively, use video-use's PIL/Manim overlay path.
- **Punch-in zooms:** `crop` + `scale` with a time expression on ffmpeg, about 1.0→1.08 over 6–10 frames on the emphasized word.
- **Music:** put licensed tracks in `projects/<p>/assets/` or `brand/music/`. Duck under speech to about -18 to -22 dB relative to voice (`sidechaincompress` or a `volume` envelope). Platform-native trending audio gets added in-app, so export a version without music when the user plans to do that.
- **SFX:** only on visible events (whoosh on a transition, pop on a text hit). Keep it to 1 per 3–5 s at most.

## 5. Captions (always for shorts, burned in LAST)

1. Transcribe the final cut so the timings match the output:
   `.venv/bin/python tools/transcribe_local.py edit/cut_9x16.mp4 --edit-dir projects/<p>/edit`
2. `.venv/bin/python tools/captions.py projects/<p>/edit/transcripts/cut_9x16.json --out-dir projects/<p>/edit/captions --res 1080x1920 --style pop --words 3 --upper --highlight "<brand accent>"`
3. Fix any misheard words, names, or tech terms (Claude, Gemini, Sony, f/1.8...) directly in the `.ass` file. It's plain text.
4. Burn them in:
   `ffmpeg -i edit/cut_9x16.mp4 -vf "subtitles=projects/<p>/edit/captions/cut_9x16.ass:fontsdir=brand/fonts" -c:v libx264 -crf 18 -preset medium -c:a copy edit/final.mp4`

See the `captions-subtitles` skill for styles and troubleshooting.

## 6. Export

`.venv/bin/python tools/export.py edit/final.mp4 --platform all-vertical --out-dir projects/<p>/exports`

This produces Shorts, Reels, TikTok, and LinkedIn versions at -14 LUFS. Follow up with the `thumbnail-designer` skill (cover) and the `post-copywriter` skill (captions and hashtags).

## 7. Self-check before showing the user

- Pull 4–6 stills from the output and look at them (`tools/frames.py final.mp4 --at ...`, or video-use's `timeline_view.py` at the cut points). Check for caption overlap with faces or UI, black frames, and bad crops.
- `tools/probe.py --loudness exports/*` should show -14 ±1 LUFS.
- The first frame isn't black and the hook text is visible at 0.0 s.
- Duration fits each platform's sweet spot (`social-video-specs`).
- Add a short session note to `projects/<p>/edit/project.md` covering the decisions and what's still open.
