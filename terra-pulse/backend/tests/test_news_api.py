"""Tests for GET /api/v1/news/{iso3}."""
import json
import pytest
import fakeredis.aioredis
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import SAMPLE_COUNTRIES, SAMPLE_NEWS


@pytest.fixture
def fresh_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def redis_with_news_cache(fresh_redis):
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(fresh_redis.setex("countries:parsed", 3600, json.dumps(SAMPLE_COUNTRIES)))
    loop.run_until_complete(fresh_redis.setex("news:DEU", 900, json.dumps(SAMPLE_NEWS)))
    loop.close()
    return fresh_redis


@pytest.fixture
def redis_with_countries_no_news(fresh_redis):
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(fresh_redis.setex("countries:parsed", 3600, json.dumps(SAMPLE_COUNTRIES)))
    loop.close()
    return fresh_redis


class TestGetNews:

    @pytest.mark.asyncio
    async def test_returns_200_from_cache(self, redis_with_news_cache):
        import app.api.v1.news as news_module
        original = news_module.get_redis
        news_module.get_redis = lambda: redis_with_news_cache
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/news/DEU")
            assert response.status_code == 200
        finally:
            news_module.get_redis = original

    @pytest.mark.asyncio
    async def test_cached_news_returns_list(self, redis_with_news_cache):
        import app.api.v1.news as news_module
        original = news_module.get_redis
        news_module.get_redis = lambda: redis_with_news_cache
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/news/DEU")
            data = response.json()
            assert isinstance(data, list)
        finally:
            news_module.get_redis = original

    @pytest.mark.asyncio
    async def test_limit_parameter_respected(self, redis_with_news_cache):
        import app.api.v1.news as news_module
        # Add multiple articles
        many_news = [{"id": str(i), "title": f"Article {i}"} for i in range(15)]
        await redis_with_news_cache.setex("news:DEU", 900, json.dumps(many_news))
        original = news_module.get_redis
        news_module.get_redis = lambda: redis_with_news_cache
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/news/DEU?limit=5")
            data = response.json()
            assert len(data) <= 5
        finally:
            news_module.get_redis = original

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_country(self, redis_with_countries_no_news):
        import app.api.v1.news as news_module
        original = news_module.get_redis
        news_module.get_redis = lambda: redis_with_countries_no_news
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/news/ZZZ")
            assert response.status_code == 404
        finally:
            news_module.get_redis = original

    @pytest.mark.asyncio
    async def test_returns_503_when_no_countries_data(self, fresh_redis):
        """503 when Redis has no countries:parsed key."""
        import app.api.v1.news as news_module
        original = news_module.get_redis
        news_module.get_redis = lambda: fresh_redis
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/news/DEU")
            assert response.status_code == 503
        finally:
            news_module.get_redis = original

    @pytest.mark.asyncio
    async def test_news_article_has_required_fields(self, redis_with_news_cache):
        import app.api.v1.news as news_module
        original = news_module.get_redis
        news_module.get_redis = lambda: redis_with_news_cache
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/news/DEU")
            articles = response.json()
            if articles:
                article = articles[0]
                assert "title" in article
                assert "sentiment" in article
        finally:
            news_module.get_redis = original
