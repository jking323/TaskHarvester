import React from 'react';

const Titlebar = ({ onToggleTheme, currentTheme }) => {
  const minimizeWindow = () => {
    if (window.electronAPI) {
      window.electronAPI.minimizeWindow();
    }
  };

  const maximizeWindow = () => {
    if (window.electronAPI) {
      window.electronAPI.maximizeWindow();
    }
  };

  const closeWindow = () => {
    if (window.electronAPI) {
      window.electronAPI.closeWindow();
    }
  };

  return (
    <div className="titlebar">
      <div className="titlebar-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
        TaskHarvester
      </div>
      
      <div className="titlebar-center">
        {/* Connection status indicator */}
        <div className="connection-status">
          <div className="status-indicator online"></div>
          <span className="status-text">Connected</span>
        </div>
      </div>
      
      <div className="titlebar-controls">
        <button 
          className="titlebar-button theme-toggle"
          onClick={onToggleTheme}
          title={`Switch to ${currentTheme === 'dark' ? 'light' : 'dark'} theme`}
        >
          {currentTheme === 'dark' ? (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 18c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm0-10c-2.2 0-4 1.8-4 4s1.8 4 4 4 4-1.8 4-4-1.8-4-4-4z"/>
              <path d="M12 2l-1.4 1.4L12 4.8l1.4-1.4L12 2zm0 16.6l-1.4 1.4L12 21.4l1.4-1.4L12 18.6zm7.1-7.1L20.5 12l-1.4 1.4-1.4-1.4 1.4-1.4zM4.9 11.5L3.5 12l1.4 1.4 1.4-1.4-1.4-1.4z"/>
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          )}
        </button>
        
        <button 
          className="titlebar-button"
          onClick={minimizeWindow}
          title="Minimize"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 19h12v2H6z"/>
          </svg>
        </button>
        
        <button 
          className="titlebar-button"
          onClick={maximizeWindow}
          title="Maximize"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path d="M4 4h16v16H4V4zm2 2v12h12V6H6z"/>
          </svg>
        </button>
        
        <button 
          className="titlebar-button close"
          onClick={closeWindow}
          title="Close"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
      
      <style jsx>{`
        .titlebar-center {
          flex: 1;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        
        .connection-status {
          display: flex;
          align-items: center;
          gap: var(--spacing-xs);
          padding: var(--spacing-xs) var(--spacing-md);
          background: var(--color-bg-tertiary);
          border-radius: var(--radius-full);
          font-size: var(--font-size-xs);
        }
        
        .status-indicator {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--color-text-muted);
        }
        
        .status-indicator.online {
          background: var(--color-accent);
          box-shadow: 0 0 6px rgba(59, 165, 92, 0.6);
        }
        
        .status-indicator.offline {
          background: var(--color-danger);
        }
        
        .status-indicator.syncing {
          background: var(--color-warning);
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        .status-text {
          color: var(--color-text-tertiary);
          font-weight: var(--font-weight-medium);
        }
        
        .theme-toggle:hover {
          background: var(--color-bg-tertiary);
          color: var(--color-primary);
        }
        
        .titlebar-button.close:hover {
          background: var(--color-danger);
          color: white;
        }
        
        @media (platform: windows) {
          .titlebar-controls {
            order: 2;
          }
        }
        
        @media (platform: darwin) {
          .titlebar {
            padding-left: 80px; /* Space for macOS traffic lights */
          }
          .titlebar-controls {
            display: none; /* macOS handles window controls */
          }
        }
      `}</style>
    </div>
  );
};

export default Titlebar;