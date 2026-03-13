<div align="center">

# 🌍 Terra Pulse

**Real-time geopolitical intelligence on an interactive 3D globe.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Nuxt](https://img.shields.io/badge/Nuxt-3-00DC82?style=flat-square&logo=nuxt.js)](https://nuxt.com)
[![Three.js](https://img.shields.io/badge/Three.js-Globe-black?style=flat-square&logo=three.js)](https://threejs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](#license)

<br/>

> Terra Pulse aggregates live news sentiment and GDELT conflict data to assign every country a real-time "pulse" score — visualized as a glowing, interactive 3D globe.

<br/>

![Terra Pulse Globe](https://via.placeholder.com/900x450/0a0a0f/4ade80?text=🌍+Terra+Pulse+Globe+Preview)

</div>

---

## What is Terra Pulse?

Terra Pulse is a full-stack geopolitical monitoring platform that combines:

- **News Sentiment** — live articles from [WorldNewsAPI](https://worldnewsapi.com) scored by sentiment
- **GDELT Events** — geopolitical event volume and tone from the [GDELT Project](https://www.gdeltproject.org)
- **Composite Pulse Score** — weighted algorithm (70% sentiment, 30% stability) normalized 0–1
- **3D Globe UI** — country-level color overlays using [Globe.gl](https://globe.gl) + Three.js

Countries pulse green when stable, shift red as conflict and negative sentiment rise.

---

## Architecture

```
┌──────────────────────────────────────────────┐
│                  Frontend                    │
│        Nuxt 3 · Vue 3 · Globe.gl             │
│           http://localhost:3000              │
└────────────────────┬─────────────────────────┘
                     │ REST API
┌────────────────────▼─────────────────────────┐
│                  Backend                     │
│          FastAPI · SQLAlchemy · Redis        │
│           http://localhost:8000              │
│                                              │
│  ┌──────────────┐   ┌──────────────────────┐ │
│  │ Celery Beat  │──▶│   Celery Workers     │ │
│  │  (scheduler) │   │  (data fetch tasks)  │ │
│  └──────────────┘   └──────────────────────┘ │
└──────┬───────────────────────┬───────────────┘
       │                       │
┌──────▼──────┐        ┌───────▼──────┐
│  PostgreSQL │        │    Redis     │
│  (data)     │        │  (cache/MQ)  │
└─────────────┘        └──────────────┘
```

**Data Sources (all free)**

| Source | Used For |
|---|---|
| [WorldNewsAPI](https://worldnewsapi.com) | News articles + sentiment scores |
| [GDELT Project](https://www.gdeltproject.org) | Event volume, tone, conflict data |
| [REST Countries](https://restcountries.com) | Country metadata (flag, region, etc.) |

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- A free [WorldNewsAPI](https://worldnewsapi.com) key

### 1. Clone & configure

```bash
git clone https://github.com/your-username/terra-pulse.git
cd terra-pulse

cp .env.example .env
# Edit .env and add your WORLDNEWS_API_KEY
```

### 2. Run with Docker

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### 3. Local development (no Docker)

<details>
<summary>Backend</summary>

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Start dependencies
docker compose up db redis -d

# Run API
uvicorn app.main:app --reload

# Run worker
celery -A app.tasks.celery_app worker --loglevel=info
```

</details>

<details>
<summary>Frontend</summary>

```bash
cd frontend
npm install
npm run dev
```

</details>

---

## API Reference

| Endpoint | Description |
|---|---|
| `GET /api/v1/countries` | All countries with latest pulse scores |
| `GET /api/v1/countries/{iso}` | Single country detail |
| `GET /api/v1/pulse/{iso}` | Pulse history for a country |
| `GET /api/v1/news/{iso}` | Recent news articles for a country |

Interactive docs available at `/docs` (Swagger) and `/redoc`.

---

## Pulse Score Algorithm

```
composite = sentiment × 0.7 + stability × 0.3

sentiment = WorldNews_score × 0.6 + GDELT_tone × 0.4
stability = 1 − (GDELT_volume / baseline) × 0.5   # max 50% penalty
```

Scores range from `0.0` (critical instability) to `1.0` (fully stable). Displayed as a color gradient from red → yellow → green on the globe.

---

## Project Structure

```
terra-pulse/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI route handlers
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── services/        # External API clients
│   │   ├── scoring/         # Pulse engine
│   │   ├── tasks/           # Celery tasks
│   │   └── config.py        # Settings via env vars
│   └── Dockerfile
├── frontend/
│   ├── pages/               # Nuxt pages (index = globe)
│   └── Dockerfile
├── docker-compose.yml
├── .env.example             # Copy to .env — never commit secrets
└── README.md
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `WORLDNEWS_API_KEY` | Yes | API key from worldnewsapi.com |
| `POSTGRES_DB` | No | Database name (default: `terrapulse`) |
| `POSTGRES_USER` | No | DB user (default: `postgres`) |
| `POSTGRES_PASSWORD` | No | DB password (default: `postgres`) |

Copy `.env.example` → `.env` and fill in your values. The `.env` file is gitignored.

---

## Roadmap

- [ ] Historical pulse timeline per country
- [ ] Trend detection (rising / falling pulse)
- [ ] Alert subscriptions for threshold crossings
- [ ] Additional data sources (social media sentiment, economic indicators)
- [ ] Shareable country report cards

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with curiosity and open data.

</div>
