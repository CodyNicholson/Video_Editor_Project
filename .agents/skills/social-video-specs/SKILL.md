---
name: social-video-specs
description: >-
  Reference for platform delivery specs and format rules for YouTube (long and
  Shorts), Instagram (Reels, feed, covers), TikTok, and LinkedIn video:
  resolutions, aspect ratios, length limits and sweet spots, loudness, safe
  zones for captions and text, thumbnail/cover sizes, caption/description
  character limits. Use whenever choosing an export target, laying out text or
  captions, sizing a thumbnail, or checking a deliverable before posting.
---

# Social video specs (late 2026)

Platforms change limits often. Treat numbers as defaults; if the user reports
a different limit, trust them and update this file.

## Delivery targets

| Target | Frame | Aspect | Length (hard / sweet spot) | Notes |
|---|---|---|---|---|
| YouTube (long/medium) | 1920x1080 (or 3840x2160 master) | 16:9 | — / 8–15 min | Chapters need 00:00 + ≥3 stamps ≥10 s apart |
| YouTube Shorts | 1080x1920 | 9:16 | 3:00 / 20–45 s | Loop-friendly endings boost replays |
| Instagram Reels | 1080x1920 | 9:16 | 3:00 for Reels reach / 7–30 s | Grid shows a 3:4 center crop of the cover |
| Instagram feed video | 1080x1350 | 4:5 | 60 min / under 60 s | 4:5 takes the most feed space |
| TikTok | 1080x1920 | 9:16 | 10:00 upload / 21–60 s (1 min+ for Creator Rewards) | Text overlays read as search keywords |
| LinkedIn | 1080x1920, 1080x1350, 1080x1080, or 1920x1080 | 9:16 / 4:5 / 1:1 / 16:9 | 15:00 / 30–90 s | Most people watch muted, so burned captions are required. Upload SRT too |

`tools/export.py` encodes every export to H.264 High, yuv420p, BT.709, AAC 320k
48 kHz, +faststart, 2 s GOP, and a two-pass loudnorm to **-14 LUFS integrated,
-1 dBTP**. Keep the source frame rate (24/25/30/60). Don't convert 24p to 30p.

## Safe zones (9:16, 1080x1920)

Platform UI covers parts of the frame. Keep captions, faces, and key text out of these areas:

- **Top 210 px**: account name, search, and Live badges.
- **Bottom 480 px**: caption text, music ticker, CTA buttons. TikTok's is the tallest.
- **Right 140 px from y≈750 to y≈1480**: like, comment, and share rail.
- **Safe area for captions**: centered around y ≈ 1150–1300 (60–68% of the height). `tools/captions.py` defaults to 68%.
- A single layout that respects the strictest zone (TikTok) works on Reels and Shorts too.

For 16:9, keep text within 5% of each edge. YouTube puts the timestamp in the bottom-right of thumbnails, so leave that corner empty.

## Thumbnails and covers

| Use | Size | Limits |
|---|---|---|
| YouTube thumbnail | 1280x720 (16:9) | JPG/PNG, **< 2 MB**. People see it at 168x94 to 360x202, so it must read at that size |
| Shorts / Reels / TikTok cover | 1080x1920 | Keep the title in the center 1080x1440 (3:4 grid crop), clear of the bottom UI |
| Instagram feed cover | 1080x1350 | |
| LinkedIn video thumbnail | 1920x1080 or match the video aspect | Under 2 MB recommended |

## Copy limits

| Platform | Title | Description/caption | Hashtags |
|---|---|---|---|
| YouTube | 100 chars (~60 show) | 5000 chars, first ~150 show above the fold | 3–5. The first 3 show above the title |
| YouTube Shorts | 100 chars | same | 2–3, include #shorts only if it helps context |
| Instagram | — | 2200 chars, first ~125 show | 3–5 targeted ones work better than 30 |
| TikTok | — | 4000 chars, ~100 show | 3–5. Searchable keywords in the caption matter more |
| LinkedIn | — | 3000 chars, ~210 show before "see more" | 3–5 broad professional tags |

## Pre-post checklist

- [ ] `tools/probe.py --loudness <export>` shows about -14 LUFS and true peak ≤ -1 dBTP
- [ ] Correct frame size for the target, with no letterboxing unless it's intentional
- [ ] Burned captions sit inside the safe zone and match the audio (spot-check 3 points)
- [ ] The first frame has a hook (text or motion), with no black or fade-in first frame on shorts
- [ ] Thumbnail is readable at 168x94 (`tools/thumbnail.py preview`)
- [ ] SRT sidecar exported for YouTube and LinkedIn upload
