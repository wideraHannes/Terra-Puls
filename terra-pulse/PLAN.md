# TERRA PULSE — Next Phase Plan

> Saved 2026-03-13. Full plan in `~/.claude/plans/crispy-conjuring-moler.md`

## Current State Summary

### What works
- Globe renders, ~174 countries colored via GDELT tone
- Side panel: flag, pulse gauge, score rows, news section
- REST Countries metadata (cached 7 days)
- URL-based country selection (`?country=DEU`)
- 25 Playwright E2E tests pass

### What's broken / inaccurate
| Problem | Root Cause |
|---|---|
| Iran = 0.5 (should be crisis) | GDELT 429 → silent fallback to neutral |
| All scores 0.5 on cold start | Placeholder logic, not real fetch |
| News always empty | WorldNews API key not set |
| Trend always "stable" | Hardcoded, no history |
| Layer toggle does nothing | Globe ignores `activeLayer` store |
| Scores lost every 15 min | Never written to PostgreSQL |
| No observability | No logs, no retries, no pipeline UI |

---

## Sprint 1 — Scoring Accuracy

**Goal:** Iran < 0.4, Yemen < 0.25, Switzerland > 0.65

**Changes:**
1. Rewrite `gdelt.py` → use **GDELT Events API** (CAMEO codes, Goldstein scale)
   - Current: naive article tone from Doc API
   - Better: structured conflict events with severity (-10 to +10)
   - Add FIPS→ISO3 country code mapping
2. Add `gdelt_events.py` + `gdelt_gkg.py` — separate fetchers with retry/backoff
3. Rewrite `pulse_engine.py` v2:
   - `conflict_score` = Goldstein scale avg, population-normalized
   - `sentiment_score` = GKG tone + WorldNews (if key set)
   - `trend` = compare vs 24h ago from PostgreSQL history
4. Add `normalizers.py` — per-source 0→1 normalization
5. Fix layer toggle in `TerraGlobe.vue` — wire `activeLayer` to switch dimension

**Key files:**
- `backend/app/services/gdelt.py` — rewrite
- `backend/app/services/gdelt_events.py` — create
- `backend/app/services/gdelt_gkg.py` — create
- `backend/app/scoring/pulse_engine.py` — v2
- `backend/app/scoring/normalizers.py` — create
- `backend/app/api/v1/pulse.py` — persist to Postgres, return trend
- `backend/app/api/v1/timeline.py` — create (GET /timeline/{iso3})
- `frontend/components/globe/TerraGlobe.vue` — layer-aware coloring

---

## Sprint 2 — Replace Celery with Dagster

**Why Dagster:** Built-in pipeline UI (Dagit), declarative retries, data lineage, backfill, sensors. Celery is a black box.

**Structure:**
```
backend/dagster/
  assets/
    countries.py        # REST Countries (weekly)
    gdelt_events.py     # GDELT Events (15 min)
    gdelt_gkg.py        # GDELT GKG sentiment (15 min)
    worldnews.py        # WorldNews articles (15 min)
    worldbank.py        # World Bank indicators (daily)
    pulse_scores.py     # Composite scores (depends on above)
  sensors/
    pulse_freshness.py  # Alert if scores > 30 min stale
  resources/
    redis_resource.py
    postgres_resource.py
    http_resource.py    # httpx with retry/backoff
  definitions.py        # Dagster Definitions
```

**Add to docker-compose:**
```yaml
dagster:
  command: dagster dev -f dagster/definitions.py -p 3002
  ports: ["3002:3002"]   # Dagit UI
```

---

## Sprint 3 — Documentation in /docs

```
terra-pulse/docs/
  README.md           # Overview + quickstart
  scoring.md          # How pulse score is calculated (most important)
  data-pipelines.md   # Dagster assets, schedules, backfill
  api-reference.md    # All REST endpoints with examples
  data-sources.md     # Each API: what we get, rate limits, auth
  setup-local.md      # Step-by-step local dev
  architecture.md     # System diagram + data flow
  deployment.md       # Docker Compose + production checklist
```

---

## Verification Targets

```bash
curl http://localhost:8001/api/v1/pulse/IRN  # composite_score < 0.4
curl http://localhost:8001/api/v1/pulse/CHE  # composite_score > 0.65
curl http://localhost:8001/api/v1/pulse/YEM  # composite_score < 0.25
curl http://localhost:8001/api/v1/timeline/DEU  # array of timestamped scores
# Dagit UI at http://localhost:3002 — pipeline runs visible
# All 25 Playwright tests still pass
```
