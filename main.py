from delivery.telegram import send_message
from collectors.youtube import collect as collect_youtube


def main():
    print("Собираю видео с YouTube...")
    videos = collect_youtube(max_per_query=5)
    print(f"Найдено видео: {len(videos)}")
    for v in videos[:5]:
        print(f"  [{v.get('views', 0):,}] {v['title'][:60]}")

    msg = f"✅ YouTube: найдено {len(videos)} видео по нишам.\nТоп-1: {videos[0]['title'][:80] if videos else '—'}"
    ok = send_message(msg)
    if ok:
        print("Сообщение отправлено в Telegram.")
    else:
        print("Ошибка отправки в Telegram.")


if __name__ == "__main__":
    main()
