#!/usr/bin/env python3
"""TikTok + Instagram Reels + Google Trends + comment mining for video-trend-research.

The data comes from the Firecrawl MCP server's Alexandria providers
(ScrapeCreators for TikTok/Instagram/YouTube comments, firecrawl-trends for
Google/YouTube search interest). The agent makes the MCP calls; this script
plans them, then parses and scores what comes back, so no API key is needed.

    # 1. print the exact alexandria_library_read `calls` to run (with a credit estimate)
    social_trends.py plan "claude code" --extra "ai coding agents" --days 30

    # 2. run those calls with the alexandria_library_read MCP tool. Big responses are
    #    saved to a tool-results file; pass that path here. If one came back inline,
    #    save it to research/<date>-<slug>.social.raw-N.json first.
    social_trends.py ingest <tool-result files...> --topic "claude code" --days 30 \
        --out research/<date>-<slug>.social.json

    # 3. optional: plan comment pulls for the top outliers (TikTok/IG/YouTube),
    #    run them, then ingest those results into the same --out file
    social_trends.py comments-plan research/<date>-<slug>.social.json \
        --youtube-json research/<date>-<slug>.raw.json --top 3

Ingest merges into --out (re-running adds new items and refreshes stats), then
prints a markdown summary for the report: TikTok/IG outlier + velocity tables,
caption hook patterns, hashtags, Google/YouTube rising searches, and the
audience questions mined from comments. Every number is from the collected data.

Metrics:
    views_per_day   views / age in days (age floored at 0.5 day)
    outlier_ratio   views / creator followers (TikTok only; IG search has no follower count)
    cohort_ratio    views / median views of the same platform's results this run
                    (works on both platforms; say "vs. cohort median" when citing it)
    save_rate, share_rate   % of views (TikTok); strongest "useful / send-to-a-friend" signals
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_trends import STOPWORDS, TITLE_PATTERN_RULES  # noqa: E402

EXTRA_PATTERNS = [
    ("comment_bait", re.compile(r"\bcomment\s+[\"“'‘]?[A-Z]{2,}", re.I)),
    ("link_in_bio", re.compile(r"\blink in (my )?bio\b", re.I)),
    ("part_2_series", re.compile(r"\b(part \d|pt\.? ?\d|follow for)\b", re.I)),
    ("free_or_hack", re.compile(r"\b(free|for free|hack|secret|nobody (knows|tells))\b", re.I)),
    ("news_or_launch", re.compile(r"\b(just (launched|dropped|released|got)|new update|announced|official)\b", re.I)),
]
PATTERNS = TITLE_PATTERN_RULES + EXTRA_PATTERNS
QUESTION_RE = re.compile(r"\?|^(how|what|why|can|does|is|where|which|will|do|any)\b|\b(tutorial|please|link|guide|part 2)\b", re.I)


# --- plan ----------------------------------------------------------------------

def tiktok_window(days: int) -> str:
    return "this-week" if days <= 7 else "this-month" if days <= 31 else "last-3-months" if days <= 93 else "last-6-months"


def ig_window(days: int) -> str:
    return "last-week" if days <= 7 else "last-month" if days <= 31 else "last-year"


def trends_window(days: int) -> str:
    return "now 7-d" if days <= 7 else "today 1-m" if days <= 31 else "today 3-m" if days <= 93 else "today 12-m"


def cmd_plan(a) -> None:
    queries = [a.topic] + a.extra
    calls: list[dict] = []
    for q in queries:
        calls.append({"provider": "scrapecreators", "capability": "tiktok/search-videos",
                      "options": {"query": q, "date_posted": tiktok_window(a.days), "trim": True}})
    for q in queries:
        for page in range(1, a.ig_pages + 1):
            opts = {"query": q, "date_posted": ig_window(a.days)}
            if page > 1:
                opts["page"] = page
            calls.append({"provider": "scrapecreators", "capability": "instagram/search-reels", "options": opts})
    calls.append({"provider": "firecrawl-trends", "capability": "trends/related_queries",
                  "options": {"keyword": a.topic, "property": "youtube", "time": trends_window(a.days)}})
    if len(queries) > 1:
        calls.append({"provider": "firecrawl-trends", "capability": "trends/interest_over_time",
                      "options": {"keywords": queries[:5], "property": "youtube", "time": "today 3-m"}})
    batches = [calls[i:i + 10] for i in range(0, len(calls), 10)]
    sc = sum(c["provider"] == "scrapecreators" for c in calls)
    print(f"# {len(calls)} calls in {len(batches)} alexandria_library_read batch(es); "
          f"~{2 * sc + 3 * (len(calls) - sc)} Firecrawl credits (2 per ScrapeCreators call, cache hits free)\n")
    for i, b in enumerate(batches, 1):
        print(f"## batch {i}: pass this as `calls`")
        print(json.dumps(b, indent=1))


# --- parse -----------------------------------------------------------------------

def load_results(path: Path) -> list[dict]:
    """Return a list of alexandria call results from any of the shapes we may be handed."""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        # some tool-result files wrap JSON in a text envelope: take the outermost object
        d = json.loads(text[text.index("{"): text.rindex("}") + 1])
    if isinstance(d, list) and d and isinstance(d[0], dict) and "type" in d[0] and "text" in d[0]:
        d = json.loads(d[0]["text"])  # MCP content-block list
    if isinstance(d, dict) and isinstance(d.get("data"), dict) and "alexandria" in d["data"]:
        res = d["data"]["alexandria"]
        if d.get("delivery") == "retained" or any("head" in r for r in res if isinstance(r, dict)):
            raise ValueError("this is a retained *preview*, not the full data. Run `social_trends.py project "
                             f"{d.get('workspaceId', '<workspaceId>')}` and pass its call to alexandria_library_read")
        # output of the firecrawl/bash projection: stdout holds the compact results
        if len(res) == 1 and res[0].get("capability") == "bash":
            out = (res[0].get("data") or {}).get("stdout") or "[]"
            return json.loads(out)
        return res
    if isinstance(d, dict) and "alexandria" in d:
        return d["alexandria"]
    if isinstance(d, list):
        return d
    if isinstance(d, dict) and "capability" in d:
        return [d]
    # bare ScrapeCreators response (e.g. from the SCRAPECREATORS_API_KEY path)
    if isinstance(d, dict) and "search_item_list" in d:
        return [{"provider": "scrapecreators", "capability": "tiktok/search-videos", "data": d}]
    if isinstance(d, dict) and "reels" in d:
        return [{"provider": "scrapecreators", "capability": "instagram/search-reels", "data": d}]
    raise ValueError(f"{path}: unrecognised result shape")


def iso_to_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def num(x) -> int | None:
    try:
        return int(x) if x is not None else None
    except (TypeError, ValueError):
        return None


def hashtags(text: str) -> list[str]:
    return [h.lower() for h in re.findall(r"#(\w{2,40})", text or "")]


def hook_line(text: str) -> str:
    t = re.sub(r"#\w+", "", text or "").strip()
    t = re.split(r"(?<=[.!?])\s|\n", t, maxsplit=1)[0].strip()
    return t if len(t) <= 140 else t[:140].rsplit(" ", 1)[0] + "…"


def norm_tiktok(r: dict) -> dict:
    s = r.get("statistics") or {}
    au = r.get("author") or {}
    v = r.get("video") or {}
    dur = v.get("duration")
    dur = dur / 1000 if isinstance(dur, (int, float)) and dur > 1000 else dur
    uid = au.get("unique_id") or ""
    vid = str(r.get("aweme_id") or "")
    ts = r.get("create_time_utc") or (datetime.fromtimestamp(r["create_time"], timezone.utc).isoformat()
                                      if r.get("create_time") else None)
    return dict(platform="tiktok", id=f"tt:{vid}", url=r.get("url") or f"https://www.tiktok.com/@{uid}/video/{vid}",
                creator=uid, followers=num(au.get("follower_count")) or None, caption=r.get("desc") or "",
                views=num(s.get("play_count")), likes=num(s.get("digg_count")), comments=num(s.get("comment_count")),
                shares=num(s.get("share_count")), saves=num(s.get("collect_count")),
                duration_s=round(dur, 1) if dur else None, published=ts,
                is_ad=bool(r.get("is_ad")), is_paid=bool(r.get("is_paid_partnership")))


def norm_instagram(r: dict) -> dict:
    ow = r.get("owner") or {}
    views = num(r.get("video_view_count")) or num(r.get("video_play_count"))
    return dict(platform="instagram", id=f"ig:{r.get('shortcode') or r.get('id')}",
                url=r.get("url") or f"https://www.instagram.com/reel/{r.get('shortcode')}/",
                creator=ow.get("username") or "", followers=num(ow.get("follower_count")),
                caption=r.get("caption") or "", views=views, likes=num(r.get("like_count")),
                comments=num(r.get("comment_count")), shares=None, saves=None,
                duration_s=round(float(r["video_duration"]), 1) if r.get("video_duration") else None,
                published=r.get("taken_at"), is_ad=bool(r.get("is_ad")), is_paid=bool(r.get("is_paid_partnership")))


def comment_rows(cap: str, data: dict) -> tuple[str | None, list[dict]]:
    rows = []
    if cap == "tiktok/video-comments":
        for c in data.get("comments") or []:
            rows.append(dict(text=c.get("text") or "", likes=num(c.get("digg_count")) or 0,
                             replies=num(c.get("reply_comment_total")) or 0))
        url = None
        if data.get("comments"):
            aw = data["comments"][0].get("aweme_id")
            url = f"tt:{aw}" if aw else None
        return url, rows
    if cap == "youtube/video-comments":
        for c in data.get("comments") or []:
            e = c.get("engagement") or {}
            rows.append(dict(text=c.get("content") or "", likes=num(e.get("likes")) or 0, replies=num(e.get("replies")) or 0))
        return None, rows
    if cap == "instagram/post-comments":
        for c in data.get("comments") or []:
            rows.append(dict(text=c.get("text") or "", likes=num(c.get("comment_like_count") or c.get("like_count")) or 0, replies=0))
        return None, rows
    return None, rows


def ingest(paths: list[Path], store: dict) -> dict:
    stats = Counter()
    for p in paths:
        try:
            results = load_results(p)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"skip {p}: {e}", file=sys.stderr)
            continue
        for res in results:
            cap = res.get("capability", "")
            if res.get("error"):
                store["errors"].append({"capability": cap, "error": res["error"]})
                stats["errors"] += 1
                continue
            data = res.get("data") or {}
            if cap == "tiktok/search-videos":
                for r in data.get("search_item_list") or []:
                    it = norm_tiktok(r.get("aweme_info") or r)
                    store["items"][it["id"]] = it
                    stats["tiktok"] += 1
            elif cap == "instagram/search-reels":
                for r in data.get("reels") or []:
                    if r.get("is_video") is False:
                        continue
                    it = norm_instagram(r)
                    store["items"][it["id"]] = it
                    stats["instagram"] += 1
            elif cap == "trends/related_queries":
                store["trends"]["related"][data.get("keyword", "?")] = {
                    "property": data.get("property"), "time": data.get("time"), "status": data.get("data_status"),
                    "top": [(q.get("query"), q.get("value")) for q in data.get("top") or []],
                    "rising": [(q.get("query"), q.get("formatted_value")) for q in data.get("rising") or []]}
                stats["trends"] += 1
            elif cap == "trends/interest_over_time":
                pts = data.get("points") or []
                kws = data.get("keywords") or [k for k in (data.get("averages") or {})] or []
                store["trends"]["interest"] = {"keywords": kws, "property": data.get("property"),
                                               "points": [(pt.get("time"), pt.get("values")) for pt in pts]}
                stats["trends"] += 1
            elif cap.endswith("comments"):
                key, rows = comment_rows(cap, data)
                # results come back in call order: match them to the URLs comments-plan recorded
                pend = store.setdefault("pending_comments", [])
                hit = next((i for i, pc in enumerate(pend) if pc["capability"] == cap), None)
                if hit is not None:
                    key = pend.pop(hit)["url"]
                key = key or f"{cap}#{len(store['comments'])}"
                store["comments"].setdefault(key, [])
                seen = {c["text"] for c in store["comments"][key]}
                store["comments"][key] += [c for c in rows if c["text"] not in seen]
                stats["comments"] += len(rows)
    print(f"ingested: {dict(stats)}", file=sys.stderr)
    return store


# --- score -----------------------------------------------------------------------

def score(store: dict, days: int, now: datetime) -> list[dict]:
    items = list(store["items"].values())
    for it in items:
        dt = iso_to_dt(it.get("published"))
        it["age_days"] = round((now - dt).total_seconds() / 86400, 2) if dt else None
        v = it.get("views")
        it["views_per_day"] = round(v / max(it["age_days"], 0.5), 1) if v is not None and it["age_days"] is not None else None
        f = it.get("followers")
        it["outlier_ratio"] = round(v / max(f, 100), 2) if v is not None and f else None
        eng = sum(x or 0 for x in (it.get("likes"), it.get("comments"), it.get("shares"), it.get("saves")))
        it["engagement_rate"] = round(100 * eng / v, 2) if v else None
        it["save_rate"] = round(100 * it["saves"] / v, 2) if v and it.get("saves") is not None else None
        it["share_rate"] = round(100 * it["shares"] / v, 2) if v and it.get("shares") is not None else None
        it["patterns"] = [n for n, rx in PATTERNS if rx.search(it.get("caption") or "")]
        it["hashtags"] = hashtags(it.get("caption") or "")
        it["hook"] = hook_line(it.get("caption") or "")
        it["in_window"] = it["age_days"] is not None and it["age_days"] <= days
    for plat in ("tiktok", "instagram"):
        group = [i for i in items if i["platform"] == plat and i["in_window"] and i.get("views")]
        med = statistics.median([i["views"] for i in group]) if group else 0
        for it in (i for i in items if i["platform"] == plat):
            it["cohort_ratio"] = round(it["views"] / med, 2) if med and it.get("views") else None
    for it in items:
        v, vel = it.get("views") or 0, it.get("views_per_day") or 0
        ratio = it.get("outlier_ratio") if it.get("outlier_ratio") is not None else it.get("cohort_ratio")
        it["score"] = round(math.log10(vel + 10) * 20 + math.log10(v + 10) * 10
                            + (math.log2(ratio + 1) * 22 if ratio else 0)
                            + min(it.get("save_rate") or 0, 10) * 2 + min(it.get("share_rate") or 0, 5) * 2, 2)
        o = it.get("outlier_ratio")
        if o is not None and o >= 5 and v >= 10_000:
            it["tier"] = "Mega outlier (>=5x followers)"
        elif o is not None and o >= 2 and v >= 5_000:
            it["tier"] = "Strong outlier (>=2x followers)"
        elif (it.get("cohort_ratio") or 0) >= 5 and v >= 10_000:
            it["tier"] = "Cohort breakout (>=5x median)"
        elif vel >= 5_000:
            it["tier"] = "High velocity (>=5k/day)"
        else:
            it["tier"] = "Baseline"
    return sorted(items, key=lambda i: i["score"], reverse=True)


# --- report ------------------------------------------------------------------------

def fmt(n) -> str:
    if n is None:
        return "–"
    n = float(n)
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            return f"{n / div:.1f}{suf}".replace(".0", "")
    return f"{n:.0f}" if n == int(n) else f"{n:.1f}"


def md_cell(s: str, n: int = 70) -> str:
    s = re.sub(r"\s+", " ", s or "").replace("|", "/").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def questions(comments: dict, top: int = 15) -> list[tuple[str, int]]:
    rows = [(c["text"], c["likes"]) for cs in comments.values() for c in cs
            if QUESTION_RE.search(c["text"] or "") and 12 <= len(c["text"]) <= 300]
    return sorted(rows, key=lambda r: r[1], reverse=True)[:top]


def report(items: list[dict], store: dict, topic: str, days: int, top: int) -> str:
    out = [f"## Social trend data: \"{topic}\" (last {days} days)\n",
           "Numbers are as collected via Firecrawl/ScrapeCreators on "
           f"{datetime.now().strftime('%Y-%m-%d')}. `x foll` = views / creator followers; "
           "`x med` = views / median of this platform's results (cohort).\n"]
    for plat, label in (("tiktok", "TikTok"), ("instagram", "Instagram Reels")):
        group = [i for i in items if i["platform"] == plat and i["in_window"]]
        stale = sum(1 for i in items if i["platform"] == plat and not i["in_window"])
        if not group:
            out.append(f"### {label}\n\nNo {label} results inside the window ({stale} older dropped).\n")
            continue
        vs = [i["views"] for i in group if i.get("views")]
        durs = [i["duration_s"] for i in group if i.get("duration_s")]
        out.append(f"### {label}: top {min(top, len(group))} of {len(group)} in window"
                   f" (median {fmt(statistics.median(vs)) if vs else '–'} views, median length "
                   f"{fmt(statistics.median(durs)) if durs else '–'}s; {stale} older results dropped)\n")
        if plat == "tiktok":
            out.append("| # | Views | x foll | x med | Views/day | Save % | Share % | Age d | Len s | Creator (followers) | Hook | Tier |\n"
                       "|---|---|---|---|---|---|---|---|---|---|---|---|")
            for n, i in enumerate(group[:top], 1):
                out.append(f"| {n} | [{fmt(i['views'])}]({i['url']}) | {fmt(i['outlier_ratio'])} | {fmt(i['cohort_ratio'])} | "
                           f"{fmt(i['views_per_day'])} | {fmt(i['save_rate'])} | {fmt(i['share_rate'])} | {fmt(i['age_days'])} | "
                           f"{fmt(i['duration_s'])} | @{i['creator']} ({fmt(i['followers'])}) | {md_cell(i['hook'])} | {i['tier']} |")
        else:
            out.append("| # | Views | x med | Views/day | Likes | Comments | Age d | Len s | Creator | Hook | Tier |\n"
                       "|---|---|---|---|---|---|---|---|---|---|---|")
            for n, i in enumerate(group[:top], 1):
                out.append(f"| {n} | [{fmt(i['views'])}]({i['url']}) | {fmt(i['cohort_ratio'])} | {fmt(i['views_per_day'])} | "
                           f"{fmt(i['likes'])} | {fmt(i['comments'])} | {fmt(i['age_days'])} | {fmt(i['duration_s'])} | "
                           f"@{i['creator']} | {md_cell(i['hook'])} | {i['tier']} |")
        pats = Counter(p for i in group for p in i["patterns"])
        top_half = group[: max(3, len(group) // 2)]
        pats_top = Counter(p for i in top_half for p in i["patterns"])
        tags = Counter(t for i in group for t in i["hashtags"])
        out.append("\n**Caption patterns** (top half / all): " + (", ".join(
            f"{p} {pats_top[p]}/{c}" for p, c in pats.most_common(10)) or "none"))
        out.append("\n**Hashtags:** " + (", ".join(f"#{t} ({c})" for t, c in tags.most_common(12)) or "none"))
        kw = Counter(w for i in top_half for w in set(re.findall(r"[a-z0-9+.-]{3,}", (i["hook"] or "").lower()))
                     if w not in STOPWORDS)
        out.append("\n**Hook keywords in the top half:** " + (", ".join(f"{w} ({c})" for w, c in kw.most_common(12)) or "none") + "\n")
        flagged = [i for i in group[:top] if i.get("is_ad") or i.get("is_paid")]
        if flagged:
            out.append(f"_Note: {len(flagged)} of these are ads / paid partnerships: {', '.join('@' + i['creator'] for i in flagged)}._\n")

    rel = store["trends"].get("related") or {}
    for kw, r in rel.items():
        out.append(f"### Search demand: \"{kw}\" ({r.get('property')} search, {r.get('time')})\n")
        if r.get("status") not in (None, "ok"):
            out.append(f"_{r.get('status')}: too little search volume to report._\n")
        out.append("- **Rising:** " + (", ".join(f"{q} ({v})" for q, v in r["rising"][:12]) or "none"))
        out.append("- **Top:** " + (", ".join(f"{q} ({v})" for q, v in r["top"][:12]) or "none") + "\n")
    io = store["trends"].get("interest")
    if io and io.get("points"):
        kws = io.get("keywords") or []
        pts = [p for p in io["points"] if p[1]]
        if pts:
            half = len(pts) // 2
            out.append(f"### Interest over time ({io.get('property')} search, relative 0-100)\n")
            for k in range(len(pts[0][1])):
                a = statistics.mean(p[1][k] for p in pts[:half] or pts)
                b = statistics.mean(p[1][k] for p in pts[half:] or pts)
                name = kws[k] if k < len(kws) else f"keyword {k + 1}"
                trend = "rising" if b > a * 1.15 else "falling" if b < a * 0.85 else "flat"
                out.append(f"- {name}: {a:.0f} -> {b:.0f} (first vs second half, {trend})")
            out.append("")

    bait = []
    for key, cs in store["comments"].items():
        texts = Counter(re.sub(r"\W+", "", (c["text"] or "").lower()) for c in cs)
        word, n = texts.most_common(1)[0] if texts else ("", 0)
        if cs and word and n / len(cs) >= 0.4 and len(cs) >= 5:
            bait.append(f"{key}: {n}/{len(cs)} sampled comments are just \"{word}\"")
    if bait:
        out.append("### Comment-bait check\n")
        out.append("These comment counts are inflated by \"comment X to get the guide\" prompts. "
                   "Don't read them as engagement:\n")
        out += [f"- {b}" for b in bait]
        out.append("")
    qs = questions(store["comments"])
    if qs:
        out.append("### Audience questions and requests (from comments, by likes)\n")
        for t, likes in qs:
            out.append(f"- ({fmt(likes)} likes) {md_cell(t, 160)}")
        out.append("")
    if store["errors"]:
        out.append("_Collection errors: " + "; ".join(f"{e['capability']}: {str(e['error'])[:80]}" for e in store["errors"][-5:]) + "_\n")
    return "\n".join(out)


# --- commands ----------------------------------------------------------------------

def empty_store(topic: str) -> dict:
    return {"topic": topic, "items": {}, "trends": {"related": {}, "interest": None}, "comments": {}, "errors": []}


def cmd_ingest(a) -> None:
    store = json.loads(a.out.read_text()) if a.out and a.out.exists() else empty_store(a.topic)
    store.setdefault("errors", [])
    ingest(a.files, store)
    items = score(store, a.days, datetime.now(timezone.utc))
    store.update(topic=a.topic or store.get("topic"), days=a.days, collected_at=datetime.now(timezone.utc).isoformat(),
                 ranked=[i["id"] for i in items])
    text = report(items, store, store["topic"], a.days, a.top)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(store, indent=1, default=str))
        print(f"saved {a.out} ({len(store['items'])} items)", file=sys.stderr)
    if a.md:
        a.md.write_text(text)
    print(text)


# jq projection run inside Firecrawl's workspace when a response comes back as a
# "retained" preview: keeps only the fields ingest() scores, ~100x smaller.
PROJECT_JQ = r'''[.data.alexandria[] | {provider, capability, error, data: (
  if .capability == "tiktok/search-videos" then {search_item_list: [.data.search_item_list[]? | (.aweme_info // .) | {aweme_id, desc: ((.desc // "")[0:300]), create_time, create_time_utc, url, is_ad, is_paid_partnership, statistics: (.statistics | {play_count, digg_count, comment_count, share_count, collect_count}), author: {unique_id: .author.unique_id, follower_count: .author.follower_count}, video: {duration: .video.duration}}]}
  elif .capability == "instagram/search-reels" then {reels: [.data.reels[]? | {shortcode, id, url, caption: ((.caption // "")[0:300]), taken_at, video_view_count, video_play_count, like_count, comment_count, video_duration, is_video, is_ad, is_paid_partnership, owner: {username: .owner.username}}]}
  elif .capability == "tiktok/video-comments" then {comments: [.data.comments[]? | {aweme_id, text: ((.text // "")[0:300]), digg_count, reply_comment_total}]}
  elif .capability == "instagram/post-comments" then {comments: [.data.comments[]? | {text: ((.text // "")[0:300]), comment_like_count}]}
  elif .capability == "youtube/video-comments" then {comments: [.data.comments[]? | {content: ((.content // "")[0:300]), engagement}]}
  else .data end)}]'''


def cmd_project(a) -> None:
    cmd = "jq -c '" + re.sub(r"\s*\n\s*", " ", PROJECT_JQ).replace("'", "'\\''") + "' response.json"
    print(json.dumps([{"provider": "firecrawl", "capability": "bash",
                       "options": {"workspaceId": a.workspace_id, "command": cmd}}], indent=1))


def cmd_comments_plan(a) -> None:
    store = json.loads(a.social_json.read_text())
    items = sorted(store["items"].values(), key=lambda i: i.get("score", 0), reverse=True)
    calls = []
    for plat, cap in (("tiktok", "tiktok/video-comments"), ("instagram", "instagram/post-comments")):
        for it in [i for i in items if i["platform"] == plat and i.get("in_window", True)][: a.top]:
            calls.append({"provider": "scrapecreators", "capability": cap, "options": {"url": it["url"]}})
    if a.youtube_json and a.youtube_json.exists():
        yt = json.loads(a.youtube_json.read_text())
        vids = (yt.get("youtube_long_form") or []) + (yt.get("youtube_shorts") or []) or yt.get("videos") or []
        vids = sorted(vids, key=lambda v: v.get("composite_score") or 0, reverse=True)[: a.top]
        for v in vids:
            calls.append({"provider": "scrapecreators", "capability": "youtube/video-comments",
                          "options": {"url": v["url"], "order": "top"}})
    store["pending_comments"] = [{"capability": c["capability"], "url": c["options"]["url"]} for c in calls]
    a.social_json.write_text(json.dumps(store, indent=1, default=str))
    print(f"# {len(calls)} comment calls (~{2 * len(calls)} credits). Run with alexandria_library_read (keep the order), then "
          f"`social_trends.py ingest <result file> --out {a.social_json}`")
    for i in range(0, len(calls), 10):
        print(json.dumps(calls[i:i + 10], indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="print the alexandria_library_read calls to run")
    p.add_argument("topic")
    p.add_argument("--extra", nargs="*", default=[], help="1-2 adjacent phrases creators actually use")
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--ig-pages", type=int, default=2, help="Instagram search pages per query (10 reels each)")
    p.set_defaults(fn=cmd_plan)
    i = sub.add_parser("ingest", help="parse + score saved alexandria results, print markdown")
    i.add_argument("files", nargs="+", type=Path)
    i.add_argument("--topic", default="")
    i.add_argument("--days", type=int, default=30)
    i.add_argument("--top", type=int, default=10, help="rows per platform table")
    i.add_argument("--out", type=Path, default=None, help="research/<date>-<slug>.social.json (merged across runs)")
    i.add_argument("--md", type=Path, default=None, help="also write the markdown summary here")
    i.set_defaults(fn=cmd_ingest)
    pr = sub.add_parser("project", help="print the firecrawl/bash call that compacts a retained response")
    pr.add_argument("workspace_id")
    pr.set_defaults(fn=cmd_project)
    c = sub.add_parser("comments-plan", help="print comment-pull calls for the top outliers")
    c.add_argument("social_json", type=Path)
    c.add_argument("--youtube-json", type=Path, default=None, help="fetch_trends.py --out-json file")
    c.add_argument("--top", type=int, default=3)
    c.set_defaults(fn=cmd_comments_plan)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
