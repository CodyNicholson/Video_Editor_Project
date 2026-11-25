# Video Trend Research: Software Development with AI Agents

- **Date:** 2026-11-24
- **Recency Window:** Last 30 days
- **Platforms Analyzed:** YouTube (Long-Form & Shorts), TikTok, Instagram Reels
- **Data Sources:** YouTube public search + watch-page enrichment (`fetch_trends.py`, 99 Long-Form + 17 Shorts collected across 3 query variants: `"Software development with AI agents"`, `"AI coding agents workflow"`, `"Claude Code coding agents"`), Google Search Grounding for TikTok & Instagram Reels trend formats and creator angles
- **Raw Dataset:** [2026-11-24-software-development-with-ai-agents.raw.json](file:///Users/codynicholson/workspace/Video_Editor_Project/research/2026-11-24-software-development-with-ai-agents.raw.json)

---

## 1. Executive Summary

- **What's winning right now:** Concrete, proof-first builds using CLI coding agents (especially **Claude Code** — appearing in 35 of 116 titles) are crushing generic AI news. Three sub-angles dominate: **(1) bold tangible builds** (1M–1.9M views even from sub-10K channels), **(2) AI coding agents automating video/creative workflows** (562K–1.36M views across multiple independent creators), and **(3) practical "how to actually engineer with AI" craft breakdowns** (527K–1.64M views).
- **Biggest outlier pattern:** Tiny channels (< 10K subscribers) are hitting **247×–273× their subscriber count** (`1.16M–1.86M` views in 9–14 days) by pointing Claude/AI agents at a single vivid, real-world project (*reverse-engineering a 32-year-old Jeep*, *hacking a smart TV*, *turning spare phones into a wireless GPU*) rather than building another generic SaaS demo.
- **Short-form vs. Long-form split:** On **YouTube 16:9**, the clear sweet spot is **10–17 minutes** (median across 99 top videos: **12m 31s**, median views: **177K**, median velocity: **14.3K views/day**). On **Shorts / TikTok / Instagram Reels**, raw terminal screen recordings showing an agent autonomously editing files, fixing bugs, or running a custom Skill in 30–60 seconds outperform talking-head theory.
- **Best opening for Cody (`brand/brand.md`):** The current "Claude + video creation" wave (1.36M / 895K / 562K views) is packed with faceless AI slop tutorials. Your actual studio setup — building a **real, non-slop AI agent video editor & research workspace** using Claude Code, Gemini, FFmpeg, and Remotion on real footage — hits the single highest-demand intersection right now with zero hype and undeniable proof.

---

## 2. YouTube Performance Breakdown (Last 30 Days)

### A. Long-Form Winners & Outliers (16:9)

| # | Video | Channel | Views | Views/Day | Subs | Outlier | Runtime | Age | Why It Worked |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | [Claude reverse engineered my 32-year-old Jeep. Then it started controlling it.](https://www.youtube.com/watch?v=WPj3aQ-xxpI) | Muhammad Zulali | 1.9M | 128.7K | 6.8K | **273.0×** | 11:42 | 14d | High-stakes physical proof; specific nostalgia + "then it started controlling it" tension |
| 2 | [Everyone's Letting AI Hack Their TVs… So I Tried It](https://www.youtube.com/watch?v=aN-65z6bvKk) | RelfWolf | 1.2M | 121.9K | 4.7K | **247.2×** | 9:35 | 9d | Rides an active social trend with a personal hands-on test in under 10 min |
| 3 | [AI agent builds itself a robot body, does exactly what experts warned](https://www.youtube.com/watch?v=QRVz697rEx0) | InsideAI | 2.9M | 96.4K | 464K | **6.3×** | 15:05 | 30d | Curiosity gap ("does exactly what experts warned") + tangible hardware visual |
| 4 | [Give Me 13 Minutes and I'll Make You Disgustingly Good With Claude](https://www.youtube.com/watch?v=OUbEeJOxjyw) | Duncan Rogoff | 807K | 85.0K | 102K | **7.9×** | 12:31 | 9d | Time-bounded promise ("13 minutes") + high-density practical mastery |
| 5 | [All Code Is Slop (Except Mine) — Lauren Tan, SpaceXSI](https://www.youtube.com/watch?v=O_zcc6Xl12g) | AI Engineer | 1.6M | 156.1K | 1.1M | 1.6× | 17:32 | 10d | Spicy, relatable engineering truth; hits dev fatigue over low-quality AI code |
| 6 | [Rethinking Claude Code Best Practices — Lydia Hallie, Anthropic](https://www.youtube.com/watch?v=vlfCjWuv4es) | AI Engineer | 1.1M | 78.0K | 1.1M | 1.0× | 17:32 | 13d | Official-insider workflow updates; "Rethinking" signals old habits are outdated |
| 7 | [How to Actually Code with AI (ft. Matt Pocock)](https://www.youtube.com/watch?v=mU8WKII1gpk) | NetworkChuck & Matt Pocock | 547K | 121.8K | — | — | 2:02:36 | 4d | "Actually" cuts through hype; real practitioner walkthrough |
| 8 | [33 Life-Changing Ways to Use Claude in 2027](https://www.youtube.com/watch?v=KDyPHt4lW60) | Nick Saraev | 1.6M | 75.1K | — | — | 14:26 | 21d | High-value listicle + forward-looking year framing ("in 2027") |
| 9 | [How to Make Viral Animated Shorts Using Claude (Full Workflow)](https://www.youtube.com/watch?v=OtbLL6OBNE4) | Mr omi | 1.4M | 64.6K | — | — | 11:53 | 21d | Concrete creative outcome + "(Full Workflow)" promises end-to-end utility |
| 10 | [How To Make Faceless YouTube Shorts with Claude (Free Skill/Automation)](https://www.youtube.com/watch?v=n1N_ZIP5x3M) | Nafay 3D | 895K | 42.6K | — | — | 16:47 | 21d | "Free Skill/Automation" giveaway trigger + Claude Code creator crossover |
| 11 | [I Made VIRAL Animation Videos Using Claude Code (FREE Plugin)](https://www.youtube.com/watch?v=3tpaWHaiLQ8) | Grow With Kaz | 562K | 40.2K | — | — | 10:01 | 14d | Proof-first framing ("I Made...") + free plugin/repo value |
| 12 | [Build Your FIRST AI Agent in Claude Code. (11 Minutes).](https://www.youtube.com/watch?v=ge2FmPeVsT8) | Tristen O'Brien | 527K | 37.6K | — | — | 10:55 | 14d | Low-friction beginner entry point with exact runtime in title |
| 13 | [Something Strange Is Happening to Developers Who Work With AI](https://www.youtube.com/watch?v=jlqBR91AiFI) | Alex - a1crew | 353K | 58.9K | — | — | 11:12 | 6d | Curiosity essay tapping developer identity shift |
| 14 | [I Turned My Spare Phones Into a Wireless GPU for AI Agents (It Actually Works)](https://www.youtube.com/watch?v=reOeczuEzOA) | orailnoor | 459K | 32.8K | — | — | 5:40 | 14d | Clever hardware constraint + "(It Actually Works)" proof parenthetical |
| 15 | [Vibe Coding vs. Agentic Coding: Which Should You Use?](https://www.youtube.com/watch?v=h4tHDFCPmQE) | IBM Technology | 85.9K | 57.7K | 1.9M | 0.1× | 8:37 | 1.5d | High immediate search velocity on the "vibe coding vs. agentic" distinction |

**Long-Form Benchmarks (across 99 collected videos):**
- **Median views:** `176.8K` | **Max views:** `2.94M` | **Median velocity:** `14.3K views/day` | **Median runtime:** `12m 31s` (`751s`)
- **Dominant title formulas observed:**
  1. *Tangible Build + Unexpected Twist:* `"Claude [did concrete thing] to my [real object]. Then [twist]."` (`273×` outlier)
  2. *Exact-Time Mastery Promise:* `"Give Me [X] Minutes and I'll Make You [Outcome] With [Tool]"` / `"Build Your FIRST [X] in [Tool]. (11 Minutes)."` (`807K` / `527K`)
  3. *Full Workflow + Free Artifact:* `"How to [Concrete Output] Using Claude Code (Full Workflow / Free Skill)"` (`1.4M` / `895K` / `562K`)
  4. *Anti-Hype Reality Check:* `"All Code Is Slop (Except Mine)"` / `"How to Actually Code with AI"` (`1.6M` / `547K`)

### B. YouTube Shorts Winners (9:16)

| # | Short | Channel | Views | Views/Day | Subs | Outlier | Age | Hook / Angle |
|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | [EdgeMesa N AI+ Series / Compact Desktop for Local AI](https://www.youtube.com/shorts/fRgC2aIhb_g) | MSI Global | 415K | 20.3K | 1.2M | 0.3× | 20d | Tangible local-AI hardware visual in frame 1 |
| 2 | [Remote Agents in Google Antigravity](https://www.youtube.com/shorts/_YIAcXZg9Yk) | Google Antigravity | 140K | 7.2K | 181K | 0.8× | 19d | Crisp 60s product-feature demo showing remote agent orchestration |
| 3 | [Synopsys Autopilot Platform: Autonomous Engineering](https://www.youtube.com/shorts/VLfg-3txAd4) | Synopsys | 71.9K | 3.2K | 33.7K | **2.1×** | 22d | Outperformed channel subs 2.1× via autonomous engineering framing |

*Observation on YouTube Shorts:* Dedicated `#shorts` uploads from independent dev creators on `"Software development with AI agents"` are surprisingly under-served right now — most of the big Shorts views are going to official product demos (Google Antigravity, MSI, Synopsys) while independent creator Shorts with `#shorts` in the title are generic "What is an AI Agent in 60s?" explainers getting < 100 views. **Huge whitespace for punchy, real-demo Shorts!**

---

## 3. TikTok Trends & Winning Formats

- **Data note:** Collected via Google Search Grounding (`search_web`) across TikTok developer trend coverage and creator pattern analyses (exact live TikTok view counts require either `SCRAPECREATORS_API_KEY` or a logged-in browser pass).
- **Top winning TikTok formats right now (November 2026):**
  1. **Raw Terminal / CLI Agent Proof ("Watch It Work"):** Fast-paced screen recordings of Claude Code or Codex CLI reading a real repo, running tests, hitting an error, and fixing it autonomously. High-density visual proof beats talking-head theory.
  2. **60-Second Build Timelapses:** `"Watch an AI agent build [specific useful app/tool] from one spec"` — moving away from vague "vibe coding" toward structured spec/PRD-driven builds (`CLAUDE.md` / `AGENTS.md`).
  3. **Terminal vs. IDE Showdowns:** Quick side-by-side comparisons (Claude Code CLI vs. Cursor vs. Windsurf vs. cloud PR agents) framed around real speed and code-quality tradeoffs.
  4. **Reality Check / Agent Fails:** Relatable, honest clips of agents going off the rails (bad refactors, hallucinated APIs, runaway loops) and the exact guardrail/test loop that fixes it.
  5. **GitHub / MCP / Skill Speedruns:** 30-second rapid breakdowns of a new open-source agent skill, MCP server, or CLI trick viewers immediately bookmark.
- **High-intent TikTok search keywords to front-load in captions & frame-1 text:**
  `claude code workflow`, `ai coding agents`, `agentic coding vs vibe coding`, `custom ai agent skills`, `claude code tips`

---

## 4. Instagram Reels Trends & Winning Formats

- **Data note:** Collected via Google Search Grounding (`search_web`) across Instagram developer content trends (exact live IG play counts require a logged-in browser pass or API integration).
- **Top winning Reels angles & formats right now:**
  1. **Saveable Blueprints & Architecture Walkthroughs:** Reels showing a clean 3-step agent workflow (e.g., `Spec → Skills → Automated Test/Verify`) or exact folder structure (`CLAUDE.md` + `.agents/skills/`) drive high **Saves** and **DM Shares** among engineers.
  2. **Creator-Tech Crossover Demos:** Visually polished desk/monitor shots pairing terminal agents with creative outputs (automated video editing, animation generation, thumbnail pipelines) perform much better on Instagram's aesthetic-driven feed than raw screen-only captures.
  3. **Lead-Magnet / Open-Source Resource CTAs:** Creators sharing a real repo, skill template, or prompt checklist (e.g., `"Save this + grab the skill file on GitHub"`) convert passive viewers into followers and saves.
- **What drives Saves & Shares on IG for this topic:** Clean visual hierarchy (readable dark-mode terminal + clear diagram or before/after output), concrete takeaways people want to try at their desk later, and zero hype.

---

## 5. Cross-Platform Pattern & Gap Analysis

### Winning Sub-Topics (Ranked by Signal)
1. **Claude Code + Custom Skills / Best Practices** — Appears across 35 YouTube titles (including 1.05M, 807K, 527K winners) AND dominates TikTok/Reels CLI workflow content. Viewers know the basics now and want *how skilled builders actually structure projects, skills, and guardrails*.
2. **Real-World / Creative-Pipeline Builds with AI Agents** — Massive outliers (`273×` Jeep, `247×` TV, `1.4M` Claude animation workflow, `895K` Claude shorts automation, `459K` spare-phone GPU). Showing an agent solve a vivid, tangible problem outside CRUD web apps pulls broad audiences.
3. **"Anti-Slop" Agentic Engineering (Beyond Vibe Coding)** — `1.6M` views (*"All Code Is Slop"*), `547K` (*"How to Actually Code with AI"*), `86K in 36h` (*"Vibe Coding vs. Agentic Coding"*), plus strong TikTok debate. Builders are tired of toy demos and want maintainable workflows, testing loops, and honest failure modes.

### Packaging & Hook Mechanics That Are Converting
- **Title formulas:** Specific time/scope (`11 Minutes`, `13 Minutes`), concrete outcome + free artifact (`(Full Workflow)`, `(Free Skill)`), or sharp contrast (`All Code Is Slop`, `Vibe Coding vs. Agentic Coding`, `It Actually Works`).
- **Thumbnail visual patterns:** Clean dark studio + crisp terminal/code or physical/visual result focal point + 2–4 punchy words that *complement* the title instead of repeating it.
- **First 3-second hooks (9:16):** Open on the **end result or live terminal action first**, never a slow setup ("Today I want to talk about...").

### Underserved Gaps (Where Cody Can Stand Out)
- **Gap 1 — Real Creator Workflows vs. Faceless AI Slop:** Three separate YouTube videos on *"making Shorts with Claude Code"* crossed `560K–1.36M` views in the last 3 weeks — and nearly all of them produce generic faceless AI cartoons. Nobody is showing a **real videographer/engineer** using Claude Code + Gemini + FFmpeg + Remotion to edit *real camera footage* without losing human craft. You literally built this studio already.
- **Gap 2 — Independent High-Craft YouTube Shorts / Reels:** Top YouTube Shorts for AI coding agents are mostly corporate promos (MSI, Synopsys, Google) while indie dev Shorts are generic AI-voice explainers getting 20 views. Tightly edited, visually sharp 40-second real-terminal + real-face demos can own this lane immediately.
- **Gap 3 — Cross-Tool Practicality (Claude + Gemini Together):** Most videos treat Claude Code, Gemini, and Cursor as tribal rivalries. Showing a pragmatic builder setup where **the same workspace skills work in both Claude Code and Gemini** (using each model for what it's actually best at — e.g., Claude/Gemini coding + Gemini multimodal video/image analysis + local Whisper) is genuinely fresh and immediately useful.

---

## 6. Recommended Videos to Make Next

> Tailored to [brand.md](file:///Users/codynicholson/workspace/Video_Editor_Project/brand/brand.md): hands-on builder voice, concrete demos, real tradeoffs, zero hype.

### YouTube Medium-Form (16:9) Concepts

#### Concept L1: Build an AI-Agent Video Editing Studio (Claude Code + Gemini + FFmpeg)
- **Slug:** `ai-agent-video-editor-workflow`
- **Pillar:** Building AI Projects × Content Creation
- **Why this will perform:** Directly intersects the two biggest proven winners in the last 30 days — **Claude Code workflows** (`807K–1.05M`) and **video automation with Claude** (`562K–1.36M` across 3 videos) — while solving the #1 viewer complaint (AI slop) by showing real camera footage edited via deterministic Python/FFmpeg tools + skills.
- **Title options (<= 60 chars):**
  1. `I Built an AI Video Editor in Claude Code (Full Workflow)` *(57 chars — direct/searchable)*
  2. `No Timeline: Editing Real Videos With AI Agents` *(47 chars — curiosity/contrast)*
  3. `My Terminal Edits My YouTube Videos Now (Free Skills)` *(53 chars — result + free artifact)*
- **Thumbnail concept:** Text: `"ZERO TIMELINE"` (white + `#FFD400` or `#38BDF8` accent) | Visual: Dark studio split — crisp terminal running a skill on the left, clean graded video frame + word-highlighted captions on the right, expressive reaction face.
- **Cold open hook (0–15s):** Start with a 4-second split-screen: raw rambling clip going into `raw/` → one terminal prompt → cut, reframed, captioned, loudness-normalized export playing back. *"Most 'AI video' tutorials just spit out faceless slop. Over the last week, I built an actual editing studio inside my terminal using Claude Code, Gemini, and Python — and this entire video was edited with it."*
- **Core structure & payoff (~12–14 min — right at the 12.5m median sweet spot):**
  1. `0:00` Cold open proof (before/after clip)
  2. `0:45` Why pure-AI video editors fail (and the secret: **deterministic tools + agent skills**)
  3. `2:30` Architecture tour: `CLAUDE.md` / `GEMINI.md`, `.agents/skills/` shared across Claude & Gemini, `tools/` scripts
  4. `5:00` Live end-to-end demo on real footage (local `mlx-whisper` transcription → EDL plan → word-boundary jump cuts → captions → 168×94 thumbnail audit)
  5. `9:30` The new `video-trend-research` skill finding outlier topics automatically
  6. `11:00` Honest limitations — what agents still get wrong and where a human editor still wins
  7. `12:30` How to steal the setup / GitHub link + CTA
- **Repurpose into Shorts:** (1) The 40s raw-to-edited terminal timelapse, (2) "Why AI coding agents need deterministic Python tools instead of vibes," (3) Showing the `video-trend-research` skill catch a 273× outlier in 20 seconds.

---

#### Concept L2: How to Actually Engineer With AI Agents (Zero-Slop Workflow)
- **Slug:** `agentic-engineering-zero-slop-workflow`
- **Pillar:** Building AI Projects
- **Why this will perform:** Rides the massive velocity around *"All Code Is Slop"* (`1.6M` in 10d), *"Rethinking Claude Code Best Practices"* (`1.05M` in 13d), *"How to Actually Code with AI"* (`547K` in 4d), and *"Vibe Coding vs. Agentic Coding"* (`86K` in 36h) — packaged in the winning ~12-minute tactical breakdown format (`Duncan Rogoff`'s `7.9×` outlier).
- **Title options (<= 60 chars):**
  1. `Stop Vibe Coding: My Real AI Agent Engineering Workflow` *(55 chars — contrast + practical)*
  2. `Give Me 12 Minutes to Fix How You Use AI Coding Agents` *(54 chars — time-bounded mastery)*
  3. `Why Your AI Coding Agent Writes Slop (And the 4 Fixes)` *(54 chars — pain-point + numbered fix)*
- **Thumbnail concept:** Text: `"STOP VIBE CODING"` or `"4 AGENT RULES"` | Visual: Left side messy red diff / broken build (`✗`), right side clean spec + passing tests (`✓`), dark moody background with cyan glow.
- **Cold open hook (0–15s):** *"If your AI coding agent keeps breaking files you didn't ask it to touch, it's not the model — it's how you're setting up the workspace. Here are the exact 4 guardrails I use every day so Claude Code and Gemini actually ship clean code."*
- **Core structure & payoff (~11–13 min):**
  1. `0:00` Hook + showing a real broken "vibe-coded" diff vs. structured agent PR
  2. `1:30` Rule 1: Spec & Context files (`CLAUDE.md` / `GEMINI.md`) that prevent drift
  3. `4:00` Rule 2: Reusable Skills (progressive disclosure so you don't blow context)
  4. `6:30` Rule 3: Deterministic scripts + automated verification loops (make the agent prove its own work)
  5. `9:00` Rule 4: Multi-agent parallelization vs. when a single focused loop is faster
  6. `10:45` Live real-world test + honest tradeoffs / cost check
- **Repurpose into Shorts:** One 45-second Short per rule (instant 4-part short-form series!).

---

#### Concept L3: Wild Real-World Proof Build — "I Built an AI Agent That Scouts Viral Videos & Plans My Channel"
- **Slug:** `ai-agent-viral-video-research-skill`
- **Pillar:** Building AI Projects × Content Creation
- **Why this will perform:** Combines the **247×–273× concrete build storytelling format** (solving one real problem live from scratch) with the **Free Skill** hook (`895K` / `562K`). You literally just built `video-trend-research` — filming the build + live results is fast, authentic, and immediately demos value.
- **Title options (<= 60 chars):**
  1. `I Built an AI Agent to Find Viral Video Outliers (Free)` *(55 chars)*
  2. `Claude + Gemini Found a 273x YouTube Outlier in 20 Sec` *(54 chars — specific metric hook)*
  3. `How to Build a Custom Claude & Gemini Skill in 10 Mins` *(54 chars — searchable tutorial)*
- **Thumbnail concept:** Text: `"273× OUTLIER"` | Visual: Terminal outlier table highlighting `273.0x` in `#FFD400` + subtle YouTube/TikTok/IG icons, clean dark frame.
- **Cold open hook (0–15s):** *"Raw view counts on YouTube lie. A 3-million-sub channel getting 100K views is flopping — a 6,000-sub channel getting 1.8 million views is a 273x outlier. So I built a free Claude and Gemini skill that hunts these automatically in 20 seconds."*
- **Core structure & payoff (~10–11 min):**
  1. `0:00` Hook + live 20-second terminal run showing the real 273× outlier table
  2. `1:30` Why Outlier Ratio + View Velocity beats scrolling YouTube manually
  3. `3:30` How the skill is structured (`SKILL.md` + `fetch_trends.py` + `references/`) and shared via symlink between Claude Code & Gemini
  4. `6:30` Live walk-through of the generated report & video ideas
  5. `8:45` Real limitation (why IG/TikTok block scrapers & the hybrid workaround)
  6. `9:45` Link to grab the skill + CTA

---

### Short-Form Concepts (YouTube Shorts / Instagram Reels / TikTok)

#### Concept S1: One Terminal Prompt Edited This Entire Short
- **Slug:** `terminal-edited-this-short`
- **Best platforms:** YouTube Shorts, TikTok, Instagram Reels
- **Target length:** `35–45s`
- **Frame-1 visual + on-screen text:** Split screen: messy raw clip on top, fast-scrolling terminal below | Text: `NO TIMELINE. ONE PROMPT.`
- **0–3s verbal hook:** *"I didn't open Premiere or DaVinci once to edit the video you're watching right now."*
- **Beat sheet:**
  - `0–3s`: Hook + quick flash of raw unedited take vs. final polished frame
  - `3–25s`: 3 rapid cuts showing the actual commands: local `mlx-whisper` transcript → word-boundary jump cuts → animated captions + `-14 LUFS` export
  - `25–38s`: Honest caveat (*"It doesn't replace creative taste — it kills the 2 hours of tedious prep"*) + CTA
- **Platform tweaks:**
  - **TikTok:** Front-load `claude code video editing workflow` in caption & frame-1 SEO text
  - **Instagram Reels:** Put the 4-tool stack (`mlx-whisper + FFmpeg + Remotion + Claude/Gemini`) in the caption so viewers **Save** it
  - **YouTube Shorts:** Link directly to Concept L1 as the Related Video
- **Why this will perform:** Rides the proven raw-terminal proof trend across TikTok/Reels + the massive `Claude + video editing` demand on YouTube.

#### Concept S2: Stop Using Raw Views — The 273× Outlier Trick
- **Slug:** `youtube-outlier-score-agent`
- **Best platforms:** TikTok, Instagram Reels, YouTube Shorts
- **Target length:** `40–50s`
- **Frame-1 visual + on-screen text:** Zoom on terminal table with `6.8K subs → 1.9M views (273×)` highlighted in yellow | Text: `6.8K SUBS → 1.9M VIEWS`
- **0–3s verbal hook:** *"This 6,000-subscriber channel just pulled 1.9 million views — and an AI agent I built found it in 20 seconds."*
- **Beat sheet:**
  - `0–3s`: Hook + exact metric on screen
  - `3–18s`: Explain why views/subscribers (`Outlier Ratio`) + views/day reveals winning ideas instead of big-channel inertia
  - `18–38s`: Quick demo of running `fetch_trends.py` inside Claude/Gemini and generating the research report
  - `38–48s`: CTA (*"Save this if you make videos — full skill breakdown is up next"*)
- **Platform tweaks:**
  - **TikTok:** Keywords `youtube outlier finder ai agent`
  - **Instagram Reels:** Clean 3:4 centered graphic card of the Outlier formula (`Views ÷ Subs >= 5×`) for saves/shares
- **Why this will perform:** Combines creator growth + AI agent utility; easy repurpose from Concept L3.

#### Concept S3: Vibe Coding vs. Agentic Engineering in 40 Seconds
- **Slug:** `vibe-coding-vs-agentic-40s`
- **Best platforms:** TikTok, Instagram Reels, YouTube Shorts
- **Target length:** `35–45s`
- **Frame-1 visual + on-screen text:** Two side-by-side terminal prompts: `VIBE CODING ❌` vs `AGENTIC WORKFLOW ✅`
- **0–3s verbal hook:** *"There's a huge difference between vibe coding and actually engineering with AI agents — here's why your codebase keeps breaking."*
- **Beat sheet:**
  - `0–3s`: Hook + side-by-side visual
  - `3–20s`: Show what breaks with 1 vague prompt (hallucinated edits, zero tests, drifted architecture)
  - `20–38s`: Show the 3-file fix (`CLAUDE.md` rules + focused `SKILL.md` + automated test/verify command)
  - `38–44s`: Crisp closing takeaway + save CTA
- **Platform tweaks:**
  - **TikTok:** Keywords `vibe coding vs agentic coding claude code`
  - **Instagram Reels:** Caption includes the exact 3-file checklist for saves
- **Why this will perform:** Directly rides the `57.7K/day` IBM surge + viral TikTok/Reels debate on AI code quality.

#### Concept S4: One Skill Folder That Works in BOTH Claude Code and Gemini
- **Slug:** `shared-claude-gemini-skills`
- **Best platforms:** TikTok, Instagram Reels, YouTube Shorts
- **Target length:** `30–40s`
- **Frame-1 visual + on-screen text:** Crisp terminal tree showing `.agents/skills/` symlinked to `.claude/skills/` | Text: `WRITE ONCE. RUN IN BOTH.`
- **0–3s verbal hook:** *"Stop rewriting your prompts twice for Claude Code and Gemini — this one symlink trick shares every skill automatically."*
- **Beat sheet:**
  - `0–3s`: Hook + directory tree visual
  - `3–22s`: Show `.agents/skills/<name>/SKILL.md` + `ln -s` into `.claude/skills/` + running the exact same skill in both
  - `22–35s`: Why it matters (deterministic scripts + consistent guardrails regardless of which model you use that day)
- **Platform tweaks:**
  - **TikTok:** Keywords `claude code skills gemini cli setup`
  - **Instagram Reels:** Exact 2-line terminal command in caption for high save rate
- **Why this will perform:** High utility, ultra-fast to film, practically guaranteed saves from developers using multiple models.

#### Concept S5: Why Pure-AI Coding Agents Fail (And the 1 Pattern That Fixes Them)
- **Slug:** `deterministic-tools-for-ai-agents`
- **Best platforms:** YouTube Shorts, TikTok, Instagram Reels
- **Target length:** `40–50s`
- **Frame-1 visual + on-screen text:** Terminal showing an LLM guessing math/timestamps vs. calling a 100-line Python script | Text: `STOP MAKING LLMS GUESS`
- **0–3s verbal hook:** *"The fastest way to make your AI agents 10 times more reliable is to stop asking the LLM to do everything itself."*
- **Beat sheet:**
  - `0–3s`: Contrarian engineering hook
  - `3–20s`: Concrete example (asking an LLM to eyeball video cuts/metrics vs. handing it a deterministic Python CLI tool)
  - `20–38s`: Rule of thumb: *LLMs decide what to do; Python scripts execute the math/media/API calls*
  - `38–45s`: Quick proof clip + CTA
- **Platform tweaks:**
  - **TikTok:** Keywords `ai agent architecture python tools`
  - **Instagram Reels:** Clean diagram overlay (`LLM = Brain | Scripts = Hands`) for DM shares
- **Why this will perform:** Directly mirrors the "Anti-Slop Engineering" wave (`1.6M` views) in a tight 45s takeaway.

---

## 7. Recommended 2-Week Filming Order

1. **Week 1 Anchor (Highest Signal Overlap):** Film **Concept L1** (*"I Built an AI Video Editor in Claude Code"*) + extract **Concept S1** (*"No Timeline. One Prompt."*) and **Concept S5** (*"Stop Making LLMs Guess"*) from the same footage.
2. **Week 1 Fast Standalone Short:** Film **Concept S4** (*"One Skill Folder for Both Claude Code & Gemini"*) — 15 minutes to shoot, high save rate, builds audience before L1 drops.
3. **Week 2 Anchor:** Film **Concept L3** (*"I Built an AI Agent to Find 273× YouTube Outliers"*) OR **Concept L2** (*"Stop Vibe Coding: My Real AI Agent Workflow"*) + spin off **Concept S2** and **Concept S3**.

---

## Ready to Start?

Pick any concept above and ask me to scaffold it:
`tools/new_project.sh <slug> <short|medium>` + pre-filled `brief.md`.
