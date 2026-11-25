# Platform Collection & Analysis Playbooks

Reference guide for `video-trend-research`. Load this when running Step 2
(TikTok & Instagram Reels discovery) or interpreting metrics.

---

## 1. YouTube (Long-Form 16:9 + Shorts 9:16)

### Automated collection via `scripts/fetch_trends.py`
The script automatically picks the best available source:
1. **YouTube Data API v3** (if `YOUTUBE_API_KEY` is in `.env` — free tier gives
   10,000 units/day; one research run uses ~250 units): returns exact
   `viewCount`, `likeCount`, `commentCount`, `publishedAt`, ISO duration, and
   `subscriberCount` for every video.
2. **Zero-key public YouTube search** (default): queries YouTube with protobuf
   `sp` upload-date + sort filters across three passes (`views`, `relevance`,
   and `#shorts`) and enriches the top candidates via their watch page to grab
   exact publish dates, subscriber counts, and likes.

### How to read YouTube Outlier Ratios
| Outlier Ratio (`views / subs`) | Meaning | Action |
|---|---|---|
| `>= 5.0×` (with >= 10K views) | **Mega Outlier** — packaging + topic pulled massive browse/search traffic outside the channel's base | Reverse-engineer title, thumbnail, angle, and first 15s hook |
| `2.0× – 4.9×` (with >= 5K views) | **Strong Outlier** — clearly resonating right now | High-confidence angle to adapt with a sharper/better execution |
| `0.5× – 1.9×` (with high `views/day`) | **Established Demand** — big channels feeding an active audience | Good topic validation; differentiate via fresher angle or tighter pacing |
| `< 0.3×` | **Channel-carried or saturated** | Avoid copying this exact framing unless there is a major untapped twist |

### Query Expansion Tips
Always pass 2 adjacent `--extra-queries` that reflect how viewers and creators
actually title videos rather than textbook descriptions:
- Broad topic: `"Software development with AI agents"`
- Adjacent creator queries: `"AI coding agents workflow"`, `"Claude Code agents build"`
- For photography: `"street photography night"` -> `"35mm night photography settings"`, `"night street photography POV"`
- For fitness: `"hypertrophy upper body"` -> `"science based upper body workout"`, `"push pull legs mistakes"`

---

## 2. TikTok

TikTok actively blocks anonymous HTTP scrapers, so use a layered approach:

### Layer 0 — Firecrawl MCP (Default when connected)
Use `scripts/social_trends.py` (see SKILL.md Step 2). It gives exact plays,
likes, comments, shares, saves, creator follower counts (TikTok) and post
dates, plus comment mining. The web-search layers below are the fallback.

### Layer A — Targeted Web Search (Fallback, Zero Keys)
Run 3–4 focused searches using `search_web` / `WebSearch`:
1. `site:tiktok.com "<topic>" <year>` — surfaces indexed TikTok videos and
   creator captions that Google ranked highly (strong proxy for engagement).
2. `site:tiktok.com/discover <topic>` — TikTok's own Discover topic clusters
   reveal related search phrases users actively type into TikTok Search.
3. `site:tiktok.com <short keyword variant> workflow OR tutorial OR demo <month year>`
4. `<topic> viral tiktok <year>` — picks up newsletters, blogs, and creator
   threads dissecting trending TikTok formats in that niche.

**What to extract from TikTok signals:**
- Exact search phrases appearing in captions & Discover pages (TikTok is heavily
  search-driven — these become frame-1 on-screen text + caption keywords).
- Repeating visual formats (e.g., split-screen screen-recording + talking head,
  "day in the life", POV desk setup, rapid 3-tool stack, hot-take green screen).
- Hook phrasing patterns (first sentence of the caption / video title).

### Layer B — Live Browser Pass (Optional)
When the user wants live TikTok view/like counts and visual hook inspection:
- Visit `https://www.tiktok.com/search/video?q=<encoded_topic>` or TikTok
  Creative Center (`https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en`).
- **Compliance guardrail:** Never attempt to solve or bypass a CAPTCHA or
  anti-bot challenge. If TikTok serves a verification gate, stop the browser
  pass for TikTok, report that cleanly, and synthesize from Layer A + YouTube
  Shorts proxies.

### Layer C — Optional API Upgrade
If the user adds `SCRAPECREATORS_API_KEY` to `.env`, `fetch_trends.py`
automatically queries ScrapeCreators' TikTok keyword search endpoint and returns
structured play counts, likes, comments, shares, and saves.

---

## 3. Instagram Reels

Instagram requires authentication for most in-app search/Explore views, so use:

### Layer 0 — Firecrawl MCP (Default when connected)
Use `scripts/social_trends.py` (see SKILL.md Step 2). It gives exact plays,
likes, comments, shares, saves, creator follower counts (TikTok) and post
dates, plus comment mining. The web-search layers below are the fallback.

### Layer A — Targeted Web Search (Fallback, Zero Keys)
Run 3 focused searches:
1. `site:instagram.com/reel "<topic>" <year>` — indexed Reels with creator
   handles, hook captions, and often snippet engagement counts.
2. `site:instagram.com/reel <short keyword variant> <month year>`
3. `instagram reels trending <topic> <year>` — surfaces current Reels editing
   styles, audio trends, and "comment X for link" lead-magnet formats.

**What to extract from Instagram Reels signals:**
- **Save & Share triggers:** Reels distribution weights *DM shares* and *saves*
  heavily. Notice which posts give a concrete checklist, prompt, lens recipe, or
  before/after visual that people bookmark or send to a friend.
- **Visual aesthetic:** Reels rewards cleaner framing, stronger color/lighting,
  and intentional 3:4 cover grid alignment compared to raw TikTok screen grabs.
- **Comment-automation / CTA patterns:** Notice whether top creators use
  "comment `<WORD>` for the repo/prompt" or direct save CTAs.

### Layer B — Live Browser Pass (Optional, Logged-In Only)
- Visit `https://www.instagram.com/explore/search/keyword/?q=<encoded_topic>`.
- Only inspect if the browser session is already signed in or the user signs in
  themselves. Never attempt to bypass login walls or CAPTCHAs.

---

## 4. Cross-Platform Synthesis Checklist

When combining YouTube + TikTok + Instagram Reels into recommendations:
- **Never treat all 3 platforms as identical.** A 14-minute YouTube build log
  and a 38-second TikTok/Reel demo win for completely different reasons.
- **Spot the "Hub & Spoke" opportunity:** Identify 1 strong YouTube Long-Form
  build/experiment that naturally spins off 3–4 standalone vertical clips (e.g.,
  the wildest result clip, the 1 tool/trick breakdown, the mistake/gotcha clip)
  for Shorts, Reels, and TikTok via `clip-repurposer`.
- **Check against `brand/brand.md`:** Filter out gimmicky trends (fake drama,
  hype claims like "AI just replaced all devs forever!") and translate winning
  structures into Cody's authentic builder voice (real demos, real tradeoffs,
  actual code/gear/results).
