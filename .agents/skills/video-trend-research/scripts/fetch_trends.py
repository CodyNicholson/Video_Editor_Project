#!/usr/bin/env python3
"""Fetch and score recent high-performing videos for a given topic.

Primary automated collector for the `video-trend-research` skill:
- YouTube (Long-Form + Shorts): Uses YouTube Data API v3 when YOUTUBE_API_KEY
  is present in .env / environment; otherwise falls back cleanly to zero-key
  YouTube public search (ytInitialData) + top-video watch-page enrichment to
  recover exact publish dates, subscriber counts, likes, and outlier ratios.
- TikTok & Instagram Reels: Emits structured web-search queries and direct
  search URLs for the agent's web-search / browser pass, and automatically uses
  SCRAPECREATORS_API_KEY if configured in .env.

Usage:
  .venv/bin/python .agents/skills/video-trend-research/scripts/fetch_trends.py \
      "Software development with AI agents" --days 30 --limit 25 --enrich-top 15 \
      --out-json research/2026-11-24-software-development-with-ai-agents.json
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import statistics
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests
from dotenv import load_dotenv

# Load repo .env if present
REPO_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(REPO_ROOT / ".env")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "at",
    "by", "from", "is", "are", "was", "were", "be", "been", "this", "that",
    "these", "those", "it", "its", "as", "into", "about", "your", "my", "our",
    "you", "we", "i", "how", "what", "why", "when", "who", "all", "new", "just",
    "more", "most", "using", "use", "used", "will", "can", "get", "make", "not",
    "no", "so", "up", "out", "do", "does", "did", "than", "then", "now", "here",
    "there", "video", "2024", "2025", "2026", "2027",
}

TITLE_PATTERN_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("how_to_or_tutorial", re.compile(r"\b(how i|how to|tutorial|guide|walkthrough|step[- ]by[- ]step|workflow|setup)\b", re.I)),
    ("build_or_demo", re.compile(r"\b(i built|building|build a|from scratch|full app|live build|demo)\b", re.I)),
    ("comparison_or_vs", re.compile(r"\b(vs\.?|versus|compared|better than|replaced|switched from)\b", re.I)),
    ("contrarian_or_warning", re.compile(r"\b(stop|don'?t|never|wrong|dead|mistake|truth|lie|overrated|killed|nobody)\b", re.I)),
    ("numbers_or_list", re.compile(r"(^|\s)\d+(\+|x|×|%|k|m|min|mins|hours|days|tools|ways|tips|things|agents)\b", re.I)),
    ("time_or_speed_claim", re.compile(r"\b(\d+\s*(sec|seconds|min|mins|minutes|hr|hrs|hours|days|weeks)|fast|instant|overnight)\b", re.I)),
    ("question_hook", re.compile(r"\?")),
    ("personal_experiment", re.compile(r"\b(i tried|i tested|i spent|i used|after \d+)\b", re.I)),
]


@dataclass
class VideoItem:
    platform: str
    format: str  # "long_form" | "short"
    video_id: str
    title: str
    url: str
    channel: str
    channel_url: str = ""
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    subscriber_count: int | None = None
    duration_seconds: int | None = None
    published_text: str = ""
    published_iso: str = ""
    age_days: float | None = None
    views_per_day: float | None = None
    outlier_ratio: float | None = None
    engagement_rate: float | None = None
    breakout_tier: str = ""
    composite_score: float = 0.0
    thumbnail_url: str = ""
    description_snippet: str = ""
    source_queries: list[str] = field(default_factory=list)
    title_patterns: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Number / date / duration parsers
# ---------------------------------------------------------------------------

def parse_human_count(text: str | None) -> int | None:
    if not text:
        return None
    s = text.strip().replace(",", "")
    # Match e.g. "1.2M", "450K", "12,345 views", "85.4K subscribers"
    m = re.search(r"(\d+(?:\.\d+)?)\s*([KMB])?\b", s, re.I)
    if not m:
        return None
    val = float(m.group(1))
    suffix = (m.group(2) or "").upper()
    mult = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[suffix]
    return int(round(val * mult))


def parse_duration_text(text: str | None) -> int | None:
    if not text:
        return None
    s = text.strip()
    if s.upper() == "SHORTS":
        return 45
    parts = re.findall(r"\d+", s)
    if not parts:
        return None
    nums = [int(p) for p in parts]
    if len(nums) == 3:
        return nums[0] * 3600 + nums[1] * 60 + nums[2]
    if len(nums) == 2:
        return nums[0] * 60 + nums[1]
    return nums[0]


def parse_iso8601_duration(iso: str | None) -> int | None:
    if not iso:
        return None
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m:
        return None
    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mi * 60 + s


def parse_relative_age_days(text: str | None) -> float | None:
    if not text:
        return None
    s = text.lower().strip()
    s = re.sub(r"^(streamed|premiered|published)\s+", "", s)
    # Match both full ("2 weeks ago", "9 days ago") and compact ("9d ago", "4w ago", "2mo ago")
    m = re.search(
        r"(\d+)\s*(seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d|weeks?|wks?|w|months?|mos?|mo|years?|yrs?|y)\s+ago\b",
        s,
    )
    if not m:
        return None
    n = float(m.group(1))
    u = m.group(2)
    if u.startswith("s"):
        scale = 1 / 86400
    elif u in ("m", "min", "mins", "minute", "minutes"):
        scale = 1 / 1440
    elif u.startswith("h"):
        scale = 1 / 24
    elif u.startswith("d"):
        scale = 1.0
    elif u.startswith("w"):
        scale = 7.0
    elif u.startswith("mo"):
        scale = 30.0
    else:
        scale = 365.0
    return max(n * scale, 0.1)


def parse_date_string(text: str | None) -> tuple[str, float | None]:
    """Parse watch-page dateText like 'Nov 12, 2026' or 'Premiered Oct 3, 2026'."""
    if not text:
        return "", None
    cleaned = re.sub(r"^(Streamed live on|Premiered|Published on)\s+", "", text.strip(), flags=re.I)
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(cleaned, fmt).replace(tzinfo=timezone.utc)
            age = max((datetime.now(timezone.utc) - dt).total_seconds() / 86400.0, 0.25)
            return dt.strftime("%Y-%m-%d"), round(age, 2)
        except ValueError:
            continue
    return "", None


def extract_text(obj: Any) -> str:
    if not obj:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        if "simpleText" in obj:
            return str(obj["simpleText"])
        if "content" in obj and isinstance(obj["content"], str):
            return obj["content"]
        if "runs" in obj and isinstance(obj["runs"], list):
            return "".join(str(r.get("text", "")) for r in obj["runs"] if isinstance(r, dict))
    return ""


def detect_title_patterns(title: str) -> list[str]:
    return [name for name, rx in TITLE_PATTERN_RULES if rx.search(title)]


# ---------------------------------------------------------------------------
# YouTube protobuf `sp` filter encoder (zero-key search)
# ---------------------------------------------------------------------------

def _encode_varint(value: int) -> bytes:
    out = bytearray()
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def _encode_field_varint(field_num: int, value: int) -> bytes:
    return _encode_varint((field_num << 3) | 0) + _encode_varint(value)


def _encode_field_bytes(field_num: int, payload: bytes) -> bytes:
    return _encode_varint((field_num << 3) | 2) + _encode_varint(len(payload)) + payload


def build_youtube_sp(
    sort: str = "relevance",
    days: int = 30,
    duration: str | None = None,
    shorts_only: bool = False,
) -> str:
    """Encode YouTube search `sp` query parameter.

    sort: 'relevance' | 'date' | 'views'
    days: <=1 (today), <=7 (week), <=30 (month), >30 (year)
    duration: None | 'short' (<4m) | 'medium' (4-20m) | 'long' (>20m)
    shorts_only: when True, sets duration <4m without requiring '#shorts' in query
    """
    sort_map = {"relevance": 0, "date": 2, "views": 3}
    if days <= 1:
        upload_code = 2  # today
    elif days <= 7:
        upload_code = 3  # this week
    elif days <= 30:
        upload_code = 4  # this month
    else:
        upload_code = 5  # this year

    sub = _encode_field_varint(1, upload_code) + _encode_field_varint(2, 1)  # type=video
    dur_map = {"short": 1, "long": 2, "medium": 3}
    eff_dur = "short" if shorts_only else duration
    if eff_dur in dur_map:
        sub += _encode_field_varint(3, dur_map[eff_dur])

    msg = b""
    s_code = sort_map.get(sort, 0)
    if s_code:
        msg += _encode_field_varint(1, s_code)
    msg += _encode_field_bytes(2, sub)
    return base64.b64encode(msg).decode("ascii")


# ---------------------------------------------------------------------------
# YouTube Collectors
# ---------------------------------------------------------------------------

def _extract_yt_initial_data(html: str) -> dict[str, Any] | None:
    patterns = [
        r"var\s+ytInitialData\s*=\s*(\{.*?\});\s*</script>",
        r"window\[\"ytInitialData\"\]\s*=\s*(\{.*?\});",
        r"ytInitialData\s*=\s*(\{.*?\});",
    ]
    for pat in patterns:
        m = re.search(pat, html, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                continue
    return None


def _walk_dict(node: Any):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk_dict(v)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_dict(item)


def fetch_youtube_public_search(
    session: requests.Session,
    query: str,
    days: int,
    sort: str,
    limit: int,
    duration: str | None = None,
) -> list[VideoItem]:
    sp = build_youtube_sp(sort=sort, days=days, duration=duration)
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}&sp={quote_plus(sp)}"
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = _extract_yt_initial_data(resp.text)
    if not data:
        return []

    items: list[VideoItem] = []
    seen: set[str] = set()

    for node in _walk_dict(data):
        # Standard videoRenderer (long-form and some shorts)
        if "videoRenderer" in node and isinstance(node["videoRenderer"], dict):
            vr = node["videoRenderer"]
            vid = vr.get("videoId")
            if not vid or vid in seen:
                continue
            title = extract_text(vr.get("title"))
            if not title:
                continue
            seen.add(vid)

            channel = extract_text(vr.get("ownerText") or vr.get("longBylineText"))
            chan_url = ""
            runs = (vr.get("ownerText") or {}).get("runs") or []
            if runs and isinstance(runs[0], dict):
                ep = runs[0].get("navigationEndpoint", {}).get("browseEndpoint", {})
                if ep.get("canonicalBaseUrl"):
                    chan_url = "https://www.youtube.com" + ep["canonicalBaseUrl"]

            view_text = extract_text(vr.get("viewCountText"))
            views = parse_human_count(view_text)
            pub_text = extract_text(vr.get("publishedTimeText"))
            age_days = parse_relative_age_days(pub_text)
            dur_text = extract_text(vr.get("lengthText"))
            dur_sec = parse_duration_text(dur_text)

            # Detect Shorts via URL command, duration <= 180s with /shorts/, or duration <= 65s
            nav_url = (
                vr.get("navigationEndpoint", {})
                .get("commandMetadata", {})
                .get("webCommandMetadata", {})
                .get("url", "")
            )
            is_short = (
                "/shorts/" in nav_url
                or (dur_sec is not None and dur_sec <= 65)
                or "#shorts" in title.lower()
            )
            vid_url = (
                f"https://www.youtube.com/shorts/{vid}"
                if is_short
                else f"https://www.youtube.com/watch?v={vid}"
            )
            thumbs = (vr.get("thumbnail") or {}).get("thumbnails") or []
            thumb_url = thumbs[-1].get("url", "") if thumbs else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
            desc_snips = vr.get("detailedMetadataSnippets") or []
            desc = ""
            if desc_snips and isinstance(desc_snips[0], dict):
                desc = extract_text(desc_snips[0].get("snippetText"))

            items.append(
                VideoItem(
                    platform="youtube",
                    format="short" if is_short else "long_form",
                    video_id=vid,
                    title=title,
                    url=vid_url,
                    channel=channel,
                    channel_url=chan_url,
                    views=views,
                    duration_seconds=dur_sec,
                    published_text=pub_text,
                    age_days=age_days,
                    thumbnail_url=thumb_url,
                    description_snippet=desc[:240],
                    source_queries=[f"{query} ({sort})"],
                    title_patterns=detect_title_patterns(title),
                )
            )

        # Shorts lockup model inside Shorts shelves
        elif "shortsLockupViewModel" in node and isinstance(node["shortsLockupViewModel"], dict):
            sm = node["shortsLockupViewModel"]
            vid = (
                sm.get("onTap", {})
                .get("innertubeCommand", {})
                .get("reelWatchEndpoint", {})
                .get("videoId")
            )
            if not vid or vid in seen:
                continue
            title = extract_text(sm.get("overlayMetadata", {}).get("primaryText")) or sm.get("accessibilityText", "")
            if not title:
                continue
            seen.add(vid)
            sec_text = extract_text(sm.get("overlayMetadata", {}).get("secondaryText"))
            views = parse_human_count(sec_text)
            items.append(
                VideoItem(
                    platform="youtube",
                    format="short",
                    video_id=vid,
                    title=title,
                    url=f"https://www.youtube.com/shorts/{vid}",
                    channel="",
                    views=views,
                    duration_seconds=45,
                    thumbnail_url=f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                    source_queries=[f"{query} ({sort}, shorts-shelf)"],
                    title_patterns=detect_title_patterns(title),
                )
            )

        if len(items) >= limit:
            break

    return items


def enrich_youtube_watch_page(session: requests.Session, item: VideoItem) -> None:
    """Fetch watch page once to extract exact publish date, subscribers, and likes."""
    watch_url = f"https://www.youtube.com/watch?v={item.video_id}"
    try:
        resp = session.get(watch_url, timeout=15)
        resp.raise_for_status()
    except Exception:
        return

    data = _extract_yt_initial_data(resp.text)
    if not data:
        return

    for node in _walk_dict(data):
        if "videoPrimaryInfoRenderer" in node and isinstance(node["videoPrimaryInfoRenderer"], dict):
            pi = node["videoPrimaryInfoRenderer"]
            dt_text = extract_text(pi.get("dateText"))
            iso, exact_age = parse_date_string(dt_text)
            if iso:
                item.published_iso = iso
                if exact_age is not None:
                    item.age_days = exact_age
                if not item.published_text:
                    item.published_text = dt_text

            vc = extract_text((pi.get("viewCount") or {}).get("videoViewCountRenderer", {}).get("viewCount"))
            parsed_vc = parse_human_count(vc)
            if parsed_vc is not None:
                item.views = parsed_vc

        elif "videoSecondaryInfoRenderer" in node and isinstance(node["videoSecondaryInfoRenderer"], dict):
            si = node["videoSecondaryInfoRenderer"]
            owner = (si.get("owner") or {}).get("videoOwnerRenderer") or {}
            if not item.channel:
                item.channel = extract_text(owner.get("title"))
            sub_text = extract_text(owner.get("subscriberCountText"))
            subs = parse_human_count(sub_text)
            if subs is not None:
                item.subscriber_count = subs

        elif "segmentedLikeDislikeButtonViewModel" in node and isinstance(node["segmentedLikeDislikeButtonViewModel"], dict):
            lm = (
                node["segmentedLikeDislikeButtonViewModel"]
                .get("likeButtonViewModel", {})
                .get("likeButtonViewModel", {})
                .get("toggleButtonViewModel", {})
                .get("toggleButtonViewModel", {})
                .get("defaultButtonViewModel", {})
                .get("buttonViewModel", {})
            )
            like_str = lm.get("title") or lm.get("accessibilityText") or ""
            likes = parse_human_count(like_str)
            if likes is not None:
                item.likes = likes

    # Also grab exact duration from microformat / ytInitialPlayerResponse if missing
    if item.duration_seconds is None:
        m = re.search(r'"lengthSeconds"\s*:\s*"(\d+)"', resp.text)
        if m:
            item.duration_seconds = int(m.group(1))
            if item.duration_seconds <= 62:
                item.format = "short"


def fetch_youtube_api_v3(
    session: requests.Session,
    api_key: str,
    queries: list[str],
    days: int,
    limit: int,
) -> list[VideoItem]:
    """Fetch exact YouTube video + channel stats using YouTube Data API v3."""
    published_after = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    id_to_queries: dict[str, list[str]] = {}
    for q in queries:
        for order in ("viewCount", "relevance"):
            params = {
                "part": "snippet",
                "type": "video",
                "q": q,
                "publishedAfter": published_after,
                "order": order,
                "maxResults": min(limit, 50),
                "relevanceLanguage": "en",
                "key": api_key,
            }
            r = session.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=20)
            r.raise_for_status()
            for entry in r.json().get("items", []):
                vid = (entry.get("id") or {}).get("videoId")
                if vid:
                    id_to_queries.setdefault(vid, []).append(f"{q} ({order})")

    video_ids = list(id_to_queries.keys())
    if not video_ids:
        return []

    raw_videos: list[dict[str, Any]] = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        r = session.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(batch),
                "key": api_key,
            },
            timeout=20,
        )
        r.raise_for_status()
        raw_videos.extend(r.json().get("items", []))

    channel_ids = list({v["snippet"]["channelId"] for v in raw_videos if v.get("snippet", {}).get("channelId")})
    chan_subs: dict[str, int] = {}
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i : i + 50]
        r = session.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "statistics", "id": ",".join(batch), "key": api_key},
            timeout=20,
        )
        r.raise_for_status()
        for ch in r.json().get("items", []):
            cid = ch.get("id")
            sc = (ch.get("statistics") or {}).get("subscriberCount")
            if cid and sc is not None:
                chan_subs[cid] = int(sc)

    now = datetime.now(timezone.utc)
    items: list[VideoItem] = []
    for v in raw_videos:
        vid = v["id"]
        sn = v.get("snippet", {})
        st = v.get("statistics", {})
        cd = v.get("contentDetails", {})
        title = sn.get("title", "")
        pub_raw = sn.get("publishedAt", "")
        age_days = None
        pub_iso = ""
        if pub_raw:
            dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            pub_iso = dt.strftime("%Y-%m-%d")
            age_days = round(max((now - dt).total_seconds() / 86400.0, 0.25), 2)

        dur_sec = parse_iso8601_duration(cd.get("duration"))
        is_short = (dur_sec is not None and dur_sec <= 62) or "#shorts" in title.lower()
        cid = sn.get("channelId", "")
        views = int(st["viewCount"]) if "viewCount" in st else None
        likes = int(st["likeCount"]) if "likeCount" in st else None
        comments = int(st["commentCount"]) if "commentCount" in st else None
        thumbs = sn.get("thumbnails") or {}
        thumb_url = (thumbs.get("high") or thumbs.get("medium") or {}).get("url", "")

        items.append(
            VideoItem(
                platform="youtube",
                format="short" if is_short else "long_form",
                video_id=vid,
                title=title,
                url=f"https://www.youtube.com/shorts/{vid}" if is_short else f"https://www.youtube.com/watch?v={vid}",
                channel=sn.get("channelTitle", ""),
                channel_url=f"https://www.youtube.com/channel/{cid}" if cid else "",
                views=views,
                likes=likes,
                comments=comments,
                subscriber_count=chan_subs.get(cid),
                duration_seconds=dur_sec,
                published_text=pub_iso,
                published_iso=pub_iso,
                age_days=age_days,
                thumbnail_url=thumb_url,
                description_snippet=(sn.get("description") or "").replace("\n", " ")[:240],
                source_queries=id_to_queries.get(vid, []),
                title_patterns=detect_title_patterns(title),
            )
        )
    return items


# ---------------------------------------------------------------------------
# Optional TikTok / Instagram API Hook (ScrapeCreators if configured)
# ---------------------------------------------------------------------------

def fetch_scrapecreators_social(
    session: requests.Session,
    api_key: str,
    topic: str,
) -> dict[str, Any]:
    """Optional structured TikTok/IG fetcher if SCRAPECREATORS_API_KEY is set."""
    headers = {"x-api-key": api_key}
    out: dict[str, Any] = {"tiktok": [], "instagram": [], "errors": []}

    # TikTok keyword search
    try:
        r = session.get(
            "https://api.scrapecreators.com/v1/tiktok/search/keyword",
            params={"query": topic, "sort_by": "most-liked"},
            headers=headers,
            timeout=25,
        )
        if r.ok:
            payload = r.json()
            for entry in (payload.get("search_item_list") or payload.get("data") or [])[:20]:
                aweme = entry.get("aweme_info") or entry
                stats = aweme.get("statistics") or {}
                author = aweme.get("author") or {}
                vid = str(aweme.get("aweme_id") or aweme.get("id") or "")
                uname = author.get("unique_id") or ""
                out["tiktok"].append({
                    "video_id": vid,
                    "title": (aweme.get("desc") or "")[:200],
                    "author": uname,
                    "url": f"https://www.tiktok.com/@{uname}/video/{vid}" if uname and vid else "",
                    "views": stats.get("play_count"),
                    "likes": stats.get("digg_count"),
                    "comments": stats.get("comment_count"),
                    "shares": stats.get("share_count"),
                    "saves": stats.get("collect_count"),
                })
        else:
            out["errors"].append(f"tiktok_api_http_{r.status_code}")
    except Exception as exc:
        out["errors"].append(f"tiktok_api_error: {exc}")

    return out


# ---------------------------------------------------------------------------
# Scoring & Pattern Synthesis
# ---------------------------------------------------------------------------

def score_items(items: list[VideoItem]) -> None:
    velocities = []
    for it in items:
        if it.views is not None and it.age_days is not None and it.age_days > 0:
            it.views_per_day = round(it.views / max(it.age_days, 0.5), 1)
            velocities.append(it.views_per_day)
        if it.views is not None and it.subscriber_count is not None and it.subscriber_count > 0:
            it.outlier_ratio = round(it.views / max(it.subscriber_count, 100), 2)
        if it.views and it.views > 0 and it.likes is not None:
            eng = (it.likes + (it.comments or 0)) / it.views
            it.engagement_rate = round(eng * 100.0, 2)

    median_vel = statistics.median(velocities) if velocities else 0.0

    for it in items:
        v = it.views or 0
        vel = it.views_per_day or 0.0
        ratio = it.outlier_ratio

        # Composite score balances real demand (log velocity + log views) with
        # packaging/topic breakout strength (outlier ratio).
        vel_term = math.log10(vel + 10.0) * 20.0
        vol_term = math.log10(v + 10.0) * 10.0
        outlier_term = math.log2(ratio + 1.0) * 22.0 if ratio is not None else 0.0
        eng_term = min((it.engagement_rate or 0.0), 10.0) * 1.5
        it.composite_score = round(vel_term + vol_term + outlier_term + eng_term, 2)

        if ratio is not None and ratio >= 5.0 and v >= 10_000:
            it.breakout_tier = "Mega Outlier (>=5x subs)"
        elif ratio is not None and ratio >= 2.0 and v >= 5_000:
            it.breakout_tier = "Strong Outlier (>=2x subs)"
        elif vel >= 5_000:
            it.breakout_tier = "High Velocity (>=5k/day)"
        elif median_vel > 0 and vel >= median_vel:
            it.breakout_tier = "Above-Median Velocity"
        else:
            it.breakout_tier = "Baseline"


def summarize_patterns(items: list[VideoItem]) -> dict[str, Any]:
    unigrams: Counter[str] = Counter()
    bigrams: Counter[str] = Counter()
    pattern_counts: Counter[str] = Counter()

    for it in items:
        tokens = [
            t for t in re.findall(r"[a-zA-Z0-9+#.-]{2,}", it.title.lower())
            if t not in STOPWORDS and not t.isdigit()
        ]
        for t in set(tokens):
            unigrams[t] += 1
        for a, b in zip(tokens, tokens[1:]):
            if a != b:
                bigrams[f"{a} {b}"] += 1
        for pat in it.title_patterns:
            pattern_counts[pat] += 1

    long_items = [i for i in items if i.format == "long_form"]
    short_items = [i for i in items if i.format == "short"]

    def _stats(group: list[VideoItem]) -> dict[str, Any]:
        vs = [i.views for i in group if i.views is not None]
        durs = [i.duration_seconds for i in group if i.duration_seconds is not None]
        vels = [i.views_per_day for i in group if i.views_per_day is not None]
        return {
            "count": len(group),
            "median_views": int(statistics.median(vs)) if vs else None,
            "max_views": max(vs) if vs else None,
            "median_views_per_day": round(statistics.median(vels), 1) if vels else None,
            "median_duration_sec": int(statistics.median(durs)) if durs else None,
        }

    return {
        "long_form_stats": _stats(long_items),
        "shorts_stats": _stats(short_items),
        "top_title_patterns": pattern_counts.most_common(8),
        "top_keywords": unigrams.most_common(15),
        "top_bigrams": bigrams.most_common(12),
    }


def build_social_research_plan(topic: str, days: int) -> dict[str, Any]:
    now = datetime.now()
    year = now.year
    month_name = now.strftime("%B %Y")
    q_enc = quote_plus(topic)
    tag_slug = re.sub(r"[^a-z0-9]", "", topic.lower())[:28]

    return {
        "window_days": days,
        "web_search_queries": {
            "tiktok": [
                f'site:tiktok.com "{topic}" {year}',
                f"site:tiktok.com {topic} viral OR views OR workflow {month_name}",
                f"site:tiktok.com/discover {topic}",
            ],
            "instagram": [
                f'site:instagram.com/reel "{topic}" {year}',
                f"site:instagram.com/reel {topic} {month_name}",
                f"instagram reels trending {topic} {year}",
            ],
            "cross_platform_buzz": [
                f"{topic} viral youtube tiktok reels {month_name}",
                f"{topic} best videos tutorials breakdown {year}",
            ],
        },
        "direct_browser_urls": {
            "youtube_views_recent": f"https://www.youtube.com/results?search_query={q_enc}&sp={quote_plus(build_youtube_sp('views', days))}",
            "tiktok_search": f"https://www.tiktok.com/search/video?q={q_enc}",
            "tiktok_creative_center": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en",
            "instagram_keyword_search": f"https://www.instagram.com/explore/search/keyword/?q={q_enc}",
            "instagram_tag": f"https://www.instagram.com/explore/tags/{tag_slug}/",
        },
    }


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def format_compact(n: int | float | None) -> str:
    if n is None:
        return "-"
    n = float(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{int(round(n))}"


def format_duration(sec: int | None) -> str:
    if sec is None:
        return "-"
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch & score recent top-performing videos for a topic.")
    ap.add_argument("topic", help='Topic to research, e.g. "Software development with AI agents"')
    ap.add_argument("--days", type=int, default=30, help="Recency window in days (default: 30)")
    ap.add_argument("--limit", type=int, default=25, help="Max results per query/sort pass (default: 25)")
    ap.add_argument("--enrich-top", type=int, default=15, help="Enrich top N videos for subscriber/outlier stats in zero-key mode (default: 15)")
    ap.add_argument("--extra-queries", nargs="*", default=[], help="Additional query variations to merge")
    ap.add_argument("--out-json", type=Path, default=None, help="Write full JSON output to path")
    args = ap.parse_args()

    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    })

    queries = [args.topic] + list(args.extra_queries)
    yt_api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    sc_api_key = os.getenv("SCRAPECREATORS_API_KEY", "").strip()

    youtube_mode = "youtube_data_api_v3" if yt_api_key else "youtube_public_search"
    merged: dict[str, VideoItem] = {}
    errors: list[str] = []

    if yt_api_key:
        try:
            fetched = fetch_youtube_api_v3(session, yt_api_key, queries, args.days, args.limit)
            for it in fetched:
                merged[it.video_id] = it
        except Exception as exc:
            errors.append(f"youtube_api_v3_failed_falling_back: {exc}")
            youtube_mode = "youtube_public_search_fallback"

    if not merged:
        # Query high-view winners, relevance winners, and short-duration (<4m) high-view clips
        search_passes: list[tuple[str, str, str | None]] = []
        for q in queries:
            search_passes.append((q, "views", None))
            search_passes.append((q, "relevance", None))
        # Short-form pass: filter <4m sorted by views (without forcing '#shorts' in title)
        # plus a relevance pass so Shorts shelves are also surfaced.
        search_passes.append((args.topic, "views", "short"))
        search_passes.append((f"{args.topic} shorts", "relevance", "short"))

        for q, sort_mode, dur_filter in search_passes:
            try:
                batch = fetch_youtube_public_search(
                    session=session,
                    query=q,
                    days=args.days,
                    sort=sort_mode,
                    limit=args.limit,
                    duration=dur_filter,
                )
                for it in batch:
                    if it.video_id in merged:
                        existing = merged[it.video_id]
                        existing.source_queries.extend(it.source_queries)
                        if existing.views is None and it.views is not None:
                            existing.views = it.views
                        if existing.age_days is None and it.age_days is not None:
                            existing.age_days = it.age_days
                            existing.published_text = it.published_text
                    else:
                        merged[it.video_id] = it
                time.sleep(0.2)
            except Exception as exc:
                errors.append(f"youtube_search_error ({q}, {sort_mode}): {exc}")

    items = list(merged.values())

    # Preliminary score to pick top candidates for watch-page enrichment
    score_items(items)
    items.sort(key=lambda x: (x.views_per_day or 0.0, x.views or 0), reverse=True)

    if youtube_mode != "youtube_data_api_v3" and args.enrich_top > 0:
        # Enrich top long-form and top shorts so both formats get outlier ratios
        top_long = [i for i in items if i.format == "long_form"][: max(1, int(args.enrich_top * 0.7))]
        top_short = [i for i in items if i.format == "short"][: max(1, args.enrich_top - len(top_long))]
        to_enrich = top_long + top_short
        for it in to_enrich:
            enrich_youtube_watch_page(session, it)
            time.sleep(0.25)

    # Filter out videos clearly outside requested window (allow 25% slack for YouTube's fuzzy "1 month ago" text)
    max_age = args.days * 1.25
    filtered = [i for i in items if i.age_days is None or i.age_days <= max_age]
    score_items(filtered)
    filtered.sort(key=lambda x: x.composite_score, reverse=True)

    long_form = [i for i in filtered if i.format == "long_form"]
    shorts = [i for i in filtered if i.format == "short"]

    social_api_data = None
    if sc_api_key:
        social_api_data = fetch_scrapecreators_social(session, sc_api_key, args.topic)

    payload = {
        "topic": args.topic,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_days": args.days,
        "collectors": {
            "youtube": youtube_mode,
            "tiktok_instagram_api": "scrapecreators" if sc_api_key else "web_search_and_browser_pass_required",
        },
        "summary": summarize_patterns(filtered),
        "youtube_long_form": [asdict(i) for i in long_form],
        "youtube_shorts": [asdict(i) for i in shorts],
        "social_api_data": social_api_data,
        "social_research_plan": build_social_research_plan(args.topic, args.days),
        "errors": errors,
    }

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print crisp terminal summary for the agent
    print(f"# Trend Fetch Summary — {args.topic} (last {args.days} days)")
    print(f"- YouTube collector: {youtube_mode} | Long-form: {len(long_form)} | Shorts: {len(shorts)}")
    print(f"- TikTok/IG mode: {payload['collectors']['tiktok_instagram_api']}")
    if args.out_json:
        print(f"- Saved JSON: {args.out_json}")
    if errors:
        print(f"- Warnings: {len(errors)} ({'; '.join(errors[:3])})")

    def _print_table(heading: str, rows: list[VideoItem], max_rows: int = 10) -> None:
        print(f"\n## {heading} (top {min(len(rows), max_rows)})")
        if not rows:
            print("(none found)")
            return
        print("| # | Views | Views/d | Subs | Outlier | Dur | Age | Channel | Title |")
        print("|---|---:|---:|---:|---:|---:|---:|---|---|")
        for idx, r in enumerate(rows[:max_rows], 1):
            ratio_s = f"{r.outlier_ratio:.1f}x" if r.outlier_ratio is not None else "-"
            age_s = f"{r.age_days:.0f}d" if r.age_days is not None else (r.published_text or "-")
            clean_title = r.title.replace("|", "/").strip()[:72]
            clean_chan = (r.channel or "-").replace("|", "/").strip()[:24]
            print(
                f"| {idx} | {format_compact(r.views)} | {format_compact(r.views_per_day)} | "
                f"{format_compact(r.subscriber_count)} | {ratio_s} | {format_duration(r.duration_seconds)} | "
                f"{age_s} | {clean_chan} | [{clean_title}]({r.url}) |"
            )

    _print_table("YouTube Long-Form Outliers & Winners", long_form, 12)
    _print_table("YouTube Shorts Outliers & Winners", shorts, 10)

    pats = payload["summary"]["top_title_patterns"]
    kws = payload["summary"]["top_keywords"][:10]
    print("\n## Detected Title Patterns & Recurring Terms")
    print("- Patterns:", ", ".join(f"{k} ({v})" for k, v in pats) or "none")
    print("- Top terms:", ", ".join(f"{k} ({v})" for k, v in kws) or "none")
    print("\n## Next Step: TikTok & Instagram Reels Queries")
    for plat in ("tiktok", "instagram"):
        for q in payload["social_research_plan"]["web_search_queries"][plat]:
            print(f"- [{plat}] {q}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
