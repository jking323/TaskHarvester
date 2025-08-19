@echo off
echo ============================================
echo   TaskHarvester - Stopping All Services
echo ============================================
echo.

echo Stopping Electron app...
taskkill /F /IM electron.exe 2>nul

echo Stopping Node.js processes (React frontend)...
taskkill /F /IM node.exe 2>nul

echo Stopping Python backend...
taskkill /F /IM python.exe 2>nul

echo Stopping Ollama (keeping it running for other apps)...
:: Uncomment the next line if you want to stop Ollama too
:: taskkill /F /IM ollama.exe 2>nul

echo.
echo All TaskHarvester services stopped.
echo.
pause