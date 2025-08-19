import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';

// Mock API for development
const mockAPI = {
    async getTasks() {
        return {
            tasks: [
                {
                    id: 1,
                    title: 'Review Q4 budget proposals',
                    description: 'Need to review the budget proposals for Q4 and provide feedback by Friday. The finance team has prepared comprehensive reports covering all departments.',
                    confidence: 0.95,
                    source: 'email',
                    sender: 'john.doe@company.com',
                    extractedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
                    status: 'pending',
                    tags: ['finance', 'review', 'urgent']
                },
                {
                    id: 2,
                    title: 'Schedule team meeting for project kickoff',
                    description: 'Coordinate with team members to schedule the initial project kickoff meeting for the new client onboarding system.',
                    confidence: 0.87,
                    source: 'teams',
                    sender: 'Sarah Chen',
                    extractedAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), // 3 hours ago
                    status: 'pending',
                    tags: ['meeting', 'project', 'coordination']
                },
                {
                    id: 3,
                    title: 'Update documentation for API endpoints',
                    description: 'The new authentication endpoints need to be documented and added to the developer portal.',
                    confidence: 0.92,
                    source: 'email',
                    sender: 'tech-team@company.com',
                    extractedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
                    status: 'pending',
                    tags: ['documentation', 'api', 'development']
                },
                {
                    id: 4,
                    title: 'Prepare presentation for client demo',
                    description: 'Create slides and demo environment for the upcoming client presentation next week.',
                    confidence: 0.78,
                    source: 'teams',
                    sender: 'Marketing Team',
                    extractedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
                    status: 'pending',
                    tags: ['presentation', 'client', 'demo']
                },
                {
                    id: 5,
                    title: 'Review security audit findings',
                    description: 'Go through the security audit report and prioritize the remediation items.',
                    confidence: 0.89,
                    source: 'email',
                    sender: 'security@company.com',
                    extractedAt: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8 hours ago
                    status: 'completed',
                    tags: ['security', 'audit', 'review']
                }
            ]
        };
    },

    async getDashboardStats() {
        return {
            total_tasks: 47,
            pending_review: 8,
            high_confidence: 42,
            synced_today: 15
        };
    },

    async updateTask(taskId, updates) {
        console.log('Mock: Updating task', taskId, 'with', updates);
        return { success: true };
    }
};

// Backend API integration
const API_BASE_URL = 'http://localhost:8000/api';

