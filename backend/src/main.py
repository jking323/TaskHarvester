"""
Action Item Extractor - Main FastAPI Application
"""
import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import auth, outlook, teams, wrike, actions, settings
from .services.ai_processor import AIProcessor
from .services.background_tasks import BackgroundTaskManager
from .models.database import init_db
from .utils.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("🚀 Starting Action Item Extractor...")
    
    # Initialize database
    await init_db()
    
    # Initialize AI processor
    ai_processor = AIProcessor()
    await ai_processor.initialize()
    app.state.ai_processor = ai_processor
    
    # Start background task manager
    task_manager = BackgroundTaskManager()
    await task_manager.start()
    app.state.task_manager = task_manager
    
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")
    if hasattr(app.state, 'task_manager'):
        await app.state.task_manager.stop()
    print("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Action Item Extractor API",
    description="Intelligent action item extraction from Outlook and Teams",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Electron app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(outlook.router, prefix="/api/outlook", tags=["outlook"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(wrike.router, prefix="/api/wrike", tags=["wrike"])
app.include_router(actions.router, prefix="/api/actions", tags=["action-items"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Action Item Extractor API", "status": "running"}


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check AI processor
        ai_status = "ready" if hasattr(app.state, 'ai_processor') else "not_ready"
        
        # Check background tasks
        task_status = "running" if hasattr(app.state, 'task_manager') else "stopped"
        
        return {
            "status": "healthy",
            "ai_processor": ai_status,
            "background_tasks": task_status,
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )