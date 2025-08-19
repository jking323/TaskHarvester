# TaskHarvester UI Implementation Guide

## Quick Start

### 1. Install Dependencies
```bash
cd desktop
npm install react react-dom react-router-dom
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
npm install date-fns
npm install --save-dev @types/react @types/react-dom
```

### 2. Set Up Main Application Structure

Update your main React entry point to use the new layout:

```jsx
// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import ReviewQueue from './pages/ReviewQueue';
import EmailSources from './pages/EmailSources';
import SyncStatus from './pages/SyncStatus';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/review" element={<ReviewQueue />} />
          <Route path="/sources" element={<EmailSources />} />
          <Route path="/sync" element={<SyncStatus />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
```

### 3. Update Preload Script

Enhance the preload script to support the UI:

```javascript
// src/preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),
  
  // Theme management
  getTheme: () => ipcRenderer.invoke('get-theme'),
  setTheme: (theme) => ipcRenderer.invoke('set-theme', theme),
  
  // API communication
  apiRequest: (method, endpoint, data) => 
    ipcRenderer.invoke('api-request', method, endpoint, data),
  
  // Settings
  getSettings: () => ipcRenderer.invoke('get-settings'),
  setSetting: (key, value) => ipcRenderer.invoke('set-setting', key, value),
  
  // Notifications
  showNotification: (title, body) => 
    ipcRenderer.invoke('show-notification', title, body),
  
  // Navigation events
  onNavigate: (callback) => {
    ipcRenderer.on('navigate-to', callback);
    return () => ipcRenderer.removeListener('navigate-to', callback);
  },
  
  // Real-time updates
  onTaskUpdate: (callback) => {
    ipcRenderer.on('task-updated', callback);
    return () => ipcRenderer.removeListener('task-updated', callback);
  },
  
  onSyncStatus: (callback) => {
    ipcRenderer.on('sync-status', callback);
    return () => ipcRenderer.removeListener('sync-status', callback);
  }
});
```

### 4. Update Main Process for Window Controls

Add window control handlers to main.js:

```javascript
// Add these IPC handlers to your main.js
ipcMain.handle('minimize-window', () => {
  if (this.mainWindow) {
    this.mainWindow.minimize();
  }
});

ipcMain.handle('maximize-window', () => {
  if (this.mainWindow) {
    if (this.mainWindow.isMaximized()) {
      this.mainWindow.unmaximize();
    } else {
      this.mainWindow.maximize();
    }
  }
});

ipcMain.handle('close-window', () => {
  if (this.mainWindow) {
    this.mainWindow.close();
  }
});

ipcMain.handle('get-theme', () => {
  return store.get('theme', 'dark');
});

ipcMain.handle('set-theme', (event, theme) => {
  store.set('theme', theme);
  return true;
});
```

## Component Integration

### Missing Components to Implement

You'll need to create these additional page components:

#### 1. Tasks Page (`src/pages/Tasks.jsx`)
```jsx
import React, { useState, useEffect } from 'react';
import TaskCard from '../components/TaskCard';
import SearchBar from '../components/SearchBar';
import FilterBar from '../components/FilterBar';

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilters, setSelectedFilters] = useState([]);

  // Implementation similar to Dashboard but for all tasks
  return (
    <div className="tasks-page">
      <div className="page-header">
        <h1>All Tasks</h1>
        <div className="page-actions">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
          <FilterBar 
            filters={[]} 
            selectedFilters={selectedFilters}
            onFilterChange={setSelectedFilters}
          />
        </div>
      </div>
      
      <div className="tasks-grid">
        {/* Task list implementation */}
      </div>
    </div>
  );
};

export default Tasks;
```

#### 2. Review Queue Page (`src/pages/ReviewQueue.jsx`)
```jsx
import React, { useState, useEffect } from 'react';

const ReviewQueue = () => {
  // Tasks that need manual review (low confidence, conflicts, etc.)
  return (
    <div className="review-queue">
      <h1>Review Queue</h1>
      {/* Implementation for reviewing AI-extracted tasks */}
    </div>
  );
};

export default ReviewQueue;
```

### API Integration

#### Backend Endpoints Expected
Make sure your backend supports these endpoints:

```python
# Expected API endpoints for the frontend
GET /api/tasks                    # List tasks with pagination
GET /api/tasks/{id}               # Get specific task
PUT /api/tasks/{id}               # Update task
DELETE /api/tasks/{id}            # Delete task
POST /api/tasks                   # Create manual task

GET /api/dashboard/stats          # Dashboard statistics
GET /api/sync/status              # Sync status and history
GET /api/sources                  # Email/Teams sources
POST /api/sync/trigger            # Manual sync trigger

GET /api/settings                 # App settings
PUT /api/settings                 # Update settings
```

#### Sample API Response Formats
```javascript
// GET /api/tasks response
{
  "tasks": [
    {
      "id": 1,
      "title": "Review Q4 budget proposals",
      "description": "Need to review...",
      "confidence": 0.95,
      "source": "email",
      "sender": "john.doe@company.com",
      "extractedAt": "2024-01-15T10:30:00Z",
      "status": "pending",
      "tags": ["finance", "review", "urgent"],
      "metadata": {
        "messageId": "msg_123",
        "subject": "Q4 Budget Review",
        "thread": "thread_456"
      }
    }
  ],
  "total": 47,
  "page": 1,
  "perPage": 20
}

// GET /api/dashboard/stats response
{
  "total_tasks": 47,
  "pending_review": 8,
  "high_confidence": 42,
  "synced_today": 15,
  "last_sync": "2024-01-15T14:30:00Z",
  "sync_status": "connected"
}
```

## Styling and Theming

### CSS Import Order
Import styles in this order in your main App component:

```jsx
// App.jsx imports
import './styles/design-system.css';  // Core design tokens first
import './styles/components.css';     // Component styles second
import './styles/pages.css';          // Page-specific styles last
```

### Theme Management
The design system supports automatic theme switching:

```javascript
// Theme switching logic
const toggleTheme = () => {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  if (window.electronAPI) {
    window.electronAPI.setTheme(newTheme);
  }
};

// Initialize theme on app start
useEffect(() => {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
}, []);
```

## Advanced Features

### Real-time Updates
Implement real-time task updates:

```jsx
// In your task components
useEffect(() => {
  if (window.electronAPI) {
    const unsubscribe = window.electronAPI.onTaskUpdate((event, taskData) => {
      // Update local state with new task data
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskData.id ? { ...task, ...taskData } : task
        )
      );
    });
    
    return unsubscribe;
  }
}, []);
```

### Keyboard Shortcuts
Add keyboard navigation:

```jsx
// Global keyboard shortcuts
useEffect(() => {
  const handleKeyboard = (event) => {
    // Cmd/Ctrl + K for search
    if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
      event.preventDefault();
      // Focus search bar
      document.querySelector('.search-input')?.focus();
    }
    
    // Cmd/Ctrl + N for new task
    if ((event.metaKey || event.ctrlKey) && event.key === 'n') {
      event.preventDefault();
      // Open new task modal
    }
  };
  
  document.addEventListener('keydown', handleKeyboard);
  return () => document.removeEventListener('keydown', handleKeyboard);
}, []);
```

### Notification System
Implement toast notifications:

```jsx
// Notification component
const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  
  const addNotification = (type, title, message) => {
    const id = Date.now();
    const notification = { id, type, title, message };
    
    setNotifications(prev => [...prev, notification]);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };
  
  return (
    <NotificationContext.Provider value={{ addNotification }}>
      {children}
      <div className="notifications-container">
        {notifications.map(notification => (
          <Notification key={notification.id} {...notification} />
        ))}
      </div>
    </NotificationContext.Provider>
  );
};
```

## Development Workflow

### 1. Start Development Server
```bash
# Terminal 1: Start React development server
cd desktop
npm start

# Terminal 2: Start Electron in development mode
npm run dev
```

### 2. Hot Reload Configuration
Update your main.js for development:

```javascript
if (isDev) {
  this.mainWindow.loadURL('http://localhost:3000');
  this.mainWindow.webContents.openDevTools();
  
  // Enable hot reload
  require('electron-reload')(__dirname, {
    electron: path.join(__dirname, '..', 'node_modules', '.bin', 'electron'),
    hardResetMethod: 'exit'
  });
}
```

### 3. Testing Considerations
```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm install --save-dev jest-environment-jsdom

# Create test files
touch src/components/__tests__/TaskCard.test.js
touch src/components/__tests__/SearchBar.test.js
```

## Production Build

### Build Configuration
Update package.json build scripts:

```json
{
  "scripts": {
    "build": "react-scripts build",
    "electron-pack": "electron-builder",
    "preelectron-pack": "npm run build",
    "build:all": "npm run build && npm run electron-pack"
  }
}
```

### Optimization
- Ensure CSS is minified in production
- Use React production builds
- Optimize images and assets
- Enable compression in Electron

## Troubleshooting

### Common Issues

1. **Styles not loading**: Check CSS import order
2. **Theme not switching**: Verify CSS custom properties support
3. **API calls failing**: Check preload script and IPC handlers
4. **Window controls not working**: Verify platform detection

### Debug Mode
Enable debug logging:

```javascript
// Add to main.js for debugging
if (isDev) {
  console.log('Debug mode enabled');
  // Enable additional logging
}
```

## Performance Optimization

### React Optimization
- Use React.memo for expensive components
- Implement proper dependency arrays in useEffect
- Consider virtual scrolling for large task lists

### Electron Optimization
- Disable node integration where not needed
- Use context isolation
- Minimize main process operations

This implementation guide provides everything needed to get the TaskHarvester UI up and running with a professional, modern interface that users will love.