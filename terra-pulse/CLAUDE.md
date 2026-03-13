# Terra Pulse — Claude Code Guide

## Architecture

```
backend/          FastAPI + Celery + Redis + PostgreSQL
  app/
    api/v1/       Routes: countries, pulse, news, status
    services/     External APIs: gdelt, rest_countries, worldnews, api_status
    scoring/      pulse_engine.py — pure scoring logic (no I/O)
    tasks/        Celery: fetch_pulse.py (background data refresh)
    db/           SQLAlchemy session
  tests/          pytest unit tests (no docker needed)

frontend/         Nuxt 3 + Three.js globe
  tests/          Playwright E2E tests
```

## Quick Commands (backend)

```bash
cd terra-pulse/backend

make test          # run all unit tests
make cov           # tests + coverage report
make watch         # TDD watch mode (requires pytest-watch)
make run F=tests/test_news_api.py   # run one file
make fail          # demo intentional failures
make status        # curl /api/v1/status (needs docker running)
```

## TDD Workflow

1. Write a failing test in `tests/test_<feature>.py`
2. Run `make run F=tests/test_<feature>.py` — confirm it fails
3. Implement the fix in `app/`
4. Run again — confirm it passes
5. Run `make test` — confirm nothing broke

## Docker

```bash
cd terra-pulse
docker compose up -d          # start everything
docker compose logs -f backend  # watch logs (shows API status on startup)
docker compose restart backend  # reload after code change
```

## External APIs

| API | Key needed | Endpoint | Notes |
|-----|-----------|----------|-------|
| WorldNews | yes (`WORLDNEWS_API_KEY`) | `/api/v1/news/{iso3}` | 50 req/day on free tier |
| GDELT | no | `/api/v1/pulse/{iso3}` | Free, no auth |
| RestCountries | no | `/api/v1/countries` | Free, no auth |

Check live status: `GET /api/v1/status`

## Key Behaviours to Know

- **Empty news is not cached** — if WorldNews returns `[]` (e.g. 402 quota hit), we skip the Redis write so the next request retries
- **Pulse fallback** — if no data, returns neutral score (0.5) not an error
- **Countries cached 7 days**, pulse cached 15 min, news cached 15 min
- **Startup** — DB tables created, API status logged, pulse fetch started in background

## Test Layout

```
tests/
  conftest.py                  shared fixtures + DB mock (prevents real DB connection)
  test_pulse_engine.py         pure scoring logic
  test_gdelt_service.py        GDELT HTTP calls (mocked with respx)
  test_rest_countries_service.py  parse_country + fetch
  test_worldnews_service.py    sentiment extraction + fetch
  test_countries_api.py        GET /countries routes
  test_pulse_api.py            GET /pulse routes
  test_news_api.py             GET /news routes (incl. caching bug regression)
  test_status_api.py           GET /status + individual API checks
  test_health.py               GET /health
  test_docker_integration.py   full stack (requires docker compose up)
  test_FAIL_demo_*.py          intentional failures (prove tests are failable)
```
