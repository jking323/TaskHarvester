"""
Email Processing Service - Fetch and process emails from Microsoft Graph
"""
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import httpx

from ..models.auth_tokens import AuthToken, TokenProvider
from ..models.database import get_db_session
from .ai_processor_simple import AIProcessor, ActionItem


class EmailProcessor:
    """Service for fetching and processing emails from Microsoft Graph"""
    
    def __init__(self):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.ai_processor: Optional[AIProcessor] = None
    
    def set_ai_processor(self, ai_processor: AIProcessor):
        """Set the AI processor for action item extraction"""
        self.ai_processor = ai_processor
    
    async def _get_access_token(self, db_session) -> Optional[str]:
        """Get valid Microsoft Graph access token"""
        token = await AuthToken.get_valid_token(db_session, TokenProvider.MICROSOFT)
        return token.access_token if token else None
    
    async def _make_graph_request(self, endpoint: str, access_token: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Microsoft Graph API"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                params=params or {},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise Exception("Authentication failed - token may be expired")
            else:
                raise Exception(f"Microsoft Graph API error: {response.status_code} - {response.text}")
    
    async def get_recent_emails(
        self, 
        db_session, 
        days_back: int = 7, 
        max_emails: int = 50,
        filter_unread: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent emails from Microsoft Graph
        
        Args:
            db_session: Database session
            days_back: Number of days to look back for emails
            max_emails: Maximum number of emails to retrieve
            filter_unread: If True, only fetch unread emails
        
        Returns:
            List of email data dictionaries
        """
        access_token = await self._get_access_token(db_session)
        if not access_token:
            raise Exception("No valid Microsoft authentication found")
        
        # Build date filter
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        date_filter = f"receivedDateTime ge {cutoff_date.isoformat()}Z"
        
        # Add unread filter if requested
        if filter_unread:
            date_filter += " and isRead eq false"
        
        # Query parameters
        params = {
            "$filter": date_filter,
            "$select": "id,subject,from,toRecipients,receivedDateTime,body,isRead,importance",
            "$orderby": "receivedDateTime desc",
            "$top": max_emails
        }
        
        try:
            response = await self._make_graph_request("/me/messages", access_token, params)
            emails = response.get("value", [])
            
            print(f"📧 Retrieved {len(emails)} emails from the last {days_back} days")
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {str(e)}")
            raise
    
    async def get_email_content(self, email_id: str, db_session) -> Optional[str]:
        """
        Get the text content of a specific email
        
        Args:
            email_id: Microsoft Graph email ID
            db_session: Database session
            
        Returns:
            Email text content or None if error
        """
        access_token = await self._get_access_token(db_session)
        if not access_token:
            return None
        
        try:
            response = await self._make_graph_request(f"/me/messages/{email_id}", access_token)
            
            # Extract text content from body
            body = response.get("body", {})
            content_type = body.get("contentType", "").lower()
            content = body.get("content", "")
            
            if content_type == "html":
                # Simple HTML to text conversion (could be enhanced with BeautifulSoup)
                import re
                # Remove HTML tags
                text_content = re.sub(r'<[^>]+>', '', content)
                # Decode common HTML entities
                text_content = text_content.replace('&nbsp;', ' ').replace('&amp;', '&')
                text_content = text_content.replace('&lt;', '<').replace('&gt;', '>')
                return text_content.strip()
            else:
                return content.strip()
                
        except Exception as e:
            print(f"❌ Error getting email content for {email_id}: {str(e)}")
            return None
    
    async def process_emails_for_action_items(
        self, 
        db_session,
        days_back: int = 7,
        max_emails: int = 20,
        filter_unread: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch emails and extract action items using AI
        
        Args:
            db_session: Database session
            days_back: Number of days to look back
            max_emails: Maximum emails to process
            filter_unread: Only process unread emails
            
        Returns:
            List of emails with extracted action items
        """
        if not self.ai_processor or not self.ai_processor.is_initialized:
            raise Exception("AI processor not available")
        
        print(f"🔍 Processing emails for action items (last {days_back} days, max {max_emails})")
        
        # Fetch recent emails
        emails = await self.get_recent_emails(
            db_session, 
            days_back=days_back, 
            max_emails=max_emails,
            filter_unread=filter_unread
        )
        
        results = []
        processed_count = 0
        
        for email in emails:
            try:
                # Get email content
                email_id = email["id"]
                email_content = await self.get_email_content(email_id, db_session)
                
                if not email_content:
                    continue
                
                # Extract action items using AI
                action_items = await self.ai_processor.extract_action_items(
                    content=email_content,
                    source_type="email",
                    source_id=email_id
                )
                
                # Prepare result
                email_result = {
                    "email_id": email_id,
                    "subject": email["subject"],
                    "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                    "received_at": email["receivedDateTime"],
                    "is_read": email["isRead"],
                    "importance": email.get("importance", "normal"),
                    "content_length": len(email_content),
                    "action_items": [
                        {
                            "task": item.task,
                            "assignee": item.assignee,
                            "deadline": item.deadline,
                            "priority": item.priority,
                            "confidence": item.confidence,
                            "context": item.context
                        }
                        for item in action_items
                    ],
                    "action_item_count": len(action_items)
                }
                
                results.append(email_result)
                processed_count += 1
                
                if len(action_items) > 0:
                    print(f"📋 Found {len(action_items)} action items in email: {email['subject'][:50]}...")
                
            except Exception as e:
                print(f"❌ Error processing email {email.get('subject', 'Unknown')}: {str(e)}")
                continue
        
        total_action_items = sum(r["action_item_count"] for r in results)
        print(f"✅ Processed {processed_count} emails, found {total_action_items} total action items")
        
        return results
    
    async def get_email_folders(self, db_session) -> List[Dict[str, Any]]:
        """Get list of email folders/mailboxes"""
        access_token = await self._get_access_token(db_session)
        if not access_token:
            raise Exception("No valid Microsoft authentication found")
        
        try:
            response = await self._make_graph_request("/me/mailFolders", access_token)
            folders = response.get("value", [])
            
            return [
                {
                    "id": folder["id"],
                    "display_name": folder["displayName"],
                    "total_item_count": folder.get("totalItemCount", 0),
                    "unread_item_count": folder.get("unreadItemCount", 0)
                }
                for folder in folders
            ]
            
        except Exception as e:
            print(f"❌ Error fetching email folders: {str(e)}")
            raise
    
    async def mark_email_as_read(self, email_id: str, db_session) -> bool:
        """Mark an email as read"""
        access_token = await self._get_access_token(db_session)
        if not access_token:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/me/messages/{email_id}",
                    headers=headers,
                    json={"isRead": True},
                    timeout=10.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"❌ Error marking email as read: {str(e)}")
            return False