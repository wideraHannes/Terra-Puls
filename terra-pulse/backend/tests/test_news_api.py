"""Tests for GET /api/v1/news/{iso3}."""
import json
import pytest
import fakeredis.aioredis
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from app.main import app
from tests.conftest import SAMPLE_COUNTRIES, SAMPLE_NEWS

SAMPLE_ARTICLES = [
    {
        "id": "1", "title": "Test Article", "text": "Summary text here",
        "url": "https://example.com", "sentiment": 0.4,
        "publish_date": "2024-01-01", "source_country": "de"
    }
]


@pytest.fixture
def fresh_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
async def redis_with_countries(fresh_redis):
    await fresh_redis.setex("countries:parsed", 3600, json.dumps(SAMPLE_COUNTRIES))
    return fresh_redis


@pytest.fixture
async def redis_with_cached_news(fresh_redis):
    await fresh_redis.setex("countries:parsed", 3600, json.dumps(SAMPLE_COUNTRIES))
    await fresh_redis.setex("news:DEU", 900, json.dumps(SAMPLE_NEWS))
    return fresh_redis


def patch_redis(module, redis):
    import app.api.v1.news as m
    original = m.get_redis
    m.get_redis = lambda: redis
    return original


class TestNewsCache:

    async def test_returns_cached_articles(self, redis_with_cached_news):
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: redis_with_cached_news
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/news/DEU")
            assert r.status_code == 200
            assert isinstance(r.json(), list)
            assert len(r.json()) > 0
        finally:
            m.get_redis = orig

    async def test_empty_api_result_is_not_cached(self, redis_with_countries):
        """
        TDD: When worldnews returns [] (e.g. 402 limit hit), the empty result
        must NOT be written to Redis. Next request must try the API again.

        CURRENTLY FAILS — news.py caches [] unconditionally.
        """
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: redis_with_countries
        try:
            with patch("app.api.v1.news.fetch_news_for_country", return_value=[]):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                    await c.get("/api/v1/news/DEU")

            # The key must NOT exist — empty results should never be cached
            cached = await redis_with_countries.get("news:DEU")
            assert cached is None, (
                f"BUG: empty result was cached as '{cached}'. "
                "When the API returns nothing, we must retry next time."
            )
        finally:
            m.get_redis = orig

    async def test_non_empty_result_is_cached(self, redis_with_countries):
        """Articles fetched from worldnews must be cached for 15 min."""
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: redis_with_countries
        try:
            with patch("app.api.v1.news.fetch_news_for_country", return_value=SAMPLE_ARTICLES):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                    await c.get("/api/v1/news/DEU")

            cached = await redis_with_countries.get("news:DEU")
            assert cached is not None, "Articles from API must be cached"
            assert len(json.loads(cached)) > 0
        finally:
            m.get_redis = orig

    async def test_limit_slices_cached_results(self, redis_with_cached_news):
        many = [{"id": str(i), "title": f"A{i}", "sentiment": 0.5} for i in range(15)]
        await redis_with_cached_news.setex("news:DEU", 900, json.dumps(many))
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: redis_with_cached_news
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/news/DEU?limit=5")
            assert len(r.json()) == 5
        finally:
            m.get_redis = orig

    async def test_limit_max_enforced_at_20(self, redis_with_cached_news):
        """Query param limit is capped at 20 by FastAPI validation."""
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: redis_with_cached_news
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/news/DEU?limit=99")
            assert r.status_code == 422
        finally:
            m.get_redis = orig


class TestNewsErrors:

    async def test_unknown_country_returns_404(self, redis_with_countries):
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: redis_with_countries
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/news/ZZZ")
            assert r.status_code == 404
        finally:
            m.get_redis = orig

    async def test_no_countries_in_redis_returns_503(self, fresh_redis):
        """If country data hasn't loaded yet, return 503 not 500."""
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: fresh_redis
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/news/DEU")
            assert r.status_code == 503
        finally:
            m.get_redis = orig


class TestNewsNormalization:

    async def test_sentiment_mapped_from_minus1_to_1_range(self, redis_with_countries):
        """WorldNews sentiment -1..1 must be mapped to 0..1 before returning."""
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: redis_with_countries
        article_with_negative_sentiment = [{
            "id": "1", "title": "Bad news", "text": "...",
            "url": "https://x.com", "sentiment": -1.0,
            "publish_date": "2024-01-01", "source_country": "de"
        }]
        try:
            with patch("app.api.v1.news.fetch_news_for_country", return_value=article_with_negative_sentiment):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                    r = await c.get("/api/v1/news/DEU")
            articles = r.json()
            assert articles[0]["sentiment"] == pytest.approx(0.0), (
                "sentiment=-1.0 from WorldNews must map to 0.0"
            )
        finally:
            m.get_redis = orig

    async def test_article_schema_matches_frontend_contract(self, redis_with_countries):
        """Each article must have the fields the frontend expects."""
        import app.api.v1.news as m
        orig = m.get_redis
        m.get_redis = lambda: redis_with_countries
        try:
            with patch("app.api.v1.news.fetch_news_for_country", return_value=SAMPLE_ARTICLES):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                    r = await c.get("/api/v1/news/DEU")
            article = r.json()[0]
            for field in ("id", "title", "summary", "url", "sentiment", "published_at", "source"):
                assert field in article, f"Missing field: {field}"
        finally:
            m.get_redis = orig
