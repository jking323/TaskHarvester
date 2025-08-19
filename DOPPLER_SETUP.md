# Doppler Setup for TaskHarvester

## Quick Setup

### 1. Install Doppler CLI

**Windows (using Scoop):**
```powershell
# Install Scoop if you don't have it
iwr -useb get.scoop.sh | iex

# Install Doppler
scoop bucket add doppler https://github.com/DopplerHQ/scoop-doppler.git
scoop install doppler
```

**Windows (Manual):**
1. Download from: https://github.com/DopplerHQ/cli/releases
2. Extract and add to PATH

**Mac:**
```bash
brew install dopplerhq/cli/doppler
```

**Linux:**
```bash
curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sudo sh
```

### 2. Login to Doppler
```bash
doppler login
```

### 3. Setup Project
```bash
# Navigate to project root
cd TaskHarvester

# Setup Doppler for this project
doppler setup

# Select:
# - Project: taskharvester (or create new)
# - Config: dev (for development)
```

### 4. Verify Connection
```bash
# List all secrets
doppler secrets

# Get a specific secret
doppler secrets get MICROSOFT_CLIENT_ID
```

## Running the Application with Doppler

### Backend Server
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run with Doppler
doppler run -- python -m uvicorn src.main:app --reload --port 8000

# Or use the shortcut script (create one)
doppler run -- python run_server.py
```

### Alternative: Export to .env (for local testing)
```bash
# Export current config to .env file
doppler secrets download --no-file --format env > backend/.env

# Then run normally
python -m uvicorn src.main:app --reload
```

## Required Secrets in Doppler

Add these secrets to your Doppler project:

### Microsoft Graph API
- `MICROSOFT_CLIENT_ID` - Azure AD Application ID
- `MICROSOFT_CLIENT_SECRET` - Azure AD Client Secret  
- `MICROSOFT_TENANT_ID` - Azure AD Tenant ID (or 'common')
- `MICROSOFT_REDIRECT_URI` - http://localhost:8000/api/auth/microsoft/callback

### Wrike API (Optional for now)
- `WRIKE_CLIENT_ID` - Wrike App Client ID
- `WRIKE_CLIENT_SECRET` - Wrike App Secret
- `WRIKE_REDIRECT_URI` - http://localhost:8000/api/auth/wrike/callback

### AI Configuration
- `AI_CONFIDENCE_THRESHOLD` - 0.7
- `OLLAMA_HOST` - http://localhost:11434
- `OLLAMA_MODEL` - llama3.1:8b

### Database
- `DATABASE_URL` - sqlite:///./action_items.db

### Security
- `SECRET_KEY` - (generate a secure random key)
- `ALGORITHM` - HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES` - 30

### Application
- `DEBUG` - true (for development)
- `LOG_LEVEL` - INFO

## Using Doppler in Python

The existing `config.py` already uses pydantic-settings which automatically reads from environment variables. Doppler injects secrets as environment variables when you use `doppler run`, so no code changes needed!

## CI/CD Integration

For GitHub Actions:
```yaml
- name: Install Doppler CLI
  uses: dopplerhq/cli-action@v2
  
- name: Run with secrets
  run: doppler run -- python test.py
  env:
    DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
```

## Troubleshooting

### "doppler: command not found"
- Ensure Doppler is in your PATH
- Restart terminal after installation

### "Unable to fetch secrets"
- Run `doppler login` to authenticate
- Check project selection: `doppler setup`

### "Secret not found"
- List all secrets: `doppler secrets`
- Add missing secret: `doppler secrets set SECRET_NAME`