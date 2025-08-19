# TaskHarvester UI Design Specification

## Overview

TaskHarvester features a modern, professional Electron interface designed for AI-powered task extraction and management. The design draws inspiration from successful Electron applications like Discord, Notion, VS Code, and Slack, creating a familiar yet unique experience optimized for productivity and task management.

## Design Philosophy

### Core Principles
- **Trust & Reliability**: Professional appearance that instills confidence in AI capabilities
- **Efficiency First**: Streamlined workflows for task review and management
- **Visual Hierarchy**: Clear organization of information with appropriate emphasis
- **Adaptive Interface**: Responsive design that works across different window sizes
- **Accessibility**: WCAG-compliant design with proper focus management

### Visual Style
- **Modern Minimalism**: Clean lines, generous whitespace, purposeful design elements
- **Subtle Sophistication**: Refined shadows, smooth transitions, and polished interactions
- **Color Psychology**: Calming blues for trust, greens for success, strategic use of red for urgency

## Design System

### Color Palette

#### Primary Colors
- **Primary Blue**: `#5865F2` - Main brand color, inspired by Discord's modern approach
- **Primary Hover**: `#4752C4` - Interactive state
- **Primary Light**: `#7289DA` - Accents and highlights
- **Primary Dark**: `#3C45A5` - Deep variants

#### Semantic Colors
- **Success/Accent**: `#3BA55C` - Completed tasks, positive indicators
- **Warning**: `#FAA61A` - Medium confidence, attention needed
- **Danger**: `#ED4245` - Errors, low confidence, critical actions
- **Info**: `#00B0F4` - Links, informational content

#### Neutral Colors (Light Theme)
- **Background Primary**: `#FFFFFF` - Main content areas
- **Background Secondary**: `#F7F8FA` - Secondary panels, subtle backgrounds
- **Background Tertiary**: `#E3E5E8` - Borders, dividers, inactive states
- **Background Elevated**: `#FFFFFF` - Cards, modals, elevated content
- **Background Sidebar**: `#F2F3F5` - Navigation sidebar

#### Text Hierarchy
- **Text Primary**: `#2E3338` - Main content, headings
- **Text Secondary**: `#4F545C` - Descriptions, labels
- **Text Tertiary**: `#72767D` - Metadata, timestamps
- **Text Muted**: `#96989D` - Placeholders, disabled text

#### Dark Theme Support
Complete dark theme implementation with adjusted colors:
- **Background Primary**: `#1E1F22` - Main content areas
- **Background Secondary**: `#2B2D31` - Secondary panels
- **Background Tertiary**: `#313338` - Elevated content
- **Text Primary**: `#F2F3F5` - High contrast text
- **Text Secondary**: `#B5BAC1` - Secondary text

### Typography

