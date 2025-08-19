@echo off
echo =====================================
echo TaskHarvester Demo Startup Script
echo =====================================
echo.

REM Check if Doppler is installed
where doppler >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Doppler CLI not found!
    echo Please install Doppler first:
    echo   - Download: https://github.com/DopplerHQ/cli/releases
    echo   - Or use Scoop: scoop install doppler
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Doppler authentication...
doppler configure get token >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Please login to Doppler first:
    echo   doppler login
    echo.
    pause
    exit /b 1
)
echo ✓ Doppler authenticated

echo.
echo [2/4] Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>nul
if %errorlevel% neq 0 (
    echo ✗ Ollama not running!
    echo.
    echo Please start Ollama in a separate terminal:
    echo   ollama serve
    echo.
    echo Then ensure model is available:
    echo   ollama pull llama3.1:8b
    echo.
    pause
    exit /b 1
)
echo ✓ Ollama is running

echo.
echo [3/4] Setting up Python environment...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install -q -r requirements.txt
echo ✓ Python environment ready

echo.
echo [4/4] Starting TaskHarvester with Doppler...
echo.
echo =====================================
echo Server starting at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo =====================================
echo.

REM Run with Doppler
doppler run -- python run_server.py

pause