/**
 * Electron Preload Script
 * Securely exposes APIs to the renderer process
 */
const { contextBridge, ipcRenderer } = require('electron');

// Expose APIs to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // Settings
  getSettings: () => ipcRenderer.invoke('get-settings'),
  setSetting: (key, value) => ipcRenderer.invoke('set-setting', key, value),
  
  // Notifications
  showNotification: (title, body) => ipcRenderer.invoke('show-notification', title, body),
  
  // External links
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // Backend API communication
  apiRequest: (method, endpoint, data) => ipcRenderer.invoke('api-request', method, endpoint, data),
  
  // OAuth authentication
  startOAuth: () => ipcRenderer.invoke('start-oauth'),
  completeOAuth: (code, state) => ipcRenderer.invoke('complete-oauth', code, state),
  
  // Navigation
  onNavigate: (callback) => ipcRenderer.on('navigate-to', callback),
  
  // OAuth completion event
  onOAuthCompleted: (callback) => ipcRenderer.on('oauth-completed', callback),
  
  // Processing events
  onProcessingToggle: (callback) => ipcRenderer.on('processing-toggle', callback),
  
  // Cleanup listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});