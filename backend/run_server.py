#!/usr/bin/env python
"""
Run the TaskHarvester backend server
Can be used with Doppler: doppler run -- python run_server.py
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Run the FastAPI server"""
    
    # Get configuration from environment (Doppler or .env)
    host = os.getenv("SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("DEBUG", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"Starting TaskHarvester Backend Server")
    print(f"Server: http://{host}:{port}")
    print(f"API Docs: http://{host}:{port}/docs")
    print(f"Debug Mode: {reload}")
    print(f"Log Level: {log_level}")
    
    # Check for critical environment variables
    critical_vars = [
        "MICROSOFT_CLIENT_ID",
        "MICROSOFT_CLIENT_SECRET",
        "OLLAMA_HOST"
    ]
    
    missing_vars = []
    for var in critical_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("\nWarning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nTip: Use 'doppler run -- python run_server.py' to inject secrets")
        print("   Or set them in backend/.env file")
    else:
        print("All critical environment variables found")
    
    # Run the server
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )

if __name__ == "__main__":
    main()