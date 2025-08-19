"""
Authentication API Routes
"""
import os
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode, parse_qs, urlparse

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import msal
import httpx

from ..utils.config import get_settings
from ..models.database import get_db_session
from ..models.auth_tokens import AuthToken, TokenProvider

router = APIRouter()

# Pydantic models
class AuthStatusResponse(BaseModel):
    microsoft_authenticated: bool
    wrike_authenticated: bool
    microsoft_user: Optional[Dict[str, Any]] = None
    wrike_user: Optional[Dict[str, Any]] = None
    microsoft_scopes: Optional[List[str]] = None
    wrike_scopes: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

class AuthUrlResponse(BaseModel):
    auth_url: str
    state: str
    code_verifier: str = Field(..., description="PKCE code verifier for security")

class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = "Bearer"
    scope: Optional[str] = None
    refresh_token: Optional[str] = None

class AuthCallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: str = Field(..., description="PKCE code verifier")

# In-memory state storage (in production, use Redis)
_oauth_states: Dict[str, Dict[str, Any]] = {}

# Microsoft Graph configuration
class MSGraphAuth:
    def __init__(self):
        self.settings = get_settings()
        self.client_id = self.settings.microsoft_client_id
        # For PublicClientApplication, we don't use client_secret
        # self.client_secret = self.settings.microsoft_client_secret
        self.tenant_id = self.settings.microsoft_tenant_id or "common"  # Support multi-tenant
        self.redirect_uri = self.settings.microsoft_redirect_uri
        
        # Microsoft Graph scopes for action item extraction
        # Note: offline_access is handled automatically by MSAL
        self.scopes = [
            "https://graph.microsoft.com/User.Read",  # Basic user info
            "https://graph.microsoft.com/Mail.Read",  # Read emails
            "https://graph.microsoft.com/Mail.ReadWrite",  # Manage email flags/categories
            "https://graph.microsoft.com/Calendars.Read",  # Read calendar events
            # Teams scopes (add these after testing basic functionality)
            # "https://graph.microsoft.com/ChannelMessage.Read.All",  # Teams channel messages
            # "https://graph.microsoft.com/Chat.Read",  # Teams chat messages
            # "https://graph.microsoft.com/Team.ReadBasic.All",  # Teams basic info
            # "https://graph.microsoft.com/CallRecords.Read.All",  # Teams meeting transcripts
            # "https://graph.microsoft.com/OnlineMeetings.Read",  # Teams meeting details
        ]
        
        # Support both single-tenant and multi-tenant
        if self.tenant_id == "common":
            self.authority = "https://login.microsoftonline.com/common"
        else:
            self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            
        # Use PublicClientApplication for Electron/desktop apps
        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority
        )
    
    def _generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge for enhanced security"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge
    
    def _store_oauth_state(self, state: str, code_verifier: str, scopes: List[str]) -> None:
        """Store OAuth state for validation (use Redis in production)"""
        _oauth_states[state] = {
            "code_verifier": code_verifier,
            "scopes": scopes,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)  # 10-minute expiry
        }
    
    def _validate_and_get_oauth_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Validate and retrieve OAuth state"""
        state_data = _oauth_states.get(state)
        if not state_data:
            return None
        
        # Check if state has expired
        if datetime.utcnow() > state_data["expires_at"]:
            _oauth_states.pop(state, None)
            return None
        
        return state_data
    
    def get_auth_url(self, custom_scopes: Optional[List[str]] = None) -> tuple[str, str, str]:
        """Generate Microsoft OAuth authorization URL with PKCE"""
        # Use custom scopes if provided, otherwise use default
        scopes = custom_scopes if custom_scopes else self.scopes
        
        # Generate secure state and PKCE parameters
        state = secrets.token_urlsafe(32)
        code_verifier, code_challenge = self._generate_pkce_pair()
        
        # Store state for later validation
        self._store_oauth_state(state, code_verifier, scopes)
        
        # Build authorization URL with PKCE
        auth_url = self.app.get_authorization_request_url(
            scopes=scopes,
            redirect_uri=self.redirect_uri,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method="S256"
        )
        
        return auth_url, state, code_verifier
    
    async def exchange_code_for_token(self, code: str, state: str, code_verifier: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        # Validate state parameter
        state_data = self._validate_and_get_oauth_state(state)
        if not state_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired state parameter"
            )
        
        # Clean up used state
        _oauth_states.pop(state, None)
        
        # Exchange code for token (MSAL handles PKCE internally)
        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=state_data["scopes"],
            redirect_uri=self.redirect_uri
        )
        
        if "error" in result:
            error_desc = result.get('error_description', 'Unknown error')
            error_code = result.get('error', 'unknown_error')
            raise HTTPException(
                status_code=400,
                detail=f"Microsoft OAuth error ({error_code}): {error_desc}"
            )
        
        return result
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        # Try to get accounts from cache first
        accounts = self.app.get_accounts()
        
        if accounts:
            # Use silent token acquisition if account is cached
            result = self.app.acquire_token_silent(
                scopes=self.scopes,
                account=accounts[0]
            )
            if result and "access_token" in result:
                return result
        
        # Fallback to refresh token flow
        try:
            result = self.app.acquire_token_by_refresh_token(
                refresh_token=refresh_token,
                scopes=self.scopes
            )
            
            if "error" in result:
                error_desc = result.get('error_description', 'Unknown error')
                raise HTTPException(
                    status_code=401,
                    detail=f"Token refresh failed: {error_desc}"
                )
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Failed to refresh Microsoft token: {str(e)}"
            )
    
    def validate_scopes(self, required_scopes: List[str], granted_scopes: str) -> bool:
        """Validate that all required scopes were granted"""
        granted_list = granted_scopes.split(' ') if granted_scopes else []
        return all(scope in granted_list for scope in required_scopes)
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get detailed user information from Microsoft Graph"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get("https://graph.microsoft.com/v1.0/me", headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get user info: {response.text}"
                )
            
            return response.json()

# Wrike OAuth configuration
class WrikeAuth:
    def __init__(self):
        self.settings = get_settings()
        self.client_id = self.settings.wrike_client_id
        self.client_secret = self.settings.wrike_client_secret
        self.redirect_uri = "http://localhost:8000/api/auth/wrike/callback"
        self.auth_base_url = "https://login.wrike.com/oauth2/authorize/v4"
        self.token_url = "https://login.wrike.com/oauth2/token"
        self.scopes = ["wsReadWrite"]
    
    def get_auth_url(self, state: str) -> str:
        """Generate Wrike OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state
        }
        return f"{self.auth_base_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to acquire Wrike token: {response.text}"
                )
            
            return response.json()
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired Wrike access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to refresh Wrike token: {response.text}"
                )
            
            return response.json()

