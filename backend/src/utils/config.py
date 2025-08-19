"""
Configuration management using Pydantic Settings
"""

import os
from typing import Optional, List
from pydantic import validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "sqlite:///./action_items.db"

    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Microsoft Graph API
    microsoft_client_id: Optional[str] = Field(
        None, description="Azure AD Application (client) ID"
    )
    microsoft_client_secret: Optional[str] = Field(
        None, description="Azure AD Client Secret"
    )
    microsoft_tenant_id: Optional[str] = Field(
        "common", description="Azure AD Tenant ID or 'common' for multi-tenant"
    )
    microsoft_redirect_uri: str = Field(
        "http://localhost:8000/api/auth/microsoft/callback",
        description="OAuth redirect URI registered in Azure AD",
    )
    microsoft_authority_url: Optional[str] = Field(
        None, description="Custom authority URL (auto-generated if not provided)"
    )

    # Wrike API
    wrike_client_id: Optional[str] = Field(
        None, description="Wrike Application Client ID"
    )
    wrike_client_secret: Optional[str] = Field(
        None, description="Wrike Application Client Secret"
    )
    wrike_redirect_uri: str = Field(
        "http://localhost:8000/api/auth/wrike/callback",
        description="Wrike OAuth redirect URI",
    )

    # AI Processing
    ai_confidence_threshold: float = 0.7
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # Processing Settings
    email_check_interval: int = 300  # 5 minutes
    teams_check_interval: int = 300  # 5 minutes
    max_content_length: int = 10000  # Max characters to process

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application
    debug: bool = False
    log_level: str = "INFO"

    @validator("microsoft_client_id")
    def validate_microsoft_client_id(cls, v):
        if v and len(v) < 30:
            raise ValueError("Microsoft Client ID appears to be invalid (too short)")
        return v

    @validator("microsoft_tenant_id")
    def validate_microsoft_tenant_id(cls, v):
        if v and v not in ["common", "organizations", "consumers"] and len(v) < 30:
            raise ValueError("Microsoft Tenant ID appears to be invalid")
        return v

    @validator("microsoft_redirect_uri", "wrike_redirect_uri")
    def validate_redirect_uris(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("Redirect URI must start with http:// or https://")
        return v

    def get_microsoft_authority(self) -> str:
        """Get the Microsoft authority URL"""
        if self.microsoft_authority_url:
            return self.microsoft_authority_url

        if self.microsoft_tenant_id in ["common", "organizations", "consumers"]:
            return f"https://login.microsoftonline.com/{self.microsoft_tenant_id}"
        else:
            return f"https://login.microsoftonline.com/{self.microsoft_tenant_id or 'common'}"

    def is_microsoft_configured(self) -> bool:
        """Check if Microsoft Graph authentication is properly configured"""
        # For PublicClientApplication, we only need client_id and redirect_uri
        return bool(self.microsoft_client_id and self.microsoft_redirect_uri)

    def is_wrike_configured(self) -> bool:
        """Check if Wrike authentication is properly configured"""
        return bool(
            self.wrike_client_id
            and self.wrike_client_secret
            and self.wrike_redirect_uri
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
