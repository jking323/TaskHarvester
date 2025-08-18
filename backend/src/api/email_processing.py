"""
Email Processing API Routes - For testing email fetching and AI processing integration
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ..models.database import get_db_session
from ..services.email_processor import EmailProcessor


router = APIRouter()

# Global email processor instance
email_processor = EmailProcessor()


class EmailProcessingRequest(BaseModel):
    days_back: int = Field(7, description="Number of days to look back for emails", ge=1, le=30)
    max_emails: int = Field(20, description="Maximum number of emails to process", ge=1, le=100)
    filter_unread: bool = Field(True, description="Only process unread emails")


class EmailProcessingResponse(BaseModel):
    status: str
    message: str
    emails_processed: int
    total_action_items: int
    processing_time_ms: Optional[float] = None
    emails: List[Dict[str, Any]]


class EmailListResponse(BaseModel):
    status: str
    message: str
    email_count: int
    emails: List[Dict[str, Any]]


class EmailFoldersResponse(BaseModel):
    status: str
    folders: List[Dict[str, Any]]


def get_email_processor():
    """Get the email processor instance"""
    return email_processor


@router.get("/folders", response_model=EmailFoldersResponse)
async def get_email_folders(
    processor: EmailProcessor = Depends(get_email_processor),
    db_session = Depends(get_db_session)
):
    """Get list of email folders"""
    try:
        folders = await processor.get_email_folders(db_session)
        
        return EmailFoldersResponse(
            status="success",
            folders=folders
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email folders: {str(e)}")


@router.get("/recent", response_model=EmailListResponse)
async def get_recent_emails(
    days_back: int = Query(7, description="Number of days to look back", ge=1, le=30),
    max_emails: int = Query(50, description="Maximum emails to retrieve", ge=1, le=200),
    filter_unread: bool = Query(False, description="Only fetch unread emails"),
    processor: EmailProcessor = Depends(get_email_processor),
    db_session = Depends(get_db_session)
):
    """Fetch recent emails without AI processing"""
    try:
        emails = await processor.get_recent_emails(
            db_session=db_session,
            days_back=days_back,
            max_emails=max_emails,
            filter_unread=filter_unread
        )
        
        # Format emails for response
        formatted_emails = []
        for email in emails:
            formatted_emails.append({
                "id": email["id"],
                "subject": email["subject"],
                "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "received_at": email["receivedDateTime"],
                "is_read": email["isRead"],
                "importance": email.get("importance", "normal"),
                "has_body": bool(email.get("body", {}).get("content"))
            })
        
        return EmailListResponse(
            status="success",
            message=f"Retrieved {len(emails)} emails from the last {days_back} days",
            email_count=len(emails),
            emails=formatted_emails
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")


@router.post("/process-for-actions", response_model=EmailProcessingResponse)
async def process_emails_for_actions(
    request: EmailProcessingRequest,
    processor: EmailProcessor = Depends(get_email_processor),
    db_session = Depends(get_db_session)
):
    """Process emails for action item extraction using AI"""
    try:
        # Get AI processor from app state (will be set during startup)
        # For now, we'll need to handle this in the main app integration
        
        # Time the processing
        import time
        start_time = time.time()
        
        # Process emails
        results = await processor.process_emails_for_action_items(
            db_session=db_session,
            days_back=request.days_back,
            max_emails=request.max_emails,
            filter_unread=request.filter_unread
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Calculate totals
        total_action_items = sum(r["action_item_count"] for r in results)
        
        return EmailProcessingResponse(
            status="success",
            message=f"Processed {len(results)} emails and found {total_action_items} action items",
            emails_processed=len(results),
            total_action_items=total_action_items,
            processing_time_ms=processing_time,
            emails=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process emails for actions: {str(e)}")


@router.get("/content/{email_id}")
async def get_email_content(
    email_id: str,
    processor: EmailProcessor = Depends(get_email_processor),
    db_session = Depends(get_db_session)
):
    """Get the text content of a specific email"""
    try:
        content = await processor.get_email_content(email_id, db_session)
        
        if content is None:
            raise HTTPException(status_code=404, detail="Email content not found")
        
        return {
            "status": "success",
            "email_id": email_id,
            "content": content,
            "content_length": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email content: {str(e)}")


@router.post("/mark-read/{email_id}")
async def mark_email_as_read(
    email_id: str,
    processor: EmailProcessor = Depends(get_email_processor),
    db_session = Depends(get_db_session)
):
    """Mark an email as read"""
    try:
        success = await processor.mark_email_as_read(email_id, db_session)
        
        if success:
            return {
                "status": "success",
                "message": f"Email {email_id} marked as read"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to mark email as read")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark email as read: {str(e)}")


@router.get("/test-connection")
async def test_email_connection(
    processor: EmailProcessor = Depends(get_email_processor),
    db_session = Depends(get_db_session)
):
    """Test email processing connection and authentication"""
    try:
        # Test by fetching a small number of recent emails
        emails = await processor.get_recent_emails(
            db_session=db_session,
            days_back=1,
            max_emails=5,
            filter_unread=False
        )
        
        return {
            "status": "success",
            "message": "Email connection successful",
            "test_email_count": len(emails),
            "authentication": "valid"
        }
        
    except Exception as e:
        error_msg = str(e)
        if "Authentication failed" in error_msg:
            return {
                "status": "error",
                "message": "Authentication failed - please re-authenticate with Microsoft",
                "authentication": "invalid"
            }
        else:
            return {
                "status": "error",
                "message": f"Connection test failed: {error_msg}",
                "authentication": "unknown"
            }