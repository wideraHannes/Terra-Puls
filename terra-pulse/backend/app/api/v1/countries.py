import json
from fastapi import APIRouter, HTTPException
import redis.asyncio as aioredis
from app.config import settings
from app.services.rest_countries import fetch_all_countries, parse_country

router = APIRouter()


async def get_redis():
    return await aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("")
async def get_countries():
    r = await get_redis()
    cached = await r.get("countries:parsed")
    if cached:
        return json.loads(cached)

    raw = await fetch_all_countries()
    countries = [parse_country(c) for c in raw]
    await r.setex("countries:parsed", 7 * 24 * 3600, json.dumps(countries))
    return countries


@router.get("/{iso3}")
async def get_country(iso3: str):
    r = await get_redis()
    cached = await r.get("countries:parsed")
    if cached:
        countries = json.loads(cached)
        for c in countries:
            if c["iso3"] == iso3.upper():
                return c
    raise HTTPException(status_code=404, detail="Country not found")
