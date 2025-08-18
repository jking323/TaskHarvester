"""
Wrike Integration API Routes
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ..models.database import get_database
from ..models.action_items import ActionItem
from ..services.wrike_integration import WrikeIntegration

router = APIRouter()

# Pydantic models
class SyncActionItemsRequest(BaseModel):
    action_item_ids: Optional[List[int]] = Field(None, description="Specific action item IDs to sync")
    confidence_threshold: float = Field(0.7, description="Minimum confidence threshold", ge=0.0, le=1.0)
    limit: int = Field(10, description="Maximum items to sync", ge=1, le=50)

class SyncActionItemsResponse(BaseModel):
    message: str
    synced_count: int
    failed_count: int
    tasks_created: List[Dict[str, Any]]

class SyncCandidatesResponse(BaseModel):
    candidates: List[Dict[str, Any]]
    total_count: int
    confidence_threshold: float


@router.get("/sync-candidates", response_model=SyncCandidatesResponse)
async def get_sync_candidates(
    confidence_threshold: float = Query(0.7, description="Minimum confidence threshold", ge=0.0, le=1.0),
    days_back: int = Query(7, description="Days to look back", ge=1, le=30),
    db: Session = Depends(get_database)
):
    """Get action items that are candidates for Wrike synchronization"""
    
    wrike_service = WrikeIntegration()
    
    try:
        candidates = await wrike_service.get_sync_candidates(
            db_session=db,
            confidence_threshold=confidence_threshold,
            days_back=days_back
        )
        
        return SyncCandidatesResponse(
            candidates=candidates,
            total_count=len(candidates),
            confidence_threshold=confidence_threshold
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get sync candidates: {str(e)}"
        )


@router.post("/sync-to-wrike", response_model=SyncActionItemsResponse)
async def sync_action_items_to_wrike(
    request: SyncActionItemsRequest,
    db: Session = Depends(get_database)
):
    """Synchronize action items to Wrike tasks"""
    
    wrike_service = WrikeIntegration()
    
    try:
        result = await wrike_service.sync_action_items_to_wrike(
            db_session=db,
            action_item_ids=request.action_item_ids,
            confidence_threshold=request.confidence_threshold,
            limit=request.limit
        )
        
        return SyncActionItemsResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync action items to Wrike: {str(e)}"
        )


@router.get("/status")
async def get_wrike_integration_status(db: Session = Depends(get_database)):
    """Get Wrike integration status and statistics"""
    
    # Count synced vs unsynced action items
    total_items = db.query(ActionItem).count()
    synced_items = db.query(ActionItem).filter(ActionItem.wrike_task_id.isnot(None)).count()
    unsynced_items = total_items - synced_items
    
    # Get high-confidence unsynced items
    high_confidence_unsynced = db.query(ActionItem)\
        .filter(ActionItem.wrike_task_id.is_(None))\
        .filter(ActionItem.confidence >= 0.7)\
        .count()
    
    return {
        "wrike_integration_enabled": True,  # In demo mode
        "total_action_items": total_items,
        "synced_to_wrike": synced_items,
        "pending_sync": unsynced_items,
        "high_confidence_pending": high_confidence_unsynced,
        "sync_rate": round((synced_items / total_items * 100), 1) if total_items > 0 else 0
    }