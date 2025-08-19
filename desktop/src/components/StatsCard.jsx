import React from 'react';

const StatsCard = ({ title, value, icon, trend, trendDirection = 'neutral' }) => {
  const getIcon = (iconType) => {
    switch (iconType) {
      case 'tasks':
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.11 0 2-.9 2-2V5c0-1.1-.89-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
        );
      case 'review':
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        );
      case 'confidence':
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
          </svg>
        );
      case 'sync':
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
          </svg>
        );
      default:
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        );
    }
  };

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'up':
        return (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14l5-5 5 5z"/>
          </svg>
        );
      case 'down':
        return (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 10l5 5 5-5z"/>
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="stats-card">
      <div className="stats-card-header">
        <div className="stats-icon">
          {getIcon(icon)}
        </div>
        <div className="stats-trend">
          {trend && (
            <div className={`trend trend-${trendDirection}`}>
              {getTrendIcon(trendDirection)}
              <span className="trend-text">{trend}</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="stats-content">
        <div className="stats-value">{value}</div>
        <div className="stats-title">{title}</div>
      </div>

      <style jsx>{`
        .stats-card {
          background: var(--color-bg-elevated);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--spacing-xl);
          transition: all var(--transition-fast);
          position: relative;
          overflow: hidden;
        }
        
        .stats-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-md);
          border-color: var(--color-primary-light);
        }
        
        .stats-card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: var(--spacing-lg);
        }
        
        .stats-icon {
          width: 48px;
          height: 48px;
          border-radius: var(--radius-lg);
          background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          flex-shrink: 0;
        }
        
        .stats-content {
          text-align: left;
        }
        
        .stats-value {
          font-size: var(--font-size-3xl);
          font-weight: var(--font-weight-bold);
          color: var(--color-text-primary);
          line-height: var(--line-height-tight);
          margin-bottom: var(--spacing-xs);
        }
        
        .stats-title {
          font-size: var(--font-size-base);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-secondary);
        }
        
        .stats-trend {
          display: flex;
          align-items: center;
        }
        
        .trend {
          display: flex;
          align-items: center;
          gap: var(--spacing-xs);
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-full);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
        }
        
        .trend-up {
          background: rgba(59, 165, 92, 0.1);
          color: var(--color-accent);
        }
        
        .trend-down {
          background: rgba(237, 66, 69, 0.1);
          color: var(--color-danger);
        }
        
        .trend-neutral {
          background: var(--color-bg-tertiary);
          color: var(--color-text-tertiary);
        }
        
        .trend-text {
          white-space: nowrap;
        }
        
        /* Subtle background pattern */
        .stats-card::before {
          content: '';
          position: absolute;
          top: 0;
          right: 0;
          width: 100px;
          height: 100px;
          background: linear-gradient(45deg, transparent 70%, rgba(88, 101, 242, 0.03));
          border-radius: 0 var(--radius-lg) 0 100%;
          pointer-events: none;
        }
        
        /* Icon specific styles */
        .stats-icon svg {
          transition: transform var(--transition-fast);
        }
        
        .stats-card:hover .stats-icon svg {
          transform: scale(1.1);
        }
        
        @media (max-width: 768px) {
          .stats-card {
            padding: var(--spacing-lg);
          }
          
          .stats-value {
            font-size: var(--font-size-2xl);
          }
          
          .stats-icon {
            width: 40px;
            height: 40px;
          }
          
          .stats-icon svg {
            width: 20px;
            height: 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default StatsCard;