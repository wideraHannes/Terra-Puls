import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import router
from app.db.session import engine, Base

logger = logging.getLogger("terra_pulse")


async def _log_api_status():
    from app.services.api_status import get_api_status
    status = await get_api_status()
    for name, result in status.items():
        icon = "✓" if result["ok"] else "✗"
        reason = f" — {result['reason']}" if not result["ok"] and "reason" in result else ""
        logger.info(f"  {icon} {name}{reason}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Log which external APIs are available
    logger.info("External API status:")
    asyncio.create_task(_log_api_status())
    # Kick off initial data fetch in background (non-blocking)
    from app.tasks.fetch_pulse import fetch_pulse_startup
    asyncio.create_task(fetch_pulse_startup())
    yield


app = FastAPI(title="Terra Pulse API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
