import React, { useState, useEffect } from 'react';
import TaskCard from '../components/TaskCard';
import StatsCard from '../components/StatsCard';
import SearchBar from '../components/SearchBar';
import FilterBar from '../components/FilterBar';

const Dashboard = ({ authData }) => {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({
    totalTasks: 0,
    pendingReview: 0,
    highConfidence: 0,
    syncedToday: 0
  });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilters, setSelectedFilters] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      if (window.electronAPI) {
        const [tasksResponse, statsResponse] = await Promise.all([
          window.electronAPI.apiRequest('GET', '/action-items/?limit=10&status=pending'),
          window.electronAPI.apiRequest('GET', '/action-items/stats/summary')
        ]);
        
        setTasks(tasksResponse.items || []);
        setStats({
          totalTasks: statsResponse.total_items || 0,
          pendingReview: statsResponse.pending_items || 0,
          highConfidence: statsResponse.items_with_high_confidence || 0,
          syncedToday: statsResponse.recent_processing_count || 0
        });
      } else {
        // Mock data for development
        setTasks(mockTasks);
        setStats(mockStats);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskClick = (task) => {
    // Navigate to task detail view
    console.log('Opening task:', task.id);
  };

  const handleTaskUpdate = async (taskId, updates) => {
    try {
      if (window.electronAPI) {
        await window.electronAPI.apiRequest('PUT', `/tasks/${taskId}`, updates);
        // Refresh tasks
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilters = selectedFilters.length === 0 || 
                          selectedFilters.some(filter => task.tags?.includes(filter));
    return matchesSearch && matchesFilters;
  });

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">AI-powered task extraction from your communications</p>
        </div>
        
        <div className="header-actions">
          <button className="btn btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
            Manual Task
          </button>
          
          <button className="btn btn-secondary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
            </svg>
            Sync Now
          </button>
        </div>
      </div>

      <div className="stats-grid">
        <StatsCard
          title="Total Tasks"
          value={stats.totalTasks}
          icon="tasks"
          trend="+12%"
          trendDirection="up"
        />
        <StatsCard
          title="Pending Review"
          value={stats.pendingReview}
          icon="review"
          trend="3 new"
          trendDirection="neutral"
        />
        <StatsCard
          title="High Confidence"
          value={stats.highConfidence}
          icon="confidence"
          trend="94%"
          trendDirection="up"
        />
        <StatsCard
          title="Synced Today"
          value={stats.syncedToday}
          icon="sync"
          trend="Last: 2m ago"
          trendDirection="neutral"
        />
      </div>

      <div className="dashboard-content">
        <div className="content-header">
          <h2>Recent Tasks</h2>
          <div className="content-controls">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search tasks..."
            />
            <FilterBar
              filters={availableFilters}
              selectedFilters={selectedFilters}
              onFilterChange={setSelectedFilters}
            />
          </div>
        </div>

        <div className="tasks-list">
          {filteredTasks.length > 0 ? (
            filteredTasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onClick={() => handleTaskClick(task)}
                onUpdate={(updates) => handleTaskUpdate(task.id, updates)}
              />
            ))
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <h3 className="empty-state-title">No tasks found</h3>
              <p className="empty-state-description">
                {searchQuery || selectedFilters.length > 0
                  ? 'Try adjusting your search or filters'
                  : 'Tasks extracted from your emails and Teams messages will appear here'
                }
              </p>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .dashboard {
          min-height: 100vh;
        }
        
        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: var(--spacing-2xl);
        }
        
        .header-content h1 {
          font-size: var(--font-size-3xl);
          font-weight: var(--font-weight-bold);
          color: var(--color-text-primary);
          margin-bottom: var(--spacing-xs);
        }
        
        .header-content p {
          color: var(--color-text-secondary);
          font-size: var(--font-size-md);
        }
        
        .header-actions {
          display: flex;
          gap: var(--spacing-md);
        }
        
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: var(--spacing-lg);
          margin-bottom: var(--spacing-2xl);
        }
        
        .content-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-xl);
        }
        
        .content-header h2 {
          font-size: var(--font-size-xl);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-primary);
        }
        
        .content-controls {
          display: flex;
          gap: var(--spacing-md);
          align-items: center;
        }
        
        .tasks-list {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-md);
        }
        
        @media (max-width: 768px) {
          .dashboard-header {
            flex-direction: column;
            gap: var(--spacing-lg);
          }
          
          .content-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);
          }
          
          .content-controls {
            width: 100%;
            flex-direction: column;
            align-items: stretch;
          }
        }
      `}</style>
    </div>
  );
};

const DashboardSkeleton = () => (
  <div className="dashboard">
    <div className="dashboard-header">
      <div className="header-content">
        <div className="skeleton" style={{ width: '200px', height: '36px', marginBottom: 'var(--spacing-xs)' }}></div>
        <div className="skeleton" style={{ width: '300px', height: '20px' }}></div>
      </div>
    </div>
    
    <div className="stats-grid">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="skeleton" style={{ height: '120px', borderRadius: 'var(--radius-lg)' }}></div>
      ))}
    </div>
    
    <div className="tasks-list">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="skeleton" style={{ height: '140px', borderRadius: 'var(--radius-lg)' }}></div>
      ))}
    </div>
  </div>
);

// Mock data for development
const mockTasks = [
  {
    id: 1,
    title: 'Review Q4 budget proposals',
    description: 'Need to review the budget proposals for Q4 and provide feedback by Friday',
    confidence: 0.95,
    source: 'email',
    sender: 'john.doe@company.com',
    extractedAt: '2024-01-15T10:30:00Z',
    status: 'pending',
    tags: ['finance', 'review', 'urgent']
  },
  {
    id: 2,
    title: 'Schedule team meeting for project kickoff',
    description: 'Coordinate with team members to schedule the initial project kickoff meeting',
    confidence: 0.87,
    source: 'teams',
    sender: 'Sarah Chen',
    extractedAt: '2024-01-15T09:15:00Z',
    status: 'pending',
    tags: ['meeting', 'project', 'coordination']
  }
];

const mockStats = {
  totalTasks: 47,
  pendingReview: 8,
  highConfidence: 42,
  syncedToday: 15
};

const availableFilters = [
  'urgent', 'review', 'meeting', 'finance', 'project', 'coordination'
];

export default Dashboard;