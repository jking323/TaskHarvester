#!/bin/bash

echo "====================================="
echo "TaskHarvester Demo Startup Script"
echo "====================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Doppler is installed
if ! command -v doppler &> /dev/null; then
    echo -e "${RED}ERROR: Doppler CLI not found!${NC}"
    echo "Please install Doppler first:"
    echo "  Mac: brew install dopplerhq/cli/doppler"
    echo "  Linux: curl -Ls https://cli.doppler.com/install.sh | sudo sh"
    echo
    exit 1
fi

echo "[1/4] Checking Doppler authentication..."
if ! doppler configure get token &> /dev/null; then
    echo
    echo -e "${YELLOW}Please login to Doppler first:${NC}"
    echo "  doppler login"
    echo
    exit 1
fi
echo -e "${GREEN}✓ Doppler authenticated${NC}"

echo
echo "[2/4] Checking Ollama status..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "${RED}✗ Ollama not running!${NC}"
    echo
    echo "Please start Ollama in a separate terminal:"
    echo "  ollama serve"
    echo
    echo "Then ensure model is available:"
    echo "  ollama pull llama3.1:8b"
    echo
    exit 1
fi
echo -e "${GREEN}✓ Ollama is running${NC}"

echo
echo "[3/4] Setting up Python environment..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Python environment ready${NC}"

echo
echo "[4/4] Starting TaskHarvester with Doppler..."
echo
echo "====================================="
echo "Server starting at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "====================================="
echo

# Run with Doppler
doppler run -- python run_server.py