const backendAPI = {
    async apiRequest(method, endpoint, data = null) {
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    async getTasks() {
        try {
            // First check if we're authenticated
            const authStatus = await this.apiRequest('GET', '/auth/status');
            
            if (!authStatus.authenticated) {
                // Return empty tasks if not authenticated
                return { tasks: [] };
            }

            // Get action items from backend
            const response = await this.apiRequest('GET', '/actions/');
            
            // Transform backend action items to UI format
            const tasks = response.action_items?.map(item => ({
                id: item.id,
                title: item.task_description,
                description: item.context || item.task_description,
                confidence: item.confidence_score,
                source: item.source_type,
                sender: item.assignee_email || 'System',
                extractedAt: item.created_at,
                status: item.status,
                tags: item.priority ? [item.priority] : []
            })) || [];

            return { tasks };
        } catch (error) {
            console.error('Failed to fetch tasks from backend:', error);
            // Fallback to mock data if backend unavailable
            return this.getMockTasks();
        }
    },

    async getDashboardStats() {
        try {
            const authStatus = await this.apiRequest('GET', '/auth/status');
            
            if (!authStatus.authenticated) {
                return {
                    total_tasks: 0,
                    pending_review: 0,
                    high_confidence: 0,
                    synced_today: 0
                };
            }

            const response = await this.apiRequest('GET', '/actions/stats');
            
            return {
                total_tasks: response.total_items || 0,
                pending_review: response.pending_items || 0,
                high_confidence: response.high_confidence_items || 0,
                synced_today: response.processed_today || 0
            };
        } catch (error) {
            console.error('Failed to fetch stats from backend:', error);
            // Fallback stats if backend unavailable
            return {
                total_tasks: 0,
                pending_review: 0,
                high_confidence: 0,
                synced_today: 0
            };
        }
    },

    async updateTask(taskId, updates) {
        try {
            const response = await this.apiRequest('PUT', `/actions/${taskId}`, {
                status: updates.status,
                priority: updates.priority,
                assignee_email: updates.assignee_email
            });
            return response;
        } catch (error) {
            console.error('Failed to update task:', error);
            throw error;
        }
    },

    async getAuthStatus() {
        try {
            return await this.apiRequest('GET', '/auth/status');
        } catch (error) {
            console.error('Failed to get auth status:', error);
            return { authenticated: false };
        }
    },

    async startOAuthLogin() {
        try {
            const response = await this.apiRequest('GET', '/auth/microsoft/login');
            if (response.auth_url) {
                // Open auth URL in external browser
                window.open(response.auth_url, '_blank');
            }
            return response;
        } catch (error) {
            console.error('Failed to start OAuth login:', error);
            throw error;
        }
    },

    async processEmails() {
        try {
            const response = await this.apiRequest('POST', '/emails/process-for-actions', {
                days_back: 7,
                max_emails: 20,
                filter_unread: true
            });
            return response;
        } catch (error) {
            console.error('Failed to process emails:', error);
            throw error;
        }
    },

    // Fallback mock data when backend is unavailable
    getMockTasks() {
        return {
            tasks: [
                {
                    id: 'mock-1',
                    title: '[Demo Mode] Review Q4 budget proposals',
                    description: 'Backend unavailable - showing demo data. Need to review the budget proposals for Q4.',
                    confidence: 0.95,
                    source: 'email',
                    sender: 'john.doe@company.com',
                    extractedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                    status: 'pending',
                    tags: ['demo', 'finance', 'review']
                }
            ]
        };
    }
};

// Enhanced electronAPI with backend integration
if (!window.electronAPI) {
    window.electronAPI = {
        async apiRequest(method, endpoint, data) {
            // Transform frontend API calls to backend format
            if (endpoint.includes('/tasks') && method === 'GET') {
                return await backendAPI.getTasks();
            } else if (endpoint.includes('/dashboard/stats')) {
                return await backendAPI.getDashboardStats();
            } else if (endpoint.includes('/tasks/') && method === 'PUT') {
                const taskId = endpoint.split('/').pop();
                return await backendAPI.updateTask(taskId, data);
            }
            
            // Direct backend pass-through for other calls
            return await backendAPI.apiRequest(method, endpoint, data);
        }
    };
}

const App = () => {
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [isLoading, setIsLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [authError, setAuthError] = useState(null);
    const [backendStatus, setBackendStatus] = useState('checking');

    useEffect(() => {
        initializeApp();
    }, []);

    const initializeApp = async () => {
        try {
            setBackendStatus('checking');
            
            // Check if backend is running
            const healthCheck = await backendAPI.apiRequest('GET', '/');
            console.log('Backend health check:', healthCheck);
            
            // Check authentication status
            const authStatus = await backendAPI.getAuthStatus();
            setIsAuthenticated(authStatus.authenticated);
            
            setBackendStatus('connected');
            setAuthError(null);
            
        } catch (error) {
            console.error('Backend connection failed:', error);
            setBackendStatus('disconnected');
            setAuthError('Backend server unavailable - running in demo mode');
            setIsAuthenticated(false);
        } finally {
            setIsLoading(false);
        }
    };

    const handleOAuthLogin = async () => {
        try {
            setAuthError(null);
            
            if (backendStatus === 'disconnected') {
                setAuthError('Backend server unavailable. Please start the backend server.');
                return;
            }
            
            await backendAPI.startOAuthLogin();
            
            // Poll for authentication completion (optional - for better UX)
            const pollAuth = setInterval(async () => {
                try {
                    const authStatus = await backendAPI.getAuthStatus();
                    if (authStatus.authenticated) {
                        setIsAuthenticated(true);
                        clearInterval(pollAuth);
                        setCurrentPage('dashboard'); // Redirect to dashboard
                    }
                } catch (error) {
                    // Continue polling
                }
            }, 2000);
            
            // Stop polling after 2 minutes
            setTimeout(() => clearInterval(pollAuth), 120000);
            
        } catch (error) {
            console.error('OAuth login failed:', error);
            setAuthError('Failed to start OAuth login. Please try again.');
        }
    };

    const handleProcessEmails = async () => {
        try {
            setAuthError(null);
            
            if (!isAuthenticated) {
                setAuthError('Please authenticate first to process emails.');
                return;
            }
            
            const result = await backendAPI.processEmails();
            console.log('Email processing result:', result);
            
            // Refresh dashboard after processing
            if (currentPage === 'dashboard') {
                window.location.reload(); // Simple refresh - could be optimized
            }
            
        } catch (error) {
            console.error('Email processing failed:', error);
            setAuthError('Failed to process emails. Please try again.');
        }
    };

    if (isLoading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                background: 'var(--color-bg-primary)',
                color: 'var(--color-text-secondary)'
            }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ 
                        fontSize: '24px', 
                        marginBottom: '16px',
                        color: 'var(--color-primary)'
                    }}>
                        📋
                    </div>
                    <div>Loading TaskHarvester...</div>
                </div>
            </div>
        );
    }

    return (
        <Layout 
            currentPage={currentPage} 
            onNavigate={setCurrentPage}
            isAuthenticated={isAuthenticated}
            backendStatus={backendStatus}
            onOAuthLogin={handleOAuthLogin}
            onProcessEmails={handleProcessEmails}
            authError={authError}
        >
            {currentPage === 'dashboard' && <Dashboard />}
            {currentPage === 'tasks' && <div style={{ padding: '24px' }}>All Tasks View (Coming Soon)</div>}
            {currentPage === 'review' && <div style={{ padding: '24px' }}>Review Queue (Coming Soon)</div>}
            {currentPage === 'email' && <EmailSourcesPage 
                isAuthenticated={isAuthenticated}
                onOAuthLogin={handleOAuthLogin}
                onProcessEmails={handleProcessEmails}
                authError={authError}
                backendStatus={backendStatus}
            />}
            {currentPage === 'sync' && <SyncStatusPage 
                backendStatus={backendStatus}
                isAuthenticated={isAuthenticated}
            />}
            {currentPage === 'settings' && <div style={{ padding: '24px' }}>Settings (Coming Soon)</div>}
        </Layout>
    );
};

