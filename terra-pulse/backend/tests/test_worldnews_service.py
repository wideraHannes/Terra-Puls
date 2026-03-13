"""Tests for app/services/worldnews.py."""
import pytest
import respx
import httpx
from unittest.mock import patch
from app.services.worldnews import extract_sentiment, fetch_news_for_country, WORLDNEWS_URL


class TestExtractSentiment:

    def test_empty_list_returns_neutral(self):
        assert extract_sentiment([]) == pytest.approx(0.5)

    def test_positive_sentiment_maps_above_half(self):
        # sentiment=1.0 → (1.0 + 1) / 2 = 1.0
        result = extract_sentiment([{"sentiment": 1.0}])
        assert result == pytest.approx(1.0)

    def test_negative_sentiment_maps_below_half(self):
        # sentiment=-1.0 → (-1.0 + 1) / 2 = 0.0
        result = extract_sentiment([{"sentiment": -1.0}])
        assert result == pytest.approx(0.0)

    def test_zero_sentiment_maps_to_half(self):
        # sentiment=0.0 → (0.0 + 1) / 2 = 0.5
        result = extract_sentiment([{"sentiment": 0.0}])
        assert result == pytest.approx(0.5)

    def test_average_of_multiple_articles(self):
        # avg of [1.0, -1.0] = 0.0 → 0.5
        result = extract_sentiment([{"sentiment": 1.0}, {"sentiment": -1.0}])
        assert result == pytest.approx(0.5)

    def test_articles_without_sentiment_ignored(self):
        # Only article with sentiment=1.0 counted
        result = extract_sentiment([{"sentiment": 1.0}, {"title": "no sentiment"}])
        assert result == pytest.approx(1.0)

    def test_all_articles_without_sentiment_returns_neutral(self):
        result = extract_sentiment([{"title": "a"}, {"title": "b"}])
        assert result == pytest.approx(0.5)

    def test_output_is_in_0_to_1_range(self):
        for s in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            result = extract_sentiment([{"sentiment": s}])
            assert 0.0 <= result <= 1.0


class TestFetchNewsForCountry:

    @pytest.mark.asyncio
    async def test_no_api_key_returns_empty_list(self):
        with patch("app.services.worldnews.settings") as mock_settings:
            mock_settings.WORLDNEWS_API_KEY = ""
            result = await fetch_news_for_country("DE")
        assert result == []

    @pytest.mark.asyncio
    async def test_successful_fetch_returns_news_list(self):
        mock_news = [{"id": 1, "title": "Test", "sentiment": 0.5}]
        with patch("app.services.worldnews.settings") as mock_settings:
            mock_settings.WORLDNEWS_API_KEY = "test-key"
            with respx.mock:
                respx.get(WORLDNEWS_URL).mock(
                    return_value=httpx.Response(200, json={"news": mock_news})
                )
                result = await fetch_news_for_country("DE", limit=10)
        assert result == mock_news

    @pytest.mark.asyncio
    async def test_network_error_returns_empty_list(self):
        with patch("app.services.worldnews.settings") as mock_settings:
            mock_settings.WORLDNEWS_API_KEY = "test-key"
            with respx.mock:
                respx.get(WORLDNEWS_URL).mock(side_effect=httpx.ConnectError("refused"))
                result = await fetch_news_for_country("DE")
        assert result == []

    @pytest.mark.asyncio
    async def test_http_error_returns_empty_list(self):
        with patch("app.services.worldnews.settings") as mock_settings:
            mock_settings.WORLDNEWS_API_KEY = "test-key"
            with respx.mock:
                respx.get(WORLDNEWS_URL).mock(return_value=httpx.Response(401))
                result = await fetch_news_for_country("DE")
        assert result == []

    @pytest.mark.asyncio
    async def test_empty_news_response_returns_empty_list(self):
        with patch("app.services.worldnews.settings") as mock_settings:
            mock_settings.WORLDNEWS_API_KEY = "test-key"
            with respx.mock:
                respx.get(WORLDNEWS_URL).mock(return_value=httpx.Response(200, json={"news": []}))
                result = await fetch_news_for_country("DE")
        assert result == []
