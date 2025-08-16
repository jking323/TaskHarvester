"""
Outlook Integration API Routes
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def outlook_status():
    """Check Outlook connection status"""
    return {"status": "not_implemented"}