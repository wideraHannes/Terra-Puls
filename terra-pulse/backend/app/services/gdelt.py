import httpx
from typing import Any

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


async def fetch_gdelt_tone(country_name: str) -> dict[str, Any]:
    """Fetch GDELT article tone for a country."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                GDELT_URL,
                params={
                    "query": f'"{country_name}" sourcelang:english',
                    "mode": "artlist",
                    "maxrecords": "25",
                    "timespan": "1d",
                    "format": "json",
                },
            )
            if response.status_code != 200:
                return {"tone": 0.0, "volume": 0}
            data = response.json()
            articles = data.get("articles", [])
            if not articles:
                return {"tone": 0.0, "volume": 0}

            tones = []
            for a in articles:
                tone_str = a.get("tone", "")
                if tone_str:
                    try:
                        tones.append(float(tone_str.split(",")[0]))
                    except (ValueError, IndexError):
                        pass

            avg_tone = sum(tones) / len(tones) if tones else 0.0
            # GDELT tone is -100 to +100, map to 0..1
            normalized = (avg_tone + 100) / 200
            return {"tone": normalized, "volume": len(articles)}
        except Exception:
            return {"tone": 0.5, "volume": 0}
