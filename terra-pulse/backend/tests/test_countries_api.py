"""Tests for GET /api/v1/countries and GET /api/v1/countries/{iso3}."""
import json
import pytest
import fakeredis.aioredis
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from app.main import app
from tests.conftest import SAMPLE_COUNTRIES


@pytest.fixture
def fresh_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def redis_with_countries(fresh_redis):
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        fresh_redis.setex("countries:parsed", 3600, json.dumps(SAMPLE_COUNTRIES))
    )
    loop.close()
    return fresh_redis


class TestGetAllCountries:

    @pytest.mark.asyncio
    async def test_returns_200_from_cache(self, redis_with_countries):
        import app.api.v1.countries as countries_module
        original = countries_module.get_redis
        countries_module.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/countries")
            assert response.status_code == 200
        finally:
            countries_module.get_redis = original

    @pytest.mark.asyncio
    async def test_cached_countries_returns_list(self, redis_with_countries):
        import app.api.v1.countries as countries_module
        original = countries_module.get_redis
        countries_module.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/countries")
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
        finally:
            countries_module.get_redis = original

    @pytest.mark.asyncio
    async def test_cached_country_has_required_fields(self, redis_with_countries):
        import app.api.v1.countries as countries_module
        original = countries_module.get_redis
        countries_module.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/countries")
            data = response.json()
            country = data[0]
            assert "iso3" in country
            assert "name" in country
            assert "region" in country
        finally:
            countries_module.get_redis = original


class TestGetCountryByIso3:

    @pytest.mark.asyncio
    async def test_returns_200_for_existing_country(self, redis_with_countries):
        import app.api.v1.countries as countries_module
        original = countries_module.get_redis
        countries_module.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/countries/DEU")
            assert response.status_code == 200
        finally:
            countries_module.get_redis = original

    @pytest.mark.asyncio
    async def test_returns_correct_country_data(self, redis_with_countries):
        import app.api.v1.countries as countries_module
        original = countries_module.get_redis
        countries_module.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/countries/DEU")
            data = response.json()
            assert data["iso3"] == "DEU"
            assert data["name"] == "Germany"
        finally:
            countries_module.get_redis = original

    @pytest.mark.asyncio
    async def test_iso3_lookup_is_case_insensitive(self, redis_with_countries):
        import app.api.v1.countries as countries_module
        original = countries_module.get_redis
        countries_module.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp_upper = await client.get("/api/v1/countries/DEU")
                resp_lower = await client.get("/api/v1/countries/deu")
            assert resp_upper.status_code == 200
            assert resp_lower.status_code == 200
        finally:
            countries_module.get_redis = original

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_country(self, redis_with_countries):
        import app.api.v1.countries as countries_module
        original = countries_module.get_redis
        countries_module.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/countries/ZZZ")
            assert response.status_code == 404
        finally:
            countries_module.get_redis = original

    @pytest.mark.asyncio
    async def test_404_response_has_detail(self, redis_with_countries):
        import app.api.v1.countries as countries_module
        original = countries_module.get_redis
        countries_module.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/countries/ZZZ")
            assert "detail" in response.json()
        finally:
            countries_module.get_redis = original
