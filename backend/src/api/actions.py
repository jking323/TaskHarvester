"""
Action Items API Routes
"""
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..models.database import get_database
from ..models.action_item import (
    ActionItem, ActionItemCreate, ActionItemUpdate, ActionItemsResponse,
    ActionItemDB, ActionItemStatus, ProcessingStats
)
from ..services.wrike_integration import WrikeIntegrator

router = APIRouter()


@router.get("/", response_model=ActionItemsResponse)
async def get_action_items(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[ActionItemStatus] = None,
    assignee: Optional[str] = None,
    db: Session = Depends(get_database)
):
    """Get action items with pagination and filtering"""
    
    # Build query
    query = db.query(ActionItemDB)
    
    if status:
        query = query.filter(ActionItemDB.status == status)
    if assignee:
        query = query.filter(ActionItemDB.assignee_email.ilike(f"%{assignee}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    items = query.order_by(desc(ActionItemDB.created_at)).offset((page - 1) * size).limit(size).all()
    
    return ActionItemsResponse(
        items=[ActionItem.from_orm(item) for item in items],
        total=total,
        page=page,
        size=size
    )


@router.get("/pending", response_model=List[ActionItem])
async def get_pending_action_items(db: Session = Depends(get_database)):
    """Get all pending action items for review"""
    
    items = db.query(ActionItemDB).filter(
        ActionItemDB.status == ActionItemStatus.PENDING
    ).order_by(desc(ActionItemDB.confidence_score), desc(ActionItemDB.created_at)).all()
    
    return [ActionItem.from_orm(item) for item in items]


@router.get("/stats", response_model=ProcessingStats)
async def get_processing_stats(db: Session = Depends(get_database)):
    """Get processing statistics for today"""
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Count items created today
    action_items_today = db.query(ActionItemDB).filter(
        and_(
            ActionItemDB.created_at >= today,
            ActionItemDB.created_at < tomorrow
        )
    ).count()
    
    # Count pending items
    pending_items = db.query(ActionItemDB).filter(
        ActionItemDB.status == ActionItemStatus.PENDING
    ).count()
    
    # Count tasks created in Wrike today
    wrike_tasks_today = db.query(ActionItemDB).filter(
        and_(
            ActionItemDB.status == ActionItemStatus.CREATED,
            ActionItemDB.updated_at >= today,
            ActionItemDB.updated_at < tomorrow,
            ActionItemDB.wrike_task_id.isnot(None)
        )
    ).count()
    
    return ProcessingStats(
        emails_processed_today=0,  # TODO: Implement email tracking
        teams_messages_processed_today=0,  # TODO: Implement Teams tracking
        action_items_extracted_today=action_items_today,
        action_items_pending=pending_items,
        action_items_created_today=wrike_tasks_today,
        wrike_tasks_created_today=wrike_tasks_today
    )


@router.get("/{item_id}", response_model=ActionItem)
async def get_action_item(item_id: int, db: Session = Depends(get_database)):
    """Get a specific action item"""
    
    item = db.query(ActionItemDB).filter(ActionItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    return ActionItem.from_orm(item)


@router.put("/{item_id}", response_model=ActionItem)
async def update_action_item(
    item_id: int,
    update_data: ActionItemUpdate,
    db: Session = Depends(get_database)
):
    """Update an action item"""
    
    item = db.query(ActionItemDB).filter(ActionItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    item.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    
    return ActionItem.from_orm(item)


@router.post("/{item_id}/approve")
async def approve_action_item(item_id: int, db: Session = Depends(get_database)):
    """Approve an action item and create Wrike task"""
    
    item = db.query(ActionItemDB).filter(ActionItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    if item.status != ActionItemStatus.PENDING:
        raise HTTPException(status_code=400, detail="Action item is not pending")
    
    try:
        # Create Wrike task
        wrike = WrikeIntegrator()
        wrike_task = await wrike.create_task_from_action_item(ActionItem.from_orm(item))
        
        # Update action item
        item.status = ActionItemStatus.CREATED
        item.wrike_task_id = wrike_task.get('id')
        item.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Action item approved and Wrike task created", "wrike_task_id": wrike_task.get('id')}
        
    except Exception as e:
        # If Wrike creation fails, mark as approved but not created
        item.status = ActionItemStatus.APPROVED
        item.updated_at = datetime.utcnow()
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Failed to create Wrike task: {str(e)}")


@router.post("/{item_id}/reject")
async def reject_action_item(item_id: int, db: Session = Depends(get_database)):
    """Reject an action item"""
    
    item = db.query(ActionItemDB).filter(ActionItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    if item.status != ActionItemStatus.PENDING:
        raise HTTPException(status_code=400, detail="Action item is not pending")
    
    item.status = ActionItemStatus.REJECTED
    item.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Action item rejected"}


@router.delete("/{item_id}")
async def delete_action_item(item_id: int, db: Session = Depends(get_database)):
    """Delete an action item"""
    
    item = db.query(ActionItemDB).filter(ActionItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Action item deleted"}


@router.post("/batch/approve")
async def batch_approve_action_items(
    item_ids: List[int],
    db: Session = Depends(get_database)
):
    """Approve multiple action items at once"""
    
    success_count = 0
    errors = []
    
    for item_id in item_ids:
        try:
            item = db.query(ActionItemDB).filter(ActionItemDB.id == item_id).first()
            if not item:
                errors.append(f"Item {item_id} not found")
                continue
            
            if item.status != ActionItemStatus.PENDING:
                errors.append(f"Item {item_id} is not pending")
                continue
            
            # Create Wrike task
            wrike = WrikeIntegrator()
            wrike_task = await wrike.create_task_from_action_item(ActionItem.from_orm(item))
            
            # Update action item
            item.status = ActionItemStatus.CREATED
            item.wrike_task_id = wrike_task.get('id')
            item.updated_at = datetime.utcnow()
            
            success_count += 1
            
        except Exception as e:
            errors.append(f"Item {item_id}: {str(e)}")
    
    db.commit()
    
    return {
        "success_count": success_count,
        "total_requested": len(item_ids),
        "errors": errors
    }