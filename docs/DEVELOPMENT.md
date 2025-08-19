# Development Guide

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ (for Electron frontend)
- **Python** 3.11+ (for FastAPI backend)
- **Ollama** with Llama 3.1 8B model
- **Doppler CLI** for environment management
- **Git** for version control

### Setup Development Environment

1. **Clone and Setup**
   ```bash
   git clone https://github.com/jking323/TaskHarvester.git
   cd TaskHarvester
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd desktop
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Install Doppler CLI
   curl -Ls https://cli.doppler.com/install.sh | sh
   
   # Configure environment
   doppler login
   doppler setup
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   doppler run -- python -m src.main
   
   # Terminal 2: Frontend
   cd desktop
   npm start
   
   # Terminal 3: Electron
   cd desktop
   npm run electron-dev
   ```

## 🏗️ Architecture Overview

### Frontend (Electron + React)
```
desktop/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.jsx      # Main app layout
│   │   ├── Login.jsx       # OAuth authentication
│   │   ├── TaskCard.jsx    # Task display component
│   │   └── ...
│   ├── pages/              # Main application pages
│   │   └── Dashboard.jsx   # Dashboard view
│   ├── styles/             # CSS stylesheets
│   │   ├── design-system.css  # Design tokens
│   │   └── components.css     # Component styles
│   ├── main.js             # Electron main process
│   ├── preload.js          # Electron preload script
│   └── App.jsx             # React root component
├── public/                 # Static assets
├── webpack.config.js       # Webpack configuration
└── package.json           # Dependencies and scripts
```

### Backend (FastAPI + SQLite)
```
backend/
├── src/
│   ├── api/                # API route definitions
│   │   ├── auth.py         # Authentication routes
│   │   ├── action_items.py # Task management
│   │   └── ...
│   ├── models/             # Database models
│   │   ├── database.py     # SQLite configuration
│   │   └── action_items.py # Task data models
│   ├── services/           # Business logic
│   │   ├── ai_processor.py # AI task extraction
│   │   ├── email_processor.py # Email integration
│   │   └── ...
│   ├── utils/              # Utility functions
│   └── main.py             # FastAPI application
├── tests/                  # Test suite
└── requirements.txt        # Python dependencies
```

## 🧪 Testing Strategy

### Test Types

1. **Unit Tests** - Test individual components/functions
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete user workflows
4. **Performance Tests** - Lighthouse CI for frontend performance

### Running Tests

**Frontend Tests**
```bash
cd desktop
npm test                    # Run all tests
npm test -- --coverage     # With coverage report
npm test -- --watch        # Watch mode
```

**Backend Tests**
```bash
cd backend
pytest                      # Run all tests
pytest --cov=src          # With coverage
pytest -m unit            # Unit tests only
pytest -m integration     # Integration tests only
```

**Coverage Requirements**
- **Frontend**: 70% minimum coverage
- **Backend**: 80% minimum coverage
- **Critical paths**: 90% coverage required

### Writing Tests

**Frontend Test Example**
```javascript
// src/components/__tests__/TaskCard.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import TaskCard from '../TaskCard';

describe('TaskCard', () => {
  const mockTask = {
    id: 1,
    title: 'Test Task',
    confidence: 0.95,
    status: 'pending'
  };

  it('renders task information correctly', () => {
    render(<TaskCard task={mockTask} />);
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('95%')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const mockClick = jest.fn();
    render(<TaskCard task={mockTask} onClick={mockClick} />);
    fireEvent.click(screen.getByText('Test Task'));
    expect(mockClick).toHaveBeenCalledWith(mockTask);
  });
});
```

**Backend Test Example**
```python
# tests/unit/test_action_items.py
import pytest
from src.models.action_items import ActionItem
from src.services.ai_processor import AIProcessor

@pytest.mark.unit
def test_action_item_creation():
    item = ActionItem(
        title="Test Task",
        description="Test description",
        confidence=0.95
    )
    assert item.title == "Test Task"
    assert item.confidence == 0.95

@pytest.mark.asyncio
async def test_ai_task_extraction():
    processor = AIProcessor()
    result = await processor.extract_tasks("Please review the budget by Friday")
    assert len(result) > 0
    assert result[0].confidence > 0.7
```

## 🔄 CI/CD Pipeline

### Workflow Overview

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Triggered on: PR, push to main/develop
   - Steps: Lint → Test → Build → Security Scan
   - Platforms: Linux, Windows, macOS

2. **Dev Release** (`.github/workflows/dev-release.yml`)
   - Triggered on: Push to main, manual dispatch
   - Creates pre-release with `-dev` suffix
   - Includes all platforms and architectures

3. **Production Release** (`.github/workflows/prod-release.yml`)
   - Triggered manually with version input
   - Comprehensive testing and validation
   - Code signing and notarization
   - Creates stable release

