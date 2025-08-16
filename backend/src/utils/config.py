"""
Configuration management using Pydantic Settings
"""
import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "sqlite:///./action_items.db"
    
    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Microsoft Graph API
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None
    microsoft_redirect_uri: str = "http://localhost:8000/api/auth/callback"
    
    # Wrike API
    wrike_client_id: Optional[str] = None
    wrike_client_secret: Optional[str] = None
    wrike_redirect_uri: str = "http://localhost:8000/api/wrike/callback"
    
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings