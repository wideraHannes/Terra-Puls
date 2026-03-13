import asyncio
import json
import redis as redis_sync
import redis.asyncio as aioredis
from app.config import settings
from app.services.worldnews import fetch_news_for_country, extract_sentiment
from app.services.gdelt import fetch_gdelt_tone
from app.services.rest_countries import fetch_all_countries, parse_country
from app.scoring.pulse_engine import PulseInput, compute_pulse
from app.tasks.celery_app import celery_app


def get_redis_sync():
    return redis_sync.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis_async():
    return await aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@celery_app.task(name="app.tasks.fetch_pulse.fetch_all_pulse")
def fetch_all_pulse():
    asyncio.run(_fetch_all_pulse_async())


async def fetch_pulse_for_country(country: dict, semaphore: asyncio.Semaphore) -> dict | None:
    """Fetch and compute pulse for a single country with concurrency control."""
    iso3 = country["iso3"]
    iso2 = country["iso2"]
    name = country["name"]

    if not iso3 or not iso2:
        return None

    async with semaphore:
        try:
            articles = await fetch_news_for_country(iso2, limit=10)
            wn_sentiment = extract_sentiment(articles) if articles else None
            gdelt_data = await fetch_gdelt_tone(name)

            pulse_input = PulseInput(
                worldnews_sentiment=wn_sentiment,
                gdelt_tone=gdelt_data["tone"],
                gdelt_volume=gdelt_data["volume"],
            )
            result = compute_pulse(pulse_input)

            return {
                "iso3": iso3,
                "composite_score": result.composite_score,
                "sentiment_score": result.sentiment_score,
                "conflict_score": result.conflict_score,
                "trend": result.trend,
            }
        except Exception as e:
            print(f"Error processing {iso3}: {e}")
            return None


async def _fetch_all_pulse_async(max_countries: int = 177):
    """Fetch pulse for all countries concurrently (max 5 parallel GDELT requests)."""
    r = get_redis_sync()

    cached = r.get("countries:all")
    if cached:
        raw_countries = json.loads(cached)
    else:
        raw_countries = await fetch_all_countries()
        r.setex("countries:all", 7 * 24 * 3600, json.dumps(raw_countries))

    countries = [parse_country(c) for c in raw_countries][:max_countries]

    # Load existing pulse scores so we can merge (partial updates)
    existing_raw = r.get("pulse:all")
    pulse_all: dict = json.loads(existing_raw) if existing_raw else {}

    semaphore = asyncio.Semaphore(5)  # max 5 concurrent GDELT requests
    tasks = [fetch_pulse_for_country(c, semaphore) for c in countries]
    results = await asyncio.gather(*tasks)

    for result in results:
        if result:
            iso3 = result["iso3"]
            pulse_all[iso3] = result
            r.setex(f"pulse:{iso3}", 900, json.dumps(result))

    r.setex("pulse:all", 900, json.dumps(pulse_all))
    print(f"Cached pulse scores for {len(pulse_all)} countries")
    return pulse_all


async def fetch_pulse_startup(max_countries: int = 177):
    """Called from FastAPI lifespan — runs fetch in background without blocking startup."""
    await _fetch_all_pulse_async(max_countries=max_countries)