# Global auth instances
try:
    ms_auth = MSGraphAuth()
except Exception as e:
    print(f"Warning: Failed to initialize Microsoft Graph auth: {str(e)}")
    ms_auth = None

try:
    wrike_auth = WrikeAuth()
except Exception as e:
    print(f"Warning: Failed to initialize Wrike auth: {str(e)}")
    wrike_auth = None

@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(db_session = Depends(get_db_session)):
    """Check authentication status for all services"""
    try:
        # Check Microsoft authentication
        ms_token = await AuthToken.get_valid_token(db_session, TokenProvider.MICROSOFT)
        ms_authenticated = ms_token is not None
        ms_user = None
        ms_scopes = None
        
        if ms_authenticated:
            # Get user info and scopes
            try:
                ms_user = {
                    "id": ms_token.user_id,
                    "displayName": ms_token.user_name,
                    "mail": ms_token.user_email,
                    "userPrincipalName": ms_token.user_email
                }
                ms_scopes = ms_token.scope.split(' ') if ms_token.scope else []
                
                # Verify token is still valid by making a test call
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {ms_token.access_token}"}
                    response = await client.get("https://graph.microsoft.com/v1.0/me", headers=headers)
                    if response.status_code != 200:
                        # Token might be invalid, mark as not authenticated
                        ms_authenticated = False
                        ms_user = None
                        ms_scopes = None
            except Exception:
                # If we can't verify the token, mark as not authenticated
                ms_authenticated = False
                ms_user = None
                ms_scopes = None
        
        # Check Wrike authentication
        wrike_token = await AuthToken.get_valid_token(db_session, TokenProvider.WRIKE)
        wrike_authenticated = wrike_token is not None
        wrike_user = None
        wrike_scopes = None
        
        if wrike_authenticated:
            # Get user info and scopes
            try:
                wrike_user = {
                    "id": wrike_token.user_id,
                    "firstName": wrike_token.user_name.split(' ')[0] if wrike_token.user_name else None,
                    "lastName": ' '.join(wrike_token.user_name.split(' ')[1:]) if wrike_token.user_name and ' ' in wrike_token.user_name else None,
                    "primaryEmail": wrike_token.user_email
                }
                wrike_scopes = wrike_token.scope.split(' ') if wrike_token.scope else []
                
                # Verify token is still valid
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {wrike_token.access_token}"}
                    response = await client.get("https://www.wrike.com/api/v4/contacts?me=true", headers=headers)
                    if response.status_code != 200:
                        wrike_authenticated = False
                        wrike_user = None
                        wrike_scopes = None
            except Exception:
                wrike_authenticated = False
                wrike_user = None
                wrike_scopes = None
        
        return AuthStatusResponse(
            microsoft_authenticated=ms_authenticated,
            wrike_authenticated=wrike_authenticated,
            microsoft_user=ms_user,
            wrike_user=wrike_user,
            microsoft_scopes=ms_scopes,
            wrike_scopes=wrike_scopes,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check auth status: {str(e)}")

@router.get("/microsoft/admin-consent")
async def microsoft_admin_consent():
    """Generate admin consent URL for Microsoft Graph permissions"""
    try:
        if not ms_auth:
            raise HTTPException(status_code=500, detail="Microsoft Graph authentication not configured")
        
        # Build admin consent URL
        params = {
            "client_id": ms_auth.client_id,
            "response_type": "code",
            "redirect_uri": ms_auth.redirect_uri,
            "scope": " ".join(ms_auth.scopes),
            "response_mode": "query",
            "prompt": "admin_consent"
        }
        
        admin_consent_url = f"{ms_auth.authority}/adminconsent?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        return {
            "admin_consent_url": admin_consent_url,
            "instructions": "Admin must visit this URL to grant consent for the application",
            "required_scopes": ms_auth.scopes,
            "tenant_id": ms_auth.tenant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate admin consent URL: {str(e)}")

@router.get("/microsoft/login", response_model=AuthUrlResponse)
async def microsoft_login(scopes: Optional[str] = None):
    """Initiate Microsoft OAuth flow with optional custom scopes"""
    try:
        # Parse custom scopes if provided
        custom_scopes = None
        if scopes:
            custom_scopes = [scope.strip() for scope in scopes.split(',')]
            # Validate custom scopes
            valid_scopes = {
                "https://graph.microsoft.com/User.Read",
                "https://graph.microsoft.com/Mail.Read",
                "https://graph.microsoft.com/Mail.ReadWrite",
                "https://graph.microsoft.com/Calendars.Read",
                "https://graph.microsoft.com/ChannelMessage.Read.All",
                "https://graph.microsoft.com/Chat.Read",
                "https://graph.microsoft.com/Team.ReadBasic.All",
                "https://graph.microsoft.com/CallRecords.Read.All",
                "https://graph.microsoft.com/OnlineMeetings.Read",
                "offline_access"
            }
            
            invalid_scopes = set(custom_scopes) - valid_scopes
            if invalid_scopes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid scopes: {', '.join(invalid_scopes)}"
                )
        
        # Generate OAuth URL with PKCE
        auth_url, state, code_verifier = ms_auth.get_auth_url(custom_scopes)
        
        return AuthUrlResponse(
            auth_url=auth_url,
            state=state,
            code_verifier=code_verifier
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Microsoft auth URL: {str(e)}")

@router.post("/microsoft/callback")
async def microsoft_callback(
    callback_data: AuthCallbackRequest,
    db_session = Depends(get_db_session)
):
    """Handle Microsoft OAuth callback with PKCE validation"""
    
    try:
        # Exchange code for token with PKCE validation
        token_data = await ms_auth.exchange_code_for_token(
            code=callback_data.code,
            state=callback_data.state,
            code_verifier=callback_data.code_verifier
        )
        
        # Get detailed user information
        user_info = None
        if "access_token" in token_data:
            try:
                user_info = await ms_auth.get_user_info(token_data["access_token"])
            except Exception as e:
                # Log the error but continue - user info is not critical
                print(f"Warning: Failed to get user info: {str(e)}")
        
        # Validate that required scopes were granted
        granted_scopes = token_data.get("scope", "")
        required_scopes = [
            "https://graph.microsoft.com/User.Read",
            "https://graph.microsoft.com/Mail.Read"
        ]
        
        if not ms_auth.validate_scopes(required_scopes, granted_scopes):
            raise HTTPException(
                status_code=400,
                detail=f"Required scopes not granted. Granted: {granted_scopes}"
            )
        
        # Store the token
        stored_token = await AuthToken.store_token(
            session=db_session,
            provider=TokenProvider.MICROSOFT,
            token_data=token_data,
            user_info=user_info
        )
        
        # Return detailed success response
        return {
            "message": "Microsoft authentication successful",
            "user": {
                "displayName": user_info.get("displayName") if user_info else "Unknown User",
                "email": user_info.get("mail") or user_info.get("userPrincipalName") if user_info else None,
                "id": user_info.get("id") if user_info else None
            },
            "scopes": granted_scopes.split(' ') if granted_scopes else [],
            "token_expires_at": stored_token.expires_at.isoformat() if stored_token.expires_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete Microsoft authentication: {str(e)}")

@router.get("/microsoft/callback")
async def microsoft_callback_get(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None
):
    """Handle Microsoft OAuth callback via GET (for browser redirects)"""
    
    # Check for OAuth errors
    if error:
        return {
            "error": error,
            "error_description": error_description,
            "message": "Microsoft OAuth failed. Please try again."
        }
    
    if not code or not state:
        return {
            "error": "missing_parameters",
            "message": "Missing required parameters. Please restart the authentication process."
        }
    
    # Return the parameters for the frontend to handle
    return {
        "code": code,
        "state": state,
        "message": "Authentication code received. Please complete the process in the application."
    }

@router.get("/wrike/login", response_model=AuthUrlResponse)
async def wrike_login():
    """Initiate Wrike OAuth flow"""
    try:
        # Generate a secure random state parameter
        state = secrets.token_urlsafe(32)
        
        auth_url = wrike_auth.get_auth_url(state)
        
        return AuthUrlResponse(auth_url=auth_url, state=state)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Wrike auth URL: {str(e)}")

@router.get("/wrike/callback")
async def wrike_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db_session = Depends(get_db_session)
):
    """Handle Wrike OAuth callback"""
    
    # Check for OAuth errors
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Wrike OAuth error: {error_description or error}"
        )
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is required")
    
    if not state:
        raise HTTPException(status_code=400, detail="State parameter is required")
    
    try:
        # Exchange code for token
        token_data = await wrike_auth.exchange_code_for_token(code, state)
        
        # Get user information
        user_info = None
        if "access_token" in token_data:
            try:
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                    response = await client.get("https://www.wrike.com/api/v4/contacts?me=true", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("data"):
                            user_info = data["data"][0]
            except Exception:
                pass  # Continue without user info if this fails
        
        # Store the token
        await AuthToken.store_token(
            session=db_session,
            provider=TokenProvider.WRIKE,
            token_data=token_data,
            user_info=user_info
        )
        
        # Return success response
        return {
            "message": "Wrike authentication successful",
            "user": f"{user_info.get('firstName', '')} {user_info.get('lastName', '')}".strip() if user_info else "Unknown User"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete Wrike authentication: {str(e)}")

@router.delete("/microsoft/logout")
async def microsoft_logout(db_session = Depends(get_db_session)):
    """Revoke Microsoft authentication"""
    try:
        success = await AuthToken.revoke_token(db_session, TokenProvider.MICROSOFT)
        
        if success:
            return {"message": "Microsoft authentication revoked successfully"}
        else:
            return {"message": "No active Microsoft authentication found"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke Microsoft authentication: {str(e)}")

@router.delete("/wrike/logout")
async def wrike_logout(db_session = Depends(get_db_session)):
    """Revoke Wrike authentication"""
    try:
        success = await AuthToken.revoke_token(db_session, TokenProvider.WRIKE)
        
        if success:
            return {"message": "Wrike authentication revoked successfully"}
        else:
            return {"message": "No active Wrike authentication found"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke Wrike authentication: {str(e)}")

@router.post("/test-connection")
async def test_connection(
    provider: str,
    db_session = Depends(get_db_session)
):
    """Test API connection for a provider"""
    
    if provider not in ["microsoft", "wrike"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Must be 'microsoft' or 'wrike'")
    
    try:
        token_provider = TokenProvider.MICROSOFT if provider == "microsoft" else TokenProvider.WRIKE
        token = await AuthToken.get_valid_token(db_session, token_provider)
        
        if not token:
            raise HTTPException(status_code=401, detail=f"No valid {provider} token found")
        
        # Test the connection
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token.access_token}"}
            
            if provider == "microsoft":
                # Test Microsoft Graph API
                response = await client.get("https://graph.microsoft.com/v1.0/me", headers=headers)
                test_url = "https://graph.microsoft.com/v1.0/me"
            else:
                # Test Wrike API
                response = await client.get("https://www.wrike.com/api/v4/contacts?me=true", headers=headers)
                test_url = "https://www.wrike.com/api/v4/contacts?me=true"
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"{provider.title()} API connection successful",
                    "test_url": test_url,
                    "response_status": response.status_code
                }
            else:
                return {
                    "status": "error",
                    "message": f"{provider.title()} API connection failed",
                    "test_url": test_url,
                    "response_status": response.status_code,
                    "error": response.text
                }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test {provider} connection: {str(e)}")

@router.get("/tokens")
async def get_tokens(db_session = Depends(get_db_session)):
    """Get information about stored tokens (without sensitive data)"""
    try:
        tokens = db_session.query(AuthToken).filter(AuthToken.is_active == True).all()
        
        return {
            "tokens": [
                {
                    "provider": token.provider.value,
                    "user_name": token.user_name,
                    "user_email": token.user_email,
                    "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                    "is_expired": token.is_expired(),
                    "created_at": token.created_at.isoformat(),
                    "scope": token.scope
                }
                for token in tokens
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get token information: {str(e)}")