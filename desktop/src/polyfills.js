/**
 * Polyfills for Node.js globals in browser/Electron renderer
 */

// Global polyfill
if (typeof global === 'undefined') {
  var global = globalThis;
}

// Process polyfill
if (typeof process === 'undefined') {
  global.process = require('process/browser');
}

// Buffer polyfill
if (typeof Buffer === 'undefined') {
  global.Buffer = require('buffer').Buffer;
}

// Export for webpack
module.exports = {};