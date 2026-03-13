import httpx
from typing import Any

REST_COUNTRIES_URL = "https://restcountries.com/v3.1/all"


async def fetch_all_countries() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            REST_COUNTRIES_URL,
            params={"fields": "name,cca2,cca3,capital,region,subregion,population,latlng,currencies,flags"},
        )
        response.raise_for_status()
        return response.json()


def parse_country(raw: dict) -> dict:
    iso3 = raw.get("cca3", "")
    iso2 = raw.get("cca2", "")
    name = raw.get("name", {}).get("common", "")
    capital_list = raw.get("capital", [])
    capital = capital_list[0] if capital_list else None
    region = raw.get("region", "")
    subregion = raw.get("subregion", "")
    population = raw.get("population", 0)
    latlng = raw.get("latlng", [0, 0])
    lat = latlng[0] if len(latlng) > 0 else 0
    lng = latlng[1] if len(latlng) > 1 else 0

    currencies = raw.get("currencies", {})
    currency_code = list(currencies.keys())[0] if currencies else None

    flags = raw.get("flags", {})
    flag_url = flags.get("png", "")

    return {
        "iso3": iso3,
        "iso2": iso2,
        "name": name,
        "capital": capital,
        "region": region,
        "subregion": subregion,
        "population": population,
        "latitude": lat,
        "longitude": lng,
        "currency_code": currency_code,
        "flag_url": flag_url,
    }
