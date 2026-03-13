"""Tests for app/services/rest_countries.py."""
import pytest
import respx
import httpx
from app.services.rest_countries import parse_country, fetch_all_countries, REST_COUNTRIES_URL


class TestParseCountry:

    def test_full_data_parsed_correctly(self):
        raw = {
            "cca3": "DEU", "cca2": "DE",
            "name": {"common": "Germany"},
            "capital": ["Berlin"],
            "region": "Europe",
            "subregion": "Western Europe",
            "population": 83000000,
            "latlng": [51.0, 9.0],
            "currencies": {"EUR": {"name": "Euro", "symbol": "€"}},
            "flags": {"png": "https://example.com/de.png"},
        }
        result = parse_country(raw)
        assert result["iso3"] == "DEU"
        assert result["iso2"] == "DE"
        assert result["name"] == "Germany"
        assert result["capital"] == "Berlin"
        assert result["region"] == "Europe"
        assert result["subregion"] == "Western Europe"
        assert result["population"] == 83000000
        assert result["latitude"] == 51.0
        assert result["longitude"] == 9.0
        assert result["currency_code"] == "EUR"
        assert result["flag_url"] == "https://example.com/de.png"

    def test_missing_capital_returns_none(self):
        raw = {"cca3": "AAA", "cca2": "AA", "name": {"common": "Test"}, "capital": []}
        result = parse_country(raw)
        assert result["capital"] is None

    def test_missing_currencies_returns_none(self):
        raw = {"cca3": "AAA", "cca2": "AA", "name": {"common": "Test"}, "currencies": {}}
        result = parse_country(raw)
        assert result["currency_code"] is None

    def test_missing_latlng_defaults_to_zero(self):
        raw = {"cca3": "AAA", "cca2": "AA", "name": {"common": "Test"}, "latlng": []}
        result = parse_country(raw)
        assert result["latitude"] == 0
        assert result["longitude"] == 0

    def test_missing_flags_returns_empty_string(self):
        raw = {"cca3": "AAA", "cca2": "AA", "name": {"common": "Test"}, "flags": {}}
        result = parse_country(raw)
        assert result["flag_url"] == ""

    def test_empty_raw_returns_default_values(self):
        result = parse_country({})
        assert result["iso3"] == ""
        assert result["name"] == ""
        assert result["population"] == 0

    def test_result_has_all_required_keys(self):
        result = parse_country({})
        expected_keys = {"iso3", "iso2", "name", "capital", "region", "subregion",
                         "population", "latitude", "longitude", "currency_code", "flag_url"}
        assert set(result.keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_fetch_all_countries_returns_list(self):
        mock_data = [{"cca3": "DEU", "cca2": "DE", "name": {"common": "Germany"}}]
        with respx.mock:
            respx.get(REST_COUNTRIES_URL).mock(return_value=httpx.Response(200, json=mock_data))
            result = await fetch_all_countries()
        assert isinstance(result, list)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_fetch_all_countries_raises_on_error(self):
        with respx.mock:
            respx.get(REST_COUNTRIES_URL).mock(return_value=httpx.Response(500))
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_all_countries()
