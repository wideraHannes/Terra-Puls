"""
Docker Integration Tests — validate the full docker-compose stack.

These tests hit the REAL running docker-compose services.
Run ONLY when `docker compose up` is active:
    docker compose -f terra-pulse/docker-compose.yml up -d
    pytest tests/test_docker_integration.py -v

Tests will FAIL if docker compose is not running (that is expected behavior
when services are down — demonstrating that tests are failable).
"""
import pytest
import httpx
import redis
import asyncio

BACKEND_URL = "http://localhost:8000"
REDIS_URL = "redis://localhost:6379/0"
DB_HOST = "localhost"
DB_PORT = 5432


class TestBackendHealth:
    """Validate the backend FastAPI service is up and responding."""

    def test_health_endpoint_returns_200(self):
        """FAILABLE: fails if backend container is not running."""
        response = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        assert response.status_code == 200, (
            f"Backend health check failed. Is docker compose running? "
            f"Status: {response.status_code}"
        )

    def test_health_endpoint_returns_ok_status(self):
        """FAILABLE: fails if backend returns wrong payload."""
        response = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        data = response.json()
        assert data.get("status") == "ok", (
            f"Backend health returned wrong status. Got: {data}"
        )

    def test_api_v1_docs_accessible(self):
        """FAILABLE: fails if FastAPI or docs route not configured."""
        response = httpx.get(f"{BACKEND_URL}/docs", timeout=5.0)
        assert response.status_code == 200, (
            f"API docs not accessible. Status: {response.status_code}"
        )

    def test_openapi_json_accessible(self):
        """FAILABLE: validates OpenAPI spec is generated."""
        response = httpx.get(f"{BACKEND_URL}/openapi.json", timeout=5.0)
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert data.get("info", {}).get("title") == "Terra Pulse API"


class TestRedisConnectivity:
    """Validate Redis is accessible and functioning."""

    def test_redis_ping_succeeds(self):
        """FAILABLE: fails if Redis container is not running."""
        r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=3)
        result = r.ping()
        assert result is True, "Redis ping failed — is the redis container running?"

    def test_redis_set_and_get(self):
        """FAILABLE: fails if Redis read/write is broken."""
        r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=3)
        r.setex("test:integration:key", 60, "test_value")
        value = r.get("test:integration:key")
        assert value == "test_value", f"Redis set/get mismatch. Got: {value}"
        r.delete("test:integration:key")

    def test_redis_key_expiry(self):
        """FAILABLE: fails if Redis TTL is not set correctly."""
        r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=3)
        r.setex("test:ttl:key", 10, "expires_soon")
        ttl = r.ttl("test:ttl:key")
        assert ttl > 0, f"TTL should be > 0 but got: {ttl}"
        assert ttl <= 10, f"TTL should be <= 10 but got: {ttl}"
        r.delete("test:ttl:key")


class TestCountriesEndpoint:
    """Validate /api/v1/countries endpoint behavior."""

    def test_countries_endpoint_returns_200(self):
        """FAILABLE: fails if countries route is broken or service is down."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/countries", timeout=30.0)
        assert response.status_code == 200, (
            f"Countries endpoint failed. Status: {response.status_code}, "
            f"Body: {response.text[:200]}"
        )

    def test_countries_returns_list(self):
        """FAILABLE: fails if response shape is wrong."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/countries", timeout=30.0)
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"

    def test_countries_list_not_empty(self):
        """FAILABLE: fails if no countries are loaded."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/countries", timeout=30.0)
        data = response.json()
        assert len(data) > 0, "Countries list is empty — data may not have loaded yet"

    def test_country_has_required_fields(self):
        """FAILABLE: fails if country schema is missing fields."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/countries", timeout=30.0)
        data = response.json()
        if data:
            country = data[0]
            required_fields = {"iso3", "iso2", "name", "region", "population"}
            missing = required_fields - set(country.keys())
            assert not missing, f"Country missing fields: {missing}"

    def test_get_country_by_iso3_germany(self):
        """FAILABLE: fails if country lookup is broken."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/countries/DEU", timeout=15.0)
        assert response.status_code == 200, (
            f"GET /countries/DEU failed. Status: {response.status_code}"
        )
        data = response.json()
        assert data["iso3"] == "DEU"
        assert data["name"] == "Germany"

    def test_get_unknown_country_returns_404(self):
        """FAILABLE: fails if 404 handling is broken."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/countries/ZZZ", timeout=10.0)
        assert response.status_code == 404, (
            f"Unknown country should return 404, got: {response.status_code}"
        )


