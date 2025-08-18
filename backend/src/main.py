"""
Action Item Extractor - Main FastAPI Application
"""
import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import auth, ai_test, email_processing  # OAuth testing, AI testing, and email processing
from .models.database import init_db
from .utils.config import get_settings
from .services.ai_processor_simple import AIProcessor
from .services.email_processor import EmailProcessor

# TODO: Import other modules when implemented
# from .api import outlook, teams, wrike, actions, settings
# from .services.background_tasks import BackgroundTaskManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("🚀 Starting TaskHarvester...")
    
    # Initialize database
    await init_db()
    
    # Initialize AI processor
    print("🤖 Initializing AI Processor...")
    ai_processor = AIProcessor()
    await ai_processor.initialize()
    app.state.ai_processor = ai_processor
    
    if ai_processor.is_initialized:
        print("✅ AI Processor ready for action item extraction")
    else:
        print("⚠️  AI Processor initialization incomplete - some features may be limited")
    
    # Initialize and configure email processor
    print("📧 Initializing Email Processor...")
    email_processor = EmailProcessor()
    email_processor.set_ai_processor(ai_processor)
    app.state.email_processor = email_processor
    
    # Set the email processor in the email_processing module
    email_processing.email_processor = email_processor
    print("✅ Email Processor configured with AI integration")
    
    # TODO: Start background task manager when implemented
    # task_manager = BackgroundTaskManager()
    # await task_manager.start()
    # app.state.task_manager = task_manager
    
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")
    # if hasattr(app.state, 'task_manager'):
    #     await app.state.task_manager.stop()
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
app.include_router(ai_test.router, prefix="/api/ai", tags=["ai-testing"])
app.include_router(email_processing.router, prefix="/api/emails", tags=["email-processing"])

# TODO: Include other routers when implemented
# app.include_router(outlook.router, prefix="/api/outlook", tags=["outlook"])
# app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
# app.include_router(wrike.router, prefix="/api/wrike", tags=["wrike"])
# app.include_router(actions.router, prefix="/api/actions", tags=["action-items"])
# app.include_router(settings.router, prefix="/api/settings", tags=["settings"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "TaskHarvester API", "status": "running", "version": "0.1.0"}

@app.get("/health")
async def simple_health():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        return {
            "status": "healthy",
            "oauth_ready": True,
            "version": "0.1.0-oauth-test"
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