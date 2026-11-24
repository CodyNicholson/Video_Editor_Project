---
name: post-copywriter
description: >-
  Writes platform-native titles, SEO descriptions, YouTube chapters, pinned
  comments, Instagram captions, TikTok searchable captions, LinkedIn posts, and
  targeted hashtags for videos about building AI projects, photography,
  videography, fitness, and content creation. Saves everything into a single
  copy-pasteable post_copy.md file per project. Use whenever writing titles,
  descriptions, captions, hooks, or social copy for a video.
---

# Post copywriter (YouTube, Instagram, TikTok, LinkedIn)

Write copy that sounds like a real builder and creator talking to a smart peer —
specific, concrete, and useful.

## 0. Gather context first

1. Read `brand/brand.md` (voice, bio/links block, gear/stack disclosure, CTA
   preferences).
2. Read the project's `brief.md`, final transcript (`edit/takes_packed.md` or the
   final `.srt`), and `edit/chapters.txt` (if medium-form).
3. Check the chosen thumbnail text so the **title and thumbnail complement each
   other** instead of saying the exact same words.

## 1. Anti-slop voice rules

Never use generic AI filler:
- Ban: *"In today's video, we dive deep into..."*, *"unlock the power of"*,
  *"game-changer"*, *"revolutionize"*, *"level up your..."*, *"let's jump right
  in"*, *"delve"*, *"tapestry"*, or emoji-bullet walls (🚀🔥💡✨).
- Lead with concrete specifics: real numbers, real tools/models/lenses/lifts,
  real mistakes and tradeoffs.
- Keep paragraphs short (1–3 lines) for mobile readability.

## 2. Deliverable format: `projects/<p>/post_copy.md`

Always write the complete copy package into `projects/<p>/post_copy.md` with
clear headings so the user can copy-paste directly into each uploader:

### A. YouTube (Long / Medium-Form)
- **5 Title options** (<= 60 chars preferred so nothing truncates on mobile; hard
  limit 100 chars), covering distinct angles:
  1. Direct / searchable (SEO-first)
  2. Curiosity / tension
  3. Specific result / metric
  4. Contrarian / mistake-framing
  5. Short punchy (< 45 chars)
  Include a 1-line note on how the top pick pairs with the thumbnail text.
- **Description:**
  - **Lines 1–2 (~150 chars, above the fold):** Restate the core value + natural
    primary keywords. No "Hey guys" or bare links on line 1.
  - **What you'll learn / resources & links:** GitHub repos, tools, prompts,
    camera/lens kit, or workout notes mentioned in the video (leave clear
    `[LINK: ...]` placeholders where URLs are needed).
  - **Chapters:** Exact `00:00` timestamps from `edit/chapters.txt` (keyword-rich
    chapter names help YouTube & Google key-moments search).
  - **Standard footer:** Pull from `brand/brand.md`.
  - **Tags / Hashtags:** 3–5 relevant hashtags at the bottom + a comma-separated
    keyword tag line for YouTube Studio.
- **Pinned comment:** One conversational question tied to the video's topic (plus
  the main resource link if relevant) to spark early comments.

### B. YouTube Shorts
- **3 Title options** (< 55 chars, punchy hook, complements frame-1 text).
- **Short description** (2–3 sentences + link to related full YouTube video if
  repurposed + 2–3 hashtags).

### C. Instagram (Reels / Feed)
- **Hook line (first ~115 chars before "...more"):** Must create curiosity or
  promise a takeaway worth saving/sharing.
- **Body:** 3–6 crisp lines — either the key steps/settings/prompt so viewers
  **save** the post, or the behind-the-scenes story that didn't fit in the 30 s
  clip.
- **CTA:** One clear action (save for your next shoot/build/session, comment a
  keyword, or reply with their setup).
- **Hashtags:** 3–5 specific, niche-accurate tags (no 30-tag spam blocks).

### D. TikTok
- **Caption (<= 300 chars ideal, front-load searchable keywords in first 90
  chars):** TikTok functions as a search engine — include the exact phrases
  someone would search (e.g. `claude code video editing workflow`,
  `sony 35mm street photography settings`, `incline dumbbell press form`).
- **On-screen SEO note:** Remind which keyword should appear in the frame-1
  hook text.
- **Hashtags:** 3–5 targeted tags.

### E. LinkedIn
- **Opening 2 lines (~180–210 chars before "see more"):** A sharp observation,
  concrete result, or lesson learned — never clickbait, never corporate fluff.
  Works especially well for **AI builds, creative workflows, photography/video
  craft, discipline/fitness habits, and content systems**.
- **Body:** Short scannable lines (what I built/tested, what broke, what worked,
  1 takeaway the reader can steal today).
- **Closing question:** Invites thoughtful peer replies (not "Agree? 👇").
- **Hashtags:** 3–4 broad professional tags (e.g. `#AI`, `#VideoProduction`,
  `#ContentCreation`, `#SoftwareEngineering`).
- **Note:** Remind user to upload the `.srt` sidecar and put external links in
  the first comment if optimizing for native feed reach.

## 3. Niche keyword banks (use naturally, never stuff)

- **AI projects:** agents, Claude Code, Gemini, local LLM, workflow automation,
  Python, FFmpeg, Remotion, build in public, AI tools
- **Photography:** lighting, composition, color grading, Lightroom, focal length,
  street photography, portrait lighting, RAW edit, camera settings
- **Videography:** color grading, cinematography, camera rig, lighting setup,
  frame rate, sound design, B-roll, editing workflow
- **Fitness:** form cues, progressive overload, hypertrophy, mobility, training
  split, consistency, gym routine
- **Content creation:** retention, hooks, storytelling, YouTube workflow,
  short-form editing, repurposing, creator tools

## 4. Quality check before finishing

- Verify every character count against `social-video-specs`.
- Confirm every timestamp in YouTube chapters starts at `00:00`, increases
  monotonically, and matches the actual video runtime.
- Read every hook line out loud — if it sounds like marketing copy instead of a
  person talking, rewrite it.
