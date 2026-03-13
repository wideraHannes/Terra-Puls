import httpx
from typing import Any
from app.config import settings

WORLDNEWS_URL = "https://api.worldnewsapi.com/search-news"


async def fetch_news_for_country(iso2: str, limit: int = 10) -> list[dict[str, Any]]:
    if not settings.WORLDNEWS_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                WORLDNEWS_URL,
                params={
                    "source-country": iso2.lower(),
                    "number": limit,
                    "sort": "publish-time",
                    "sort-direction": "DESC",
                    "api-key": settings.WORLDNEWS_API_KEY,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("news", [])
        except Exception:
            return []


def extract_sentiment(articles: list[dict]) -> float:
    """Extract average sentiment from articles. Returns 0.5 if no data."""
    sentiments = [a.get("sentiment", 0) for a in articles if a.get("sentiment") is not None]
    if not sentiments:
        return 0.5
    avg = sum(sentiments) / len(sentiments)
    # Map from -1..1 to 0..1
    return (avg + 1) / 2
