"""Check which external APIs are reachable and usable."""
import httpx
from app.config import settings


async def check_worldnews() -> dict:
    if not settings.WORLDNEWS_API_KEY:
        return {"ok": False, "reason": "no API key configured"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                "https://api.worldnewsapi.com/search-news",
                params={"source-country": "us", "number": 1, "api-key": settings.WORLDNEWS_API_KEY},
            )
        if r.status_code == 200:
            return {"ok": True}
        if r.status_code == 402:
            return {"ok": False, "reason": "daily quota exceeded (402)"}
        return {"ok": False, "reason": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


async def check_gdelt() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                "https://api.gdeltproject.org/api/v2/doc/doc",
                params={"query": "world", "mode": "artlist", "maxrecords": "1", "format": "json"},
            )
        return {"ok": r.status_code == 200}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


async def check_rest_countries() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                "https://restcountries.com/v3.1/alpha/DEU",
                params={"fields": "name"},
            )
        return {"ok": r.status_code == 200}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


async def get_api_status() -> dict:
    worldnews, gdelt, rest_countries = await __import__("asyncio").gather(
        check_worldnews(), check_gdelt(), check_rest_countries()
    )
    return {
        "worldnews": worldnews,
        "gdelt": gdelt,
        "rest_countries": rest_countries,
    }
