from datetime import datetime, timezone
import re


def _parse_duration_seconds(iso: str) -> int:
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not match:
        return 0
    h, m, s = (int(x or 0) for x in match.groups())
    return h * 3600 + m * 60 + s


def _hours_since(published: str) -> float:
    try:
        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        hours = delta.total_seconds() / 3600
        return max(hours, 1)
    except Exception:
        return 720


def score_video(video: dict) -> float:
    views = video.get("views", 0)
    likes = video.get("likes", 0)
    comments = video.get("comments", 0)
    published = video.get("published", "")
    duration = video.get("duration", "")

    hours = _hours_since(published)

    # velocity: скорость набора просмотров
    velocity = views / hours

    # weighted engagement: комментарии x5 (прокси пересылок), лайки x1
    # по данным 2026: shares > saves > comments > likes
    weighted_engagement = (likes * 1 + comments * 5) / max(views, 1)

    dur_sec = _parse_duration_seconds(duration)
    is_short = 1 <= dur_sec <= 60
    short_bonus = 1.3 if is_short else 1.0

    return round(velocity * (1 + weighted_engagement) * short_bonus, 2)


def score_news(item: dict) -> float:
    published = item.get("published", "")
    hours = _hours_since(published)
    return round(1000 / max(hours, 1), 2)


def rank_videos(videos: list[dict]) -> list[dict]:
    for v in videos:
        v["score"] = score_video(v)
    return sorted(videos, key=lambda x: x["score"], reverse=True)


def rank_news(news: list[dict]) -> list[dict]:
    for n in news:
        n["score"] = score_news(n)
    return sorted(news, key=lambda x: x["score"], reverse=True)
