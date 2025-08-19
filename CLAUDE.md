# TaskHarvester Development Notes

## Platform-Specific Commands

### macOS Development
- **Directory Changes**: Use `bin/bash -c cd` for directory changes in terminal commands
- **Example**: `bin/bash -c "cd /path/to/directory && npm install"`
- **Reason**: zoxide integration in macOS terminal can interfere with simple `cd` commands

## UI Development

### Current Status
- Native task management UI implemented
- No external PM tool integration (Wrike removed)
- Mock data demonstrates AI confidence scoring
- Professional Discord/Slack-inspired design

### Architecture
- **Frontend**: Electron + React + Webpack
- **Backend**: Python FastAPI with SQLite
- **AI Processing**: Ollama + Llama 3.1 8B (local)
- **Authentication**: Microsoft Graph OAuth with PKCE

### Build Commands
- **Development**: `npm run start` (webpack dev server)
- **Production**: `npm run build` (static build + Electron packaging)
- **Electron**: `npm run electron-dev` (development mode)

### Known Issues & Solutions
- **Node.js Polyfills**: Webpack requires comprehensive polyfills for browser compatibility
- **Hot Reload**: Disabled in development to avoid Node.js module conflicts
- **React Router**: Removed in favor of simple state-based navigation

### UI Components
- **Layout.jsx**: Main app structure with sidebar/content
- **TaskCard.jsx**: AI confidence indicators and task display  
- **Dashboard.jsx**: Stats overview and task management
- **Sidebar.jsx**: Navigation with badge notifications

Last Updated: 2025-08-19