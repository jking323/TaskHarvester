/**
 * Electron Main Process
 * Handles window management, system tray, and backend communication
 */
const { app, BrowserWindow, Tray, Menu, ipcMain, shell } = require('electron');
const path = require('path');
const Store = require('electron-store');

// Initialize settings store
const store = new Store();

class ActionItemExtractorApp {
  constructor() {
    this.mainWindow = null;
    this.tray = null;
    this.isQuitting = false;
    
    // App settings
    this.settings = {
      windowBounds: store.get('windowBounds', { width: 1200, height: 800 }),
      startMinimized: store.get('startMinimized', false),
      autoStart: store.get('autoStart', true)
    };
  }

  async initialize() {
    // Handle app ready
    app.whenReady().then(() => {
      this.createMainWindow();
      this.createSystemTray();
      this.setupEventHandlers();
      
      app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
          this.createMainWindow();
        }
      });
    });

    // Handle app window close
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    // Handle before quit
    app.on('before-quit', () => {
      this.isQuitting = true;
    });
  }

  createMainWindow() {
    // Create browser window
    this.mainWindow = new BrowserWindow({
      ...this.settings.windowBounds,
      minWidth: 800,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js')
      },
      icon: path.join(__dirname, '../public/icon.png'),
      show: !this.settings.startMinimized,
      title: 'Action Item Extractor'
    });

    // Load the React app
    const isDev = process.env.NODE_ENV === 'development';
    if (isDev) {
      this.mainWindow.loadURL('http://localhost:3000');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }

    // Handle window events
    this.mainWindow.on('close', (event) => {
      if (!this.isQuitting) {
        event.preventDefault();
        this.mainWindow.hide();
        
        // Show notification on first minimize
        if (!store.get('hasShownMinimizeNotification')) {
          this.showNotification(
            'Action Item Extractor',
            'App minimized to system tray. Right-click the tray icon to access options.'
          );
          store.set('hasShownMinimizeNotification', true);
        }
      }
    });

    this.mainWindow.on('resized', () => {
      this.saveWindowBounds();
    });

    this.mainWindow.on('moved', () => {
      this.saveWindowBounds();
    });
  }

  createSystemTray() {
    try {
      // Create system tray
      const trayIconPath = path.join(__dirname, '../public/tray-icon.png');
      this.tray = new Tray(trayIconPath);
      
      this.updateTrayMenu();
    } catch (error) {
      console.log('System tray not available or icon missing:', error.message);
      // Continue without tray
    }
    
    if (this.tray) {
      // Handle tray click
      this.tray.on('click', () => {
        if (this.mainWindow.isVisible()) {
          this.mainWindow.hide();
        } else {
          this.showMainWindow();
        }
      });

      // Handle tray double-click
      this.tray.on('double-click', () => {
        this.showMainWindow();
      });
    }
  }

  updateTrayMenu() {
    if (!this.tray) return;
    
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Open Dashboard',
        click: () => this.showMainWindow()
      },
      {
        label: 'Review Queue',
        click: () => this.showMainWindow('review')
      },
      { type: 'separator' },
      {
        label: 'Settings',
        click: () => this.showMainWindow('settings')
      },
      {
        label: 'Pause Processing',
        type: 'checkbox',
        checked: store.get('processingPaused', false),
        click: (menuItem) => {
          store.set('processingPaused', menuItem.checked);
          this.sendToRenderer('processing-toggle', menuItem.checked);
        }
      },
      { type: 'separator' },
      {
        label: 'Quit',
        click: () => {
          this.isQuitting = true;
          app.quit();
        }
      }
    ]);

    this.tray.setContextMenu(contextMenu);
    this.tray.setToolTip('Action Item Extractor');
  }

  setupEventHandlers() {
    // IPC handlers
    ipcMain.handle('get-app-version', () => app.getVersion());
    
    ipcMain.handle('get-settings', () => {
      return store.store;
    });
    
    ipcMain.handle('set-setting', (event, key, value) => {
      store.set(key, value);
      return true;
    });

    ipcMain.handle('show-notification', (event, title, body) => {
      this.showNotification(title, body);
    });

    ipcMain.handle('open-external', (event, url) => {
      shell.openExternal(url);
    });

    // Backend API communication
    ipcMain.handle('api-request', async (event, method, endpoint, data) => {
      return await this.makeApiRequest(method, endpoint, data);
    });
  }

  showMainWindow(route = '') {
    if (this.mainWindow) {
      if (route) {
        this.mainWindow.webContents.send('navigate-to', route);
      }
      this.mainWindow.show();
      this.mainWindow.focus();
    }
  }

  saveWindowBounds() {
    if (this.mainWindow) {
      const bounds = this.mainWindow.getBounds();
      store.set('windowBounds', bounds);
    }
  }

  showNotification(title, body) {
    new Notification(title, { body });
  }

  sendToRenderer(channel, data) {
    if (this.mainWindow && this.mainWindow.webContents) {
      this.mainWindow.webContents.send(channel, data);
    }
  }

  async makeApiRequest(method, endpoint, data = null) {
    const axios = require('axios');
    const baseURL = 'http://127.0.0.1:8000/api';
    
    try {
      const config = {
        method,
        url: `${baseURL}${endpoint}`,
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.data = data;
      }

      const response = await axios(config);
      return response.data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
}

// Initialize and start the app
const actionItemApp = new ActionItemExtractorApp();
actionItemApp.initialize();