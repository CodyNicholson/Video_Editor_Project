# Script: I Built an AI Video Editor in Claude Code (Full Workflow)

- **Target Long-Form Runtime:** ~12:00–12:45 (16:9 YouTube sweet spot)
- **Modular Shorts Built In:** **7 standalone 9:16 clips** (35–55 seconds each) — engineered to slice straight out of the main edit via `tools/cut_clips.py` (`clip-repurposer`)
- **Thumbnail Concept:** Text: `ZERO TIMELINE` (white + `#FFD400` or `#38BDF8` accent) | Visual: Moody dark studio split — live Claude Code terminal running a skill on the left, clean graded frame + active-word captions on the right, expressive reaction face.
- **Alternate Titles (<= 60 chars):**
  1. `I Built an AI Video Editor in Claude Code (Full Workflow)` *(57 chars — primary)*
  2. `My Terminal Edits My YouTube Videos Now (Free Skills)` *(53 chars)*
  3. `No Timeline: Editing Real Videos With AI Agents` *(47 chars)*

---

## Filming Rules (Read Before Hitting Record)

To make splitting this video into 7 clean Shorts effortless later:
1. **Pause 1.5 seconds in silence** before every `[SHORT #N START]` and after every `[SHORT #N END]`. Don't run sentences together across those lines — it gives `tools/cut_clips.py` crystal-clear word boundaries.
2. **Treat `[YT BRIDGE]` lines as YouTube-only glue:** Read them normally while filming for the 16:9 flow; we trim them out in `clips.json` when exporting the standalone Shorts.
3. **Center your framing for 9:16:** Keep your head and shoulders centered in the 16:9 frame so `tools/reframe.py --mode face` crops cleanly to vertical without clipping you.
4. **Zoom your terminal to 18–22pt** during every screen recording so viewers on phones can actually read commands, tables, and folder trees.

---

## Quick Map: Long-Form Chapters & Extractable Shorts

| Part | YouTube Chapter | Approx. Time | Standalone Short? | Short Hook / Title | Short Runtime |
|---|---|---:|---|---|---:|
| **Part 1** | Cold Open & The Proof | `0:00–0:50` | **Short #1** | *I Didn't Open Premiere Once to Edit This Video* | ~45s |
| **Part 2** | Why Pure-AI Video Editors Fail | `0:50–1:45` | **Short #2** | *Stop Making LLMs Guess (Brain vs. Hands Pattern)* | ~48s |
| **Part 3** | One Repo for Both Claude Code & Gemini | `1:45–3:05` | **Short #3** | *Write Every Skill Once — Run It in Claude & Gemini* | ~42s |
| **Part 4** | Before You Record: The 273× Outlier Agent | `3:05–4:30` | **Short #4** | *This AI Agent Found a 273× YouTube Outlier in 20s* | ~50s |
| **Part 5** | Live Edit: Local Transcription & Word-Boundary Cuts | `4:30–6:50` | *(Optional Short)* | *Free Offline Word-Level Transcription on Apple Silicon* | ~40s |
| **Part 6** | 1 Long Video → 7 Captioned Shorts From Terminal | `6:50–8:45` | **Short #5** | *How I Turn 1 Video Into 7 Shorts Without a Timeline* | ~50s |
| **Part 7** | AI Thumbnails & The 168×94 Mobile Audit | `8:45–10:15` | **Short #6** | *Why Most AI Thumbnails Fail (The 168×94 Test)* | ~48s |
| **Part 8** | Honest Reality Check: What Still Breaks | `10:15–12:15` | **Short #7** | *What AI Video Editors Still Can't Replace* | ~45s |

---

## PART 1 — Cold Open & The Proof (`0:00–0:50`)

> **SHORT #1 METADATA**
> - **Clip ID:** `s01-no-timeline-proof`
> - **Frame-1 On-Screen Text:** `NO TIMELINE. ONE WORKSPACE.`
> - **TikTok Search Keywords:** `claude code video editing workflow ai video editor`
> - **IG Reels Save Angle:** Put the 4-layer stack (`Claude Code / Gemini + mlx-whisper + FFmpeg + Remotion`) in the caption.

