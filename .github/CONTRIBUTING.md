# Contributing to TaskHarvester

Thank you for your interest in contributing to TaskHarvester! This guide will help you get started with the development process and understand our workflow.

## Table of Contents
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Management](#issue-management)

## Development Setup

### Prerequisites
- Python 3.9+ for backend development
- Node.js 18+ for frontend development
- Git for version control
- NVIDIA GPU with 20GB+ VRAM (for AI model testing)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd desktop
npm install
```

### Running the Application
```bash
# Start backend server
cd backend
python -m uvicorn src.main:app --reload

# Start desktop application (in another terminal)
cd desktop
npm run dev
```

## Project Structure

```
TaskHarvester/
├── backend/               # Python FastAPI backend
│   ├── src/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utility functions
│   └── tests/            # Backend tests
├── desktop/              # Electron React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Application pages
│   │   └── services/     # Frontend services
│   └── public/           # Static assets
├── ai-models/            # AI model configurations
├── config/               # Configuration files
├── docs/                 # Documentation
└── scripts/              # Build and deployment scripts
```

## Development Workflow

### Branch Strategy
We use GitHub Flow with the following branch naming conventions:

- `main` - Production-ready code
- `feature/ISSUE-short-description` - New features
- `fix/ISSUE-short-description` - Bug fixes
- `hotfix/short-description` - Critical production fixes
- `refactor/short-description` - Code refactoring
- `docs/short-description` - Documentation updates

### Creating a Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/123-microsoft-graph-oauth
```

### Committing Changes
We follow conventional commits format:
```
type(scope): description

feat(auth): implement Microsoft Graph OAuth flow
fix(ui): resolve dashboard loading issue
docs(readme): update installation instructions
refactor(api): simplify email processing logic
test(integration): add Wrike API integration tests
```

## Coding Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Maximum line length: 127 characters
- Use `black` for code formatting
- Use `flake8` for linting
- Use `mypy` for type checking

### JavaScript/TypeScript (Frontend)
- Use TypeScript for all new code
- Follow ESLint configuration
- Use Prettier for code formatting
- Prefer functional components and hooks
- Use consistent naming conventions

### Code Quality Tools
```bash
# Backend
cd backend
black src/
flake8 src/
mypy src/

# Frontend
cd desktop
npm run lint
npm run format
npm run type-check
```

## Testing Guidelines

### Backend Testing
- Write unit tests for all business logic
- Use pytest for testing framework
- Aim for 90%+ code coverage
- Include integration tests for API endpoints

```bash
cd backend
pytest tests/ -v --cov=src
```

### Frontend Testing
- Write tests for all React components
- Use Jest and React Testing Library
- Include E2E tests for critical workflows

```bash
cd desktop
npm test
npm run test:e2e
```

## Pull Request Process

### Before Creating a PR
1. Ensure your branch is up to date with main
2. Run all tests and ensure they pass
3. Run code quality checks
4. Update documentation if needed
5. Test your changes thoroughly

### PR Requirements
- Fill out the complete PR template
- Link to related issues
- Include screenshots/demos for UI changes
- Ensure all CI checks pass
- Request review from appropriate code owners

### PR Review Process
1. Automated CI checks must pass
2. At least one code owner approval required
3. Address all review feedback
4. Squash commits before merging (if requested)

## Issue Management

### Issue Labels
- `type:` - bug, feature, enhancement, documentation
- `priority:` - critical, high, medium, low
- `area:` - backend, frontend, ai, integrations, auth
- `status:` - blocked, needs-review, in-progress

### Creating Issues
- Use appropriate issue templates
- Provide detailed descriptions and acceptance criteria
- Assign to relevant project boards
- Link to related issues or PRs

### Working on Issues
1. Comment on the issue to indicate you're working on it
2. Create a feature branch linked to the issue
3. Reference the issue in commit messages
4. Update issue status as you progress

## Component-Specific Guidelines

### Backend Development
- Use FastAPI best practices
- Implement proper error handling and validation
- Follow REST API conventions
- Use SQLAlchemy for database operations
- Implement proper logging and monitoring

### Frontend Development
- Use React best practices and hooks
- Implement responsive design principles
- Ensure accessibility compliance
- Use proper state management (Context API or Redux)
- Implement proper error boundaries

### AI Integration
- Test with actual AI models when possible
- Implement proper fallback mechanisms
- Monitor performance and memory usage
- Use appropriate prompt engineering techniques
- Document model requirements and limitations

### External Integrations
- Implement proper error handling and retries
- Respect API rate limits
- Use proper authentication mechanisms
- Implement comprehensive logging
- Create mock services for testing

## Getting Help

### Communication Channels
- GitHub Issues for bug reports and feature requests
- GitHub Discussions for questions and ideas
- Project boards for tracking progress

### Resources
- [Project Roadmap](../ROADMAP.md)
- [API Documentation](../docs/api.md)
- [Architecture Guide](../docs/architecture.md)
- [Setup Guide](../README.md)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation

Thank you for contributing to TaskHarvester! 🚀