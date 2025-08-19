@echo off
echo ============================================
echo   TaskHarvester - Starting All Services
echo ============================================
echo.

:: Check if running as administrator (optional, remove if not needed)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Warning: Not running as administrator. Some features may be limited.
    echo.
)

:: Set the base directory
cd /d "%~dp0"

echo [1/4] Starting Backend API Server...
echo ---------------------------------------
start "TaskHarvester Backend" cmd /k "cd backend && doppler run -- python -m src.main"
timeout /t 3 /nobreak >nul

echo [2/4] Starting React Frontend...
echo ---------------------------------------
start "TaskHarvester Frontend" cmd /k "cd desktop && npm start"
timeout /t 5 /nobreak >nul

echo [3/4] Checking Ollama AI Service...
echo ---------------------------------------
:: Check if Ollama is running
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Ollama is already running.
) else (
    echo Starting Ollama...
    start "Ollama" ollama serve
    timeout /t 3 /nobreak >nul
)

echo [4/4] Launching Electron Desktop App...
echo ---------------------------------------
timeout /t 2 /nobreak >nul
start "TaskHarvester App" cmd /k "cd desktop && set NODE_ENV=development && npm run electron-dev"

echo.
echo ============================================
echo   All services started successfully!
echo ============================================
echo.
echo Services running:
echo   - Backend API:    http://localhost:8000
echo   - React Frontend: http://localhost:3001
echo   - Electron App:   Launching...
echo   - Ollama AI:      http://localhost:11434
echo.
echo Press any key to close this window (services will continue running)...
pause >nul