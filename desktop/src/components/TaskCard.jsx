import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';

const TaskCard = ({ task, onClick, onUpdate }) => {
  const [showActions, setShowActions] = useState(false);

  const getConfidenceLevel = (confidence) => {
    if (confidence >= 0.9) return 'high';
    if (confidence >= 0.7) return 'medium';
    return 'low';
  };

  const getConfidenceText = (confidence) => {
    return `${Math.round(confidence * 100)}% confidence`;
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'email':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
          </svg>
        );
      case 'teams':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        );
      default:
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        );
    }
  };

  const handleStatusChange = (newStatus) => {
    onUpdate({ status: newStatus });
    setShowActions(false);
  };

  const handleCardClick = (e) => {
    // Don't trigger card click if clicking on action buttons
    if (e.target.closest('.task-actions') || e.target.closest('.dropdown-menu')) {
      return;
    }
    onClick(task);
  };

  const timeAgo = formatDistanceToNow(new Date(task.extractedAt), { addSuffix: true });

  return (
    <div 
      className={`task-card ${task.status === 'completed' ? 'completed' : ''}`}
      onClick={handleCardClick}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="task-card-header">
        <div className="task-card-main">
          <h3 className="task-card-title">{task.title}</h3>
          <div className="task-card-meta">
            <div className="source-info">
              {getSourceIcon(task.source)}
              <span className="source-label">{task.source}</span>
              <span className="source-sender">{task.sender}</span>
            </div>
            <div className="extraction-time">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                <path d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
              </svg>
              {timeAgo}
            </div>
          </div>
        </div>
        
        <div className={`task-actions ${showActions ? 'visible' : ''}`}>
          <div className="dropdown">
            <button className="btn btn-icon btn-ghost dropdown-trigger">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
              </svg>
            </button>
            
            <div className="dropdown-menu">
              <button 
                className="dropdown-item"
                onClick={() => handleStatusChange('in-progress')}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                Start Working
              </button>
              <button 
                className="dropdown-item"
                onClick={() => handleStatusChange('completed')}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                Mark Complete
              </button>
              <div className="dropdown-divider"></div>
              <button className="dropdown-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
                Edit Task
              </button>
              <button className="dropdown-item text-danger">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      {task.description && (
        <p className="task-card-description">
          {task.description.length > 150 
            ? `${task.description.substring(0, 150)}...`
            : task.description
          }
        </p>
      )}

      <div className="task-card-footer">
        <div className="task-tags">
          {task.tags?.slice(0, 3).map(tag => (
            <span key={tag} className="tag">
              {tag}
            </span>
          ))}
          {task.tags?.length > 3 && (
            <span className="tag tag-more">
              +{task.tags.length - 3} more
            </span>
          )}
        </div>
        
        <div className="task-indicators">
          <div className={`ai-confidence ${getConfidenceLevel(task.confidence)}`}>
            <div className="ai-confidence-indicator"></div>
            <span>{getConfidenceText(task.confidence)}</span>
          </div>
          
          <div className={`status-pill ${task.status}`}>
            {task.status.replace('-', ' ')}
          </div>
        </div>
      </div>

      <style jsx>{`
        .task-card.completed {
          opacity: 0.7;
        }
        
        .task-card.completed .task-card-title {
          text-decoration: line-through;
          color: var(--color-text-tertiary);
        }
        
        .task-card-main {
          flex: 1;
        }
        
        .task-actions {
          opacity: 0;
          transition: opacity var(--transition-fast);
        }
        
        .task-actions.visible {
          opacity: 1;
        }
        
        .source-info {
          display: flex;
          align-items: center;
          gap: var(--spacing-xs);
        }
        
        .source-label {
          text-transform: capitalize;
          font-weight: var(--font-weight-medium);
        }
        
        .source-sender {
          color: var(--color-text-muted);
        }
        
        .extraction-time {
          display: flex;
          align-items: center;
          gap: var(--spacing-xs);
        }
        
        .task-tags {
          display: flex;
          gap: var(--spacing-xs);
          flex-wrap: wrap;
        }
        
        .tag {
          padding: 2px var(--spacing-sm);
          background: var(--color-bg-tertiary);
          border-radius: var(--radius-sm);
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-secondary);
        }
        
        .tag-more {
          background: var(--color-primary);
          color: white;
        }
        
        .task-indicators {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
        }
        
        .dropdown {
          position: relative;
        }
        
        .dropdown-trigger:hover + .dropdown-menu,
        .dropdown-menu:hover {
          opacity: 1;
          visibility: visible;
          transform: translateY(0);
        }
        
        .text-danger {
          color: var(--color-danger) !important;
        }
        
        .task-card:hover .task-actions {
          opacity: 1;
        }
        
        @media (max-width: 768px) {
          .task-card-header {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .task-actions {
            opacity: 1;
            margin-top: var(--spacing-sm);
          }
          
          .task-card-footer {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-sm);
          }
        }
      `}</style>
    </div>
  );
};

export default TaskCard;