import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Titlebar from './Titlebar';
import '../styles/design-system.css';
import '../styles/components.css';

const Layout = ({ children, currentPage, onNavigate, isAuthenticated, backendStatus }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="app-container">
      <Titlebar 
        onToggleTheme={toggleTheme} 
        currentTheme={theme}
        isAuthenticated={isAuthenticated}
        backendStatus={backendStatus}
      />
      
      <Sidebar 
        collapsed={sidebarCollapsed}
        onToggle={toggleSidebar}
        currentPage={currentPage}
        onNavigate={onNavigate}
        isAuthenticated={isAuthenticated}
        backendStatus={backendStatus}
      />
      
      <main className={`main-content ${sidebarCollapsed ? 'expanded' : ''}`}>
        {children}
      </main>
    </div>
  );
};

export default Layout;