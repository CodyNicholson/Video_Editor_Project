---
name: video-trend-research
description: >-
  Researches recent high-performing videos across YouTube (Long-Form & Shorts),
  Instagram Reels, and TikTok for any given topic, calculates view velocity and
  channel outlier scores to isolate what is actually winning right now, analyzes
  hook/title/thumbnail/format patterns, and outputs concrete, ready-to-film
  video recommendations tailored to the creator's brand. Use whenever the user
  asks what videos are performing best or getting the most views on a topic,
  wants trend research, competitor/outlier analysis, content ideation, or asks
  "what videos should I make about a topic" across YouTube, Instagram, or TikTok.
---

# Video Trend Research & Content Recommendation Engine

Research what recent videos on a topic are genuinely outperforming across
**YouTube (16:9 + Shorts)**, **Instagram Reels**, and **TikTok**, explain *why*
they are winning, and turn those signals into concrete, ready-to-film video
concepts aligned with `brand/brand.md`.

## Core Philosophy: Signal Over Vanity Views

Raw view counts alone are noisy: a 3M-subscriber channel getting 80K views is
underperforming, whereas a 12K-subscriber channel getting 180K views is a **15×
outlier** — proof that the *topic angle, title, thumbnail, and hook* pulled
viewers from outside the creator's existing audience.

Always prioritize three metrics together:
1. **Outlier Ratio (`views / channel_subscribers`)** — isolates packaging and
   topic pull from channel size. Anything `>= 2×` is strong; `>= 5×` is a mega
   outlier worth studying closely.
2. **View Velocity (`views / age_in_days`)** — measures live momentum inside the
   recency window (default **last 30 days**, unless the user asks for 7d / 90d).
3. **Cross-Platform Convergence** — when the same sub-angle or pain point shows
   up on YouTube *and* TikTok/Instagram Reels, it signals durable audience demand
   rather than a one-platform fluke.

---

## End-to-End Workflow

### Step 0 — Parse Input & Load Brand Context

1. Read `brand/brand.md` so every recommendation fits Cody's actual voice
   (hands-on builder, practical, zero hype, no AI-slop buzzwords) and content
   pillars (AI builds, photography, videography, fitness, content creation).
