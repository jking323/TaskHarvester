import React, { useState, useEffect } from 'react';

const Login = ({ onAuthSuccess }) => {
    const [authStatus, setAuthStatus] = useState('loading');
    const [userInfo, setUserInfo] = useState(null);
    const [isAuthenticating, setIsAuthenticating] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            setAuthStatus('loading');
            const response = await window.electronAPI.apiRequest('GET', '/auth/status');
            
            if (response.microsoft_authenticated && response.microsoft_user) {
                setAuthStatus('authenticated');
                setUserInfo(response.microsoft_user);
                onAuthSuccess(response);
            } else {
                setAuthStatus('not-authenticated');
            }
        } catch (error) {
            console.error('Auth status check failed:', error);
            setAuthStatus('not-authenticated');
            setError('Failed to check authentication status');
        }
    };

    const handleMicrosoftLogin = async () => {
        try {
            setIsAuthenticating(true);
            setError(null);
            
            if (window.electronAPI) {
                // Use Electron's seamless OAuth flow
                const result = await window.electronAPI.startOAuth();
                
                // OAuth completion is handled automatically by Electron
                // The main process will send oauth-completed event
            } else {
                // Fallback for browser testing
                const response = await window.electronAPI.apiRequest('GET', '/auth/microsoft/login');
                
                if (response.auth_url) {
                    window.location.href = response.auth_url;
                }
            }
        } catch (error) {
            console.error('Microsoft login failed:', error);
            setError('Failed to start Microsoft login. Please try again.');
            setIsAuthenticating(false);
        }
    };

    // Handle OAuth completion from Electron main process
    useEffect(() => {
        if (window.electronAPI && window.electronAPI.onOAuthCompleted) {
            window.electronAPI.onOAuthCompleted((event, result) => {
                console.log('OAuth completed:', result);
                setIsAuthenticating(false);
                
                // Check auth status again to get updated user info
                setTimeout(() => {
                    checkAuthStatus();
                }, 500);
            });
        }
    }, []);

    if (authStatus === 'authenticated') {
        // Auto-redirect to dashboard
        setTimeout(() => onAuthSuccess({ 
            microsoft_authenticated: true, 
            microsoft_user: userInfo 
        }), 100);
        return (
            <div className="login-container">
                <div className="login-content">
                    <div className="login-success">
                        <div className="success-icon">✅</div>
                        <h2>Welcome back!</h2>
                        <p>Redirecting to your dashboard...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="login-container">
            <div className="login-content">
                <div className="login-header">
                    <div className="app-logo">
                        <span className="logo-icon">📋</span>
                        <span className="logo-text">TaskHarvester</span>
                    </div>
                    <p className="app-tagline">AI-Powered Action Item Extractor</p>
                </div>

                <div className="auth-section">
                    <div className={`auth-status ${authStatus}`}>
                        {authStatus === 'loading' && (
                            <>
                                <div className="spinner"></div>
                                <span>Checking authentication...</span>
                            </>
                        )}
                        {authStatus === 'not-authenticated' && (
                            <>
                                <span className="status-icon">🔐</span>
                                <span>Please sign in to continue</span>
                            </>
                        )}
                    </div>

                    {error && (
                        <div className="error-message">
                            <span className="error-icon">⚠️</span>
                            <span>{error}</span>
                        </div>
                    )}

                    <div className="login-actions">
                        <button 
                            className="login-button microsoft-login"
                            onClick={handleMicrosoftLogin}
                            disabled={isAuthenticating || authStatus === 'loading'}
                        >
                            {isAuthenticating ? (
                                <>
                                    <div className="spinner"></div>
                                    <span>Signing in...</span>
                                </>
                            ) : (
                                <>
                                    <span className="microsoft-icon">🏢</span>
                                    <span>Sign in with Microsoft</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>

                <div className="features-section">
                    <h3>What you can do with TaskHarvester</h3>
                    <div className="features-grid">
                        <div className="feature-item">
                            <div className="feature-icon">📧</div>
                            <div className="feature-text">
                                <h4>Email Analysis</h4>
                                <p>Automatically extract action items from your emails</p>
                            </div>
                        </div>
                        <div className="feature-item">
                            <div className="feature-icon">📅</div>
                            <div className="feature-text">
                                <h4>Calendar Integration</h4>
                                <p>Process meeting notes and action items from calendar events</p>
                            </div>
                        </div>
                        <div className="feature-item">
                            <div className="feature-icon">🤖</div>
                            <div className="feature-text">
                                <h4>AI-Powered</h4>
                                <p>Smart confidence scoring and intelligent task categorization</p>
                            </div>
                        </div>
                        <div className="feature-item">
                            <div className="feature-icon">📊</div>
                            <div className="feature-text">
                                <h4>Dashboard & Analytics</h4>
                                <p>Track your productivity and task completion over time</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;