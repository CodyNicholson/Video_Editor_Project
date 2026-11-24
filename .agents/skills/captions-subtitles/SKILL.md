---
name: captions-subtitles
description: >-
  Workflow and craft guide for generating, proofreading, styling, and burning
  word-highlighted ASS captions, Remotion animated captions, and clean SRT
  closed-caption sidecars across YouTube, Shorts, Reels, TikTok, and LinkedIn.
  Use when creating or fixing subtitles, styling kinetic captions, or checking
  caption safe zones and timing sync.
---

# Captions & subtitles

## Hard rules

1. **Transcribe the FINAL rendered cut**, not the raw take — unless you are
   using `video-use`'s EDL offset calculator. Generating captions from the final
   video guarantees zero timeline drift.
2. **Burn captions LAST**, after every B-roll cutaway, zoom, color grade, and
   motion-graphic overlay. Otherwise overlays cover the text.
3. **Always proofread before burning.** Whisper routinely mangles proper nouns,
   AI model names, camera gear, and fitness terms (e.g., "Claude", "Gemini",
   "Remotion", "FFmpeg", "f/1.4", "Sony FX3", "LUT", "RPE", "hypertrophy").
   Because `.ass` and `.srt` are plain text, fix spelling directly in the file
   before running `ffmpeg`.
4. **Keep inside safe zones** (see `social-video-specs`):
   - 9:16 vertical: center around `y = 0.62–0.68` (never below `0.75`, never on
     the right 14% action rail).
   - 16:9 horizontal: `y = 0.84–0.88`, clear of the YouTube scrubber bar.

## Fast path: `tools/captions.py` + ffmpeg `libass`

```bash
# 1. Transcribe the final cut
.venv/bin/python tools/transcribe_local.py edit/cut_9x16.mp4 --edit-dir projects/<p>/edit --language en

# 2. Build styled .ass + plain .srt sidecar
.venv/bin/python tools/captions.py projects/<p>/edit/transcripts/cut_9x16.json \
  --out-dir projects/<p>/edit/captions \
  --res 1080x1920 --style pop --words 3 --upper \
  --font "Archivo Black" --highlight "#FFD400" --y 0.66

# 3. Proofread projects/<p>/edit/captions/cut_9x16.ass and .srt!

# 4. Burn into the video (fontsdir lets libass load bundled brand/fonts/)
ffmpeg -y -i edit/cut_9x16.mp4 \
  -vf "subtitles=projects/<p>/edit/captions/cut_9x16.ass:fontsdir=brand/fonts" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a copy \
  edit/final.mp4
```

### Choosing a style by format and niche

| Use case | Recommended flags | Look |
|---|---|---|
| Shorts / Reels / TikTok (high energy, AI builds, fitness, tips) | `--style pop --words 3 --upper --font "Archivo Black" --highlight "#FFD400"` | Bold punchy uppercase, thick black stroke, active word pops in accent color + 108% scale |
| Photography / videography (cinematic, editorial) | `--style clean --words 4 --font "Instrument Sans" --highlight "#F5C542" --size 66 --y 0.70` | Cleaner sentence case, thin outline + soft shadow, doesn't fight the imagery |
| LinkedIn 16:9 / 4:5 (muted autoplay) | `--style clean --words 6 --font "Inter" --highlight "#FFD400" --y 0.84` | Readable professional captions; also upload the `.srt` |
| Screen recordings / busy backgrounds | `--style boxed --words 4 --font "JetBrains Mono"` or `"Instrument Sans"` | Semi-opaque dark pill behind text so captions never disappear over white UI |

Read `brand/brand.md` first and substitute the user's chosen brand font and
accent hex color if configured.

### Available bundled fonts (`brand/fonts/`)

Strong caption faces already installed locally (pass exact family name to `--font`):
- Bold / punchy: `Archivo Black`, `Anton`, `Bebas Neue`, `Big Shoulders`, `Bricolage Grotesque`, `Outfit`
- Clean / editorial: `Instrument Sans`, `Inter`, `Montserrat`
- Tech / AI / code: `JetBrains Mono`, `Geist Mono`, `IBM Plex Mono`, `DM Mono`

If `libass` silently falls back to Arial/Helvetica, check the exact font family
name with `fc-scan --format '%{family}\n' brand/fonts/<file>.ttf` and confirm
`:fontsdir=brand/fonts` is in the `subtitles=` filter string.

## Custom kinetic captions: Remotion

When the user wants custom spring physics, emoji/icon reactions, dual-line
layouts, or full React/Tailwind styling, switch to the **`remotion-captions`**
skill and feed it the word timestamps from `edit/transcripts/<stem>.json`.

## Verification

Pull 3 frames from the burned video at different speech moments using
`tools/frames.py final.mp4 --out-dir edit/verify --at <t1> <t2> <t3>` and inspect
them visually:
- Correct font rendered (not fallback Arial)?
- Text sits inside safe zone and doesn't cover the speaker's eyes/mouth?
- Active-word highlight matches the spoken word at that timestamp?
- No escaped braces, clipped edges, or typos?