### `[SHORT #1 START]`

**[VISUAL: 0:00–0:04 — Fast split-screen: top shows raw, unedited talking-head take with a stumble/silence being dropped into `raw/`; bottom shows Claude Code terminal executing `transcribe_local.py` → `jumpcut.py` → `captions.py` → finished graded clip snapping into place.]**

**CODY (A-Roll, direct to lens, energetic):**
I didn't open Premiere, Final Cut, or DaVinci Resolve once to edit the video you're watching right now.

**[VISUAL: Quick 2-second flash of the `Video_Editor_Project/` folder tree in terminal — `tools/`, `.agents/skills/`, `brand/brand.md`, `projects/`.]**

Right now, YouTube and TikTok are flooded with tutorials showing how to make faceless AI cartoon shorts with Claude Code. And honestly, most of it looks like AI slop.

I didn't want a slop generator. I shoot real footage with real cameras, and I wanted an actual editing studio inside my terminal that handles the boring 80% — transcribing, cutting dead air, reframing for vertical, burning word-highlighted captions, building thumbnails, and writing post copy — without touching a timeline.

**[VISUAL: Flash of the final rendered clip playing with crisp word-highlighted captions + `-14 LUFS` export line in terminal.]**

So I built an entire agent-driven video studio using Claude Code, Gemini, Python, FFmpeg, and Remotion.

### `[SHORT #1 END — ~43s | Pause 1.5s silently]`

**[YT BRIDGE — trim for Short]**
In the next 12 minutes, I'm going to walk you through the exact architecture, run a live edit from raw camera files to platform-ready exports, show you the trend-research agent that literally picked this video topic, and be honest about what still breaks.

---

## PART 2 — Why Pure-AI Video Editors Fail (`0:50–1:45`)

> **SHORT #2 METADATA**
> - **Clip ID:** `s02-stop-making-llms-guess`
> - **Frame-1 On-Screen Text:** `STOP MAKING LLMS GUESS`
> - **TikTok Search Keywords:** `ai coding agents architecture deterministic python tools`
> - **IG Reels Save Angle:** Clean visual overlay: `LLM = Brain (Decisions) | Python/FFmpeg = Hands (Execution)`.

### `[SHORT #2 START]`

**[VISUAL: A-Roll → cut to clean simple diagram graphic (Remotion overlay): `LLM (Decisions)` → `Deterministic Scripts (Math / Pixels / Audio)`.]**

**CODY:**
The fastest way to break an AI coding agent is asking the LLM to do everything itself.

Hand raw video to a plain AI prompt and it hallucinates timestamps, slices mid-word, drifts captions by half a second, and blows out your audio levels.

**[VISUAL: Screen capture scrolling cleanly through `tools/` showing `probe.py`, `transcribe_local.py`, `jumpcut.py`, `cut_clips.py`, `reframe.py`, `captions.py`, `export.py`, `frames.py`, `thumbnail.py`.]**

Here's the pattern that actually works: **the LLM is the brain, and deterministic Python scripts are the hands.**

Claude Code never guesses loudness math or crop coordinates. It calls ten small Python and FFmpeg scripts in `tools/` that enforce 30-millisecond audio fades at every cut, lock loudness to `-14 LUFS`, and never touch my untouched files in `raw/`.

**[VISUAL: Quick cut back to A-Roll.]**

The AI makes editorial decisions. Deterministic code does the math. That split turns a toy demo into a studio you can ship with every week.

### `[SHORT #2 END — ~48s | Pause 1.5s silently]`

**[YT BRIDGE — trim for Short]**
Let's open up the repo so you can see how the whole workspace is organized — and how I made every single skill work in both Claude Code and Gemini without duplicating a single file.

---

## PART 3 — The Workspace Architecture (`1:45–3:05`)