// Email Sources Page Component
const EmailSourcesPage = ({ isAuthenticated, onOAuthLogin, onProcessEmails, authError, backendStatus }) => {
    return (
        <div style={{ padding: '24px' }}>
            <h2 style={{ marginBottom: '24px', fontSize: '24px', fontWeight: '600' }}>Email Sources</h2>
            
            {/* Backend Status */}
            <div style={{ 
                background: backendStatus === 'connected' ? '#e8f5e8' : '#ffe6e6',
                border: `1px solid ${backendStatus === 'connected' ? '#4CAF50' : '#f44336'}`,
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '24px'
            }}>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>
                    Backend Status: {backendStatus === 'connected' ? '✅ Connected' : '❌ Disconnected'}
                </h3>
                <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
                    {backendStatus === 'connected' 
                        ? 'Successfully connected to TaskHarvester backend server'
                        : 'Backend server is not running. Please start the backend server to use email processing features.'
                    }
                </p>
            </div>

            {/* Authentication Status */}
            <div style={{ 
                background: isAuthenticated ? '#e8f5e8' : '#fff3cd',
                border: `1px solid ${isAuthenticated ? '#4CAF50' : '#ffc107'}`,
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '24px'
            }}>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>
                    Microsoft Graph: {isAuthenticated ? '✅ Authenticated' : '⚠️ Not Authenticated'}
                </h3>
                <p style={{ margin: '0 0 16px 0', fontSize: '14px', color: '#666' }}>
                    {isAuthenticated 
                        ? 'Successfully authenticated with Microsoft Graph. You can now process emails.'
                        : 'You need to authenticate with Microsoft Graph to access your emails.'
                    }
                </p>
                
                {!isAuthenticated && (
                    <button
                        onClick={onOAuthLogin}
                        disabled={backendStatus !== 'connected'}
                        style={{
                            background: '#5865F2',
                            color: 'white',
                            border: 'none',
                            padding: '10px 20px',
                            borderRadius: '6px',
                            cursor: backendStatus === 'connected' ? 'pointer' : 'not-allowed',
                            opacity: backendStatus === 'connected' ? 1 : 0.5
                        }}
                    >
                        🔐 Sign in with Microsoft
                    </button>
                )}
            </div>

            {/* Email Processing */}
            {isAuthenticated && (
                <div style={{ 
                    background: '#f0f8ff',
                    border: '1px solid #007acc',
                    borderRadius: '8px',
                    padding: '16px',
                    marginBottom: '24px'
                }}>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>Email Processing</h3>
                    <p style={{ margin: '0 0 16px 0', fontSize: '14px', color: '#666' }}>
                        Process your recent emails to extract action items using AI.
                    </p>
                    
                    <button
                        onClick={onProcessEmails}
                        style={{
                            background: '#007acc',
                            color: 'white',
                            border: 'none',
                            padding: '10px 20px',
                            borderRadius: '6px',
                            cursor: 'pointer'
                        }}
                    >
                        🤖 Process Recent Emails
                    </button>
                </div>
            )}

            {/* Error Display */}
            {authError && (
                <div style={{ 
                    background: '#ffe6e6',
                    border: '1px solid #f44336',
                    borderRadius: '8px',
                    padding: '16px',
                    color: '#d32f2f'
                }}>
                    <strong>Error:</strong> {authError}
                </div>
            )}
        </div>
    );
};

