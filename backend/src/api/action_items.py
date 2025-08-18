"""
Action Items API Routes
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ..models.database import get_database
from ..models.action_items import ActionItem, ActionItemStatus, ActionItemPriority, ProcessingLog
from ..models.auth_tokens import AuthToken, TokenProvider

router = APIRouter()

# Pydantic models for requests/responses
class ActionItemResponse(BaseModel):
    id: int
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    priority: str
    status: str
    confidence: float
    context: Optional[str] = None
    source_type: str
    source_id: str
    source_subject: Optional[str] = None
    source_sender: Optional[str] = None
    source_date: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    wrike_task_id: Optional[str] = None
    external_url: Optional[str] = None

class ActionItemListResponse(BaseModel):
    items: List[ActionItemResponse]
    total_count: int
    filtered_count: int
    page: int
    per_page: int

class UpdateActionItemRequest(BaseModel):
    status: Optional[ActionItemStatus] = None
    priority: Optional[ActionItemPriority] = None
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    wrike_task_id: Optional[str] = None
    external_url: Optional[str] = None

class ActionItemStatsResponse(BaseModel):
    total_items: int
    pending_items: int
    in_progress_items: int
    completed_items: int
    cancelled_items: int
    high_priority_items: int
    items_with_deadlines: int
    avg_confidence: float
    recent_processing_count: int  # Last 24 hours


async def get_current_user_id(db: Session = Depends(get_database)) -> Optional[str]:
    """Get current authenticated user ID"""
    # In a real implementation, this would extract user ID from JWT token
    # For now, we'll look for any valid Microsoft token
    token = await AuthToken.get_valid_token(db, TokenProvider.MICROSOFT)
    return token.user_id if token else None


@router.get("/", response_model=ActionItemListResponse)
async def list_action_items(
    status: Optional[ActionItemStatus] = Query(None, description="Filter by status"),
    priority: Optional[ActionItemPriority] = Query(None, description="Filter by priority"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    days_back: int = Query(30, description="Days to look back", ge=1, le=365),
    confidence_min: float = Query(0.0, description="Minimum confidence score", ge=0.0, le=1.0),
    page: int = Query(1, description="Page number", ge=1),
    per_page: int = Query(50, description="Items per page", ge=1, le=200),
    db: Session = Depends(get_database),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """List action items with filtering and pagination"""
    
    # Build query
    query = db.query(ActionItem)
    
    # Filter by user (if authenticated)
    if user_id:
        query = query.filter(ActionItem.user_id == user_id)
    
    # Apply filters
    if status:
        query = query.filter(ActionItem.status == status)
    
    if priority:
        query = query.filter(ActionItem.priority == priority)
    
    if assignee:
        query = query.filter(ActionItem.assignee.ilike(f"%{assignee}%"))
    
    if source_type:
        query = query.filter(ActionItem.source_type == source_type)
    
    # Date range filter
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    query = query.filter(ActionItem.created_at >= cutoff_date)
    
    # Confidence filter
    if confidence_min > 0:
        query = query.filter(ActionItem.confidence >= confidence_min)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply ordering and pagination
    items = query.order_by(desc(ActionItem.created_at))\
                 .offset((page - 1) * per_page)\
                 .limit(per_page)\
                 .all()
    
    # Convert to response format
    item_responses = [ActionItemResponse(**item.to_dict()) for item in items]
    
    return ActionItemListResponse(
        items=item_responses,
        total_count=total_count,
        filtered_count=len(item_responses),
        page=page,
        per_page=per_page
    )


@router.get("/{item_id}", response_model=ActionItemResponse)
async def get_action_item(
    item_id: int,
    db: Session = Depends(get_database),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """Get a specific action item"""
    
    query = db.query(ActionItem).filter(ActionItem.id == item_id)
    
    # Filter by user if authenticated
    if user_id:
        query = query.filter(ActionItem.user_id == user_id)
    
    item = query.first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    return ActionItemResponse(**item.to_dict())


@router.patch("/{item_id}", response_model=ActionItemResponse)
async def update_action_item(
    item_id: int,
    update_data: UpdateActionItemRequest,
    db: Session = Depends(get_database),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """Update an action item"""
    
    query = db.query(ActionItem).filter(ActionItem.id == item_id)
    
    # Filter by user if authenticated
    if user_id:
        query = query.filter(ActionItem.user_id == user_id)
    
    item = query.first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(item, field, value)
    
    # Set completion timestamp if status changed to completed
    if update_data.status == ActionItemStatus.COMPLETED and item.completed_at is None:
        item.completed_at = datetime.utcnow()
    elif update_data.status and update_data.status != ActionItemStatus.COMPLETED:
        item.completed_at = None
    
    item.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    
    return ActionItemResponse(**item.to_dict())


@router.delete("/{item_id}")
async def delete_action_item(
    item_id: int,
    db: Session = Depends(get_database),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """Delete an action item"""
    
    query = db.query(ActionItem).filter(ActionItem.id == item_id)
    
    # Filter by user if authenticated
    if user_id:
        query = query.filter(ActionItem.user_id == user_id)
    
    item = query.first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Action item deleted successfully"}


@router.get("/stats/summary", response_model=ActionItemStatsResponse)
async def get_action_item_stats(
    days_back: int = Query(30, description="Days to include in stats", ge=1, le=365),
    db: Session = Depends(get_database),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """Get action item statistics"""
    
    # Build base query
    query = db.query(ActionItem)
    
    # Filter by user if authenticated
    if user_id:
        query = query.filter(ActionItem.user_id == user_id)
    
    # Date range filter
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    query = query.filter(ActionItem.created_at >= cutoff_date)
    
    items = query.all()
    
    # Calculate statistics
    total_items = len(items)
    pending_items = sum(1 for item in items if item.status == ActionItemStatus.PENDING)
    in_progress_items = sum(1 for item in items if item.status == ActionItemStatus.IN_PROGRESS)
    completed_items = sum(1 for item in items if item.status == ActionItemStatus.COMPLETED)
    cancelled_items = sum(1 for item in items if item.status == ActionItemStatus.CANCELLED)
    
    high_priority_items = sum(1 for item in items if item.priority in [ActionItemPriority.HIGH, ActionItemPriority.URGENT])
    items_with_deadlines = sum(1 for item in items if item.deadline)
    
    # Average confidence
    avg_confidence = sum(item.confidence for item in items) / total_items if total_items > 0 else 0.0
    
    # Recent processing (last 24 hours)
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    recent_processing_count = db.query(ProcessingLog)\
        .filter(ProcessingLog.processed_at >= recent_cutoff)\
        .count()
    
    return ActionItemStatsResponse(
        total_items=total_items,
        pending_items=pending_items,
        in_progress_items=in_progress_items,
        completed_items=completed_items,
        cancelled_items=cancelled_items,
        high_priority_items=high_priority_items,
        items_with_deadlines=items_with_deadlines,
        avg_confidence=round(avg_confidence, 3),
        recent_processing_count=recent_processing_count
    )


@router.post("/bulk-update")
async def bulk_update_action_items(
    item_ids: List[int],
    update_data: UpdateActionItemRequest,
    db: Session = Depends(get_database),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """Bulk update multiple action items"""
    
    query = db.query(ActionItem).filter(ActionItem.id.in_(item_ids))
    
    # Filter by user if authenticated
    if user_id:
        query = query.filter(ActionItem.user_id == user_id)
    
    items = query.all()
    
    if not items:
        raise HTTPException(status_code=404, detail="No action items found")
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    updated_count = 0
    
    for item in items:
        for field, value in update_dict.items():
            setattr(item, field, value)
        
        # Handle completion timestamp
        if update_data.status == ActionItemStatus.COMPLETED and item.completed_at is None:
            item.completed_at = datetime.utcnow()
        elif update_data.status and update_data.status != ActionItemStatus.COMPLETED:
            item.completed_at = None
        
        item.updated_at = datetime.utcnow()
        updated_count += 1
    
    db.commit()
    
    return {"message": f"Updated {updated_count} action items successfully"}