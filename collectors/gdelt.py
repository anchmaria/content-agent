import requests

BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

QUERIES = [
    # Фэн-шуй и метафизика
    "feng shui", "фэн-шуй", "chinese metaphysics", "bagua", "бацзы",
    # Астрология
    "astrology", "астрология", "horoscope", "гороскоп", "astrología",
    "mercury retrograde", "ретроград меркурий", "lunar eclipse", "solar eclipse",
    "затмение", "планетарный транзит",
    # Астрономия и космос
    "astronomy news", "NASA", "space discovery", "космос новости",
    "aurora borealis", "meteor shower", "northern lights",
    # Биоэнергетика и эзотерика
    "bioenergetics", "биоэнергетика", "energy healing", "chakra",
    # Инновации и технологии
    "breakthrough innovation", "AI discovery", "technology breakthrough",
    "инновации", "научное открытие", "future technology",
    # Планетарные новости
    "global transformation", "world crisis", "planetary event",
    # Тревожность как боль аудитории
    "anxiety epidemic", "anxiety healing", "тревожность", "mental health crisis",
    "panic attacks treatment", "stress anxiety relief",
]


def fetch_query(query: str, max_records: int = 5) -> list[dict]:
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": max_records,
        "format": "json",
        "timespan": "2w",
        "sort": "hybridrel",
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        if r.status_code != 200:
            return []
        data = r.json()
        articles = data.get("articles", [])
        result = []
        for a in articles:
            result.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "published": a.get("seendate", ""),
                "source": a.get("domain", ""),
                "lang": a.get("language", ""),
                "query": query,
            })
        return result
    except Exception as e:
        print(f"GDELT error [{query}]: {e}")
        return []


def collect() -> list[dict]:
    all_items = []
    seen = set()
    for query in QUERIES:
        items = fetch_query(query, max_records=5)
        for item in items:
            if item["title"] and item["title"] not in seen:
                seen.add(item["title"])
                all_items.append(item)
    return all_items