**[VISUAL: Screen capture of repo root in editor/terminal: `CLAUDE.md`, `GEMINI.md`, `brand/brand.md`, `tools/`, `projects/`, `research/`.]**

**CODY (YouTube Setup — 25s):**
Every video starts with one shell command: `tools/new_project.sh`. That scaffolds a dated folder under `projects/` with `raw/`, `assets/`, `edit/`, `thumbnails/`, `exports/`, and a `brief.md`.

Rule number one in this repo is that `raw/` is strictly read-only — no agent is ever allowed to overwrite or delete source footage. And right next to it sits `brand/brand.md`, which stores my voice rules, bundled open-source fonts like Anton and Archivo Black, accent colors, and channel handles so I never have to re-explain my style in a prompt.

*(Pause 1.5s silently before starting Short #3)*

> **SHORT #3 METADATA**
> - **Clip ID:** `s03-shared-claude-gemini-skills`
> - **Frame-1 On-Screen Text:** `WRITE ONCE. RUN IN BOTH.`
> - **TikTok Search Keywords:** `claude code skills gemini cli shared setup symlink`
> - **IG Reels Save Angle:** Put the exact 1-line `ln -s` symlink command in the caption so devs save it.

### `[SHORT #3 START]`

**[VISUAL: Zoomed terminal showing `ls -la .agents/skills` and `ls -la .claude/skills` with the symlinks pointing straight back to `../../.agents/skills/...`.]**

**CODY:**
If you switch between Claude Code and Gemini like I do, stop maintaining two separate folders of prompts and skills.

Here's the cleanest workspace trick I've built all year. I keep every canonical skill inside `.agents/skills/` — things like `short-form-editor`, `medium-form-editor`, `clip-repurposer`, `thumbnail-designer`, `captions-subtitles`, and `post-copywriter`.

**[VISUAL: Highlight `CLAUDE.md` and `GEMINI.md` side by side, plus the symlink arrow `.claude/skills/<name> -> ../../.agents/skills/<name>`.]**

Gemini discovers `.agents/skills/` natively. Then I just symlink every folder into `.claude/skills/` so Claude Code picks up the exact same `SKILL.md` files and bundled scripts automatically.

That means I write a workflow once, fix a bug once, and whether I'm using Claude Code for heavy refactoring or Gemini for multimodal video and image analysis, both agents follow the exact same production rules.

### `[SHORT #3 END — ~42s | Pause 1.5s silently]`

**[YT BRIDGE — trim for Short]**
Now, before I even turn the camera on for a video like this one, I actually use one of those shared skills to decide *what* to film in the first place.

---

## PART 4 — Before You Hit Record: The 273× Outlier Research Agent (`3:05–4:30`)

> **SHORT #4 METADATA**
> - **Clip ID:** `s04-273x-outlier-agent`
> - **Frame-1 On-Screen Text:** `6.8K SUBS → 1.9M VIEWS (273×)`
> - **TikTok Search Keywords:** `youtube outlier finder ai agent claude code skill`
> - **IG Reels Save Angle:** Display the Outlier formula (`Outlier Ratio = Views ÷ Subscribers`) cleanly inside the 3:4 center crop.

### `[SHORT #4 START]`

**[VISUAL: Screen capture running `.venv/bin/python .agents/skills/video-trend-research/scripts/fetch_trends.py "Software development with AI agents" --days 30` — fast-forward 3× into the ranked Markdown table popping up on screen.]**

**CODY:**
Raw view counts on YouTube lie. A 3-million-subscriber channel getting 100K views is actually underperforming — whereas a 6,800-subscriber channel pulling 1.9 million views in two weeks is a **273x outlier**.

**[VISUAL: Zoom tight onto row #1 (`6.8K subs | 1.9M views | 273.0x`) and rows #9–11 showing three separate `Claude Code + video workflow` videos at 562K, 895K, and 1.4M views.]**

So I built a custom Claude and Gemini skill called `video-trend-research`. I give it any topic — like *"Software development with AI agents"* — and a Python script pulls recent YouTube long-form and Shorts results, enriches channel subscriber counts, and ranks them by **Outlier Ratio** and **Views per Day**, then pairs that with TikTok and Instagram Reels trend searches.

In 20 seconds, it showed me that three separate videos about automating video creation with Claude Code had crossed half a million to 1.4 million views in the last three weeks — almost all of them faceless AI slop.

**[VISUAL: Cut to the generated `research/2026-11-24-software-development-with-ai-agents.md` showing Concept L1: *"I Built an AI Video Editor in Claude Code"*.]**

It literally wrote the brief and hook for the exact video you're watching right now.

### `[SHORT #4 END — ~50s | Pause 1.5s silently]`

**[YT BRIDGE — trim for Short]**
With the brief locked in and raw footage dropped into `raw/`, let's walk through what happens in the terminal when I actually edit a video from scratch.

---

## PART 5 — Live Edit, Stage 1: Local Transcription, Planning & Word-Boundary Cuts (`4:30–6:50`)

**[VISUAL: Screen capture running `probe.py` on `raw/*.mp4`, printing clean resolution, fps, codec, HDR, and loudness lines.]**

**CODY (Stage 1A — Probe & Plan First):**
Step one is always `tools/probe.py`. Before cutting a single frame, the agent audits resolution, frame rate, rotation metadata, color space, and audio loudness. That prevents classic FFmpeg disasters like variable-frame-rate drift or washed-out HDR-to-SDR exports.

*(Pause 1.5s silently if you want to pull the optional local-transcription clip below as a bonus Short)*

### `[OPTIONAL BONUS SHORT — Local Free Transcription (~38s)]`

**[VISUAL: Terminal running `.venv/bin/python tools/transcribe_local.py projects/.../raw/take01.mp4 --edit-dir projects/.../edit` — progress bar flying on Apple Silicon GPU, outputting JSON with exact word timestamps.]**

**CODY:**
You don't need to pay per-minute API fees just to transcribe your footage for AI editing.

Inside my terminal editor, `transcribe_local.py` runs `mlx-whisper` directly on my Mac's Apple Silicon GPU — completely free, completely offline. And here's the clever part: it outputs exact word-level start and end timestamps in the same JSON schema that ElevenLabs Scribe uses.

That means every downstream editing tool — packing multi-take transcripts, removing filler words, cutting on exact word boundaries, and generating animated captions — works out of the box with zero cloud latency and zero per-minute cost.

### `[END OPTIONAL BONUS SHORT | Pause 1.5s silently]`

**[VISUAL: Screen capture showing the agent presenting a plain-English Edit Plan (Hook → Chapters → Cuts → Target Runtime) BEFORE running any render command.]**

**CODY (Stage 1B — Plan First, Word-Boundary Cuts & 30ms Fades):**
Now here's one of the most important rules baked into `CLAUDE.md` and `GEMINI.md`: **Plan first, cut second.**

The agent reads the packed transcript, spots my retakes and dead air, and hands me a plain-English edit plan — which takes it's keeping, the exact hook, the structure, and the target runtime. Nothing renders until I approve the plan.

Once I say go, either `tools/jumpcut.py` (for fast talking-head cuts) or our EDL renderer builds the cut. And every single cut follows two strict audio rules:
1. Cuts only happen on **exact word boundaries** with 60 to 150 milliseconds of breathing padding so words never get clipped.
2. Every splice gets a **30-millisecond audio fade** (`afade`), so you never hear those harsh digital clicks and pops between jump cuts.

**[VISUAL: Quick audio waveform / clip playback showing a clean before/after jump-cut transition with zero pops.]**

And if I need animated diagrams, callouts, or code highlight cards — like the diagram you saw two minutes ago — the agent spins up a React composition using our Remotion skills and renders it cleanly right onto the timeline.

---

## PART 6 — Live Edit, Stage 2: 1 Long Video → 7 Captioned Shorts, Reframing & Loudness (`6:50–8:45`)

> **SHORT #5 METADATA**
> - **Clip ID:** `s05-one-video-into-seven-shorts`
> - **Frame-1 On-Screen Text:** `1 VIDEO → 7 SHORTS (TERMINAL)`
> - **TikTok Search Keywords:** `repurpose youtube video into shorts ai ffmpeg python`
> - **IG Reels Save Angle:** Show the exact 4-script chain (`cut_clips.py → reframe.py → captions.py → export.py`) cleanly on screen.

### `[SHORT #5 START]`

**[VISUAL: Screen capture showing `clips.json` being fed into `tools/cut_clips.py`, spawning 7 individual vertical MP4s inside `clips/`.]**

**CODY:**
Every 12-minute YouTube video I script is built in modular blocks so one terminal pipeline turns it into 7 standalone Shorts automatically.

Here are the four Python scripts Claude Code runs after the main edit:

**[VISUAL: Rapid 4-beat visual sequence showing each script's output on screen:]**
1. `cut_clips.py` reads the transcript, finds exact word-boundary timestamps for each hook, and slices every clip with 30-millisecond audio fades.
2. `reframe.py` crops 16:9 to 9:16 using OpenCV face detection — or switches to blur-pad mode for screen recordings.
3. **Captions always go on LAST.** We transcribe the *final* cut and run `captions.py` to burn active-word subtitles inside the vertical safe zone, clear of TikTok and Reels UI, so timing never drifts.
4. `export.py` runs 2-pass `-14 LUFS` loudness normalization for Shorts, Reels, TikTok, and LinkedIn in one shot.

**[VISUAL: Cut back to A-Roll.]**

One shoot. One main video. Seven ready-to-post Shorts — zero timeline dragging.

### `[SHORT #5 END — ~50s | Pause 1.5s silently]`

**[YT BRIDGE — trim for Short]**
Of course, none of that matters if nobody clicks the video in the first place — and thumbnails are where most AI workflows completely fall apart. Here's how I fixed that.

---

## PART 7 — AI Thumbnails That Actually Pass the 168×94 Mobile Test (`8:45–10:15`)

> **SHORT #6 METADATA**
> - **Clip ID:** `s06-168x94-thumbnail-audit`
> - **Frame-1 On-Screen Text:** `THE 168×94 THUMBNAIL TEST`
> - **TikTok Search Keywords:** `youtube thumbnail workflow ai gemini python`
> - **IG Reels Save Angle:** Show the actual `thumbnail.py preview` contact sheet with the tiny 168×94 dark/light comparison + green 3:4 IG grid crop box!

### `[SHORT #6 START]`

**[VISUAL: Screen capture of `tools/frames.py` contact sheet (12 numbered frames ranked by sharpness, exposure, and face presence).]**

**CODY:**
Most AI thumbnails flop for two reasons: people let image models garble the text, and nobody checks how it looks at **168 by 94 pixels** — the tiny size viewers actually see on YouTube mobile.

Here's my 3-step terminal thumbnail pipeline:

**[VISUAL: Beat 1 — `frames.py` contact sheet → Beat 2 — `gemini-api image` dark-studio relight with ZERO text → Beat 3 — `thumbnail.py compose` stamping crisp `Anton` font + `#FFD400` accent.]**

First, `frames.py` scores my real footage for sharpness, exposure, and face clarity so I pick an expressive frame — never mid-blink.

Second, Gemini's image model cleans or relights the background — with one hard rule: **zero AI-generated text.** Typography always runs through `thumbnail.py compose` with real fonts, 2 to 4 bold words max.

**[VISUAL: Show `thumbnail.py preview` output sheet: 168×94 dark/light mockups + green 3:4 Instagram grid safe box.]**

Third, `thumbnail.py preview` renders a 168-by-94 dark and light legibility sheet — plus the Instagram 3:4 grid crop — and the agent visually inspects it before handing it off. If it isn't readable in half a second, it iterates.

### `[SHORT #6 END — ~50s | Pause 1.5s silently]`

**[YT BRIDGE — trim for Short]**
After that, the `post-copywriter` skill reads the final transcript, chapter timestamps, and thumbnail text to draft copy-paste titles, SEO descriptions, chapters, and platform captions in `post_copy.md` — with an explicit ban list against generic AI phrases like *"dive deep"* or *"game-changer"*.

Now, before you think this replaces video editors overnight, let me give you the honest reality check.

---

## PART 8 — Honest Reality Check: What Still Breaks & Where Humans Win (`10:15–12:15`)

> **SHORT #7 METADATA**
> - **Clip ID:** `s07-what-ai-editors-cant-replace`
> - **Frame-1 On-Screen Text:** `WHAT AI EDITING STILL BREAKS`
> - **TikTok Search Keywords:** `ai video editing honest review claude code reality check`
> - **IG Reels Save Angle:** Straight-talk builder takeaway people share with creative/dev friends.

### `[SHORT #7 START]`

**[VISUAL: A-Roll, slightly tighter crop, conversational and grounded.]**

**CODY:**
After editing real footage with Claude Code and Gemini, here's the honest truth nobody puts in their viral "AI replaced everything" demos: **AI agents still can't replace editorial taste.**

They're incredible at the mechanical 80% — transcribing, finding outliers, slicing silences on exact word boundaries, reframing 16:9 to 9:16, syncing captions, normalizing loudness, and testing thumbnails at mobile size.

**[VISUAL: Quick B-roll/screen flashes of a real `project.md` edit log / tweaking an EDL cut or swapping a B-roll moment manually.]**

Where they still need a human in the loop is pacing nuance: knowing when a half-second awkward pause is actually funnier *kept in*, choosing the exact B-roll shot that lands an emotional beat, or deciding which part of a story to cut even though the transcript looks fine on paper.

That's why the real win isn't "100% hands-off autopilot." The real win is collapsing 4 hours of repetitive timeline prep down to 20 minutes — so all your energy goes into shooting better footage and telling better stories.

### `[SHORT #7 END — ~45s | Pause 1.5s silently]`

**[YT OUTRO — 30s, YouTube only]**
**[VISUAL: Screen flash of GitHub repo / folder tree + final side-by-side of the 7 exported Shorts generated from this video.]**

**CODY:**
Every single part of this video — the research report, the project brief, the local transcript, the cuts, the thumbnail audit, and the 7 Shorts spun out of these exact chapters — came out of this one workspace.

If you want to steal the structure, build your own skills, or see the scripts I used, I've linked the resources and breakdown down in the description.

Drop a comment telling me which part of your own editing or coding workflow you'd hand off to an agent first — and subscribe if you want more practical AI builds and real creator workflows without the hype. I'll see you in the next one.

---

## Post-Production Checklist (For When Footage Lands in `raw/`)

1. Drop raw A-roll + screen recordings into `projects/2026-11-24-ai-video-editor-claude-code/raw/`.
2. Run `tools/probe.py` and `tools/transcribe_local.py` (free offline Apple Silicon GPU).
3. Assemble the 16:9 YouTube master using `medium-form-editor` + `video-use` (plan first, cut second, 120–150ms pad, 30ms `afade`).
4. Run `clip-repurposer` (`tools/cut_clips.py`) using the 7 `[SHORT #N]` timestamps from the final transcript (trimming out `[YT BRIDGE]` lines), then `reframe.py --mode face` (A-roll) / `--mode blurpad` (screen captures), `captions.py` (burned LAST), and `export.py --platform all-vertical`.
5. Run `thumbnail-designer` (`frames.py` → optional `gemini-api image` → `thumbnail.py compose` → `thumbnail.py preview` 168×94 audit).
6. Run `post-copywriter` to generate `post_copy.md` for YouTube, Shorts, Instagram Reels, TikTok, and LinkedIn.
