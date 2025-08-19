/**
 * Electron Main Process
 * Handles window management, system tray, and backend communication
 */
const { app, BrowserWindow, Menu, ipcMain, shell, Notification } = require('electron');
const path = require('path');

// Simple in-memory store for now (replace with electron-store later)
const store = {
  data: {},
  get: function(key, defaultValue) {
    return this.data[key] !== undefined ? this.data[key] : defaultValue;
  },
  set: function(key, value) {
    this.data[key] = value;
  },
  delete: function(key) {
    delete this.data[key];
  }
};

class ActionItemExtractorApp {
  constructor() {
    this.mainWindow = null;
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

    // Load the FastAPI backend web interface
    this.mainWindow.loadURL('http://localhost:8000');
    
    // Open dev tools in development
    const isDev = process.env.NODE_ENV === 'development';
    if (isDev) {
      this.mainWindow.webContents.openDevTools();
    }

    // Handle window events
    this.mainWindow.on('close', (event) => {
      // Just close the app normally for now
      app.quit();
    });

    this.mainWindow.on('resized', () => {
      this.saveWindowBounds();
    });

    this.mainWindow.on('moved', () => {
      this.saveWindowBounds();
    });
  }

  createOAuthWindow(authUrl) {
    return new Promise((resolve, reject) => {
      // Create OAuth popup window
      const oauthWindow = new BrowserWindow({
        width: 500,
        height: 700,
        modal: true,
        parent: this.mainWindow,
        show: true,
        webPreferences: {
          nodeIntegration: false,
          contextIsolation: true,
          enableRemoteModule: false
        },
        title: 'Microsoft Sign In'
      });

      // Load the OAuth URL
      oauthWindow.loadURL(authUrl);

      // Handle URL changes to capture the callback
      oauthWindow.webContents.on('will-redirect', (event, newUrl) => {
        this.handleOAuthCallback(newUrl, oauthWindow, resolve, reject);
      });

      // Also handle navigation (some OAuth flows use this instead of redirect)
      oauthWindow.webContents.on('did-navigate', (event, newUrl) => {
        this.handleOAuthCallback(newUrl, oauthWindow, resolve, reject);
      });

      // Handle window close
      oauthWindow.on('closed', () => {
        reject(new Error('OAuth window was closed by user'));
      });

      // Handle load failures
      oauthWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
        console.error('OAuth window load failed:', errorCode, errorDescription);
        oauthWindow.close();
        reject(new Error(`OAuth window load failed: ${errorDescription}`));
      });
    });
  }

  async handleOAuthCallback(url, oauthWindow, resolve, reject) {
    console.log('OAuth URL navigation:', url);
    
    // Check if this is our callback URL
    if (url.startsWith('http://localhost:8000/api/auth/microsoft/callback')) {
      try {
        // Parse the callback URL
        const urlObj = new URL(url);
        const code = urlObj.searchParams.get('code');
        const state = urlObj.searchParams.get('state');
        const error = urlObj.searchParams.get('error');

        if (error) {
          oauthWindow.close();
          reject(new Error(`OAuth error: ${urlObj.searchParams.get('error_description') || error}`));
          return;
        }

        if (code && state) {
          // Complete OAuth flow automatically
          const storedState = store.get('oauthState');
          const codeVerifier = store.get('oauthCodeVerifier');
          
          if (state !== storedState) {
            oauthWindow.close();
            reject(new Error('Invalid OAuth state'));
            return;
          }

          try {
            // Make the token exchange request
            const response = await this.makeApiRequest('POST', '/auth/microsoft/callback', {
              code,
              state,
              code_verifier: codeVerifier
            });

            // Clean up stored OAuth data
            store.delete('oauthState');
            store.delete('oauthCodeVerifier');

            // Close OAuth window
            oauthWindow.close();

            // Show success notification
            this.showNotification('Authentication Success', 'Successfully connected to Microsoft!');

            // Refresh the main window to show updated auth status
            this.mainWindow.webContents.send('oauth-completed', response);

            resolve(response);
          } catch (tokenError) {
            oauthWindow.close();
            reject(tokenError);
          }
        } else {
          oauthWindow.close();
          reject(new Error('Missing authorization code or state'));
        }
      } catch (parseError) {
        console.error('Error parsing OAuth callback:', parseError);
        oauthWindow.close();
        reject(parseError);
      }
    }
  }

  // Tray functionality removed for simplicity

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

    // OAuth flow handling - seamless in-app flow
    ipcMain.handle('start-oauth', async (event) => {
      try {
        console.log('Starting OAuth flow...');
        const response = await this.makeApiRequest('GET', '/auth/microsoft/login');
        console.log('Got OAuth response:', response);
        
        // Store OAuth state for validation
        store.set('oauthState', response.state);
        store.set('oauthCodeVerifier', response.code_verifier);
        
        // Create OAuth window instead of external browser
        await this.createOAuthWindow(response.auth_url);
        
        return { success: true, auth_url: response.auth_url };
      } catch (error) {
        console.error('OAuth start failed:', error);
        throw error;
      }
    });

    // Handle OAuth completion
    ipcMain.handle('complete-oauth', async (event, code, state) => {
      try {
        const storedState = store.get('oauthState');
        const codeVerifier = store.get('oauthCodeVerifier');
        
        if (state !== storedState) {
          throw new Error('Invalid OAuth state');
        }
        
        const response = await this.makeApiRequest('POST', '/auth/microsoft/callback', {
          code,
          state,
          code_verifier: codeVerifier
        });
        
        // Clean up stored OAuth data
        store.delete('oauthState');
        store.delete('oauthCodeVerifier');
        
        // Show success notification
        this.showNotification('Authentication Success', 'Successfully connected to Microsoft!');
        
        return response;
      } catch (error) {
        console.error('OAuth completion failed:', error);
        throw error;
      }
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
    // Use Electron's notification system
    if (Notification.isSupported()) {
      const notification = new Notification({ title, body });
      notification.show();
    } else {
      console.log(`Notification: ${title} - ${body}`);
    }
  }

  sendToRenderer(channel, data) {
    if (this.mainWindow && this.mainWindow.webContents) {
      this.mainWindow.webContents.send(channel, data);
    }
  }

  async makeApiRequest(method, endpoint, data = null) {
    const http = require('http');
    const baseURL = 'http://localhost:8000/api';
    
    return new Promise((resolve, reject) => {
      const url = new URL(`${baseURL}${endpoint}`);
      
      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000
      };

      const req = http.request(options, (res) => {
        let responseData = '';
        
        res.on('data', (chunk) => {
          responseData += chunk;
        });
        
        res.on('end', () => {
          try {
            const parsedData = JSON.parse(responseData);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(parsedData);
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${parsedData.detail || responseData}`));
            }
          } catch (error) {
            reject(new Error(`Failed to parse response: ${responseData}`));
          }
        });
      });

      req.on('error', (error) => {
        console.error('API request failed:', error);
        reject(error);
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        req.write(JSON.stringify(data));
      }

      req.end();
    });
  }
}

// Initialize and start the app
const actionItemApp = new ActionItemExtractorApp();
actionItemApp.initialize();