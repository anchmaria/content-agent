import json
import os
from datetime import datetime

_REF = os.path.join(os.path.dirname(__file__), "..", "references")


def _load(filename):
    with open(os.path.join(_REF, filename), encoding="utf-8") as f:
        return json.load(f)


SEGMENT_LABELS = {
    "seeker": "Ищущие смысл",
    "anxious": "Тревожные",
    "practical": "Практики",
    "ambitious": "Амбициозные",
    "skeptic": "Скептики",
    "general": "Широкая аудитория",
}

AXES_LABELS = {
    "money": "Деньги и финансы",
    "health": "Здоровье и wellness",
    "ai_future": "ИИ и будущее",
    "psychology": "Психология и отношения",
    "freedom": "Свобода и образ жизни",
    "simplicity": "Время и простота",
    "identity": "Идентичность и статус",
    "other": "Другое",
}


def _seg(segments):
    return ", ".join(SEGMENT_LABELS.get(s, s) for s in (segments or ["general"]))


def _axes(axes):
    return ", ".join(AXES_LABELS.get(a, a) for a in (axes or ["other"]))


def _trunc(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    last_space = cut.rfind(" ")
    return (cut[:last_space] if last_space > max_len * 0.7 else cut) + "..."


def _engagement_rate(v: dict) -> str:
    views = v.get("views", 0)
    if not views:
        return "—"
    er = (v.get("likes", 0) + v.get("comments", 0)) / views * 100
    return f"{er:.1f}%"


def _apply_formula(title: str) -> tuple[str, str]:
    t = title.lower()
    # Anxiety / stress — permanent pain topic
    if any(w in t for w in ["тревог", "anxiety", "паник", "стресс", "stress", "депрессия", "выгорани", "burnout", "mental health", "ansiedad", "angst", "焦虑"]):
        formula = "Попадание в боль"
        headline = "Если тревога не отпускает даже ночью — вот почему и что с этим делать"
    # Feng shui
    elif any(w in t for w in ["фэн-шуй", "фэн шуй", "фэншуй", "feng shui", "风水", "багуа", "bagua"]):
        formula = "Незакрытая петля"
        headline = "Одна вещь в квартире, которая блокирует деньги — и это не хлам"
    # Astrology / horoscope
    elif any(w in t for w in ["астролог", "гороскоп", "ретроград", "меркурий", "затмение", "horoscope", "astrology", "retrograde", "mercury", "eclipse", "astrología", "占星"]):
        formula = "Открытие-сюрприз"
        headline = "Этот астрологический период меняет всё — большинство об этом не знают"
    # Chinese metaphysics / bioenergetics
    elif any(w in t for w in ["метафизик", "биоэнергетик", "чакр", "медитац", "энергетик", "chinese metaphysics", "bioenergetics", "chakra"]):
        formula = "Попадание в боль"
        headline = "Почему энергетические практики не работают — и что делать вместо этого"
    # Money / finance
    elif any(w in t for w in ["деньг", "money", "доход", "финанс", "богатств", "wealth", "финанс"]):
        formula = "Попадание в боль"
        headline = "Куда утекают деньги даже когда вы экономите — разбор по энергиям"
    # Astronomy / space / science
    elif any(w in t for w in ["астроном", "космос", "звезда", "галактик", "планет", "nasa", "webb", "astronomy", "space", "galaxy", "planet", "astronomie", "astronomía", "天文"]):
        formula = "Открытие-сюрприз"
        headline = "Новое открытие в космосе, которое меняет представление о Вселенной"
    # Innovation / AI / tech
    elif any(w in t for w in ["инновац", "технолог", "искусственный интеллект", "нейросет", "innovation", "breakthrough", "artificial intelligence", " ai "]):
        formula = "Разрыв шаблона"
        headline = "Технология, которая уже меняет мир — а большинство ещё не заметили"
    # Energy / fatigue
    elif any(w in t for w in ["энерг", "energy", "усталост", "tired"]):
        formula = "Попадание в боль"
        headline = "Почему вы устаёте даже когда высыпаетесь"
    else:
        formula = "Попадание в боль"
        headline = "Что эксперты по метафизике никогда не делают — и вам не советуют"
    return headline, formula


def build_report(videos: list[dict], news: list[dict]) -> str:
    hook_data = _load("hook_formulas.json")
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    pain_videos = sorted(
        [v for v in videos if v.get("is_pain_demand")],
        key=lambda x: x.get("score", 0), reverse=True
    )
    pain_news = sorted(
        [n for n in news if n.get("is_pain_demand")],
        key=lambda x: x.get("score", 0), reverse=True
    )

    top_items = []
    vi, ni = 0, 0
    while len(top_items) < 10:
        if vi < len(pain_videos):
            top_items.append(("video", pain_videos[vi])); vi += 1
        if len(top_items) < 10 and ni < len(pain_news):
            top_items.append(("news", pain_news[ni])); ni += 1
        if vi >= len(pain_videos) and ni >= len(pain_news):
            break

    lines = []
    lines.append("=" * 62)
    lines.append("  ЕЖЕНЕДЕЛЬНЫЙ КОНТЕНТ-ОТЧЁТ")
    lines.append(f"  Сгенерировано: {now}")
    lines.append("=" * 62)
    lines.append(f"\nСобрано за последние 7 дней: {len(videos)} видео · {len(news)} новостей")
    lines.append(f"Боль-спрос: {len(pain_videos)} видео · {len(pain_news)} новостей\n")

    # ── РАЗДЕЛ 1: БОЛИ ИЗ КОММЕНТАРИЕВ ──────────────────────────
    lines.append("=" * 62)
    lines.append("  РАЗДЕЛ 1: РЕАЛЬНЫЕ БОЛИ АУДИТОРИИ (из комментариев)")
    lines.append("  Что люди пишут под роликами — их словами")
    lines.append("=" * 62)

    videos_with_pains = [v for v in videos if v.get("pains")]
    if videos_with_pains:
        all_pains = []
        for v in videos_with_pains[:5]:
            lines.append(f"\n🎥 {_trunc(v.get('title', ''), 70)}")
            lines.append(f"   👁 {v.get('views', 0):,} просмотров  |  ❤️ {v.get('likes', 0):,}  |  💬 {v.get('comments', 0):,}  |  ER: {_engagement_rate(v)}")
            lines.append(f"   🔗 https://youtube.com/watch?v={v.get('id', '')}")
            lines.append(f"   Аудитория: {_seg(v.get('segments'))}")
            lines.append(f"\n   Что пишут в комментариях (боли):")
            for pain in v.get("pains", [])[:5]:
                lines.append(f"   • {_trunc(pain, 120)}")
            all_pains.extend(v.get("pains", []))
    else:
        lines.append("\n  Данные комментариев будут доступны со следующего запуска")
        lines.append("  (лимит YouTube API сбрасывается каждые 24 часа)")

    # ── РАЗДЕЛ 2: 10 ЗАГОЛОВКОВ ──────────────────────────────────
    lines.append(f"\n{'=' * 62}")
    lines.append("  РАЗДЕЛ 2: 10 ТЕМ-ЗАГОЛОВКОВ (боль-спрос первыми)")
    lines.append("  Готово к съёмке — с источниками")
    lines.append("=" * 62)

    for i, (kind, item) in enumerate(top_items[:10], 1):
        title = item.get("title", "")
        headline, formula = _apply_formula(title)
        seg = _seg(item.get("segments"))
        axes = _axes(item.get("axes"))

        if kind == "video":
            source_url = f"https://youtube.com/watch?v={item.get('id', '')}"
            source_type = f"YouTube · {item.get('channel', '—')}"
            stats = (f"👁 {item.get('views', 0):,}  ❤️ {item.get('likes', 0):,}"
                     f"  💬 {item.get('comments', 0):,}  ER: {_engagement_rate(item)}")
        else:
            source_url = item.get("url") or item.get("link", "—")
            source_type = f"Google News · {item.get('source', '—')} [{item.get('lang', '')}]"
            stats = f"Опубликовано: {item.get('published', '')[:22]}"

        lines.append(f"\n{'─' * 58}")
        lines.append(f"#{i}  🔥 ЗАГОЛОВОК:")
        lines.append(f"    «{headline}»")
        lines.append(f"")
        lines.append(f"    Формула: {formula}")
        lines.append(f"    Аудитория: {seg}")
        lines.append(f"    Тема: {axes}")
        lines.append(f"    Источник: {source_type}")
        lines.append(f"    Ссылка: {source_url}")
        lines.append(f"    Оригинал: {_trunc(title, 80)}")
        lines.append(f"    Статистика: {stats}")

    # ── РАЗДЕЛ 3: ТОП ВИДЕО ──────────────────────────────────────
    lines.append(f"\n{'=' * 62}")
    lines.append("  РАЗДЕЛ 3: ТОП-10 ВИДЕО ПО ВОВЛЕЧЁННОСТИ")
    lines.append("=" * 62)

    for i, v in enumerate(videos[:10], 1):
        pain_mark = "🔥" if v.get("is_pain_demand") else "▶"
        lines.append(f"\n{pain_mark} #{i} {_trunc(v.get('title', ''), 75)}")
        lines.append(f"   👁 {v.get('views', 0):,} просмотров  ❤️ {v.get('likes', 0):,} лайков"
                     f"  💬 {v.get('comments', 0):,} комментариев  ER: {_engagement_rate(v)}")
        lines.append(f"   Канал: {v.get('channel', '—')}  |  Аудитория: {_seg(v.get('segments'))}")
        lines.append(f"   Ссылка: https://youtube.com/watch?v={v.get('id', '')}")
        if v.get("pains"):
            lines.append(f"   Боль из комментариев: {_trunc(v['pains'][0], 100)}")

    # ── РАЗДЕЛ 4: ТОП НОВОСТИ ────────────────────────────────────
    lines.append(f"\n{'=' * 62}")
    lines.append("  РАЗДЕЛ 4: ТОП-10 НОВОСТЕЙ (последние 7 дней)")
    lines.append("=" * 62)

    for i, n in enumerate(news[:10], 1):
        pain_mark = "🔥" if n.get("is_pain_demand") else "📌"
        lines.append(f"\n{pain_mark} #{i} {_trunc(n.get('title', ''), 75)}")
        lines.append(f"   Источник: {n.get('source', '—')}  |  Язык: {n.get('lang', '—')}")
        lines.append(f"   Аудитория: {_seg(n.get('segments'))}")
        lines.append(f"   Опубликовано: {n.get('published', '')[:22]}")
        url = n.get("url") or n.get("link", "—")
        lines.append(f"   Ссылка: {url}")

    # ── РАЗДЕЛ 5: БОЛИ ПО СЕГМЕНТАМ ─────────────────────────────
    lines.append(f"\n{'=' * 62}")
    lines.append("  РАЗДЕЛ 5: БОЛИ АУДИТОРИИ ПО СЕГМЕНТАМ")
    lines.append("=" * 62)

    segment_items: dict[str, list[str]] = {}
    for item in list(pain_videos) + list(pain_news):
        for seg in item.get("segments", ["general"]):
            if seg not in segment_items:
                segment_items[seg] = []
            if len(segment_items[seg]) < 5:
                segment_items[seg].append(_trunc(item.get("title", ""), 75))

    for seg_id, titles in segment_items.items():
        if titles:
            lines.append(f"\n👥 {SEGMENT_LABELS.get(seg_id, seg_id).upper()}:")
            for t in titles:
                lines.append(f"   • {t}")

    lines.append(f"\n{'=' * 62}")
    lines.append("  Конец отчёта. Content-Agent — Maria")
    lines.append("=" * 62)

    return "\n".join(lines)
