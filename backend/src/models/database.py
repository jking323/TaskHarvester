"""
Database configuration and initialization
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Create base class for models
Base = declarative_base()
from ..utils.config import get_settings

settings = get_settings()

# Database URL
DATABASE_URL = settings.database_url or "sqlite:///./action_items.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def init_db():
    """Initialize database tables"""
    # Import all models to ensure they're registered with Base
    from . import auth_tokens, action_items
    
    Base.metadata.create_all(bind=engine)
    print("Database initialized")


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database dependency for FastAPI
async def get_database():
    """Async database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get database session (sync version for compatibility)"""
    return SessionLocal()