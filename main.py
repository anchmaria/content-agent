import os
import tempfile
from datetime import datetime

from delivery.telegram import send_message, send_document
from collectors.youtube import collect as collect_youtube
from collectors.google_news import collect as collect_news
from core.scoring import rank_videos, rank_news
from core.dedup import filter_new_videos, filter_new_news, mark_seen
from core.categorizer import categorize_all
from core.report_builder import build_report


def main():
    print("Собираю видео с YouTube...")
    videos = collect_youtube(max_per_query=10)
    print(f"YouTube: {len(videos)}")

    print("Собираю новости из Google News...")
    news = collect_news()
    print(f"Google News: {len(news)}")

    videos = filter_new_videos(videos)
    news = filter_new_news(news)

    videos = rank_videos(videos)
    news = rank_news(news)

    videos = categorize_all(videos)
    news = categorize_all(news)

    mark_seen(videos, news)

    pain_videos = [v for v in videos if v.get("is_pain_demand")]
    pain_news = [n for n in news if n.get("is_pain_demand")]

    print("Генерирую отчёт...")
    report_text = build_report(videos, news)

    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(tempfile.gettempdir(), f"content_report_{date_str}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    summary = (
        f"📊 <b>Еженедельный контент-отчёт</b> — {datetime.now().strftime('%d.%m.%Y')}\n\n"
        f"📹 Видео: {len(videos)}  |  🔥 боль-спрос: {len(pain_videos)}\n"
        f"📰 Новости: {len(news)}  |  🔥 боль-спрос: {len(pain_news)}\n\n"
        f"Топ-3 заголовка этой недели:\n"
    )
    top3 = (pain_videos + pain_news)[:3]
    for i, item in enumerate(top3, 1):
        summary += f"{i}. {item.get('title', '')[:60]}\n"
    summary += "\n⬇️ Полный отчёт с источниками и сценариями — в файле ниже"

    send_message(summary)
    ok = send_document(report_path, caption=f"Полный отчёт {date_str}")
    if ok:
        print("Отчёт отправлен в Telegram.")
    else:
        print("Ошибка отправки файла.")


if __name__ == "__main__":
    main()
