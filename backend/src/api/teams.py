"""
Teams Integration API Routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def teams_status():
    """Check Teams connection status"""
    return {"status": "not_implemented"}
