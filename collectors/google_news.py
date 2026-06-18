import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

QUERIES = {
    "ru": [
        "фэн-шуй", "астрология", "биоэнергетика", "китайская метафизика",
        "астрономия новости", "затмение", "инновации", "научное открытие",
        "ретроград меркурий", "гороскоп",
        "тревожность", "тревога и стресс", "панические атаки лечение",
    ],
    "en": [
        "feng shui", "astrology trends", "bioenergetics", "chinese metaphysics",
        "astronomy news", "space discovery", "eclipse", "innovation breakthrough",
        "mercury retrograde", "horoscope",
        "anxiety epidemic", "anxiety healing", "mental health anxiety",
    ],
    "es": ["feng shui consejos", "astrología", "astronomía", "innovación tecnológica", "ansiedad solución"],
    "zh": ["风水", "占星", "天文", "创新", "焦虑"],
    "de": ["Feng Shui", "Astrologie", "Astronomie", "Innovation Durchbruch", "Angststörung"],
}

BASE_URL = "https://news.google.com/rss/search?q={query}&hl={lang}&gl={country}&ceid={ceid}"

LANG_PARAMS = {
    "ru": ("ru", "RU", "RU:ru"),
    "en": ("en", "US", "US:en"),
    "es": ("es", "ES", "ES:es"),
    "zh": ("zh-CN", "CN", "CN:zh-Hans"),
    "de": ("de", "DE", "DE:de"),
}


def _parse_date(pub: str):
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(pub)
    except Exception:
        return None


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
            source = item.findtext("source", "")
            pub_dt = _parse_date(pub)
            if pub_dt and pub_dt < week_ago:
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