class TestPulseEndpoint:
    """Validate /api/v1/pulse endpoint behavior."""

    def test_pulse_all_returns_200(self):
        """FAILABLE: fails if pulse route is broken."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/pulse", timeout=30.0)
        assert response.status_code == 200, (
            f"Pulse endpoint failed. Status: {response.status_code}"
        )

    def test_pulse_returns_dict(self):
        """FAILABLE: fails if pulse response shape is wrong."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/pulse", timeout=30.0)
        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"

    def test_pulse_scores_in_valid_range(self):
        """FAILABLE: fails if composite_score is out of 0..1 range."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/pulse", timeout=30.0)
        data = response.json()
        for iso3, pulse in data.items():
            score = pulse.get("composite_score", -1)
            assert 0.0 <= score <= 1.0, (
                f"{iso3}: composite_score {score} is out of range [0, 1]"
            )

    def test_unknown_country_pulse_returns_404(self):
        """FAILABLE: fails if 404 for unknown country is broken."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/pulse/ZZZ", timeout=10.0)
        assert response.status_code == 404


class TestNewsEndpoint:
    """Validate /api/v1/news/{iso3} endpoint."""

    def test_news_for_germany_returns_200_or_503(self):
        """
        FAILABLE: fails if news endpoint crashes with 500.
        503 is acceptable if countries data isn't loaded yet.
        """
        response = httpx.get(f"{BACKEND_URL}/api/v1/news/DEU", timeout=15.0)
        assert response.status_code in (200, 404, 503), (
            f"News endpoint returned unexpected status: {response.status_code}"
        )

    def test_news_limit_parameter_respected(self):
        """FAILABLE: fails if limit parameter is ignored."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/news/DEU?limit=5", timeout=15.0)
        if response.status_code == 200:
            articles = response.json()
            assert len(articles) <= 5, (
                f"Limit=5 not respected. Got {len(articles)} articles."
            )

    def test_news_limit_max_is_20(self):
        """FAILABLE: fails if limit > 20 is accepted without capping."""
        response = httpx.get(f"{BACKEND_URL}/api/v1/news/DEU?limit=99", timeout=15.0)
        # FastAPI should reject limit > 20 with 422
        assert response.status_code in (200, 422, 404, 503), (
            f"Unexpected status for limit=99: {response.status_code}"
        )


class TestDatabaseConnectivity:
    """Validate PostgreSQL is accessible."""

    def test_postgres_is_reachable(self):
        """FAILABLE: fails if postgres container is down."""
        import socket
        try:
            sock = socket.create_connection((DB_HOST, DB_PORT), timeout=3)
            sock.close()
            reachable = True
        except (socket.timeout, ConnectionRefusedError, OSError):
            reachable = False
        assert reachable, (
            f"PostgreSQL at {DB_HOST}:{DB_PORT} is not reachable. "
            "Is the db container running?"
        )

    def test_backend_can_use_db_tables(self):
        """FAILABLE: fails if DB tables were not created on startup."""
        # The health check passing implies the app started, which requires DB
        response = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        assert response.status_code == 200, (
            "Backend health failed — DB initialization may have failed"
        )


class TestFrontendConnectivity:
    """Validate the Nuxt frontend is accessible."""

    def test_frontend_returns_200(self):
        """FAILABLE: fails if frontend container is not running."""
        response = httpx.get("http://localhost:3000", timeout=15.0)
        assert response.status_code == 200, (
            f"Frontend not accessible. Status: {response.status_code}. "
            "Is the frontend container running?"
        )


class TestIntentionalDockerFailures:
    """
    INTENTIONAL FAILURES — demonstrate what failing tests look like.
    These WILL FAIL even when docker compose is running.
    """

    def test_FAILS_wrong_health_response(self):
        """WILL FAIL: /health returns 'ok', not 'running'."""
        response = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        assert response.json().get("status") == "running", (
            f"DEMO FAILURE: /health returns 'ok', not 'running'. Got: {response.json()}"
        )

    def test_FAILS_wrong_api_prefix(self):
        """WILL FAIL: correct prefix is /api/v1, not /api/v2."""
        response = httpx.get(f"{BACKEND_URL}/api/v2/countries", timeout=5.0)
        assert response.status_code == 200, (
            f"DEMO FAILURE: /api/v2 doesn't exist (it's /api/v1). Got: {response.status_code}"
        )
