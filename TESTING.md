# TaskHarvester Testing Guide

## Quick Start Testing

### Prerequisites
- Python 3.13+ installed
- Node.js 18+ installed  
- Ollama installed with llama3.1:8b model

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn[standard] python-multipart msal msgraph-core requests httpx sqlalchemy alembic pydantic python-dotenv cryptography beautifulsoup4 python-dateutil pytest pytest-asyncio ollama
python -m src.main
```

Backend will start on http://127.0.0.1:8000

### Frontend Setup
```bash
cd desktop
npm install
npm start  # Start webpack dev server
npm run electron-dev  # Start Electron app
```

## Testing Status ✅

### ✅ Working Components
- **Backend API Server**: FastAPI running on port 8000
- **Database**: SQLite with action_items table created
- **AI Processor**: Ollama + Llama 3.1 8B integration ready
- **Frontend**: Electron + React UI loads successfully  
- **API Communication**: Frontend ↔ Backend connectivity established
- **Core Endpoints**:
  - `GET /api/` - API root (200 OK)
  - `GET /api/health` - Health check (200 OK)
  - `GET /api/dashboard/stats` - Dashboard stats (200 OK)
  - `GET /api/tasks/` - Task listing (200 OK, returns empty list)
  - `GET /api/auth/status` - Auth status (200 OK)
  - `GET /api/ai/status` - AI status (200 OK)

### 🟡 Pending Components
- **OAuth Flow**: Microsoft Graph authentication (ready but untested)
- **AI Inference**: Working but slow on laptop (test on powerful machine)
- **Email Processing**: Backend ready, needs OAuth tokens

### ⚙️ Architecture Verified
- **Frontend**: Electron + React + Webpack dev server
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **AI**: Ollama + Llama 3.1 8B (local processing)
- **Communication**: HTTP API calls over IPv4

## Key Insights

`★ Insight ─────────────────────────────────────`
**Database Model Integration**: Fixed SQLAlchemy table creation by ensuring all models import from the shared `Base` in `database.py` rather than creating separate declarative bases.

**IPv6 vs IPv4 Resolution**: Resolved connectivity issues by explicitly using `127.0.0.1` instead of `localhost` to force IPv4 resolution in the Electron app.

**FastAPI Auto-reload**: Leveraged uvicorn's file watching for rapid development iteration during database schema fixes.
`─────────────────────────────────────────────────`

## Current System State

- **Backend**: Running and stable on http://127.0.0.1:8000
- **Database**: `action_items.db` created with proper schema
- **Frontend**: Loading with professional UI, making successful API calls
- **Processes**: 3 background processes (backend, webpack, electron)

## Next Steps for Production Testing
1. Test OAuth authentication with real Microsoft account
2. Test AI inference on more powerful hardware
3. Test email processing pipeline
4. Add sample data for UI testing
5. Test task creation and management workflows

## Known Issues
- **System Tray**: Missing tray icon file (non-critical)
- **AI Performance**: Inference slow on laptop (expected, use powerful machine)

*Last Updated: 2025-08-19*
*Status: ✅ READY FOR TESTING*