### Branch Strategy

```
main                    # Production-ready code
├── develop            # Integration branch
├── feature/*          # Feature development
├── bugfix/*           # Bug fixes
└── hotfix/*           # Critical production fixes
```

### Release Process

**Development Release**
```bash
# Automatic on main branch push
git push origin main

# Manual trigger with version bump
gh workflow run dev-release.yml -f version_bump=minor
```

**Production Release**
```bash
# Manual trigger only
gh workflow run prod-release.yml \
  -f version=0.1.0 \
  -f release_notes="Initial stable release with OAuth and AI integration"
```

## 🛠️ Development Workflow

### Feature Development

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-awesome-feature
   ```

2. **Develop with TDD**
   ```bash
   # Write tests first
   npm test -- --watch  # Frontend
   pytest --watch       # Backend
   
   # Implement feature
   # Run tests continuously
   ```

3. **Code Quality Checks**
   ```bash
   # Frontend
   npm run lint
   npm run test -- --coverage
   
   # Backend  
   black src/
   flake8 src/
   mypy src/
   pytest --cov=src
   ```

4. **Create Pull Request**
   - Include comprehensive description
   - Link related issues
   - Add screenshots for UI changes
   - Ensure CI passes

### Debugging

**Frontend Debugging**
```bash
# Debug Electron main process
npm run electron-dev
# Open Chrome DevTools: Ctrl+Shift+I

# Debug React components
npm start
# Browser DevTools with React DevTools extension
```

**Backend Debugging**
```bash
# Debug with breakpoints
python -m debugpy --listen 5678 --wait-for-client -m src.main

# Debug tests
pytest --pdb
```

### Performance Optimization

**Frontend Performance**
- Lighthouse CI runs on every PR
- Bundle size monitoring with webpack-bundle-analyzer
- React DevTools Profiler for component optimization

**Backend Performance**
- FastAPI built-in performance monitoring
- Database query optimization
- AI processing performance metrics

## 📋 Code Standards

### JavaScript/React Standards
- **ESLint**: Airbnb configuration with React hooks
- **Prettier**: Code formatting
- **Naming**: camelCase for variables, PascalCase for components
- **File Structure**: One component per file, index.js for barrel exports

### Python Standards
- **Black**: Code formatting (line length 88)
- **Flake8**: Linting with complexity checking
- **MyPy**: Type hints required for public APIs
- **Naming**: snake_case for variables, PascalCase for classes

### Git Commit Standards
```
type(scope): description

feat(ui): add dark mode toggle
fix(auth): resolve OAuth callback issue  
docs(api): update authentication documentation
test(backend): add integration tests for AI processor
ci(workflow): optimize build performance
```

### Documentation Standards
- **Code Comments**: Focus on "why" not "what"
- **API Documentation**: OpenAPI/Swagger for backend
- **Component Documentation**: JSDoc for React components
- **README**: Keep updated with setup instructions

## 🔧 Configuration Management

### Environment Variables
```bash
# Required for development
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
DATABASE_URL=sqlite:///action_items.db
OLLAMA_BASE_URL=http://localhost:11434
ENCRYPTION_KEY=your_encryption_key

# Optional
DEBUG=true
LOG_LEVEL=debug
SENTRY_DSN=your_sentry_dsn
```

### Doppler Configuration
```bash
# Production
doppler secrets set MICROSOFT_CLIENT_ID=prod_value -p taskharvester -c prd

# Development  
doppler secrets set MICROSOFT_CLIENT_ID=dev_value -p taskharvester -c dev
```

## 🚨 Troubleshooting

### Common Issues

**Electron App Won't Start**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Electron version compatibility
npm ls electron
```

**Backend API Connection Issues**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify Doppler configuration
doppler secrets list

# Check Python dependencies
pip check
```

**OAuth Authentication Failing**
```bash
# Verify redirect URI in Azure app registration
# Check CORS settings in backend
# Validate client ID and secret in Doppler
```

**AI Processing Not Working**
```bash
# Check Ollama service
ollama list
ollama serve

# Verify model is downloaded
ollama pull llama3.1:8b

# Check API connectivity
curl http://localhost:11434/api/tags
```

### Debug Tools

**Electron DevTools**
- Main process: `Ctrl+Shift+I` 
- Renderer process: F12
- Remote debugging: `--remote-debugging-port=9222`

**Backend Debug Tools**
- FastAPI docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Database explorer: SQLite browser

**Performance Monitoring**
- React DevTools Profiler
- Lighthouse CI reports
- FastAPI performance metrics

## 📚 Additional Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Doppler Documentation](https://docs.doppler.com/)

---

For questions or issues, please create a GitHub issue or check our [FAQ](FAQ.md).