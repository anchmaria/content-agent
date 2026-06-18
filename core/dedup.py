import json
import os

SEEN_FILE = os.path.join(os.path.dirname(__file__), "..", "seen.json")


def _load() -> dict:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"videos": [], "news": []}


def _save(seen: dict) -> None:
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def filter_new_videos(videos: list[dict]) -> list[dict]:
    seen = _load()
    seen_ids = set(seen.get("videos", []))
    return [v for v in videos if v["id"] not in seen_ids]


def filter_new_news(news: list[dict]) -> list[dict]:
    seen = _load()
    seen_urls = set(seen.get("news", []))
    return [n for n in news if n.get("url") not in seen_urls]


def mark_seen(videos: list[dict], news: list[dict]) -> None:
    seen = _load()
    seen["videos"] = list(set(seen.get("videos", [])) | {v["id"] for v in videos})
    seen["news"] = list(set(seen.get("news", [])) | {n["url"] for n in news if n.get("url")})
    _save(seen)