#### Font Stack
- **Primary**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif`
- **Monospace**: `'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Consolas', monospace`

#### Type Scale
- **3XL (30px)**: Page titles, hero headings
- **2XL (24px)**: Section headings
- **XL (20px)**: Subsection headings
- **LG (18px)**: Card titles, prominent text
- **MD (16px)**: Body text, form labels
- **Base (14px)**: Standard body text, interface text
- **SM (12px)**: Metadata, captions
- **XS (11px)**: Fine print, tiny labels

#### Font Weights
- **Normal (400)**: Body text
- **Medium (500)**: Emphasized text, navigation
- **Semibold (600)**: Section headings, important labels
- **Bold (700)**: Main headings, strong emphasis

### Spacing System

Based on 4px grid system:
- **XS**: 4px - Tight spacing
- **SM**: 8px - Close elements
- **MD**: 12px - Related content
- **LG**: 16px - Component padding
- **XL**: 24px - Section spacing
- **2XL**: 32px - Large gaps
- **3XL**: 48px - Major sections
- **4XL**: 64px - Page-level spacing

### Border Radius
- **SM**: 4px - Small elements, chips
- **MD**: 6px - Buttons, inputs
- **LG**: 8px - Cards, panels
- **XL**: 12px - Large cards, modals
- **2XL**: 16px - Hero elements
- **Full**: 50% - Circular elements, pills

### Shadows & Elevation
- **SM**: `0 1px 2px rgba(0, 0, 0, 0.05)` - Subtle elevation
- **MD**: `0 4px 6px rgba(0, 0, 0, 0.07)` - Standard cards
- **LG**: `0 10px 25px rgba(0, 0, 0, 0.1)` - Prominent cards
- **XL**: `0 20px 40px rgba(0, 0, 0, 0.15)` - Major modals
- **Elevated**: `0 8px 16px rgba(0, 0, 0, 0.12)` - Floating elements

## Layout Architecture

### Application Structure
```
┌─────────────────────────────────────────────────────────┐
│                    Custom Titlebar                     │ 32px
│  TaskHarvester    [Theme] [Status]    [- □ ×]          │
├─────────────────────────────────────────────────────────┤
│          │                                             │
│          │              Main Content                   │
│ Sidebar  │                                             │
│ 240px    │         Dashboard/Tasks/Settings            │
│          │                                             │
│          │                                             │
│          │                                             │
└─────────────────────────────────────────────────────────┘
```

### Grid System
- **Sidebar Width**: 240px (collapsed: 64px)
- **Content Margin**: Dynamic based on sidebar state
- **Max Content Width**: No limit (responsive to window)
- **Responsive Breakpoints**: 768px for mobile considerations

## Component Specifications

### Custom Titlebar
**Purpose**: Native-feeling window controls with app branding
**Features**:
- App icon and name
- Real-time connection status indicator
- Theme toggle button
- Platform-specific window controls
- Drag region for window movement

**Visual Elements**:
- Height: 32px
- Background: Secondary background color
- Border: 1px bottom border
- Typography: Small (12px), medium weight

### Sidebar Navigation
**Purpose**: Primary navigation with visual feedback
**Features**:
- Collapsible design (240px → 64px)
- Active state indicators
- Badge notifications for counts
- User profile section
- Hover tooltips when collapsed

**Navigation Items**:
1. **Dashboard** - Overview and recent tasks
2. **All Tasks** - Complete task management
3. **Review Queue** - Tasks needing attention
4. **Email Sources** - Source configuration
5. **Sync Status** - Connection and sync information
6. **Settings** - App configuration

### Task Card Component
**Purpose**: Primary interface for task display and interaction
**Features**:
- AI confidence indicators (High/Medium/Low)
- Source identification (Email/Teams)
- Quick actions dropdown
- Status indicators
- Tag system
- Hover interactions

**Visual States**:
- **Default**: Clean card with subtle shadow
- **Hover**: Elevated with stronger shadow, action buttons visible
- **Selected**: Primary border color
- **Completed**: Reduced opacity, strikethrough title

### AI Confidence Indicators
**Purpose**: Communicate AI extraction reliability
**Design**:
- **High (90%+)**: Green indicator, "High Confidence"
- **Medium (70-89%)**: Orange indicator, "Medium Confidence"  
- **Low (<70%)**: Red indicator, "Needs Review"
- **Visual**: Colored dot + percentage + descriptive text

### Stats Cards
**Purpose**: Dashboard metrics display
**Features**:
- Large numeric values
- Trend indicators (up/down/neutral)
- Iconography for quick recognition
- Hover animations
- Gradient backgrounds

### Search & Filter System
**Purpose**: Efficient task discovery and organization
**Components**:
- **Search Bar**: Full-text search with suggestions
- **Quick Filters**: One-click common filters
- **Advanced Filters**: Comprehensive filter dropdown
- **Active Filter Display**: Current filter state visibility

## Interaction Patterns

### Hover States
- **Cards**: Subtle elevation increase (2px up), stronger shadow
- **Buttons**: Background color change, slight scale increase
- **Navigation**: Background change, icon/text color shift

### Focus States
- **Keyboard Navigation**: 2px solid primary color outline
- **Interactive Elements**: Consistent focus ring
- **Skip Links**: Hidden until focused

### Loading States
- **Skeleton Screens**: Animated loading placeholders
- **Spinners**: For async operations
- **Progress Indicators**: For known duration tasks

### Transitions
- **Fast (150ms)**: Hover states, color changes
- **Base (250ms)**: Layout changes, component state
- **Slow (350ms)**: Page transitions, modal open/close

## Responsive Design

### Breakpoints
- **Desktop**: Default layout (1024px+)
- **Tablet**: Simplified layouts (768px - 1023px)
- **Mobile**: Stacked layouts, hidden sidebar (< 768px)

### Adaptive Behaviors
- **Sidebar**: Auto-collapse on smaller screens
- **Cards**: Stack vertically on mobile
- **Tables**: Horizontal scroll or card view
- **Modals**: Full-screen on mobile

## Accessibility Features

### Keyboard Navigation
- **Tab Order**: Logical flow through interface
- **Shortcuts**: Common actions accessible via keyboard
- **Focus Management**: Proper focus trapping in modals

### Screen Reader Support
- **ARIA Labels**: Comprehensive labeling
- **Live Regions**: Status updates announced
- **Semantic HTML**: Proper heading hierarchy

### Color & Contrast
- **WCAG AA Compliance**: 4.5:1 contrast ratios
- **Color Independence**: Information not conveyed by color alone
- **High Contrast Mode**: Support for system preferences

## Animation & Microinteractions

### Page Transitions
- **Slide In**: New content slides from appropriate direction
- **Fade**: Smooth opacity transitions
- **Scale**: Subtle scale effects for modals

### Feedback Animations
- **Success**: Checkmark animation, green flash
- **Error**: Shake animation, red flash  
- **Loading**: Pulse effects, skeleton screens

### Performance Considerations
- **Hardware Acceleration**: CSS transforms for smooth animations
- **Reduced Motion**: Respect system preferences
- **Frame Rate**: 60fps target for all animations

## Platform-Specific Considerations

### macOS
- **Traffic Lights**: Native window controls
- **Titlebar**: Integrated with system styling
- **Shadows**: Subtle, system-appropriate

### Windows
- **Window Controls**: Custom implementation
- **Titlebar**: Custom design with system integration
- **Borders**: Appropriate for Windows 10/11

### Linux
- **Flexibility**: Adapt to various desktop environments
- **Themes**: System theme integration where possible

## Implementation Guidelines

### CSS Architecture
- **Custom Properties**: CSS variables for theming
- **Component Isolation**: Scoped styles per component
- **Utility Classes**: Common patterns as reusable classes

### Performance Optimization
- **Critical CSS**: Inline critical path styles
- **Code Splitting**: Load styles per route
- **Caching**: Proper cache headers for assets

### Browser Compatibility
- **Electron Chromium**: Latest stable features
- **Fallbacks**: Graceful degradation for older versions
- **Testing**: Cross-platform testing required

## File Structure

```
desktop/src/
├── styles/
│   ├── design-system.css    # Core design tokens
│   └── components.css       # Component styles
├── components/
│   ├── Layout.jsx          # Main layout wrapper
│   ├── Titlebar.jsx        # Custom titlebar
│   ├── Sidebar.jsx         # Navigation sidebar
│   ├── TaskCard.jsx        # Task display component
│   ├── StatsCard.jsx       # Dashboard statistics
│   ├── SearchBar.jsx       # Search functionality
│   └── FilterBar.jsx       # Filtering system
└── pages/
    └── Dashboard.jsx       # Main dashboard page
```

## Future Enhancements

### Phase 2 Features
- **Drag & Drop**: Task reordering and organization
- **Bulk Operations**: Multi-select task management
- **Custom Views**: User-defined task layouts
- **Keyboard Shortcuts**: Power user productivity features

### Advanced Interactions
- **Split Panes**: Resizable layout sections
- **Panels**: Collapsible information panels
- **Workspace Switching**: Multiple project contexts

### Integration Features
- **Native Notifications**: System notification integration
- **System Tray**: Background operation indicators
- **Quick Add**: Global hotkey for task creation

This design system provides a comprehensive foundation for building a professional, modern, and highly usable task management interface that users will enjoy using daily.