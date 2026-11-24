---
name: medium-form-editor
description: >-
  End-to-end workflow for editing medium-form horizontal video (3–20 min YouTube
  16:9 videos, walkthroughs, tutorials, essays, gear/camera reviews, build logs,
  and LinkedIn native videos): cold-open hook, chapter structure, A-roll + B-roll
  and screen-recording assembly, pacing, audio mix, color matching, chapters,
  SRT closed captions, and 16:9 export. Use when the user asks to edit a YouTube
  video, build log, tutorial, review, or any medium-form clip over 3 minutes.
---

# Medium-form editor (16:9, 3–20 min)

Run all commands from the repo root. Python is `.venv/bin/python`. Project
folders follow `projects/<date>-<slug>/{raw,assets,edit,exports,thumbnails}`.
Create one with `tools/new_project.sh <slug> medium`.

## 0. Audit footage and align on the cut

1. Read `brand/brand.md` and `projects/<p>/brief.md`.
2. Probe every source file:
   `.venv/bin/python tools/probe.py projects/<p>/raw/*`
   Flag mixed frame rates (e.g. 24 fps A-roll + 60 fps screen capture), HDR/HLG
   phone footage (needs SDR tone-mapping before mixing with Rec.709 camera
   footage), and dual-track audio.
3. Transcribe all talking-head takes (cached):
   `.venv/bin/python tools/transcribe_local.py projects/<p>/raw/*.mp4 --edit-dir projects/<p>/edit --language en`
   For multi-speaker interviews where diarization matters, use
   `.agents/skills/video-use/helpers/transcribe.py` (ElevenLabs Scribe) if
   `ELEVENLABS_API_KEY` is set in `.env`.
4. Pack transcripts:
   `.venv/bin/python .agents/skills/video-use/helpers/pack_transcripts.py --edit-dir projects/<p>/edit`
5. Read `takes_packed.md` and present a **plain-English edit plan** for approval
   before cutting:
   - Cold-open hook (0–25 s) — often pulled from a payoff clip later in the video
   - Chapter outline with approximate timestamps and target runtime
   - Retakes dropped vs. kept, and where B-roll / screen recordings / graphics cover cuts
   - Music / color / caption choices

## 1. Medium-form retention architecture

- **0:00–0:25 Cold open & promise:** Confirm the title/thumbnail promise in the
  first 5 seconds. Show the finished AI project, final photo/video grade, or
  workout result *before* explaining how you built it. Cut throat-clearing and
  "Hey everyone, welcome back to the channel."
- **Chapters every 1.5–4 minutes:** Each chapter has a clear micro-payoff and a
  clean transition (brief lower-third title card, whoosh, or B-roll reset).
- **Pattern interrupt every 30–60 s:** Switch from A-roll to screen recording,
  tight 1.08× punch-in on A-roll, B-roll cutaway, comparison graphic, or
  Remotion diagram. Never leave a static talking head untouched for > 45 s.
- **Pacing:** Medium-form breathes more than Shorts. Keep natural 0.12–0.20 s
  padding at cut boundaries so sentences land with authority, while still
  removing dead pauses > 0.6 s, retakes, and stumbles.
- **Niche playbooks:**
  - *AI builds / coding:* Show the working demo first. Zoom terminal/IDE screen
    recordings into the active region (`crop` + `scale`) rather than showing tiny
    full-screen 4K text. Use Remotion (`remotion-*`) for architecture diagrams.
  - *Photography & videography:* Show full-frame uncropped stills (add subtle
    Ken Burns slow push-in `zoompan` or clean 2–3 s holds), before/after wipes,
    and EXIF/gear overlays (`35mm · f/1.4 · 1/500 · ISO 100`). Never crush
    blacks or oversaturate graded camera footage.
  - *Fitness:* Pair voiceover explanations with clean form B-roll, slow-mo
    replays (`setpts=2.0*PTS` on 60 fps clips -> crisp 30 fps 50% speed), and
    callout cues.
  - *Content creation:* Show timeline breakdowns, side-by-side raw vs. edited
    clips, and concrete metrics/workflows.

## 2. Assemble the A-roll spine

- Use the **`video-use` skill** for multi-take editorial assembly (EDL ->
  per-segment graded extraction with 30 ms audio fades -> lossless `-c copy`
  concat). Follow every `video-use` Hard Rule.
- For a clean single-take monologue with no retakes, `tools/jumpcut.py` with
  `--pad 0.15 --min-gap 0.55` builds a fast first pass.
- Save the assembled A-roll timeline as `projects/<p>/edit/aroll.mp4`.

## 3. Layer B-roll, screen recordings, and motion graphics

- **B-roll cutaways:** Overlay B-roll onto `aroll.mp4` while keeping the A-roll
  audio continuous (J-cut by starting B-roll audio/video 0.25–0.5 s early or
  L-cut by letting A-roll audio carry under the incoming B-roll). Always reset
  overlay timestamps with `setpts=PTS-STARTPTS+<start>/TB`.
- **Motion graphics & chapter cards:** Build animated diagrams, lower-thirds,
  EXIF cards, or code callouts in Remotion (`remotion-create`, `remotion-markup`,
  `remotion-render`) or `video-use`'s PIL/Manim overlays. Spawn parallel
  subagents if rendering multiple independent animation slots.
- **Color matching:** Match B-roll/phone clips to A-roll exposure and white
  balance (`eq`, `colorbalance`, `lut3d`). Keep skin tones natural.

## 4. Audio mix and chapters

- **Dialogue first:** Clean voice is the anchor. Light high-pass at 80 Hz
  (`highpass=f=80`) removes rumble; gentle compression evens dynamic range.
- **Music bed:** Place subtle background tracks under intros, transitions, and
  B-roll montages, ducked to **-20 to -24 dB** under speech (or automated via
  `sidechaincompress`). Let music drop out completely during key technical
  explanations so the pacing shifts.
- **Chapter timestamps:** Generate `projects/<p>/edit/chapters.txt` directly
  from the final cut's edit boundaries (must start at `00:00`, at least 3
  chapters, each >= 10 s apart). `post-copywriter` will drop these directly into
  the YouTube description.

## 5. Captions and export

1. Transcribe the final cut (`edit/final_master.mp4`) and run
   `tools/captions.py` to generate a clean sentence-level **`.srt`** sidecar for
   YouTube and LinkedIn closed captions (proofread jargon!).
2. **YouTube 16:9:** Do **not** burn captions into YouTube medium-form unless
   requested — upload the `.srt` sidecar so viewers can toggle CC and YouTube
   indexes the clean text.
3. **LinkedIn 16:9 / 4:5 (if cross-posting):** Burn subtle `clean` style
   captions (`tools/captions.py --res 1920x1080 --style clean --y 0.86`) because
   most LinkedIn feeds autoplay muted.
4. Export with loudness normalization (-14 LUFS / -1 dBTP):
   - YouTube 1080p: `.venv/bin/python tools/export.py edit/final_master.mp4 --platform youtube --out-dir projects/<p>/exports`
   - YouTube 4K master: add `--keep-res`
   - LinkedIn: `--platform linkedin`

## 6. Post-production handoff

Once the medium-form master is approved:
1. Run **`clip-repurposer`** to carve 3–8 vertical shorts/Reels/TikToks/LinkedIn
   clips from the finished video.
2. Run **`thumbnail-designer`** to create 2–3 A/B YouTube 16:9 thumbnail
   concepts.
3. Run **`post-copywriter`** to generate YouTube titles, SEO description with
   chapters, pinned comment, and LinkedIn post copy.
4. Append a session summary to `projects/<p>/edit/project.md`.
