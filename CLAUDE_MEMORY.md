# TaskHarvester - Claude Memory File
*Last Updated: August 20, 2025*

## 🎯 **Current Status & Next Steps**

### **Where We Left Off**
We just successfully completed a major CI/CD infrastructure overhaul and the PR has been merged to main. The application is in a **fully functional state** with:

- ✅ **Complete CI/CD Pipeline** - All tests passing (Frontend, Backend, Security)
- ✅ **OAuth Integration** - Microsoft Graph authentication working
- ✅ **Native UI** - Professional React-based task management interface
- ✅ **AI Processing** - Ollama + Llama 3.1 8B integration for action item extraction
- ✅ **Cross-platform Support** - Windows builds configured

### **Ready for Testing Phase**
The user mentioned they want to test on their **test PC**, suggesting we're moving from development to validation/testing phase.

## 🏗️ **Architecture Overview**

### **Tech Stack**
- **Frontend**: Electron + React + Webpack (Node.js 22)
- **Backend**: Python FastAPI + SQLite + Ollama
- **AI**: Local Llama 3.1 8B model via Ollama
- **Auth**: Microsoft Graph OAuth with PKCE security
- **CI/CD**: GitHub Actions with comprehensive testing

### **Key Components**
1. **Desktop App**: `/desktop/` - Electron React app with professional UI
2. **Backend API**: `/backend/` - FastAPI server with AI processing
3. **CI/CD**: `/.github/workflows/` - Complete testing & release pipeline
4. **Documentation**: `/docs/` - Comprehensive setup guides

## 🚀 **Application Features**

### **Currently Working**
- **OAuth Authentication**: Microsoft Graph integration with secure PKCE flow
- **Task Management**: Native UI for viewing/managing action items
- **AI Processing**: Extract action items from emails/content with confidence scoring
- **Cross-platform**: Windows builds (x64, ia32) with NSIS installer

### **Mock Data Demo**
The app currently shows **mock action items** to demonstrate:
- AI confidence scoring (High/Medium/Low indicators)
- Professional Discord/Slack-inspired design
- Task categorization and filtering
- Dashboard with statistics

## 🔧 **Development Environment**

### **Prerequisites on Test PC**
```bash
# Required installations:
- Node.js 22+ (for frontend)
- Python 3.11+ (for backend)
- Ollama (for AI processing)
- Git (for repository access)

# Optional but recommended:
- Doppler CLI (for environment management)
- VSCode (with Claude Code extension)
```

### **Quick Setup Commands**
```bash
# 1. Clone and setup
git clone https://github.com/jking323/TaskHarvester.git
cd TaskHarvester

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt

# 3. Frontend setup
cd ../desktop
npm install

# 4. Start Ollama (separate terminal)
ollama serve
ollama pull llama3.1:8b

# 5. Run application
# Terminal 1: Backend
cd backend && python src/main.py
# Terminal 2: Frontend
cd desktop && npm run electron-dev
```

## 🛠️ **Build & Release**

### **Available Commands**
```bash
# Development
npm run electron-dev          # Run Electron in development mode
npm run start                 # Webpack dev server only
python src/main.py            # Backend API server

# Building
npm run build                 # Production build + Electron packaging
npm run build:win             # Windows-specific build

# Testing & Quality
npm run lint                  # ESLint for frontend
npm test                      # Jest tests
black src/                    # Python code formatting
flake8 src/                   # Python linting
pytest tests/                 # Python tests
```

### **CI/CD Status**
- **Automated Testing**: ✅ Passing on all PRs
- **Dev Releases**: ✅ Auto-deploy on main branch pushes  
- **Prod Releases**: ✅ Manual trigger for v0.1.0+
- **Multi-platform**: ✅ Linux, Windows, macOS builds
- **Security**: ✅ CodeQL, Trivy, GitGuardian scans

## 📋 **Known Issues & Considerations**

### **Areas Needing Attention**
1. **Integration Tests**: Currently skipped (need database setup)
2. **Real Email Processing**: Currently using mock data
3. **Wrike Integration**: Temporarily removed (was in original scope)
4. **Error Handling**: Could be enhanced for production readiness

### **Recent Changes (August 19-20, 2025)**
- ✅ Fixed all CI pipeline failures
- ✅ Added comprehensive linting configurations
- ✅ Updated to Node.js 22
- ✅ Implemented Windows build support
- ✅ Created proper testing infrastructure

## 🎯 **Likely Next Steps**

### **Testing Phase**
Since you're moving to test PC, likely priorities:
1. **End-to-End Testing**: Verify OAuth flow works on test environment
2. **Email Integration**: Connect real Microsoft Graph email processing
3. **Performance Testing**: Test with actual AI model and real data
4. **User Experience**: Validate UI/UX with real workflows

### **Production Readiness**
1. **Environment Configuration**: Set up production environment variables
2. **Database Migration**: Move from SQLite to production database
3. **Security Hardening**: Review and enhance security measures
4. **Documentation**: User guides and deployment instructions

## 🔐 **Configuration Notes**

### **Environment Variables**
```bash
# Microsoft Graph OAuth (required)
MICROSOFT_CLIENT_ID=your_azure_app_id
MICROSOFT_TENANT_ID=common  # or specific tenant
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/auth/microsoft/callback

# AI Processing
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
AI_CONFIDENCE_THRESHOLD=0.7

# Database
DATABASE_URL=sqlite:///./action_items.db

# Security
SECRET_KEY=your-secret-key-change-in-production
```

### **OAuth Setup Required**
- Azure AD App Registration with:
  - Redirect URI: `http://localhost:8000/api/auth/microsoft/callback`
  - Permissions: User.Read, Mail.Read, Mail.ReadWrite, Calendars.Read
  - Public client enabled for PKCE

## 💡 **Development Tips**

### **Debugging**
- Backend logs: Check console output from `python src/main.py`
- Frontend logs: Open DevTools in Electron app (Ctrl+Shift+I)
- CI logs: Check GitHub Actions tab for detailed pipeline info

### **Common Commands**
```bash
# Reset development environment
git clean -xdf && git reset --hard HEAD

# Update dependencies
cd desktop && npm update
cd backend && pip install -r requirements.txt --upgrade

# Check CI status
gh pr status  # (if GitHub CLI installed)
```

## 📞 **Contact & Support**

When resuming work:
1. **Current Branch**: `main` (clean, all features merged)
2. **Application State**: Fully functional with mock data
3. **CI/CD**: All pipelines working and validated
4. **Ready For**: Real-world testing and validation

---

*This memory file ensures seamless continuation of TaskHarvester development across different environments and sessions.*