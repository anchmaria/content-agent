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


def _apply_formula(title: str, segment: str) -> tuple[str, str]:
    title_short = title[:60].strip()

    if "почему" in title.lower() or "why" in title.lower():
        formula = "pain_targeting"
        headline = f"Почему вы не можете избавиться от этого — даже когда стараетесь ({title_short})"
    elif any(w in title.lower() for w in ["ошибк", "mistake", "wrong"]):
        formula = "pattern_break"
        headline = f"Ошибка, которую делают все: {title_short}"
    elif any(w in title.lower() for w in ["как", "how", "способ"]):
        formula = "concrete_value"
        headline = f"3 шага, которые меняют всё: {title_short}"
    elif any(w in title.lower() for w in ["тревог", "anxiety", "stress", "стресс"]):
        formula = "pain_targeting"
        headline = f"Если тревога не отпускает — это видео для вас ({title_short})"
    elif any(w in title.lower() for w in ["фэн-шуй", "feng shui", "风水"]):
        formula = "curiosity_gap"
        headline = f"Я нашла одну вещь в квартире, которая блокирует энергию. Это не хлам ({title_short})"
    elif any(w in title.lower() for w in ["астролог", "astro", "гороскоп"]):
        formula = "discovery"
        headline = f"Мне понадобилось 5 лет, чтобы понять этот принцип в астрологии ({title_short})"
    else:
        formula = "pain_targeting"
        headline = f"Куда уходит ваша энергия, пока вы этого не знаете ({title_short})"

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
            top_items.append(("video", pain_videos[vi]))
            vi += 1
        if len(top_items) < 10 and ni < len(pain_news):
            top_items.append(("news", pain_news[ni]))
            ni += 1
        if vi >= len(pain_videos) and ni >= len(pain_news):
            break

    lines = []
    lines.append("=" * 60)
    lines.append(f"  ЕЖЕНЕДЕЛЬНЫЙ КОНТЕНТ-ОТЧЁТ")
    lines.append(f"  Сгенерировано: {now}")
    lines.append("=" * 60)
    lines.append(f"\nСобрано: {len(videos)} видео · {len(news)} новостей")
    lines.append(f"Боль-спрос: {len(pain_videos)} видео · {len(pain_news)} новостей\n")

    lines.append("=" * 60)
    lines.append("  РАЗДЕЛ 1: 10 ТЕМ-ЗАГОЛОВКОВ (боль-спрос первыми)")
    lines.append("  Готово к съёмке — с источниками и аудиторией")
    lines.append("=" * 60)

    formula_names = {
        "pain_targeting": "Попадание в боль",
        "pattern_break": "Разрыв шаблона",
        "concrete_value": "Конкретная польза",
        "curiosity_gap": "Незакрытая петля",
        "discovery": "Открытие-сюрприз",
    }

    for i, (kind, item) in enumerate(top_items[:10], 1):
        title = item.get("title", "")
        headline, formula = _apply_formula(title, (item.get("segments") or ["general"])[0])
        seg = _seg(item.get("segments"))
        axes = _axes(item.get("axes"))

        if kind == "video":
            source_type = "YouTube"
            source_url = f"https://youtube.com/watch?v={item.get('id', '')}"
            views = item.get("views", 0)
            stats = f"{views:,} просмотров · канал: {item.get('channel', '—')}"
        else:
            source_type = item.get("source", "Google News")
            source_url = item.get("url", "—")
            stats = f"Опубликовано: {item.get('published', '')[:16]}"

        lines.append(f"\n{'─' * 55}")
        lines.append(f"#{i}  🔥 ЗАГОЛОВОК (боль-спрос):")
        lines.append(f"    «{headline}»")
        lines.append(f"")
        lines.append(f"    Формула: {formula_names.get(formula, formula)}")
        lines.append(f"    Аудитория: {seg}")
        lines.append(f"    Макро-ось: {axes}")
        lines.append(f"    Источник ({source_type}): {source_url}")
        lines.append(f"    Оригинал: {title[:70]}")
        lines.append(f"    Статистика: {stats}")

    lines.append(f"\n{'=' * 60}")
    lines.append("  РАЗДЕЛ 2: ТОП-10 ВИДЕО ПО СКОРИНГУ")
    lines.append("=" * 60)

    for i, v in enumerate(videos[:10], 1):
        seg = _seg(v.get("segments"))
        pain_mark = "🔥" if v.get("is_pain_demand") else "  "
        lines.append(f"\n{pain_mark} #{i} {v.get('title', '')[:70]}")
        lines.append(f"     Просмотры: {v.get('views', 0):,}  |  Лайки: {v.get('likes', 0):,}  |  Комменты: {v.get('comments', 0):,}")
        lines.append(f"     Скор: {v.get('score', 0):.1f}  |  Аудитория: {seg}")
        lines.append(f"     Канал: {v.get('channel', '—')}")
        lines.append(f"     Ссылка: https://youtube.com/watch?v={v.get('id', '')}")

    lines.append(f"\n{'=' * 60}")
    lines.append("  РАЗДЕЛ 3: ТОП-10 НОВОСТЕЙ И ТРЕНДОВ")
    lines.append("=" * 60)

    for i, n in enumerate(news[:10], 1):
        seg = _seg(n.get("segments"))
        pain_mark = "🔥" if n.get("is_pain_demand") else "  "
        lines.append(f"\n{pain_mark} #{i} {n.get('title', '')[:70]}")
        lines.append(f"     Источник: {n.get('source', '—')}  |  Язык: {n.get('lang', '—')}")
        lines.append(f"     Аудитория: {seg}")
        lines.append(f"     Ссылка: {n.get('url') or n.get('link', '—')}")

    lines.append(f"\n{'=' * 60}")
    lines.append("  РАЗДЕЛ 4: БОЛИ АУДИТОРИИ ПО СЕГМЕНТАМ")
    lines.append("=" * 60)

    segment_items = {}
    for item in list(pain_videos) + list(pain_news):
        for seg in item.get("segments", ["general"]):
            if seg not in segment_items:
                segment_items[seg] = []
            if len(segment_items[seg]) < 5:
                segment_items[seg].append(item.get("title", "")[:70])

    for seg_id, titles in segment_items.items():
        if titles:
            lines.append(f"\n👥 {SEGMENT_LABELS.get(seg_id, seg_id).upper()}:")
            for t in titles:
                lines.append(f"   • {t}")

    lines.append(f"\n{'=' * 60}")
    lines.append("  РАЗДЕЛ 5: КАК СНИМАТЬ (памятка)")
    lines.append("=" * 60)
    hooks = hook_data.get("hook_types", [])
    lines.append(f"\nТоп-5 типов хуков по просмотрам (2026):")
    for h in hooks[:5]:
        lines.append(f"\n  [{h['type'].upper()}] {h['name']}")
        lines.append(f"  Механика: {h['mechanic']}")
        lines.append(f"  Пример: «{h['example']}»")
        lines.append(f"  Почему работает: {h['why_works']}")

    lines.append(f"\nСтруктура короткого видео 15–60 сек:")
    struct = hook_data.get("video_structure", {}).get("short_15_60s", {})
    for k, v in struct.items():
        lines.append(f"  {k.replace('_', '–')} сек: {v}")

    lines.append(f"\nАнтипаттерны (что убивает охваты):")
    for ap in hook_data.get("anti_patterns", []):
        lines.append(f"  ✗ {ap}")

    lines.append(f"\n{'=' * 60}")
    lines.append("  Конец отчёта. Content-Agent by Maria")
    lines.append("=" * 60)

    return "\n".join(lines)
