# CLAUDE.md — Video Editor Project

This workspace is an agent-driven video editing, thumbnail design, and social
publishing studio for **short-form** (YouTube Shorts, Instagram Reels, TikTok,
LinkedIn vertical) and **medium-form** (YouTube 16:9, LinkedIn native) content.

## Creator & Topics

- **Channels:** YouTube (medium-form 16:9 + Shorts 9:16), Instagram (Reels 9:16
  + Feed 4:5), TikTok (9:16), LinkedIn (native 9:16 / 4:5 / 16:9).
- **Content pillars:** Building AI projects, photography, videography, fitness,
  and content creation.
- **Brand defaults:** Always read `brand/brand.md` before cutting, styling
  captions, designing thumbnails, or writing post copy.

## Directory Layout

```text
Video_Editor_Project/
├── CLAUDE.md / GEMINI.md      # Agent instructions (Claude Code & Gemini)
├── brand/
│   ├── brand.md               # Voice, colors, fonts, CTAs, channel handles
│   └── fonts/                 # Bundled OFL display/caption fonts (Anton, Archivo Black, etc.)
├── tools/                     # Deterministic Python & shell media utilities
│   ├── new_project.sh         # Scaffold a new projects/<date>-<slug>/ folder
│   ├── probe.py               # Resolution, fps, codecs, rotation, HDR, LUFS audit
│   ├── transcribe_local.py    # Local Apple-Silicon mlx-whisper -> Scribe-compatible JSON
│   ├── jumpcut.py             # Fast automatic silence + filler removal
│   ├── cut_clips.py           # Multi-range highlight clipper (clips.json -> clips/)
│   ├── reframe.py             # 16:9 -> 9:16 / 4:5 (YuNet face-center, crop, or blurpad)
│   ├── captions.py            # Word-highlighted ASS + clean SRT sidecar generator
│   ├── export.py              # Platform exports with 2-pass -14 LUFS loudness normalization, BT.709 conversion, auto QA
│   ├── frames.py              # Sharpness + exposure + face-ranked frame extractor + contact sheet
│   ├── qa.py                  # Pre-handoff QA gate: specs, loudness, faststart, SRT/ASS, safe zones, thumbnails (exit 1 on FAIL)
│   ├── thumbnail.py           # High-CTR thumbnail compositor + 168x94 / 3:4-grid preview sheet
│   └── hooks/guard_raw.py     # Claude Code PreToolUse hook that blocks writes/deletes in raw/
├── projects/
│   └── <YYYY-MM-DD>-<slug>/
│       ├── brief.md           # Topic, hook, payoff, target platforms
│       ├── raw/               # Untouched source footage (NEVER overwrite or delete)
│       ├── assets/            # B-roll, screen captures, music, SFX, photos
│       ├── edit/              # Transcripts, takes_packed.md, EDL, project.md, intermediates
│       ├── thumbnails/        # Extracted frames, AI backgrounds, final thumbnails + previews
│       ├── exports/           # Platform-ready MP4s and .srt sidecars
│       └── post_copy.md       # Copy-paste titles, descriptions, chapters, captions, hashtags
├── research/                  # Cross-platform trend analyses & video idea briefs
├── .agents/skills/            # Canonical skill store (shared with Gemini)
└── .claude/skills/            # Symlinks to .agents/skills/ for native Claude Code discovery
```

## Installed Skills — Route by Task

Load the matching `SKILL.md` before executing a task:

| Task | Skill(s) to Use |
|---|---|
| Research trending videos & outliers across YouTube, IG Reels & TikTok to plan what to film | `video-trend-research` |
| Edit a vertical short / Reel / TikTok / LinkedIn clip (<= 3 min) | `short-form-editor` (+ `video-use` for multi-take/retakes) |
| Edit a YouTube or LinkedIn medium-form video (3–20 min) | `medium-form-editor` (+ `video-use`) |
| Multi-take conversational edit, EDL, color grade, `timeline_view` QA | `video-use` |
| Carve 3–10 viral shorts out of a longer video | `clip-repurposer` |
| Generate, proofread, style, or burn captions & SRT sidecars | `captions-subtitles` (or `remotion-captions` for custom React motion) |
| Build motion graphics, animated callouts, diagrams, kinetic titles | `remotion-best-practices` (routes to `remotion-create`, `remotion-markup`, `remotion-render`, `remotion-maps`, etc.) |
| Create YouTube thumbnails & vertical/feed covers | `thumbnail-designer` (+ `canvas-design` for editorial graphic layouts) |
| Write YouTube titles, SEO descriptions, chapters, IG/TikTok/LinkedIn copy | `post-copywriter` |
| Check platform resolutions, safe zones, lengths, loudness, char limits | `social-video-specs` |
| Create or refine custom project skills | `skill-creator` |

