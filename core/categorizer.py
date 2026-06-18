import json
import os

_REF = os.path.join(os.path.dirname(__file__), "..", "references")


def _load(filename):
    with open(os.path.join(_REF, filename), encoding="utf-8") as f:
        return json.load(f)


def _match_keywords(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(kw.lower() in text for kw in keywords)


def detect_axes(title: str) -> list[str]:
    data = _load("macro_axes.json")
    matched = []
    for axis in data["macro_axes"]:
        kws = axis["keywords_ru"] + axis["keywords_en"]
        if _match_keywords(title, kws):
            matched.append(axis["id"])
    return matched or ["other"]


def detect_segment(title: str) -> list[str]:
    data = _load("audience_segments.json")
    matched = []
    for seg in data["segments"]:
        if _match_keywords(title, seg["keywords"]):
            matched.append(seg["id"])
    return matched or ["general"]


def is_pain_demand(title: str) -> bool:
    pain_signals = [
        "почему", "как", "ошибка", "боль", "страх", "проблема", "не могу",
        "помогает", "избавиться", "устала", "тревог", "стресс", "панич",
        "why", "how", "mistake", "pain", "fear", "anxiety", "stress", "help",
        "problem", "can't", "stop", "relief"
    ]
    return _match_keywords(title, pain_signals)


def categorize(item: dict) -> dict:
    title = item.get("title", "")
    item["axes"] = detect_axes(title)
    item["segments"] = detect_segment(title)
    item["is_pain_demand"] = is_pain_demand(title)
    if item["is_pain_demand"]:
        item["score"] = item.get("score", 0) * 1.5
    return item


def categorize_all(items: list[dict]) -> list[dict]:
    return [categorize(item) for item in items]
