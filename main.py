from delivery.telegram import send_message
from collectors.youtube import collect as collect_youtube
from collectors.google_news import collect as collect_news
from core.scoring import rank_videos, rank_news
from core.dedup import filter_new_videos, filter_new_news, mark_seen


def main():
    print("Собираю видео с YouTube...")
    videos = collect_youtube(max_per_query=5)
    print(f"Найдено видео: {len(videos)}")

    print("Собираю новости из Google News...")
    news = collect_news()
    print(f"Найдено новостей: {len(news)}")

    # Дедупликация
    videos = filter_new_videos(videos)
    news = filter_new_news(news)
    print(f"Новых (не показанных ранее): {len(videos)} видео, {len(news)} новостей")

    # Скоринг
    videos = rank_videos(videos)
    news = rank_news(news)

    # Запоминаем показанное
    mark_seen(videos, news)

    top_video = videos[0]["title"][:60] if videos else "—"
    top_news = news[0]["title"][:60] if news else "—"

    msg = (
        f"✅ Сбор данных завершён.\n"
        f"📹 YouTube: {len(videos)} новых видео\n"
        f"📰 Google News: {len(news)} новых новостей\n\n"
        f"🏆 Топ видео: {top_video}\n"
        f"🔥 Топ новость: {top_news}"
    )
    ok = send_message(msg)
    if ok:
        print("Сообщение отправлено в Telegram.")
    else:
        print("Ошибка отправки в Telegram.")


if __name__ == "__main__":
    main()
