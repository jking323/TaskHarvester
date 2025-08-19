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

// Mock electron API
if (!window.electronAPI) {
    window.electronAPI = {
        async apiRequest(method, endpoint, data) {
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 500));
            
            if (endpoint.includes('/tasks')) {
                if (method === 'GET') {
                    return await mockAPI.getTasks();
                } else if (method === 'PUT') {
                    return await mockAPI.updateTask(endpoint.split('/').pop(), data);
                }
            } else if (endpoint.includes('/dashboard/stats')) {
                return await mockAPI.getDashboardStats();
            }
            
            return { error: 'Endpoint not found' };
        }
    };
}

const App = () => {
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Simulate app initialization
        setTimeout(() => {
            setIsLoading(false);
        }, 1000);
    }, []);

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
        <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
            {currentPage === 'dashboard' && <Dashboard />}
            {currentPage === 'tasks' && <div style={{ padding: '24px' }}>All Tasks View (Coming Soon)</div>}
            {currentPage === 'review' && <div style={{ padding: '24px' }}>Review Queue (Coming Soon)</div>}
            {currentPage === 'email' && <div style={{ padding: '24px' }}>Email Sources (Coming Soon)</div>}
            {currentPage === 'sync' && <div style={{ padding: '24px' }}>Sync Status (Coming Soon)</div>}
            {currentPage === 'settings' && <div style={{ padding: '24px' }}>Settings (Coming Soon)</div>}
        </Layout>
    );
};

export default App;