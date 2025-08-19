import '@testing-library/jest-dom';

// Mock Electron APIs
global.electronAPI = {
  apiRequest: jest.fn(),
  startOAuth: jest.fn(),
  onOAuthCompleted: jest.fn(),
  showNotification: jest.fn(),
  openExternal: jest.fn(),
  getSettings: jest.fn(),
  setSetting: jest.fn()
};

// Mock window methods
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Suppress console warnings in tests
const originalWarn = console.warn;
console.warn = (...args) => {
  if (args[0]?.includes('ReactDOM.render')) return;
  originalWarn(...args);
};