"""
Settings API Routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_settings():
    """Get application settings"""
    return {"status": "not_implemented"}
