from fastapi import APIRouter
from app.services.api_status import get_api_status

router = APIRouter()


@router.get("")
async def api_status():
    """Returns which external APIs are currently reachable and usable."""
    return await get_api_status()
