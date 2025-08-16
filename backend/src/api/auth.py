"""
Authentication API Routes
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def auth_status():
    """Check authentication status"""
    return {"status": "not_implemented"}