import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

QUERIES = {
    "ru": ["фэн-шуй", "астрология", "биоэнергетика", "китайская метафизика"],
    "en": ["feng shui", "astrology trends", "bioenergetics", "chinese metaphysics"],
    "es": ["feng shui consejos", "astrología"],
    "zh": ["风水", "占星"],
    "de": ["Feng Shui", "Astrologie"],
}

BASE_URL = "https://news.google.com/rss/search?q={query}&hl={lang}&gl={country}&ceid={ceid}"

LANG_PARAMS = {
    "ru": ("ru", "RU", "RU:ru"),
    "en": ("en", "US", "US:en"),
    "es": ("es", "ES", "ES:es"),
    "zh": ("zh-CN", "CN", "CN:zh-Hans"),
    "de": ("de", "DE", "DE:de"),
}


def fetch_feed(query: str, lang: str) -> list[dict]:
    hl, gl, ceid = LANG_PARAMS[lang]
    url = BASE_URL.format(query=quote(query), lang=hl, country=gl, ceid=ceid)
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:5]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub = item.findtext("pubDate", "")
            source = item.findtext("source", "")
            items.append({"title": title, "link": link, "published": pub,
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
