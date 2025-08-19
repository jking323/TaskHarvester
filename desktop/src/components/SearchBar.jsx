import React, { useState, useRef, useEffect } from 'react';

const SearchBar = ({ value, onChange, placeholder = "Search...", suggestions = [] }) => {
  const [isFocused, setIsFocused] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        inputRef.current && 
        !inputRef.current.contains(event.target) &&
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
        setIsFocused(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    onChange(newValue);
    
    if (newValue.length > 0 && suggestions.length > 0) {
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  const handleInputFocus = () => {
    setIsFocused(true);
    if (value.length > 0 && suggestions.length > 0) {
      setShowSuggestions(true);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    onChange(suggestion);
    setShowSuggestions(false);
    inputRef.current?.blur();
  };

  const clearSearch = () => {
    onChange('');
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const filteredSuggestions = suggestions.filter(suggestion =>
    suggestion.toLowerCase().includes(value.toLowerCase()) && 
    suggestion.toLowerCase() !== value.toLowerCase()
  );

  return (
    <div className="search-bar">
      <div className={`search-input-container ${isFocused ? 'focused' : ''}`}>
        <div className="search-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
        </div>
        
        <input
          ref={inputRef}
          type="text"
          className="search-input"
          placeholder={placeholder}
          value={value}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
        />
        
        {value && (
          <button 
            className="search-clear"
            onClick={clearSearch}
            aria-label="Clear search"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        )}
      </div>
      
      {showSuggestions && filteredSuggestions.length > 0 && (
        <div ref={suggestionsRef} className="search-suggestions">
          <div className="suggestions-header">
            <span>Suggestions</span>
          </div>
          {filteredSuggestions.slice(0, 5).map((suggestion, index) => (
            <button
              key={index}
              className="suggestion-item"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
              <span>{suggestion}</span>
            </button>
          ))}
        </div>
      )}

      <style jsx>{`
        .search-bar {
          position: relative;
          width: 100%;
          max-width: 400px;
        }
        
        .search-input-container {
          position: relative;
          display: flex;
          align-items: center;
          background: var(--color-bg-tertiary);
          border: 1px solid transparent;
          border-radius: var(--radius-full);
          transition: all var(--transition-fast);
          overflow: hidden;
        }
        
        .search-input-container.focused,
        .search-input-container:hover {
          background: var(--color-bg-primary);
          border-color: var(--color-primary);
          box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.1);
        }
        
        .search-icon {
          position: absolute;
          left: 14px;
          color: var(--color-text-tertiary);
          pointer-events: none;
          z-index: 1;
        }
        
        .search-input {
          width: 100%;
          padding: var(--spacing-sm) var(--spacing-md);
          padding-left: 44px;
          padding-right: 44px;
          background: transparent;
          border: none;
          font-size: var(--font-size-base);
          color: var(--color-text-primary);
          outline: none;
        }
        
        .search-input::placeholder {
          color: var(--color-text-muted);
        }
        
        .search-clear {
          position: absolute;
          right: 12px;
          background: none;
          border: none;
          color: var(--color-text-tertiary);
          cursor: pointer;
          padding: 2px;
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .search-clear:hover {
          color: var(--color-text-primary);
          background: var(--color-bg-tertiary);
        }
        
        .search-suggestions {
          position: absolute;
          top: calc(100% + var(--spacing-xs));
          left: 0;
          right: 0;
          background: var(--color-bg-elevated);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-elevated);
          z-index: var(--z-dropdown);
          overflow: hidden;
          animation: slideInFromTop var(--transition-fast);
        }
        
        .suggestions-header {
          padding: var(--spacing-sm) var(--spacing-md);
          background: var(--color-bg-secondary);
          border-bottom: 1px solid var(--color-border);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-tertiary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .suggestion-item {
          width: 100%;
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm) var(--spacing-md);
          background: none;
          border: none;
          color: var(--color-text-primary);
          cursor: pointer;
          transition: all var(--transition-fast);
          text-align: left;
        }
        
        .suggestion-item:hover {
          background: var(--color-bg-tertiary);
          color: var(--color-primary);
        }
        
        .suggestion-item svg {
          color: var(--color-text-muted);
          flex-shrink: 0;
        }
        
        .suggestion-item:hover svg {
          color: var(--color-primary);
        }
        
        /* Quick search shortcuts */
        .search-shortcuts {
          position: absolute;
          top: calc(100% + var(--spacing-xs));
          left: 0;
          right: 0;
          background: var(--color-bg-elevated);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-elevated);
          z-index: var(--z-dropdown);
          padding: var(--spacing-sm);
        }
        
        .shortcut-group {
          margin-bottom: var(--spacing-sm);
        }
        
        .shortcut-title {
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-tertiary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: var(--spacing-xs);
        }
        
        .shortcut-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: all var(--transition-fast);
        }
        
        .shortcut-item:hover {
          background: var(--color-bg-tertiary);
        }
        
        .shortcut-label {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }
        
        .shortcut-key {
          font-size: var(--font-size-xs);
          color: var(--color-text-muted);
          background: var(--color-bg-tertiary);
          padding: 2px 6px;
          border-radius: var(--radius-sm);
          font-family: var(--font-mono);
        }
        
        @media (max-width: 768px) {
          .search-bar {
            max-width: none;
          }
          
          .search-suggestions {
            left: var(--spacing-md);
            right: var(--spacing-md);
          }
        }
      `}</style>
    </div>
  );
};

export default SearchBar;