from delivery.telegram import send_message
from collectors.youtube import collect as collect_youtube
from collectors.google_news import collect as collect_news
from core.scoring import rank_videos, rank_news
from core.dedup import filter_new_videos, filter_new_news, mark_seen
from core.categorizer import categorize_all


def _segment_label(segments: list[str]) -> str:
    labels = {
        "seeker": "Ищущие смысл",
        "anxious": "Тревожные",
        "practical": "Практики",
        "ambitious": "Амбициозные",
        "skeptic": "Скептики",
        "general": "Широкая аудитория",
    }
    return ", ".join(labels.get(s, s) for s in segments)


def main():
    print("Собираю видео с YouTube...")
    videos = collect_youtube(max_per_query=5)

    print("Собираю новости из Google News...")
    news = collect_news()

    videos = filter_new_videos(videos)
    news = filter_new_news(news)

    videos = rank_videos(videos)
    news = rank_news(news)

    videos = categorize_all(videos)
    news = categorize_all(news)

    mark_seen(videos, news)

    pain_videos = [v for v in videos if v.get("is_pain_demand")]
    pain_news = [n for n in news if n.get("is_pain_demand")]

    lines = [
        f"✅ Сбор данных завершён.\n",
        f"📹 YouTube: {len(videos)} видео  |  🔥 боль-спрос: {len(pain_videos)}",
        f"📰 Google News: {len(news)} новостей  |  🔥 боль-спрос: {len(pain_news)}\n",
        "━━━━ ТОП ВИДЕО (боль-спрос) ━━━━",
    ]

    for v in (pain_videos or videos)[:3]:
        seg = _segment_label(v.get("segments", []))
        lines.append(f"▶ {v['title'][:65]}\n   👥 Аудитория: {seg}")

    lines.append("\n━━━━ ТОП НОВОСТИ (боль-спрос) ━━━━")
    for n in (pain_news or news)[:3]:
        seg = _segment_label(n.get("segments", []))
        lines.append(f"📌 {n['title'][:65]}\n   👥 Аудитория: {seg}")

    msg = "\n".join(lines)
    ok = send_message(msg)
    if ok:
        print("Сообщение отправлено в Telegram.")
    else:
        print("Ошибка отправки.")


if __name__ == "__main__":
    main()