## Environment & Commands

Always run commands from the repo root using the project virtualenv:

- **Python:** `.venv/bin/python` (managed by `uv`; dependencies in `pyproject.toml`).
- **FFmpeg:** Homebrew `ffmpeg-full` is linked on `PATH` with `libass`, `drawtext`, `loudnorm`, `x264`, and `videotoolbox`.
- **Local transcription (default, free, offline):**
  ```bash
  .venv/bin/python tools/transcribe_local.py <video> --edit-dir projects/<p>/edit --language en
  ```
  Outputs ElevenLabs-Scribe-shaped JSON to `<edit_dir>/transcripts/<stem>.json`, so every `video-use` helper (`pack_transcripts.py`, `timeline_view.py`, `render.py`) works out of the box without requiring an ElevenLabs key. If `ELEVENLABS_API_KEY` is set in `.env` and multi-speaker diarization is needed, use `.agents/skills/video-use/helpers/transcribe.py`.
- **AI image / thumbnail generation:** `gemini-api` CLI (`~/.local/bin/gemini-api`) and the `google-genai` Python SDK are installed. Set `GEMINI_API_KEY` in `.env` (copied from `.env.example`) to enable AI thumbnail backgrounds/relighting via `gemini-api image`.

## Non-Negotiable Production Rules

1. **Plan first, cut second:** Probe footage, transcribe, pack transcripts, and present a plain-English edit plan (hook, structure, cuts, target length, caption style) for user confirmation before rendering cuts.
2. **Never touch `raw/`:** Source footage is read-only. All working artifacts go in `projects/<p>/edit/`, finals in `exports/`, covers in `thumbnails/`, copy in `post_copy.md`. Enforced: `.claude/settings.json` denies file edits under `projects/*/raw/` and runs `tools/hooks/guard_raw.py` on every Bash command (blocks rm/mv/overwrite/`git clean -X`, asks before copying new footage in), and every `tools/*.py` refuses raw/ output paths.
3. **Word-boundary cuts + padding + fades:** Never slice mid-word. Pad cut edges (60–100 ms for shorts, 120–200 ms for medium-form) and apply 30 ms audio fades (`afade`) at every segment splice so cuts never pop.
4. **Captions go on LAST:** Always burn subtitles after every cutaway, zoom, grade, and overlay — and transcribe the final assembled cut (or compute exact EDL output offsets) so timing never drifts. Always proofread AI/camera/fitness jargon in `.ass` / `.srt` before burning.
5. **Respect safe zones:** Keep vertical 9:16 captions centered around `y = 0.62–0.68`, clear of bottom UI (480 px) and right action rail (140 px). Keep YouTube thumbnail text out of the bottom-right timestamp corner, and vertical cover text inside the center 3:4 Instagram grid crop.
6. **Loudness & codec spec:** Deliver exports through `tools/export.py` (-14 LUFS integrated, -1 dBTP, H.264 High `yuv420p` BT.709, AAC 320k 48 kHz, `+faststart`).
7. **Visual self-eval before handing off:** Always inspect extracted frames (`tools/frames.py` or `video-use/helpers/timeline_view.py`) and thumbnail preview sheets (`tools/thumbnail.py preview`) using the `Read` tool to verify legibility at 168×94, caption alignment, font rendering, and framing before presenting results.
   **QA gate:** before presenting any deliverable, run `.venv/bin/python tools/qa.py projects/<p>` (add caption `.ass` paths to check safe zones). It must exit 0. Fix every FAIL; mention any WARN to the user.
8. **Parallelize independent work:** Use the `Agent` tool to run independent Remotion animation slots, multi-clip renders, or thumbnail variations in parallel rather than sequentially.
9. **Persist session memory:** Append decisions, cut rationales, and open items to `projects/<p>/edit/project.md` at the end of every editing session.
10. **Git hygiene:** Never run `git add`, `git commit`, `git push`, or `git pull` unless the user explicitly asks. Large video binaries are ignored in `.gitignore`.
