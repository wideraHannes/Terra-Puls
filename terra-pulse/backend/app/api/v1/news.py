import json
from fastapi import APIRouter, HTTPException, Query
import redis.asyncio as aioredis
from app.config import settings
from app.services.worldnews import fetch_news_for_country

router = APIRouter()


async def get_redis():
    return await aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("/{iso3}")
async def get_news(iso3: str, limit: int = Query(default=10, le=20)):
    iso3 = iso3.upper()
    r = await get_redis()

    cache_key = f"news:{iso3}"
    cached = await r.get(cache_key)
    if cached:
        articles = json.loads(cached)
        return articles[:limit]

    # Need iso2 - get from countries cache
    countries_cached = await r.get("countries:parsed")
    if countries_cached:
        countries = json.loads(countries_cached)
        country = next((c for c in countries if c["iso3"] == iso3), None)
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        iso2 = country["iso2"]
    else:
        raise HTTPException(status_code=503, detail="Country data not available yet")

    articles = await fetch_news_for_country(iso2, limit=20)

    # Normalize articles
    normalized = []
    for a in articles:
        sentiment = a.get("sentiment", 0) or 0
        normalized.append(
            {
                "id": a.get("id", ""),
                "title": a.get("title", ""),
                "summary": a.get("text", "")[:300] if a.get("text") else "",
                "url": a.get("url", ""),
                "sentiment": (sentiment + 1) / 2,  # -1..1 -> 0..1
                "published_at": a.get("publish_date", ""),
                "source": a.get("source_country", ""),
            }
        )

    await r.setex(cache_key, 900, json.dumps(normalized))
    return normalized[:limit]
