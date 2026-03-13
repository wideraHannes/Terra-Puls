"""Tests for GET /api/v1/pulse and GET /api/v1/pulse/{iso3}."""
import json
import pytest
import fakeredis.aioredis
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import SAMPLE_COUNTRIES, SAMPLE_PULSE_ALL


@pytest.fixture
def fresh_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def redis_with_pulse(fresh_redis):
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        fresh_redis.setex("pulse:all", 300, json.dumps(SAMPLE_PULSE_ALL))
    )
    loop.close()
    return fresh_redis


@pytest.fixture
def redis_with_pulse_and_countries(fresh_redis):
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(fresh_redis.setex("pulse:all", 300, json.dumps(SAMPLE_PULSE_ALL)))
    loop.run_until_complete(fresh_redis.setex("countries:parsed", 3600, json.dumps(SAMPLE_COUNTRIES)))
    deu_pulse = SAMPLE_PULSE_ALL["DEU"]
    loop.run_until_complete(fresh_redis.setex("pulse:DEU", 900, json.dumps(deu_pulse)))
    loop.close()
    return fresh_redis


class TestGetAllPulse:

    @pytest.mark.asyncio
    async def test_returns_200_with_cached_data(self, redis_with_pulse):
        import app.api.v1.pulse as pulse_module
        original = pulse_module.get_redis
        pulse_module.get_redis = lambda: redis_with_pulse
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/pulse")
            assert response.status_code == 200
        finally:
            pulse_module.get_redis = original

    @pytest.mark.asyncio
    async def test_returns_dict_of_iso3_scores(self, redis_with_pulse):
        import app.api.v1.pulse as pulse_module
        original = pulse_module.get_redis
        pulse_module.get_redis = lambda: redis_with_pulse
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/pulse")
            data = response.json()
            assert isinstance(data, dict)
            assert "DEU" in data
            assert "USA" in data
        finally:
            pulse_module.get_redis = original

    @pytest.mark.asyncio
    async def test_pulse_entry_has_required_fields(self, redis_with_pulse):
        import app.api.v1.pulse as pulse_module
        original = pulse_module.get_redis
        pulse_module.get_redis = lambda: redis_with_pulse
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/pulse")
            data = response.json()
            deu = data["DEU"]
            assert "composite_score" in deu
            assert "sentiment_score" in deu
            assert "conflict_score" in deu
            assert "trend" in deu
        finally:
            pulse_module.get_redis = original

    @pytest.mark.asyncio
    async def test_composite_score_in_valid_range(self, redis_with_pulse):
        import app.api.v1.pulse as pulse_module
        original = pulse_module.get_redis
        pulse_module.get_redis = lambda: redis_with_pulse
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/pulse")
            data = response.json()
            for iso3, pulse in data.items():
                assert 0.0 <= pulse["composite_score"] <= 1.0
        finally:
            pulse_module.get_redis = original


class TestGetPulseByIso3:

    @pytest.mark.asyncio
    async def test_returns_200_from_cache(self, redis_with_pulse_and_countries):
        import app.api.v1.pulse as pulse_module
        original = pulse_module.get_redis
        pulse_module.get_redis = lambda: redis_with_pulse_and_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/pulse/DEU")
            assert response.status_code == 200
        finally:
            pulse_module.get_redis = original

    @pytest.mark.asyncio
    async def test_returns_correct_iso3(self, redis_with_pulse_and_countries):
        import app.api.v1.pulse as pulse_module
        original = pulse_module.get_redis
        pulse_module.get_redis = lambda: redis_with_pulse_and_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/pulse/DEU")
            data = response.json()
            assert data["iso3"] == "DEU"
        finally:
            pulse_module.get_redis = original

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_country(self, redis_with_pulse_and_countries):
        import app.api.v1.pulse as pulse_module
        original = pulse_module.get_redis
        pulse_module.get_redis = lambda: redis_with_pulse_and_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/pulse/ZZZ")
            assert response.status_code == 404
        finally:
            pulse_module.get_redis = original
