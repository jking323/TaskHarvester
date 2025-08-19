module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
    jest: true
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended'
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true
    },
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  plugins: [
    'react',
    'react-hooks'
  ],
  rules: {
    // React specific rules
    'react/prop-types': 'off', // We're not using PropTypes
    'react/react-in-jsx-scope': 'off', // React 17+ doesn't require importing React
    'react/no-unknown-property': 'off', // Allow JSX pragmas and custom properties
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    
    // General JavaScript rules - focus on real issues
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-console': 'off', // Allow console statements for debugging
    'prefer-const': 'warn',
    'no-var': 'warn',
    
    // Disable formatting rules - focus on logic, not style
    'indent': 'off',
    'quotes': 'off',
    'semi': 'off',
    'comma-dangle': 'off'
  },
  settings: {
    react: {
      version: 'detect'
    }
  },
  ignorePatterns: [
    'dist/',
    'build/',
    'node_modules/',
    'coverage/',
    '*.config.js'
  ]
};