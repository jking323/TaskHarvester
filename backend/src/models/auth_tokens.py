"""
Authentication Token Models

Handles storage and management of OAuth tokens for Microsoft Graph and Wrike APIs.
"""
import enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Boolean
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from .database import Base

class TokenProvider(str, enum.Enum):
    """Supported OAuth providers"""
    MICROSOFT = "microsoft"
    WRIKE = "wrike"

class AuthToken(Base):
    """OAuth token storage"""
    __tablename__ = "auth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(Enum(TokenProvider), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="Bearer")
    expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)  # Space-separated scopes
    
    # User information
    user_id = Column(String(255), nullable=True, index=True)  # Provider user ID
    user_email = Column(String(255), nullable=True, index=True)
    user_name = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    @classmethod
    async def store_token(
        cls,
        session: Session,
        provider: TokenProvider,
        token_data: Dict[str, Any],
        user_info: Optional[Dict[str, Any]] = None
    ) -> "AuthToken":
        """Store or update an OAuth token"""
        
        # Calculate expiration time
        expires_at = None
        if "expires_in" in token_data:
            expires_at = datetime.utcnow() + timedelta(seconds=int(token_data["expires_in"]))
        elif "expires_at" in token_data:
            expires_at = datetime.fromtimestamp(token_data["expires_at"])
        
        # Extract user information
        user_id = None
        user_email = None
        user_name = None
        
        if user_info:
            if provider == TokenProvider.MICROSOFT:
                user_id = user_info.get("id")
                user_email = user_info.get("mail") or user_info.get("userPrincipalName")
                user_name = user_info.get("displayName")
            elif provider == TokenProvider.WRIKE:
                user_id = user_info.get("id")
                user_email = user_info.get("primaryEmail")
                user_name = f"{user_info.get('firstName', '')} {user_info.get('lastName', '')}".strip()
        
        # Check if token already exists for this provider
        existing_token = session.query(cls).filter(
            cls.provider == provider,
            cls.is_active == True
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = token_data["access_token"]
            existing_token.refresh_token = token_data.get("refresh_token")
            existing_token.token_type = token_data.get("token_type", "Bearer")
            existing_token.expires_at = expires_at
            existing_token.scope = token_data.get("scope")
            existing_token.updated_at = datetime.utcnow()
            
            # Update user info if provided
            if user_info:
                existing_token.user_id = user_id
                existing_token.user_email = user_email
                existing_token.user_name = user_name
            
            session.commit()
            session.refresh(existing_token)
            return existing_token
        else:
            # Create new token
            new_token = cls(
                provider=provider,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_type=token_data.get("token_type", "Bearer"),
                expires_at=expires_at,
                scope=token_data.get("scope"),
                user_id=user_id,
                user_email=user_email,
                user_name=user_name
            )
            
            session.add(new_token)
            session.commit()
            session.refresh(new_token)
            return new_token
    
    @classmethod
    async def get_valid_token(
        cls,
        session: Session,
        provider: TokenProvider,
        buffer_minutes: int = 5
    ) -> Optional["AuthToken"]:
        """Get a valid (non-expired) token for the provider"""
        
        token = session.query(cls).filter(
            cls.provider == provider,
            cls.is_active == True
        ).first()
        
        if not token:
            return None
        
        # Check if token is expired (with buffer)
        if token.expires_at:
            buffer_time = datetime.utcnow() + timedelta(minutes=buffer_minutes)
            if token.expires_at <= buffer_time:
                # Token is expired or will expire soon
                if token.refresh_token:
                    # Try to refresh the token
                    try:
                        if provider == TokenProvider.MICROSOFT:
                            from ..api.auth import ms_auth
                            new_token_data = await ms_auth.refresh_token(token.refresh_token)
                        elif provider == TokenProvider.WRIKE:
                            from ..api.auth import wrike_auth
                            new_token_data = await wrike_auth.refresh_token(token.refresh_token)
                        else:
                            return None
                        
                        # Update token with refreshed data
                        return await cls.store_token(session, provider, new_token_data)
                        
                    except Exception:
                        # Refresh failed, mark token as inactive
                        token.is_active = False
                        session.commit()
                        return None
                else:
                    # No refresh token, mark as inactive
                    token.is_active = False
                    session.commit()
                    return None
        
        return token
    
    @classmethod
    async def revoke_token(cls, session: Session, provider: TokenProvider) -> bool:
        """Revoke (deactivate) a token for a provider"""
        token = session.query(cls).filter(
            cls.provider == provider,
            cls.is_active == True
        ).first()
        
        if token:
            token.is_active = False
            session.commit()
            return True
        
        return False
    
    def is_expired(self, buffer_minutes: int = 5) -> bool:
        """Check if the token is expired"""
        if not self.expires_at:
            return False
        
        buffer_time = datetime.utcnow() + timedelta(minutes=buffer_minutes)
        return self.expires_at <= buffer_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary"""
        return {
            "id": self.id,
            "provider": self.provider.value,
            "token_type": self.token_type,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "scope": self.scope,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_name": self.user_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "is_expired": self.is_expired()
        }