2. Extract from the user's request:
   - **Topic** (e.g., `"Software development with AI agents"`).
   - **Recency window** (default `30` days; honor explicit overrides like "last
     7 days", "this week", or "last 90 days").
   - **Platform focus** (default all three: YouTube, Instagram Reels, TikTok).
   - **Extra angles** — generate 1–2 tighter adjacent search phrases that
     creators actually put in titles (e.g., for `"Software development with AI
     agents"`, add `"AI coding agents workflow"` and `"Claude Code Codex agents"`).
3. Choose the report path:
   `research/<YYYY-MM-DD>-<topic-slug>.md` (and raw data JSON next to it in
   `research/<YYYY-MM-DD>-<topic-slug>.raw.json` if saving raw output).

---

### Step 1 — Pull Quantitative YouTube Data (`scripts/fetch_trends.py`)

Run the bundled collector script first. It uses YouTube Data API v3
automatically when `YOUTUBE_API_KEY` is in `.env`, and otherwise falls back to
zero-cost public YouTube search (`ytInitialData`) plus watch-page enrichment to
recover exact publish dates, subscriber counts, likes, and outlier ratios.

```bash
.venv/bin/python .agents/skills/video-trend-research/scripts/fetch_trends.py \
  "<topic>" \
  --days 30 \
  --limit 25 \
  --enrich-top 15 \
  --extra-queries "<adjacent query 1>" "<adjacent query 2>" \
  --out-json research/<YYYY-MM-DD>-<topic-slug>.raw.json
```

> **Network note:** Because this script fetches live YouTube search results, if
> you are running in a sandboxed terminal without outbound network access, run
> this command with network access enabled. If `SCRAPECREATORS_API_KEY` is set
> in `.env`, the script will also pull structured TikTok data automatically.

Inspect the output tables and JSON:
- Separate **YouTube Long-Form (16:9)** winners from **YouTube Shorts (9:16)**
  winners.
- Flag the top **Outliers** (high `outlier_ratio`) *and* top **High-Velocity**
  videos (high `views_per_day`) — both tell different parts of the story.

---

### Step 2 — Pull TikTok, Instagram Reels, Search Demand & Comments (`scripts/social_trends.py`)

Real TikTok and Instagram metrics come from the **Firecrawl MCP server**
(`alexandria_library_read`: ScrapeCreators for TikTok/Instagram/YouTube
comments, `firecrawl-trends` for Google/YouTube search demand). No API key is
needed when Firecrawl is connected. The script plans the calls and scores the
results. You make the MCP calls. Costs are ~2 Firecrawl credits per
ScrapeCreators call, and a standard run is ~18–25 credits (the plan prints the
estimate).

```bash
SOCIAL=.agents/skills/video-trend-research/scripts/social_trends.py
OUT=research/<YYYY-MM-DD>-<topic-slug>.social.json
```

1. **Plan the calls.** Use the same topic and adjacent phrases as Step 1:
   ```bash
   .venv/bin/python $SOCIAL plan "<topic>" --extra "<adjacent 1>" "<adjacent 2>" --days 30
   ```
   This prints TikTok search + Instagram Reels search (2 pages) for each phrase,
   YouTube-search related queries for the topic, and an interest-over-time
   comparison of the phrases.
2. **Run each printed batch** with `alexandria_library_read` (`calls` = the
   printed array). Then get the full data to disk in one of three ways:
   - **Saved to a tool-results file** (large responses): pass that file path to ingest.
   - **Retained preview** (the result says `"delivery":"retained"` and shows
     only `head` rows): **do not re-run the provider** (it charges again). Run
     `.venv/bin/python $SOCIAL project <workspaceId>` and send the printed call to
     `alexandria_library_read` (0 credits). It returns only the scored fields.
     Save that whole result with `Write` to `research/<date>-<slug>.social.raw-<n>.json`.
   - **Small inline result:** save it with `Write` the same way.
3. **Ingest + score** (re-runnable; merges into `$OUT`):
   ```bash
   .venv/bin/python $SOCIAL ingest <result files...> --topic "<topic>" --days 30 --out $OUT \
       --md research/<YYYY-MM-DD>-<topic-slug>.social.md
   ```
   This prints ready-to-paste markdown: TikTok and Reels outlier tables
   (views, views/day, **x followers** on TikTok, **x cohort median** on both,
   save % and share % on TikTok), caption hook patterns (including
   `comment_bait`, `link_in_bio` and `part_2_series`), hashtags, and YouTube
   search rising/top queries.
4. **Mine comments of the winners.** Do this by default for the top 2 per platform:
   ```bash
   .venv/bin/python $SOCIAL comments-plan $OUT --youtube-json research/<YYYY-MM-DD>-<topic-slug>.raw.json --top 2
   ```
   Run the printed calls in the printed order, apply the same save/`project`
   rule, then `ingest ... --out $OUT` again. The report gains **Audience
   questions and requests** (real video ideas) and a **Comment-bait check**
   that flags comment counts inflated by "comment X for the guide" prompts.
5. **Fallbacks:** if Firecrawl isn't connected or a call errors, use the
   targeted web searches printed by `fetch_trends.py` (`site:tiktok.com`,
   `site:instagram.com/reel`). Optionally use a live browser pass on the
   `direct_browser_urls`, but **never** bypass a login wall or CAPTCHA. Label
   those findings as indexed/qualitative, not measured.
6. **Optional deep hook audit** (`GEMINI_API_KEY`): for the #1–#2 outliers,
   run `gemini-api analyze` on the opening 15 s or the thumbnail to extract the
   real verbal and visual hook.

**Reading the social numbers:**
- TikTok `x foll` is the true outlier ratio. ≥5× with ≥10K views is a mega outlier.
- Instagram search returns no follower counts. Use `x med` (vs. the median of
  this run's reels) and **say "vs. cohort median"** when citing it.
- Save % and share % are the strongest "useful" and "send to a friend"
  signals for Cody's tutorial/build content. Weight them above likes.
- Discount comment counts on posts flagged `comment_bait` or in the Comment-bait check.
- TikTok's `date_posted` filter isn't enforced upstream. The script drops
  out-of-window videos locally and reports how many.

---

### Step 3 — Synthesize Patterns & Content Gaps

Before writing a single recommendation, look across all collected evidence and
extract concrete patterns (never generic advice):

1. **Winning Sub-Topics & Angles:** Which specific slices of the broad topic
   are outperforming? (e.g., real cost/speed benchmarks, multi-agent setups,
   "I replaced X workflow", live end-to-end builds, honest failure postmortems).
2. **Title & Packaging Formulas:** What exact phrasing, contrast, numbers, or
   curiosity gaps appear in the outlier titles? How do top thumbnails pair with
   titles without repeating the same words?
3. **Format & Length Sweet Spots:** Compare median runtime and views for
   YouTube Long-Form vs. Shorts/Reels/TikTok. Note whether tutorials, build
   logs, rapid demos, or talking-head takes are winning on each platform.
4. **Hook Archetypes (First 3 Seconds):** What visual proof or tension opens
   the winning clips on Shorts/TikTok/Reels vs. YouTube cold opens?
5. **Audience Gaps & Differentiated Edge for Cody:** What are viewers confused
   about, skeptical of, or tired of seeing (e.g., hype demos with toy apps
   instead of real production workflows)? Where does Cody's hands-on builder
   voice (`brand/brand.md`) create an immediate unfair advantage?

**Honesty rule on data quality:** Never fabricate view counts, likes, or URLs.
Cite TikTok/IG numbers from the `social_trends.py` tables. Cite search-demand
numbers as relative (0–100, or % growth), never as absolute search counts.
Every video cited in the report must come from actual collected data in this
session. Clearly label exact metrics (e.g., `142K views · 8.4× outlier`) versus
qualitative/indexed search signals from TikTok or Instagram where exact play
counts weren't exposed.

---

### Step 4 — Write the Report & Actionable Video Recommendations

Read `references/report-template.md` and write the complete analysis to:

`research/<YYYY-MM-DD>-<topic-slug>.md`

Every report must include:
- **Executive Summary** (3–5 crisp bullets on what's hot right now and why).
- **Platform Breakdowns** (YouTube Long-Form Outliers table, YouTube Shorts
  table, TikTok trending angles & formats, Instagram Reels trending angles &
  formats — with real clickable URLs).
- **Cross-Platform Pattern Analysis** (winning sub-topics, title/thumbnail
  formulas, hook patterns, length sweet spots, content gaps).
- **Recommended Videos to Make Next** — tailored to `brand/brand.md` (zero
  clickbait slop, concrete builder angles):
  - **2–3 YouTube Medium-Form (16:9) Concepts:** Working title options (<= 60
    chars), complementary 2–4 word thumbnail text + visual concept, 0–15s cold
    open hook, beat-by-beat outline, target length, why it wins (tied directly
    to specific outlier evidence), and repurposing potential.
  - **4–6 Short-Form Concepts (YouTube Shorts / IG Reels / TikTok):** Frame-1
    visual + on-screen text hook, 3-second verbal hook, 30–60s beat sheet,
    platform-specific tweak (TikTok search keyword vs. IG save/share angle),
    and whether it can be clipped from one of the long-form builds.
- **Suggested 2-Week Production Sequence** (which 1 long-form + 2–3 shorts to
  film first for maximum momentum).

---

### Step 5 — Hand Off & Offer Project Scaffolding

In your final message to the user:
1. Link directly to the saved report (`research/<YYYY-MM-DD>-<topic-slug>.md`).
2. Highlight the top 2–3 breakout insights and your #1 recommended Long-Form
   video + #1 recommended Short-Form video.
3. Offer to immediately scaffold whichever concept(s) the user picks into a
   ready-to-shoot project folder using `tools/new_project.sh <slug> <short|medium>`
   and populate `projects/<YYYY-MM-DD>-<slug>/brief.md` with the hook, payoff,
   CTA, and shot notes from the report.

---

## Bundled Resources

- `scripts/social_trends.py` — TikTok / Instagram Reels / search-demand /
  comment pipeline over the Firecrawl MCP (`plan`, `project`, `ingest`,
  `comments-plan`); scores outliers, velocity, save/share rates, hook patterns,
  comment-bait, and audience questions.
- `scripts/fetch_trends.py` — Deterministic YouTube collector (API v3 or
  zero-key public search + watch-page enrichment), outlier/velocity scorer,
  title pattern analyzer, optional ScrapeCreators hook, and TikTok/IG search
  plan generator.
- `references/platform-playbooks.md` — Platform-specific collection playbooks,
  outlier scoring interpretation, optional API key upgrades, and compliance
  guardrails.
- `references/report-template.md` — Exact Markdown structure for saved reports
  in `research/<YYYY-MM-DD>-<topic-slug>.md`.
