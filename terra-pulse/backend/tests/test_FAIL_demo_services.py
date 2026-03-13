"""
INTENTIONAL FAILURE DEMONSTRATIONS for test/services branch.
These tests WILL FAIL — they show the test suite is failable.
Run: pytest tests/test_FAIL_demo_services.py -v
Expected: ALL tests FAIL
"""
import pytest
import respx
import httpx
from app.services.gdelt import fetch_gdelt_tone, GDELT_URL
from app.services.rest_countries import parse_country
from app.services.worldnews import extract_sentiment


class TestIntentionalServiceFailures:

    @pytest.mark.asyncio
    async def test_FAILS_wrong_tone_normalization(self):
        """WILL FAIL: GDELT tone +100 → normalized=1.0, not 0.5."""
        articles = [{"tone": "100,0,0"}]
        with respx.mock:
            respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={"articles": articles}))
            result = await fetch_gdelt_tone("Country")
        assert result["tone"] == pytest.approx(0.5, abs=1e-4), (
            f"DEMO FAILURE: tone=100 normalizes to 1.0, not 0.5. Actual: {result['tone']}"
        )

    def test_FAILS_wrong_parse_country_capital(self):
        """WILL FAIL: capital is 'Berlin', not 'Paris'."""
        raw = {"capital": ["Berlin"], "name": {"common": "Germany"}, "cca3": "DEU", "cca2": "DE"}
        result = parse_country(raw)
        assert result["capital"] == "Paris", (
            f"DEMO FAILURE: capital should be 'Berlin', not 'Paris'. Actual: {result['capital']}"
        )

    def test_FAILS_wrong_sentiment_mapping(self):
        """WILL FAIL: sentiment=1.0 maps to 1.0, not 0.5."""
        result = extract_sentiment([{"sentiment": 1.0}])
        assert result == pytest.approx(0.5, abs=1e-4), (
            f"DEMO FAILURE: sentiment=1.0 maps to 1.0, not 0.5. Actual: {result}"
        )
