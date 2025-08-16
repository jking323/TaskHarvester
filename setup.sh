#!/bin/bash

echo "🚀 Setting up Action Item Extractor..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if Redis is available
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis not found. Installing Redis..."
    # Platform-specific Redis installation
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "Please install Redis for Windows manually."
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install redis
    else
        sudo apt-get update && sudo apt-get install redis-server
    fi
fi

echo "📦 Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate || venv\Scripts\activate
pip install -r requirements.txt

echo "🤖 Setting up AI models..."
# Install spaCy model
python -m spacy download en_core_web_sm

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "🦙 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Pull Llama model (this will take a while)
echo "📥 Downloading Llama 3.1 8B model (this may take 20-30 minutes)..."
ollama pull llama3.1:8b

cd ..

echo "🖥️  Installing desktop app dependencies..."
cd desktop
npm install
cd ..

echo "⚙️  Creating configuration files..."
# Create environment file
cat > backend/.env << EOF
# Database
DATABASE_URL=sqlite:///./action_items.db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Microsoft Graph API (configure these in the app)
MICROSOFT_CLIENT_ID=your_client_id_here
MICROSOFT_CLIENT_SECRET=your_client_secret_here
MICROSOFT_TENANT_ID=your_tenant_id_here

# Wrike API (configure these in the app)
WRIKE_CLIENT_ID=your_wrike_client_id_here
WRIKE_CLIENT_SECRET=your_wrike_client_secret_here

# AI Settings
AI_CONFIDENCE_THRESHOLD=0.7
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Processing Settings
EMAIL_CHECK_INTERVAL=300
TEAMS_CHECK_INTERVAL=300
MAX_CONTENT_LENGTH=10000

# Security
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=false
LOG_LEVEL=INFO
EOF

echo "🎯 Creating startup scripts..."
# Create Windows startup script
cat > start-windows.bat << 'EOF'
@echo off
echo Starting Action Item Extractor...

echo Starting Redis...
start redis-server

echo Starting Ollama...
start ollama serve

echo Starting backend...
cd backend
venv\Scripts\activate
start python src/main.py

echo Starting desktop app...
cd ..\desktop
start npm start

echo All services started!
pause
EOF

# Create Unix startup script
cat > start-unix.sh << 'EOF'
#!/bin/bash
echo "Starting Action Item Extractor..."

echo "Starting Redis..."
redis-server --daemonize yes

echo "Starting Ollama..."
ollama serve &

echo "Starting backend..."
cd backend
source venv/bin/activate
python src/main.py &

echo "Starting desktop app..."
cd ../desktop
npm start &

echo "All services started!"
echo "Press Ctrl+C to stop all services"
wait
EOF

chmod +x start-unix.sh

echo "✅ Setup complete!"
echo ""
echo "🎉 Action Item Extractor is ready to use!"
echo ""
echo "Next steps:"
echo "1. Configure your Microsoft and Wrike API credentials in the app"
echo "2. Run the application:"
echo "   - Windows: double-click start-windows.bat"
echo "   - Mac/Linux: ./start-unix.sh"
echo ""
echo "3. Open the desktop app and complete the setup wizard"
echo ""
echo "📚 For detailed setup instructions, see the README.md file"