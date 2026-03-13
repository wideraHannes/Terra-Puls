import sys
import os
import json
import pytest
import fakeredis.aioredis
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Sample country data used across tests
SAMPLE_COUNTRIES = [
    {
        "iso3": "DEU", "iso2": "DE", "name": "Germany",
        "capital": "Berlin", "region": "Europe", "subregion": "Western Europe",
        "population": 83000000, "latitude": 51.0, "longitude": 9.0,
        "currency_code": "EUR", "flag_url": "https://example.com/de.png"
    },
    {
        "iso3": "USA", "iso2": "US", "name": "United States",
        "capital": "Washington D.C.", "region": "Americas", "subregion": "North America",
        "population": 330000000, "latitude": 38.0, "longitude": -97.0,
        "currency_code": "USD", "flag_url": "https://example.com/us.png"
    },
]

SAMPLE_PULSE_ALL = {
    "DEU": {"iso3": "DEU", "composite_score": 0.72, "sentiment_score": 0.75, "conflict_score": 0.65, "trend": "stable"},
    "USA": {"iso3": "USA", "composite_score": 0.68, "sentiment_score": 0.70, "conflict_score": 0.62, "trend": "stable"},
}

SAMPLE_NEWS = [
    {
        "id": "1", "title": "Test Article", "summary": "Summary",
        "url": "https://example.com", "sentiment": 0.7,
        "published_at": "2024-01-01", "source": "US"
    }
]


@pytest.fixture
def fake_redis():
    """Return a fresh fakeredis instance for each test."""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def fake_redis_with_countries(fake_redis):
    """Fakeredis pre-populated with country data."""
    import asyncio
    asyncio.get_event_loop().run_until_complete(
        fake_redis.setex("countries:parsed", 3600, json.dumps(SAMPLE_COUNTRIES))
    )
    return fake_redis


@pytest.fixture(autouse=True)
def mock_db_lifespan():
    """Prevent DB connection during tests by patching engine.begin and startup task."""

    @asynccontextmanager
    async def fake_begin():
        conn = AsyncMock()
        conn.run_sync = AsyncMock()
        yield conn

    # Patch engine.begin by replacing the engine object's begin method via patch.object
    import app.db.session as session_module

    fake_engine = MagicMock()
    fake_engine.begin = fake_begin

    with patch.object(session_module, "engine", fake_engine):
        with patch("app.tasks.fetch_pulse.fetch_pulse_startup", new_callable=AsyncMock):
            yield
