# Report Template: `research/<YYYY-MM-DD>-<topic-slug>.md`

Use this exact structure when saving trend analysis reports so every report is
scannable, grounded in real collected data, and directly actionable for filming
and scaffolding `projects/<YYYY-MM-DD>-<slug>/brief.md`.

```markdown
# Video Trend Research: <Topic>

- **Date:** <YYYY-MM-DD>
- **Recency Window:** Last <N> days
- **Platforms Analyzed:** YouTube (Long-Form & Shorts), TikTok, Instagram Reels
- **Data Sources:** <e.g., YouTube public search + watch enrichment (exact views/subs/dates), Web Search (`site:tiktok.com`, `site:instagram.com/reel`)>
- **Raw Dataset:** `<YYYY-MM-DD>-<topic-slug>.raw.json`

---

## 1. Executive Summary

- **What's winning right now:** <1–2 sentences naming the #1 proven angle with concrete numbers>
- **Biggest outlier pattern:** <What smaller channels are doing to get 3x–10x their sub count>
- **Short-form vs. Long-form split:** <What's working in 16:9 vs. 9:16 right now>
- **Best opening for Cody (`brand/brand.md`):** <Where hands-on builder credibility beats current hype videos>

---

## 2. YouTube Performance Breakdown (Last <N> Days)

### A. Long-Form Winners & Outliers (16:9)

| # | Video | Channel | Views | Views/Day | Subs | Outlier | Runtime | Age | Why It Worked |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | [Title](url) | Channel | 145K | 12.1K | 18K | 8.1× | 14:22 | 12d | <1 crisp line on angle/hook/packaging> |

**Long-Form Benchmarks:**
- Median views: `<X>` | Median velocity: `<Y>/day` | Sweet-spot runtime: `<M–N min>`
- Dominant title formulas: <list top 2–3 observed formulas with real examples>

### B. YouTube Shorts Winners (9:16)

| # | Short | Channel | Views | Views/Day | Subs | Outlier | Age | Hook / Angle |
|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | [Title](url) | Channel | 210K | 30.0K | 42K | 5.0× | 7d | <1 crisp line> |

---

## 3. TikTok Trends & Winning Formats

- **Data:** <N> videos in window via Firecrawl/ScrapeCreators (<date>), median <X> views, median length <Y>s
  <!-- or: "indexed web search only, no exact metrics" when Firecrawl was unavailable -->

| # | Video | Creator (followers) | Views | x foll | Views/Day | Save % | Share % | Age | Hook |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | [Hook text](url) | @creator (20K) | 1.2M | 60× | 56K | 9.0 | 1.5 | 21d | <1 line> |

- **Winning TikTok formats:** <e.g., split-screen terminal proof, 30s workflow, contrarian hot-take>
- **Caption/hook patterns that over-index in the top half:** <from the pattern line, e.g. free_or_hack 6/10>
- **High-intent TikTok search keywords / hashtags:** `<keyword>`, `#<tag>`

---

## 4. Instagram Reels Trends & Winning Formats

- **Data:** <N> reels in window via Firecrawl/ScrapeCreators (<date>). No follower counts, so outliers are **vs. cohort median**

| # | Reel | Creator | Views | x cohort median | Views/Day | Likes | Comments | Age | Hook |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | [Hook text](url) | @creator | 115K | 23× | 14K | 3.9K | 4.4K* | 8d | <1 line> |

<!-- * mark comment counts inflated by comment-bait ("comment X for the guide") -->
- **What drives Saves & Shares on IG for this topic:** <e.g., saveable checklist card, before/after>

---

## 4b. Search Demand & Audience Questions

- **Rising YouTube searches (last <window>):** <query (+450%)>, ... (relative growth, not volume)
- **Top YouTube searches:** <query (100)>, ...
- **Interest over time:** <phrase A rising / phrase B flat>
- **What viewers are asking in the winners' comments** (each one is a video idea):
  1. "<question>" (<likes> likes, on [video](url))
  2. ...

---

## 5. Cross-Platform Pattern & Gap Analysis

### Winning Sub-Topics (Ranked by Signal)
1. **<Sub-topic 1>** — <Evidence across platforms>
2. **<Sub-topic 2>** — <Evidence across platforms>
3. **<Sub-topic 3>** — <Evidence across platforms>

### Packaging & Hook Mechanics That Are Converting
- **Title formulas:** <Concrete templates derived from actual outliers>
- **Thumbnail visual patterns:** <What catches the eye at 168×94>
- **First 3-second hooks (9:16):** <Exact verbal + visual proof openings>

### Underserved Gaps (Where You Can Stand Out)
- **Gap 1:** <What current top videos miss, oversimplify, or hype — and how Cody can nail it honestly>
- **Gap 2:** <...>

---

## 6. Recommended Videos to Make Next

> Tailored to `brand/brand.md` (direct, hands-on builder, practical proof, zero hype).

### YouTube Medium-Form (16:9) Concepts

#### Concept L1: <Working Title>
- **Slug:** `<suggested-project-slug>`
- **Pillar:** `<AI builds | photography | videography | fitness | content creation>`
- **Why this will perform:** <Tie directly to specific outlier data from Sections 2–5>
- **Title options (<= 60 chars):**
  1. `<Option 1 — direct/searchable>`
  2. `<Option 2 — curiosity/tension>`
  3. `<Option 3 — concrete result/metric>`
- **Thumbnail concept:** Text: `"<2–4 WORDS>"` (complements title, doesn't repeat it) | Visual: <concrete focal point>
- **Cold open hook (0–15s):** <Exact spoken hook + what's on screen in second 1>
- **Core structure & payoff (<target runtime>):**
  1. `0:00` Hook + immediate proof of outcome
  2. `...`
- **Repurpose into Shorts:** <List 2–3 standalone vertical moments to cut from this video>

#### Concept L2: <Working Title>
...

---

### Short-Form Concepts (YouTube Shorts / Instagram Reels / TikTok)

#### Concept S1: <Working Concept Name>
- **Slug:** `<suggested-project-slug>`
- **Best platforms:** YouTube Shorts, TikTok, Instagram Reels
- **Target length:** `<30–55s>`
- **Frame-1 visual + on-screen text:** <Exact visual + <= 5 words text>
- **0–3s verbal hook:** `"<Exact opening line>"`
- **Beat sheet:**
  - `0–3s`: Hook + proof
  - `3–25s`: Concrete step/demo
  - `25–45s`: Payoff + honest caveat + CTA
- **Platform tweaks:**
  - **TikTok:** Front-load `<search keyword>` in caption + frame-1 text
  - **Instagram Reels:** Add clean saveable summary card / caption checklist so viewers bookmark it
  - **YouTube Shorts:** Tight loop or curiosity payoff tied to `<Concept L1>`
- **Why this will perform:** <Tie to observed short-form/TikTok/IG trend>

*(Include 4–6 Short-Form concepts total.)*

---

## 7. Recommended 2-Week Filming Order

1. **Week 1 Anchor:** Film `<Concept L1>` (16:9) + pull `<Concept S1>` & `<Concept S2>` from it.
2. **Week 1 Standalone Short:** Film `<Concept S3>` (fast turnaround to ride current trend velocity).
3. **Week 2 Anchor:** Film `<Concept L2>` + pull `<Concept S4>`.

---

## Ready to Start?

Pick any concept above and ask me to scaffold it:
`tools/new_project.sh <slug> <short|medium>` + pre-filled `brief.md`.
```
