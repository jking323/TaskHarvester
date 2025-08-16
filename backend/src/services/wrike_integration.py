"""
Wrike Integration Service
"""
from typing import Dict, List, Optional
import httpx
from datetime import datetime

from ..models.action_item import ActionItem
from ..utils.config import get_settings


class WrikeIntegrator:
    """Service for integrating with Wrike API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_base = "https://www.wrike.com/api/v4"
        self.access_token = None  # TODO: Implement OAuth flow
        
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Wrike API"""
        if not self.access_token:
            # TODO: Get access token from settings/database
            raise ValueError("Wrike access token not configured")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def map_priority(self, priority: str) -> str:
        """Map priority to Wrike importance level"""
        priority_mapping = {
            "low": "Low",
            "medium": "Normal", 
            "high": "High"
        }
        return priority_mapping.get(priority, "Normal")
    
    def map_user(self, assignee_email: str) -> str:
        """Map email to Wrike user ID"""
        # TODO: Implement user mapping lookup
        # For now, return email as-is
        return assignee_email
    
    async def create_task_from_action_item(self, action_item: ActionItem) -> Dict:
        """Create a Wrike task from an action item"""
        
        # Prepare task data
        task_data = {
            "title": action_item.task_description[:200],  # Wrike title limit
            "description": self._build_task_description(action_item),
            "status": "Active",
            "importance": self.map_priority(action_item.priority),
        }
        
        # Add deadline if present
        if action_item.deadline:
            task_data["dates"] = {
                "due": action_item.deadline.isoformat(),
                "type": "Planned"
            }
        
        # Add assignee if present
        if action_item.assignee_email:
            task_data["responsibleIds"] = [self.map_user(action_item.assignee_email)]
        
        # Add custom fields
        task_data["customFields"] = [
            {"id": "IEAAAQKAJUAACTET", "value": str(action_item.confidence_score)},  # Confidence
            {"id": "IEAAAQKAJUAACTET", "value": action_item.source_type or "email"},  # Source
            {"id": "IEAAAQKAJUAACTET", "value": "true"}  # Auto-generated flag
        ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/tasks",
                    headers=self._get_headers(),
                    json=task_data,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("data", [{}])[0] if result.get("data") else {}
                
        except httpx.HTTPError as e:
            raise Exception(f"Failed to create Wrike task: {e}")
    
    def _build_task_description(self, action_item: ActionItem) -> str:
        """Build detailed task description"""
        lines = [
            f"**Auto-extracted Action Item**",
            f"",
            f"**Task:** {action_item.task_description}",
            f"**Source:** {action_item.source_type or 'Unknown'}",
            f"**Confidence:** {action_item.confidence_score:.2f}",
            f"**Extracted:** {action_item.created_at.strftime('%Y-%m-%d %H:%M')}",
        ]
        
        if action_item.context:
            lines.extend([
                f"",
                f"**Context:**",
                action_item.context
            ])
        
        if action_item.assignee_email:
            lines.append(f"**Assigned to:** {action_item.assignee_email}")
        
        return "\n".join(lines)
    
    async def get_folders(self) -> List[Dict]:
        """Get available Wrike folders for task assignment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/folders",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("data", [])
                
        except httpx.HTTPError as e:
            raise Exception(f"Failed to get Wrike folders: {e}")
    
    async def get_users(self) -> List[Dict]:
        """Get Wrike users for mapping"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/contacts",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("data", [])
                
        except httpx.HTTPError as e:
            raise Exception(f"Failed to get Wrike users: {e}")
    
    async def test_connection(self) -> bool:
        """Test Wrike API connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/version",
                    headers=self._get_headers(),
                    timeout=10.0
                )
                return response.status_code == 200
                
        except Exception:
            return False