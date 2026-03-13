"""Tests for GET /api/v1/status — external API health checks."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app


MOCK_ALL_OK = {
    "worldnews":    {"ok": True},
    "gdelt":        {"ok": True},
    "rest_countries": {"ok": True},
}

MOCK_WORLDNEWS_DOWN = {
    "worldnews":    {"ok": False, "reason": "daily quota exceeded (402)"},
    "gdelt":        {"ok": True},
    "rest_countries": {"ok": True},
}


class TestStatusEndpoint:

    async def test_returns_200(self):
        with patch("app.api.v1.status.get_api_status", new_callable=AsyncMock, return_value=MOCK_ALL_OK):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/status")
        assert r.status_code == 200

    async def test_response_has_all_three_apis(self):
        with patch("app.api.v1.status.get_api_status", new_callable=AsyncMock, return_value=MOCK_ALL_OK):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/status")
        data = r.json()
        assert "worldnews" in data
        assert "gdelt" in data
        assert "rest_countries" in data

    async def test_each_api_entry_has_ok_field(self):
        with patch("app.api.v1.status.get_api_status", new_callable=AsyncMock, return_value=MOCK_ALL_OK):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/status")
        for name, entry in r.json().items():
            assert "ok" in entry, f"{name} is missing 'ok' field"

    async def test_down_api_reports_reason(self):
        with patch("app.api.v1.status.get_api_status", new_callable=AsyncMock, return_value=MOCK_WORLDNEWS_DOWN):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/status")
        data = r.json()
        assert data["worldnews"]["ok"] is False
        assert "reason" in data["worldnews"]
        assert "402" in data["worldnews"]["reason"]


class TestApiStatusChecks:
    """Unit tests for the individual check functions."""

    async def test_worldnews_no_key_reports_not_ok(self):
        from app.services.api_status import check_worldnews
        with patch("app.services.api_status.settings") as s:
            s.WORLDNEWS_API_KEY = ""
            result = await check_worldnews()
        assert result["ok"] is False
        assert "no API key" in result["reason"]

    async def test_worldnews_402_reports_quota_exceeded(self):
        import httpx, respx
        from app.services.api_status import check_worldnews
        with patch("app.services.api_status.settings") as s:
            s.WORLDNEWS_API_KEY = "test-key"
            with respx.mock:
                respx.get("https://api.worldnewsapi.com/search-news").mock(
                    return_value=httpx.Response(402)
                )
                result = await check_worldnews()
        assert result["ok"] is False
        assert "402" in result["reason"]

    async def test_worldnews_200_reports_ok(self):
        import httpx, respx
        from app.services.api_status import check_worldnews
        with patch("app.services.api_status.settings") as s:
            s.WORLDNEWS_API_KEY = "test-key"
            with respx.mock:
                respx.get("https://api.worldnewsapi.com/search-news").mock(
                    return_value=httpx.Response(200, json={"news": []})
                )
                result = await check_worldnews()
        assert result["ok"] is True

    async def test_gdelt_200_reports_ok(self):
        import httpx, respx
        from app.services.api_status import check_gdelt
        with respx.mock:
            respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
                return_value=httpx.Response(200, json={})
            )
            result = await check_gdelt()
        assert result["ok"] is True

    async def test_rest_countries_network_error_reports_not_ok(self):
        import httpx, respx
        from app.services.api_status import check_rest_countries
        with respx.mock:
            respx.get("https://restcountries.com/v3.1/alpha/DEU").mock(
                side_effect=httpx.ConnectError("refused")
            )
            result = await check_rest_countries()
        assert result["ok"] is False
