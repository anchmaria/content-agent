from delivery.telegram import send_message
from collectors.youtube import collect as collect_youtube
from collectors.google_news import collect as collect_news


def main():
    print("Собираю видео с YouTube...")
    videos = collect_youtube(max_per_query=5)
    print(f"Найдено видео: {len(videos)}")

    print("Собираю новости из Google News...")
    news = collect_news()
    print(f"Найдено новостей: {len(news)}")
    for n in news[:3]:
        print(f"  [{n['lang']}] {n['title'][:70]}")

    msg = (
        f"✅ Сбор данных завершён.\n"
        f"📹 YouTube: {len(videos)} видео\n"
        f"📰 Google News: {len(news)} новостей\n\n"
        f"Топ видео: {videos[0]['title'][:60] if videos else '—'}\n"
        f"Топ новость: {news[0]['title'][:60] if news else '—'}"
    )
    ok = send_message(msg)
    if ok:
        print("Сообщение отправлено в Telegram.")
    else:
        print("Ошибка отправки в Telegram.")


if __name__ == "__main__":
    main()
