import React, { useState, useEffect } from 'react';

const Sidebar = ({ collapsed, onToggle, currentPage, onNavigate }) => {
  const [unreadCounts, setUnreadCounts] = useState({
    review: 0,
    tasks: 0,
    sync: 0
  });

  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
        </svg>
      ),
      path: '/',
      badge: null
    },
    {
      id: 'tasks',
      label: 'All Tasks',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.11 0 2-.9 2-2V5c0-1.1-.89-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
      ),
      path: '/tasks',
      badge: unreadCounts.tasks > 0 ? unreadCounts.tasks : null
    },
    {
      id: 'review',
      label: 'Review Queue',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      path: '/review',
      badge: unreadCounts.review > 0 ? unreadCounts.review : null
    },
    {
      id: 'sources',
      label: 'Email Sources',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
        </svg>
      ),
      path: '/sources',
      badge: null
    },
    {
      id: 'sync',
      label: 'Sync Status',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
        </svg>
      ),
      path: '/sync',
      badge: unreadCounts.sync > 0 ? unreadCounts.sync : null
    }
  ];

  const settingsItem = {
    id: 'settings',
    label: 'Settings',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
      </svg>
    ),
    path: '/settings',
    badge: null
  };

  useEffect(() => {
    // Simulate fetching unread counts
    const fetchUnreadCounts = async () => {
      try {
        if (window.electronAPI) {
          const response = await window.electronAPI.apiRequest('GET', '/dashboard/stats');
          setUnreadCounts({
            review: response.pending_review || 0,
            tasks: response.total_tasks || 0,
            sync: response.sync_errors || 0
          });
        }
      } catch (error) {
        console.error('Failed to fetch unread counts:', error);
      }
    };

    fetchUnreadCounts();
    const interval = setInterval(fetchUnreadCounts, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const handleNavigation = (pageId) => {
    onNavigate(pageId);
  };

  const isActive = (itemId) => {
    if (itemId === 'dashboard') {
      return currentPage === 'dashboard';
    }
    return currentPage === itemId;
  };

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button 
          className="btn btn-ghost btn-icon"
          onClick={onToggle}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
          </svg>
        </button>
        
        {!collapsed && (
          <div className="sidebar-brand">
            <h2 className="brand-title">TaskHarvester</h2>
            <p className="brand-subtitle">AI Task Extraction</p>
          </div>
        )}
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${isActive(item.id) ? 'active' : ''}`}
              onClick={() => handleNavigation(item.id)}
              title={collapsed ? item.label : ''}
            >
              <span className="nav-item-icon">{item.icon}</span>
              {!collapsed && (
                <>
                  <span className="nav-item-label">{item.label}</span>
                  {item.badge && (
                    <span className="nav-item-badge">{item.badge}</span>
                  )}
                </>
              )}
            </button>
          ))}
        </div>

        <div className="nav-section nav-section-bottom">
          <button
            className={`nav-item ${isActive(settingsItem.id) ? 'active' : ''}`}
            onClick={() => handleNavigation(settingsItem.id)}
            title={collapsed ? settingsItem.label : ''}
          >
            <span className="nav-item-icon">{settingsItem.icon}</span>
            {!collapsed && (
              <span className="nav-item-label">{settingsItem.label}</span>
            )}
          </button>
        </div>
      </nav>

      {!collapsed && (
        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            <div className="user-info">
              <div className="user-name">John Doe</div>
              <div className="user-status">Connected</div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .sidebar-brand {
          margin-left: var(--spacing-md);
        }
        
        .brand-title {
          font-size: var(--font-size-md);
          font-weight: var(--font-weight-bold);
          color: var(--color-text-primary);
          margin-bottom: 2px;
        }
        
        .brand-subtitle {
          font-size: var(--font-size-xs);
          color: var(--color-text-tertiary);
          font-weight: var(--font-weight-medium);
        }
        
        .nav-section {
          margin-bottom: var(--spacing-lg);
        }
        
        .nav-section-bottom {
          margin-top: auto;
          margin-bottom: 0;
          border-top: 1px solid var(--color-border);
          padding-top: var(--spacing-md);
        }
        
        .sidebar-footer {
          padding: var(--spacing-md);
          border-top: 1px solid var(--color-border);
          margin-top: auto;
        }
        
        .user-profile {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          padding: var(--spacing-sm);
          background: var(--color-bg-tertiary);
          border-radius: var(--radius-lg);
        }
        
        .user-avatar {
          width: 32px;
          height: 32px;
          background: var(--color-primary);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          flex-shrink: 0;
        }
        
        .user-info {
          flex: 1;
          overflow: hidden;
        }
        
        .user-name {
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .user-status {
          font-size: var(--font-size-xs);
          color: var(--color-text-tertiary);
        }
        
        .collapsed .sidebar-footer {
          display: none;
        }
        
        .collapsed .nav-item {
          justify-content: center;
          padding: var(--spacing-md);
        }
        
        .collapsed .nav-item-icon {
          margin: 0;
        }
      `}</style>
    </div>
  );
};

export default Sidebar;