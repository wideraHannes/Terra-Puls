"""Tests for app/services/gdelt.py — all failable assertions against real computed values."""
import pytest
import respx
import httpx
from app.services.gdelt import fetch_gdelt_tone, GDELT_URL


class TestFetchGdeltTone:

    @pytest.mark.asyncio
    async def test_empty_articles_returns_zero_tone_and_volume(self):
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": []}))
            result = await fetch_gdelt_tone("Germany")
        assert result == {"tone": 0.0, "volume": 0}

    @pytest.mark.asyncio
    async def test_positive_tone_normalised_above_half(self):
        """GDELT tone +50 → normalized = (50+100)/200 = 0.75"""
        articles = [{"tone": "50,0,0,0,0,0,0"}]
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": articles}))
            result = await fetch_gdelt_tone("Germany")
        assert result["tone"] == pytest.approx(0.75, abs=1e-4)
        assert result["volume"] == 1

    @pytest.mark.asyncio
    async def test_negative_tone_normalised_below_half(self):
        """GDELT tone -50 → normalized = (-50+100)/200 = 0.25"""
        articles = [{"tone": "-50,0,0,0,0,0,0"}]
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": articles}))
            result = await fetch_gdelt_tone("Syria")
        assert result["tone"] == pytest.approx(0.25, abs=1e-4)

    @pytest.mark.asyncio
    async def test_zero_tone_normalises_to_half(self):
        """GDELT tone 0 → normalized = 100/200 = 0.5"""
        articles = [{"tone": "0,0,0,0,0,0,0"}]
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": articles}))
            result = await fetch_gdelt_tone("France")
        assert result["tone"] == pytest.approx(0.5, abs=1e-4)

    @pytest.mark.asyncio
    async def test_volume_equals_article_count(self):
        articles = [{"tone": "10,0,0,0,0,0,0"}, {"tone": "20,0,0,0,0,0,0"}, {"tone": "30,0,0,0,0,0,0"}]
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": articles}))
            result = await fetch_gdelt_tone("Brazil")
        assert result["volume"] == 3

    @pytest.mark.asyncio
    async def test_average_tone_of_multiple_articles(self):
        """Average of +100 and -100 = 0.0 → normalized = 0.5"""
        articles = [{"tone": "100,0"}, {"tone": "-100,0"}]
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": articles}))
            result = await fetch_gdelt_tone("Test")
        assert result["tone"] == pytest.approx(0.5, abs=1e-4)

    @pytest.mark.asyncio
    async def test_non_200_response_returns_zero_tone(self):
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(429))
            result = await fetch_gdelt_tone("Country")
        assert result == {"tone": 0.0, "volume": 0}

    @pytest.mark.asyncio
    async def test_network_error_returns_fallback(self):
        with respx.mock:
            respx.get(GDELT_URL).mock(side_effect=httpx.ConnectError("Connection refused"))
            result = await fetch_gdelt_tone("Country")
        assert result == {"tone": 0.5, "volume": 0}

    @pytest.mark.asyncio
    async def test_articles_with_no_tone_field_ignored(self):
        """Articles without 'tone' key should not crash; volume still counted."""
        articles = [{"tone": ""}, {"title": "No tone here"}]
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": articles}))
            result = await fetch_gdelt_tone("Country")
        assert result["volume"] == 2
        # avg_tone = 0.0 (no valid tones), normalized = 0.5
        assert result["tone"] == pytest.approx(0.5, abs=1e-4)

    @pytest.mark.asyncio
    async def test_malformed_tone_string_ignored(self):
        articles = [{"tone": "not_a_number"}]
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": articles}))
            result = await fetch_gdelt_tone("Country")
        assert result["volume"] == 1
        assert result["tone"] == pytest.approx(0.5, abs=1e-4)
