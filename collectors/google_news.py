import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

QUERIES = {
    "ru": [
        "фэн-шуй", "астрология", "биоэнергетика", "китайская метафизика",
        "затмение", "ретроград меркурий", "гороскоп",
        "тревожность", "тревога и стресс", "панические атаки",
        "астрономия открытие", "научное открытие", "инновации технологии",
    ],
    "en": [
        "feng shui", "astrology trends", "chinese metaphysics",
        "mercury retrograde", "horoscope", "eclipse astronomy",
        "anxiety healing", "mental health anxiety",
        "space discovery", "innovation breakthrough",
    ],
    "es": ["feng shui", "astrología", "ansiedad solución", "astronomía descubrimiento"],
    "zh": ["风水", "占星", "天文发现", "焦虑"],
    "de": ["Feng Shui", "Astrologie", "Angststörung", "Astronomie Entdeckung"],
}

BASE_URL = "https://news.google.com/rss/search?q={query}&hl={lang}&gl={country}&ceid={ceid}"

LANG_PARAMS = {
    "ru": ("ru", "RU", "RU:ru"),
    "en": ("en", "US", "US:en"),
    "es": ("es", "ES", "ES:es"),
    "zh": ("zh-CN", "CN", "CN:zh-Hans"),
    "de": ("de", "DE", "DE:de"),
}

BLOCKED_SOURCES = {
    "vietnam.vn", "vietnamplus.vn", "mtv.ru", "мтв.онлайн",
    "kp.ru", "aif.ru", "mk.ru",  # tabloids with low niche relevance
}

NICHE_KEYWORDS = [
    # фэн-шуй
    "фэн-шуй", "фэншуй", "feng shui", "фэн шуй",
    # метафизика / астрология
    "астролог", "гороскоп", "ретроград", "меркурий", "затмение",
    "astrology", "horoscope", "retrograde", "eclipse", "mercury",
    "astrología", "占星", "Astrologie",
    # биоэнергетика / метафизика
    "биоэнергетик", "метафизик", "энергетик", "чакр", "медитац",
    "chinese metaphysics", "bioenergetics", "风水",
    # астрономия / космос
    "астроном", "космос", "звезда", "галактик", "планет", "nasa", "webb",
    "astronomy", "space", "galaxy", "planet", "star", "cosmos",
    "Astronomie", "astronomía", "天文",
    # инновации
    "инновац", "технолог", "искусственный интеллект", "ии ", "нейросет",
    "innovation", "breakthrough", "ai ", "artificial intelligence",
    # тревожность (постоянная боль)
    "тревог", "тревожн", "паник", "стресс", "депрессия", "выгорани",
    "anxiety", "panic", "stress", "burnout", "depression", "mental health",
    "ansiedad", "Angst", "焦虑",
]


def _parse_date(pub: str):
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(pub)
    except Exception:
        return None


def _is_niche_relevant(title: str) -> bool:
    t = title.lower()
    return any(kw.lower() in t for kw in NICHE_KEYWORDS)


def _is_blocked_source(source: str) -> bool:
    s = source.lower()
    return any(blocked in s for blocked in BLOCKED_SOURCES)


def fetch_feed(query: str, lang: str) -> list[dict]:
    from datetime import datetime, timedelta, timezone
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    hl, gl, ceid = LANG_PARAMS[lang]
    query_with_date = f"{query} when:7d"
    url = BASE_URL.format(query=quote(query_with_date), lang=hl, country=gl, ceid=ceid)
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:10]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub = item.findtext("pubDate", "")
            source = item.findtext("source", "") or ""
            pub_dt = _parse_date(pub)
            if pub_dt and pub_dt < week_ago:
                continue
            if _is_blocked_source(source):
                continue
            if not _is_niche_relevant(title):
                continue
            items.append({"title": title, "url": link, "published": pub,
                          "source": source, "query": query, "lang": lang})
        return items
    except Exception as e:
        print(f"Google News error [{lang}] {query}: {e}")
        return []


def collect() -> list[dict]:
    all_items = []
    seen = set()
    for lang, queries in QUERIES.items():
        for query in queries:
            items = fetch_feed(query, lang)
            for item in items:
                if item["title"] not in seen:
                    seen.add(item["title"])
                    all_items.append(item)
    return all_items
