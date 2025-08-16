"""
Wrike Integration API Routes
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def wrike_status():
    """Check Wrike connection status"""
    return {"status": "not_implemented"}