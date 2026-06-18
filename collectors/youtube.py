import os
import requests
from datetime import datetime, timedelta, timezone
from config import YOUTUBE_API_KEY

BASE_URL = "https://www.googleapis.com/youtube/v3"

QUERIES = [
    "фэн-шуй", "китайская метафизика", "астрология", "биоэнергетика",
    "feng shui", "chinese metaphysics", "astrology trends",
    "feng shui consejos", "astrología", "风水", "占星",
    "Feng Shui Tipps", "Astrologie",
]


def _published_after(days: int = 14) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def search_videos(query: str, max_results: int = 10) -> list[dict]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "publishedAfter": _published_after(14),
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    r = requests.get(f"{BASE_URL}/search", params=params, timeout=10)
    if r.status_code != 200:
        print(f"YouTube search error {r.status_code}: {r.text[:200]}")
        return []
    items = r.json().get("items", [])
    return [{"id": i["id"]["videoId"], "title": i["snippet"]["title"],
             "channel": i["snippet"]["channelTitle"],
             "published": i["snippet"]["publishedAt"]} for i in items]


def get_stats(video_ids: list[str]) -> dict[str, dict]:
    if not video_ids:
        return {}
    params = {
        "part": "statistics,contentDetails",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY,
    }
    r = requests.get(f"{BASE_URL}/videos", params=params, timeout=10)
    if r.status_code != 200:
        print(f"YouTube stats error {r.status_code}: {r.text[:200]}")
        return {}
    result = {}
    for item in r.json().get("items", []):
        vid = item["id"]
        s = item.get("statistics", {})
        duration = item.get("contentDetails", {}).get("duration", "")
        result[vid] = {
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
            "duration": duration,
        }
    return result


def collect(max_per_query: int = 10) -> list[dict]:
    all_videos = {}
    for query in QUERIES:
        videos = search_videos(query, max_per_query)
        for v in videos:
            all_videos[v["id"]] = v

    stats = get_stats(list(all_videos.keys()))

    result = []
    for vid_id, meta in all_videos.items():
        s = stats.get(vid_id, {})
        result.append({**meta, **s})

    result.sort(key=lambda x: x.get("views", 0), reverse=True)
    return result
