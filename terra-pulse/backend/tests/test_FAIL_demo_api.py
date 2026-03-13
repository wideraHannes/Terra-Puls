"""
INTENTIONAL FAILURE DEMONSTRATIONS for test/api-routes branch.
These tests WILL FAIL — they prove the test suite is failable.
Run: pytest tests/test_FAIL_demo_api.py -v
Expected: ALL tests FAIL
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


class TestIntentionalAPIFailures:

    @pytest.mark.asyncio
    async def test_FAILS_health_wrong_status_value(self):
        """WILL FAIL: /health returns {"status": "ok"}, not "healthy"."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.json()["status"] == "healthy", (
            f"DEMO FAILURE: /health returns 'ok', not 'healthy'. Actual: {response.json()}"
        )

    @pytest.mark.asyncio
    async def test_FAILS_nonexistent_endpoint_should_200(self):
        """WILL FAIL: /api/v1/doesnotexist returns 404, not 200."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/doesnotexist")
        assert response.status_code == 200, (
            f"DEMO FAILURE: nonexistent endpoint returns 404, not 200. Actual: {response.status_code}"
        )
