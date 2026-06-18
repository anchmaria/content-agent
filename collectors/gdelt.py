import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

QUERIES = [
    # Фэн-шуй и метафизика
    "feng shui", "chinese metaphysics", "bagua",
    # Астрология
    "astrology", "mercury retrograde", "lunar eclipse", "solar eclipse",
    # Астрономия и космос
    "astronomy news", "NASA space discovery", "aurora borealis",
    # Биоэнергетика и эзотерика
    "energy healing", "bioenergetics",
    # Инновации и технологии
    "breakthrough innovation", "AI discovery", "technology breakthrough",
    # Планетарные новости
    "world crisis planetary", "global transformation",
    # Тревожность как боль аудитории
    "anxiety epidemic", "mental health crisis", "panic attacks treatment",
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
        r = requests.get(BASE_URL, params=params, timeout=8)
        if r.status_code != 200:
            return []
        articles = r.json().get("articles", [])
        return [{
            "title": a.get("title", ""),
            "url": a.get("url", ""),
            "published": a.get("seendate", ""),
            "source": a.get("domain", ""),
            "lang": a.get("language", ""),
            "query": query,
        } for a in articles]
    except Exception as e:
        print(f"GDELT error [{query}]: {e}")
        return []


def collect() -> list[dict]:
    all_items = []
    seen = set()
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_query, q): q for q in QUERIES}
        for future in as_completed(futures):
            for item in future.result():
                if item["title"] and item["title"] not in seen:
                    seen.add(item["title"])
                    all_items.append(item)
    return all_items
