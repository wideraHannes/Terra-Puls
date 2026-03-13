import json
from fastapi import APIRouter, HTTPException
import redis.asyncio as aioredis
from app.config import settings
from app.services.rest_countries import fetch_all_countries, parse_country
from app.services.worldnews import fetch_news_for_country, extract_sentiment
from app.services.gdelt import fetch_gdelt_tone
from app.scoring.pulse_engine import PulseInput, compute_pulse

router = APIRouter()


async def get_redis():
    return await aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("")
async def get_all_pulse():
    r = await get_redis()
    cached = await r.get("pulse:all")
    if cached:
        return json.loads(cached)

    # If no cached data, return placeholder scores
    # In production, Celery would have populated this
    countries_cached = await r.get("countries:parsed")
    if not countries_cached:
        raw = await fetch_all_countries()
        countries = [parse_country(c) for c in raw]
        await r.setex("countries:parsed", 7 * 24 * 3600, json.dumps(countries))
    else:
        countries = json.loads(countries_cached)

    # Return neutral scores as placeholder
    result = {}
    for c in countries:
        if c["iso3"]:
            result[c["iso3"]] = {
                "iso3": c["iso3"],
                "composite_score": 0.5,
                "sentiment_score": 0.5,
                "conflict_score": 0.5,
                "trend": "stable",
            }

    await r.setex("pulse:all", 300, json.dumps(result))
    return result


@router.get("/{iso3}")
async def get_pulse(iso3: str):
    iso3 = iso3.upper()
    r = await get_redis()

    cached = await r.get(f"pulse:{iso3}")
    if cached:
        return json.loads(cached)

    # Compute on demand
    countries_cached = await r.get("countries:parsed")
    if countries_cached:
        countries = json.loads(countries_cached)
        country = next((c for c in countries if c["iso3"] == iso3), None)
    else:
        country = None

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    articles = await fetch_news_for_country(country["iso2"], limit=10)
    wn_sentiment = extract_sentiment(articles) if articles else None
    gdelt_data = await fetch_gdelt_tone(country["name"])

    pulse_input = PulseInput(
        worldnews_sentiment=wn_sentiment,
        gdelt_tone=gdelt_data["tone"],
        gdelt_volume=gdelt_data["volume"],
    )
    result = compute_pulse(pulse_input)

    data = {
        "iso3": iso3,
        "composite_score": result.composite_score,
        "sentiment_score": result.sentiment_score,
        "conflict_score": result.conflict_score,
        "trend": result.trend,
        "name": country["name"],
    }

    await r.setex(f"pulse:{iso3}", 900, json.dumps(data))
    return data
