/**
 * TaskHarvester Renderer Process
 * React app entry point with mock data
 */

// Ensure global is available before importing React
if (typeof global === 'undefined') {
  window.global = window;
}

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles/design-system.css';
import './styles/components.css';

// Initialize React app
const container = document.getElementById('root');
const root = createRoot(container);

root.render(<App />);

// Hot module replacement for development
if (module.hot) {
    module.hot.accept('./App.jsx', () => {
        const NextApp = require('./App.jsx').default;
        root.render(<NextApp />);
    });
}