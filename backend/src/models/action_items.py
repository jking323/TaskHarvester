"""
Action Item Database Models
"""
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from .database import Base


class ActionItemStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActionItemPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ActionItem(Base):
    """Action item model for storing extracted tasks"""
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core task information
    task = Column(Text, nullable=False, index=True)
    assignee = Column(String(255), nullable=True, index=True)
    deadline = Column(String(255), nullable=True)  # Store as string initially, can be parsed later
    priority = Column(String(20), nullable=False, default=ActionItemPriority.MEDIUM)
    status = Column(String(20), nullable=False, default=ActionItemStatus.PENDING)
    
    # AI extraction metadata
    confidence = Column(Float, nullable=False, default=0.0)
    context = Column(Text, nullable=True)  # Additional context from the source
    
    # Source information
    source_type = Column(String(50), nullable=False)  # "email", "teams", "calendar", etc.
    source_id = Column(String(255), nullable=False, index=True)  # Original source ID (email ID, etc.)
    source_subject = Column(Text, nullable=True)  # Email subject, meeting title, etc.
    source_sender = Column(String(255), nullable=True)  # Email sender, meeting organizer, etc.
    source_date = Column(DateTime, nullable=True)  # When the source was created
    
    # Task management
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Integration tracking
    wrike_task_id = Column(String(255), nullable=True, index=True)  # Wrike task ID if synced
    wrike_folder_id = Column(String(255), nullable=True)  # Wrike folder ID
    external_url = Column(Text, nullable=True)  # Link to external task (Wrike, etc.)
    
    # User and organization (for multi-tenant support)
    user_id = Column(String(255), nullable=True, index=True)  # Microsoft user ID
    tenant_id = Column(String(255), nullable=True, index=True)  # Azure tenant ID
    
    def __repr__(self):
        return f"<ActionItem(id={self.id}, task='{self.task[:50]}...', status='{self.status}')>"
    
    @classmethod
    def create_from_ai_result(
        cls,
        task: str,
        assignee: Optional[str],
        deadline: Optional[str],
        priority: str,
        confidence: float,
        context: str,
        source_type: str,
        source_id: str,
        source_subject: Optional[str] = None,
        source_sender: Optional[str] = None,
        source_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> 'ActionItem':
        """Create ActionItem from AI extraction result"""
        return cls(
            task=task,
            assignee=assignee,
            deadline=deadline,
            priority=priority,
            confidence=confidence,
            context=context,
            source_type=source_type,
            source_id=source_id,
            source_subject=source_subject,
            source_sender=source_sender,
            source_date=source_date,
            user_id=user_id,
            tenant_id=tenant_id
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "task": self.task,
            "assignee": self.assignee,
            "deadline": self.deadline,
            "priority": self.priority,
            "status": self.status,
            "confidence": self.confidence,
            "context": self.context,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "source_subject": self.source_subject,
            "source_sender": self.source_sender,
            "source_date": self.source_date.isoformat() if self.source_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "wrike_task_id": self.wrike_task_id,
            "external_url": self.external_url,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id
        }


class ActionItemComment(Base):
    """Comments and notes on action items"""
    __tablename__ = "action_item_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    action_item_id = Column(Integer, ForeignKey("action_items.id"), nullable=False, index=True)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(255), nullable=True)  # User ID who added the comment
    
    # Relationship
    action_item = relationship("ActionItem", backref="comments")


class ProcessingLog(Base):
    """Log of email/content processing for debugging and analytics"""
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source information
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(255), nullable=False, index=True)
    source_subject = Column(Text, nullable=True)
    
    # Processing details
    processed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processing_duration = Column(Float, nullable=True)  # seconds
    action_items_found = Column(Integer, nullable=False, default=0)
    high_confidence_items = Column(Integer, nullable=False, default=0)
    
    # AI model information
    ai_model_used = Column(String(100), nullable=True)
    confidence_threshold = Column(Float, nullable=True)
    
    # Results
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    
    # User context
    user_id = Column(String(255), nullable=True, index=True)
    tenant_id = Column(String(255), nullable=True, index=True)