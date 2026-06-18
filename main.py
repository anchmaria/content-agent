from delivery.telegram import send_message


def main():
    ok = send_message("✅ Content-agent на связи. Фаза 1 пройдена.")
    if ok:
        print("Сообщение отправлено в Telegram.")
    else:
        print("Не удалось отправить сообщение. Проверь токен и chat_id в файле .env")


if __name__ == "__main__":
    main()
