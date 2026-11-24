---
name: thumbnail-designer
description: >-
  End-to-end workflow for designing high-CTR YouTube thumbnails (1280x720),
  vertical 9:16 covers for Shorts/Reels/TikTok (respecting the 3:4 Instagram
  grid crop), 4:5 Instagram feed covers, and LinkedIn video thumbnails. Uses
  tools/frames.py for candidate extraction, Gemini image generation/editing
  (gemini-api image or google-genai) for backgrounds and enhancements,
  tools/thumbnail.py compose for crisp typography and subject cutouts, and
  tools/thumbnail.py preview for mandatory small-size legibility audits. Use
  whenever creating thumbnails, covers, or visual hooks for a video post.
---

# Thumbnail & cover designer

Thumbnails are not posters — viewers see them at **168×94 px** on mobile
sidebars and **360×202 px** in feeds, for less than 0.5 seconds. Clarity and
curiosity beat polish every time.

## 1. Design principles (non-negotiable)

- **One focal point, max 3 visual elements** (e.g., face/subject + one visual
  object/screenshot + 2–4 bold words). Clutter kills CTR.
- **Title + thumbnail complement, never repeat.** If the YouTube title says *"I
  Built an AI Video Editor in 48 Hours"*, the thumbnail text says *"ZERO
  TIMELINE"* or *"10× FASTER"* — never the exact same sentence.
- **Text cap:** 0–4 words ideal, hard max 5 words. Huge, high-contrast display
  type (`Anton`, `Archivo Black`, `Bebas Neue`, `Montserrat` Black).
- **Avoid dead zones:**
  - YouTube 16:9: leave the **bottom-right corner** clear for the duration badge.
  - Vertical 9:16 covers (Reels/TikTok/Shorts): place the subject and title
    inside the **center 3:4 crop** (1080×1440) so the Instagram profile grid
    looks intentional, and above `y = 0.72` to clear feed UI.
- **File limit:** YouTube enforces **< 2 MB** (`tools/thumbnail.py` auto-caps
  JPGs under 1.9 MB).
- **Always pitch 2–3 distinct concepts** (different emotional/curiosity angles,
  not minor color variations) so the user can pick or run YouTube's built-in
  Thumbnail Test & Compare.

## 2. Step-by-step workflow

### Step A — Extract real candidate frames from the video

```bash
.venv/bin/python tools/frames.py <video.mp4> --out-dir projects/<p>/thumbnails/frames --samples 90 --top 12
```

Inspect `projects/<p>/thumbnails/frames/contact_sheet.jpg` visually. Look for:
- Expressive face with sharp eyes (not mid-blink or mid-syllable mouth)
- Clean separation from background
- Hero moments (completed AI UI, sharp camera shot, peak athletic movement)

If a better moment exists at a known timestamp, pull it directly:
`tools/frames.py <video.mp4> --out-dir ... --at 14.2 14.5 14.8`

### Step B — Choose the visual build path

Pick whichever path fits the concept (or combine them):

1. **Real frame + typography (`tools/thumbnail.py compose`)** — fastest and most
   authentic for photography, videography, fitness, and studio talking heads.
   ```bash
   .venv/bin/python tools/thumbnail.py compose \
     --bg projects/<p>/thumbnails/frames/frame_01_14.20s.jpg \
     --size youtube \
     --text "ZERO|*TIMELINE*" \
     --font Anton --accent "#FFD400" --align left --scrim 0.6 \
     --out projects/<p>/thumbnails/yt_v1.jpg
   ```
   Syntax: `|` = line break, `*word*` = accent color. Add `--subject cutout.png`
   for a cut-out subject with crisp white rim outline + drop shadow.

2. **AI-generated or AI-enhanced background + crisp real typography** — best for
   AI build concepts, dramatic lighting relights, background cleanup, or
   expanding a tight shot to 16:9.
   - Use **`gemini-api image`** (requires `GEMINI_API_KEY` in `.env` or
     keychain; default model `gemini-nano-banana-2.1`) or the `google-genai`
     Python SDK, or Antigravity's `image-generator` subagent when running inside
     Antigravity:
     ```bash
     # Generate a clean background or relight a real frame (-i attaches the reference frame)
     gemini-api image "Edit this frame: keep the person's exact face and pose on the right third, clean up the cluttered desk into a moody dark studio with subtle cyan rim light, leave clean dark negative space on the left half for bold text, photorealistic, no text" \
       -i projects/<p>/thumbnails/frames/frame_01_14.20s.jpg \
       --aspect-ratio 16:9 --image-size 2K \
       --out projects/<p>/thumbnails/ai_bg_v2.png
     ```
   - **Rule:** Prefer keeping typography in `tools/thumbnail.py compose` (or
     `canvas-design` / Remotion still) instead of letting an image model render
     text, unless you explicitly verify every letter for spelling and kerning.
   - **Rule for photography/videography:** Never AI-alter a sample photo you are
     claiming came straight out of a camera/lens — use the real frame!

3. **Graphic / editorial cover (`canvas-design` or Remotion still)** — great for
   clean typography-led LinkedIn thumbnails, before/after comparison grids, or
   EXIF/architecture diagrams.

### Step C — Niche concept recipes

| Pillar | High-CTR thumbnail patterns |
|---|---|
| **AI builds** | Left: 2–3 bold words + clean simplified UI/terminal glow or node graphic; Right: expressive reaction face. Or dramatic before/after time/cost stat (`4 HRS → 40 SEC`). |
| **Photography** | Split-screen `RAW vs EDIT` or `35mm vs 85mm` with crisp divider line; OR clean hero photo with zero clutter and 2-word hook + subtle focal length badge (`f/1.2`). |
| **Videography** | Color grade wipe (`LOG → GRADE`), lighting diagram BTS vs. final frame, or hero rig shot with dramatic contrast. |
| **Fitness** | Peak-tension action frame (crisp freeze, high contrast), subtle form arrow or green/red `✓ / ✗` cue, minimal 2–3 word callout (`FIX THIS`). |
| **Content creation** | Clean timeline/analytics arrow, gear desk overhead, or `1 VIDEO → 8 CLIPS` visual flow. |

### Step D — Mandatory legibility audit (`preview`)

Always run `preview` on every candidate and **inspect the resulting preview
image visually** before presenting to the user:

```bash
.venv/bin/python tools/thumbnail.py preview projects/<p>/thumbnails/yt_v1.jpg projects/<p>/thumbnails/yt_v2.jpg
```

Check the `_preview.jpg` sheet:
- **168×94 px (bottom-right of sheet):** Can you instantly read the words and
  tell what the subject is in < 1 second, on both dark mode and light mode?
- **Contrast:** Does the text pop cleanly off the background? If not, bump
  `--scrim`, `--stroke`, or move the text to a quieter area.
- **Vertical covers:** Does the green 3:4 grid box frame the subject and title
  cleanly? Are all elements out of the red UI overlap zones?

If anything fails the 168×94 test, iterate before showing the user.
