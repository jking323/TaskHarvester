import React, { useState, useRef, useEffect } from 'react';

const FilterBar = ({ filters = [], selectedFilters = [], onFilterChange }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleFilterToggle = (filter) => {
    const newFilters = selectedFilters.includes(filter)
      ? selectedFilters.filter(f => f !== filter)
      : [...selectedFilters, filter];
    
    onFilterChange(newFilters);
  };

  const clearAllFilters = () => {
    onFilterChange([]);
    setShowDropdown(false);
  };

  const predefinedFilterGroups = {
    'Status': ['pending', 'in-progress', 'completed', 'review'],
    'Priority': ['urgent', 'high', 'medium', 'low'],
    'Source': ['email', 'teams', 'manual'],
    'Confidence': ['high-confidence', 'medium-confidence', 'low-confidence']
  };

  const quickFilters = [
    { label: 'Needs Review', value: 'review', icon: 'review' },
    { label: 'High Priority', value: 'urgent', icon: 'priority' },
    { label: 'Recent', value: 'recent', icon: 'time' },
    { label: 'AI Extracted', value: 'ai-extracted', icon: 'ai' }
  ];

  const getFilterIcon = (iconType) => {
    switch (iconType) {
      case 'review':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        );
      case 'priority':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
          </svg>
        );
      case 'time':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
            <path d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
          </svg>
        );
      case 'ai':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="filter-bar">
      {/* Quick Filter Chips */}
      <div className="quick-filters">
        {quickFilters.map(filter => (
          <button
            key={filter.value}
            className={`filter-chip ${selectedFilters.includes(filter.value) ? 'active' : ''}`}
            onClick={() => handleFilterToggle(filter.value)}
          >
            {getFilterIcon(filter.icon)}
            <span>{filter.label}</span>
          </button>
        ))}
      </div>

      {/* Advanced Filters Dropdown */}
      <div className="filter-dropdown" ref={dropdownRef}>
        <button
          className={`filter-trigger btn btn-secondary ${showDropdown ? 'active' : ''}`}
          onClick={() => setShowDropdown(!showDropdown)}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
          </svg>
          More Filters
          {selectedFilters.length > 0 && (
            <span className="filter-count">{selectedFilters.length}</span>
          )}
        </button>

        {showDropdown && (
          <div className="filter-dropdown-menu">
            <div className="filter-dropdown-header">
              <h4>Filter Tasks</h4>
              {selectedFilters.length > 0 && (
                <button 
                  className="clear-filters-btn"
                  onClick={clearAllFilters}
                >
                  Clear All
                </button>
              )}
            </div>

            <div className="filter-groups">
              {Object.entries(predefinedFilterGroups).map(([groupName, groupFilters]) => (
                <div key={groupName} className="filter-group">
                  <h5 className="filter-group-title">{groupName}</h5>
                  <div className="filter-group-items">
                    {groupFilters.map(filter => (
                      <label key={filter} className="filter-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedFilters.includes(filter)}
                          onChange={() => handleFilterToggle(filter)}
                        />
                        <span className="checkbox-custom"></span>
                        <span className="filter-label">{filter.replace('-', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Custom Filter Input */}
            <div className="custom-filter">
              <label className="filter-group-title">Custom Tags</label>
              <input
                type="text"
                placeholder="Enter custom tag..."
                className="custom-filter-input"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    handleFilterToggle(e.target.value.trim());
                    e.target.value = '';
                  }
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Active Filters Display */}
      {selectedFilters.length > 0 && (
        <div className="active-filters">
          <span className="active-filters-label">Active:</span>
          {selectedFilters.map(filter => (
            <span key={filter} className="active-filter-tag">
              {filter.replace('-', ' ')}
              <button
                className="remove-filter"
                onClick={() => handleFilterToggle(filter)}
                aria-label={`Remove ${filter} filter`}
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </span>
          ))}
        </div>
      )}

      <style jsx>{`
        .filter-bar {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          flex-wrap: wrap;
        }
        
        .quick-filters {
          display: flex;
          gap: var(--spacing-sm);
          flex-wrap: wrap;
        }
        
        .filter-chip {
          display: inline-flex;
          align-items: center;
          gap: var(--spacing-xs);
          padding: var(--spacing-xs) var(--spacing-md);
          background: var(--color-bg-primary);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-full);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          cursor: pointer;
          transition: all var(--transition-fast);
          color: var(--color-text-secondary);
        }
        
        .filter-chip:hover {
          border-color: var(--color-primary);
          color: var(--color-primary);
          transform: translateY(-1px);
        }
        
        .filter-chip.active {
          background: var(--color-primary);
          border-color: var(--color-primary);
          color: white;
        }
        
        .filter-dropdown {
          position: relative;
        }
        
        .filter-trigger {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          position: relative;
        }
        
        .filter-trigger.active {
          background: var(--color-primary);
          color: white;
        }
        
        .filter-count {
          background: var(--color-danger);
          color: white;
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-bold);
          border-radius: var(--radius-full);
          padding: 2px 6px;
          margin-left: var(--spacing-xs);
        }
        
        .filter-dropdown-menu {
          position: absolute;
          top: calc(100% + var(--spacing-xs));
          right: 0;
          min-width: 320px;
          max-width: 400px;
          background: var(--color-bg-elevated);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-elevated);
          z-index: var(--z-dropdown);
          padding: var(--spacing-lg);
          animation: slideInFromTop var(--transition-fast);
        }
        
        .filter-dropdown-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-lg);
          padding-bottom: var(--spacing-sm);
          border-bottom: 1px solid var(--color-border);
        }
        
        .filter-dropdown-header h4 {
          font-size: var(--font-size-md);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-primary);
          margin: 0;
        }
        
        .clear-filters-btn {
          background: none;
          border: none;
          color: var(--color-primary);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          cursor: pointer;
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
        }
        
        .clear-filters-btn:hover {
          background: var(--color-bg-tertiary);
        }
        
        .filter-groups {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }
        
        .filter-group {
          margin-bottom: var(--spacing-md);
        }
        
        .filter-group-title {
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: var(--spacing-sm);
        }
        
        .filter-group-items {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
        }
        
        .filter-checkbox {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          cursor: pointer;
          padding: var(--spacing-xs);
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
        }
        
        .filter-checkbox:hover {
          background: var(--color-bg-tertiary);
        }
        
        .filter-checkbox input[type="checkbox"] {
          display: none;
        }
        
        .checkbox-custom {
          width: 16px;
          height: 16px;
          border: 2px solid var(--color-border);
          border-radius: var(--radius-sm);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all var(--transition-fast);
          flex-shrink: 0;
        }
        
        .filter-checkbox input[type="checkbox"]:checked + .checkbox-custom {
          background: var(--color-primary);
          border-color: var(--color-primary);
        }
        
        .filter-checkbox input[type="checkbox"]:checked + .checkbox-custom::after {
          content: '';
          width: 6px;
          height: 6px;
          background: white;
          border-radius: 1px;
        }
        
        .filter-label {
          font-size: var(--font-size-sm);
          color: var(--color-text-primary);
          text-transform: capitalize;
        }
        
        .custom-filter {
          border-top: 1px solid var(--color-border);
          padding-top: var(--spacing-md);
          margin-top: var(--spacing-md);
        }
        
        .custom-filter-input {
          width: 100%;
          padding: var(--spacing-sm) var(--spacing-md);
          background: var(--color-bg-primary);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          font-size: var(--font-size-sm);
          color: var(--color-text-primary);
          transition: all var(--transition-fast);
        }
        
        .custom-filter-input:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.1);
        }
        
        .active-filters {
          display: flex;
          align-items: center;
          gap: var(--spacing-xs);
          flex-wrap: wrap;
        }
        
        .active-filters-label {
          font-size: var(--font-size-sm);
          color: var(--color-text-tertiary);
          font-weight: var(--font-weight-medium);
        }
        
        .active-filter-tag {
          display: inline-flex;
          align-items: center;
          gap: var(--spacing-xs);
          padding: var(--spacing-xs) var(--spacing-sm);
          background: var(--color-primary);
          color: white;
          border-radius: var(--radius-full);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          text-transform: capitalize;
        }
        
        .remove-filter {
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          padding: 2px;
          border-radius: 50%;
          transition: all var(--transition-fast);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .remove-filter:hover {
          background: rgba(255, 255, 255, 0.2);
        }
        
        @media (max-width: 768px) {
          .filter-bar {
            flex-direction: column;
            align-items: stretch;
          }
          
          .quick-filters {
            width: 100%;
            justify-content: flex-start;
          }
          
          .filter-dropdown-menu {
            left: 0;
            right: 0;
            min-width: auto;
          }
        }
      `}</style>
    </div>
  );
};

export default FilterBar;