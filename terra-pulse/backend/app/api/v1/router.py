from fastapi import APIRouter
from app.api.v1 import countries, pulse, news, status

router = APIRouter()
router.include_router(countries.router, prefix="/countries", tags=["countries"])
router.include_router(pulse.router, prefix="/pulse", tags=["pulse"])
router.include_router(news.router, prefix="/news", tags=["news"])
router.include_router(status.router, prefix="/status", tags=["status"])
