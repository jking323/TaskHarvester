"""
Action Item Models - Pydantic and SQLAlchemy models
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"


class ActionItemStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CREATED = "created"
    ARCHIVED = "archived"


class SourceType(str, Enum):
    EMAIL = "email"
    TEAMS_MESSAGE = "teams_message"
    MEETING_TRANSCRIPT = "meeting_transcript"


# SQLAlchemy Models
class ActionItemDB(Base):
    """SQLAlchemy model for action items"""
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False)
    source_type = Column(String(50), nullable=False)
    task_description = Column(Text, nullable=False)
    assignee_email = Column(String(255))
    deadline = Column(DateTime)
    priority = Column(String(20), default="medium")
    confidence_score = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    context = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    wrike_task_id = Column(String(255))
    

class EmailDB(Base):
    """SQLAlchemy model for emails"""
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, nullable=False)
    subject = Column(Text)
    body = Column(Text)
    sender_email = Column(String(255))
    received_at = Column(DateTime)
    processed_at = Column(DateTime)
    source_type = Column(String(50), default="outlook")


class TeamsMessageDB(Base):
    """SQLAlchemy model for Teams messages"""
    __tablename__ = "teams_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, nullable=False)
    channel_id = Column(String(255))
    content = Column(Text)
    author_email = Column(String(255))
    created_at = Column(DateTime)
    processed_at = Column(DateTime)
    message_type = Column(String(50))  # 'chat', 'meeting_transcript'


class UserMappingDB(Base):
    """SQLAlchemy model for user mappings"""
    __tablename__ = "user_mappings"
    
    email = Column(String(255), primary_key=True)
    wrike_user_id = Column(String(255))
    display_name = Column(String(255))
    is_active = Column(Boolean, default=True)


# Pydantic Models for API
class ActionItemBase(BaseModel):
    """Base action item model"""
    task_description: str = Field(..., min_length=1, max_length=1000)
    assignee_email: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Priority = Priority.MEDIUM
    context: Optional[str] = None


class ActionItemCreate(ActionItemBase):
    """Model for creating action items"""
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    source_id: Optional[int] = None
    source_type: Optional[SourceType] = None


class ActionItemUpdate(BaseModel):
    """Model for updating action items"""
    task_description: Optional[str] = None
    assignee_email: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[Priority] = None
    status: Optional[ActionItemStatus] = None
    context: Optional[str] = None
    wrike_task_id: Optional[str] = None


class ActionItem(ActionItemBase):
    """Full action item model with database fields"""
    id: int
    source_id: Optional[int] = None
    source_type: Optional[SourceType] = None
    confidence_score: float
    status: ActionItemStatus
    created_at: datetime
    updated_at: datetime
    wrike_task_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class ActionItemWithSource(ActionItem):
    """Action item with source content included"""
    source_content: Optional[str] = None
    source_subject: Optional[str] = None


# Email Models
class EmailBase(BaseModel):
    """Base email model"""
    message_id: str
    subject: Optional[str] = None
    body: Optional[str] = None
    sender_email: Optional[str] = None
    received_at: Optional[datetime] = None


class EmailCreate(EmailBase):
    """Model for creating emails"""
    source_type: str = "outlook"


class Email(EmailBase):
    """Full email model"""
    id: int
    processed_at: Optional[datetime] = None
    source_type: str
    
    class Config:
        from_attributes = True


# Teams Message Models
class TeamsMessageBase(BaseModel):
    """Base Teams message model"""
    message_id: str
    channel_id: Optional[str] = None
    content: Optional[str] = None
    author_email: Optional[str] = None
    created_at: Optional[datetime] = None
    message_type: Optional[str] = None


class TeamsMessageCreate(TeamsMessageBase):
    """Model for creating Teams messages"""
    pass


class TeamsMessage(TeamsMessageBase):
    """Full Teams message model"""
    id: int
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# User Mapping Models
class UserMappingBase(BaseModel):
    """Base user mapping model"""
    email: str
    wrike_user_id: Optional[str] = None
    display_name: Optional[str] = None
    is_active: bool = True


class UserMappingCreate(UserMappingBase):
    """Model for creating user mappings"""
    pass


class UserMapping(UserMappingBase):
    """Full user mapping model"""
    
    class Config:
        from_attributes = True


# Response Models
class ActionItemsResponse(BaseModel):
    """Response model for action items list"""
    items: list[ActionItem]
    total: int
    page: int
    size: int


class ProcessingStats(BaseModel):
    """Model for processing statistics"""
    emails_processed_today: int
    teams_messages_processed_today: int
    action_items_extracted_today: int
    action_items_pending: int
    action_items_created_today: int
    wrike_tasks_created_today: int