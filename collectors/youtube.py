import requests
from datetime import datetime, timedelta, timezone
from config import YOUTUBE_API_KEY

BASE_URL = "https://www.googleapis.com/youtube/v3"

QUERIES = [
    # Ниши
    "фэн-шуй", "китайская метафизика", "астрология", "биоэнергетика",
    "feng shui", "chinese metaphysics", "astrology trends",
    "feng shui consejos", "astrología", "风水", "占星",
    "Feng Shui Tipps", "Astrologie",
    # Тревожность как боль аудитории
    "тревожность как избавиться", "тревога панические атаки", "стресс и тревога",
    "anxiety relief", "how to stop anxiety", "anxiety healing",
    "ansiedad como combatir", "Angst überwinden",
]

PAIN_KEYWORDS = [
    "почему", "не могу", "помогите", "устала", "страх", "боюсь", "тревог",
    "как избавиться", "что делать", "не работает", "не помогает", "всё плохо",
    "депрессия", "паника", "не сплю", "теряю", "зря", "обман", "не верю",
    "why", "can't", "help", "scared", "fear", "anxiety", "panic", "doesn't work",
    "what to do", "losing", "depressed", "exhausted", "struggling",
]


def _published_after(days: int = 7) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def search_videos(query: str, max_results: int = 10) -> list[dict]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
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
    result = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        params = {
            "part": "statistics,contentDetails",
            "id": ",".join(batch),
            "key": YOUTUBE_API_KEY,
        }
        r = requests.get(f"{BASE_URL}/videos", params=params, timeout=10)
        if r.status_code != 200:
            print(f"YouTube stats error {r.status_code}: {r.text[:200]}")
            continue
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


def fetch_comments(video_id: str, max_comments: int = 30) -> list[str]:
    params = {
        "part": "snippet",
        "videoId": video_id,
        "order": "relevance",
        "maxResults": max_comments,
        "key": YOUTUBE_API_KEY,
    }
    try:
        r = requests.get(f"{BASE_URL}/commentThreads", params=params, timeout=10)
        if r.status_code != 200:
            return []
        items = r.json().get("items", [])
        return [
            i["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            for i in items
        ]
    except Exception:
        return []


def extract_pains(comments: list[str]) -> list[str]:
    pains = []
    for comment in comments:
        comment_lower = comment.lower()
        if any(kw in comment_lower for kw in PAIN_KEYWORDS):
            clean = comment.replace("\n", " ").strip()
            if 10 < len(clean) < 300:
                pains.append(clean)
    return pains[:10]


def collect(max_per_query: int = 10) -> list[dict]:
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)

    all_videos = {}
    for query in QUERIES:
        videos = search_videos(query, max_per_query)
        for v in videos:
            all_videos[v["id"]] = v

    stats = get_stats(list(all_videos.keys()))

    result = []
    for vid_id, meta in all_videos.items():
        s = stats.get(vid_id, {})
        views = s.get("views", 0)
        if views < 100000:
            continue
        try:
            pub_dt = datetime.fromisoformat(meta["published"].replace("Z", "+00:00"))
            if pub_dt < cutoff:
                continue
        except Exception:
            pass
        result.append({**meta, **s})

    result.sort(key=lambda x: x.get("views", 0), reverse=True)
    return result


def collect_with_comments(videos: list[dict], top_n: int = 5) -> list[dict]:
    for video in videos[:top_n]:
        comments = fetch_comments(video["id"])
        video["raw_comments"] = comments
        video["pains"] = extract_pains(comments)
    return videos
