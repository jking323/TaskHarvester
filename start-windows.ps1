# TaskHarvester Startup Script for Windows
# Run with: powershell -ExecutionPolicy Bypass -File start-windows.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  TaskHarvester - Starting All Services" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Function to check if a port is in use
function Test-Port {
    param($Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# 1. Start Backend API
Write-Host "[1/4] Starting Backend API Server..." -ForegroundColor Yellow
Write-Host "---------------------------------------"
if (Test-Port 8000) {
    Write-Host "Backend already running on port 8000" -ForegroundColor Green
} else {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; doppler run -- python -m src.main" -WindowStyle Normal
    Start-Sleep -Seconds 3
}

# 2. Start React Frontend
Write-Host "[2/4] Starting React Frontend..." -ForegroundColor Yellow
Write-Host "---------------------------------------"
if (Test-Port 3001) {
    Write-Host "Frontend already running on port 3001" -ForegroundColor Green
} else {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd desktop; npm start" -WindowStyle Normal
    Start-Sleep -Seconds 5
}

# 3. Check/Start Ollama
Write-Host "[3/4] Checking Ollama AI Service..." -ForegroundColor Yellow
Write-Host "---------------------------------------"
$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
if ($ollamaProcess) {
    Write-Host "Ollama is already running" -ForegroundColor Green
} else {
    Write-Host "Starting Ollama..." -ForegroundColor White
    try {
        Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        Write-Host "Ollama started successfully" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Could not start Ollama. Make sure it's installed." -ForegroundColor Red
        Write-Host "Install from: https://ollama.ai" -ForegroundColor Yellow
    }
}

# 4. Launch Electron App
Write-Host "[4/4] Launching Electron Desktop App..." -ForegroundColor Yellow
Write-Host "---------------------------------------"
Start-Sleep -Seconds 2
$env:NODE_ENV = "development"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd desktop; `$env:NODE_ENV='development'; npm run electron-dev" -WindowStyle Normal

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All services started successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services running:" -ForegroundColor Cyan
Write-Host "  - Backend API:    http://localhost:8000" -ForegroundColor White
Write-Host "  - React Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "  - Electron App:   Launching..." -ForegroundColor White
Write-Host "  - Ollama AI:      http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close this window (services will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")