"""
Wrike Integration Service - Create tasks from action items
"""
import asyncio
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import httpx

from ..models.auth_tokens import AuthToken, TokenProvider
from ..models.database import get_db_session
from ..models.action_items import ActionItem, ActionItemPriority
from ..utils.config import get_settings


class WrikeIntegration:
    """Service for integrating with Wrike task management"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://www.wrike.com/api/v4"
        
    async def _get_access_token(self, db_session) -> Optional[str]:
        """Get valid Wrike access token"""
        token = await AuthToken.get_valid_token(db_session, TokenProvider.WRIKE)
        return token.access_token if token else None
    
    def _map_priority_to_wrike(self, priority: str) -> str:
        """Map TaskHarvester priority to Wrike importance"""
        priority_map = {
            ActionItemPriority.LOW: "Low",
            ActionItemPriority.MEDIUM: "Normal", 
            ActionItemPriority.HIGH: "High",
            ActionItemPriority.URGENT: "High"
        }
        return priority_map.get(priority, "Normal")
    
    async def create_task_from_action_item(
        self, 
        action_item: ActionItem, 
        db_session,
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a Wrike task from an ActionItem (simulated for demo)"""
        
        # For demo purposes, we'll simulate task creation
        # In production, this would make actual Wrike API calls
        
        # Simulate task creation
        task_id = f"wrike_task_{action_item.id}_{int(datetime.utcnow().timestamp())}"
        
        # Update action item with simulated Wrike data
        action_item.wrike_task_id = task_id
        action_item.external_url = f"https://www.wrike.com/open.htm?id={task_id}"
        
        db_session.commit()
        
        print(f"[WRIKE] Simulated task creation for action item {action_item.id}: '{action_item.task[:50]}...'")
        
        return {
            "id": task_id,
            "title": action_item.task[:140],
            "status": "Active",
            "importance": self._map_priority_to_wrike(action_item.priority),
            "url": f"https://www.wrike.com/open.htm?id={task_id}"
        }
    
    async def sync_action_items_to_wrike(
        self,
        db_session,
        action_item_ids: Optional[List[int]] = None,
        confidence_threshold: float = 0.7,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Sync action items to Wrike tasks"""
        
        # Build query for action items to sync
        query = db_session.query(ActionItem)\
                          .filter(ActionItem.wrike_task_id.is_(None))\
                          .filter(ActionItem.confidence >= confidence_threshold)
        
        if action_item_ids:
            query = query.filter(ActionItem.id.in_(action_item_ids))
        
        action_items = query.limit(limit).all()
        
        if not action_items:
            return {
                "message": "No action items found to sync",
                "synced_count": 0,
                "failed_count": 0,
                "tasks_created": []
            }
        
        # Sync each action item
        synced_count = 0
        failed_count = 0
        tasks_created = []
        
        for action_item in action_items:
            try:
                task = await self.create_task_from_action_item(action_item, db_session)
                if task.get("id"):
                    synced_count += 1
                    tasks_created.append({
                        "action_item_id": action_item.id,
                        "wrike_task_id": task["id"],
                        "task_title": task.get("title", ""),
                        "task_url": task.get("url", "")
                    })
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                print(f"[ERROR] Failed to sync action item {action_item.id} to Wrike: {e}")
        
        return {
            "message": f"Synced {synced_count} action items to Wrike",
            "synced_count": synced_count,
            "failed_count": failed_count,
            "tasks_created": tasks_created
        }
    
    async def get_sync_candidates(
        self,
        db_session,
        confidence_threshold: float = 0.7,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """Get action items that are candidates for Wrike sync"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        candidates = db_session.query(ActionItem)\
                              .filter(ActionItem.wrike_task_id.is_(None))\
                              .filter(ActionItem.confidence >= confidence_threshold)\
                              .filter(ActionItem.created_at >= cutoff_date)\
                              .order_by(ActionItem.confidence.desc())\
                              .limit(50)\
                              .all()
        
        return [
            {
                "id": item.id,
                "task": item.task,
                "assignee": item.assignee,
                "priority": item.priority,
                "confidence": item.confidence,
                "source_type": item.source_type,
                "source_subject": item.source_subject,
                "created_at": item.created_at.isoformat()
            }
            for item in candidates
        ]