// Sync Status Page Component
const SyncStatusPage = ({ backendStatus, isAuthenticated }) => {
    return (
        <div style={{ padding: '24px' }}>
            <h2 style={{ marginBottom: '24px', fontSize: '24px', fontWeight: '600' }}>Sync Status</h2>
            
            <div style={{ display: 'grid', gap: '16px' }}>
                {/* Backend Connection */}
                <div style={{ 
                    background: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '8px',
                    padding: '16px'
                }}>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>Backend Server</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ 
                            width: '12px', 
                            height: '12px', 
                            borderRadius: '50%', 
                            background: backendStatus === 'connected' ? '#4CAF50' : '#f44336',
                            display: 'inline-block'
                        }}></span>
                        <span>{backendStatus === 'connected' ? 'Connected' : 'Disconnected'}</span>
                    </div>
                </div>

                {/* Microsoft Graph */}
                <div style={{ 
                    background: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '8px',
                    padding: '16px'
                }}>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>Microsoft Graph</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ 
                            width: '12px', 
                            height: '12px', 
                            borderRadius: '50%', 
                            background: isAuthenticated ? '#4CAF50' : '#f44336',
                            display: 'inline-block'
                        }}></span>
                        <span>{isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</span>
                    </div>
                </div>

                {/* AI Processor */}
                <div style={{ 
                    background: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '8px',
                    padding: '16px'
                }}>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>AI Processor (Ollama)</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ 
                            width: '12px', 
                            height: '12px', 
                            borderRadius: '50%', 
                            background: backendStatus === 'connected' ? '#4CAF50' : '#f44336',
                            display: 'inline-block'
                        }}></span>
                        <span>Status depends on backend connection</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default App;